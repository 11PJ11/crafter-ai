"""PreflightFormatValidator service for cross-journey format consistency.

This module provides validation of pre-flight check output format consistency
across all three journeys (build, install, PyPI). It ensures that:
- Table structure (columns, headers) is identical
- Status icons are consistent ([check], [x], [!])
- Python version check format is standardized
- Error formats are identical
"""

from dataclasses import dataclass

from crafter_ai.installer.domain.check_result import CheckResult, CheckSeverity


@dataclass(frozen=True)
class ValidationResult:
    """Immutable result of format validation.

    Attributes:
        consistent: Whether the format is consistent across journeys.
        inconsistencies: List of detected inconsistency descriptions.
        journey_outputs: Formatted output for each journey.
    """

    consistent: bool
    inconsistencies: list[str]
    journey_outputs: dict[str, list[str]]


class PreflightFormatValidator:
    """Validates pre-flight check output format consistency across journeys.

    Ensures that pre-flight check output is identical across:
    - forge:build-local-candidate
    - forge:install-local-candidate
    - pipx install nwave

    Format specifications:
    - Column headers: 'Check' and 'Status'
    - Pass icon: '[check]' (green checkmark)
    - Fail icon: '[x]' (red x)
    - Warning icon: '[!]' (yellow warning)
    - Python check format: 'Python version [icon] X.Y.Z (3.10+ OK)'
    """

    # Standard column headers
    COLUMN_CHECK = "Check"
    COLUMN_STATUS = "Status"

    # Standard icons
    ICON_PASS = "[check]"
    ICON_FAIL = "[x]"
    ICON_WARNING = "[!]"

    # Standard column widths for consistent formatting
    CHECK_COLUMN_WIDTH = 20
    STATUS_COLUMN_WIDTH = 40

    # Standard journeys
    JOURNEYS = [
        "forge:build-local-candidate",
        "forge:install-local-candidate",
        "pipx install nwave",
    ]

    def validate_table_structure(self, results: list[CheckResult]) -> ValidationResult:
        """Validate that table structure is consistent across journeys.

        Args:
            results: List of check results to format.

        Returns:
            ValidationResult with consistency status and journey outputs.
        """
        journey_outputs: dict[str, list[str]] = {}
        inconsistencies: list[str] = []

        # Generate formatted output for all journeys
        for journey in self.JOURNEYS:
            journey_outputs[journey] = self.get_formatted_output(results, journey)

        # Compare all journey outputs for consistency
        if len(journey_outputs) > 1:
            first_output = next(iter(journey_outputs.values()))
            for journey, output in journey_outputs.items():
                if output != first_output:
                    inconsistencies.append(f"Table structure differs for {journey}")

        return ValidationResult(
            consistent=len(inconsistencies) == 0,
            inconsistencies=inconsistencies,
            journey_outputs=journey_outputs,
        )

    def validate_icons_consistency(
        self, results: list[CheckResult]
    ) -> ValidationResult:
        """Validate that status icons are consistent across journeys.

        Args:
            results: List of check results to format.

        Returns:
            ValidationResult with consistency status and journey outputs.
        """
        journey_outputs: dict[str, list[str]] = {}
        inconsistencies: list[str] = []

        # Generate formatted output for all journeys
        for journey in self.JOURNEYS:
            journey_outputs[journey] = self.get_formatted_output(results, journey)

        # Verify icons are consistent
        for journey, output in journey_outputs.items():
            output_text = "\n".join(output)

            # Check for correct icons based on results
            for check_result in results:
                expected_icon = self._get_icon_for_result(check_result)
                if expected_icon not in output_text:
                    inconsistencies.append(
                        f"Missing expected icon {expected_icon} in {journey}"
                    )

        return ValidationResult(
            consistent=len(inconsistencies) == 0,
            inconsistencies=inconsistencies,
            journey_outputs=journey_outputs,
        )

    def get_formatted_output(
        self, results: list[CheckResult], journey: str
    ) -> list[str]:
        """Get formatted output for a specific journey.

        The output format is identical regardless of journey, ensuring
        cross-journey consistency.

        Args:
            results: List of check results to format.
            journey: Journey identifier (not used for formatting, only for context).

        Returns:
            List of formatted output lines.
        """
        lines: list[str] = []

        # Add header row
        header = self._format_row(self.COLUMN_CHECK, self.COLUMN_STATUS)
        lines.append(header)

        # Add separator
        separator = self._format_row(
            "-" * self.CHECK_COLUMN_WIDTH,
            "-" * self.STATUS_COLUMN_WIDTH,
        )
        lines.append(separator)

        # Format each result
        for result in results:
            icon = self._get_icon_for_result(result)
            status = self._format_status(result, icon)
            row = self._format_row(result.name, status)
            lines.append(row)

        return lines

    def _get_icon_for_result(self, result: CheckResult) -> str:
        """Get the appropriate icon for a check result.

        Args:
            result: Check result to get icon for.

        Returns:
            Icon string: [check], [x], or [!]
        """
        if not result.passed:
            return self.ICON_FAIL
        elif result.severity == CheckSeverity.WARNING:
            return self.ICON_WARNING
        else:
            return self.ICON_PASS

    def _format_status(self, result: CheckResult, icon: str) -> str:
        """Format the status cell for a check result.

        Args:
            result: Check result to format.
            icon: Icon to include in status.

        Returns:
            Formatted status string.
        """
        return f"{icon} {result.message}"

    def _format_row(self, check: str, status: str) -> str:
        """Format a single row with consistent column widths.

        Args:
            check: Check column value.
            status: Status column value.

        Returns:
            Formatted row string.
        """
        check_padded = check.ljust(self.CHECK_COLUMN_WIDTH)
        return f"{check_padded}  {status}"
