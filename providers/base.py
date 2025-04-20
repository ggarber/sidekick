from abc import ABC, abstractmethod
from pydantic import BaseModel
from typing import Optional


class CompletionResponse(BaseModel):
    """Model representing a completion response from an LLM."""

    text: str
    tokens_used: int


class LLMProvider(ABC):
    """Abstract base class for LLM providers."""

    @property
    @abstractmethod
    def max_tokens(self) -> int:
        """
        Returns the maximum number of tokens supported by this LLM provider.
        Each provider should implement this based on their model's limitations.
        """
        pass

    @abstractmethod
    def completion(self, prompt: str) -> Optional[CompletionResponse]:
        """Generate a completion for the given prompt.

        Args:
            prompt: The input prompt to generate a completion for

        Returns:
            CompletionResponse containing the generated text and tokens used
        """
        pass
