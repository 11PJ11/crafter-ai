"""Post-execution hooks for DES (Deterministic Execution System).

Hooks fire when sub-agents complete execution to validate step file state
and detect any deviations from expected phase progression.
"""

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
        # Minimum implementation: just return success
        # Validation logic will be added in subsequent implementation steps
        return HookResult(
            validation_status="PASSED",
            hook_fired=True
        )
