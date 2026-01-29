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
    (agents_nw / "software-crafter.md").write_text(
        "# Software Crafter Agent\nversion: 1.2.3-rc.main.20260127.1"
    )

    # Create commands/nw/ directory with sample command
    commands_nw = dist_dir / "commands" / "nw"
    commands_nw.mkdir(parents=True, exist_ok=True)
    (commands_nw / "version.md").write_text(
        "# Version Command\nversion: 1.2.3-rc.main.20260127.1"
    )

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
def run_forge_install_command(
    clean_test_environment, cli_environment, forge_install_cli_path
):
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
    assert (
        installed_version.read_text() == "1.2.3-rc.main.20260127.1"
    ), f"VERSION mismatch. {diagnostic}"

    # nWave-prefixed content in ~/.claude/agents/nw/ is replaced
    agents_nw = claude_dir / "agents" / "nw" / "software-crafter.md"
    assert agents_nw.exists(), f"agents/nw/ content not installed. {diagnostic}"

    # nWave-prefixed content in ~/.claude/commands/nw/ is replaced
    commands_nw = claude_dir / "commands" / "nw" / "version.md"
    assert commands_nw.exists(), f"commands/nw/ content not installed. {diagnostic}"

    # Success message displays "Installation complete."
    assert (
        "Installation complete." in stdout
    ), f"Success message not found. {diagnostic}"

    # CLI should return success (exit code 0)
    assert returncode == 0, f"Expected exit code 0, got {returncode}. {diagnostic}"


# ============================================================================
# Test: Installation preserves non-nWave user content (Step 06-02)
# ============================================================================


@pytest.fixture
def user_content_with_valid_dist(valid_dist_structure):
    """
    Create user content in ~/.claude/ that should be preserved during installation.

    User content includes:
    - Custom agent at ~/.claude/agents/my-agent/
    - Custom command at ~/.claude/commands/my-command/
    """
    env = valid_dist_structure
    claude_dir = env["claude_dir"]

    # Create custom user agent (should be preserved)
    user_agent_dir = claude_dir / "agents" / "my-agent"
    user_agent_dir.mkdir(parents=True, exist_ok=True)
    user_agent_file = user_agent_dir / "agent.md"
    user_agent_file.write_text(
        "# My Custom Agent\nThis is Elena's custom agent that should be preserved."
    )

    # Create custom user command (should be preserved)
    user_command_dir = claude_dir / "commands" / "my-command"
    user_command_dir.mkdir(parents=True, exist_ok=True)
    user_command_file = user_command_dir / "command.md"
    user_command_file.write_text(
        "# My Custom Command\nThis is Elena's custom command that should be preserved."
    )

    return env


@pytest.mark.usefixtures("user_content_with_valid_dist")
def test_installation_preserves_non_nwave_user_content(
    user_content_with_valid_dist,
    run_forge_install_command,
    cli_environment,
):
    """
    Scenario: Installation preserves non-nWave user content

    Given Elena has a valid dist/ directory from a previous /nw:forge build
    And she has custom agents in ~/.claude/agents/my-agent/
    And she has custom commands in ~/.claude/commands/my-command/
    When Elena runs the /nw:forge:install command through the CLI entry point
    Then her custom agent at ~/.claude/agents/my-agent/ remains untouched
    And her custom command at ~/.claude/commands/my-command/ remains untouched

    CRITICAL: This test validates that user content (non-nw/ prefixed) is PRESERVED
    during installation, while nWave content (nw/ prefixed) is REPLACED.
    """
    env = user_content_with_valid_dist
    claude_dir = env["claude_dir"]
    dist_dir = env["dist_dir"]

    # GIVEN: Elena has a valid dist/ directory
    assert dist_dir.exists(), "dist/ directory should exist"
    assert (dist_dir / "VERSION").exists(), "dist/VERSION should exist"

    # GIVEN: She has custom agents in ~/.claude/agents/my-agent/
    user_agent_file = claude_dir / "agents" / "my-agent" / "agent.md"
    assert user_agent_file.exists(), "User agent should exist before installation"
    original_agent_content = user_agent_file.read_text()
    assert "Elena's custom agent" in original_agent_content

    # GIVEN: She has custom commands in ~/.claude/commands/my-command/
    user_command_file = claude_dir / "commands" / "my-command" / "command.md"
    assert user_command_file.exists(), "User command should exist before installation"
    original_command_content = user_command_file.read_text()
    assert "Elena's custom command" in original_command_content

    # WHEN: Elena runs /nw:forge:install command
    result = run_forge_install_command()

    # Diagnostic info for debugging
    stdout = result["stdout"]
    stderr = result["stderr"]
    returncode = result["returncode"]

    diagnostic = (
        f"Installation result:\n"
        f"STDOUT: {stdout!r}\n"
        f"STDERR: {stderr!r}\n"
        f"Return code: {returncode}"
    )

    # THEN: Her custom agent at ~/.claude/agents/my-agent/ remains untouched
    assert user_agent_file.exists(), f"User agent was deleted! {diagnostic}"
    preserved_agent_content = user_agent_file.read_text()
    assert preserved_agent_content == original_agent_content, (
        f"User agent content was modified!\n"
        f"Expected: {original_agent_content!r}\n"
        f"Got: {preserved_agent_content!r}\n"
        f"{diagnostic}"
    )

    # THEN: Her custom command at ~/.claude/commands/my-command/ remains untouched
    assert user_command_file.exists(), f"User command was deleted! {diagnostic}"
    preserved_command_content = user_command_file.read_text()
    assert preserved_command_content == original_command_content, (
        f"User command content was modified!\n"
        f"Expected: {original_command_content!r}\n"
        f"Got: {preserved_command_content!r}\n"
        f"{diagnostic}"
    )

    # ALSO VERIFY: nWave content WAS installed (both behaviors work together)
    nw_agent = claude_dir / "agents" / "nw" / "software-crafter.md"
    assert nw_agent.exists(), f"nWave agent should be installed. {diagnostic}"

    nw_command = claude_dir / "commands" / "nw" / "version.md"
    assert nw_command.exists(), f"nWave command should be installed. {diagnostic}"

    # Installation should succeed
    assert returncode == 0, f"Expected exit code 0. {diagnostic}"


# ============================================================================
# Test: Installation fails when dist/ is missing required files (Step 06-04)
# ============================================================================


@pytest.fixture
def empty_dist_structure(clean_test_environment):
    """
    Create a dist/ directory that exists but is empty (missing required files).

    This simulates the error condition where dist/ exists but lacks the
    required nWave structure (VERSION, agents/nw/, commands/nw/).
    """
    # dist_dir is already created by clean_test_environment
    # It exists but is empty - no VERSION, no agents/nw/, no commands/nw/
    return clean_test_environment


def test_installation_fails_when_dist_missing_required_files(
    empty_dist_structure,
    run_forge_install_command,
):
    """
    Scenario: Installation fails when dist/ is missing required files

    Given Greta has a dist/ directory that is missing required files
    And the dist/ directory exists but is empty
    When Greta runs the /nw:forge:install command through the CLI entry point
    Then the error displays "Invalid distribution: missing required files. Rebuild with /nw:forge."
    And the test ~/.claude/ directory is unchanged
    And the CLI exit code is non-zero
    """
    env = empty_dist_structure
    claude_dir = env["claude_dir"]
    dist_dir = env["dist_dir"]

    # GIVEN: Greta has a dist/ directory that exists but is empty
    assert dist_dir.exists(), "dist/ directory should exist"
    assert not (
        dist_dir / "VERSION"
    ).exists(), "dist/VERSION should NOT exist (empty dist)"
    assert not list(dist_dir.iterdir()), "dist/ should be empty"

    # Capture initial state of ~/.claude/ to verify it's unchanged
    initial_claude_contents = set()
    for item in claude_dir.rglob("*"):
        if item.is_file():
            initial_claude_contents.add(
                (str(item.relative_to(claude_dir)), item.read_text())
            )

    # WHEN: Greta runs /nw:forge:install command
    result = run_forge_install_command()

    # THEN: Assertions
    stdout = result["stdout"]
    stderr = result["stderr"]
    returncode = result["returncode"]

    diagnostic = (
        f"Expected installation to fail:\n"
        f"STDOUT: {stdout!r}\n"
        f"STDERR: {stderr!r}\n"
        f"Return code: {returncode}"
    )

    # Error displays "Invalid distribution: missing required files. Rebuild with /nw:forge."
    expected_error = (
        "Invalid distribution: missing required files. Rebuild with /nw:forge."
    )
    assert (
        expected_error in stderr
    ), f"Expected error message not found in stderr. {diagnostic}"

    # CLI exit code is non-zero
    assert (
        returncode != 0
    ), f"Expected non-zero exit code, got {returncode}. {diagnostic}"

    # Test ~/.claude/ directory is unchanged
    final_claude_contents = set()
    for item in claude_dir.rglob("*"):
        if item.is_file():
            final_claude_contents.add(
                (str(item.relative_to(claude_dir)), item.read_text())
            )

    assert initial_claude_contents == final_claude_contents, (
        f"~/.claude/ directory was modified.\n"
        f"Initial: {initial_claude_contents}\n"
        f"Final: {final_claude_contents}\n"
        f"{diagnostic}"
    )


# ============================================================================
# Test: Smoke test failure reports error (Step 06-05)
# ============================================================================


@pytest.fixture
def corrupted_dist_structure(clean_test_environment):
    """
    Create a dist/ directory with corrupted files that will cause smoke test to fail.

    The VERSION file exists but version_cli.py will fail when run against this
    installation because the installed content is corrupted/invalid.
    """
    dist_dir = clean_test_environment["dist_dir"]

    # Create VERSION file in dist (valid so installation proceeds)
    version_file = dist_dir / "VERSION"
    version_file.write_text("1.2.3-rc.main.20260127.1")

    # Create agents/nw/ directory with corrupted agent file
    # (smoke test will fail because version command expects certain structure)
    agents_nw = dist_dir / "agents" / "nw"
    agents_nw.mkdir(parents=True, exist_ok=True)
    (agents_nw / "software-crafter.md").write_text("CORRUPTED CONTENT - INVALID YAML")

    # Create commands/nw/ directory with corrupted command file
    commands_nw = dist_dir / "commands" / "nw"
    commands_nw.mkdir(parents=True, exist_ok=True)
    (commands_nw / "version.md").write_text("CORRUPTED CONTENT - INVALID YAML")

    return clean_test_environment


@pytest.fixture
def cli_environment_with_forced_smoke_failure(clean_test_environment, project_root):
    """
    Environment variables for CLI execution with forced smoke test failure.

    Sets NWAVE_FORCE_SMOKE_FAILURE=true to simulate corrupted installation.
    """
    env = os.environ.copy()
    env["NWAVE_HOME"] = str(clean_test_environment["claude_dir"])
    env["NWAVE_DIST_DIR"] = str(clean_test_environment["dist_dir"])
    env["NWAVE_TEST_MODE"] = "true"
    env["NWAVE_FORCE_SMOKE_FAILURE"] = "true"  # Force smoke test to fail

    # Add project root to PYTHONPATH so nWave module can be imported
    existing_pythonpath = env.get("PYTHONPATH", "")
    if existing_pythonpath:
        env["PYTHONPATH"] = f"{project_root}:{existing_pythonpath}"
    else:
        env["PYTHONPATH"] = str(project_root)

    return env


@pytest.fixture
def run_forge_install_with_smoke_failure(
    clean_test_environment,
    cli_environment_with_forced_smoke_failure,
    forge_install_cli_path,
):
    """
    Factory fixture for running forge install command with forced smoke failure.

    Returns a function that executes the CLI and captures results.
    """

    def _run():
        try:
            result = subprocess.run(
                [sys.executable, str(forge_install_cli_path)],
                capture_output=True,
                text=True,
                timeout=30,
                env=cli_environment_with_forced_smoke_failure,
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


def test_smoke_test_failure_reports_error(
    corrupted_dist_structure,
    run_forge_install_with_smoke_failure,
):
    """
    Scenario: Smoke test failure reports error (Step 06-05)

    Given Elena has a dist/ directory with corrupted files
    And the smoke test for /nw:version will fail
    When Elena runs the /nw:forge:install command through the CLI entry point
    Then installation proceeds
    And the smoke test fails
    And a warning displays "Installation complete but smoke test failed. Verify with /nw:version."
    """
    env = corrupted_dist_structure
    claude_dir = env["claude_dir"]
    dist_dir = env["dist_dir"]

    # GIVEN: Elena has a dist/ directory with corrupted files
    assert dist_dir.exists(), "dist/ directory should exist"
    assert (dist_dir / "VERSION").exists(), "dist/VERSION should exist"

    # WHEN: Elena runs /nw:forge:install command
    result = run_forge_install_with_smoke_failure()

    # THEN: Assertions
    stdout = result["stdout"]
    stderr = result["stderr"]
    returncode = result["returncode"]

    diagnostic = (
        f"Test diagnostics:\n"
        f"STDOUT: {stdout!r}\n"
        f"STDERR: {stderr!r}\n"
        f"Return code: {returncode}"
    )

    # Installation proceeds - files should be copied
    installed_version = claude_dir / "VERSION"
    assert (
        installed_version.exists()
    ), f"VERSION file should be copied despite smoke failure. {diagnostic}"
    assert (
        installed_version.read_text() == "1.2.3-rc.main.20260127.1"
    ), f"VERSION mismatch. {diagnostic}"

    # A warning displays the specific message
    expected_message = (
        "Installation complete but smoke test failed. Verify with /nw:version."
    )
    assert (
        expected_message in stdout
    ), f"Expected warning message not found. {diagnostic}"

    # CLI should still return success (installation completed, just smoke test failed)
    assert returncode == 0, f"Expected exit code 0, got {returncode}. {diagnostic}"


# ============================================================================
# Test: Installation fails when dist/ directory does not exist (Step 06-03)
# ============================================================================


@pytest.fixture
def environment_without_dist(tmp_path, project_root):
    """
    Create isolated test environment WITHOUT dist/ directory.

    Structure:
    tmp_path/
        .claude/
            agents/nw/
            commands/nw/
            VERSION (pre-existing installation)
        repo/
            (NO dist/ directory)
    """
    # Create target ~/.claude/ directory structure with existing installation
    claude_dir = tmp_path / ".claude"
    claude_dir.mkdir(parents=True)
    (claude_dir / "agents" / "nw").mkdir(parents=True)
    (claude_dir / "commands" / "nw").mkdir(parents=True)

    # Add pre-existing VERSION to verify it remains unchanged
    existing_version = claude_dir / "VERSION"
    existing_version.write_text("0.9.0-existing-installation")

    # Add pre-existing agent file to verify it remains unchanged
    existing_agent = claude_dir / "agents" / "nw" / "old-agent.md"
    existing_agent.write_text("# Old Agent - Should Not Be Removed")

    # Create repository directory WITHOUT dist/
    repo_dir = tmp_path / "repo"
    repo_dir.mkdir(parents=True)
    # NOTE: dist_dir is NOT created - this is the test condition

    return {
        "tmp_path": tmp_path,
        "claude_dir": claude_dir,
        "repo_dir": repo_dir,
        "dist_dir": repo_dir / "dist",  # Path exists but directory does not
        "version_file": claude_dir / "VERSION",
        "existing_agent": existing_agent,
    }


@pytest.fixture
def cli_environment_without_dist(environment_without_dist, project_root):
    """
    Environment variables for CLI execution without dist/ directory.
    """
    env = os.environ.copy()
    env["NWAVE_HOME"] = str(environment_without_dist["claude_dir"])
    env["NWAVE_DIST_DIR"] = str(environment_without_dist["dist_dir"])
    env["NWAVE_TEST_MODE"] = "true"

    # Add project root to PYTHONPATH so nWave module can be imported
    existing_pythonpath = env.get("PYTHONPATH", "")
    if existing_pythonpath:
        env["PYTHONPATH"] = f"{project_root}:{existing_pythonpath}"
    else:
        env["PYTHONPATH"] = str(project_root)

    return env


@pytest.fixture
def run_forge_install_without_dist(
    environment_without_dist, cli_environment_without_dist, project_root
):
    """
    Factory fixture for running forge install command when dist/ does not exist.
    """
    forge_install_cli_path = project_root / "nWave" / "cli" / "forge_install_cli.py"

    def _run():
        try:
            result = subprocess.run(
                [sys.executable, str(forge_install_cli_path)],
                capture_output=True,
                text=True,
                timeout=30,
                env=cli_environment_without_dist,
                cwd=str(environment_without_dist["repo_dir"]),
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


def test_installation_fails_when_dist_directory_does_not_exist(
    environment_without_dist,
    run_forge_install_without_dist,
):
    """
    Scenario: Installation fails when dist/ directory does not exist (Step 06-03)

    Given Fabio has no dist/ directory in the repository
    When Fabio runs the /nw:forge:install command through the CLI entry point
    Then the error displays "No distribution found. Run /nw:forge first to build."
    And the test ~/.claude/ directory is unchanged
    And the CLI exit code is non-zero
    """
    env = environment_without_dist
    dist_dir = env["dist_dir"]
    version_file = env["version_file"]
    existing_agent = env["existing_agent"]

    # GIVEN: Fabio has no dist/ directory in the repository
    assert not dist_dir.exists(), "dist/ directory should NOT exist for this test"

    # Capture pre-existing state
    original_version = version_file.read_text()
    original_agent_content = existing_agent.read_text()

    # WHEN: Fabio runs /nw:forge:install command
    result = run_forge_install_without_dist()

    # THEN: Assertions
    stdout = result["stdout"]
    stderr = result["stderr"]
    returncode = result["returncode"]

    diagnostic = (
        f"Test diagnostics:\n"
        f"STDOUT: {stdout!r}\n"
        f"STDERR: {stderr!r}\n"
        f"Return code: {returncode}"
    )

    # The error displays the expected message
    expected_error = "No distribution found. Run /nw:forge first to build."
    assert (
        expected_error in stderr
    ), f"Expected error message not found in stderr. {diagnostic}"

    # The test ~/.claude/ directory is unchanged
    assert version_file.read_text() == original_version, (
        f"VERSION file should not change. Original: {original_version!r}, "
        f"Current: {version_file.read_text()!r}. {diagnostic}"
    )
    assert (
        existing_agent.read_text() == original_agent_content
    ), f"Existing agent file should not change. {diagnostic}"

    # The CLI exit code is non-zero
    assert (
        returncode != 0
    ), f"Expected non-zero exit code, got {returncode}. {diagnostic}"
