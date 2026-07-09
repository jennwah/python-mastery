"""15 — Descriptors, properties, and __init_subclass__.

Descriptors are the machinery behind `property`, `classmethod`, `staticmethod`, and
`functools.cached_property`. Understanding them = understanding how attribute access
really works. `__init_subclass__` is the modern, lightweight hook for customizing
subclasses (often what people reach for metaclasses to do — see 16).

MUST KNOW
  - Descriptor protocol: `__get__`, `__set__`, `__delete__`, `__set_name__`.
  - DATA descriptor (has `__set__`/`__delete__`) beats the instance `__dict__`;
    NON-DATA descriptor (only `__get__`) is shadowed by the instance `__dict__`.
  - `property` is just a data descriptor.
  - `__set_name__` lets a descriptor learn the attribute name it's assigned to.
  - `__init_subclass__` runs when a subclass is created — great for registration/validation.

INTERVIEW QUESTIONS
  - "How does `property` work under the hood?" (a data descriptor).
  - "What's the difference between a data and non-data descriptor?"
  - "How would you validate an attribute on every assignment?" (data descriptor).
"""

from __future__ import annotations

from typing import Any


# --- 1. A reusable validating (data) descriptor ---
class Positive:
    def __set_name__(self, owner: type, name: str) -> None:
        self._name = f"_{name}"  # where to stash the real value on the instance

    def __get__(self, obj: Any, objtype: type | None = None) -> Any:
        if obj is None:  # accessed on the class, not an instance
            return self
        return getattr(obj, self._name)

    def __set__(self, obj: Any, value: float) -> None:  # having __set__ makes it a DATA descriptor
        if value <= 0:
            raise ValueError(f"must be positive, got {value}")
        setattr(obj, self._name, value)


class Hyperparams:
    temperature = Positive()  # validated on every assignment
    max_tokens = Positive()

    def __init__(self, temperature: float, max_tokens: int) -> None:
        self.temperature = temperature  # goes through Positive.__set__
        self.max_tokens = max_tokens


# --- 2. property is a data descriptor (compute on access, validate on set) ---
class Circle:
    def __init__(self, radius: float) -> None:
        self._radius = radius

    @property
    def radius(self) -> float:
        return self._radius

    @radius.setter
    def radius(self, value: float) -> None:
        if value < 0:
            raise ValueError("radius >= 0")
        self._radius = value

    @property
    def area(self) -> float:  # computed, read-only
        return 3.14159 * self._radius**2


# --- 3. Non-data descriptor (only __get__) is overridden by the instance dict ---
class Const:
    def __get__(self, obj: Any, owner: type | None = None) -> str:
        return "from-descriptor"


class Holder:
    value = Const()


# --- 4. __init_subclass__: register/validate subclasses without a metaclass ---
class Tool:
    registry: dict[str, type[Tool]] = {}

    def __init_subclass__(cls, *, name: str | None = None, **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)
        if name is not None:
            Tool.registry[name] = cls


class SearchTool(Tool, name="search"):
    pass


class CalcTool(Tool, name="calc"):
    pass


def _demo() -> None:
    hp = Hyperparams(temperature=0.7, max_tokens=512)
    assert hp.temperature == 0.7 and hp.max_tokens == 512
    try:
        Hyperparams(temperature=-1, max_tokens=10)
        raise AssertionError("negative temperature should fail")
    except ValueError:
        pass
    # Reassignment is validated too (data descriptor intercepts every set).
    try:
        hp.max_tokens = 0
        raise AssertionError
    except ValueError:
        pass

    c = Circle(2.0)
    assert c.area == 3.14159 * 4  # computed property
    c.radius = 3.0
    assert c.radius == 3.0
    try:
        c.radius = -1
        raise AssertionError
    except ValueError:
        pass

    # Data vs non-data precedence:
    h = Holder()
    assert h.value == "from-descriptor"  # non-data descriptor
    h.__dict__["value"] = "from-instance"
    assert h.value == "from-instance"  # instance dict WINS over non-data descriptor
    # (A data descriptor like Positive/property would still win over the instance dict.)

    # __init_subclass__ registered subclasses automatically.
    assert Tool.registry == {"search": SearchTool, "calc": CalcTool}

    print("15_descriptors: all assertions passed ✅")


if __name__ == "__main__":
    _demo()
