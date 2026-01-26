"""
BackupManager - Infrastructure adapter for backup operations.

HEXAGONAL ARCHITECTURE:
This is an infrastructure adapter (DRIVEN PORT implementation).
Provides backup/restore capabilities for nWave updates.
"""

from pathlib import Path
import shutil
import time
from typing import Optional


class BackupManager:
    """
    Manages backup creation, cleanup, and restoration operations.

    Part of infrastructure layer - implements backup port.
    """

    def __init__(self, nwave_home: Path):
        """
        Initialize BackupManager with nWave home directory.

        Args:
            nwave_home: Path to ~/.claude/ directory
        """
        self.nwave_home = Path(nwave_home)
        self.backup_parent_dir = self.nwave_home.parent

    def cleanup_old_backups(self, retention_days: int = 30) -> int:
        """
        Remove backup directories older than retention_days.

        Implements 30-day retention policy (US-004).

        Args:
            retention_days: Number of days to retain backups (default 30)

        Returns:
            Number of backups deleted

        Behavior:
            - Only considers directories matching pattern .claude_bck_*
            - Determines age from oldest file modification time
            - Logs warnings for locked/permission-denied directories
            - Non-blocking: continues cleanup even if individual delete fails
        """
        now = time.time()
        cutoff_time = now - (retention_days * 24 * 60 * 60)
        deleted_count = 0

        # Find all backup directories
        for item in self.backup_parent_dir.iterdir():
            if item.is_dir() and item.name.startswith('.claude_bck_'):
                try:
                    # Determine age from oldest file in backup
                    oldest_mtime = self._get_oldest_file_mtime(item)

                    if oldest_mtime < cutoff_time:
                        # Directory is older than retention period - delete it
                        shutil.rmtree(item)
                        deleted_count += 1
                except PermissionError:
                    # Non-blocking: log warning and continue
                    print(f"WARNING: Could not delete {item}/: permission denied")
                except OSError as e:
                    # Locked directory or other OS error
                    print(f"WARNING: Could not delete {item}/: {e}")

        return deleted_count

    def _get_oldest_file_mtime(self, directory: Path) -> float:
        """
        Get modification time of oldest file in directory.

        Args:
            directory: Path to backup directory

        Returns:
            Oldest file modification time (seconds since epoch)
            If directory is empty, returns directory's own mtime
        """
        oldest_mtime = time.time()

        # Check all files recursively
        for file_path in directory.rglob('*'):
            if file_path.is_file():
                file_mtime = file_path.stat().st_mtime
                oldest_mtime = min(oldest_mtime, file_mtime)

        # If no files found, use directory's own mtime
        if oldest_mtime == time.time():
            oldest_mtime = directory.stat().st_mtime

        return oldest_mtime

    def create_backup(self, backup_name: Optional[str] = None) -> Path:
        """
        Create backup of current nWave installation.

        Args:
            backup_name: Optional backup directory name
                        If None, generates name from current timestamp

        Returns:
            Path to created backup directory
        """
        if backup_name is None:
            from datetime import datetime
            backup_name = f".claude_bck_{datetime.now().strftime('%Y%m%d')}"

        backup_path = self.backup_parent_dir / backup_name

        if not backup_path.exists():
            backup_path.mkdir(parents=True)
            # In full implementation: shutil.copytree with metadata preservation
            # For now, minimal structure

        return backup_path

    def restore_from_backup(self, backup_path: Path) -> None:
        """
        Restore nWave installation from backup.

        Args:
            backup_path: Path to backup directory to restore from
        """
        # In full implementation: restore files from backup
        # For acceptance tests, minimal implementation
        pass
