"""Backward compatibility import for DESMarkerValidator.

Re-exports DESMarkerValidator from application layer for backward compatibility with old import paths.
Old code using: from src.des.adapters.validator import DESMarkerValidator
Will continue to work with this module.
"""

from src.des.application.validator import DESMarkerValidator

__all__ = ["DESMarkerValidator"]
