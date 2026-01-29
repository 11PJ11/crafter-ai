"""
FileSystemAdapter - Concrete implementation of FileSystemPort.

Implements file system operations for the versioning feature:
- Reading VERSION file
- Reading/writing watermark file
- Backup operations

HEXAGONAL ARCHITECTURE:
- This is a DRIVEN ADAPTER (outside the hexagon)
- Implements FileSystemPort interface
- Handles actual file system I/O
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional
import os
import shutil

from nWave.core.versioning.domain.version import Version
from nWave.core.versioning.domain.watermark import Watermark
from nWave.core.versioning.ports.file_system_port import FileSystemPort


class FileSystemAdapter(FileSystemPort):
    """
    Concrete file system adapter for versioning operations.

    Reads/writes files in the ~/.claude/ directory structure:
    - VERSION: Contains the installed version string
    - nwave.update: Contains the watermark JSON

    Example:
        >>> adapter = FileSystemAdapter(nwave_home=Path.home() / ".claude")
        >>> version = adapter.read_version()
        >>> print(f"Installed: {version}")
    """

    VERSION_FILENAME = "VERSION"
    WATERMARK_FILENAME = "nwave.update"

    def __init__(self, nwave_home: Path = None) -> None:
        """
        Create a FileSystemAdapter.

        Args:
            nwave_home: Path to ~/.claude/ directory.
                        Defaults to $NWAVE_HOME or ~/.claude/
        """
        if nwave_home is None:
            env_home = os.getenv("NWAVE_HOME")
            if env_home:
                nwave_home = Path(env_home)
            else:
                nwave_home = Path.home() / ".claude"

        self._nwave_home = nwave_home

    @property
    def version_file(self) -> Path:
        """Path to the VERSION file."""
        return self._nwave_home / self.VERSION_FILENAME

    @property
    def watermark_file(self) -> Path:
        """Path to the watermark file."""
        return self._nwave_home / self.WATERMARK_FILENAME

    def read_version(self) -> Version:
        """
        Read the VERSION file from ~/.claude/VERSION.

        Returns:
            Version: Parsed version from VERSION file

        Raises:
            FileNotFoundError: If VERSION file does not exist
            ValueError: If VERSION content is not valid semver
        """
        if not self.version_file.exists():
            raise FileNotFoundError(f"VERSION file not found at {self.version_file}")

        content = self.version_file.read_text().strip()
        return Version(content)

    def read_watermark(self) -> Optional[Watermark]:
        """
        Read the watermark file tracking last update check.

        Returns:
            Optional[Watermark]: Watermark state, or None if not found
        """
        if not self.watermark_file.exists():
            return None

        content = self.watermark_file.read_text()
        return Watermark.from_json(content)

    def write_watermark(self, watermark: Watermark) -> None:
        """
        Write the watermark file with current update check state.

        Args:
            watermark: Watermark state to persist

        Raises:
            PermissionError: If write access is denied
            IOError: If write operation fails
        """
        self._nwave_home.mkdir(parents=True, exist_ok=True)
        self.watermark_file.write_text(watermark.to_json())

    def create_backup(self, backup_path: Path) -> None:
        """
        Create a backup of ~/.claude/ directory at specified path.

        Args:
            backup_path: Destination path for backup

        Raises:
            PermissionError: If read/write access is denied
            FileExistsError: If backup path already exists
        """
        if backup_path.exists():
            raise FileExistsError(f"Backup path already exists: {backup_path}")

        shutil.copytree(self._nwave_home, backup_path)

    def list_backups(self) -> list[Path]:
        """
        List all existing backup directories.

        Returns:
            list[Path]: List of backup directory paths
        """
        parent = self._nwave_home.parent
        return sorted(parent.glob(".claude.backup.*"))

    def delete_backup(self, backup_path: Path) -> bool:
        """
        Delete a backup directory.

        Args:
            backup_path: Path to backup directory to delete

        Returns:
            bool: True if deletion successful, False if backup not found
        """
        if not backup_path.exists():
            return False

        shutil.rmtree(backup_path)
        return True
