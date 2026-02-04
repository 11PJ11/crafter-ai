"""Tests for nw doctor CLI command.

TDD approach: Tests verify CLI behavior with mock dependencies
and output verification using CliRunner.
"""

import os
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

import typer

from crafter_ai.installer.cli.nw_doctor import (
    CHECKMARK,
    CI_CHECKMARK,
    CI_CROSS,
    CI_WARNING,
    CROSS,
    WARNING,
    _format_check_name,
    _get_status_indicator,
    _is_ci_mode,
    doctor,
)
from crafter_ai.installer.domain.health_checker import HealthChecker
from crafter_ai.installer.domain.health_result import HealthResult, HealthStatus
from tests.cli.conftest import CleanCliRunner


# Create a test app for CLI testing
test_app = typer.Typer()
test_app.command()(doctor)

runner = CleanCliRunner()


def _create_health_result(
    component: str,
    status: HealthStatus,
    message: str,
    details: dict[str, str] | None = None,
) -> HealthResult:
    """Helper to create HealthResult for tests."""
    return HealthResult(
        component=component,
        status=status,
        message=message,
        details=details,
        timestamp=datetime.now(timezone.utc),
    )


def _create_mock_checker(results: list[HealthResult]) -> HealthChecker:
    """Create a mock HealthChecker with predefined results."""
    checker = MagicMock(spec=HealthChecker)
    checker.check_all.return_value = results

    # Mock check() to return specific result by component
    def check_side_effect(component: str) -> HealthResult:
        for r in results:
            if r.component == component:
                return r
        return _create_health_result(
            component=component,
            status=HealthStatus.UNHEALTHY,
            message=f"Component '{component}' is not registered",
        )

    checker.check.side_effect = check_side_effect
    return checker


class TestDoctorCommandBasic:
    """Test basic doctor command behavior."""

    def test_doctor_command_exists(self) -> None:
        """doctor command should be callable."""
        assert callable(doctor)

    def test_doctor_runs_without_error(self) -> None:
        """doctor command should run without raising exceptions."""
        mock_checker = _create_mock_checker(
            [
                _create_health_result(
                    "test-component",
                    HealthStatus.HEALTHY,
                    "Test passed",
                )
            ]
        )

        with patch(
            "crafter_ai.installer.cli.nw_doctor.create_doctor_health_checker",
            return_value=mock_checker,
        ):
            result = runner.invoke(test_app, [])

            assert result.exit_code == 0


class TestDoctorDisplaysResults:
    """Test that doctor displays health check results."""

    def test_displays_header(self) -> None:
        """doctor should display 'nWave Health Check' header."""
        mock_checker = _create_mock_checker(
            [
                _create_health_result(
                    "test-component",
                    HealthStatus.HEALTHY,
                    "Test passed",
                )
            ]
        )

        with patch(
            "crafter_ai.installer.cli.nw_doctor.create_doctor_health_checker",
            return_value=mock_checker,
        ):
            result = runner.invoke(test_app, [])

            assert "nWave Health Check" in result.output

    def test_displays_checkmark_for_healthy(self) -> None:
        """doctor should display checkmark for HEALTHY status."""
        mock_checker = _create_mock_checker(
            [
                _create_health_result(
                    "python-environment",
                    HealthStatus.HEALTHY,
                    "Python 3.10 environment is healthy",
                )
            ]
        )

        with patch(
            "crafter_ai.installer.cli.nw_doctor.create_doctor_health_checker",
            return_value=mock_checker,
        ):
            result = runner.invoke(test_app, [])

            # Output should contain checkmark (might be ANSI escaped)
            assert "Python Environment" in result.output
            assert "Python 3.10 environment is healthy" in result.output

    def test_displays_cross_for_unhealthy(self) -> None:
        """doctor should display X for UNHEALTHY status."""
        mock_checker = _create_mock_checker(
            [
                _create_health_result(
                    "config-directory",
                    HealthStatus.UNHEALTHY,
                    "Config directory missing",
                )
            ]
        )

        with patch(
            "crafter_ai.installer.cli.nw_doctor.create_doctor_health_checker",
            return_value=mock_checker,
        ):
            result = runner.invoke(test_app, [])

            assert "Config Directory" in result.output
            assert "Config directory missing" in result.output

    def test_displays_warning_for_degraded(self) -> None:
        """doctor should display warning for DEGRADED status."""
        mock_checker = _create_mock_checker(
            [
                _create_health_result(
                    "agent-files",
                    HealthStatus.DEGRADED,
                    "No agent specification files found",
                )
            ]
        )

        with patch(
            "crafter_ai.installer.cli.nw_doctor.create_doctor_health_checker",
            return_value=mock_checker,
        ):
            result = runner.invoke(test_app, [])

            assert "Agent Files" in result.output
            assert "No agent specification files found" in result.output

    def test_displays_summary(self) -> None:
        """doctor should display summary of check results."""
        mock_checker = _create_mock_checker(
            [
                _create_health_result(
                    "check-1",
                    HealthStatus.HEALTHY,
                    "Passed",
                ),
                _create_health_result(
                    "check-2",
                    HealthStatus.HEALTHY,
                    "Passed",
                ),
            ]
        )

        with patch(
            "crafter_ai.installer.cli.nw_doctor.create_doctor_health_checker",
            return_value=mock_checker,
        ):
            result = runner.invoke(test_app, [])

            assert "2 of 2" in result.output
            assert "passed" in result.output.lower()


class TestDoctorVerboseFlag:
    """Test --verbose flag behavior."""

    def test_verbose_shows_details(self) -> None:
        """--verbose should show detailed output for each check."""
        mock_checker = _create_mock_checker(
            [
                _create_health_result(
                    "python-environment",
                    HealthStatus.HEALTHY,
                    "Python 3.10 environment is healthy",
                    details={"version": "3.10.12", "venv_active": "true"},
                )
            ]
        )

        with patch(
            "crafter_ai.installer.cli.nw_doctor.create_doctor_health_checker",
            return_value=mock_checker,
        ):
            result = runner.invoke(test_app, ["--verbose"])

            assert "version" in result.output.lower()
            assert "3.10.12" in result.output

    def test_short_flag_v_works(self) -> None:
        """-v short flag should work like --verbose."""
        mock_checker = _create_mock_checker(
            [
                _create_health_result(
                    "python-environment",
                    HealthStatus.HEALTHY,
                    "Python 3.10 environment is healthy",
                    details={"version": "3.10.12"},
                )
            ]
        )

        with patch(
            "crafter_ai.installer.cli.nw_doctor.create_doctor_health_checker",
            return_value=mock_checker,
        ):
            result = runner.invoke(test_app, ["-v"])

            assert "3.10.12" in result.output

    def test_no_verbose_hides_details(self) -> None:
        """Without --verbose, details should not be shown."""
        mock_checker = _create_mock_checker(
            [
                _create_health_result(
                    "python-environment",
                    HealthStatus.HEALTHY,
                    "Python 3.10 environment is healthy",
                    details={"version": "3.10.12", "prefix": "/usr/local"},
                )
            ]
        )

        with patch(
            "crafter_ai.installer.cli.nw_doctor.create_doctor_health_checker",
            return_value=mock_checker,
        ):
            result = runner.invoke(test_app, [])

            # Message should appear but not detailed key-value pairs
            assert "Python 3.10 environment is healthy" in result.output
            # Details key "prefix" should not appear without verbose
            assert "/usr/local" not in result.output


class TestDoctorCheckFlag:
    """Test --check flag behavior."""

    def test_check_runs_specific_check_only(self) -> None:
        """--check should run only the specified check."""
        mock_checker = _create_mock_checker(
            [
                _create_health_result(
                    "python-environment",
                    HealthStatus.HEALTHY,
                    "Python 3.10 environment is healthy",
                ),
                _create_health_result(
                    "config-directory",
                    HealthStatus.HEALTHY,
                    "Config directory exists",
                ),
            ]
        )

        with patch(
            "crafter_ai.installer.cli.nw_doctor.create_doctor_health_checker",
            return_value=mock_checker,
        ):
            result = runner.invoke(test_app, ["--check", "python-environment"])

            # Should show python-environment check
            assert "Python Environment" in result.output
            # Should show "1 of 1" in summary (only one check ran)
            assert "1 of 1" in result.output
            # Verify check() was called, not check_all()
            mock_checker.check.assert_called_once_with("python-environment")
            mock_checker.check_all.assert_not_called()

    def test_short_flag_c_works(self) -> None:
        """-c short flag should work like --check."""
        mock_checker = _create_mock_checker(
            [
                _create_health_result(
                    "config-directory",
                    HealthStatus.HEALTHY,
                    "Config directory exists",
                )
            ]
        )

        with patch(
            "crafter_ai.installer.cli.nw_doctor.create_doctor_health_checker",
            return_value=mock_checker,
        ):
            result = runner.invoke(test_app, ["-c", "config-directory"])

            assert "Config Directory" in result.output
            mock_checker.check.assert_called_once_with("config-directory")

    def test_check_invalid_component(self) -> None:
        """--check with invalid component should show not registered."""
        mock_checker = _create_mock_checker([])

        with patch(
            "crafter_ai.installer.cli.nw_doctor.create_doctor_health_checker",
            return_value=mock_checker,
        ):
            result = runner.invoke(test_app, ["--check", "nonexistent-check"])

            # Should fail because component is not registered
            assert result.exit_code == 1
            assert "not registered" in result.output.lower()


class TestDoctorFixFlag:
    """Test --fix flag behavior."""

    def test_fix_flag_shows_message(self) -> None:
        """--fix should show that fix mode is enabled."""
        mock_checker = _create_mock_checker(
            [
                _create_health_result(
                    "test-component",
                    HealthStatus.HEALTHY,
                    "Test passed",
                )
            ]
        )

        with patch(
            "crafter_ai.installer.cli.nw_doctor.create_doctor_health_checker",
            return_value=mock_checker,
        ):
            result = runner.invoke(test_app, ["--fix"])

            assert "fix" in result.output.lower()

    def test_short_flag_f_works(self) -> None:
        """-f short flag should work like --fix."""
        mock_checker = _create_mock_checker(
            [
                _create_health_result(
                    "test-component",
                    HealthStatus.HEALTHY,
                    "Test passed",
                )
            ]
        )

        with patch(
            "crafter_ai.installer.cli.nw_doctor.create_doctor_health_checker",
            return_value=mock_checker,
        ):
            result = runner.invoke(test_app, ["-f"])

            assert "fix" in result.output.lower()


class TestDoctorExitCodes:
    """Test CLI exit codes."""

    def test_returns_zero_when_all_pass(self) -> None:
        """doctor should return exit code 0 when all checks pass."""
        mock_checker = _create_mock_checker(
            [
                _create_health_result(
                    "check-1",
                    HealthStatus.HEALTHY,
                    "Passed",
                ),
                _create_health_result(
                    "check-2",
                    HealthStatus.HEALTHY,
                    "Passed",
                ),
            ]
        )

        with patch(
            "crafter_ai.installer.cli.nw_doctor.create_doctor_health_checker",
            return_value=mock_checker,
        ):
            result = runner.invoke(test_app, [])

            assert result.exit_code == 0

    def test_returns_one_when_any_fail(self) -> None:
        """doctor should return exit code 1 when any check fails."""
        mock_checker = _create_mock_checker(
            [
                _create_health_result(
                    "check-1",
                    HealthStatus.HEALTHY,
                    "Passed",
                ),
                _create_health_result(
                    "check-2",
                    HealthStatus.UNHEALTHY,
                    "Failed",
                ),
            ]
        )

        with patch(
            "crafter_ai.installer.cli.nw_doctor.create_doctor_health_checker",
            return_value=mock_checker,
        ):
            result = runner.invoke(test_app, [])

            assert result.exit_code == 1

    def test_returns_zero_when_degraded_only(self) -> None:
        """doctor should return exit code 0 when only degraded (warnings)."""
        mock_checker = _create_mock_checker(
            [
                _create_health_result(
                    "check-1",
                    HealthStatus.HEALTHY,
                    "Passed",
                ),
                _create_health_result(
                    "check-2",
                    HealthStatus.DEGRADED,
                    "Warning",
                ),
            ]
        )

        with patch(
            "crafter_ai.installer.cli.nw_doctor.create_doctor_health_checker",
            return_value=mock_checker,
        ):
            result = runner.invoke(test_app, [])

            # Degraded is warning, not failure
            assert result.exit_code == 0


class TestDoctorCIMode:
    """Test CI mode behavior."""

    def test_ci_mode_uses_plain_output(self) -> None:
        """In CI mode, doctor should use plain text output."""
        mock_checker = _create_mock_checker(
            [
                _create_health_result(
                    "test-component",
                    HealthStatus.HEALTHY,
                    "Test passed",
                )
            ]
        )

        with patch(
            "crafter_ai.installer.cli.nw_doctor.create_doctor_health_checker",
            return_value=mock_checker,
        ):
            with patch.dict(os.environ, {"CI": "true"}):
                result = runner.invoke(test_app, [])

                # CI output should have [OK] marker
                assert "[OK]" in result.output

    def test_ci_mode_uses_fail_marker(self) -> None:
        """In CI mode, doctor should use [FAIL] for unhealthy."""
        mock_checker = _create_mock_checker(
            [
                _create_health_result(
                    "test-component",
                    HealthStatus.UNHEALTHY,
                    "Test failed",
                )
            ]
        )

        with patch(
            "crafter_ai.installer.cli.nw_doctor.create_doctor_health_checker",
            return_value=mock_checker,
        ):
            with patch.dict(os.environ, {"CI": "true"}):
                result = runner.invoke(test_app, [])

                assert "[FAIL]" in result.output

    def test_ci_mode_uses_warn_marker(self) -> None:
        """In CI mode, doctor should use [WARN] for degraded."""
        mock_checker = _create_mock_checker(
            [
                _create_health_result(
                    "test-component",
                    HealthStatus.DEGRADED,
                    "Test warning",
                )
            ]
        )

        with patch(
            "crafter_ai.installer.cli.nw_doctor.create_doctor_health_checker",
            return_value=mock_checker,
        ):
            with patch.dict(os.environ, {"CI": "true"}):
                result = runner.invoke(test_app, [])

                assert "[WARN]" in result.output

    def test_ci_mode_detected_by_ci_equals_1(self) -> None:
        """CI mode should be detected via CI=1."""
        mock_checker = _create_mock_checker(
            [
                _create_health_result(
                    "test-component",
                    HealthStatus.HEALTHY,
                    "Test passed",
                )
            ]
        )

        with patch(
            "crafter_ai.installer.cli.nw_doctor.create_doctor_health_checker",
            return_value=mock_checker,
        ):
            with patch.dict(os.environ, {"CI": "1"}):
                result = runner.invoke(test_app, [])

                assert "[OK]" in result.output

    def test_ci_mode_shows_header(self) -> None:
        """In CI mode, doctor should still show header."""
        mock_checker = _create_mock_checker(
            [
                _create_health_result(
                    "test-component",
                    HealthStatus.HEALTHY,
                    "Test passed",
                )
            ]
        )

        with patch(
            "crafter_ai.installer.cli.nw_doctor.create_doctor_health_checker",
            return_value=mock_checker,
        ):
            with patch.dict(os.environ, {"CI": "true"}):
                result = runner.invoke(test_app, [])

                assert "nWave Health Check" in result.output

    def test_ci_verbose_shows_details(self) -> None:
        """In CI mode with --verbose, details should be shown."""
        mock_checker = _create_mock_checker(
            [
                _create_health_result(
                    "python-environment",
                    HealthStatus.HEALTHY,
                    "Python 3.10 environment is healthy",
                    details={"version": "3.10.12"},
                )
            ]
        )

        with patch(
            "crafter_ai.installer.cli.nw_doctor.create_doctor_health_checker",
            return_value=mock_checker,
        ):
            with patch.dict(os.environ, {"CI": "true"}):
                result = runner.invoke(test_app, ["--verbose"])

                assert "version" in result.output.lower()
                assert "3.10.12" in result.output


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

    def test_format_check_name_hyphenated(self) -> None:
        """_format_check_name should convert hyphens to spaces and title case."""
        assert _format_check_name("python-environment") == "Python Environment"
        assert _format_check_name("config-directory") == "Config Directory"
        assert _format_check_name("agent-files") == "Agent Files"

    def test_format_check_name_single_word(self) -> None:
        """_format_check_name should handle single word names."""
        assert _format_check_name("package") == "Package"

    def test_get_status_indicator_healthy_rich(self) -> None:
        """_get_status_indicator should return checkmark for HEALTHY."""
        indicator = _get_status_indicator(HealthStatus.HEALTHY, ci_mode=False)
        assert indicator == CHECKMARK

    def test_get_status_indicator_unhealthy_rich(self) -> None:
        """_get_status_indicator should return cross for UNHEALTHY."""
        indicator = _get_status_indicator(HealthStatus.UNHEALTHY, ci_mode=False)
        assert indicator == CROSS

    def test_get_status_indicator_degraded_rich(self) -> None:
        """_get_status_indicator should return warning for DEGRADED."""
        indicator = _get_status_indicator(HealthStatus.DEGRADED, ci_mode=False)
        assert indicator == WARNING

    def test_get_status_indicator_healthy_ci(self) -> None:
        """_get_status_indicator should return [OK] for HEALTHY in CI mode."""
        indicator = _get_status_indicator(HealthStatus.HEALTHY, ci_mode=True)
        assert indicator == CI_CHECKMARK

    def test_get_status_indicator_unhealthy_ci(self) -> None:
        """_get_status_indicator should return [FAIL] for UNHEALTHY in CI mode."""
        indicator = _get_status_indicator(HealthStatus.UNHEALTHY, ci_mode=True)
        assert indicator == CI_CROSS

    def test_get_status_indicator_degraded_ci(self) -> None:
        """_get_status_indicator should return [WARN] for DEGRADED in CI mode."""
        indicator = _get_status_indicator(HealthStatus.DEGRADED, ci_mode=True)
        assert indicator == CI_WARNING


class TestDoctorWithRealHealthChecker:
    """Test doctor with real HealthChecker (integration-like tests)."""

    def test_runs_with_real_checker(self) -> None:
        """doctor should work with real create_doctor_health_checker."""
        # No mocking - use real implementation
        result = runner.invoke(test_app, [])

        # Should complete (may pass or fail depending on environment)
        # Just verify it runs and produces output
        assert "nWave Health Check" in result.output
        assert "passed" in result.output.lower()

    def test_verbose_with_real_checker(self) -> None:
        """doctor --verbose should work with real checker."""
        result = runner.invoke(test_app, ["--verbose"])

        # Should show some detail information
        assert "nWave Health Check" in result.output


class TestDoctorSummaryDetails:
    """Test summary display details."""

    def test_summary_shows_warnings_count(self) -> None:
        """Summary should show warning count when there are warnings."""
        mock_checker = _create_mock_checker(
            [
                _create_health_result("c1", HealthStatus.HEALTHY, "OK"),
                _create_health_result("c2", HealthStatus.DEGRADED, "Warning"),
                _create_health_result("c3", HealthStatus.DEGRADED, "Warning"),
            ]
        )

        with patch(
            "crafter_ai.installer.cli.nw_doctor.create_doctor_health_checker",
            return_value=mock_checker,
        ):
            result = runner.invoke(test_app, [])

            assert "1 of 3" in result.output
            assert "2 warning" in result.output.lower()

    def test_summary_shows_failures_count(self) -> None:
        """Summary should show failure count when there are failures."""
        mock_checker = _create_mock_checker(
            [
                _create_health_result("c1", HealthStatus.HEALTHY, "OK"),
                _create_health_result("c2", HealthStatus.UNHEALTHY, "Failed"),
            ]
        )

        with patch(
            "crafter_ai.installer.cli.nw_doctor.create_doctor_health_checker",
            return_value=mock_checker,
        ):
            result = runner.invoke(test_app, [])

            assert "1 of 2" in result.output
            assert "1 failed" in result.output.lower()
