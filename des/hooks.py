"""Post-execution hooks for DES (Deterministic Execution System).

Hooks fire when sub-agents complete execution to validate step file state
and detect any deviations from expected phase progression.
"""

import json
from dataclasses import dataclass, field
from typing import Optional, List


@dataclass
class HookResult:
    """Result from SubagentStopHook validation after agent completion.

    Attributes:
        validation_status: Result of hook validation ("PASSED" or "FAILED")
        hook_fired: Whether the hook executed successfully (default: True)
        abandoned_phases: Phases that were started but not completed
        incomplete_phases: Phases that show incomplete state
        invalid_skips: Phases with invalid [Ignore] markers
        error_count: Number of validation errors detected
        error_type: Category of error found (if any)
        error_message: Human-readable error description
        recovery_suggestions: Recommended actions to resolve issues
        not_executed_phases: Count of phases with NOT_EXECUTED status (diagnostic)
    """

    validation_status: str
    hook_fired: bool = True
    abandoned_phases: List[str] = field(default_factory=list)
    incomplete_phases: List[str] = field(default_factory=list)
    invalid_skips: List[str] = field(default_factory=list)
    error_count: int = 0
    error_type: Optional[str] = None
    error_message: Optional[str] = None
    recovery_suggestions: List[str] = field(default_factory=list)
    not_executed_phases: int = 0


class SubagentStopHook:
    """Hook that fires when a sub-agent completes execution.

    Validates step file state and ensures all expected phases completed
    without being abandoned or left in incomplete state.
    """

    def on_agent_complete(self, step_file_path: str) -> HookResult:
        """Validate step file after agent completion.

        Args:
            step_file_path: Path to the step JSON file to validate

        Returns:
            HookResult indicating validation success/failure and any issues found
        """
        with open(step_file_path, 'r') as f:
            step_data = json.load(f)

        result = HookResult(validation_status="PASSED", hook_fired=True)
        phase_log = step_data.get("tdd_cycle", {}).get("phase_execution_log", [])
        task_state = step_data.get("state", {}).get("status", "UNKNOWN")

        # Aggregate all validation errors instead of early return
        errors = []

        # Check for abandoned phases (IN_PROGRESS status)
        abandoned_phases = self._detect_abandoned_phases(phase_log)
        if abandoned_phases:
            result.abandoned_phases = abandoned_phases
            errors.append(("ABANDONED_PHASE", abandoned_phases))

        # Check for silent completion (task IN_PROGRESS but all phases NOT_EXECUTED)
        not_executed_count = self._count_not_executed_phases(phase_log)
        result.not_executed_phases = not_executed_count

        if task_state == "IN_PROGRESS" and not_executed_count == len(phase_log):
            errors.append(("SILENT_COMPLETION", not_executed_count))

        # Check for EXECUTED phases missing outcome
        incomplete_phases = self._detect_incomplete_phases(phase_log)
        if incomplete_phases:
            result.incomplete_phases = incomplete_phases
            errors.append(("MISSING_OUTCOME", incomplete_phases))

        # Check for SKIPPED phases missing blocked_by reason
        invalid_skips = self._detect_invalid_skips(phase_log)
        if invalid_skips:
            result.invalid_skips = invalid_skips
            errors.append(("INVALID_SKIP", invalid_skips))

        # If any errors found, populate comprehensive failure details
        if errors:
            self._populate_aggregated_failures(result, errors, step_file_path, step_data)
            return result

        return result

    def _detect_abandoned_phases(self, phase_log: List[dict]) -> List[str]:
        """Detect phases left in IN_PROGRESS state after agent completion.

        Args:
            phase_log: List of phase execution entries from step file

        Returns:
            List of phase names found in IN_PROGRESS state
        """
        abandoned = []
        for phase in phase_log:
            if phase.get("status") == "IN_PROGRESS":
                phase_name = phase.get("phase_name", "UNKNOWN")
                abandoned.append(phase_name)
        return abandoned

    def _populate_validation_failure(self, result: HookResult, abandoned_phases: List[str]) -> None:
        """Update HookResult with validation failure details.

        Args:
            result: HookResult object to populate
            abandoned_phases: List of abandoned phase names
        """
        result.abandoned_phases = abandoned_phases
        result.error_count = len(abandoned_phases)
        result.validation_status = "FAILED"
        result.error_type = "ABANDONED_PHASE"
        result.error_message = f"Phase {abandoned_phases[0]} left IN_PROGRESS (abandoned)"

    def _count_not_executed_phases(self, phase_log: List[dict]) -> int:
        """Count phases with NOT_EXECUTED status.

        Args:
            phase_log: List of phase execution entries from step file

        Returns:
            Count of phases with NOT_EXECUTED status
        """
        count = 0
        for phase in phase_log:
            if phase.get("status") == "NOT_EXECUTED":
                count += 1
        return count

    def _populate_silent_completion_failure(self, result: HookResult, not_executed_count: int) -> None:
        """Update HookResult with silent completion failure details.

        Args:
            result: HookResult object to populate
            not_executed_count: Number of phases with NOT_EXECUTED status
        """
        result.validation_status = "FAILED"
        result.error_type = "SILENT_COMPLETION"
        result.error_count = 1
        result.error_message = f"Agent completed without updating step file ({not_executed_count} phases NOT_EXECUTED)"
        result.recovery_suggestions = [
            "Re-execute step with verbose logging to identify early exit cause",
            "Review agent logs for error or exception that prevented work",
            "Verify step file is writable and accessible to agent"
        ]

    def _detect_incomplete_phases(self, phase_log: List[dict]) -> List[str]:
        """Detect phases marked EXECUTED but missing outcome field.

        Args:
            phase_log: List of phase execution entries from step file

        Returns:
            List of phase names with EXECUTED status but no outcome
        """
        incomplete = []
        for phase in phase_log:
            if phase.get("status") == "EXECUTED" and phase.get("outcome") is None:
                phase_name = phase.get("phase_name", "UNKNOWN")
                incomplete.append(phase_name)
        return incomplete

    def _populate_missing_outcome_failure(self, result: HookResult, incomplete_phases: List[str]) -> None:
        """Update HookResult with missing outcome failure details.

        Args:
            result: HookResult object to populate
            incomplete_phases: List of phase names missing outcome
        """
        result.incomplete_phases = incomplete_phases
        result.error_count = len(incomplete_phases)
        result.validation_status = "FAILED"
        result.error_type = "MISSING_OUTCOME"
        result.error_message = f"Phase {incomplete_phases[0]} marked EXECUTED but missing outcome"

    def _detect_invalid_skips(self, phase_log: List[dict]) -> List[str]:
        """Detect phases marked SKIPPED but missing blocked_by reason.

        Args:
            phase_log: List of phase execution entries from step file

        Returns:
            List of phase names with SKIPPED status but no blocked_by reason
        """
        invalid_skips = []
        for phase in phase_log:
            if phase.get("status") == "SKIPPED":
                blocked_by = phase.get("blocked_by")
                # Check if blocked_by is None or empty string
                if not blocked_by:
                    phase_name = phase.get("phase_name", "UNKNOWN")
                    invalid_skips.append(phase_name)
        return invalid_skips

    def _populate_invalid_skip_failure(self, result: HookResult, invalid_skips: List[str]) -> None:
        """Update HookResult with invalid skip failure details.

        Args:
            result: HookResult object to populate
            invalid_skips: List of phase names with invalid SKIPPED status
        """
        result.invalid_skips = invalid_skips
        result.error_count = len(invalid_skips)
        result.validation_status = "FAILED"
        result.error_type = "INVALID_SKIP"
        result.error_message = f"Phase {invalid_skips[0]} marked SKIPPED but missing blocked_by reason"

    def _populate_aggregated_failures(
        self, result: HookResult, errors: List[tuple], step_file_path: str, step_data: dict
    ) -> None:
        """Update HookResult with aggregated validation failures and recovery suggestions.

        Args:
            result: HookResult object to populate
            errors: List of (error_type, error_data) tuples
            step_file_path: Path to step file for updating state
            step_data: Current step file data
        """
        result.validation_status = "FAILED"

        # Count total errors
        total_errors = 0
        error_details = []

        for error_type, error_data in errors:
            if error_type == "ABANDONED_PHASE":
                count = len(error_data)
                total_errors += count
                error_details.append(f"{count} abandoned phase(s): {', '.join(error_data)}")
            elif error_type == "MISSING_OUTCOME":
                count = len(error_data)
                total_errors += count
                error_details.append(f"{count} incomplete phase(s): {', '.join(error_data)}")
            elif error_type == "INVALID_SKIP":
                count = len(error_data)
                total_errors += count
                error_details.append(f"{count} invalid skip(s): {', '.join(error_data)}")
            elif error_type == "SILENT_COMPLETION":
                total_errors += 1
                error_details.append(f"Silent completion ({error_data} phases NOT_EXECUTED)")

        result.error_count = total_errors
        result.error_type = "MULTIPLE_ERRORS" if len(errors) > 1 else errors[0][0]

        # Use specific error messages for single errors (backward compatibility)
        if len(errors) == 1:
            error_type, error_data = errors[0]
            if error_type == "ABANDONED_PHASE":
                result.error_message = f"Phase {error_data[0]} left IN_PROGRESS (abandoned)"
            elif error_type == "MISSING_OUTCOME":
                result.error_message = f"Phase {error_data[0]} marked EXECUTED but missing outcome"
            elif error_type == "INVALID_SKIP":
                result.error_message = f"Phase {error_data[0]} marked SKIPPED but missing blocked_by reason"
            elif error_type == "SILENT_COMPLETION":
                result.error_message = f"Agent completed without updating step file ({error_data} phases NOT_EXECUTED)"
        else:
            # Multiple errors - use aggregated format
            result.error_message = f"{total_errors} validation error(s) found: {'; '.join(error_details)}"

        # Generate recovery suggestions
        result.recovery_suggestions = self._generate_recovery_suggestions(errors)

        # Update step file state to FAILED
        self._update_step_file_state(step_file_path, step_data, result.error_message)

    def _generate_recovery_suggestions(self, errors: List[tuple]) -> List[str]:
        """Generate actionable recovery suggestions based on validation errors.

        Args:
            errors: List of (error_type, error_data) tuples

        Returns:
            List of recovery suggestion strings
        """
        suggestions = []

        # For single SILENT_COMPLETION error, use existing suggestions
        if len(errors) == 1 and errors[0][0] == "SILENT_COMPLETION":
            return [
                "Re-execute step with verbose logging to identify early exit cause",
                "Review agent logs for error or exception that prevented work",
                "Verify step file is writable and accessible to agent"
            ]

        # For other errors, always start with transcript review (explains WHY)
        suggestions.append(
            "Review agent transcript for error details to understand what went wrong during execution."
        )

        # Add error-specific suggestions (explains HOW to fix)
        for error_type, error_data in errors:
            if error_type == "ABANDONED_PHASE":
                for phase in error_data:
                    suggestions.append(
                        f"Reset {phase} phase status to NOT_EXECUTED since it was left IN_PROGRESS without completion."
                    )
                suggestions.append(
                    "Run `/nw:execute` again to resume from the first incomplete phase."
                )
            elif error_type == "MISSING_OUTCOME":
                for phase in error_data:
                    suggestions.append(
                        f"Add outcome to {phase} phase from transcript evidence showing PASS or FAIL result."
                    )
            elif error_type == "INVALID_SKIP":
                for phase in error_data:
                    suggestions.append(
                        f"Add blocked_by reason to {phase} phase explaining why it was skipped."
                    )

        # Ensure minimum 3 suggestions (add generic if needed)
        if len(suggestions) < 3:
            suggestions.append(
                "Update step file manually with correct phase states based on transcript review."
            )

        return suggestions

    def _update_step_file_state(self, step_file_path: str, step_data: dict, failure_reason: str) -> None:
        """Update step file state to FAILED with failure reason.

        Args:
            step_file_path: Path to step file to update
            step_data: Current step file data
            failure_reason: Reason for validation failure
        """
        # Update state
        if "state" not in step_data:
            step_data["state"] = {}

        step_data["state"]["status"] = "FAILED"
        step_data["state"]["failure_reason"] = failure_reason

        # Write updated step file
        with open(step_file_path, 'w') as f:
            json.dump(step_data, f, indent=2)
