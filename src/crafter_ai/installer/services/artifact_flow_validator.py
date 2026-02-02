"""ArtifactFlowValidator for validating artifact consistency across journey stages.

This module provides the ArtifactFlowValidator application service that:
- Validates version consistency across build, install, and doctor stages
- Validates wheel path consistency across preflight, readiness, and install stages
- Validates component counts consistency across wheel validation, doctor, and report stages
- Returns FlowValidationResult with drift detection details

Used by: horizontal coherence tests and cross-journey validation
"""

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class CountData:
    """Immutable data for component counts.

    Attributes:
        agent_count: Number of agents in the package.
        command_count: Number of commands in the package.
        template_count: Number of templates in the package.
    """

    agent_count: int
    command_count: int
    template_count: int


@dataclass
class FlowValidationResult:
    """Result of flow validation across journey stages.

    Attributes:
        consistent: True if all stages have identical values.
        drift_detected: List of stage names where drift was detected.
        expected_value: The expected value (from first stage).
        actual_values: Dict mapping stage names to their actual values.
    """

    consistent: bool
    drift_detected: list[str]
    expected_value: str | Path | CountData
    actual_values: dict[str, str | Path | CountData]


class ArtifactFlowValidator:
    """Application service for validating artifact consistency across journey stages.

    This service:
    - Compares artifact values across multiple journey stages
    - Detects drift where values don't match the expected (first stage) value
    - Reports all stages with drift for debugging and resolution

    The validator uses the first stage's value as the expected value and
    compares all subsequent stages against it.
    """

    def validate_version_consistency(
        self, stages: dict[str, str]
    ) -> FlowValidationResult:
        """Validate that version strings are consistent across all stages.

        Args:
            stages: Dict mapping stage names to version strings.
                   The first stage's value is used as the expected value.

        Returns:
            FlowValidationResult with consistency status and drift details.
        """
        return self._validate_consistency(stages)

    def validate_wheel_path_consistency(
        self, stages: dict[str, Path]
    ) -> FlowValidationResult:
        """Validate that wheel paths are consistent across all stages.

        Args:
            stages: Dict mapping stage names to wheel Paths.
                   The first stage's value is used as the expected value.

        Returns:
            FlowValidationResult with consistency status and drift details.
        """
        return self._validate_consistency(stages)

    def validate_counts_consistency(
        self, stages: dict[str, CountData]
    ) -> FlowValidationResult:
        """Validate that component counts are consistent across all stages.

        Args:
            stages: Dict mapping stage names to CountData instances.
                   The first stage's value is used as the expected value.

        Returns:
            FlowValidationResult with consistency status and drift details.
        """
        return self._validate_consistency(stages)

    def _validate_consistency(
        self, stages: dict[str, str | Path | CountData]
    ) -> FlowValidationResult:
        """Generic validation logic for any artifact type.

        Uses the first stage's value as the expected value and compares
        all subsequent stages against it.

        Args:
            stages: Dict mapping stage names to artifact values.

        Returns:
            FlowValidationResult with consistency status and drift details.
        """
        if not stages:
            return FlowValidationResult(
                consistent=True,
                drift_detected=[],
                expected_value="",
                actual_values={},
            )

        # Get first stage value as expected
        stage_items = list(stages.items())
        _first_stage_name, expected_value = stage_items[0]

        # Check all stages for drift
        drift_detected: list[str] = []
        actual_values: dict[str, str | Path | CountData] = {}

        for stage_name, actual_value in stages.items():
            actual_values[stage_name] = actual_value
            if actual_value != expected_value:
                drift_detected.append(stage_name)

        return FlowValidationResult(
            consistent=len(drift_detected) == 0,
            drift_detected=drift_detected,
            expected_value=expected_value,
            actual_values=actual_values,
        )
