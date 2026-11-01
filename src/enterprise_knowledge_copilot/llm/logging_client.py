"""Provide an LLM client that logs every call to a JSON Lines file."""

import json
import time
from datetime import UTC, datetime
from pathlib import Path

from enterprise_knowledge_copilot.llm.base import LLMClient
from enterprise_knowledge_copilot.llm.models import LLMRequest, LLMResponse


class LoggingClient:
    """Wrap an LLM client and log each call."""

    def __init__(self, inner: LLMClient, log_path: Path) -> None:
        """Initialize the inner client and log file path."""
        self._inner = inner
        self._log_path = log_path
        self._log_path.parent.mkdir(parents=True, exist_ok=True)

    def complete(self, request: LLMRequest) -> LLMResponse:
        """Call the inner client, log the call, and return its response."""
        start = time.perf_counter()
        response = self._inner.complete(request)
        elapsed = (time.perf_counter() - start) * 1000
        log_entry = {
            "model": response.model,
            "input_tokens": response.input_tokens,
            "output_tokens": response.output_tokens,
            "cost_usd": response.cost_usd,
            "stop_reason": response.stop_reason,
            "cached": response.cached,
            "duration_ms": elapsed,
            "timestamp": datetime.now(UTC).isoformat(),
        }
        line = json.dumps(log_entry)
        with self._log_path.open("a", encoding="utf-8") as f:
            f.write(line + "\n")
        return response
