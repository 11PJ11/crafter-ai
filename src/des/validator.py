"""Backward compatibility import for validator module components.

Re-exports validator classes from application for backward compatibility with old import paths.
Old code using: from src.des.validator import TemplateValidator
Will continue to work with this module.
"""

from src.des.application.validator import (
    TemplateValidator,
    ValidationResult,
    MandatorySectionChecker,
    TDDPhaseValidator,
)

__all__ = [
    "TemplateValidator",
    "ValidationResult",
    "MandatorySectionChecker",
    "TDDPhaseValidator",
]
