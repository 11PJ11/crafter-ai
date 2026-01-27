"""Backward compatibility import for hooks module components.

Re-exports hooks classes from application for backward compatibility with old import paths.
Old code using: from src.des.hooks import SubagentStopHook
Will continue to work with this module.
"""

from src.des.application.hooks import SubagentStopHook

__all__ = [
    "SubagentStopHook",
]
