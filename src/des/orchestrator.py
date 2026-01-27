"""Backward compatibility import for DESOrchestrator.

Re-exports orchestrator classes from application for backward compatibility with old import paths.
Old code using: from src.des.orchestrator import DESOrchestrator
Will continue to work with this module.
"""

from src.des.application.orchestrator import DESOrchestrator

__all__ = [
    "DESOrchestrator",
]
