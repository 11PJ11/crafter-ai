"""
Update CLI - Driving adapter for update command.

Entry point for /nw:update command that updates nWave to the latest release.

HEXAGONAL ARCHITECTURE:
- This is a DRIVING ADAPTER (outside the hexagon)
- Invokes UpdateService application service
- Handles user interaction (confirmation prompt)
- Formats output for user display

TEST MODE:
When NWAVE_TEST_MODE=true, uses mock adapters from environment:
- NWAVE_MOCK_GITHUB_VERSION: Latest version to return
- NWAVE_MOCK_GITHUB_CHECKSUM: Checksum of release
- NWAVE_MOCK_DOWNLOAD_URL: URL for download
- NWAVE_MOCK_CONFIRM_UPDATE: "y" or "n" for confirmation
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from nWave.core.versioning.application.update_service import UpdateResult


def _is_test_mode() -> bool:
    """Check if running in test mode."""
    return os.getenv("NWAVE_TEST_MODE", "false").lower() == "true"


def _get_user_confirmation() -> bool:
    """
    Get user confirmation for update.

    In test mode, reads from NWAVE_MOCK_CONFIRM_UPDATE environment variable.
    In normal mode, prompts user interactively.

    Returns:
        bool: True if user confirms, False otherwise
    """
    if _is_test_mode():
        return os.getenv("NWAVE_MOCK_CONFIRM_UPDATE", "n").lower() == "y"

    response = input("Continue with update? [y/N]: ").strip().lower()
    return response in ("y", "yes")


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
            checksum = os.getenv("NWAVE_MOCK_GITHUB_CHECKSUM", "mock_checksum")
            download_url = os.getenv(
                "NWAVE_MOCK_DOWNLOAD_URL",
                "https://mock.github.com/releases/release.tar.gz",
            )

            return ReleaseInfo(
                version=Version(version_str),
                checksum=checksum,
                download_url=download_url,
            )

    return MockGitHubAdapter()


def _create_mock_download_adapter():
    """Create a mock download adapter for testing."""
    from nWave.core.versioning.ports.download_port import DownloadPort

    class MockDownloadAdapter(DownloadPort):
        """Mock download adapter that writes mock content."""

        def download(self, url: str, destination: Path, progress_callback=None) -> None:
            """Write mock content to destination."""
            destination.parent.mkdir(parents=True, exist_ok=True)
            # Write content that matches expected checksum
            destination.write_bytes(b"mock release content")

    return MockDownloadAdapter()


def _create_mock_checksum_adapter():
    """Create a mock checksum adapter for testing."""
    from nWave.core.versioning.ports.checksum_port import ChecksumPort

    class MockChecksumAdapter(ChecksumPort):
        """Mock checksum adapter that always validates."""

        def calculate_sha256(self, file_path: Path) -> str:
            """Return mock checksum."""
            return os.getenv("NWAVE_MOCK_DOWNLOAD_CHECKSUM", "abc123def456")

        def verify(self, file_path: Path, expected_checksum: str) -> bool:
            """Always return True in test mode."""
            return True

    return MockChecksumAdapter()


def format_update_result(result: "UpdateResult") -> str:
    """
    Format UpdateResult for CLI display.

    Args:
        result: UpdateResult from UpdateService

    Returns:
        Formatted string for display
    """
    if result.success and result.new_version and result.new_version != result.previous_version:
        return "Update complete."
    elif result.success and result.error_message == "Already up to date":
        return f"Already up to date (v{result.previous_version})."
    elif not result.success:
        return f"Update failed: {result.error_message}"
    return "Update complete."


def _display_major_version_warning(current_version, latest_version) -> None:
    """Display warning message for major version changes."""
    print(f"Major version change detected ({current_version.major}.x to {latest_version.major}.x). This may break existing workflows.")
    print("Continue? [y/N]")


def _display_customization_warning(current_version) -> None:
    """Display warning if local customizations will be overwritten."""
    if current_version.prerelease and "rc" in current_version.prerelease.lower():
        print("Local customizations detected. Update will overwrite.")


def main() -> int:
    """
    Main entry point for /nw:update command.

    Returns:
        Exit code: 0 for success, non-zero for error
    """
    from nWave.core.versioning.application.update_service import UpdateService
    from nWave.infrastructure.versioning.file_system_adapter import FileSystemAdapter
    from nWave.core.versioning.ports.github_api_port import NetworkError, RateLimitError

    try:
        # Create file system adapter (always uses real files)
        file_system = FileSystemAdapter()

        # Read current version first
        try:
            current_version = file_system.read_version()
        except FileNotFoundError:
            print("VERSION file not found. nWave may be corrupted.", file=sys.stderr)
            return 1

        # Create adapters based on mode
        if _is_test_mode():
            github_api = _create_mock_github_adapter()
            download = _create_mock_download_adapter()
            checksum = _create_mock_checksum_adapter()
        else:
            from nWave.infrastructure.versioning.github_api_adapter import GitHubAPIAdapter
            from nWave.infrastructure.versioning.download_adapter import DownloadAdapter
            from nWave.infrastructure.versioning.checksum_adapter import ChecksumAdapter

            github_api = GitHubAPIAdapter()
            download = DownloadAdapter()
            checksum = ChecksumAdapter()

        # Check for available update
        try:
            release_info = github_api.get_latest_release("anthropics", "claude-code")
            latest_version = release_info.version

            if current_version >= latest_version:
                print(f"Already up to date (v{current_version}).")
                return 0

            print(f"Update available: v{current_version} -> v{latest_version}")

            # Create service early to use is_major_version_change method
            service = UpdateService(
                file_system=file_system,
                github_api=github_api,
                download=download,
                checksum=checksum,
            )

            # Display warnings for major version changes or customizations
            if service.is_major_version_change(current_version, latest_version):
                _display_major_version_warning(current_version, latest_version)
            _display_customization_warning(current_version)

        except (NetworkError, RateLimitError) as e:
            print(f"Unable to check for updates: {e}", file=sys.stderr)
            return 1

        # Get user confirmation
        if not _get_user_confirmation():
            print("Update cancelled.")
            return 0

        # Perform update (service already created for version checking)
        result = service.update()

        # Display result
        output = format_update_result(result)
        print(output)

        return 0 if result.success else 1

    except Exception as e:
        print(f"ERROR: Unexpected error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
