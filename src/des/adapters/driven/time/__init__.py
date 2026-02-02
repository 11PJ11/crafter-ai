"""Time provider driven adapters."""

from src.des.adapters.driven.time.mocked_time import MockedTimeProvider
from src.des.adapters.driven.time.system_time import SystemTimeProvider


# Backward compatibility alias
SystemTime = SystemTimeProvider

__all__ = ["MockedTimeProvider", "SystemTime", "SystemTimeProvider"]
