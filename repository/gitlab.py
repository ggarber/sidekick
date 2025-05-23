import os
import requests
from typing import Dict, List, Any
from urllib.parse import urljoin
from .base import Repository
from repository.code_request import CodeRequest, CodeChange


class GitLabRepository(Repository):
    """Class to download merge request diffs from GitLab."""

    def __init__(self):
        self.token = os.getenv("GITLAB_TOKEN")
        self.host = os.getenv("GITLAB_HOST", "https://gitlab.com")

        if not self.token:
            raise ValueError("GITLAB_TOKEN environment variable is required")

        self.headers = {"PRIVATE-TOKEN": self.token, "Content-Type": "application/json"}

    def get_merge_request_changes(self, project_id: int, request_id: int) -> Dict:
        url = urljoin(
            self.host,
            f"/api/v4/projects/{project_id}/merge_requests/{request_id}/changes",
        )

        response = requests.get(url, headers=self.headers)
        response.raise_for_status()

        return response.json()

    def get_code_request(self, project_id: int, mr_id: int) -> CodeRequest:
        url = f"{self.host}/api/v4/projects/{project_id}/merge_requests/{mr_id}"

        response = requests.get(url, headers=self.headers)
        response.raise_for_status()

        mr_data = response.json()
        data = self.get_merge_request_changes(project_id, mr_id)
        diff_refs = data["diff_refs"]
        # Format changes to match CodeRequest model
        formatted_changes = []
        for change in data["changes"]:
            formatted_changes.append(
                CodeChange(
                    path=change["new_path"],
                    diff=change["diff"],
                    base_sha=diff_refs["base_sha"],
                    start_sha=diff_refs["start_sha"],
                    head_sha=diff_refs["head_sha"],
                )
            )

        return CodeRequest(
            title=mr_data["title"],
            description=mr_data["description"] or "",
            changes=formatted_changes,
            project_id=project_id,
            mr_id=mr_id,
            base_branch=mr_data["target_branch"],
        )

    def post_comment(self, project_id: int, mr_id: int, comment: str) -> None:
        url = f"{self.host}/api/v4/projects/{project_id}/merge_requests/{mr_id}/notes"
        headers = {**self.headers, "Content-Type": "application/json"}

        data = {"body": comment}

        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()  # Raise exception for non-200 status codes

    def post_code_request_discussion(
        self, project_id: int, mr_id: int, comment: str,
        position: Dict[str, Any]
    ) -> None:
        url = f"{self.host}/api/v4/projects/{project_id}/merge_requests/{mr_id}/discussions"

        headers = {**self.headers, "Content-Type": "application/json"}
        
        data = {
            "body": comment,
            "base_sha": position["base_sha"],
            "start_sha": position["start_sha"],
            "head_sha": position["head_sha"],
            "position_type": "text",
            "old_path": position["old_path"],
            "new_path": position["new_path"],
            "old_line": None, #position["old_line"],
            "new_line": str(position["new_line"]),
        }

        # print(" GET ", requests.get(url, headers=headers).json())
        # print(data)
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()  # Raise exception for non-200 status codes

    def label_code_request(
        self, project_id: int, mr_id: int, labels: List[str]
    ) -> None:
        url = f"{self.host}/api/v4/projects/{project_id}/merge_requests/{mr_id}"

        headers = {**self.headers, "Content-Type": "application/json"}

        data = {"add_labels": labels}

        response = requests.put(url, headers=headers, json=data)
        response.raise_for_status()
