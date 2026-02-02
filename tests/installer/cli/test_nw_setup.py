"""Tests for nw setup CLI command.

TDD approach: Tests verify CLI behavior with mock dependencies
and output verification using StringIO capture.
"""

import os
from pathlib import Path
from unittest.mock import patch

# Create a test app for CLI testing
import typer
from typer.testing import CliRunner

from crafter_ai.installer.cli.nw_setup import setup


test_app = typer.Typer()
test_app.command()(setup)

runner = CliRunner()


class TestSetupCommandBasic:
    """Test basic setup command behavior."""

    def test_setup_command_exists(self) -> None:
        """setup command should be callable."""
        assert callable(setup)

    def test_setup_runs_without_error(self, tmp_path: Path) -> None:
        """setup command should run without raising exceptions."""
        with patch("crafter_ai.installer.cli.nw_setup.Path") as mock_path:
            mock_path.home.return_value = tmp_path / "home"
            mock_path.cwd.return_value = tmp_path / "project"
            # Create the directories so the filesystem adapter works
            (tmp_path / "home").mkdir()
            (tmp_path / "project").mkdir()

            result = runner.invoke(test_app, [])

            # Should not raise exception (exit code 0)
            assert result.exit_code == 0


class TestSetupCommandGlobalFlag:
    """Test --global flag behavior."""

    def test_global_flag_sets_up_only_global_config(self, tmp_path: Path) -> None:
        """--global flag should setup only ~/.claude/ not .claude/."""
        home_dir = tmp_path / "home"
        project_dir = tmp_path / "project"
        home_dir.mkdir()
        project_dir.mkdir()

        with patch("crafter_ai.installer.cli.nw_setup.Path") as mock_path:
            mock_path.home.return_value = home_dir
            mock_path.cwd.return_value = project_dir

            result = runner.invoke(test_app, ["--global"])

            assert result.exit_code == 0
            # Global config should exist
            assert (home_dir / ".claude").exists()
            # Project config should NOT exist
            assert not (project_dir / ".claude").exists()

    def test_short_flag_g_works(self, tmp_path: Path) -> None:
        """-g short flag should work like --global."""
        home_dir = tmp_path / "home"
        project_dir = tmp_path / "project"
        home_dir.mkdir()
        project_dir.mkdir()

        with patch("crafter_ai.installer.cli.nw_setup.Path") as mock_path:
            mock_path.home.return_value = home_dir
            mock_path.cwd.return_value = project_dir

            result = runner.invoke(test_app, ["-g"])

            assert result.exit_code == 0
            assert (home_dir / ".claude").exists()
            assert not (project_dir / ".claude").exists()


class TestSetupCommandProjectFlag:
    """Test --project flag behavior."""

    def test_project_flag_sets_up_only_project_config(self, tmp_path: Path) -> None:
        """--project flag should setup only .claude/ not ~/.claude/."""
        home_dir = tmp_path / "home"
        project_dir = tmp_path / "project"
        home_dir.mkdir()
        project_dir.mkdir()

        with patch("crafter_ai.installer.cli.nw_setup.Path") as mock_path:
            mock_path.home.return_value = home_dir
            mock_path.cwd.return_value = project_dir

            result = runner.invoke(test_app, ["--project"])

            assert result.exit_code == 0
            # Global config should NOT exist
            assert not (home_dir / ".claude").exists()
            # Project config should exist
            assert (project_dir / ".claude").exists()

    def test_short_flag_p_works(self, tmp_path: Path) -> None:
        """-p short flag should work like --project."""
        home_dir = tmp_path / "home"
        project_dir = tmp_path / "project"
        home_dir.mkdir()
        project_dir.mkdir()

        with patch("crafter_ai.installer.cli.nw_setup.Path") as mock_path:
            mock_path.home.return_value = home_dir
            mock_path.cwd.return_value = project_dir

            result = runner.invoke(test_app, ["-p"])

            assert result.exit_code == 0
            assert not (home_dir / ".claude").exists()
            assert (project_dir / ".claude").exists()


class TestSetupCommandDefaultBehavior:
    """Test default behavior (no flags)."""

    def test_no_flags_sets_up_both_configs(self, tmp_path: Path) -> None:
        """Without flags, setup should configure both global and project."""
        home_dir = tmp_path / "home"
        project_dir = tmp_path / "project"
        home_dir.mkdir()
        project_dir.mkdir()

        with patch("crafter_ai.installer.cli.nw_setup.Path") as mock_path:
            mock_path.home.return_value = home_dir
            mock_path.cwd.return_value = project_dir

            result = runner.invoke(test_app, [])

            assert result.exit_code == 0
            # Both configs should exist
            assert (home_dir / ".claude").exists()
            assert (project_dir / ".claude").exists()


class TestSetupCommandForceFlag:
    """Test --force flag behavior."""

    def test_force_flag_overwrites_existing_files(self, tmp_path: Path) -> None:
        """--force flag should overwrite existing configuration files."""
        home_dir = tmp_path / "home"
        project_dir = tmp_path / "project"
        home_dir.mkdir()
        project_dir.mkdir()

        # Pre-create config with custom content
        (home_dir / ".claude").mkdir()
        (home_dir / ".claude" / "commands").mkdir()
        (home_dir / ".claude" / "CLAUDE.md").write_text("custom content")

        with patch("crafter_ai.installer.cli.nw_setup.Path") as mock_path:
            mock_path.home.return_value = home_dir
            mock_path.cwd.return_value = project_dir

            result = runner.invoke(test_app, ["--global", "--force"])

            assert result.exit_code == 0
            # Content should be overwritten with default template
            content = (home_dir / ".claude" / "CLAUDE.md").read_text()
            assert "custom content" not in content
            assert "CLAUDE.md" in content

    def test_short_flag_f_works(self, tmp_path: Path) -> None:
        """-f short flag should work like --force."""
        home_dir = tmp_path / "home"
        project_dir = tmp_path / "project"
        home_dir.mkdir()
        project_dir.mkdir()

        # Pre-create config
        (home_dir / ".claude").mkdir()
        (home_dir / ".claude" / "commands").mkdir()
        (home_dir / ".claude" / "CLAUDE.md").write_text("old")

        with patch("crafter_ai.installer.cli.nw_setup.Path") as mock_path:
            mock_path.home.return_value = home_dir
            mock_path.cwd.return_value = project_dir

            result = runner.invoke(test_app, ["-g", "-f"])

            assert result.exit_code == 0
            content = (home_dir / ".claude" / "CLAUDE.md").read_text()
            assert "old" not in content


class TestSetupCommandOutput:
    """Test CLI output messages."""

    def test_displays_success_message_on_completion(self, tmp_path: Path) -> None:
        """Setup should display success message when complete."""
        home_dir = tmp_path / "home"
        project_dir = tmp_path / "project"
        home_dir.mkdir()
        project_dir.mkdir()

        with patch("crafter_ai.installer.cli.nw_setup.Path") as mock_path:
            mock_path.home.return_value = home_dir
            mock_path.cwd.return_value = project_dir

            result = runner.invoke(test_app, [])

            assert (
                "complete" in result.output.lower() or "setup" in result.output.lower()
            )

    def test_displays_created_paths(self, tmp_path: Path) -> None:
        """Setup should display paths that were created."""
        home_dir = tmp_path / "home"
        project_dir = tmp_path / "project"
        home_dir.mkdir()
        project_dir.mkdir()

        with patch("crafter_ai.installer.cli.nw_setup.Path") as mock_path:
            mock_path.home.return_value = home_dir
            mock_path.cwd.return_value = project_dir

            result = runner.invoke(test_app, ["-g"])

            # Should mention created paths
            assert ".claude" in result.output or "Created" in result.output


class TestSetupCommandCIMode:
    """Test CI mode behavior."""

    def test_ci_mode_uses_plain_output(self, tmp_path: Path) -> None:
        """In CI mode, setup should use plain text output (no Rich formatting)."""
        home_dir = tmp_path / "home"
        project_dir = tmp_path / "project"
        home_dir.mkdir()
        project_dir.mkdir()

        with patch("crafter_ai.installer.cli.nw_setup.Path") as mock_path:
            mock_path.home.return_value = home_dir
            mock_path.cwd.return_value = project_dir

            with patch.dict(os.environ, {"CI": "true"}):
                result = runner.invoke(test_app, ["-g"])

                # CI output should have markers like [OK] or [INFO]
                assert "[OK]" in result.output or "[INFO]" in result.output

    def test_ci_mode_detected_by_env_var(self, tmp_path: Path) -> None:
        """CI mode should be detected via CI=true or CI=1."""
        home_dir = tmp_path / "home"
        project_dir = tmp_path / "project"
        home_dir.mkdir()
        project_dir.mkdir()

        with patch("crafter_ai.installer.cli.nw_setup.Path") as mock_path:
            mock_path.home.return_value = home_dir
            mock_path.cwd.return_value = project_dir

            # Test CI=1
            with patch.dict(os.environ, {"CI": "1"}):
                result = runner.invoke(test_app, ["-g"])
                assert "[OK]" in result.output or "[INFO]" in result.output


class TestSetupCommandExitCodes:
    """Test CLI exit codes."""

    def test_returns_zero_on_success(self, tmp_path: Path) -> None:
        """Setup should return exit code 0 on success."""
        home_dir = tmp_path / "home"
        project_dir = tmp_path / "project"
        home_dir.mkdir()
        project_dir.mkdir()

        with patch("crafter_ai.installer.cli.nw_setup.Path") as mock_path:
            mock_path.home.return_value = home_dir
            mock_path.cwd.return_value = project_dir

            result = runner.invoke(test_app, [])

            assert result.exit_code == 0

    def test_returns_nonzero_on_failure(self, tmp_path: Path) -> None:
        """Setup should return non-zero exit code on failure."""
        # Use a path that will cause permission errors
        with patch("crafter_ai.installer.cli.nw_setup.Path") as mock_path:
            # Point to non-existent root path to cause failure
            mock_path.home.return_value = Path("/nonexistent/root/path")
            mock_path.cwd.return_value = tmp_path

            result = runner.invoke(test_app, ["-g"])

            # Should fail because /nonexistent/root/path doesn't exist
            assert result.exit_code != 0


class TestSetupCommandAlreadyConfigured:
    """Test behavior when already configured."""

    def test_reports_already_configured(self, tmp_path: Path) -> None:
        """Setup should report when config already exists."""
        home_dir = tmp_path / "home"
        project_dir = tmp_path / "project"
        home_dir.mkdir()
        project_dir.mkdir()

        # Pre-create complete setup
        (home_dir / ".claude" / "commands").mkdir(parents=True)
        (home_dir / ".claude" / "CLAUDE.md").write_text("existing")

        with patch("crafter_ai.installer.cli.nw_setup.Path") as mock_path:
            mock_path.home.return_value = home_dir
            mock_path.cwd.return_value = project_dir

            result = runner.invoke(test_app, ["-g"])

            # Should indicate already configured or no changes
            assert (
                "already" in result.output.lower()
                or "no changes" in result.output.lower()
            )
