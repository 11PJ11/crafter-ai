"""
ReleaseService - Application service for release operations.

Orchestrates the release workflow for creating official releases:
1. Validate current branch is development
2. Validate no uncommitted changes
3. Create PR from development to main

HEXAGONAL ARCHITECTURE:
- This is an APPLICATION SERVICE (inside the hexagon)
- Depends only on PORT interfaces, not concrete adapters
- Uses real domain objects, never mocks

Example:
    >>> service = ReleaseService(git=git_adapter, github_cli=gh_adapter)
    >>> result = service.create_release_pr()
    >>> if result.success:
    ...     print(f"PR #{result.pr_number} created")
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Protocol


@dataclass(frozen=True)
class ReleaseResult:
    """
    Result of a release operation.

    Contains the release outcome and PR metadata for display.

    Attributes:
        success: True if release PR was created successfully
        pr_number: The PR number (e.g., 123)
        pr_url: The full URL to the PR
        error_message: Optional error message if release failed
    """

    success: bool
    pr_number: Optional[int]
    pr_url: Optional[str]
    error_message: Optional[str] = None


class GitProtocol(Protocol):
    """Protocol for Git operations - PORT boundary."""

    def get_current_branch(self) -> str: ...
    def has_uncommitted_changes(self) -> bool: ...


class GitHubCLIProtocol(Protocol):
    """Protocol for GitHub CLI operations - PORT boundary."""

    def create_pr(
        self, base_branch: str, head_branch: str, title: str
    ) -> "PRResult": ...


@dataclass(frozen=True)
class PRResult:
    """Result from GitHubCLI create_pr operation."""

    success: bool
    pr_number: Optional[int]
    pr_url: Optional[str]
    error_message: Optional[str] = None


class ReleaseService:
    """
    Application service for release operations.

    Orchestrates the release workflow:
    1. Validate current branch is development
    2. Validate no uncommitted changes
    3. Create PR from development to main via GitHub CLI

    Example:
        >>> service = ReleaseService(git=adapter, github_cli=gh_adapter)
        >>> result = service.create_release_pr()
        >>> if result.success:
        ...     print(f"PR #{result.pr_number}: {result.pr_url}")
    """

    ALLOWED_BRANCH = "development"
    TARGET_BRANCH = "main"

    def __init__(
        self,
        git: GitProtocol,
        github_cli: GitHubCLIProtocol,
    ) -> None:
        """
        Create a ReleaseService.

        Args:
            git: Adapter implementing GitPort
            github_cli: Adapter implementing GitHubCLIPort
        """
        self._git = git
        self._github_cli = github_cli

    def create_release_pr(self) -> ReleaseResult:
        """
        Execute the release workflow.

        Workflow:
        1. Validate current branch is development
        2. Validate no uncommitted changes
        3. Create PR from development to main

        Returns:
            ReleaseResult with success status and PR info
        """
        # Validate preconditions
        validation_error = self._validate_release_preconditions()
        if validation_error:
            return validation_error

        # Create PR from development to main
        return self._create_pr()

    def _validate_release_preconditions(self) -> Optional[ReleaseResult]:
        """
        Validate all preconditions for release.

        Returns:
            ReleaseResult with error if validation fails, None if all pass
        """
        branch_error = self._validate_branch()
        if branch_error:
            return branch_error

        uncommitted_error = self._validate_no_uncommitted_changes()
        if uncommitted_error:
            return uncommitted_error

        return None

    def _validate_branch(self) -> Optional[ReleaseResult]:
        """Validate current branch is development."""
        current_branch = self._git.get_current_branch()
        if current_branch != self.ALLOWED_BRANCH:
            return ReleaseResult(
                success=False,
                pr_number=None,
                pr_url=None,
                error_message="Release must be initiated from the development branch.",
            )
        return None

    def _validate_no_uncommitted_changes(self) -> Optional[ReleaseResult]:
        """Validate no uncommitted changes in working directory."""
        if self._git.has_uncommitted_changes():
            return ReleaseResult(
                success=False,
                pr_number=None,
                pr_url=None,
                error_message="Uncommitted changes detected. Commit or stash changes before releasing.",
            )
        return None

    def _create_pr(self) -> ReleaseResult:
        """Create PR from development to main via GitHub CLI."""
        pr_title = f"Release: {self.ALLOWED_BRANCH} -> {self.TARGET_BRANCH}"
        pr_result = self._github_cli.create_pr(
            base_branch=self.TARGET_BRANCH,
            head_branch=self.ALLOWED_BRANCH,
            title=pr_title,
        )

        if not pr_result.success:
            return ReleaseResult(
                success=False,
                pr_number=None,
                pr_url=None,
                error_message=pr_result.error_message,
            )

        return ReleaseResult(
            success=True,
            pr_number=pr_result.pr_number,
            pr_url=pr_result.pr_url,
        )
