import os
import anthropic
from .base import LLMProvider, CompletionResponse


class AnthropicProvider(LLMProvider):
    def __init__(self):
        self.client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        if not os.getenv("ANTHROPIC_API_KEY"):
            raise ValueError("ANTHROPIC_API_KEY environment variable is not set")
        self.model = os.getenv("ANTHROPIC_MODEL", "claude-3-opus-20240229")

    def completion(self, prompt: str) -> CompletionResponse:
        response = self.client.messages.create(
            model=self.model,
            max_tokens=4096,
            messages=[{"role": "user", "content": prompt}],
        )

        return CompletionResponse(
            text=response.content[0].text,
            tokens_used=response.usage.input_tokens + response.usage.output_tokens,
        )

    def get_context_window(self) -> int:
        context_windows = {
            "claude-3-opus-20240229": 200000,
            "claude-3-sonnet-20240229": 200000,
            "claude-3-haiku-20240307": 200000,
            "claude-2.1": 200000,
            "claude-2.0": 100000,
        }
        return context_windows.get(self.model, 200000)

    @property
    def max_tokens(self) -> int:
        # Claude supports up to 100K tokens
        return 100000
