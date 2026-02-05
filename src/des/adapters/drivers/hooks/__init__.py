"""Hook driver adapters.

Note: Hooks are now in adapters/driven/hooks (hexagonal architecture).
This __init__.py is kept for backwards compatibility.
"""

from src.des.adapters.driven.hooks.subagent_stop_hook import SubagentStopHook
from src.des.adapters.drivers.hooks.mocked_hook import MockedSubagentStopHook

# Backwards compatibility alias
RealSubagentStopHook = SubagentStopHook

__all__ = ["MockedSubagentStopHook", "SubagentStopHook", "RealSubagentStopHook"]
