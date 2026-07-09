"""19 — Regular expressions (`re`): parsing and extraction.

You'll use these to scrape structure out of text: extract JSON blobs from LLM output,
parse logs, validate IDs, split on delimiters.

MUST KNOW
  - `re.match` (anchored at START) vs `re.search` (ANYWHERE) vs `re.fullmatch` (whole string).
  - `findall` (all matches as strings/tuples) vs `finditer` (Match objects, with spans).
  - Groups: numbered `\1`/`.group(1)`, named `(?P<name>...)` / `.group("name")`.
  - `re.sub` (replace), `re.split`. `re.compile` once for reuse.
  - Greedy `*`/`+` vs lazy `*?`/`+?` (matches as little as possible).
  - Flags: `re.IGNORECASE`, `re.MULTILINE`, `re.DOTALL`, `re.VERBOSE`.

INTERVIEW QUESTIONS
  - "match vs search?"  "greedy vs lazy — give an example."
  - "Extract all numbers / a named field from this string."
"""

from __future__ import annotations

import re


def _demo() -> None:
    # match is anchored at the start; search scans the whole string.
    assert re.match(r"\d+", "123abc") is not None
    assert re.match(r"\d+", "abc123") is None  # doesn't start with digits
    assert re.search(r"\d+", "abc123") is not None  # found later in the string

    # groups + named groups
    m = re.search(r"(?P<user>\w+)@(?P<domain>[\w.]+)", "contact ada@nimbus.example now")
    assert m is not None
    assert m.group("user") == "ada" and m.group("domain") == "nimbus.example"
    assert m.group(0) == "ada@nimbus.example"  # group 0 = whole match
    assert m.span() == (8, 26)  # start/end indices

    # findall returns strings (or tuples if multiple groups)
    assert re.findall(r"\d+", "a1 b22 c333") == ["1", "22", "333"]
    assert re.findall(r"(\w+)=(\d+)", "x=1 y=2") == [("x", "1"), ("y", "2")]

    # finditer gives Match objects (positions, groups) lazily
    positions = [mo.start() for mo in re.finditer(r"cat", "cat scatter cat")]
    assert positions == [0, 5, 12]

    # sub: replace; a function can compute the replacement
    assert re.sub(r"\s+", "_", "a  b\tc") == "a_b_c"
    assert re.sub(r"\d+", lambda mo: str(int(mo.group()) * 2), "a1 b2") == "a2 b4"

    # split on a pattern
    assert re.split(r"[,;]\s*", "a, b; c,d") == ["a", "b", "c", "d"]

    # GREEDY vs LAZY — the classic bug. Greedy takes as much as possible.
    greedy = re.search(r"<(.+)>", "<a><b>")
    lazy = re.search(r"<(.+?)>", "<a><b>")
    assert greedy is not None and greedy.group(1) == "a><b"  # spans both tags
    assert lazy is not None and lazy.group(1) == "a"  # stops at first '>'

    # compile once, reuse; flags for readability + case-insensitivity
    pattern = re.compile(r"error: (\w+)", re.IGNORECASE)
    assert pattern.findall("ERROR: rate\nerror: timeout") == ["rate", "timeout"]

    # fullmatch: validate an entire string (e.g., a model-id shape)
    assert re.fullmatch(r"(gpt|claude)-[\w.-]+", "gpt-4o") is not None
    assert re.fullmatch(r"(gpt|claude)-[\w.-]+", "llama-3") is None

    print("19_regex: all assertions passed ✅")


if __name__ == "__main__":
    _demo()
