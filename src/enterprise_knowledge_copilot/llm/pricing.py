"""Model prices, in US dollars per million tokens."""

from pydantic import BaseModel, ConfigDict

from enterprise_knowledge_copilot.llm.errors import LLMPermanentError


class ModelPrice(BaseModel):
    """The price of one model."""

    model_config = ConfigDict(frozen=True)

    input_per_mtok: float
    output_per_mtok: float


# Checked on 2026-10-19 at platform.claude.com/docs/en/about-claude/pricing.
PRICES: dict[str, ModelPrice] = {
    "claude-haiku-5-5": ModelPrice(input_per_mtok=0.10, output_per_mtok=0.50),
    "claude-sonnet-5-5": ModelPrice(input_per_mtok=2.00, output_per_mtok=10.00),
}


def get_price(model: str) -> ModelPrice:
    """Return the price of a model.

    Args:
        model: The model name, for example "claude-haiku-5-5".

    Returns:
        The price of the model.

    Raises:
        LLMPermanentError: If we have no price for this model.
    """
    try:
        return PRICES[model]
    except KeyError:
        raise LLMPermanentError(f"No price known for model '{model}'.") from None


def calculate_cost(price: ModelPrice, input_tokens: int, output_tokens: int) -> float:
    """Return the cost in US dollars of one call."""
    total = input_tokens * price.input_per_mtok + output_tokens * price.output_per_mtok
    return total / 1_000_000
