"""18 — Advanced asyncio: queues, locks, events, cancellation, timeouts.

Beyond `gather` (08), real async systems coordinate work: bounded queues for
backpressure, locks for shared state, events for signaling, and correct cancellation +
timeouts so a stuck call doesn't hang the whole pipeline.

MUST KNOW
  - `asyncio.Queue(maxsize=)` — producer/consumer with backpressure (put() blocks when full).
  - `asyncio.Lock` — mutual exclusion across coroutines (yes, you still need it: a coroutine
    can be interrupted at every `await`).
  - `asyncio.Event` — one coroutine signals, others `await event.wait()`.
  - Cancellation: `task.cancel()` raises `CancelledError` inside the task; clean up in
    `finally`/`except` and re-raise. `asyncio.timeout()` (3.11+) cancels on deadline.
  - `asyncio.as_completed()` — consume results in completion order.

INTERVIEW QUESTIONS
  - "How do you cancel an in-flight task and clean up?"
  - "Why would you need a lock in single-threaded async code?" (interleaving at `await`).
  - "How do you apply a timeout to an async call?"
"""

from __future__ import annotations

import asyncio


async def producer(q: asyncio.Queue[int | None], n: int) -> None:
    for i in range(n):
        await q.put(i)  # blocks if the queue is full -> natural backpressure
    await q.put(None)  # sentinel = "done"


async def consumer(q: asyncio.Queue[int | None], out: list[int]) -> None:
    while True:
        item = await q.get()
        try:
            if item is None:
                return
            out.append(item)
        finally:
            q.task_done()


async def _demo() -> None:
    # 1. Queue: bounded producer/consumer.
    q: asyncio.Queue[int | None] = asyncio.Queue(maxsize=2)
    out: list[int] = []
    await asyncio.gather(producer(q, 5), consumer(q, out))
    assert out == [0, 1, 2, 3, 4]

    # 2. Lock: protect a read-modify-write across `await` points.
    counter = {"n": 0}
    lock = asyncio.Lock()

    async def inc() -> None:
        async with lock:
            v = counter["n"]
            await asyncio.sleep(0)  # yields control — without the lock this would race
            counter["n"] = v + 1

    await asyncio.gather(*(inc() for _ in range(20)))
    assert counter["n"] == 20  # correct because the lock serialized the updates

    # 3. Event: signal waiters.
    event = asyncio.Event()
    log: list[str] = []

    async def waiter() -> None:
        await event.wait()
        log.append("go")

    async def setter() -> None:
        await asyncio.sleep(0.01)
        event.set()

    await asyncio.gather(waiter(), waiter(), setter())
    assert log == ["go", "go"]

    # 4. Cancellation with cleanup.
    state = {"cleaned": False}

    async def long_running() -> None:
        try:
            await asyncio.sleep(10)
        except asyncio.CancelledError:
            state["cleaned"] = True  # release resources here
            raise  # ALWAYS re-raise CancelledError

    task = asyncio.create_task(long_running())
    await asyncio.sleep(0.01)  # let it start
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass
    assert task.cancelled() and state["cleaned"]

    # 5. Timeout (3.11+): cancels the body if it exceeds the deadline.
    try:
        async with asyncio.timeout(0.01):
            await asyncio.sleep(1)
        raise AssertionError("should have timed out")
    except TimeoutError:
        pass

    # 6. as_completed: results arrive fastest-first, not submission order.
    async def work(label: str, delay: float) -> str:
        await asyncio.sleep(delay)
        return label

    order: list[str] = []
    for fut in asyncio.as_completed([work("slow", 0.03), work("fast", 0.01)]):
        order.append(await fut)
    assert order == ["fast", "slow"]

    print("18_async_advanced: all assertions passed ✅")


if __name__ == "__main__":
    asyncio.run(_demo())
