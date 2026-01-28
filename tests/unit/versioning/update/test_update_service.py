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

from unittest.mock import MagicMock, patch


# Domain objects - REAL, never mocked
from nWave.core.versioning.domain.version import Version


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
        mock_file_system.create_backup.side_effect = lambda p: call_order.append(
            "backup"
        )
        mock_download.download.side_effect = lambda u, d, c=None: call_order.append(
            "download"
        )

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
        assert result.success is True, (
            f"Update should succeed, got: {result.error_message}"
        )
        assert version_file.read_text().strip() == "1.3.0", (
            "VERSION file should contain 1.3.0"
        )


# ============================================================================
# Step 04-06: Network failure during download leaves installation unchanged
# ============================================================================


class TestUpdateServiceHandlesNetworkFailure:
    """
    Test that UpdateService handles network failures gracefully.

    Step 04-06: Network failure during download leaves installation unchanged.

    Key behaviors:
    - DownloadAdapter raises NetworkError when network failure occurs
    - UpdateService catches NetworkError and ensures no partial files remain
    - Original installation (v1.2.3) must be completely preserved
    - User sees clear error message: 'Download failed: network error. Your nWave installation is unchanged.'
    """

    def test_update_service_handles_network_failure(self, tmp_path):
        """
        GIVEN: UpdateService with mocked ports
        AND: DownloadPort raises NetworkError
        WHEN: update() is called
        THEN: UpdateResult.success is False
        AND: error_message contains user-friendly network error message
        """
        from nWave.core.versioning.application.update_service import UpdateService
        from nWave.core.versioning.ports.download_port import NetworkError

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

        # Configure download to raise NetworkError
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

        # Assert
        assert result.success is False, "Update should fail on network error"
        assert "Download failed" in result.error_message, (
            f"Error message should start with 'Download failed', got: {result.error_message}"
        )
        assert "network error" in result.error_message.lower(), (
            f"Error message should mention 'network error', got: {result.error_message}"
        )
        assert "unchanged" in result.error_message.lower(), (
            f"Error message should indicate installation is 'unchanged', got: {result.error_message}"
        )

    def test_partial_files_cleaned_up_on_network_failure(self, tmp_path):
        """
        GIVEN: UpdateService with mocked ports
        AND: DownloadPort creates partial file then raises NetworkError
        WHEN: update() is called
        THEN: Partial download file is cleaned up
        """
        from nWave.core.versioning.application.update_service import UpdateService
        from nWave.core.versioning.ports.download_port import NetworkError

        # Arrange
        claude_dir = tmp_path / ".claude"
        claude_dir.mkdir(parents=True)
        version_file = claude_dir / "VERSION"
        version_file.write_text("1.2.3")

        # Track partial file path
        partial_file_path = None

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

        def download_with_partial(url, destination, progress_callback=None):
            nonlocal partial_file_path
            partial_file_path = destination
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(b"partial content")
            raise NetworkError("Connection lost mid-download")

        mock_download.download.side_effect = download_with_partial

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
        assert partial_file_path is not None, "Download should have been attempted"
        assert not partial_file_path.exists(), (
            f"Partial file should be cleaned up: {partial_file_path}"
        )

    def test_installation_unchanged_on_network_failure(self, tmp_path):
        """
        GIVEN: Antonio has nWave v1.2.3 installed
        AND: Download fails with network error
        WHEN: update() is called
        THEN: VERSION file still contains "1.2.3"
        AND: Original installation is preserved
        """
        from nWave.core.versioning.application.update_service import UpdateService
        from nWave.core.versioning.ports.download_port import NetworkError

        # Arrange
        claude_dir = tmp_path / ".claude"
        claude_dir.mkdir(parents=True)
        version_file = claude_dir / "VERSION"
        version_file.write_text("1.2.3")

        # Create some test files to represent installation
        agents_dir = claude_dir / "agents" / "nw"
        agents_dir.mkdir(parents=True)
        (agents_dir / "test_agent.md").write_text("agent content")

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

        # Assert
        assert result.success is False
        assert result.previous_version == Version("1.2.3")
        assert version_file.read_text().strip() == "1.2.3", (
            "VERSION file should still contain 1.2.3"
        )
        assert (agents_dir / "test_agent.md").exists(), (
            "Original installation files should be preserved"
        )
        assert (agents_dir / "test_agent.md").read_text() == "agent content", (
            "Original file content should be unchanged"
        )


# ============================================================================
# Step 04-02: Major version change detection
# ============================================================================


class TestUpdateServiceDetectsMajorVersionChange:
    """Test that UpdateService detects major version changes (1.x -> 2.x)."""

    def test_update_service_detects_major_version_change(self):
        """
        GIVEN: UpdateService with current v1.3.0 and target v2.0.0
        WHEN: is_major_version_change() is called
        THEN: Returns True (1.x to 2.x is a major change)
        """
        from nWave.core.versioning.application.update_service import UpdateService

        # Arrange
        mock_file_system = MagicMock()
        mock_github_api = MagicMock()
        mock_download = MagicMock()
        mock_checksum = MagicMock()

        service = UpdateService(
            file_system=mock_file_system,
            github_api=mock_github_api,
            download=mock_download,
            checksum=mock_checksum,
        )

        current = Version("1.3.0")
        target = Version("2.0.0")

        # Act
        is_major_change = service.is_major_version_change(current, target)

        # Assert
        assert is_major_change is True, (
            "1.3.0 -> 2.0.0 should be a major version change"
        )

    def test_update_service_detects_minor_version_not_major(self):
        """
        GIVEN: UpdateService with current v1.2.3 and target v1.3.0
        WHEN: is_major_version_change() is called
        THEN: Returns False (minor version change, not major)
        """
        from nWave.core.versioning.application.update_service import UpdateService

        # Arrange
        mock_file_system = MagicMock()
        mock_github_api = MagicMock()
        mock_download = MagicMock()
        mock_checksum = MagicMock()

        service = UpdateService(
            file_system=mock_file_system,
            github_api=mock_github_api,
            download=mock_download,
            checksum=mock_checksum,
        )

        current = Version("1.2.3")
        target = Version("1.3.0")

        # Act
        is_major_change = service.is_major_version_change(current, target)

        # Assert
        assert is_major_change is False, (
            "1.2.3 -> 1.3.0 should NOT be a major version change"
        )

    def test_update_service_detects_patch_version_not_major(self):
        """
        GIVEN: UpdateService with current v1.2.3 and target v1.2.4
        WHEN: is_major_version_change() is called
        THEN: Returns False (patch version change, not major)
        """
        from nWave.core.versioning.application.update_service import UpdateService

        # Arrange
        mock_file_system = MagicMock()
        mock_github_api = MagicMock()
        mock_download = MagicMock()
        mock_checksum = MagicMock()

        service = UpdateService(
            file_system=mock_file_system,
            github_api=mock_github_api,
            download=mock_download,
            checksum=mock_checksum,
        )

        current = Version("1.2.3")
        target = Version("1.2.4")

        # Act
        is_major_change = service.is_major_version_change(current, target)

        # Assert
        assert is_major_change is False, (
            "1.2.3 -> 1.2.4 should NOT be a major version change"
        )


class TestVersionComparisonDetectsMajorBump:
    """Test that Version entity properly exposes major version for comparison."""

    def test_version_major_property_accessible(self):
        """
        GIVEN: A Version object
        WHEN: major property is accessed
        THEN: Returns the major version number
        """
        version = Version("2.3.4")
        assert version.major == 2, "Major version should be 2"

    def test_version_major_property_v1(self):
        """
        GIVEN: A Version "1.3.0"
        WHEN: major property is accessed
        THEN: Returns 1
        """
        version = Version("1.3.0")
        assert version.major == 1, "Major version should be 1"

    def test_version_comparison_different_major(self):
        """
        GIVEN: Two versions with different major numbers
        WHEN: major versions are compared
        THEN: They are different
        """
        v1 = Version("1.3.0")
        v2 = Version("2.0.0")
        assert v1.major != v2.major, "Major versions should be different"


# ============================================================================
# Step 04-09: Non-nWave user content is preserved during update
# ============================================================================


class TestUpdateServicePreservesUserContent:
    """
    Test that UpdateService preserves user content during update.

    Step 04-09: Non-nWave user content is preserved during update.

    Key behaviors:
    - CoreContentIdentifier distinguishes nw-prefixed from user content
    - UpdateService replaces only content where is_core_content() returns True
    - User content (agents/my-custom-agent/, commands/my-custom-command/) is preserved
    - nWave content (agents/nw/, commands/nw/) is replaced
    """

    def test_update_service_uses_core_content_identifier(self, tmp_path):
        """
        GIVEN: UpdateService with CoreContentIdentifier
        WHEN: apply_update() is called
        THEN: CoreContentIdentifier is used to classify paths
        """
        from nWave.core.versioning.application.update_service import UpdateService
        from nWave.core.versioning.domain.core_content_identifier import (
            CoreContentIdentifier,
        )

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

        # Verify CoreContentIdentifier is available (real domain object, never mocked)
        identifier = CoreContentIdentifier()
        assert identifier.is_core_content("~/.claude/agents/nw/test.md") is True
        assert identifier.is_core_content("~/.claude/agents/my-custom/test.md") is False

        # Verify UpdateService has access to CoreContentIdentifier for selective replacement
        # This test will FAIL until UpdateService is updated to use CoreContentIdentifier
        assert hasattr(service, "_content_identifier") or hasattr(
            service, "_core_content_identifier"
        ), (
            "UpdateService should have CoreContentIdentifier as dependency for selective content replacement"
        )

    def test_update_service_preserves_user_agents(self, tmp_path):
        """
        GIVEN: Maria has custom agents in ~/.claude/agents/my-custom-agent/
        WHEN: update() is called with selective replacement
        THEN: User agents are NOT replaced
        """
        from nWave.core.versioning.application.update_service import UpdateService

        # Arrange
        claude_dir = tmp_path / ".claude"
        claude_dir.mkdir(parents=True)
        version_file = claude_dir / "VERSION"
        version_file.write_text("1.2.3")

        # Create user's custom agent
        custom_agent_dir = claude_dir / "agents" / "my-custom-agent"
        custom_agent_dir.mkdir(parents=True)
        custom_agent_file = custom_agent_dir / "agent.md"
        custom_agent_file.write_text("# Maria's Custom Agent\nDo not modify!")

        # Create nWave agent (should be replaced)
        nw_agent_dir = claude_dir / "agents" / "nw"
        nw_agent_dir.mkdir(parents=True)
        nw_agent_file = nw_agent_dir / "software-crafter.md"
        nw_agent_file.write_text("# nWave Agent v1.2.3\nOld version")

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

        # Configure file_system to track which paths are being replaced
        replaced_paths = []
        mock_file_system.replace_directory.side_effect = (
            lambda src, dst: replaced_paths.append(str(dst))
        )

        service = UpdateService(
            file_system=mock_file_system,
            github_api=mock_github_api,
            download=mock_download,
            checksum=mock_checksum,
            nwave_home=claude_dir,
        )

        # Act
        service.update()

        # Assert: User agent content should be preserved
        assert custom_agent_file.exists(), "User agent file should still exist"
        assert (
            custom_agent_file.read_text() == "# Maria's Custom Agent\nDo not modify!"
        ), "User agent content should be unchanged"

        # Assert: User agent path should NOT be in replaced_paths
        str(custom_agent_dir)
        assert not any("my-custom-agent" in p for p in replaced_paths), (
            f"User agent directory should NOT be replaced. Replaced paths: {replaced_paths}"
        )

    def test_update_service_preserves_user_commands(self, tmp_path):
        """
        GIVEN: Maria has custom commands in ~/.claude/commands/my-custom-command/
        WHEN: update() is called with selective replacement
        THEN: User commands are NOT replaced
        """
        from nWave.core.versioning.application.update_service import UpdateService

        # Arrange
        claude_dir = tmp_path / ".claude"
        claude_dir.mkdir(parents=True)
        version_file = claude_dir / "VERSION"
        version_file.write_text("1.2.3")

        # Create user's custom command
        custom_command_dir = claude_dir / "commands" / "my-custom-command"
        custom_command_dir.mkdir(parents=True)
        custom_command_file = custom_command_dir / "run.md"
        custom_command_file.write_text("# Maria's Custom Command\nDo not modify!")

        # Create nWave command (should be replaced)
        nw_command_dir = claude_dir / "commands" / "nw"
        nw_command_dir.mkdir(parents=True)
        nw_command_file = nw_command_dir / "develop.md"
        nw_command_file.write_text("# nWave Command v1.2.3\nOld version")

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

        # Configure file_system to track which paths are being replaced
        replaced_paths = []
        mock_file_system.replace_directory.side_effect = (
            lambda src, dst: replaced_paths.append(str(dst))
        )

        service = UpdateService(
            file_system=mock_file_system,
            github_api=mock_github_api,
            download=mock_download,
            checksum=mock_checksum,
            nwave_home=claude_dir,
        )

        # Act
        service.update()

        # Assert: User command content should be preserved
        assert custom_command_file.exists(), "User command file should still exist"
        assert (
            custom_command_file.read_text()
            == "# Maria's Custom Command\nDo not modify!"
        ), "User command content should be unchanged"

        # Assert: User command path should NOT be in replaced_paths
        assert not any("my-custom-command" in p for p in replaced_paths), (
            f"User command directory should NOT be replaced. Replaced paths: {replaced_paths}"
        )

    def test_update_service_replaces_nw_content(self, tmp_path):
        """
        GIVEN: nWave content exists in ~/.claude/agents/nw/ and ~/.claude/commands/nw/
        WHEN: update() is called with selective replacement
        THEN: nWave-prefixed content IS replaced
        """
        from nWave.core.versioning.application.update_service import UpdateService

        # Arrange
        claude_dir = tmp_path / ".claude"
        claude_dir.mkdir(parents=True)
        version_file = claude_dir / "VERSION"
        version_file.write_text("1.2.3")

        # Create nWave agent (should be replaced)
        nw_agent_dir = claude_dir / "agents" / "nw"
        nw_agent_dir.mkdir(parents=True)
        nw_agent_file = nw_agent_dir / "software-crafter.md"
        nw_agent_file.write_text("# nWave Agent v1.2.3\nOld version")

        # Create nWave command (should be replaced)
        nw_command_dir = claude_dir / "commands" / "nw"
        nw_command_dir.mkdir(parents=True)
        nw_command_file = nw_command_dir / "develop.md"
        nw_command_file.write_text("# nWave Command v1.2.3\nOld version")

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

        # Configure file_system to track which paths are being replaced
        replaced_paths = []
        mock_file_system.replace_directory.side_effect = (
            lambda src, dst: replaced_paths.append(str(dst))
        )

        service = UpdateService(
            file_system=mock_file_system,
            github_api=mock_github_api,
            download=mock_download,
            checksum=mock_checksum,
            nwave_home=claude_dir,
        )

        # Act: Patch _is_test_mode to return False so _apply_selective_update is executed
        # This allows us to test the actual business logic of selective content replacement
        with patch.object(service, "_is_test_mode", return_value=False):
            service.update()

        # Assert: nWave content paths SHOULD be in replaced_paths
        assert any("agents/nw" in p or "agents\\nw" in p for p in replaced_paths), (
            f"nWave agents directory SHOULD be replaced. Replaced paths: {replaced_paths}"
        )
        assert any("commands/nw" in p or "commands\\nw" in p for p in replaced_paths), (
            f"nWave commands directory SHOULD be replaced. Replaced paths: {replaced_paths}"
        )


# ============================================================================
# Step 04-05: Local RC version triggers customization warning
# ============================================================================


class TestUpdateServiceDetectsRCVersion:
    """
    Test that UpdateService detects RC (Release Candidate) versions.

    Step 04-05: Local RC version triggers customization warning.

    Key behaviors:
    - RC versions indicate local customizations
    - Update should warn user before overwriting
    - User must be able to proceed or cancel

    HEXAGONAL ARCHITECTURE:
    - UpdateService is APPLICATION SERVICE (inside hexagon)
    - Uses REAL domain objects (Version) - never mocked
    - Mocks only PORT interfaces (FileSystemPort, GitHubAPIPort)
    """

    def test_update_service_detects_rc_version(self):
        """
        GIVEN: UpdateService with RC version (1.2.3-rc.main.20260127.1)
        WHEN: check_version_type() is called
        THEN: Returns that current version is a prerelease/RC version
        """
        from nWave.core.versioning.application.update_service import UpdateService

        # Arrange
        mock_file_system = MagicMock()
        mock_github_api = MagicMock()
        mock_download = MagicMock()
        mock_checksum = MagicMock()

        # RC version - indicates local customizations
        rc_version = Version("1.2.3-rc.main.20260127.1")
        mock_file_system.read_version.return_value = rc_version

        service = UpdateService(
            file_system=mock_file_system,
            github_api=mock_github_api,
            download=mock_download,
            checksum=mock_checksum,
        )

        # Act
        is_rc = service.is_local_customization()

        # Assert
        assert is_rc is True, (
            "RC version 1.2.3-rc.main.20260127.1 should be detected as local customization"
        )

    def test_update_service_stable_version_not_rc(self):
        """
        GIVEN: UpdateService with stable version (1.2.3)
        WHEN: check_version_type() is called
        THEN: Returns that current version is NOT an RC version
        """
        from nWave.core.versioning.application.update_service import UpdateService

        # Arrange
        mock_file_system = MagicMock()
        mock_github_api = MagicMock()
        mock_download = MagicMock()
        mock_checksum = MagicMock()

        # Stable version - NOT local customization
        stable_version = Version("1.2.3")
        mock_file_system.read_version.return_value = stable_version

        service = UpdateService(
            file_system=mock_file_system,
            github_api=mock_github_api,
            download=mock_download,
            checksum=mock_checksum,
        )

        # Act
        is_rc = service.is_local_customization()

        # Assert
        assert is_rc is False, (
            "Stable version 1.2.3 should NOT be detected as local customization"
        )

    def test_update_service_returns_customization_warning(self):
        """
        GIVEN: UpdateService with RC version
        WHEN: get_update_warnings() is called
        THEN: Returns customization warning message
        """
        from nWave.core.versioning.application.update_service import UpdateService

        # Arrange
        mock_file_system = MagicMock()
        mock_github_api = MagicMock()
        mock_download = MagicMock()
        mock_checksum = MagicMock()

        rc_version = Version("1.2.3-rc.main.20260127.1")
        mock_file_system.read_version.return_value = rc_version
        mock_github_api.get_latest_release.return_value = MagicMock(
            version=Version("1.3.0"),
            checksum="abc123def456",
            download_url="https://example.com/release.tar.gz",
        )

        service = UpdateService(
            file_system=mock_file_system,
            github_api=mock_github_api,
            download=mock_download,
            checksum=mock_checksum,
        )

        # Act
        warnings = service.get_update_warnings()

        # Assert
        assert any("Local customizations detected" in w for w in warnings), (
            f"Expected 'Local customizations detected' warning, got: {warnings}"
        )


# ============================================================================
# Step 04-10: Already up-to-date shows message without update
# ============================================================================


class TestUpdateServiceDetectsAlreadyUpToDate:
    """
    Test that UpdateService correctly detects when already up to date.

    Step 04-10: Already up-to-date shows message without update.

    Key behaviors:
    - When current_version == latest_version, no update is needed
    - Return UpdateResult with success=True but indication of "Already up to date"
    - No backup should be created
    - No download should occur
    """

    def test_update_service_detects_already_up_to_date(self):
        """
        GIVEN: Sofia has nWave v1.3.0 installed
        AND: GitHub API returns v1.3.0 as latest release
        WHEN: update() is called
        THEN: UpdateResult indicates already up to date
        AND: No update operations occur
        """
        from nWave.core.versioning.application.update_service import UpdateService

        # Arrange
        mock_file_system = MagicMock()
        mock_github_api = MagicMock()
        mock_download = MagicMock()
        mock_checksum = MagicMock()

        # Sofia has v1.3.0 installed
        current_version = Version("1.3.0")
        mock_file_system.read_version.return_value = current_version
        mock_file_system.list_backups.return_value = []

        # GitHub API returns same version as latest
        mock_github_api.get_latest_release.return_value = MagicMock(
            version=Version("1.3.0"),
            checksum="abc123def456",
            download_url="https://github.com/releases/v1.3.0.tar.gz",
        )

        service = UpdateService(
            file_system=mock_file_system,
            github_api=mock_github_api,
            download=mock_download,
            checksum=mock_checksum,
        )

        # Act
        result = service.update()

        # Assert: Result indicates up to date
        assert result.success is True, (
            "Should succeed (already up to date is a success state)"
        )
        assert result.error_message == "Already up to date", (
            f"Error message should be 'Already up to date', got: {result.error_message}"
        )
        assert result.previous_version == current_version, (
            "Previous version should match"
        )

    def test_no_backup_on_up_to_date(self):
        """
        GIVEN: UpdateService with current version == latest version
        WHEN: update() is called
        THEN: No backup is created
        """
        from nWave.core.versioning.application.update_service import UpdateService

        # Arrange
        mock_file_system = MagicMock()
        mock_github_api = MagicMock()
        mock_download = MagicMock()
        mock_checksum = MagicMock()

        mock_file_system.read_version.return_value = Version("1.3.0")
        mock_file_system.list_backups.return_value = []
        mock_github_api.get_latest_release.return_value = MagicMock(
            version=Version("1.3.0"),
            checksum="abc123def456",
            download_url="https://github.com/releases/v1.3.0.tar.gz",
        )

        service = UpdateService(
            file_system=mock_file_system,
            github_api=mock_github_api,
            download=mock_download,
            checksum=mock_checksum,
        )

        # Act
        service.update()

        # Assert: Backup should NOT be created
        mock_file_system.create_backup.assert_not_called()

    def test_no_download_on_up_to_date(self):
        """
        GIVEN: UpdateService with current version == latest version
        WHEN: update() is called
        THEN: No download occurs
        """
        from nWave.core.versioning.application.update_service import UpdateService

        # Arrange
        mock_file_system = MagicMock()
        mock_github_api = MagicMock()
        mock_download = MagicMock()
        mock_checksum = MagicMock()

        mock_file_system.read_version.return_value = Version("1.3.0")
        mock_file_system.list_backups.return_value = []
        mock_github_api.get_latest_release.return_value = MagicMock(
            version=Version("1.3.0"),
            checksum="abc123def456",
            download_url="https://github.com/releases/v1.3.0.tar.gz",
        )

        service = UpdateService(
            file_system=mock_file_system,
            github_api=mock_github_api,
            download=mock_download,
            checksum=mock_checksum,
        )

        # Act
        service.update()

        # Assert: Download should NOT be called
        mock_download.download.assert_not_called()

    def test_up_to_date_with_greater_or_equal_version(self):
        """
        GIVEN: UpdateService with current version > latest version
        WHEN: update() is called
        THEN: No update occurs (handles edge case of local RC version being higher)
        """
        from nWave.core.versioning.application.update_service import UpdateService

        # Arrange
        mock_file_system = MagicMock()
        mock_github_api = MagicMock()
        mock_download = MagicMock()
        mock_checksum = MagicMock()

        # Local version is higher than official release
        mock_file_system.read_version.return_value = Version("1.3.1")
        mock_file_system.list_backups.return_value = []
        mock_github_api.get_latest_release.return_value = MagicMock(
            version=Version("1.3.0"),
            checksum="abc123def456",
            download_url="https://github.com/releases/v1.3.0.tar.gz",
        )

        service = UpdateService(
            file_system=mock_file_system,
            github_api=mock_github_api,
            download=mock_download,
            checksum=mock_checksum,
        )

        # Act
        result = service.update()

        # Assert
        assert result.success is True
        mock_download.download.assert_not_called()
        mock_file_system.create_backup.assert_not_called()


# ============================================================================
# Step 04-03: Major version update proceeds with confirmation
# ============================================================================


class TestUpdateServiceProceedsOnMajorConfirmation:
    """
    Test that UpdateService proceeds with update when major version confirmation given.

    Step 04-03: Major version update proceeds with confirmation.

    Key behaviors:
    - UpdateService.update() proceeds normally when called after confirmation
    - Version file is updated to new major version (v2.0.0)
    - Update completes successfully

    HEXAGONAL ARCHITECTURE:
    - UpdateService is APPLICATION SERVICE (inside hexagon)
    - Uses REAL domain objects (Version) - never mocked
    - Mocks only PORT interfaces (FileSystemPort, GitHubAPIPort, etc.)
    """

    def test_update_service_proceeds_on_major_confirmation(self, tmp_path):
        """
        GIVEN: UpdateService with current v1.3.0 and target v2.0.0
        AND: Major version confirmation has been given
        WHEN: update() is called
        THEN: Update proceeds successfully to v2.0.0
        AND: VERSION file is updated to 2.0.0
        """
        from nWave.core.versioning.application.update_service import UpdateService

        # Arrange
        claude_dir = tmp_path / ".claude"
        claude_dir.mkdir(parents=True)
        version_file = claude_dir / "VERSION"
        version_file.write_text("1.3.0")

        mock_file_system = MagicMock()
        mock_github_api = MagicMock()
        mock_download = MagicMock()
        mock_checksum = MagicMock()

        # Configure mocks - major version change: 1.3.0 -> 2.0.0
        mock_file_system.read_version.return_value = Version("1.3.0")
        mock_file_system.list_backups.return_value = []
        mock_github_api.get_latest_release.return_value = MagicMock(
            version=Version("2.0.0"),
            checksum="abc123def456",
            download_url="https://github.com/releases/v2.0.0.tar.gz",
        )
        mock_checksum.verify.return_value = True

        service = UpdateService(
            file_system=mock_file_system,
            github_api=mock_github_api,
            download=mock_download,
            checksum=mock_checksum,
            nwave_home=claude_dir,
        )

        # Verify this IS a major version change
        assert (
            service.is_major_version_change(Version("1.3.0"), Version("2.0.0")) is True
        )

        # Act - Confirmation already given, proceed with update
        result = service.update()

        # Assert: Update succeeded to v2.0.0
        assert result.success is True, (
            f"Update should succeed, got: {result.error_message}"
        )
        assert result.new_version == Version("2.0.0"), (
            f"New version should be 2.0.0, got: {result.new_version}"
        )
        assert result.previous_version == Version("1.3.0"), (
            f"Previous version should be 1.3.0, got: {result.previous_version}"
        )

        # Assert: VERSION file was written with new version
        assert version_file.read_text().strip() == "2.0.0", (
            f"VERSION file should contain 2.0.0, got: {version_file.read_text()}"
        )

    def test_update_service_major_version_backup_created(self, tmp_path):
        """
        GIVEN: UpdateService with current v1.3.0 and target v2.0.0
        WHEN: update() is called after major version confirmation
        THEN: Backup is created before update proceeds
        """
        from nWave.core.versioning.application.update_service import UpdateService

        # Arrange
        claude_dir = tmp_path / ".claude"
        claude_dir.mkdir(parents=True)
        version_file = claude_dir / "VERSION"
        version_file.write_text("1.3.0")

        mock_file_system = MagicMock()
        mock_github_api = MagicMock()
        mock_download = MagicMock()
        mock_checksum = MagicMock()

        mock_file_system.read_version.return_value = Version("1.3.0")
        mock_file_system.list_backups.return_value = []
        mock_github_api.get_latest_release.return_value = MagicMock(
            version=Version("2.0.0"),
            checksum="abc123def456",
            download_url="https://github.com/releases/v2.0.0.tar.gz",
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

        # Assert: Backup was created
        assert result.success is True
        mock_file_system.create_backup.assert_called_once()
        assert result.backup_path is not None, "Backup path should be set"
