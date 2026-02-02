"""IntegrationCheckpointService for verifying build-to-install data consistency.

This module provides the IntegrationCheckpointService application service that:
- Verifies version consistency between build and install phases
- Verifies wheel path exists and matches expected
- Verifies artifact counts (agents, commands, templates) are consistent
- Returns CheckpointResult with display-ready output

Used by: forge:install CLI commands at build-to-install transition
"""

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class CheckpointData:
    """Immutable data for checkpoint verification.

    Attributes:
        version: Version string being installed.
        wheel_path: Path to the wheel file (or None if not applicable).
        agent_count: Number of agents in the package.
        command_count: Number of commands in the package.
        template_count: Number of templates in the package.
    """

    version: str
    wheel_path: Path | None
    agent_count: int
    command_count: int
    template_count: int


@dataclass
class CheckpointResult:
    """Result of checkpoint verification.

    Attributes:
        passed: True if all checks passed.
        mismatches: List of mismatch descriptions.
        version_match: True if versions match.
        wheel_path_match: True if wheel paths match.
        counts_match: True if all artifact counts match.
        display_lines: Formatted output lines for display.
    """

    passed: bool
    mismatches: list[str]
    version_match: bool
    wheel_path_match: bool
    counts_match: bool
    display_lines: list[str]


class IntegrationCheckpointService:
    """Application service for verifying build-to-install data consistency.

    This service:
    - Compares expected checkpoint data against actual data
    - Reports all mismatches with expected vs actual values
    - Provides display-ready output for CLI rendering
    """

    # Display indicators
    CHECKMARK = "\u2713"  # Unicode checkmark
    CROSS = "\u2717"  # Unicode X

    def verify_checkpoint(
        self, expected: CheckpointData, actual: CheckpointData
    ) -> CheckpointResult:
        """Verify that actual checkpoint data matches expected.

        Args:
            expected: Expected checkpoint data from build phase.
            actual: Actual checkpoint data from install phase.

        Returns:
            CheckpointResult with verification status and display lines.
        """
        mismatches: list[str] = []
        display_lines: list[str] = []

        # Header
        display_lines.append("")
        display_lines.append("=" * 50)
        display_lines.append("       INTEGRATION CHECKPOINT")
        display_lines.append("=" * 50)
        display_lines.append("")

        # Check version
        version_match = expected.version == actual.version
        if version_match:
            display_lines.append(f"  {self.CHECKMARK} Version matches build")
        else:
            display_lines.append(f"  {self.CROSS} Version mismatch")
            display_lines.append(f"      Expected: {expected.version}")
            display_lines.append(f"      Found: {actual.version}")
            mismatches.append(
                f"Version mismatch: expected {expected.version}, found {actual.version}"
            )

        # Check wheel path
        wheel_path_match = expected.wheel_path == actual.wheel_path
        if wheel_path_match:
            display_lines.append(f"  {self.CHECKMARK} Wheel path verified")
        else:
            display_lines.append(f"  {self.CROSS} Wheel path mismatch")
            display_lines.append(f"      Expected: {expected.wheel_path}")
            display_lines.append(f"      Found: {actual.wheel_path}")
            mismatches.append(
                f"Wheel path mismatch: expected {expected.wheel_path}, found {actual.wheel_path}"
            )

        # Check artifact counts
        agent_match = expected.agent_count == actual.agent_count
        command_match = expected.command_count == actual.command_count
        template_match = expected.template_count == actual.template_count
        counts_match = agent_match and command_match and template_match

        if counts_match:
            display_lines.append(f"  {self.CHECKMARK} Artifact counts consistent")
            display_lines.append(
                f"      Agents: {actual.agent_count}, Commands: {actual.command_count}, Templates: {actual.template_count}"
            )
        else:
            display_lines.append(f"  {self.CROSS} Artifact counts mismatch")
            if not agent_match:
                display_lines.append(
                    f"      Agent count - Expected: {expected.agent_count}, Found: {actual.agent_count}"
                )
                mismatches.append(
                    f"Agent count mismatch: expected {expected.agent_count}, found {actual.agent_count}"
                )
            if not command_match:
                display_lines.append(
                    f"      Command count - Expected: {expected.command_count}, Found: {actual.command_count}"
                )
                mismatches.append(
                    f"Command count mismatch: expected {expected.command_count}, found {actual.command_count}"
                )
            if not template_match:
                display_lines.append(
                    f"      Template count - Expected: {expected.template_count}, Found: {actual.template_count}"
                )
                mismatches.append(
                    f"Template count mismatch: expected {expected.template_count}, found {actual.template_count}"
                )

        # Footer
        display_lines.append("")
        passed = version_match and wheel_path_match and counts_match
        if passed:
            display_lines.append(f"  {self.CHECKMARK} All checks passed")
        else:
            display_lines.append(f"  {self.CROSS} Checkpoint verification failed")
        display_lines.append("=" * 50)

        return CheckpointResult(
            passed=passed,
            mismatches=mismatches,
            version_match=version_match,
            wheel_path_match=wheel_path_match,
            counts_match=counts_match,
            display_lines=display_lines,
        )
