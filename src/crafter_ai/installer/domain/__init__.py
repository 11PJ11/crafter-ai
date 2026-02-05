"""Domain layer for the crafter-ai installer.

This package contains pure domain objects with no external dependencies.
"""

from .artifact_registry import ArtifactRegistry
from .asset_deployment_result import AssetDeploymentResult
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
from .deployment_validation_result import DeploymentValidationResult
from .health_checker import HealthChecker
from .health_result import HealthResult, HealthStatus
from .ide_bundle_build_result import IdeBundleBuildResult
from .ide_bundle_constants import (
    AGENTS_SUBDIR,
    BUILD_AGENTS_SUBDIR,
    BUILD_COMMANDS_SUBDIR,
    BUILD_SCRIPTS_SUBDIR,
    BUILD_TEMPLATES_SUBDIR,
    COMMANDS_SUBDIR,
    DEFAULT_DEPLOY_TARGET,
    DEFAULT_OUTPUT_DIR,
    DEFAULT_SOURCE_DIR,
    DEPLOY_AGENTS_SUBDIR,
    DEPLOY_COMMANDS_SUBDIR,
    DEPLOY_SCRIPTS_SUBDIR,
    DEPLOY_TEMPLATES_SUBDIR,
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


__all__ = [
    "AGENTS_SUBDIR",
    "BUILD_AGENTS_SUBDIR",
    "BUILD_COMMANDS_SUBDIR",
    "BUILD_SCRIPTS_SUBDIR",
    "BUILD_TEMPLATES_SUBDIR",
    "COMMANDS_SUBDIR",
    "DEFAULT_DEPLOY_TARGET",
    "DEFAULT_OUTPUT_DIR",
    "DEFAULT_SOURCE_DIR",
    "DEPLOY_AGENTS_SUBDIR",
    "DEPLOY_COMMANDS_SUBDIR",
    "DEPLOY_SCRIPTS_SUBDIR",
    "DEPLOY_TEMPLATES_SUBDIR",
    "EXPECTED_AGENT_COUNT",
    "EXPECTED_COMMAND_COUNT",
    "EXPECTED_SCHEMA_PHASES",
    "EXPECTED_SCHEMA_VERSION",
    "EXPECTED_SCRIPT_COUNT",
    "EXPECTED_TEAM_COUNT",
    "EXPECTED_TEMPLATE_COUNT",
    "SCRIPTS_SUBDIR",
    "TEMPLATES_SUBDIR",
    "ArtifactRegistry",
    "AssetDeploymentResult",
    "BumpType",
    "CandidateVersion",
    "CheckExecutor",
    "CheckRegistry",
    "CheckResult",
    "CheckSeverity",
    "DeploymentValidationResult",
    "HealthChecker",
    "HealthResult",
    "HealthStatus",
    "IdeBundleBuildResult",
    "calculate_next_version",
    "create_candidate",
    "parse_version",
]
