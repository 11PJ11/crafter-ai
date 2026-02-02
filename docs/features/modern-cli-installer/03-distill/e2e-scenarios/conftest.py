"""
Shared Fixtures and Step Definitions for modern_CLI_installer E2E Tests
=======================================================================

This module provides:
1. pytest fixtures for dependency injection
2. Shared step definitions for common Given/When/Then steps
3. Service factories with mock adapters
4. Test context management

Usage:
    pytest docs/features/modern-cli-installer/03-distill/e2e-scenarios/ -v --pspec
"""

import pytest
from pytest_bdd import given, when, then, parsers
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

from typer.testing import CliRunner

# Import the production CLI app
from crafter_ai.cli import app

# Import mock adapters
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "fixtures"))

from test_data import (
    ARTIFACTS,
    PREFLIGHT,
    DOCTOR,
    RELEASE_READINESS,
    BUILD_PHASES,
    WHEEL_VALIDATION,
    VERSION_BUMP,
)
from mock_filesystem import MockFileSystemAdapter
from mock_git import MockGitAdapter
from mock_pipx import MockPipxAdapter
from mock_build import MockBuildAdapter, MockWheelValidator

# CLI runner for invoking production commands
cli_runner = CliRunner()


# =============================================================================
# TEST CONTEXT - Tracks state across steps
# =============================================================================

@dataclass
class TestContext:
    """
    Mutable test context passed between steps.

    This dataclass tracks the state of the test scenario,
    allowing steps to share information and verify outcomes.
    """

    # Environment
    python_version: str = ARTIFACTS.python_version
    ci_mode: bool = False
    environment_vars: Dict[str, str] = field(default_factory=dict)

    # Pre-flight results
    preflight_passed: bool = False
    preflight_results: List[Dict[str, Any]] = field(default_factory=list)

    # Version resolution results
    bump_type: Optional[str] = None
    current_version: str = ARTIFACTS.base_version
    new_version: Optional[str] = None
    candidate_version: Optional[str] = None

    # Build results
    build_completed: bool = False
    build_success: bool = False
    wheel_path: Optional[str] = None
    build_duration: float = 0.0
    build_phases: List[Dict[str, Any]] = field(default_factory=list)

    # Wheel validation results
    wheel_validated: bool = False
    wheel_validation_passed: bool = False
    agent_count: int = 0
    command_count: int = 0
    template_count: int = 0

    # Install results
    install_completed: bool = False
    install_success: bool = False
    install_path: str = ARTIFACTS.install_path

    # Doctor results
    doctor_ran: bool = False
    doctor_status: Optional[str] = None
    doctor_checks: List[Dict[str, Any]] = field(default_factory=list)

    # Release readiness results
    release_readiness_ran: bool = False
    release_readiness_status: Optional[str] = None

    # User interactions
    user_inputs: List[str] = field(default_factory=list)
    prompts_shown: List[str] = field(default_factory=list)

    # Output capture
    messages: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)

    # Command results
    command_executed: Optional[str] = None
    exit_code: int = 0


# =============================================================================
# PYTEST FIXTURES
# =============================================================================

@pytest.fixture
def test_context() -> TestContext:
    """Provide fresh test context for each scenario."""
    return TestContext()


@pytest.fixture
def mock_filesystem() -> MockFileSystemAdapter:
    """Provide mock file system adapter."""
    mock = MockFileSystemAdapter()
    mock.setup_valid_repo()
    return mock


@pytest.fixture
def mock_git() -> MockGitAdapter:
    """Provide mock git adapter."""
    return MockGitAdapter()


@pytest.fixture
def mock_pipx() -> MockPipxAdapter:
    """Provide mock pipx adapter."""
    mock = MockPipxAdapter()
    mock.setup_available()
    return mock


@pytest.fixture
def mock_build() -> MockBuildAdapter:
    """Provide mock build adapter."""
    mock = MockBuildAdapter()
    mock.setup_available()
    return mock


@pytest.fixture
def mock_wheel_validator() -> MockWheelValidator:
    """Provide mock wheel validator."""
    return MockWheelValidator()


# =============================================================================
# SHARED GIVEN STEPS - Background
# =============================================================================

@given("the developer has a terminal open")
def developer_has_terminal(test_context: TestContext):
    """Background step - terminal is always available."""
    pass


@given("the developer is in the nWave project root directory")
def developer_in_project_root(test_context: TestContext, mock_filesystem: MockFileSystemAdapter):
    """Background step - set up project root."""
    mock_filesystem.setup_valid_repo()


@given("the user has a terminal open")
def user_has_terminal(test_context: TestContext):
    """Background step for Journey 3 - terminal is always available."""
    pass


@given(parsers.parse("Python {version} is installed"))
def python_installed(test_context: TestContext, version: str):
    """Set Python version in test context."""
    test_context.python_version = version


@given("the user has Python 3.12.1 installed")
def user_has_python(test_context: TestContext):
    """Background step for Journey 3."""
    test_context.python_version = ARTIFACTS.python_version


@given("the user has Claude Code installed")
def user_has_claude_code(test_context: TestContext, mock_filesystem: MockFileSystemAdapter):
    """Background step for Journey 3."""
    mock_filesystem.directories.add("~/.claude")
    mock_filesystem.writable_paths.add("~/.claude")


@given(parsers.parse("pipx {version} is installed and in PATH"))
def pipx_installed_version(test_context: TestContext, mock_pipx: MockPipxAdapter, version: str):
    """Set pipx version in test context."""
    mock_pipx.setup_available(version.replace("v", ""))


@given(parsers.parse("the user has pipx {version} installed"))
def user_has_pipx(test_context: TestContext, mock_pipx: MockPipxAdapter, version: str):
    """Set pipx version for Journey 3."""
    mock_pipx.setup_available(version.replace("v", ""))


# =============================================================================
# SHARED GIVEN STEPS - Pre-flight Setup
# =============================================================================

@given(parsers.parse("the build package {version} is installed"))
def build_package_installed(mock_build: MockBuildAdapter, version: str):
    """Configure build package as installed."""
    mock_build.setup_available(version.replace("v", ""))


@given("the build package is NOT installed")
def build_package_not_installed(mock_build: MockBuildAdapter):
    """Configure build package as not installed."""
    mock_build.setup_unavailable()


@given(parsers.parse('pyproject.toml is valid with version "{version}"'))
def pyproject_valid(mock_filesystem: MockFileSystemAdapter, version: str):
    """Configure valid pyproject.toml."""
    mock_filesystem.files["pyproject.toml"] = f"""
[project]
name = "nwave"
version = "{version}"
description = "nWave Framework"
[project.scripts]
nw = "nWave.cli:main"
"""


@given("pyproject.toml exists and is valid with version \"1.3.0\"")
def pyproject_exists_valid(mock_filesystem: MockFileSystemAdapter):
    """Shorthand for valid pyproject.toml."""
    pyproject_valid(mock_filesystem, "1.3.0")


@given("pyproject.toml does NOT exist")
def pyproject_missing(mock_filesystem: MockFileSystemAdapter):
    """Configure missing pyproject.toml."""
    mock_filesystem.setup_missing_pyproject()


@given(parsers.parse("pyproject.toml has a syntax error on line {line:d}"))
def pyproject_invalid(mock_filesystem: MockFileSystemAdapter, line: int):
    """Configure invalid pyproject.toml."""
    mock_filesystem.setup_invalid_pyproject(line)


@given(parsers.parse("the nWave/ source directory exists with {count:d} agents"))
def source_dir_exists_with_agents(mock_filesystem: MockFileSystemAdapter, count: int):
    """Configure source directory with agent count."""
    mock_filesystem.directories.add("nWave")
    mock_filesystem.directories.add("nWave/agents")
    mock_filesystem.file_counts["nWave/agents"] = count


@given("the nWave/ source directory exists")
def source_dir_exists(mock_filesystem: MockFileSystemAdapter):
    """Configure source directory exists."""
    mock_filesystem.directories.add("nWave")
    mock_filesystem.directories.add("nWave/agents")


@given("the nWave/ source directory does NOT exist")
def source_dir_missing(mock_filesystem: MockFileSystemAdapter):
    """Configure missing source directory."""
    mock_filesystem.setup_missing_source_dir()


@given("the dist/ directory is writable")
def dist_writable(mock_filesystem: MockFileSystemAdapter):
    """Configure writable dist directory."""
    mock_filesystem.directories.add("dist")
    mock_filesystem.writable_paths.add("dist")


@given("~/.claude is writable")
def claude_dir_writable(mock_filesystem: MockFileSystemAdapter):
    """Configure writable Claude directory."""
    mock_filesystem.directories.add("~/.claude")
    mock_filesystem.writable_paths.add("~/.claude")


@given("~/.claude directory is writable")
def claude_dir_writable_alt(mock_filesystem: MockFileSystemAdapter):
    """Alternative phrasing for writable Claude directory."""
    claude_dir_writable(mock_filesystem)


@given("~/.claude directory is NOT writable")
def claude_dir_not_writable(mock_filesystem: MockFileSystemAdapter):
    """Configure unwritable Claude directory."""
    mock_filesystem.setup_unwritable_claude_dir()


@given("pipx is NOT installed")
def pipx_not_installed(mock_pipx: MockPipxAdapter):
    """Configure pipx as not available."""
    mock_pipx.setup_unavailable()


# =============================================================================
# SHARED GIVEN STEPS - Version and Git
# =============================================================================

@given(parsers.parse('there are commits with "{prefix}" prefix since last tag'))
def commits_with_prefix(mock_git: MockGitAdapter, prefix: str):
    """Configure commits with specific prefix."""
    if prefix == "feat:":
        mock_git.setup_feature_commits()
    elif prefix == "fix:":
        mock_git.setup_fix_commits()
    elif "BREAKING" in prefix:
        mock_git.setup_breaking_change_commits()


@given('there are commits with "BREAKING CHANGE:" since last tag')
def commits_breaking(mock_git: MockGitAdapter):
    """Configure breaking change commits."""
    mock_git.setup_breaking_change_commits()


@given('there are only commits with "fix:" prefix since last tag')
def commits_fix_only(mock_git: MockGitAdapter):
    """Configure fix-only commits."""
    mock_git.setup_fix_commits()


@given("there are no commits since the last tag")
def no_commits_since_tag(mock_git: MockGitAdapter):
    """Configure no commits since tag."""
    mock_git.setup_no_commits_since_tag()


@given(parsers.parse('the current version in pyproject.toml is "{version}"'))
def current_version_in_pyproject(test_context: TestContext, mock_filesystem: MockFileSystemAdapter, version: str):
    """Set current version in pyproject.toml."""
    test_context.current_version = version
    pyproject_valid(mock_filesystem, version)


@given(parsers.parse('the current version is "{version}"'))
def current_version(test_context: TestContext, version: str):
    """Set current version in context."""
    test_context.current_version = version


# =============================================================================
# SHARED GIVEN STEPS - Wheel and Install
# =============================================================================

@given(parsers.parse('a wheel exists at "{wheel_path}"'))
def wheel_exists(mock_filesystem: MockFileSystemAdapter, wheel_path: str):
    """Configure existing wheel file."""
    mock_filesystem.setup_existing_wheel(wheel_path)


@given("no wheel exists in dist/")
def no_wheel_exists(mock_filesystem: MockFileSystemAdapter):
    """Ensure no wheel in dist."""
    # Remove any wheel files
    to_remove = [f for f in mock_filesystem.files if f.endswith(".whl")]
    for f in to_remove:
        del mock_filesystem.files[f]


@given(parsers.parse('a wheel has been built at "{wheel_path}"'))
def wheel_built(test_context: TestContext, mock_filesystem: MockFileSystemAdapter, wheel_path: str):
    """Configure built wheel."""
    mock_filesystem.setup_existing_wheel(wheel_path)
    test_context.wheel_path = wheel_path
    test_context.build_completed = True


@given("pre-flight checks have passed")
def preflight_passed(test_context: TestContext):
    """Mark pre-flight as passed."""
    test_context.preflight_passed = True


@given("the candidate has been installed successfully")
def candidate_installed(test_context: TestContext):
    """Mark candidate as installed."""
    test_context.install_completed = True
    test_context.install_success = True


@given("no previous nWave installation exists")
def no_previous_install(mock_filesystem: MockFileSystemAdapter):
    """Ensure no previous installation."""
    mock_filesystem.directories.discard("~/.claude/agents/nw")


# =============================================================================
# SHARED WHEN STEPS
# =============================================================================

@when(parsers.parse('the developer runs "{command}"'))
def developer_runs_command(test_context: TestContext, command: str):
    """Execute command via production CLI."""
    test_context.command_executed = command
    # Parse command into args (remove 'crafter-ai' prefix if present)
    args = command.replace("crafter-ai ", "").split()
    result = cli_runner.invoke(app, args)
    test_context.exit_code = result.exit_code
    if result.output:
        test_context.messages.append(result.output)
    if result.exception and not isinstance(result.exception, SystemExit):
        test_context.errors.append(str(result.exception))


@when(parsers.parse('the user runs "{command}"'))
def user_runs_command(test_context: TestContext, command: str):
    """Execute command for user via production CLI (Journey 3)."""
    test_context.command_executed = command
    # Parse command into args (remove 'crafter-ai' prefix if present)
    args = command.replace("crafter-ai ", "").split()
    result = cli_runner.invoke(app, args)
    test_context.exit_code = result.exit_code
    if result.output:
        test_context.messages.append(result.output)
    if result.exception and not isinstance(result.exception, SystemExit):
        test_context.errors.append(str(result.exception))


@when("the pre-flight checks run")
def preflight_runs(test_context: TestContext):
    """Run pre-flight checks via production CLI."""
    # Pre-flight checks are part of install-nwave command
    # For isolated testing, we run nw doctor which performs similar checks
    result = cli_runner.invoke(app, ["nw", "doctor"])
    test_context.exit_code = result.exit_code
    test_context.preflight_passed = result.exit_code == 0
    if result.output:
        test_context.messages.append(result.output)


@when("the version resolution runs")
def version_resolution_runs(test_context: TestContext):
    """Run version resolution."""
    raise NotImplementedError(
        "Production code needed: Execute VersionBumpService.analyze_commits()"
    )


@when("the build process runs")
def build_runs(test_context: TestContext):
    """Run build process."""
    raise NotImplementedError(
        "Production code needed: Execute BuildService.build()"
    )


@when("the wheel validation runs")
def wheel_validation_runs(test_context: TestContext):
    """Run wheel validation."""
    raise NotImplementedError(
        "Production code needed: Execute WheelValidator.validate()"
    )


@when("the success summary displays")
def summary_displays(test_context: TestContext):
    """Display success summary."""
    raise NotImplementedError(
        "Production code needed: Display build summary via CLI adapter"
    )


@when("the doctor verification runs")
def doctor_runs(test_context: TestContext):
    """Run doctor verification via production CLI."""
    result = cli_runner.invoke(app, ["nw", "doctor"])
    test_context.doctor_ran = True
    test_context.exit_code = result.exit_code
    test_context.doctor_status = "healthy" if result.exit_code == 0 else "unhealthy"
    if result.output:
        test_context.messages.append(result.output)


@when(parsers.parse('the developer types "{input}"'))
def developer_types(test_context: TestContext, input: str):
    """Record user input."""
    test_context.user_inputs.append(input)


@when(parsers.parse('the user types "{input}"'))
def user_types(test_context: TestContext, input: str):
    """Record user input for Journey 3."""
    test_context.user_inputs.append(input)


@when('the developer types "Y" or presses Enter')
def developer_accepts(test_context: TestContext):
    """User accepts prompt."""
    test_context.user_inputs.append("Y")


@when('the user types "Y" or presses Enter')
def user_accepts(test_context: TestContext):
    """User accepts prompt for Journey 3."""
    test_context.user_inputs.append("Y")


# =============================================================================
# SHARED THEN STEPS
# =============================================================================

@then("the pre-flight checks should all pass")
def all_preflight_pass(test_context: TestContext):
    """Assert all pre-flight checks passed."""
    assert test_context.preflight_passed, (
        f"Pre-flight checks should pass. Exit code: {test_context.exit_code}, "
        f"Messages: {test_context.messages}"
    )


@then(parsers.parse('the check should display "{expected}"'))
def check_displays(test_context: TestContext, expected: str):
    """Assert check displayed expected message."""
    output = "\n".join(test_context.messages)
    assert expected in output, (
        f"Expected '{expected}' in output. Got: {output}"
    )


@then(parsers.parse('the pre-flight check should fail for "{check_name}"'))
def preflight_fails_for(test_context: TestContext, check_name: str):
    """Assert pre-flight failed for specific check."""
    assert not test_context.preflight_passed, (
        f"Pre-flight should fail for '{check_name}'. "
        f"Exit code: {test_context.exit_code}"
    )
    output = "\n".join(test_context.messages)
    assert check_name.lower() in output.lower(), (
        f"Expected check '{check_name}' mentioned in output. Got: {output}"
    )


@then(parsers.parse('the error should display "{expected}"'))
def error_displays(test_context: TestContext, expected: str):
    """Assert error message displayed."""
    all_output = "\n".join(test_context.messages + test_context.errors)
    assert expected in all_output, (
        f"Expected error '{expected}' in output. Got: {all_output}"
    )


@then(parsers.parse('the status should show "{status}"'))
def status_shows(test_context: TestContext, status: str):
    """Assert status displayed."""
    output = "\n".join(test_context.messages)
    assert status.lower() in output.lower(), (
        f"Expected status '{status}' in output. Got: {output}"
    )


@then(parsers.parse('exit code should be {code:d} on success'))
def exit_code_on_success(test_context: TestContext, code: int):
    """Assert exit code on success."""
    assert test_context.exit_code == code, (
        f"Expected exit code {code}, got {test_context.exit_code}"
    )


@then(parsers.parse("exit code should be {code:d}"))
def exit_code(test_context: TestContext, code: int):
    """Assert specific exit code."""
    assert test_context.exit_code == code, (
        f"Expected exit code {code}, got {test_context.exit_code}"
    )


# =============================================================================
# TEST DATA FIXTURES (for parametrized tests)
# =============================================================================

@pytest.fixture
def test_artifacts():
    """Provide standardized test artifacts."""
    return ARTIFACTS


@pytest.fixture
def preflight_data():
    """Provide pre-flight check test data."""
    return PREFLIGHT


@pytest.fixture
def doctor_data():
    """Provide doctor check test data."""
    return DOCTOR


@pytest.fixture
def release_readiness_data():
    """Provide release readiness test data."""
    return RELEASE_READINESS


@pytest.fixture
def build_phases_data():
    """Provide build phases test data."""
    return BUILD_PHASES


@pytest.fixture
def wheel_validation_data():
    """Provide wheel validation test data."""
    return WHEEL_VALIDATION


@pytest.fixture
def version_bump_data():
    """Provide version bump test data."""
    return VERSION_BUMP
