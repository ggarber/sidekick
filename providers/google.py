import os
import google.generativeai as genai
from .base import LLMProvider, CompletionResponse


class GoogleProvider(LLMProvider):
    def __init__(self):
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
        if not os.getenv("GOOGLE_API_KEY"):
            raise ValueError("GOOGLE_API_KEY environment variable is not set")
        self.model = os.getenv("GOOGLE_MODEL", "gemini-1.5-pro")

    def completion(self, prompt: str) -> CompletionResponse:
        model = genai.GenerativeModel(self.model)
        response = model.generate_content(prompt)

        return CompletionResponse(
            text=response.text,
            tokens_used=response.usage_metadata.prompt_token_count
            + response.usage_metadata.candidates_token_count,
        )

    def get_context_window(self) -> int:
        context_windows = {
            "gemini-1.5-pro": 1000000,
            "gemini-1.0-pro": 32768,
        }
        return context_windows.get(self.model, 1000000)
