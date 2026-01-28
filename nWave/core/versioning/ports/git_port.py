"""
GitPort - Port interface for Git operations.

HEXAGONAL ARCHITECTURE:
This is a PORT (abstract interface at hexagon boundary).
- Defines contract for git operations (branch info, commit state, repo root)
- Adapters implement this interface for actual git command execution
- Domain/Application layers depend on this abstraction, not concrete implementations

Methods:
- get_current_branch(): Get the current branch name
- has_uncommitted_changes(): Check if there are uncommitted changes
- get_repo_root(): Get the repository root directory path
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path


class GitError(Exception):
    """
    Raised when a git operation fails.

    This exception indicates a failure in git operations, such as:
    - Not being in a git repository
    - Git command execution failures
    - Detached HEAD state when branch name is required

    Example:
        >>> raise GitError("Not a git repository")
        GitError: Not a git repository
    """

    pass


class GitPort(ABC):
    """
    Abstract port interface for git operations.

    This port defines the contract for all git interactions
    required by the versioning domain. Adapters implement this interface
    to provide actual git command execution.

    HEXAGONAL ARCHITECTURE:
    - This is a PORT (hexagon boundary interface)
    - Mocking allowed ONLY at this boundary
    - Used by BuildService and ReleaseService for branch info

    Example:
        >>> class GitAdapter(GitPort):
        ...     def get_current_branch(self) -> str:
        ...         # Execute: git branch --show-current
        ...         return "main"
        ...
        ...     def has_uncommitted_changes(self) -> bool:
        ...         # Execute: git status --porcelain
        ...         return False
        ...
        ...     def get_repo_root(self) -> Path:
        ...         # Execute: git rev-parse --show-toplevel
        ...         return Path("/path/to/repo")
    """

    @abstractmethod
    def get_current_branch(self) -> str:
        """
        Get the name of the current git branch.

        Returns:
            str: The current branch name (e.g., "main", "feature/new-agent")

        Raises:
            GitError: If not in a git repository or HEAD is detached
        """
        ...

    @abstractmethod
    def has_uncommitted_changes(self) -> bool:
        """
        Check if there are uncommitted changes in the working directory.

        This includes both staged and unstaged changes. Untracked files
        are not considered uncommitted changes.

        Returns:
            bool: True if there are uncommitted changes, False otherwise

        Raises:
            GitError: If not in a git repository
        """
        ...

    @abstractmethod
    def get_repo_root(self) -> Path:
        """
        Get the root directory of the git repository.

        Returns:
            Path: Absolute path to the repository root directory

        Raises:
            GitError: If not in a git repository
        """
        ...
