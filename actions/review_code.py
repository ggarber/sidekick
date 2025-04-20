from providers import LLMProvider, stringify_code_changes, stringify_rules
from repository import CodeRequest
from colorama import Fore, Style
from rules import Rule
from repository import Repository
from .base import Action, ActionResult
from typing import List

PROMPT = """Review the following code changes according to these rules:

Rules:
{rules_text}

Changes:
{changes_text}

The lines that were added are marked with a + and the lines that were removed are marked with a -.

Review only the lines that were added and check if the rules are followed.

For every rule not followed, provide a clear and structured explanation of why it was not followed as well as the file and line number when that happened.

Return your review in a clear and structured JSON format.

```json
[
    {{
        "file": "src/index.js",
        "line": 10,
        "reason": "The function is not following the rule 'Avoid code duplication'"
    }}
]
```
"""


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
        selected_rules = []
        for rule in self.rules:
            if rule.filename.startswith("format."):
                continue
            selected_rules.append(rule)

        rules_text = stringify_rules(selected_rules)
        changes_text = stringify_code_changes(cr.changes)
        prompt = PROMPT.format(rules_text=rules_text, cr=cr, changes_text=changes_text)

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
