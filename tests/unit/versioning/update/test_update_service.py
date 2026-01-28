"""
Unit tests for UpdateService application service.

HEXAGONAL ARCHITECTURE:
- UpdateService is an APPLICATION SERVICE (inside the hexagon)
- Tests use REAL domain objects (Version, BackupPolicy) - NEVER mocked
- Tests mock ONLY port interfaces (FileSystemPort, DownloadPort, ChecksumPort, GitHubAPIPort)

Test coverage for step 04-01:
- test_update_service_creates_backup_before_update
- test_update_service_downloads_release_asset
- test_update_service_validates_checksum
- test_update_service_applies_update
- test_update_service_updates_version_file
"""

from pathlib import Path
from unittest.mock import MagicMock, patch
from datetime import datetime

import pytest

# Domain objects - REAL, never mocked
from nWave.core.versioning.domain.version import Version
from nWave.core.versioning.domain.backup_policy import BackupPolicy


class TestUpdateServiceCreatesBackupBeforeUpdate:
    """Test that UpdateService creates backup before any update operations."""

    def test_update_service_creates_backup_before_update(self):
        """
        GIVEN: UpdateService with mocked ports
        WHEN: update() is called
        THEN: Backup is created BEFORE download begins
        """
        # Import here to trigger failure if module doesn't exist
        from nWave.core.versioning.application.update_service import UpdateService

        # Arrange: Create mocked ports (only at hexagon boundary)
        mock_file_system = MagicMock()
        mock_github_api = MagicMock()
        mock_download = MagicMock()
        mock_checksum = MagicMock()

        # Configure mocks with real domain objects
        mock_file_system.read_version.return_value = Version("1.2.3")
        mock_github_api.get_latest_release.return_value = MagicMock(
            version=Version("1.3.0"),
            checksum="abc123def456",
            download_url="https://example.com/release.tar.gz",
        )
        mock_checksum.verify.return_value = True

        # Track call order
        call_order = []
        mock_file_system.create_backup.side_effect = lambda p: call_order.append("backup")
        mock_download.download.side_effect = lambda u, d, c=None: call_order.append("download")

        service = UpdateService(
            file_system=mock_file_system,
            github_api=mock_github_api,
            download=mock_download,
            checksum=mock_checksum,
        )

        # Act
        service.update()

        # Assert: Backup created BEFORE download
        assert "backup" in call_order, "Backup should be created"
        assert "download" in call_order, "Download should occur"
        assert call_order.index("backup") < call_order.index("download"), (
            "Backup must happen before download"
        )


class TestUpdateServiceDownloadsReleaseAsset:
    """Test that UpdateService downloads release asset from GitHub."""

    def test_update_service_downloads_release_asset(self):
        """
        GIVEN: UpdateService with mocked ports
        WHEN: update() is called
        THEN: Release asset is downloaded via DownloadPort
        """
        from nWave.core.versioning.application.update_service import UpdateService

        # Arrange
        mock_file_system = MagicMock()
        mock_github_api = MagicMock()
        mock_download = MagicMock()
        mock_checksum = MagicMock()

        mock_file_system.read_version.return_value = Version("1.2.3")
        mock_github_api.get_latest_release.return_value = MagicMock(
            version=Version("1.3.0"),
            checksum="abc123def456",
            download_url="https://github.com/releases/v1.3.0.tar.gz",
        )
        mock_checksum.verify.return_value = True

        service = UpdateService(
            file_system=mock_file_system,
            github_api=mock_github_api,
            download=mock_download,
            checksum=mock_checksum,
        )

        # Act
        service.update()

        # Assert: Download was called with correct URL
        mock_download.download.assert_called_once()
        call_args = mock_download.download.call_args
        assert "github.com/releases/v1.3.0" in str(call_args)


class TestUpdateServiceValidatesChecksum:
    """Test that UpdateService validates checksum after download."""

    def test_update_service_validates_checksum(self):
        """
        GIVEN: UpdateService with mocked ports
        WHEN: update() is called
        THEN: Downloaded file is validated against expected checksum
        """
        from nWave.core.versioning.application.update_service import UpdateService

        # Arrange
        mock_file_system = MagicMock()
        mock_github_api = MagicMock()
        mock_download = MagicMock()
        mock_checksum = MagicMock()

        mock_file_system.read_version.return_value = Version("1.2.3")
        mock_github_api.get_latest_release.return_value = MagicMock(
            version=Version("1.3.0"),
            checksum="abc123def456",
            download_url="https://example.com/release.tar.gz",
        )
        mock_checksum.verify.return_value = True

        service = UpdateService(
            file_system=mock_file_system,
            github_api=mock_github_api,
            download=mock_download,
            checksum=mock_checksum,
        )

        # Act
        service.update()

        # Assert: Checksum verification was called
        mock_checksum.verify.assert_called_once()
        call_args = mock_checksum.verify.call_args
        # Second argument should be expected checksum
        assert "abc123def456" in str(call_args)


class TestUpdateServiceAppliesUpdate:
    """Test that UpdateService applies update after validation."""

    def test_update_service_applies_update(self):
        """
        GIVEN: UpdateService with mocked ports and valid checksum
        WHEN: update() is called
        THEN: Update is applied to installation
        """
        from nWave.core.versioning.application.update_service import UpdateService

        # Arrange
        mock_file_system = MagicMock()
        mock_github_api = MagicMock()
        mock_download = MagicMock()
        mock_checksum = MagicMock()

        mock_file_system.read_version.return_value = Version("1.2.3")
        mock_github_api.get_latest_release.return_value = MagicMock(
            version=Version("1.3.0"),
            checksum="abc123def456",
            download_url="https://example.com/release.tar.gz",
        )
        mock_checksum.verify.return_value = True

        service = UpdateService(
            file_system=mock_file_system,
            github_api=mock_github_api,
            download=mock_download,
            checksum=mock_checksum,
        )

        # Act
        result = service.update()

        # Assert: Update was applied (apply_update or similar method called)
        assert result.success is True, "Update should succeed"
        assert result.new_version == Version("1.3.0"), "New version should be 1.3.0"


class TestUpdateServiceUpdatesVersionFile:
    """Test that UpdateService updates VERSION file after successful update."""

    def test_update_service_updates_version_file(self, tmp_path):
        """
        GIVEN: UpdateService with mocked ports
        WHEN: update() completes successfully
        THEN: VERSION file is updated to new version
        """
        from nWave.core.versioning.application.update_service import UpdateService

        # Arrange - set up real test directory
        claude_dir = tmp_path / ".claude"
        claude_dir.mkdir(parents=True)
        version_file = claude_dir / "VERSION"
        version_file.write_text("1.2.3")

        mock_file_system = MagicMock()
        mock_github_api = MagicMock()
        mock_download = MagicMock()
        mock_checksum = MagicMock()

        mock_file_system.read_version.return_value = Version("1.2.3")
        mock_file_system.list_backups.return_value = []
        mock_github_api.get_latest_release.return_value = MagicMock(
            version=Version("1.3.0"),
            checksum="abc123def456",
            download_url="https://example.com/release.tar.gz",
        )
        mock_checksum.verify.return_value = True

        service = UpdateService(
            file_system=mock_file_system,
            github_api=mock_github_api,
            download=mock_download,
            checksum=mock_checksum,
            nwave_home=claude_dir,
        )

        # Act
        result = service.update()

        # Assert: Update succeeded and VERSION file was written
        assert result.success is True, f"Update should succeed, got: {result.error_message}"
        assert version_file.read_text().strip() == "1.3.0", "VERSION file should contain 1.3.0"
