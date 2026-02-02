"""
Mock FileSystemPort for Acceptance Tests
=========================================

Provides controlled file system behavior for testing without touching
the real file system. Aligns with hexagonal architecture boundaries.

Port Interface: nWave/core/installer/ports/file_system_port.py
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Protocol, Set


class FileSystemPort(Protocol):
    """
    Port interface for file system operations.

    This protocol defines what the application services expect from
    a file system adapter. Tests inject MockFileSystemAdapter to
    control behavior.
    """

    def exists(self, path: Path) -> bool:
        """Check if path exists."""
        ...

    def is_writable(self, path: Path) -> bool:
        """Check if path is writable."""
        ...

    def read_text(self, path: Path) -> str:
        """Read file as text."""
        ...

    def write_text(self, path: Path, content: str) -> None:
        """Write text to file."""
        ...

    def copy_tree(self, src: Path, dst: Path) -> int:
        """Copy directory tree, return file count."""
        ...

    def remove_tree(self, path: Path) -> None:
        """Remove directory tree."""
        ...

    def count_files(self, path: Path, pattern: str = "*.md") -> int:
        """Count files matching pattern."""
        ...

    def ensure_directory(self, path: Path) -> None:
        """Create directory if not exists."""
        ...


@dataclass
class MockFileSystemAdapter:
    """
    Mock implementation of FileSystemPort for testing.

    Provides controlled file system behavior without touching
    the real file system.
    """

    # Simulated file contents
    files: Dict[str, str] = field(default_factory=dict)

    # Simulated directories
    directories: Set[str] = field(default_factory=set)

    # Simulated file counts per directory
    file_counts: Dict[str, int] = field(default_factory=dict)

    # Writable paths
    writable_paths: Set[str] = field(default_factory=set)

    # Paths to simulate errors
    error_on_read: Set[str] = field(default_factory=set)
    error_on_write: Set[str] = field(default_factory=set)

    def exists(self, path: Path) -> bool:
        """Check if path exists in mock file system."""
        path_str = str(path)
        return path_str in self.files or path_str in self.directories

    def is_writable(self, path: Path) -> bool:
        """Check if path is writable in mock file system."""
        path_str = str(path)
        # Check exact path or parent directory
        if path_str in self.writable_paths:
            return True
        parent = str(path.parent)
        return parent in self.writable_paths

    def read_text(self, path: Path) -> str:
        """Read file content from mock file system."""
        path_str = str(path)
        if path_str in self.error_on_read:
            raise PermissionError(f"Cannot read {path_str}")
        if path_str not in self.files:
            raise FileNotFoundError(f"File not found: {path_str}")
        return self.files[path_str]

    def write_text(self, path: Path, content: str) -> None:
        """Write content to mock file system."""
        path_str = str(path)
        if path_str in self.error_on_write:
            raise PermissionError(f"Cannot write to {path_str}")
        if not self.is_writable(path):
            raise PermissionError(f"Path not writable: {path_str}")
        self.files[path_str] = content

    def copy_tree(self, src: Path, dst: Path) -> int:
        """Simulate copying directory tree."""
        src_str = str(src)
        if src_str not in self.directories:
            raise FileNotFoundError(f"Source directory not found: {src_str}")

        # Return preconfigured file count or default
        count = self.file_counts.get(src_str, 10)
        self.directories.add(str(dst))
        return count

    def remove_tree(self, path: Path) -> None:
        """Simulate removing directory tree."""
        path_str = str(path)
        self.directories.discard(path_str)
        # Remove files under this path
        to_remove = [f for f in self.files if f.startswith(path_str)]
        for f in to_remove:
            del self.files[f]

    def count_files(self, path: Path, pattern: str = "*.md") -> int:
        """Return preconfigured file count for path."""
        path_str = str(path)
        return self.file_counts.get(path_str, 0)

    def ensure_directory(self, path: Path) -> None:
        """Simulate creating directory."""
        self.directories.add(str(path))

    # Test setup helpers

    def setup_valid_repo(self) -> None:
        """Configure mock for a valid nWave repository."""
        # Pyproject.toml
        self.files["pyproject.toml"] = """
[project]
name = "nwave"
version = "1.3.0"
description = "nWave Framework"
[project.scripts]
nw = "nWave.cli:main"
"""
        # Directories
        self.directories.add("nWave")
        self.directories.add("nWave/agents")
        self.directories.add("nWave/commands")
        self.directories.add("nWave/templates")
        self.directories.add("dist")

        # File counts
        self.file_counts["nWave/agents"] = 47
        self.file_counts["nWave/commands"] = 23
        self.file_counts["nWave/templates"] = 12
        self.file_counts["nWave"] = 127

        # Writable paths
        self.writable_paths.add("dist")
        self.writable_paths.add("~/.claude")
        self.writable_paths.add("~/.claude/agents/nw")

    def setup_invalid_pyproject(self, error_line: int = 42) -> None:
        """Configure mock with invalid pyproject.toml."""
        self.files["pyproject.toml"] = f"""
[project]
name = "nwave"
# Syntax error at line {error_line}
version = 1.3.0  # Missing quotes
"""

    def setup_missing_pyproject(self) -> None:
        """Configure mock without pyproject.toml."""
        if "pyproject.toml" in self.files:
            del self.files["pyproject.toml"]

    def setup_missing_source_dir(self) -> None:
        """Configure mock without source directory."""
        self.directories.discard("nWave")

    def setup_unwritable_dist(self) -> None:
        """Configure mock with unwritable dist directory."""
        self.writable_paths.discard("dist")

    def setup_existing_wheel(self, wheel_path: str) -> None:
        """Configure mock with existing wheel file."""
        self.files[wheel_path] = "wheel content"

    def setup_multiple_wheels(self, wheel_paths: List[str]) -> None:
        """Configure mock with multiple wheel files."""
        for path in wheel_paths:
            self.files[path] = "wheel content"

    def setup_installed_nwave(
        self,
        install_path: str = "~/.claude/agents/nw",
        version: str = "1.2.0",
        agent_count: int = 47
    ) -> None:
        """Configure mock with existing nWave installation."""
        self.directories.add(install_path)
        self.directories.add(f"{install_path}/agents")
        self.file_counts[f"{install_path}/agents"] = agent_count
        self.files[f"{install_path}/manifest.yaml"] = f"version: {version}"

    def setup_unwritable_claude_dir(self) -> None:
        """Configure mock with unwritable ~/.claude directory."""
        self.writable_paths.discard("~/.claude")
        self.writable_paths.discard("~/.claude/agents/nw")
