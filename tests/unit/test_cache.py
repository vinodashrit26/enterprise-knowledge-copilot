"""Tests for LLM request cache-key generation."""

from enterprise_knowledge_copilot.llm.cache import cache_key
from enterprise_knowledge_copilot.llm.models import LLMRequest


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
