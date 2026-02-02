"""Validator driver adapters."""

from src.des.adapters.drivers.validators.mocked_validator import MockedTemplateValidator
from src.des.adapters.drivers.validators.real_validator import RealTemplateValidator


__all__ = ["MockedTemplateValidator", "RealTemplateValidator"]
