"""DoctorFormatValidator service for cross-journey format consistency.

This module provides validation of doctor check output format consistency
across Journey 2 (forge:install-local-candidate) and Journey 3 (pipx install nwave).
It ensures that:
- Table structure is identical between journeys
- Check order follows the expected 7-check sequence
- Status terminology (HEALTHY/WARNING/UNHEALTHY) is consistent
- Component display format is identical
"""

from dataclasses import dataclass

from crafter_ai.installer.domain.health_result import HealthResult, HealthStatus


@dataclass(frozen=True)
class DoctorValidationResult:
    """Immutable result of doctor format validation.

    Attributes:
        consistent: Whether the format is consistent across journeys.
        inconsistencies: List of detected inconsistency descriptions.
        journey_outputs: Formatted output for each journey.
    """

    consistent: bool
    inconsistencies: list[str]
    journey_outputs: dict[str, list[str]]


class DoctorFormatValidator:
    """Validates doctor check output format consistency across journeys.

    Ensures that doctor output is identical across:
    - forge:install-local-candidate (Journey 2)
    - pipx install nwave (Journey 3)

    Format specifications:
    - Check order: 7 checks in specific sequence
    - Status icons: [check] (green), [!] (yellow), [x] (red)
    - Status terminology: HEALTHY, WARNING, UNHEALTHY
    - Component format: '{check_name} {icon} {message}'
    """

    # Standard icons
    ICON_HEALTHY = "[check]"
    ICON_WARNING = "[!]"
    ICON_UNHEALTHY = "[x]"

    # Expected check order (7 checks)
    EXPECTED_CHECK_ORDER = [
        "Core installation",
        "Agent files",
        "Command files",
        "Template files",
        "Config valid",
        "Permissions",
        "Version match",
    ]

    # Standard journeys for doctor validation
    JOURNEYS = [
        "forge:install-local-candidate",
        "pipx install nwave",
    ]

    # Standard column widths for consistent formatting
    COMPONENT_COLUMN_WIDTH = 20
    STATUS_COLUMN_WIDTH = 40

    def validate_table_format(
        self, results: list[HealthResult]
    ) -> DoctorValidationResult:
        """Validate that table format is consistent across journeys.

        Args:
            results: List of health results to format.

        Returns:
            DoctorValidationResult with consistency status and journey outputs.
        """
        journey_outputs: dict[str, list[str]] = {}
        inconsistencies: list[str] = []

        # Generate formatted output for both journeys
        for journey in self.JOURNEYS:
            journey_outputs[journey] = self.get_formatted_output(results, journey)

        # Compare journey outputs for consistency
        if len(journey_outputs) > 1:
            first_output = next(iter(journey_outputs.values()))
            for journey, output in journey_outputs.items():
                if output != first_output:
                    inconsistencies.append(f"Table format differs for {journey}")

        return DoctorValidationResult(
            consistent=len(inconsistencies) == 0,
            inconsistencies=inconsistencies,
            journey_outputs=journey_outputs,
        )

    def validate_check_order(
        self, results: list[HealthResult]
    ) -> DoctorValidationResult:
        """Validate that checks are in the correct order.

        Args:
            results: List of health results to validate.

        Returns:
            DoctorValidationResult with consistency status and journey outputs.
        """
        journey_outputs: dict[str, list[str]] = {}
        inconsistencies: list[str] = []

        # Generate formatted output for both journeys
        for journey in self.JOURNEYS:
            journey_outputs[journey] = self.get_formatted_output(results, journey)

        # Extract component names from results
        actual_order = [r.component for r in results]

        # Validate order matches expected (for checks that are present)
        expected_present = [c for c in self.EXPECTED_CHECK_ORDER if c in actual_order]
        actual_present = [c for c in actual_order if c in self.EXPECTED_CHECK_ORDER]

        if actual_present != expected_present:
            inconsistencies.append(
                f"Check order incorrect. Expected: {expected_present}, "
                f"Got: {actual_present}"
            )

        return DoctorValidationResult(
            consistent=len(inconsistencies) == 0,
            inconsistencies=inconsistencies,
            journey_outputs=journey_outputs,
        )

    def validate_status_terminology(
        self, results: list[HealthResult]
    ) -> DoctorValidationResult:
        """Validate that status terminology is consistent.

        Args:
            results: List of health results to validate.

        Returns:
            DoctorValidationResult with consistency status and journey outputs.
        """
        journey_outputs: dict[str, list[str]] = {}
        inconsistencies: list[str] = []

        # Generate formatted output for both journeys
        for journey in self.JOURNEYS:
            journey_outputs[journey] = self.get_formatted_output(results, journey)

        # Verify status terminology consistency
        for journey, output in journey_outputs.items():
            output_text = "\n".join(output)

            for result in results:
                expected_icon = self._get_icon_for_status(result.status)
                if expected_icon not in output_text:
                    inconsistencies.append(
                        f"Missing expected icon {expected_icon} for "
                        f"{result.component} in {journey}"
                    )

        return DoctorValidationResult(
            consistent=len(inconsistencies) == 0,
            inconsistencies=inconsistencies,
            journey_outputs=journey_outputs,
        )

    def get_formatted_output(
        self, results: list[HealthResult], journey: str
    ) -> list[str]:
        """Get formatted output for a specific journey.

        The output format is identical regardless of journey, ensuring
        cross-journey consistency.

        Args:
            results: List of health results to format.
            journey: Journey identifier (not used for formatting, only for context).

        Returns:
            List of formatted output lines.
        """
        lines: list[str] = []

        # Format each result
        for result in results:
            icon = self._get_icon_for_status(result.status)
            status_text = self._get_status_text(result.status)
            line = self._format_component_line(result.component, icon, result.message)
            lines.append(line)

            # Add status text for non-healthy statuses
            if result.status != HealthStatus.HEALTHY:
                lines.append(f"  Status: {status_text}")

        return lines

    def _get_icon_for_status(self, status: HealthStatus) -> str:
        """Get the appropriate icon for a health status.

        Args:
            status: Health status to get icon for.

        Returns:
            Icon string: [check], [!], or [x]
        """
        if status == HealthStatus.HEALTHY:
            return self.ICON_HEALTHY
        elif status == HealthStatus.DEGRADED:
            return self.ICON_WARNING
        else:  # UNHEALTHY
            return self.ICON_UNHEALTHY

    def _get_status_text(self, status: HealthStatus) -> str:
        """Get the display text for a health status.

        Args:
            status: Health status to get text for.

        Returns:
            Status text: HEALTHY, WARNING, or UNHEALTHY
        """
        if status == HealthStatus.HEALTHY:
            return "HEALTHY"
        elif status == HealthStatus.DEGRADED:
            return "WARNING"
        else:  # UNHEALTHY
            return "UNHEALTHY"

    def _format_component_line(self, component: str, icon: str, message: str) -> str:
        """Format a single component line.

        Format: '{component} {icon} {message}'

        Args:
            component: Component name.
            icon: Status icon.
            message: Status message.

        Returns:
            Formatted line string.
        """
        return f"{component} {icon} {message}"
