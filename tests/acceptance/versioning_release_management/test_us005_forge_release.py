"""
Step definitions for US-005: Create Official Release acceptance tests.

CRITICAL: Hexagonal boundary enforcement - tests invoke CLI entry points ONLY.
- FORBIDDEN: Direct imports of nWave.core.* components
- REQUIRED: Invoke through driving ports (CLI entry points)

Feature file: docs/features/versioning-release-management/distill/acceptance-tests.feature
"""


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
        if mock_github_cli_response["pr_number"] is not None:
            env["NWAVE_MOCK_GH_PR_NUMBER"] = str(mock_github_cli_response["pr_number"])
        if mock_github_cli_response["pr_url"] is not None:
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

    # AND: The output indicates PR was created and pipeline is running
    # Format (per 07-06): "PR #123 created." + "CI/CD pipeline triggered. Monitor at: {url}"
    assert "PR #123 created." in stdout or "PR created" in stdout, (
        f"Expected PR created message in output:\n"
        f"STDOUT: {stdout!r}\n"
        f"STDERR: {stderr!r}\n"
        f"Return code: {returncode}"
    )
    assert "CI/CD pipeline triggered" in stdout or "Pipeline running" in stdout, (
        f"Expected pipeline status message in output:\n"
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


# ============================================================================
# Step 07-02: Release command fails on main branch
# ============================================================================


@pytest.mark.usefixtures("clean_test_environment")
def test_release_command_fails_on_main_branch(
    clean_test_environment,
    mock_git_state,
    mock_github_cli_response,
    run_forge_release_command,
    scenario_context,
):
    """
    Scenario: Release command fails on main branch

    Given Paola is on the main branch
    When Paola runs the /nw:forge:release command through the CLI entry point
    Then the error displays "Release must be initiated from the development branch."
    And no PR is created
    And the CLI exit code is non-zero
    """
    # GIVEN: Paola is on the main branch
    scenario_context["persona"] = "Paola"
    mock_git_state["branch"] = "main"
    mock_git_state["has_uncommitted_changes"] = False

    # Configure mock - should NOT be called since branch validation fails
    mock_github_cli_response["success"] = True
    mock_github_cli_response["pr_number"] = 123
    mock_github_cli_response["pr_url"] = (
        "https://github.com/UndeadGrishnackh/crafter-ai/pull/123"
    )

    # WHEN: Paola runs /nw:forge:release command
    result = run_forge_release_command()

    # THEN: The error displays "Release must be initiated from the development branch."
    stdout = result["stdout"]
    stderr = result["stderr"]
    returncode = result["returncode"]
    combined_output = stdout + stderr

    expected_error = "Release must be initiated from the development branch."
    assert expected_error in combined_output, (
        f"Expected error message '{expected_error}' in output:\n"
        f"STDOUT: {stdout!r}\n"
        f"STDERR: {stderr!r}\n"
        f"Return code: {returncode}"
    )

    # AND: No PR is created (verified by absence of PR info in output)
    assert "PR #" not in stdout, (
        f"Expected no PR to be created, but found PR info in output:\n"
        f"STDOUT: {stdout!r}"
    )

    # AND: The CLI exit code is non-zero
    assert returncode != 0, (
        f"Expected non-zero exit code, got {returncode}\n"
        f"STDOUT: {stdout!r}\n"
        f"STDERR: {stderr!r}"
    )


# ============================================================================
# Step 07-04: Permission denied for non-admin user
# ============================================================================


@pytest.mark.usefixtures("clean_test_environment")
def test_permission_denied_for_non_admin_user(
    clean_test_environment,
    mock_git_state,
    mock_github_cli_response,
    run_forge_release_command,
    scenario_context,
):
    """
    Scenario: Permission denied for non-admin user (Line 428)

    Given Oscar does not have repository write access configured
    And the git branch is "development"
    And the gh CLI returns a permission denied error
    When Oscar runs the /nw:forge:release command through the CLI entry point
    Then the error displays "Permission denied. You don't have access to create releases for this repository."
    And no PR is created
    And the CLI exit code is non-zero
    """
    # GIVEN: Oscar does not have repository write access configured
    scenario_context["persona"] = "Oscar"
    scenario_context["has_admin_access"] = False

    # AND: The git branch is "development"
    mock_git_state["branch"] = "development"

    # AND: There are no uncommitted changes
    mock_git_state["has_uncommitted_changes"] = False

    # AND: The gh CLI returns a permission denied error
    mock_github_cli_response["success"] = False
    mock_github_cli_response["pr_number"] = None
    mock_github_cli_response["pr_url"] = None
    mock_github_cli_response["error"] = (
        "Permission denied. You don't have access to create releases for this repository."
    )

    # WHEN: Oscar runs /nw:forge:release command
    result = run_forge_release_command()

    # THEN: The error displays permission denied message
    stdout = result["stdout"]
    stderr = result["stderr"]
    returncode = result["returncode"]
    combined_output = stdout + stderr

    expected_error = (
        "Permission denied. You don't have access to create releases for this repository."
    )
    assert expected_error in combined_output, (
        f"Expected '{expected_error}' in output:\n"
        f"STDOUT: {stdout!r}\n"
        f"STDERR: {stderr!r}\n"
        f"Return code: {returncode}"
    )

    # AND: No PR is created (verified by error response - no PR number/URL)
    assert "PR #" not in stdout, (
        f"Expected no PR number in stdout (PR should not be created):\n"
        f"STDOUT: {stdout!r}"
    )

    # AND: The CLI exit code is non-zero
    assert returncode != 0, (
        f"Expected non-zero exit code, got {returncode}\n"
        f"STDOUT: {stdout!r}\n"
        f"STDERR: {stderr!r}"
    )


# ============================================================================
# Step 07-05: Release fails with uncommitted changes
# ============================================================================


@pytest.mark.usefixtures("clean_test_environment")
def test_release_fails_with_uncommitted_changes(
    clean_test_environment,
    mock_git_state,
    mock_github_cli_response,
    run_forge_release_command,
    scenario_context,
):
    """
    Scenario: Release fails with uncommitted changes (Line 438)

    Given Matteo has repository admin access configured
    And the git branch is "development"
    And there are uncommitted changes in the working directory
    When Matteo runs the /nw:forge:release command through the CLI entry point
    Then the error displays "Uncommitted changes detected. Commit or stash changes before releasing."
    And no PR is created
    And the CLI exit code is non-zero
    """
    # GIVEN: Matteo has repository admin access configured
    scenario_context["persona"] = "Matteo"
    scenario_context["has_admin_access"] = True

    # AND: The git branch is "development"
    mock_git_state["branch"] = "development"

    # AND: There are uncommitted changes in the working directory
    mock_git_state["has_uncommitted_changes"] = True

    # Configure mock GitHub CLI - should NOT be called since validation fails
    mock_github_cli_response["success"] = True
    mock_github_cli_response["pr_number"] = 123
    mock_github_cli_response["pr_url"] = (
        "https://github.com/UndeadGrishnackh/crafter-ai/pull/123"
    )

    # WHEN: Matteo runs /nw:forge:release command
    result = run_forge_release_command()

    # THEN: The error displays "Uncommitted changes detected..."
    stdout = result["stdout"]
    stderr = result["stderr"]
    returncode = result["returncode"]
    combined_output = stdout + stderr

    expected_error = "Uncommitted changes detected. Commit or stash changes before releasing."
    assert expected_error in combined_output, (
        f"Expected error message '{expected_error}' in output:\n"
        f"STDOUT: {stdout!r}\n"
        f"STDERR: {stderr!r}\n"
        f"Return code: {returncode}"
    )

    # AND: No PR is created (verified by absence of PR info in output)
    assert "PR #" not in stdout, (
        f"Expected no PR to be created, but found PR info in output:\n"
        f"STDOUT: {stdout!r}"
    )

    # AND: The CLI exit code is non-zero
    assert returncode != 0, (
        f"Expected non-zero exit code, got {returncode}\n"
        f"STDOUT: {stdout!r}\n"
        f"STDERR: {stderr!r}"
    )


# ============================================================================
# Step 07-06: Release shows pipeline status after PR creation
# ============================================================================


@pytest.mark.usefixtures("clean_test_environment")
def test_release_shows_pipeline_status_after_pr_creation(
    clean_test_environment,
    mock_git_state,
    mock_github_cli_response,
    run_forge_release_command,
    scenario_context,
):
    """
    Scenario: Release shows pipeline status after PR creation (Line 448)

    Given Matteo has repository admin access configured
    And the git branch is "development"
    And there are no uncommitted changes
    And the CI/CD pipeline is configured to run on PR
    When Matteo runs the /nw:forge:release command through the CLI entry point
    Then a PR is created
    And the output displays "PR #123 created."
    And the output displays "CI/CD pipeline triggered. Monitor at: {pr_url}"
    """
    # GIVEN: Matteo has repository admin access configured
    scenario_context["persona"] = "Matteo"
    scenario_context["has_admin_access"] = True

    # AND: The git branch is "development"
    mock_git_state["branch"] = "development"

    # AND: There are no uncommitted changes
    mock_git_state["has_uncommitted_changes"] = False

    # AND: The CI/CD pipeline is configured to run on PR
    # (Implicit - mocked environment simulates CI/CD configured)

    # Configure mock GitHub CLI response for successful PR creation
    mock_github_cli_response["pr_number"] = 123
    mock_github_cli_response["pr_url"] = (
        "https://github.com/UndeadGrishnackh/crafter-ai/pull/123"
    )
    mock_github_cli_response["success"] = True

    # WHEN: Matteo runs /nw:forge:release command
    result = run_forge_release_command()

    # THEN: A PR is created
    stdout = result["stdout"]
    stderr = result["stderr"]
    returncode = result["returncode"]

    # Verify successful exit code
    assert returncode == 0, (
        f"Expected exit code 0, got {returncode}\n"
        f"STDOUT: {stdout!r}\n"
        f"STDERR: {stderr!r}"
    )

    # AND: The output displays "PR #123 created."
    expected_pr_message = "PR #123 created."
    assert expected_pr_message in stdout, (
        f"Expected '{expected_pr_message}' in output:\n"
        f"STDOUT: {stdout!r}\n"
        f"STDERR: {stderr!r}\n"
        f"Return code: {returncode}"
    )

    # AND: The output displays "CI/CD pipeline triggered. Monitor at: {pr_url}"
    expected_pipeline_message = (
        "CI/CD pipeline triggered. Monitor at: "
        "https://github.com/UndeadGrishnackh/crafter-ai/pull/123"
    )
    assert expected_pipeline_message in stdout, (
        f"Expected '{expected_pipeline_message}' in output:\n"
        f"STDOUT: {stdout!r}\n"
        f"STDERR: {stderr!r}\n"
        f"Return code: {returncode}"
    )


# ============================================================================
# Step 07-03: Release command fails on feature branch
# ============================================================================


@pytest.mark.usefixtures("clean_test_environment")
def test_release_command_fails_on_feature_branch(
    clean_test_environment,
    mock_git_state,
    mock_github_cli_response,
    run_forge_release_command,
    scenario_context,
):
    """
    Scenario: Release command fails on feature branch

    Given Paola is on a feature/test branch
    When Paola runs the /nw:forge:release command through the CLI entry point
    Then the error displays "Release must be initiated from the development branch."
    And no PR is created
    And the CLI exit code is non-zero
    """
    # GIVEN: Paola is on a feature/test branch
    scenario_context["persona"] = "Paola"
    mock_git_state["branch"] = "feature/test"
    mock_git_state["has_uncommitted_changes"] = False

    # Configure mock GitHub CLI - should NOT be called
    mock_github_cli_response["success"] = True
    mock_github_cli_response["pr_number"] = 123
    mock_github_cli_response["pr_url"] = (
        "https://github.com/UndeadGrishnackh/crafter-ai/pull/123"
    )

    # WHEN: Paola runs /nw:forge:release command
    result = run_forge_release_command()

    # THEN: The error displays "Release must be initiated from the development branch."
    stdout = result["stdout"]
    stderr = result["stderr"]
    returncode = result["returncode"]
    combined_output = stdout + stderr

    expected_error = "Release must be initiated from the development branch."
    assert expected_error in combined_output, (
        f"Expected error message '{expected_error}' in output:\n"
        f"STDOUT: {stdout!r}\n"
        f"STDERR: {stderr!r}\n"
        f"Return code: {returncode}"
    )

    # AND: No PR is created (verified by error output - no PR number/URL displayed)
    assert "PR #" not in stdout, (
        f"Expected no PR to be created, but found PR number in output:\n"
        f"STDOUT: {stdout!r}"
    )

    # AND: CLI exit code is non-zero
    assert returncode != 0, (
        f"Expected non-zero exit code, got {returncode}\n"
        f"STDOUT: {stdout!r}\n"
        f"STDERR: {stderr!r}"
    )
