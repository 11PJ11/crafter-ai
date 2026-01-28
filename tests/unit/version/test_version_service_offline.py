"""
Unit tests for VersionService - Step 03-03: Display version when offline.

Test Coverage:
- Handling NetworkError gracefully
- Formatting offline message correctly
- No exception propagation to caller

CRITICAL: Domain objects (Version) use REAL objects, not mocks.
Mocks are ONLY used at port boundaries (GitHubAPIPort).
"""

import pytest

from nWave.core.versioning.domain.version import Version
from nWave.core.versioning.ports.github_api_port import (
    GitHubAPIPort,
    NetworkError,
    ReleaseInfo,
)


class TestVersionServiceShould:
    """Unit tests for VersionService offline behavior."""

    def test_return_offline_result_when_network_error_occurs(self, tmp_path):
        """
        GIVEN a VERSION file exists with version 1.2.3
        AND the GitHub API raises NetworkError
        WHEN VersionService checks version
        THEN it returns a result with is_offline=True
        AND no exception is raised
        """
        # Arrange
        from nWave.core.versioning.application.version_service import VersionService

        version_file = tmp_path / "VERSION"
        version_file.write_text("1.2.3")

        class OfflineGitHubAdapter(GitHubAPIPort):
            def get_latest_release(self, owner: str, repo: str) -> ReleaseInfo:
                raise NetworkError("Connection timed out")

        service = VersionService(
            version_file_path=version_file,
            github_api=OfflineGitHubAdapter(),
        )

        # Act
        result = service.check_version()

        # Assert
        assert result.local_version == Version("1.2.3")
        assert result.is_offline is True
        assert result.remote_version is None

    def test_format_offline_message_correctly(self, tmp_path):
        """
        GIVEN a VersionCheckResult with is_offline=True
        AND local_version is 1.2.3
        WHEN formatting the display message
        THEN it returns "nWave v1.2.3 (Unable to check for updates)"
        """
        # Arrange
        from nWave.core.versioning.application.version_service import (
            VersionCheckResult,
        )

        result = VersionCheckResult(
            local_version=Version("1.2.3"),
            remote_version=None,
            is_offline=True,
        )

        # Act
        message = result.format_display_message()

        # Assert
        assert message == "nWave v1.2.3 (Unable to check for updates)"

    def test_not_raise_exception_when_offline(self, tmp_path):
        """
        GIVEN a VERSION file exists with version 1.2.3
        AND the GitHub API raises NetworkError
        WHEN VersionService checks version
        THEN no exception propagates to the caller
        """
        # Arrange
        from nWave.core.versioning.application.version_service import VersionService

        version_file = tmp_path / "VERSION"
        version_file.write_text("1.2.3")

        class OfflineGitHubAdapter(GitHubAPIPort):
            def get_latest_release(self, owner: str, repo: str) -> ReleaseInfo:
                raise NetworkError("Connection refused")

        service = VersionService(
            version_file_path=version_file,
            github_api=OfflineGitHubAdapter(),
        )

        # Act & Assert - No exception should be raised
        result = service.check_version()
        assert result is not None

    def test_handle_rate_limit_error_gracefully(self, tmp_path):
        """
        GIVEN a VERSION file exists with version 1.2.3
        AND the GitHub API raises RateLimitError
        WHEN VersionService checks version
        THEN it returns a result with is_offline=True (same as network error)
        """
        # Arrange
        from nWave.core.versioning.application.version_service import VersionService
        from nWave.core.versioning.ports.github_api_port import RateLimitError

        version_file = tmp_path / "VERSION"
        version_file.write_text("1.2.3")

        class RateLimitedGitHubAdapter(GitHubAPIPort):
            def get_latest_release(self, owner: str, repo: str) -> ReleaseInfo:
                raise RateLimitError("API rate limit exceeded", retry_after=60)

        service = VersionService(
            version_file_path=version_file,
            github_api=RateLimitedGitHubAdapter(),
        )

        # Act
        result = service.check_version()

        # Assert - Rate limited is treated like offline
        assert result.local_version == Version("1.2.3")
        assert result.is_offline is True
