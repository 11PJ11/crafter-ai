"""
Unit tests for forge_release_cli - Driving adapter for forge:release command.

HEXAGONAL ARCHITECTURE:
- forge_release_cli is a DRIVING ADAPTER (entry point)
- Invokes ReleaseService application service
- Formats output for CLI display

Test coverage:
- test_forge_release_cli_shows_pr_info: CLI displays PR number, URL, and status message
"""

from dataclasses import dataclass
from typing import Optional, Tuple

import pytest


@dataclass(frozen=True)
class ReleaseResult:
    """Result of release operation from ReleaseService."""

    success: bool
    pr_number: Optional[int]
    pr_url: Optional[str]
    error_message: Optional[str] = None


class TestForgeReleaseCLIShowsPRInfo:
    """
    Test: forge_release_cli displays PR info to user.

    Acceptance Criteria:
    - Output displays the PR number and URL
    - Output indicates "PR created. Pipeline running..."
    """

    def test_format_release_output_shows_pr_number_and_url(self):
        """
        GIVEN: Successful release result with PR info
        WHEN: format_release_output() is called
        THEN: Output includes PR number and URL
        """
        # Act - Import CLI module (will fail until implemented)
        from nWave.cli.forge_release_cli import format_release_output

        result = ReleaseResult(
            success=True,
            pr_number=123,
            pr_url="https://github.com/UndeadGrishnackh/crafter-ai/pull/123",
        )

        output = format_release_output(result)

        # Assert
        assert "123" in output or "PR #123" in output
        assert (
            "https://github.com/UndeadGrishnackh/crafter-ai/pull/123" in output
            or "pull/123" in output
        )

    def test_format_release_output_shows_pipeline_running_message(self):
        """
        GIVEN: Successful release result
        WHEN: format_release_output() is called
        THEN: Output includes "PR created. Pipeline running..."
        """
        from nWave.cli.forge_release_cli import format_release_output

        result = ReleaseResult(
            success=True,
            pr_number=456,
            pr_url="https://github.com/owner/repo/pull/456",
        )

        output = format_release_output(result)

        # Assert
        assert "PR created. Pipeline running..." in output

    def test_format_release_output_shows_error_on_failure(self):
        """
        GIVEN: Failed release result with error message
        WHEN: format_release_output() is called
        THEN: Output includes error message
        """
        from nWave.cli.forge_release_cli import format_release_output

        result = ReleaseResult(
            success=False,
            pr_number=None,
            pr_url=None,
            error_message="Release must be initiated from the development branch.",
        )

        output = format_release_output(result)

        # Assert
        assert "Release must be initiated from the development branch" in output

    def test_format_release_output_shows_branch_error(self):
        """
        GIVEN: Release failed due to wrong branch
        WHEN: format_release_output() is called
        THEN: Output shows appropriate branch error
        """
        from nWave.cli.forge_release_cli import format_release_output

        result = ReleaseResult(
            success=False,
            pr_number=None,
            pr_url=None,
            error_message="Release must be initiated from the development branch.",
        )

        output = format_release_output(result)

        # Assert
        assert "development branch" in output.lower() or "development" in output

    def test_format_release_output_shows_uncommitted_changes_error(self):
        """
        GIVEN: Release failed due to uncommitted changes
        WHEN: format_release_output() is called
        THEN: Output shows uncommitted changes error
        """
        from nWave.cli.forge_release_cli import format_release_output

        result = ReleaseResult(
            success=False,
            pr_number=None,
            pr_url=None,
            error_message="Uncommitted changes detected. Commit or stash changes before releasing.",
        )

        output = format_release_output(result)

        # Assert
        assert "uncommitted" in output.lower() or "Uncommitted" in output
