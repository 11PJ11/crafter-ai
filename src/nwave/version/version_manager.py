"""Version management for nWave framework."""
from pathlib import Path


class VersionManager:
    """Manages version checking and status reporting.

    This class follows hexagonal architecture principles by focusing
    on domain logic without external dependencies. It reads the local
    version from a file and provides version comparison capabilities.
    """

    def __init__(self, version_file_path: Path):
        """Initialize VersionManager with path to VERSION file.

        Args:
            version_file_path: Path to the VERSION file containing local version
        """
        self._version_file_path = version_file_path

    def get_local_version(self) -> str:
        """Read local version from VERSION file.

        Returns:
            str: The local version string (e.g., "1.5.7")

        Raises:
            FileNotFoundError: If VERSION file does not exist
        """
        if not self._version_file_path.exists():
            raise FileNotFoundError(
                f"VERSION file not found at {self._version_file_path}"
            )
        return self._version_file_path.read_text().strip()

    def is_up_to_date(self, remote_version: str) -> bool:
        """Determine if local version matches remote version.

        Args:
            remote_version: The remote version string to compare against

        Returns:
            bool: True if versions match, False otherwise
        """
        local_version = self.get_local_version()
        return local_version == remote_version

    def format_status_message(self, is_up_to_date: bool) -> str:
        """Format version status message for display.

        Args:
            is_up_to_date: Whether the local version is current

        Returns:
            str: Formatted status message (e.g., "nWave v1.5.7 (up to date)")
        """
        local_version = self.get_local_version()
        if is_up_to_date:
            return f"nWave v{local_version} (up to date)"
        else:
            return f"nWave v{local_version} (update available)"
