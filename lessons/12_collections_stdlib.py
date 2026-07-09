"""12 — The standard library power tools you should reach for by reflex.

MUST KNOW
  - `collections`: `Counter` (frequencies/top-k), `defaultdict` (grouping),
    `deque` (O(1) ends / fixed-size window), `ChainMap` (layered config).
  - `heapq`: a min-heap → priority queues and top-k in O(n log k).
  - `bisect`: binary search + insertion into a sorted list.
  - `enum`: `StrEnum` (3.11+) for string constants that are also enums.
  - `pathlib.Path`: the modern file-path API (not `os.path` string munging).

INTERVIEW QUESTIONS
  - "Top-k frequent elements?" (`Counter.most_common`, or `heapq.nlargest`).
  - "Efficiently keep the last N items?" (`deque(maxlen=N)`).
  - "Group items by a key without KeyErrors?" (`defaultdict(list)`).
"""

from __future__ import annotations

import bisect
import heapq
from collections import Counter, defaultdict, deque
from enum import StrEnum
from pathlib import Path


class Model(StrEnum):  # StrEnum members ARE strings
    GPT4O = "gpt-4o"
    HAIKU = "claude-haiku-4-5"


def _demo() -> None:
    # Counter: frequencies + top-k in one line.
    words = "the cat the dog the cat".split()
    c = Counter(words)
    assert c["the"] == 3
    assert c.most_common(1) == [("the", 3)]

    # defaultdict: grouping without "if key not in d" boilerplate.
    by_len: dict[int, list[str]] = defaultdict(list)
    for w in ["a", "bb", "cc", "d"]:
        by_len[len(w)].append(w)
    assert by_len == {1: ["a", "d"], 2: ["bb", "cc"]}

    # deque(maxlen): a fixed-size sliding window; old items fall off the left.
    window: deque[int] = deque(maxlen=3)
    for n in range(5):
        window.append(n)
    assert list(window) == [2, 3, 4]
    window.appendleft(99)  # O(1) at both ends (a list is O(n) at the front)
    assert list(window) == [99, 2, 3]

    # heapq: min-heap. Top-k largest without sorting everything.
    nums = [5, 1, 8, 3, 9, 2]
    assert heapq.nlargest(3, nums) == [9, 8, 5]
    assert heapq.nsmallest(2, nums) == [1, 2]
    heap: list[int] = []
    for n in nums:
        heapq.heappush(heap, n)
    assert heapq.heappop(heap) == 1  # smallest first

    # bisect: keep a list sorted and do O(log n) lookups.
    scores = [10, 20, 30, 40]
    assert bisect.bisect_left(scores, 25) == 2  # insertion index
    bisect.insort(scores, 25)
    assert scores == [10, 20, 25, 30, 40]

    # StrEnum: a real enum that compares/serializes as its string value.
    assert Model.GPT4O == "gpt-4o" and f"{Model.GPT4O}" == "gpt-4o"
    assert Model("gpt-4o") is Model.GPT4O

    # pathlib: composable, OS-independent paths.
    p = Path("data") / "kb" / "faq.md"
    assert p.name == "faq.md" and p.suffix == ".md" and p.stem == "faq"
    assert p.parts == ("data", "kb", "faq.md")

    print("12_collections_stdlib: all assertions passed ✅")


if __name__ == "__main__":
    _demo()
