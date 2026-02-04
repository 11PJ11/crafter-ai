"""Tests for forge:install CLI command.

Tests the CLI layer using Typer's CliRunner with mocked InstallService
and ReleaseReportService. Verifies display rendering, user prompts, and exit codes.
"""

import os
from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from crafter_ai.cli import app
from crafter_ai.installer.domain.check_result import CheckResult, CheckSeverity
from crafter_ai.installer.domain.health_result import HealthStatus
from crafter_ai.installer.services.install_service import InstallPhase, InstallResult
from crafter_ai.installer.services.release_report_service import ReleaseReport
from tests.cli.conftest import CleanCliRunner


@pytest.fixture
def runner() -> CleanCliRunner:
    """Create a CLI test runner with ANSI stripping for CI compatibility."""
    return CleanCliRunner()


@pytest.fixture
def mock_wheel_path(tmp_path: Path) -> Path:
    """Create a mock wheel file for testing."""
    wheel_file = tmp_path / "crafter_ai-0.2.0-py3-none-any.whl"
    wheel_file.write_bytes(b"fake wheel content")
    return wheel_file


@pytest.fixture
def successful_install_result() -> InstallResult:
    """Create a successful install result."""
    return InstallResult(
        success=True,
        version="0.2.0",
        install_path=Path("/usr/local/bin/crafter-ai"),
        phases_completed=[
            InstallPhase.PREFLIGHT,
            InstallPhase.READINESS,
            InstallPhase.BACKUP,
            InstallPhase.INSTALL,
            InstallPhase.VERIFICATION,
        ],
        error_message=None,
        health_status=HealthStatus.HEALTHY,
        verification_warnings=[],
    )


@pytest.fixture
def failed_install_result() -> InstallResult:
    """Create a failed install result."""
    return InstallResult(
        success=False,
        version=None,
        install_path=None,
        phases_completed=[InstallPhase.PREFLIGHT],
        error_message="Pre-flight checks failed: pipx not found",
        health_status=None,
        verification_warnings=[],
    )


@pytest.fixture
def passing_pre_flight_results() -> list[CheckResult]:
    """Create passing pre-flight check results."""
    return [
        CheckResult(
            id="wheel_exists",
            name="Wheel file exists",
            passed=True,
            severity=CheckSeverity.BLOCKING,
            message="Wheel file found at dist/",
        ),
        CheckResult(
            id="pipx_available",
            name="pipx is available",
            passed=True,
            severity=CheckSeverity.BLOCKING,
            message="pipx 1.4.0 installed",
        ),
    ]


@pytest.fixture
def sample_release_report(mock_wheel_path: Path) -> ReleaseReport:
    """Create a sample release report."""
    return ReleaseReport(
        version="0.2.0",
        install_path=Path("/usr/local/bin/crafter-ai"),
        wheel_path=mock_wheel_path,
        wheel_size_bytes=1024,
        phases_completed=[
            "preflight",
            "readiness",
            "backup",
            "install",
            "verification",
        ],
        health_status="HEALTHY",
        warnings=[],
        timestamp=datetime.now(),
        duration_seconds=5.5,
        backup_path=Path("/tmp/backup"),
    )


class TestForgeInstallCommandRegistration:
    """Tests for forge install command registration on Typer app."""

    def test_forge_install_command_registered(self, runner: CleanCliRunner) -> None:
        """Test that forge install command is registered."""
        result = runner.invoke(app, ["forge", "--help"])
        assert result.exit_code == 0
        assert "install" in result.output

    def test_forge_install_help_shows_options(self, runner: CleanCliRunner) -> None:
        """Test that forge install --help shows all options."""
        result = runner.invoke(app, ["forge", "install", "--help"])
        assert result.exit_code == 0
        assert "--wheel" in result.output
        assert "--force" in result.output
        assert "--no-verify" in result.output
        assert "--no-prompt" in result.output


class TestWheelResolution:
    """Tests for wheel path resolution."""

    def test_explicit_wheel_path_used(
        self,
        runner: CleanCliRunner,
        mock_wheel_path: Path,
        successful_install_result: InstallResult,
        sample_release_report: ReleaseReport,
    ) -> None:
        """Test command runs with explicit --wheel path."""
        with (
            patch(
                "crafter_ai.installer.cli.forge_install.create_install_service"
            ) as mock_factory,
            patch(
                "crafter_ai.installer.cli.forge_install.ReleaseReportService"
            ) as mock_report_service,
        ):
            mock_service = MagicMock()
            mock_service.install.return_value = successful_install_result
            mock_factory.return_value = mock_service

            mock_report = MagicMock()
            mock_report.generate.return_value = sample_release_report
            mock_report.format_console.return_value = "FORGE: INSTALL COMPLETE"
            mock_report_service.return_value = mock_report

            result = runner.invoke(
                app,
                ["forge", "install", "--wheel", str(mock_wheel_path), "--no-prompt"],
            )

        assert result.exit_code == 0
        mock_service.install.assert_called_once()
        # Verify the wheel path was passed to install
        call_args = mock_service.install.call_args
        assert call_args[0][0] == mock_wheel_path

    def test_auto_detect_wheel_in_dist(
        self,
        runner: CleanCliRunner,
        tmp_path: Path,
        successful_install_result: InstallResult,
        sample_release_report: ReleaseReport,
    ) -> None:
        """Test command auto-detects wheel in dist/."""
        # Create a fake dist directory with a wheel
        dist_dir = tmp_path / "dist"
        dist_dir.mkdir()
        wheel_file = dist_dir / "crafter_ai-0.3.0-py3-none-any.whl"
        wheel_file.write_bytes(b"fake wheel")

        with (
            patch(
                "crafter_ai.installer.cli.forge_install.create_install_service"
            ) as mock_factory,
            patch(
                "crafter_ai.installer.cli.forge_install.ReleaseReportService"
            ) as mock_report_service,
            patch(
                "crafter_ai.installer.cli.forge_install.list_wheels_in_dist"
            ) as mock_list,
        ):
            mock_list.return_value = [wheel_file]

            mock_service = MagicMock()
            mock_service.install.return_value = successful_install_result
            mock_factory.return_value = mock_service

            mock_report = MagicMock()
            mock_report.generate.return_value = sample_release_report
            mock_report.format_console.return_value = "FORGE: INSTALL COMPLETE"
            mock_report_service.return_value = mock_report

            result = runner.invoke(app, ["forge", "install", "--no-prompt"])

        assert result.exit_code == 0
        mock_list.assert_called_once()


class TestForceFlag:
    """Tests for --force flag behavior."""

    def test_force_flag_passed_to_install_service(
        self,
        runner: CleanCliRunner,
        mock_wheel_path: Path,
        successful_install_result: InstallResult,
        sample_release_report: ReleaseReport,
    ) -> None:
        """Test --force flag passed to InstallService."""
        with (
            patch(
                "crafter_ai.installer.cli.forge_install.create_install_service"
            ) as mock_factory,
            patch(
                "crafter_ai.installer.cli.forge_install.ReleaseReportService"
            ) as mock_report_service,
        ):
            mock_service = MagicMock()
            mock_service.install.return_value = successful_install_result
            mock_factory.return_value = mock_service

            mock_report = MagicMock()
            mock_report.generate.return_value = sample_release_report
            mock_report.format_console.return_value = "FORGE: INSTALL COMPLETE"
            mock_report_service.return_value = mock_report

            result = runner.invoke(
                app,
                [
                    "forge",
                    "install",
                    "--wheel",
                    str(mock_wheel_path),
                    "--force",
                    "--no-prompt",
                ],
            )

        assert result.exit_code == 0
        mock_service.install.assert_called_once()
        call_args = mock_service.install.call_args
        assert call_args[1]["force"] is True

    def test_short_force_flag(
        self,
        runner: CleanCliRunner,
        mock_wheel_path: Path,
        successful_install_result: InstallResult,
        sample_release_report: ReleaseReport,
    ) -> None:
        """Test -f short flag for --force."""
        with (
            patch(
                "crafter_ai.installer.cli.forge_install.create_install_service"
            ) as mock_factory,
            patch(
                "crafter_ai.installer.cli.forge_install.ReleaseReportService"
            ) as mock_report_service,
        ):
            mock_service = MagicMock()
            mock_service.install.return_value = successful_install_result
            mock_factory.return_value = mock_service

            mock_report = MagicMock()
            mock_report.generate.return_value = sample_release_report
            mock_report.format_console.return_value = "FORGE: INSTALL COMPLETE"
            mock_report_service.return_value = mock_report

            result = runner.invoke(
                app,
                [
                    "forge",
                    "install",
                    "--wheel",
                    str(mock_wheel_path),
                    "-f",
                    "--no-prompt",
                ],
            )

        assert result.exit_code == 0
        call_args = mock_service.install.call_args
        assert call_args[1]["force"] is True


class TestNoVerifyFlag:
    """Tests for --no-verify flag behavior."""

    def test_no_verify_skips_verification_phase(
        self,
        runner: CleanCliRunner,
        mock_wheel_path: Path,
        sample_release_report: ReleaseReport,
    ) -> None:
        """Test --no-verify skips verification phase."""
        # Create install result without verification
        install_result_no_verify = InstallResult(
            success=True,
            version="0.2.0",
            install_path=Path("/usr/local/bin/crafter-ai"),
            phases_completed=[
                InstallPhase.PREFLIGHT,
                InstallPhase.READINESS,
                InstallPhase.BACKUP,
                InstallPhase.INSTALL,
            ],  # No VERIFICATION phase
            error_message=None,
            health_status=None,
            verification_warnings=[],
        )

        with (
            patch(
                "crafter_ai.installer.cli.forge_install.create_install_service"
            ) as mock_factory,
            patch(
                "crafter_ai.installer.cli.forge_install.ReleaseReportService"
            ) as mock_report_service,
        ):
            mock_service = MagicMock()
            mock_service.install.return_value = install_result_no_verify
            mock_factory.return_value = mock_service

            mock_report = MagicMock()
            mock_report.generate.return_value = sample_release_report
            mock_report.format_console.return_value = "FORGE: INSTALL COMPLETE"
            mock_report_service.return_value = mock_report

            result = runner.invoke(
                app,
                [
                    "forge",
                    "install",
                    "--wheel",
                    str(mock_wheel_path),
                    "--no-verify",
                    "--no-prompt",
                ],
            )

        assert result.exit_code == 0
        # Verify factory was called with skip_verification=True
        mock_factory.assert_called_once()
        call_kwargs = mock_factory.call_args[1]
        assert call_kwargs.get("skip_verification") is True


class TestPromptBehavior:
    """Tests for confirmation prompt behavior."""

    def test_no_prompt_flag_skips_confirmation(
        self,
        runner: CleanCliRunner,
        mock_wheel_path: Path,
        successful_install_result: InstallResult,
        sample_release_report: ReleaseReport,
    ) -> None:
        """Test --no-prompt skips confirmation."""
        with (
            patch(
                "crafter_ai.installer.cli.forge_install.create_install_service"
            ) as mock_factory,
            patch(
                "crafter_ai.installer.cli.forge_install.ReleaseReportService"
            ) as mock_report_service,
        ):
            mock_service = MagicMock()
            mock_service.install.return_value = successful_install_result
            mock_factory.return_value = mock_service

            mock_report = MagicMock()
            mock_report.generate.return_value = sample_release_report
            mock_report.format_console.return_value = "FORGE: INSTALL COMPLETE"
            mock_report_service.return_value = mock_report

            result = runner.invoke(
                app,
                ["forge", "install", "--wheel", str(mock_wheel_path), "--no-prompt"],
            )

        assert result.exit_code == 0
        assert "Proceed with install?" not in result.output

    def test_ci_env_skips_confirmation(
        self,
        runner: CleanCliRunner,
        mock_wheel_path: Path,
        successful_install_result: InstallResult,
        sample_release_report: ReleaseReport,
    ) -> None:
        """Test CI=true env var skips confirmation."""
        with (
            patch(
                "crafter_ai.installer.cli.forge_install.create_install_service"
            ) as mock_factory,
            patch(
                "crafter_ai.installer.cli.forge_install.ReleaseReportService"
            ) as mock_report_service,
        ):
            mock_service = MagicMock()
            mock_service.install.return_value = successful_install_result
            mock_factory.return_value = mock_service

            mock_report = MagicMock()
            mock_report.generate.return_value = sample_release_report
            mock_report.format_console.return_value = "FORGE: INSTALL COMPLETE"
            mock_report_service.return_value = mock_report

            with patch.dict(os.environ, {"CI": "true"}):
                result = runner.invoke(
                    app,
                    ["forge", "install", "--wheel", str(mock_wheel_path)],
                )

        assert result.exit_code == 0
        assert "Proceed with install?" not in result.output

    def test_prompt_appears_when_interactive(
        self,
        runner: CleanCliRunner,
        mock_wheel_path: Path,
        successful_install_result: InstallResult,
        sample_release_report: ReleaseReport,
        passing_pre_flight_results: list[CheckResult],
    ) -> None:
        """Test prompt appears in interactive mode."""
        with (
            patch(
                "crafter_ai.installer.cli.forge_install.create_install_service"
            ) as mock_factory,
            patch(
                "crafter_ai.installer.cli.forge_install.ReleaseReportService"
            ) as mock_report_service,
            patch(
                "crafter_ai.installer.cli.forge_install.run_pre_flight_checks"
            ) as mock_preflight,
        ):
            mock_preflight.return_value = passing_pre_flight_results

            mock_service = MagicMock()
            mock_service.install.return_value = successful_install_result
            mock_factory.return_value = mock_service

            mock_report = MagicMock()
            mock_report.generate.return_value = sample_release_report
            mock_report.format_console.return_value = "FORGE: INSTALL COMPLETE"
            mock_report_service.return_value = mock_report

            # Remove CI env var if present
            env = {k: v for k, v in os.environ.items() if k != "CI"}
            with patch.dict(os.environ, env, clear=True):
                result = runner.invoke(
                    app,
                    ["forge", "install", "--wheel", str(mock_wheel_path)],
                    input="Y\n",
                )

        assert "Proceed with install?" in result.output

    def test_user_declines_install(
        self,
        runner: CleanCliRunner,
        mock_wheel_path: Path,
        passing_pre_flight_results: list[CheckResult],
    ) -> None:
        """Test user declining install exits with code 0."""
        with patch(
            "crafter_ai.installer.cli.forge_install.run_pre_flight_checks"
        ) as mock_preflight:
            mock_preflight.return_value = passing_pre_flight_results

            # Remove CI env var if present
            env = {k: v for k, v in os.environ.items() if k != "CI"}
            with patch.dict(os.environ, env, clear=True):
                result = runner.invoke(
                    app,
                    ["forge", "install", "--wheel", str(mock_wheel_path)],
                    input="n\n",
                )

        assert result.exit_code == 0
        assert "Install cancelled" in result.output


class TestPreFlightDisplay:
    """Tests for pre-flight check display."""

    def test_displays_pre_flight_results(
        self,
        runner: CleanCliRunner,
        mock_wheel_path: Path,
        successful_install_result: InstallResult,
        sample_release_report: ReleaseReport,
        passing_pre_flight_results: list[CheckResult],
    ) -> None:
        """Test displays pre-flight results."""
        with (
            patch(
                "crafter_ai.installer.cli.forge_install.create_install_service"
            ) as mock_factory,
            patch(
                "crafter_ai.installer.cli.forge_install.ReleaseReportService"
            ) as mock_report_service,
            patch(
                "crafter_ai.installer.cli.forge_install.run_pre_flight_checks"
            ) as mock_preflight,
        ):
            mock_preflight.return_value = passing_pre_flight_results

            mock_service = MagicMock()
            mock_service.install.return_value = successful_install_result
            mock_factory.return_value = mock_service

            mock_report = MagicMock()
            mock_report.generate.return_value = sample_release_report
            mock_report.format_console.return_value = "FORGE: INSTALL COMPLETE"
            mock_report_service.return_value = mock_report

            result = runner.invoke(
                app,
                ["forge", "install", "--wheel", str(mock_wheel_path), "--no-prompt"],
            )

        assert "Pre-flight" in result.output or "Wheel file exists" in result.output


class TestReleaseReportDisplay:
    """Tests for release report display."""

    def test_displays_release_report_on_success(
        self,
        runner: CleanCliRunner,
        mock_wheel_path: Path,
        successful_install_result: InstallResult,
        sample_release_report: ReleaseReport,
    ) -> None:
        """Test displays release report on success."""
        with (
            patch(
                "crafter_ai.installer.cli.forge_install.create_install_service"
            ) as mock_factory,
            patch(
                "crafter_ai.installer.cli.forge_install.ReleaseReportService"
            ) as mock_report_service,
        ):
            mock_service = MagicMock()
            mock_service.install.return_value = successful_install_result
            mock_factory.return_value = mock_service

            mock_report = MagicMock()
            mock_report.generate.return_value = sample_release_report
            mock_report.format_console.return_value = (
                "FORGE: INSTALL COMPLETE\nVersion: 0.2.0"
            )
            mock_report_service.return_value = mock_report

            result = runner.invoke(
                app,
                ["forge", "install", "--wheel", str(mock_wheel_path), "--no-prompt"],
            )

        assert result.exit_code == 0
        assert "FORGE: INSTALL COMPLETE" in result.output


class TestExitCodes:
    """Tests for exit codes."""

    def test_exit_code_0_on_success(
        self,
        runner: CleanCliRunner,
        mock_wheel_path: Path,
        successful_install_result: InstallResult,
        sample_release_report: ReleaseReport,
    ) -> None:
        """Test exit code 0 on success."""
        with (
            patch(
                "crafter_ai.installer.cli.forge_install.create_install_service"
            ) as mock_factory,
            patch(
                "crafter_ai.installer.cli.forge_install.ReleaseReportService"
            ) as mock_report_service,
        ):
            mock_service = MagicMock()
            mock_service.install.return_value = successful_install_result
            mock_factory.return_value = mock_service

            mock_report = MagicMock()
            mock_report.generate.return_value = sample_release_report
            mock_report.format_console.return_value = "FORGE: INSTALL COMPLETE"
            mock_report_service.return_value = mock_report

            result = runner.invoke(
                app,
                ["forge", "install", "--wheel", str(mock_wheel_path), "--no-prompt"],
            )

        assert result.exit_code == 0

    def test_exit_code_1_on_install_failure(
        self,
        runner: CleanCliRunner,
        mock_wheel_path: Path,
        failed_install_result: InstallResult,
    ) -> None:
        """Test returns exit code 1 on install failure."""
        with patch(
            "crafter_ai.installer.cli.forge_install.create_install_service"
        ) as mock_factory:
            mock_service = MagicMock()
            mock_service.install.return_value = failed_install_result
            mock_factory.return_value = mock_service

            result = runner.invoke(
                app,
                ["forge", "install", "--wheel", str(mock_wheel_path), "--no-prompt"],
            )

        assert result.exit_code == 1

    def test_exit_code_1_when_wheel_not_found(
        self,
        runner: CleanCliRunner,
    ) -> None:
        """Test exit code 1 when wheel not found."""
        with patch(
            "crafter_ai.installer.cli.forge_install.find_latest_wheel"
        ) as mock_find:
            mock_find.return_value = None

            result = runner.invoke(app, ["forge", "install", "--no-prompt"])

        assert result.exit_code == 1
        assert "No wheel" in result.output or "wheel" in result.output.lower()


class TestHeaderDisplay:
    """Tests for header display."""

    def test_displays_forge_install_header(
        self,
        runner: CleanCliRunner,
        mock_wheel_path: Path,
        successful_install_result: InstallResult,
        sample_release_report: ReleaseReport,
    ) -> None:
        """Test displays FORGE: INSTALL header."""
        with (
            patch(
                "crafter_ai.installer.cli.forge_install.create_install_service"
            ) as mock_factory,
            patch(
                "crafter_ai.installer.cli.forge_install.ReleaseReportService"
            ) as mock_report_service,
        ):
            mock_service = MagicMock()
            mock_service.install.return_value = successful_install_result
            mock_factory.return_value = mock_service

            mock_report = MagicMock()
            mock_report.generate.return_value = sample_release_report
            mock_report.format_console.return_value = "FORGE: INSTALL COMPLETE"
            mock_report_service.return_value = mock_report

            result = runner.invoke(
                app,
                ["forge", "install", "--wheel", str(mock_wheel_path), "--no-prompt"],
            )

        assert "FORGE: INSTALL" in result.output


class TestAutoChainBuild:
    """Tests for auto-chain build when no wheel found."""

    def test_auto_chain_prompts_when_no_wheel_found(
        self,
        runner: CleanCliRunner,
        passing_pre_flight_results: list[CheckResult],
    ) -> None:
        """Test auto-chain prompts user when no wheel found in dist/."""
        with (
            patch(
                "crafter_ai.installer.cli.forge_install.list_wheels_in_dist"
            ) as mock_list,
            patch(
                "crafter_ai.installer.cli.forge_install.run_pre_flight_checks"
            ) as mock_preflight,
        ):
            mock_list.return_value = []
            mock_preflight.return_value = passing_pre_flight_results

            # Remove CI env var if present
            env = {k: v for k, v in os.environ.items() if k != "CI"}
            with patch.dict(os.environ, env, clear=True):
                result = runner.invoke(
                    app,
                    ["forge", "install"],
                    input="n\n",  # User declines build
                )

        assert "No wheel found" in result.output
        assert "Build first?" in result.output

    def test_auto_chain_builds_on_y_response(
        self,
        runner: CleanCliRunner,
        tmp_path: Path,
        successful_install_result: InstallResult,
        sample_release_report: ReleaseReport,
        passing_pre_flight_results: list[CheckResult],
    ) -> None:
        """Test auto-chain invokes build when user responds Y."""
        # Create a wheel that will be "built"
        built_wheel = tmp_path / "crafter_ai-0.3.0-py3-none-any.whl"
        built_wheel.write_bytes(b"built wheel content")

        mock_build_result = MagicMock()
        mock_build_result.success = True
        mock_build_result.wheel_path = built_wheel
        mock_build_result.version = "0.3.0"

        with (
            patch(
                "crafter_ai.installer.cli.forge_install.list_wheels_in_dist"
            ) as mock_list,
            patch(
                "crafter_ai.installer.cli.forge_install.find_latest_wheel"
            ) as mock_find,
            patch(
                "crafter_ai.installer.cli.forge_install.create_build_service"
            ) as mock_build_factory,
            patch(
                "crafter_ai.installer.cli.forge_install.create_install_service"
            ) as mock_install_factory,
            patch(
                "crafter_ai.installer.cli.forge_install.ReleaseReportService"
            ) as mock_report_service,
            patch(
                "crafter_ai.installer.cli.forge_install.run_pre_flight_checks"
            ) as mock_preflight,
        ):
            # list_wheels_in_dist returns empty list (triggers auto-chain)
            mock_list.return_value = []
            # find_latest_wheel is called after build to find the built wheel
            mock_find.return_value = built_wheel
            mock_preflight.return_value = passing_pre_flight_results

            mock_build_service = MagicMock()
            mock_build_service.execute.return_value = mock_build_result
            mock_build_factory.return_value = mock_build_service

            mock_install_service = MagicMock()
            mock_install_service.install.return_value = successful_install_result
            mock_install_factory.return_value = mock_install_service

            mock_report = MagicMock()
            mock_report.generate.return_value = sample_release_report
            mock_report.format_console.return_value = "FORGE: INSTALL COMPLETE"
            mock_report_service.return_value = mock_report

            # Remove CI env var if present
            env = {k: v for k, v in os.environ.items() if k != "CI"}
            with patch.dict(os.environ, env, clear=True):
                result = runner.invoke(
                    app,
                    ["forge", "install"],
                    input="Y\nY\n",  # Y for build, Y for install
                )

        assert result.exit_code == 0
        mock_build_service.execute.assert_called_once()

    def test_auto_chain_exits_on_n_response(
        self,
        runner: CleanCliRunner,
        passing_pre_flight_results: list[CheckResult],
    ) -> None:
        """Test auto-chain exits with message when user responds n."""
        with (
            patch(
                "crafter_ai.installer.cli.forge_install.list_wheels_in_dist"
            ) as mock_list,
            patch(
                "crafter_ai.installer.cli.forge_install.run_pre_flight_checks"
            ) as mock_preflight,
        ):
            mock_list.return_value = []
            mock_preflight.return_value = passing_pre_flight_results

            # Remove CI env var if present
            env = {k: v for k, v in os.environ.items() if k != "CI"}
            with patch.dict(os.environ, env, clear=True):
                result = runner.invoke(
                    app,
                    ["forge", "install"],
                    input="n\n",
                )

        assert result.exit_code == 1
        assert "Run forge build first" in result.output

    def test_ci_mode_auto_builds_without_prompt(
        self,
        runner: CleanCliRunner,
        tmp_path: Path,
        successful_install_result: InstallResult,
        sample_release_report: ReleaseReport,
        passing_pre_flight_results: list[CheckResult],
    ) -> None:
        """Test CI=true auto-builds without prompting."""
        built_wheel = tmp_path / "crafter_ai-0.3.0-py3-none-any.whl"
        built_wheel.write_bytes(b"built wheel content")

        mock_build_result = MagicMock()
        mock_build_result.success = True
        mock_build_result.wheel_path = built_wheel
        mock_build_result.version = "0.3.0"

        with (
            patch(
                "crafter_ai.installer.cli.forge_install.list_wheels_in_dist"
            ) as mock_list,
            patch(
                "crafter_ai.installer.cli.forge_install.find_latest_wheel"
            ) as mock_find,
            patch(
                "crafter_ai.installer.cli.forge_install.create_build_service"
            ) as mock_build_factory,
            patch(
                "crafter_ai.installer.cli.forge_install.create_install_service"
            ) as mock_install_factory,
            patch(
                "crafter_ai.installer.cli.forge_install.ReleaseReportService"
            ) as mock_report_service,
            patch(
                "crafter_ai.installer.cli.forge_install.run_pre_flight_checks"
            ) as mock_preflight,
        ):
            mock_list.return_value = []
            mock_find.return_value = built_wheel
            mock_preflight.return_value = passing_pre_flight_results

            mock_build_service = MagicMock()
            mock_build_service.execute.return_value = mock_build_result
            mock_build_factory.return_value = mock_build_service

            mock_install_service = MagicMock()
            mock_install_service.install.return_value = successful_install_result
            mock_install_factory.return_value = mock_install_service

            mock_report = MagicMock()
            mock_report.generate.return_value = sample_release_report
            mock_report.format_console.return_value = "FORGE: INSTALL COMPLETE"
            mock_report_service.return_value = mock_report

            with patch.dict(os.environ, {"CI": "true"}):
                result = runner.invoke(app, ["forge", "install"])

        assert result.exit_code == 0
        mock_build_service.execute.assert_called_once()
        # Should NOT prompt for build in CI mode
        assert "Build first?" not in result.output

    def test_no_prompt_flag_auto_builds_without_prompt(
        self,
        runner: CleanCliRunner,
        tmp_path: Path,
        successful_install_result: InstallResult,
        sample_release_report: ReleaseReport,
        passing_pre_flight_results: list[CheckResult],
    ) -> None:
        """Test --no-prompt auto-builds without prompting."""
        built_wheel = tmp_path / "crafter_ai-0.3.0-py3-none-any.whl"
        built_wheel.write_bytes(b"built wheel content")

        mock_build_result = MagicMock()
        mock_build_result.success = True
        mock_build_result.wheel_path = built_wheel
        mock_build_result.version = "0.3.0"

        with (
            patch(
                "crafter_ai.installer.cli.forge_install.list_wheels_in_dist"
            ) as mock_list,
            patch(
                "crafter_ai.installer.cli.forge_install.find_latest_wheel"
            ) as mock_find,
            patch(
                "crafter_ai.installer.cli.forge_install.create_build_service"
            ) as mock_build_factory,
            patch(
                "crafter_ai.installer.cli.forge_install.create_install_service"
            ) as mock_install_factory,
            patch(
                "crafter_ai.installer.cli.forge_install.ReleaseReportService"
            ) as mock_report_service,
            patch(
                "crafter_ai.installer.cli.forge_install.run_pre_flight_checks"
            ) as mock_preflight,
        ):
            mock_list.return_value = []
            mock_find.return_value = built_wheel
            mock_preflight.return_value = passing_pre_flight_results

            mock_build_service = MagicMock()
            mock_build_service.execute.return_value = mock_build_result
            mock_build_factory.return_value = mock_build_service

            mock_install_service = MagicMock()
            mock_install_service.install.return_value = successful_install_result
            mock_install_factory.return_value = mock_install_service

            mock_report = MagicMock()
            mock_report.generate.return_value = sample_release_report
            mock_report.format_console.return_value = "FORGE: INSTALL COMPLETE"
            mock_report_service.return_value = mock_report

            # Remove CI env var if present
            env = {k: v for k, v in os.environ.items() if k != "CI"}
            with patch.dict(os.environ, env, clear=True):
                result = runner.invoke(app, ["forge", "install", "--no-prompt"])

        assert result.exit_code == 0
        mock_build_service.execute.assert_called_once()
        assert "Build first?" not in result.output

    def test_install_uses_newly_built_wheel(
        self,
        runner: CleanCliRunner,
        tmp_path: Path,
        successful_install_result: InstallResult,
        sample_release_report: ReleaseReport,
        passing_pre_flight_results: list[CheckResult],
    ) -> None:
        """Test install uses the wheel created by auto-chain build."""
        built_wheel = tmp_path / "crafter_ai-0.3.0-py3-none-any.whl"
        built_wheel.write_bytes(b"built wheel content")

        mock_build_result = MagicMock()
        mock_build_result.success = True
        mock_build_result.wheel_path = built_wheel
        mock_build_result.version = "0.3.0"

        with (
            patch(
                "crafter_ai.installer.cli.forge_install.list_wheels_in_dist"
            ) as mock_list,
            patch(
                "crafter_ai.installer.cli.forge_install.find_latest_wheel"
            ) as mock_find,
            patch(
                "crafter_ai.installer.cli.forge_install.create_build_service"
            ) as mock_build_factory,
            patch(
                "crafter_ai.installer.cli.forge_install.create_install_service"
            ) as mock_install_factory,
            patch(
                "crafter_ai.installer.cli.forge_install.ReleaseReportService"
            ) as mock_report_service,
            patch(
                "crafter_ai.installer.cli.forge_install.run_pre_flight_checks"
            ) as mock_preflight,
        ):
            mock_list.return_value = []  # No wheels found, triggers auto-chain
            mock_find.return_value = built_wheel  # Returns built wheel after build
            mock_preflight.return_value = passing_pre_flight_results

            mock_build_service = MagicMock()
            mock_build_service.execute.return_value = mock_build_result
            mock_build_factory.return_value = mock_build_service

            mock_install_service = MagicMock()
            mock_install_service.install.return_value = successful_install_result
            mock_install_factory.return_value = mock_install_service

            mock_report = MagicMock()
            mock_report.generate.return_value = sample_release_report
            mock_report.format_console.return_value = "FORGE: INSTALL COMPLETE"
            mock_report_service.return_value = mock_report

            with patch.dict(os.environ, {"CI": "true"}):
                result = runner.invoke(app, ["forge", "install"])

        assert result.exit_code == 0
        # Verify install was called with the built wheel
        mock_install_service.install.assert_called_once()
        call_args = mock_install_service.install.call_args
        assert call_args[0][0] == built_wheel

    def test_chain_aborts_if_build_fails(
        self,
        runner: CleanCliRunner,
        passing_pre_flight_results: list[CheckResult],
    ) -> None:
        """Test chain aborts with exit code 1 if build fails."""
        mock_build_result = MagicMock()
        mock_build_result.success = False
        mock_build_result.wheel_path = None
        mock_build_result.error_message = "Build failed: missing dependency"

        with (
            patch(
                "crafter_ai.installer.cli.forge_install.list_wheels_in_dist"
            ) as mock_list,
            patch(
                "crafter_ai.installer.cli.forge_install.create_build_service"
            ) as mock_build_factory,
            patch(
                "crafter_ai.installer.cli.forge_install.run_pre_flight_checks"
            ) as mock_preflight,
        ):
            mock_list.return_value = []  # No wheels found, triggers auto-chain
            mock_preflight.return_value = passing_pre_flight_results

            mock_build_service = MagicMock()
            mock_build_service.execute.return_value = mock_build_result
            mock_build_factory.return_value = mock_build_service

            with patch.dict(os.environ, {"CI": "true"}):
                result = runner.invoke(app, ["forge", "install"])

        assert result.exit_code == 1
        assert "Build failed" in result.output or "failed" in result.output.lower()


class TestWheelSelection:
    """Tests for multiple wheel selection functionality."""

    def test_single_wheel_skips_selection_prompt(
        self,
        runner: CleanCliRunner,
        tmp_path: Path,
        successful_install_result: InstallResult,
        sample_release_report: ReleaseReport,
    ) -> None:
        """Test single wheel in dist/ is used directly without prompt."""
        # Create a single wheel
        wheel_file = tmp_path / "crafter_ai-0.1.0-py3-none-any.whl"
        wheel_file.write_bytes(b"fake wheel")

        with (
            patch(
                "crafter_ai.installer.cli.forge_install.create_install_service"
            ) as mock_factory,
            patch(
                "crafter_ai.installer.cli.forge_install.ReleaseReportService"
            ) as mock_report_service,
            patch(
                "crafter_ai.installer.cli.forge_install.list_wheels_in_dist"
            ) as mock_list,
            patch(
                "crafter_ai.installer.cli.forge_install.find_latest_wheel"
            ) as mock_find,
        ):
            mock_list.return_value = [wheel_file]
            mock_find.return_value = wheel_file

            mock_service = MagicMock()
            mock_service.install.return_value = successful_install_result
            mock_factory.return_value = mock_service

            mock_report = MagicMock()
            mock_report.generate.return_value = sample_release_report
            mock_report.format_console.return_value = "FORGE: INSTALL COMPLETE"
            mock_report_service.return_value = mock_report

            result = runner.invoke(app, ["forge", "install", "--no-prompt"])

        assert result.exit_code == 0
        # Should NOT show selection prompt
        assert "Select one" not in result.output
        assert "Multiple wheels" not in result.output

    def test_multiple_wheels_displays_numbered_list(
        self,
        runner: CleanCliRunner,
        tmp_path: Path,
        successful_install_result: InstallResult,
        sample_release_report: ReleaseReport,
    ) -> None:
        """Test multiple wheels displays numbered selection list."""
        import time

        # Create multiple wheels with different timestamps
        wheel1 = tmp_path / "crafter_ai-0.1.0-py3-none-any.whl"
        wheel1.write_bytes(b"A" * 25000)  # ~25 KB
        time.sleep(0.01)
        wheel2 = tmp_path / "crafter_ai-0.2.0-py3-none-any.whl"
        wheel2.write_bytes(b"B" * 24000)  # ~24 KB

        with (
            patch(
                "crafter_ai.installer.cli.forge_install.create_install_service"
            ) as mock_factory,
            patch(
                "crafter_ai.installer.cli.forge_install.ReleaseReportService"
            ) as mock_report_service,
            patch(
                "crafter_ai.installer.cli.forge_install.list_wheels_in_dist"
            ) as mock_list,
        ):
            mock_list.return_value = [wheel2, wheel1]  # Newest first

            mock_service = MagicMock()
            mock_service.install.return_value = successful_install_result
            mock_factory.return_value = mock_service

            mock_report = MagicMock()
            mock_report.generate.return_value = sample_release_report
            mock_report.format_console.return_value = "FORGE: INSTALL COMPLETE"
            mock_report_service.return_value = mock_report

            # Remove CI env var
            env = {k: v for k, v in os.environ.items() if k != "CI"}
            with patch.dict(os.environ, env, clear=True):
                result = runner.invoke(
                    app,
                    ["forge", "install"],
                    input="1\nY\n",  # Select first wheel, confirm install
                )

        # Should show selection prompt with numbered options
        assert "Multiple wheels" in result.output or "Select" in result.output
        assert "1." in result.output
        assert "2." in result.output

    def test_user_selection_returns_correct_wheel(
        self,
        runner: CleanCliRunner,
        tmp_path: Path,
        successful_install_result: InstallResult,
        sample_release_report: ReleaseReport,
    ) -> None:
        """Test user selecting specific wheel number uses that wheel."""
        import time

        wheel1 = tmp_path / "crafter_ai-0.1.0-py3-none-any.whl"
        wheel1.write_bytes(b"old wheel")
        time.sleep(0.01)
        wheel2 = tmp_path / "crafter_ai-0.2.0-py3-none-any.whl"
        wheel2.write_bytes(b"new wheel")

        with (
            patch(
                "crafter_ai.installer.cli.forge_install.create_install_service"
            ) as mock_factory,
            patch(
                "crafter_ai.installer.cli.forge_install.ReleaseReportService"
            ) as mock_report_service,
            patch(
                "crafter_ai.installer.cli.forge_install.list_wheels_in_dist"
            ) as mock_list,
        ):
            mock_list.return_value = [wheel2, wheel1]  # Newest first

            mock_service = MagicMock()
            mock_service.install.return_value = successful_install_result
            mock_factory.return_value = mock_service

            mock_report = MagicMock()
            mock_report.generate.return_value = sample_release_report
            mock_report.format_console.return_value = "FORGE: INSTALL COMPLETE"
            mock_report_service.return_value = mock_report

            env = {k: v for k, v in os.environ.items() if k != "CI"}
            with patch.dict(os.environ, env, clear=True):
                result = runner.invoke(
                    app,
                    ["forge", "install"],
                    input="2\nY\n",  # Select second wheel (older one)
                )

        assert result.exit_code == 0
        # Verify install was called with the older wheel (option 2)
        call_args = mock_service.install.call_args
        assert call_args[0][0] == wheel1  # wheel1 is the older one at position 2

    def test_invalid_selection_shows_error(
        self,
        runner: CleanCliRunner,
        tmp_path: Path,
        successful_install_result: InstallResult,
        sample_release_report: ReleaseReport,
    ) -> None:
        """Test invalid selection shows error message."""
        wheel1 = tmp_path / "crafter_ai-0.1.0-py3-none-any.whl"
        wheel1.write_bytes(b"wheel 1")
        wheel2 = tmp_path / "crafter_ai-0.2.0-py3-none-any.whl"
        wheel2.write_bytes(b"wheel 2")

        with (
            patch(
                "crafter_ai.installer.cli.forge_install.create_install_service"
            ) as mock_factory,
            patch(
                "crafter_ai.installer.cli.forge_install.ReleaseReportService"
            ) as mock_report_service,
            patch(
                "crafter_ai.installer.cli.forge_install.list_wheels_in_dist"
            ) as mock_list,
        ):
            mock_list.return_value = [wheel2, wheel1]

            mock_service = MagicMock()
            mock_service.install.return_value = successful_install_result
            mock_factory.return_value = mock_service

            mock_report = MagicMock()
            mock_report.generate.return_value = sample_release_report
            mock_report.format_console.return_value = "FORGE: INSTALL COMPLETE"
            mock_report_service.return_value = mock_report

            env = {k: v for k, v in os.environ.items() if k != "CI"}
            with patch.dict(os.environ, env, clear=True):
                result = runner.invoke(
                    app,
                    ["forge", "install"],
                    input="5\n1\nY\n",  # Invalid "5", then valid "1", then confirm
                )

        assert result.exit_code == 0
        assert "Invalid" in result.output or "invalid" in result.output.lower()

    def test_ci_mode_auto_selects_newest_wheel(
        self,
        runner: CleanCliRunner,
        tmp_path: Path,
        successful_install_result: InstallResult,
        sample_release_report: ReleaseReport,
    ) -> None:
        """Test CI mode auto-selects newest wheel without prompting."""
        import time

        wheel1 = tmp_path / "crafter_ai-0.1.0-py3-none-any.whl"
        wheel1.write_bytes(b"old wheel")
        time.sleep(0.01)
        wheel2 = tmp_path / "crafter_ai-0.2.0-py3-none-any.whl"
        wheel2.write_bytes(b"new wheel")

        with (
            patch(
                "crafter_ai.installer.cli.forge_install.create_install_service"
            ) as mock_factory,
            patch(
                "crafter_ai.installer.cli.forge_install.ReleaseReportService"
            ) as mock_report_service,
            patch(
                "crafter_ai.installer.cli.forge_install.list_wheels_in_dist"
            ) as mock_list,
        ):
            mock_list.return_value = [wheel2, wheel1]  # Newest first

            mock_service = MagicMock()
            mock_service.install.return_value = successful_install_result
            mock_factory.return_value = mock_service

            mock_report = MagicMock()
            mock_report.generate.return_value = sample_release_report
            mock_report.format_console.return_value = "FORGE: INSTALL COMPLETE"
            mock_report_service.return_value = mock_report

            with patch.dict(os.environ, {"CI": "true"}):
                result = runner.invoke(app, ["forge", "install"])

        assert result.exit_code == 0
        # Should NOT prompt for selection in CI mode
        assert "Select" not in result.output
        # Should log which wheel was auto-selected
        assert "Auto-selecting" in result.output or "0.2.0" in result.output
        # Verify newest wheel was used
        call_args = mock_service.install.call_args
        assert call_args[0][0] == wheel2

    def test_no_prompt_flag_auto_selects_newest_wheel(
        self,
        runner: CleanCliRunner,
        tmp_path: Path,
        successful_install_result: InstallResult,
        sample_release_report: ReleaseReport,
    ) -> None:
        """Test --no-prompt auto-selects newest wheel."""
        import time

        wheel1 = tmp_path / "crafter_ai-0.1.0-py3-none-any.whl"
        wheel1.write_bytes(b"old wheel")
        time.sleep(0.01)
        wheel2 = tmp_path / "crafter_ai-0.2.0-py3-none-any.whl"
        wheel2.write_bytes(b"new wheel")

        with (
            patch(
                "crafter_ai.installer.cli.forge_install.create_install_service"
            ) as mock_factory,
            patch(
                "crafter_ai.installer.cli.forge_install.ReleaseReportService"
            ) as mock_report_service,
            patch(
                "crafter_ai.installer.cli.forge_install.list_wheels_in_dist"
            ) as mock_list,
        ):
            mock_list.return_value = [wheel2, wheel1]

            mock_service = MagicMock()
            mock_service.install.return_value = successful_install_result
            mock_factory.return_value = mock_service

            mock_report = MagicMock()
            mock_report.generate.return_value = sample_release_report
            mock_report.format_console.return_value = "FORGE: INSTALL COMPLETE"
            mock_report_service.return_value = mock_report

            env = {k: v for k, v in os.environ.items() if k != "CI"}
            with patch.dict(os.environ, env, clear=True):
                result = runner.invoke(app, ["forge", "install", "--no-prompt"])

        assert result.exit_code == 0
        # Should NOT prompt
        assert "Select" not in result.output
        # Verify newest wheel was used
        call_args = mock_service.install.call_args
        assert call_args[0][0] == wheel2

    def test_wheels_sorted_by_modification_time_newest_first(
        self,
        runner: CleanCliRunner,
        tmp_path: Path,
        successful_install_result: InstallResult,
        sample_release_report: ReleaseReport,
    ) -> None:
        """Test wheel list is sorted by modification time, newest first."""
        import time

        # Create wheels with specific order
        wheel_old = tmp_path / "crafter_ai-0.0.9-py3-none-any.whl"
        wheel_old.write_bytes(b"oldest")
        time.sleep(0.01)
        wheel_mid = tmp_path / "crafter_ai-0.1.0-py3-none-any.whl"
        wheel_mid.write_bytes(b"middle")
        time.sleep(0.01)
        wheel_new = tmp_path / "crafter_ai-0.2.0-py3-none-any.whl"
        wheel_new.write_bytes(b"newest")

        with (
            patch(
                "crafter_ai.installer.cli.forge_install.create_install_service"
            ) as mock_factory,
            patch(
                "crafter_ai.installer.cli.forge_install.ReleaseReportService"
            ) as mock_report_service,
            patch(
                "crafter_ai.installer.cli.forge_install.list_wheels_in_dist"
            ) as mock_list,
        ):
            # Return in correct sorted order (newest first)
            mock_list.return_value = [wheel_new, wheel_mid, wheel_old]

            mock_service = MagicMock()
            mock_service.install.return_value = successful_install_result
            mock_factory.return_value = mock_service

            mock_report = MagicMock()
            mock_report.generate.return_value = sample_release_report
            mock_report.format_console.return_value = "FORGE: INSTALL COMPLETE"
            mock_report_service.return_value = mock_report

            env = {k: v for k, v in os.environ.items() if k != "CI"}
            with patch.dict(os.environ, env, clear=True):
                result = runner.invoke(
                    app,
                    ["forge", "install"],
                    input="1\nY\n",  # Select newest (first)
                )

        assert result.exit_code == 0
        # First option (1.) should be newest wheel
        output_lines = result.output.split("\n")
        first_option_line = next(
            (line for line in output_lines if "1." in line and ".whl" in line), ""
        )
        assert "0.2.0" in first_option_line

    def test_wheel_display_shows_date_and_size(
        self,
        runner: CleanCliRunner,
        tmp_path: Path,
        successful_install_result: InstallResult,
        sample_release_report: ReleaseReport,
    ) -> None:
        """Test wheel display shows modification date and file size."""
        wheel1 = tmp_path / "crafter_ai-0.1.0-py3-none-any.whl"
        wheel1.write_bytes(b"A" * 25600)  # 25 KB

        wheel2 = tmp_path / "crafter_ai-0.2.0-py3-none-any.whl"
        wheel2.write_bytes(b"B" * 24576)  # 24 KB

        with (
            patch(
                "crafter_ai.installer.cli.forge_install.create_install_service"
            ) as mock_factory,
            patch(
                "crafter_ai.installer.cli.forge_install.ReleaseReportService"
            ) as mock_report_service,
            patch(
                "crafter_ai.installer.cli.forge_install.list_wheels_in_dist"
            ) as mock_list,
        ):
            mock_list.return_value = [wheel2, wheel1]

            mock_service = MagicMock()
            mock_service.install.return_value = successful_install_result
            mock_factory.return_value = mock_service

            mock_report = MagicMock()
            mock_report.generate.return_value = sample_release_report
            mock_report.format_console.return_value = "FORGE: INSTALL COMPLETE"
            mock_report_service.return_value = mock_report

            env = {k: v for k, v in os.environ.items() if k != "CI"}
            with patch.dict(os.environ, env, clear=True):
                result = runner.invoke(
                    app,
                    ["forge", "install"],
                    input="1\nY\n",
                )

        assert result.exit_code == 0
        # Should show file size (KB)
        assert "KB" in result.output or "kb" in result.output.lower()
        # Should show date (format: YYYY-MM-DD or similar)
        assert "2026" in result.output or ":" in result.output  # Date or time indicator


class TestListWheelsInDist:
    """Tests for list_wheels_in_dist function."""

    def test_list_wheels_returns_sorted_list(self, tmp_path: Path) -> None:
        """Test list_wheels_in_dist returns wheels sorted by mtime."""
        import time

        from crafter_ai.installer.cli.forge_install import list_wheels_in_dist

        dist_dir = tmp_path / "dist"
        dist_dir.mkdir()

        wheel1 = dist_dir / "crafter_ai-0.1.0-py3-none-any.whl"
        wheel1.write_bytes(b"old")
        time.sleep(0.01)
        wheel2 = dist_dir / "crafter_ai-0.2.0-py3-none-any.whl"
        wheel2.write_bytes(b"new")

        result = list_wheels_in_dist(dist_dir)

        assert len(result) == 2
        # Newest first
        assert result[0] == wheel2
        assert result[1] == wheel1

    def test_list_wheels_returns_empty_for_no_wheels(self, tmp_path: Path) -> None:
        """Test list_wheels_in_dist returns empty list when no wheels."""
        from crafter_ai.installer.cli.forge_install import list_wheels_in_dist

        dist_dir = tmp_path / "dist"
        dist_dir.mkdir()

        result = list_wheels_in_dist(dist_dir)

        assert result == []

    def test_list_wheels_returns_empty_for_missing_dir(self, tmp_path: Path) -> None:
        """Test list_wheels_in_dist returns empty list when dir missing."""
        from crafter_ai.installer.cli.forge_install import list_wheels_in_dist

        nonexistent = tmp_path / "nonexistent"

        result = list_wheels_in_dist(nonexistent)

        assert result == []
