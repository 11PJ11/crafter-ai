"""
Shared fixtures for CLI command tests.

Provides fixtures for testing Typer CLI commands:
- CLI runner for isolated command invocation
- Mock service dependencies for unit testing
- Integration fixtures with real services
"""

import pytest
from typer.testing import CliRunner

# Lazy imports for mock adapters to avoid circular imports at module load time
# These are imported inside fixtures intentionally (PLC0415 noqa applied)
from tests.installer.conftest import (
    InMemoryFileSystemAdapter,
    MockBuildAdapter,
    MockGitAdapter,
    MockPipxAdapter,
)


@pytest.fixture
def cli_runner() -> CliRunner:
    """
    Provide a CLI test runner for testing Typer commands.

    Returns:
        CliRunner: Typer CLI test runner for isolated command testing
    """
    return CliRunner()


@pytest.fixture
def cli_runner_isolated() -> CliRunner:
    """
    Provide an isolated CLI test runner with separate environment.

    Uses mix_stderr=False to keep stdout and stderr separate for assertions.

    Returns:
        CliRunner: Isolated CLI test runner
    """
    return CliRunner(mix_stderr=False)


# Re-export mock adapters from installer conftest for CLI tests that need them
@pytest.fixture
def mock_filesystem() -> InMemoryFileSystemAdapter:
    """
    Provide in-memory filesystem adapter.

    Returns:
        InMemoryFileSystemAdapter: Fresh instance for isolated testing.
    """
    return InMemoryFileSystemAdapter()


@pytest.fixture
def mock_git() -> MockGitAdapter:
    """
    Provide mock git adapter.

    Returns:
        MockGitAdapter: Fresh instance for testing without git.
    """
    return MockGitAdapter()


@pytest.fixture
def mock_build() -> MockBuildAdapter:
    """
    Provide mock build adapter.

    Returns:
        MockBuildAdapter: Fresh instance for testing without subprocess.
    """
    return MockBuildAdapter()


@pytest.fixture
def mock_pipx() -> MockPipxAdapter:
    """
    Provide mock pipx adapter.

    Returns:
        MockPipxAdapter: Fresh instance for testing without real pipx.
    """
    return MockPipxAdapter()
