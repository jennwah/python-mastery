"""14 — The gotchas interviewers love. Know the trap AND the fix.

Every one of these has bitten a real production system. Being able to explain them
signals genuine Python depth.

INTERVIEW QUESTIONS
  - "What's wrong with `def f(x, acc=[])`?"
  - "Why do these lambdas in a loop all print the same value?"
  - "`is` vs `==`?"  "Shallow vs deep copy?"  "`[[0]*3]*3` — what's the bug?"
"""

from __future__ import annotations

import copy
import math


def _demo() -> None:
    # --- 1. is (identity) vs == (equality) ---
    a, b = [1, 2], [1, 2]
    assert a == b  # same value
    assert a is not b  # different objects
    assert a is a  # same object
    # `is` is only for singletons: `x is None`, `x is True`. Never `x is 0` / `x == None`.
    # Int cache side-note: small ints (-5..256) are cached, so identity is unreliable:
    assert int("257") is not int("257")  # equal value, different objects

    # --- 2. Mutable default argument: evaluated ONCE at def time, then shared ---
    def bad(x: int, acc: list[int] = []) -> list[int]:  # noqa: B006 - intentional demo
        acc.append(x)
        return acc

    assert bad(1) == [1]
    assert bad(2) == [1, 2]  # TRAP: same list reused across calls!

    def good(x: int, acc: list[int] | None = None) -> list[int]:  # the fix
        acc = [] if acc is None else acc
        acc.append(x)
        return acc

    assert good(1) == [1] and good(2) == [2]  # fresh each call

    # --- 3. Late-binding closures: the loop variable is captured by REFERENCE ---
    funcs = [lambda: i for i in range(3)]  # noqa: B023
    assert [f() for f in funcs] == [2, 2, 2]  # all see the FINAL i
    fixed = [lambda i=i: i for i in range(3)]  # bind now via default arg
    assert [f() for f in fixed] == [0, 1, 2]

    # --- 4. Shallow vs deep copy: shallow copies share nested objects ---
    original = {"tags": [1, 2]}
    shallow = dict(original)  # or copy.copy(original)
    shallow["tags"].append(3)
    assert original["tags"] == [1, 2, 3]  # TRAP: nested list is shared

    original = {"tags": [1, 2]}
    deep = copy.deepcopy(original)  # independent nested objects
    deep["tags"].append(3)
    assert original["tags"] == [1, 2]  # safe

    # --- 5. list * n copies the REFERENCE, not the object ---
    grid = [[0] * 3] * 3  # 3 references to the SAME inner list
    grid[0][0] = 1
    assert grid == [[1, 0, 0], [1, 0, 0], [1, 0, 0]]  # TRAP: all rows changed
    grid2 = [[0] * 3 for _ in range(3)]  # the fix: build each row fresh
    grid2[0][0] = 1
    assert grid2 == [[1, 0, 0], [0, 0, 0], [0, 0, 0]]

    # --- 6. Floats are not exact ---
    assert 0.1 + 0.2 != 0.3
    assert math.isclose(0.1 + 0.2, 0.3)  # compare floats with isclose (or a tolerance)

    # --- 7. Handy truths ---
    x = 5
    assert 0 < x < 10  # chained comparison (like math)
    # trailing comma makes the tuple; (1) is just an int, not a tuple
    assert type((1,)) is tuple and type((1)) is int  # noqa: UP003, UP034
    assert bool([]) is False and bool([0]) is True  # empty containers are falsy
    assert ([] or "default") == "default"  # `or` returns first truthy operand

    print("14_gotchas: all assertions passed ✅")


if __name__ == "__main__":
    _demo()
