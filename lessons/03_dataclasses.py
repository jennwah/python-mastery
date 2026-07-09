"""03 — dataclasses: the idiomatic way to model data.

MUST KNOW
  - `@dataclass` auto-generates `__init__`, `__repr__`, `__eq__`.
  - Mutable defaults MUST use `field(default_factory=list)` — never `= []`.
  - `frozen=True` → immutable + hashable (great dict/set keys, thread-safety).
  - `slots=True` (3.10+) → memory savings + no accidental attributes.
  - `kw_only=True`, `order=True`, `__post_init__`, `field(compare=/repr=/init=)`.
  - `dataclasses.replace()` for immutable "copy with changes".

WHEN TO USE WHAT
  - dataclass:  mutable/rich data objects you control.
  - NamedTuple: lightweight immutable records that are also tuples.
  - TypedDict:  the *shape* of a plain dict (e.g. JSON), zero runtime validation.
  - pydantic:   data crossing a trust boundary (API/LLM input) — validated. (see 04)

INTERVIEW QUESTIONS
  - "Why `default_factory` instead of `field = []`?" (shared mutable default trap.)
  - "dataclass vs NamedTuple vs pydantic — when each?"
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from typing import NamedTuple


# --- 1. Basics + the mutable-default fix ---
@dataclass
class Agent:
    name: str
    model: str = "gpt-4o"
    tools: list[str] = field(default_factory=list)  # NOT `= []`
    _id: int = field(default=0, repr=False, compare=False)  # hidden from repr & ==

    def __post_init__(self) -> None:  # runs after __init__; validate/derive here
        if not self.name:
            raise ValueError("name required")


# --- 2. frozen + slots: immutable, hashable, memory-light value object ---
@dataclass(frozen=True, slots=True)
class Point:
    x: float
    y: float


# --- 3. kw_only + order ---
@dataclass(kw_only=True, order=True)
class Task:
    priority: int
    name: str = field(compare=False)  # order by priority only


# --- 4. NamedTuple: immutable record that is also a tuple ---
class RGB(NamedTuple):
    r: int
    g: int
    b: int


def _demo() -> None:
    a = Agent("triage")
    assert a.model == "gpt-4o" and a.tools == []
    assert repr(a) == "Agent(name='triage', model='gpt-4o', tools=[])"  # _id hidden

    # THE trap: each Agent gets its OWN list because of default_factory.
    a.tools.append("search")
    assert Agent("other").tools == []  # not polluted — this is why default_factory

    p = Point(1.0, 2.0)
    assert p == Point(1.0, 2.0)
    assert hash(p)  # frozen => hashable => usable as dict/set key
    assert {p: "origin-ish"}[Point(1.0, 2.0)] == "origin-ish"
    try:
        p.x = 9.0  # type: ignore[misc]
        raise AssertionError("frozen should block assignment")
    except AttributeError:
        pass

    # replace() = immutable update
    p2 = replace(p, x=5.0)
    assert p2 == Point(5.0, 2.0) and p == Point(1.0, 2.0)

    # kw_only forces keyword args; order sorts by `priority` (name excluded from compare)
    tasks = [Task(priority=2, name="b"), Task(priority=1, name="a")]
    assert sorted(tasks)[0].priority == 1

    # NamedTuple: tuple + named access
    c = RGB(255, 128, 0)
    assert c.r == 255 and c[0] == 255 and tuple(c) == (255, 128, 0)
    red, *_ = c  # unpacks like a tuple

    print("03_dataclasses: all assertions passed ✅")


if __name__ == "__main__":
    _demo()
