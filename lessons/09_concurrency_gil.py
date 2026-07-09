"""09 — The GIL, threads vs processes vs async. The classic interview question.

MUST KNOW
  - The **GIL** (Global Interpreter Lock): in CPython, only ONE thread executes Python
    bytecode at a time. So threads do NOT give parallel speedup for **CPU-bound** work.
  - BUT the GIL is released during **I/O** (network, disk) — so threads DO help
    **I/O-bound** work (many blocking calls in parallel).
  - Decision guide:
      * I/O-bound, high concurrency  -> asyncio (scales to thousands)
      * I/O-bound, simple / blocking libs -> ThreadPoolExecutor
      * CPU-bound (parsing, math, tokenizing) -> ProcessPoolExecutor / multiprocessing
        (separate processes = separate GILs = real parallelism), or NumPy/native code.
  - `concurrent.futures` gives a uniform API: `ThreadPoolExecutor`, `ProcessPoolExecutor`,
    `.submit()` -> Future, `.map()`.
  - Python 3.13 ships an experimental **free-threaded** build (PEP 703, `--disable-gil`)
    — know it exists; the GIL is still the default.

INTERVIEW QUESTIONS
  - "What is the GIL and how does it affect multithreading?"
  - "You need to speed up CPU-bound code — threads or processes? Why?"
  - "Why can threads still help with API calls despite the GIL?"
"""

from __future__ import annotations

import time
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor


def io_task(_: int) -> str:
    time.sleep(0.1)  # simulates a blocking network call; GIL is released during sleep
    return "done"


def cpu_task(n: int) -> int:
    return sum(i * i for i in range(n))  # pure Python compute; GIL-bound


def _demo() -> None:
    # I/O-bound: threads overlap the waiting -> big speedup even WITH the GIL.
    items = list(range(8))

    t0 = time.perf_counter()
    _ = [io_task(i) for i in items]  # sequential: ~0.8s
    seq_time = time.perf_counter() - t0

    t0 = time.perf_counter()
    with ThreadPoolExecutor(max_workers=8) as pool:
        results = list(pool.map(io_task, items))  # concurrent waiting: ~0.1s
    pool_time = time.perf_counter() - t0

    assert results == ["done"] * 8
    assert pool_time < seq_time / 2  # threads help I/O-bound work

    # submit() returns Futures you can await/collect as they complete.
    with ThreadPoolExecutor() as pool:
        futures = [pool.submit(io_task, i) for i in range(3)]
        assert [f.result() for f in futures] == ["done"] * 3

    # CPU-bound: use PROCESSES for real parallelism (each process has its own GIL).
    # (We don't assert timing here — process startup cost makes it noisy for tiny tasks.)
    with ProcessPoolExecutor(max_workers=2) as pool:
        sums = list(pool.map(cpu_task, [10_000, 10_000]))
    assert sums == [cpu_task(10_000)] * 2

    # Takeaway to say out loud:
    #   "Threads for I/O-bound, processes for CPU-bound, asyncio when I need thousands
    #    of concurrent I/O operations. The GIL is why threads don't parallelize compute."
    print("09_concurrency_gil: all assertions passed ✅")


if __name__ == "__main__":
    _demo()
