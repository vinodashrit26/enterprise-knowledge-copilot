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


def test_refused_is_true_when_stop_reason_is_refusal() -> None:
    """Verify that refused is true when stop_reason is refusal."""
    response = LLMResponse(
        text="abc",
        model="m",
        input_tokens=1,
        output_tokens=2,
        cost_usd=0.0,
        stop_reason="refusal",
    )
    assert response.refused is True


def test_refused_is_false_when_stop_reason_is_end_turn() -> None:
    """Verify refused is false when stop_reason is end_turn."""
    response = LLMResponse(
        text="abc",
        model="m",
        input_tokens=1,
        output_tokens=2,
        cost_usd=0.0,
        stop_reason="end_turn",
    )
    assert response.refused is False


def test_refused_is_false_when_stop_reason_is_max_tokens() -> None:
    """Verify refused is false when stop_reason is max_tokens."""
    response = LLMResponse(
        text="abc",
        model="m",
        input_tokens=1,
        output_tokens=2,
        cost_usd=0.0,
        stop_reason="max_tokens",
    )
    assert response.refused is False


def test_output_schema_defaults_to_none() -> None:
    """Verify output schema defaults to none."""
    request = LLMRequest(
        prompt="Output schema test",
    )
    assert request.output_schema is None
