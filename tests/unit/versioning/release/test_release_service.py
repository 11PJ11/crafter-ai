"""
Unit tests for ReleaseService - Application service for release operations.

HEXAGONAL ARCHITECTURE:
- Tests use REAL domain objects (no mocks inside hexagon)
- Mocks only at PORT boundaries (GitPort, GitHubCLIPort)
- ReleaseService orchestrates PR creation workflow

Test coverage:
- test_release_service_creates_pr: Core PR creation workflow
- test_release_service_validates_branch: Must be on development branch
"""

from dataclasses import dataclass
from typing import Optional, Protocol
from unittest.mock import Mock


# ============================================================================
# Port Protocols (for mocking at boundaries)
# ============================================================================


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
    """Result of PR creation operation."""

    success: bool
    pr_number: Optional[int]
    pr_url: Optional[str]
    error_message: Optional[str] = None


# ============================================================================
# Unit Tests for ReleaseService
# ============================================================================


class TestReleaseServiceCreatesPR:
    """
    Test: ReleaseService creates PR from development to main.

    Acceptance Criteria:
    - PR is created from development to main via gh CLI
    - Output displays the PR number and URL
    """

    def test_release_service_creates_pr_from_development_branch(self):
        """
        GIVEN: On development branch with no uncommitted changes
        WHEN: ReleaseService.create_release_pr() is called
        THEN: PR is created from development to main
        """
        # Arrange - Mock port boundaries
        mock_git = Mock(spec=GitProtocol)
        mock_git.get_current_branch.return_value = "development"
        mock_git.has_uncommitted_changes.return_value = False

        mock_github_cli = Mock(spec=GitHubCLIProtocol)
        mock_github_cli.create_pr.return_value = PRResult(
            success=True,
            pr_number=123,
            pr_url="https://github.com/UndeadGrishnackh/crafter-ai/pull/123",
        )

        # Act - Import and use the service (will fail until implemented)
        from nWave.core.versioning.application.release_service import ReleaseService

        service = ReleaseService(git=mock_git, github_cli=mock_github_cli)
        result = service.create_release_pr()

        # Assert
        assert result.success is True
        assert result.pr_number == 123
        assert (
            result.pr_url == "https://github.com/UndeadGrishnackh/crafter-ai/pull/123"
        )

        # Verify the GitHub CLI was called with correct parameters
        mock_github_cli.create_pr.assert_called_once_with(
            base_branch="main",
            head_branch="development",
            title="Release: development -> main",
        )

    def test_release_service_returns_pr_number_and_url(self):
        """
        GIVEN: Successful PR creation
        WHEN: Result is returned
        THEN: PR number and URL are accessible
        """
        # Arrange
        mock_git = Mock(spec=GitProtocol)
        mock_git.get_current_branch.return_value = "development"
        mock_git.has_uncommitted_changes.return_value = False

        mock_github_cli = Mock(spec=GitHubCLIProtocol)
        mock_github_cli.create_pr.return_value = PRResult(
            success=True,
            pr_number=456,
            pr_url="https://github.com/owner/repo/pull/456",
        )

        # Act
        from nWave.core.versioning.application.release_service import ReleaseService

        service = ReleaseService(git=mock_git, github_cli=mock_github_cli)
        result = service.create_release_pr()

        # Assert
        assert isinstance(result.pr_number, int)
        assert result.pr_number == 456
        assert "pull/456" in result.pr_url


class TestReleaseServiceValidatesBranch:
    """
    Test: ReleaseService validates current branch is development.

    Acceptance Criteria:
    - Release must be initiated from development branch
    """

    def test_release_service_validates_on_development_branch(self):
        """
        GIVEN: On development branch
        WHEN: Branch validation occurs
        THEN: Validation passes and PR creation proceeds
        """
        # Arrange
        mock_git = Mock(spec=GitProtocol)
        mock_git.get_current_branch.return_value = "development"
        mock_git.has_uncommitted_changes.return_value = False

        mock_github_cli = Mock(spec=GitHubCLIProtocol)
        mock_github_cli.create_pr.return_value = PRResult(
            success=True, pr_number=123, pr_url="https://github.com/owner/repo/pull/123"
        )

        # Act
        from nWave.core.versioning.application.release_service import ReleaseService

        service = ReleaseService(git=mock_git, github_cli=mock_github_cli)
        result = service.create_release_pr()

        # Assert - PR creation should have been called
        assert result.success is True
        mock_github_cli.create_pr.assert_called_once()

    def test_release_service_rejects_main_branch(self):
        """
        GIVEN: On main branch (not development)
        WHEN: create_release_pr() is called
        THEN: Error is returned, no PR created
        """
        # Arrange
        mock_git = Mock(spec=GitProtocol)
        mock_git.get_current_branch.return_value = "main"
        mock_git.has_uncommitted_changes.return_value = False

        mock_github_cli = Mock(spec=GitHubCLIProtocol)

        # Act
        from nWave.core.versioning.application.release_service import ReleaseService

        service = ReleaseService(git=mock_git, github_cli=mock_github_cli)
        result = service.create_release_pr()

        # Assert
        assert result.success is False
        assert (
            "Release must be initiated from the development branch"
            in result.error_message
        )
        mock_github_cli.create_pr.assert_not_called()

    def test_release_service_rejects_feature_branch(self):
        """
        GIVEN: On a feature branch (not development)
        WHEN: create_release_pr() is called
        THEN: Error is returned, no PR created
        """
        # Arrange
        mock_git = Mock(spec=GitProtocol)
        mock_git.get_current_branch.return_value = "feature/new-feature"
        mock_git.has_uncommitted_changes.return_value = False

        mock_github_cli = Mock(spec=GitHubCLIProtocol)

        # Act
        from nWave.core.versioning.application.release_service import ReleaseService

        service = ReleaseService(git=mock_git, github_cli=mock_github_cli)
        result = service.create_release_pr()

        # Assert
        assert result.success is False
        assert (
            "Release must be initiated from the development branch"
            in result.error_message
        )
        mock_github_cli.create_pr.assert_not_called()

    def test_release_service_rejects_uncommitted_changes(self):
        """
        GIVEN: On development branch with uncommitted changes
        WHEN: create_release_pr() is called
        THEN: Error is returned, no PR created
        """
        # Arrange
        mock_git = Mock(spec=GitProtocol)
        mock_git.get_current_branch.return_value = "development"
        mock_git.has_uncommitted_changes.return_value = True

        mock_github_cli = Mock(spec=GitHubCLIProtocol)

        # Act
        from nWave.core.versioning.application.release_service import ReleaseService

        service = ReleaseService(git=mock_git, github_cli=mock_github_cli)
        result = service.create_release_pr()

        # Assert
        assert result.success is False
        assert (
            "Uncommitted changes detected" in result.error_message
            or "uncommitted" in result.error_message.lower()
        )
        mock_github_cli.create_pr.assert_not_called()


class TestReleaseServiceHandlesPermissionDenied:
    """
    Test: ReleaseService handles permission denied errors from GitHub CLI.

    Acceptance Criteria (Step 07-04):
    - Error displays "Permission denied. You don't have access to create releases for this repository."
    - No PR is created
    - CLI exit code is non-zero
    """

    def test_release_service_handles_permission_denied(self):
        """
        GIVEN: User lacks repository write access
        WHEN: GitHub CLI returns permission denied error
        THEN: ReleaseService returns error with permission denied message
        """
        # Arrange - Mock port boundaries
        mock_git = Mock(spec=GitProtocol)
        mock_git.get_current_branch.return_value = "development"
        mock_git.has_uncommitted_changes.return_value = False

        mock_github_cli = Mock(spec=GitHubCLIProtocol)
        mock_github_cli.create_pr.return_value = PRResult(
            success=False,
            pr_number=None,
            pr_url=None,
            error_message="Permission denied. You don't have access to create releases for this repository.",
        )

        # Act
        from nWave.core.versioning.application.release_service import ReleaseService

        service = ReleaseService(git=mock_git, github_cli=mock_github_cli)
        result = service.create_release_pr()

        # Assert
        assert result.success is False
        assert result.pr_number is None
        assert result.pr_url is None
        assert "Permission denied" in result.error_message
        assert "don't have access" in result.error_message

    def test_release_service_propagates_permission_error_message(self):
        """
        GIVEN: GitHub CLI returns permission denied error
        WHEN: ReleaseService processes the result
        THEN: The exact error message is propagated for CLI display
        """
        # Arrange
        mock_git = Mock(spec=GitProtocol)
        mock_git.get_current_branch.return_value = "development"
        mock_git.has_uncommitted_changes.return_value = False

        expected_error = "Permission denied. You don't have access to create releases for this repository."
        mock_github_cli = Mock(spec=GitHubCLIProtocol)
        mock_github_cli.create_pr.return_value = PRResult(
            success=False,
            pr_number=None,
            pr_url=None,
            error_message=expected_error,
        )

        # Act
        from nWave.core.versioning.application.release_service import ReleaseService

        service = ReleaseService(git=mock_git, github_cli=mock_github_cli)
        result = service.create_release_pr()

        # Assert - exact error message is propagated
        assert result.error_message == expected_error
