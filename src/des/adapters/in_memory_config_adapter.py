"""Backward compatibility import for InMemoryConfigAdapter.

Re-exports InMemoryConfigAdapter from driven adapters for backward compatibility with old import paths.
Old code using: from src.des.adapters.in_memory_config_adapter import InMemoryConfigAdapter
Will continue to work with this module.
"""

from src.des.adapters.driven.config.in_memory_config_adapter import InMemoryConfigAdapter

__all__ = ["InMemoryConfigAdapter"]
