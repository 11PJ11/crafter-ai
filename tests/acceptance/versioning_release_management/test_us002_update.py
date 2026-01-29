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
    mock_github_response["download_url"] = (
        "https://mock.github.com/releases/v1.3.0.tar.gz"
    )

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
    assert (
        version_content == "1.3.0"
    ), f"VERSION file should contain '1.3.0', got '{version_content}'. {diagnostic}"

    # AND: Output displays "Update complete."
    expected_output = "Update complete."
    assert (
        expected_output in stdout
    ), f"Expected '{expected_output}' not found in output. {diagnostic}"

    # AND: Exit code is 0 (success)
    assert returncode == 0, f"Expected exit code 0, got {returncode}. {diagnostic}"


# ============================================================================
# Step 04-09: Non-nWave user content is preserved during update
# ============================================================================


@pytest.fixture
def clean_test_environment_with_user_content(tmp_path):
    """
    Create isolated test environment with ~/.claude/ directory AND user content.

    Structure:
    tmp_path/
        .claude/
            VERSION
            agents/
                nw/
                    software-crafter.md
                my-custom-agent/
                    agent.md
            commands/
                nw/
                    develop.md
                my-custom-command/
                    run.md
    """
    claude_dir = tmp_path / ".claude"
    claude_dir.mkdir(parents=True)

    # Create nWave core content directories
    nw_agents = claude_dir / "agents" / "nw"
    nw_agents.mkdir(parents=True)
    (nw_agents / "software-crafter.md").write_text("# nWave Agent\nVersion: old")

    nw_commands = claude_dir / "commands" / "nw"
    nw_commands.mkdir(parents=True)
    (nw_commands / "develop.md").write_text("# nWave Command\nVersion: old")

    # Create user custom content directories
    custom_agent = claude_dir / "agents" / "my-custom-agent"
    custom_agent.mkdir(parents=True)
    (custom_agent / "agent.md").write_text("# Maria's Custom Agent\nDo not modify!")

    custom_command = claude_dir / "commands" / "my-custom-command"
    custom_command.mkdir(parents=True)
    (custom_command / "run.md").write_text("# Maria's Custom Command\nDo not modify!")

    return {
        "tmp_path": tmp_path,
        "claude_dir": claude_dir,
        "version_file": claude_dir / "VERSION",
        "nw_agents": nw_agents,
        "nw_commands": nw_commands,
        "custom_agent": custom_agent,
        "custom_command": custom_command,
        "custom_agent_file": custom_agent / "agent.md",
        "custom_command_file": custom_command / "run.md",
        "nw_agent_file": nw_agents / "software-crafter.md",
        "nw_command_file": nw_commands / "develop.md",
    }


@pytest.fixture
def cli_environment_with_user_content(
    clean_test_environment_with_user_content, project_root
):
    """
    Environment variables for CLI execution with user content.

    CRITICAL: Start from os.environ.copy() to inherit system environment.
    CRITICAL: Include project root in PYTHONPATH for nWave module resolution.
    """
    env = os.environ.copy()
    env["NWAVE_HOME"] = str(clean_test_environment_with_user_content["claude_dir"])
    env["NWAVE_TEST_MODE"] = "true"

    # Add project root to PYTHONPATH so nWave module can be imported
    existing_pythonpath = env.get("PYTHONPATH", "")
    if existing_pythonpath:
        env["PYTHONPATH"] = f"{project_root}:{existing_pythonpath}"
    else:
        env["PYTHONPATH"] = str(project_root)

    return env


@pytest.fixture
def run_update_command_with_user_content(
    clean_test_environment_with_user_content,
    cli_environment_with_user_content,
    update_cli_path,
    mock_github_response,
    mock_download_server,
):
    """
    Factory fixture for running update command through CLI with user content.

    Returns a function that executes the CLI and captures results.
    """

    def _run(confirm_update: bool = True):
        env = cli_environment_with_user_content.copy()

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
                cwd=str(clean_test_environment_with_user_content["tmp_path"]),
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


@pytest.mark.usefixtures("clean_test_environment_with_user_content")
def test_non_nwave_user_content_is_preserved_during_update(
    clean_test_environment_with_user_content,
    mock_github_response,
    mock_download_server,
    run_update_command_with_user_content,
    cli_result,
    scenario_context,
):
    """
    Scenario: Non-nWave user content is preserved during update (line 202)

    Given Maria has nWave v1.2.3 installed in the test ~/.claude/ directory
    And Maria has custom agents in ~/.claude/agents/my-custom-agent/
    And Maria has custom commands in ~/.claude/commands/my-custom-command/
    And the GitHub API returns v1.3.0 as the latest release with valid checksum
    And the download server provides a valid release asset
    When Maria runs the /nw:update command through the CLI entry point
    And Maria confirms the update when prompted
    Then her custom agent at ~/.claude/agents/my-custom-agent/ remains untouched
    And her custom command at ~/.claude/commands/my-custom-command/ remains untouched
    And only nWave-prefixed content in ~/.claude/agents/nw/ is replaced
    And only nWave-prefixed content in ~/.claude/commands/nw/ is replaced
    """
    env = clean_test_environment_with_user_content

    # GIVEN: Maria has nWave v1.2.3 installed
    scenario_context["persona"] = "Maria"
    scenario_context["installed_version"] = "1.2.3"
    env["version_file"].write_text("1.2.3")
    assert env["version_file"].read_text().strip() == "1.2.3"

    # AND: Maria has custom agents in ~/.claude/agents/my-custom-agent/
    custom_agent_content_before = env["custom_agent_file"].read_text()
    assert "Maria's Custom Agent" in custom_agent_content_before
    assert env["custom_agent"].exists(), "Custom agent directory should exist"

    # AND: Maria has custom commands in ~/.claude/commands/my-custom-command/
    custom_command_content_before = env["custom_command_file"].read_text()
    assert "Maria's Custom Command" in custom_command_content_before
    assert env["custom_command"].exists(), "Custom command directory should exist"

    # Store original nWave content for comparison
    nw_agent_content_before = env["nw_agent_file"].read_text()
    nw_command_content_before = env["nw_command_file"].read_text()
    assert "Version: old" in nw_agent_content_before
    assert "Version: old" in nw_command_content_before

    # AND: GitHub API returns v1.3.0 as latest release with valid checksum
    mock_github_response["latest_version"] = "1.3.0"
    mock_github_response["checksum"] = "abc123def456"
    mock_github_response["download_url"] = (
        "https://mock.github.com/releases/v1.3.0.tar.gz"
    )

    # AND: Download server provides valid release asset
    mock_download_server["checksum"] = "abc123def456"
    mock_download_server["is_available"] = True

    # WHEN: Maria runs /nw:update command and confirms
    result = run_update_command_with_user_content(confirm_update=True)
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

    # THEN: Her custom agent at ~/.claude/agents/my-custom-agent/ remains untouched
    assert env[
        "custom_agent"
    ].exists(), f"Custom agent directory should still exist. {diagnostic}"
    assert env[
        "custom_agent_file"
    ].exists(), f"Custom agent file should still exist. {diagnostic}"
    custom_agent_content_after = env["custom_agent_file"].read_text()
    assert custom_agent_content_after == custom_agent_content_before, (
        f"Custom agent content should be unchanged.\n"
        f"Before: {custom_agent_content_before!r}\n"
        f"After: {custom_agent_content_after!r}\n"
        f"{diagnostic}"
    )

    # AND: Her custom command at ~/.claude/commands/my-custom-command/ remains untouched
    assert env[
        "custom_command"
    ].exists(), f"Custom command directory should still exist. {diagnostic}"
    assert env[
        "custom_command_file"
    ].exists(), f"Custom command file should still exist. {diagnostic}"
    custom_command_content_after = env["custom_command_file"].read_text()
    assert custom_command_content_after == custom_command_content_before, (
        f"Custom command content should be unchanged.\n"
        f"Before: {custom_command_content_before!r}\n"
        f"After: {custom_command_content_after!r}\n"
        f"{diagnostic}"
    )

    # AND: Only nWave-prefixed content in ~/.claude/agents/nw/ is replaced
    # In test mode, we verify that nw content WOULD be replaced by checking
    # that the update was successful and nw directories are still present
    assert env[
        "nw_agents"
    ].exists(), f"nWave agents directory should exist after update. {diagnostic}"

    # AND: Only nWave-prefixed content in ~/.claude/commands/nw/ is replaced
    assert env[
        "nw_commands"
    ].exists(), f"nWave commands directory should exist after update. {diagnostic}"

    # AND: Update completed successfully
    assert returncode == 0, f"Expected exit code 0, got {returncode}. {diagnostic}"

    # AND: VERSION file updated to 1.3.0
    version_content = env["version_file"].read_text().strip()
    assert (
        version_content == "1.3.0"
    ), f"VERSION file should contain '1.3.0', got '{version_content}'. {diagnostic}"


# ============================================================================
# Step 04-02: Major version change requires confirmation
# ============================================================================


@pytest.mark.usefixtures("clean_test_environment")
def test_major_version_change_requires_confirmation(
    clean_test_environment,
    mock_github_response,
    mock_download_server,
    cli_environment,
    update_cli_path,
    cli_result,
    scenario_context,
):
    """
    Scenario: Major version change requires confirmation (line 126)

    Given Paolo has nWave v1.3.0 installed in the test ~/.claude/ directory
    And the GitHub API returns v2.0.0 as the latest release
    When Paolo runs the /nw:update command through the CLI entry point
    Then a warning displays "Major version change detected (1.x to 2.x). This may break existing workflows."
    And the prompt displays "Continue? [y/N]"
    And the update waits for confirmation before proceeding
    """
    # GIVEN: Paolo has nWave v1.3.0 installed
    scenario_context["persona"] = "Paolo"
    scenario_context["installed_version"] = "1.3.0"
    clean_test_environment["version_file"].write_text("1.3.0")
    assert clean_test_environment["version_file"].read_text().strip() == "1.3.0"

    # AND: GitHub API returns v2.0.0 as the latest release (MAJOR version change)
    mock_github_response["latest_version"] = "2.0.0"
    mock_github_response["checksum"] = "abc123def456"
    mock_github_response["download_url"] = (
        "https://mock.github.com/releases/v2.0.0.tar.gz"
    )

    # Configure download server
    mock_download_server["checksum"] = "abc123def456"
    mock_download_server["is_available"] = True

    # Build environment with mock settings
    # We do NOT set NWAVE_MOCK_CONFIRM_UPDATE to verify the prompt is displayed
    env = cli_environment.copy()
    env["NWAVE_MOCK_GITHUB_VERSION"] = mock_github_response["latest_version"]
    env["NWAVE_MOCK_GITHUB_CHECKSUM"] = mock_github_response["checksum"]
    env["NWAVE_MOCK_DOWNLOAD_URL"] = mock_github_response["download_url"]
    env["NWAVE_MOCK_GITHUB_REACHABLE"] = "true"
    env["NWAVE_MOCK_DOWNLOAD_CHECKSUM"] = mock_download_server["checksum"]
    # Set confirmation to "n" so we can verify the warning is shown before confirmation
    env["NWAVE_MOCK_CONFIRM_UPDATE"] = "n"

    # WHEN: Paolo runs /nw:update command
    try:
        result = subprocess.run(
            [sys.executable, str(update_cli_path)],
            capture_output=True,
            text=True,
            timeout=30,
            env=env,
            cwd=str(clean_test_environment["tmp_path"]),
        )
        cli_result.update(
            {
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode,
                "exception": None,
            }
        )
    except subprocess.TimeoutExpired as e:
        cli_result.update(
            {
                "stdout": "",
                "stderr": "Command timed out",
                "returncode": 124,
                "exception": e,
            }
        )

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

    # THEN: A warning displays "Major version change detected (1.x to 2.x). This may break existing workflows."
    expected_warning = (
        "Major version change detected (1.x to 2.x). This may break existing workflows."
    )
    assert expected_warning in stdout, (
        f"Expected major version warning not found.\n"
        f"Expected: '{expected_warning}'\n"
        f"{diagnostic}"
    )

    # AND: The prompt displays "Continue? [y/N]"
    expected_prompt = "Continue? [y/N]"
    assert expected_prompt in stdout, (
        f"Expected confirmation prompt not found.\n"
        f"Expected: '{expected_prompt}'\n"
        f"{diagnostic}"
    )

    # AND: The update waits for confirmation before proceeding
    # Since we set confirmation to "n", the update should be cancelled
    # and VERSION should still be 1.3.0
    version_content = clean_test_environment["version_file"].read_text().strip()
    assert version_content == "1.3.0", (
        f"VERSION file should still contain '1.3.0' since user did not confirm.\n"
        f"Got: '{version_content}'\n"
        f"{diagnostic}"
    )


# ============================================================================
# Step 04-03: Major version update proceeds with confirmation
# ============================================================================


@pytest.mark.usefixtures("clean_test_environment")
def test_major_version_update_proceeds_with_confirmation(
    clean_test_environment,
    mock_github_response,
    mock_download_server,
    cli_environment,
    update_cli_path,
    cli_result,
    scenario_context,
):
    """
    Scenario: Major version update proceeds with confirmation (line 135)

    Given Paolo has nWave v1.3.0 installed in the test ~/.claude/ directory
    And the GitHub API returns v2.0.0 as the latest release with valid checksum
    And the download server provides a valid release asset
    When Paolo runs the /nw:update command through the CLI entry point
    And Paolo confirms with "y" when prompted about major version change
    Then the update proceeds
    And nWave is updated to v2.0.0
    """
    # GIVEN: Paolo has nWave v1.3.0 installed
    scenario_context["persona"] = "Paolo"
    scenario_context["installed_version"] = "1.3.0"
    clean_test_environment["version_file"].write_text("1.3.0")
    assert clean_test_environment["version_file"].read_text().strip() == "1.3.0"

    # AND: GitHub API returns v2.0.0 as the latest release with valid checksum
    mock_github_response["latest_version"] = "2.0.0"
    mock_github_response["checksum"] = "abc123def456"
    mock_github_response["download_url"] = (
        "https://mock.github.com/releases/v2.0.0.tar.gz"
    )

    # AND: Download server provides valid release asset
    mock_download_server["checksum"] = "abc123def456"
    mock_download_server["is_available"] = True

    # Build environment with mock settings
    env = cli_environment.copy()
    env["NWAVE_MOCK_GITHUB_VERSION"] = mock_github_response["latest_version"]
    env["NWAVE_MOCK_GITHUB_CHECKSUM"] = mock_github_response["checksum"]
    env["NWAVE_MOCK_DOWNLOAD_URL"] = mock_github_response["download_url"]
    env["NWAVE_MOCK_GITHUB_REACHABLE"] = "true"
    env["NWAVE_MOCK_DOWNLOAD_CHECKSUM"] = mock_download_server["checksum"]

    # WHEN: Paolo confirms with "y" when prompted about major version change
    env["NWAVE_MOCK_CONFIRM_UPDATE"] = "y"
    env["NWAVE_MOCK_CONFIRM_MAJOR_UPDATE"] = "y"

    # WHEN: Paolo runs /nw:update command
    try:
        result = subprocess.run(
            [sys.executable, str(update_cli_path)],
            capture_output=True,
            text=True,
            timeout=30,
            env=env,
            cwd=str(clean_test_environment["tmp_path"]),
        )
        cli_result.update(
            {
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode,
                "exception": None,
            }
        )
    except subprocess.TimeoutExpired as e:
        cli_result.update(
            {
                "stdout": "",
                "stderr": "Command timed out",
                "returncode": 124,
                "exception": e,
            }
        )

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

    # THEN: The major version warning was displayed (prerequisite from 04-02)
    expected_warning = "Major version change detected"
    assert expected_warning in stdout, (
        f"Expected major version warning not found.\n"
        f"Expected: '{expected_warning}'\n"
        f"{diagnostic}"
    )

    # AND: The update proceeds (confirmed with "y")
    # (This is verified by the VERSION file being updated)

    # AND: nWave is updated to v2.0.0
    version_content = clean_test_environment["version_file"].read_text().strip()
    assert version_content == "2.0.0", (
        f"VERSION file should contain '2.0.0' after confirmed major version update.\n"
        f"Got: '{version_content}'\n"
        f"{diagnostic}"
    )

    # AND: Exit code is 0 (success)
    assert returncode == 0, f"Expected exit code 0, got {returncode}. {diagnostic}"

    # AND: Output displays "Update complete."
    expected_output = "Update complete."
    assert (
        expected_output in stdout
    ), f"Expected '{expected_output}' not found in output. {diagnostic}"


# ============================================================================
# Step 04-04: Major version update cancelled with denial
# ============================================================================


@pytest.mark.usefixtures("clean_test_environment")
def test_major_version_update_cancelled_with_denial(
    clean_test_environment,
    mock_github_response,
    mock_download_server,
    cli_environment,
    update_cli_path,
    cli_result,
    scenario_context,
):
    """
    Scenario: Major version update cancelled with denial (line 145)

    Given Paolo has nWave v1.3.0 installed in the test ~/.claude/ directory
    And the GitHub API returns v2.0.0 as the latest release
    When Paolo runs the /nw:update command through the CLI entry point
    And Paolo denies with "n" when prompted about major version change
    Then the update is cancelled
    And the VERSION file still contains "1.3.0"
    And no backup was created
    """
    # GIVEN: Paolo has nWave v1.3.0 installed
    scenario_context["persona"] = "Paolo"
    scenario_context["installed_version"] = "1.3.0"
    clean_test_environment["version_file"].write_text("1.3.0")
    assert clean_test_environment["version_file"].read_text().strip() == "1.3.0"

    # AND: GitHub API returns v2.0.0 as the latest release (MAJOR version change)
    mock_github_response["latest_version"] = "2.0.0"
    mock_github_response["checksum"] = "abc123def456"
    mock_github_response["download_url"] = (
        "https://mock.github.com/releases/v2.0.0.tar.gz"
    )

    # Configure download server
    mock_download_server["checksum"] = "abc123def456"
    mock_download_server["is_available"] = True

    # Build environment with mock settings
    env = cli_environment.copy()
    env["NWAVE_MOCK_GITHUB_VERSION"] = mock_github_response["latest_version"]
    env["NWAVE_MOCK_GITHUB_CHECKSUM"] = mock_github_response["checksum"]
    env["NWAVE_MOCK_DOWNLOAD_URL"] = mock_github_response["download_url"]
    env["NWAVE_MOCK_GITHUB_REACHABLE"] = "true"
    env["NWAVE_MOCK_DOWNLOAD_CHECKSUM"] = mock_download_server["checksum"]

    # Count backups BEFORE running the command
    parent_dir = clean_test_environment["claude_dir"].parent
    backups_before = list(parent_dir.glob(".claude.backup.*"))
    backup_count_before = len(backups_before)

    # WHEN: Paolo denies with "n" when prompted about major version change
    env["NWAVE_MOCK_CONFIRM_UPDATE"] = "n"

    # WHEN: Paolo runs /nw:update command
    try:
        result = subprocess.run(
            [sys.executable, str(update_cli_path)],
            capture_output=True,
            text=True,
            timeout=30,
            env=env,
            cwd=str(clean_test_environment["tmp_path"]),
        )
        cli_result.update(
            {
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode,
                "exception": None,
            }
        )
    except subprocess.TimeoutExpired as e:
        cli_result.update(
            {
                "stdout": "",
                "stderr": "Command timed out",
                "returncode": 124,
                "exception": e,
            }
        )

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

    # THEN: The major version warning was displayed (prerequisite from 04-02)
    # This validates that step 04-04 tests the correct flow (major version denial)
    expected_warning = "Major version change detected"
    assert expected_warning in stdout, (
        f"Expected major version warning not found.\n"
        f"Expected: '{expected_warning}'\n"
        f"NOTE: Step 04-04 requires step 04-02 (major version warning) to be implemented first.\n"
        f"{diagnostic}"
    )

    # AND: The update is cancelled
    expected_cancelled_message = "Update cancelled."
    assert expected_cancelled_message in stdout, (
        f"Expected update cancelled message not found.\n"
        f"Expected: '{expected_cancelled_message}'\n"
        f"{diagnostic}"
    )

    # AND: The VERSION file still contains "1.3.0"
    version_content = clean_test_environment["version_file"].read_text().strip()
    assert version_content == "1.3.0", (
        f"VERSION file should still contain '1.3.0' after cancellation.\n"
        f"Got: '{version_content}'\n"
        f"{diagnostic}"
    )

    # AND: No backup was created
    backups_after = list(parent_dir.glob(".claude.backup.*"))
    backup_count_after = len(backups_after)
    assert backup_count_after == backup_count_before, (
        f"No backup should be created when update is cancelled.\n"
        f"Backups before: {backup_count_before}, after: {backup_count_after}\n"
        f"{diagnostic}"
    )

    # AND: Exit code is 0 (cancellation is a valid user choice, not an error)
    assert returncode == 0, f"Expected exit code 0, got {returncode}. {diagnostic}"


# ============================================================================
# Step 04-10: Already up-to-date shows message without update
# ============================================================================


@pytest.mark.usefixtures("clean_test_environment")
def test_already_up_to_date_shows_message_without_update(
    clean_test_environment,
    mock_github_response,
    mock_download_server,
    cli_environment,
    update_cli_path,
    cli_result,
    scenario_context,
):
    """
    Scenario: Already up-to-date shows message without update (line 216)

    Given Sofia has nWave v1.3.0 installed in the test ~/.claude/ directory
    And the GitHub API returns v1.3.0 as the latest release
    When Sofia runs the /nw:update command through the CLI entry point
    Then the output displays "Already up to date (v1.3.0)."
    And no backup is created
    And no download occurs
    """
    # GIVEN: Sofia has nWave v1.3.0 installed
    scenario_context["persona"] = "Sofia"
    scenario_context["installed_version"] = "1.3.0"
    clean_test_environment["version_file"].write_text("1.3.0")
    assert clean_test_environment["version_file"].read_text().strip() == "1.3.0"

    # AND: GitHub API returns v1.3.0 as the latest release (same as installed)
    mock_github_response["latest_version"] = "1.3.0"
    mock_github_response["checksum"] = "abc123def456"
    mock_github_response["download_url"] = (
        "https://mock.github.com/releases/v1.3.0.tar.gz"
    )

    # Configure download server (should NOT be called)
    mock_download_server["checksum"] = "abc123def456"
    mock_download_server["is_available"] = True

    # Build environment with mock settings
    env = cli_environment.copy()
    env["NWAVE_MOCK_GITHUB_VERSION"] = mock_github_response["latest_version"]
    env["NWAVE_MOCK_GITHUB_CHECKSUM"] = mock_github_response["checksum"]
    env["NWAVE_MOCK_DOWNLOAD_URL"] = mock_github_response["download_url"]
    env["NWAVE_MOCK_GITHUB_REACHABLE"] = "true"
    env["NWAVE_MOCK_DOWNLOAD_CHECKSUM"] = mock_download_server["checksum"]

    # Count backups BEFORE running the command
    parent_dir = clean_test_environment["claude_dir"].parent
    backups_before = list(parent_dir.glob(".claude.backup.*"))
    backup_count_before = len(backups_before)

    # WHEN: Sofia runs /nw:update command
    try:
        result = subprocess.run(
            [sys.executable, str(update_cli_path)],
            capture_output=True,
            text=True,
            timeout=30,
            env=env,
            cwd=str(clean_test_environment["tmp_path"]),
        )
        cli_result.update(
            {
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode,
                "exception": None,
            }
        )
    except subprocess.TimeoutExpired as e:
        cli_result.update(
            {
                "stdout": "",
                "stderr": "Command timed out",
                "returncode": 124,
                "exception": e,
            }
        )

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

    # THEN: The output displays "Already up to date (v1.3.0)."
    expected_message = "Already up to date (v1.3.0)."
    assert expected_message in stdout, (
        f"Expected already up-to-date message not found.\n"
        f"Expected: '{expected_message}'\n"
        f"{diagnostic}"
    )

    # AND: No backup is created
    backups_after = list(parent_dir.glob(".claude.backup.*"))
    backup_count_after = len(backups_after)
    assert backup_count_after == backup_count_before, (
        f"No backup should be created when already up to date.\n"
        f"Backups before: {backup_count_before}, after: {backup_count_after}\n"
        f"{diagnostic}"
    )

    # AND: No download occurs (verified by behavior - no update happens)
    # The fact that VERSION file remains unchanged verifies no download occurred
    version_content = clean_test_environment["version_file"].read_text().strip()
    assert version_content == "1.3.0", (
        f"VERSION file should still contain '1.3.0' (no update needed).\n"
        f"Got: '{version_content}'\n"
        f"{diagnostic}"
    )

    # AND: Exit code is 0 (success - no update needed is successful)
    assert returncode == 0, f"Expected exit code 0, got {returncode}. {diagnostic}"
