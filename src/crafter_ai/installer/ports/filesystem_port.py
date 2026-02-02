"""FileSystemPort Protocol - abstract interface for file system operations.

This is a hexagonal architecture port that defines how the application
accesses the file system. Adapters implement this protocol for different
storage mechanisms (real file system, in-memory for testing, etc.).
"""

from pathlib import Path
from typing import Protocol, runtime_checkable


@runtime_checkable
class FileSystemPort(Protocol):
    """Protocol defining file system access interface.

    This is a hexagonal port - the application depends on this interface,
    not on concrete implementations. Adapters (like RealFileSystemAdapter)
    implement this protocol.
    """

    def exists(self, path: Path) -> bool:
        """Check if a path exists.

        Args:
            path: The path to check.

        Returns:
            True if the path exists, False otherwise.
        """
        ...

    def read_text(self, path: Path) -> str:
        """Read file contents as text.

        Args:
            path: The path to the file.

        Returns:
            The file contents as a string.

        Raises:
            FileNotFoundError: If the file does not exist.
        """
        ...

    def write_text(self, path: Path, content: str) -> None:
        """Write text content to a file.

        Args:
            path: The path to the file.
            content: The content to write.
        """
        ...

    def mkdir(self, path: Path, parents: bool = False) -> None:
        """Create a directory.

        Args:
            path: The path to the directory.
            parents: If True, create parent directories as needed.
        """
        ...

    def list_dir(self, path: Path) -> list[Path]:
        """List contents of a directory.

        Args:
            path: The path to the directory.

        Returns:
            List of paths in the directory.

        Raises:
            FileNotFoundError: If the directory does not exist.
        """
        ...

    def copy_file(self, src: Path, dst: Path) -> None:
        """Copy a file from source to destination.

        Args:
            src: The source file path.
            dst: The destination file path.

        Raises:
            FileNotFoundError: If the source file does not exist.
        """
        ...

    def remove(self, path: Path) -> None:
        """Remove a file or empty directory.

        Args:
            path: The path to remove.

        Raises:
            FileNotFoundError: If the path does not exist.
        """
        ...
