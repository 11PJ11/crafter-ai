"""Domain layer for the crafter-ai installer.

This package contains pure domain objects with no external dependencies.
"""

from .artifact_registry import ArtifactRegistry
from .candidate_version import (
    BumpType,
    CandidateVersion,
    calculate_next_version,
    create_candidate,
    parse_version,
)
from .check_executor import CheckExecutor
from .check_registry import CheckRegistry
from .check_result import CheckResult, CheckSeverity
from .health_checker import HealthChecker
from .health_result import HealthResult, HealthStatus


__all__ = [
    "ArtifactRegistry",
    "BumpType",
    "CandidateVersion",
    "CheckExecutor",
    "CheckRegistry",
    "CheckResult",
    "CheckSeverity",
    "HealthChecker",
    "HealthResult",
    "HealthStatus",
    "calculate_next_version",
    "create_candidate",
    "parse_version",
]
