"""
VersionManager - Core domain service for version checking.

Business Responsibility:
- Read local version from VERSION file
- Compare local version with remote version
- Determine if system is up to date
- Format status messages for display
"""

from pathlib import Path


class VersionManager:
    """Manages version checking and status reporting."""

    def __init__(self, version_file_path: Path):
        """
        Initialize VersionManager with path to VERSION file.

        Args:
            version_file_path: Path to the VERSION file containing local version
        """
        self._version_file_path = version_file_path

    def get_local_version(self) -> str:
        """
        Read the local version from VERSION file.

        Returns:
            Version string (e.g., "1.5.7")

        Raises:
            FileNotFoundError: If VERSION file does not exist
        """
        if not self._version_file_path.exists():
            raise FileNotFoundError(
                f"VERSION file not found at {self._version_file_path}"
            )

        return self._version_file_path.read_text().strip()

    def is_up_to_date(self, remote_version: str) -> bool:
        """
        Determine if local version matches remote version.

        Args:
            remote_version: Version string from remote (e.g., "1.6.0")

        Returns:
            True if versions match (up to date), False otherwise
        """
        local_version = self.get_local_version()
        return local_version == remote_version

    def format_status_message(self, is_up_to_date: bool) -> str:
        """
        Format the version status message for display.

        Args:
            is_up_to_date: Whether the system is up to date

        Returns:
            Formatted status message (e.g., "nWave v1.5.7 (up to date)")
        """
        local_version = self.get_local_version()

        if is_up_to_date:
            return f"nWave v{local_version} (up to date)"
        else:
            return f"nWave v{local_version} (update available)"
