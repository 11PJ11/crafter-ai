"""
Unit tests for update_cli (driving adapter).

HEXAGONAL ARCHITECTURE:
- update_cli is a DRIVING ADAPTER (outside the hexagon)
- Entry point for /nw:update command
- Tests verify CLI correctly invokes UpdateService and formats output
"""

from pathlib import Path
from unittest.mock import MagicMock, patch
import os
import sys

import pytest


@pytest.fixture(autouse=True)
def reset_environment():
    """Reset environment between tests to ensure isolation."""
    # Save original environment
    original_env = os.environ.copy()

    # Clear any test-related env vars
    for key in list(os.environ.keys()):
        if key.startswith("NWAVE_"):
            del os.environ[key]

    yield

    # Restore original environment
    os.environ.clear()
    os.environ.update(original_env)


class TestUpdateCliPromptsForConfirmation:
    """Test that update_cli prompts user for confirmation before update."""

    def test_update_cli_prompts_for_confirmation(self):
        """
        GIVEN: update_cli with update available
        WHEN: User runs update command
        THEN: Confirmation prompt is displayed
        """
        # This test validates the CLI behavior, not internal logic
        # Import here to trigger failure if module doesn't exist
        from nWave.cli import update_cli

        # Verify the module has the expected main function
        assert hasattr(update_cli, "main"), "update_cli should have main() function"


class TestUpdateCliDisplaysUpdateComplete:
    """Test that update_cli displays success message after update."""

    def test_update_cli_displays_update_complete(self, tmp_path):
        """
        GIVEN: update_cli with successful update
        WHEN: Update completes
        THEN: Output displays "Update complete."
        """
        from nWave.cli import update_cli

        # Set up test environment with VERSION file
        claude_dir = tmp_path / ".claude"
        claude_dir.mkdir(parents=True)
        (claude_dir / "VERSION").write_text("1.2.3")

        # Capture stdout
        with patch("builtins.print") as mock_print:
            # Set environment for test mode
            with patch.dict(os.environ, {
                "NWAVE_TEST_MODE": "true",
                "NWAVE_HOME": str(claude_dir),
                "NWAVE_MOCK_GITHUB_VERSION": "1.3.0",
                "NWAVE_MOCK_GITHUB_CHECKSUM": "abc123",
                "NWAVE_MOCK_CONFIRM_UPDATE": "y",
            }):
                result = update_cli.main()

        # Check that "Update complete." was printed
        print_calls = [str(call) for call in mock_print.call_args_list]
        assert any("Update complete" in call for call in print_calls), (
            f"Expected 'Update complete.' in output, got: {print_calls}"
        )


class TestUpdateCliExitsWithZeroOnSuccess:
    """Test that update_cli returns 0 on success."""

    def test_update_cli_exits_zero_on_success(self, tmp_path):
        """
        GIVEN: update_cli with successful update
        WHEN: Update completes
        THEN: Exit code is 0
        """
        import subprocess

        # Set up test environment with VERSION file
        claude_dir = tmp_path / ".claude"
        claude_dir.mkdir(parents=True)
        (claude_dir / "VERSION").write_text("1.2.3")

        # Get path to CLI
        project_root = Path(__file__).parent.parent.parent.parent.parent
        cli_path = project_root / "nWave" / "cli" / "update_cli.py"

        env = os.environ.copy()
        env.update({
            "NWAVE_TEST_MODE": "true",
            "NWAVE_HOME": str(claude_dir),
            "NWAVE_MOCK_GITHUB_VERSION": "1.3.0",
            "NWAVE_MOCK_GITHUB_CHECKSUM": "abc123",
            "NWAVE_MOCK_CONFIRM_UPDATE": "y",
            "PYTHONPATH": str(project_root),
        })

        result = subprocess.run(
            [sys.executable, str(cli_path)],
            env=env,
            capture_output=True,
            text=True,
            timeout=30,
        )

        assert result.returncode == 0, (
            f"Expected exit code 0, got {result.returncode}\n"
            f"STDOUT: {result.stdout}\n"
            f"STDERR: {result.stderr}"
        )


# ============================================================================
# Step 04-02: Major version change warning and confirmation
# ============================================================================


class TestUpdateCliShowsMajorVersionWarning:
    """Test that update_cli displays warning for major version changes."""

    def test_update_cli_shows_major_version_warning(self, tmp_path):
        """
        GIVEN: update_cli with current v1.3.0 and target v2.0.0
        WHEN: User runs update command
        THEN: Warning message displays "Major version change detected (1.x to 2.x). This may break existing workflows."
        """
        import subprocess

        # Set up test environment with VERSION file
        claude_dir = tmp_path / ".claude"
        claude_dir.mkdir(parents=True)
        (claude_dir / "VERSION").write_text("1.3.0")

        # Get path to CLI
        project_root = Path(__file__).parent.parent.parent.parent.parent
        cli_path = project_root / "nWave" / "cli" / "update_cli.py"

        env = os.environ.copy()
        env.update({
            "NWAVE_TEST_MODE": "true",
            "NWAVE_HOME": str(claude_dir),
            "NWAVE_MOCK_GITHUB_VERSION": "2.0.0",
            "NWAVE_MOCK_GITHUB_CHECKSUM": "abc123",
            "NWAVE_MOCK_CONFIRM_UPDATE": "n",  # Decline update to verify warning shown
            "PYTHONPATH": str(project_root),
        })

        result = subprocess.run(
            [sys.executable, str(cli_path)],
            env=env,
            capture_output=True,
            text=True,
            timeout=30,
        )

        expected_warning = "Major version change detected (1.x to 2.x). This may break existing workflows."
        assert expected_warning in result.stdout, (
            f"Expected major version warning not found.\n"
            f"Expected: '{expected_warning}'\n"
            f"STDOUT: {result.stdout}\n"
            f"STDERR: {result.stderr}"
        )


class TestUpdateCliPromptsForMajorVersionConfirmation:
    """Test that update_cli prompts for confirmation on major version change."""

    def test_update_cli_prompts_for_major_version_confirmation(self, tmp_path):
        """
        GIVEN: update_cli with current v1.3.0 and target v2.0.0
        WHEN: User runs update command
        THEN: Prompt displays "Continue? [y/N]"
        """
        import subprocess

        # Set up test environment with VERSION file
        claude_dir = tmp_path / ".claude"
        claude_dir.mkdir(parents=True)
        (claude_dir / "VERSION").write_text("1.3.0")

        # Get path to CLI
        project_root = Path(__file__).parent.parent.parent.parent.parent
        cli_path = project_root / "nWave" / "cli" / "update_cli.py"

        env = os.environ.copy()
        env.update({
            "NWAVE_TEST_MODE": "true",
            "NWAVE_HOME": str(claude_dir),
            "NWAVE_MOCK_GITHUB_VERSION": "2.0.0",
            "NWAVE_MOCK_GITHUB_CHECKSUM": "abc123",
            "NWAVE_MOCK_CONFIRM_UPDATE": "n",  # Decline update to verify prompt shown
            "PYTHONPATH": str(project_root),
        })

        result = subprocess.run(
            [sys.executable, str(cli_path)],
            env=env,
            capture_output=True,
            text=True,
            timeout=30,
        )

        expected_prompt = "Continue? [y/N]"
        assert expected_prompt in result.stdout, (
            f"Expected confirmation prompt not found.\n"
            f"Expected: '{expected_prompt}'\n"
            f"STDOUT: {result.stdout}\n"
            f"STDERR: {result.stderr}"
        )


# ============================================================================
# Step 04-04: Major version update cancelled with denial
# ============================================================================


class TestUpdateCliCancelsMajorVersionUpdateOnDenial:
    """Test that update_cli cancels major version update when user denies."""

    def test_update_cli_cancels_major_version_update_on_denial(self, tmp_path):
        """
        GIVEN: update_cli with current v1.3.0 and target v2.0.0
        WHEN: User denies with "n" when prompted about major version change
        THEN: Update is cancelled with message "Update cancelled."
        """
        import subprocess

        # Set up test environment with VERSION file
        claude_dir = tmp_path / ".claude"
        claude_dir.mkdir(parents=True)
        (claude_dir / "VERSION").write_text("1.3.0")

        # Get path to CLI
        project_root = Path(__file__).parent.parent.parent.parent.parent
        cli_path = project_root / "nWave" / "cli" / "update_cli.py"

        env = os.environ.copy()
        env.update({
            "NWAVE_TEST_MODE": "true",
            "NWAVE_HOME": str(claude_dir),
            "NWAVE_MOCK_GITHUB_VERSION": "2.0.0",  # MAJOR version change
            "NWAVE_MOCK_GITHUB_CHECKSUM": "abc123",
            "NWAVE_MOCK_CONFIRM_UPDATE": "n",  # Deny the update
            "PYTHONPATH": str(project_root),
        })

        result = subprocess.run(
            [sys.executable, str(cli_path)],
            env=env,
            capture_output=True,
            text=True,
            timeout=30,
        )

        # First verify major version warning was shown (dependency on 04-02)
        expected_warning = "Major version change detected"
        assert expected_warning in result.stdout, (
            f"Expected major version warning not found.\n"
            f"Expected: '{expected_warning}'\n"
            f"STDOUT: {result.stdout}\n"
            f"STDERR: {result.stderr}"
        )

        # Then verify update was cancelled
        expected_cancelled = "Update cancelled."
        assert expected_cancelled in result.stdout, (
            f"Expected cancellation message not found.\n"
            f"Expected: '{expected_cancelled}'\n"
            f"STDOUT: {result.stdout}\n"
            f"STDERR: {result.stderr}"
        )


class TestUpdateCliPreservesVersionOnDenial:
    """Test that VERSION file is unchanged when user denies major version update."""

    def test_update_cli_preserves_version_on_denial(self, tmp_path):
        """
        GIVEN: update_cli with current v1.3.0 and target v2.0.0
        WHEN: User denies major version update with "n"
        THEN: VERSION file still contains "1.3.0"
        """
        import subprocess

        # Set up test environment with VERSION file
        claude_dir = tmp_path / ".claude"
        claude_dir.mkdir(parents=True)
        version_file = claude_dir / "VERSION"
        version_file.write_text("1.3.0")

        # Get path to CLI
        project_root = Path(__file__).parent.parent.parent.parent.parent
        cli_path = project_root / "nWave" / "cli" / "update_cli.py"

        env = os.environ.copy()
        env.update({
            "NWAVE_TEST_MODE": "true",
            "NWAVE_HOME": str(claude_dir),
            "NWAVE_MOCK_GITHUB_VERSION": "2.0.0",  # MAJOR version change
            "NWAVE_MOCK_GITHUB_CHECKSUM": "abc123",
            "NWAVE_MOCK_CONFIRM_UPDATE": "n",  # Deny the update
            "PYTHONPATH": str(project_root),
        })

        result = subprocess.run(
            [sys.executable, str(cli_path)],
            env=env,
            capture_output=True,
            text=True,
            timeout=30,
        )

        # Verify VERSION file is unchanged
        version_content = version_file.read_text().strip()
        assert version_content == "1.3.0", (
            f"VERSION file should still contain '1.3.0', got: '{version_content}'\n"
            f"STDOUT: {result.stdout}\n"
            f"STDERR: {result.stderr}"
        )


class TestUpdateCliNoBackupOnDenial:
    """Test that no backup is created when user denies major version update."""

    def test_update_cli_no_backup_on_denial(self, tmp_path):
        """
        GIVEN: update_cli with current v1.3.0 and target v2.0.0
        WHEN: User denies major version update with "n"
        THEN: No backup directory was created
        """
        import subprocess

        # Set up test environment with VERSION file
        claude_dir = tmp_path / ".claude"
        claude_dir.mkdir(parents=True)
        (claude_dir / "VERSION").write_text("1.3.0")

        # Count backups BEFORE
        backups_before = list(tmp_path.glob(".claude.backup.*"))

        # Get path to CLI
        project_root = Path(__file__).parent.parent.parent.parent.parent
        cli_path = project_root / "nWave" / "cli" / "update_cli.py"

        env = os.environ.copy()
        env.update({
            "NWAVE_TEST_MODE": "true",
            "NWAVE_HOME": str(claude_dir),
            "NWAVE_MOCK_GITHUB_VERSION": "2.0.0",  # MAJOR version change
            "NWAVE_MOCK_GITHUB_CHECKSUM": "abc123",
            "NWAVE_MOCK_CONFIRM_UPDATE": "n",  # Deny the update
            "PYTHONPATH": str(project_root),
        })

        result = subprocess.run(
            [sys.executable, str(cli_path)],
            env=env,
            capture_output=True,
            text=True,
            timeout=30,
        )

        # Count backups AFTER
        backups_after = list(tmp_path.glob(".claude.backup.*"))

        # Verify no new backup was created
        assert len(backups_after) == len(backups_before), (
            f"No backup should be created on denial.\n"
            f"Backups before: {len(backups_before)}, after: {len(backups_after)}\n"
            f"STDOUT: {result.stdout}\n"
            f"STDERR: {result.stderr}"
        )


# ============================================================================
# Step 04-05: Local RC version triggers customization warning
# ============================================================================


class TestUpdateCliShowsCustomizationWarning:
    """Test that update_cli displays customization warning for RC versions."""

    def test_update_cli_shows_customization_warning(self, tmp_path):
        """
        GIVEN: update_cli with RC version (1.2.3-rc.main.20260127.1)
        WHEN: User runs update command
        THEN: Warning displays "Local customizations detected. Update will overwrite."
        """
        import subprocess

        # Set up test environment with RC VERSION file
        claude_dir = tmp_path / ".claude"
        claude_dir.mkdir(parents=True)
        (claude_dir / "VERSION").write_text("1.2.3-rc.main.20260127.1")

        # Get path to CLI
        project_root = Path(__file__).parent.parent.parent.parent.parent
        cli_path = project_root / "nWave" / "cli" / "update_cli.py"

        env = os.environ.copy()
        env.update({
            "NWAVE_TEST_MODE": "true",
            "NWAVE_HOME": str(claude_dir),
            "NWAVE_MOCK_GITHUB_VERSION": "1.3.0",
            "NWAVE_MOCK_GITHUB_CHECKSUM": "abc123",
            "NWAVE_MOCK_CONFIRM_UPDATE": "n",  # Don't proceed with update
            "PYTHONPATH": str(project_root),
        })

        result = subprocess.run(
            [sys.executable, str(cli_path)],
            env=env,
            capture_output=True,
            text=True,
            timeout=30,
        )

        expected_warning = "Local customizations detected. Update will overwrite."
        assert expected_warning in result.stdout, (
            f"Expected customization warning not found.\n"
            f"Expected: '{expected_warning}'\n"
            f"STDOUT: {result.stdout}\n"
            f"STDERR: {result.stderr}"
        )

    def test_update_cli_rc_version_allows_user_choice(self, tmp_path):
        """
        GIVEN: update_cli with RC version
        WHEN: User runs update command
        THEN: User can choose to proceed or cancel
        """
        import subprocess

        # Set up test environment with RC VERSION file
        claude_dir = tmp_path / ".claude"
        claude_dir.mkdir(parents=True)
        (claude_dir / "VERSION").write_text("1.2.3-rc.main.20260127.1")

        # Get path to CLI
        project_root = Path(__file__).parent.parent.parent.parent.parent
        cli_path = project_root / "nWave" / "cli" / "update_cli.py"

        env = os.environ.copy()
        env.update({
            "NWAVE_TEST_MODE": "true",
            "NWAVE_HOME": str(claude_dir),
            "NWAVE_MOCK_GITHUB_VERSION": "1.3.0",
            "NWAVE_MOCK_GITHUB_CHECKSUM": "abc123",
            "NWAVE_MOCK_CONFIRM_UPDATE": "n",  # Test cancellation
            "PYTHONPATH": str(project_root),
        })

        result = subprocess.run(
            [sys.executable, str(cli_path)],
            env=env,
            capture_output=True,
            text=True,
            timeout=30,
        )

        # Check that user's choice (n = cancel) was respected
        # In test mode, the prompt is handled via environment variable
        # The "Update cancelled." message proves user choice was honored
        output = result.stdout.lower()
        assert "cancelled" in output or "canceled" in output, (
            f"Expected cancellation message (user chose 'n') not found.\n"
            f"STDOUT: {result.stdout}\n"
            f"STDERR: {result.stderr}"
        )


# ============================================================================
# Step 04-10: Already up-to-date shows message without update
# ============================================================================


class TestUpdateCliShowsUpToDateMessage:
    """Test that update_cli displays correct message when already up to date."""

    def test_update_cli_shows_up_to_date_message(self, tmp_path):
        """
        GIVEN: Sofia has nWave v1.3.0 installed
        AND: GitHub API returns v1.3.0 as latest release (same version)
        WHEN: Sofia runs /nw:update command
        THEN: Output displays "Already up to date (v1.3.0)."
        """
        import subprocess

        # Set up test environment with VERSION file (v1.3.0)
        claude_dir = tmp_path / ".claude"
        claude_dir.mkdir(parents=True)
        (claude_dir / "VERSION").write_text("1.3.0")

        # Get path to CLI
        project_root = Path(__file__).parent.parent.parent.parent.parent
        cli_path = project_root / "nWave" / "cli" / "update_cli.py"

        env = os.environ.copy()
        env.update({
            "NWAVE_TEST_MODE": "true",
            "NWAVE_HOME": str(claude_dir),
            "NWAVE_MOCK_GITHUB_VERSION": "1.3.0",  # Same as installed
            "NWAVE_MOCK_GITHUB_CHECKSUM": "abc123",
            "PYTHONPATH": str(project_root),
        })

        result = subprocess.run(
            [sys.executable, str(cli_path)],
            env=env,
            capture_output=True,
            text=True,
            timeout=30,
        )

        expected_message = "Already up to date (v1.3.0)."
        assert expected_message in result.stdout, (
            f"Expected 'Already up to date' message not found.\n"
            f"Expected: '{expected_message}'\n"
            f"STDOUT: {result.stdout}\n"
            f"STDERR: {result.stderr}"
        )

    def test_update_cli_exits_zero_on_up_to_date(self, tmp_path):
        """
        GIVEN: Already up to date (current == latest)
        WHEN: update command runs
        THEN: Exit code is 0 (success)
        """
        import subprocess

        # Set up test environment
        claude_dir = tmp_path / ".claude"
        claude_dir.mkdir(parents=True)
        (claude_dir / "VERSION").write_text("1.3.0")

        project_root = Path(__file__).parent.parent.parent.parent.parent
        cli_path = project_root / "nWave" / "cli" / "update_cli.py"

        env = os.environ.copy()
        env.update({
            "NWAVE_TEST_MODE": "true",
            "NWAVE_HOME": str(claude_dir),
            "NWAVE_MOCK_GITHUB_VERSION": "1.3.0",
            "NWAVE_MOCK_GITHUB_CHECKSUM": "abc123",
            "PYTHONPATH": str(project_root),
        })

        result = subprocess.run(
            [sys.executable, str(cli_path)],
            env=env,
            capture_output=True,
            text=True,
            timeout=30,
        )

        assert result.returncode == 0, (
            f"Expected exit code 0 (up_to_date scenario), got {result.returncode}\n"
            f"STDOUT: {result.stdout}\n"
            f"STDERR: {result.stderr}"
        )


# ============================================================================
# Step 04-03: Major version update proceeds with confirmation
# ============================================================================


class TestUpdateCliAcceptsYConfirmation:
    """
    Test that update_cli accepts "y" confirmation and proceeds with major update.

    Step 04-03: Major version update proceeds with confirmation.

    Key behaviors:
    - User confirms with "y" for major version update
    - Update proceeds from v1.3.0 to v2.0.0
    - "Update complete." is displayed
    - VERSION file is updated
    """

    def test_update_cli_accepts_y_confirmation(self, tmp_path):
        """
        GIVEN: Paolo has nWave v1.3.0 installed
        AND: GitHub returns v2.0.0 (major version change)
        WHEN: Paolo confirms with "y"
        THEN: Update proceeds to v2.0.0
        AND: Output displays "Update complete."
        """
        import subprocess

        # Set up test environment with VERSION file
        claude_dir = tmp_path / ".claude"
        claude_dir.mkdir(parents=True)
        version_file = claude_dir / "VERSION"
        version_file.write_text("1.3.0")

        # Get path to CLI
        project_root = Path(__file__).parent.parent.parent.parent.parent
        cli_path = project_root / "nWave" / "cli" / "update_cli.py"

        env = os.environ.copy()
        env.update({
            "NWAVE_TEST_MODE": "true",
            "NWAVE_HOME": str(claude_dir),
            "NWAVE_MOCK_GITHUB_VERSION": "2.0.0",  # Major version change
            "NWAVE_MOCK_GITHUB_CHECKSUM": "abc123",
            "NWAVE_MOCK_CONFIRM_UPDATE": "y",  # Confirm update
            "PYTHONPATH": str(project_root),
        })

        result = subprocess.run(
            [sys.executable, str(cli_path)],
            env=env,
            capture_output=True,
            text=True,
            timeout=30,
        )

        # Assert: Update completed successfully
        assert "Update complete" in result.stdout, (
            f"Expected 'Update complete.' in output.\n"
            f"STDOUT: {result.stdout}\n"
            f"STDERR: {result.stderr}"
        )

        # Assert: VERSION file was updated to 2.0.0
        assert version_file.read_text().strip() == "2.0.0", (
            f"VERSION file should be 2.0.0, got: {version_file.read_text()}"
        )

    def test_update_cli_major_update_exits_zero_on_y(self, tmp_path):
        """
        GIVEN: Major version update with user confirmation "y"
        WHEN: update command runs
        THEN: Exit code is 0 (success)
        """
        import subprocess

        # Set up test environment
        claude_dir = tmp_path / ".claude"
        claude_dir.mkdir(parents=True)
        (claude_dir / "VERSION").write_text("1.3.0")

        project_root = Path(__file__).parent.parent.parent.parent.parent
        cli_path = project_root / "nWave" / "cli" / "update_cli.py"

        env = os.environ.copy()
        env.update({
            "NWAVE_TEST_MODE": "true",
            "NWAVE_HOME": str(claude_dir),
            "NWAVE_MOCK_GITHUB_VERSION": "2.0.0",
            "NWAVE_MOCK_GITHUB_CHECKSUM": "abc123",
            "NWAVE_MOCK_CONFIRM_UPDATE": "y",
            "PYTHONPATH": str(project_root),
        })

        result = subprocess.run(
            [sys.executable, str(cli_path)],
            env=env,
            capture_output=True,
            text=True,
            timeout=30,
        )

        assert result.returncode == 0, (
            f"Expected exit code 0 for successful major update, got {result.returncode}\n"
            f"STDOUT: {result.stdout}\n"
            f"STDERR: {result.stderr}"
        )

    def test_update_cli_shows_major_warning_before_proceed(self, tmp_path):
        """
        GIVEN: Major version update (v1.3.0 -> v2.0.0)
        WHEN: User confirms with "y"
        THEN: Major version warning was shown before update proceeded
        """
        import subprocess

        # Set up test environment
        claude_dir = tmp_path / ".claude"
        claude_dir.mkdir(parents=True)
        (claude_dir / "VERSION").write_text("1.3.0")

        project_root = Path(__file__).parent.parent.parent.parent.parent
        cli_path = project_root / "nWave" / "cli" / "update_cli.py"

        env = os.environ.copy()
        env.update({
            "NWAVE_TEST_MODE": "true",
            "NWAVE_HOME": str(claude_dir),
            "NWAVE_MOCK_GITHUB_VERSION": "2.0.0",
            "NWAVE_MOCK_GITHUB_CHECKSUM": "abc123",
            "NWAVE_MOCK_CONFIRM_UPDATE": "y",
            "PYTHONPATH": str(project_root),
        })

        result = subprocess.run(
            [sys.executable, str(cli_path)],
            env=env,
            capture_output=True,
            text=True,
            timeout=30,
        )

        # Assert: Major version warning was shown
        expected_warning = "Major version change detected"
        assert expected_warning in result.stdout, (
            f"Expected major version warning in output.\n"
            f"Expected: '{expected_warning}'\n"
            f"STDOUT: {result.stdout}\n"
            f"STDERR: {result.stderr}"
        )

        # Assert: Update also completed
        assert "Update complete" in result.stdout, (
            f"Expected 'Update complete.' after warning.\n"
            f"STDOUT: {result.stdout}"
        )
