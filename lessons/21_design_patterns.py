"""21 — Design patterns, the Pythonic way.

Most GoF patterns collapse in Python because functions are first-class and duck typing
is everywhere. Know the pattern, but reach for the light version. (Your agentic-system
portfolio uses Strategy, Factory/Registry, and Dependency Injection — name them!)

MUST KNOW
  - Strategy = pass a function (no Strategy class hierarchy needed).
  - Factory = a function or a dict dispatch table.
  - Registry = a decorator that records implementations by key.
  - Dependency Injection = pass collaborators into the constructor (testability!).
  - Singleton = a module-level instance (modules are singletons in Python).
  - Observer = a list of callbacks.

INTERVIEW QUESTIONS
  - "Implement Strategy / Factory in Python." (functions + dicts, not class trees.)
  - "How do you make a class testable?" (inject dependencies, don't construct them inside).
  - "How do you do a singleton in Python?" (module global, or `__new__`).
"""

from __future__ import annotations

from collections.abc import Callable


# --- 1. Strategy: behavior is just a function you pass in ---
def apply(nums: list[int], strategy: Callable[[list[int]], int]) -> int:
    return strategy(nums)


# --- 2. Factory / dispatch table: map a key to a constructor ---
class OpenAIClient:
    provider = "openai"


class AnthropicClient:
    provider = "anthropic"


_PROVIDERS: dict[str, Callable[[], object]] = {
    "openai": OpenAIClient,
    "anthropic": AnthropicClient,
}


def make_client(name: str) -> object:
    try:
        return _PROVIDERS[name]()
    except KeyError:
        raise ValueError(f"unknown provider: {name}") from None


# --- 3. Registry via decorator (the pattern behind plugin systems) ---
_HANDLERS: dict[str, Callable[..., str]] = {}


def handler(kind: str) -> Callable[[Callable[..., str]], Callable[..., str]]:
    def deco(fn: Callable[..., str]) -> Callable[..., str]:
        _HANDLERS[kind] = fn
        return fn

    return deco


@handler("search")
def _search(q: str) -> str:
    return f"searching {q}"


# --- 4. Dependency Injection: pass the collaborator in (mock it in tests) ---
class Summarizer:
    def __init__(self, llm: Callable[[str], str]) -> None:
        self._llm = llm  # injected, not constructed here

    def run(self, text: str) -> str:
        return self._llm(f"summarize: {text}")


# --- 5. Observer: a list of callbacks ---
class Event:
    def __init__(self) -> None:
        self._subs: list[Callable[[str], None]] = []

    def subscribe(self, fn: Callable[[str], None]) -> None:
        self._subs.append(fn)

    def fire(self, payload: str) -> None:
        for fn in self._subs:
            fn(payload)


def _demo() -> None:
    # Strategy
    assert apply([3, 1, 2], min) == 1
    assert apply([3, 1, 2], lambda xs: sum(xs)) == 6

    # Factory
    assert make_client("openai").provider == "openai"  # type: ignore[attr-defined]
    try:
        make_client("nope")
        raise AssertionError
    except ValueError:
        pass

    # Registry
    assert _HANDLERS["search"]("cats") == "searching cats"

    # Dependency injection: inject a fake "LLM" -> trivially testable, no network.
    s = Summarizer(llm=lambda prompt: f"[{prompt}]")
    assert s.run("hello") == "[summarize: hello]"

    # Observer
    seen: list[str] = []
    e = Event()
    e.subscribe(seen.append)
    e.subscribe(lambda p: seen.append(p.upper()))
    e.fire("ping")
    assert seen == ["ping", "PING"]

    print("21_design_patterns: all assertions passed ✅")


if __name__ == "__main__":
    _demo()
