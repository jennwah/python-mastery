# Python Interview Q&A (model answers)

Drill these out loud. Answers are concise on purpose — say the core, then offer detail.
Each links to the lesson that proves it.

### 1. What is the GIL and how does it affect concurrency? (`09`)
CPython's Global Interpreter Lock lets only one thread execute Python bytecode at a
time, so threads give **no speedup for CPU-bound** work. But the GIL is **released
during I/O**, so threads (and asyncio) *do* help I/O-bound work like API calls. For CPU
parallelism use processes (`ProcessPoolExecutor`) or native/NumPy code. 3.13 has an
experimental free-threaded build.

### 2. How do you run 100 LLM calls concurrently, max 10 at a time? (`08`)
`asyncio` with a `Semaphore(10)`: wrap each call in `async with sem`, then run them under
a `TaskGroup`/`gather`. Add retries with backoff, and `return_exceptions=True` (or handle
the `ExceptionGroup`) so one failure doesn't kill the batch. It's I/O-bound, so one thread
handles all of them.

### 3. What happens if you call `time.sleep()` or `requests.get()` in a coroutine?
It **blocks the entire event loop** — every other task stalls until it returns. Use
`await asyncio.sleep()` / an async HTTP client, or push blocking work to
`asyncio.to_thread()`.

### 4. `list` comprehension vs generator expression? (`05`)
List comp is **eager** — builds the whole list, O(n) memory. Genexpr is **lazy** — yields
one item at a time, O(1) memory, and can be infinite. Use a genexpr when streaming/piping
or when you won't need all items at once.

### 5. What's a `Protocol` and why use it over an ABC? (`01`)
Structural typing: any object with the right methods/attributes satisfies it — no
inheritance required (statically-checked duck typing). Prefer it for interfaces you don't
own or don't want to force callers to subclass; ABCs are nominal (must inherit).

### 6. Are type hints enforced at runtime?
No — they're for static checkers (mypy/pyright) and IDEs; the interpreter ignores them.
If you need runtime enforcement, use **pydantic** (or manual validation).

### 7. dataclass vs NamedTuple vs TypedDict vs pydantic? (`03`,`04`)
dataclass = mutable/rich object you control. NamedTuple = immutable record that's also a
tuple. TypedDict = the *shape* of a plain dict (no validation). pydantic = validated model
for data crossing a trust boundary (API/LLM/config).

### 8. Why `field(default_factory=list)` instead of `= []`? (`03`,`14`)
A default value is evaluated **once** at definition time and shared across all instances,
so `= []` gives every instance the *same* list. `default_factory` calls the factory per
instance.

### 9. Explain the `__eq__`/`__hash__` contract. (`02`)
If two objects are equal they **must** have the same hash, because sets/dicts first bucket
by hash then compare with `==`. Defining `__eq__` without `__hash__` makes the object
unhashable. Frozen dataclasses handle both for you.

### 10. `is` vs `==`? (`14`)
`==` compares value (`__eq__`); `is` compares identity (same object). Use `is` only for
singletons: `x is None`, `x is True`. Small ints and some strings are cached, so `is` on
them is unreliable.

### 11. Write a retry decorator. (`06`)
```python
def retry(times, exc=(Exception,)):
    def deco(fn):
        @functools.wraps(fn)
        def wrap(*a, **k):
            for i in range(times):
                try: return fn(*a, **k)
                except exc as e:
                    last = e
            raise last
        return wrap
    return deco
```
Three layers because it takes arguments; `@wraps` preserves the wrapped function's identity.

### 12. Why `functools.wraps`? (`06`)
Without it the wrapper replaces the original's `__name__`, `__doc__`, `__wrapped__`, and
signature — breaking introspection, docs, and debugging.

### 13. `lru_cache`/`cache` — how and when is it dangerous? (`06`)
Memoizes by arguments (which must be **hashable**). Dangers: unbounded memory
(`maxsize=None`), stale results if the underlying data changes, and caching on `self`
keeps instances alive. Great for pure, repeated computations.

### 14. Shallow vs deep copy? (`14`)
Shallow (`copy.copy`, `dict(d)`, `list(l)`) copies the top level but **shares nested
objects**. `copy.deepcopy` recursively copies everything. `[[0]*3]*3` is the classic
shallow-sharing bug (all rows are the same list).

### 15. How do you process a 50GB file without loading it into memory? (`05`)
Iterate lazily: a generator that reads line-by-line (files are iterators), piped through
generator stages (`filter`/`map`/`itertools.islice`), writing as you go. Memory stays O(1).

### 16. `ExceptionGroup` / `except*`? (`10`)
3.11 feature for handling **multiple** simultaneous exceptions (asyncio `TaskGroup` raises
them). `except* ValueError` catches all ValueErrors in the group; you can have several
`except*` clauses.

### 17. `raise X from e` — why? (`10`)
Preserves the original error as `__cause__` so the traceback shows the root cause when you
re-wrap into a domain exception. Losing the cause makes production bugs undebuggable.

### 18. When would you use `match/case` over `if/elif`? (`11`)
When you're **destructuring** structure: matching the shape of a dict/object and binding
its parts in one step — parsing LLM tool calls, message unions, ASTs. Cleaner than nested
`isinstance` + indexing.

### 19. Why is NumPy faster than a Python loop? (`13`)
Data is a contiguous, fixed-dtype buffer; operations run in compiled C loops (often SIMD)
with no per-element Python object boxing or interpreter overhead. 10-100x typical.

### 20. Does NumPy slicing copy? (`13`)
No — basic slicing returns a **view** sharing memory (mutating it mutates the original).
Boolean/fancy indexing returns a **copy**. A frequent source of "why did my array change?"

### 21. How do you test code that calls an LLM/API? (`15`)
Inject the client as a dependency and **mock** it (`Mock`/`AsyncMock`); assert on the
prompt you sent and stub the response. Unit tests never hit the network. Integration tests
(fewer, gated) can exercise the real thing.

### 22. `@contextmanager` — implement one. (`07`)
```python
@contextlib.contextmanager
def span(name):
    start = time.perf_counter()
    try: yield
    finally: log(name, time.perf_counter() - start)
```
`try/yield/finally` guarantees cleanup even if the body raises.

### 23. How does `with` interact with exceptions? (`07`)
`__exit__(exc_type, exc, tb)` always runs; returning `True` **suppresses** the exception,
`False`/`None` lets it propagate. That's how `contextlib.suppress` works.

### 24. `*args`/`**kwargs`, keyword-only, positional-only?
`*args` collects extra positionals into a tuple, `**kwargs` extra keywords into a dict. A
bare `*` forces following params to be keyword-only; `/` forces preceding params to be
positional-only (`def f(a, /, b, *, c)`).

### 25. What modern tooling do you use and why?
`uv` (fast deps/venv + lockfile), `ruff` (lint+format, replaces flake8/isort/black),
`mypy`/pyright (static types, run in CI), `pytest` (fixtures/parametrize/mocking), all
configured in `pyproject.toml`. This signals you write production-grade, maintainable code
— which is most of the AI-engineer job.

### 26. How does `property` work under the hood? (`15`)
It's a **data descriptor** — an object defining `__get__`/`__set__` that lives on the
class. Because it defines `__set__`, it takes precedence over the instance `__dict__`, so
every access/assignment routes through it. You can build your own reusable descriptor
(e.g. a `Positive` validator) the same way, using `__set_name__` to learn its attribute name.

### 27. What's a metaclass and when would you use one? (`16`)
A metaclass builds *classes* (a class is an instance of its metaclass; the default is
`type`). Override `type.__new__` to customize class creation — validate/register a class
as it's defined (ABCs, ORMs use this). In practice I reach for `__init_subclass__` or a
class decorator first; a metaclass only when I must intercept class creation itself.

### 28. How does Python manage memory? What's a weak reference? (`17`)
Reference counting frees objects immediately at zero refs; a separate cyclic collector
(`gc`) reclaims reference cycles. A `weakref` points at an object *without* incrementing
its refcount, so it doesn't keep it alive — ideal for caches (`WeakValueDictionary`) that
must not leak. `__slots__` cuts per-instance memory by dropping `__dict__`.

### 29. How do you cancel an in-flight async task and clean up? (`18`)
`task.cancel()` raises `CancelledError` at the task's next `await`. Catch it to release
resources in a `finally`/`except`, then **re-raise** it (swallowing it breaks cancellation
semantics). For deadlines, `async with asyncio.timeout(s):` cancels the body and raises
`TimeoutError`.

### 30. Greedy vs lazy regex? (`19`)
Quantifiers are greedy by default (`.*` matches as much as possible); add `?` to make them
lazy (`.*?` matches as little as possible). Classic bug: `<(.+)>` on `<a><b>` captures
`a><b`; `<(.+?)>` captures `a`.

### 31. print vs logging — and how do you attach request context? (`20`)
`logging` gives levels, routing (handlers), formatting, and per-module loggers you can
filter/aggregate; `print` gives none of that. Use lazy args (`log.info("x %s", y)`) so
filtered messages cost nothing, `log.exception()` inside `except` for tracebacks, and
`extra={"request_id": ...}` (or a JSON formatter) to attach structured, queryable context.

---

**Closing move if asked "anything else?":** mention you care about *correctness at
boundaries* (pydantic-validate LLM output), *concurrency for throughput* (async + bounded
semaphores), *memory for scale* (generators), and *evals/tests* so changes don't silently
regress — and that you keep all of it typed and linted in CI.
