"""
DES Validation Package

Provides validators for:
- Prompt validation (PromptValidator) - mandatory sections in prompts
- Scope validation (ScopeValidator) - post-execution file scope checking
"""

from src.des.validation.prompt_validator import PromptValidator, ValidationResult

__all__ = ["PromptValidator", "ValidationResult"]
