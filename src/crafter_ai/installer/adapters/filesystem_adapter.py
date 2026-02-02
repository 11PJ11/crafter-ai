"""RealFileSystemAdapter - file-based implementation of FileSystemPort.

This adapter implements the FileSystemPort protocol using the real file system
via pathlib.Path operations. Used in production for actual file operations.
"""

import shutil
from pathlib import Path


class RealFileSystemAdapter:
    """Real file system adapter implementing FileSystemPort.

    This adapter performs actual file system operations using pathlib.Path.
    It is used in production environments.
    """

    def exists(self, path: Path) -> bool:
        """Check if a path exists.

        Args:
            path: The path to check.

        Returns:
            True if the path exists, False otherwise.
        """
        return path.exists()

    def read_text(self, path: Path) -> str:
        """Read file contents as text.

        Args:
            path: The path to the file.

        Returns:
            The file contents as a string.

        Raises:
            FileNotFoundError: If the file does not exist.
        """
        return path.read_text()

    def write_text(self, path: Path, content: str) -> None:
        """Write text content to a file.

        Args:
            path: The path to the file.
            content: The content to write.
        """
        # Ensure parent directory exists
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)

    def mkdir(self, path: Path, parents: bool = False) -> None:
        """Create a directory.

        Args:
            path: The path to the directory.
            parents: If True, create parent directories as needed.
        """
        path.mkdir(parents=parents, exist_ok=True)

    def list_dir(self, path: Path) -> list[Path]:
        """List contents of a directory.

        Args:
            path: The path to the directory.

        Returns:
            List of paths in the directory.

        Raises:
            FileNotFoundError: If the directory does not exist.
        """
        if not path.exists():
            raise FileNotFoundError(f"Directory not found: {path}")
        return list(path.iterdir())

    def copy_file(self, src: Path, dst: Path) -> None:
        """Copy a file from source to destination.

        Args:
            src: The source file path.
            dst: The destination file path.

        Raises:
            FileNotFoundError: If the source file does not exist.
        """
        if not src.exists():
            raise FileNotFoundError(f"Source file not found: {src}")
        # Ensure parent directory exists
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)

    def remove(self, path: Path) -> None:
        """Remove a file or empty directory.

        Args:
            path: The path to remove.

        Raises:
            FileNotFoundError: If the path does not exist.
        """
        if not path.exists():
            raise FileNotFoundError(f"Path not found: {path}")
        if path.is_dir():
            path.rmdir()
        else:
            path.unlink()
