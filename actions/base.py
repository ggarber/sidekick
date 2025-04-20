from abc import ABC, abstractmethod
from providers import LLMProvider, CompletionResponse
from repository.code_request import CodeRequest
from repository.base import Repository
from rules import Rule
from typing import List


class ActionResult:
    def __init__(self, tokens_used: int):
        self.tokens_used = tokens_used


class Action(ABC):
    def __init__(
        self,
        provider: LLMProvider,
        repository: Repository,
        rules: List[Rule],
        verbose: bool = False,
    ):
        self.provider = provider
        self.repository = repository
        self.rules = rules
        self.verbose = verbose

    @abstractmethod
    def run(self, cr: CodeRequest, post: bool = False) -> ActionResult:
        """Execute the action on the given code request.

        Args:
            cr: The code request to process

        Returns:
            The result of the action as a CompletionResponse
        """
