"""DES Driven Hook Adapters - Secondary/Outbound adapters for validation.

Hexagonal architecture: These adapters implement the HookPort interface
and are plugged into the application layer (DESOrchestrator).
"""

from src.des.adapters.driven.hooks.subagent_stop_hook import SubagentStopHook

__all__ = ["SubagentStopHook"]
