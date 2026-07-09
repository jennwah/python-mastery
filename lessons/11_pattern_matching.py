"""11 — Structural pattern matching (`match`/`case`, 3.10+).

Great for parsing semi-structured data: LLM tool calls, message unions, JSON-ish
payloads, ASTs. It matches STRUCTURE and binds variables in one step.

MUST KNOW
  - Patterns: literal, capture (`case x`), wildcard (`case _`), sequence (`[a, *rest]`),
    mapping (`{"key": v}`), class (`Point(x=0)`), OR (`case 1 | 2`), guards (`case x if ...`).
  - Class patterns use `__match_args__` (dataclasses provide it) for positional matching.
  - `case _` is the default/catch-all. A name like `case x` ALWAYS matches and binds.

INTERVIEW QUESTIONS
  - "When would you use match/case over if/elif?" (destructuring + shape matching).
  - "What's the difference between `case x` and `case 'x'`?" (capture-all vs literal).
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Point:
    x: int
    y: int


# --- 1. Match on the SHAPE of a dict (e.g., a decoded tool call) ---
def handle_tool(call: dict) -> str:
    match call:
        case {"kind": "search", "query": str(q)}:  # binds q, and checks it's a str
            return f"search:{q}"
        case {"kind": "calc", "expr": expr}:
            return f"calc:{expr}"
        case {"kind": kind}:
            return f"unknown:{kind}"
        case _:
            return "malformed"


# --- 2. Sequence patterns + guards ---
def classify(seq: list[int]) -> str:
    match seq:
        case []:
            return "empty"
        case [x]:
            return f"one:{x}"
        case [x, y] if x == y:  # guard
            return "pair-equal"
        case [first, *rest]:  # capture head + tail
            return f"head:{first} tail:{len(rest)}"


# --- 3. Class patterns (positional via __match_args__, keyword by name) + OR ---
def describe(p: Point) -> str:
    match p:
        case Point(0, 0):
            return "origin"
        case Point(x=0, y=y):  # keyword pattern, binds y
            return f"on-y-axis:{y}"
        case Point(x, 0):  # positional pattern, binds x
            return f"on-x-axis:{x}"
        case Point():
            return "somewhere"


def http_meaning(code: int) -> str:
    match code:
        case 200 | 201 | 204:  # OR-pattern
            return "ok"
        case 400 | 401 | 403 | 404:
            return "client-error"
        case c if c >= 500:  # guard
            return "server-error"
        case _:
            return "other"


def _demo() -> None:
    assert handle_tool({"kind": "search", "query": "cats"}) == "search:cats"
    assert handle_tool({"kind": "calc", "expr": "2+2"}) == "calc:2+2"
    assert handle_tool({"kind": "email"}) == "unknown:email"
    assert handle_tool({"bad": 1}) == "malformed"

    assert classify([]) == "empty"
    assert classify([7]) == "one:7"
    assert classify([3, 3]) == "pair-equal"
    assert classify([1, 2, 3, 4]) == "head:1 tail:3"

    assert describe(Point(0, 0)) == "origin"
    assert describe(Point(0, 5)) == "on-y-axis:5"
    assert describe(Point(9, 0)) == "on-x-axis:9"
    assert describe(Point(1, 1)) == "somewhere"

    assert http_meaning(204) == "ok"
    assert http_meaning(404) == "client-error"
    assert http_meaning(503) == "server-error"
    assert http_meaning(301) == "other"

    print("11_pattern_matching: all assertions passed ✅")


if __name__ == "__main__":
    _demo()
