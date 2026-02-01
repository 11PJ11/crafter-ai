"""
Plugin system for nWave framework installation.

Provides base classes and registry for modular component installation.
"""

from scripts.install.plugins.base import (
    InstallationPlugin,
    InstallContext,
    PluginResult,
)
from scripts.install.plugins.registry import PluginRegistry

__all__ = [
    "InstallationPlugin",
    "InstallContext",
    "PluginResult",
    "PluginRegistry",
]
