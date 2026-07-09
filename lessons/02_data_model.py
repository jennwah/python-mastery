"""02 — The data model (dunder methods) = what makes code "Pythonic".

MUST KNOW
  - `__repr__` (unambiguous, for devs) vs `__str__` (readable, for users).
  - The `__eq__` / `__hash__` contract: if you define `__eq__`, you usually must define
    `__hash__` (or the object becomes unhashable). Equal objects MUST have equal hashes.
  - Container protocol: `__len__`, `__getitem__`, `__iter__`, `__contains__`.
  - Context manager: `__enter__` / `__exit__`.
  - `__call__` (make instances callable), `__slots__` (memory + attribute locking).

INTERVIEW QUESTIONS
  - "Why must equal objects have equal hashes?" (dicts/sets bucket by hash, then ==).
  - "What does `__slots__` do?" (no per-instance __dict__: less memory, no new attrs).
  - "repr vs str?"  "How do you make an object work with `with`?"
"""

from __future__ import annotations

from collections.abc import Iterator
from functools import total_ordering


# --- 1. repr/str, eq/hash: the value-object contract ---
class Money:
    __slots__ = ("cents",)  # no __dict__: saves memory, forbids new attributes

    def __init__(self, cents: int) -> None:
        self.cents = cents

    def __repr__(self) -> str:  # for developers/debuggers; aim to be unambiguous
        return f"Money(cents={self.cents})"

    def __str__(self) -> str:  # for users
        return f"${self.cents / 100:.2f}"

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Money) and other.cents == self.cents

    def __hash__(self) -> int:
        # Equal objects MUST hash equal — hash the same data used in __eq__.
        return hash(self.cents)


# --- 2. Ordering: define __eq__ + __lt__, let total_ordering derive the rest ---
@total_ordering
class Version:
    def __init__(self, major: int, minor: int) -> None:
        self.major, self.minor = major, minor

    def _key(self) -> tuple[int, int]:
        return (self.major, self.minor)

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Version) and other._key() == self._key()

    def __lt__(self, other: Version) -> bool:
        return self._key() < other._key()

    def __hash__(self) -> int:
        return hash(self._key())

    def __repr__(self) -> str:
        return f"Version({self.major}.{self.minor})"


# --- 3. Container + iterator protocol: behaves like a real collection ---
class Ring:
    """A fixed-size ring buffer that is iterable, sized, and indexable."""

    def __init__(self, capacity: int) -> None:
        self._items: list[int] = []
        self._cap = capacity

    def push(self, x: int) -> None:
        self._items.append(x)
        if len(self._items) > self._cap:
            self._items.pop(0)

    def __len__(self) -> int:
        return len(self._items)

    def __getitem__(self, i: int) -> int:
        return self._items[i]

    def __iter__(self) -> Iterator[int]:
        return iter(self._items)

    def __contains__(self, x: object) -> bool:
        return x in self._items


# --- 4. Context manager + callable ---
class Timer:
    def __enter__(self) -> Timer:
        self.entered = True
        return self

    def __exit__(self, exc_type: object, exc: object, tb: object) -> bool:
        self.exited = True
        return False  # False = don't suppress exceptions

    def __call__(self, x: int) -> int:  # instances are callable
        return x * 2


def _demo() -> None:
    a, b = Money(150), Money(150)
    assert a == b and hash(a) == hash(b)  # equal => same hash
    assert repr(a) == "Money(cents=150)" and str(a) == "$1.50"
    assert {a, b} == {a}  # set dedups because they're equal + hash-equal

    assert Version(1, 2) < Version(1, 10)  # total_ordering gave us <, >, <=, >= free
    assert sorted([Version(2, 0), Version(1, 5)]) == [Version(1, 5), Version(2, 0)]

    r = Ring(3)
    for n in (1, 2, 3, 4):
        r.push(n)
    assert list(r) == [2, 3, 4]  # __iter__
    assert len(r) == 3 and r[0] == 2 and 4 in r  # __len__, __getitem__, __contains__

    with Timer() as t:  # __enter__/__exit__
        assert t.entered
    assert t.exited
    assert t(21) == 42  # __call__

    # __slots__ forbids unexpected attributes (catches typos, saves memory):
    try:
        a.dollars = 5  # type: ignore[attr-defined]
        raise AssertionError("should have failed")
    except AttributeError:
        pass

    print("02_data_model: all assertions passed ✅")


if __name__ == "__main__":
    _demo()
