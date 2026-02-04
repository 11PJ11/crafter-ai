"""
Shared fixtures for installer domain tests.

Provides port mocking fixtures for hexagonal architecture testing:
- FileSystemPort mocks for isolated file operations
- GitPort mocks for commit analysis without git dependency
- BuildPort mocks for wheel building without subprocess
- PipxPort mocks for installation without real pipx
- ConfigPort mocks for configuration without disk I/O
"""

import re
from pathlib import Path
from typing import Protocol, runtime_checkable

import pytest


# ============================================================================
# ANSI Escape Code Utilities
# ============================================================================

# Regex to match ANSI escape sequences
ANSI_ESCAPE_PATTERN = re.compile(r"\x1b\[[0-9;]*[a-zA-Z]|\x1b\][^\x07]*\x07")


def strip_ansi(text: str) -> str:
    """Remove ANSI escape codes from text.

    Handles:
    - CSI sequences: ESC [ ... letter (colors, cursor, etc.)
    - OSC sequences: ESC ] ... BEL (window titles, hyperlinks)

    Args:
        text: String potentially containing ANSI escape codes.

    Returns:
        String with all ANSI escape codes removed.
    """
    return ANSI_ESCAPE_PATTERN.sub("", text)


# ============================================================================
# Port Protocols (for type hints before production ports exist)
# ============================================================================


@runtime_checkable
class FileSystemPort(Protocol):
    """Port for file system operations."""

    def exists(self, path: Path) -> bool:
        """Check if path exists."""
        ...

    def read_text(self, path: Path) -> str:
        """Read file contents as text."""
        ...

    def write_text(self, path: Path, content: str) -> None:
        """Write text content to file."""
        ...

    def mkdir(self, path: Path, parents: bool = False) -> None:
        """Create directory."""
        ...

    def list_dir(self, path: Path) -> list[Path]:
        """List directory contents."""
        ...


@runtime_checkable
class GitPort(Protocol):
    """Port for git operations."""

    def get_commits_since_tag(self, tag: str) -> list[str]:
        """Get commit messages since a tag."""
        ...

    def get_latest_tag(self) -> str | None:
        """Get the latest version tag."""
        ...

    def get_current_branch(self) -> str:
        """Get current branch name."""
        ...


@runtime_checkable
class BuildPort(Protocol):
    """Port for build operations."""

    def build_wheel(self, output_dir: Path) -> Path:
        """Build wheel and return path to built wheel."""
        ...

    def build_sdist(self, output_dir: Path) -> Path:
        """Build source distribution and return path."""
        ...


@runtime_checkable
class PipxPort(Protocol):
    """Port for pipx operations."""

    def install(self, package: str, force: bool = False) -> bool:
        """Install package via pipx."""
        ...

    def uninstall(self, package: str) -> bool:
        """Uninstall package via pipx."""
        ...

    def is_installed(self, package: str) -> bool:
        """Check if package is installed."""
        ...

    def get_version(self, package: str) -> str | None:
        """Get installed package version."""
        ...


# ============================================================================
# In-Memory Port Implementations for Testing
# ============================================================================


class InMemoryFileSystemAdapter:
    """In-memory file system for isolated testing."""

    def __init__(self) -> None:
        self._files: dict[str, str] = {}
        self._directories: set[str] = set()

    def exists(self, path: Path) -> bool:
        """Check if path exists in memory."""
        path_str = str(path)
        return path_str in self._files or path_str in self._directories

    def read_text(self, path: Path) -> str:
        """Read file contents from memory."""
        path_str = str(path)
        if path_str not in self._files:
            raise FileNotFoundError(f"File not found: {path}")
        return self._files[path_str]

    def write_text(self, path: Path, content: str) -> None:
        """Write content to in-memory file."""
        path_str = str(path)
        self._files[path_str] = content
        # Ensure parent directories exist
        parent = path.parent
        while parent != parent.parent:
            self._directories.add(str(parent))
            parent = parent.parent

    def mkdir(self, path: Path, parents: bool = False) -> None:
        """Create directory in memory."""
        path_str = str(path)
        if parents:
            parent = path
            while parent != parent.parent:
                self._directories.add(str(parent))
                parent = parent.parent
        else:
            self._directories.add(path_str)

    def list_dir(self, path: Path) -> list[Path]:
        """List directory contents from memory."""
        path_str = str(path)
        if path_str not in self._directories and path_str != ".":
            raise FileNotFoundError(f"Directory not found: {path}")

        results = []
        prefix = path_str + "/" if not path_str.endswith("/") else path_str

        # Find files and directories directly under this path
        for file_path in self._files:
            if file_path.startswith(prefix):
                relative = file_path[len(prefix) :]
                if "/" not in relative:
                    results.append(Path(file_path))

        for dir_path in self._directories:
            if dir_path.startswith(prefix):
                relative = dir_path[len(prefix) :]
                if "/" not in relative and relative:
                    results.append(Path(dir_path))

        return results

    # Test helper methods
    def _set_file(self, path: str, content: str) -> None:
        """Test helper to pre-populate files."""
        self._files[path] = content

    def _set_directory(self, path: str) -> None:
        """Test helper to pre-populate directories."""
        self._directories.add(path)


class MockGitAdapter:
    """Mock git adapter for testing without git dependency."""

    def __init__(self) -> None:
        self._commits: list[str] = []
        self._latest_tag: str | None = None
        self._current_branch: str = "main"

    def get_commits_since_tag(self, tag: str) -> list[str]:
        """Return pre-configured commits."""
        return self._commits

    def get_latest_tag(self) -> str | None:
        """Return pre-configured latest tag."""
        return self._latest_tag

    def get_current_branch(self) -> str:
        """Return pre-configured branch name."""
        return self._current_branch

    # Test helper methods
    def _set_commits(self, commits: list[str]) -> None:
        """Test helper to configure commits."""
        self._commits = commits

    def _set_latest_tag(self, tag: str | None) -> None:
        """Test helper to configure latest tag."""
        self._latest_tag = tag

    def _set_current_branch(self, branch: str) -> None:
        """Test helper to configure current branch."""
        self._current_branch = branch


class MockBuildAdapter:
    """Mock build adapter for testing without subprocess."""

    def __init__(self) -> None:
        self._wheel_path: Path | None = None
        self._sdist_path: Path | None = None
        self._should_fail: bool = False
        self._failure_message: str = "Build failed"

    def build_wheel(self, output_dir: Path) -> Path:
        """Return pre-configured wheel path or raise error."""
        if self._should_fail:
            raise RuntimeError(self._failure_message)
        if self._wheel_path:
            return self._wheel_path
        return output_dir / "crafter_ai-0.1.0-py3-none-any.whl"

    def build_sdist(self, output_dir: Path) -> Path:
        """Return pre-configured sdist path or raise error."""
        if self._should_fail:
            raise RuntimeError(self._failure_message)
        if self._sdist_path:
            return self._sdist_path
        return output_dir / "crafter_ai-0.1.0.tar.gz"

    # Test helper methods
    def _set_wheel_path(self, path: Path) -> None:
        """Test helper to configure wheel path."""
        self._wheel_path = path

    def _set_sdist_path(self, path: Path) -> None:
        """Test helper to configure sdist path."""
        self._sdist_path = path

    def _set_should_fail(
        self, should_fail: bool, message: str = "Build failed"
    ) -> None:
        """Test helper to configure build failure."""
        self._should_fail = should_fail
        self._failure_message = message


class MockPipxAdapter:
    """Mock pipx adapter for testing without real pipx."""

    def __init__(self) -> None:
        self._installed_packages: dict[str, str] = {}
        self._should_fail: bool = False
        self._failure_message: str = "pipx operation failed"

    def install(self, package: str, force: bool = False) -> bool:
        """Simulate package installation."""
        if self._should_fail:
            raise RuntimeError(self._failure_message)
        # Extract version from package path if wheel
        if package.endswith(".whl"):
            # Parse version from wheel filename (format: name-version-py3-none-any.whl)
            # Wheel spec requires at least name-version, so minimum 2 parts
            parts = Path(package).stem.split("-")
            min_wheel_parts = 2  # Wheel filename requires at least name-version
            if len(parts) >= min_wheel_parts:
                name = parts[0].replace("_", "-")
                version = parts[1]
                self._installed_packages[name] = version
                return True
        self._installed_packages[package] = "0.1.0"
        return True

    def uninstall(self, package: str) -> bool:
        """Simulate package uninstallation."""
        if self._should_fail:
            raise RuntimeError(self._failure_message)
        if package in self._installed_packages:
            del self._installed_packages[package]
            return True
        return False

    def is_installed(self, package: str) -> bool:
        """Check if package is in mock installed list."""
        return package in self._installed_packages

    def get_version(self, package: str) -> str | None:
        """Get version from mock installed packages."""
        return self._installed_packages.get(package)

    # Test helper methods
    def _set_installed(self, package: str, version: str) -> None:
        """Test helper to pre-configure installed package."""
        self._installed_packages[package] = version

    def _set_should_fail(
        self, should_fail: bool, message: str = "pipx operation failed"
    ) -> None:
        """Test helper to configure operation failure."""
        self._should_fail = should_fail
        self._failure_message = message


# ============================================================================
# Pytest Fixtures
# ============================================================================


@pytest.fixture
def mock_filesystem() -> InMemoryFileSystemAdapter:
    """Provide in-memory filesystem for isolated testing."""
    return InMemoryFileSystemAdapter()


@pytest.fixture
def mock_git() -> MockGitAdapter:
    """Provide mock git adapter for testing without git."""
    return MockGitAdapter()


@pytest.fixture
def mock_build() -> MockBuildAdapter:
    """Provide mock build adapter for testing without subprocess."""
    return MockBuildAdapter()


@pytest.fixture
def mock_pipx() -> MockPipxAdapter:
    """Provide mock pipx adapter for testing without real pipx."""
    return MockPipxAdapter()


@pytest.fixture
def tmp_project_dir(tmp_path: Path, mock_filesystem: InMemoryFileSystemAdapter) -> Path:
    """
    Provide a temporary project directory with basic structure.

    Sets up:
    - pyproject.toml with basic configuration
    - src/crafter_ai/__init__.py with version
    - dist/ directory for wheel output
    """
    project_dir = tmp_path / "crafter-ai"

    # Set up directory structure in mock filesystem
    mock_filesystem.mkdir(project_dir, parents=True)
    mock_filesystem.mkdir(project_dir / "src" / "crafter_ai", parents=True)
    mock_filesystem.mkdir(project_dir / "dist", parents=True)

    # Create pyproject.toml
    pyproject_content = """[project]
name = "crafter-ai"
version = "0.1.0"
"""
    mock_filesystem.write_text(project_dir / "pyproject.toml", pyproject_content)

    # Create __init__.py
    init_content = '__version__ = "0.1.0"\n'
    mock_filesystem.write_text(
        project_dir / "src" / "crafter_ai" / "__init__.py", init_content
    )

    return project_dir
