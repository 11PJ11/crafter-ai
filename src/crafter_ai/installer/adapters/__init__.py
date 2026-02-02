"""Adapters (implementations) for the installer hexagonal architecture."""

from crafter_ai.installer.adapters.build_adapter import SubprocessBuildAdapter
from crafter_ai.installer.adapters.config_adapter import FileConfigAdapter
from crafter_ai.installer.adapters.git_adapter import SubprocessGitAdapter
from crafter_ai.installer.adapters.pipx_adapter import SubprocessPipxAdapter


__all__ = [
    "FileConfigAdapter",
    "SubprocessBuildAdapter",
    "SubprocessGitAdapter",
    "SubprocessPipxAdapter",
]
