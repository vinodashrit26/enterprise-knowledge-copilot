"""Create stable cache keys for LLM requests."""

import hashlib
import json

from enterprise_knowledge_copilot.llm.models import LLMRequest


def cache_key(request: LLMRequest) -> str:
    """Return the SHA-256 hex digest of the request's canonical JSON.

    Keys are sorted so the same request always produces the same JSON text.
    The text is encoded to bytes because hashlib works on bytes.
    """
    cache_dict = request.model_dump()
    canonical_json = json.dumps(cache_dict, sort_keys=True)
    return hashlib.sha256(canonical_json.encode("utf-8")).hexdigest()
