"""Tests for CheckRegistry and CheckExecutor.

TDD tests for the pre-flight check infrastructure.
"""

from crafter_ai.installer.domain.check_executor import CheckExecutor
from crafter_ai.installer.domain.check_registry import CheckRegistry
from crafter_ai.installer.domain.check_result import CheckResult, CheckSeverity


# Test constants for expected counts
EXPECTED_COUNT_ZERO = 0
EXPECTED_COUNT_ONE = 1
EXPECTED_COUNT_TWO = 2


# ═══════════════════════════════════════════════════════════════════════════════
# CheckRegistry Tests
# ═══════════════════════════════════════════════════════════════════════════════


class TestCheckRegistry:
    """Tests for CheckRegistry registration and retrieval."""

    def test_register_and_get_check(self):
        """Test that a registered check can be retrieved."""
        registry = CheckRegistry()

        def sample_check() -> CheckResult:
            return CheckResult(
                id="test_check",
                name="Test Check",
                passed=True,
                severity=CheckSeverity.BLOCKING,
                message="Check passed",
            )

        registry.register("test_check", sample_check)
        retrieved = registry.get("test_check")

        assert retrieved is sample_check

    def test_get_returns_none_for_unknown_check_id(self):
        """Test that get returns None for unregistered check_id."""
        registry = CheckRegistry()

        result = registry.get("nonexistent_check")

        assert result is None

    def test_has_returns_true_for_registered_check(self):
        """Test that has returns True for registered check."""
        registry = CheckRegistry()

        def sample_check() -> CheckResult:
            return CheckResult(
                id="test_check",
                name="Test Check",
                passed=True,
                severity=CheckSeverity.BLOCKING,
                message="Check passed",
            )

        registry.register("test_check", sample_check)

        assert registry.has("test_check") is True

    def test_has_returns_false_for_unknown_check(self):
        """Test that has returns False for unregistered check."""
        registry = CheckRegistry()

        assert registry.has("nonexistent_check") is False

    def test_count_returns_number_of_registered_checks(self):
        """Test that count property returns correct count."""
        registry = CheckRegistry()

        def check_one() -> CheckResult:
            return CheckResult(
                id="check_one",
                name="Check One",
                passed=True,
                severity=CheckSeverity.BLOCKING,
                message="OK",
            )

        def check_two() -> CheckResult:
            return CheckResult(
                id="check_two",
                name="Check Two",
                passed=True,
                severity=CheckSeverity.WARNING,
                message="OK",
            )

        assert registry.count == EXPECTED_COUNT_ZERO
        registry.register("check_one", check_one)
        assert registry.count == EXPECTED_COUNT_ONE
        registry.register("check_two", check_two)
        assert registry.count == EXPECTED_COUNT_TWO

    def test_get_all_returns_all_registered_checks(self):
        """Test that get_all returns all check tuples."""
        registry = CheckRegistry()

        def check_one() -> CheckResult:
            return CheckResult(
                id="check_one",
                name="Check One",
                passed=True,
                severity=CheckSeverity.BLOCKING,
                message="OK",
            )

        def check_two() -> CheckResult:
            return CheckResult(
                id="check_two",
                name="Check Two",
                passed=True,
                severity=CheckSeverity.WARNING,
                message="OK",
            )

        registry.register("check_one", check_one)
        registry.register("check_two", check_two)

        all_checks = registry.get_all()

        assert len(all_checks) == EXPECTED_COUNT_TWO
        assert ("check_one", check_one) in all_checks
        assert ("check_two", check_two) in all_checks


# ═══════════════════════════════════════════════════════════════════════════════
# CheckExecutor Tests
# ═══════════════════════════════════════════════════════════════════════════════


class TestCheckExecutor:
    """Tests for CheckExecutor check execution."""

    def test_run_check_executes_single_check(self):
        """Test that run_check executes a single check by ID."""
        registry = CheckRegistry()

        def sample_check() -> CheckResult:
            return CheckResult(
                id="test_check",
                name="Test Check",
                passed=True,
                severity=CheckSeverity.BLOCKING,
                message="Check passed",
            )

        registry.register("test_check", sample_check)
        executor = CheckExecutor(registry)

        result = executor.run_check("test_check")

        assert result.id == "test_check"
        assert result.passed is True
        assert result.message == "Check passed"

    def test_run_all_executes_all_registered_checks(self):
        """Test that run_all executes all checks and returns results."""
        registry = CheckRegistry()

        def check_one() -> CheckResult:
            return CheckResult(
                id="check_one",
                name="Check One",
                passed=True,
                severity=CheckSeverity.BLOCKING,
                message="One passed",
            )

        def check_two() -> CheckResult:
            return CheckResult(
                id="check_two",
                name="Check Two",
                passed=False,
                severity=CheckSeverity.WARNING,
                message="Two failed",
            )

        registry.register("check_one", check_one)
        registry.register("check_two", check_two)
        executor = CheckExecutor(registry)

        results = executor.run_all()

        assert len(results) == EXPECTED_COUNT_TWO
        ids = [r.id for r in results]
        assert "check_one" in ids
        assert "check_two" in ids

    def test_run_blocking_only_filters_by_severity(self):
        """Test that run_blocking_only only runs BLOCKING checks."""
        registry = CheckRegistry()

        def blocking_check() -> CheckResult:
            return CheckResult(
                id="blocking",
                name="Blocking Check",
                passed=True,
                severity=CheckSeverity.BLOCKING,
                message="Blocking OK",
            )

        def warning_check() -> CheckResult:
            return CheckResult(
                id="warning",
                name="Warning Check",
                passed=True,
                severity=CheckSeverity.WARNING,
                message="Warning OK",
            )

        registry.register("blocking", blocking_check)
        registry.register("warning", warning_check)
        executor = CheckExecutor(registry)

        results = executor.run_blocking_only()

        assert len(results) == 1
        assert results[0].id == "blocking"
        assert results[0].severity == CheckSeverity.BLOCKING

    def test_run_check_handles_missing_check_id(self):
        """Test that run_check returns failed CheckResult for missing ID."""
        registry = CheckRegistry()
        executor = CheckExecutor(registry)

        result = executor.run_check("nonexistent")

        assert result.passed is False
        assert result.severity == CheckSeverity.BLOCKING
        assert "not found" in result.message.lower()

    def test_run_check_catches_exceptions(self):
        """Test that exceptions in check functions are caught gracefully."""
        registry = CheckRegistry()

        def failing_check() -> CheckResult:
            raise RuntimeError("Something went wrong")

        registry.register("failing", failing_check)
        executor = CheckExecutor(registry)

        result = executor.run_check("failing")

        assert result.passed is False
        assert result.severity == CheckSeverity.BLOCKING
        assert "Something went wrong" in result.message
