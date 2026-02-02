"""VersionBumpService for conventional commit analysis.

This application service analyzes git commits following the Conventional Commits
specification to determine appropriate semantic version bumps.
"""

import re

from crafter_ai.installer.domain.candidate_version import (
    BumpType,
    CandidateVersion,
    create_candidate,
)
from crafter_ai.installer.ports.git_port import GitPort


class VersionBumpService:
    """Service for analyzing commits and determining version bumps.

    This is an application service that orchestrates domain objects (CandidateVersion)
    and ports (GitPort) to determine version bumps based on Conventional Commits.

    Conventional Commits spec:
        - feat!: or BREAKING CHANGE: footer -> MAJOR bump
        - feat: -> MINOR bump
        - fix: -> PATCH bump
        - Other prefixes (docs:, chore:, etc.) -> no bump
    """

    # Priority order for bump types (highest first)
    _BUMP_PRIORITY = {
        BumpType.MAJOR: 3,
        BumpType.MINOR: 2,
        BumpType.PATCH: 1,
        BumpType.NONE: 0,
    }

    # Regex patterns for conventional commits
    _BREAKING_PATTERN = re.compile(r"^[a-z]+!:")
    _BREAKING_FOOTER_PATTERN = re.compile(r"BREAKING CHANGE:", re.MULTILINE)
    _FEAT_PATTERN = re.compile(r"^feat:")
    _FIX_PATTERN = re.compile(r"^fix:")

    def __init__(self, git_port: GitPort) -> None:
        """Initialize VersionBumpService with a GitPort.

        Args:
            git_port: GitPort implementation for accessing git operations.
        """
        self._git_port = git_port
        self._analyzed_commits: list[str] = []

    def analyze_commits(self, since_tag: str | None = None) -> list[str]:
        """Retrieve and store commit messages since the specified tag.

        If since_tag is None, uses the latest tag from the repository.

        Args:
            since_tag: Tag to start from, or None to use latest tag.

        Returns:
            List of commit messages since the tag.
        """
        tag = since_tag
        if tag is None:
            tag = self._git_port.get_latest_tag()

        if tag is None:
            self._analyzed_commits = []
            return []

        self._analyzed_commits = self._git_port.get_commits_since_tag(tag)
        return self._analyzed_commits

    def determine_bump_type(self, commits: list[str]) -> BumpType:
        """Determine the version bump type from commit messages.

        Analyzes each commit following Conventional Commits spec:
            - feat!: or BREAKING CHANGE: -> MAJOR
            - feat: -> MINOR
            - fix: -> PATCH
            - Other -> NONE

        Returns the highest bump type found across all commits.

        Args:
            commits: List of commit messages to analyze.

        Returns:
            The highest BumpType determined from commits.
        """
        if not commits:
            return BumpType.NONE

        highest_bump = BumpType.NONE

        for commit in commits:
            bump = self._analyze_single_commit(commit)
            if self._BUMP_PRIORITY[bump] > self._BUMP_PRIORITY[highest_bump]:
                highest_bump = bump
                # Short-circuit if we already found MAJOR
                if highest_bump == BumpType.MAJOR:
                    break

        return highest_bump

    def _analyze_single_commit(self, commit: str) -> BumpType:
        """Analyze a single commit message for bump type.

        Args:
            commit: Single commit message to analyze.

        Returns:
            BumpType for this commit.
        """
        # Check for breaking changes first (highest priority)
        if self._BREAKING_PATTERN.match(commit):
            return BumpType.MAJOR
        if self._BREAKING_FOOTER_PATTERN.search(commit):
            return BumpType.MAJOR

        # Check for feat (MINOR)
        if self._FEAT_PATTERN.match(commit):
            return BumpType.MINOR

        # Check for fix (PATCH)
        if self._FIX_PATTERN.match(commit):
            return BumpType.PATCH

        # Other prefixes (docs, chore, style, etc.)
        return BumpType.NONE

    def create_version_candidate(
        self,
        current_version: str,
        prerelease: str | None = None,
    ) -> CandidateVersion:
        """Create a version candidate based on analyzed commits.

        Uses the stored commits from the last analyze_commits call
        to determine bump type and create the candidate.

        Args:
            current_version: Current version string (e.g., '1.2.3').
            prerelease: Optional prerelease suffix (e.g., 'dev1', 'rc1').

        Returns:
            CandidateVersion with calculated next version.
        """
        bump_type = self.determine_bump_type(self._analyzed_commits)
        return create_candidate(
            current=current_version,
            bump_type=bump_type,
            commits=self._analyzed_commits,
            prerelease=prerelease,
        )
