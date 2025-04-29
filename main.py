import os
import argparse
from dotenv import load_dotenv
from colorama import init, Fore, Style
from providers import (
    OpenAIProvider,
    AnthropicProvider,
    GoogleProvider,
    BedrockProvider,
    LLMProvider,
)
from repository.code_request import CodeRequest
from repository import Repository, GitLabRepository
from actions import (
    ReviewCodeAction,
    ReviewFormatAction,
    SummarizeAction,
    LabelAction,
    Action,
)
from rules import load_rules

# Initialize colorama
init()

# Load environment variables
load_dotenv()


def get_provider() -> LLMProvider:
    provider_name = os.getenv("PROVIDER", "openai").lower()

    providers = {
        "openai": OpenAIProvider,
        "anthropic": AnthropicProvider,
        "google": GoogleProvider,
        "bedrock": BedrockProvider,
    }

    if provider_name not in providers:
        raise ValueError(
            f"Invalid provider '{provider_name}'. "
            f"Must be one of: {', '.join(providers.keys())}"
        )

    return providers[provider_name]()


def get_repository() -> Repository:
    repository_type = os.getenv("REPOSITORY", "gitlab").lower()

    repositories = {"gitlab": GitLabRepository}

    if repository_type not in repositories:
        raise ValueError(
            f"Invalid repository type '{repository_type}'. "
            f"Must be one of: {', '.join(repositories.keys())}"
        )

    return repositories[repository_type]()


def get_action(
    action_name: str,
    provider: LLMProvider,
    repository: Repository,
    rules: list,
    verbose: bool = False,
) -> Action:
    actions = {
        "review_code": ReviewCodeAction,
        "review_format": ReviewFormatAction,
        "label": LabelAction,
        "summarize": SummarizeAction,
    }

    if action_name not in actions:
        raise ValueError(
            f"Invalid action '{action_name}'. "
            f"Must be one of: {', '.join(actions.keys())}"
        )

    return actions[action_name](provider, repository, rules, verbose)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="AI-powered GitLab merge request tools"
    )
    parser.add_argument(
        "actions",
        help="Comma-separated list of actions to perform (review_code,review_format,label,summarize)",
    )
    parser.add_argument("project_id", type=int, help="GitLab project ID")
    parser.add_argument("cr_id", type=int, help="Merge/Pull request ID")
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Enable verbose output with colors"
    )
    parser.add_argument(
        "-r", "--rules", help="Optional path to rules file or directory"
    )
    parser.add_argument(
        "-p", "--post", action="store_true", help="Post results to merge/pull request"
    )
    parser.add_argument(
        "-t", "--tag", action="store_true", help="Tag merge/pull request and avoid duplication"
    )
    args = parser.parse_args()

    try:
        # Parse actions
        action_names = [action.strip() for action in args.actions.split(",")]

        # Validate actions
        valid_actions = ["review_code", "review_format", "label", "summarize"]
        invalid_actions = [
            action for action in action_names if action not in valid_actions
        ]
        if invalid_actions:
            raise ValueError(
                f"Invalid action(s): {', '.join(invalid_actions)}. "
                f"Must be one of: {', '.join(valid_actions)}"
            )

        repository = get_repository()
        code_request = repository.get_code_request(args.project_id, args.cr_id)

        if args.verbose:
            print(f"\n{Fore.WHITE}Changes from repository:{Style.RESET_ALL}")
            for change in code_request.changes:
                print(f"\n{Fore.WHITE}File: {change.path}{Style.RESET_ALL}")
                print(f"{Fore.WHITE}{change.diff}{Style.RESET_ALL}")

        rules = load_rules(args.rules)

        print(
            f"{Fore.WHITE}Loaded {len(rules)} rules from {'rules'if args.rules else 'default'} locations{Style.RESET_ALL}"
        )

        provider = get_provider()

        total_tokens_used = 0
        # Run each action
        for action_name in action_names:
            print(f"\n{Fore.WHITE}Running action: {action_name}{Style.RESET_ALL}")

            action = get_action(action_name, provider, repository, rules, args.verbose)
            result = action.run(code_request, args.post)

            total_tokens_used += result.tokens_used

            if args.verbose:
                print(f"\n{Fore.WHITE}Action {action_name} completed{Style.RESET_ALL}")

        if args.tag:
            repository.label_code_request(args.project_id, args.cr_id, ["sidekick"])
        print(f"{Fore.WHITE}Total tokens used: {total_tokens_used}{Style.RESET_ALL}")

    except ValueError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")


if __name__ == "__main__":
    main()
