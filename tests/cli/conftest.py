"""
Shared fixtures for CLI command tests.

Provides fixtures for testing Typer CLI commands:
- CLI runner for isolated command invocation
- Mock service dependencies for unit testing
- Integration fixtures with real services
- ANSI-stripping utilities for CI-compatible assertions
"""

from dataclasses import dataclass
from typing import Any

import pytest
from typer.testing import CliRunner, Result

# Lazy imports for mock adapters to avoid circular imports at module load time
# These are imported inside fixtures intentionally (PLC0415 noqa applied)
from tests.installer.conftest import (
    InMemoryFileSystemAdapter,
    MockBuildAdapter,
    MockGitAdapter,
    MockPipxAdapter,
    strip_ansi,
)


@dataclass
class CleanResult:
    """Wrapper around Typer Result with ANSI-stripped output.

    In CI environments, Rich/Typer may emit ANSI escape codes even when NO_COLOR
    is set, because the Console is created at module import time before env vars
    are configured. This wrapper strips ANSI codes for reliable assertions.

    Attributes:
        exit_code: The command's exit code.
        output: The command's stdout with ANSI codes stripped.
        stdout: Alias for output (for compatibility with Result.stdout).
        stderr: The command's stderr with ANSI codes stripped (if available).
        exception: Any exception raised during command execution.
        _original: The original Result object for accessing raw data.
    """

    exit_code: int
    output: str
    stderr: str
    exception: BaseException | None
    _original: Result

    @property
    def stdout(self) -> str:
        """Alias for output (compatibility with Result.stdout)."""
        return self.output

    @classmethod
    def from_result(cls, result: Result) -> "CleanResult":
        """Create a CleanResult from a Typer Result.

        Args:
            result: Original Typer CliRunner Result.

        Returns:
            CleanResult with ANSI codes stripped from output.
        """
        return cls(
            exit_code=result.exit_code,
            output=strip_ansi(result.output),
            stderr=strip_ansi(result.stderr) if result.stderr else "",
            exception=result.exception,
            _original=result,
        )


class CleanCliRunner:
    """CliRunner wrapper that returns CleanResult with ANSI codes stripped.

    This wrapper ensures consistent test assertions across local development
    and CI environments by automatically stripping ANSI escape codes from
    command output.

    Usage:
        runner = CleanCliRunner()
        result = runner.invoke(app, ["command", "--option"])
        assert "--flag" in result.output  # Works even with Rich styling
    """

    def __init__(self, **kwargs: Any) -> None:
        """Initialize with CliRunner kwargs.

        Args:
            **kwargs: Arguments passed to CliRunner constructor.
        """
        # Always set NO_COLOR for best-effort color suppression
        env = kwargs.pop("env", {})
        env["NO_COLOR"] = "1"
        self._runner = CliRunner(env=env, **kwargs)

    def invoke(self, app: Any, args: list[str], **kwargs: Any) -> CleanResult:
        """Invoke a CLI command and return cleaned result.

        Args:
            app: Typer application to invoke.
            args: Command line arguments.
            **kwargs: Additional arguments passed to CliRunner.invoke.

        Returns:
            CleanResult with ANSI codes stripped from output.
        """
        result = self._runner.invoke(app, args, **kwargs)
        return CleanResult.from_result(result)


@pytest.fixture
def cli_runner() -> CleanCliRunner:
    """
    Provide a CLI test runner for testing Typer commands.

    Returns CleanCliRunner that automatically strips ANSI escape codes
    from output for reliable CI assertions.

    Returns:
        CleanCliRunner: Typer CLI test runner with ANSI stripping.
    """
    return CleanCliRunner()


@pytest.fixture
def cli_runner_isolated() -> CleanCliRunner:
    """
    Provide an isolated CLI test runner with separate environment.

    Uses mix_stderr=False to keep stdout and stderr separate for assertions.
    Returns CleanCliRunner that automatically strips ANSI escape codes.

    Returns:
        CleanCliRunner: Isolated CLI test runner with ANSI stripping.
    """
    return CleanCliRunner()


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
