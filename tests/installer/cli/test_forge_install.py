"""Tests for forge:install CLI command.

Tests the CLI layer using Typer's CliRunner with mocked InstallService
and ReleaseReportService. Verifies display rendering, user prompts, and exit codes.
"""

import os
from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from typer.testing import CliRunner

from crafter_ai.cli import app
from crafter_ai.installer.domain.check_result import CheckResult, CheckSeverity
from crafter_ai.installer.domain.health_result import HealthStatus
from crafter_ai.installer.services.install_service import InstallPhase, InstallResult
from crafter_ai.installer.services.release_report_service import ReleaseReport


@pytest.fixture
def runner() -> CliRunner:
    """Create a CLI test runner."""
    return CliRunner()


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

    def test_forge_install_command_registered(self, runner: CliRunner) -> None:
        """Test that forge install command is registered."""
        result = runner.invoke(app, ["forge", "--help"])
        assert result.exit_code == 0
        assert "install" in result.output

    def test_forge_install_help_shows_options(self, runner: CliRunner) -> None:
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
        runner: CliRunner,
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
        runner: CliRunner,
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
                "crafter_ai.installer.cli.forge_install.find_latest_wheel"
            ) as mock_find,
        ):
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
        mock_find.assert_called_once()


class TestForceFlag:
    """Tests for --force flag behavior."""

    def test_force_flag_passed_to_install_service(
        self,
        runner: CliRunner,
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
        runner: CliRunner,
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
        runner: CliRunner,
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
        runner: CliRunner,
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
        runner: CliRunner,
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
        runner: CliRunner,
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
        runner: CliRunner,
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
        runner: CliRunner,
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
        runner: CliRunner,
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
        runner: CliRunner,
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
        runner: CliRunner,
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
        runner: CliRunner,
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
        runner: CliRunner,
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
        runner: CliRunner,
        passing_pre_flight_results: list[CheckResult],
    ) -> None:
        """Test auto-chain prompts user when no wheel found in dist/."""
        with (
            patch(
                "crafter_ai.installer.cli.forge_install.find_latest_wheel"
            ) as mock_find,
            patch(
                "crafter_ai.installer.cli.forge_install.run_pre_flight_checks"
            ) as mock_preflight,
        ):
            mock_find.return_value = None
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
        runner: CliRunner,
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
            # First call returns None (no wheel), second call returns built wheel
            mock_find.side_effect = [None, built_wheel]
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
        runner: CliRunner,
        passing_pre_flight_results: list[CheckResult],
    ) -> None:
        """Test auto-chain exits with message when user responds n."""
        with (
            patch(
                "crafter_ai.installer.cli.forge_install.find_latest_wheel"
            ) as mock_find,
            patch(
                "crafter_ai.installer.cli.forge_install.run_pre_flight_checks"
            ) as mock_preflight,
        ):
            mock_find.return_value = None
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
        runner: CliRunner,
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
            mock_find.side_effect = [None, built_wheel]
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
        runner: CliRunner,
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
            mock_find.side_effect = [None, built_wheel]
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
        runner: CliRunner,
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
            mock_find.side_effect = [None, built_wheel]
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
        runner: CliRunner,
        passing_pre_flight_results: list[CheckResult],
    ) -> None:
        """Test chain aborts with exit code 1 if build fails."""
        mock_build_result = MagicMock()
        mock_build_result.success = False
        mock_build_result.wheel_path = None
        mock_build_result.error_message = "Build failed: missing dependency"

        with (
            patch(
                "crafter_ai.installer.cli.forge_install.find_latest_wheel"
            ) as mock_find,
            patch(
                "crafter_ai.installer.cli.forge_install.create_build_service"
            ) as mock_build_factory,
            patch(
                "crafter_ai.installer.cli.forge_install.run_pre_flight_checks"
            ) as mock_preflight,
        ):
            mock_find.return_value = None
            mock_preflight.return_value = passing_pre_flight_results

            mock_build_service = MagicMock()
            mock_build_service.execute.return_value = mock_build_result
            mock_build_factory.return_value = mock_build_service

            with patch.dict(os.environ, {"CI": "true"}):
                result = runner.invoke(app, ["forge", "install"])

        assert result.exit_code == 1
        assert "Build failed" in result.output or "failed" in result.output.lower()
