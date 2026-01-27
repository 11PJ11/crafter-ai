"""Backward compatibility import for invocation limits validation.

Re-exports from domain for backward compatibility with old import paths.
"""

from src.des.domain.invocation_limits_validator import (
    InvocationLimitsValidator,
    InvocationLimitsResult,
)

__all__ = [
    "InvocationLimitsValidator",
    "InvocationLimitsResult",
]
