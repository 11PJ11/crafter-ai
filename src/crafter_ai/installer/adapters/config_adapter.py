"""FileConfigAdapter - file-based implementation of ConfigPort.

This adapter implements the ConfigPort protocol using the file system
for configuration storage. It uses platformdirs for cross-platform
path resolution and YAML for configuration file format.
"""

import tempfile
from pathlib import Path
from typing import Any

import platformdirs
import yaml


class FileConfigAdapter:
    """File-based configuration adapter implementing ConfigPort.

    This adapter stores configuration in a YAML file and uses
    platformdirs for platform-specific directory paths.

    Attributes:
        _base_path: Optional override for base directory (for testing).
        _config: In-memory configuration cache.
        _loaded: Whether config has been loaded from disk.
    """

    APP_NAME = "crafter-ai"

    def __init__(self, base_path: Path | None = None) -> None:
        """Initialize the adapter.

        Args:
            base_path: Optional base path override for testing.
                      If None, uses platformdirs for system paths.
        """
        self._base_path = base_path
        self._config: dict[str, str] = {}
        self._loaded = False

    def get_config_dir(self) -> Path:
        """Return the configuration directory path.

        Creates the directory if it doesn't exist.

        Returns:
            Path to the configuration directory.
        """
        if self._base_path:
            path = self._base_path / "config"
        else:
            path = Path(platformdirs.user_config_dir(self.APP_NAME))
        path.mkdir(parents=True, exist_ok=True)
        return path

    def get_data_dir(self) -> Path:
        """Return the data directory path.

        Creates the directory if it doesn't exist.

        Returns:
            Path to the data directory.
        """
        if self._base_path:
            path = self._base_path / "data"
        else:
            path = Path(platformdirs.user_data_dir(self.APP_NAME))
        path.mkdir(parents=True, exist_ok=True)
        return path

    def get_cache_dir(self) -> Path:
        """Return the cache directory path.

        Creates the directory if it doesn't exist.

        Returns:
            Path to the cache directory.
        """
        if self._base_path:
            path = self._base_path / "cache"
        else:
            path = Path(platformdirs.user_cache_dir(self.APP_NAME))
        path.mkdir(parents=True, exist_ok=True)
        return path

    def get_log_dir(self) -> Path:
        """Return the log directory path.

        Creates the directory if it doesn't exist.

        Returns:
            Path to the log directory.
        """
        if self._base_path:
            path = self._base_path / "log"
        else:
            path = Path(platformdirs.user_log_dir(self.APP_NAME))
        path.mkdir(parents=True, exist_ok=True)
        return path

    def get(self, key: str, default: str | None = None) -> str | None:
        """Get a configuration value by key.

        Loads config lazily on first access.

        Args:
            key: The configuration key to retrieve.
            default: Default value if key doesn't exist.

        Returns:
            The configuration value, or default if not found.
        """
        self._ensure_loaded()
        return self._config.get(key, default)

    def set(self, key: str, value: str) -> None:
        """Set a configuration value.

        Args:
            key: The configuration key.
            value: The value to set.
        """
        self._ensure_loaded()
        self._config[key] = value

    def load(self) -> dict[str, str]:
        """Load all configuration values from disk.

        Returns:
            Dictionary of all configuration key-value pairs.
        """
        config_file = self.get_config_dir() / "config.yaml"
        if config_file.exists():
            with open(config_file, "r") as f:
                loaded: Any = yaml.safe_load(f)
                self._config = loaded if loaded else {}
        else:
            self._config = {}
        self._loaded = True
        return dict(self._config)

    def save(self) -> None:
        """Persist configuration to YAML file atomically.

        Writes to a temporary file first, then renames to ensure
        atomic write operation.
        """
        config_dir = self.get_config_dir()
        config_file = config_dir / "config.yaml"

        # Write atomically: write to temp file, then rename
        with tempfile.NamedTemporaryFile(
            mode="w",
            dir=config_dir,
            suffix=".yaml",
            delete=False,
        ) as tmp_file:
            yaml.safe_dump(self._config, tmp_file, default_flow_style=False)
            tmp_path = Path(tmp_file.name)

        # Atomic rename
        tmp_path.rename(config_file)

    def _ensure_loaded(self) -> None:
        """Ensure configuration is loaded from disk."""
        if not self._loaded:
            self.load()
