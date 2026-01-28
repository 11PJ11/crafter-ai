"""
pytest-bdd configuration for versioning-release-management acceptance tests.

This file provides:
1. Test fixtures for isolation and dependency injection
2. pytest-bdd configuration and hooks
3. Shared test utilities

CRITICAL: All fixtures support hexagonal boundary enforcement.
Tests interact with the system through CLI entry points (driving ports) only.
"""

import os
import pytest
from pathlib import Path


# ============================================================================
# Test Isolation Fixtures
# ============================================================================


@pytest.fixture(scope="function")
def isolated_claude_home(tmp_path, monkeypatch):
    """
    Create isolated ~/.claude/ directory for each test.

    Prevents tests from affecting real installation.
    Provides clean state for each test execution.
    """
    fake_home = tmp_path / "test-home"
    fake_home.mkdir()

    fake_claude = fake_home / ".claude"
    fake_claude.mkdir()

    monkeypatch.setenv("HOME", str(fake_home))
    monkeypatch.setenv("NWAVE_HOME", str(fake_claude))

    yield fake_claude

    # Cleanup is automatic via tmp_path fixture


@pytest.fixture
def version_file(isolated_claude_home):
    """
    Fixture for VERSION file within isolated environment.
    """
    version_file_path = isolated_claude_home / "VERSION"
    return version_file_path


@pytest.fixture
def watermark_file(isolated_claude_home):
    """
    Fixture for nwave.update watermark file.
    """
    watermark_path = isolated_claude_home / "nwave.update"
    return watermark_path


@pytest.fixture
def cli_result():
    """
    Container for CLI execution results.
    """
    return {
        "stdout": "",
        "stderr": "",
        "returncode": 0,
        "exception": None,
    }


@pytest.fixture
def mock_github_api():
    """
    Mock GitHub API responses for testing.

    Attributes:
        latest_version: Version returned by the API
        is_reachable: Whether the API is reachable (for offline testing)
        rate_limited: Whether to simulate rate limiting
    """
    return {
        "latest_version": None,
        "is_reachable": True,
        "rate_limited": False,
    }


# ============================================================================
# CLI Execution Utilities
# ============================================================================


@pytest.fixture
def cli_environment(isolated_claude_home, monkeypatch):
    """
    Environment variables for CLI execution.
    """
    env = os.environ.copy()
    env["NWAVE_HOME"] = str(isolated_claude_home)
    env["HOME"] = str(isolated_claude_home.parent)
    return env
