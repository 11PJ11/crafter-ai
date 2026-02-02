"""CheckExecutor for running pre-flight checks and collecting results.

This module provides the application service for orchestrating check execution.
It uses the CheckRegistry to retrieve and run checks.
"""

from crafter_ai.installer.domain.check_registry import CheckRegistry
from crafter_ai.installer.domain.check_result import CheckResult, CheckSeverity


class CheckExecutor:
    """Executor for running pre-flight checks and collecting results.

    This service orchestrates the execution of checks registered in a CheckRegistry.
    It handles error cases gracefully and provides filtering capabilities.
    """

    def __init__(self, registry: CheckRegistry) -> None:
        """Initialize the executor with a check registry.

        Args:
            registry: The CheckRegistry containing check definitions.
        """
        self._registry = registry

    def run_check(self, check_id: str) -> CheckResult:
        """Run a single check by its ID.

        Args:
            check_id: The ID of the check to run.

        Returns:
            CheckResult from the check, or a failed result if check not found
            or an exception occurred.
        """
        check_fn = self._registry.get(check_id)

        if check_fn is None:
            return CheckResult(
                id=check_id,
                name=f"Unknown Check: {check_id}",
                passed=False,
                severity=CheckSeverity.BLOCKING,
                message=f"Check '{check_id}' not found in registry",
            )

        try:
            return check_fn()
        except Exception as e:
            return CheckResult(
                id=check_id,
                name=f"Failed Check: {check_id}",
                passed=False,
                severity=CheckSeverity.BLOCKING,
                message=f"Check '{check_id}' raised an exception: {e}",
            )

    def run_all(self) -> list[CheckResult]:
        """Run all registered checks.

        Returns:
            List of CheckResult objects from all checks.
        """
        results = []
        for check_id, _ in self._registry.get_all():
            results.append(self.run_check(check_id))
        return results

    def run_blocking_only(self) -> list[CheckResult]:
        """Run only checks that would produce BLOCKING results.

        This method runs all checks but filters to only return BLOCKING results.
        Useful for determining if installation can proceed.

        Returns:
            List of CheckResult objects with BLOCKING severity only.
        """
        all_results = self.run_all()
        return [r for r in all_results if r.severity == CheckSeverity.BLOCKING]
