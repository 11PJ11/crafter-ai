"""Backward compatibility import for TimeProvider.

Re-exports TimeProvider from driven_ports for backward compatibility with old import paths.
Old code using: from src.des.ports.time_provider_port import TimeProvider
Will continue to work with this module.
"""

from src.des.ports.driven_ports.time_provider_port import TimeProvider

__all__ = ["TimeProvider"]
