"""
pytest-bdd configuration for versioning-release-management acceptance tests.

CRITICAL: All fixtures support hexagonal boundary enforcement.
Tests interact with the system through CLI entry points (driving ports) only.
"""

import os
import subprocess
import sys
from pathlib import Path

import pytest


@pytest.fixture
def clean_test_environment(tmp_path):
    """
    Create isolated test environment with ~/.claude/ directory.

    Structure:
    tmp_path/
        .claude/
            VERSION
            nwave.update (watermark file, created by tests)
    """
    claude_dir = tmp_path / ".claude"
    claude_dir.mkdir(parents=True)

    return {
        "tmp_path": tmp_path,
        "claude_dir": claude_dir,
        "version_file": claude_dir / "VERSION",
        "watermark_file": claude_dir / "nwave.update",
    }


@pytest.fixture
def cli_result():
    """Shared dictionary for CLI command execution results."""
    return {"stdout": "", "stderr": "", "returncode": None, "exception": None}


@pytest.fixture
def mock_github_response():
    """Mock GitHub API response configuration."""
    return {
        "latest_version": None,
        "is_reachable": True,
        "rate_limited": False,
    }


@pytest.fixture
def project_root():
    """Get the project root directory."""
    return Path(__file__).parent.parent.parent.parent


@pytest.fixture
def cli_environment(clean_test_environment, project_root):
    """
    Environment variables for CLI execution.

    CRITICAL: Start from os.environ.copy() to inherit system environment.
    CRITICAL: Include project root in PYTHONPATH for nWave module resolution.
    """
    env = os.environ.copy()
    env["NWAVE_HOME"] = str(clean_test_environment["claude_dir"])
    env["NWAVE_TEST_MODE"] = "true"

    # Add project root to PYTHONPATH so nWave module can be imported
    existing_pythonpath = env.get("PYTHONPATH", "")
    if existing_pythonpath:
        env["PYTHONPATH"] = f"{project_root}:{existing_pythonpath}"
    else:
        env["PYTHONPATH"] = str(project_root)

    return env


@pytest.fixture
def version_cli_path(project_root):
    """Path to the version CLI entry point."""
    return project_root / "nWave" / "cli" / "version_cli.py"


@pytest.fixture
def run_version_command(clean_test_environment, cli_environment, version_cli_path, mock_github_response):
    """
    Factory fixture for running version command through CLI.

    Returns a function that executes the CLI and captures results.
    """

    def _run():
        env = cli_environment.copy()

        # Inject mock GitHub response via environment
        if mock_github_response["latest_version"]:
            env["NWAVE_MOCK_GITHUB_VERSION"] = mock_github_response["latest_version"]
        env["NWAVE_MOCK_GITHUB_REACHABLE"] = str(mock_github_response["is_reachable"]).lower()
        env["NWAVE_MOCK_GITHUB_RATE_LIMITED"] = str(mock_github_response["rate_limited"]).lower()

        try:
            result = subprocess.run(
                [sys.executable, str(version_cli_path)],
                capture_output=True,
                text=True,
                timeout=10,
                env=env,
                cwd=str(clean_test_environment["tmp_path"]),
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
                "stderr": "Command timed out",
                "returncode": 124,
                "exception": e,
            }
        except FileNotFoundError as e:
            return {
                "stdout": "",
                "stderr": f"CLI not found: {version_cli_path}",
                "returncode": 1,
                "exception": e,
            }

    return _run
