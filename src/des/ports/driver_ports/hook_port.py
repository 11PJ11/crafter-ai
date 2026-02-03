from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Optional


if TYPE_CHECKING:
    from src.des.adapters.driven.validation.scope_validator import ScopeValidationResult


@dataclass
class HookResult:
    """Result from hook validation."""

    validation_status: str
    hook_fired: bool = True
    abandoned_phases: list[str] = field(default_factory=list)
    incomplete_phases: list[str] = field(default_factory=list)
    invalid_skips: list[str] = field(default_factory=list)
    error_count: int = 0
    error_type: str | None = None
    error_message: str | None = None
    recovery_suggestions: list[str] = field(default_factory=list)
    not_executed_phases: int = 0
    turn_limit_exceeded: bool = False
    timeout_exceeded: bool = False
    scope_validation_result: Optional["ScopeValidationResult"] = None


class HookPort(ABC):
    """Port for post-execution validation hooks."""

    @abstractmethod
    def persist_turn_count(
        self, step_file_path: str, phase_name: str, turn_count: int
    ) -> None:
        """Persist turn_count to phase_execution_log entry.

        Updates the phase_execution_log entry for the specified phase with the turn_count value.

        Args:
            step_file_path: Absolute path to step JSON file
            phase_name: Name of the phase to update (e.g., "PREPARE", "RED_ACCEPTANCE")
            turn_count: Turn count value to persist (must be non-negative)

        Raises:
            ValueError: If turn_count is negative
            KeyError: If phase_name not found in phase_execution_log
        """
        pass

    @abstractmethod
    def on_agent_complete(self, step_file_path: str) -> HookResult:
        """Validate step file after sub-agent completion.

        Args:
            step_file_path: Absolute path to step JSON file

        Returns:
            HookResult with validation status and any errors found
        """
        pass
