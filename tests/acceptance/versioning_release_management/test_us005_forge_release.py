"""
Step definitions for US-005: Create Official Release acceptance tests.

CRITICAL: Hexagonal boundary enforcement - tests invoke CLI entry points ONLY.
- FORBIDDEN: Direct imports of nWave.core.* components
- REQUIRED: Invoke through driving ports (CLI entry points)

Feature file: docs/features/versioning-release-management/distill/acceptance-tests.feature
"""

from pathlib import Path

import pytest


@pytest.fixture
def scenario_context():
    """Shared context between steps."""
    return {}


@pytest.fixture
def mock_git_state():
    """Mock Git state for testing."""
    return {
        "branch": "development",
        "has_uncommitted_changes": False,
    }


@pytest.fixture
def mock_github_cli_response():
    """Mock GitHub CLI response configuration."""
    return {
        "pr_number": 123,
        "pr_url": "https://github.com/UndeadGrishnackh/crafter-ai/pull/123",
        "success": True,
        "error": None,
    }


@pytest.fixture
def forge_release_cli_path(project_root):
    """Path to the forge:release CLI entry point."""
    return project_root / "nWave" / "cli" / "forge_release_cli.py"


@pytest.fixture
def run_forge_release_command(
    clean_test_environment,
    cli_environment,
    forge_release_cli_path,
    mock_git_state,
    mock_github_cli_response,
):
    """
    Factory fixture for running forge:release command through CLI.

    Returns a function that executes the CLI and captures results.
    """
    import os
    import subprocess
    import sys

    def _run():
        env = cli_environment.copy()

        # Inject mock Git state via environment
        env["NWAVE_MOCK_GIT_BRANCH"] = mock_git_state["branch"]
        env["NWAVE_MOCK_GIT_HAS_UNCOMMITTED"] = str(
            mock_git_state["has_uncommitted_changes"]
        ).lower()

        # Inject mock GitHub CLI response via environment
        env["NWAVE_MOCK_GH_PR_NUMBER"] = str(mock_github_cli_response["pr_number"])
        env["NWAVE_MOCK_GH_PR_URL"] = mock_github_cli_response["pr_url"]
        env["NWAVE_MOCK_GH_SUCCESS"] = str(mock_github_cli_response["success"]).lower()
        if mock_github_cli_response["error"]:
            env["NWAVE_MOCK_GH_ERROR"] = mock_github_cli_response["error"]

        try:
            result = subprocess.run(
                [sys.executable, str(forge_release_cli_path)],
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
                "stderr": f"CLI not found: {forge_release_cli_path}",
                "returncode": 1,
                "exception": e,
            }

    return _run


# ============================================================================
# Step 07-01: Successful release PR creation from development branch
# ============================================================================


@pytest.mark.usefixtures("clean_test_environment")
def test_successful_release_pr_creation_from_development_branch(
    clean_test_environment,
    mock_git_state,
    mock_github_cli_response,
    run_forge_release_command,
    scenario_context,
):
    """
    Scenario: Successful release PR creation from development branch

    Given Matteo has repository admin access configured
    And the git branch is "development"
    And there are no uncommitted changes
    When Matteo runs the /nw:forge:release command through the CLI entry point
    Then a PR is created from development to main via gh CLI
    And the output displays the PR number and URL
    And the output indicates "PR created. Pipeline running..."
    """
    # GIVEN: Matteo has repository admin access configured
    scenario_context["persona"] = "Matteo"
    scenario_context["has_admin_access"] = True

    # AND: The git branch is "development"
    mock_git_state["branch"] = "development"

    # AND: There are no uncommitted changes
    mock_git_state["has_uncommitted_changes"] = False

    # Configure mock GitHub CLI response for successful PR creation
    mock_github_cli_response["pr_number"] = 123
    mock_github_cli_response["pr_url"] = (
        "https://github.com/UndeadGrishnackh/crafter-ai/pull/123"
    )
    mock_github_cli_response["success"] = True

    # WHEN: Matteo runs /nw:forge:release command
    result = run_forge_release_command()

    # THEN: A PR is created from development to main via gh CLI
    # (Verified through output - PR number and URL displayed)
    stdout = result["stdout"]
    stderr = result["stderr"]
    returncode = result["returncode"]

    # AND: The output displays the PR number and URL
    assert "PR #123" in stdout or "123" in stdout, (
        f"Expected PR number '123' in output:\n"
        f"STDOUT: {stdout!r}\n"
        f"STDERR: {stderr!r}\n"
        f"Return code: {returncode}"
    )

    assert (
        "https://github.com/UndeadGrishnackh/crafter-ai/pull/123" in stdout
        or "pull/123" in stdout
    ), (
        f"Expected PR URL in output:\n"
        f"STDOUT: {stdout!r}\n"
        f"STDERR: {stderr!r}\n"
        f"Return code: {returncode}"
    )

    # AND: The output indicates "PR created. Pipeline running..."
    expected_message = "PR created. Pipeline running..."
    assert expected_message in stdout, (
        f"Expected '{expected_message}' in output:\n"
        f"STDOUT: {stdout!r}\n"
        f"STDERR: {stderr!r}\n"
        f"Return code: {returncode}"
    )

    # Verify successful exit code
    assert returncode == 0, (
        f"Expected exit code 0, got {returncode}\n"
        f"STDOUT: {stdout!r}\n"
        f"STDERR: {stderr!r}"
    )
