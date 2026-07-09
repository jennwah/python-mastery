# Python Cheat Sheet (night-before-interview)

Dense quick-reference. Each block maps to a lesson file for the runnable version.

## Typing (`01`)
- `list[int]`, `dict[str, int]`, `X | None` (not `Optional`/`List` anymore).
- `Protocol` = structural typing (matches by shape, no inheritance). `@runtime_checkable` for `isinstance`.
- Generics (3.12+): `def f[T](x: T) -> T`, `class Box[T]:`, `type Vec = list[float]`.
- `Literal["a","b"]`, `TypedDict` (dict shape, **no runtime validation**), `Final`, `ClassVar`, `Self`.
- `@overload` for signature variants. `ParamSpec` to type decorators.
- **Hints aren't enforced at runtime** — mypy/pyright check; pydantic enforces.

## Data model / dunders (`02`)
- `__repr__` (dev, unambiguous) vs `__str__` (user).
- `__eq__` ⇒ define `__hash__` too; **equal objects must hash equal** (dict/set correctness).
- Container: `__len__`, `__getitem__`, `__iter__`, `__contains__`.
- Context mgr: `__enter__`/`__exit__` (`__exit__` returns `True` to suppress the exception).
- `__call__` (callable instances), `__slots__` (no `__dict__`: less memory, locks attrs).

## dataclasses (`03`)
- `@dataclass`; mutable default ⇒ `field(default_factory=list)` **never `= []`**.
- `frozen=True` (immutable+hashable), `slots=True`, `kw_only=True`, `order=True`, `__post_init__`.
- `dataclasses.replace(obj, x=1)` = immutable copy-with-change.
- dataclass (rich/mutable) · NamedTuple (immutable tuple record) · TypedDict (dict shape) · pydantic (validated).

## pydantic v2 (`04`)
- `BaseModel` validates + coerces on construction; raises `ValidationError`.
- `Field(ge=, le=, gt=, default=, alias=)`, `@field_validator`, `@model_validator(mode="after")`.
- `model_dump()`, `model_dump_json()`, `model_validate()`, `model_validate_json()`.
- Discriminated union: `Field(discriminator="kind")`. `BaseSettings` for env config.
- Use it at trust boundaries: API input, config, **LLM structured outputs**.

## Generators / itertools (`05`)
- `yield` = lazy iterator (O(1) memory). Genexpr `(x for x ...)` lazy vs list comp eager.
- `yield from sub` delegates. Generators are **single-use**.
- `itertools`: `islice`, `chain`, `groupby` (consecutive!), `accumulate`, `batched` (3.12), `tee`, `product`.

## Decorators / functools (`06`)
- Decorator = fn→fn; **always `@functools.wraps(fn)`** on the wrapper.
- With args = a factory (3 nested levels). Type with `ParamSpec`/`TypeVar`.
- `functools`: `cache`/`lru_cache` (memoize; args must be hashable, watch memory),
  `cached_property`, `partial`, `reduce`, `singledispatch` (dispatch by type).

## Context managers (`07`)
- `@contextlib.contextmanager` + `try/yield/finally` = the common form.
- `ExitStack` for a dynamic number of CMs; `suppress(Err)`, `closing()`.
- `async with` for async resources.

## async (`08`)
- `async def`/`await`; `asyncio.run(main())`.
- Concurrency: `asyncio.gather(*coros)` or `async with asyncio.TaskGroup()` (3.11, safer).
- Bound concurrency: `asyncio.Semaphore(n)` + `async with sem`.
- `asyncio.to_thread(fn)` for blocking code; `async for` (async generators); `asyncio.timeout()`.
- **Never** call blocking code (`time.sleep`, `requests`) in a coroutine — it freezes the loop.

## GIL / concurrency (`09`)
- GIL ⇒ one thread runs Python bytecode at a time. Threads DON'T parallelize CPU work.
- I/O-bound ⇒ threads/async (GIL released during I/O). CPU-bound ⇒ processes (`ProcessPoolExecutor`).
- `concurrent.futures`: `ThreadPoolExecutor`/`ProcessPoolExecutor`, `.submit()`→Future, `.map()`.
- 3.13 has an experimental free-threaded (no-GIL) build.

## Errors (`10`)
- Custom hierarchy (base + specifics). `raise New() from e` keeps `__cause__`.
- `try/except/else/finally`: `else`=no-exception, `finally`=always.
- `ExceptionGroup` + `except*` (3.11; asyncio TaskGroup raises these). EAFP > LBYL.

## match/case (`11`)
- Patterns: literal, capture (`case x`), `_`, sequence `[a, *rest]`, mapping `{"k": v}`,
  class `Point(x=0)`, OR `1 | 2`, guard `case x if ...`. Great for tool-call/message parsing.

## stdlib (`12`)
- `Counter` (`.most_common`), `defaultdict(list)`, `deque(maxlen=N)` (O(1) ends).
- `heapq.nlargest/nsmallest`, `heappush/heappop` (top-k, priority queue).
- `bisect.insort/bisect_left` (sorted lists). `StrEnum`. `pathlib.Path` (`/`, `.stem`, `.suffix`).

## NumPy (`13`)
- Vectorize (C loops, contiguous memory) instead of Python loops. Broadcasting aligns shapes.
- Slicing ⇒ **view** (mutates original); boolean/fancy indexing ⇒ **copy**.
- `axis=`, `argmax`, `@`/`dot`, `np.linalg.norm`, stable softmax = `exp(x-max)/sum`.

## Gotchas (`14`)
- `is` (identity) vs `==` (value); `is` only for `None`/`True`/`False`.
- Mutable default arg (`def f(x=[])`) → use `None` sentinel.
- Late-binding closures in loops → bind with `lambda i=i:`.
- Shallow copy shares nested objects → `copy.deepcopy`. `[[0]*3]*3` shares rows.
- `0.1+0.2 != 0.3` → `math.isclose`.

## Descriptors / metaclasses (`15`,`16`)
- Descriptor = `__get__`/`__set__`/`__set_name__`. **Data** descriptor (has `__set__`) beats the instance dict; **non-data** (only `__get__`) is shadowed by it. `property` is a data descriptor.
- `__init_subclass__(cls)` runs per subclass — registration/validation without a metaclass.
- Metaclass = a class whose instances are classes (default = `type`). `type(name, bases, ns)` builds a class. Prefer `__init_subclass__`/decorators unless you must intercept class creation.

## Memory / GC (`17`)
- `=` binds a name (no copy). Refcount frees at 0; the cyclic GC (`gc`) breaks reference cycles.
- `weakref` / `WeakValueDictionary` = references that don't keep objects alive (leak-free caches).
- `__slots__` drops the per-instance `__dict__`; `sys.intern` shares identical strings.

## Advanced async (`18`)
- `asyncio.Queue(maxsize=)` (backpressure); `Lock` (yes—coroutines interleave at every `await`); `Event`.
- Cancel: `task.cancel()` → `CancelledError` inside; clean up in `finally`, **re-raise**. `async with asyncio.timeout(s)` (3.11+) → `TimeoutError`. `as_completed` = fastest-first.

## Regex (`19`)
- `match` (start) vs `search` (anywhere) vs `fullmatch` (whole). `findall`/`finditer`/`sub`/`split`.
- Named groups `(?P<n>…)`; greedy `.*` vs lazy `.*?`; `re.compile` + flags (`IGNORECASE`/`MULTILINE`/`DOTALL`/`VERBOSE`).

## Logging (`20`)
- `logging.getLogger(__name__)`; DEBUG<INFO<WARNING<ERROR<CRITICAL. Handlers = where, Formatters = shape.
- Lazy args `log.info("hi %s", x)`; `log.exception()` in `except` = ERROR+traceback; context via `extra={...}`. Libraries add `NullHandler`; the app configures.

## Design patterns (`21`)
- Strategy = pass a function. Factory = dict dispatch. Registry = decorator. DI = inject collaborators (testable). Singleton = module global. Observer = list of callbacks.

## Tooling
- `uv sync` / `uv add pkg` / `uv run cmd` — venv + deps + lockfile.
- `ruff check` / `ruff format` — lint + format (replaces flake8/isort/black).
- `mypy --strict` / pyright — static types.
- `pytest -q` — fixtures, `parametrize`, `raises`, `tmp_path`, `monkeypatch`, `Mock`/`AsyncMock`.
- `pyproject.toml` = single source: `[project]`, deps, tool config.
