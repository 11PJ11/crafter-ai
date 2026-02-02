"""ProgressDisplayService for displaying installation progress.

This module provides the ProgressDisplayService application service that:
- Displays installation progress using Rich library components
- Shows phase headers with Rich Panel
- Shows step progress with spinner/checkmark/X based on status
- Shows overall progress bar
- Supports CI mode with simple text output

Used by: forge:install CLI commands for progress display
"""

import os
from dataclasses import dataclass
from enum import Enum
from typing import IO

from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.status import Status


class ProgressStatus(Enum):
    """Status of an installation step.

    PENDING: Step has not started yet.
    RUNNING: Step is currently in progress.
    COMPLETE: Step completed successfully.
    FAILED: Step failed.
    """

    PENDING = "pending"
    RUNNING = "running"
    COMPLETE = "complete"
    FAILED = "failed"


@dataclass(frozen=True)
class InstallProgress:
    """Immutable progress state for an installation step.

    Attributes:
        phase: Name of the current phase.
        step: Current step number within the phase.
        total_steps: Total number of steps in the phase.
        message: Description of the current step.
        status: Current status of the step.
    """

    phase: str
    step: int
    total_steps: int
    message: str
    status: ProgressStatus


class ProgressDisplayService:
    """Application service for displaying installation progress.

    This service:
    - Uses Rich library for interactive terminal output
    - Falls back to simple text in CI mode
    - Displays phase headers, step progress, and overall progress bar
    """

    # Status indicators
    CHECKMARK = "[green]✓[/green]"
    CROSS = "[red]✗[/red]"
    PENDING_INDICATOR = "[dim]○[/dim]"

    def __init__(
        self,
        console: Console | None = None,
        file: IO[str] | None = None,
    ) -> None:
        """Initialize ProgressDisplayService.

        Args:
            console: Optional Rich Console for output. If None, creates one.
            file: Optional file for CI mode output. If None, uses stdout.
        """
        self._file = file
        if console is not None:
            self._console = console
        else:
            self._console = Console()

    def is_ci_mode(self) -> bool:
        """Check if running in CI mode.

        CI mode is detected via CI environment variable set to 'true' or '1'.

        Returns:
            True if in CI mode, False otherwise.
        """
        ci_value = os.environ.get("CI", "").lower()
        return ci_value in ("true", "1")

    def display_phase_start(self, phase_name: str) -> None:
        """Display the start of a phase.

        Shows a Rich Panel with the phase name, or simple text in CI mode.

        Args:
            phase_name: Name of the phase starting.
        """
        if self.is_ci_mode():
            self._print_ci(f"\n== {phase_name} ==")
            return

        panel = Panel(
            f"[bold cyan]{phase_name}[/bold cyan]",
            border_style="cyan",
            padding=(0, 2),
        )
        self._console.print()
        self._console.print(panel)

    def display_step(self, progress: InstallProgress) -> None:
        """Display a step's progress.

        Shows spinner for running status, checkmark for complete,
        X for failed, or pending indicator for pending.

        Args:
            progress: InstallProgress with step details and status.
        """
        if self.is_ci_mode():
            status_char = self._get_ci_status_char(progress.status)
            self._print_ci(
                f"  {status_char} [{progress.step}/{progress.total_steps}] {progress.message}"
            )
            return

        if progress.status == ProgressStatus.RUNNING:
            self._display_running_step(progress)
        else:
            self._display_static_step(progress)

    def display_phase_complete(self, phase_name: str, success: bool) -> None:
        """Display phase completion summary.

        Shows success (green checkmark) or failure (red X) message.

        Args:
            phase_name: Name of the completed phase.
            success: True if phase completed successfully, False otherwise.
        """
        if self.is_ci_mode():
            status = "COMPLETE" if success else "FAILED"
            char = "[OK]" if success else "[FAIL]"
            self._print_ci(f"{char} {phase_name} {status}")
            return

        if success:
            message = f"{self.CHECKMARK} [green]{phase_name} complete[/green]"
        else:
            message = f"{self.CROSS} [red]{phase_name} failed[/red]"

        self._console.print(message)

    def display_overall_progress(self, current_phase: int, total_phases: int) -> None:
        """Display overall installation progress.

        Shows a progress bar with current phase out of total phases.

        Args:
            current_phase: Current phase number (1-based).
            total_phases: Total number of phases.
        """
        if self.is_ci_mode():
            percentage = (current_phase / total_phases) * 100
            self._print_ci(
                f"Progress: {current_phase}/{total_phases} phases ({percentage:.0f}%)"
            )
            return

        # Display progress information
        self._console.print(
            f"\n[bold]Overall Progress:[/bold] Phase {current_phase} of {total_phases}"
        )

        # Visual progress bar using Rich Progress
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self._console,
            transient=True,
        ) as progress_bar:
            task = progress_bar.add_task(
                f"Phase {current_phase}/{total_phases}",
                total=total_phases,
                completed=current_phase,
            )
            progress_bar.update(task, completed=current_phase)

    def _display_running_step(self, progress: InstallProgress) -> None:
        """Display a step that is currently running with spinner.

        Args:
            progress: InstallProgress with step details.
        """
        step_text = f"[{progress.step}/{progress.total_steps}] {progress.message}"
        with Status(step_text, console=self._console, spinner="dots"):
            pass  # Status is just shown momentarily; caller manages actual work

    def _display_static_step(self, progress: InstallProgress) -> None:
        """Display a step with static indicator (checkmark, X, or pending).

        Args:
            progress: InstallProgress with step details.
        """
        indicator = self._get_status_indicator(progress.status)
        step_text = (
            f"  {indicator} [{progress.step}/{progress.total_steps}] {progress.message}"
        )
        self._console.print(step_text)

    def _get_status_indicator(self, status: ProgressStatus) -> str:
        """Get the Rich-formatted status indicator.

        Args:
            status: ProgressStatus to get indicator for.

        Returns:
            Rich-formatted string with status indicator.
        """
        indicators = {
            ProgressStatus.PENDING: self.PENDING_INDICATOR,
            ProgressStatus.RUNNING: "[yellow]⋯[/yellow]",
            ProgressStatus.COMPLETE: self.CHECKMARK,
            ProgressStatus.FAILED: self.CROSS,
        }
        return indicators.get(status, self.PENDING_INDICATOR)

    def _get_ci_status_char(self, status: ProgressStatus) -> str:
        """Get simple text status character for CI mode.

        Args:
            status: ProgressStatus to get character for.

        Returns:
            Simple text status character.
        """
        chars = {
            ProgressStatus.PENDING: "[ ]",
            ProgressStatus.RUNNING: "[..]",
            ProgressStatus.COMPLETE: "[OK]",
            ProgressStatus.FAILED: "[FAIL]",
        }
        return chars.get(status, "[ ]")

    def _print_ci(self, text: str) -> None:
        """Print text in CI mode.

        Args:
            text: Text to print.
        """
        if self._file is not None:
            self._file.write(text + "\n")
        else:
            print(text)
