"""Tests for AutoRepairService.

This module tests the auto-repair functionality for fixable check failures.
Tests cover interactive prompts, command execution, and CI mode behavior.
"""

import os
import subprocess
from unittest.mock import MagicMock, patch

import pytest

from crafter_ai.installer.domain.check_result import CheckResult, CheckSeverity
from crafter_ai.installer.services.auto_repair_service import (
    AutoRepairService,
    RepairResult,
)


class TestRepairResult:
    """Tests for RepairResult dataclass."""

    def test_repair_result_is_frozen(self) -> None:
        """RepairResult should be immutable."""
        result = RepairResult(
            success=True,
            message="Installed successfully",
            command_output="Successfully installed build-1.0.0",
        )

        with pytest.raises(AttributeError):
            result.success = False  # type: ignore[misc]

    def test_repair_result_success(self) -> None:
        """RepairResult should store success state and message."""
        result = RepairResult(
            success=True,
            message="Installed build package",
            command_output="Successfully installed build-1.0.0",
        )

        assert result.success is True
        assert result.message == "Installed build package"
        assert result.command_output == "Successfully installed build-1.0.0"

    def test_repair_result_failure(self) -> None:
        """RepairResult should store failure state and message."""
        result = RepairResult(
            success=False,
            message="Installation failed",
            command_output="ERROR: Could not find package",
        )

        assert result.success is False
        assert result.message == "Installation failed"
        assert result.command_output == "ERROR: Could not find package"


class TestCanRepair:
    """Tests for AutoRepairService.can_repair method."""

    def test_can_repair_returns_true_for_fixable_check(self) -> None:
        """can_repair should return True for fixable checks with fix_command."""
        service = AutoRepairService()
        check_result = CheckResult(
            id="build-package",
            name="Build Package Installed",
            passed=False,
            severity=CheckSeverity.BLOCKING,
            message="Build package is not installed",
            fixable=True,
            fix_command="pip install build",
        )

        assert service.can_repair(check_result) is True

    def test_can_repair_returns_false_for_non_fixable_check(self) -> None:
        """can_repair should return False for non-fixable checks."""
        service = AutoRepairService()
        check_result = CheckResult(
            id="pyproject-exists",
            name="Pyproject.toml Exists",
            passed=False,
            severity=CheckSeverity.BLOCKING,
            message="pyproject.toml not found",
            fixable=False,
        )

        assert service.can_repair(check_result) is False

    def test_can_repair_returns_false_for_fixable_without_command(self) -> None:
        """can_repair should return False when fixable but no fix_command."""
        service = AutoRepairService()
        check_result = CheckResult(
            id="some-check",
            name="Some Check",
            passed=False,
            severity=CheckSeverity.BLOCKING,
            message="Check failed",
            fixable=True,
            fix_command=None,
        )

        assert service.can_repair(check_result) is False

    def test_can_repair_returns_false_for_passed_check(self) -> None:
        """can_repair should return False for checks that passed."""
        service = AutoRepairService()
        check_result = CheckResult(
            id="build-package",
            name="Build Package Installed",
            passed=True,
            severity=CheckSeverity.BLOCKING,
            message="Build package found",
            fixable=True,
            fix_command="pip install build",
        )

        assert service.can_repair(check_result) is False


class TestRepairWithPrompt:
    """Tests for AutoRepairService.repair method with interactive prompts."""

    @pytest.fixture(autouse=True)
    def disable_ci_mode(self):
        """Disable CI mode for tests that verify interactive prompt behavior.

        GitHub Actions sets CI=true, which causes the service to auto-accept
        repairs without prompting. This fixture ensures tests that verify
        prompt behavior work in both local and CI environments.
        """
        with patch.dict(os.environ, {"CI": "false"}):
            yield

    def test_repair_prompts_user_and_runs_command_on_yes(self) -> None:
        """repair should prompt user and run fix_command when user says Y."""
        service = AutoRepairService()
        console = MagicMock()
        console.input.return_value = "Y"

        check_result = CheckResult(
            id="build-package",
            name="Build Package Installed",
            passed=False,
            severity=CheckSeverity.BLOCKING,
            message="Build package is not installed",
            fixable=True,
            fix_command="pip install build",
        )

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(
                returncode=0,
                stdout="Successfully installed build-1.0.0",
                stderr="",
            )

            result = service.repair(check_result, console)

            console.input.assert_called_once()
            assert "Install it now?" in console.input.call_args[0][0]
            mock_run.assert_called_once()
            assert result.success is True

    def test_repair_returns_declined_on_no(self) -> None:
        """repair should return declined result when user says n."""
        service = AutoRepairService()
        console = MagicMock()
        console.input.return_value = "n"

        check_result = CheckResult(
            id="build-package",
            name="Build Package Installed",
            passed=False,
            severity=CheckSeverity.BLOCKING,
            message="Build package is not installed",
            fixable=True,
            fix_command="pip install build",
        )

        with patch("subprocess.run") as mock_run:
            result = service.repair(check_result, console)

            mock_run.assert_not_called()
            assert result.success is False
            assert "declined" in result.message.lower()

    def test_repair_shows_spinner_during_execution(self) -> None:
        """repair should show spinner during command execution."""
        service = AutoRepairService()
        console = MagicMock()
        console.input.return_value = "Y"
        mock_status = MagicMock()
        console.status.return_value.__enter__ = MagicMock(return_value=mock_status)
        console.status.return_value.__exit__ = MagicMock(return_value=None)

        check_result = CheckResult(
            id="build-package",
            name="Build Package Installed",
            passed=False,
            severity=CheckSeverity.BLOCKING,
            message="Build package is not installed",
            fixable=True,
            fix_command="pip install build",
        )

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(
                returncode=0,
                stdout="Successfully installed build-1.0.0",
                stderr="",
            )

            service.repair(check_result, console)

            console.status.assert_called_once()
            assert "Installing" in console.status.call_args[0][0]


class TestRepairCommandExecution:
    """Tests for repair command execution behavior."""

    @pytest.fixture(autouse=True)
    def disable_ci_mode(self):
        """Disable CI mode for tests that verify interactive prompt behavior."""
        with patch.dict(os.environ, {"CI": "false"}):
            yield

    def test_repair_returns_success_with_output_on_success(self) -> None:
        """repair should return success with command output on successful execution."""
        service = AutoRepairService()
        console = MagicMock()
        console.input.return_value = "Y"
        console.status.return_value.__enter__ = MagicMock()
        console.status.return_value.__exit__ = MagicMock(return_value=None)

        check_result = CheckResult(
            id="build-package",
            name="Build Package Installed",
            passed=False,
            severity=CheckSeverity.BLOCKING,
            message="Build package is not installed",
            fixable=True,
            fix_command="pip install build",
        )

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(
                returncode=0,
                stdout="Successfully installed build-1.0.0\n",
                stderr="",
            )

            result = service.repair(check_result, console)

            assert result.success is True
            assert "build-1.0.0" in result.command_output

    def test_repair_returns_failure_on_command_error(self) -> None:
        """repair should return failure with error on command failure."""
        service = AutoRepairService()
        console = MagicMock()
        console.input.return_value = "Y"
        console.status.return_value.__enter__ = MagicMock()
        console.status.return_value.__exit__ = MagicMock(return_value=None)

        check_result = CheckResult(
            id="build-package",
            name="Build Package Installed",
            passed=False,
            severity=CheckSeverity.BLOCKING,
            message="Build package is not installed",
            fixable=True,
            fix_command="pip install nonexistent-package",
        )

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(
                returncode=1,
                stdout="",
                stderr="ERROR: Could not find a version that satisfies the requirement",
            )

            result = service.repair(check_result, console)

            assert result.success is False
            assert "Could not find" in result.command_output

    def test_repair_handles_subprocess_exception(self) -> None:
        """repair should handle subprocess exceptions gracefully."""
        service = AutoRepairService()
        console = MagicMock()
        console.input.return_value = "Y"
        console.status.return_value.__enter__ = MagicMock()
        console.status.return_value.__exit__ = MagicMock(return_value=None)

        check_result = CheckResult(
            id="build-package",
            name="Build Package Installed",
            passed=False,
            severity=CheckSeverity.BLOCKING,
            message="Build package is not installed",
            fixable=True,
            fix_command="pip install build",
        )

        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = subprocess.SubprocessError("Command failed")

            result = service.repair(check_result, console)

            assert result.success is False
            assert "failed" in result.message.lower()


class TestCIMode:
    """Tests for CI mode (auto-accept without prompting)."""

    def test_ci_mode_auto_accepts_without_prompting(self) -> None:
        """In CI mode (CI=true), repair should auto-accept without prompting."""
        service = AutoRepairService()
        console = MagicMock()

        check_result = CheckResult(
            id="build-package",
            name="Build Package Installed",
            passed=False,
            severity=CheckSeverity.BLOCKING,
            message="Build package is not installed",
            fixable=True,
            fix_command="pip install build",
        )

        with (
            patch.dict("os.environ", {"CI": "true"}),
            patch("subprocess.run") as mock_run,
        ):
            mock_run.return_value = MagicMock(
                returncode=0,
                stdout="Successfully installed build-1.0.0",
                stderr="",
            )
            console.status.return_value.__enter__ = MagicMock()
            console.status.return_value.__exit__ = MagicMock(return_value=None)

            result = service.repair(check_result, console)

            # In CI mode, should NOT prompt the user
            console.input.assert_not_called()
            # But should still run the command
            mock_run.assert_called_once()
            assert result.success is True

    def test_non_ci_mode_prompts_user(self) -> None:
        """Outside CI mode, repair should prompt the user."""
        service = AutoRepairService()
        console = MagicMock()
        console.input.return_value = "Y"
        console.status.return_value.__enter__ = MagicMock()
        console.status.return_value.__exit__ = MagicMock(return_value=None)

        check_result = CheckResult(
            id="build-package",
            name="Build Package Installed",
            passed=False,
            severity=CheckSeverity.BLOCKING,
            message="Build package is not installed",
            fixable=True,
            fix_command="pip install build",
        )

        with (
            patch.dict("os.environ", {"CI": ""}, clear=False),
            patch("subprocess.run") as mock_run,
        ):
            mock_run.return_value = MagicMock(
                returncode=0,
                stdout="Successfully installed build-1.0.0",
                stderr="",
            )

            service.repair(check_result, console)

            # Outside CI mode, should prompt the user
            console.input.assert_called_once()


class TestRepairForNonRepairableChecks:
    """Tests for repair with non-repairable checks."""

    def test_repair_returns_failure_for_non_repairable_check(self) -> None:
        """repair should return failure for checks that cannot be repaired."""
        service = AutoRepairService()
        console = MagicMock()

        check_result = CheckResult(
            id="pyproject-exists",
            name="Pyproject.toml Exists",
            passed=False,
            severity=CheckSeverity.BLOCKING,
            message="pyproject.toml not found",
            fixable=False,
        )

        result = service.repair(check_result, console)

        assert result.success is False
        assert "cannot be auto-repaired" in result.message.lower()
        console.input.assert_not_called()
