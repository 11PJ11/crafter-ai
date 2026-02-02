"""CheckRegistry for storing and retrieving pre-flight check definitions.

This module provides the registry pattern for managing check functions.
The registry is injectable (not a singleton) for testability.
"""

from collections.abc import Callable

from crafter_ai.installer.domain.check_result import CheckResult


class CheckRegistry:
    """Registry for storing and retrieving pre-flight check definitions.

    The registry stores check functions keyed by their unique ID.
    It is designed to be injectable for testability and flexibility.
    """

    def __init__(self) -> None:
        """Initialize an empty registry."""
        self._checks: dict[str, Callable[[], CheckResult]] = {}

    def register(self, check_id: str, check_fn: Callable[[], CheckResult]) -> None:
        """Register a check function with the given ID.

        Args:
            check_id: Unique identifier for the check.
            check_fn: Callable that returns a CheckResult when executed.
        """
        self._checks[check_id] = check_fn

    def get(self, check_id: str) -> Callable[[], CheckResult] | None:
        """Retrieve a check function by its ID.

        Args:
            check_id: The ID of the check to retrieve.

        Returns:
            The check function if found, None otherwise.
        """
        return self._checks.get(check_id)

    def get_all(self) -> list[tuple[str, Callable[[], CheckResult]]]:
        """Retrieve all registered checks.

        Returns:
            List of (check_id, check_fn) tuples for all registered checks.
        """
        return list(self._checks.items())

    def has(self, check_id: str) -> bool:
        """Check if a check is registered with the given ID.

        Args:
            check_id: The ID to check.

        Returns:
            True if a check is registered with this ID, False otherwise.
        """
        return check_id in self._checks

    @property
    def count(self) -> int:
        """Return the number of registered checks."""
        return len(self._checks)
