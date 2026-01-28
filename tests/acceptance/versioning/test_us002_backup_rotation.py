"""
Acceptance tests for US-002: Backup rotation maintains exactly 3 copies.

Step 04-08: Backup rotation maintains exactly 3 copies

HEXAGONAL BOUNDARY ENFORCEMENT:
- Tests invoke through UpdateService application service
- Mocking allowed ONLY at port boundaries (DownloadPort, FileSystemPort, etc.)
- Real domain objects used (Version, BackupPolicy) - NEVER mocked

Scenario from acceptance-tests.feature (line 188):
    Scenario: Backup rotation maintains exactly 3 copies
      Given Roberto has nWave v1.2.3 installed in the test ~/.claude/ directory
      And 3 existing backups exist at ~/.claude.backup.20260124120000/
      And ~/.claude.backup.20260125120000/
      And ~/.claude.backup.20260126120000/
      And the GitHub API returns v1.3.0 as the latest release with valid checksum
      And the download server provides a valid release asset
      When Roberto runs the /nw:update command through the CLI entry point
      And Roberto confirms the update when prompted
      Then a new backup is created with current timestamp
      And the oldest backup ~/.claude.backup.20260124120000/ is deleted
      And exactly 3 backups remain
"""

import pytest
from pathlib import Path
from unittest.mock import MagicMock

# Domain objects - REAL, never mocked
from nWave.core.versioning.domain.version import Version
from nWave.core.versioning.domain.backup_policy import BackupPolicy


class TestBackupRotationMaintainsExactly3Copies:
    """
    Step 04-08: Backup rotation maintains exactly 3 copies.

    Acceptance Criteria:
    - New backup created with current timestamp
    - Oldest backup ~/.claude.backup.20260124120000/ is deleted
    - Exactly 3 backups remain
    """

    def test_update_service_rotates_backups_keeping_max_3(self, tmp_path):
        """
        GIVEN: Roberto has nWave v1.2.3 installed
        AND: 3 existing backups exist (20260124, 20260125, 20260126)
        AND: GitHub API returns v1.3.0 as latest release with valid checksum
        AND: Download server provides a valid release asset
        WHEN: Roberto runs /nw:update command and confirms
        THEN: A new backup is created with current timestamp
        AND: The oldest backup (20260124) is deleted
        AND: Exactly 3 backups remain
        """
        from nWave.core.versioning.application.update_service import UpdateService

        # Arrange: Set up test installation
        claude_dir = tmp_path / ".claude"
        claude_dir.mkdir(parents=True)
        version_file = claude_dir / "VERSION"
        version_file.write_text("1.2.3")

        # Create 3 existing backups
        existing_backups = [
            tmp_path / ".claude.backup.20260124120000",
            tmp_path / ".claude.backup.20260125120000",
            tmp_path / ".claude.backup.20260126120000",
        ]
        for backup in existing_backups:
            backup.mkdir(parents=True)
            (backup / "VERSION").write_text("1.2.3")

        # Track state
        current_backups = existing_backups.copy()
        deleted_backups = []
        new_backup_path = None

        # Mock ports at hexagon boundary
        mock_file_system = MagicMock()
        mock_github_api = MagicMock()
        mock_download = MagicMock()
        mock_checksum = MagicMock()

        # Configure mocks with real domain objects
        mock_file_system.read_version.return_value = Version("1.2.3")

        def list_backups():
            # Returns current state including any newly created backup
            return current_backups.copy()

        def create_backup(backup_path):
            nonlocal new_backup_path
            new_backup_path = backup_path
            current_backups.append(backup_path)

        def delete_backup(backup_path):
            deleted_backups.append(backup_path)
            if backup_path in current_backups:
                current_backups.remove(backup_path)
            return True

        mock_file_system.list_backups.side_effect = list_backups
        mock_file_system.create_backup.side_effect = create_backup
        mock_file_system.delete_backup.side_effect = delete_backup

        mock_github_api.get_latest_release.return_value = MagicMock(
            version=Version("1.3.0"),
            checksum="abc123def456",
            download_url="https://github.com/releases/v1.3.0.tar.gz",
        )

        # Download succeeds
        mock_download.download.return_value = None

        # Checksum validates successfully
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

        # Assert
        assert result.success is True, f"Update should succeed, got error: {result.error_message}"

        # Verify backup was created
        assert result.backup_path is not None, "New backup should be created"
        mock_file_system.create_backup.assert_called_once()

        # Verify oldest backup was identified for deletion
        assert len(deleted_backups) == 1, f"Expected 1 backup deleted, got {len(deleted_backups)}"
        assert deleted_backups[0] == tmp_path / ".claude.backup.20260124120000", (
            f"Oldest backup should be deleted, got {deleted_backups[0]}"
        )

        # Verify exactly 3 backups remain
        assert len(current_backups) == 3, f"Expected 3 backups remaining, got {len(current_backups)}"

    def test_backup_policy_identifies_oldest_for_deletion(self):
        """
        GIVEN: 4 existing backups (3 original + 1 new from current update)
        WHEN: BackupPolicy determines which to delete
        THEN: Returns the oldest backup for deletion

        NOTE: This tests the scenario AFTER create_backup() has added a new
        backup, so there are 4 total when cleanup runs.
        """
        # Arrange: Use REAL BackupPolicy domain object
        policy = BackupPolicy(max_backups=3)
        # 4 backups: 3 original + 1 new (simulating post-create state)
        existing_backups = [
            Path("~/.claude.backup.20260124120000"),  # oldest - should be deleted
            Path("~/.claude.backup.20260125120000"),  # should remain
            Path("~/.claude.backup.20260126120000"),  # should remain
            Path("~/.claude.backup.20260127143000"),  # newest (just created) - should remain
        ]

        # Act
        to_delete = policy.get_backups_to_delete(existing_backups)

        # Assert
        assert len(to_delete) == 1, f"Expected 1 backup to delete, got {len(to_delete)}"
        assert to_delete[0] == Path("~/.claude.backup.20260124120000"), (
            f"Oldest backup should be identified for deletion, got {to_delete[0]}"
        )

    def test_exactly_3_backups_remain_after_rotation(self, tmp_path):
        """
        GIVEN: 3 existing backups
        AND: Update succeeds creating new backup
        WHEN: Backup rotation completes
        THEN: Exactly 3 backups remain (oldest deleted, new one created)
        """
        from nWave.core.versioning.application.update_service import UpdateService

        # Arrange
        claude_dir = tmp_path / ".claude"
        claude_dir.mkdir(parents=True)
        version_file = claude_dir / "VERSION"
        version_file.write_text("1.2.3")

        # Create 3 existing backups
        existing_backups = [
            tmp_path / ".claude.backup.20260124120000",
            tmp_path / ".claude.backup.20260125120000",
            tmp_path / ".claude.backup.20260126120000",
        ]
        for backup in existing_backups:
            backup.mkdir(parents=True)
            (backup / "VERSION").write_text("1.2.3")

        # Track state
        current_backups = existing_backups.copy()
        new_backup_created = []

        mock_file_system = MagicMock()
        mock_github_api = MagicMock()
        mock_download = MagicMock()
        mock_checksum = MagicMock()

        mock_file_system.read_version.return_value = Version("1.2.3")

        def list_backups():
            return current_backups.copy()

        def create_backup(backup_path):
            new_backup_created.append(backup_path)
            current_backups.append(backup_path)

        def delete_backup(backup_path):
            if backup_path in current_backups:
                current_backups.remove(backup_path)
            return True

        mock_file_system.list_backups.side_effect = list_backups
        mock_file_system.create_backup.side_effect = create_backup
        mock_file_system.delete_backup.side_effect = delete_backup

        mock_github_api.get_latest_release.return_value = MagicMock(
            version=Version("1.3.0"),
            checksum="abc123def456",
            download_url="https://github.com/releases/v1.3.0.tar.gz",
        )
        mock_download.download.return_value = None
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

        # Assert
        assert result.success is True
        assert len(new_backup_created) == 1, "One new backup should be created"
        assert len(current_backups) == 3, (
            f"Exactly 3 backups should remain after rotation, got {len(current_backups)}"
        )

        # Verify the oldest one was deleted and newest kept
        backup_names = [b.name for b in current_backups]
        assert ".claude.backup.20260124120000" not in backup_names, (
            "Oldest backup should be deleted"
        )
        assert ".claude.backup.20260125120000" in backup_names, (
            "Second oldest backup should remain"
        )
        assert ".claude.backup.20260126120000" in backup_names, (
            "Previous newest backup should remain"
        )

    def test_new_backup_created_with_current_timestamp(self, tmp_path):
        """
        GIVEN: Roberto performs an update
        WHEN: Backup is created
        THEN: Backup path includes current timestamp in format YYYYMMDDHHMMSS
        """
        from nWave.core.versioning.application.update_service import UpdateService
        from datetime import datetime

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
        mock_file_system.list_backups.return_value = []  # No existing backups
        mock_github_api.get_latest_release.return_value = MagicMock(
            version=Version("1.3.0"),
            checksum="abc123def456",
            download_url="https://github.com/releases/v1.3.0.tar.gz",
        )
        mock_download.download.return_value = None
        mock_checksum.verify.return_value = True

        service = UpdateService(
            file_system=mock_file_system,
            github_api=mock_github_api,
            download=mock_download,
            checksum=mock_checksum,
            nwave_home=claude_dir,
        )

        # Record time before update
        before_time = datetime.now()

        # Act
        result = service.update()

        # Record time after update
        after_time = datetime.now()

        # Assert
        assert result.success is True
        assert result.backup_path is not None

        # Verify backup path format
        backup_name = result.backup_path.name
        assert backup_name.startswith(".claude.backup."), (
            f"Backup should start with '.claude.backup.', got {backup_name}"
        )

        # Extract and validate timestamp
        timestamp_str = backup_name.split(".")[-1]
        assert len(timestamp_str) == 14, (
            f"Timestamp should be 14 chars (YYYYMMDDHHMMSS), got {len(timestamp_str)}"
        )

        # Parse timestamp and verify it's within expected range
        backup_time = datetime.strptime(timestamp_str, "%Y%m%d%H%M%S")
        assert before_time.replace(microsecond=0) <= backup_time <= after_time.replace(microsecond=0), (
            f"Backup timestamp {backup_time} should be between {before_time} and {after_time}"
        )
