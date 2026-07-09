"""22 — Packaging, project layout, and tooling.

This is "do you write real, shippable Python?" — highly signal-rich in interviews.

MUST KNOW
  - `pyproject.toml` is the single config file: `[project]` (name, version, deps),
    `[dependency-groups]` (dev deps), and `[tool.*]` (ruff/mypy/pytest).
  - Module = one `.py`; package = a directory (with `__init__.py`, or a namespace pkg).
  - `src/` layout (package under `src/`) prevents "accidentally importing from cwd" bugs.
  - `__all__` controls what `from module import *` exports (and documents the public API).
  - `if __name__ == "__main__":` — code that runs only when executed, not when imported.
  - Build artifacts: **sdist** (source) + **wheel** (built); a build backend (hatchling,
    setuptools) turns your project into them. `[project.scripts]` = CLI entry points.
  - `importlib.metadata` reads installed-package metadata at runtime (version, entry points).

TOOLING (be able to say what each does)
  - uv:     `uv sync` (venv+deps from lockfile), `uv add`, `uv run`, `uv lock`, `uv build`.
  - ruff:   lint + format (replaces flake8 + isort + black).
  - mypy:   static type checking (`strict = true`); run in CI.
  - pytest: tests; discovery via `testpaths`.
  - Versioning: SemVer (MAJOR.MINOR.PATCH) — breaking / feature / fix.

INTERVIEW QUESTIONS
  - "How do you structure and package a Python project?"
  - "What's a wheel vs an sdist?"  "Editable install — what and why?" (`uv pip install -e .`
    / a non-package project; import your code without reinstalling on each change).
  - "How do you expose a CLI command from a package?" (`[project.scripts]` entry point).
"""

from __future__ import annotations

from importlib import metadata

# `__all__` declares the public API for `from this_module import *`.
__all__ = ["public_api"]


def public_api() -> str:
    return "exported"


def _private_helper() -> str:  # not in __all__ -> not exported by `import *`
    return "hidden"


def _demo() -> None:
    # importlib.metadata: read the installed version of any dependency at runtime.
    v = metadata.version("pydantic")
    assert isinstance(v, str) and v[0].isdigit()  # e.g. "2.13.4"

    # Package metadata (name/summary come from that package's pyproject).
    meta = metadata.metadata("pydantic")
    assert meta["Name"].lower() == "pydantic"

    # __all__ is a plain list you can introspect; it's the documented public surface.
    assert __all__ == ["public_api"]
    assert public_api() == "exported" and _private_helper() == "hidden"

    # A minimal pyproject.toml (what makes the above installable) looks like:
    #
    #   [project]
    #   name = "my-agent"
    #   version = "0.1.0"
    #   requires-python = ">=3.12"
    #   dependencies = ["pydantic>=2.7", "httpx"]
    #
    #   [project.scripts]
    #   my-agent = "my_agent.cli:main"     # `my-agent` CLI -> my_agent/cli.py:main()
    #
    #   [build-system]
    #   requires = ["hatchling"]
    #   build-backend = "hatchling.build"
    #
    # Then: `uv build` -> dist/*.whl + dist/*.tar.gz ; `uv publish` -> PyPI.

    print("22_packaging: all assertions passed ✅")


if __name__ == "__main__":
    _demo()
