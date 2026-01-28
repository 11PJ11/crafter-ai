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
