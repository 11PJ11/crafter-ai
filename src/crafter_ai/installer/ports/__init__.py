"""Ports (interfaces) for the installer hexagonal architecture."""

from crafter_ai.installer.ports.backup_port import (
    BackupInfo,
    BackupPort,
    BackupResult,
    CleanupResult,
    RestoreResult,
)
from crafter_ai.installer.ports.build_port import BuildError, BuildPort
from crafter_ai.installer.ports.config_port import ConfigPort
from crafter_ai.installer.ports.git_port import GitPort
from crafter_ai.installer.ports.pipx_port import (
    InstalledPackage,
    InstallResult,
    PipxPort,
    UninstallResult,
)


__all__ = [
    "BackupInfo",
    "BackupPort",
    "BackupResult",
    "BuildError",
    "BuildPort",
    "CleanupResult",
    "ConfigPort",
    "GitPort",
    "InstallResult",
    "InstalledPackage",
    "PipxPort",
    "RestoreResult",
    "UninstallResult",
]
