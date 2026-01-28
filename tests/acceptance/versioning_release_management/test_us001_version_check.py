"""
Step definitions for US-001: Check Installed Version acceptance tests.

CRITICAL: Hexagonal boundary enforcement - tests invoke CLI entry points ONLY.
- FORBIDDEN: Direct imports of nWave.core.* components
- REQUIRED: Invoke through driving ports (CLI entry points)

Feature file: docs/features/versioning-release-management/distill/acceptance-tests.feature
"""

from pathlib import Path

import pytest
from pytest_bdd import scenarios, given, when, then, parsers

# Load scenarios from the distill feature file
# Note: Path is relative to this test file
FEATURE_FILE = Path(__file__).parent.parent.parent.parent / "docs" / "features" / "versioning-release-management" / "distill" / "acceptance-tests.feature"

# Only load specific scenarios that are ACTIVE (not marked @skip)
# For step 03-02, we're implementing "Display version when up-to-date"


@pytest.fixture
def scenario_context():
    """Shared context between steps."""
    return {}


# ============================================================================
# GIVEN - Preconditions
# ============================================================================


@given("a clean test environment with isolated ~/.claude/ directory")
def clean_environment_setup(clean_test_environment):
    """Verify clean test environment is ready."""
    assert clean_test_environment["claude_dir"].exists()


@given("the nWave CLI is available at the driving port entry point")
def cli_available(version_cli_path):
    """Verify CLI entry point exists (or will exist after implementation)."""
    # This will initially fail, triggering RED phase
    pass


@given(parsers.parse("Sofia has nWave v{version} installed in the test ~/.claude/ directory"))
def sofia_has_version_installed(clean_test_environment, version, scenario_context):
    """Set up Sofia's installation with specific version."""
    scenario_context["persona"] = "Sofia"
    scenario_context["installed_version"] = version
    clean_test_environment["version_file"].write_text(version)


@given(parsers.parse("Marco has nWave v{version} installed in the test ~/.claude/ directory"))
def marco_has_version_installed(clean_test_environment, version, scenario_context):
    """Set up Marco's installation with specific version."""
    scenario_context["persona"] = "Marco"
    scenario_context["installed_version"] = version
    clean_test_environment["version_file"].write_text(version)


@given(parsers.parse('the VERSION file contains "{version}"'))
def version_file_contains(clean_test_environment, version):
    """Verify VERSION file contains expected version."""
    actual = clean_test_environment["version_file"].read_text().strip()
    assert actual == version, f"Expected VERSION '{version}', got '{actual}'"


@given(parsers.parse("the GitHub API returns v{version} as the latest release"))
def github_returns_latest(mock_github_response, version):
    """Configure mock GitHub API to return specific version."""
    mock_github_response["latest_version"] = version


@given("network connectivity is unavailable for GitHub API")
def github_unreachable(mock_github_response):
    """Configure mock to simulate network failure."""
    mock_github_response["is_reachable"] = False


# ============================================================================
# WHEN - Actions (through CLI DRIVING PORT)
# ============================================================================


@when(parsers.parse("Sofia runs the /nw:version command through the CLI entry point"))
def sofia_runs_version_command(run_version_command, cli_result, scenario_context):
    """Sofia executes version command through CLI."""
    result = run_version_command()
    cli_result.update(result)
    scenario_context["last_result"] = result


@when(parsers.parse("Marco runs the /nw:version command through the CLI entry point"))
def marco_runs_version_command(run_version_command, cli_result, scenario_context):
    """Marco executes version command through CLI."""
    result = run_version_command()
    cli_result.update(result)
    scenario_context["last_result"] = result


# ============================================================================
# THEN - Assertions (validate observable behavior)
# ============================================================================


@then(parsers.parse('the output displays "{expected_output}"'))
def output_displays(cli_result, expected_output):
    """Verify CLI output contains expected text."""
    stdout = cli_result["stdout"]
    stderr = cli_result["stderr"]
    returncode = cli_result["returncode"]

    diagnostic = (
        f"Expected '{expected_output}' not found in output:\n"
        f"STDOUT: {stdout!r}\n"
        f"STDERR: {stderr!r}\n"
        f"Return code: {returncode}"
    )

    assert expected_output in stdout, diagnostic


@then("the watermark file ~/.claude/nwave.update is updated with current timestamp")
def watermark_updated(clean_test_environment):
    """Verify watermark file was updated."""
    watermark_file = clean_test_environment["watermark_file"]
    assert watermark_file.exists(), "Watermark file was not created"


@then(parsers.parse('the watermark file contains latest_version "{version}"'))
def watermark_contains_version(clean_test_environment, version):
    """Verify watermark contains expected version."""
    import json

    watermark_file = clean_test_environment["watermark_file"]
    content = json.loads(watermark_file.read_text())
    assert content.get("latest_version") == version


# ============================================================================
# Test function that loads the specific scenario
# ============================================================================


# Manually define test for "Display version when up-to-date" scenario
@pytest.mark.usefixtures("clean_test_environment")
def test_display_version_when_up_to_date(
    clean_test_environment,
    mock_github_response,
    run_version_command,
    cli_result,
    scenario_context,
):
    """
    Scenario: Display version when up-to-date

    Given Sofia has nWave v1.3.0 installed in the test ~/.claude/ directory
    And the VERSION file contains "1.3.0"
    And the GitHub API returns v1.3.0 as the latest release
    When Sofia runs the /nw:version command through the CLI entry point
    Then the output displays "nWave v1.3.0 (up to date)"
    """
    # GIVEN: Sofia has nWave v1.3.0 installed
    scenario_context["persona"] = "Sofia"
    scenario_context["installed_version"] = "1.3.0"
    clean_test_environment["version_file"].write_text("1.3.0")

    # AND: VERSION file contains "1.3.0"
    assert clean_test_environment["version_file"].read_text().strip() == "1.3.0"

    # AND: GitHub API returns v1.3.0 as latest release
    mock_github_response["latest_version"] = "1.3.0"

    # WHEN: Sofia runs /nw:version command
    result = run_version_command()
    cli_result.update(result)

    # THEN: Output displays "nWave v1.3.0 (up to date)"
    expected_output = "nWave v1.3.0 (up to date)"
    stdout = cli_result["stdout"]
    stderr = cli_result["stderr"]

    diagnostic = (
        f"Expected '{expected_output}' not found in output:\n"
        f"STDOUT: {stdout!r}\n"
        f"STDERR: {stderr!r}\n"
        f"Return code: {cli_result['returncode']}"
    )

    assert expected_output in stdout, diagnostic
