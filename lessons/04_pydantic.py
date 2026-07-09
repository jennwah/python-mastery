"""04 — Pydantic v2: validation at the trust boundary.

Pydantic is *the* data layer of modern AI apps: it validates API requests, app config,
and — critically — **LLM structured outputs** (you give the model a schema; pydantic
guarantees what you get back matches it). Unlike dataclasses/TypedDict, pydantic
*enforces* types at runtime.

MUST KNOW
  - `BaseModel` validates + coerces on construction; raises `ValidationError` on bad data.
  - `Field(...)` for constraints/metadata; `field_validator` / `model_validator` for logic.
  - `model_dump()` / `model_dump_json()` (serialize), `model_validate()` (parse).
  - Discriminated unions → clean modeling of LLM tool calls / message variants.
  - `pydantic-settings` (`BaseSettings`) reads config from env/.env (used in the portfolio).

INTERVIEW QUESTIONS
  - "How do you validate untrusted/LLM data?"  "dataclass vs pydantic?"
  - "How do you get structured/typed output from an LLM?" (schema -> validate).
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, ValidationError, field_validator, model_validator


# --- 1. Validation + coercion happen on construction ---
class Hyperparams(BaseModel):
    temperature: float = Field(ge=0.0, le=2.0)  # bounded
    max_tokens: int = Field(default=512, gt=0)
    model: str = "gpt-4o"

    @field_validator("model")
    @classmethod
    def _known(cls, v: str) -> str:
        if not v.startswith(("gpt-", "claude-")):
            raise ValueError("unknown model family")
        return v

    @model_validator(mode="after")
    def _cost_guard(self) -> Hyperparams:  # cross-field validation
        if self.temperature > 1.5 and self.max_tokens > 1000:
            raise ValueError("high temp + long output is expensive")
        return self


# --- 2. Structured output shape (what you'd force an LLM to return) ---
class Triage(BaseModel):
    category: Literal["billing", "account", "technical", "refund", "other"]
    priority: Literal["low", "normal", "high"]
    reasoning: str


# --- 3. Discriminated union: model LLM tool calls / message variants precisely ---
class SearchTool(BaseModel):
    kind: Literal["search"] = "search"
    query: str


class CalcTool(BaseModel):
    kind: Literal["calc"] = "calc"
    expression: str


class ToolCall(BaseModel):
    # pydantic picks the right variant by the `kind` field — fast + clear errors.
    tool: SearchTool | CalcTool = Field(discriminator="kind")


def _demo() -> None:
    # Coercion: the string "0.7" becomes a float; "512" -> int.
    hp = Hyperparams(temperature="0.7", max_tokens="512")  # type: ignore[arg-type]
    assert hp.temperature == 0.7 and hp.max_tokens == 512 and isinstance(hp.temperature, float)

    # Validation errors are structured and informative.
    try:
        Hyperparams(temperature=9.0)
        raise AssertionError("should reject out-of-range temperature")
    except ValidationError as e:
        assert e.error_count() == 1 and e.errors()[0]["type"] == "less_than_equal"

    try:
        Hyperparams(temperature=0.5, model="llama-3")
        raise AssertionError("should reject unknown model")
    except ValidationError:
        pass

    # Parse from JSON (e.g., an LLM's raw output) straight into a typed object.
    t = Triage.model_validate_json('{"category":"refund","priority":"high","reasoning":"x"}')
    assert t.category == "refund"
    # Serialize back out.
    assert t.model_dump()["priority"] == "high"
    assert '"category":"refund"' in t.model_dump_json()

    # Discriminated union routes to the correct model by `kind`.
    call = ToolCall.model_validate({"tool": {"kind": "calc", "expression": "2+2"}})
    assert isinstance(call.tool, CalcTool) and call.tool.expression == "2+2"

    print("04_pydantic: all assertions passed ✅")


if __name__ == "__main__":
    _demo()
