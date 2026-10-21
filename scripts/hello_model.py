"""First call to the model: print the answer, the token counts and the cost."""

import anthropic

MODEL = "claude-haiku-5-5"
# Prices in US dollars per million tokens, checked on 2026-10-19.
INPUT_PRICE = 0.10
OUTPUT_PRICE = 0.50
QUESTION = "In two sentences, explain why an expired certificate can block a customer's login."


def main() -> None:
    """Ask one question and show the answer and what it cost."""
    client = anthropic.Anthropic()
    message = client.messages.create(
        model=MODEL,
        max_tokens=200,
        messages=[{"role": "user", "content": QUESTION}],
    )
    block = message.content[0]
    if block.type == "text":
        print(block.text)
    usage = message.usage
    cost = (usage.input_tokens * INPUT_PRICE + usage.output_tokens * OUTPUT_PRICE) / 1_000_000
    print(f"input tokens: {usage.input_tokens}")
    print(f"output tokens: {usage.output_tokens}")
    print(f"cost: ${cost:.6f}")

    print(f"stop reason: {message.stop_reason}")


if __name__ == "__main__":
    main()
