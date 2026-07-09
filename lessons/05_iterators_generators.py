"""05 — Iterators, generators, and itertools: lazy, memory-efficient pipelines.

This is how you process a 10GB file or a token stream without loading it into RAM.

MUST KNOW
  - Iterator protocol: `__iter__` returns an iterator; `__next__` yields items, raises
    `StopIteration` when done. `for` is sugar over this.
  - Generators (`yield`) are lazy iterators — they compute one item at a time.
  - Generator *expressions* `(x for x in ...)` — like a list comp but lazy.
  - `yield from` delegates to a sub-iterator.
  - `itertools` = the batteries: `islice`, `chain`, `groupby`, `accumulate`, `batched`.

INTERVIEW QUESTIONS
  - "Difference between a list comprehension and a generator expression?" (eager vs lazy;
    memory: O(n) vs O(1)).
  - "How would you process a huge file/stream without loading it all?" (generators).
  - "What does `yield` do?"  "What's `StopIteration`?"
"""

from __future__ import annotations

import sys
from collections.abc import Iterable, Iterator
from itertools import accumulate, batched, chain, groupby, islice


# --- 1. A generator is a lazy iterator ---
def countdown(n: int) -> Iterator[int]:
    while n > 0:
        yield n  # suspends here; resumes on next()
        n -= 1


# --- 2. Pipelines: chain generators; each stage is lazy (nothing runs until consumed) ---
def read_numbers(lines: Iterable[str]) -> Iterator[int]:
    for line in lines:
        line = line.strip()
        if line:
            yield int(line)


def running_totals(nums: Iterable[int]) -> Iterator[int]:
    yield from accumulate(nums)  # yield from delegates to another iterator


# --- 3. Batching a stream (e.g., embed records in chunks) — 3.12+ `batched` ---
def batch_stream[T](items: Iterable[T], size: int) -> Iterator[tuple[T, ...]]:
    yield from batched(items, size)


def _demo() -> None:
    assert list(countdown(3)) == [3, 2, 1]

    # Manual iterator protocol (what `for` does under the hood):
    it = iter([10, 20])
    assert next(it) == 10 and next(it) == 20
    try:
        next(it)
        raise AssertionError
    except StopIteration:
        pass

    # Lazy pipeline over "lines" — memory is O(1), not O(n).
    lines = ["1", "", "2", "3"]
    assert list(running_totals(read_numbers(lines))) == [1, 3, 6]

    # islice: take without materializing an infinite/large source.
    def naturals() -> Iterator[int]:
        n = 0
        while True:
            yield n
            n += 1

    assert list(islice(naturals(), 5)) == [0, 1, 2, 3, 4]

    # chain: concatenate iterables lazily.
    assert list(chain([1, 2], [3, 4])) == [1, 2, 3, 4]

    # batched: fixed-size chunks (last may be short).
    assert list(batch_stream(range(7), 3)) == [(0, 1, 2), (3, 4, 5), (6,)]

    # groupby: groups *consecutive* equal keys (sort first if you want global groups).
    data = [("a", 1), ("a", 2), ("b", 3)]
    grouped = {k: [v for _, v in g] for k, g in groupby(data, key=lambda t: t[0])}
    assert grouped == {"a": [1, 2], "b": [3]}

    # Memory proof: a genexpr holds one item; a list holds them all.
    gen = (x * x for x in range(1_000_000))
    lst = [0]  # tiny stand-in
    assert sys.getsizeof(gen) < sys.getsizeof(list(range(1000)))
    assert next(gen) == 0  # only computed on demand
    _ = lst

    # Generators are single-use: once exhausted, they're empty.
    g = countdown(2)
    assert list(g) == [2, 1]
    assert list(g) == []  # already consumed

    print("05_iterators_generators: all assertions passed ✅")


if __name__ == "__main__":
    _demo()
