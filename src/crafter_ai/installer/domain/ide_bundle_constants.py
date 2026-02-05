"""IDE bundle constants for the unified install pipeline.

Single source of truth for expected artifact counts, schema version,
and directory paths used by the IDE bundle build and deployment services.
These are pure domain constants with no external dependencies beyond pathlib.

ADR-003: Prevents magic number drift by centralizing all counts here.
All services and tests that reference these values must import from this module.
"""

from pathlib import Path


# --- Expected artifact counts (source: journey-forge-tui.yaml) ---

EXPECTED_AGENT_COUNT = 30
EXPECTED_COMMAND_COUNT = 23
EXPECTED_TEMPLATE_COUNT = 16
EXPECTED_SCRIPT_COUNT = 2
EXPECTED_TEAM_COUNT = 0

# --- Schema expectations ---

EXPECTED_SCHEMA_VERSION = "v3.0"
EXPECTED_SCHEMA_PHASES = 7

# --- Directory paths ---

DEFAULT_SOURCE_DIR = Path("nWave")
DEFAULT_OUTPUT_DIR = Path("dist/ide")
DEFAULT_DEPLOY_TARGET = Path.home() / ".claude"

# --- Build subdirectory layout (source paths in nWave/) ---
# These paths are used by IdeBundleBuildService to scan nWave/ source

BUILD_AGENTS_SUBDIR = "agents"
BUILD_COMMANDS_SUBDIR = "tasks/nw"
BUILD_TEMPLATES_SUBDIR = "templates"
BUILD_SCRIPTS_SUBDIR = "scripts/des"  # Scripts live in nested des/ subdirectory

# --- Deployment subdirectory layout (destination paths in ~/.claude/) ---
# These paths are used by AssetDeploymentService for final deployment

DEPLOY_AGENTS_SUBDIR = "agents/nw"
DEPLOY_COMMANDS_SUBDIR = "commands/nw"
DEPLOY_TEMPLATES_SUBDIR = "templates"
DEPLOY_SCRIPTS_SUBDIR = "scripts"

# --- Legacy constants (deprecated, use BUILD_* or DEPLOY_* instead) ---

AGENTS_SUBDIR = BUILD_AGENTS_SUBDIR
COMMANDS_SUBDIR = BUILD_COMMANDS_SUBDIR
TEMPLATES_SUBDIR = BUILD_TEMPLATES_SUBDIR
SCRIPTS_SUBDIR = BUILD_SCRIPTS_SUBDIR
