"""Tests for ArtifactFlowValidator.

Tests verify:
- CountData dataclass creation with all fields
- FlowValidationResult dataclass with consistent/drift states
- validate_version_consistency passes when all stages match
- validate_version_consistency detects drift
- validate_wheel_path_consistency passes when all paths match
- validate_wheel_path_consistency detects path drift
- validate_counts_consistency passes when all counts match
- validate_counts_consistency detects count drift
"""

from pathlib import Path

import pytest

from crafter_ai.installer.services.artifact_flow_validator import (
    ArtifactFlowValidator,
    CountData,
    FlowValidationResult,
)


class TestCountData:
    """Tests for CountData dataclass."""

    def test_count_data_has_all_required_fields(self) -> None:
        """CountData should have all required fields."""
        data = CountData(
            agent_count=47,
            command_count=23,
            template_count=12,
        )

        assert data.agent_count == 47
        assert data.command_count == 23
        assert data.template_count == 12

    def test_count_data_is_immutable(self) -> None:
        """CountData should be immutable (frozen)."""
        data = CountData(
            agent_count=47,
            command_count=23,
            template_count=12,
        )

        with pytest.raises(AttributeError):
            data.agent_count = 50  # type: ignore[misc]

    def test_count_data_equality(self) -> None:
        """CountData instances with same values should be equal."""
        data1 = CountData(agent_count=47, command_count=23, template_count=12)
        data2 = CountData(agent_count=47, command_count=23, template_count=12)

        assert data1 == data2

    def test_count_data_inequality(self) -> None:
        """CountData instances with different values should not be equal."""
        data1 = CountData(agent_count=47, command_count=23, template_count=12)
        data2 = CountData(agent_count=50, command_count=23, template_count=12)

        assert data1 != data2


class TestFlowValidationResult:
    """Tests for FlowValidationResult dataclass."""

    def test_flow_validation_result_consistent_state(self) -> None:
        """FlowValidationResult should represent consistent state."""
        result = FlowValidationResult(
            consistent=True,
            drift_detected=[],
            expected_value="1.3.0-dev-20260201-001",
            actual_values={
                "build_summary": "1.3.0-dev-20260201-001",
                "install_preflight": "1.3.0-dev-20260201-001",
            },
        )

        assert result.consistent is True
        assert result.drift_detected == []
        assert result.expected_value == "1.3.0-dev-20260201-001"

    def test_flow_validation_result_drift_state(self) -> None:
        """FlowValidationResult should represent drift state."""
        result = FlowValidationResult(
            consistent=False,
            drift_detected=["install_preflight", "doctor"],
            expected_value="1.3.0-dev-20260201-001",
            actual_values={
                "build_summary": "1.3.0-dev-20260201-001",
                "install_preflight": "1.2.0",
                "doctor": "1.2.0",
            },
        )

        assert result.consistent is False
        assert "install_preflight" in result.drift_detected
        assert "doctor" in result.drift_detected
        assert len(result.drift_detected) == 2

    def test_flow_validation_result_with_path_value(self) -> None:
        """FlowValidationResult should support Path values."""
        wheel_path = Path("dist/nwave-1.3.0.dev20260201001-py3-none-any.whl")
        result = FlowValidationResult(
            consistent=True,
            drift_detected=[],
            expected_value=wheel_path,
            actual_values={
                "preflight": wheel_path,
                "readiness": wheel_path,
            },
        )

        assert result.expected_value == wheel_path
        assert result.actual_values["preflight"] == wheel_path

    def test_flow_validation_result_with_count_data_value(self) -> None:
        """FlowValidationResult should support CountData values."""
        counts = CountData(agent_count=47, command_count=23, template_count=12)
        result = FlowValidationResult(
            consistent=True,
            drift_detected=[],
            expected_value=counts,
            actual_values={
                "wheel_validation": counts,
                "doctor": counts,
            },
        )

        assert result.expected_value == counts
        assert result.actual_values["wheel_validation"] == counts


class TestArtifactFlowValidatorVersionConsistency:
    """Tests for validate_version_consistency method."""

    @pytest.fixture
    def validator(self) -> ArtifactFlowValidator:
        """Create an ArtifactFlowValidator instance."""
        return ArtifactFlowValidator()

    def test_validate_version_consistency_passes_when_all_stages_match(
        self, validator: ArtifactFlowValidator
    ) -> None:
        """validate_version_consistency should pass when all stages match."""
        stages = {
            "build_summary": "1.3.0-dev-20260201-001",
            "install_preflight": "1.3.0-dev-20260201-001",
            "release_readiness": "1.3.0-dev-20260201-001",
            "doctor": "1.3.0-dev-20260201-001",
            "report": "1.3.0-dev-20260201-001",
        }

        result = validator.validate_version_consistency(stages)

        assert result.consistent is True
        assert result.drift_detected == []

    def test_validate_version_consistency_detects_single_drift(
        self, validator: ArtifactFlowValidator
    ) -> None:
        """validate_version_consistency should detect single stage drift."""
        stages = {
            "build_summary": "1.3.0-dev-20260201-001",
            "install_preflight": "1.3.0-dev-20260201-001",
            "release_readiness": "1.2.0",  # Drift here
            "doctor": "1.3.0-dev-20260201-001",
            "report": "1.3.0-dev-20260201-001",
        }

        result = validator.validate_version_consistency(stages)

        assert result.consistent is False
        assert "release_readiness" in result.drift_detected
        assert len(result.drift_detected) == 1

    def test_validate_version_consistency_detects_multiple_drifts(
        self, validator: ArtifactFlowValidator
    ) -> None:
        """validate_version_consistency should detect multiple stage drifts."""
        stages = {
            "build_summary": "1.3.0-dev-20260201-001",
            "install_preflight": "1.2.0",  # Drift
            "release_readiness": "1.1.0",  # Drift
            "doctor": "1.3.0-dev-20260201-001",
            "report": "1.0.0",  # Drift
        }

        result = validator.validate_version_consistency(stages)

        assert result.consistent is False
        assert "install_preflight" in result.drift_detected
        assert "release_readiness" in result.drift_detected
        assert "report" in result.drift_detected
        assert len(result.drift_detected) == 3

    def test_validate_version_consistency_uses_first_stage_as_expected(
        self, validator: ArtifactFlowValidator
    ) -> None:
        """validate_version_consistency should use first stage value as expected."""
        stages = {
            "build_summary": "1.3.0-dev-20260201-001",
            "install_preflight": "1.3.0-dev-20260201-001",
        }

        result = validator.validate_version_consistency(stages)

        assert result.expected_value == "1.3.0-dev-20260201-001"

    def test_validate_version_consistency_stores_all_actual_values(
        self, validator: ArtifactFlowValidator
    ) -> None:
        """validate_version_consistency should store all actual values."""
        stages = {
            "build_summary": "1.3.0-dev-20260201-001",
            "install_preflight": "1.2.0",
        }

        result = validator.validate_version_consistency(stages)

        assert "build_summary" in result.actual_values
        assert "install_preflight" in result.actual_values
        assert result.actual_values["install_preflight"] == "1.2.0"


class TestArtifactFlowValidatorWheelPathConsistency:
    """Tests for validate_wheel_path_consistency method."""

    @pytest.fixture
    def validator(self) -> ArtifactFlowValidator:
        """Create an ArtifactFlowValidator instance."""
        return ArtifactFlowValidator()

    @pytest.fixture
    def expected_wheel_path(self) -> Path:
        """Standard wheel path for testing."""
        return Path("dist/nwave-1.3.0.dev20260201001-py3-none-any.whl")

    def test_validate_wheel_path_consistency_passes_when_all_paths_match(
        self, validator: ArtifactFlowValidator, expected_wheel_path: Path
    ) -> None:
        """validate_wheel_path_consistency should pass when all paths match."""
        stages = {
            "preflight": expected_wheel_path,
            "readiness": expected_wheel_path,
            "install_command": expected_wheel_path,
            "report": expected_wheel_path,
        }

        result = validator.validate_wheel_path_consistency(stages)

        assert result.consistent is True
        assert result.drift_detected == []

    def test_validate_wheel_path_consistency_detects_path_drift(
        self, validator: ArtifactFlowValidator, expected_wheel_path: Path
    ) -> None:
        """validate_wheel_path_consistency should detect path drift."""
        stages = {
            "preflight": expected_wheel_path,
            "readiness": expected_wheel_path,
            "install_command": Path("dist/wrong-wheel.whl"),  # Drift
            "report": expected_wheel_path,
        }

        result = validator.validate_wheel_path_consistency(stages)

        assert result.consistent is False
        assert "install_command" in result.drift_detected

    def test_validate_wheel_path_consistency_detects_multiple_path_drifts(
        self, validator: ArtifactFlowValidator, expected_wheel_path: Path
    ) -> None:
        """validate_wheel_path_consistency should detect multiple path drifts."""
        stages = {
            "preflight": expected_wheel_path,
            "readiness": Path("dist/wrong1.whl"),  # Drift
            "install_command": Path("dist/wrong2.whl"),  # Drift
            "report": expected_wheel_path,
        }

        result = validator.validate_wheel_path_consistency(stages)

        assert result.consistent is False
        assert "readiness" in result.drift_detected
        assert "install_command" in result.drift_detected
        assert len(result.drift_detected) == 2

    def test_validate_wheel_path_consistency_uses_first_stage_as_expected(
        self, validator: ArtifactFlowValidator, expected_wheel_path: Path
    ) -> None:
        """validate_wheel_path_consistency should use first stage path as expected."""
        stages = {
            "preflight": expected_wheel_path,
            "readiness": expected_wheel_path,
        }

        result = validator.validate_wheel_path_consistency(stages)

        assert result.expected_value == expected_wheel_path

    def test_validate_wheel_path_consistency_stores_all_actual_values(
        self, validator: ArtifactFlowValidator, expected_wheel_path: Path
    ) -> None:
        """validate_wheel_path_consistency should store all actual values."""
        wrong_path = Path("dist/wrong.whl")
        stages = {
            "preflight": expected_wheel_path,
            "readiness": wrong_path,
        }

        result = validator.validate_wheel_path_consistency(stages)

        assert "preflight" in result.actual_values
        assert "readiness" in result.actual_values
        assert result.actual_values["readiness"] == wrong_path


class TestArtifactFlowValidatorCountsConsistency:
    """Tests for validate_counts_consistency method."""

    @pytest.fixture
    def validator(self) -> ArtifactFlowValidator:
        """Create an ArtifactFlowValidator instance."""
        return ArtifactFlowValidator()

    @pytest.fixture
    def expected_counts(self) -> CountData:
        """Standard counts for testing."""
        return CountData(agent_count=47, command_count=23, template_count=12)

    def test_validate_counts_consistency_passes_when_all_counts_match(
        self, validator: ArtifactFlowValidator, expected_counts: CountData
    ) -> None:
        """validate_counts_consistency should pass when all counts match."""
        stages = {
            "wheel_validation": expected_counts,
            "doctor": expected_counts,
            "release_report": expected_counts,
        }

        result = validator.validate_counts_consistency(stages)

        assert result.consistent is True
        assert result.drift_detected == []

    def test_validate_counts_consistency_detects_agent_count_drift(
        self, validator: ArtifactFlowValidator, expected_counts: CountData
    ) -> None:
        """validate_counts_consistency should detect agent count drift."""
        wrong_counts = CountData(agent_count=50, command_count=23, template_count=12)
        stages = {
            "wheel_validation": expected_counts,
            "doctor": wrong_counts,  # Agent count drift
            "release_report": expected_counts,
        }

        result = validator.validate_counts_consistency(stages)

        assert result.consistent is False
        assert "doctor" in result.drift_detected

    def test_validate_counts_consistency_detects_command_count_drift(
        self, validator: ArtifactFlowValidator, expected_counts: CountData
    ) -> None:
        """validate_counts_consistency should detect command count drift."""
        wrong_counts = CountData(agent_count=47, command_count=30, template_count=12)
        stages = {
            "wheel_validation": expected_counts,
            "doctor": expected_counts,
            "release_report": wrong_counts,  # Command count drift
        }

        result = validator.validate_counts_consistency(stages)

        assert result.consistent is False
        assert "release_report" in result.drift_detected

    def test_validate_counts_consistency_detects_template_count_drift(
        self, validator: ArtifactFlowValidator, expected_counts: CountData
    ) -> None:
        """validate_counts_consistency should detect template count drift."""
        wrong_counts = CountData(agent_count=47, command_count=23, template_count=15)
        stages = {
            "wheel_validation": expected_counts,
            "doctor": wrong_counts,  # Template count drift
        }

        result = validator.validate_counts_consistency(stages)

        assert result.consistent is False
        assert "doctor" in result.drift_detected

    def test_validate_counts_consistency_detects_multiple_count_drifts(
        self, validator: ArtifactFlowValidator, expected_counts: CountData
    ) -> None:
        """validate_counts_consistency should detect multiple count drifts."""
        wrong_counts1 = CountData(agent_count=50, command_count=23, template_count=12)
        wrong_counts2 = CountData(agent_count=45, command_count=20, template_count=10)
        stages = {
            "wheel_validation": expected_counts,
            "doctor": wrong_counts1,  # Drift
            "release_report": wrong_counts2,  # Drift
        }

        result = validator.validate_counts_consistency(stages)

        assert result.consistent is False
        assert "doctor" in result.drift_detected
        assert "release_report" in result.drift_detected
        assert len(result.drift_detected) == 2

    def test_validate_counts_consistency_uses_first_stage_as_expected(
        self, validator: ArtifactFlowValidator, expected_counts: CountData
    ) -> None:
        """validate_counts_consistency should use first stage counts as expected."""
        stages = {
            "wheel_validation": expected_counts,
            "doctor": expected_counts,
        }

        result = validator.validate_counts_consistency(stages)

        assert result.expected_value == expected_counts

    def test_validate_counts_consistency_stores_all_actual_values(
        self, validator: ArtifactFlowValidator, expected_counts: CountData
    ) -> None:
        """validate_counts_consistency should store all actual values."""
        wrong_counts = CountData(agent_count=50, command_count=23, template_count=12)
        stages = {
            "wheel_validation": expected_counts,
            "doctor": wrong_counts,
        }

        result = validator.validate_counts_consistency(stages)

        assert "wheel_validation" in result.actual_values
        assert "doctor" in result.actual_values
        assert result.actual_values["doctor"] == wrong_counts


class TestArtifactFlowValidatorIntegration:
    """Integration tests for ArtifactFlowValidator."""

    def test_full_validation_workflow_all_consistent(self) -> None:
        """Test complete validation workflow with all consistent data."""
        validator = ArtifactFlowValidator()

        # Version consistency
        version_stages = {
            "build_summary": "1.3.0-dev-20260201-001",
            "install_preflight": "1.3.0-dev-20260201-001",
            "doctor": "1.3.0-dev-20260201-001",
        }
        version_result = validator.validate_version_consistency(version_stages)
        assert version_result.consistent is True

        # Wheel path consistency
        wheel_path = Path("dist/nwave-1.3.0.dev20260201001-py3-none-any.whl")
        path_stages = {
            "preflight": wheel_path,
            "readiness": wheel_path,
            "install_command": wheel_path,
        }
        path_result = validator.validate_wheel_path_consistency(path_stages)
        assert path_result.consistent is True

        # Counts consistency
        counts = CountData(agent_count=47, command_count=23, template_count=12)
        count_stages = {
            "wheel_validation": counts,
            "doctor": counts,
            "release_report": counts,
        }
        count_result = validator.validate_counts_consistency(count_stages)
        assert count_result.consistent is True

    def test_full_validation_workflow_with_drift(self) -> None:
        """Test complete validation workflow detecting drift."""
        validator = ArtifactFlowValidator()

        # Version with drift
        version_stages = {
            "build_summary": "1.3.0-dev-20260201-001",
            "install_preflight": "1.2.0",  # Drift
        }
        version_result = validator.validate_version_consistency(version_stages)
        assert version_result.consistent is False
        assert "install_preflight" in version_result.drift_detected

        # Wheel path with drift
        wheel_path = Path("dist/nwave-1.3.0.dev20260201001-py3-none-any.whl")
        path_stages = {
            "preflight": wheel_path,
            "install_command": Path("dist/wrong.whl"),  # Drift
        }
        path_result = validator.validate_wheel_path_consistency(path_stages)
        assert path_result.consistent is False
        assert "install_command" in path_result.drift_detected

        # Counts with drift
        expected_counts = CountData(agent_count=47, command_count=23, template_count=12)
        wrong_counts = CountData(agent_count=45, command_count=20, template_count=10)
        count_stages = {
            "wheel_validation": expected_counts,
            "doctor": wrong_counts,  # Drift
        }
        count_result = validator.validate_counts_consistency(count_stages)
        assert count_result.consistent is False
        assert "doctor" in count_result.drift_detected
