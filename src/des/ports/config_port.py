"""Backward compatibility import for ConfigPort.

Re-exports ConfigPort from driven_ports for backward compatibility with old import paths.
Old code using: from src.des.ports.config_port import ConfigPort
Will continue to work with this module.
"""

from src.des.ports.driven_ports.config_port import ConfigPort

__all__ = ["ConfigPort"]
