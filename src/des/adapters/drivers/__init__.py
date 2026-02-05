"""
DES Driver Adapters - Primary/Inbound adapter implementations.

Exports all driver adapter implementations that serve as entry points to DES.

Note: Hooks moved to adapters/driven/hooks (hexagonal architecture).
"""

from src.des.adapters.driven.hooks.subagent_stop_hook import SubagentStopHook

# Backward compatibility aliases
RealSubagentStopHook = SubagentStopHook
RealHook = SubagentStopHook

__all__ = [
    "RealHook",
    "RealSubagentStopHook",
    "SubagentStopHook",
]
