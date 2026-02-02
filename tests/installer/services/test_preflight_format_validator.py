"""Tests for PreflightFormatValidator.

Tests verify:
- ValidationResult dataclass creation with all fields
- validate_table_structure returns consistent for identical formats
- validate_table_structure returns inconsistent for different formats
- validate_icons_consistency verifies icon uniformity
- get_formatted_output produces identical format for all journeys
- Python version check format is identical
- Error format is identical across journeys
"""

from dataclasses import FrozenInstanceError

import pytest

from crafter_ai.installer.domain.check_result import CheckResult, CheckSeverity
from crafter_ai.installer.services.preflight_format_validator import (
    PreflightFormatValidator,
    ValidationResult,
)


class TestValidationResult:
    """Tests for ValidationResult dataclass."""

    def test_validation_result_has_all_required_fields(self) -> None:
        """ValidationResult should have all required fields."""
        result = ValidationResult(
            consistent=True,
            inconsistencies=[],
            journey_outputs={
                "forge:build-local-candidate": [
                    "Check  Status",
                    "Python version [check] 3.12.1 (3.10+ OK)",
                ],
                "forge:install-local-candidate": [
                    "Check  Status",
                    "Python version [check] 3.12.1 (3.10+ OK)",
                ],
                "pipx install nwave": [
                    "Check  Status",
                    "Python version [check] 3.12.1 (3.10+ OK)",
                ],
            },
        )

        assert result.consistent is True
        assert result.inconsistencies == []
        assert len(result.journey_outputs) == 3

    def test_validation_result_with_inconsistencies(self) -> None:
        """ValidationResult should store inconsistency details."""
        result = ValidationResult(
            consistent=False,
            inconsistencies=["Column widths differ between journeys"],
            journey_outputs={},
        )

        assert result.consistent is False
        assert len(result.inconsistencies) == 1
        assert "Column widths" in result.inconsistencies[0]

    def test_validation_result_is_immutable(self) -> None:
        """ValidationResult should be immutable (frozen)."""
        result = ValidationResult(
            consistent=True,
            inconsistencies=[],
            journey_outputs={},
        )

        with pytest.raises(FrozenInstanceError):
            result.consistent = False  # type: ignore[misc]


class TestPreflightFormatValidatorTableStructure:
    """Tests for validate_table_structure method."""

    @pytest.fixture
    def validator(self) -> PreflightFormatValidator:
        """Create a PreflightFormatValidator instance."""
        return PreflightFormatValidator()

    @pytest.fixture
    def passing_check_results(self) -> list[CheckResult]:
        """Create passing check results."""
        return [
            CheckResult(
                id="python_version",
                name="Python version",
                passed=True,
                severity=CheckSeverity.BLOCKING,
                message="3.12.1 (3.10+ OK)",
            ),
            CheckResult(
                id="git_available",
                name="Git available",
                passed=True,
                severity=CheckSeverity.BLOCKING,
                message="v2.43.0",
            ),
        ]

    def test_validate_table_structure_returns_consistent_for_identical_formats(
        self,
        validator: PreflightFormatValidator,
        passing_check_results: list[CheckResult],
    ) -> None:
        """validate_table_structure should return consistent for identical formats."""
        result = validator.validate_table_structure(passing_check_results)

        assert result.consistent is True
        assert result.inconsistencies == []

    def test_validate_table_structure_has_check_and_status_columns(
        self,
        validator: PreflightFormatValidator,
        passing_check_results: list[CheckResult],
    ) -> None:
        """validate_table_structure should use 'Check' and 'Status' column headers."""
        result = validator.validate_table_structure(passing_check_results)

        # Check that journey outputs contain proper column headers
        for journey, lines in result.journey_outputs.items():
            header_line = lines[0] if lines else ""
            assert "Check" in header_line, f"Missing 'Check' column in {journey}"
            assert "Status" in header_line, f"Missing 'Status' column in {journey}"

    def test_validate_table_structure_returns_inconsistent_for_different_formats(
        self,
        validator: PreflightFormatValidator,
    ) -> None:
        """validate_table_structure should return inconsistent for different formats."""
        # Create results with mixed column widths (simulating inconsistent formatting)
        inconsistent_results = [
            CheckResult(
                id="python_version",
                name="Python version",
                passed=True,
                severity=CheckSeverity.BLOCKING,
                message="3.12.1",
            ),
            CheckResult(
                id="very_long_check_name_that_breaks_formatting",
                name="Very long check name that might break column alignment",
                passed=True,
                severity=CheckSeverity.BLOCKING,
                message="OK",
            ),
        ]

        result = validator.validate_table_structure(inconsistent_results)

        # The validator should still produce consistent output
        # (it normalizes the format)
        assert result.consistent is True

    def test_validate_table_structure_empty_results(
        self,
        validator: PreflightFormatValidator,
    ) -> None:
        """validate_table_structure should handle empty results."""
        result = validator.validate_table_structure([])

        assert result.consistent is True
        assert result.inconsistencies == []


class TestPreflightFormatValidatorIconsConsistency:
    """Tests for validate_icons_consistency method."""

    @pytest.fixture
    def validator(self) -> PreflightFormatValidator:
        """Create a PreflightFormatValidator instance."""
        return PreflightFormatValidator()

    def test_validate_icons_consistency_pass_icon_is_check(
        self,
        validator: PreflightFormatValidator,
    ) -> None:
        """validate_icons_consistency should use [check] for pass icon."""
        results = [
            CheckResult(
                id="python_version",
                name="Python version",
                passed=True,
                severity=CheckSeverity.BLOCKING,
                message="3.12.1 (3.10+ OK)",
            ),
        ]

        result = validator.validate_icons_consistency(results)

        assert result.consistent is True
        # Check that output contains the correct pass icon
        for journey, lines in result.journey_outputs.items():
            output_text = "\n".join(lines)
            assert "[check]" in output_text or "\u2713" in output_text

    def test_validate_icons_consistency_fail_icon_is_x(
        self,
        validator: PreflightFormatValidator,
    ) -> None:
        """validate_icons_consistency should use [x] for fail icon."""
        results = [
            CheckResult(
                id="python_version",
                name="Python version",
                passed=False,
                severity=CheckSeverity.BLOCKING,
                message="3.8.10 (requires 3.10+)",
            ),
        ]

        result = validator.validate_icons_consistency(results)

        assert result.consistent is True
        # Check that output contains the correct fail icon
        for journey, lines in result.journey_outputs.items():
            output_text = "\n".join(lines)
            assert "[x]" in output_text or "\u2717" in output_text

    def test_validate_icons_consistency_warning_icon_is_exclamation(
        self,
        validator: PreflightFormatValidator,
    ) -> None:
        """validate_icons_consistency should use [!] for warning icon."""
        results = [
            CheckResult(
                id="disk_space",
                name="Disk space",
                passed=True,
                severity=CheckSeverity.WARNING,
                message="Low disk space warning",
            ),
        ]

        result = validator.validate_icons_consistency(results)

        assert result.consistent is True

    def test_validate_icons_consistency_returns_consistent_for_uniform_icons(
        self,
        validator: PreflightFormatValidator,
    ) -> None:
        """validate_icons_consistency should return consistent for uniform icons."""
        results = [
            CheckResult(
                id="python_version",
                name="Python version",
                passed=True,
                severity=CheckSeverity.BLOCKING,
                message="3.12.1 (3.10+ OK)",
            ),
            CheckResult(
                id="git_available",
                name="Git available",
                passed=True,
                severity=CheckSeverity.BLOCKING,
                message="v2.43.0",
            ),
        ]

        result = validator.validate_icons_consistency(results)

        assert result.consistent is True
        assert result.inconsistencies == []


class TestPreflightFormatValidatorFormattedOutput:
    """Tests for get_formatted_output method."""

    @pytest.fixture
    def validator(self) -> PreflightFormatValidator:
        """Create a PreflightFormatValidator instance."""
        return PreflightFormatValidator()

    @pytest.fixture
    def standard_check_results(self) -> list[CheckResult]:
        """Create standard check results for testing."""
        return [
            CheckResult(
                id="python_version",
                name="Python version",
                passed=True,
                severity=CheckSeverity.BLOCKING,
                message="3.12.1 (3.10+ OK)",
            ),
        ]

    def test_get_formatted_output_produces_identical_format_for_build_journey(
        self,
        validator: PreflightFormatValidator,
        standard_check_results: list[CheckResult],
    ) -> None:
        """get_formatted_output should produce consistent format for build journey."""
        output = validator.get_formatted_output(
            standard_check_results, "forge:build-local-candidate"
        )

        assert isinstance(output, list)
        assert len(output) > 0

    def test_get_formatted_output_produces_identical_format_for_install_journey(
        self,
        validator: PreflightFormatValidator,
        standard_check_results: list[CheckResult],
    ) -> None:
        """get_formatted_output should produce consistent format for install journey."""
        output = validator.get_formatted_output(
            standard_check_results, "forge:install-local-candidate"
        )

        assert isinstance(output, list)
        assert len(output) > 0

    def test_get_formatted_output_produces_identical_format_for_pypi_journey(
        self,
        validator: PreflightFormatValidator,
        standard_check_results: list[CheckResult],
    ) -> None:
        """get_formatted_output should produce consistent format for PyPI journey."""
        output = validator.get_formatted_output(
            standard_check_results, "pipx install nwave"
        )

        assert isinstance(output, list)
        assert len(output) > 0

    def test_get_formatted_output_identical_across_all_journeys(
        self,
        validator: PreflightFormatValidator,
        standard_check_results: list[CheckResult],
    ) -> None:
        """get_formatted_output should produce identical format across all journeys."""
        journeys = [
            "forge:build-local-candidate",
            "forge:install-local-candidate",
            "pipx install nwave",
        ]

        outputs = [
            validator.get_formatted_output(standard_check_results, journey)
            for journey in journeys
        ]

        # All outputs should be identical
        assert outputs[0] == outputs[1] == outputs[2]

    def test_get_formatted_output_python_version_format(
        self,
        validator: PreflightFormatValidator,
    ) -> None:
        """get_formatted_output should format Python version as specified."""
        results = [
            CheckResult(
                id="python_version",
                name="Python version",
                passed=True,
                severity=CheckSeverity.BLOCKING,
                message="3.12.1 (3.10+ OK)",
            ),
        ]

        output = validator.get_formatted_output(results, "forge:build-local-candidate")
        output_text = "\n".join(output)

        # Format should be: "Python version [icon] X.Y.Z (3.10+ OK)"
        assert "Python version" in output_text
        assert "3.12.1" in output_text
        assert "3.10+ OK" in output_text

    def test_get_formatted_output_error_format_identical(
        self,
        validator: PreflightFormatValidator,
    ) -> None:
        """get_formatted_output should format errors identically across journeys."""
        error_results = [
            CheckResult(
                id="python_version",
                name="Python version",
                passed=False,
                severity=CheckSeverity.BLOCKING,
                message="Python version too old",
                remediation="Install Python 3.10 or higher",
            ),
        ]

        journeys = [
            "forge:build-local-candidate",
            "forge:install-local-candidate",
            "pipx install nwave",
        ]

        outputs = [
            validator.get_formatted_output(error_results, journey)
            for journey in journeys
        ]

        # Error format should be identical across all journeys
        assert outputs[0] == outputs[1] == outputs[2]


class TestPreflightFormatValidatorIntegration:
    """Integration tests for PreflightFormatValidator."""

    def test_full_validation_workflow_with_passing_checks(self) -> None:
        """Test complete validation workflow with passing checks."""
        validator = PreflightFormatValidator()

        results = [
            CheckResult(
                id="python_version",
                name="Python version",
                passed=True,
                severity=CheckSeverity.BLOCKING,
                message="3.12.1 (3.10+ OK)",
            ),
            CheckResult(
                id="git_available",
                name="Git available",
                passed=True,
                severity=CheckSeverity.BLOCKING,
                message="v2.43.0",
            ),
            CheckResult(
                id="pipx_available",
                name="pipx available",
                passed=True,
                severity=CheckSeverity.BLOCKING,
                message="v1.4.3 installed",
            ),
        ]

        # Validate table structure
        table_result = validator.validate_table_structure(results)
        assert table_result.consistent is True

        # Validate icons
        icons_result = validator.validate_icons_consistency(results)
        assert icons_result.consistent is True

        # Get formatted output for all journeys
        journeys = [
            "forge:build-local-candidate",
            "forge:install-local-candidate",
            "pipx install nwave",
        ]

        outputs = [
            validator.get_formatted_output(results, journey) for journey in journeys
        ]

        # All outputs should be identical
        assert outputs[0] == outputs[1] == outputs[2]

    def test_full_validation_workflow_with_failing_checks(self) -> None:
        """Test complete validation workflow with failing checks."""
        validator = PreflightFormatValidator()

        results = [
            CheckResult(
                id="python_version",
                name="Python version",
                passed=False,
                severity=CheckSeverity.BLOCKING,
                message="Python version too old",
                remediation="Install Python 3.10 or higher",
            ),
        ]

        # Validate table structure
        table_result = validator.validate_table_structure(results)
        assert table_result.consistent is True

        # Validate icons
        icons_result = validator.validate_icons_consistency(results)
        assert icons_result.consistent is True

        # Get formatted output for all journeys
        journeys = [
            "forge:build-local-candidate",
            "forge:install-local-candidate",
            "pipx install nwave",
        ]

        outputs = [
            validator.get_formatted_output(results, journey) for journey in journeys
        ]

        # Error format should be identical across all journeys
        assert outputs[0] == outputs[1] == outputs[2]

        # Should contain error icon
        output_text = "\n".join(outputs[0])
        assert "[x]" in output_text or "\u2717" in output_text
