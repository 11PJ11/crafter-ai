"""
Unit tests for checksum validation failure handling in UpdateService.

Step 04-07: Checksum validation failure aborts update

HEXAGONAL ARCHITECTURE:
- UpdateService is an APPLICATION SERVICE (inside the hexagon)
- Tests use REAL domain objects (Version, BackupPolicy) - NEVER mocked
- Tests mock ONLY port interfaces (ChecksumPort, FileSystemPort, DownloadPort, GitHubAPIPort)

Acceptance Criteria:
- Error displays "Download corrupted (checksum mismatch). Update aborted."
- Corrupted download is deleted
- Test ~/.claude/ directory is unchanged
- VERSION file still contains "1.2.3"
"""

from unittest.mock import MagicMock


# Domain objects - REAL, never mocked
from nWave.core.versioning.domain.version import Version


class TestUpdateServiceChecksumValidationFailure:
    """
    Test that UpdateService aborts update on checksum mismatch.

    Step 04-07: Chiara's download has wrong checksum. Error displayed,
    corrupted download deleted, installation unchanged.

    Key behaviors:
    - ChecksumPort.verify() returns False when checksums don't match
    - UpdateService does NOT apply the update when checksum fails
    - Corrupted download file is deleted
    - Original installation (v1.2.3) must be completely preserved
    - User sees clear error message with security context
    """

    def test_update_service_aborts_on_checksum_mismatch(self, tmp_path):
        """
        GIVEN: UpdateService with mocked ports
        AND: ChecksumPort.verify() returns False
        WHEN: update() is called
        THEN: UpdateResult.success is False
        AND: error_message indicates checksum mismatch
        """
        from nWave.core.versioning.application.update_service import UpdateService

        # Arrange
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
            checksum="expected_sha256_hash",
            download_url="https://github.com/releases/v1.3.0.tar.gz",
        )

        # Configure checksum to return False (mismatch)
        mock_checksum.verify.return_value = False

        service = UpdateService(
            file_system=mock_file_system,
            github_api=mock_github_api,
            download=mock_download,
            checksum=mock_checksum,
            nwave_home=claude_dir,
        )

        # Act
        result = service.update()

        # Assert
        assert result.success is False, "Update should fail on checksum mismatch"
        assert "checksum" in result.error_message.lower(), (
            f"Error message should mention 'checksum', got: {result.error_message}"
        )

    def test_version_file_unchanged_on_checksum_failure(self, tmp_path):
        """
        GIVEN: Chiara has nWave v1.2.3 installed
        AND: Downloaded file has wrong checksum
        WHEN: update() is called
        THEN: VERSION file still contains "1.2.3"
        """
        from nWave.core.versioning.application.update_service import UpdateService

        # Arrange
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
            checksum="expected_sha256_hash",
            download_url="https://github.com/releases/v1.3.0.tar.gz",
        )
        mock_checksum.verify.return_value = False

        service = UpdateService(
            file_system=mock_file_system,
            github_api=mock_github_api,
            download=mock_download,
            checksum=mock_checksum,
            nwave_home=claude_dir,
        )

        # Act
        result = service.update()

        # Assert
        assert result.success is False
        assert version_file.read_text().strip() == "1.2.3", (
            "VERSION file should still contain 1.2.3 after checksum failure"
        )

    def test_installation_unchanged_on_checksum_failure(self, tmp_path):
        """
        GIVEN: nWave v1.2.3 is installed with agent files
        AND: Downloaded file has wrong checksum
        WHEN: update() is called
        THEN: All original installation files are preserved
        """
        from nWave.core.versioning.application.update_service import UpdateService

        # Arrange
        claude_dir = tmp_path / ".claude"
        claude_dir.mkdir(parents=True)
        version_file = claude_dir / "VERSION"
        version_file.write_text("1.2.3")

        # Create installation structure
        agents_dir = claude_dir / "agents" / "nw"
        agents_dir.mkdir(parents=True)
        test_agent = agents_dir / "software-crafter.md"
        test_agent.write_text("original agent content")

        nwave_dir = claude_dir / "nWave"
        nwave_dir.mkdir()
        test_file = nwave_dir / "config.yaml"
        test_file.write_text("original config")

        mock_file_system = MagicMock()
        mock_github_api = MagicMock()
        mock_download = MagicMock()
        mock_checksum = MagicMock()

        mock_file_system.read_version.return_value = Version("1.2.3")
        mock_file_system.list_backups.return_value = []
        mock_github_api.get_latest_release.return_value = MagicMock(
            version=Version("1.3.0"),
            checksum="expected_sha256_hash",
            download_url="https://github.com/releases/v1.3.0.tar.gz",
        )
        mock_checksum.verify.return_value = False

        service = UpdateService(
            file_system=mock_file_system,
            github_api=mock_github_api,
            download=mock_download,
            checksum=mock_checksum,
            nwave_home=claude_dir,
        )

        # Act
        result = service.update()

        # Assert
        assert result.success is False
        assert test_agent.exists(), "Agent file should be preserved"
        assert test_agent.read_text() == "original agent content"
        assert test_file.exists(), "Config file should be preserved"
        assert test_file.read_text() == "original config"

    def test_error_message_includes_security_context(self, tmp_path):
        """
        GIVEN: UpdateService with checksum mismatch
        WHEN: update() is called
        THEN: Error message explains security implications
        """
        from nWave.core.versioning.application.update_service import UpdateService

        # Arrange
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
            checksum="expected_sha256_hash",
            download_url="https://github.com/releases/v1.3.0.tar.gz",
        )
        mock_checksum.verify.return_value = False

        service = UpdateService(
            file_system=mock_file_system,
            github_api=mock_github_api,
            download=mock_download,
            checksum=mock_checksum,
            nwave_home=claude_dir,
        )

        # Act
        result = service.update()

        # Assert
        error_lower = result.error_message.lower()
        assert "corrupted" in error_lower or "mismatch" in error_lower, (
            f"Error should mention corruption/mismatch: {result.error_message}"
        )
