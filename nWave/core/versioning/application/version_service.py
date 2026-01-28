"""
VersionService - Application service for version check operations.

Orchestrates version checking through ports:
1. Reads installed version from FileSystemPort
2. Fetches latest version from GitHubAPIPort
3. Updates watermark via FileSystemPort
4. Returns VersionCheckResult with comparison

HEXAGONAL ARCHITECTURE:
- This is an APPLICATION SERVICE (inside the hexagon)
- Depends only on PORT interfaces, not concrete adapters
- Uses real domain objects (Version, Watermark), never mocks

OFFLINE HANDLING (Step 03-03):
- NetworkError and RateLimitError are caught gracefully
- Returns result with is_offline=True when network unavailable
- No exceptions propagated for network issues
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import TYPE_CHECKING, Optional, Protocol

from nWave.core.versioning.domain.version import Version
from nWave.core.versioning.domain.watermark import Watermark
from nWave.core.versioning.ports.github_api_port import (
    GitHubAPIPort,
    NetworkError,
    RateLimitError,
)

if TYPE_CHECKING:
    from nWave.core.versioning.ports.file_system_port import FileSystemPort


@dataclass(frozen=True)
class VersionCheckResult:
    """
    Result of a version check operation.

    Contains the installed version, optional latest version,
    and status flags for display formatting.

    Attributes:
        local_version: The locally installed version (alias for installed_version)
        remote_version: The latest available version from GitHub (None if offline)
        is_offline: True if unable to reach GitHub (network error or rate limited)
        update_available: True if remote_version > local_version
        error_message: Optional error message (not used in normal flow)

    Note:
        local_version and installed_version refer to the same value.
        remote_version and latest_version refer to the same value.
        These aliases maintain backward compatibility while following naming conventions.
    """

    local_version: Version
    remote_version: Optional[Version] = None
    is_offline: bool = False
    error_message: Optional[str] = None

    @property
    def installed_version(self) -> Version:
        """Alias for local_version (backward compatibility)."""
        return self.local_version

    @property
    def latest_version(self) -> Optional[Version]:
        """Alias for remote_version (backward compatibility)."""
        return self.remote_version

    @property
    def update_available(self) -> bool:
        """Check if an update is available."""
        if self.remote_version is None:
            return False
        return self.local_version < self.remote_version

    def format_display_message(self) -> str:
        """
        Format the version check result for CLI display.

        Returns:
            str: Formatted message for user display

        Examples:
            - "nWave v1.2.3 (up to date)"
            - "nWave v1.2.3 (update available: v1.3.0)"
            - "nWave v1.2.3 (Unable to check for updates)"
        """
        version_str = f"nWave v{self.local_version}"

        if self._is_unable_to_check():
            return f"{version_str} (Unable to check for updates)"

        if self._is_up_to_date():
            return f"{version_str} (up to date)"

        return f"{version_str} (update available: v{self.remote_version})"

    def _is_unable_to_check(self) -> bool:
        """Determine if unable to check for updates (offline or no remote version)."""
        return self.is_offline or self.remote_version is None

    def _is_up_to_date(self) -> bool:
        """Determine if local version matches remote version."""
        return self.local_version == self.remote_version


class GitHubAPIProtocol(Protocol):
    """Protocol for GitHub API operations."""

    def get_latest_release(self, owner: str, repo: str): ...


class FileSystemProtocol(Protocol):
    """Protocol for file system operations."""

    def read_version(self) -> Version: ...
    def read_watermark(self): ...
    def write_watermark(self, watermark: Watermark) -> None: ...


class VersionService:
    """
    Application service for version check operations.

    Orchestrates the version check workflow:
    1. Read installed version from file system
    2. Fetch latest version from GitHub API
    3. Update watermark with check timestamp and latest version
    4. Return comparison result

    Handles network errors gracefully - returns is_offline=True instead
    of raising exceptions for NetworkError or RateLimitError.

    Example:
        >>> service = VersionService(github_api=adapter, file_system=fs)
        >>> result = service.check_version()
        >>> if result.update_available:
        ...     print(f"Update to {result.latest_version} available!")
        >>> if result.is_offline:
        ...     print("Unable to check for updates")
    """

    # Default repository configuration
    DEFAULT_OWNER = "anthropics"
    DEFAULT_REPO = "claude-code"

    def __init__(
        self,
        github_api: GitHubAPIProtocol,
        file_system: FileSystemProtocol = None,
        version_file_path: Path = None,
        owner: str = None,
        repo: str = None,
    ) -> None:
        """
        Create a VersionService.

        Args:
            github_api: Adapter implementing GitHubAPIPort
            file_system: Adapter implementing FileSystemPort (optional if version_file_path provided)
            version_file_path: Path to VERSION file (alternative to file_system)
            owner: GitHub repository owner (default: anthropics)
            repo: GitHub repository name (default: claude-code)

        Note:
            Either file_system OR version_file_path must be provided.
            If version_file_path is provided, a simple file reader is used.
        """
        self._github_api = github_api
        self._file_system = file_system
        self._version_file_path = version_file_path
        self._owner = owner or self.DEFAULT_OWNER
        self._repo = repo or self.DEFAULT_REPO

    def check_version(self) -> VersionCheckResult:
        """
        Check the installed version against GitHub latest release.

        Workflow:
        1. Read installed version from VERSION file
        2. Fetch latest release from GitHub API (graceful on network error)
        3. Update watermark file with timestamp and latest version (if online)
        4. Return comparison result

        Returns:
            VersionCheckResult with installed, latest versions and update flag.
            If network is unavailable, is_offline=True and remote_version=None.

        Raises:
            FileNotFoundError: If VERSION file is missing

        Note:
            NetworkError and RateLimitError are NOT raised - they are handled
            gracefully by returning is_offline=True.
        """
        # Step 1: Read installed version
        installed_version = self._read_local_version()

        # Step 2: Fetch latest release from GitHub (with graceful error handling)
        try:
            release_info = self._github_api.get_latest_release(self._owner, self._repo)
            latest_version = release_info.version

            # Step 3: Update watermark (only if online)
            if self._file_system is not None:
                watermark = Watermark(
                    last_check=datetime.now(timezone.utc),
                    latest_version=latest_version,
                )
                self._file_system.write_watermark(watermark)

            return VersionCheckResult(
                local_version=installed_version,
                remote_version=latest_version,
                is_offline=False,
            )

        except (NetworkError, RateLimitError):
            # Handle network errors gracefully - user is offline or rate limited
            return VersionCheckResult(
                local_version=installed_version,
                remote_version=None,
                is_offline=True,
            )

    def _read_local_version(self) -> Version:
        """
        Read the local version from VERSION file.

        Returns:
            Version: The locally installed version

        Raises:
            FileNotFoundError: If VERSION file doesn't exist
        """
        if self._file_system is not None:
            return self._file_system.read_version()

        if self._version_file_path is not None:
            if not self._version_file_path.exists():
                raise FileNotFoundError(
                    f"VERSION file not found at {self._version_file_path}"
                )
            version_string = self._version_file_path.read_text().strip()
            return Version(version_string)

        raise ValueError("Either file_system or version_file_path must be provided")
