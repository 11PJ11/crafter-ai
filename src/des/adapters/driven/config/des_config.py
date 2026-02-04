"""
DES Configuration Adapter - Driven Port Implementation.

Loads configuration from ~/.claude/des/config.yaml and provides access to settings.
Falls back to safe defaults (audit logging enabled) when file is missing or invalid.

Hexagonal Architecture:
- DRIVEN ADAPTER: Implements configuration port (driven by business logic)
- SAFE DEFAULTS: Audit logging enabled by default for security
"""

from pathlib import Path
from typing import Any

import yaml


class DESConfig:
    """
    Configuration loader for DES settings.

    Loads configuration from ~/.claude/des/config.yaml with safe defaults.
    Creates default config file on first use with explanatory comments.
    """

    # Default configuration template
    _DEFAULT_CONFIG_TEMPLATE = """# DES (Deterministic Execution System) Configuration
# Created automatically on first use

# Audit Logging
# Controls whether hooks log execution to audit trail
# Default: true (recommended for production)
audit_logging_enabled: true

# Future settings can be added here
"""

    def __init__(self, config_path: Path | None = None):
        """
        Initialize DESConfig.

        Args:
            config_path: Optional path to config file (defaults to ~/.claude/des/config.yaml)
        """
        if config_path is None:
            home_dir = Path.home()
            config_path = home_dir / ".claude" / "des" / "config.yaml"

        self._config_path = config_path
        self._config_data = self._load_configuration()

    def _load_configuration(self) -> dict[str, Any]:
        """
        Load configuration from YAML file.

        Returns:
            Configuration dictionary with safe defaults if loading fails
        """
        # If config file doesn't exist, create it with defaults
        if not self._config_path.exists():
            return self._create_default_config()

        # Try to load existing config file
        try:
            with open(self._config_path) as f:
                config_data = yaml.safe_load(f)

            # Handle case where YAML is empty or invalid (returns None)
            if config_data is None:
                return self._get_safe_defaults()

            return config_data

        except yaml.YAMLError:
            # Invalid YAML - fall back to safe defaults without overwriting file
            return self._get_safe_defaults()

        except Exception:
            # Any other error - fall back to safe defaults
            return self._get_safe_defaults()

    def _create_default_config(self) -> dict[str, Any]:
        """
        Create default configuration file with explanatory comments.

        Returns:
            Default configuration dictionary
        """
        # Ensure parent directory exists
        self._config_path.parent.mkdir(parents=True, exist_ok=True)

        # Write default config template
        self._config_path.write_text(self._DEFAULT_CONFIG_TEMPLATE)

        # Return default configuration
        return self._get_safe_defaults()

    def _get_safe_defaults(self) -> dict[str, Any]:
        """
        Get safe default configuration values.

        Returns:
            Configuration dictionary with safe defaults
        """
        return {
            "audit_logging_enabled": True  # Safe default - audit logging enabled
        }

    @property
    def audit_logging_enabled(self) -> bool:
        """
        Check if audit logging is enabled.

        Returns:
            True if audit logging enabled, False otherwise (defaults to True)
        """
        return self._config_data.get("audit_logging_enabled", True)
