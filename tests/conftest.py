"""
Root pytest configuration for all tests.

Provides shared fixtures accessible to both acceptance and scenario tests.
"""

import pytest
from datetime import datetime, timezone


@pytest.fixture
def in_memory_filesystem():
    """
    In-memory filesystem for testing without disk I/O.

    Returns:
        InMemoryFileSystem: Fresh in-memory filesystem instance
    """
    from des.adapters import InMemoryFileSystem

    return InMemoryFileSystem()


@pytest.fixture
def real_filesystem():
    """
    Real filesystem for integration tests that need actual disk I/O.

    Returns:
        RealFileSystem: Filesystem that performs actual disk operations
    """
    from des.adapters import RealFileSystem

    return RealFileSystem()


@pytest.fixture
def mocked_time_provider():
    """
    Mocked time provider with fixed time for deterministic testing.

    Returns:
        MockedTimeProvider: Time provider starting at 2026-01-26T10:00:00Z
    """
    from des.adapters import MockedTimeProvider

    return MockedTimeProvider(datetime(2026, 1, 26, 10, 0, 0, tzinfo=timezone.utc))


@pytest.fixture
def mocked_hook():
    """
    Mocked subagent stop hook for testing without real hook behavior.

    Returns:
        MockedSubagentStopHook: Hook that returns predefined results
    """
    from des.adapters import MockedSubagentStopHook

    return MockedSubagentStopHook()


@pytest.fixture
def mocked_validator():
    """
    Mocked template validator for testing without real validation.

    Returns:
        MockedTemplateValidator: Validator returning passing results by default
    """
    from des.adapters import MockedTemplateValidator

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
    from des.orchestrator import DESOrchestrator

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
    from des.orchestrator import DESOrchestrator

    return DESOrchestrator(
        hook=mocked_hook,
        validator=mocked_validator,
        filesystem=real_filesystem,
        time_provider=mocked_time_provider,
    )
