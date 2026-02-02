"""ArtifactRegistry for storing and sharing artifact values between journey stages.

This module provides a registry pattern for managing artifact values (paths, strings)
that need to be shared between different stages of the installation journey.
The registry is injectable (not a singleton) for testability.
"""

from pathlib import Path


class ArtifactRegistry:
    """Registry for storing and sharing artifact values between journey stages.

    The registry stores artifact values (paths or strings) keyed by their identifier.
    It is designed to be injectable for testability and flexibility. Each journey
    instance gets its own registry for isolated state management.

    Attributes:
        WHEEL_PATH: Key constant for the path to built wheel.
        BACKUP_PATH: Key constant for the path to backup directory.
        INSTALL_PATH: Key constant for the path to installation.
        VERSION: Key constant for version string being installed.
        SOURCE: Key constant for source of installation (local/pypi).
    """

    # Predefined key constants for common artifact keys
    WHEEL_PATH: str = "wheel_path"
    BACKUP_PATH: str = "backup_path"
    INSTALL_PATH: str = "install_path"
    VERSION: str = "version"
    SOURCE: str = "source"

    def __init__(self) -> None:
        """Initialize an empty registry."""
        self._artifacts: dict[str, Path | str] = {}

    def set(self, key: str, value: Path | str) -> None:
        """Store an artifact value with the given key.

        Args:
            key: Unique identifier for the artifact.
            value: The artifact value (Path or string) to store.
        """
        self._artifacts[key] = value

    def get(self, key: str) -> Path | str | None:
        """Retrieve an artifact value by its key.

        Args:
            key: The key of the artifact to retrieve.

        Returns:
            The artifact value if found, None otherwise.
        """
        return self._artifacts.get(key)

    def get_required(self, key: str) -> Path | str:
        """Retrieve an artifact value, raising an error if not found.

        Args:
            key: The key of the artifact to retrieve.

        Returns:
            The artifact value.

        Raises:
            KeyError: If the key is not found in the registry.
        """
        if key not in self._artifacts:
            raise KeyError(f"Required artifact '{key}' not found in registry")
        return self._artifacts[key]

    def has(self, key: str) -> bool:
        """Check if an artifact is registered with the given key.

        Args:
            key: The key to check.

        Returns:
            True if an artifact is registered with this key, False otherwise.
        """
        return key in self._artifacts

    def keys(self) -> list[str]:
        """Retrieve all registered artifact keys.

        Returns:
            List of all registered keys.
        """
        return list(self._artifacts.keys())

    def clear(self) -> None:
        """Remove all artifacts from the registry."""
        self._artifacts.clear()

    @property
    def count(self) -> int:
        """Return the number of registered artifacts."""
        return len(self._artifacts)
