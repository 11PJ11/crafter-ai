"""Tests for CheckResult domain object and CheckSeverity enum."""

from dataclasses import FrozenInstanceError

import pytest

from crafter_ai.installer.domain import CheckResult, CheckSeverity


# Test constants
EXPECTED_SEVERITY_COUNT = 2  # BLOCKING and WARNING


class TestCheckSeverity:
    """Tests for CheckSeverity enum."""

    def test_has_blocking_value(self):
        """CheckSeverity has BLOCKING value."""
        assert CheckSeverity.BLOCKING.value == "blocking"

    def test_has_warning_value(self):
        """CheckSeverity has WARNING value."""
        assert CheckSeverity.WARNING.value == "warning"

    def test_only_two_values(self):
        """CheckSeverity has exactly two values."""
        assert len(CheckSeverity) == EXPECTED_SEVERITY_COUNT


class TestCheckResult:
    """Tests for CheckResult dataclass."""

    def test_creation_with_all_properties(self):
        """CheckResult can be created with all properties."""
        result = CheckResult(
            id="python-version",
            name="Python Version Check",
            passed=True,
            severity=CheckSeverity.BLOCKING,
            message="Python 3.10+ detected",
            remediation="Install Python 3.10 or higher",
            fixable=False,
            fix_command=None,
        )

        assert result.id == "python-version"
        assert result.name == "Python Version Check"
        assert result.passed is True
        assert result.severity == CheckSeverity.BLOCKING
        assert result.message == "Python 3.10+ detected"
        assert result.remediation == "Install Python 3.10 or higher"
        assert result.fixable is False
        assert result.fix_command is None

    def test_creation_with_none_optional_fields(self):
        """CheckResult can be created with None optional fields."""
        result = CheckResult(
            id="uv-installed",
            name="UV Installation Check",
            passed=False,
            severity=CheckSeverity.WARNING,
            message="UV not found",
        )

        assert result.id == "uv-installed"
        assert result.remediation is None
        assert result.fixable is False
        assert result.fix_command is None

    def test_creation_with_fixable_check(self):
        """CheckResult can represent a fixable check."""
        result = CheckResult(
            id="uv-installed",
            name="UV Installation Check",
            passed=False,
            severity=CheckSeverity.WARNING,
            message="UV not found",
            remediation="Install UV using pip",
            fixable=True,
            fix_command="pip install uv",
        )

        assert result.fixable is True
        assert result.fix_command == "pip install uv"

    def test_immutability(self):
        """CheckResult is immutable (frozen)."""
        result = CheckResult(
            id="test",
            name="Test Check",
            passed=True,
            severity=CheckSeverity.WARNING,
            message="Test message",
        )

        with pytest.raises(FrozenInstanceError):
            result.passed = False

    def test_equality_same_values(self):
        """CheckResult instances with same values are equal."""
        result1 = CheckResult(
            id="test",
            name="Test Check",
            passed=True,
            severity=CheckSeverity.BLOCKING,
            message="Test message",
        )
        result2 = CheckResult(
            id="test",
            name="Test Check",
            passed=True,
            severity=CheckSeverity.BLOCKING,
            message="Test message",
        )

        assert result1 == result2

    def test_equality_different_values(self):
        """CheckResult instances with different values are not equal."""
        result1 = CheckResult(
            id="test",
            name="Test Check",
            passed=True,
            severity=CheckSeverity.BLOCKING,
            message="Test message",
        )
        result2 = CheckResult(
            id="test",
            name="Test Check",
            passed=False,
            severity=CheckSeverity.BLOCKING,
            message="Test message",
        )

        assert result1 != result2
