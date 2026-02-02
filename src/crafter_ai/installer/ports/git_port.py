"""GitPort Protocol - abstract interface for git operations.

This is a hexagonal architecture port that defines how the application
accesses git repository information. Adapters implement this protocol
for different execution mechanisms (subprocess, libgit2, etc.).
"""

from typing import Protocol, runtime_checkable


@runtime_checkable
class GitPort(Protocol):
    """Protocol defining git operations interface.

    This is a hexagonal port - the application depends on this interface,
    not on concrete implementations. Adapters (like SubprocessGitAdapter)
    implement this protocol.

    Used by:
        - VersionBumpService for conventional commit analysis
        - build_checks for clean git status verification
    """

    def get_current_branch(self) -> str:
        """Return the current git branch name.

        Returns:
            The name of the current branch (e.g., 'main', 'feature/foo').
        """
        ...

    def get_commits_since_tag(self, tag: str) -> list[str]:
        """Return commit messages since the specified tag.

        Args:
            tag: The git tag to start from (e.g., 'v0.1.0').

        Returns:
            List of commit messages from tag to HEAD.
        """
        ...

    def get_latest_tag(self) -> str | None:
        """Return the most recent tag in the repository.

        Returns:
            The latest tag name, or None if no tags exist.
        """
        ...

    def get_commit_hash(self, short: bool = True) -> str:
        """Return the current commit hash.

        Args:
            short: If True, return short hash (7 chars). If False, full hash.

        Returns:
            The commit hash string.
        """
        ...

    def has_uncommitted_changes(self) -> bool:
        """Check if there are uncommitted changes in the working tree.

        Returns:
            True if there are uncommitted changes, False if clean.
        """
        ...

    def is_git_repo(self) -> bool:
        """Check if the current directory is inside a git repository.

        Returns:
            True if inside a git repo, False otherwise.
        """
        ...
