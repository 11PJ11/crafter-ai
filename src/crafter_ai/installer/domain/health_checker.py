"""HealthChecker for running health checks on system components.

This module provides the health checker pattern for monitoring system health.
The checker is injectable (not a singleton) for testability.
"""

from collections.abc import Callable
from datetime import datetime, timezone

from crafter_ai.installer.domain.health_result import HealthResult, HealthStatus


class HealthChecker:
    """Health checker for running health checks on system components.

    The checker stores check functions keyed by component name.
    It is designed to be injectable for testability and flexibility.
    """

    def __init__(self) -> None:
        """Initialize an empty health checker."""
        self._checks: dict[str, Callable[[], HealthResult]] = {}

    def register(self, component: str, check_fn: Callable[[], HealthResult]) -> None:
        """Register a health check function for a component.

        Args:
            component: Name of the component to check.
            check_fn: Callable that returns a HealthResult when executed.
        """
        self._checks[component] = check_fn

    def check(self, component: str) -> HealthResult:
        """Run the health check for a specific component.

        Args:
            component: Name of the component to check.

        Returns:
            HealthResult with the check outcome. Returns UNHEALTHY if
            the component is not registered or if the check raises an exception.
        """
        check_fn = self._checks.get(component)
        if check_fn is None:
            return HealthResult(
                component=component,
                status=HealthStatus.UNHEALTHY,
                message=f"Component '{component}' is not registered",
                details=None,
                timestamp=datetime.now(timezone.utc),
            )

        try:
            return check_fn()
        except Exception as e:
            return HealthResult(
                component=component,
                status=HealthStatus.UNHEALTHY,
                message=f"Health check error: {e}",
                details={"exception_type": type(e).__name__},
                timestamp=datetime.now(timezone.utc),
            )

    def check_all(self) -> list[HealthResult]:
        """Run health checks for all registered components.

        Returns:
            List of HealthResult for all registered components.
        """
        return [self.check(component) for component in self._checks]

    def is_healthy(self) -> bool:
        """Check if all components are healthy.

        Returns:
            True if all registered components return HEALTHY status.
        """
        results = self.check_all()
        return all(r.status == HealthStatus.HEALTHY for r in results)

    def get_unhealthy(self) -> list[HealthResult]:
        """Get all components that are not healthy.

        Returns:
            List of HealthResult for components with DEGRADED or UNHEALTHY status.
        """
        results = self.check_all()
        return [r for r in results if r.status != HealthStatus.HEALTHY]
