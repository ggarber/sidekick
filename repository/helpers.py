from repository.code_request import CodeRequest, CodeChange
import tiktoken
from typing import List


def count_tokens(text: str) -> int:
    """Count the number of tokens in a text using tiktoken."""
    encoder = tiktoken.get_encoding("cl100k_base")  # Using OpenAI's common encoder
    return len(encoder.encode(text))


def count_tokens_change(change: CodeChange) -> int:
    """Count the number of tokens in a change."""
    return count_tokens(change.path) + count_tokens(change.diff)


def count_tokens_cr(cr: CodeRequest) -> int:
    """Count the number of tokens in a CodeRequest."""
    changes_text = "\n".join(
        f"File: {change.path}\n{change.diff}\n" for change in cr.changes
    )
    return (
        count_tokens(cr.title)
        + count_tokens(cr.description)
        + count_tokens(changes_text)
    )


def split(cr: CodeRequest, max_tokens: int) -> List[CodeRequest]:
    """
    Split a CodeRequest into multiple CodeRequests if the changes exceed the token limit.

    Args:
        cr: The original CodeRequest
        max_tokens: Maximum number of tokens allowed per request (default: 10000)

    Returns:
        List of CodeRequests, each containing a portion of the changes
    """
    if count_tokens(cr.changes) <= max_tokens:
        return [cr]

    # Split changes into individual files/hunks
    changes_sections = cr.changes.split("diff --git ")
    current_changes = ""
    current_tokens = 0
    split_requests = []
    part = 1

    for section in changes_sections:
        if not section.strip():
            continue

        # Add "diff --git" back to all sections except the first empty one
        section = "diff --git " + section if section else section
        section_tokens = count_tokens(section)

        # If adding this section would exceed the token limit,
        # create a new CodeRequest
        if current_tokens + section_tokens > max_tokens and current_changes:
            new_request = CodeRequest(
                title=f"{cr.title} (Part {part})",
                description=f"{cr.description}\n(Part {part} of split request)",
                changes=current_changes.strip(),
            )
            split_requests.append(new_request)
            current_changes = ""
            current_tokens = 0
            part += 1

        current_changes += section
        current_tokens += section_tokens

    # Add the last batch of changes
    if current_changes:
        new_request = CodeRequest(
            title=f"{cr.title} (Part {part})",
            description=f"{cr.description}\n(Part {part} of split request)",
            changes=current_changes.strip(),
        )
        split_requests.append(new_request)

    return split_requests
