"""08 — asyncio: the concurrency model AI engineers live in.

LLM/API calls are I/O-bound (you're waiting on the network). asyncio lets a single
thread juggle hundreds of in-flight requests. THE core skill: fan out N model calls
concurrently, with bounded concurrency (rate limits) and retries.

MUST KNOW
  - `async def` makes a coroutine; `await` yields control while waiting.
  - `asyncio.run(main())` starts the event loop.
  - `asyncio.gather(*coros)` runs them concurrently; `TaskGroup` (3.11+) is the modern,
    exception-safe way.
  - `asyncio.Semaphore(n)` bounds concurrency (respect provider rate limits).
  - Never block the loop: use `await asyncio.sleep()`, and `asyncio.to_thread()` for
    unavoidably-blocking code.
  - `async for` (async generators — token streaming), `async with` (async resources).

INTERVIEW QUESTIONS
  - "How do you make 100 API calls concurrently but at most 10 at a time?"
  - "What happens if you call a blocking function (time.sleep, requests) in a coroutine?"
    (it freezes the whole event loop — nothing else progresses).
  - "gather vs TaskGroup?"  "asyncio vs threads for I/O-bound work?"
"""

from __future__ import annotations

import asyncio
import time
from collections.abc import AsyncIterator


# --- 1. A fake async "LLM call": I/O-bound work simulated with asyncio.sleep ---
async def fake_llm(prompt: str, delay: float = 0.1) -> str:
    await asyncio.sleep(delay)  # non-blocking: the loop runs other tasks meanwhile
    return f"answer:{prompt}"


# --- 2. Bounded concurrency: at most `limit` calls in flight (rate limiting) ---
async def fan_out(prompts: list[str], limit: int) -> list[str]:
    sem = asyncio.Semaphore(limit)

    async def one(p: str) -> str:
        async with sem:  # acquire a slot; releases on exit
            return await fake_llm(p)

    # TaskGroup (3.11+): if any task raises, the others are cancelled and the error
    # propagates as an ExceptionGroup. Safer than bare gather.
    async with asyncio.TaskGroup() as tg:
        tasks = [tg.create_task(one(p)) for p in prompts]
    return [t.result() for t in tasks]


# --- 3. Async generator: stream tokens as they arrive (`async for`) ---
async def stream_tokens(text: str) -> AsyncIterator[str]:
    for tok in text.split():
        await asyncio.sleep(0)  # yield control between chunks
        yield tok


# --- 4. Offload blocking/CPU work so it doesn't freeze the loop ---
def blocking_hash(s: str) -> int:
    return sum(ord(c) for c in s)  # pretend this is slow/CPU-bound


async def _demo() -> None:
    # Concurrency proof: 5 calls x 0.1s run in ~0.1s concurrently, not ~0.5s.
    prompts = [f"q{i}" for i in range(5)]

    t0 = time.perf_counter()
    concurrent = await asyncio.gather(*(fake_llm(p) for p in prompts))
    concurrent_time = time.perf_counter() - t0

    t0 = time.perf_counter()
    sequential = [await fake_llm(p) for p in prompts]  # awaits one at a time
    sequential_time = time.perf_counter() - t0

    assert concurrent == sequential == [f"answer:q{i}" for i in range(5)]
    assert concurrent_time < sequential_time / 2  # dramatically faster

    # Bounded concurrency still returns all results, but never exceeds `limit` in flight.
    results = await fan_out(prompts, limit=2)
    assert results == [f"answer:q{i}" for i in range(5)]

    # Stream tokens with async for.
    toks = [t async for t in stream_tokens("hello there world")]
    assert toks == ["hello", "there", "world"]

    # to_thread: run blocking code without stalling the loop.
    h = await asyncio.to_thread(blocking_hash, "abc")
    assert h == ord("a") + ord("b") + ord("c")

    # gather(..., return_exceptions=True): collect failures instead of raising.
    async def maybe_fail(x: int) -> int:
        if x == 2:
            raise ValueError("two")
        return x

    mixed = await asyncio.gather(*(maybe_fail(i) for i in range(3)), return_exceptions=True)
    assert mixed[0] == 0 and isinstance(mixed[2], ValueError)

    print("08_async_: all assertions passed ✅")


if __name__ == "__main__":
    asyncio.run(_demo())
