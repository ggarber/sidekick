from .base import Action
from providers import LLMProvider
from repository.code_request import CodeRequest
from colorama import Fore, Style
from rules import Rule
from repository.base import Repository
from actions.base import ActionResult
from typing import List

PROMPT = """Review the following code changes according to these rules:

Rules:
{rules_text}

Title: {cr.title}

Description:
{cr.description}

Changes:
{cr.changes}

Please review the code changes and provide feedback on:
1. Code quality and maintainability
2. Potential bugs or issues
3. Performance considerations
4. Security concerns
5. Any other relevant aspects

Return your review in a clear and structured format."""


class ReviewCodeAction(Action):
    def __init__(
        self,
        provider: LLMProvider,
        repository: Repository,
        rules: List[Rule],
        verbose: bool = False,
    ):
        super().__init__(provider, repository, rules, verbose)

    def run(self, cr: CodeRequest, post: bool = False) -> ActionResult:
        # rules_by_glob = Set()

        rules_text = "\n".join(f"- {rule.content}" for rule in self.rules)
        prompt = PROMPT.format(rules_text=rules_text, cr=cr)

        if self.verbose:
            print(f"\n{Fore.GREEN}Prompt sent to LLM:{Style.RESET_ALL}")
            print(f"{Fore.GREEN}{prompt}{Style.RESET_ALL}\n")

        result = self.provider.completion(prompt)

        if self.verbose:
            print(f"\n{Fore.YELLOW}Response from LLM:{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}{result.text}{Style.RESET_ALL}\n")
            print(f"{Fore.YELLOW}Tokens used: {result.tokens_used}{Style.RESET_ALL}\n")

        if post:
            self.post_result(cr, result)

        return ActionResult(result.tokens_used)

    def post_result(self, cr: CodeRequest, result: str) -> None:
        """Post review results as a comment on the merge request."""
        pass
