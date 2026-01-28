"""
Infrastructure adapters for versioning.

Contains concrete implementations of ports for external systems.
"""

from nWave.infrastructure.versioning.git_adapter import GitAdapter
from nWave.infrastructure.versioning.github_cli_adapter import GitHubCLIAdapter

__all__ = ["GitAdapter", "GitHubCLIAdapter"]
