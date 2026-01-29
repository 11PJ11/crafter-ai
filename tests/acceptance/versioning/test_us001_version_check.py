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


class TestDailyAutoCheckUpdatesWatermarkWhenStale:
    """
    Scenario: Daily auto-check updates watermark when stale (Step 03-04)

    Given Elena has nWave v1.2.3 installed in the test ~/.claude/ directory
    And the watermark file shows last_check was 25 hours ago
    And the GitHub API returns v1.3.0 as the latest release
    When Elena runs the /nw:version command through the CLI entry point
    Then the system checks GitHub Releases
    And the watermark file is updated with new timestamp
    And the watermark file contains latest_version "1.3.0"
    """

    def test_stale_watermark_triggers_github_check(
        self,
        test_installation,
        mock_github_adapter,
        in_memory_file_system_adapter,
        cli_result,
    ):
        """
        ACCEPTANCE TEST: Stale watermark (>24h) triggers GitHub check.

        This test exercises the complete system path with stale watermark:
        CLI -> VersionService -> (checks watermark staleness) -> GitHubAPIAdapter -> updates watermark
        """
        from datetime import timedelta

        # GIVEN: Elena has nWave v1.2.3 installed
        version_file = test_installation["version_file"]
        version_file.write_text("1.2.3")

        # AND: The watermark file shows last_check was 25 hours ago
        stale_timestamp = datetime.now(timezone.utc) - timedelta(hours=25)
        stale_watermark_content = json.dumps(
            {
                "last_check": stale_timestamp.isoformat(),
                "latest_version": "1.2.0",  # Old version in watermark
            }
        )
        watermark_file = test_installation["watermark_file"]
        watermark_file.write_text(stale_watermark_content)

        # AND: GitHub API returns v1.3.0 as latest release
        mock_github_adapter.configure(latest_version="1.3.0")

        # Track if GitHub API was called
        github_call_count_before = getattr(mock_github_adapter, "_call_count", 0)
        original_get_latest = mock_github_adapter.get_latest_release

        def tracking_get_latest(owner, repo):
            mock_github_adapter._call_count = (
                getattr(mock_github_adapter, "_call_count", 0) + 1
            )
            return original_get_latest(owner, repo)

        mock_github_adapter.get_latest_release = tracking_get_latest

        # Capture timestamp before action
        timestamp_before = datetime.now(timezone.utc)

        # WHEN: Elena runs the /nw:version command through CLI entry point
        from nWave.core.versioning.application.version_service import VersionService
        from nWave.cli.version_cli import format_version_output

        version_service = VersionService(
            github_api=mock_github_adapter,
            file_system=in_memory_file_system_adapter,
        )

        result = version_service.check_version()
        output = format_version_output(result)
        cli_result["output"] = output

        # Capture timestamp after action
        timestamp_after = datetime.now(timezone.utc)

        # THEN: The system checks GitHub Releases (API was called)
        github_call_count_after = getattr(mock_github_adapter, "_call_count", 0)
        assert github_call_count_after > github_call_count_before, (
            "Expected GitHub API to be called when watermark is stale"
        )

        # AND: The watermark file is updated with new timestamp
        updated_watermark_content = json.loads(watermark_file.read_text())
        updated_timestamp = datetime.fromisoformat(
            updated_watermark_content["last_check"]
        )

        assert updated_timestamp > stale_timestamp, (
            f"Watermark timestamp {updated_timestamp} should be newer than stale {stale_timestamp}"
        )
        assert timestamp_before <= updated_timestamp <= timestamp_after, (
            f"Watermark timestamp {updated_timestamp} not within expected range "
            f"[{timestamp_before}, {timestamp_after}]"
        )

        # AND: The watermark file contains latest_version "1.3.0"
        assert updated_watermark_content["latest_version"] == "1.3.0", (
            f"Expected latest_version '1.3.0', got '{updated_watermark_content['latest_version']}'"
        )
