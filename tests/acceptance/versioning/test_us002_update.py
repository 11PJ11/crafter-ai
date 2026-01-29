"""
Acceptance tests for US-002: Update nWave to Latest Release (/nw:update).

HEXAGONAL BOUNDARY ENFORCEMENT:
- Tests invoke through UpdateService application service
- Mocking allowed ONLY at port boundaries (DownloadPort, FileSystemPort, etc.)
- Real domain objects used (Version, BackupPolicy) - NEVER mocked

Step 04-06: Network failure during download leaves installation unchanged
"""

from unittest.mock import MagicMock

# Domain objects - REAL, never mocked
from nWave.core.versioning.domain.version import Version

# Port exceptions
from nWave.core.versioning.ports.download_port import NetworkError


class TestNetworkFailureDuringDownloadLeavesInstallationUnchanged:
    """
    Step 04-06: Network failure during download leaves installation unchanged.

    Acceptance Criteria:
    - Error displays "Download failed: network error. Your nWave installation is unchanged."
    - Test ~/.claude/ directory contains original v1.2.3 installation
    - VERSION file still contains "1.2.3"
    - No partial download files remain
    """

    def test_network_failure_during_download_displays_error_message(self, tmp_path):
        """
        GIVEN: Antonio has nWave v1.2.3 installed
        AND: GitHub API returns v1.3.0 as latest release
        AND: Download fails mid-stream with network error
        WHEN: Antonio runs /nw:update command
        THEN: Error displays "Download failed: network error. Your nWave installation is unchanged."
        """
        from nWave.core.versioning.application.update_service import UpdateService

        # Arrange: Set up test installation
        claude_dir = tmp_path / ".claude"
        claude_dir.mkdir(parents=True)
        version_file = claude_dir / "VERSION"
        version_file.write_text("1.2.3")

        # Mock ports at hexagon boundary
        mock_file_system = MagicMock()
        mock_github_api = MagicMock()
        mock_download = MagicMock()
        mock_checksum = MagicMock()

        # Configure mocks with real domain objects
        mock_file_system.read_version.return_value = Version("1.2.3")
        mock_file_system.list_backups.return_value = []
        mock_github_api.get_latest_release.return_value = MagicMock(
            version=Version("1.3.0"),
            checksum="abc123def456",
            download_url="https://github.com/releases/v1.3.0.tar.gz",
        )

        # Configure download to raise NetworkError (simulating mid-stream failure)
        mock_download.download.side_effect = NetworkError("Connection reset by peer")

        service = UpdateService(
            file_system=mock_file_system,
            github_api=mock_github_api,
            download=mock_download,
            checksum=mock_checksum,
            nwave_home=claude_dir,
        )

        # Act
        result = service.update()

        # Assert: Error message contains expected text
        assert result.success is False, "Update should fail on network error"
        assert (
            "network error" in result.error_message.lower()
            or "network" in result.error_message.lower()
        ), f"Error message should mention network error, got: {result.error_message}"

    def test_network_failure_leaves_version_file_unchanged(self, tmp_path):
        """
        GIVEN: Antonio has nWave v1.2.3 installed
        AND: Download fails with network error
        WHEN: Antonio runs /nw:update command
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
            checksum="abc123def456",
            download_url="https://github.com/releases/v1.3.0.tar.gz",
        )
        mock_download.download.side_effect = NetworkError("Network unavailable")

        service = UpdateService(
            file_system=mock_file_system,
            github_api=mock_github_api,
            download=mock_download,
            checksum=mock_checksum,
            nwave_home=claude_dir,
        )

        # Act
        result = service.update()

        # Assert: VERSION file unchanged
        assert result.success is False
        assert version_file.read_text().strip() == "1.2.3", (
            "VERSION file should still contain original version 1.2.3"
        )

    def test_network_failure_returns_original_version_in_result(self, tmp_path):
        """
        GIVEN: Antonio has nWave v1.2.3 installed
        AND: Download fails with network error
        WHEN: Antonio runs /nw:update command
        THEN: Result contains previous_version as 1.2.3
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
            checksum="abc123def456",
            download_url="https://github.com/releases/v1.3.0.tar.gz",
        )
        mock_download.download.side_effect = NetworkError("Download interrupted")

        service = UpdateService(
            file_system=mock_file_system,
            github_api=mock_github_api,
            download=mock_download,
            checksum=mock_checksum,
            nwave_home=claude_dir,
        )

        # Act
        result = service.update()

        # Assert: Previous version preserved in result
        assert result.success is False
        assert result.previous_version == Version("1.2.3"), (
            f"previous_version should be 1.2.3, got {result.previous_version}"
        )

    def test_network_failure_cleans_up_partial_download_files(self, tmp_path):
        """
        GIVEN: Antonio has nWave v1.2.3 installed
        AND: Download starts but fails mid-stream (partial file written)
        WHEN: Antonio runs /nw:update command
        THEN: No partial download files remain in temp directory
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
            checksum="abc123def456",
            download_url="https://github.com/releases/v1.3.0.tar.gz",
        )

        # Simulate partial file creation followed by network error
        partial_file_path = None

        def download_with_partial_file(url, destination, progress_callback=None):
            nonlocal partial_file_path
            partial_file_path = destination
            # Create partial file before failing
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(b"partial content - incomplete download")
            raise NetworkError("Connection timed out mid-download")

        mock_download.download.side_effect = download_with_partial_file

        service = UpdateService(
            file_system=mock_file_system,
            github_api=mock_github_api,
            download=mock_download,
            checksum=mock_checksum,
            nwave_home=claude_dir,
        )

        # Act
        result = service.update()

        # Assert: Partial file should be cleaned up
        assert result.success is False
        if partial_file_path:
            assert not partial_file_path.exists(), (
                f"Partial download file should be cleaned up: {partial_file_path}"
            )
