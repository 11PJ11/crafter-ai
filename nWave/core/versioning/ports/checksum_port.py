"""
ChecksumPort - Port interface for SHA256 validation operations.

This port defines the contract for checksum calculation and verification.
Adapters implementing this port handle the actual cryptographic operations
to ensure downloaded files are not corrupted or tampered with.

HEXAGONAL ARCHITECTURE:
This is a PORT (abstract interface at hexagon boundary).
- Defines contract for checksum operations on files
- Adapters implement this interface using hashlib or similar
- Domain/Application layers depend on this abstraction

Example:
    class SHA256Adapter(ChecksumPort):
        def calculate_sha256(self, file_path: Path) -> str:
            # Implementation with hashlib
            ...

        def verify(self, file_path: Path, expected_checksum: str) -> bool:
            actual = self.calculate_sha256(file_path)
            return actual == expected_checksum
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional


class ChecksumMismatchError(Exception):
    """
    Raised when a file's checksum does not match the expected value.

    This exception indicates that a downloaded file may be corrupted
    or has been tampered with. The update process should be aborted
    when this error is raised.

    Attributes:
        expected_checksum: The checksum value that was expected
        actual_checksum: The checksum value that was calculated

    Example:
        >>> raise ChecksumMismatchError(
        ...     "Checksum verification failed",
        ...     expected_checksum="abc123...",
        ...     actual_checksum="def456..."
        ... )
        ChecksumMismatchError: Checksum verification failed
    """

    def __init__(
        self,
        message: str,
        expected_checksum: Optional[str] = None,
        actual_checksum: Optional[str] = None,
    ) -> None:
        """
        Create a ChecksumMismatchError.

        Args:
            message: Error description
            expected_checksum: The expected SHA256 checksum value
            actual_checksum: The actual SHA256 checksum calculated from the file
        """
        super().__init__(message)
        self.expected_checksum = expected_checksum
        self.actual_checksum = actual_checksum


class ChecksumPort(ABC):
    """
    Port interface for checksum validation operations.

    This abstract class defines the contract for calculating and verifying
    SHA256 checksums on files. Implementations handle the actual
    cryptographic operations using appropriate libraries.

    HEXAGONAL ARCHITECTURE:
    - This is a PORT (hexagon boundary interface)
    - Mocking allowed ONLY at this boundary
    - Used to validate file integrity after downloads

    Implementers must handle:
        - SHA256 checksum calculation
        - Checksum comparison and verification
        - Efficient file reading for large files

    Example:
        >>> class MockChecksumAdapter(ChecksumPort):
        ...     def calculate_sha256(self, file_path: Path) -> str:
        ...         return "abc123def456..."
        ...
        ...     def verify(self, file_path: Path, expected: str) -> bool:
        ...         return self.calculate_sha256(file_path) == expected
    """

    @abstractmethod
    def calculate_sha256(self, file_path: Path) -> str:
        """
        Calculate the SHA256 checksum of a file.

        Reads the file and computes its SHA256 hash, returning
        the hexadecimal digest string.

        Args:
            file_path: Path to the file to checksum

        Returns:
            str: SHA256 hexadecimal digest (64 characters)

        Raises:
            FileNotFoundError: If the file does not exist
            PermissionError: If read access is denied
            IOError: If the file cannot be read
        """
        ...

    @abstractmethod
    def verify(self, file_path: Path, expected_checksum: str) -> bool:
        """
        Verify that a file's checksum matches the expected value.

        Calculates the SHA256 checksum of the file and compares it
        with the expected checksum value.

        Args:
            file_path: Path to the file to verify
            expected_checksum: Expected SHA256 hex digest

        Returns:
            bool: True if checksums match, False otherwise

        Raises:
            FileNotFoundError: If the file does not exist
            PermissionError: If read access is denied
            IOError: If the file cannot be read

        Note:
            For strict validation where mismatch should be an error,
            callers should check the return value and raise
            ChecksumMismatchError if False.
        """
        ...
