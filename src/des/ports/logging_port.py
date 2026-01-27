"""Backward compatibility import for LoggingPort.

Re-exports LoggingPort from driven_ports for backward compatibility with old import paths.
Old code using: from src.des.ports.logging_port import LoggingPort
Will continue to work with this module.
"""

from src.des.ports.driven_ports.logging_port import LoggingPort

__all__ = ["LoggingPort"]
