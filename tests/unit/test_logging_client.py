"""Tests for logging LLM API calls."""

import json
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock

from enterprise_knowledge_copilot.llm.base import LLMClient
from enterprise_knowledge_copilot.llm.logging_client import LoggingClient
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
    """Create a mock LLM client that returns FAKE_RESPONSE."""
    inner = MagicMock(spec=LLMClient)
    inner.complete.return_value = FAKE_RESPONSE
    return inner


def make_request() -> LLMRequest:
    """Return an LLMRequest for testing."""
    return LLMRequest(
        prompt="Logging Test",
        model="claude-haiku-5-5",
        max_tokens=1024,
    )


def read_entries(log_file: Path) -> list[dict[str, Any]]:
    """Read the log file and return its entries as a list of dictionaries."""
    return [json.loads(line) for line in log_file.read_text(encoding="utf-8").splitlines()]


def test_logging_client_writes_one_line(tmp_path: Path) -> None:
    """Verify that one LLM call produces exactly one JSONL log entry."""
    log_file = tmp_path / "calls.jsonl"
    inner = make_mock_client()
    client = LoggingClient(inner, log_file)

    request = make_request()
    result = client.complete(request)
    log_entries = read_entries(log_file)
    assert result == FAKE_RESPONSE
    assert len(log_entries) == 1
    assert log_entries[0]["model"] == "claude-haiku-5-5"
    assert log_entries[0]["cached"] is False


def test_logging_client_logs_usage_and_cost(tmp_path: Path) -> None:
    """Verify input_tokens, output_tokens, cost_usd, stop_reason."""
    log_file = tmp_path / "calls.jsonl"
    inner = make_mock_client()
    client = LoggingClient(inner, log_file)

    request = make_request()
    client.complete(request)
    log_entries = read_entries(log_file)
    assert log_entries[0]["input_tokens"] == 3
    assert log_entries[0]["output_tokens"] == 1
    assert log_entries[0]["cost_usd"] == 0.0000008
    assert log_entries[0]["stop_reason"] == "end_turn"


def test_logging_client_appends_each_call(tmp_path: Path) -> None:
    """Verify writing multiple lines to the log file."""
    inner = make_mock_client()
    log_file = tmp_path / "calls.jsonl"
    client = LoggingClient(inner, log_file)

    request = make_request()
    client.complete(request)
    client.complete(request)
    assert len(read_entries(log_file)) == 2


def test_logging_client_logs_cached_flag(tmp_path: Path) -> None:
    """Verify that the cached flag is logged correctly."""
    inner = make_mock_client()
    response = FAKE_RESPONSE.model_copy(update={"cached": True})
    inner.complete.return_value = response
    log_file = tmp_path / "calls.jsonl"
    client = LoggingClient(inner, log_file)
    request = make_request()
    client.complete(request)
    assert read_entries(log_file)[0]["cached"] is True


def test_logging_client_logs_duration_and_timestamp(tmp_path: Path) -> None:
    """Verify that duration and timezone-aware timestamp are logged correctly."""

    def slow_complete(request: LLMRequest) -> LLMResponse:
        time.sleep(0.05)
        return FAKE_RESPONSE

    inner = make_mock_client()
    inner.complete.side_effect = slow_complete
    log_file = tmp_path / "calls.jsonl"
    client = LoggingClient(inner, log_file)
    request = make_request()
    client.complete(request)
    log_entries = read_entries(log_file)
    assert log_entries[0]["duration_ms"] >= 40
    timestamp = datetime.fromisoformat(log_entries[0]["timestamp"])
    assert timestamp.utcoffset() == timedelta(0)


def test_logging_client_creates_missing_log_folder(tmp_path: Path) -> None:
    """Verify that the log folder is created if it does not exist."""
    inner = make_mock_client()
    log_file = tmp_path / "logs" / "calls.jsonl"
    client = LoggingClient(inner, log_file)
    request = make_request()
    client.complete(request)
    assert len(read_entries(log_file)) == 1
