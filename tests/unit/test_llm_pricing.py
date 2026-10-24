"""Tests for model prices and errors."""

import pytest

from enterprise_knowledge_copilot.llm.errors import (
    LLMError,
    LLMPermanentError,
    LLMTemporaryError,
)
from enterprise_knowledge_copilot.llm.pricing import calculate_cost, get_price


def test_cost_matches_the_first_real_call() -> None:
    """31 input and 20 output tokens on Haiku 5.5 cost about $0.0000131."""
    price = get_price("claude-haiku-5-5")
    assert calculate_cost(price, 31, 20) == pytest.approx(0.0000131)


def test_unknown_model_is_a_permanent_error() -> None:
    """A model with no known price is rejected, so we never pay blind."""
    with pytest.raises(LLMPermanentError):
        get_price("not-a-real-model")


def test_temporary_and_permanent_errors_are_llm_errors() -> None:
    """Callers can catch every client problem with one type."""
    assert issubclass(LLMTemporaryError, LLMError)
    assert issubclass(LLMPermanentError, LLMError)
