from .base import Action
from providers import LLMProvider, CompletionResponse
from repository.code_request import CodeRequest
from colorama import Fore, Style
from rules import Rule
from repository.base import Repository
from pydantic import BaseModel
from actions.base import ActionResult
from typing import List

PROMPT = """Summarize the following code changes according to these rules:

Rules:
{rules_text}

Title: {pr.title}

Description:
{pr.description}

Changes:
{pr.changes}

Please provide a concise summary that:
1. Captures the main purpose of the changes
2. Highlights key technical decisions
3. Notes any significant impacts or considerations

Return your summary in a clear and structured format using markdown."""


class Summary(BaseModel):
    title: str
    lines_added: int
    lines_removed: int
    lines_modified: int
    what: str
    how: str


class SummarizeAction(Action):
    def __init__(
        self,
        provider: LLMProvider,
        repository: Repository,
        rules: List[Rule],
        verbose: bool = False,
    ):
        super().__init__(provider, repository, rules, verbose)

    def run(self, pr: CodeRequest, post: bool = False) -> ActionResult:
        rules_text = "\n".join(f"- {rule.content}" for rule in self.rules)
        prompt = PROMPT.format(rules_text=rules_text, pr=pr)

        if self.verbose:
            print(f"\n{Fore.GREEN}Prompt sent to LLM:{Style.RESET_ALL}")
            print(f"{Fore.GREEN}{prompt}{Style.RESET_ALL}\n")

        result = self.provider.completion(prompt)

        if self.verbose:
            print(f"\n{Fore.YELLOW}Response from LLM:{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}{result.text}{Style.RESET_ALL}\n")
            print(f"{Fore.YELLOW}Tokens used: {result.tokens_used}{Style.RESET_ALL}\n")

        if post:
            self.repository.post_comment(pr.project_id, pr.mr_id, result.text)

        return ActionResult(result.tokens_used)
