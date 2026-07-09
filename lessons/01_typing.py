"""01 — Modern typing (Python 3.12+).

MUST KNOW
  - Builtin generics: `list[int]`, `dict[str, int]` (no more `typing.List`).
  - Unions with `|`; `Optional[X]` is just `X | None`.
  - `Protocol` = structural typing ("duck typing, but statically checked").
  - `TypeVar`/generics, incl. PEP 695 syntax: `def f[T](x: T) -> T`, `class Box[T]`.
  - `Literal`, `TypedDict`, `Final`, `ClassVar`, `Self`, `overload`, `ParamSpec`.
  - Hints are NOT enforced at runtime — mypy/pyright check them. `pydantic` DOES enforce.

INTERVIEW QUESTIONS THIS PREPARES YOU FOR
  - "What's a Protocol and why prefer it over an ABC?"
  - "Difference between `TypedDict` and a dataclass?"
  - "Are type hints enforced at runtime?"
  - "How do you type a decorator that preserves the wrapped signature?" (ParamSpec)
"""

from __future__ import annotations

from collections.abc import Callable, Iterable, Sequence
from typing import (
    Final,
    Literal,
    Protocol,
    Self,
    TypedDict,
    overload,
    runtime_checkable,
)


# --- 1. Builtins as generics; unions with | ---
def total(xs: list[int]) -> int:
    return sum(xs)


def find(xs: Sequence[int], target: int) -> int | None:  # Optional[int]
    return xs.index(target) if target in xs else None


# --- 2. PEP 695 generics (3.12+): no explicit TypeVar needed ---
def first[T](xs: Sequence[T]) -> T:
    return xs[0]


class Box[T]:
    def __init__(self, value: T) -> None:
        self._value = value

    def get(self) -> T:
        return self._value

    def map[R](self, f: Callable[[T], R]) -> Box[R]:
        return Box(f(self._value))


# PEP 695 type alias
type Vector = list[float]


def scale(v: Vector, k: float) -> Vector:
    return [x * k for x in v]


# --- 3. Protocol: structural typing. Anything with .name is a Named — no inheritance. ---
@runtime_checkable
class Named(Protocol):
    name: str


class User:  # note: does NOT inherit Named
    def __init__(self, name: str) -> None:
        self.name = name


def greet(x: Named) -> str:
    return f"hi {x.name}"


# --- 4. Literal + TypedDict: precise strings and dict shapes (LLM message shapes) ---
Role = Literal["system", "user", "assistant"]


class Message(TypedDict):
    role: Role
    content: str


def render(msg: Message) -> str:
    return f"{msg['role']}: {msg['content']}"


# --- 5. overload: same function, different type signatures by argument ---
@overload
def parse(x: int) -> int: ...
@overload
def parse(x: str) -> list[str]: ...
def parse(x: int | str) -> int | list[str]:
    return x * 2 if isinstance(x, int) else x.split()


# --- 6. Self (3.11+): fluent/builder return types ---
class Query:
    def __init__(self) -> None:
        self.parts: list[str] = []

    def where(self, clause: str) -> Self:  # returns the concrete subclass type
        self.parts.append(clause)
        return self


# --- 7. Final / ClassVar: constants and class-level (not per-instance) attrs ---
MAX_TOKENS: Final = 4096


def _demo() -> None:
    assert total([1, 2, 3]) == 6
    assert find([10, 20], 20) == 1 and find([10], 99) is None
    assert first(["a", "b"]) == "a"
    assert Box(3).map(lambda n: n + 1).get() == 4
    assert scale([1.0, 2.0], 2.0) == [2.0, 4.0]

    # Protocol matches by shape, not inheritance. runtime_checkable enables isinstance.
    assert greet(User("Ada")) == "hi Ada"
    assert isinstance(User("Ada"), Named)  # structural check at runtime

    # A TypedDict is a plain dict at runtime (no validation!).
    msg: Message = {"role": "user", "content": "hello"}
    assert render(msg) == "user: hello"
    assert isinstance(msg, dict)

    assert parse(3) == 6
    assert parse("a b c") == ["a", "b", "c"]
    assert Query().where("x=1").where("y=2").parts == ["x=1", "y=2"]
    assert MAX_TOKENS == 4096

    # KEY POINT: hints are not enforced. This "wrong" call runs fine at runtime;
    # only a static checker (mypy) would flag it.
    bad: int = "not an int"  # type: ignore[assignment]
    assert bad == "not an int"

    print("01_typing: all assertions passed ✅")


if __name__ == "__main__":
    _demo()


# Bonus for interviews — typing a decorator with ParamSpec so the wrapper keeps the
# wrapped function's exact signature (see 06_decorators.py for the runtime version):
#
#   from typing import ParamSpec, TypeVar
#   P = ParamSpec("P"); R = TypeVar("R")
#   def timed(fn: Callable[P, R]) -> Callable[P, R]: ...
#
# Also know: `cast(T, x)` (tell the checker to trust you), `assert_type`, `reveal_type`
# (mypy-only), and `NewType("UserId", int)` for distinct-but-int types.
_ = Iterable  # (imported to mention: prefer collections.abc over typing for ABCs)
