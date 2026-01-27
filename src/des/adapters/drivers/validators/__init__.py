"""Validator driver adapters."""

from src.des.adapters.drivers.validators.real_validator import RealTemplateValidator
from src.des.adapters.drivers.validators.mocked_validator import MockedTemplateValidator

__all__ = ["RealTemplateValidator", "MockedTemplateValidator"]
