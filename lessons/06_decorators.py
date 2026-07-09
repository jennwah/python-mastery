"""06 — Closures, decorators, and functools.

Decorators wrap behavior around functions (timing, retry, caching, auth) — everywhere
in AI code. Built on closures.

MUST KNOW
  - A closure captures variables from its enclosing scope.
  - A decorator is a function that takes a function and returns a replacement.
  - ALWAYS `@functools.wraps(fn)` the wrapper (preserves name/docstring/signature).
  - Decorators WITH arguments = one more layer (a decorator factory).
  - `functools`: `lru_cache`/`cache`, `cached_property`, `partial`, `reduce`, `singledispatch`.

INTERVIEW QUESTIONS
  - "Write a retry decorator."  "Write a decorator that takes arguments."
  - "Why `functools.wraps`?"  "What's `lru_cache` and when is it dangerous?"
    (danger: caches on args -> unbounded memory / stale results / must be hashable args).
"""

from __future__ import annotations

import functools
import time
from collections.abc import Callable
from typing import ParamSpec, TypeVar

P = ParamSpec("P")  # captures the wrapped function's parameters
R = TypeVar("R")


# --- 1. A plain decorator (note wraps + ParamSpec so the signature is preserved) ---
def timed(fn: Callable[P, R]) -> Callable[P, R]:  # noqa: UP047  (ParamSpec on purpose)
    @functools.wraps(fn)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        start = time.perf_counter()
        try:
            return fn(*args, **kwargs)
        finally:
            wrapper.calls += 1  # type: ignore[attr-defined]
            _ = time.perf_counter() - start

    wrapper.calls = 0  # type: ignore[attr-defined]
    return wrapper


# --- 2. A decorator WITH arguments = a factory returning a decorator ---
def retry(  # noqa: UP047
    times: int, exceptions: tuple[type[Exception], ...] = (Exception,)
) -> Callable[[Callable[P, R]], Callable[P, R]]:
    def decorator(fn: Callable[P, R]) -> Callable[P, R]:
        @functools.wraps(fn)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            last: Exception | None = None
            for _ in range(times):
                try:
                    return fn(*args, **kwargs)
                except exceptions as e:
                    last = e
            raise last  # type: ignore[misc]

        return wrapper

    return decorator


# --- 3. functools.cache: memoize pure functions (here: Fibonacci) ---
@functools.cache  # like lru_cache(maxsize=None)
def fib(n: int) -> int:
    return n if n < 2 else fib(n - 1) + fib(n - 2)


# --- 4. cached_property: compute once per instance, then store ---
class Embedding:
    def __init__(self, vec: list[float]) -> None:
        self.vec = vec
        self.norm_calls = 0

    @functools.cached_property
    def norm(self) -> float:
        self.norm_calls += 1
        return sum(x * x for x in self.vec) ** 0.5


# --- 5. singledispatch: function overloading by argument TYPE ---
@functools.singledispatch
def describe(x: object) -> str:
    return f"object:{x}"


@describe.register
def _(x: int) -> str:
    return f"int:{x}"


@describe.register
def _(x: list) -> str:
    return f"list of {len(x)}"


def _demo() -> None:
    @timed
    def add(a: int, b: int) -> int:
        """add two ints"""
        return a + b

    assert add(2, 3) == 5
    assert add.__name__ == "add" and add.__doc__ == "add two ints"  # wraps preserved these
    assert add.calls == 1  # type: ignore[attr-defined]

    calls = {"n": 0}

    @retry(times=3, exceptions=(ValueError,))
    def flaky() -> str:
        calls["n"] += 1
        if calls["n"] < 3:
            raise ValueError("nope")
        return "ok"

    assert flaky() == "ok" and calls["n"] == 3  # retried until success

    assert fib(30) == 832040  # fast thanks to @cache (no exponential blowup)

    e = Embedding([3.0, 4.0])
    assert e.norm == 5.0 and e.norm == 5.0  # second access is cached
    assert e.norm_calls == 1  # computed only once

    assert describe(5) == "int:5"
    assert describe([1, 2]) == "list of 2"
    assert describe("x") == "object:x"

    # partial: pre-bind arguments to make a specialized callable.
    to_base2 = functools.partial(int, base=2)
    assert to_base2("1010") == 10

    print("06_decorators: all assertions passed ✅")


if __name__ == "__main__":
    _demo()
