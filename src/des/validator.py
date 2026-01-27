"""Backward compatibility import for validator module components.

Re-exports validator classes from application for backward compatibility with old import paths.
Old code using: from src.des.validator import ValidationResult, ExecutionLogValidator, etc.
Will continue to work with this module.
"""

from src.des.application.validator import (
    ValidationResult,
    ExecutionLogValidator,
    MandatorySectionChecker,
    TDDPhaseValidator,
    DESMarkerValidator,
    TemplateValidator,
)

__all__ = [
    "ValidationResult",
    "ExecutionLogValidator",
    "MandatorySectionChecker",
    "TDDPhaseValidator",
    "DESMarkerValidator",
    "TemplateValidator",
]
