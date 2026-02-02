"""
Mock GitPort for Acceptance Tests
=================================

Provides controlled Git behavior for testing version bumping
and conventional commit analysis.

Port Interface: nWave/core/installer/ports/git_port.py
"""

from dataclasses import dataclass, field
from typing import List, Optional, Protocol


class GitPort(Protocol):
    """
    Port interface for Git operations.

    Abstracts Git commands for testability.
    """

    def get_current_branch(self) -> str:
        """Get current branch name."""
        ...

    def get_commits_since_tag(self, tag: str) -> List[str]:
        """Get commit messages since tag."""
        ...

    def get_latest_tag(self) -> Optional[str]:
        """Get latest version tag."""
        ...

    def has_uncommitted_changes(self) -> bool:
        """Check for uncommitted changes."""
        ...


@dataclass
class MockGitAdapter:
    """
    Mock implementation of GitPort for testing.

    Provides controlled Git behavior for version bumping
    and conventional commit analysis tests.
    """

    # Current branch
    current_branch: str = "installer"

    # Commit history since last tag
    commits_since_tag: List[str] = field(default_factory=list)

    # Latest tag
    latest_tag: Optional[str] = "v1.2.0"

    # Uncommitted changes flag
    uncommitted_changes: bool = False

    # Error simulation
    raise_on_tag_fetch: bool = False

    def get_current_branch(self) -> str:
        """Return configured branch name."""
        return self.current_branch

    def get_commits_since_tag(self, tag: str) -> List[str]:
        """Return configured commit messages."""
        return self.commits_since_tag

    def get_latest_tag(self) -> Optional[str]:
        """Return configured latest tag."""
        if self.raise_on_tag_fetch:
            raise RuntimeError("No tags found in repository")
        return self.latest_tag

    def has_uncommitted_changes(self) -> bool:
        """Return configured uncommitted changes status."""
        return self.uncommitted_changes

    # Test setup helpers

    def setup_feature_commits(self) -> None:
        """Configure mock with feature commits (MINOR bump)."""
        self.commits_since_tag = [
            "feat: add Luna agent for UX design",
            "docs: update installation guide",
            "test: add acceptance tests for build journey",
        ]

    def setup_breaking_change_commits(self) -> None:
        """Configure mock with breaking change commits (MAJOR bump)."""
        self.commits_since_tag = [
            "feat!: redesign CLI API",
            "BREAKING CHANGE: remove deprecated commands",
            "docs: update migration guide",
        ]

    def setup_fix_commits(self) -> None:
        """Configure mock with fix-only commits (PATCH bump)."""
        self.commits_since_tag = [
            "fix: correct typo in config loading",
            "fix: handle edge case in version parsing",
            "chore: update dependencies",
        ]

    def setup_no_commits_since_tag(self) -> None:
        """Configure mock with no commits since last tag."""
        self.commits_since_tag = []

    def setup_no_tags(self) -> None:
        """Configure mock with no tags in repository."""
        self.latest_tag = None
        self.commits_since_tag = [
            "feat: initial implementation",
            "docs: add README",
        ]

    def setup_dirty_working_tree(self) -> None:
        """Configure mock with uncommitted changes."""
        self.uncommitted_changes = True


def create_git_mock_for_minor_bump() -> MockGitAdapter:
    """Factory: Create mock configured for MINOR version bump."""
    mock = MockGitAdapter()
    mock.setup_feature_commits()
    return mock


def create_git_mock_for_major_bump() -> MockGitAdapter:
    """Factory: Create mock configured for MAJOR version bump."""
    mock = MockGitAdapter()
    mock.setup_breaking_change_commits()
    return mock


def create_git_mock_for_patch_bump() -> MockGitAdapter:
    """Factory: Create mock configured for PATCH version bump."""
    mock = MockGitAdapter()
    mock.setup_fix_commits()
    return mock
