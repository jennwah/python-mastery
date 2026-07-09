"""10 — Exceptions: design, chaining, groups.

MUST KNOW
  - Build a small exception HIERARCHY so callers can catch broadly or narrowly.
  - `raise NewError(...) from original` preserves the cause (`__cause__`) — don't lose
    the root error when re-wrapping.
  - `try/except/else/finally`: `else` runs only if no exception; `finally` always runs.
  - `ExceptionGroup` + `except*` (3.11+): handle multiple concurrent failures (asyncio
    `TaskGroup` raises these).
  - EAFP ("easier to ask forgiveness than permission") is the Pythonic default over LBYL.

INTERVIEW QUESTIONS
  - "How do you re-raise while keeping the original traceback?" (`raise ... from e`).
  - "Difference between `except` and `except*`?"
  - "When does `finally` run?" (always — even on return/raise inside try).
"""

from __future__ import annotations


# --- 1. A domain exception hierarchy ---
class LLMError(Exception):
    """Base for all model-layer errors."""


class RateLimitError(LLMError):
    def __init__(self, retry_after: float) -> None:
        super().__init__(f"rate limited; retry after {retry_after}s")
        self.retry_after = retry_after


class ContentFilterError(LLMError):
    pass


def call_model(prompt: str) -> str:
    if prompt == "spam":
        raise RateLimitError(retry_after=1.5)
    return f"ok:{prompt}"


# --- 2. Wrapping/chaining: don't swallow the cause ---
class PipelineError(Exception):
    pass


def run_pipeline(prompt: str) -> str:
    try:
        return call_model(prompt)
    except LLMError as e:
        raise PipelineError("pipeline failed") from e  # keeps __cause__ = e


def _demo() -> None:
    # Catch narrowly, read structured info off the exception.
    try:
        call_model("spam")
    except RateLimitError as e:
        assert e.retry_after == 1.5
    # Catch broadly via the base class.
    try:
        call_model("spam")
    except LLMError as e:
        assert isinstance(e, RateLimitError)

    # Chaining preserves the original error.
    try:
        run_pipeline("spam")
    except PipelineError as e:
        assert isinstance(e.__cause__, RateLimitError)

    # else / finally semantics.
    events: list[str] = []
    try:
        events.append("try")
    except Exception:  # noqa: BLE001
        events.append("except")
    else:
        events.append("else")  # runs: no exception
    finally:
        events.append("finally")  # always
    assert events == ["try", "else", "finally"]

    # ExceptionGroup + except*: handle several failures at once (what TaskGroup raises).
    caught: list[str] = []
    try:
        raise ExceptionGroup(
            "batch", [ValueError("bad value"), KeyError("missing"), ValueError("bad2")]
        )
    except* ValueError as eg:
        caught.append(f"values:{len(eg.exceptions)}")
    except* KeyError as eg:
        caught.append(f"keys:{len(eg.exceptions)}")
    assert caught == ["values:2", "keys:1"]

    # EAFP: try the operation; handle failure — instead of pre-checking (LBYL).
    d = {"a": 1}
    try:
        val = d["b"]
    except KeyError:
        val = -1
    assert val == -1

    print("10_errors: all assertions passed ✅")


if __name__ == "__main__":
    _demo()
