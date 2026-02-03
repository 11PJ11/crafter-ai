"""
DES Driver Adapters - Primary/Inbound adapter implementations.

Exports all driver adapter implementations that serve as entry points to DES.
"""

from src.des.adapters.drivers.hooks.real_hook import RealSubagentStopHook


# Backward compatibility aliases
RealHook = RealSubagentStopHook

__all__ = [
    "RealHook",
    "RealSubagentStopHook",
]
