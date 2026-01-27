"""
DES Driver Adapters - Primary/Inbound adapter implementations.

Exports all driver adapter implementations that serve as entry points to DES.
"""

from src.des.adapters.drivers.hooks.real_hook import RealSubagentStopHook
from src.des.adapters.drivers.validators.real_validator import RealTemplateValidator

# Backward compatibility aliases
RealHook = RealSubagentStopHook
RealValidator = RealTemplateValidator

__all__ = [
    "RealSubagentStopHook",
    "RealTemplateValidator",
    "RealHook",
    "RealValidator",
]
