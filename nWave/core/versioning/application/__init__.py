"""
Application layer for versioning feature.

Contains application services that orchestrate domain logic
and coordinate with ports for external communication.
"""

from nWave.core.versioning.application.version_service import (
    VersionService,
    VersionCheckResult,
)

__all__ = ["VersionService", "VersionCheckResult"]
