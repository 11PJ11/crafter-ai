"""
BackupPolicy - Domain service for backup retention management.

HEXAGONAL ARCHITECTURE:
This is a DOMAIN SERVICE (pure business logic).
- Determines which backups to delete based on rolling retention rules
- Generates backup directory paths with timestamps
- NO infrastructure dependencies (pure Python)
"""

from datetime import datetime
from pathlib import Path


class BackupPolicy:
    """
    Domain service for backup retention policy.

    Enforces rolling retention rules (maximum N backups) and
    generates backup directory paths with timestamps.

    Attributes:
        max_backups: Maximum number of backups to retain (default: 3)
    """

    BACKUP_PATH_PREFIX = "~/.claude.backup."
    TIMESTAMP_FORMAT = "%Y%m%d%H%M%S"

    def __init__(self, max_backups: int = 3):
        """
        Initialize BackupPolicy with retention limit.

        Args:
            max_backups: Maximum number of backups to keep (default: 3)
        """
        self.max_backups = max_backups

    def get_backups_to_delete(self, existing_backups: list[Path]) -> list[Path]:
        """
        Determine which backups should be deleted based on retention policy.

        Returns the oldest backups that exceed the maximum retention limit.
        With max_backups=3, if there are 3 existing backups and a new one
        will be created, the oldest backup should be deleted.

        Args:
            existing_backups: List of existing backup paths

        Returns:
            List of backup paths that should be deleted (oldest first)
        """
        if len(existing_backups) < self.max_backups:
            return []

        sorted_backups = self._sort_by_timestamp(existing_backups)
        excess_count = len(existing_backups) - self.max_backups + 1
        return sorted_backups[:excess_count]

    def generate_backup_path(self, timestamp: datetime | None = None) -> Path:
        """
        Generate a backup directory path with timestamp.

        Args:
            timestamp: Optional datetime for path generation.
                      Uses current time if not provided.

        Returns:
            Path in format ~/.claude.backup.{YYYYMMDDHHMMSS}
        """
        if timestamp is None:
            timestamp = datetime.now()

        timestamp_str = timestamp.strftime(self.TIMESTAMP_FORMAT)
        return Path(f"{self.BACKUP_PATH_PREFIX}{timestamp_str}")

    def _sort_by_timestamp(self, backups: list[Path]) -> list[Path]:
        """
        Sort backup paths by their embedded timestamp (oldest first).

        Args:
            backups: List of backup paths

        Returns:
            Sorted list with oldest backups first
        """
        return sorted(backups, key=self._extract_timestamp)

    def _extract_timestamp(self, backup_path: Path) -> str:
        """
        Extract timestamp string from backup path.

        Args:
            backup_path: Path like ~/.claude.backup.20260128143045

        Returns:
            Timestamp string for sorting (e.g., "20260128143045")
        """
        path_str = str(backup_path)
        return path_str.split(".")[-1]
