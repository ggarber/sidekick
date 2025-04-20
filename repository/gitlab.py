import os
import requests
from typing import Dict, List, Optional
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
        """Get merge request diff from GitLab.

        Args:
            project_id: The project ID
            request_id: The merge request ID

        Returns:
            Dict containing the merge request details and changes
        """
        url = urljoin(
            self.host,
            f"/api/v4/projects/{project_id}/merge_requests/{request_id}/changes",
        )

        response = requests.get(url, headers=self.headers)
        response.raise_for_status()

        return response.json()

    def get_code_request(self, project_id: int, mr_id: int) -> CodeRequest:
        """Get merge request details and create a CodeRequest object."""
        url = f"{self.host}/api/v4/projects/{project_id}/merge_requests/{mr_id}"

        headers = {"PRIVATE-TOKEN": self.token}

        response = requests.get(url, headers=headers)
        response.raise_for_status()

        mr_data = response.json()
        data = self.get_merge_request_changes(project_id, mr_id)

        # Format changes to match CodeRequest model
        formatted_changes = []
        for change in data["changes"]:
            formatted_changes.append(
                CodeChange(path=change["new_path"], diff=change["diff"])
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
        """Post a comment on a merge request using the GitLab API.

        Args:
            project_id: The ID of the GitLab project
            mr_id: The ID of the merge request
            comment: The comment text to post

        Raises:
            requests.exceptions.RequestException: If the API request fails
        """
        url = f"{self.host}/api/v4/projects/{project_id}/merge_requests/{mr_id}/notes"

        headers = {"PRIVATE-TOKEN": self.token, "Content-Type": "application/json"}

        data = {"body": comment}

        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()  # Raise exception for non-200 status codes

    def post_merge_request_discussion(
        self, project_id: int, mr_id: int, comment: str
    ) -> None:
        """Post a merge request comment using the GitLab API.

        Args:
            project_id: The ID of the GitLab project
            mr_id: The ID of the merge request
            comment: The comment text to post

        Raises:
            requests.exceptions.RequestException: If the API request fails
        """
        url = f"{self.host}/api/v4/projects/{project_id}/merge_requests/{mr_id}/discussions"

        headers = {"PRIVATE-TOKEN": self.token, "Content-Type": "application/json"}

        data = {"body": comment}

        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()  # Raise exception for non-200 status codes

    def label_merge_request(
        self, project_id: int, mr_id: int, labels: List[str]
    ) -> None:
        """Label a merge request using the GitLab API.

        Args:
            project_id: The ID of the GitLab project
            mr_id: The ID of the merge request
            labels: The list of labels to add

        Raises:
            requests.exceptions.RequestException: If the API request fails
        """
        url = f"{self.host}/api/v4/projects/{project_id}/merge_requests/{mr_id}"

        headers = {"PRIVATE-TOKEN": self.token, "Content-Type": "application/json"}

        data = {"add_labels": labels}

        response = requests.put(url, headers=headers, json=data)
        response.raise_for_status()
