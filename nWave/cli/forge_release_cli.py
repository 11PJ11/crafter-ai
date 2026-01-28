"""
Forge Release CLI - Driving adapter for release command.

Entry point for /nw:forge:release command that creates release PRs
from development to main branch.

HEXAGONAL ARCHITECTURE:
- This is a DRIVING ADAPTER (outside the hexagon)
- Invokes ReleaseService application service
- Formats output and handles CLI interaction
"""

from __future__ import annotations

import os
import sys
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class ReleaseResult:
    """Result of release operation from ReleaseService."""

    success: bool
    pr_number: Optional[int]
    pr_url: Optional[str]
    error_message: Optional[str] = None


def format_release_output(result: ReleaseResult) -> str:
    """
    Format ReleaseResult for CLI display.

    Args:
        result: ReleaseResult from ReleaseService

    Returns:
        Formatted output string for display

    Output format (07-06):
        PR #123 created.
        CI/CD pipeline triggered. Monitor at: {pr_url}
    """
    if not result.success:
        return result.error_message or "Unknown error"

    output_lines = []

    # Show PR created message with number
    if result.pr_number:
        output_lines.append(f"PR #{result.pr_number} created.")

    # Show pipeline status with monitoring URL
    if result.pr_url:
        output_lines.append(f"CI/CD pipeline triggered. Monitor at: {result.pr_url}")

    return "\n".join(output_lines)


def main() -> int:
    """
    Main entry point for /nw:forge:release command.

    Returns:
        Exit code: 0 for success, non-zero for error
    """
    # Check for test mode (mock injection via environment)
    if os.environ.get("NWAVE_TEST_MODE") == "true":
        return _run_test_mode()

    # Production mode
    return _run_production_mode()


def _run_test_mode() -> int:
    """Run in test mode with mocked adapters."""
    from unittest.mock import Mock

    # Get mock values from environment
    mock_branch = os.environ.get("NWAVE_MOCK_GIT_BRANCH", "development")
    mock_has_uncommitted = (
        os.environ.get("NWAVE_MOCK_GIT_HAS_UNCOMMITTED", "false").lower() == "true"
    )
    mock_pr_number = int(os.environ.get("NWAVE_MOCK_GH_PR_NUMBER", "123"))
    mock_pr_url = os.environ.get(
        "NWAVE_MOCK_GH_PR_URL",
        "https://github.com/UndeadGrishnackh/crafter-ai/pull/123",
    )
    mock_gh_success = os.environ.get("NWAVE_MOCK_GH_SUCCESS", "true").lower() == "true"
    mock_gh_error = os.environ.get("NWAVE_MOCK_GH_ERROR", "")

    # Create mock adapters
    mock_git = Mock()
    mock_git.get_current_branch.return_value = mock_branch
    mock_git.has_uncommitted_changes.return_value = mock_has_uncommitted

    mock_github_cli = Mock()
    if mock_gh_success:
        from nWave.core.versioning.ports.github_cli_port import PRResult

        mock_github_cli.create_pr.return_value = PRResult(
            success=True,
            pr_number=mock_pr_number,
            pr_url=mock_pr_url,
        )
    else:
        from nWave.core.versioning.ports.github_cli_port import PRResult

        mock_github_cli.create_pr.return_value = PRResult(
            success=False,
            pr_number=None,
            pr_url=None,
            error_message=mock_gh_error or "Mock error",
        )

    # Create service with mock adapters
    from nWave.core.versioning.application.release_service import ReleaseService

    service = ReleaseService(git=mock_git, github_cli=mock_github_cli)
    result = service.create_release_pr()

    # Convert to local ReleaseResult for formatting
    local_result = ReleaseResult(
        success=result.success,
        pr_number=result.pr_number,
        pr_url=result.pr_url,
        error_message=result.error_message,
    )

    # Format and print output
    output = format_release_output(local_result)
    if result.success:
        print(output)
        return 0
    else:
        print(output, file=sys.stderr)
        return 1


def _run_production_mode() -> int:
    """Run in production mode with real adapters."""
    try:
        from nWave.core.versioning.application.release_service import ReleaseService
        from nWave.infrastructure.versioning.git_adapter import GitAdapter
        from nWave.infrastructure.versioning.github_cli_adapter import GitHubCLIAdapter

        # Create real adapters
        git_adapter = GitAdapter()
        github_cli_adapter = GitHubCLIAdapter()

        # Create service with real adapters
        service = ReleaseService(git=git_adapter, github_cli=github_cli_adapter)
        result = service.create_release_pr()

        # Convert to local ReleaseResult for formatting
        local_result = ReleaseResult(
            success=result.success,
            pr_number=result.pr_number,
            pr_url=result.pr_url,
            error_message=result.error_message,
        )

        # Format and print output
        output = format_release_output(local_result)
        if result.success:
            print(output)
            return 0
        else:
            print(output, file=sys.stderr)
            return 1

    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
