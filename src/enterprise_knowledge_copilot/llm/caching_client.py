"""Provide an LLM client with file-based response caching."""

from pathlib import Path

from enterprise_knowledge_copilot.llm.base import LLMClient
from enterprise_knowledge_copilot.llm.cache import cache_key
from enterprise_knowledge_copilot.llm.models import LLMRequest, LLMResponse


class CachingClient:
    """Wrap an LLM client with file-based response caching."""

    def __init__(self, inner: LLMClient, cache_dir: Path) -> None:
        """Keep the LLMClient object and cache directory we were given."""
        self._inner = inner
        self._cache_dir = cache_dir
        self._cache_dir.mkdir(parents=True, exist_ok=True)

    def complete(self, request: LLMRequest) -> LLMResponse:
        """Return a cached response if it is not truncated accoring to ADR-0002."""
        key = cache_key(request)

        cache_path = self._cache_dir / (key + ".json")

        if cache_path.exists():
            text = cache_path.read_text(encoding="utf-8")
            response = LLMResponse.model_validate_json(text)
            return response.model_copy(update={"cached": True})
        else:
            # not available in the cache
            response = self._inner.complete(request)
            if response.truncated:
                return response
            cache_path.write_text(response.model_dump_json(), encoding="utf-8")
            return response
