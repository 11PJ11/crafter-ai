"""
Pytest configuration for DES acceptance tests.

Provides shared fixtures for test setup and teardown.
"""

import pytest


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
def des_orchestrator(in_memory_filesystem):
    """
    DES orchestrator with mocked adapters for testing.

    Uses in-memory filesystem and mocked time/hook/validator for:
    - Zero real filesystem operations
    - Deterministic time behavior
    - Fast test execution (<1 second)

    Returns:
        DESOrchestrator: Configured orchestrator with mocked dependencies
    """
    from datetime import datetime, timezone
    from des.orchestrator import DESOrchestrator
    from des.adapters import (
        MockedSubagentStopHook,
        MockedTemplateValidator,
        MockedTimeProvider,
    )

    return DESOrchestrator(
        hook=MockedSubagentStopHook(),
        validator=MockedTemplateValidator(),
        filesystem=in_memory_filesystem,
        time_provider=MockedTimeProvider(
            datetime(2026, 1, 26, 10, 0, 0, tzinfo=timezone.utc)
        ),
    )
