"""Time provider driven adapters."""

from src.des.adapters.driven.time.system_time import SystemTimeProvider
from src.des.adapters.driven.time.mocked_time import MockedTimeProvider

# Backward compatibility alias
SystemTime = SystemTimeProvider

__all__ = ["SystemTimeProvider", "SystemTime", "MockedTimeProvider"]
