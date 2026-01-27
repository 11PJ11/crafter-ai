"""Backward compatibility import for HookPort and HookResult.

Re-exports HookPort and HookResult from driver_ports for backward compatibility with old import paths.
Old code using: from src.des.ports.hook_port import HookPort, HookResult
Will continue to work with this module.
"""

from src.des.ports.driver_ports.hook_port import HookPort, HookResult

__all__ = ["HookPort", "HookResult"]
