"""FileSystemBackupAdapter - filesystem-based implementation of BackupPort.

This adapter implements the BackupPort protocol using filesystem operations
(shutil/pathlib) for backup creation, restoration, and management.
"""

import shutil
from datetime import datetime, timezone
from pathlib import Path

from crafter_ai.installer.ports.backup_port import (
    BackupInfo,
    BackupResult,
    CleanupResult,
    RestoreResult,
)


class FileSystemBackupAdapter:
    """Filesystem-based backup adapter implementing BackupPort.

    This adapter creates timestamped backup directories using shutil.copytree()
    and pathlib for path operations. Backups follow the naming convention:
    nwave-YYYYMMDD-HHMMSS

    Used by:
        - InstallService for creating backups before upgrades
        - RollbackService for restoring from backups

    Attributes:
        backup_root: Root directory where backups are stored.
    """

    def __init__(self, backup_root: Path | None = None) -> None:
        """Initialize the backup adapter.

        Args:
            backup_root: Root directory for backups. Defaults to ~/.claude/backups/
        """
        if backup_root is None:
            backup_root = Path.home() / ".claude" / "backups"
        self._backup_root = backup_root

    def create_backup(self, source_path: Path) -> BackupResult:
        """Create a backup of the source directory.

        Creates a timestamped backup directory and copies all contents
        from the source path using shutil.copytree().

        Args:
            source_path: Path to the directory to backup.

        Returns:
            BackupResult with success status, backup_path, timestamp, or error.
        """
        if not source_path.exists():
            return BackupResult(
                success=False,
                backup_path=None,
                timestamp=None,
                error_message=f"Source path does not exist: {source_path}",
            )

        try:
            # Generate timestamp and backup path
            timestamp = datetime.now(timezone.utc)
            backup_name = f"nwave-{timestamp.strftime('%Y%m%d-%H%M%S')}"
            backup_path = self._backup_root / backup_name

            # Ensure backup root exists
            self._backup_root.mkdir(parents=True, exist_ok=True)

            # Copy source to backup location
            shutil.copytree(source_path, backup_path)

            return BackupResult(
                success=True,
                backup_path=backup_path,
                timestamp=timestamp,
                error_message=None,
            )
        except OSError as e:
            return BackupResult(
                success=False,
                backup_path=None,
                timestamp=None,
                error_message=f"Backup failed: {e}",
            )

    def restore_backup(self, backup_path: Path, target_path: Path) -> RestoreResult:
        """Restore a backup to the target directory.

        Copies the backup contents to the target path using shutil.copytree().

        Args:
            backup_path: Path to the backup directory to restore from.
            target_path: Path where backup should be restored to.

        Returns:
            RestoreResult with success status, restored_path, or error.
        """
        if not backup_path.exists():
            return RestoreResult(
                success=False,
                restored_path=None,
                error_message=f"Backup path does not exist: {backup_path}",
            )

        try:
            # Ensure target parent exists
            target_path.parent.mkdir(parents=True, exist_ok=True)

            # Remove target if it exists to allow fresh restore
            if target_path.exists():
                shutil.rmtree(target_path)

            # Copy backup to target
            shutil.copytree(backup_path, target_path)

            return RestoreResult(
                success=True,
                restored_path=target_path,
                error_message=None,
            )
        except OSError as e:
            return RestoreResult(
                success=False,
                restored_path=None,
                error_message=f"Restore failed: {e}",
            )

    def list_backups(self) -> list[BackupInfo]:
        """List all available backups.

        Scans the backup root directory for backup directories matching
        the naming pattern nwave-YYYYMMDD-HHMMSS and returns them sorted
        by timestamp (newest first).

        Returns:
            List of BackupInfo objects sorted by timestamp (newest first).
            Empty list if no backups exist or backup root doesn't exist.
        """
        if not self._backup_root.exists():
            return []

        backups: list[BackupInfo] = []

        for entry in self._backup_root.iterdir():
            if entry.is_dir() and entry.name.startswith("nwave-"):
                try:
                    # Parse timestamp from name: nwave-YYYYMMDD-HHMMSS
                    timestamp_str = entry.name[6:]  # Remove "nwave-" prefix
                    timestamp = datetime.strptime(
                        timestamp_str, "%Y%m%d-%H%M%S"
                    ).replace(tzinfo=timezone.utc)

                    # Calculate total size
                    size_bytes = self._calculate_dir_size(entry)

                    backups.append(
                        BackupInfo(
                            path=entry,
                            timestamp=timestamp,
                            size_bytes=size_bytes,
                        )
                    )
                except ValueError:
                    # Skip directories that don't match expected format
                    continue

        # Sort by timestamp descending (newest first)
        backups.sort(key=lambda b: b.timestamp, reverse=True)

        return backups

    def cleanup_old_backups(self, keep_count: int = 5) -> CleanupResult:
        """Remove old backups, keeping the most recent ones.

        Lists all backups, sorts by timestamp, and removes the oldest
        ones to keep only the specified number of most recent backups.

        Args:
            keep_count: Number of most recent backups to keep (default: 5).

        Returns:
            CleanupResult with success status, counts, or error.
        """
        try:
            backups = self.list_backups()

            if len(backups) <= keep_count:
                return CleanupResult(
                    success=True,
                    removed_count=0,
                    kept_count=len(backups),
                    error_message=None,
                )

            # Keep newest, remove oldest
            backups_to_keep = backups[:keep_count]
            backups_to_remove = backups[keep_count:]

            removed_count = 0
            for backup in backups_to_remove:
                try:
                    shutil.rmtree(backup.path)
                    removed_count += 1
                except OSError:
                    # Continue with other removals even if one fails
                    pass

            return CleanupResult(
                success=True,
                removed_count=removed_count,
                kept_count=len(backups_to_keep),
                error_message=None,
            )
        except OSError as e:
            return CleanupResult(
                success=False,
                removed_count=0,
                kept_count=0,
                error_message=f"Cleanup failed: {e}",
            )

    def _calculate_dir_size(self, path: Path) -> int:
        """Calculate total size of a directory in bytes.

        Args:
            path: Path to the directory.

        Returns:
            Total size in bytes.
        """
        total = 0
        for entry in path.rglob("*"):
            if entry.is_file():
                total += entry.stat().st_size
        return total
