"""
File Manager

Handles all file I/O operations, path management, and directory creation
for the nWave IDE bundle generation system.
"""

import logging
import os
from pathlib import Path
from typing import Optional, List
import shutil


class FileManager:
    """Manages file operations with dry-run support and error handling."""

    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run

    def read_file(self, file_path: Path) -> Optional[str]:
        """
        Read content from a file.

        Args:
            file_path: Path to file to read

        Returns:
            str: File content or None if reading fails
        """
        try:
            file_path = Path(file_path)

            if not file_path.exists():
                logging.error(f"File does not exist: {file_path}")
                return None

            if not file_path.is_file():
                logging.error(f"Path is not a file: {file_path}")
                return None

            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            logging.debug(f"Read file: {file_path} ({len(content)} chars)")
            return content

        except UnicodeDecodeError as e:
            logging.error(f"Unicode decode error reading {file_path}: {e}")
            return None
        except PermissionError as e:
            logging.error(f"Permission denied reading {file_path}: {e}")
            return None
        except Exception as e:
            logging.error(f"Error reading file {file_path}: {e}")
            return None

    def write_file(self, file_path: Path, content: str) -> bool:
        """
        Write content to a file.

        Args:
            file_path: Path to file to write
            content: Content to write

        Returns:
            bool: True if successful
        """
        try:
            file_path = Path(file_path)

            # Ensure parent directory exists
            if not self.ensure_directory(file_path.parent):
                return False

            if self.dry_run:
                logging.info(f"[DRY RUN] Would write file: {file_path} ({len(content)} chars)")
                return True

            # Write file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)

            logging.debug(f"Wrote file: {file_path} ({len(content)} chars)")
            return True

        except PermissionError as e:
            logging.error(f"Permission denied writing {file_path}: {e}")
            return False
        except Exception as e:
            logging.error(f"Error writing file {file_path}: {e}")
            return False

    def ensure_directory(self, dir_path: Path) -> bool:
        """
        Ensure a directory exists, creating it if necessary.

        Args:
            dir_path: Path to directory

        Returns:
            bool: True if directory exists or was created successfully
        """
        try:
            dir_path = Path(dir_path)

            if dir_path.exists():
                if dir_path.is_dir():
                    return True
                else:
                    logging.error(f"Path exists but is not a directory: {dir_path}")
                    return False

            if self.dry_run:
                logging.info(f"[DRY RUN] Would create directory: {dir_path}")
                return True

            # Create directory
            dir_path.mkdir(parents=True, exist_ok=True)
            logging.debug(f"Created directory: {dir_path}")
            return True

        except PermissionError as e:
            logging.error(f"Permission denied creating directory {dir_path}: {e}")
            return False
        except Exception as e:
            logging.error(f"Error creating directory {dir_path}: {e}")
            return False

    def copy_file(self, source: Path, destination: Path) -> bool:
        """
        Copy a file from source to destination.

        Args:
            source: Source file path
            destination: Destination file path

        Returns:
            bool: True if successful
        """
        try:
            source = Path(source)
            destination = Path(destination)

            if not source.exists():
                logging.error(f"Source file does not exist: {source}")
                return False

            # Ensure destination directory exists
            if not self.ensure_directory(destination.parent):
                return False

            if self.dry_run:
                logging.info(f"[DRY RUN] Would copy file: {source} -> {destination}")
                return True

            # Copy file
            shutil.copy2(source, destination)
            logging.debug(f"Copied file: {source} -> {destination}")
            return True

        except Exception as e:
            logging.error(f"Error copying file {source} to {destination}: {e}")
            return False

    def list_files(self, directory: Path, pattern: str = "*", recursive: bool = False) -> List[Path]:
        """
        List files in a directory matching a pattern.

        Args:
            directory: Directory to search
            pattern: File pattern (glob syntax)
            recursive: Whether to search recursively

        Returns:
            list: List of matching file paths
        """
        try:
            directory = Path(directory)

            if not directory.exists():
                logging.error(f"Directory does not exist: {directory}")
                return []

            if not directory.is_dir():
                logging.error(f"Path is not a directory: {directory}")
                return []

            if recursive:
                files = list(directory.rglob(pattern))
            else:
                files = list(directory.glob(pattern))

            # Filter to only files (not directories)
            files = [f for f in files if f.is_file()]

            logging.debug(f"Found {len(files)} files in {directory} matching '{pattern}'")
            return files

        except Exception as e:
            logging.error(f"Error listing files in {directory}: {e}")
            return []

    def file_exists(self, file_path: Path) -> bool:
        """
        Check if a file exists.

        Args:
            file_path: Path to check

        Returns:
            bool: True if file exists
        """
        try:
            return Path(file_path).is_file()
        except Exception:
            return False

    def directory_exists(self, dir_path: Path) -> bool:
        """
        Check if a directory exists.

        Args:
            dir_path: Path to check

        Returns:
            bool: True if directory exists
        """
        try:
            return Path(dir_path).is_dir()
        except Exception:
            return False

    def remove_file(self, file_path: Path) -> bool:
        """
        Remove a file.

        Args:
            file_path: Path to file to remove

        Returns:
            bool: True if successful
        """
        try:
            file_path = Path(file_path)

            if not file_path.exists():
                logging.warning(f"File does not exist (already removed?): {file_path}")
                return True

            if self.dry_run:
                logging.info(f"[DRY RUN] Would remove file: {file_path}")
                return True

            file_path.unlink()
            logging.debug(f"Removed file: {file_path}")
            return True

        except Exception as e:
            logging.error(f"Error removing file {file_path}: {e}")
            return False

    def remove_directory(self, dir_path: Path, recursive: bool = False) -> bool:
        """
        Remove a directory.

        Args:
            dir_path: Path to directory to remove
            recursive: Whether to remove directory tree

        Returns:
            bool: True if successful
        """
        try:
            dir_path = Path(dir_path)

            if not dir_path.exists():
                logging.warning(f"Directory does not exist (already removed?): {dir_path}")
                return True

            if self.dry_run:
                action = "remove directory tree" if recursive else "remove empty directory"
                logging.info(f"[DRY RUN] Would {action}: {dir_path}")
                return True

            if recursive:
                shutil.rmtree(dir_path)
            else:
                dir_path.rmdir()

            logging.debug(f"Removed directory: {dir_path}")
            return True

        except Exception as e:
            logging.error(f"Error removing directory {dir_path}: {e}")
            return False

    def get_file_size(self, file_path: Path) -> int:
        """
        Get file size in bytes.

        Args:
            file_path: Path to file

        Returns:
            int: File size in bytes, or -1 if error
        """
        try:
            return Path(file_path).stat().st_size
        except Exception as e:
            logging.error(f"Error getting file size for {file_path}: {e}")
            return -1

    def get_relative_path(self, file_path: Path, base_path: Path) -> Path:
        """
        Get relative path from base to file.

        Args:
            file_path: Target file path
            base_path: Base path

        Returns:
            Path: Relative path
        """
        try:
            return Path(file_path).relative_to(base_path)
        except ValueError:
            # If paths are not relative, return absolute path
            return Path(file_path)

    def normalize_path(self, path: str) -> Path:
        """
        Normalize a path string to a Path object.

        Args:
            path: Path string

        Returns:
            Path: Normalized path
        """
        return Path(path).resolve()