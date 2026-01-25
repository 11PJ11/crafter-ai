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

        # Check for abandoned phases (IN_PROGRESS status)
        abandoned_phases = self._detect_abandoned_phases(phase_log)
        if abandoned_phases:
            self._populate_validation_failure(result, abandoned_phases)
            return result

        # Check for silent completion (task IN_PROGRESS but all phases NOT_EXECUTED)
        not_executed_count = self._count_not_executed_phases(phase_log)
        result.not_executed_phases = not_executed_count

        if task_state == "IN_PROGRESS" and not_executed_count == len(phase_log):
            self._populate_silent_completion_failure(result, not_executed_count)
            return result

        # Check for EXECUTED phases missing outcome
        incomplete_phases = self._detect_incomplete_phases(phase_log)
        if incomplete_phases:
            self._populate_missing_outcome_failure(result, incomplete_phases)
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
