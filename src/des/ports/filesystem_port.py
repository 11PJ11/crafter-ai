"""Backward compatibility import for FileSystemPort.

Re-exports FileSystemPort from driven_ports for backward compatibility with old import paths.
Old code using: from src.des.ports.filesystem_port import FileSystemPort
Will continue to work with this module.
"""

from src.des.ports.driven_ports.filesystem_port import FileSystemPort

__all__ = ["FileSystemPort"]
