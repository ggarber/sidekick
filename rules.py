import os
from dataclasses import dataclass
from typing import List


@dataclass
class Rule:
    filename: str
    description: str
    globs: str
    alwaysApply: str
    content: str


def parse_rule_file(filepath: str) -> Rule:
    """Parse a single rule file and return a Rule object."""
    with open(filepath, "r") as f:
        content = f.read()

    # Parse YAML front matter
    if not content.startswith("---"):
        return Rule(
            filename=os.path.basename(filepath),
            description="",
            globs="",
            alwaysApply="",
            content=content,
        )

    yaml_end = content.find("---", 3)
    if yaml_end == -1:
        return Rule(
            filename=os.path.basename(filepath),
            description="",
            globs="",
            alwaysApply="",
            content=content,
        )

    yaml_content = content[3:yaml_end].strip()
    rule_content = content[yaml_end + 3 :].strip()

    # Parse YAML fields
    description = ""
    globs = ""
    alwaysApply = ""

    for line in yaml_content.split("\n"):
        if line.startswith("description:"):
            description = line.split(":", 1)[1].strip()
        elif line.startswith("globs:"):
            globs = line.split(":", 1)[1].strip()
        elif line.startswith("alwaysApply:"):
            alwaysApply = line.split(":", 1)[1].strip()

    return Rule(
        filename=os.path.basename(filepath),
        description=description,
        globs=globs,
        alwaysApply=alwaysApply,
        content=rule_content,
    )


def load_rules_from_dir(directory: str) -> List[Rule]:
    """Load all rule files from a directory.

    Args:
        directory: Path to the directory containing rule files

    Returns:
        List of Rule objects
    """
    rules = []
    if os.path.exists(directory) and os.path.isdir(directory):
        for filename in os.listdir(directory):
            filepath = os.path.join(directory, filename)
            if os.path.isfile(filepath):
                rules.append(parse_rule_file(filepath))
    return rules


def load_rules(rules_path: str = None) -> List[Rule]:
    """Load rules from specified path or default locations.

    Args:
        rules_path: Optional path to a rules file or directory

    Returns:
        List of Rule objects
    """
    # If path is specified, load from that location
    if rules_path:
        if os.path.isfile(rules_path):
            return [parse_rule_file(rules_path)]
        elif os.path.isdir(rules_path):
            return load_rules_from_dir(rules_path)
        return []

    # No path specified, load from default locations
    # First try to load from .sidekick directory
    sidekick_rules = load_rules_from_dir(".sidekick")
    if sidekick_rules:
        return sidekick_rules

    # If .sidekick doesn't exist, try .cursor/rules directory
    cursor_rules = load_rules_from_dir(".cursor/rules")

    # Load from .cursorrules file if it exists
    if os.path.exists(".cursorrules") and os.path.isfile(".cursorrules"):
        cursor_rules.append(parse_rule_file(".cursorrules"))

    return cursor_rules
