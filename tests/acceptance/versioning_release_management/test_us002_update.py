"""
Acceptance tests for US-002: Update nWave to Latest Release.

Step 04-01: Successful update with backup creation

CRITICAL: Hexagonal boundary enforcement - tests invoke CLI entry points ONLY.
- FORBIDDEN: Direct imports of nWave.core.* components
- REQUIRED: Invoke through driving ports (CLI entry points)

Feature file: docs/features/versioning-release-management/distill/acceptance-tests.feature
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
            nwave.update (watermark file)
            agents/nw/
            commands/nw/
    """
    claude_dir = tmp_path / ".claude"
    claude_dir.mkdir(parents=True)
    (claude_dir / "agents" / "nw").mkdir(parents=True)
    (claude_dir / "commands" / "nw").mkdir(parents=True)

    return {
        "tmp_path": tmp_path,
        "claude_dir": claude_dir,
        "version_file": claude_dir / "VERSION",
        "watermark_file": claude_dir / "nwave.update",
    }


@pytest.fixture
def scenario_context():
    """Shared context between steps."""
    return {}


@pytest.fixture
def cli_result():
    """Shared dictionary for CLI command execution results."""
    return {"stdout": "", "stderr": "", "returncode": None, "exception": None}


@pytest.fixture
def mock_github_response():
    """Mock GitHub API response configuration."""
    return {
        "latest_version": None,
        "checksum": None,
        "download_url": None,
        "is_reachable": True,
        "rate_limited": False,
    }


@pytest.fixture
def mock_download_server():
    """Mock download server configuration."""
    return {
        "release_content": b"mock release content for v1.3.0",
        "checksum": "abc123def456",
        "is_available": True,
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
def update_cli_path(project_root):
    """Path to the update CLI entry point."""
    return project_root / "nWave" / "cli" / "update_cli.py"


@pytest.fixture
def run_update_command(
    clean_test_environment,
    cli_environment,
    update_cli_path,
    mock_github_response,
    mock_download_server,
):
    """
    Factory fixture for running update command through CLI.

    Returns a function that executes the CLI and captures results.
    """

    def _run(confirm_update: bool = True):
        env = cli_environment.copy()

        # Inject mock GitHub response via environment
        if mock_github_response["latest_version"]:
            env["NWAVE_MOCK_GITHUB_VERSION"] = mock_github_response["latest_version"]
        if mock_github_response["checksum"]:
            env["NWAVE_MOCK_GITHUB_CHECKSUM"] = mock_github_response["checksum"]
        if mock_github_response["download_url"]:
            env["NWAVE_MOCK_DOWNLOAD_URL"] = mock_github_response["download_url"]
        env["NWAVE_MOCK_GITHUB_REACHABLE"] = str(
            mock_github_response["is_reachable"]
        ).lower()

        # Inject mock download server config
        env["NWAVE_MOCK_DOWNLOAD_CHECKSUM"] = mock_download_server["checksum"]
        env["NWAVE_MOCK_DOWNLOAD_AVAILABLE"] = str(
            mock_download_server["is_available"]
        ).lower()

        # Inject confirmation response
        env["NWAVE_MOCK_CONFIRM_UPDATE"] = "y" if confirm_update else "n"

        try:
            result = subprocess.run(
                [sys.executable, str(update_cli_path)],
                capture_output=True,
                text=True,
                timeout=30,
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
                "stderr": f"CLI not found: {update_cli_path}",
                "returncode": 1,
                "exception": e,
            }

    return _run


# ============================================================================
# Step 04-01: Successful update with backup creation
# ============================================================================


@pytest.mark.usefixtures("clean_test_environment")
def test_successful_update_with_backup_creation(
    clean_test_environment,
    mock_github_response,
    mock_download_server,
    run_update_command,
    cli_result,
    scenario_context,
):
    """
    Scenario: Successful update with backup creation (line 112)

    Given Giulia has nWave v1.2.3 installed in the test ~/.claude/ directory
    And the GitHub API returns v1.3.0 as the latest release with SHA256 checksum "abc123def456"
    And the download server provides a valid release asset matching the checksum
    When Giulia runs the /nw:update command through the CLI entry point
    And she confirms the update when prompted
    Then a full backup is created at ~/.claude.backup.{timestamp}/
    And the release asset is downloaded from the mock server
    And the download is validated against SHA256 checksum "abc123def456"
    And nWave is updated to v1.3.0 in the test ~/.claude/ directory
    And the VERSION file now contains "1.3.0"
    And the output displays "Update complete."
    """
    # GIVEN: Giulia has nWave v1.2.3 installed
    scenario_context["persona"] = "Giulia"
    scenario_context["installed_version"] = "1.2.3"
    clean_test_environment["version_file"].write_text("1.2.3")
    assert clean_test_environment["version_file"].read_text().strip() == "1.2.3"

    # AND: GitHub API returns v1.3.0 as latest release with SHA256 checksum
    mock_github_response["latest_version"] = "1.3.0"
    mock_github_response["checksum"] = "abc123def456"
    mock_github_response["download_url"] = "https://mock.github.com/releases/v1.3.0.tar.gz"

    # AND: Download server provides valid release asset matching checksum
    mock_download_server["checksum"] = "abc123def456"
    mock_download_server["is_available"] = True

    # WHEN: Giulia runs /nw:update command and confirms
    result = run_update_command(confirm_update=True)
    cli_result.update(result)

    # Diagnostic output for debugging
    stdout = cli_result["stdout"]
    stderr = cli_result["stderr"]
    returncode = cli_result["returncode"]

    diagnostic = (
        f"\nCLI Execution Result:\n"
        f"STDOUT: {stdout!r}\n"
        f"STDERR: {stderr!r}\n"
        f"Return code: {returncode}"
    )

    # THEN: A full backup is created at ~/.claude.backup.{timestamp}/
    parent_dir = clean_test_environment["claude_dir"].parent
    backups = list(parent_dir.glob(".claude.backup.*"))
    assert len(backups) >= 1, f"No backup created. {diagnostic}"

    # AND: The VERSION file now contains "1.3.0"
    version_content = clean_test_environment["version_file"].read_text().strip()
    assert version_content == "1.3.0", (
        f"VERSION file should contain '1.3.0', got '{version_content}'. {diagnostic}"
    )

    # AND: Output displays "Update complete."
    expected_output = "Update complete."
    assert expected_output in stdout, (
        f"Expected '{expected_output}' not found in output. {diagnostic}"
    )

    # AND: Exit code is 0 (success)
    assert returncode == 0, f"Expected exit code 0, got {returncode}. {diagnostic}"
