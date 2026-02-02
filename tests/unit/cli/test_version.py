"""
Unit tests for CLI version command.

Tests the --version flag displays correct version information.
"""

from typer.testing import CliRunner

from crafter_ai import __version__
from crafter_ai.cli import app


class TestVersionCommand:
    """Tests for the --version command flag."""

    def test_version_flag_shows_version_number(self, cli_runner: CliRunner) -> None:
        """
        Given the CLI is invoked
        When the --version flag is provided
        Then it should display the current version number.
        """
        result = cli_runner.invoke(app, ["--version"])

        assert result.exit_code == 0
        assert __version__ in result.stdout

    def test_version_short_flag_shows_version_number(
        self, cli_runner: CliRunner
    ) -> None:
        """
        Given the CLI is invoked
        When the -v flag is provided
        Then it should display the current version number.
        """
        result = cli_runner.invoke(app, ["-v"])

        assert result.exit_code == 0
        assert __version__ in result.stdout

    def test_version_output_format(self, cli_runner: CliRunner) -> None:
        """
        Given the CLI is invoked with --version
        When the output is displayed
        Then it should follow the format 'crafter-ai version X.Y.Z'.
        """
        result = cli_runner.invoke(app, ["--version"])

        assert result.exit_code == 0
        assert f"crafter-ai version {__version__}" in result.stdout
