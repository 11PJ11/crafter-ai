"""Backward compatibility import for config_loader module components.

Re-exports config_loader classes from application for backward compatibility with old import paths.
Old code using: from src.des.config_loader import ConfigLoader, ConfigValidationError
Will continue to work with this module.
"""

from src.des.application.config_loader import (
    ConfigLoader,
    ConfigValidationError,
)

__all__ = [
    "ConfigLoader",
    "ConfigValidationError",
]
