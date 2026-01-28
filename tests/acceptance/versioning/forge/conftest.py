"""
pytest configuration for US-003 Forge acceptance tests.

HEXAGONAL BOUNDARY ENFORCEMENT:
- Tests invoke CLI entry points only
- Mocking allowed only at port boundaries (GitPort, FileSystemPort, TestRunnerPort)
- No direct imports from nWave.core.* in test code
"""

import os
import pytest
from pathlib import Path
from datetime import date
from typing import List, Optional, Callable


@pytest.fixture(scope="function")
def test_repository(tmp_path, monkeypatch):
    """
    Create isolated test repository for each test.
    Simulates a developer's local nWave clone.
    """
    repo_dir = tmp_path / "test-repo"
    repo_dir.mkdir()

    # Create dist directory (will be cleaned during build)
    dist_dir = repo_dir / "dist"
    dist_dir.mkdir()

    monkeypatch.chdir(repo_dir)

    return {
        "root": repo_dir,
        "dist": dist_dir,
    }


@pytest.fixture
def mock_git_adapter():
    """
    In-memory mock for GitPort.

    Returns configured git state for testing.
    """
    class MockGitAdapter:
        def __init__(self):
            self.current_branch = "main"
            self._uncommitted_changes = False
            self._repo_root: Optional[Path] = None

        def configure(
            self,
            branch: str = "main",
            uncommitted_changes: bool = False,
            repo_root: Path = None,
        ):
            self.current_branch = branch
            self._uncommitted_changes = uncommitted_changes
            self._repo_root = repo_root

        def get_current_branch(self) -> str:
            return self.current_branch

        def has_uncommitted_changes(self) -> bool:
            return self._uncommitted_changes

        def get_repo_root(self) -> Path:
            if self._repo_root is None:
                raise ValueError("repo_root not configured")
            return self._repo_root

    return MockGitAdapter()


@pytest.fixture
def mock_test_runner():
    """
    In-memory mock for test runner.

    Simulates pytest execution with configurable results.
    """
    class MockTestRunner:
        def __init__(self):
            self.tests_pass = True
            self.failure_count = 0
            self.run_count = 0

        def configure(self, tests_pass: bool = True, failure_count: int = 0):
            self.tests_pass = tests_pass
            self.failure_count = failure_count

        def run_tests(self) -> tuple[bool, int]:
            """
            Run tests and return (success, failure_count).
            """
            self.run_count += 1
            if self.tests_pass:
                return True, 0
            return False, self.failure_count

        @property
        def was_called(self) -> bool:
            return self.run_count > 0

    return MockTestRunner()


@pytest.fixture
def mock_date_provider():
    """
    Mock for date provider to control "today's date".
    """
    class MockDateProvider:
        def __init__(self):
            self._today = date(2026, 1, 27)

        def configure(self, today: date):
            self._today = today

        def today(self) -> date:
            return self._today

    return MockDateProvider()


@pytest.fixture
def in_memory_file_system_for_forge(test_repository):
    """
    In-memory implementation for build file system operations.

    Manages:
    - pyproject.toml (base version)
    - dist/ directory (cleaned before build, populated after)
    - VERSION file in dist/
    """
    class InMemoryBuildFileSystem:
        def __init__(self, test_dirs):
            self._test_dirs = test_dirs
            self._pyproject_version = "1.2.3"
            self._dist_contents: List[str] = []
            self._dist_version: Optional[str] = None
            self._was_cleaned = False

        def configure(self, base_version: str = "1.2.3"):
            self._pyproject_version = base_version

        def read_base_version(self) -> str:
            """Read base version from pyproject.toml."""
            return self._pyproject_version

        def clean_dist(self) -> bool:
            """Clean dist/ directory before build."""
            self._was_cleaned = True
            self._dist_contents = []
            self._dist_version = None
            return True

        def create_distribution(self, version: str) -> bool:
            """Create distribution in dist/ directory."""
            self._dist_version = version
            self._dist_contents = [
                "VERSION",
                "nWave/",
                "agents/",
                "commands/",
            ]
            return True

        def get_dist_version(self) -> Optional[str]:
            """Get version from dist/VERSION."""
            return self._dist_version

        @property
        def dist_was_cleaned(self) -> bool:
            return self._was_cleaned

        @property
        def dist_exists(self) -> bool:
            return len(self._dist_contents) > 0

    return InMemoryBuildFileSystem(test_repository)


@pytest.fixture
def cli_result():
    """Container for CLI execution results."""
    return {
        "stdout": "",
        "stderr": "",
        "returncode": 0,
        "output": "",
        "prompt": "",
    }
