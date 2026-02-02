"""Hook driver adapters."""

from src.des.adapters.drivers.hooks.mocked_hook import MockedSubagentStopHook
from src.des.adapters.drivers.hooks.real_hook import RealSubagentStopHook


__all__ = ["MockedSubagentStopHook", "RealSubagentStopHook"]
