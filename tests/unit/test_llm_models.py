"""Tests for the language model data shapes."""

import pytest
from pydantic import ValidationError

from enterprise_knowledge_copilot.llm.models import LLMRequest, LLMResponse


def test_request_rejects_empty_prompt() -> None:
    """An empty prompt is rejected before any money is spent."""
    with pytest.raises(ValidationError):
        LLMRequest(prompt="")


def test_request_rejects_zero_max_tokens() -> None:
    """The token limit must be positive."""
    with pytest.raises(ValidationError):
        LLMRequest(prompt="hello", max_tokens=0)


def test_response_is_truncated_when_cut_off() -> None:
    """A max_tokens stop reason means the answer was cut off."""
    response = LLMResponse(
        text="abc",
        model="m",
        input_tokens=1,
        output_tokens=2,
        cost_usd=0.0,
        stop_reason="max_tokens",
    )
    assert response.truncated is True


def test_response_is_not_truncated_on_normal_end() -> None:
    """A normal end of turn is not truncated."""
    response = LLMResponse(
        text="abc",
        model="m",
        input_tokens=1,
        output_tokens=2,
        cost_usd=0.0,
        stop_reason="end_turn",
    )
    assert response.truncated is False
