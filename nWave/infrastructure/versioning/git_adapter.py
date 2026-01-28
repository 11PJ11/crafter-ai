"""
GitAdapter - Infrastructure adapter for Git operations.

Implements GitPort interface for actual git command execution.

HEXAGONAL ARCHITECTURE:
- This is an INFRASTRUCTURE ADAPTER (outside the hexagon)
- Implements GitPort abstract interface
- Uses subprocess to execute git commands
"""

from __future__ import annotations

import subprocess
from pathlib import Path

from nWave.core.versioning.ports.git_port import GitError, GitPort


class GitAdapter(GitPort):
    """
    Infrastructure adapter for git operations.

    Implements GitPort interface by executing git commands via subprocess.

    Example:
        >>> adapter = GitAdapter()
        >>> branch = adapter.get_current_branch()
        >>> print(f"On branch: {branch}")
    """

    def get_current_branch(self) -> str:
        """
        Get the name of the current git branch.

        Returns:
            str: The current branch name (e.g., "main", "feature/new-agent")

        Raises:
            GitError: If not in a git repository or HEAD is detached
        """
        try:
            result = subprocess.run(
                ["git", "branch", "--show-current"],
                capture_output=True,
                text=True,
                check=False,
            )

            if result.returncode != 0:
                raise GitError(f"Git error: {result.stderr.strip()}")

            branch = result.stdout.strip()
            if not branch:
                raise GitError("Detached HEAD state - no branch name available")

            return branch

        except FileNotFoundError:
            raise GitError("Git is not installed or not in PATH")

    def has_uncommitted_changes(self) -> bool:
        """
        Check if there are uncommitted changes in the working directory.

        Returns:
            bool: True if there are uncommitted changes, False otherwise

        Raises:
            GitError: If not in a git repository
        """
        try:
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                capture_output=True,
                text=True,
                check=False,
            )

            if result.returncode != 0:
                raise GitError(f"Git error: {result.stderr.strip()}")

            # If there's output, there are uncommitted changes
            return bool(result.stdout.strip())

        except FileNotFoundError:
            raise GitError("Git is not installed or not in PATH")

    def get_repo_root(self) -> Path:
        """
        Get the root directory of the git repository.

        Returns:
            Path: Absolute path to the repository root directory

        Raises:
            GitError: If not in a git repository
        """
        try:
            result = subprocess.run(
                ["git", "rev-parse", "--show-toplevel"],
                capture_output=True,
                text=True,
                check=False,
            )

            if result.returncode != 0:
                raise GitError(f"Git error: {result.stderr.strip()}")

            return Path(result.stdout.strip())

        except FileNotFoundError:
            raise GitError("Git is not installed or not in PATH")
