"""
GitHubCLIPort - Port interface for GitHub CLI operations.

HEXAGONAL ARCHITECTURE:
This is a PORT (abstract interface at hexagon boundary).
- Defines contract for GitHub CLI operations (PR creation)
- Adapters implement this interface for actual gh CLI execution
- Application layers depend on this abstraction, not concrete implementations

Methods:
- create_pr(): Create a pull request from head to base branch
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional


class GitHubCLIError(Exception):
    """
    Raised when a GitHub CLI operation fails.

    This exception indicates a failure in gh CLI operations, such as:
    - Permission denied
    - Network errors
    - Invalid branch names
    - gh CLI not installed

    Example:
        >>> raise GitHubCLIError("Permission denied")
        GitHubCLIError: Permission denied
    """

    pass


@dataclass(frozen=True)
class PRResult:
    """
    Result of PR creation operation.

    Attributes:
        success: True if PR was created successfully
        pr_number: The PR number (e.g., 123)
        pr_url: The full URL to the PR
        error_message: Error description if success is False
    """

    success: bool
    pr_number: Optional[int]
    pr_url: Optional[str]
    error_message: Optional[str] = None


class GitHubCLIPort(ABC):
    """
    Abstract port interface for GitHub CLI operations.

    This port defines the contract for GitHub CLI interactions
    required by the release functionality. Adapters implement this interface
    to provide actual gh CLI command execution.

    HEXAGONAL ARCHITECTURE:
    - This is a PORT (hexagon boundary interface)
    - Mocking allowed ONLY at this boundary
    - Used by ReleaseService for PR creation

    Example:
        >>> class GitHubCLIAdapter(GitHubCLIPort):
        ...     def create_pr(self, base_branch, head_branch, title) -> PRResult:
        ...         # Execute: gh pr create --base main --head development
        ...         return PRResult(success=True, pr_number=123, pr_url="...")
    """

    @abstractmethod
    def create_pr(self, base_branch: str, head_branch: str, title: str) -> PRResult:
        """
        Create a pull request from head branch to base branch.

        Args:
            base_branch: The target branch (e.g., "main")
            head_branch: The source branch (e.g., "development")
            title: The PR title

        Returns:
            PRResult: Contains success status, PR number, URL, or error message

        Raises:
            GitHubCLIError: If gh CLI is not installed or fails unexpectedly
        """
        ...
