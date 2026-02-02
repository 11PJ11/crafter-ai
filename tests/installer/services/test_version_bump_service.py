"""Tests for VersionBumpService.

Tests conventional commit analysis and version bump determination.
Uses mock GitPort for isolation from actual git operations.
"""

from crafter_ai.installer.domain.candidate_version import BumpType, CandidateVersion
from crafter_ai.installer.ports.git_port import GitPort
from crafter_ai.installer.services.version_bump_service import VersionBumpService


class MockGitPort:
    """Mock implementation of GitPort for testing."""

    def __init__(
        self,
        commits: list[str] | None = None,
        latest_tag: str | None = "v0.1.0",
    ):
        self._commits = commits or []
        self._latest_tag = latest_tag

    def get_current_branch(self) -> str:
        return "main"

    def get_commits_since_tag(self, _tag: str) -> list[str]:
        return self._commits

    def get_latest_tag(self) -> str | None:
        return self._latest_tag

    def get_commit_hash(self, short: bool = True) -> str:
        return "abc1234" if short else "abc1234567890"

    def has_uncommitted_changes(self) -> bool:
        return False

    def is_git_repo(self) -> bool:
        return True


# Verify MockGitPort implements GitPort Protocol
assert isinstance(MockGitPort(), GitPort)


class TestAnalyzeCommits:
    """Tests for analyze_commits method."""

    def test_analyze_commits_calls_git_port_get_commits_since_tag(self):
        """analyze_commits should delegate to git_port.get_commits_since_tag."""
        commits = ["feat: add feature", "fix: bug fix"]
        mock_git = MockGitPort(commits=commits, latest_tag="v0.1.0")
        service = VersionBumpService(mock_git)

        result = service.analyze_commits(since_tag="v0.1.0")

        assert result == commits

    def test_analyze_commits_with_none_uses_latest_tag(self):
        """When since_tag is None, should use latest tag from git_port."""
        commits = ["feat: new feature"]
        mock_git = MockGitPort(commits=commits, latest_tag="v1.0.0")
        service = VersionBumpService(mock_git)

        result = service.analyze_commits(since_tag=None)

        assert result == commits

    def test_analyze_commits_empty_returns_empty_list(self):
        """When no commits exist, should return empty list."""
        mock_git = MockGitPort(commits=[])
        service = VersionBumpService(mock_git)

        result = service.analyze_commits(since_tag="v0.1.0")

        assert result == []


class TestDetermineBumpType:
    """Tests for determine_bump_type method."""

    def test_determine_bump_type_returns_major_for_breaking_change_exclamation(self):
        """feat! commit should trigger MAJOR bump."""
        mock_git = MockGitPort()
        service = VersionBumpService(mock_git)
        commits = ["feat!: remove deprecated API"]

        result = service.determine_bump_type(commits)

        assert result == BumpType.MAJOR

    def test_determine_bump_type_returns_major_for_breaking_change_footer(self):
        """BREAKING CHANGE footer should trigger MAJOR bump."""
        mock_git = MockGitPort()
        service = VersionBumpService(mock_git)
        commits = ["feat: add new API\n\nBREAKING CHANGE: old API removed"]

        result = service.determine_bump_type(commits)

        assert result == BumpType.MAJOR

    def test_determine_bump_type_returns_major_for_fix_with_breaking_change(self):
        """fix!: should trigger MAJOR bump."""
        mock_git = MockGitPort()
        service = VersionBumpService(mock_git)
        commits = ["fix!: change return type"]

        result = service.determine_bump_type(commits)

        assert result == BumpType.MAJOR

    def test_determine_bump_type_returns_minor_for_feat_commit(self):
        """feat: commit should trigger MINOR bump."""
        mock_git = MockGitPort()
        service = VersionBumpService(mock_git)
        commits = ["feat: add new feature"]

        result = service.determine_bump_type(commits)

        assert result == BumpType.MINOR

    def test_determine_bump_type_returns_patch_for_fix_commit(self):
        """fix: commit should trigger PATCH bump."""
        mock_git = MockGitPort()
        service = VersionBumpService(mock_git)
        commits = ["fix: resolve null pointer issue"]

        result = service.determine_bump_type(commits)

        assert result == BumpType.PATCH

    def test_determine_bump_type_returns_none_for_docs_commit(self):
        """docs: commit should trigger NONE bump."""
        mock_git = MockGitPort()
        service = VersionBumpService(mock_git)
        commits = ["docs: update readme"]

        result = service.determine_bump_type(commits)

        assert result == BumpType.NONE

    def test_determine_bump_type_returns_none_for_chore_commit(self):
        """chore: commit should trigger NONE bump."""
        mock_git = MockGitPort()
        service = VersionBumpService(mock_git)
        commits = ["chore: update dependencies"]

        result = service.determine_bump_type(commits)

        assert result == BumpType.NONE

    def test_determine_bump_type_returns_none_for_style_commit(self):
        """style: commit should trigger NONE bump."""
        mock_git = MockGitPort()
        service = VersionBumpService(mock_git)
        commits = ["style: format code"]

        result = service.determine_bump_type(commits)

        assert result == BumpType.NONE

    def test_determine_bump_type_returns_none_for_empty_commits(self):
        """Empty commit list should return NONE."""
        mock_git = MockGitPort()
        service = VersionBumpService(mock_git)

        result = service.determine_bump_type([])

        assert result == BumpType.NONE

    def test_determine_bump_type_takes_highest_bump_major_over_minor(self):
        """When multiple commits, highest bump wins (MAJOR > MINOR)."""
        mock_git = MockGitPort()
        service = VersionBumpService(mock_git)
        commits = ["feat: add feature", "feat!: breaking change"]

        result = service.determine_bump_type(commits)

        assert result == BumpType.MAJOR

    def test_determine_bump_type_takes_highest_bump_minor_over_patch(self):
        """When multiple commits, highest bump wins (MINOR > PATCH)."""
        mock_git = MockGitPort()
        service = VersionBumpService(mock_git)
        commits = ["fix: bug fix", "feat: new feature"]

        result = service.determine_bump_type(commits)

        assert result == BumpType.MINOR

    def test_determine_bump_type_takes_highest_bump_patch_over_none(self):
        """When multiple commits, highest bump wins (PATCH > NONE)."""
        mock_git = MockGitPort()
        service = VersionBumpService(mock_git)
        commits = ["docs: update readme", "fix: bug fix"]

        result = service.determine_bump_type(commits)

        assert result == BumpType.PATCH


class TestCreateVersionCandidate:
    """Tests for create_version_candidate method."""

    def test_create_version_candidate_returns_candidate_version(self):
        """create_version_candidate should return CandidateVersion instance."""
        commits = ["feat: new feature"]
        mock_git = MockGitPort(commits=commits)
        service = VersionBumpService(mock_git)

        result = service.create_version_candidate(
            current_version="1.0.0",
            prerelease=None,
        )

        assert isinstance(result, CandidateVersion)

    def test_create_version_candidate_with_prerelease(self):
        """create_version_candidate should handle prerelease suffix."""
        commits = ["feat: new feature"]
        mock_git = MockGitPort(commits=commits)
        service = VersionBumpService(mock_git)

        result = service.create_version_candidate(
            current_version="1.0.0",
            prerelease="dev1",
        )

        assert result.is_prerelease is True
        assert result.prerelease_suffix == "dev1"


class TestIntegration:
    """Integration tests for full analyze -> determine -> create flow."""

    def test_full_flow_feat_commit_creates_minor_bump(self):
        """Full flow: feat commit should result in minor version bump."""
        commits = ["feat: add awesome feature"]
        mock_git = MockGitPort(commits=commits, latest_tag="v1.2.3")
        service = VersionBumpService(mock_git)

        analyzed = service.analyze_commits(since_tag=None)
        bump_type = service.determine_bump_type(analyzed)
        candidate = service.create_version_candidate("1.2.3")

        assert bump_type == BumpType.MINOR
        assert candidate.current_version == "1.2.3"
        assert candidate.next_version == "1.3.0"
        assert candidate.bump_type == BumpType.MINOR

    def test_full_flow_breaking_change_creates_major_bump(self):
        """Full flow: breaking change should result in major version bump."""
        commits = ["feat!: remove deprecated method"]
        mock_git = MockGitPort(commits=commits, latest_tag="v2.1.5")
        service = VersionBumpService(mock_git)

        analyzed = service.analyze_commits(since_tag=None)
        bump_type = service.determine_bump_type(analyzed)
        candidate = service.create_version_candidate("2.1.5")

        assert bump_type == BumpType.MAJOR
        assert candidate.next_version == "3.0.0"

    def test_full_flow_fix_commit_creates_patch_bump(self):
        """Full flow: fix commit should result in patch version bump."""
        commits = ["fix: resolve memory leak"]
        mock_git = MockGitPort(commits=commits, latest_tag="v0.5.2")
        service = VersionBumpService(mock_git)

        analyzed = service.analyze_commits(since_tag=None)
        bump_type = service.determine_bump_type(analyzed)
        candidate = service.create_version_candidate("0.5.2")

        assert bump_type == BumpType.PATCH
        assert candidate.next_version == "0.5.3"

    def test_full_flow_with_prerelease_suffix(self):
        """Full flow with prerelease should include suffix in version."""
        commits = ["feat: add beta feature"]
        mock_git = MockGitPort(commits=commits)
        service = VersionBumpService(mock_git)

        analyzed = service.analyze_commits(since_tag=None)
        service.determine_bump_type(analyzed)  # Populates internal state
        candidate = service.create_version_candidate("1.0.0", prerelease="rc1")

        assert candidate.next_version == "1.1.0rc1"
        assert candidate.is_prerelease is True
