"""
FileSystemPort - Abstract interface for file system operations.

HEXAGONAL ARCHITECTURE:
This is a PORT (abstract interface at hexagon boundary).
- Defines contract for read/write operations on ~/.claude/ directory
- Adapters implement this interface for actual file system access
- Domain/Application layers depend on this abstraction, not concrete implementations

Methods:
- read_version(): Read VERSION file content
- read_watermark(): Read update check watermark state
- write_watermark(): Persist update check watermark
- create_backup(): Create backup directory copy
- list_backups(): List existing backup directories
- delete_backup(): Remove backup directory
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from nWave.core.versioning.domain.version import Version
    from nWave.core.versioning.domain.watermark import Watermark


class FileSystemPort(ABC):
    """
    Abstract port interface for file system operations.

    This port defines the contract for all file system interactions
    required by the versioning domain. Adapters implement this interface
    to provide actual file system access.

    HEXAGONAL ARCHITECTURE:
    - This is a PORT (hexagon boundary interface)
    - Mocking allowed ONLY at this boundary
    - Domain objects (Version, Watermark) passed through, never mocked
    """

    @abstractmethod
    def read_version(self) -> "Version":
        """
        Read the VERSION file from ~/.claude/VERSION.

        Returns:
            Version: Parsed version from VERSION file

        Raises:
            FileNotFoundError: If VERSION file does not exist
            PermissionError: If read access is denied
            ValueError: If VERSION content is not valid semver
        """
        ...

    @abstractmethod
    def read_watermark(self) -> Optional["Watermark"]:
        """
        Read the watermark file tracking last update check.

        The watermark stores when the last update check was performed
        and what version was found. Returns None if no watermark exists.

        Returns:
            Optional[Watermark]: Watermark state, or None if not found

        Raises:
            FileNotFoundError: If watermark file does not exist (returns None instead)
            PermissionError: If read access is denied
            ValueError: If watermark content is corrupted
        """
        ...

    @abstractmethod
    def write_watermark(self, watermark: "Watermark") -> None:
        """
        Write the watermark file with current update check state.

        Args:
            watermark: Watermark state to persist

        Raises:
            PermissionError: If write access is denied
            IOError: If write operation fails
        """
        ...

    @abstractmethod
    def create_backup(self, backup_path: Path) -> None:
        """
        Create a backup of ~/.claude/ directory at specified path.

        Copies the entire ~/.claude/ directory to the backup path.
        The backup preserves directory structure and file contents.

        Args:
            backup_path: Destination path for backup (e.g., ~/.claude.backup.20260128143045)

        Raises:
            PermissionError: If read/write access is denied
            FileExistsError: If backup path already exists
            IOError: If copy operation fails
        """
        ...

    @abstractmethod
    def list_backups(self) -> list[Path]:
        """
        List all existing backup directories.

        Finds all directories matching ~/.claude.backup.* pattern.

        Returns:
            list[Path]: List of backup directory paths, may be empty

        Raises:
            PermissionError: If directory listing is denied
        """
        ...

    @abstractmethod
    def delete_backup(self, backup_path: Path) -> bool:
        """
        Delete a backup directory.

        Removes the specified backup directory and all its contents.

        Args:
            backup_path: Path to backup directory to delete

        Returns:
            bool: True if deletion successful, False if backup not found

        Raises:
            PermissionError: If delete access is denied
            IOError: If deletion fails
        """
        ...
