"""Tests for HealthStatus, HealthResult, and HealthChecker.

These tests verify the domain objects for the health check system.
"""

from dataclasses import FrozenInstanceError
from datetime import datetime, timezone

import pytest

from crafter_ai.installer.domain.health_checker import HealthChecker
from crafter_ai.installer.domain.health_result import HealthResult, HealthStatus


# Test constants for expected counts
EXPECTED_HEALTH_STATUS_COUNT = 3
EXPECTED_TWO_COMPONENTS = 2


class TestHealthStatus:
    """Tests for HealthStatus enum."""

    def test_has_healthy_value(self) -> None:
        """HealthStatus should have HEALTHY value."""
        assert HealthStatus.HEALTHY.value == "healthy"

    def test_has_degraded_value(self) -> None:
        """HealthStatus should have DEGRADED value."""
        assert HealthStatus.DEGRADED.value == "degraded"

    def test_has_unhealthy_value(self) -> None:
        """HealthStatus should have UNHEALTHY value."""
        assert HealthStatus.UNHEALTHY.value == "unhealthy"

    def test_has_exactly_three_values(self) -> None:
        """HealthStatus should have exactly three values."""
        assert len(HealthStatus) == EXPECTED_HEALTH_STATUS_COUNT


class TestHealthResult:
    """Tests for HealthResult dataclass."""

    def test_creation_with_all_properties(self) -> None:
        """HealthResult should be created with all properties."""
        timestamp = datetime.now(timezone.utc)
        result = HealthResult(
            component="python",
            status=HealthStatus.HEALTHY,
            message="Python is installed",
            details={"version": "3.12.0"},
            timestamp=timestamp,
        )
        assert result.component == "python"
        assert result.status == HealthStatus.HEALTHY
        assert result.message == "Python is installed"
        assert result.details == {"version": "3.12.0"}
        assert result.timestamp == timestamp

    def test_creation_with_none_details(self) -> None:
        """HealthResult should allow None for optional details field."""
        timestamp = datetime.now(timezone.utc)
        result = HealthResult(
            component="git",
            status=HealthStatus.UNHEALTHY,
            message="Git is not installed",
            details=None,
            timestamp=timestamp,
        )
        assert result.details is None

    def test_is_immutable(self) -> None:
        """HealthResult should be immutable (frozen)."""
        timestamp = datetime.now(timezone.utc)
        result = HealthResult(
            component="python",
            status=HealthStatus.HEALTHY,
            message="Python is installed",
            details=None,
            timestamp=timestamp,
        )
        with pytest.raises(FrozenInstanceError):
            result.component = "other"  # type: ignore[misc]


class TestHealthChecker:
    """Tests for HealthChecker class."""

    def test_register_and_check_component(self) -> None:
        """HealthChecker should register and check a component."""
        checker = HealthChecker()
        timestamp = datetime.now(timezone.utc)

        def check_python() -> HealthResult:
            return HealthResult(
                component="python",
                status=HealthStatus.HEALTHY,
                message="Python is installed",
                details=None,
                timestamp=timestamp,
            )

        checker.register("python", check_python)
        result = checker.check("python")

        assert result.component == "python"
        assert result.status == HealthStatus.HEALTHY

    def test_check_all_returns_all_results(self) -> None:
        """HealthChecker.check_all should return results for all registered components."""
        checker = HealthChecker()
        timestamp = datetime.now(timezone.utc)

        checker.register(
            "python",
            lambda: HealthResult(
                component="python",
                status=HealthStatus.HEALTHY,
                message="OK",
                details=None,
                timestamp=timestamp,
            ),
        )
        checker.register(
            "git",
            lambda: HealthResult(
                component="git",
                status=HealthStatus.DEGRADED,
                message="Old version",
                details=None,
                timestamp=timestamp,
            ),
        )

        results = checker.check_all()

        assert len(results) == EXPECTED_TWO_COMPONENTS
        components = {r.component for r in results}
        assert components == {"python", "git"}

    def test_is_healthy_returns_true_when_all_healthy(self) -> None:
        """HealthChecker.is_healthy should return True when all components are HEALTHY."""
        checker = HealthChecker()
        timestamp = datetime.now(timezone.utc)

        checker.register(
            "python",
            lambda: HealthResult(
                component="python",
                status=HealthStatus.HEALTHY,
                message="OK",
                details=None,
                timestamp=timestamp,
            ),
        )
        checker.register(
            "git",
            lambda: HealthResult(
                component="git",
                status=HealthStatus.HEALTHY,
                message="OK",
                details=None,
                timestamp=timestamp,
            ),
        )

        assert checker.is_healthy() is True

    def test_is_healthy_returns_false_when_any_unhealthy(self) -> None:
        """HealthChecker.is_healthy should return False when any component is UNHEALTHY."""
        checker = HealthChecker()
        timestamp = datetime.now(timezone.utc)

        checker.register(
            "python",
            lambda: HealthResult(
                component="python",
                status=HealthStatus.HEALTHY,
                message="OK",
                details=None,
                timestamp=timestamp,
            ),
        )
        checker.register(
            "git",
            lambda: HealthResult(
                component="git",
                status=HealthStatus.UNHEALTHY,
                message="Not installed",
                details=None,
                timestamp=timestamp,
            ),
        )

        assert checker.is_healthy() is False

    def test_is_healthy_returns_false_when_any_degraded(self) -> None:
        """HealthChecker.is_healthy should return False when any component is DEGRADED."""
        checker = HealthChecker()
        timestamp = datetime.now(timezone.utc)

        checker.register(
            "python",
            lambda: HealthResult(
                component="python",
                status=HealthStatus.HEALTHY,
                message="OK",
                details=None,
                timestamp=timestamp,
            ),
        )
        checker.register(
            "git",
            lambda: HealthResult(
                component="git",
                status=HealthStatus.DEGRADED,
                message="Old version",
                details=None,
                timestamp=timestamp,
            ),
        )

        assert checker.is_healthy() is False

    def test_get_unhealthy_filters_correctly(self) -> None:
        """HealthChecker.get_unhealthy should return only non-HEALTHY components."""
        checker = HealthChecker()
        timestamp = datetime.now(timezone.utc)

        checker.register(
            "python",
            lambda: HealthResult(
                component="python",
                status=HealthStatus.HEALTHY,
                message="OK",
                details=None,
                timestamp=timestamp,
            ),
        )
        checker.register(
            "git",
            lambda: HealthResult(
                component="git",
                status=HealthStatus.DEGRADED,
                message="Old version",
                details=None,
                timestamp=timestamp,
            ),
        )
        checker.register(
            "node",
            lambda: HealthResult(
                component="node",
                status=HealthStatus.UNHEALTHY,
                message="Not installed",
                details=None,
                timestamp=timestamp,
            ),
        )

        unhealthy = checker.get_unhealthy()

        assert len(unhealthy) == EXPECTED_TWO_COMPONENTS
        components = {r.component for r in unhealthy}
        assert components == {"git", "node"}

    def test_check_missing_component_returns_unhealthy(self) -> None:
        """HealthChecker.check should return UNHEALTHY for unregistered component."""
        checker = HealthChecker()
        result = checker.check("nonexistent")

        assert result.component == "nonexistent"
        assert result.status == HealthStatus.UNHEALTHY
        assert "not registered" in result.message.lower()

    def test_check_catches_exception_and_returns_unhealthy(self) -> None:
        """HealthChecker.check should catch exceptions and return UNHEALTHY."""
        checker = HealthChecker()

        def failing_check() -> HealthResult:
            raise RuntimeError("Check failed unexpectedly")

        checker.register("failing", failing_check)
        result = checker.check("failing")

        assert result.component == "failing"
        assert result.status == HealthStatus.UNHEALTHY
        assert (
            "exception" in result.message.lower() or "error" in result.message.lower()
        )
