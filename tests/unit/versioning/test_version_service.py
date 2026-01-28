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
from nWave.core.versioning.ports.github_api_port import ReleaseInfo, RateLimitError


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
        version_service.check_version()

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


# ============================================================================
# Step 03-04: Daily auto-check updates watermark when stale
# ============================================================================


class TestVersionServiceChecksGitHubWhenWatermarkStale:
    """
    Step 03-04: Test that VersionService checks GitHub when watermark is stale.

    Acceptance criteria: System checks GitHub Releases when watermark is stale (>24h)
    """

    def test_version_service_checks_github_when_watermark_stale(self):
        """VersionService should call GitHub API when watermark is stale (>24h)."""
        from datetime import timedelta
        from nWave.core.versioning.application.version_service import VersionService

        # GIVEN: A stale watermark (25 hours old)
        stale_timestamp = datetime.now(timezone.utc) - timedelta(hours=25)
        stale_watermark = Watermark(
            last_check=stale_timestamp,
            latest_version=Version("1.2.0"),
        )

        mock_file_system = Mock()
        mock_file_system.read_version.return_value = Version("1.2.3")
        mock_file_system.read_watermark.return_value = stale_watermark

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

        # THEN: GitHub API was called (because watermark is stale)
        mock_github.get_latest_release.assert_called_once()

        # AND: The result contains the latest version from GitHub
        assert result.latest_version == Version("1.3.0")

    def test_watermark_is_stale_after_24_hours(self):
        """Watermark is considered stale after 24 hours."""
        from datetime import timedelta

        # GIVEN: A watermark from 25 hours ago
        stale_timestamp = datetime.now(timezone.utc) - timedelta(hours=25)
        watermark = Watermark(
            last_check=stale_timestamp,
            latest_version=Version("1.2.0"),
        )

        # THEN: Watermark is stale
        assert watermark.is_stale is True

        # GIVEN: A watermark from 23 hours ago
        fresh_timestamp = datetime.now(timezone.utc) - timedelta(hours=23)
        fresh_watermark = Watermark(
            last_check=fresh_timestamp,
            latest_version=Version("1.2.0"),
        )

        # THEN: Watermark is NOT stale
        assert fresh_watermark.is_stale is False

    def test_version_service_updates_watermark_after_check(self):
        """VersionService should update watermark with new timestamp after GitHub check."""
        from datetime import timedelta
        from nWave.core.versioning.application.version_service import VersionService

        # GIVEN: A stale watermark
        stale_timestamp = datetime.now(timezone.utc) - timedelta(hours=25)
        stale_watermark = Watermark(
            last_check=stale_timestamp,
            latest_version=Version("1.2.0"),
        )

        mock_file_system = Mock()
        mock_file_system.read_version.return_value = Version("1.2.3")
        mock_file_system.read_watermark.return_value = stale_watermark

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
        version_service.check_version()

        timestamp_after = datetime.now(timezone.utc)

        # THEN: FileSystemPort.write_watermark was called
        mock_file_system.write_watermark.assert_called_once()

        # AND: The new watermark has updated timestamp (not the old stale one)
        written_watermark = mock_file_system.write_watermark.call_args[0][0]
        assert written_watermark.last_check > stale_timestamp
        assert timestamp_before <= written_watermark.last_check <= timestamp_after

        # AND: The new watermark contains latest_version from GitHub
        assert written_watermark.latest_version == Version("1.3.0")


# ============================================================================
# Step 03-06: Handle missing VERSION file gracefully
# ============================================================================


class TestVersionServiceHandlesMissingVersionFile:
    """Test that VersionService propagates FileNotFoundError when VERSION file is missing."""

    def test_version_service_handles_missing_version_file(self):
        """
        VersionService should raise FileNotFoundError when FileSystemPort cannot find VERSION file.

        Port-boundary test: FileSystemPort is mocked to simulate missing file.
        No mocks inside hexagon - we test the service's error propagation behavior.
        """
        from nWave.core.versioning.application.version_service import VersionService

        # GIVEN: FileSystemPort raises FileNotFoundError (simulating missing VERSION file)
        mock_file_system = Mock()
        mock_file_system.read_version.side_effect = FileNotFoundError(
            "VERSION file not found"
        )

        mock_github = Mock()
        # GitHub should never be called since VERSION file check fails first

        version_service = VersionService(
            github_api=mock_github,
            file_system=mock_file_system,
        )

        # WHEN/THEN: check_version raises FileNotFoundError
        with pytest.raises(FileNotFoundError) as exc_info:
            version_service.check_version()

        # AND: The error message indicates VERSION file is missing
        assert "VERSION" in str(exc_info.value)

        # AND: GitHub API was NOT called (early failure due to missing VERSION)
        mock_github.get_latest_release.assert_not_called()


# ============================================================================
# Step 03-07: Handle GitHub API rate limit gracefully
# ============================================================================


class TestVersionServiceHandlesRateLimitGracefully:
    """
    Test that VersionService handles GitHub API rate limiting (HTTP 403) gracefully.

    Scenario: Handle GitHub API rate limit gracefully
    Given Marco has nWave v1.2.3 installed
    And the GitHub API returns HTTP 403 with rate limit headers
    When checking version
    Then the output displays "nWave v1.2.3 (Unable to check for updates)"
    And no error is thrown
    """

    def test_version_service_handles_rate_limit_gracefully(self):
        """
        VersionService should catch RateLimitError and return graceful offline result.

        Port-boundary test: GitHubAPIPort is mocked to raise RateLimitError.
        No mocks inside hexagon - real Version and Watermark domain objects used.
        """
        from nWave.core.versioning.application.version_service import VersionService

        # GIVEN: FileSystemPort returns v1.2.3
        mock_file_system = Mock()
        mock_file_system.read_version.return_value = Version("1.2.3")

        # AND: GitHubAPIPort raises RateLimitError (HTTP 403)
        mock_github = Mock()
        mock_github.get_latest_release.side_effect = RateLimitError(
            "GitHub API rate limit exceeded",
            retry_after=3600,  # 1 hour until rate limit resets
        )

        version_service = VersionService(
            github_api=mock_github,
            file_system=mock_file_system,
        )

        # WHEN: check_version is called
        result = version_service.check_version()

        # THEN: No exception is raised (graceful handling)
        # AND: Result contains local version
        assert result.local_version == Version("1.2.3")
        assert result.installed_version == Version("1.2.3")  # Alias

        # AND: Result indicates offline/unable to check status
        assert result.is_offline is True
        assert result.remote_version is None
        assert result.latest_version is None  # Alias

        # AND: No update is available (cannot determine)
        assert result.update_available is False

        # AND: No error message is set (graceful degradation)
        assert result.error_message is None

    def test_version_service_rate_limit_does_not_update_watermark(self):
        """
        VersionService should NOT update watermark when rate limited.

        When GitHub returns HTTP 403, we don't have valid latest version info,
        so watermark should remain unchanged.
        """
        from nWave.core.versioning.application.version_service import VersionService

        # GIVEN: FileSystemPort returns v1.2.3
        mock_file_system = Mock()
        mock_file_system.read_version.return_value = Version("1.2.3")

        # AND: GitHubAPIPort raises RateLimitError
        mock_github = Mock()
        mock_github.get_latest_release.side_effect = RateLimitError(
            "GitHub API rate limit exceeded"
        )

        version_service = VersionService(
            github_api=mock_github,
            file_system=mock_file_system,
        )

        # WHEN: check_version is called
        version_service.check_version()

        # THEN: write_watermark was NOT called (no valid data to write)
        mock_file_system.write_watermark.assert_not_called()

    def test_version_service_formats_rate_limit_display_message(self):
        """
        VersionCheckResult should format rate limit status correctly.

        Display message: "nWave v1.2.3 (Unable to check for updates)"
        """
        from nWave.core.versioning.application.version_service import (
            VersionCheckResult,
        )

        # GIVEN: A result from rate-limited check
        result = VersionCheckResult(
            local_version=Version("1.2.3"),
            remote_version=None,
            is_offline=True,
        )

        # WHEN: format_display_message is called
        message = result.format_display_message()

        # THEN: Message shows unable to check (same as offline)
        assert message == "nWave v1.2.3 (Unable to check for updates)"

    def test_version_service_rate_limit_with_retry_after(self):
        """
        VersionService handles RateLimitError with retry_after information.

        The retry_after value indicates when the rate limit will reset,
        but for now we just gracefully degrade without using this info.
        """
        from nWave.core.versioning.application.version_service import VersionService

        # GIVEN: FileSystemPort returns v1.2.3
        mock_file_system = Mock()
        mock_file_system.read_version.return_value = Version("1.2.3")

        # AND: GitHubAPIPort raises RateLimitError with retry_after
        mock_github = Mock()
        mock_github.get_latest_release.side_effect = RateLimitError(
            "GitHub API rate limit exceeded",
            retry_after=1800,  # 30 minutes
        )

        version_service = VersionService(
            github_api=mock_github,
            file_system=mock_file_system,
        )

        # WHEN: check_version is called
        result = version_service.check_version()

        # THEN: Graceful degradation (same as rate limit without retry_after)
        assert result.is_offline is True
        assert result.local_version == Version("1.2.3")


# ============================================================================
# Step 03-05: Skip update check when watermark is fresh
# ============================================================================


class TestVersionServiceSkipsGitHubWhenWatermarkFresh:
    """
    Step 03-05: Test that VersionService skips GitHub API when watermark is fresh.

    Acceptance criteria:
    - No GitHub API call is made when watermark is fresh (<24h)
    - Output displays "nWave v1.2.3 (update available: v1.3.0)" using cached data
    """

    def test_version_service_skips_github_when_watermark_fresh(self):
        """VersionService should NOT call GitHub API when watermark is fresh (<24h)."""
        from datetime import timedelta
        from nWave.core.versioning.application.version_service import VersionService

        # GIVEN: A fresh watermark (1 hour old)
        fresh_timestamp = datetime.now(timezone.utc) - timedelta(hours=1)
        fresh_watermark = Watermark(
            last_check=fresh_timestamp,
            latest_version=Version("1.3.0"),
        )

        mock_file_system = Mock()
        mock_file_system.read_version.return_value = Version("1.2.3")
        mock_file_system.read_watermark.return_value = fresh_watermark

        mock_github = Mock()
        mock_github.get_latest_release.return_value = ReleaseInfo(
            version=Version("1.4.0"),  # Different to detect if called
            checksum="abc123",
            download_url="https://example.com/release.zip",
        )

        version_service = VersionService(
            github_api=mock_github,
            file_system=mock_file_system,
        )

        # WHEN: check_version is called
        version_service.check_version()

        # THEN: GitHub API was NOT called (watermark is fresh)
        mock_github.get_latest_release.assert_not_called()

    def test_version_service_uses_cached_latest_version(self):
        """VersionService should use cached latest_version from fresh watermark."""
        from datetime import timedelta
        from nWave.core.versioning.application.version_service import VersionService

        # GIVEN: A fresh watermark with cached latest_version "1.3.0"
        fresh_timestamp = datetime.now(timezone.utc) - timedelta(hours=1)
        fresh_watermark = Watermark(
            last_check=fresh_timestamp,
            latest_version=Version("1.3.0"),
        )

        mock_file_system = Mock()
        mock_file_system.read_version.return_value = Version("1.2.3")
        mock_file_system.read_watermark.return_value = fresh_watermark

        mock_github = Mock()

        version_service = VersionService(
            github_api=mock_github,
            file_system=mock_file_system,
        )

        # WHEN: check_version is called
        result = version_service.check_version()

        # THEN: Result uses cached latest_version from watermark
        assert result.latest_version == Version("1.3.0")
        assert result.remote_version == Version("1.3.0")

    def test_watermark_is_not_stale_within_24_hours(self):
        """Watermark is NOT stale within 24 hours boundary."""
        from datetime import timedelta

        # Test various fresh timestamps (all <24h)
        fresh_cases = [
            (1, "1 hour ago"),
            (12, "12 hours ago"),
            (23, "23 hours ago"),
            (23.9, "23.9 hours ago"),  # Just under 24h
        ]

        for hours, description in fresh_cases:
            fresh_timestamp = datetime.now(timezone.utc) - timedelta(hours=hours)
            watermark = Watermark(
                last_check=fresh_timestamp,
                latest_version=Version("1.0.0"),
            )

            # THEN: Watermark is NOT stale
            assert watermark.is_stale is False, f"Failed for {description}"

    def test_version_service_does_not_write_watermark_when_fresh(self):
        """VersionService should NOT update watermark when it is fresh."""
        from datetime import timedelta
        from nWave.core.versioning.application.version_service import VersionService

        # GIVEN: A fresh watermark
        fresh_timestamp = datetime.now(timezone.utc) - timedelta(hours=1)
        fresh_watermark = Watermark(
            last_check=fresh_timestamp,
            latest_version=Version("1.3.0"),
        )

        mock_file_system = Mock()
        mock_file_system.read_version.return_value = Version("1.2.3")
        mock_file_system.read_watermark.return_value = fresh_watermark

        mock_github = Mock()

        version_service = VersionService(
            github_api=mock_github,
            file_system=mock_file_system,
        )

        # WHEN: check_version is called
        version_service.check_version()

        # THEN: write_watermark was NOT called (no need to update fresh watermark)
        mock_file_system.write_watermark.assert_not_called()

    def test_version_service_detects_update_available_from_cache(self):
        """VersionService should detect update available from cached watermark data."""
        from datetime import timedelta
        from nWave.core.versioning.application.version_service import VersionService

        # GIVEN: Fresh watermark with cached version > installed version
        fresh_timestamp = datetime.now(timezone.utc) - timedelta(hours=1)
        fresh_watermark = Watermark(
            last_check=fresh_timestamp,
            latest_version=Version("1.3.0"),
        )

        mock_file_system = Mock()
        mock_file_system.read_version.return_value = Version("1.2.3")
        mock_file_system.read_watermark.return_value = fresh_watermark

        mock_github = Mock()

        version_service = VersionService(
            github_api=mock_github,
            file_system=mock_file_system,
        )

        # WHEN: check_version is called
        result = version_service.check_version()

        # THEN: Update available is detected using cached data
        assert result.update_available is True
        assert result.local_version == Version("1.2.3")
        assert result.latest_version == Version("1.3.0")

    def test_version_service_formats_message_from_cache(self):
        """VersionService result formats display message correctly from cached data."""
        from datetime import timedelta
        from nWave.core.versioning.application.version_service import VersionService

        # GIVEN: Fresh watermark with cached data
        fresh_timestamp = datetime.now(timezone.utc) - timedelta(hours=1)
        fresh_watermark = Watermark(
            last_check=fresh_timestamp,
            latest_version=Version("1.3.0"),
        )

        mock_file_system = Mock()
        mock_file_system.read_version.return_value = Version("1.2.3")
        mock_file_system.read_watermark.return_value = fresh_watermark

        mock_github = Mock()

        version_service = VersionService(
            github_api=mock_github,
            file_system=mock_file_system,
        )

        # WHEN: check_version and format
        result = version_service.check_version()
        message = result.format_display_message()

        # THEN: Message shows update available using cached data
        assert message == "nWave v1.2.3 (update available: v1.3.0)"
