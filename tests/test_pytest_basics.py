"""15 — pytest: the testing skills every AI engineer is expected to have.

Run:  uv run pytest -q

MUST KNOW
  - Plain `assert` (pytest rewrites it to show rich diffs — no `self.assertEqual`).
  - `@pytest.fixture` for setup/teardown (yield = teardown after the test).
  - `@pytest.mark.parametrize` to run one test over many inputs.
  - `pytest.raises` to assert exceptions.
  - Built-in fixtures: `tmp_path` (temp dir), `monkeypatch` (patch env/attrs).
  - Mocking: `unittest.mock.Mock`/`patch`/`AsyncMock` — isolate the unit under test
    (never hit a real LLM/DB in a unit test).

INTERVIEW QUESTIONS
  - "How do you test code that calls an external API/LLM?" (mock the client / patch it).
  - "fixtures vs setup methods?"  "How do you test that a function raises?"
"""

from __future__ import annotations

import asyncio
import os
from pathlib import Path
from unittest.mock import AsyncMock, Mock

import pytest


# --- code under test (would normally be imported from your package) ---
def normalize(name: str) -> str:
    return name.strip().lower()


def divide(a: int, b: int) -> float:
    if b == 0:
        raise ZeroDivisionError("no dividing by zero")
    return a / b


class Summarizer:
    """Depends on an injected 'client' — so we can mock it in tests."""

    def __init__(self, client: object) -> None:
        self.client = client

    def summarize(self, text: str) -> str:
        return self.client.complete(f"summarize: {text}")  # type: ignore[attr-defined]


# --- fixture: setup + teardown via yield ---
@pytest.fixture
def sample_agent() -> object:
    created = {"name": "triage", "open": True}
    yield created  # the test runs here
    created["open"] = False  # teardown (runs even if the test fails)


def test_uses_fixture(sample_agent: dict) -> None:
    assert sample_agent["name"] == "triage"


# --- parametrize: one test, many cases ---
@pytest.mark.parametrize(
    ("raw", "expected"),
    [("  Ada ", "ada"), ("BOB", "bob"), ("cara", "cara")],
)
def test_normalize(raw: str, expected: str) -> None:
    assert normalize(raw) == expected


# --- asserting exceptions ---
def test_divide_raises() -> None:
    with pytest.raises(ZeroDivisionError, match="dividing by zero"):
        divide(1, 0)


# --- monkeypatch: safely set env / patch attributes for one test ---
def test_reads_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("MODEL", "gpt-4o")
    assert os.environ["MODEL"] == "gpt-4o"
    # auto-reverted after the test — no leakage.


# --- tmp_path: a per-test temporary directory ---
def test_writes_file(tmp_path: Path) -> None:
    f = tmp_path / "out.txt"
    f.write_text("hello")
    assert f.read_text() == "hello"


# --- mocking: isolate the unit; never call the real LLM in a unit test ---
def test_summarizer_mocks_client() -> None:
    client = Mock()
    client.complete.return_value = "a short summary"
    result = Summarizer(client).summarize("long text")
    assert result == "a short summary"
    client.complete.assert_called_once_with("summarize: long text")  # verify the call


# --- AsyncMock: mocking async calls (run the coroutine with asyncio.run) ---
def test_async_client() -> None:
    client = AsyncMock()
    client.acomplete.return_value = "async summary"

    async def run() -> str:
        return await client.acomplete("hi")

    assert asyncio.run(run()) == "async summary"
    client.acomplete.assert_awaited_once_with("hi")


# --- marks: skip / xfail ---
@pytest.mark.skip(reason="demoing the skip marker")
def test_skipped() -> None:
    raise AssertionError("never runs")
