"""
Unit tests for FileSystemPort interface contract.

HEXAGONAL ARCHITECTURE:
- FileSystemPort is a PORT (abstract interface at hexagon boundary)
- Defines contract for file system operations (read/write ~/.claude/)
- Adapters implement this port for actual file system access

These tests verify the PORT CONTRACT:
- Abstract class cannot be instantiated
- All required methods are defined
- Error handling contracts are clear
"""

from abc import ABC

import pytest


class TestFileSystemPortIsAbstract:
    """Tests that FileSystemPort is properly defined as an abstract class."""

    def test_file_system_port_is_abstract(self):
        """
        GIVEN: The FileSystemPort class
        WHEN: Checking if it's abstract
        THEN: It should be an ABC that cannot be instantiated
        """
        # ARRANGE
        from nWave.core.versioning.ports.file_system_port import FileSystemPort

        # ACT & ASSERT
        assert issubclass(FileSystemPort, ABC)
        with pytest.raises(TypeError, match="Can't instantiate abstract class"):
            FileSystemPort()


class TestFileSystemPortVersionMethods:
    """Tests for version file operations."""

    def test_read_version_method_defined(self):
        """
        GIVEN: The FileSystemPort class
        WHEN: Checking for read_version method
        THEN: It should be an abstract method returning Version
        """
        # ARRANGE
        from nWave.core.versioning.ports.file_system_port import FileSystemPort

        # ACT
        method = getattr(FileSystemPort, "read_version", None)

        # ASSERT
        assert method is not None, "read_version method must be defined"
        assert hasattr(method, "__isabstractmethod__")
        assert method.__isabstractmethod__ is True


class TestFileSystemPortWatermarkMethods:
    """Tests for watermark file operations."""

    def test_read_watermark_method_defined(self):
        """
        GIVEN: The FileSystemPort class
        WHEN: Checking for read_watermark method
        THEN: It should be an abstract method returning Watermark or None
        """
        # ARRANGE
        from nWave.core.versioning.ports.file_system_port import FileSystemPort

        # ACT
        method = getattr(FileSystemPort, "read_watermark", None)

        # ASSERT
        assert method is not None, "read_watermark method must be defined"
        assert hasattr(method, "__isabstractmethod__")
        assert method.__isabstractmethod__ is True

    def test_write_watermark_method_defined(self):
        """
        GIVEN: The FileSystemPort class
        WHEN: Checking for write_watermark method
        THEN: It should be an abstract method accepting Watermark
        """
        # ARRANGE
        from nWave.core.versioning.ports.file_system_port import FileSystemPort

        # ACT
        method = getattr(FileSystemPort, "write_watermark", None)

        # ASSERT
        assert method is not None, "write_watermark method must be defined"
        assert hasattr(method, "__isabstractmethod__")
        assert method.__isabstractmethod__ is True


class TestFileSystemPortBackupMethods:
    """Tests for backup directory operations."""

    def test_create_backup_method_defined(self):
        """
        GIVEN: The FileSystemPort class
        WHEN: Checking for create_backup method
        THEN: It should be an abstract method accepting backup_path
        """
        # ARRANGE
        from nWave.core.versioning.ports.file_system_port import FileSystemPort

        # ACT
        method = getattr(FileSystemPort, "create_backup", None)

        # ASSERT
        assert method is not None, "create_backup method must be defined"
        assert hasattr(method, "__isabstractmethod__")
        assert method.__isabstractmethod__ is True

    def test_list_backups_method_defined(self):
        """
        GIVEN: The FileSystemPort class
        WHEN: Checking for list_backups method
        THEN: It should be an abstract method returning list of paths
        """
        # ARRANGE
        from nWave.core.versioning.ports.file_system_port import FileSystemPort

        # ACT
        method = getattr(FileSystemPort, "list_backups", None)

        # ASSERT
        assert method is not None, "list_backups method must be defined"
        assert hasattr(method, "__isabstractmethod__")
        assert method.__isabstractmethod__ is True

    def test_delete_backup_method_defined(self):
        """
        GIVEN: The FileSystemPort class
        WHEN: Checking for delete_backup method
        THEN: It should be an abstract method accepting backup_path
        """
        # ARRANGE
        from nWave.core.versioning.ports.file_system_port import FileSystemPort

        # ACT
        method = getattr(FileSystemPort, "delete_backup", None)

        # ASSERT
        assert method is not None, "delete_backup method must be defined"
        assert hasattr(method, "__isabstractmethod__")
        assert method.__isabstractmethod__ is True


class TestFileSystemPortErrorHandling:
    """Tests for error handling contracts."""

    def test_file_not_found_error_handling(self):
        """
        GIVEN: The FileSystemPort interface contract
        WHEN: A file is not found
        THEN: Methods should raise FileNotFoundError (documented in docstrings)
        """
        # ARRANGE
        from nWave.core.versioning.ports.file_system_port import FileSystemPort

        # ACT - Check method docstrings document FileNotFoundError
        read_version_doc = FileSystemPort.read_version.__doc__ or ""

        # ASSERT
        assert (
            "FileNotFoundError" in read_version_doc
        ), "read_version must document FileNotFoundError in docstring"

    def test_permission_error_handling(self):
        """
        GIVEN: The FileSystemPort interface contract
        WHEN: Permission is denied for file operations
        THEN: Methods should raise PermissionError (documented in docstrings)
        """
        # ARRANGE
        from nWave.core.versioning.ports.file_system_port import FileSystemPort

        # ACT - Check method docstrings document PermissionError
        create_backup_doc = FileSystemPort.create_backup.__doc__ or ""
        write_watermark_doc = FileSystemPort.write_watermark.__doc__ or ""

        # ASSERT
        assert (
            "PermissionError" in create_backup_doc
        ), "create_backup must document PermissionError in docstring"
        assert (
            "PermissionError" in write_watermark_doc
        ), "write_watermark must document PermissionError in docstring"
