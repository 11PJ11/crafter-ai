"""
Step definitions for US-004: Install Built Distribution acceptance tests.

CRITICAL: Hexagonal boundary enforcement - tests invoke CLI entry points ONLY.
- FORBIDDEN: Direct imports of nWave.core.* components
- REQUIRED: Invoke through driving ports (CLI entry points)

Feature file: docs/features/versioning-release-management/distill/acceptance-tests.feature
Scenario: Successful installation with smoke test (line 339)
"""

import os
import subprocess
import sys
from pathlib import Path

import pytest


@pytest.fixture
def clean_test_environment(tmp_path):
    """
    Create isolated test environment with ~/.claude/ directory and dist/ directory.

    Structure:
    tmp_path/
        .claude/
            agents/nw/
            commands/nw/
            VERSION
        repo/
            dist/
                agents/nw/
                commands/nw/
                VERSION
    """
    # Create target ~/.claude/ directory structure
    claude_dir = tmp_path / ".claude"
    claude_dir.mkdir(parents=True)
    (claude_dir / "agents" / "nw").mkdir(parents=True)
    (claude_dir / "commands" / "nw").mkdir(parents=True)

    # Create repository directory with dist/
    repo_dir = tmp_path / "repo"
    repo_dir.mkdir(parents=True)
    dist_dir = repo_dir / "dist"
    dist_dir.mkdir(parents=True)

    return {
        "tmp_path": tmp_path,
        "claude_dir": claude_dir,
        "repo_dir": repo_dir,
        "dist_dir": dist_dir,
        "version_file": claude_dir / "VERSION",
    }


@pytest.fixture
def valid_dist_structure(clean_test_environment):
    """
    Create a valid dist/ directory with all required nWave structure.

    Structure matches what /nw:forge would produce.
    """
    dist_dir = clean_test_environment["dist_dir"]

    # Create VERSION file in dist
    version_file = dist_dir / "VERSION"
    version_file.write_text("1.2.3-rc.main.20260127.1")

    # Create agents/nw/ directory with sample agent
    agents_nw = dist_dir / "agents" / "nw"
    agents_nw.mkdir(parents=True, exist_ok=True)
    (agents_nw / "software-crafter.md").write_text("# Software Crafter Agent\nversion: 1.2.3-rc.main.20260127.1")

    # Create commands/nw/ directory with sample command
    commands_nw = dist_dir / "commands" / "nw"
    commands_nw.mkdir(parents=True, exist_ok=True)
    (commands_nw / "version.md").write_text("# Version Command\nversion: 1.2.3-rc.main.20260127.1")

    return clean_test_environment


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
    env["NWAVE_DIST_DIR"] = str(clean_test_environment["dist_dir"])
    env["NWAVE_TEST_MODE"] = "true"

    # Add project root to PYTHONPATH so nWave module can be imported
    existing_pythonpath = env.get("PYTHONPATH", "")
    if existing_pythonpath:
        env["PYTHONPATH"] = f"{project_root}:{existing_pythonpath}"
    else:
        env["PYTHONPATH"] = str(project_root)

    return env


@pytest.fixture
def forge_install_cli_path(project_root):
    """Path to the forge install CLI entry point."""
    return project_root / "nWave" / "cli" / "forge_install_cli.py"


@pytest.fixture
def run_forge_install_command(clean_test_environment, cli_environment, forge_install_cli_path):
    """
    Factory fixture for running forge install command through CLI.

    Returns a function that executes the CLI and captures results.
    """

    def _run():
        try:
            result = subprocess.run(
                [sys.executable, str(forge_install_cli_path)],
                capture_output=True,
                text=True,
                timeout=30,  # Longer timeout since smoke test runs version CLI
                env=cli_environment,
                cwd=str(clean_test_environment["repo_dir"]),
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
                "stderr": f"CLI not found: {forge_install_cli_path}",
                "returncode": 1,
                "exception": e,
            }

    return _run


# ============================================================================
# Test: Successful installation with smoke test (Step 06-01)
# ============================================================================


@pytest.mark.usefixtures("valid_dist_structure")
def test_successful_installation_with_smoke_test(
    valid_dist_structure,
    run_forge_install_command,
    cli_environment,
):
    """
    Scenario: Successful installation with smoke test

    Given Elena has a valid dist/ directory from a previous /nw:forge build
    And the dist/ directory contains all required nWave structure
    And the dist/ VERSION file contains "1.2.3-rc.main.20260127.1"
    When Elena runs the /nw:forge:install command through the CLI entry point
    Then the contents of dist/ are copied to the test ~/.claude/ directory
    And nWave-prefixed content in ~/.claude/agents/nw/ is replaced
    And nWave-prefixed content in ~/.claude/commands/nw/ is replaced
    And the smoke test runs /nw:version successfully
    And the success message displays "Installation complete."
    """
    env = valid_dist_structure
    claude_dir = env["claude_dir"]
    dist_dir = env["dist_dir"]

    # GIVEN: Elena has a valid dist/ directory
    assert dist_dir.exists(), "dist/ directory should exist"
    assert (dist_dir / "VERSION").exists(), "dist/VERSION should exist"
    assert (dist_dir / "VERSION").read_text() == "1.2.3-rc.main.20260127.1"
    assert (dist_dir / "agents" / "nw").exists(), "dist/agents/nw/ should exist"
    assert (dist_dir / "commands" / "nw").exists(), "dist/commands/nw/ should exist"

    # WHEN: Elena runs /nw:forge:install command
    result = run_forge_install_command()

    # THEN: Assertions
    stdout = result["stdout"]
    stderr = result["stderr"]
    returncode = result["returncode"]

    diagnostic = (
        f"Installation failed:\n"
        f"STDOUT: {stdout!r}\n"
        f"STDERR: {stderr!r}\n"
        f"Return code: {returncode}"
    )

    # Contents of dist/ are copied to the test ~/.claude/ directory
    installed_version = claude_dir / "VERSION"
    assert installed_version.exists(), f"VERSION file not copied. {diagnostic}"
    assert installed_version.read_text() == "1.2.3-rc.main.20260127.1", f"VERSION mismatch. {diagnostic}"

    # nWave-prefixed content in ~/.claude/agents/nw/ is replaced
    agents_nw = claude_dir / "agents" / "nw" / "software-crafter.md"
    assert agents_nw.exists(), f"agents/nw/ content not installed. {diagnostic}"

    # nWave-prefixed content in ~/.claude/commands/nw/ is replaced
    commands_nw = claude_dir / "commands" / "nw" / "version.md"
    assert commands_nw.exists(), f"commands/nw/ content not installed. {diagnostic}"

    # Success message displays "Installation complete."
    assert "Installation complete." in stdout, f"Success message not found. {diagnostic}"

    # CLI should return success (exit code 0)
    assert returncode == 0, f"Expected exit code 0, got {returncode}. {diagnostic}"
