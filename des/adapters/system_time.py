"""Production implementation of time provider adapter."""

from des.ports.time_provider_port import TimeProvider
from datetime import datetime, timezone


class SystemTimeProvider(TimeProvider):
    """Production implementation of time provider.

    Returns actual system time in UTC.
    """

    def now_utc(self) -> datetime:
        """Get current UTC time.

        Returns:
            Current datetime in UTC timezone
        """
        return datetime.now(timezone.utc)
