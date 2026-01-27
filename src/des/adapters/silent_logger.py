"""Backward compatibility import for SilentLogger.

Re-exports SilentLogger from driven adapters for backward compatibility with old import paths.
Old code using: from src.des.adapters.silent_logger import SilentLogger
Will continue to work with this module.
"""

from src.des.adapters.driven.logging.silent_logger import SilentLogger

__all__ = ["SilentLogger"]
