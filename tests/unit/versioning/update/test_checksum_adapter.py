"""
Unit tests for ChecksumAdapter (driven adapter).

HEXAGONAL ARCHITECTURE:
- ChecksumAdapter is a DRIVEN ADAPTER (outside the hexagon)
- Implements ChecksumPort interface
- Tests verify adapter correctly calculates and validates SHA256 checksums
"""

from pathlib import Path
import tempfile



class TestChecksumAdapterValidatesSHA256:
    """Test that ChecksumAdapter correctly validates SHA256 checksums."""

    def test_checksum_adapter_validates_sha256(self):
        """
        GIVEN: ChecksumAdapter and a file with known content
        WHEN: verify() is called with correct checksum
        THEN: Returns True
        """
        # Import here to trigger failure if module doesn't exist
        from nWave.infrastructure.versioning.checksum_adapter import ChecksumAdapter

        with tempfile.TemporaryDirectory() as tmp_dir:
            # Arrange
            test_file = Path(tmp_dir) / "test_file.txt"
            test_content = b"test content for checksum"
            test_file.write_bytes(test_content)

            # Calculate expected SHA256 for this content
            import hashlib
            expected_checksum = hashlib.sha256(test_content).hexdigest()

            adapter = ChecksumAdapter()

            # Act
            result = adapter.verify(test_file, expected_checksum)

            # Assert
            assert result is True, "Checksum should match"

    def test_checksum_adapter_rejects_wrong_checksum(self):
        """
        GIVEN: ChecksumAdapter and a file
        WHEN: verify() is called with wrong checksum
        THEN: Returns False
        """
        from nWave.infrastructure.versioning.checksum_adapter import ChecksumAdapter

        with tempfile.TemporaryDirectory() as tmp_dir:
            # Arrange
            test_file = Path(tmp_dir) / "test_file.txt"
            test_file.write_bytes(b"test content")
            adapter = ChecksumAdapter()

            # Act
            result = adapter.verify(test_file, "wrong_checksum_value")

            # Assert
            assert result is False, "Checksum should not match"

    def test_checksum_adapter_calculates_sha256(self):
        """
        GIVEN: ChecksumAdapter and a file
        WHEN: calculate_sha256() is called
        THEN: Returns correct SHA256 hex digest
        """
        from nWave.infrastructure.versioning.checksum_adapter import ChecksumAdapter

        with tempfile.TemporaryDirectory() as tmp_dir:
            # Arrange
            test_file = Path(tmp_dir) / "test_file.txt"
            test_content = b"known content"
            test_file.write_bytes(test_content)

            import hashlib
            expected = hashlib.sha256(test_content).hexdigest()

            adapter = ChecksumAdapter()

            # Act
            actual = adapter.calculate_sha256(test_file)

            # Assert
            assert actual == expected, f"Expected {expected}, got {actual}"
