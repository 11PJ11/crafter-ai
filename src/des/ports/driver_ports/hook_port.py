from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class HookResult:
    """Result from hook validation."""
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

class HookPort(ABC):
    """Port for post-execution validation hooks."""

    @abstractmethod
    def on_agent_complete(self, step_file_path: str) -> HookResult:
        """Validate step file after sub-agent completion.

        Args:
            step_file_path: Absolute path to step JSON file

        Returns:
            HookResult with validation status and any errors found
        """
        pass
