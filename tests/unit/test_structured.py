"""Tests for structured response."""

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
