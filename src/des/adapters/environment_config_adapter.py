"""Backward compatibility import for EnvironmentConfigAdapter.

Re-exports EnvironmentConfigAdapter from driven adapters for backward compatibility with old import paths.
Old code using: from src.des.adapters.environment_config_adapter import EnvironmentConfigAdapter
Will continue to work with this module.
"""

from src.des.adapters.driven.config.environment_config_adapter import EnvironmentConfigAdapter

__all__ = ["EnvironmentConfigAdapter"]
