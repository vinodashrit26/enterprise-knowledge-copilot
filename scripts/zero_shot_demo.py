"""Demonstrate zero-shot prompting with caching and logging."""

from pathlib import Path

from enterprise_knowledge_copilot.llm.anthropic_client import (
    AnthropicClient,
    create_sdk_client,
)
from enterprise_knowledge_copilot.llm.caching_client import CachingClient
from enterprise_knowledge_copilot.llm.logging_client import LoggingClient
from enterprise_knowledge_copilot.llm.models import LLMRequest

MODEL = "claude-haiku-5-5"

QUESTIONS = [
    "What is the purpose of document versioning?",
    "Why should access permissions be reviewed regularly?",
    "What happens when a document is checked out?",
    "How does an audit trail help administrators?",
    "Why are document retention policies important?",
]

SYSTEM_PROMPT = (
    "You are an enterprise document management expert. Answer each question in one short sentence."
)

CACHE_DIR = Path(".cache/llm_cache")
LOG_PATH = Path(".cache/zero_shot_demo.jsonl")


def main() -> None:
    """Run the zero-shot demo."""
    # 1. Create the real Anthropic SDK client.
    sdk_client = create_sdk_client()

    # 2. Wrap it in our AnthropicClient.
    anthropic_client = AnthropicClient(sdk=sdk_client)

    # 3. Add caching.
    caching_client = CachingClient(inner=anthropic_client, cache_dir=CACHE_DIR)

    # 4. Add Logging.
    logging_client = LoggingClient(inner=caching_client, log_path=LOG_PATH)

    client = logging_client

    for question in QUESTIONS:
        request = LLMRequest(prompt=question, model=MODEL, max_tokens=1024, system=SYSTEM_PROMPT)
        response = client.complete(request)
        print(f"\nQuestion: {question}")
        print(f"Answer: {response.text}")
        print(f"Cost: {response.cost_usd:.6f}")
        print(f"Is cached: {response.cached}")


if __name__ == "__main__":
    main()
