"""
Unit tests for version_cli (driving adapter).

version_cli formats VersionCheckResult into user-facing output.
"""

import pytest
from datetime import datetime, timezone

from nWave.core.versioning.domain.version import Version


class TestVersionCliFormatsOutput:
    """Test that version_cli formats output correctly."""

    def test_version_cli_formats_output_with_update_indicator(self):
        """CLI should format 'nWave v1.2.3 (update available: v1.3.0)'."""
        from nWave.core.versioning.application.version_service import VersionCheckResult
        from nWave.cli.version_cli import format_version_output

        # GIVEN: VersionCheckResult with update available (local < remote)
        result = VersionCheckResult(
            local_version=Version("1.2.3"),
            remote_version=Version("1.3.0"),
        )

        # WHEN: format_version_output is called
        output = format_version_output(result)

        # THEN: Output matches expected format
        assert "nWave v1.2.3 (update available: v1.3.0)" in output

    def test_version_cli_formats_up_to_date_output(self):
        """CLI should format 'nWave v1.3.0 (up to date)' when no update."""
        from nWave.core.versioning.application.version_service import VersionCheckResult
        from nWave.cli.version_cli import format_version_output

        # GIVEN: VersionCheckResult without update available (local == remote)
        result = VersionCheckResult(
            local_version=Version("1.3.0"),
            remote_version=Version("1.3.0"),
        )

        # WHEN: format_version_output is called
        output = format_version_output(result)

        # THEN: Output matches expected format
        assert "nWave v1.3.0 (up to date)" in output
