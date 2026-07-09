# Python Mastery for AI Engineers

Modern Python 3 (3.12/3.13), targeted at the fluency an **AI engineer** is expected to
have in interviews at top startups. Written for someone with ~5 years of software
experience — it skips "what is a loop" and focuses on **modern idioms, the data model,
typing, async, and the gotchas interviewers probe.**

Every lesson is a **single runnable file**: the lesson is in the comments, the proof is
in the `assert`s. Run one and read it top to bottom.

```bash
uv sync                                   # create venv (numpy + pydantic)
uv run python lessons/01_typing.py        # run any lesson; it prints + asserts
uv run pytest -q                          # the testing lesson is real tests
```

## How to study this

1. Read the **top docstring** of each lesson first — it lists *what you must know* and
   *the interview questions that topic maps to*.
2. Run the file, then read the code. Change things and re-run.
3. Skim [`CHEATSHEET.md`](CHEATSHEET.md) before an interview.
4. Drill [`INTERVIEW.md`](INTERVIEW.md) — rapid-fire Q&A with model answers.

## Curriculum

| # | Lesson | Why it matters for AI engineering |
|---|--------|-----------------------------------|
| 01 | `typing.py` | Type hints are everywhere in AI code (pydantic, function signatures, structured outputs). Interviewers test `Protocol`, `TypeVar`, `Literal`, `TypedDict`. |
| 02 | `data_model.py` | Dunder methods = "Pythonic". `__repr__`, `__eq__/__hash__`, iterator/context-manager protocols, `__slots__`. |
| 03 | `dataclasses.py` | The idiomatic way to model data without boilerplate. `frozen`, `slots`, `kw_only`, vs NamedTuple/TypedDict/pydantic. |
| 04 | `pydantic.py` | The backbone of AI apps: validation, settings, and LLM **structured outputs**. Pydantic v2. |
| 05 | `iterators_generators.py` | Lazy pipelines + `itertools` = memory-efficient data processing (batching tokens/records). |
| 06 | `decorators.py` | Closures, `functools` (`wraps`, `lru_cache`, `cached_property`), retry/timing decorators. |
| 07 | `context_managers.py` | Resource safety (`with`, `ExitStack`, async CMs) — connections, files, spans. |
| 08 | `async_.py` | **The** AI-eng concurrency model: concurrent LLM calls, bounded concurrency, streaming, `TaskGroup`. |
| 09 | `concurrency_gil.py` | The GIL, threads vs processes vs async, `concurrent.futures`, free-threading (3.13). The classic interview question. |
| 10 | `errors.py` | Exception design, chaining (`raise from`), `ExceptionGroup`/`except*`, EAFP. |
| 11 | `pattern_matching.py` | `match/case` — parsing LLM/tool outputs and message unions cleanly. |
| 12 | `collections_stdlib.py` | `Counter`/`defaultdict`/`deque`, `heapq`, `bisect`, `enum` (`StrEnum`), `pathlib`. |
| 13 | `numpy_basics.py` | Vectorization, broadcasting, views vs copies, dtypes — non-negotiable for AI. |
| 14 | `gotchas.py` | `is` vs `==`, mutable defaults, late-binding closures, copy semantics — the trap questions. |
| 15 | `descriptors.py` | The machinery behind `property`/`cached_property`; validate attributes; `__init_subclass__`. |
| 16 | `metaclasses.py` | Classes that build classes — how ABCs/ORMs work, and when NOT to use them. |
| 17 | `memory_gc.py` | Reference counting, cyclic GC, `weakref`, interning, `__slots__` — how memory really works. |
| 18 | `async_advanced.py` | Queues (backpressure), locks, events, cancellation + timeouts. |
| 19 | `regex.py` | `re` for extraction/validation; groups, greedy vs lazy, `sub`. |
| 20 | `logging.py` | Levels, handlers, formatters, structured logging — production instead of `print`. |
| 21 | `design_patterns.py` | Pythonic Strategy/Factory/Registry/DI/Observer — the light versions of GoF. |
| 22 | `packaging.py` | `pyproject.toml`, wheels vs sdist, `__all__`, entry points, uv/ruff/mypy. |
| T | `tests/test_pytest_basics.py` | pytest: fixtures, `parametrize`, `raises`, `AsyncMock`, `tmp_path`. Run `uv run pytest`. |

## The 12 things AI-eng interviewers actually test

1. **The GIL** — what it is, why it makes threads useless for CPU-bound work, and why async/threads *are* right for I/O-bound LLM calls. (`09`)
2. **async/await** — run N LLM calls concurrently with bounded concurrency + retries; don't block the event loop. (`08`)
3. **Generators** — process a large stream without loading it into memory; `yield`, `yield from`, `itertools`. (`05`)
4. **Type hints** — `Protocol` (duck typing, statically checked), `TypeVar`/generics, `Literal`, `TypedDict`, `Optional`. (`01`)
5. **Pydantic** — validate external/LLM data; settings; structured outputs. (`04`)
6. **The data model** — `__eq__`+`__hash__` contract, `__repr__`, context managers, `__slots__`. (`02`)
7. **Decorators & closures** — write a `@retry`/`@timed`; why `functools.wraps`; late-binding trap. (`06`, `14`)
8. **Mutable-default / identity gotchas** — `def f(x=[])`, `is` vs `==`, shallow vs deep copy. (`14`)
9. **Exceptions** — custom hierarchies, `raise from`, cleanup, `ExceptionGroup`. (`10`)
10. **Comprehensions & the walrus** — and when a generator is better. (`05`)
11. **NumPy vectorization** — replace a Python loop with a vectorized op and explain why it's faster. (`13`)
12. **Modern tooling** — `uv`, `ruff`, `mypy`, `pytest`, `pyproject.toml`, `src` layout. (this repo *is* the example)

## Tooling you should be able to speak to

- **uv** — fast dependency + venv manager; `uv sync`, `uv add`, `uv run`, lockfiles.
- **ruff** — linter + formatter (replaces flake8/isort/black), configured in `pyproject.toml`.
- **mypy / pyright** — static type checking; `strict = true`.
- **pytest** — fixtures, parametrization, mocking; the standard.
- **pyproject.toml** — the single config file; `[project]`, dependency groups, tool config.

> Everything here targets **Python 3.12+** (PEP 695 generics, `type` aliases, `batched`,
> `StrEnum`, `TaskGroup`, `except*`). Notes call out the version where it matters.
