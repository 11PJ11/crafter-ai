"""
Audit event type definitions and AuditEvent dataclass.

Defines standardized event categories:
- TASK_INVOCATION: Task invocation lifecycle events
- PHASE: TDD phase execution events
- SUBAGENT_STOP: Subagent termination events
- COMMIT: Git commit events
"""

from dataclasses import dataclass, asdict
from enum import Enum
from typing import Any, Dict, List, Optional


class EventType(Enum):
    """Audit event type categories."""

    # TASK_INVOCATION events
    TASK_INVOCATION_STARTED = "TASK_INVOCATION_STARTED"
    TASK_INVOCATION_VALIDATED = "TASK_INVOCATION_VALIDATED"
    TASK_INVOCATION_REJECTED = "TASK_INVOCATION_REJECTED"

    # PHASE events
    PHASE_STARTED = "PHASE_STARTED"
    PHASE_EXECUTED = "PHASE_EXECUTED"
    PHASE_SKIPPED = "PHASE_SKIPPED"
    PHASE_FAILED = "PHASE_FAILED"

    # SUBAGENT_STOP events
    SUBAGENT_STOP_VALIDATION = "SUBAGENT_STOP_VALIDATION"
    SUBAGENT_STOP_FAILURE = "SUBAGENT_STOP_FAILURE"

    # COMMIT events
    COMMIT_SUCCESS = "COMMIT_SUCCESS"
    COMMIT_FAILURE = "COMMIT_FAILURE"

    # VALIDATION events
    VALIDATION_REJECTED = "VALIDATION_REJECTED"


@dataclass
class AuditEvent:
    """Structured audit event with complete execution context."""

    timestamp: str  # ISO 8601 format: YYYY-MM-DDTHH:MM:SS.sssZ
    event: str  # Event type from EventType enum
    step_path: Optional[str] = None  # Path to the step file
    phase_name: Optional[str] = None  # Name of the TDD phase
    status: Optional[str] = None  # Phase status: IN_PROGRESS, EXECUTED, SKIPPED
    outcome: Optional[str] = None  # Success or failure outcome
    duration_minutes: Optional[float] = None  # Duration of phase/event
    reason: Optional[str] = None  # Reason for failure/rejection
    commit_hash: Optional[str] = None  # Git commit hash (for COMMIT events)
    rejection_reason: Optional[str] = None  # Detailed rejection reason
    extra_context: Optional[Dict[str, Any]] = None  # Additional contextual data

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization.

        Excludes None values for cleaner JSONL output.
        """
        data = asdict(self)
        # Remove None values
        return {k: v for k, v in data.items() if v is not None}

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'AuditEvent':
        """Create AuditEvent from dictionary.

        Args:
            data: Dictionary with event data

        Returns:
            AuditEvent instance
        """
        return AuditEvent(**data)


def validate_event_type(event_type: str) -> bool:
    """Validate that event type is in allowed categories.

    Args:
        event_type: Event type string to validate

    Returns:
        True if valid, False otherwise
    """
    return any(e.value == event_type for e in EventType)


def get_event_category(event_type: str) -> str:
    """Get event category from event type.

    Args:
        event_type: Event type string (e.g., 'TASK_INVOCATION_STARTED')

    Returns:
        Event category (e.g., 'TASK_INVOCATION')
    """
    if event_type.startswith("TASK_INVOCATION"):
        return "TASK_INVOCATION"
    elif event_type.startswith("PHASE"):
        return "PHASE"
    elif event_type.startswith("SUBAGENT_STOP"):
        return "SUBAGENT_STOP"
    elif event_type.startswith("COMMIT"):
        return "COMMIT"
    elif event_type.startswith("VALIDATION"):
        return "VALIDATION"
    else:
        return "UNKNOWN"
