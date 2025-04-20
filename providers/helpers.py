import json5
import re
from typing import Any, Optional


def parse_json(text: str) -> Optional[Any]:
    if "```json" in text:
        text = text.split("```json")[1]
        text = text.split("```")[0]

    # Looks for a json object in the text
    # and returns it as a python object
    match = re.search(
        r"[\{\[].*[\}\]]", text.strip(), re.MULTILINE | re.IGNORECASE | re.DOTALL
    )
    if not match or not match.group(0):
        raise Exception("No json object found")

    return json5.loads(match.group(0), strict=False)
