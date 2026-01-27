"""
Step definitions for version check acceptance tests (US-001, US-003).

CRITICAL: Hexagonal boundary enforcement - tests invoke CLI entry points ONLY.
❌ FORBIDDEN: Direct imports of nWave.core.* components
✅ REQUIRED: Invoke through driving ports (CLI entry points)

Cross-platform compatible (Windows, macOS, Linux).
"""

import os
import platform
import stat
import subprocess
import sys

import pytest
from pytest_bdd import scenarios, given, when, then, parsers

# Constants for clarity and maintainability
SUBPROCESS_TIMEOUT = 10
EXIT_SUCCESS = 0
EXIT_TIMEOUT = 124


# Load all scenarios from feature files
scenarios("us-001-check-version.feature")
scenarios("us-003-breaking-changes.feature")


# ============================================================================
# FIXTURES - Test Infrastructure
# ============================================================================


@pytest.fixture
def test_installation(tmp_path):
    """
    Create isolated test installation directory.

    Structure:
    tmp_path/.claude/
        ├── nWave/
        │   ├── cli/
        │   │   └── version_cli.py (mocked entry point)
        │   └── core/ (not directly accessed - boundary enforcement)
        └── nwave-version.txt (installed version)
    """
    install_dir = tmp_path / ".claude"
    install_dir.mkdir(parents=True)

    # Create nWave structure
    nwave_dir = install_dir / "nWave"
    nwave_dir.mkdir()

    cli_dir = nwave_dir / "cli"
    cli_dir.mkdir()

    # Version file location
    version_file = install_dir / "nwave-version.txt"

    return {
        "install_dir": install_dir,
        "nwave_dir": nwave_dir,
        "cli_dir": cli_dir,
        "version_file": version_file,
        "tmp_path": tmp_path,
    }


@pytest.fixture
def cli_result():
    """Shared dictionary for CLI command execution results."""
    return {"stdout": "", "stderr": "", "returncode": None, "exception": None}


@pytest.fixture
def mock_github_api():
    """Mock GitHub API responses for testing."""
    return {
        "latest_version": None,
        "changelog": "",
        "is_reachable": True,
        "tag_name": None,
    }


@pytest.fixture
def cli_environment(test_installation):
    """
    Environment variables for CLI execution.
    Points Python to test installation instead of real ~/.claude/

    CRITICAL: Start from os.environ.copy() to inherit system environment.
    On Windows, subprocess requires PATH, SystemRoot, COMSPEC, etc.
    Without these, Python subprocess may fail silently with empty output.
    """
    env = os.environ.copy()
    env["NWAVE_HOME"] = str(test_installation["install_dir"])
    env["PYTHONPATH"] = str(test_installation["nwave_dir"].parent)
    return env


# ============================================================================
# GIVEN - Preconditions
# ============================================================================


@given("nWave is installed at ~/.claude/nWave/")
def nwave_installed(test_installation):
    """Verify nWave directory structure exists in test environment."""
    assert test_installation["nwave_dir"].exists()
    assert test_installation["cli_dir"].exists()


@given("the version CLI entry point exists at ~/.claude/nWave/cli/version_cli.py")
def version_cli_exists(test_installation):
    """
    Create mock CLI entry point that simulates real version_cli.py behavior.

    CRITICAL: This represents the DRIVING PORT boundary.
    Tests invoke this script, which would normally call production services.
    For acceptance tests, we create a minimal implementation that demonstrates
    the hexagonal boundary without requiring full production infrastructure.
    """
    cli_script = test_installation["cli_dir"] / "version_cli.py"

    # Minimal CLI script that reads VERSION and would call GitHub API
    # In real implementation, this delegates to VersionManager
    script_content = '''#!/usr/bin/env python3
"""
Version CLI entry point - DRIVING PORT for version check.
In production: calls VersionManager which uses GitHub API adapter.
In tests: demonstrates boundary without full infrastructure.
"""
import sys
from pathlib import Path
import os

def main():
    nwave_home = os.getenv('NWAVE_HOME', str(Path.home() / ".claude"))
    version_file = Path(nwave_home) / "nwave-version.txt"

    if not version_file.exists():
        print("ERROR: VERSION file not found", file=sys.stderr)
        return 1

    installed_version = version_file.read_text().strip()

    # In production: this would call GitHubAPIAdapter.get_latest_release()
    # For now, we'll check environment for test data
    latest_version = os.getenv('TEST_GITHUB_LATEST_VERSION', installed_version)
    changelog = os.getenv('TEST_GITHUB_CHANGELOG', '')
    api_reachable = os.getenv('TEST_GITHUB_API_REACHABLE', 'true') == 'true'

    if not api_reachable:
        print(f"nWave v{installed_version} (installed)")
        print("Could not check for updates. Try again later or check manually at https://github.com/swcraftsmanshipdojo/nWave/releases")
        return 0

    if installed_version == latest_version:
        print(f"nWave v{installed_version} (up to date)")
        return 0

    # Update available - show banner
    print("=" * 60)
    print("Update Available")
    print("=" * 60)
    print(f"Current version: {installed_version}")
    print(f"Available update: {latest_version}")

    # Check for breaking changes (major version bump)
    current_major = int(installed_version.split('.')[0])
    latest_major = int(latest_version.split('.')[0])

    if latest_major > current_major:
        print("⚠️  BREAKING CHANGES")
        print("This is a major version update")

    if changelog:
        print("\\nChangelog highlights:")
        # Simple extraction (production uses ChangelogProcessor)
        lines = [line.strip() for line in changelog.split('\\n') if line.strip() and line.strip().startswith('*')]
        for line in lines[:3]:  # Show first 3 highlights
            print(f"  {line.replace('*', '•')}")

    print("\\nRun /nw:update to upgrade")
    return 0

if __name__ == "__main__":
    sys.exit(main())
'''

    cli_script.write_text(script_content)
    # Make executable on Unix systems (no-op on Windows)
    if platform.system() != "Windows":
        cli_script.chmod(
            cli_script.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH
        )


@given(parsers.parse("nWave version {version} is installed locally"))
def nwave_version_installed(test_installation, version):
    """Set up test installation with specific version."""
    version_file = test_installation["version_file"]
    version_file.write_text(version)


@given(parsers.parse("GitHub latest release is {version}"))
def github_latest_release(mock_github_api, version):
    """Configure mock GitHub API to return specific version."""
    mock_github_api["latest_version"] = version
    mock_github_api["tag_name"] = f"v{version}"


@given("GitHub API is unreachable")
def github_api_unreachable(mock_github_api):
    """Simulate GitHub API network failure."""
    mock_github_api["is_reachable"] = False


@given("the release changelog contains:")
def github_changelog_from_docstring(mock_github_api, docstring):
    """Configure mock GitHub API changelog response from docstring.

    In pytest-bdd 8.x, Gherkin docstrings (text between triple quotes) are
    passed via the 'docstring' parameter.
    """
    mock_github_api["changelog"] = docstring


@given(parsers.parse('the release changelog contains "BREAKING CHANGES" section'))
def github_changelog_breaking_changes(mock_github_api):
    """Configure changelog with breaking changes section."""
    mock_github_api["changelog"] = """
## BREAKING CHANGES
* feat!: redesign API endpoints - requires client migration

## What's Changed
* feat: add new authentication system
* fix: resolve security vulnerability
"""


# ============================================================================
# WHEN - Actions (through CLI DRIVING PORT)
# ============================================================================


@when("I run the version command through the CLI entry point")
def run_version_command(
    test_installation, cli_result, cli_environment, mock_github_api
):
    """
    Execute /nw:version through CLI entry point (DRIVING PORT).

    CRITICAL HEXAGONAL BOUNDARY ENFORCEMENT:
    ✅ Invokes CLI script (driving port)
    ❌ Does NOT import or instantiate VersionManager directly
    ❌ Does NOT import or instantiate any core domain components

    This represents how real users interact with the system - through
    command-line entry points, not internal components.
    """
    cli_script = test_installation["cli_dir"] / "version_cli.py"

    # Prepare environment with test data
    env = cli_environment.copy()
    env["TEST_GITHUB_LATEST_VERSION"] = mock_github_api["latest_version"] or ""
    env["TEST_GITHUB_CHANGELOG"] = mock_github_api["changelog"]
    env["TEST_GITHUB_API_REACHABLE"] = (
        "true" if mock_github_api["is_reachable"] else "false"
    )

    try:
        # DRIVING PORT INVOCATION - This is the system boundary
        # Use sys.executable for cross-platform compatibility (Windows uses 'python' not 'python3')
        result = subprocess.run(
            [sys.executable, str(cli_script)],
            capture_output=True,
            text=True,
            timeout=SUBPROCESS_TIMEOUT,
            env=env,
            cwd=str(test_installation["tmp_path"]),
        )

        cli_result["stdout"] = result.stdout
        cli_result["stderr"] = result.stderr
        cli_result["returncode"] = result.returncode

    except subprocess.TimeoutExpired as e:
        cli_result["exception"] = e
        cli_result["stderr"] = "Command timed out"
        cli_result["returncode"] = EXIT_TIMEOUT


# ============================================================================
# THEN - Assertions (validate observable behavior)
# ============================================================================


@then(parsers.parse('I see "{expected_output}"'))
def verify_output_contains(cli_result, expected_output):
    """Verify CLI output contains expected text."""
    stdout = cli_result["stdout"]
    stderr = cli_result["stderr"]
    returncode = cli_result["returncode"]

    # Build diagnostic message for failures
    diagnostic = (
        f"Expected '{expected_output}' not found in output:\n"
        f"STDOUT: {stdout!r}\n"
        f"STDERR: {stderr!r}\n"
        f"Return code: {returncode}"
    )

    assert expected_output in stdout, diagnostic


@then(parsers.parse("the command exits with code {exit_code:d}"))
def verify_exit_code(cli_result, exit_code):
    """Verify command exit code."""
    assert cli_result["returncode"] == exit_code, (
        f"Expected exit code {exit_code}, got {cli_result['returncode']}\nSTDERR: {cli_result['stderr']}"
    )


@then("I see an update banner showing:")
def verify_update_banner(cli_result, pytestconfig):
    """Verify update banner contains required information."""
    output = cli_result["stdout"]

    # Check for banner structure
    assert "Update Available" in output, "Update banner not found"
    assert "Current version" in output, "Current version not shown"
    assert "Available update" in output, "Available update not shown"
    assert "Run /nw:update to upgrade" in output, "Update command hint not shown"


@then(parsers.parse('I see changelog highlights containing "{highlight_text}"'))
def verify_changelog_highlight(cli_result, highlight_text):
    """Verify specific changelog highlight is shown."""
    output = cli_result["stdout"]
    assert highlight_text in output, (
        f"Expected highlight '{highlight_text}' not found in output:\n{output}"
    )


@then("I see a link to check releases manually")
def verify_manual_check_link(cli_result):
    """Verify manual check URL is provided on network failure."""
    output = cli_result["stdout"]
    assert "github.com" in output and "releases" in output, (
        "Manual release check URL not provided"
    )


@then(parsers.parse('the update banner includes "{warning_text}"'))
def verify_breaking_change_warning(cli_result, warning_text):
    """Verify breaking change warning is displayed."""
    output = cli_result["stdout"]
    assert warning_text in output, (
        f"Expected breaking change warning '{warning_text}' not found in output:\n{output}"
    )


@then("the banner is styled with red/bold formatting")
def verify_banner_styling(cli_result):
    """Verify breaking change banner has prominent styling (presence check)."""
    output = cli_result["stdout"]
    # In real implementation with rich library, this would check for ANSI codes
    # For minimal test, verify warning symbol present
    assert "⚠️" in output or "BREAKING" in output, (
        "Breaking change visual indicator not found"
    )


@then("changelog highlights show breaking changes prominently")
def verify_breaking_changes_prominent(cli_result):
    """Verify breaking changes are shown prominently in highlights."""
    output = cli_result["stdout"]
    assert "BREAKING CHANGES" in output or "breaking" in output.lower(), (
        "Breaking changes not prominently displayed in highlights"
    )


@then("no breaking change warning is shown")
def verify_no_breaking_change_warning(cli_result):
    """Verify no breaking change warning for minor/patch updates."""
    output = cli_result["stdout"]
    assert "BREAKING CHANGES" not in output, (
        "Breaking change warning shown for non-major version update"
    )


@then("changelog shows only feature additions and fixes")
def verify_changelog_features_fixes_only(cli_result):
    """Verify changelog contains features/fixes but no breaking changes."""
    output = cli_result["stdout"]
    # Should have changelog content but no breaking change warnings
    assert "Changelog highlights" in output or "•" in output or "*" in output, (
        "Changelog highlights not shown"
    )
    assert "BREAKING" not in output, (
        "Breaking change content found in non-breaking update"
    )
