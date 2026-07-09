"""17 — Memory model, reference counting, GC, and weakref.

MUST KNOW
  - Variables are NAMES bound to objects; assignment binds a name, it doesn't copy.
  - CPython frees an object when its reference count hits 0 (immediate, deterministic).
  - A separate cyclic garbage collector (`gc`) reclaims reference CYCLES that refcounting
    can't (A→B→A).
  - `weakref` gives a reference that does NOT keep the object alive — used for caches so
    you don't leak memory.
  - `__slots__` removes the per-instance `__dict__` (big memory win for many small objects).
  - `sys.intern` / small-int caching share identical immutable objects.

INTERVIEW QUESTIONS
  - "How does Python manage memory?" (refcounting + cyclic GC).
  - "What's a weak reference and when would you use one?"
  - "Does `b = a` copy the object?" (no — both names point to the same object).
"""

from __future__ import annotations

import gc
import sys
import weakref


class Node:
    """A plain object we can point weak references at (needs a __weakref__ slot)."""


def _demo() -> None:
    # 1. Names bind to objects; mutation is visible through every name.
    a = [1, 2, 3]
    b = a  # same object, not a copy
    b.append(4)
    assert a == [1, 2, 3, 4] and a is b

    # 2. Immutable "rebinding" doesn't affect the other name.
    x = 10
    y = x
    x += 1  # rebinds x to a NEW int object; y still points at 10
    assert x == 11 and y == 10

    # 3. weakref: does not keep the object alive.
    obj = Node()
    ref = weakref.ref(obj)
    assert ref() is obj  # dereference while alive
    del obj
    gc.collect()
    assert ref() is None  # collected once the last strong ref is gone

    # 4. WeakValueDictionary: a cache that auto-evicts when values are no longer used
    #    elsewhere (no memory leak from a growing cache).
    cache: weakref.WeakValueDictionary[str, Node] = weakref.WeakValueDictionary()
    n = Node()
    cache["k"] = n
    assert cache["k"] is n
    del n
    gc.collect()
    assert "k" not in cache  # value was weakly held, so the entry vanished

    # 5. Reference CYCLES need the cyclic GC (refcount alone can't free them).
    p, q = Node(), Node()
    p.other = q  # type: ignore[attr-defined]
    q.other = p  # type: ignore[attr-defined]  # cycle: p <-> q
    wp = weakref.ref(p)
    del p, q  # refcounts stay > 0 because of the cycle...
    gc.collect()  # ...the cyclic collector breaks it
    assert wp() is None

    # 6. sys.intern: force identical strings to be the SAME object (fast `is` compares,
    #    memory savings for many repeated tokens/keys).
    s1 = sys.intern("a_long_dynamic_" + "key")
    s2 = sys.intern("a_long_dynamic_" + "key")
    assert s1 is s2  # interned -> identical object

    # 7. __slots__ instances have no __dict__ (memory saving).
    class Slotted:
        __slots__ = ("v",)

        def __init__(self, v: int) -> None:
            self.v = v

    assert not hasattr(Slotted(1), "__dict__")

    print("17_memory_gc: all assertions passed ✅")


if __name__ == "__main__":
    _demo()
