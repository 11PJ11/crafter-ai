from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional

@dataclass
class ValidationResult:
    """Result of template validation."""
    status: str
    errors: List[str]
    task_invocation_allowed: bool
    duration_ms: float
    recovery_guidance: Optional[List[str]] = None

class ValidatorPort(ABC):
    """Port for template validation."""

    @abstractmethod
    def validate_prompt(self, prompt: str) -> ValidationResult:
        """Validate prompt for mandatory sections and TDD phases.

        Args:
            prompt: Full prompt text to validate

        Returns:
            ValidationResult with status, errors, and task invocation flag
        """
        pass
