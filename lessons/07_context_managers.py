"""07 — Context managers: deterministic resource cleanup.

`with` guarantees cleanup runs even if the body raises — files, DB connections, locks,
HTTP clients, tracing spans. AI apps open a lot of resources; leaking them is a common
production bug.

MUST KNOW
  - `with` calls `__enter__` (returns the "as" value) and `__exit__` (always runs).
  - `@contextlib.contextmanager` turns a generator into a context manager (the common way).
  - `__exit__` returning True SUPPRESSES the exception; False (default) re-raises.
  - `ExitStack` manages a dynamic/unknown number of context managers.
  - `suppress`, `closing`; and `async with` for async resources (see 08).

INTERVIEW QUESTIONS
  - "Implement a context manager two ways" (class with __enter__/__exit__; @contextmanager).
  - "How do you open N files/connections and guarantee all get closed?" (ExitStack).
  - "How does `with` interact with exceptions?"
"""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import ExitStack, contextmanager, suppress


# --- 1. The generator-based context manager (most common in real code) ---
@contextmanager
def acquired(resource: str, log: list[str]) -> Iterator[str]:
    log.append(f"open:{resource}")
    try:
        yield resource  # <- becomes the `as` value; body runs here
    finally:
        log.append(f"close:{resource}")  # runs even if body raises


# --- 2. A managed resource with cleanup that can also swallow specific errors ---
class Transaction:
    def __init__(self) -> None:
        self.committed = False
        self.rolled_back = False

    def __enter__(self) -> Transaction:
        return self

    def __exit__(self, exc_type: type[BaseException] | None, exc: object, tb: object) -> bool:
        if exc_type is None:
            self.committed = True
        else:
            self.rolled_back = True
        return False  # don't suppress — let the caller see the error


def _demo() -> None:
    # Cleanup runs on the normal path...
    log: list[str] = []
    with acquired("db", log) as r:
        assert r == "db"
    assert log == ["open:db", "close:db"]

    # ...and on the error path.
    log.clear()
    with suppress(RuntimeError):  # suppress = swallow just this exception type
        with acquired("db", log):
            raise RuntimeError("boom")
    assert log == ["open:db", "close:db"]  # closed despite the raise

    # Transaction commits on success, rolls back on error.
    with Transaction() as tx:
        pass
    assert tx.committed and not tx.rolled_back

    tx2 = Transaction()
    with suppress(ValueError):
        with tx2:
            raise ValueError("bad")
    assert tx2.rolled_back and not tx2.committed

    # ExitStack: manage a DYNAMIC number of context managers; all close in reverse order.
    order: list[str] = []
    with ExitStack() as stack:
        for name in ("a", "b", "c"):
            stack.enter_context(acquired(name, order))
    # opened a,b,c then closed c,b,a
    assert order == ["open:a", "open:b", "open:c", "close:c", "close:b", "close:a"]

    print("07_context_managers: all assertions passed ✅")


if __name__ == "__main__":
    _demo()
