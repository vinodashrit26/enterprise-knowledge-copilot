"""Tests for the LLM cache key and the caching client."""

from pathlib import Path
from unittest.mock import MagicMock

from enterprise_knowledge_copilot.llm.base import LLMClient
from enterprise_knowledge_copilot.llm.cache import cache_key
from enterprise_knowledge_copilot.llm.caching_client import CachingClient
from enterprise_knowledge_copilot.llm.models import LLMRequest, LLMResponse

FAKE_RESPONSE = LLMResponse(
    text="hi",
    model="claude-haiku-5-5",
    input_tokens=3,
    output_tokens=1,
    cost_usd=0.0000008,
    stop_reason="end_turn",
)


def make_mock_client() -> MagicMock:
    """Return a fake inner client whose complete() always returns FAKE_RESPONSE."""
    inner = MagicMock(spec=LLMClient)
    inner.complete.return_value = FAKE_RESPONSE
    return inner


def test_cache_key_is_64_hex_characters() -> None:
    """Verify the key is a 64-character lowercase hexadecimal string."""
    request = LLMRequest(
        prompt="Caching Test",
        model="claude-haiku-5-5",
        max_tokens=1024,
        system=None,
    )

    sha256_in_hex_key = cache_key(request)

    assert len(sha256_in_hex_key) == 64
    assert all(hexchar in "0123456789abcdef" for hexchar in sha256_in_hex_key)


def test_same_request_gives_same_key() -> None:
    """Verify identical requests produce identical cache keys."""
    request1 = LLMRequest(
        prompt="Caching Test",
        model="claude-haiku-5-5",
        max_tokens=1024,
        system=None,
    )

    request2 = LLMRequest(
        prompt="Caching Test",
        model="claude-haiku-5-5",
        max_tokens=1024,
        system=None,
    )
    assert cache_key(request1) == cache_key(request2)


def test_different_prompt_gives_different_key() -> None:
    """Verify different prompts produce different cache keys."""
    request1 = LLMRequest(
        prompt="Caching Test1",
        model="claude-haiku-5-5",
        max_tokens=1024,
        system=None,
    )

    request2 = LLMRequest(
        prompt="Caching Test2",
        model="claude-haiku-5-5",
        max_tokens=1024,
        system=None,
    )

    assert cache_key(request1) != cache_key(request2)


def test_different_model_gives_different_key() -> None:
    """Verify different models produce different cache keys."""
    request1 = LLMRequest(
        prompt="Caching Test",
        model="claude-haiku-5-5",
        max_tokens=1024,
        system=None,
    )

    request2 = LLMRequest(
        prompt="Caching Test",
        model="claude-sonnet-5-5",
        max_tokens=1024,
        system=None,
    )

    assert cache_key(request1) != cache_key(request2)


def test_different_max_tokens_gives_different_key() -> None:
    """Verify different max_tokens values produce different cache keys."""
    request1 = LLMRequest(
        prompt="Caching Test",
        model="claude-haiku-5-5",
        max_tokens=10,
        system=None,
    )

    request2 = LLMRequest(
        prompt="Caching Test",
        model="claude-haiku-5-5",
        max_tokens=100,
        system=None,
    )

    assert cache_key(request1) != cache_key(request2)


def test_different_system_gives_different_key() -> None:
    """Verify different system values produce different cache keys."""
    request1 = LLMRequest(
        prompt="Caching Test",
        model="claude-haiku-5-5",
        max_tokens=100,
        system=None,
    )

    request2 = LLMRequest(
        prompt="Caching Test",
        model="claude-haiku-5-5",
        max_tokens=100,
        system="new system",
    )

    assert cache_key(request1) != cache_key(request2)


def test_first_call_goes_to_inner_client_and_writes_a_file(tmp_path: Path) -> None:
    """Verify the first call invokes the inner client and writes a cache file."""
    inner = make_mock_client()

    client = CachingClient(inner, tmp_path)
    request = LLMRequest(
        prompt="Caching client Test",
        model="claude-haiku-5-5",
        max_tokens=100,
        system=None,
    )
    result = client.complete(request)

    inner.complete.assert_called_once_with(request)
    assert result.cached is False
    assert result.text == "hi"
    assert len(list(tmp_path.glob("*.json"))) == 1


def test_second_identical_call_does_not_call_inner_client(tmp_path: Path) -> None:
    """Verify an identical second call replays the file and skips the inner client."""

    inner = make_mock_client()
    client = CachingClient(inner, tmp_path)
    request = LLMRequest(
        prompt="Caching client Test",
        model="claude-haiku-5-5",
        max_tokens=100,
        system=None,
    )

    first_result = client.complete(request)
    second_result = client.complete(request)

    assert inner.complete.call_count == 1
    assert second_result.cached is True
    assert len(list(tmp_path.glob("*.json"))) == 1

    assert second_result.text == first_result.text
    assert second_result.input_tokens == first_result.input_tokens
    assert second_result.output_tokens == first_result.output_tokens
    assert second_result.cost_usd == first_result.cost_usd


def test_different_request_calls_inner_client_again(tmp_path: Path) -> None:
    """Verify different prompts call the inner client and create cache files."""

    inner = make_mock_client()
    client = CachingClient(inner, tmp_path)
    request1 = LLMRequest(
        prompt="Caching client Test",
        model="claude-haiku-5-5",
        max_tokens=100,
        system=None,
    )

    request2 = LLMRequest(
        prompt="Hello World!",
        model="claude-haiku-5-5",
        max_tokens=100,
        system=None,
    )

    client.complete(request1)
    client.complete(request2)

    assert inner.complete.call_count == 2
    assert len(list(tmp_path.glob("*.json"))) == 2
