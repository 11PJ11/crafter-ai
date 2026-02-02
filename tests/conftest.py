"""
Root pytest configuration for all tests.

Provides shared fixtures accessible to both acceptance and scenario tests.
"""

from datetime import datetime, timezone

import pytest
from typer.testing import CliRunner


def pytest_ignore_collect(collection_path, config):  # noqa: ARG001
    """Skip collection of test files that may have import issues in mutation testing."""
    path_str = str(collection_path)

    # Skip specific problematic test files (always)
    ignore_files = [
        "test_install_nwave_target_hooks.py",
        "test_validate_documentation_versions.py",
    ]
    for pattern in ignore_files:
        if pattern in path_str:
            return True

    # During mutation testing (when running from mutants folder), skip tests
    # that use subprocess calls or path-dependent file access
    if "/mutants/" in path_str:
        mutant_skip_patterns = [
            "tests/acceptance/versioning_release_management/",
            "tests/acceptance/features/versioning-release-management/",
            "tests/nwave/",  # Tests that access nWave templates by path
            "test_step_schema",  # Schema tests with path dependencies
            "test_template_integrity",  # Template integrity checks
            "tests/unit/git_workflow/",  # Git hook tests with path dependencies
            # Versioning tests with subprocess calls
            "test_git_adapter_forge.py",
            "test_update_cli.py",
            "test_github_cli_adapter.py",
        ]
        for pattern in mutant_skip_patterns:
            if pattern in path_str:
                return True

    return False


@pytest.fixture
def in_memory_filesystem():
    """
    In-memory filesystem for testing without disk I/O.

    Returns:
        InMemoryFileSystem: Fresh in-memory filesystem instance
    """
    from tests.des.adapters import InMemoryFileSystem  # noqa: PLC0415

    return InMemoryFileSystem()


@pytest.fixture
def real_filesystem():
    """
    Real filesystem for integration tests that need actual disk I/O.

    Returns:
        RealFileSystem: Filesystem that performs actual disk operations
    """
    from src.des.adapters import RealFileSystem  # noqa: PLC0415

    return RealFileSystem()


@pytest.fixture
def mocked_time_provider():
    """
    Mocked time provider with fixed time for deterministic testing.

    Returns:
        MockedTimeProvider: Time provider starting at 2026-01-26T10:00:00Z
    """
    from tests.des.adapters import MockedTimeProvider  # noqa: PLC0415

    return MockedTimeProvider(datetime(2026, 1, 26, 10, 0, 0, tzinfo=timezone.utc))


@pytest.fixture
def mocked_hook():
    """
    Mocked subagent stop hook for testing without real hook behavior.

    Returns:
        MockedSubagentStopHook: Hook that returns predefined results
    """
    from tests.des.adapters import MockedSubagentStopHook  # noqa: PLC0415

    return MockedSubagentStopHook()


@pytest.fixture
def mocked_validator():
    """
    Mocked template validator for testing without real validation.

    Returns:
        MockedTemplateValidator: Validator returning passing results by default
    """
    from tests.des.adapters import MockedTemplateValidator  # noqa: PLC0415

    return MockedTemplateValidator()


@pytest.fixture
def des_orchestrator(
    in_memory_filesystem, mocked_hook, mocked_validator, mocked_time_provider
):
    """
    DES orchestrator with all mocked adapters for testing.

    Uses in-memory filesystem, mocked time, mocked hook, and mocked validator for:
    - Zero real filesystem operations
    - Deterministic time behavior
    - Fast test execution (<1 second)
    - Predictable validation results

    Returns:
        DESOrchestrator: Configured orchestrator with mocked dependencies
    """
    from src.des.application.orchestrator import DESOrchestrator  # noqa: PLC0415

    return DESOrchestrator(
        hook=mocked_hook,
        validator=mocked_validator,
        filesystem=in_memory_filesystem,
        time_provider=mocked_time_provider,
    )


@pytest.fixture
def scenario_des_orchestrator(
    real_filesystem, mocked_hook, mocked_validator, mocked_time_provider
):
    """
    DES orchestrator for scenario tests that require real filesystem operations.

    Uses real filesystem but keeps mocked time, hook, and validator for:
    - Actual disk I/O for scenario test file operations
    - Deterministic time behavior
    - Predictable validation and hook results
    - Isolation from external dependencies

    Returns:
        DESOrchestrator: Configured orchestrator with real filesystem
    """
    from src.des.application.orchestrator import DESOrchestrator  # noqa: PLC0415

    return DESOrchestrator(
        hook=mocked_hook,
        validator=mocked_validator,
        filesystem=real_filesystem,
        time_provider=mocked_time_provider,
    )


# ============================================================================
# crafter-ai CLI Fixtures
# ============================================================================


@pytest.fixture
def cli_runner() -> CliRunner:
    """
    Provide a CLI test runner for testing Typer commands.

    Returns:
        CliRunner: Typer CLI test runner for isolated command testing
    """
    return CliRunner()
