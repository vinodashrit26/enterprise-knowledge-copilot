"""Data shapes for talking to a language model."""

from pydantic import BaseModel, ConfigDict, Field


class LLMRequest(BaseModel):
    """One question sent to a language model."""

    model_config = ConfigDict(frozen=True)

    prompt: str = Field(min_length=1)
    model: str = "claude-haiku-5-5"
    max_tokens: int = Field(default=1024, gt=0)
    system: str | None = None


class LLMResponse(BaseModel):
    """What came back from a language model, with usage and cost."""

    model_config = ConfigDict(frozen=True)

    text: str
    model: str
    input_tokens: int = Field(ge=0)
    output_tokens: int = Field(ge=0)
    cost_usd: float = Field(ge=0)
    stop_reason: str | None
    cached: bool = False

    @property
    def truncated(self) -> bool:
        """Return True if the model was cut off by the max_tokens limit."""
        return self.stop_reason == "max_tokens"
