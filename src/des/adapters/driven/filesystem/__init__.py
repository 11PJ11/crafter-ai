"""Filesystem driven adapters."""

from src.des.adapters.driven.filesystem.real_filesystem import RealFileSystem
from src.des.adapters.driven.filesystem.in_memory_filesystem import InMemoryFileSystem

# Backward compatibility alias
RealFilesystem = RealFileSystem

__all__ = ["RealFileSystem", "RealFilesystem", "InMemoryFileSystem"]
