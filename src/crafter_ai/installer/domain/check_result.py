"""CheckResult domain object and CheckSeverity enum.

This module defines the core domain objects for the pre-flight check system.
These are pure domain objects with no external dependencies.
"""

from dataclasses import dataclass
from enum import Enum


class CheckSeverity(Enum):
    """Severity level for a pre-flight check.

    BLOCKING: Check failure prevents installation from proceeding.
    WARNING: Check failure shows a warning but allows continuation.
    """

    BLOCKING = "blocking"
    WARNING = "warning"


@dataclass(frozen=True)
class CheckResult:
    """Immutable result of a pre-flight check.

    Attributes:
        id: Unique identifier for the check.
        name: Human-readable check name.
        passed: Whether the check passed.
        severity: BLOCKING or WARNING severity level.
        message: Result message describing the outcome.
        remediation: How to fix if failed (optional).
        fixable: Whether the issue can be auto-fixed.
        fix_command: Command to auto-fix the issue (optional).
    """

    id: str
    name: str
    passed: bool
    severity: CheckSeverity
    message: str
    remediation: str | None = None
    fixable: bool = False
    fix_command: str | None = None
