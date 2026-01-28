"""
Unit tests for VersionService application service.

VersionService orchestrates version check:
1. Reads installed version from FileSystemPort
2. Fetches latest version from GitHubAPIPort
3. Updates watermark via FileSystemPort
4. Returns VersionCheckResult with comparison

NO MOCKS inside hexagon - uses real domain objects (Version, Watermark).
Mocks ONLY at port boundaries (GitHubAPIPort, FileSystemPort).
"""

import pytest
from datetime import datetime, timezone
from unittest.mock import Mock

from nWave.core.versioning.domain.version import Version
from nWave.core.versioning.domain.watermark import Watermark
from nWave.core.versioning.ports.github_api_port import ReleaseInfo, NetworkError, RateLimitError


class TestVersionServiceReturnsInstalledVersion:
    """Test that VersionService returns the installed version."""

    def test_version_service_returns_installed_version(self):
        """VersionService should return installed version from FileSystemPort."""
        # GIVEN: FileSystemPort returns v1.2.3
        from nWave.core.versioning.application.version_service import VersionService

        mock_file_system = Mock()
        mock_file_system.read_version.return_value = Version("1.2.3")
        mock_file_system.read_watermark.return_value = None

        mock_github = Mock()
        mock_github.get_latest_release.return_value = ReleaseInfo(
            version=Version("1.3.0"),
            checksum="abc123",
            download_url="https://example.com/release.zip",
        )

        version_service = VersionService(
            github_api=mock_github,
            file_system=mock_file_system,
        )

        # WHEN: check_version is called
        result = version_service.check_version()

        # THEN: installed_version is 1.2.3
        assert result.installed_version == Version("1.2.3")


class TestVersionServiceChecksGitHubForLatest:
    """Test that VersionService fetches latest version from GitHub."""

    def test_version_service_checks_github_for_latest(self):
        """VersionService should call GitHubAPIPort for latest release."""
        from nWave.core.versioning.application.version_service import VersionService

        mock_file_system = Mock()
        mock_file_system.read_version.return_value = Version("1.2.3")
        mock_file_system.read_watermark.return_value = None

        mock_github = Mock()
        mock_github.get_latest_release.return_value = ReleaseInfo(
            version=Version("1.3.0"),
            checksum="abc123",
            download_url="https://example.com/release.zip",
        )

        version_service = VersionService(
            github_api=mock_github,
            file_system=mock_file_system,
        )

        # WHEN: check_version is called
        result = version_service.check_version()

        # THEN: GitHubAPIPort.get_latest_release was called
        mock_github.get_latest_release.assert_called_once()

        # AND: latest_version is 1.3.0
        assert result.latest_version == Version("1.3.0")


class TestVersionServiceUpdatesWatermark:
    """Test that VersionService updates watermark after check."""

    def test_version_service_updates_watermark_on_check(self):
        """VersionService should write watermark with timestamp and latest version."""
        from nWave.core.versioning.application.version_service import VersionService

        mock_file_system = Mock()
        mock_file_system.read_version.return_value = Version("1.2.3")
        mock_file_system.read_watermark.return_value = None

        mock_github = Mock()
        mock_github.get_latest_release.return_value = ReleaseInfo(
            version=Version("1.3.0"),
            checksum="abc123",
            download_url="https://example.com/release.zip",
        )

        version_service = VersionService(
            github_api=mock_github,
            file_system=mock_file_system,
        )

        timestamp_before = datetime.now(timezone.utc)

        # WHEN: check_version is called
        result = version_service.check_version()

        timestamp_after = datetime.now(timezone.utc)

        # THEN: FileSystemPort.write_watermark was called
        mock_file_system.write_watermark.assert_called_once()

        # AND: The watermark contains latest_version 1.3.0
        written_watermark = mock_file_system.write_watermark.call_args[0][0]
        assert written_watermark.latest_version == Version("1.3.0")

        # AND: The watermark timestamp is within expected range
        assert timestamp_before <= written_watermark.last_check <= timestamp_after


class TestVersionServiceUpdateAvailableDetection:
    """Test that VersionService correctly detects update availability."""

    def test_update_available_when_latest_greater_than_installed(self):
        """VersionService should detect update available."""
        from nWave.core.versioning.application.version_service import VersionService

        mock_file_system = Mock()
        mock_file_system.read_version.return_value = Version("1.2.3")
        mock_file_system.read_watermark.return_value = None

        mock_github = Mock()
        mock_github.get_latest_release.return_value = ReleaseInfo(
            version=Version("1.3.0"),
            checksum="abc123",
            download_url="https://example.com/release.zip",
        )

        version_service = VersionService(
            github_api=mock_github,
            file_system=mock_file_system,
        )

        # WHEN: check_version is called
        result = version_service.check_version()

        # THEN: update_available is True
        assert result.update_available is True

    def test_no_update_when_already_latest(self):
        """VersionService should detect no update when versions match."""
        from nWave.core.versioning.application.version_service import VersionService

        mock_file_system = Mock()
        mock_file_system.read_version.return_value = Version("1.3.0")
        mock_file_system.read_watermark.return_value = None

        mock_github = Mock()
        mock_github.get_latest_release.return_value = ReleaseInfo(
            version=Version("1.3.0"),
            checksum="abc123",
            download_url="https://example.com/release.zip",
        )

        version_service = VersionService(
            github_api=mock_github,
            file_system=mock_file_system,
        )

        # WHEN: check_version is called
        result = version_service.check_version()

        # THEN: update_available is False
        assert result.update_available is False
