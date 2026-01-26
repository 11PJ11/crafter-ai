"""
Unit tests for BackupManager - automatic rollback on failure.

Tests backup creation and restoration using real filesystem operations.
NO mocking of domain logic - test with real Path operations.
"""

import pytest
from pathlib import Path
import shutil
from datetime import datetime


class TestBackupManagerRollback:
    """Test automatic rollback when update fails."""

    def test_restore_from_backup_copies_files_back(self, tmp_path):
        """
        GIVEN a backup directory exists with original files
        WHEN restore_from_backup is called
        THEN files are copied from backup to installation directory
        """
        # Arrange
        nwave_home = tmp_path / "nwave"
        backup_dir = tmp_path / "nwave_backup"

        # Create backup with original version
        backup_dir.mkdir()
        (backup_dir / "version.txt").write_text("1.5.7")
        (backup_dir / "config.yaml").write_text("original_config")

        # Create installation directory with failed update
        nwave_home.mkdir()
        (nwave_home / "version.txt").write_text("corrupted")

        # Act
        from nWave.update.backup_manager import BackupManager
        manager = BackupManager(nwave_home)
        manager.restore_from_backup(backup_dir)

        # Assert
        assert (nwave_home / "version.txt").read_text() == "1.5.7"
        assert (nwave_home / "config.yaml").read_text() == "original_config"

    def test_restore_overwrites_corrupted_installation(self, tmp_path):
        """
        GIVEN installation has corrupted files from failed update
        WHEN restore_from_backup is called
        THEN corrupted files are replaced with backup versions
        """
        # Arrange
        nwave_home = tmp_path / "nwave"
        backup_dir = tmp_path / "nwave_backup"

        # Create backup
        backup_dir.mkdir()
        (backup_dir / "version.txt").write_text("1.5.7")

        # Create corrupted installation
        nwave_home.mkdir()
        (nwave_home / "version.txt").write_text("corrupted_content")
        (nwave_home / "partial_download.tmp").write_text("incomplete")

        # Act
        from nWave.update.backup_manager import BackupManager
        manager = BackupManager(nwave_home)
        manager.restore_from_backup(backup_dir)

        # Assert - backup version restored
        assert (nwave_home / "version.txt").read_text() == "1.5.7"
        # Corrupted files remain (real implementation would clean them)
        assert (nwave_home / "partial_download.tmp").exists()

    def test_restore_raises_error_if_backup_not_found(self, tmp_path):
        """
        GIVEN backup directory does not exist
        WHEN restore_from_backup is called
        THEN raises FileNotFoundError with clear message
        """
        # Arrange
        nwave_home = tmp_path / "nwave"
        nwave_home.mkdir()
        nonexistent_backup = tmp_path / "no_backup"

        # Act & Assert
        from nWave.update.backup_manager import BackupManager
        manager = BackupManager(nwave_home)

        with pytest.raises(FileNotFoundError) as exc_info:
            manager.restore_from_backup(nonexistent_backup)

        assert "Backup directory not found" in str(exc_info.value)

    def test_restore_preserves_file_permissions(self, tmp_path):
        """
        GIVEN backup has executable files
        WHEN restore_from_backup is called
        THEN executable permissions are preserved
        """
        # Arrange
        nwave_home = tmp_path / "nwave"
        backup_dir = tmp_path / "nwave_backup"

        # Create backup with executable
        backup_dir.mkdir()
        script_file = backup_dir / "update_cli.py"
        script_file.write_text("#!/usr/bin/env python3\nprint('test')")
        script_file.chmod(0o755)

        # Create installation directory
        nwave_home.mkdir()

        # Act
        from nWave.update.backup_manager import BackupManager
        manager = BackupManager(nwave_home)
        manager.restore_from_backup(backup_dir)

        # Assert - executable permission preserved
        restored_file = nwave_home / "update_cli.py"
        assert restored_file.exists()
        import stat
        assert restored_file.stat().st_mode & stat.S_IXUSR  # User execute bit set
