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
        turn_limit_exceeded: Whether any phase exceeded configured max_turns limit
        timeout_exceeded: Whether total duration exceeded configured time limit
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
    turn_limit_exceeded: bool = False
    timeout_exceeded: bool = False


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

        # Check for turn limit exceeded
        max_turns = step_data.get("tdd_cycle", {}).get("max_turns")
        exceeded_phases = self._detect_turn_limit_exceeded(phase_log, max_turns)
        if exceeded_phases:
            result.turn_limit_exceeded = True
            errors.append(("TURN_LIMIT_EXCEEDED", exceeded_phases))

        # Check for timeout exceeded
        duration_minutes = step_data.get("tdd_cycle", {}).get("duration_minutes")
        total_extensions_minutes = step_data.get("tdd_cycle", {}).get("total_extensions_minutes")
        timeout_info = self._detect_timeout_exceeded(phase_log, duration_minutes, total_extensions_minutes)
        if timeout_info["timeout_exceeded"]:
            result.timeout_exceeded = True
            errors.append(("TIMEOUT_EXCEEDED", timeout_info))

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

    def _detect_silent_completion(self, phase_log: List[dict]) -> bool:
        """Detect if all phases are NOT_EXECUTED (silent completion).

        Args:
            phase_log: List of phase execution entries from step file

        Returns:
            True if all phases are NOT_EXECUTED (silent completion), False otherwise
        """
        if not phase_log:
            return False

        not_executed_count = self._count_not_executed_phases(phase_log)
        return not_executed_count == len(phase_log)

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

    def _detect_turn_limit_exceeded(self, phase_log: List[dict], max_turns: Optional[int]) -> List[dict]:
        """Detect phases where turn_count exceeds max_turns limit.

        Args:
            phase_log: List of phase execution entries from step file
            max_turns: Maximum turns allowed per phase (from tdd_cycle config)

        Returns:
            List of dicts with phase_name, turn_count, and max_turns for exceeded phases
        """
        if max_turns is None:
            return []

        exceeded = []
        for phase in phase_log:
            turn_count = phase.get("turn_count")
            phase_max_turns = phase.get("max_turns", max_turns)

            # Only check phases that have turn_count tracked
            if turn_count is not None and turn_count > phase_max_turns:
                phase_name = phase.get("phase_name", "UNKNOWN")
                exceeded.append({
                    "phase_name": phase_name,
                    "turn_count": turn_count,
                    "max_turns": phase_max_turns
                })
        return exceeded

    def _detect_timeout_exceeded(self, phase_log: List[dict], duration_minutes: Optional[int], total_extensions_minutes: Optional[int]) -> dict:
        """Detect if total execution duration exceeded configured time limit.

        Args:
            phase_log: List of phase execution entries from step file
            duration_minutes: Configured base duration limit in minutes
            total_extensions_minutes: Total extension time granted in minutes

        Returns:
            Dict with timeout_exceeded bool, actual_seconds, and expected_seconds
        """
        if duration_minutes is None:
            return {"timeout_exceeded": False, "actual_seconds": 0, "expected_seconds": 0}

        # Calculate expected duration limit in seconds
        base_seconds = duration_minutes * 60
        extension_seconds = (total_extensions_minutes or 0) * 60
        expected_seconds = base_seconds + extension_seconds

        # Calculate actual duration from phase log
        actual_seconds = 0
        for phase in phase_log:
            phase_duration = phase.get("duration_seconds", 0)
            if phase_duration is not None:
                actual_seconds += phase_duration

        # Check if timeout exceeded
        timeout_exceeded = actual_seconds > expected_seconds

        return {
            "timeout_exceeded": timeout_exceeded,
            "actual_seconds": actual_seconds,
            "expected_seconds": expected_seconds,
            "actual_minutes": actual_seconds // 60,
            "expected_minutes": expected_seconds // 60
        }

    def _populate_silent_completion_failure(self, result: HookResult, not_executed_count: int) -> None:
        """Populate HookResult with SILENT_COMPLETION error details.

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
            elif error_type == "TURN_LIMIT_EXCEEDED":
                count = len(error_data)
                total_errors += count
                phase_names = [p["phase_name"] for p in error_data]
                error_details.append(f"{count} phase(s) exceeded turn limit: {', '.join(phase_names)}")
            elif error_type == "TIMEOUT_EXCEEDED":
                total_errors += 1
                actual = error_data["actual_minutes"]
                expected = error_data["expected_minutes"]
                error_details.append(f"Execution timeout exceeded ({actual}min > {expected}min)")

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
            elif error_type == "TURN_LIMIT_EXCEEDED":
                phase_info = error_data[0]
                result.error_message = (
                    f"Phase {phase_info['phase_name']} exceeded turn limit "
                    f"({phase_info['turn_count']}/{phase_info['max_turns']} turns)"
                )
            elif error_type == "TIMEOUT_EXCEEDED":
                result.error_message = (
                    f"Execution timeout exceeded: {error_data['actual_seconds']}s "
                    f"({error_data['actual_minutes']}min) > {error_data['expected_seconds']}s "
                    f"({error_data['expected_minutes']}min)"
                )
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
            elif error_type == "TURN_LIMIT_EXCEEDED":
                for phase_info in error_data:
                    phase_name = phase_info["phase_name"]
                    turn_count = phase_info["turn_count"]
                    max_turns = phase_info["max_turns"]
                    suggestions.append(
                        f"Increase max_turns limit from {max_turns} to at least {turn_count + 10} "
                        f"to accommodate {phase_name} phase complexity."
                    )
                suggestions.append(
                    "Break step into smaller, simpler sub-tasks to reduce turn count per phase."
                )
            elif error_type == "TIMEOUT_EXCEEDED":
                actual_min = error_data["actual_minutes"]
                expected_min = error_data["expected_minutes"]
                additional_min = actual_min - expected_min + 10
                suggestions.append(
                    f"Request time extension of at least {additional_min} minutes to accommodate step complexity."
                )
                suggestions.append(
                    "Break step into smaller sub-tasks to reduce execution time per step."
                )
                suggestions.append(
                    "Simplify step requirements or reduce scope to fit within time limit."
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
