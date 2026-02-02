"""AutoRepairService for handling fixable check failures.

This module provides the AutoRepairService application service that handles
interactive repair of fixable pre-flight check failures. It prompts users
for confirmation and executes fix commands with progress feedback.

Used by: forge:build CLI command for auto-repairing missing dependencies.
"""

import os
import subprocess
from dataclasses import dataclass

from rich.console import Console

from crafter_ai.installer.domain.check_result import CheckResult


@dataclass(frozen=True)
class RepairResult:
    """Immutable result of a repair attempt.

    Attributes:
        success: Whether the repair completed successfully.
        message: Human-readable message describing the outcome.
        command_output: Output from the executed command (stdout/stderr).
    """

    success: bool
    message: str
    command_output: str


class AutoRepairService:
    """Application service for auto-repairing fixable check failures.

    This service handles:
    - Checking if a check result can be auto-repaired
    - Prompting the user for confirmation (interactive mode)
    - Auto-accepting repairs in CI mode (CI=true environment)
    - Executing fix commands with spinner feedback
    - Reporting repair outcomes

    Example usage:
        service = AutoRepairService()
        if service.can_repair(check_result):
            result = service.repair(check_result, console)
            if result.success:
                print("Repair successful!")
    """

    def can_repair(self, check_result: CheckResult) -> bool:
        """Check if a check result can be auto-repaired.

        A check can be repaired if:
        - It did not pass (failed)
        - It is marked as fixable
        - It has a fix_command defined

        Args:
            check_result: The check result to evaluate.

        Returns:
            True if the check can be auto-repaired, False otherwise.
        """
        return (
            not check_result.passed
            and check_result.fixable
            and check_result.fix_command is not None
        )

    def repair(self, check_result: CheckResult, console: Console) -> RepairResult:
        """Attempt to repair a failed check.

        This method:
        1. Verifies the check can be repaired
        2. Prompts for user confirmation (unless in CI mode)
        3. Executes the fix command with a spinner
        4. Returns the repair outcome

        In CI mode (CI=true environment variable), repairs are auto-accepted
        without prompting.

        Args:
            check_result: The failed check result to repair.
            console: Rich Console for prompts and output.

        Returns:
            RepairResult with success status, message, and command output.
        """
        # Check if this can be repaired
        if not self.can_repair(check_result):
            return RepairResult(
                success=False,
                message=f"Check '{check_result.name}' cannot be auto-repaired",
                command_output="",
            )

        # In CI mode, auto-accept without prompting
        is_ci_mode = os.environ.get("CI", "").lower() in ("true", "1", "yes")

        if not is_ci_mode:
            # Prompt user for confirmation
            prompt_text = (
                f"\n[yellow]{check_result.name}[/yellow] failed.\n"
                f"Fix command: [cyan]{check_result.fix_command}[/cyan]\n"
                f"Install it now? [Y/n] "
            )
            response = console.input(prompt_text)

            # Default to Y if empty response, otherwise check for affirmative
            if response.strip().lower() not in ("", "y", "yes"):
                return RepairResult(
                    success=False,
                    message="User declined auto-repair",
                    command_output="",
                )

        # Execute the fix command with spinner
        fix_command = check_result.fix_command
        assert fix_command is not None  # Already validated in can_repair

        try:
            with console.status(f"[bold cyan]Installing... {fix_command}"):
                result = subprocess.run(
                    fix_command,
                    shell=True,
                    capture_output=True,
                    text=True,
                    check=False,
                )

            # Combine stdout and stderr for output
            command_output = result.stdout + result.stderr

            if result.returncode == 0:
                return RepairResult(
                    success=True,
                    message=f"Successfully repaired '{check_result.name}'",
                    command_output=command_output.strip(),
                )
            else:
                return RepairResult(
                    success=False,
                    message=f"Repair failed for '{check_result.name}'",
                    command_output=command_output.strip(),
                )

        except subprocess.SubprocessError as e:
            return RepairResult(
                success=False,
                message=f"Repair failed: {e}",
                command_output=str(e),
            )
