"""
Unit tests for backup cleanup functionality (30-day retention policy).

CRITICAL: Tests follow hexagonal architecture - BackupManager is part of domain.
"""

import pytest
from datetime import datetime, timedelta
from pathlib import Path
import tempfile
import shutil
import time
import os
from nWave.infrastructure.backup_manager import BackupManager


class TestBackupCleanup:
    """Test 30-day retention policy for backup cleanup."""

    def test_cleanup_removes_backups_older_than_30_days(self):
        """
        GIVEN: Backup directories with ages 53, 39, and 13 days
        WHEN: Cleanup is triggered with 30-day retention
        THEN: Backups older than 30 days are deleted, recent preserved
        """
        # ARRANGE
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)

            # Create backups with different ages
            backup_53_days = tmp_path / ".claude_bck_20251201"
            backup_39_days = tmp_path / ".claude_bck_20251215"
            backup_13_days = tmp_path / ".claude_bck_20260110"

            backup_53_days.mkdir()
            backup_39_days.mkdir()
            backup_13_days.mkdir()

            # Set modification times
            now = time.time()

            # 53 days ago
            old_time_53 = now - (53 * 24 * 60 * 60)
            (backup_53_days / "marker.txt").write_text("test")
            os.utime(backup_53_days / "marker.txt", (old_time_53, old_time_53))

            # 39 days ago
            old_time_39 = now - (39 * 24 * 60 * 60)
            (backup_39_days / "marker.txt").write_text("test")
            os.utime(backup_39_days / "marker.txt", (old_time_39, old_time_39))

            # 13 days ago
            old_time_13 = now - (13 * 24 * 60 * 60)
            (backup_13_days / "marker.txt").write_text("test")
            os.utime(backup_13_days / "marker.txt", (old_time_13, old_time_13))

            # ACT
            # This will fail until BackupManager.cleanup_old_backups is implemented
            from nWave.infrastructure.backup_manager import BackupManager

            manager = BackupManager(tmp_path)
            manager.cleanup_old_backups(retention_days=30)

            # ASSERT
            assert not backup_53_days.exists(), "53-day old backup should be deleted"
            assert not backup_39_days.exists(), "39-day old backup should be deleted"
            assert backup_13_days.exists(), "13-day old backup should be preserved"


    def test_cleanup_identifies_backup_directories_by_pattern(self):
        """
        GIVEN: Mix of backup dirs and non-backup dirs
        WHEN: Cleanup runs
        THEN: Only .claude_bck_* directories are considered for cleanup
        """
        # ARRANGE
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)

            # Create backup directory (old)
            old_backup = tmp_path / ".claude_bck_20251201"
            old_backup.mkdir()
            (old_backup / "marker.txt").write_text("test")

            # Create non-backup directory (should never be deleted)
            other_dir = tmp_path / ".claude_other"
            other_dir.mkdir()
            (other_dir / "file.txt").write_text("test")

            # Set old modification time on both
            import time, os
            old_time = time.time() - (40 * 24 * 60 * 60)
            os.utime(old_backup / "marker.txt", (old_time, old_time))
            os.utime(other_dir / "file.txt", (old_time, old_time))

            # ACT
            from nWave.infrastructure.backup_manager import BackupManager

            manager = BackupManager(tmp_path)
            manager.cleanup_old_backups(retention_days=30)

            # ASSERT
            assert not old_backup.exists(), "Old backup should be deleted"
            assert other_dir.exists(), "Non-backup directory should be preserved"


    def test_cleanup_handles_empty_backup_directory(self):
        """
        GIVEN: Empty backup directory older than 30 days
        WHEN: Cleanup runs
        THEN: Empty directory is successfully deleted
        """
        # ARRANGE
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)

            old_backup = tmp_path / ".claude_bck_20251201"
            old_backup.mkdir()

            # Set old modification time
            import time, os
            old_time = time.time() - (40 * 24 * 60 * 60)
            os.utime(old_backup, (old_time, old_time))

            # ACT
            from nWave.infrastructure.backup_manager import BackupManager

            manager = BackupManager(tmp_path)
            manager.cleanup_old_backups(retention_days=30)

            # ASSERT
            assert not old_backup.exists(), "Empty old backup should be deleted"


    def test_cleanup_counts_deleted_backups(self):
        """
        GIVEN: Multiple old backups
        WHEN: Cleanup runs
        THEN: Returns count of deleted backups
        """
        # ARRANGE
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)

            # Create 3 old backups
            for i in range(3):
                backup = tmp_path / f".claude_bck_202401{i:02d}"
                backup.mkdir()
                (backup / "file.txt").write_text("test")

                import time, os
                old_time = time.time() - (40 * 24 * 60 * 60)
                os.utime(backup / "file.txt", (old_time, old_time))

            # ACT
            from nWave.infrastructure.backup_manager import BackupManager

            manager = BackupManager(tmp_path)
            deleted_count = manager.cleanup_old_backups(retention_days=30)

            # ASSERT
            assert deleted_count == 3, f"Expected 3 backups deleted, got {deleted_count}"
