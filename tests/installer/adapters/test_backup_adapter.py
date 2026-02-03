"""Tests for FileSystemBackupAdapter.

These tests verify the backup adapter correctly implements the BackupPort
protocol for filesystem-based backup operations.
"""

import time
from datetime import datetime
from pathlib import Path

from crafter_ai.installer.adapters.backup_adapter import FileSystemBackupAdapter
from crafter_ai.installer.ports.backup_port import (
    BackupInfo,
    BackupPort,
    BackupResult,
    CleanupResult,
    RestoreResult,
)


class TestFileSystemBackupAdapterProtocol:
    """Test that FileSystemBackupAdapter implements BackupPort protocol."""

    def test_adapter_implements_backup_port_protocol(self) -> None:
        """FileSystemBackupAdapter should implement BackupPort protocol."""
        adapter = FileSystemBackupAdapter(backup_root=Path("/tmp/test"))
        assert isinstance(adapter, BackupPort)


class TestCreateBackup:
    """Tests for create_backup method."""

    def test_create_backup_creates_timestamped_directory(self, tmp_path: Path) -> None:
        """create_backup should create a backup directory with timestamp."""
        # Arrange
        backup_root = tmp_path / "backups"
        source = tmp_path / "source"
        source.mkdir()
        # Create a file from BACKUP_TARGETS so backup has something to copy
        (source / "CLAUDE.md").write_text("test content")

        adapter = FileSystemBackupAdapter(backup_root=backup_root)

        # Act
        result = adapter.create_backup(source)

        # Assert
        assert result.success is True
        assert result.backup_path is not None
        assert result.backup_path.exists()
        assert result.backup_path.name.startswith("nwave-")
        # Format: nwave-YYYYMMDD-HHMMSS
        assert len(result.backup_path.name) == len("nwave-YYYYMMDD-HHMMSS")

    def test_create_backup_copies_nwave_config_contents(self, tmp_path: Path) -> None:
        """create_backup should copy only nwave-related files and directories."""
        # Arrange
        backup_root = tmp_path / "backups"
        source = tmp_path / "source"
        source.mkdir()

        # Create nwave-specific files (from BACKUP_TARGETS)
        (source / "commands").mkdir()
        (source / "commands" / "cmd1.md").write_text("command content")
        (source / "templates").mkdir()
        (source / "templates" / "tpl1.md").write_text("template content")
        (source / "CLAUDE.md").write_text("claude config")
        (source / "nwave-manifest.txt").write_text("manifest: true")
        # Also create non-backup files that should NOT be copied
        (source / "history.jsonl").write_text("should not be copied")
        (source / "projects").mkdir()
        (source / "projects" / "data.json").write_text("should not be copied")

        adapter = FileSystemBackupAdapter(backup_root=backup_root)

        # Act
        result = adapter.create_backup(source)

        # Assert
        assert result.success is True
        backup_path = result.backup_path
        assert (backup_path / "commands" / "cmd1.md").exists()
        assert (backup_path / "commands" / "cmd1.md").read_text() == "command content"
        assert (backup_path / "templates" / "tpl1.md").exists()
        assert (backup_path / "CLAUDE.md").exists()
        assert (backup_path / "nwave-manifest.txt").exists()
        # Non-backup files should NOT be copied
        assert not (backup_path / "history.jsonl").exists()
        assert not (backup_path / "projects").exists()

    def test_create_backup_returns_success_with_backup_path(
        self, tmp_path: Path
    ) -> None:
        """create_backup should return success with backup_path and timestamp."""
        # Arrange
        backup_root = tmp_path / "backups"
        source = tmp_path / "source"
        source.mkdir()
        (source / "VERSION").write_text("0.1.0")

        adapter = FileSystemBackupAdapter(backup_root=backup_root)

        # Act
        result = adapter.create_backup(source)

        # Assert
        assert isinstance(result, BackupResult)
        assert result.success is True
        assert result.backup_path is not None
        assert result.timestamp is not None
        assert result.error_message is None

    def test_create_backup_returns_failure_when_source_not_found(
        self, tmp_path: Path
    ) -> None:
        """create_backup should return failure when source path doesn't exist."""
        # Arrange
        backup_root = tmp_path / "backups"
        nonexistent_source = tmp_path / "nonexistent"

        adapter = FileSystemBackupAdapter(backup_root=backup_root)

        # Act
        result = adapter.create_backup(nonexistent_source)

        # Assert
        assert result.success is False
        assert result.backup_path is None
        assert result.error_message is not None
        assert (
            "not found" in result.error_message.lower()
            or "does not exist" in result.error_message.lower()
        )


class TestRestoreBackup:
    """Tests for restore_backup method."""

    def test_restore_backup_restores_contents_to_target(self, tmp_path: Path) -> None:
        """restore_backup should restore backup contents to target path."""
        # Arrange
        backup_root = tmp_path / "backups"
        source = tmp_path / "source"
        target = tmp_path / "target"
        source.mkdir()

        # Use BACKUP_TARGETS files
        (source / "commands").mkdir()
        (source / "commands" / "cmd1.md").write_text("command content")
        (source / "nwave-manifest.txt").write_text("manifest: true")

        adapter = FileSystemBackupAdapter(backup_root=backup_root)

        # Create backup first
        backup_result = adapter.create_backup(source)
        assert backup_result.success is True

        # Act
        restore_result = adapter.restore_backup(backup_result.backup_path, target)

        # Assert
        assert restore_result.success is True
        assert restore_result.restored_path == target
        assert (target / "commands" / "cmd1.md").exists()
        assert (target / "commands" / "cmd1.md").read_text() == "command content"
        assert (target / "nwave-manifest.txt").exists()

    def test_restore_backup_returns_failure_when_backup_not_found(
        self, tmp_path: Path
    ) -> None:
        """restore_backup should return failure when backup path doesn't exist."""
        # Arrange
        backup_root = tmp_path / "backups"
        nonexistent_backup = tmp_path / "nonexistent_backup"
        target = tmp_path / "target"

        adapter = FileSystemBackupAdapter(backup_root=backup_root)

        # Act
        result = adapter.restore_backup(nonexistent_backup, target)

        # Assert
        assert isinstance(result, RestoreResult)
        assert result.success is False
        assert result.restored_path is None
        assert result.error_message is not None
        assert (
            "not found" in result.error_message.lower()
            or "does not exist" in result.error_message.lower()
        )


class TestListBackups:
    """Tests for list_backups method."""

    def test_list_backups_returns_sorted_list_newest_first(
        self, tmp_path: Path
    ) -> None:
        """list_backups should return backups sorted by timestamp, newest first."""
        # Arrange
        backup_root = tmp_path / "backups"
        source = tmp_path / "source"
        source.mkdir()
        (source / "VERSION").write_text("0.1.0")

        adapter = FileSystemBackupAdapter(backup_root=backup_root)

        # Create multiple backups with small delay
        adapter.create_backup(source)
        time.sleep(1.1)  # Ensure different timestamps
        adapter.create_backup(source)
        time.sleep(1.1)
        result3 = adapter.create_backup(source)

        # Act
        backups = adapter.list_backups()

        # Assert
        assert len(backups) == 3
        assert all(isinstance(b, BackupInfo) for b in backups)
        # Newest should be first
        assert backups[0].path == result3.backup_path
        # Verify sorted by timestamp descending
        for i in range(len(backups) - 1):
            assert backups[i].timestamp >= backups[i + 1].timestamp

    def test_list_backups_returns_empty_list_when_no_backups(
        self, tmp_path: Path
    ) -> None:
        """list_backups should return empty list when no backups exist."""
        # Arrange
        backup_root = tmp_path / "backups"
        adapter = FileSystemBackupAdapter(backup_root=backup_root)

        # Act
        backups = adapter.list_backups()

        # Assert
        assert backups == []

    def test_list_backups_includes_size_information(self, tmp_path: Path) -> None:
        """list_backups should include size_bytes for each backup."""
        # Arrange
        backup_root = tmp_path / "backups"
        source = tmp_path / "source"
        source.mkdir()
        (source / "VERSION").write_text("test content with some bytes")

        adapter = FileSystemBackupAdapter(backup_root=backup_root)
        adapter.create_backup(source)

        # Act
        backups = adapter.list_backups()

        # Assert
        assert len(backups) == 1
        assert backups[0].size_bytes > 0


class TestCleanupOldBackups:
    """Tests for cleanup_old_backups method."""

    def test_cleanup_old_backups_removes_oldest_keeps_newest(
        self, tmp_path: Path
    ) -> None:
        """cleanup_old_backups should remove oldest, keep specified count."""
        # Arrange
        backup_root = tmp_path / "backups"
        source = tmp_path / "source"
        source.mkdir()
        (source / "VERSION").write_text("0.1.0")

        adapter = FileSystemBackupAdapter(backup_root=backup_root)

        # Create 5 backups
        oldest_backup = adapter.create_backup(source)
        time.sleep(1.1)
        adapter.create_backup(source)
        time.sleep(1.1)
        adapter.create_backup(source)
        time.sleep(1.1)
        adapter.create_backup(source)
        time.sleep(1.1)
        newest_backup = adapter.create_backup(source)

        # Act - keep only 2
        result = adapter.cleanup_old_backups(keep_count=2)

        # Assert
        assert isinstance(result, CleanupResult)
        assert result.success is True
        assert result.removed_count == 3
        assert result.kept_count == 2
        assert result.error_message is None

        # Verify oldest removed, newest kept
        assert not oldest_backup.backup_path.exists()
        assert newest_backup.backup_path.exists()

        # List should now have 2
        remaining = adapter.list_backups()
        assert len(remaining) == 2

    def test_cleanup_old_backups_handles_fewer_backups_than_keep_count(
        self, tmp_path: Path
    ) -> None:
        """cleanup_old_backups should do nothing when fewer backups than keep_count."""
        # Arrange
        backup_root = tmp_path / "backups"
        source = tmp_path / "source"
        source.mkdir()
        (source / "VERSION").write_text("0.1.0")

        adapter = FileSystemBackupAdapter(backup_root=backup_root)

        # Create only 2 backups
        adapter.create_backup(source)
        time.sleep(1.1)
        adapter.create_backup(source)

        # Act - keep 5 (more than we have)
        result = adapter.cleanup_old_backups(keep_count=5)

        # Assert
        assert result.success is True
        assert result.removed_count == 0
        assert result.kept_count == 2

        # All backups should still exist
        remaining = adapter.list_backups()
        assert len(remaining) == 2

    def test_cleanup_old_backups_with_no_backups(self, tmp_path: Path) -> None:
        """cleanup_old_backups should handle empty backup directory gracefully."""
        # Arrange
        backup_root = tmp_path / "backups"
        adapter = FileSystemBackupAdapter(backup_root=backup_root)

        # Act
        result = adapter.cleanup_old_backups(keep_count=5)

        # Assert
        assert result.success is True
        assert result.removed_count == 0
        assert result.kept_count == 0


class TestBackupPathFormat:
    """Tests for backup path naming format."""

    def test_backup_path_format_matches_spec(self, tmp_path: Path) -> None:
        """Backup path should follow format: nwave-YYYYMMDD-HHMMSS."""
        # Arrange
        backup_root = tmp_path / "backups"
        source = tmp_path / "source"
        source.mkdir()
        (source / "VERSION").write_text("0.1.0")

        adapter = FileSystemBackupAdapter(backup_root=backup_root)

        # Act
        result = adapter.create_backup(source)

        # Assert
        backup_name = result.backup_path.name
        # Should match pattern nwave-YYYYMMDD-HHMMSS
        assert backup_name.startswith("nwave-")
        parts = backup_name.split("-")
        assert len(parts) == 3
        assert parts[0] == "nwave"
        assert len(parts[1]) == 8  # YYYYMMDD
        assert len(parts[2]) == 6  # HHMMSS
        # Verify it's a valid date/time
        datetime.strptime(f"{parts[1]}-{parts[2]}", "%Y%m%d-%H%M%S")
