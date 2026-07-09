"""20 — logging: the production alternative to print().

Real services log, they don't print. You need to speak to levels, handlers, formatters,
per-module loggers, and structured logging (the JSON logs your aggregator queries).

MUST KNOW
  - `logging.getLogger(__name__)` — one named logger per module (hierarchical by dots).
  - Levels: DEBUG < INFO < WARNING < ERROR < CRITICAL; the logger's level filters.
  - Handlers decide WHERE logs go (stream/file); Formatters decide the TEXT/JSON shape.
  - Use `%`-style lazy args: `log.info("hi %s", name)` — the string is only built if it
    passes the level filter.
  - `log.exception(...)` inside an `except` logs at ERROR WITH the traceback.
  - Structured logging: pass `extra={...}`; a JSON formatter emits queryable fields.
  - Libraries should NOT configure logging (add a `NullHandler`); the APP configures it.

INTERVIEW QUESTIONS
  - "print vs logging?"  "How do you attach context (request id, user) to logs?" (extra).
  - "Why lazy `%` formatting instead of f-strings in log calls?" (skip formatting when filtered).
"""

from __future__ import annotations

import logging


class CaptureHandler(logging.Handler):
    """A handler that stores records so we can assert on them (real apps use Stream/File)."""

    def __init__(self) -> None:
        super().__init__()
        self.records: list[logging.LogRecord] = []

    def emit(self, record: logging.LogRecord) -> None:
        self.records.append(record)


def _demo() -> None:
    logger = logging.getLogger("demo.service")
    logger.setLevel(logging.INFO)  # DEBUG messages will be filtered out
    logger.propagate = False  # don't bubble to the root logger (avoid duplicate output)
    cap = CaptureHandler()
    logger.addHandler(cap)

    logger.debug("this is filtered")  # below INFO -> dropped
    logger.info("hello %s", "world")  # lazy formatting
    logger.warning("disk at %d%%", 90)
    logger.info("request handled", extra={"request_id": "req-42"})  # structured context
    try:
        _ = 1 / 0
    except ZeroDivisionError:
        logger.exception("computation failed")  # ERROR + traceback attached

    levels = [r.levelname for r in cap.records]
    assert "DEBUG" not in levels  # filtered by level
    assert levels == ["INFO", "WARNING", "INFO", "ERROR"]

    # Lazy args were rendered correctly.
    assert cap.records[0].getMessage() == "hello world"
    assert cap.records[1].getMessage() == "disk at 90%"

    # Structured field rode along via `extra` (a JSON formatter would emit it as a key).
    assert cap.records[2].request_id == "req-42"  # type: ignore[attr-defined]

    # The exception record carries traceback info.
    assert cap.records[3].exc_info is not None

    # Logger names are hierarchical: "demo.service" is a child of "demo".
    assert logger.name == "demo.service"
    assert logging.getLogger("demo.service") is logger  # same name -> same object

    print("20_logging: all assertions passed ✅")


if __name__ == "__main__":
    _demo()
