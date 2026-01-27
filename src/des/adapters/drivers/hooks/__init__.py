"""Hook driver adapters."""

from src.des.adapters.drivers.hooks.real_hook import RealSubagentStopHook
from src.des.adapters.drivers.hooks.mocked_hook import MockedSubagentStopHook

__all__ = ["RealSubagentStopHook", "MockedSubagentStopHook"]
