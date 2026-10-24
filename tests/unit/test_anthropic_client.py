"""Tests for the Anthropic client, using a fake SDK so nothing hits the network."""

from types import SimpleNamespace
from unittest.mock import MagicMock

import anthropic
import pytest

from enterprise_knowledge_copilot.llm.anthropic_client import (
    MAX_RETRIES,
    TIMEOUT_SECONDS,
    AnthropicClient,
    create_sdk_client,
)
from enterprise_knowledge_copilot.llm.base import LLMClient
from enterprise_knowledge_copilot.llm.errors import (
    LLMPermanentError,
    LLMTemporaryError,
)
from enterprise_knowledge_copilot.llm.models import LLMRequest


def make_fake_message(stop_reason: str = "end_turn") -> SimpleNamespace:
    """Build an object shaped like the SDK's reply."""
    return SimpleNamespace(
        content=[SimpleNamespace(type="text", text="hello")],
        usage=SimpleNamespace(input_tokens=31, output_tokens=20),
        stop_reason=stop_reason,
        model="claude-haiku-5-5",
    )


def test_complete_returns_text_tokens_and_cost() -> None:
    """A normal reply becomes our response type, with the cost worked out."""
    sdk = MagicMock()
    sdk.messages.create.return_value = make_fake_message()
    response = AnthropicClient(sdk).complete(LLMRequest(prompt="hi"))
    assert response.text == "hello"
    assert response.input_tokens == 31
    assert response.output_tokens == 20
    assert response.cost_usd == pytest.approx(0.0000131)
    assert response.cached is False
    assert response.truncated is False


def test_complete_sends_the_request_fields_to_the_sdk() -> None:
    """The model, token limit and prompt reach the SDK unchanged."""
    sdk = MagicMock()
    sdk.messages.create.return_value = make_fake_message()
    AnthropicClient(sdk).complete(LLMRequest(prompt="hi", max_tokens=50))
    kwargs = sdk.messages.create.call_args.kwargs
    assert kwargs["model"] == "claude-haiku-5-5"
    assert kwargs["max_tokens"] == 50
    assert kwargs["messages"] == [{"role": "user", "content": "hi"}]
    assert kwargs["system"] is anthropic.omit


def test_system_prompt_is_passed_when_given() -> None:
    """A system prompt is sent to the SDK when the request has one."""
    sdk = MagicMock()
    sdk.messages.create.return_value = make_fake_message()
    AnthropicClient(sdk).complete(LLMRequest(prompt="hi", system="Be brief."))
    assert sdk.messages.create.call_args.kwargs["system"] == "Be brief."


def test_cut_off_answer_is_marked_truncated() -> None:
    """A max_tokens stop reason shows up as a truncated response."""
    sdk = MagicMock()
    sdk.messages.create.return_value = make_fake_message("max_tokens")
    response = AnthropicClient(sdk).complete(LLMRequest(prompt="hi"))
    assert response.truncated is True


def test_unknown_model_fails_before_calling_the_sdk() -> None:
    """With no known price, we stop before any money can be spent."""
    sdk = MagicMock()
    with pytest.raises(LLMPermanentError):
        AnthropicClient(sdk).complete(LLMRequest(prompt="hi", model="not-a-model"))
    sdk.messages.create.assert_not_called()


def test_timeout_becomes_a_temporary_error() -> None:
    """A timeout may succeed later, so it is a temporary error."""
    sdk = MagicMock()
    sdk.messages.create.side_effect = anthropic.APITimeoutError(request=MagicMock())
    with pytest.raises(LLMTemporaryError):
        AnthropicClient(sdk).complete(LLMRequest(prompt="hi"))


@pytest.mark.parametrize("status", [408, 409, 429, 500, 529])
def test_temporary_status_codes_become_temporary_errors(status: int) -> None:
    """Rate limits and server errors may succeed if tried again."""
    sdk = MagicMock()
    sdk.messages.create.side_effect = anthropic.APIStatusError(
        "problem", response=MagicMock(status_code=status), body=None
    )
    with pytest.raises(LLMTemporaryError):
        AnthropicClient(sdk).complete(LLMRequest(prompt="hi"))


@pytest.mark.parametrize("status", [400, 401, 403, 404])
def test_other_status_codes_become_permanent_errors(status: int) -> None:
    """A bad request or a bad key will fail the same way again."""
    sdk = MagicMock()
    sdk.messages.create.side_effect = anthropic.APIStatusError(
        "problem", response=MagicMock(status_code=status), body=None
    )
    with pytest.raises(LLMPermanentError):
        AnthropicClient(sdk).complete(LLMRequest(prompt="hi"))


def test_unexpected_sdk_error_is_permanent() -> None:
    """An error we did not plan for is not retried blindly."""
    sdk = MagicMock()
    sdk.messages.create.side_effect = anthropic.APIError("odd", MagicMock(), body=None)
    with pytest.raises(LLMPermanentError):
        AnthropicClient(sdk).complete(LLMRequest(prompt="hi"))


def test_sdk_client_uses_the_settings_from_adr_0001() -> None:
    """The real SDK client is built with the retry and timeout we decided on."""
    sdk = create_sdk_client()
    assert sdk.max_retries == MAX_RETRIES
    assert sdk.timeout == TIMEOUT_SECONDS


def test_anthropic_client_follows_the_interface() -> None:
    """mypy checks that AnthropicClient fits the LLMClient contract."""
    client: LLMClient = AnthropicClient(MagicMock())
    assert client is not None
