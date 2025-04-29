from abc import ABC, abstractmethod
from repository.code_request import CodeRequest
from typing import List


class Repository(ABC):
    """Abstract base class for repository implementations."""

    @abstractmethod
    def get_code_request(self, project_id: int, request_id: int) -> CodeRequest:
        """Get formatted changes from a code request.

        Args:
            project_id: The project ID
            request_id: The request ID

        Returns:
            List of dictionaries containing file changes
        """
        pass

    @abstractmethod
    def post_comment(self, project_id: int, mr_id: int, comment: str) -> None:
        """Post a comment on a merge request."""
        pass

    @abstractmethod
    def post_code_request_discussion(
        self, project_id: int, mr_id: int, comment: str
    ) -> None:
        """Post a discussion on a code request."""
        pass

    @abstractmethod
    def label_code_request(
        self, project_id: int, mr_id: int, labels: List[str]
    ) -> None:
        """Label a merge request."""
        pass
