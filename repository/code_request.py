from typing import List
from pydantic import BaseModel


class CodeChange(BaseModel):
    """Model representing a file change in a code request."""

    path: str
    diff: str


class CodeRequest:
    def __init__(
        self,
        title: str,
        description: str,
        changes: List[CodeChange],
        project_id: int,
        mr_id: int,
        base_branch: str,
    ):
        self.title = title
        self.description = description
        self.changes = changes
        self.project_id = project_id
        self.mr_id = mr_id
        self.base_branch = base_branch

