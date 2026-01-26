"""
VersionComparator - semantic version comparison logic.

Business capability: Determine update significance (major, minor, patch).
"""


class VersionComparator:
    """Compares semantic versions to determine update type."""

    def is_major_update(self, current_version: str, new_version: str) -> bool:
        """
        Determine if update represents a major version bump.

        Major version bump = first number increases (1.x.x -> 2.x.x).
        Indicates breaking changes per semantic versioning.

        Args:
            current_version: Currently installed version (e.g., "1.5.7" or "v1.5.7")
            new_version: New available version (e.g., "2.0.0" or "v2.0.0")

        Returns:
            True if major version increased, False otherwise
        """
        current_major = self._extract_major_version(current_version)
        new_major = self._extract_major_version(new_version)

        return new_major > current_major

    def _extract_major_version(self, version: str) -> int:
        """
        Extract major version number from version string.

        Handles both "1.2.3" and "v1.2.3" formats.

        Args:
            version: Version string

        Returns:
            Major version number as integer
        """
        # Remove 'v' prefix if present
        version_clean = version.lstrip('v')

        # Split and get first component
        major_str = version_clean.split('.')[0]

        return int(major_str)
