"""
pytest-bdd configuration for version-update-experience acceptance tests.

This file provides:
1. Test fixtures for isolation and dependency injection
2. pytest-bdd configuration and hooks
3. Shared test utilities

CRITICAL: All fixtures support hexagonal boundary enforcement.
Tests interact with the system through CLI entry points (driving ports) only.
"""

import pytest
from pathlib import Path
import os


# ============================================================================
# pytest-bdd Configuration
# ============================================================================


def pytest_bdd_step_error(
    request, feature, scenario, step, step_func, step_func_args, exception
):
    """
    Custom error handler for BDD step failures.
    Provides detailed context for debugging.
    """
    print(f"\n{'=' * 70}")
    print("BDD Step Failure:")
    print(f"  Feature: {feature.name}")
    print(f"  Scenario: {scenario.name}")
    print(f"  Step: {step.keyword} {step.name}")
    print(f"  Exception: {type(exception).__name__}: {exception}")
    print(f"{'=' * 70}\n")


# ============================================================================
# Test Isolation Fixtures
# ============================================================================


@pytest.fixture(scope="function")
def isolated_home(tmp_path, monkeypatch):
    """
    Create isolated HOME directory for each test.

    Prevents tests from affecting real ~/.claude/ installation.
    Provides clean state for each test execution.
    """
    # Create isolated .claude directory
    fake_home = tmp_path / "test-home"
    fake_home.mkdir()

    fake_claude = fake_home / ".claude"
    fake_claude.mkdir()

    # Set HOME environment variable
    monkeypatch.setenv("HOME", str(fake_home))

    yield fake_home

    # Cleanup is automatic via tmp_path fixture


@pytest.fixture(scope="function")
def clean_environment(monkeypatch):
    """
    Clean environment variables for test isolation.

    Removes environment variables that might affect test behavior.
    """
    # Clear potentially interfering environment variables
    env_vars_to_clear = [
        "NWAVE_BACKUP_RETENTION_DAYS",
        "NWAVE_GITHUB_API_TIMEOUT",
        "NWAVE_UPDATE_LOG_LEVEL",
        "NWAVE_LOCK_TIMEOUT_HOURS",
    ]

    for var in env_vars_to_clear:
        monkeypatch.delenv(var, raising=False)

    yield


# ============================================================================
# CLI Execution Utilities
# ============================================================================


@pytest.fixture
def cli_executor(isolated_home):
    """
    Utility for executing CLI scripts through subprocess.

    CRITICAL: This enforces hexagonal boundary - all tests execute
    through CLI entry points, never importing core domain directly.
    """

    def execute_cli(script_path: Path, env: dict = None, timeout: int = 10):
        """
        Execute CLI script and return result.

        Args:
            script_path: Path to CLI script to execute
            env: Environment variables for execution
            timeout: Timeout in seconds

        Returns:
            dict with stdout, stderr, returncode
        """
        import subprocess

        execution_env = os.environ.copy()
        if env:
            execution_env.update(env)

        try:
            result = subprocess.run(
                ["python3", str(script_path)],
                capture_output=True,
                text=True,
                timeout=timeout,
                env=execution_env,
                cwd=str(isolated_home),
            )

            return {
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode,
                "exception": None,
            }

        except subprocess.TimeoutExpired as e:
            return {
                "stdout": "",
                "stderr": f"Command timed out after {timeout} seconds",
                "returncode": 124,
                "exception": e,
            }

        except Exception as e:
            return {"stdout": "", "stderr": str(e), "returncode": 1, "exception": e}

    return execute_cli


# ============================================================================
# Test Data Builders
# ============================================================================


@pytest.fixture
def version_file_builder(isolated_home):
    """
    Builder for creating VERSION files with specific content.

    Usage:
        version_file_builder.create("1.5.7")
        version_file_builder.create("2.0.0", location=custom_path)
    """

    class VersionFileBuilder:
        def __init__(self, home_dir):
            self.home_dir = home_dir
            self.default_location = home_dir / ".claude" / "nwave-version.txt"

        def create(self, version: str, location: Path = None):
            """Create VERSION file with specified version."""
            target = location or self.default_location
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(version)
            return target

        def read(self, location: Path = None):
            """Read VERSION file content."""
            target = location or self.default_location
            if target.exists():
                return target.read_text().strip()
            return None

    return VersionFileBuilder(isolated_home)


@pytest.fixture
def backup_builder(isolated_home):
    """
    Builder for creating backup directories for testing.

    Usage:
        backup_builder.create("20260123")
        backup_builder.create("20251201", age_days=40)
    """

    class BackupBuilder:
        def __init__(self, home_dir):
            self.home_dir = home_dir

        def create(self, date_str: str, age_days: int = 0, sequence: int = 0):
            """
            Create backup directory with optional sequence number and age.

            Args:
                date_str: Date in YYYYMMDD format
                age_days: Age in days (sets modification time)
                sequence: Sequence number (0 = no sequence, 1+ = append _NN)
            """
            if sequence > 0:
                backup_name = f".claude_bck_{date_str}_{sequence:02d}"
            else:
                backup_name = f".claude_bck_{date_str}"

            backup_path = self.home_dir / backup_name
            backup_path.mkdir(parents=True, exist_ok=True)

            # Set modification time if age specified
            if age_days > 0:
                import time

                old_time = time.time() - (age_days * 24 * 60 * 60)
                os.utime(backup_path, (old_time, old_time))

            return backup_path

        def list_backups(self):
            """List all backup directories."""
            return sorted(self.home_dir.glob(".claude_bck_*"))

        def count_backups(self):
            """Count backup directories."""
            return len(list(self.home_dir.glob(".claude_bck_*")))

    return BackupBuilder(isolated_home)


# ============================================================================
# Mock Infrastructure
# ============================================================================


@pytest.fixture
def mock_installer():
    """
    Mock for existing install_nwave.py script.

    In production, UpdateDownloadOrchestrator delegates to install_nwave.py.
    For tests, we mock this delegation point.
    """

    class MockInstaller:
        def __init__(self):
            self.called = False
            self.call_count = 0
            self.exit_code = 0
            self.backup_created = False

        def simulate_call(self, exit_code: int = 0):
            """Simulate installer invocation."""
            self.called = True
            self.call_count += 1
            self.exit_code = exit_code
            return exit_code

    return MockInstaller()


# ============================================================================
# Assertion Helpers
# ============================================================================


@pytest.fixture
def assert_cli_output():
    """Helper for asserting CLI output patterns."""

    class OutputAssertions:
        @staticmethod
        def contains(output: str, expected: str, message: str = None):
            """Assert output contains expected text."""
            assert expected in output, (
                message or f"Expected '{expected}' not found in output:\n{output}"
            )

        @staticmethod
        def matches_pattern(output: str, pattern: str, message: str = None):
            """Assert output matches regex pattern."""
            import re

            assert re.search(pattern, output), (
                message or f"Pattern '{pattern}' not found in output:\n{output}"
            )

        @staticmethod
        def exit_code_is(result: dict, expected_code: int, message: str = None):
            """Assert command exit code."""
            actual = result["returncode"]
            assert actual == expected_code, (
                message
                or f"Expected exit code {expected_code}, got {actual}\nSTDERR: {result['stderr']}"
            )

    return OutputAssertions()


# ============================================================================
# Performance Testing Support
# ============================================================================


@pytest.fixture
def performance_timer():
    """Timer for performance assertions."""
    import time

    class PerformanceTimer:
        def __init__(self):
            self.start_time = None
            self.end_time = None

        def start(self):
            """Start timing."""
            self.start_time = time.time()

        def stop(self):
            """Stop timing."""
            self.end_time = time.time()

        def elapsed_seconds(self):
            """Get elapsed time in seconds."""
            if self.start_time and self.end_time:
                return self.end_time - self.start_time
            return None

        def assert_completed_within(self, max_seconds: float, message: str = None):
            """Assert operation completed within time limit."""
            elapsed = self.elapsed_seconds()
            assert elapsed is not None, "Timer not started or stopped"
            assert elapsed <= max_seconds, (
                message or f"Operation took {elapsed:.2f}s, expected <{max_seconds}s"
            )

    return PerformanceTimer()


# ============================================================================
# Logging and Debugging
# ============================================================================


@pytest.fixture(autouse=True)
def test_logging(request, caplog):
    """
    Automatic logging for all tests.

    Captures and displays logs on test failure.
    """
    import logging

    caplog.set_level(logging.DEBUG)

    yield

    # On failure, print captured logs
    if request.node.rep_call.failed if hasattr(request.node, "rep_call") else False:
        print("\n" + "=" * 70)
        print("Captured Logs:")
        print("=" * 70)
        for record in caplog.records:
            print(f"{record.levelname}: {record.message}")
        print("=" * 70)


# ============================================================================
# pytest Hooks
# ============================================================================


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    Store test result on test item for access in fixtures.

    Allows fixtures to check if test failed and provide additional context.
    """
    outcome = yield
    rep = outcome.get_result()

    # Store report on item for access in fixtures
    setattr(item, f"rep_{rep.when}", rep)


# ============================================================================
# Custom Markers
# ============================================================================


def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers",
        "integration: marks tests as integration tests requiring external services",
    )
    config.addinivalue_line(
        "markers",
        "hexagonal_boundary: marks tests that enforce hexagonal architecture boundaries",
    )
