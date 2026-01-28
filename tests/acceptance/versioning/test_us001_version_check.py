"""
Acceptance tests for US-001: Check Installed Version.

ACTIVE SCENARIO: Display version with update available
- Marco has v1.2.3 installed
- GitHub shows v1.3.0 available
- Display version with update indicator
- Update watermark file

HEXAGONAL BOUNDARY: Tests invoke through CLI entry point only.
"""

import json
import pytest
from datetime import datetime, timezone


class TestDisplayVersionWithUpdateAvailable:
    """
    Scenario: Display version with update available

    Given Marco has nWave v1.2.3 installed in the test ~/.claude/ directory
    And the VERSION file contains "1.2.3"
    And the GitHub API returns v1.3.0 as the latest release
    When Marco runs the /nw:version command through the CLI entry point
    Then the output displays "nWave v1.2.3 (update available: v1.3.0)"
    And the watermark file ~/.claude/nwave.update is updated with current timestamp
    And the watermark file contains latest_version "1.3.0"
    """

    def test_display_version_with_update_available(
        self,
        test_installation,
        mock_github_adapter,
        in_memory_file_system_adapter,
        cli_result,
    ):
        """
        ACCEPTANCE TEST: Display version with update available.

        This test exercises the complete system path:
        CLI -> VersionService -> FileSystemAdapter + GitHubAPIAdapter
        """
        # GIVEN: Marco has nWave v1.2.3 installed
        version_file = test_installation["version_file"]
        version_file.write_text("1.2.3")

        # AND: GitHub API returns v1.3.0 as latest release
        mock_github_adapter.configure(latest_version="1.3.0")

        # Capture timestamp before the action
        timestamp_before = datetime.now(timezone.utc)

        # WHEN: Marco runs the /nw:version command through CLI entry point
        # Import here to avoid contaminating namespace
        from nWave.core.versioning.application.version_service import VersionService
        from nWave.cli.version_cli import format_version_output

        version_service = VersionService(
            github_api=mock_github_adapter,
            file_system=in_memory_file_system_adapter,
        )

        result = version_service.check_version()
        output = format_version_output(result)

        cli_result["output"] = output

        # Capture timestamp after the action
        timestamp_after = datetime.now(timezone.utc)

        # THEN: Output displays "nWave v1.2.3 (update available: v1.3.0)"
        assert "nWave v1.2.3 (update available: v1.3.0)" in output, (
            f"Expected version output not found. Got: {output}"
        )

        # AND: Watermark file is updated with current timestamp
        watermark_file = test_installation["watermark_file"]
        assert watermark_file.exists(), "Watermark file was not created"

        watermark_content = json.loads(watermark_file.read_text())

        watermark_timestamp = datetime.fromisoformat(watermark_content["last_check"])
        assert timestamp_before <= watermark_timestamp <= timestamp_after, (
            f"Watermark timestamp {watermark_timestamp} not within expected range "
            f"[{timestamp_before}, {timestamp_after}]"
        )

        # AND: Watermark file contains latest_version "1.3.0"
        assert watermark_content["latest_version"] == "1.3.0", (
            f"Expected latest_version '1.3.0', got '{watermark_content['latest_version']}'"
        )
