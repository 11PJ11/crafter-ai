"""Tests for DoctorFormatValidator.

Tests verify:
- ValidationResult dataclass creation with all fields
- validate_table_format returns consistent for identical formats
- validate_check_order verifies 7 checks in correct sequence
- validate_status_terminology verifies HEALTHY/WARNING/UNHEALTHY
- get_formatted_output produces identical format for Journey 2 and 3
- Component display format is identical
- Version display format is identical
"""

from dataclasses import FrozenInstanceError
from datetime import datetime

import pytest

from crafter_ai.installer.domain.health_result import HealthResult, HealthStatus
from crafter_ai.installer.services.doctor_format_validator import (
    DoctorFormatValidator,
    DoctorValidationResult,
)


class TestDoctorValidationResult:
    """Tests for DoctorValidationResult dataclass."""

    def test_validation_result_has_all_required_fields(self) -> None:
        """DoctorValidationResult should have all required fields."""
        result = DoctorValidationResult(
            consistent=True,
            inconsistencies=[],
            journey_outputs={
                "forge:install-local-candidate": [
                    "Check  Status",
                    "Core installation [check] ~/.claude/agents/nw/",
                ],
                "pipx install nwave": [
                    "Check  Status",
                    "Core installation [check] ~/.claude/agents/nw/",
                ],
            },
        )

        assert result.consistent is True
        assert result.inconsistencies == []
        assert len(result.journey_outputs) == 2

    def test_validation_result_with_inconsistencies(self) -> None:
        """DoctorValidationResult should store inconsistency details."""
        result = DoctorValidationResult(
            consistent=False,
            inconsistencies=["Check order differs between journeys"],
            journey_outputs={},
        )

        assert result.consistent is False
        assert len(result.inconsistencies) == 1
        assert "Check order" in result.inconsistencies[0]

    def test_validation_result_is_immutable(self) -> None:
        """DoctorValidationResult should be immutable (frozen)."""
        result = DoctorValidationResult(
            consistent=True,
            inconsistencies=[],
            journey_outputs={},
        )

        with pytest.raises(FrozenInstanceError):
            result.consistent = False  # type: ignore[misc]


class TestDoctorFormatValidatorCheckOrder:
    """Tests for validate_check_order method."""

    @pytest.fixture
    def validator(self) -> DoctorFormatValidator:
        """Create a DoctorFormatValidator instance."""
        return DoctorFormatValidator()

    @pytest.fixture
    def health_results_correct_order(self) -> list[HealthResult]:
        """Create health results in correct order."""
        now = datetime.now()
        return [
            HealthResult(
                component="Core installation",
                status=HealthStatus.HEALTHY,
                message="~/.claude/agents/nw/",
                details=None,
                timestamp=now,
            ),
            HealthResult(
                component="Agent files",
                status=HealthStatus.HEALTHY,
                message="47 OK",
                details=None,
                timestamp=now,
            ),
            HealthResult(
                component="Command files",
                status=HealthStatus.HEALTHY,
                message="23 OK",
                details=None,
                timestamp=now,
            ),
            HealthResult(
                component="Template files",
                status=HealthStatus.HEALTHY,
                message="12 OK",
                details=None,
                timestamp=now,
            ),
            HealthResult(
                component="Config valid",
                status=HealthStatus.HEALTHY,
                message="OK",
                details=None,
                timestamp=now,
            ),
            HealthResult(
                component="Permissions",
                status=HealthStatus.HEALTHY,
                message="OK",
                details=None,
                timestamp=now,
            ),
            HealthResult(
                component="Version match",
                status=HealthStatus.HEALTHY,
                message="1.3.0",
                details=None,
                timestamp=now,
            ),
        ]

    def test_validate_check_order_returns_consistent_for_correct_order(
        self,
        validator: DoctorFormatValidator,
        health_results_correct_order: list[HealthResult],
    ) -> None:
        """validate_check_order should return consistent for correct order."""
        result = validator.validate_check_order(health_results_correct_order)

        assert result.consistent is True
        assert result.inconsistencies == []

    def test_validate_check_order_verifies_7_checks_in_sequence(
        self,
        validator: DoctorFormatValidator,
        health_results_correct_order: list[HealthResult],
    ) -> None:
        """validate_check_order should verify 7 checks in correct sequence."""
        result = validator.validate_check_order(health_results_correct_order)

        assert result.consistent is True
        # Verify we have exactly 7 checks
        assert len(health_results_correct_order) == 7

    def test_validate_check_order_returns_inconsistent_for_wrong_order(
        self,
        validator: DoctorFormatValidator,
    ) -> None:
        """validate_check_order should return inconsistent for wrong order."""
        now = datetime.now()
        # Wrong order: Agent files before Core installation
        wrong_order_results = [
            HealthResult(
                component="Agent files",
                status=HealthStatus.HEALTHY,
                message="47 OK",
                details=None,
                timestamp=now,
            ),
            HealthResult(
                component="Core installation",
                status=HealthStatus.HEALTHY,
                message="~/.claude/agents/nw/",
                details=None,
                timestamp=now,
            ),
        ]

        result = validator.validate_check_order(wrong_order_results)

        assert result.consistent is False
        assert len(result.inconsistencies) > 0

    def test_validate_check_order_expected_sequence(
        self,
        validator: DoctorFormatValidator,
    ) -> None:
        """validate_check_order should expect specific sequence."""
        expected_order = [
            "Core installation",
            "Agent files",
            "Command files",
            "Template files",
            "Config valid",
            "Permissions",
            "Version match",
        ]

        assert expected_order == validator.EXPECTED_CHECK_ORDER


class TestDoctorFormatValidatorStatusTerminology:
    """Tests for validate_status_terminology method."""

    @pytest.fixture
    def validator(self) -> DoctorFormatValidator:
        """Create a DoctorFormatValidator instance."""
        return DoctorFormatValidator()

    def test_validate_status_terminology_healthy_is_valid(
        self,
        validator: DoctorFormatValidator,
    ) -> None:
        """validate_status_terminology should accept HEALTHY status."""
        now = datetime.now()
        results = [
            HealthResult(
                component="Core installation",
                status=HealthStatus.HEALTHY,
                message="OK",
                details=None,
                timestamp=now,
            ),
        ]

        result = validator.validate_status_terminology(results)

        assert result.consistent is True

    def test_validate_status_terminology_unhealthy_is_valid(
        self,
        validator: DoctorFormatValidator,
    ) -> None:
        """validate_status_terminology should accept UNHEALTHY status."""
        now = datetime.now()
        results = [
            HealthResult(
                component="Core installation",
                status=HealthStatus.UNHEALTHY,
                message="Not found",
                details=None,
                timestamp=now,
            ),
        ]

        result = validator.validate_status_terminology(results)

        assert result.consistent is True

    def test_validate_status_terminology_degraded_maps_to_warning(
        self,
        validator: DoctorFormatValidator,
    ) -> None:
        """validate_status_terminology should map DEGRADED to WARNING display."""
        now = datetime.now()
        results = [
            HealthResult(
                component="Permissions",
                status=HealthStatus.DEGRADED,
                message="Some files have issues",
                details=None,
                timestamp=now,
            ),
        ]

        result = validator.validate_status_terminology(results)

        assert result.consistent is True
        # Check output contains WARNING terminology
        for journey, lines in result.journey_outputs.items():
            output_text = "\n".join(lines)
            # DEGRADED should be displayed as WARNING
            assert "WARNING" in output_text or "[!]" in output_text

    def test_validate_status_terminology_uses_correct_icons(
        self,
        validator: DoctorFormatValidator,
    ) -> None:
        """validate_status_terminology should use correct icons for each status."""
        assert validator.ICON_HEALTHY == "[check]"
        assert validator.ICON_WARNING == "[!]"
        assert validator.ICON_UNHEALTHY == "[x]"


class TestDoctorFormatValidatorTableFormat:
    """Tests for validate_table_format method."""

    @pytest.fixture
    def validator(self) -> DoctorFormatValidator:
        """Create a DoctorFormatValidator instance."""
        return DoctorFormatValidator()

    @pytest.fixture
    def standard_health_results(self) -> list[HealthResult]:
        """Create standard health results for testing."""
        now = datetime.now()
        return [
            HealthResult(
                component="Core installation",
                status=HealthStatus.HEALTHY,
                message="~/.claude/agents/nw/",
                details=None,
                timestamp=now,
            ),
            HealthResult(
                component="Agent files",
                status=HealthStatus.HEALTHY,
                message="47 OK",
                details=None,
                timestamp=now,
            ),
        ]

    def test_validate_table_format_returns_consistent_for_identical_formats(
        self,
        validator: DoctorFormatValidator,
        standard_health_results: list[HealthResult],
    ) -> None:
        """validate_table_format should return consistent for identical formats."""
        result = validator.validate_table_format(standard_health_results)

        assert result.consistent is True
        assert result.inconsistencies == []

    def test_validate_table_format_generates_output_for_both_journeys(
        self,
        validator: DoctorFormatValidator,
        standard_health_results: list[HealthResult],
    ) -> None:
        """validate_table_format should generate output for Journey 2 and 3."""
        result = validator.validate_table_format(standard_health_results)

        assert "forge:install-local-candidate" in result.journey_outputs
        assert "pipx install nwave" in result.journey_outputs

    def test_validate_table_format_outputs_are_identical(
        self,
        validator: DoctorFormatValidator,
        standard_health_results: list[HealthResult],
    ) -> None:
        """validate_table_format outputs should be identical for both journeys."""
        result = validator.validate_table_format(standard_health_results)

        journey2_output = result.journey_outputs["forge:install-local-candidate"]
        journey3_output = result.journey_outputs["pipx install nwave"]

        assert journey2_output == journey3_output


class TestDoctorFormatValidatorFormattedOutput:
    """Tests for get_formatted_output method."""

    @pytest.fixture
    def validator(self) -> DoctorFormatValidator:
        """Create a DoctorFormatValidator instance."""
        return DoctorFormatValidator()

    def test_get_formatted_output_produces_identical_format_for_journey_2(
        self,
        validator: DoctorFormatValidator,
    ) -> None:
        """get_formatted_output should produce consistent format for Journey 2."""
        now = datetime.now()
        results = [
            HealthResult(
                component="Agent files",
                status=HealthStatus.HEALTHY,
                message="47 OK",
                details=None,
                timestamp=now,
            ),
        ]

        output = validator.get_formatted_output(
            results, "forge:install-local-candidate"
        )

        assert isinstance(output, list)
        assert len(output) > 0

    def test_get_formatted_output_produces_identical_format_for_journey_3(
        self,
        validator: DoctorFormatValidator,
    ) -> None:
        """get_formatted_output should produce consistent format for Journey 3."""
        now = datetime.now()
        results = [
            HealthResult(
                component="Agent files",
                status=HealthStatus.HEALTHY,
                message="47 OK",
                details=None,
                timestamp=now,
            ),
        ]

        output = validator.get_formatted_output(results, "pipx install nwave")

        assert isinstance(output, list)
        assert len(output) > 0

    def test_get_formatted_output_identical_across_journeys(
        self,
        validator: DoctorFormatValidator,
    ) -> None:
        """get_formatted_output should produce identical format across journeys."""
        now = datetime.now()
        results = [
            HealthResult(
                component="Agent files",
                status=HealthStatus.HEALTHY,
                message="47 OK",
                details=None,
                timestamp=now,
            ),
        ]

        journeys = [
            "forge:install-local-candidate",
            "pipx install nwave",
        ]

        outputs = [
            validator.get_formatted_output(results, journey) for journey in journeys
        ]

        assert outputs[0] == outputs[1]

    def test_get_formatted_output_component_display_format(
        self,
        validator: DoctorFormatValidator,
    ) -> None:
        """get_formatted_output should format components as '{name} {icon} {message}'."""
        now = datetime.now()
        results = [
            HealthResult(
                component="Agent files",
                status=HealthStatus.HEALTHY,
                message="47 OK",
                details=None,
                timestamp=now,
            ),
        ]

        output = validator.get_formatted_output(
            results, "forge:install-local-candidate"
        )
        output_text = "\n".join(output)

        assert "Agent files" in output_text
        assert "[check]" in output_text
        assert "47 OK" in output_text

    def test_get_formatted_output_version_display_format(
        self,
        validator: DoctorFormatValidator,
    ) -> None:
        """get_formatted_output should format version check correctly."""
        now = datetime.now()
        results = [
            HealthResult(
                component="Version match",
                status=HealthStatus.HEALTHY,
                message="1.3.0",
                details=None,
                timestamp=now,
            ),
        ]

        output = validator.get_formatted_output(
            results, "forge:install-local-candidate"
        )
        output_text = "\n".join(output)

        assert "Version match" in output_text
        assert "[check]" in output_text
        assert "1.3.0" in output_text

    def test_get_formatted_output_install_path_display_format(
        self,
        validator: DoctorFormatValidator,
    ) -> None:
        """get_formatted_output should format install path correctly."""
        now = datetime.now()
        results = [
            HealthResult(
                component="Core installation",
                status=HealthStatus.HEALTHY,
                message="~/.claude/agents/nw/",
                details=None,
                timestamp=now,
            ),
        ]

        output = validator.get_formatted_output(
            results, "forge:install-local-candidate"
        )
        output_text = "\n".join(output)

        assert "Core installation" in output_text
        assert "[check]" in output_text
        assert "~/.claude/agents/nw/" in output_text


class TestDoctorFormatValidatorIntegration:
    """Integration tests for DoctorFormatValidator."""

    def test_full_validation_workflow_with_healthy_checks(self) -> None:
        """Test complete validation workflow with healthy checks."""
        validator = DoctorFormatValidator()
        now = datetime.now()

        results = [
            HealthResult(
                component="Core installation",
                status=HealthStatus.HEALTHY,
                message="~/.claude/agents/nw/",
                details=None,
                timestamp=now,
            ),
            HealthResult(
                component="Agent files",
                status=HealthStatus.HEALTHY,
                message="47 OK",
                details=None,
                timestamp=now,
            ),
            HealthResult(
                component="Command files",
                status=HealthStatus.HEALTHY,
                message="23 OK",
                details=None,
                timestamp=now,
            ),
            HealthResult(
                component="Template files",
                status=HealthStatus.HEALTHY,
                message="12 OK",
                details=None,
                timestamp=now,
            ),
            HealthResult(
                component="Config valid",
                status=HealthStatus.HEALTHY,
                message="OK",
                details=None,
                timestamp=now,
            ),
            HealthResult(
                component="Permissions",
                status=HealthStatus.HEALTHY,
                message="OK",
                details=None,
                timestamp=now,
            ),
            HealthResult(
                component="Version match",
                status=HealthStatus.HEALTHY,
                message="1.3.0",
                details=None,
                timestamp=now,
            ),
        ]

        # Validate table format
        table_result = validator.validate_table_format(results)
        assert table_result.consistent is True

        # Validate check order
        order_result = validator.validate_check_order(results)
        assert order_result.consistent is True

        # Validate status terminology
        status_result = validator.validate_status_terminology(results)
        assert status_result.consistent is True

        # Get formatted output for both journeys
        journeys = [
            "forge:install-local-candidate",
            "pipx install nwave",
        ]

        outputs = [
            validator.get_formatted_output(results, journey) for journey in journeys
        ]

        # All outputs should be identical
        assert outputs[0] == outputs[1]

    def test_full_validation_workflow_with_unhealthy_checks(self) -> None:
        """Test complete validation workflow with unhealthy checks."""
        validator = DoctorFormatValidator()
        now = datetime.now()

        results = [
            HealthResult(
                component="Core installation",
                status=HealthStatus.UNHEALTHY,
                message="Not found",
                details=None,
                timestamp=now,
            ),
        ]

        # Validate table format
        table_result = validator.validate_table_format(results)
        assert table_result.consistent is True

        # Get formatted output for both journeys
        journeys = [
            "forge:install-local-candidate",
            "pipx install nwave",
        ]

        outputs = [
            validator.get_formatted_output(results, journey) for journey in journeys
        ]

        # Error format should be identical across all journeys
        assert outputs[0] == outputs[1]

        # Should contain unhealthy icon
        output_text = "\n".join(outputs[0])
        assert "[x]" in output_text
