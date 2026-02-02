"""HealthResult domain object and HealthStatus enum.

This module defines the core domain objects for the health check system.
These are pure domain objects with no external dependencies.
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class HealthStatus(Enum):
    """Health status for a component.

    HEALTHY: Component is fully operational.
    DEGRADED: Component works but with issues.
    UNHEALTHY: Component is not working.
    """

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


@dataclass(frozen=True)
class HealthResult:
    """Immutable result of a health check.

    Attributes:
        component: Name of the component being checked.
        status: Health status of the component.
        message: Status description.
        details: Optional diagnostic details.
        timestamp: When the check was performed.
    """

    component: str
    status: HealthStatus
    message: str
    details: dict[str, str] | None
    timestamp: datetime
