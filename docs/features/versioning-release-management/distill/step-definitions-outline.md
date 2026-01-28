# Step Definitions Outline - nWave Versioning and Release Management

## Document Metadata

| Field | Value |
|-------|-------|
| Feature | nWave Versioning and Release Management |
| Wave | DISTILL |
| Author | Quinn (acceptance-designer) |
| Date | 2026-01-28 |
| Version | 1.0.0 |

---

## Hexagonal Architecture Boundary Enforcement

### Critical Rule: Driving Port Invocation Only

All step definitions MUST invoke through CLI entry points (driving ports). Direct import of internal components is FORBIDDEN.

```python
# CORRECT: Invoke through CLI entry point
result = subprocess.run(
    [sys.executable, "nwave_cli.py", "version"],
    capture_output=True,
    text=True,
    cwd=str(repo_path)
)

# FORBIDDEN: Direct internal component import
from nWave.core.version_management.version_comparator import VersionComparator
from nWave.domain.backup_policy import BackupPolicy
```

### Adapter Mocking Strategy

Mock adapters at external system boundaries only:

| Adapter | Mock Strategy |
|---------|---------------|
| `GitHubAPIAdapter` | HTTP mock returning configured release metadata |
| `DownloadAdapter` | Local test server providing test assets |
| `FileSystemAdapter` | Isolated temp directory operations |
| `GitAdapter` | Mock git commands or isolated test repository |
| `ChecksumAdapter` | Real implementation with test checksums |

---

## Test Environment Setup

### conftest.py - Shared Fixtures

```python
"""
Shared fixtures for acceptance tests.
All fixtures support hexagonal architecture by providing
isolated environments that tests invoke through CLI entry points.
"""
import pytest
import tempfile
import shutil
import subprocess
import sys
from pathlib import Path
from datetime import datetime, timedelta
from http.server import HTTPServer, SimpleHTTPRequestHandler
import threading
import json


@pytest.fixture(scope="function")
def isolated_claude_dir(tmp_path):
    """
    Create isolated ~/.claude/ directory for test isolation.

    Returns:
        Path: Path to temporary ~/.claude/ equivalent
    """
    claude_dir = tmp_path / ".claude"
    claude_dir.mkdir(parents=True)

    # Create standard nWave directory structure
    (claude_dir / "agents" / "nw").mkdir(parents=True)
    (claude_dir / "commands" / "nw").mkdir(parents=True)

    return claude_dir


@pytest.fixture(scope="function")
def isolated_repo_dir(tmp_path):
    """
    Create isolated repository directory for build tests.

    Returns:
        Path: Path to temporary repository
    """
    repo_dir = tmp_path / "nwave-repo"
    repo_dir.mkdir(parents=True)

    # Initialize minimal git repository
    subprocess.run(["git", "init"], cwd=repo_dir, check=True, capture_output=True)
    subprocess.run(
        ["git", "config", "user.email", "test@example.com"],
        cwd=repo_dir, check=True, capture_output=True
    )
    subprocess.run(
        ["git", "config", "user.name", "Test User"],
        cwd=repo_dir, check=True, capture_output=True
    )

    return repo_dir


@pytest.fixture(scope="function")
def cli_entry_point(isolated_repo_dir):
    """
    Provide path to CLI entry point for driving port invocation.

    CRITICAL: All tests MUST invoke through this entry point,
    never through direct internal imports.
    """
    # In real implementation, this points to the actual CLI module
    return isolated_repo_dir / "nwave_cli.py"


@pytest.fixture(scope="function")
def mock_github_api():
    """
    Mock GitHub API responses for release metadata.

    Usage in steps:
        mock_github_api.set_latest_release("1.3.0", checksum="abc123")
    """
    class MockGitHubAPI:
        def __init__(self):
            self.latest_version = None
            self.checksum = None
            self.is_available = True
            self.rate_limited = False

        def set_latest_release(self, version, checksum=""):
            self.latest_version = version
            self.checksum = checksum

        def set_unavailable(self):
            self.is_available = False

        def set_rate_limited(self):
            self.rate_limited = True

        def get_response(self):
            if self.rate_limited:
                return {"status": 403, "headers": {"X-RateLimit-Remaining": "0"}}
            if not self.is_available:
                return {"status": 503, "error": "Service unavailable"}
            return {
                "status": 200,
                "tag_name": f"v{self.latest_version}",
                "assets": [{
                    "name": "nwave-release.tar.gz",
                    "browser_download_url": f"https://mock/releases/{self.latest_version}",
                    "checksum": self.checksum
                }]
            }

    return MockGitHubAPI()


@pytest.fixture(scope="function")
def mock_download_server(tmp_path):
    """
    Local HTTP server for mocking release asset downloads.

    Provides:
        - Valid release assets with correct checksums
        - Corrupted assets for checksum validation tests
        - Network failure simulation
    """
    class DownloadServer:
        def __init__(self, serve_dir):
            self.serve_dir = serve_dir
            self.server = None
            self.thread = None
            self.simulate_failure = False

        def start(self, port=8765):
            handler = SimpleHTTPRequestHandler
            handler.directory = str(self.serve_dir)
            self.server = HTTPServer(("localhost", port), handler)
            self.thread = threading.Thread(target=self.server.serve_forever)
            self.thread.daemon = True
            self.thread.start()
            return f"http://localhost:{port}"

        def stop(self):
            if self.server:
                self.server.shutdown()

        def create_valid_asset(self, version, checksum):
            """Create a valid release asset for download tests."""
            asset_path = self.serve_dir / f"nwave-{version}.tar.gz"
            asset_path.write_bytes(b"mock release content")
            return asset_path

        def create_corrupted_asset(self, version):
            """Create corrupted asset for checksum validation tests."""
            asset_path = self.serve_dir / f"nwave-{version}.tar.gz"
            asset_path.write_bytes(b"corrupted content")
            return asset_path

    server = DownloadServer(tmp_path / "downloads")
    (tmp_path / "downloads").mkdir()
    yield server
    server.stop()


@pytest.fixture(scope="function")
def mock_test_runner():
    """
    Mock test runner for build tests.

    Controls test pass/fail behavior for forge command testing.
    """
    class MockTestRunner:
        def __init__(self):
            self.tests_pass = True
            self.failure_count = 0

        def set_tests_pass(self):
            self.tests_pass = True
            self.failure_count = 0

        def set_tests_fail(self, count=1):
            self.tests_pass = False
            self.failure_count = count

        def get_result(self):
            if self.tests_pass:
                return {"exit_code": 0, "output": "All tests passed"}
            return {
                "exit_code": 1,
                "output": f"{self.failure_count} test(s) failed"
            }

    return MockTestRunner()


@pytest.fixture(scope="function")
def backup_dirs(tmp_path):
    """
    Fixture for managing backup directories in tests.
    """
    class BackupManager:
        def __init__(self, base_path):
            self.base_path = base_path

        def create_backup(self, timestamp_str):
            """Create a backup directory with given timestamp."""
            backup_path = self.base_path / f".claude.backup.{timestamp_str}"
            backup_path.mkdir(parents=True)
            return backup_path

        def list_backups(self):
            """List all backup directories."""
            return sorted(self.base_path.glob(".claude.backup.*"))

        def count_backups(self):
            """Count number of backup directories."""
            return len(self.list_backups())

    return BackupManager(tmp_path)
```

---

## Step Definitions by Feature

### US-001: Check Installed Version

```python
"""
Step definitions for US-001: Check Installed Version

HEXAGONAL BOUNDARY: All steps invoke through CLI entry point.
No direct imports of internal version management components.
"""
import subprocess
import sys
from datetime import datetime, timedelta
from behave import given, when, then


# ============================================================================
# GIVEN Steps - Setup Test State
# ============================================================================

@given('a clean test environment with isolated ~/.claude/ directory')
def step_clean_test_environment(context):
    """
    Setup isolated test environment.

    Implementation:
        - Create temp directory structure
        - Set environment variable to override ~/.claude/ location
        - Ensure clean state for each test
    """
    context.test_claude_dir = context.isolated_claude_dir
    context.env = {"NWAVE_HOME": str(context.test_claude_dir)}


@given('the nWave CLI is available at the driving port entry point')
def step_cli_available(context):
    """
    Verify CLI entry point exists and is executable.

    CRITICAL: Tests MUST use this entry point, never internal imports.
    """
    context.cli_path = context.cli_entry_point
    assert context.cli_path.exists(), "CLI entry point must exist"


@given('{user} has nWave v{version} installed in the test ~/.claude/ directory')
def step_nwave_installed(context, user, version):
    """
    Setup nWave installation with specific version.

    Creates:
        - VERSION file with specified version
        - Minimal nWave directory structure
    """
    context.current_user = user
    context.installed_version = version

    # Create VERSION file - the source of truth for installed version
    version_file = context.test_claude_dir / "VERSION"
    version_file.write_text(version)


@given('the VERSION file contains "{version}"')
def step_version_file_contains(context, version):
    """Write specific version to VERSION file."""
    version_file = context.test_claude_dir / "VERSION"
    version_file.write_text(version)


@given('the GitHub API returns v{version} as the latest release')
def step_github_returns_version(context, version):
    """
    Configure mock GitHub API to return specific version.

    Uses MockGitHubAPI fixture to configure response.
    """
    context.mock_github_api.set_latest_release(version)
    context.expected_latest_version = version


@given('the GitHub API returns v{version} as the latest release with SHA256 checksum "{checksum}"')
def step_github_returns_version_with_checksum(context, version, checksum):
    """Configure mock GitHub API with version and checksum."""
    context.mock_github_api.set_latest_release(version, checksum=checksum)
    context.expected_latest_version = version
    context.expected_checksum = checksum


@given('network connectivity is unavailable for GitHub API')
def step_network_unavailable(context):
    """Configure mock to simulate network unavailability."""
    context.mock_github_api.set_unavailable()


@given('the watermark file shows last_check was {hours:d} hours ago')
def step_watermark_stale(context, hours):
    """
    Create watermark file with timestamp in the past.

    Used to test daily auto-check behavior.
    """
    watermark_path = context.test_claude_dir / "nwave.update"
    past_time = datetime.utcnow() - timedelta(hours=hours)
    watermark_content = f"""last_check: {past_time.isoformat()}Z
latest_version: 1.2.0
"""
    watermark_path.write_text(watermark_content)


@given('the watermark file contains latest_version "{version}"')
def step_watermark_version(context, version):
    """Set latest_version in watermark file."""
    watermark_path = context.test_claude_dir / "nwave.update"
    now = datetime.utcnow()
    watermark_content = f"""last_check: {now.isoformat()}Z
latest_version: {version}
"""
    watermark_path.write_text(watermark_content)


@given('the GitHub API returns HTTP 403 with rate limit headers')
def step_github_rate_limited(context):
    """Configure mock to simulate rate limiting."""
    context.mock_github_api.set_rate_limited()


@given('the VERSION file does not exist')
def step_version_file_missing(context):
    """Ensure VERSION file does not exist (incomplete installation)."""
    version_file = context.test_claude_dir / "VERSION"
    if version_file.exists():
        version_file.unlink()


# ============================================================================
# WHEN Steps - Execute Actions Through CLI
# ============================================================================

@when('{user} runs the /nw:version command through the CLI entry point')
def step_run_version_command(context, user):
    """
    Execute version command through CLI entry point.

    CRITICAL: This invokes the driving port, NOT internal components.

    Implementation must:
        - Use subprocess to invoke CLI
        - Pass environment variables for test isolation
        - Capture stdout, stderr, and exit code
    """
    result = subprocess.run(
        [sys.executable, str(context.cli_path), "version"],
        capture_output=True,
        text=True,
        env={**context.env, "MOCK_GITHUB_RESPONSE": context.mock_github_api.get_response()}
    )

    context.cli_result = {
        "stdout": result.stdout,
        "stderr": result.stderr,
        "exit_code": result.returncode
    }


# ============================================================================
# THEN Steps - Verify Outcomes
# ============================================================================

@then('the output displays "{expected_message}"')
def step_output_displays(context, expected_message):
    """
    Verify CLI output contains expected message.

    Validates observable behavior through CLI output.
    """
    assert expected_message in context.cli_result["stdout"], \
        f"Expected '{expected_message}' in output. Got: {context.cli_result['stdout']}"


@then('the watermark file ~/.claude/nwave.update is updated with current timestamp')
def step_watermark_updated(context):
    """
    Verify watermark file was updated.

    Validates file system side effect through observation.
    """
    watermark_path = context.test_claude_dir / "nwave.update"
    assert watermark_path.exists(), "Watermark file should exist"

    content = watermark_path.read_text()
    assert "last_check:" in content, "Watermark should contain last_check"

    # Verify timestamp is recent (within last minute)
    # Parse and validate timestamp is close to now


@then('the watermark file contains latest_version "{version}"')
def step_watermark_contains_version(context, version):
    """Verify watermark file contains expected version."""
    watermark_path = context.test_claude_dir / "nwave.update"
    content = watermark_path.read_text()
    assert f"latest_version: {version}" in content, \
        f"Expected latest_version: {version} in watermark"


@then('no error is thrown')
def step_no_error(context):
    """Verify no error occurred during execution."""
    assert not context.cli_result["stderr"], \
        f"Expected no errors. Got: {context.cli_result['stderr']}"


@then('the CLI exit code is {expected_code}')
def step_exit_code(context, expected_code):
    """Verify CLI exit code matches expected."""
    expected = 0 if expected_code == "0" else int(expected_code)
    assert context.cli_result["exit_code"] == expected, \
        f"Expected exit code {expected}. Got: {context.cli_result['exit_code']}"


@then('the CLI exit code is non-zero')
def step_exit_code_nonzero(context):
    """Verify CLI exited with error code."""
    assert context.cli_result["exit_code"] != 0, \
        f"Expected non-zero exit code. Got: {context.cli_result['exit_code']}"


@then('no GitHub API call is made')
def step_no_api_call(context):
    """
    Verify no GitHub API call was made.

    Implementation: Check mock call count or request log.
    """
    # Implementation depends on mock tracking
    pass


@then('an error displays "{expected_error}"')
def step_error_displays(context, expected_error):
    """Verify error message in output."""
    output = context.cli_result["stdout"] + context.cli_result["stderr"]
    assert expected_error in output, \
        f"Expected error '{expected_error}'. Got: {output}"


@then('the system checks GitHub Releases')
def step_system_checks_github(context):
    """Verify GitHub API was called."""
    # Implementation: Verify mock was called
    pass
```

### US-002: Update to Latest Release

```python
"""
Step definitions for US-002: Update nWave to Latest Release

HEXAGONAL BOUNDARY: All update operations invoke through CLI.
Backup creation, download, validation all happen through driving port.
"""

@given('a mock download server is available for release assets')
def step_download_server_available(context):
    """Start mock download server for release assets."""
    context.download_url = context.mock_download_server.start()


@given('the download server provides a valid release asset matching the checksum')
def step_valid_download_asset(context):
    """Configure download server with valid asset."""
    context.mock_download_server.create_valid_asset(
        context.expected_latest_version,
        context.expected_checksum
    )


@given('the download server simulates a network failure mid-download')
def step_download_failure(context):
    """Configure download server to fail mid-download."""
    context.mock_download_server.simulate_failure = True


@given('the download server provides a corrupted file with different checksum')
def step_corrupted_download(context):
    """Configure download server with corrupted asset."""
    context.mock_download_server.create_corrupted_asset(
        context.expected_latest_version
    )


@given('3 existing backups exist at {backup_paths}')
def step_existing_backups(context, backup_paths):
    """Create existing backup directories for rotation testing."""
    timestamps = ["20260124120000", "20260125120000", "20260126120000"]
    for ts in timestamps:
        context.backup_dirs.create_backup(ts)


@given('{user} has custom agents in ~/.claude/agents/{agent_name}/')
def step_custom_agent(context, user, agent_name):
    """Create custom (non-nWave) agent for preservation testing."""
    agent_path = context.test_claude_dir / "agents" / agent_name
    agent_path.mkdir(parents=True)
    (agent_path / "agent.md").write_text("Custom agent content")
    context.custom_agents = context.custom_agents if hasattr(context, 'custom_agents') else []
    context.custom_agents.append(agent_path)


@given('{user} has custom commands in ~/.claude/commands/{command_name}/')
def step_custom_command(context, user, command_name):
    """Create custom (non-nWave) command for preservation testing."""
    command_path = context.test_claude_dir / "commands" / command_name
    command_path.mkdir(parents=True)
    (command_path / "command.md").write_text("Custom command content")
    context.custom_commands = context.custom_commands if hasattr(context, 'custom_commands') else []
    context.custom_commands.append(command_path)


@given('{user} has a local RC version {version} installed')
def step_local_rc_installed(context, user, version):
    """Setup local RC version installation."""
    context.current_user = user
    context.installed_version = version
    version_file = context.test_claude_dir / "VERSION"
    version_file.write_text(version)


@when('{user} runs the /nw:update command through the CLI entry point')
def step_run_update_command(context, user):
    """
    Execute update command through CLI entry point.

    CRITICAL: Invokes driving port for complete update workflow.
    """
    result = subprocess.run(
        [sys.executable, str(context.cli_path), "update"],
        capture_output=True,
        text=True,
        env=context.env,
        input="y\n"  # Default confirmation
    )

    context.cli_result = {
        "stdout": result.stdout,
        "stderr": result.stderr,
        "exit_code": result.returncode
    }


@when('{user} confirms the update when prompted')
def step_confirm_update(context, user):
    """User confirms update prompt."""
    # Handled by input parameter in subprocess call
    pass


@when('{user} confirms with "{response}" when prompted about major version change')
def step_confirm_major_version(context, user, response):
    """Handle major version confirmation."""
    context.confirmation_response = response


@when('{user} denies with "{response}" when prompted about major version change')
def step_deny_major_version(context, user, response):
    """Handle major version denial."""
    context.confirmation_response = response


@then('a full backup is created at ~/.claude.backup.{{timestamp}}/')
def step_backup_created(context):
    """Verify backup was created."""
    backups = context.backup_dirs.list_backups()
    assert len(backups) > 0, "At least one backup should exist"


@then('the release asset is downloaded from the mock server')
def step_asset_downloaded(context):
    """Verify download occurred."""
    # Verify through mock server request log
    pass


@then('the download is validated against SHA256 checksum "{checksum}"')
def step_checksum_validated(context, checksum):
    """Verify checksum validation occurred."""
    # Verify through CLI output or logs
    pass


@then('nWave is updated to v{version} in the test ~/.claude/ directory')
def step_nwave_updated(context, version):
    """Verify installation was updated."""
    version_file = context.test_claude_dir / "VERSION"
    actual_version = version_file.read_text().strip()
    assert actual_version == version, \
        f"Expected version {version}. Got: {actual_version}"


@then('the VERSION file now contains "{version}"')
def step_version_file_updated(context, version):
    """Verify VERSION file content."""
    version_file = context.test_claude_dir / "VERSION"
    actual = version_file.read_text().strip()
    assert actual == version, f"Expected {version}. Got: {actual}"


@then('the VERSION file still contains "{version}"')
def step_version_unchanged(context, version):
    """Verify VERSION file was not modified."""
    version_file = context.test_claude_dir / "VERSION"
    actual = version_file.read_text().strip()
    assert actual == version, f"Expected unchanged {version}. Got: {actual}"


@then('the test ~/.claude/ directory contains the original v{version} installation')
def step_installation_unchanged(context, version):
    """Verify installation was not modified."""
    version_file = context.test_claude_dir / "VERSION"
    actual = version_file.read_text().strip()
    assert actual == version


@then('no partial download files remain')
def step_no_partial_files(context):
    """Verify cleanup of partial downloads."""
    temp_files = list(context.test_claude_dir.parent.glob("*.tmp"))
    assert len(temp_files) == 0, "No temporary files should remain"


@then('the corrupted download is deleted')
def step_corrupted_deleted(context):
    """Verify corrupted download was cleaned up."""
    # Verify through file system check
    pass


@then('the oldest backup {backup_path} is deleted')
def step_oldest_deleted(context, backup_path):
    """Verify oldest backup was removed."""
    path = context.test_claude_dir.parent / backup_path.split("/")[-1]
    assert not path.exists(), f"Oldest backup should be deleted: {path}"


@then('exactly {count:d} backups remain')
def step_backup_count(context, count):
    """Verify exact number of backups."""
    actual_count = context.backup_dirs.count_backups()
    assert actual_count == count, f"Expected {count} backups. Got: {actual_count}"


@then('her custom agent at {path} remains untouched')
def step_custom_agent_preserved(context, path):
    """Verify custom agent was preserved."""
    agent_path = context.test_claude_dir / path.replace("~/.claude/", "")
    assert agent_path.exists(), f"Custom agent should be preserved: {agent_path}"


@then('her custom command at {path} remains untouched')
def step_custom_command_preserved(context, path):
    """Verify custom command was preserved."""
    command_path = context.test_claude_dir / path.replace("~/.claude/", "")
    assert command_path.exists(), f"Custom command should be preserved: {command_path}"


@then('only nWave-prefixed content in ~/.claude/agents/nw/ is replaced')
def step_nw_agents_replaced(context):
    """Verify only nw/ agents were replaced."""
    nw_agents = context.test_claude_dir / "agents" / "nw"
    assert nw_agents.exists(), "nw agents directory should exist"


@then('only nWave-prefixed content in ~/.claude/commands/nw/ is replaced')
def step_nw_commands_replaced(context):
    """Verify only nw/ commands were replaced."""
    nw_commands = context.test_claude_dir / "commands" / "nw"
    assert nw_commands.exists(), "nw commands directory should exist"


@then('no backup is created')
def step_no_backup(context):
    """Verify no new backup was created."""
    # Check backup count unchanged from start of test
    pass


@then('no download occurs')
def step_no_download(context):
    """Verify no download was attempted."""
    # Check mock server request count
    pass


@then('a warning displays "{message}"')
def step_warning_displays(context, message):
    """Verify warning message in output."""
    assert message in context.cli_result["stdout"], \
        f"Expected warning '{message}'. Got: {context.cli_result['stdout']}"


@then('the prompt displays "{prompt}"')
def step_prompt_displays(context, prompt):
    """Verify prompt message."""
    assert prompt in context.cli_result["stdout"]


@then('the update waits for confirmation before proceeding')
def step_update_waits(context):
    """Verify update did not proceed without confirmation."""
    # Implementation: Check that update didn't complete
    pass


@then('the update proceeds')
def step_update_proceeds(context):
    """Verify update completed."""
    assert context.cli_result["exit_code"] == 0


@then('the update is cancelled')
def step_update_cancelled(context):
    """Verify update was cancelled."""
    # Verify VERSION unchanged
    pass


@then('no backup was created')
def step_confirm_no_backup(context):
    """Verify no backup directory was created."""
    backups = context.backup_dirs.list_backups()
    initial_count = getattr(context, 'initial_backup_count', 0)
    assert len(backups) == initial_count
```

### US-003: Build Custom Local Distribution

```python
"""
Step definitions for US-003: Build Custom Local Distribution

HEXAGONAL BOUNDARY: Build operations invoke through CLI.
Test runner, git operations all accessed through driving port.
"""

@given('a clean test environment with isolated repository directory')
def step_repo_environment(context):
    """Setup isolated repository for build tests."""
    context.test_repo_dir = context.isolated_repo_dir
    context.env = {"NWAVE_REPO": str(context.test_repo_dir)}


@given('{user} is working in the test repository')
def step_working_in_repo(context, user):
    """Setup user context for repository."""
    context.current_user = user


@given('the git branch is "{branch}"')
def step_git_branch(context, branch):
    """Set git branch for build tests."""
    subprocess.run(
        ["git", "checkout", "-b", branch],
        cwd=context.test_repo_dir,
        capture_output=True
    )
    context.current_branch = branch


@given('the pyproject.toml contains base version "{version}"')
def step_pyproject_version(context, version):
    """Create pyproject.toml with version."""
    pyproject_path = context.test_repo_dir / "pyproject.toml"
    pyproject_content = f"""[project]
name = "nwave"
version = "{version}"
"""
    pyproject_path.write_text(pyproject_content)
    context.base_version = version


@given('all tests pass when the test runner is invoked')
def step_tests_pass(context):
    """Configure mock test runner for passing tests."""
    context.mock_test_runner.set_tests_pass()


@given('{count:d} tests fail when the test runner is invoked')
def step_tests_fail(context, count):
    """Configure mock test runner for failing tests."""
    context.mock_test_runner.set_tests_fail(count)


@given("today's date is {date}")
def step_set_date(context, date):
    """Set mock date for version generation."""
    context.test_date = date


@given('a previous build created version "{version}" in dist/')
def step_previous_build(context, version):
    """Create dist/ with previous build version."""
    dist_dir = context.test_repo_dir / "dist"
    dist_dir.mkdir(parents=True, exist_ok=True)
    (dist_dir / "VERSION").write_text(version)
    context.previous_version = version


@given('a previous build from yesterday created version "{version}"')
def step_previous_build_yesterday(context, version):
    """Create dist/ with previous day's build."""
    dist_dir = context.test_repo_dir / "dist"
    dist_dir.mkdir(parents=True, exist_ok=True)
    (dist_dir / "VERSION").write_text(version)


@when('{user} runs the /nw:forge command through the CLI entry point')
def step_run_forge(context, user):
    """
    Execute forge command through CLI entry point.

    CRITICAL: Invokes driving port for complete build workflow.
    """
    result = subprocess.run(
        [sys.executable, str(context.cli_path), "forge"],
        capture_output=True,
        text=True,
        env={
            **context.env,
            "MOCK_TEST_RESULT": str(context.mock_test_runner.get_result()),
            "MOCK_DATE": context.test_date if hasattr(context, 'test_date') else ""
        },
        input="n\n"  # Default: don't install after build
    )

    context.cli_result = {
        "stdout": result.stdout,
        "stderr": result.stderr,
        "exit_code": result.returncode
    }


@when('{user} responds "{response}" to the install prompt')
def step_respond_install(context, user, response):
    """Handle install prompt response."""
    context.install_response = response


@then('the dist/ directory is cleaned before build')
def step_dist_cleaned(context):
    """Verify dist/ was cleaned."""
    # Check through CLI output or build log
    pass


@then('the build process runs all tests first')
def step_tests_run_first(context):
    """Verify tests ran before build."""
    assert "Running tests" in context.cli_result["stdout"] or \
           "test" in context.cli_result["stdout"].lower()


@then('dist/ is created with the built distribution')
def step_dist_created(context):
    """Verify dist/ directory was created."""
    dist_dir = context.test_repo_dir / "dist"
    assert dist_dir.exists(), "dist/ directory should be created"


@then('the version is set to "{expected_version}"')
def step_version_set(context, expected_version):
    """Verify RC version in dist/."""
    version_file = context.test_repo_dir / "dist" / "VERSION"
    actual = version_file.read_text().strip()
    assert actual == expected_version, \
        f"Expected version {expected_version}. Got: {actual}"


@then('the version becomes "{expected_version}"')
def step_version_becomes(context, expected_version):
    """Verify version changed to expected value."""
    version_file = context.test_repo_dir / "dist" / "VERSION"
    actual = version_file.read_text().strip()
    assert actual == expected_version


@then('the build aborts with exit code non-zero')
def step_build_aborts(context):
    """Verify build failed with error code."""
    assert context.cli_result["exit_code"] != 0


@then('the dist/ directory is not modified')
def step_dist_unmodified(context):
    """Verify dist/ was not modified."""
    # Compare with state before test
    pass


@then('special characters in the branch name are normalized to hyphens')
def step_branch_normalized(context):
    """Verify branch name normalization."""
    version_file = context.test_repo_dir / "dist" / "VERSION"
    version = version_file.read_text().strip()
    assert "/" not in version, "Slashes should be normalized to hyphens"


@then('the previous dist/ contents are cleaned before the new build')
def step_previous_cleaned(context):
    """Verify previous dist/ was cleaned."""
    # Verify through build log or file timestamps
    pass


@then('no installation to ~/.claude/ occurs')
def step_no_installation(context):
    """Verify no installation happened."""
    # Verify ~/.claude/ unchanged
    pass


@then('the /nw:forge:install command is invoked')
def step_install_invoked(context):
    """Verify install command was triggered."""
    # Verify through CLI output
    pass


@then('the distribution is installed to ~/.claude/')
def step_distribution_installed(context):
    """Verify installation completed."""
    version_file = context.test_claude_dir / "VERSION"
    dist_version = (context.test_repo_dir / "dist" / "VERSION").read_text().strip()
    installed_version = version_file.read_text().strip()
    assert installed_version == dist_version
```

### US-004 and US-005 Step Definitions

Follow the same patterns as above, with:
- All actions through CLI entry points
- Mock adapters for external systems (GitHub CLI, file system)
- Observable outcome verification

---

## Test Isolation Requirements

### Environment Isolation

1. **Temp Directories**: All file operations in pytest tmp_path
2. **Environment Variables**: Override NWAVE_HOME, NWAVE_REPO
3. **Mock External Services**: GitHub API, download server, git

### Cleanup After Tests

```python
@pytest.fixture(autouse=True)
def cleanup_after_test(request, tmp_path):
    """Automatic cleanup after each test."""
    yield
    # Cleanup is automatic with tmp_path fixture

    # Stop any running servers
    if hasattr(request.instance, 'mock_download_server'):
        request.instance.mock_download_server.stop()
```

### Parallel Test Safety

```python
# Each test gets unique identifiers
@pytest.fixture(scope="function")
def unique_test_id():
    """Generate unique ID for test isolation."""
    return f"test_{uuid.uuid4().hex[:8]}"
```

---

## Implementation Notes

### Production Service Integration

Step methods MUST call production services through driving ports:

```python
# CORRECT: Invoke CLI which internally uses production services
result = subprocess.run([sys.executable, "nwave_cli.py", "version"])

# The CLI internally does:
# - VersionService.check_version()
# - GitHubAPIAdapter.get_latest_release()
# - FileSystemAdapter.read_version_file()

# FORBIDDEN: Direct service invocation in tests
# version_service = VersionService()
# result = version_service.check_version()
```

### Assertion Patterns

Focus on observable outcomes:

```python
# CORRECT: Verify observable output
assert "nWave v1.2.3" in context.cli_result["stdout"]

# CORRECT: Verify file system state
assert (context.test_claude_dir / "VERSION").read_text() == "1.3.0"

# FORBIDDEN: Verify internal state
# assert version_service._last_check_time == expected_time
```
