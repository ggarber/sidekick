from .base import Action
from providers import LLMProvider
from repository.code_request import CodeRequest
from colorama import Fore, Style
from rules import Rule
from repository.base import Repository
from actions.base import ActionResult
from typing import List
import os

CUSTOM_LABELS = [label for label in os.getenv("CUSTOM_LABELS", "").split(",") if label]

PROMPT = """Based on the following pull request and rules, suggest appropriate labels:

Rules:
{rules_text}

Title: {pr.title}

Description:
{pr.description}

Changes:
{pr.changes}

Please suggest a list of labels that would be appropriate for this pull request.
{label_instructions}

Return only a comma-separated list of labels, nothing else."""

# Define different instructions based on whether custom labels are provided
DEFAULT_INSTRUCTIONS = """Focus on:
1. Type of change (feature, bugfix, refactor, etc.)
2. Impact (major, minor, etc.)
3. Technical areas affected (frontend, backend, documentation, etc.)"""

CUSTOM_INSTRUCTIONS = """Choose from the following labels:
{}

Select all appropriate labels from this list that apply to the changes."""


class LabelAction(Action):
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

        # Choose instructions based on whether custom labels are provided
        if CUSTOM_LABELS:
            label_instructions = CUSTOM_INSTRUCTIONS.format(", ".join(CUSTOM_LABELS))
        else:
            label_instructions = DEFAULT_INSTRUCTIONS

        prompt = PROMPT.format(
            rules_text=rules_text, pr=pr, label_instructions=label_instructions
        )

        if self.verbose:
            print(f"\n{Fore.GREEN}Prompt sent to LLM:{Style.RESET_ALL}")
            print(f"{Fore.GREEN}{prompt}{Style.RESET_ALL}\n")

        result = self.provider.completion(prompt)

        labels = result.text.split(",")

        if self.verbose:
            print(f"\n{Fore.YELLOW}Response from LLM:{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}{labels}{Style.RESET_ALL}\n")
            print(f"{Fore.YELLOW}Tokens used: {result.tokens_used}{Style.RESET_ALL}\n")

        if post:
            self.post_result(pr, labels)

        return ActionResult(result.tokens_used)

    def post_result(self, pr: CodeRequest, labels: List[str]) -> None:
        """Post the suggested labels as a comment on the pull request."""
        if self.verbose:
            print(f"\n{Fore.WHITE}Posting labels as comment...{Style.RESET_ALL}")
            print(f"{Fore.WHITE}Labels: {labels}{Style.RESET_ALL}")

        self.repository.label_merge_request(pr.project_id, pr.mr_id, labels)

        if self.verbose:
            print(f"{Fore.WHITE}Labels posted successfully{Style.RESET_ALL}")
