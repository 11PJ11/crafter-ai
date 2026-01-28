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
        THEN: Output includes pipeline triggered message with monitoring URL

        NOTE: Updated per 07-06 - new format includes monitoring URL
        """
        from nWave.cli.forge_release_cli import format_release_output

        result = ReleaseResult(
            success=True,
            pr_number=456,
            pr_url="https://github.com/owner/repo/pull/456",
        )

        output = format_release_output(result)

        # Assert - Updated format per 07-06
        assert "CI/CD pipeline triggered" in output
        assert "https://github.com/owner/repo/pull/456" in output

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


# ============================================================================
# Step 07-06: Pipeline Status Display Tests
# ============================================================================


class TestForgeReleaseCLIPipelineStatus:
    """
    Test: forge_release_cli displays pipeline status per step 07-06.

    Acceptance Criteria:
    - Output displays "PR #123 created."
    - Output displays "CI/CD pipeline triggered. Monitor at: {pr_url}"
    """

    def test_format_release_output_shows_pr_created_message(self):
        """
        GIVEN: Successful release result with PR info
        WHEN: format_release_output() is called
        THEN: Output includes "PR #123 created."

        Step 07-06 requirement: "PR #123 created." format
        """
        from nWave.cli.forge_release_cli import format_release_output

        result = ReleaseResult(
            success=True,
            pr_number=123,
            pr_url="https://github.com/UndeadGrishnackh/crafter-ai/pull/123",
        )

        output = format_release_output(result)

        # Assert - exact format "PR #123 created."
        assert "PR #123 created." in output, (
            f"Expected 'PR #123 created.' in output, got: {output!r}"
        )

    def test_format_release_output_shows_pipeline_monitor_url(self):
        """
        GIVEN: Successful release result with PR URL
        WHEN: format_release_output() is called
        THEN: Output includes "CI/CD pipeline triggered. Monitor at: {pr_url}"

        Step 07-06 requirement: Pipeline monitoring message with URL
        """
        from nWave.cli.forge_release_cli import format_release_output

        result = ReleaseResult(
            success=True,
            pr_number=456,
            pr_url="https://github.com/owner/repo/pull/456",
        )

        output = format_release_output(result)

        # Assert - exact format "CI/CD pipeline triggered. Monitor at: {url}"
        expected_message = "CI/CD pipeline triggered. Monitor at: https://github.com/owner/repo/pull/456"
        assert expected_message in output, (
            f"Expected '{expected_message}' in output, got: {output!r}"
        )


# ============================================================================
# Step 07-04: Permission Denied Error Display Tests
# ============================================================================


class TestForgeReleaseCLIPermissionError:
    """
    Test: forge_release_cli displays permission denied error per step 07-04.

    Acceptance Criteria:
    - Error displays "Permission denied. You don't have access to create releases for this repository."
    - No PR info is shown
    """

    def test_format_release_output_shows_permission_error(self):
        """
        GIVEN: Release failed due to permission denied
        WHEN: format_release_output() is called
        THEN: Output shows permission denied error message

        Step 07-04 requirement: Exact error message display
        """
        from nWave.cli.forge_release_cli import format_release_output

        result = ReleaseResult(
            success=False,
            pr_number=None,
            pr_url=None,
            error_message="Permission denied. You don't have access to create releases for this repository.",
        )

        output = format_release_output(result)

        # Assert - exact error message
        assert "Permission denied" in output
        assert "don't have access to create releases" in output

    def test_format_release_output_permission_error_contains_full_message(self):
        """
        GIVEN: Release failed due to permission denied
        WHEN: format_release_output() is called
        THEN: Output contains the complete permission denied error message

        Step 07-04 requirement: Full error message display
        """
        from nWave.cli.forge_release_cli import format_release_output

        expected_error = "Permission denied. You don't have access to create releases for this repository."
        result = ReleaseResult(
            success=False,
            pr_number=None,
            pr_url=None,
            error_message=expected_error,
        )

        output = format_release_output(result)

        # Assert - full error message is present
        assert expected_error in output
