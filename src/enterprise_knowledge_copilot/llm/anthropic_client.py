"""A model client that calls Claude through the Anthropic SDK."""

import anthropic

from enterprise_knowledge_copilot.llm.errors import (
    LLMPermanentError,
    LLMTemporaryError,
)
from enterprise_knowledge_copilot.llm.models import LLMRequest, LLMResponse
from enterprise_knowledge_copilot.llm.pricing import calculate_cost, get_price

# Settings from ADR-0001. We set them explicitly instead of using SDK defaults.
MAX_RETRIES = 2
TIMEOUT_SECONDS = 60.0

# Status codes that may succeed if tried again (the SDK retries these too).
TEMPORARY_STATUS_CODES = frozenset({408, 409, 429})


def create_sdk_client() -> anthropic.Anthropic:
    """Create the real SDK client. It reads ANTHROPIC_API_KEY from the environment."""
    return anthropic.Anthropic(max_retries=MAX_RETRIES, timeout=TIMEOUT_SECONDS)


class AnthropicClient:
    """Sends requests to Claude and returns our own response type."""

    def __init__(self, sdk: anthropic.Anthropic) -> None:
        """Keep the SDK object we were given. Tests pass in a fake one."""
        self._sdk = sdk

    def complete(self, request: LLMRequest) -> LLMResponse:
        """Send a request to Claude and return the response.

        Args:
            request: The question to send.

        Returns:
            The answer, with token counts, cost and stop reason.

        Raises:
            LLMTemporaryError: If the call failed in a way that may pass later.
            LLMPermanentError: If the call can never succeed as it is.
        """
        price = get_price(request.model)
        try:
            message = self._sdk.messages.create(
                model=request.model,
                max_tokens=request.max_tokens,
                system=request.system if request.system is not None else anthropic.omit,
                messages=[{"role": "user", "content": request.prompt}],
            )
        except anthropic.APIConnectionError as err:
            raise LLMTemporaryError(f"Connection problem or timeout: {err}") from err
        except anthropic.APIStatusError as err:
            if err.status_code in TEMPORARY_STATUS_CODES or err.status_code >= 500:
                raise LLMTemporaryError(f"Temporary API error {err.status_code}") from err
            raise LLMPermanentError(f"API error {err.status_code}: {err}") from err
        except anthropic.APIError as err:
            raise LLMPermanentError(f"Unexpected API error: {err}") from err

        text = "".join(block.text for block in message.content if block.type == "text")
        usage = message.usage
        return LLMResponse(
            text=text,
            model=message.model,
            input_tokens=usage.input_tokens,
            output_tokens=usage.output_tokens,
            cost_usd=calculate_cost(price, usage.input_tokens, usage.output_tokens),
            stop_reason=message.stop_reason,
        )
