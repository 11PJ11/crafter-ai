"""Tests for FileSystemPort Protocol and RealFileSystemAdapter implementation.

TDD approach: Tests verify Protocol compliance and real file system operations.
"""

from pathlib import Path
from typing import Protocol

import pytest

from crafter_ai.installer.adapters.filesystem_adapter import RealFileSystemAdapter
from crafter_ai.installer.ports.filesystem_port import FileSystemPort


class TestFileSystemPortProtocol:
    """Test that FileSystemPort is a proper Protocol interface."""

    def test_filesystem_port_is_protocol(self) -> None:
        """FileSystemPort should be a typing.Protocol (not ABC)."""
        assert hasattr(FileSystemPort, "__protocol_attrs__") or issubclass(
            type(FileSystemPort), type(Protocol)
        )

    def test_filesystem_port_is_runtime_checkable(self) -> None:
        """FileSystemPort should be runtime_checkable for isinstance checks."""
        adapter = RealFileSystemAdapter()
        assert isinstance(adapter, FileSystemPort)


class TestRealFileSystemAdapterImplementsProtocol:
    """Test that RealFileSystemAdapter properly implements FileSystemPort."""

    def test_adapter_implements_filesystem_port(self) -> None:
        """RealFileSystemAdapter should implement FileSystemPort protocol."""
        adapter = RealFileSystemAdapter()
        # Check all required methods exist
        assert hasattr(adapter, "exists")
        assert hasattr(adapter, "read_text")
        assert hasattr(adapter, "write_text")
        assert hasattr(adapter, "mkdir")
        assert hasattr(adapter, "list_dir")
        assert hasattr(adapter, "copy_file")
        assert hasattr(adapter, "remove")


class TestRealFileSystemAdapterExists:
    """Test exists() method."""

    def test_exists_returns_true_for_existing_file(self, tmp_path: Path) -> None:
        """exists() should return True for existing files."""
        adapter = RealFileSystemAdapter()
        test_file = tmp_path / "test.txt"
        test_file.write_text("content")

        assert adapter.exists(test_file) is True

    def test_exists_returns_true_for_existing_directory(self, tmp_path: Path) -> None:
        """exists() should return True for existing directories."""
        adapter = RealFileSystemAdapter()
        test_dir = tmp_path / "test_dir"
        test_dir.mkdir()

        assert adapter.exists(test_dir) is True

    def test_exists_returns_false_for_nonexistent_path(self, tmp_path: Path) -> None:
        """exists() should return False for nonexistent paths."""
        adapter = RealFileSystemAdapter()
        nonexistent = tmp_path / "nonexistent"

        assert adapter.exists(nonexistent) is False


class TestRealFileSystemAdapterReadWrite:
    """Test read_text() and write_text() methods."""

    def test_write_text_creates_file(self, tmp_path: Path) -> None:
        """write_text() should create a file with content."""
        adapter = RealFileSystemAdapter()
        test_file = tmp_path / "test.txt"

        adapter.write_text(test_file, "test content")

        assert test_file.exists()
        assert test_file.read_text() == "test content"

    def test_read_text_returns_file_content(self, tmp_path: Path) -> None:
        """read_text() should return file contents."""
        adapter = RealFileSystemAdapter()
        test_file = tmp_path / "test.txt"
        test_file.write_text("expected content")

        result = adapter.read_text(test_file)

        assert result == "expected content"

    def test_read_text_raises_for_nonexistent_file(self, tmp_path: Path) -> None:
        """read_text() should raise FileNotFoundError for missing files."""
        adapter = RealFileSystemAdapter()
        nonexistent = tmp_path / "nonexistent.txt"

        with pytest.raises(FileNotFoundError):
            adapter.read_text(nonexistent)

    def test_write_text_overwrites_existing_file(self, tmp_path: Path) -> None:
        """write_text() should overwrite existing file content."""
        adapter = RealFileSystemAdapter()
        test_file = tmp_path / "test.txt"
        test_file.write_text("old content")

        adapter.write_text(test_file, "new content")

        assert test_file.read_text() == "new content"


class TestRealFileSystemAdapterMkdir:
    """Test mkdir() method."""

    def test_mkdir_creates_directory(self, tmp_path: Path) -> None:
        """mkdir() should create a directory."""
        adapter = RealFileSystemAdapter()
        new_dir = tmp_path / "new_dir"

        adapter.mkdir(new_dir)

        assert new_dir.exists()
        assert new_dir.is_dir()

    def test_mkdir_with_parents_creates_nested_directories(
        self, tmp_path: Path
    ) -> None:
        """mkdir(parents=True) should create nested directories."""
        adapter = RealFileSystemAdapter()
        nested_dir = tmp_path / "a" / "b" / "c"

        adapter.mkdir(nested_dir, parents=True)

        assert nested_dir.exists()
        assert nested_dir.is_dir()

    def test_mkdir_without_parents_raises_for_missing_parent(
        self, tmp_path: Path
    ) -> None:
        """mkdir(parents=False) should raise for missing parent directories."""
        adapter = RealFileSystemAdapter()
        nested_dir = tmp_path / "missing_parent" / "child"

        with pytest.raises(FileNotFoundError):
            adapter.mkdir(nested_dir, parents=False)


class TestRealFileSystemAdapterListDir:
    """Test list_dir() method."""

    def test_list_dir_returns_directory_contents(self, tmp_path: Path) -> None:
        """list_dir() should return list of paths in directory."""
        adapter = RealFileSystemAdapter()
        # Create test files
        (tmp_path / "file1.txt").write_text("1")
        (tmp_path / "file2.txt").write_text("2")
        (tmp_path / "subdir").mkdir()

        result = adapter.list_dir(tmp_path)

        assert len(result) == 3
        result_names = {p.name for p in result}
        assert result_names == {"file1.txt", "file2.txt", "subdir"}

    def test_list_dir_returns_empty_for_empty_directory(self, tmp_path: Path) -> None:
        """list_dir() should return empty list for empty directory."""
        adapter = RealFileSystemAdapter()
        empty_dir = tmp_path / "empty"
        empty_dir.mkdir()

        result = adapter.list_dir(empty_dir)

        assert result == []

    def test_list_dir_raises_for_nonexistent_directory(self, tmp_path: Path) -> None:
        """list_dir() should raise FileNotFoundError for nonexistent directory."""
        adapter = RealFileSystemAdapter()
        nonexistent = tmp_path / "nonexistent"

        with pytest.raises(FileNotFoundError):
            adapter.list_dir(nonexistent)


class TestRealFileSystemAdapterCopyFile:
    """Test copy_file() method."""

    def test_copy_file_copies_content(self, tmp_path: Path) -> None:
        """copy_file() should copy file content to destination."""
        adapter = RealFileSystemAdapter()
        source = tmp_path / "source.txt"
        dest = tmp_path / "dest.txt"
        source.write_text("content to copy")

        adapter.copy_file(source, dest)

        assert dest.exists()
        assert dest.read_text() == "content to copy"

    def test_copy_file_preserves_source(self, tmp_path: Path) -> None:
        """copy_file() should not remove the source file."""
        adapter = RealFileSystemAdapter()
        source = tmp_path / "source.txt"
        dest = tmp_path / "dest.txt"
        source.write_text("content")

        adapter.copy_file(source, dest)

        assert source.exists()

    def test_copy_file_raises_for_nonexistent_source(self, tmp_path: Path) -> None:
        """copy_file() should raise FileNotFoundError for missing source."""
        adapter = RealFileSystemAdapter()
        nonexistent = tmp_path / "nonexistent.txt"
        dest = tmp_path / "dest.txt"

        with pytest.raises(FileNotFoundError):
            adapter.copy_file(nonexistent, dest)


class TestRealFileSystemAdapterRemove:
    """Test remove() method."""

    def test_remove_deletes_file(self, tmp_path: Path) -> None:
        """remove() should delete a file."""
        adapter = RealFileSystemAdapter()
        test_file = tmp_path / "to_delete.txt"
        test_file.write_text("content")

        adapter.remove(test_file)

        assert not test_file.exists()

    def test_remove_deletes_empty_directory(self, tmp_path: Path) -> None:
        """remove() should delete an empty directory."""
        adapter = RealFileSystemAdapter()
        empty_dir = tmp_path / "empty_dir"
        empty_dir.mkdir()

        adapter.remove(empty_dir)

        assert not empty_dir.exists()

    def test_remove_raises_for_nonexistent_path(self, tmp_path: Path) -> None:
        """remove() should raise FileNotFoundError for nonexistent path."""
        adapter = RealFileSystemAdapter()
        nonexistent = tmp_path / "nonexistent"

        with pytest.raises(FileNotFoundError):
            adapter.remove(nonexistent)
