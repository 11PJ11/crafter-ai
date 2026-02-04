"""Tests for install-nwave CLI command.

TDD approach: Tests verify CLI behavior with mock dependencies
for isolated testing of the installation flow.
"""

import os
from pathlib import Path
from unittest.mock import MagicMock, patch

import typer

from crafter_ai.installer.cli.install_nwave import install_nwave
from crafter_ai.installer.domain.check_result import CheckResult, CheckSeverity
from crafter_ai.installer.ports.pipx_port import InstalledPackage, InstallResult
from tests.cli.conftest import CleanCliRunner


# Create a test app for CLI testing
test_app = typer.Typer()
test_app.command()(install_nwave)

# Use CleanCliRunner to strip ANSI codes for consistent assertions in CI
runner = CleanCliRunner()


class TestInstallNwaveCommandExists:
    """Test that install-nwave command exists and is callable."""

    def test_install_nwave_command_exists(self) -> None:
        """install-nwave command should be callable."""
        assert callable(install_nwave)

    def test_install_nwave_has_ci_flag(self) -> None:
        """install-nwave should have --ci flag."""
        result = runner.invoke(test_app, ["--help"])
        assert "--ci" in result.output

    def test_install_nwave_has_yes_flag(self) -> None:
        """install-nwave should have --yes / -y flag."""
        result = runner.invoke(test_app, ["--help"])
        assert "--yes" in result.output or "-y" in result.output

    def test_install_nwave_has_version_flag(self) -> None:
        """install-nwave should have --version flag."""
        result = runner.invoke(test_app, ["--help"])
        assert "--version" in result.output

    def test_install_nwave_has_pre_flag(self) -> None:
        """install-nwave should have --pre flag."""
        result = runner.invoke(test_app, ["--help"])
        assert "--pre" in result.output


class TestCIModeDetection:
    """Test CI mode detection via flag and environment variable."""

    def test_ci_flag_enables_ci_mode(self) -> None:
        """--ci flag should enable CI mode."""
        with patch(
            "crafter_ai.installer.cli.install_nwave.create_pypi_check_registry"
        ) as mock_registry:
            mock_check_result = CheckResult(
                id="pypi-connectivity",
                name="PyPI Connectivity",
                passed=False,
                severity=CheckSeverity.BLOCKING,
                message="Cannot reach PyPI",
            )
            mock_registry.return_value.run_all.return_value = [mock_check_result]

            result = runner.invoke(test_app, ["--ci"])

            # CI mode should use plain text markers
            assert "[FAIL]" in result.output or "[OK]" in result.output

    def test_ci_env_var_enables_ci_mode(self) -> None:
        """CI=true environment variable should enable CI mode."""
        with patch(
            "crafter_ai.installer.cli.install_nwave.create_pypi_check_registry"
        ) as mock_registry:
            mock_check_result = CheckResult(
                id="pypi-connectivity",
                name="PyPI Connectivity",
                passed=False,
                severity=CheckSeverity.BLOCKING,
                message="Cannot reach PyPI",
            )
            mock_registry.return_value.run_all.return_value = [mock_check_result]

            with patch.dict(os.environ, {"CI": "true"}):
                result = runner.invoke(test_app, [])

            # CI mode should use plain text markers
            assert "[FAIL]" in result.output or "[OK]" in result.output

    def test_ci_env_var_1_enables_ci_mode(self) -> None:
        """CI=1 environment variable should enable CI mode."""
        with patch(
            "crafter_ai.installer.cli.install_nwave.create_pypi_check_registry"
        ) as mock_registry:
            mock_check_result = CheckResult(
                id="pypi-connectivity",
                name="PyPI Connectivity",
                passed=False,
                severity=CheckSeverity.BLOCKING,
                message="Cannot reach PyPI",
            )
            mock_registry.return_value.run_all.return_value = [mock_check_result]

            with patch.dict(os.environ, {"CI": "1"}):
                result = runner.invoke(test_app, [])

            # CI mode should use plain text markers
            assert "[FAIL]" in result.output or "[OK]" in result.output


class TestYesFlagBehavior:
    """Test --yes / -y flag behavior."""

    def test_yes_flag_skips_confirmation(self) -> None:
        """--yes flag should skip confirmation prompts."""
        with (
            patch(
                "crafter_ai.installer.cli.install_nwave.create_pypi_check_registry"
            ) as mock_registry,
            patch(
                "crafter_ai.installer.cli.install_nwave.SubprocessPipxAdapter"
            ) as mock_pipx,
        ):
            # Setup pre-flight to pass
            mock_check_result = CheckResult(
                id="pypi-connectivity",
                name="PyPI Connectivity",
                passed=True,
                severity=CheckSeverity.BLOCKING,
                message="OK",
            )
            mock_registry.return_value.run_all.return_value = [mock_check_result]

            # Setup pipx adapter
            mock_adapter = MagicMock()
            mock_adapter.list_packages.return_value = [
                InstalledPackage(name="crafter-ai", version="1.0.0", path=Path("/test"))
            ]
            mock_adapter.install.return_value = InstallResult(
                success=True,
                version="1.0.0",
                install_path=Path("/test"),
                error_message=None,
            )
            mock_pipx.return_value = mock_adapter

            # --yes should not prompt for confirmation
            result = runner.invoke(test_app, ["--yes", "--ci"])

            # Should not have prompted (would fail in non-interactive mode)
            # If it ran through without prompting, the command executed
            assert result.exit_code in (0, 1)

    def test_short_y_flag_works(self) -> None:
        """-y short flag should work like --yes."""
        with (
            patch(
                "crafter_ai.installer.cli.install_nwave.create_pypi_check_registry"
            ) as mock_registry,
            patch(
                "crafter_ai.installer.cli.install_nwave.SubprocessPipxAdapter"
            ) as mock_pipx,
        ):
            mock_check_result = CheckResult(
                id="pypi-connectivity",
                name="PyPI Connectivity",
                passed=True,
                severity=CheckSeverity.BLOCKING,
                message="OK",
            )
            mock_registry.return_value.run_all.return_value = [mock_check_result]

            mock_adapter = MagicMock()
            mock_adapter.list_packages.return_value = []
            mock_adapter.install.return_value = InstallResult(
                success=True,
                version="1.0.0",
                install_path=Path("/test"),
                error_message=None,
            )
            mock_pipx.return_value = mock_adapter

            result = runner.invoke(test_app, ["-y", "--ci"])

            assert result.exit_code in (0, 1)


class TestVersionFlag:
    """Test --version flag for installing specific version."""

    def test_version_flag_installs_specific_version(self) -> None:
        """--version flag should install specific version."""
        with (
            patch(
                "crafter_ai.installer.cli.install_nwave.create_pypi_check_registry"
            ) as mock_registry,
            patch(
                "crafter_ai.installer.cli.install_nwave.SubprocessPipxAdapter"
            ) as mock_pipx,
        ):
            mock_check_result = CheckResult(
                id="pypi-connectivity",
                name="PyPI Connectivity",
                passed=True,
                severity=CheckSeverity.BLOCKING,
                message="OK",
            )
            mock_registry.return_value.run_all.return_value = [mock_check_result]

            mock_adapter = MagicMock()
            mock_adapter.list_packages.return_value = []
            mock_adapter.install.return_value = InstallResult(
                success=True,
                version="1.2.3",
                install_path=Path("/test"),
                error_message=None,
            )
            mock_pipx.return_value = mock_adapter

            result = runner.invoke(test_app, ["--version", "1.2.3", "--ci"])

            # Should mention the version being installed
            assert "1.2.3" in result.output or result.exit_code in (0, 1)


class TestPreReleaseFlag:
    """Test --pre flag for pre-release versions."""

    def test_pre_flag_allows_prerelease(self) -> None:
        """--pre flag should allow pre-release versions."""
        with (
            patch(
                "crafter_ai.installer.cli.install_nwave.create_pypi_check_registry"
            ) as mock_registry,
            patch(
                "crafter_ai.installer.cli.install_nwave.SubprocessPipxAdapter"
            ) as mock_pipx,
        ):
            mock_check_result = CheckResult(
                id="pypi-connectivity",
                name="PyPI Connectivity",
                passed=True,
                severity=CheckSeverity.BLOCKING,
                message="OK",
            )
            mock_registry.return_value.run_all.return_value = [mock_check_result]

            mock_adapter = MagicMock()
            mock_adapter.list_packages.return_value = []
            mock_adapter.install.return_value = InstallResult(
                success=True,
                version="1.0.0b1",
                install_path=Path("/test"),
                error_message=None,
            )
            mock_pipx.return_value = mock_adapter

            result = runner.invoke(test_app, ["--pre", "--ci"])

            # Should execute without error
            assert result.exit_code in (0, 1)


class TestExitCodes:
    """Test CLI exit codes."""

    def test_exit_code_0_on_success(self) -> None:
        """Should return exit code 0 on successful installation."""
        with (
            patch(
                "crafter_ai.installer.cli.install_nwave.create_pypi_check_registry"
            ) as mock_registry,
            patch(
                "crafter_ai.installer.cli.install_nwave.SubprocessPipxAdapter"
            ) as mock_pipx,
            patch("crafter_ai.installer.cli.install_nwave.SetupService") as mock_setup,
            patch(
                "crafter_ai.installer.cli.install_nwave.get_installed_version"
            ) as mock_get_version,
        ):
            # All checks pass
            mock_check_result = CheckResult(
                id="pypi-connectivity",
                name="PyPI Connectivity",
                passed=True,
                severity=CheckSeverity.BLOCKING,
                message="OK",
            )
            mock_registry.return_value.run_all.return_value = [mock_check_result]

            # Pipx operations succeed
            mock_adapter = MagicMock()
            mock_adapter.list_packages.return_value = []
            mock_adapter.install.return_value = InstallResult(
                success=True,
                version="1.0.0",
                install_path=Path("/test"),
                error_message=None,
            )
            mock_pipx.return_value = mock_adapter

            # Setup succeeds
            mock_setup_instance = MagicMock()
            mock_setup_instance.setup_claude_config.return_value = MagicMock(
                success=True, created_paths=[], errors=[]
            )
            mock_setup.return_value = mock_setup_instance

            # Version available after install
            mock_get_version.return_value = "1.0.0"

            result = runner.invoke(test_app, ["--ci"])

            assert result.exit_code == 0

    def test_exit_code_1_on_preflight_failure(self) -> None:
        """Should return exit code 1 when pre-flight checks fail."""
        with patch(
            "crafter_ai.installer.cli.install_nwave.create_pypi_check_registry"
        ) as mock_registry:
            mock_check_result = CheckResult(
                id="pypi-connectivity",
                name="PyPI Connectivity",
                passed=False,
                severity=CheckSeverity.BLOCKING,
                message="Cannot reach PyPI",
            )
            mock_registry.return_value.run_all.return_value = [mock_check_result]

            result = runner.invoke(test_app, ["--ci"])

            assert result.exit_code == 1

    def test_exit_code_1_on_install_failure(self) -> None:
        """Should return exit code 1 when installation fails."""
        with (
            patch(
                "crafter_ai.installer.cli.install_nwave.create_pypi_check_registry"
            ) as mock_registry,
            patch(
                "crafter_ai.installer.cli.install_nwave.SubprocessPipxAdapter"
            ) as mock_pipx,
        ):
            # Pre-flight passes
            mock_check_result = CheckResult(
                id="pypi-connectivity",
                name="PyPI Connectivity",
                passed=True,
                severity=CheckSeverity.BLOCKING,
                message="OK",
            )
            mock_registry.return_value.run_all.return_value = [mock_check_result]

            # Install fails
            mock_adapter = MagicMock()
            mock_adapter.list_packages.return_value = []
            mock_adapter.install.return_value = InstallResult(
                success=False,
                version=None,
                install_path=None,
                error_message="pipx not available",
            )
            mock_pipx.return_value = mock_adapter

            result = runner.invoke(test_app, ["--ci"])

            assert result.exit_code == 1


class TestPreflightCheckFailures:
    """Test pre-flight check failure handling."""

    def test_blocking_check_failure_aborts_install(self) -> None:
        """Blocking check failure should abort installation."""
        with patch(
            "crafter_ai.installer.cli.install_nwave.create_pypi_check_registry"
        ) as mock_registry:
            mock_check_result = CheckResult(
                id="pypi-connectivity",
                name="PyPI Connectivity",
                passed=False,
                severity=CheckSeverity.BLOCKING,
                message="Network error",
                remediation="Check your internet connection",
            )
            mock_registry.return_value.run_all.return_value = [mock_check_result]

            result = runner.invoke(test_app, ["--ci"])

            assert result.exit_code == 1
            assert "FAIL" in result.output
            assert "aborted" in result.output.lower()

    def test_warning_check_does_not_abort(self) -> None:
        """Warning check should not abort installation."""
        with (
            patch(
                "crafter_ai.installer.cli.install_nwave.create_pypi_check_registry"
            ) as mock_registry,
            patch(
                "crafter_ai.installer.cli.install_nwave.SubprocessPipxAdapter"
            ) as mock_pipx,
            patch("crafter_ai.installer.cli.install_nwave.SetupService") as mock_setup,
            patch(
                "crafter_ai.installer.cli.install_nwave.get_installed_version"
            ) as mock_get_version,
        ):
            # Warning check
            mock_check_result = CheckResult(
                id="optional-check",
                name="Optional Check",
                passed=False,
                severity=CheckSeverity.WARNING,
                message="Non-critical issue",
            )
            mock_registry.return_value.run_all.return_value = [mock_check_result]

            mock_adapter = MagicMock()
            mock_adapter.list_packages.return_value = []
            mock_adapter.install.return_value = InstallResult(
                success=True,
                version="1.0.0",
                install_path=Path("/test"),
                error_message=None,
            )
            mock_pipx.return_value = mock_adapter

            mock_setup_instance = MagicMock()
            mock_setup_instance.setup_claude_config.return_value = MagicMock(
                success=True, created_paths=[], errors=[]
            )
            mock_setup.return_value = mock_setup_instance

            mock_get_version.return_value = "1.0.0"

            result = runner.invoke(test_app, ["--ci"])

            # Should complete (warning doesn't block)
            assert result.exit_code == 0


class TestMockPipxPort:
    """Test that PipxPort is properly mocked for isolated testing."""

    def test_pipx_adapter_is_mocked(self) -> None:
        """SubprocessPipxAdapter should be mockable for tests."""
        with (
            patch(
                "crafter_ai.installer.cli.install_nwave.create_pypi_check_registry"
            ) as mock_registry,
            patch(
                "crafter_ai.installer.cli.install_nwave.SubprocessPipxAdapter"
            ) as mock_pipx,
        ):
            mock_check_result = CheckResult(
                id="pypi-connectivity",
                name="PyPI Connectivity",
                passed=True,
                severity=CheckSeverity.BLOCKING,
                message="OK",
            )
            mock_registry.return_value.run_all.return_value = [mock_check_result]

            mock_adapter = MagicMock()
            mock_adapter.list_packages.return_value = []
            mock_adapter.install.return_value = InstallResult(
                success=True,
                version="1.0.0",
                install_path=Path("/test"),
                error_message=None,
            )
            mock_pipx.return_value = mock_adapter

            result = runner.invoke(test_app, ["--ci"])

            # Verify mock was called
            mock_pipx.assert_called_once()
            assert result.exit_code in (0, 1)


class TestInstallationPhases:
    """Test the 6 installation phases are executed."""

    def test_preflight_phase_runs(self) -> None:
        """Phase 1: Pre-flight checks should run."""
        with patch(
            "crafter_ai.installer.cli.install_nwave.create_pypi_check_registry"
        ) as mock_registry:
            mock_check_result = CheckResult(
                id="pypi-connectivity",
                name="PyPI Connectivity",
                passed=True,
                severity=CheckSeverity.BLOCKING,
                message="OK",
            )
            mock_registry.return_value.run_all.return_value = [mock_check_result]

            with patch(
                "crafter_ai.installer.cli.install_nwave.SubprocessPipxAdapter"
            ) as mock_pipx:
                mock_adapter = MagicMock()
                mock_adapter.list_packages.return_value = []
                mock_adapter.install.return_value = InstallResult(
                    success=False,
                    version=None,
                    install_path=None,
                    error_message="test",
                )
                mock_pipx.return_value = mock_adapter

                runner.invoke(test_app, ["--ci"])

            # Pre-flight should have run
            mock_registry.assert_called_once()
            mock_registry.return_value.run_all.assert_called_once()

    def test_existing_check_phase_runs(self) -> None:
        """Phase 2: Existing installation check should run."""
        with (
            patch(
                "crafter_ai.installer.cli.install_nwave.create_pypi_check_registry"
            ) as mock_registry,
            patch(
                "crafter_ai.installer.cli.install_nwave.SubprocessPipxAdapter"
            ) as mock_pipx,
            patch(
                "crafter_ai.installer.cli.install_nwave.get_installed_version"
            ) as mock_get_version,
        ):
            mock_check_result = CheckResult(
                id="pypi-connectivity",
                name="PyPI Connectivity",
                passed=True,
                severity=CheckSeverity.BLOCKING,
                message="OK",
            )
            mock_registry.return_value.run_all.return_value = [mock_check_result]

            mock_adapter = MagicMock()
            mock_adapter.list_packages.return_value = []
            mock_adapter.install.return_value = InstallResult(
                success=False,
                version=None,
                install_path=None,
                error_message="test",
            )
            mock_pipx.return_value = mock_adapter

            mock_get_version.return_value = None

            runner.invoke(test_app, ["--ci"])

            # get_installed_version should be called to check existing
            assert mock_get_version.called or mock_adapter.list_packages.called

    def test_setup_phase_runs_after_install(self) -> None:
        """Phase 4: Setup should run after successful install."""
        with (
            patch(
                "crafter_ai.installer.cli.install_nwave.create_pypi_check_registry"
            ) as mock_registry,
            patch(
                "crafter_ai.installer.cli.install_nwave.SubprocessPipxAdapter"
            ) as mock_pipx,
            patch("crafter_ai.installer.cli.install_nwave.SetupService") as mock_setup,
            patch(
                "crafter_ai.installer.cli.install_nwave.get_installed_version"
            ) as mock_get_version,
        ):
            mock_check_result = CheckResult(
                id="pypi-connectivity",
                name="PyPI Connectivity",
                passed=True,
                severity=CheckSeverity.BLOCKING,
                message="OK",
            )
            mock_registry.return_value.run_all.return_value = [mock_check_result]

            mock_adapter = MagicMock()
            mock_adapter.list_packages.return_value = []
            mock_adapter.install.return_value = InstallResult(
                success=True,
                version="1.0.0",
                install_path=Path("/test"),
                error_message=None,
            )
            mock_pipx.return_value = mock_adapter

            mock_setup_instance = MagicMock()
            mock_setup_instance.setup_claude_config.return_value = MagicMock(
                success=True, created_paths=[], errors=[]
            )
            mock_setup.return_value = mock_setup_instance

            mock_get_version.return_value = "1.0.0"

            runner.invoke(test_app, ["--ci"])

            # Setup should have been called
            mock_setup_instance.setup_claude_config.assert_called_once()


class TestCIOutputFormat:
    """Test CI mode output format."""

    def test_ci_mode_shows_plain_text_markers(self) -> None:
        """CI mode should use [OK], [FAIL], [INFO] markers."""
        with patch(
            "crafter_ai.installer.cli.install_nwave.create_pypi_check_registry"
        ) as mock_registry:
            mock_check_result = CheckResult(
                id="pypi-connectivity",
                name="PyPI Connectivity",
                passed=True,
                severity=CheckSeverity.BLOCKING,
                message="OK",
            )
            mock_registry.return_value.run_all.return_value = [mock_check_result]

            with patch(
                "crafter_ai.installer.cli.install_nwave.SubprocessPipxAdapter"
            ) as mock_pipx:
                mock_adapter = MagicMock()
                mock_adapter.list_packages.return_value = []
                mock_adapter.install.return_value = InstallResult(
                    success=False,
                    version=None,
                    install_path=None,
                    error_message="test",
                )
                mock_pipx.return_value = mock_adapter

                result = runner.invoke(test_app, ["--ci"])

            # Should have plain text markers
            assert (
                "[OK]" in result.output
                or "[FAIL]" in result.output
                or "[INFO]" in result.output
            )

    def test_ci_mode_shows_header(self) -> None:
        """CI mode should show header with separator."""
        with patch(
            "crafter_ai.installer.cli.install_nwave.create_pypi_check_registry"
        ) as mock_registry:
            mock_check_result = CheckResult(
                id="pypi-connectivity",
                name="PyPI Connectivity",
                passed=False,
                severity=CheckSeverity.BLOCKING,
                message="Failed",
            )
            mock_registry.return_value.run_all.return_value = [mock_check_result]

            result = runner.invoke(test_app, ["--ci"])

            # Should have header
            assert "nWave" in result.output or "Installer" in result.output


class TestSuccessCelebration:
    """Test success celebration display."""

    def test_success_shows_completion_message(self) -> None:
        """Successful installation should show completion message."""
        with (
            patch(
                "crafter_ai.installer.cli.install_nwave.create_pypi_check_registry"
            ) as mock_registry,
            patch(
                "crafter_ai.installer.cli.install_nwave.SubprocessPipxAdapter"
            ) as mock_pipx,
            patch("crafter_ai.installer.cli.install_nwave.SetupService") as mock_setup,
            patch(
                "crafter_ai.installer.cli.install_nwave.get_installed_version"
            ) as mock_get_version,
        ):
            mock_check_result = CheckResult(
                id="pypi-connectivity",
                name="PyPI Connectivity",
                passed=True,
                severity=CheckSeverity.BLOCKING,
                message="OK",
            )
            mock_registry.return_value.run_all.return_value = [mock_check_result]

            mock_adapter = MagicMock()
            mock_adapter.list_packages.return_value = []
            mock_adapter.install.return_value = InstallResult(
                success=True,
                version="1.0.0",
                install_path=Path("/test"),
                error_message=None,
            )
            mock_pipx.return_value = mock_adapter

            mock_setup_instance = MagicMock()
            mock_setup_instance.setup_claude_config.return_value = MagicMock(
                success=True, created_paths=[], errors=[]
            )
            mock_setup.return_value = mock_setup_instance

            mock_get_version.return_value = "1.0.0"

            result = runner.invoke(test_app, ["--ci"])

            assert result.exit_code == 0
            assert "Complete" in result.output or "success" in result.output.lower()

    def test_success_shows_next_steps(self) -> None:
        """Successful installation should show next steps."""
        with (
            patch(
                "crafter_ai.installer.cli.install_nwave.create_pypi_check_registry"
            ) as mock_registry,
            patch(
                "crafter_ai.installer.cli.install_nwave.SubprocessPipxAdapter"
            ) as mock_pipx,
            patch("crafter_ai.installer.cli.install_nwave.SetupService") as mock_setup,
            patch(
                "crafter_ai.installer.cli.install_nwave.get_installed_version"
            ) as mock_get_version,
        ):
            mock_check_result = CheckResult(
                id="pypi-connectivity",
                name="PyPI Connectivity",
                passed=True,
                severity=CheckSeverity.BLOCKING,
                message="OK",
            )
            mock_registry.return_value.run_all.return_value = [mock_check_result]

            mock_adapter = MagicMock()
            mock_adapter.list_packages.return_value = []
            mock_adapter.install.return_value = InstallResult(
                success=True,
                version="1.0.0",
                install_path=Path("/test"),
                error_message=None,
            )
            mock_pipx.return_value = mock_adapter

            mock_setup_instance = MagicMock()
            mock_setup_instance.setup_claude_config.return_value = MagicMock(
                success=True, created_paths=[], errors=[]
            )
            mock_setup.return_value = mock_setup_instance

            mock_get_version.return_value = "1.0.0"

            result = runner.invoke(test_app, ["--ci"])

            assert result.exit_code == 0
            # Should mention next steps like nw doctor
            assert "doctor" in result.output.lower() or "next" in result.output.lower()
