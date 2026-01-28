"""
Version CLI - Driving adapter for version check command.

Entry point for /nw:version command that displays installed version
and checks for available updates.

HEXAGONAL ARCHITECTURE:
- This is a DRIVING ADAPTER (outside the hexagon)
- Invokes VersionService application service
- Formats output for user display

TEST MODE:
When NWAVE_TEST_MODE=true, uses mock GitHub API responses from environment:
- NWAVE_MOCK_GITHUB_VERSION: Latest version to return
- NWAVE_MOCK_GITHUB_REACHABLE: "true" or "false" for network status
"""

from __future__ import annotations

import os
import sys
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from nWave.core.versioning.application.version_service import VersionCheckResult


def format_version_output(result: "VersionCheckResult") -> str:
    """
    Format VersionCheckResult for CLI display.

    Produces output in the format:
    - "nWave v1.2.3 (update available: v1.3.0)" when update available
    - "nWave v1.3.0 (up to date)" when no update available
    - "nWave v1.2.3 (Unable to check for updates)" when offline

    Args:
        result: VersionCheckResult from VersionService

    Returns:
        Formatted string for display
    """
    # Use the VersionCheckResult's built-in formatting
    return result.format_display_message()


def _is_test_mode() -> bool:
    """Check if running in test mode."""
    return os.getenv("NWAVE_TEST_MODE", "false").lower() == "true"


def _create_mock_github_adapter():
    """Create a mock GitHub adapter for testing."""
    from nWave.core.versioning.domain.version import Version
    from nWave.core.versioning.ports.github_api_port import (
        GitHubAPIPort,
        NetworkError,
        ReleaseInfo,
    )

    class MockGitHubAdapter(GitHubAPIPort):
        """Mock GitHub adapter for testing."""

        def get_latest_release(self, owner: str, repo: str) -> ReleaseInfo:
            """Return mock release info from environment."""
            is_reachable = os.getenv("NWAVE_MOCK_GITHUB_REACHABLE", "true").lower() == "true"

            if not is_reachable:
                raise NetworkError("Mock: GitHub API unreachable")

            version_str = os.getenv("NWAVE_MOCK_GITHUB_VERSION", "1.0.0")
            return ReleaseInfo(
                version=Version(version_str),
                checksum="mock_checksum_abc123",
                download_url="https://example.com/mock/release.zip",
            )

    return MockGitHubAdapter()


def main() -> int:
    """
    Main entry point for /nw:version command.

    Returns:
        Exit code: 0 for success, non-zero for error
    """
    from nWave.core.versioning.application.version_service import VersionService
    from nWave.infrastructure.versioning.file_system_adapter import FileSystemAdapter
    from nWave.core.versioning.ports.github_api_port import NetworkError, RateLimitError

    try:
        # Create file system adapter (always uses real files)
        file_system = FileSystemAdapter()

        # Create GitHub adapter (mock in test mode, real otherwise)
        if _is_test_mode():
            github_api = _create_mock_github_adapter()
        else:
            from nWave.infrastructure.versioning.github_api_adapter import GitHubAPIAdapter
            github_api = GitHubAPIAdapter()

        # Create service and check version
        service = VersionService(
            github_api=github_api,
            file_system=file_system,
        )

        result = service.check_version()

        # Display output using the result's built-in formatting
        output = format_version_output(result)
        print(output)

        return 0

    except FileNotFoundError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1

    except (NetworkError, RateLimitError):
        # Graceful degradation - show version without update info
        return _handle_offline_degradation()

    except Exception as e:
        print(f"ERROR: Unexpected error: {e}", file=sys.stderr)
        return 1


def _handle_offline_degradation() -> int:
    """
    Handle graceful degradation when GitHub API is unreachable.

    Shows installed version with "Unable to check for updates" message.

    Returns:
        0 for success, 1 if VERSION file not found
    """
    from nWave.infrastructure.versioning.file_system_adapter import FileSystemAdapter

    try:
        file_system = FileSystemAdapter()
        version = file_system.read_version()
        print(f"nWave v{version} (Unable to check for updates)")
        return 0
    except FileNotFoundError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
