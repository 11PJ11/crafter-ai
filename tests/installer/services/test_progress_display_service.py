"""Tests for ProgressDisplayService.

Tests verify:
- InstallProgress dataclass creation and defaults
- Phase start display with Rich Panel
- Step display with spinner/checkmark/X based on status
- Phase completion display with success/failure summary
- Overall progress bar display
- CI mode detection and simple text output
- Mock Rich console for all display tests
"""

import os
from io import StringIO
from unittest.mock import MagicMock, patch

import pytest

from crafter_ai.installer.services.progress_display_service import (
    InstallProgress,
    ProgressDisplayService,
    ProgressStatus,
)


class TestInstallProgress:
    """Tests for InstallProgress dataclass."""

    def test_install_progress_has_all_required_fields(self) -> None:
        """InstallProgress should have all required fields."""
        progress = InstallProgress(
            phase="Pre-flight Checks",
            step=1,
            total_steps=5,
            message="Checking Python version",
            status=ProgressStatus.RUNNING,
        )

        assert progress.phase == "Pre-flight Checks"
        assert progress.step == 1
        assert progress.total_steps == 5
        assert progress.message == "Checking Python version"
        assert progress.status == ProgressStatus.RUNNING

    def test_install_progress_status_pending(self) -> None:
        """InstallProgress should support PENDING status."""
        progress = InstallProgress(
            phase="Installation",
            step=2,
            total_steps=3,
            message="Waiting to start",
            status=ProgressStatus.PENDING,
        )

        assert progress.status == ProgressStatus.PENDING

    def test_install_progress_status_complete(self) -> None:
        """InstallProgress should support COMPLETE status."""
        progress = InstallProgress(
            phase="Verification",
            step=3,
            total_steps=3,
            message="Health check passed",
            status=ProgressStatus.COMPLETE,
        )

        assert progress.status == ProgressStatus.COMPLETE

    def test_install_progress_status_failed(self) -> None:
        """InstallProgress should support FAILED status."""
        progress = InstallProgress(
            phase="Backup",
            step=1,
            total_steps=2,
            message="Backup failed: permission denied",
            status=ProgressStatus.FAILED,
        )

        assert progress.status == ProgressStatus.FAILED

    def test_install_progress_is_immutable(self) -> None:
        """InstallProgress should be immutable (frozen)."""
        progress = InstallProgress(
            phase="Test",
            step=1,
            total_steps=1,
            message="Test message",
            status=ProgressStatus.PENDING,
        )

        with pytest.raises(AttributeError):
            progress.phase = "Modified"  # type: ignore[misc]


class TestProgressStatus:
    """Tests for ProgressStatus enum."""

    def test_progress_status_has_all_values(self) -> None:
        """ProgressStatus should have pending, running, complete, failed values."""
        assert ProgressStatus.PENDING.value == "pending"
        assert ProgressStatus.RUNNING.value == "running"
        assert ProgressStatus.COMPLETE.value == "complete"
        assert ProgressStatus.FAILED.value == "failed"


class TestProgressDisplayServiceCIDetection:
    """Tests for CI mode detection."""

    def test_is_ci_mode_returns_true_when_ci_env_is_true(self) -> None:
        """is_ci_mode() should return True when CI=true."""
        with patch.dict(os.environ, {"CI": "true"}):
            service = ProgressDisplayService()
            assert service.is_ci_mode() is True

    def test_is_ci_mode_returns_true_when_ci_env_is_1(self) -> None:
        """is_ci_mode() should return True when CI=1."""
        with patch.dict(os.environ, {"CI": "1"}):
            service = ProgressDisplayService()
            assert service.is_ci_mode() is True

    def test_is_ci_mode_returns_false_when_ci_env_not_set(self) -> None:
        """is_ci_mode() should return False when CI env var is not set."""
        with patch.dict(os.environ, {}, clear=True):
            # Remove CI if it exists
            env_copy = os.environ.copy()
            env_copy.pop("CI", None)
            with patch.dict(os.environ, env_copy, clear=True):
                service = ProgressDisplayService()
                assert service.is_ci_mode() is False

    def test_is_ci_mode_returns_false_when_ci_env_is_false(self) -> None:
        """is_ci_mode() should return False when CI=false."""
        with patch.dict(os.environ, {"CI": "false"}):
            service = ProgressDisplayService()
            assert service.is_ci_mode() is False


class TestProgressDisplayServiceDisplayPhaseStart:
    """Tests for display_phase_start() method."""

    @pytest.fixture
    def mock_console(self) -> MagicMock:
        """Create a mock Rich console."""
        return MagicMock()

    @pytest.fixture
    def service_with_mock_console(
        self, mock_console: MagicMock
    ) -> ProgressDisplayService:
        """Create service with mock console."""
        service = ProgressDisplayService(console=mock_console)
        return service

    def test_display_phase_start_calls_console_print(
        self, service_with_mock_console: ProgressDisplayService, mock_console: MagicMock
    ) -> None:
        """display_phase_start() should call console.print()."""
        service_with_mock_console.display_phase_start("Pre-flight Checks")

        mock_console.print.assert_called()

    def test_display_phase_start_uses_panel_for_header(
        self, service_with_mock_console: ProgressDisplayService, mock_console: MagicMock
    ) -> None:
        """display_phase_start() should use Rich Panel for phase header."""
        with patch(
            "crafter_ai.installer.services.progress_display_service.Panel"
        ) as mock_panel:
            service_with_mock_console.display_phase_start("Installation")

            mock_panel.assert_called()
            # Verify phase name is in the Panel
            call_args = mock_panel.call_args
            assert "Installation" in str(call_args)

    def test_display_phase_start_ci_mode_uses_simple_text(self) -> None:
        """display_phase_start() should use simple text in CI mode."""
        output = StringIO()
        with patch.dict(os.environ, {"CI": "true"}):
            service = ProgressDisplayService(file=output)
            service.display_phase_start("Pre-flight Checks")

        output_text = output.getvalue()
        assert "Pre-flight Checks" in output_text
        # CI mode uses simple text, not Rich formatting
        assert "[" not in output_text or "==" in output_text


class TestProgressDisplayServiceDisplayStep:
    """Tests for display_step() method."""

    @pytest.fixture
    def mock_console(self) -> MagicMock:
        """Create a mock Rich console."""
        return MagicMock()

    @pytest.fixture
    def service_with_mock_console(
        self, mock_console: MagicMock
    ) -> ProgressDisplayService:
        """Create service with mock console."""
        return ProgressDisplayService(console=mock_console)

    def test_display_step_running_shows_spinner(
        self, service_with_mock_console: ProgressDisplayService, mock_console: MagicMock
    ) -> None:
        """display_step() should show spinner for RUNNING status."""
        progress = InstallProgress(
            phase="Installation",
            step=1,
            total_steps=3,
            message="Installing package",
            status=ProgressStatus.RUNNING,
        )

        with patch(
            "crafter_ai.installer.services.progress_display_service.Status"
        ) as mock_status:
            mock_status_instance = MagicMock()
            mock_status.return_value.__enter__ = MagicMock(
                return_value=mock_status_instance
            )
            mock_status.return_value.__exit__ = MagicMock(return_value=False)

            service_with_mock_console.display_step(progress)

            mock_status.assert_called()

    def test_display_step_complete_shows_checkmark(
        self, service_with_mock_console: ProgressDisplayService, mock_console: MagicMock
    ) -> None:
        """display_step() should show checkmark for COMPLETE status."""
        progress = InstallProgress(
            phase="Installation",
            step=1,
            total_steps=3,
            message="Package installed",
            status=ProgressStatus.COMPLETE,
        )

        service_with_mock_console.display_step(progress)

        # Check that print was called with a checkmark
        call_args_list = mock_console.print.call_args_list
        output_texts = [str(call) for call in call_args_list]
        output_combined = " ".join(output_texts)
        assert "✓" in output_combined or "green" in output_combined.lower()

    def test_display_step_failed_shows_x(
        self, service_with_mock_console: ProgressDisplayService, mock_console: MagicMock
    ) -> None:
        """display_step() should show X for FAILED status."""
        progress = InstallProgress(
            phase="Installation",
            step=1,
            total_steps=3,
            message="Installation failed",
            status=ProgressStatus.FAILED,
        )

        service_with_mock_console.display_step(progress)

        # Check that print was called with an X
        call_args_list = mock_console.print.call_args_list
        output_texts = [str(call) for call in call_args_list]
        output_combined = " ".join(output_texts)
        assert "✗" in output_combined or "red" in output_combined.lower()

    def test_display_step_pending_shows_pending_indicator(
        self, service_with_mock_console: ProgressDisplayService, mock_console: MagicMock
    ) -> None:
        """display_step() should show pending indicator for PENDING status."""
        progress = InstallProgress(
            phase="Installation",
            step=2,
            total_steps=3,
            message="Waiting",
            status=ProgressStatus.PENDING,
        )

        service_with_mock_console.display_step(progress)

        mock_console.print.assert_called()

    def test_display_step_shows_step_number(
        self, service_with_mock_console: ProgressDisplayService, mock_console: MagicMock
    ) -> None:
        """display_step() should show step number."""
        progress = InstallProgress(
            phase="Verification",
            step=2,
            total_steps=5,
            message="Running health check",
            status=ProgressStatus.COMPLETE,
        )

        service_with_mock_console.display_step(progress)

        call_args_list = mock_console.print.call_args_list
        output_texts = [str(call) for call in call_args_list]
        output_combined = " ".join(output_texts)
        assert "2" in output_combined or "[2/5]" in output_combined

    def test_display_step_shows_message(
        self, service_with_mock_console: ProgressDisplayService, mock_console: MagicMock
    ) -> None:
        """display_step() should show step message."""
        progress = InstallProgress(
            phase="Backup",
            step=1,
            total_steps=2,
            message="Creating backup archive",
            status=ProgressStatus.COMPLETE,
        )

        service_with_mock_console.display_step(progress)

        call_args_list = mock_console.print.call_args_list
        output_texts = [str(call) for call in call_args_list]
        output_combined = " ".join(output_texts)
        assert "Creating backup archive" in output_combined

    def test_display_step_ci_mode_uses_simple_text(self) -> None:
        """display_step() should use simple text in CI mode."""
        output = StringIO()
        with patch.dict(os.environ, {"CI": "true"}):
            service = ProgressDisplayService(file=output)
            progress = InstallProgress(
                phase="Test",
                step=1,
                total_steps=2,
                message="Test step",
                status=ProgressStatus.COMPLETE,
            )
            service.display_step(progress)

        output_text = output.getvalue()
        assert "Test step" in output_text


class TestProgressDisplayServiceDisplayPhaseComplete:
    """Tests for display_phase_complete() method."""

    @pytest.fixture
    def mock_console(self) -> MagicMock:
        """Create a mock Rich console."""
        return MagicMock()

    @pytest.fixture
    def service_with_mock_console(
        self, mock_console: MagicMock
    ) -> ProgressDisplayService:
        """Create service with mock console."""
        return ProgressDisplayService(console=mock_console)

    def test_display_phase_complete_success_shows_success_message(
        self, service_with_mock_console: ProgressDisplayService, mock_console: MagicMock
    ) -> None:
        """display_phase_complete() should show success message when success=True."""
        service_with_mock_console.display_phase_complete("Installation", success=True)

        call_args_list = mock_console.print.call_args_list
        output_texts = [str(call) for call in call_args_list]
        output_combined = " ".join(output_texts)
        assert "Installation" in output_combined
        assert "✓" in output_combined or "complete" in output_combined.lower()

    def test_display_phase_complete_failure_shows_failure_message(
        self, service_with_mock_console: ProgressDisplayService, mock_console: MagicMock
    ) -> None:
        """display_phase_complete() should show failure message when success=False."""
        service_with_mock_console.display_phase_complete(
            "Pre-flight Checks", success=False
        )

        call_args_list = mock_console.print.call_args_list
        output_texts = [str(call) for call in call_args_list]
        output_combined = " ".join(output_texts)
        assert "Pre-flight Checks" in output_combined
        assert "✗" in output_combined or "failed" in output_combined.lower()

    def test_display_phase_complete_success_uses_green(
        self, service_with_mock_console: ProgressDisplayService, mock_console: MagicMock
    ) -> None:
        """display_phase_complete() should use green for success."""
        service_with_mock_console.display_phase_complete("Verification", success=True)

        call_args_list = mock_console.print.call_args_list
        output_texts = [str(call) for call in call_args_list]
        output_combined = " ".join(output_texts)
        assert "green" in output_combined.lower() or "✓" in output_combined

    def test_display_phase_complete_failure_uses_red(
        self, service_with_mock_console: ProgressDisplayService, mock_console: MagicMock
    ) -> None:
        """display_phase_complete() should use red for failure."""
        service_with_mock_console.display_phase_complete("Backup", success=False)

        call_args_list = mock_console.print.call_args_list
        output_texts = [str(call) for call in call_args_list]
        output_combined = " ".join(output_texts)
        assert "red" in output_combined.lower() or "✗" in output_combined

    def test_display_phase_complete_ci_mode_uses_simple_text(self) -> None:
        """display_phase_complete() should use simple text in CI mode."""
        output = StringIO()
        with patch.dict(os.environ, {"CI": "true"}):
            service = ProgressDisplayService(file=output)
            service.display_phase_complete("Installation", success=True)

        output_text = output.getvalue()
        assert "Installation" in output_text


class TestProgressDisplayServiceDisplayOverallProgress:
    """Tests for display_overall_progress() method."""

    @pytest.fixture
    def mock_console(self) -> MagicMock:
        """Create a mock Rich console."""
        return MagicMock()

    @pytest.fixture
    def service_with_mock_console(
        self, mock_console: MagicMock
    ) -> ProgressDisplayService:
        """Create service with mock console."""
        return ProgressDisplayService(console=mock_console)

    def test_display_overall_progress_shows_progress_bar(
        self, service_with_mock_console: ProgressDisplayService, mock_console: MagicMock
    ) -> None:
        """display_overall_progress() should show a progress bar."""
        with patch(
            "crafter_ai.installer.services.progress_display_service.Progress"
        ) as mock_progress:
            mock_progress_instance = MagicMock()
            mock_progress.return_value.__enter__ = MagicMock(
                return_value=mock_progress_instance
            )
            mock_progress.return_value.__exit__ = MagicMock(return_value=False)

            service_with_mock_console.display_overall_progress(
                current_phase=2, total_phases=5
            )

            mock_progress.assert_called()

    def test_display_overall_progress_shows_current_and_total(
        self, service_with_mock_console: ProgressDisplayService, mock_console: MagicMock
    ) -> None:
        """display_overall_progress() should show current phase and total phases."""
        service_with_mock_console.display_overall_progress(
            current_phase=3, total_phases=5
        )

        call_args_list = mock_console.print.call_args_list
        output_texts = [str(call) for call in call_args_list]
        output_combined = " ".join(output_texts)
        # Should show something like "3/5" or "Phase 3 of 5"
        assert "3" in output_combined and "5" in output_combined

    def test_display_overall_progress_ci_mode_uses_simple_text(self) -> None:
        """display_overall_progress() should use simple text in CI mode."""
        output = StringIO()
        with patch.dict(os.environ, {"CI": "true"}):
            service = ProgressDisplayService(file=output)
            service.display_overall_progress(current_phase=2, total_phases=5)

        output_text = output.getvalue()
        assert "2" in output_text and "5" in output_text


class TestProgressDisplayServiceIntegration:
    """Integration tests for ProgressDisplayService."""

    def test_full_phase_workflow(self) -> None:
        """Test displaying a complete phase workflow."""
        mock_console = MagicMock()
        service = ProgressDisplayService(console=mock_console)

        # Display phase start
        service.display_phase_start("Pre-flight Checks")

        # Display steps
        steps = [
            ("Checking Python version", ProgressStatus.COMPLETE),
            ("Checking pipx", ProgressStatus.COMPLETE),
            ("Checking disk space", ProgressStatus.FAILED),
        ]

        for i, (message, status) in enumerate(steps, 1):
            progress = InstallProgress(
                phase="Pre-flight Checks",
                step=i,
                total_steps=len(steps),
                message=message,
                status=status,
            )
            service.display_step(progress)

        # Display phase complete (failed because step 3 failed)
        service.display_phase_complete("Pre-flight Checks", success=False)

        # Verify console.print was called multiple times
        assert mock_console.print.call_count >= 4

    def test_service_with_real_console_output(
        self, capsys: pytest.CaptureFixture
    ) -> None:
        """Test service produces actual console output."""
        with patch.dict(os.environ, {"CI": "true"}):
            output = StringIO()
            service = ProgressDisplayService(file=output)

            service.display_phase_start("Test Phase")

            output_text = output.getvalue()
            assert "Test Phase" in output_text

    def test_all_phases_displayed_correctly(self) -> None:
        """Test all five installation phases can be displayed."""
        mock_console = MagicMock()
        service = ProgressDisplayService(console=mock_console)

        phases = [
            "Phase 1: Pre-flight Checks",
            "Phase 2: Release Readiness",
            "Phase 3: Backup Current",
            "Phase 4: Installation",
            "Phase 5: Verification",
        ]

        for phase in phases:
            service.display_phase_start(phase)
            service.display_phase_complete(phase, success=True)

        # Should have called print for each phase start and complete
        assert mock_console.print.call_count >= len(phases) * 2
