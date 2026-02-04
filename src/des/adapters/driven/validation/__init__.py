"""
Validation adapters for DES (driven side).

This module contains adapters that interact with external systems
for validation purposes (e.g., git subprocess for scope validation).
"""

from src.des.adapters.driven.validation.scope_validator import (
    ScopeValidationResult,
    ScopeValidator,
)


__all__ = ["ScopeValidationResult", "ScopeValidator"]
