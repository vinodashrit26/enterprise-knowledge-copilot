"""Structured response models and parsing."""

from typing import Literal

from pydantic import BaseModel, ConfigDict

from enterprise_knowledge_copilot.llm.errors import RefusalError, TruncatedResponseError
from enterprise_knowledge_copilot.llm.models import LLMResponse


class Answer(BaseModel):
    """Represents a structured answer returned by the LLM."""

    model_config = ConfigDict(frozen=True)
    answer: str
    confidence: Literal["low", "medium", "high"]


def parse_answer(response: LLMResponse) -> Answer:
    """Parse the LLM response text into Answer model.

    Args:
        response: The response returned by the LLM.

    Returns:
        A validated Answer object.

    Raises:
        TruncatedResponseError: If the LLM response was truncated.
        RefusalError: If the LLM declined to respond.
    """
    if response.truncated:
        raise TruncatedResponseError(
            "The answer was cut off at the max_tokens. Increase the token limit."
        )
    if response.refused:
        raise RefusalError("The LLM declined to respond and there is no answer to parse.")
    return Answer.model_validate_json(response.text)
