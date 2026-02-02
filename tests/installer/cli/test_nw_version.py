"""Tests for nw version CLI command.

TDD approach: Tests verify CLI behavior with mock dependencies
and output verification using CliRunner.
"""

import json
import os
import platform
import sys
from unittest.mock import MagicMock, patch

import typer
from typer.testing import CliRunner

from crafter_ai.installer.cli.nw_version import (
    _get_installed_version,
    _is_ci_mode,
    version,
)


# Create a test app for CLI testing
test_app = typer.Typer()
test_app.command()(version)

runner = CliRunner()


class TestVersionCommandBasic:
    """Test basic version command behavior."""

    def test_version_command_exists(self) -> None:
        """version command should be callable."""
        assert callable(version)

    def test_version_runs_without_error(self) -> None:
        """version command should run without raising exceptions."""
        result = runner.invoke(test_app, [])
        assert result.exit_code == 0

    def test_version_shows_header(self) -> None:
        """version should display 'nWave Framework' header."""
        result = runner.invoke(test_app, [])
        assert "nWave Framework" in result.output


class TestVersionDisplaysInstalledVersion:
    """Test that version displays installed version."""

    def test_displays_installed_version(self) -> None:
        """version should display installed version."""
        result = runner.invoke(test_app, [])
        assert "Installed:" in result.output or "crafter-ai v" in result.output

    def test_displays_crafter_ai_package(self) -> None:
        """version should display crafter-ai package name."""
        result = runner.invoke(test_app, [])
        assert "crafter-ai" in result.output.lower()


class TestVersionDisplaysSystemInfo:
    """Test that version displays system information."""

    def test_displays_python_version(self) -> None:
        """version should display Python version."""
        result = runner.invoke(test_app, [])
        assert "Python:" in result.output or "python" in result.output.lower()

    def test_displays_correct_python_version(self) -> None:
        """version should display the actual Python version."""
        result = runner.invoke(test_app, [])
        python_version = f"{sys.version_info.major}.{sys.version_info.minor}"
        assert python_version in result.output

    def test_displays_platform(self) -> None:
        """version should display platform information."""
        result = runner.invoke(test_app, [])
        assert "Platform:" in result.output or "platform" in result.output.lower()

    def test_displays_current_platform(self) -> None:
        """version should display the current platform."""
        result = runner.invoke(test_app, [])
        current_platform = platform.system().lower()
        assert current_platform in result.output.lower()


class TestVersionShortFlag:
    """Test --short flag behavior."""

    def test_short_flag_shows_only_version(self) -> None:
        """--short should show only the version number."""
        with patch(
            "crafter_ai.installer.cli.nw_version._get_installed_version",
            return_value="0.1.0",
        ):
            result = runner.invoke(test_app, ["--short"])

            # Should only contain version number
            assert "0.1.0" in result.output
            # Should NOT contain other info
            assert "Python:" not in result.output
            assert "Platform:" not in result.output
            assert "nWave Framework" not in result.output

    def test_short_flag_s_works(self) -> None:
        """-s short flag should work like --short."""
        with patch(
            "crafter_ai.installer.cli.nw_version._get_installed_version",
            return_value="0.1.0",
        ):
            result = runner.invoke(test_app, ["-s"])

            assert "0.1.0" in result.output
            assert "Python:" not in result.output


class TestVersionJsonFlag:
    """Test --json flag behavior."""

    def test_json_flag_outputs_valid_json(self) -> None:
        """--json should output valid JSON."""
        with patch(
            "crafter_ai.installer.cli.nw_version._get_installed_version",
            return_value="0.1.0",
        ):
            result = runner.invoke(test_app, ["--json"])

            # Should be valid JSON
            data = json.loads(result.output)
            assert isinstance(data, dict)

    def test_json_output_has_installed_version(self) -> None:
        """JSON output should have installed_version field."""
        with patch(
            "crafter_ai.installer.cli.nw_version._get_installed_version",
            return_value="0.1.0",
        ):
            result = runner.invoke(test_app, ["--json"])

            data = json.loads(result.output)
            assert "installed_version" in data
            assert data["installed_version"] == "0.1.0"

    def test_json_output_has_python_version(self) -> None:
        """JSON output should have python_version field."""
        result = runner.invoke(test_app, ["--json"])

        data = json.loads(result.output)
        assert "python_version" in data
        python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        assert data["python_version"] == python_version

    def test_json_output_has_platform(self) -> None:
        """JSON output should have platform field."""
        result = runner.invoke(test_app, ["--json"])

        data = json.loads(result.output)
        assert "platform" in data
        assert data["platform"] == platform.system().lower()

    def test_json_j_flag_works(self) -> None:
        """-j short flag should work like --json."""
        with patch(
            "crafter_ai.installer.cli.nw_version._get_installed_version",
            return_value="0.1.0",
        ):
            result = runner.invoke(test_app, ["-j"])

            data = json.loads(result.output)
            assert "installed_version" in data


class TestVersionCheckUpdatesFlag:
    """Test --check-updates flag behavior."""

    def test_check_updates_queries_pypi(self) -> None:
        """--check-updates should query PyPI for latest version."""
        mock_get_latest = MagicMock(return_value="0.2.0")

        with patch(
            "crafter_ai.installer.cli.nw_version._get_installed_version",
            return_value="0.1.0",
        ):
            with patch(
                "crafter_ai.installer.cli.nw_version.get_latest_pypi_version",
                mock_get_latest,
            ):
                result = runner.invoke(test_app, ["--check-updates"])

                mock_get_latest.assert_called_once()
                assert result.exit_code == 0

    def test_check_updates_shows_latest_version(self) -> None:
        """--check-updates should show latest available version."""
        with patch(
            "crafter_ai.installer.cli.nw_version._get_installed_version",
            return_value="0.1.0",
        ):
            with patch(
                "crafter_ai.installer.cli.nw_version.get_latest_pypi_version",
                return_value="0.2.0",
            ):
                result = runner.invoke(test_app, ["--check-updates"])

                assert "0.2.0" in result.output

    def test_check_updates_shows_upgrade_available(self) -> None:
        """--check-updates should indicate when upgrade is available."""
        with patch(
            "crafter_ai.installer.cli.nw_version._get_installed_version",
            return_value="0.1.0",
        ):
            with patch(
                "crafter_ai.installer.cli.nw_version.get_latest_pypi_version",
                return_value="0.2.0",
            ):
                result = runner.invoke(test_app, ["--check-updates"])

                # Should indicate upgrade is available
                output_lower = result.output.lower()
                assert (
                    "latest" in output_lower
                    or "upgrade" in output_lower
                    or "available" in output_lower
                )

    def test_check_updates_shows_up_to_date(self) -> None:
        """--check-updates should show 'up to date' when current."""
        with patch(
            "crafter_ai.installer.cli.nw_version._get_installed_version",
            return_value="0.2.0",
        ):
            with patch(
                "crafter_ai.installer.cli.nw_version.get_latest_pypi_version",
                return_value="0.2.0",
            ):
                result = runner.invoke(test_app, ["--check-updates"])

                output_lower = result.output.lower()
                assert "up to date" in output_lower or "current" in output_lower

    def test_check_updates_u_flag_works(self) -> None:
        """-u short flag should work like --check-updates."""
        with patch(
            "crafter_ai.installer.cli.nw_version._get_installed_version",
            return_value="0.1.0",
        ):
            with patch(
                "crafter_ai.installer.cli.nw_version.get_latest_pypi_version",
                return_value="0.2.0",
            ):
                result = runner.invoke(test_app, ["-u"])

                assert "0.2.0" in result.output

    def test_check_updates_handles_pypi_failure(self) -> None:
        """--check-updates should handle PyPI unavailability gracefully."""
        with patch(
            "crafter_ai.installer.cli.nw_version._get_installed_version",
            return_value="0.1.0",
        ):
            with patch(
                "crafter_ai.installer.cli.nw_version.get_latest_pypi_version",
                return_value=None,
            ):
                result = runner.invoke(test_app, ["--check-updates"])

                # Should not crash
                assert result.exit_code == 0
                # Should indicate PyPI is unavailable
                output_lower = result.output.lower()
                assert (
                    "unavailable" in output_lower
                    or "could not" in output_lower
                    or "unable" in output_lower
                )


class TestVersionJsonWithCheckUpdates:
    """Test JSON output with --check-updates flag."""

    def test_json_with_check_updates_has_latest_version(self) -> None:
        """JSON output with --check-updates should have latest_version."""
        with patch(
            "crafter_ai.installer.cli.nw_version._get_installed_version",
            return_value="0.1.0",
        ):
            with patch(
                "crafter_ai.installer.cli.nw_version.get_latest_pypi_version",
                return_value="0.2.0",
            ):
                result = runner.invoke(test_app, ["--json", "--check-updates"])

                data = json.loads(result.output)
                assert "latest_version" in data
                assert data["latest_version"] == "0.2.0"

    def test_json_with_check_updates_has_upgrade_available(self) -> None:
        """JSON output with --check-updates should have upgrade_available."""
        with patch(
            "crafter_ai.installer.cli.nw_version._get_installed_version",
            return_value="0.1.0",
        ):
            with patch(
                "crafter_ai.installer.cli.nw_version.get_latest_pypi_version",
                return_value="0.2.0",
            ):
                result = runner.invoke(test_app, ["--json", "--check-updates"])

                data = json.loads(result.output)
                assert "upgrade_available" in data
                assert data["upgrade_available"] is True

    def test_json_with_check_updates_false_when_current(self) -> None:
        """upgrade_available should be false when version is current."""
        with patch(
            "crafter_ai.installer.cli.nw_version._get_installed_version",
            return_value="0.2.0",
        ):
            with patch(
                "crafter_ai.installer.cli.nw_version.get_latest_pypi_version",
                return_value="0.2.0",
            ):
                result = runner.invoke(test_app, ["--json", "--check-updates"])

                data = json.loads(result.output)
                assert data["upgrade_available"] is False

    def test_json_without_check_updates_no_latest_version(self) -> None:
        """JSON output without --check-updates should not have latest_version."""
        with patch(
            "crafter_ai.installer.cli.nw_version._get_installed_version",
            return_value="0.1.0",
        ):
            result = runner.invoke(test_app, ["--json"])

            data = json.loads(result.output)
            assert "latest_version" not in data
            assert "upgrade_available" not in data


class TestVersionCIMode:
    """Test CI mode behavior."""

    def test_ci_mode_uses_plain_output(self) -> None:
        """In CI mode, version should use plain text output."""
        with patch(
            "crafter_ai.installer.cli.nw_version._get_installed_version",
            return_value="0.1.0",
        ):
            with patch.dict(os.environ, {"CI": "true"}):
                result = runner.invoke(test_app, [])

                # Should not have Rich formatting markup in CI mode
                assert "nWave Framework" in result.output

    def test_ci_mode_detected_by_ci_equals_1(self) -> None:
        """CI mode should be detected via CI=1."""
        with patch(
            "crafter_ai.installer.cli.nw_version._get_installed_version",
            return_value="0.1.0",
        ):
            with patch.dict(os.environ, {"CI": "1"}):
                result = runner.invoke(test_app, [])

                # Should still run successfully
                assert result.exit_code == 0


class TestHelperFunctions:
    """Test helper functions."""

    def test_is_ci_mode_true(self) -> None:
        """_is_ci_mode should return True when CI=true."""
        with patch.dict(os.environ, {"CI": "true"}):
            assert _is_ci_mode() is True

    def test_is_ci_mode_one(self) -> None:
        """_is_ci_mode should return True when CI=1."""
        with patch.dict(os.environ, {"CI": "1"}):
            assert _is_ci_mode() is True

    def test_is_ci_mode_false(self) -> None:
        """_is_ci_mode should return False when CI not set."""
        with patch.dict(os.environ, {}, clear=True):
            os.environ.pop("CI", None)
            assert _is_ci_mode() is False

    def test_is_ci_mode_other_value(self) -> None:
        """_is_ci_mode should return False for other values."""
        with patch.dict(os.environ, {"CI": "false"}):
            assert _is_ci_mode() is False

    def test_get_installed_version_returns_string(self) -> None:
        """_get_installed_version should return a version string."""
        version_str = _get_installed_version()
        assert isinstance(version_str, str)
        # Should look like a version (contains digits and dots)
        assert any(c.isdigit() for c in version_str)

    def test_get_installed_version_fallback_on_error(self) -> None:
        """_get_installed_version should return 'unknown' on error."""
        with patch(
            "crafter_ai.installer.cli.nw_version.importlib_metadata_version",
            side_effect=Exception("Not found"),
        ):
            version_str = _get_installed_version()
            assert version_str == "unknown"


class TestVersionWithRealData:
    """Test version with real system data (integration-like tests)."""

    def test_runs_with_real_system_info(self) -> None:
        """version should work with real system information."""
        result = runner.invoke(test_app, [])

        # Should complete and produce output
        assert result.exit_code == 0
        assert "nWave Framework" in result.output

    def test_json_with_real_system_info(self) -> None:
        """version --json should produce valid JSON with real data."""
        result = runner.invoke(test_app, ["--json"])

        data = json.loads(result.output)
        assert "installed_version" in data
        assert "python_version" in data
        assert "platform" in data
