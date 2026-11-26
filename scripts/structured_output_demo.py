"""Demonstrate structured output with caching and logging."""

from pathlib import Path

from anthropic import transform_schema

from enterprise_knowledge_copilot.llm.anthropic_client import (
    AnthropicClient,
    create_sdk_client,
)
from enterprise_knowledge_copilot.llm.caching_client import CachingClient
from enterprise_knowledge_copilot.llm.logging_client import LoggingClient
from enterprise_knowledge_copilot.llm.models import LLMRequest
from enterprise_knowledge_copilot.llm.structured import Answer, parse_answer

MODEL = "claude-haiku-5-5"

QUESTION = "What is the purpose of document versioning?"

SYSTEM_PROMPT = (
    "You are an enterprise document management expert. "
    "Answer each question in one short sentence. "
    "Rate your confidence in the answer as low, medium, or high."
)

CACHE_DIR = Path(".cache/llm_cache")
LOG_PATH = Path(".cache/model_reply_answer_demo.jsonl")


def main() -> None:
    """Run the structured output demo."""
    # 1. Create the real Anthropic SDK client.
    sdk_client = create_sdk_client()

    # 2. Wrap it in our AnthropicClient.
    anthropic_client = AnthropicClient(sdk=sdk_client)

    # 3. Add caching.
    caching_client = CachingClient(inner=anthropic_client, cache_dir=CACHE_DIR)

    # 4. Add logging as the outermost wrapper.
    logging_client = LoggingClient(inner=caching_client, log_path=LOG_PATH)

    client = logging_client

    # 5. Build the JSON schema from the Answer model.
    output_schema = transform_schema(Answer)

    # 6. Build the request.
    request = LLMRequest(
        prompt=QUESTION,
        model=MODEL,
        max_tokens=300,
        system=SYSTEM_PROMPT,
        output_schema=output_schema,
    )

    # 7. Get the response and parse the structured answer.
    response = client.complete(request)
    parsed_response = parse_answer(response)

    # 8. Print the results.
    print(f"\nQuestion: {QUESTION}")
    print(f"Answer: {parsed_response.answer}")
    print(f"Confidence: {parsed_response.confidence}")
    print(f"Cost: {response.cost_usd:.6f}")
    print(f"Is cached: {response.cached}")


if __name__ == "__main__":
    main()
