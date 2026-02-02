"""ConfigPort Protocol - abstract interface for configuration access.

This is a hexagonal architecture port that defines how the application
accesses configuration. Adapters implement this protocol for different
storage mechanisms (file system, environment variables, etc.).
"""

from pathlib import Path
from typing import Protocol, runtime_checkable


@runtime_checkable
class ConfigPort(Protocol):
    """Protocol defining configuration access interface.

    This is a hexagonal port - the application depends on this interface,
    not on concrete implementations. Adapters (like FileConfigAdapter)
    implement this protocol.
    """

    def get_config_dir(self) -> Path:
        """Return the configuration directory path.

        Returns:
            Path to the configuration directory.
        """
        ...

    def get_data_dir(self) -> Path:
        """Return the data directory path.

        Returns:
            Path to the data directory.
        """
        ...

    def get_cache_dir(self) -> Path:
        """Return the cache directory path.

        Returns:
            Path to the cache directory.
        """
        ...

    def get_log_dir(self) -> Path:
        """Return the log directory path.

        Returns:
            Path to the log directory.
        """
        ...

    def get(self, key: str, default: str | None = None) -> str | None:
        """Get a configuration value by key.

        Args:
            key: The configuration key to retrieve.
            default: Default value if key doesn't exist.

        Returns:
            The configuration value, or default if not found.
        """
        ...

    def set(self, key: str, value: str) -> None:
        """Set a configuration value.

        Args:
            key: The configuration key.
            value: The value to set.
        """
        ...

    def load(self) -> dict[str, str]:
        """Load all configuration values.

        Returns:
            Dictionary of all configuration key-value pairs.
        """
        ...

    def save(self) -> None:
        """Persist configuration to storage."""
        ...
