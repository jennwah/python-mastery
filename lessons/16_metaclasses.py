"""16 — Metaclasses: classes that create classes.

A metaclass controls how a *class* is built (not how instances behave). Rarely needed —
`__init_subclass__` (15), class decorators, and descriptors cover most cases — but you
must be able to explain them, and frameworks (Django models, ABCs, pydantic v1) use them.

MUST KNOW
  - A class is an instance of its metaclass; the default metaclass is `type`.
  - `type(name, bases, namespace)` creates a class dynamically.
  - Define one by subclassing `type` and overriding `__new__`/`__init__`.
  - `type(obj)` gives an object's class; `type(SomeClass)` gives its metaclass.
  - "Prefer `__init_subclass__` or a class decorator unless you must intercept class
    creation itself" — the interview-safe stance.

INTERVIEW QUESTIONS
  - "What's a metaclass and when have you needed one?"
  - "How do you create a class dynamically?" (`type(...)`).
  - "metaclass vs `__init_subclass__` vs class decorator?"
"""

from __future__ import annotations

from typing import Any


# --- 1. Dynamic class creation: classes are objects built by `type` ---
def make_class() -> type:
    return type("Dynamic", (), {"x": 1, "double": lambda self: self.x * 2})


# --- 2. A metaclass that auto-registers concrete subclasses + enforces a rule ---
class PluginMeta(type):
    registry: dict[str, type] = {}

    def __new__(mcs, name: str, bases: tuple[type, ...], ns: dict[str, Any]) -> type:
        cls = super().__new__(mcs, name, bases, ns)
        if bases:  # skip the base class itself (no bases means it's the root here)
            if "run" not in ns:
                raise TypeError(f"{name} must define run()")
            PluginMeta.registry[name.lower()] = cls
        return cls


class Plugin(metaclass=PluginMeta):
    pass


class Summarizer(Plugin):
    def run(self) -> str:
        return "summary"


# --- 3. A class decorator does a similar job more simply (usually preferred) ---
_decorated: dict[str, type] = {}


def register(cls: type) -> type:
    _decorated[cls.__name__.lower()] = cls
    return cls


@register
class Translator:
    pass


def _demo() -> None:
    Dyn = make_class()
    obj = Dyn()
    assert obj.x == 1 and obj.double() == 2  # type: ignore[attr-defined]

    # A class's type IS its metaclass.
    assert type(Summarizer) is PluginMeta
    assert type(int) is type  # ordinary classes use `type`
    assert isinstance(Summarizer, type)  # classes are instances of type

    # The metaclass registered the concrete plugin and enforced the run() rule.
    assert PluginMeta.registry == {"summarizer": Summarizer}
    try:
        class Broken(Plugin):  # no run() -> metaclass rejects it at creation time
            pass
        raise AssertionError("should have failed")
    except TypeError as e:
        assert "run()" in str(e)

    # The decorator approach — same registry effect, no metaclass.
    assert _decorated == {"translator": Translator}

    print("16_metaclasses: all assertions passed ✅")


if __name__ == "__main__":
    _demo()
