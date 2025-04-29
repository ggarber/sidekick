from providers import LLMProvider, stringify_code_changes, stringify_rules
from providers.helpers import parse_json
from repository import CodeRequest
from colorama import Fore, Style
from rules import Rule
from repository import Repository
from .base import Action, ActionResult
from typing import List

PROMPT = """Review the following code changes according to these rules:

=== Rules ===
{rules_text}

=== Changes ===
{changes_text}

The lines that were added are marked with a + and the lines that were removed are marked with a -.

Review the rules only for lines starting with a +.

For every rule not followed, provide a clear and structured explanation of why it was not followed as well as the file and line number when that happened.

To calculate the line number use the first number in the range in the header of the diff starting with @@.

Return your review in a clear and structured JSON format.

```json
[
    {{
        "change_number": 1,
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
        # Split code changes into chunks of 1000 lines

        selected_rules = []
        for rule in self.rules:
            # Skip format rules that are used for the review_format action instead
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

        parsed_results = parse_json(result.text)
        if parsed_results is None:
            print(f"{Fore.RED}Error: Could not parse JSON response{Style.RESET_ALL}")
            return ActionResult(
                result.tokens_used if hasattr(result, "tokens_used") else 0
            )

        if post:
            self.post_result(cr, parsed_results)

        return ActionResult(result.tokens_used)

    def post_result(self, cr: CodeRequest, parsed_results: List[dict]) -> None:
        for result in parsed_results:
            change = cr.changes[result["change_number"] - 1]
            position = {
                "base_sha": change.base_sha,
                "start_sha": change.start_sha,
                "head_sha": change.head_sha,
                "old_path": change.path,
                "new_path": change.path,
                "old_line": result["line"],
                "new_line": result["line"],
            }
            self.repository.post_code_request_discussion(
                cr.project_id,
                cr.mr_id,
                result["reason"],
                position,
            )
