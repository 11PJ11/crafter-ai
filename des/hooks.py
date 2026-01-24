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

        abandoned_phases = self._detect_abandoned_phases(phase_log)
        if abandoned_phases:
            self._populate_validation_failure(result, abandoned_phases)

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
