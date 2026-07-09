"""13 — NumPy: vectorization, broadcasting, views. Non-negotiable for AI.

Embeddings, logits, and tensors are arrays. You must be able to replace Python loops
with vectorized NumPy (10-100x faster) and explain WHY (contiguous memory + C loops +
SIMD, no per-element Python object overhead).

MUST KNOW
  - `ndarray` has a fixed `dtype` and shape; operations are elementwise + vectorized.
  - **Broadcasting**: ops between different-but-compatible shapes without copying.
  - **Views vs copies**: slicing returns a VIEW (mutating it mutates the original);
    fancy/boolean indexing returns a COPY. This is a classic bug source.
  - `axis=` reduces along a dimension. `argmax`, `dot`/`@`, `norm`, `reshape`.

INTERVIEW QUESTIONS
  - "Why is NumPy faster than a Python loop?"
  - "What's broadcasting?"  "Does slicing copy?"  "Implement softmax with NumPy."
"""

from __future__ import annotations

import numpy as np


def softmax(logits: np.ndarray) -> np.ndarray:
    # Subtract max for numerical stability (avoid overflow in exp) — interview favorite.
    shifted = logits - logits.max(axis=-1, keepdims=True)
    exp = np.exp(shifted)
    return exp / exp.sum(axis=-1, keepdims=True)


def _demo() -> None:
    a = np.array([1, 2, 3], dtype=np.float64)

    # Vectorized elementwise ops (no Python loop):
    assert np.array_equal(a * 2, [2, 4, 6])
    assert np.array_equal(a + a, [2, 4, 6])

    # Broadcasting: (3,) op scalar, and (2,3) + (3,) align by trailing dims.
    m = np.array([[1, 2, 3], [4, 5, 6]])
    assert np.array_equal(m + np.array([10, 20, 30]), [[11, 22, 33], [14, 25, 36]])

    # axis reductions: axis=0 collapses rows, axis=1 collapses columns.
    assert np.array_equal(m.sum(axis=0), [5, 7, 9])
    assert np.array_equal(m.sum(axis=1), [6, 15])
    assert m.mean() == 3.5

    # argmax / dot / norm — the ops you use on logits & embeddings.
    assert m.argmax() == 5  # flat index of the max (value 6)
    assert np.array_equal(m.argmax(axis=1), [2, 2])  # per-row
    assert np.dot(a, a) == 14.0  # 1+4+9
    assert a @ a == 14.0  # @ is matmul/dot
    assert np.linalg.norm(np.array([3.0, 4.0])) == 5.0

    # softmax: rows sum to 1, larger logits -> larger probability.
    probs = softmax(np.array([[1.0, 2.0, 3.0]]))
    assert np.allclose(probs.sum(axis=-1), 1.0)
    assert probs[0, 2] > probs[0, 0]

    # VIEWS vs COPIES — the trap:
    base = np.array([0, 1, 2, 3, 4])
    view = base[1:4]  # a VIEW into base's memory
    view[0] = 99
    assert base[1] == 99  # mutating the view mutated the original!

    boolean = base[base > 2]  # boolean indexing returns a COPY
    boolean[0] = -1
    assert base[3] == 3  # original untouched

    # reshape shares memory when possible (also a view).
    r = np.arange(6).reshape(2, 3)
    assert r.shape == (2, 3) and r[1, 2] == 5

    # dtype matters: integer arrays truncate.
    ints = np.array([1, 2, 3])  # int64
    assert (ints / 2).dtype == np.float64  # true division promotes to float

    print("13_numpy_basics: all assertions passed ✅")


if __name__ == "__main__":
    _demo()
