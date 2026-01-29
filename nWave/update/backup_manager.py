"""
BackupManager - Infrastructure adapter for backup restoration.

HEXAGONAL ARCHITECTURE:
This is an infrastructure adapter (DRIVEN PORT implementation).
Provides backup restoration (rollback) capabilities for nWave updates.
"""

import shutil
from pathlib import Path


class BackupManager:
    """
    Manages backup restoration for nWave automatic rollback.

    Restores files from backup to installation directory when
    update fails mid-process.
    """

    def __init__(self, nwave_home: Path):
        """
        Initialize BackupManager with nWave installation directory.

        Args:
            nwave_home: Path to nWave installation directory
        """
        self.nwave_home = Path(nwave_home)

    def restore_from_backup(self, backup_dir: Path) -> None:
        """
        Restore nWave installation from backup directory.

        Copies all files from backup to installation directory,
        preserving file permissions.

        Args:
            backup_dir: Path to backup directory to restore from

        Raises:
            FileNotFoundError: If backup directory does not exist
        """
        backup_dir = Path(backup_dir)

        if not backup_dir.exists():
            raise FileNotFoundError(f"Backup directory not found: {backup_dir}")

        # Copy files from backup to installation, preserving permissions
        # Using copy2 to preserve metadata (including permissions)
        for item in backup_dir.iterdir():
            dest_path = self.nwave_home / item.name

            if item.is_dir():
                if dest_path.exists():
                    shutil.rmtree(dest_path)
                shutil.copytree(item, dest_path)
            else:
                shutil.copy2(item, dest_path)
