"""Backward compatibility import for SubagentStopHook.

Re-exports SubagentStopHook from driver_ports for backward compatibility with old import paths.
Old code using: from src.des.hooks import SubagentStopHook
Will continue to work with this module.
"""

from src.des.ports.driver_ports.hook_port import HookPort as SubagentStopHook

__all__ = ["SubagentStopHook"]
