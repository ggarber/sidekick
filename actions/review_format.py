from .base import Action
from providers import LLMProvider, parse_json
from repository import CodeRequest
from colorama import Fore, Style
from rules import Rule
from typing import List
from repository import Repository
from actions.base import ActionResult
from repository import count_tokens, count_tokens_change

PROMPT = """You are a senior software engineer. Review the structure and format of this change according to the following rules:

=== Rules ===
{rules_text}

=== Title ===
{cr.title}

=== Description ===
{cr.description}

=== Changes ===
{changes_text}

For each of the rules defined above report:
- Rule title
- Rule passed or failed
- If it failed, explain why it failed
- If it passed, explain why it passed

Return your review in a clear and structured format using the following JSON schema:
```json
[
    {{
        "rule_title": str,
        "result": str,   # passed or failed
        "explanation": str
    }},
    ...
]
```

"""


class ReviewFormatAction(Action):
    def __init__(
        self,
        provider: LLMProvider,
        repository: Repository,
        rules: List[Rule],
        verbose: bool = False,
    ):
        super().__init__(provider, repository, rules, verbose)

    def run(self, cr: CodeRequest, post: bool = False) -> ActionResult:
        selected_rules = [
            rule for rule in self.rules if rule.filename.startswith("format.")
        ]
        rules_text = "\n".join(f"- {rule.content}" for rule in selected_rules)

        request_tokens = count_tokens(PROMPT + rules_text + cr.title + cr.description)

        if request_tokens > self.provider.max_tokens:
            raise ValueError("Code request is too long to review")

        changes_text = ""
        for change in cr.changes:
            tokens = count_tokens_change(change)
            request_tokens += tokens

            if request_tokens < self.provider.max_tokens:
                changes_text += f"File: {change.path}\n{change.diff}\n"
            else:
                print(
                    f"{Fore.RED}Skipping change {change.path} because it exceeds the token limit{Style.RESET_ALL}"
                )
                break

        prompt = PROMPT.format(rules_text=rules_text, changes_text=changes_text, cr=cr)

        if self.verbose:
            print(f"\n{Fore.GREEN}Prompt sent to LLM:{Style.RESET_ALL}")
            print(f"{Fore.GREEN}{prompt}{Style.RESET_ALL}\n")

        result = self.provider.completion(prompt)

        if result is None:
            print(
                f"{Fore.RED}Error: No response received from LLM provider{Style.RESET_ALL}"
            )
            return ActionResult(0)

        if self.verbose:
            print(f"\n{Fore.YELLOW}Response from LLM:{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}{result.text}{Style.RESET_ALL}\n")
            if hasattr(result, "tokens_used"):
                print(
                    f"{Fore.YELLOW}Tokens used: {result.tokens_used}{Style.RESET_ALL}\n"
                )

        parsed_results = parse_json(result.text)
        if parsed_results is None:
            print(f"{Fore.RED}Error: Could not parse JSON response{Style.RESET_ALL}")
            return ActionResult(
                result.tokens_used if hasattr(result, "tokens_used") else 0
            )

        if post:
            self.post_result(cr, parsed_results)

        return ActionResult(result.tokens_used if hasattr(result, "tokens_used") else 0)

    def post_result(self, cr: CodeRequest, results: List[dict]) -> None:
        """Post review results as a comment on the merge request."""
        if self.verbose:
            print(
                f"\n{Fore.WHITE}Posting review results as comment...{Style.RESET_ALL}"
            )

        comment = "# Code Review Results\n\n"
        failed = [result for result in results if result["result"] != "passed"]

        comment += f"Rules passed: {len(results)-len(failed)}/{len(results)}\n\n"

        for rule in results:
            if rule.get("result") != "passed":
                comment += f"❌ {rule.get('rule_title')}\n{rule.get('explanation')}\n\n"

        self.repository.post_comment(cr.project_id, cr.mr_id, comment)

        if self.verbose:
            print(f"{Fore.WHITE}Results posted successfully{Style.RESET_ALL}")
