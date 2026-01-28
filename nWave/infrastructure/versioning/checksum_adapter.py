"""
ChecksumAdapter - Concrete implementation of ChecksumPort.

Implements SHA256 checksum calculation and verification for downloaded files.

HEXAGONAL ARCHITECTURE:
- This is a DRIVEN ADAPTER (outside the hexagon)
- Implements ChecksumPort interface
- Uses hashlib for cryptographic operations
"""

from __future__ import annotations

import hashlib
from pathlib import Path

from nWave.core.versioning.ports.checksum_port import ChecksumPort


class ChecksumAdapter(ChecksumPort):
    """
    Concrete adapter for SHA256 checksum operations.

    Calculates and verifies SHA256 checksums for files, typically used
    to validate downloaded release assets before installation.

    Example:
        >>> adapter = ChecksumAdapter()
        >>> checksum = adapter.calculate_sha256(Path("/path/to/file"))
        >>> is_valid = adapter.verify(Path("/path/to/file"), "expected_checksum")
    """

    # Buffer size for reading files in chunks (64KB)
    BUFFER_SIZE = 65536

    def calculate_sha256(self, file_path: Path) -> str:
        """
        Calculate the SHA256 checksum of a file.

        Reads the file in chunks to handle large files efficiently.

        Args:
            file_path: Path to the file to checksum

        Returns:
            str: SHA256 hexadecimal digest (64 characters)

        Raises:
            FileNotFoundError: If the file does not exist
            PermissionError: If read access is denied
            IOError: If the file cannot be read
        """
        sha256_hash = hashlib.sha256()

        with open(file_path, "rb") as f:
            while True:
                data = f.read(self.BUFFER_SIZE)
                if not data:
                    break
                sha256_hash.update(data)

        return sha256_hash.hexdigest()

    def verify(self, file_path: Path, expected_checksum: str) -> bool:
        """
        Verify that a file's checksum matches the expected value.

        Calculates the SHA256 checksum of the file and compares it
        with the expected checksum value (case-insensitive comparison).

        Args:
            file_path: Path to the file to verify
            expected_checksum: Expected SHA256 hex digest

        Returns:
            bool: True if checksums match, False otherwise

        Raises:
            FileNotFoundError: If the file does not exist
            PermissionError: If read access is denied
            IOError: If the file cannot be read
        """
        actual_checksum = self.calculate_sha256(file_path)
        return actual_checksum.lower() == expected_checksum.lower()
