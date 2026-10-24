"""The interface every model client follows."""

from typing import Protocol

from enterprise_knowledge_copilot.llm.models import LLMRequest, LLMResponse


class LLMClient(Protocol):
    """Anything that can turn a request into a response."""

    def complete(self, request: LLMRequest) -> LLMResponse:
        """Send a request to a model and return its response."""
