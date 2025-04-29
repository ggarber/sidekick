import os
from openai import OpenAI
from .base import LLMProvider, CompletionResponse


class OpenAIProvider(LLMProvider):
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        if not os.getenv("OPENAI_API_KEY"):
            raise ValueError("OPENAI_API_KEY environment variable is not set")
        self.model = os.getenv("OPENAI_MODEL", "gpt-4-turbo-preview")

    def completion(self, prompt: str) -> CompletionResponse:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
        )

        return CompletionResponse(
            text=response.choices[0].message.content,
            tokens_used=response.usage.total_tokens,
        )

    def get_context_window(self) -> int:
        context_windows = {
            "gpt-4-turbo-preview": 128000,
            "gpt-4": 8192,
            "gpt-3.5-turbo": 16385,
        }
        return context_windows.get(self.model, 128000)

    @property
    def max_tokens(self) -> int:
        return self.get_context_window()
