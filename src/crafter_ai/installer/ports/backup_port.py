"""BackupPort Protocol - abstract interface for backup operations.

This is a hexagonal architecture port that defines how the application
performs backup and restore operations for nWave configuration files.
Adapters implement this protocol for different storage mechanisms.
"""

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Protocol, runtime_checkable


@dataclass
class BackupResult:
    """Result of a backup operation.

    Attributes:
        success: True if backup succeeded, False otherwise.
        backup_path: Path where backup was created, or None if failed.
        timestamp: When the backup was created, or None if failed.
        error_message: Error description if backup failed, None otherwise.
    """

    success: bool
    backup_path: Path | None
    timestamp: datetime | None
    error_message: str | None


@dataclass
class RestoreResult:
    """Result of a restore operation.

    Attributes:
        success: True if restore succeeded, False otherwise.
        restored_path: Path where backup was restored to, or None if failed.
        error_message: Error description if restore failed, None otherwise.
    """

    success: bool
    restored_path: Path | None
    error_message: str | None


@dataclass
class BackupInfo:
    """Information about an existing backup.

    Attributes:
        path: Path to the backup directory.
        timestamp: When the backup was created.
        size_bytes: Total size of the backup in bytes.
    """

    path: Path
    timestamp: datetime
    size_bytes: int


@dataclass
class CleanupResult:
    """Result of a cleanup operation.

    Attributes:
        success: True if cleanup succeeded, False otherwise.
        removed_count: Number of backups removed.
        kept_count: Number of backups kept.
        error_message: Error description if cleanup failed, None otherwise.
    """

    success: bool
    removed_count: int
    kept_count: int
    error_message: str | None


@runtime_checkable
class BackupPort(Protocol):
    """Protocol defining backup operations interface.

    This is a hexagonal port - the application depends on this interface,
    not on concrete implementations. Adapters (like FileSystemBackupAdapter)
    implement this protocol.

    Used by:
        - InstallService for creating backups before upgrades
        - RollbackService for restoring from backups
    """

    def create_backup(self, source_path: Path) -> BackupResult:
        """Create a backup of the source directory.

        Creates a timestamped backup of the source path contents.
        Backup path format: ~/.claude/backups/nwave-YYYYMMDD-HHMMSS/

        Args:
            source_path: Path to the directory to backup.

        Returns:
            BackupResult with success status, backup_path, timestamp, or error.
        """
        ...

    def restore_backup(self, backup_path: Path, target_path: Path) -> RestoreResult:
        """Restore a backup to the target directory.

        Copies the backup contents to the target path.

        Args:
            backup_path: Path to the backup directory to restore from.
            target_path: Path where backup should be restored to.

        Returns:
            RestoreResult with success status, restored_path, or error.
        """
        ...

    def list_backups(self) -> list[BackupInfo]:
        """List all available backups.

        Returns:
            List of BackupInfo objects sorted by timestamp (newest first).
            Empty list if no backups exist or on error.
        """
        ...

    def cleanup_old_backups(self, keep_count: int = 5) -> CleanupResult:
        """Remove old backups, keeping the most recent ones.

        Args:
            keep_count: Number of most recent backups to keep (default: 5).

        Returns:
            CleanupResult with success status, counts, or error.
        """
        ...
