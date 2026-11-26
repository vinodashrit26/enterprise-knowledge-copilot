"""Tests for structured response."""

import pytest
from pydantic import ValidationError

from enterprise_knowledge_copilot.llm.errors import RefusalError, TruncatedResponseError
from enterprise_knowledge_copilot.llm.models import LLMResponse
from enterprise_knowledge_copilot.llm.structured import Answer, parse_answer


def test_parse_answer_returns_answer_for_valid_json() -> None:
    """Verify return answer for valid json."""
    response = LLMResponse(
        text='{"answer": "The service is healthy", "confidence": "high"}',
        model="claude-haiku-5-5",
        input_tokens=3,
        output_tokens=1,
        cost_usd=0.0000008,
        stop_reason="end_turn",
    )
    result = parse_answer(response)
    assert isinstance(result, Answer)

    assert result.answer == "The service is healthy"
    assert result.confidence == "high"


def test_parse_answer_raises_when_truncated() -> None:
    """Verify return answer is truncated."""
    response = LLMResponse(
        text='{"answer": "The service is heal',
        model="claude-haiku-5-5",
        input_tokens=3,
        output_tokens=1,
        cost_usd=0.0000008,
        stop_reason="max_tokens",
    )
    with pytest.raises(TruncatedResponseError):
        parse_answer(response)


def test_parse_answer_raises_when_refused() -> None:
    """Verify return answer for refused response."""
    response = LLMResponse(
        text="The service is healthy",
        model="claude-haiku-5-5",
        input_tokens=3,
        output_tokens=1,
        cost_usd=0.0000008,
        stop_reason="refusal",
    )
    with pytest.raises(RefusalError):
        parse_answer(response)


def test_parse_answer_raises_for_invalid_json() -> None:
    """Raise exception for invalid json."""
    response = LLMResponse(
        text="The service is healthy",
        model="claude-haiku-5-5",
        input_tokens=3,
        output_tokens=1,
        cost_usd=0.0000008,
        stop_reason="end_turn",
    )
    with pytest.raises(ValidationError):
        parse_answer(response)


def test_parse_answer_raises_for_wrong_shape() -> None:
    """Raise exception for wrong shape."""
    response = LLMResponse(
        text='{"answer": "The service is healthy", "confidence": "very high"}',
        model="claude-haiku-5-5",
        input_tokens=3,
        output_tokens=1,
        cost_usd=0.0000008,
        stop_reason="end_turn",
    )

    with pytest.raises(ValidationError):
        parse_answer(response)
