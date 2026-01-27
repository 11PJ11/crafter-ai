"""Backward compatibility import for StructuredLogger.

Re-exports StructuredLogger from driven adapters for backward compatibility with old import paths.
Old code using: from src.des.adapters.structured_logger import StructuredLogger
Will continue to work with this module.
"""

from src.des.adapters.driven.logging.structured_logger import StructuredLogger

__all__ = ["StructuredLogger"]
