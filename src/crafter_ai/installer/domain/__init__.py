"""Domain layer for the crafter-ai installer.

This package contains pure domain objects with no external dependencies.
"""

from .artifact_registry import ArtifactRegistry
from .asset_deployment_result import AssetDeploymentResult
from .deployment_validation_result import DeploymentValidationResult
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
from .ide_bundle_constants import (
    AGENTS_SUBDIR,
    COMMANDS_SUBDIR,
    DEFAULT_DEPLOY_TARGET,
    DEFAULT_OUTPUT_DIR,
    DEFAULT_SOURCE_DIR,
    EXPECTED_AGENT_COUNT,
    EXPECTED_COMMAND_COUNT,
    EXPECTED_SCHEMA_PHASES,
    EXPECTED_SCHEMA_VERSION,
    EXPECTED_SCRIPT_COUNT,
    EXPECTED_TEAM_COUNT,
    EXPECTED_TEMPLATE_COUNT,
    SCRIPTS_SUBDIR,
    TEMPLATES_SUBDIR,
)
from .health_result import HealthResult, HealthStatus
from .ide_bundle_build_result import IdeBundleBuildResult


__all__ = [
    "AGENTS_SUBDIR",
    "ArtifactRegistry",
    "AssetDeploymentResult",
    "DeploymentValidationResult",
    "BumpType",
    "COMMANDS_SUBDIR",
    "CandidateVersion",
    "CheckExecutor",
    "CheckRegistry",
    "CheckResult",
    "CheckSeverity",
    "DEFAULT_DEPLOY_TARGET",
    "DEFAULT_OUTPUT_DIR",
    "DEFAULT_SOURCE_DIR",
    "EXPECTED_AGENT_COUNT",
    "EXPECTED_COMMAND_COUNT",
    "EXPECTED_SCHEMA_PHASES",
    "EXPECTED_SCHEMA_VERSION",
    "EXPECTED_SCRIPT_COUNT",
    "EXPECTED_TEAM_COUNT",
    "EXPECTED_TEMPLATE_COUNT",
    "HealthChecker",
    "HealthResult",
    "HealthStatus",
    "IdeBundleBuildResult",
    "SCRIPTS_SUBDIR",
    "TEMPLATES_SUBDIR",
    "calculate_next_version",
    "create_candidate",
    "parse_version",
]
