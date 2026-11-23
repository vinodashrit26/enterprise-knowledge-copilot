"""Structured response models and parsing."""

from typing import Literal

from pydantic import BaseModel, ConfigDict

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
    """
    return Answer.model_validate_json(response.text)
