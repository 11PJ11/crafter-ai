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
EXPECTED_TEMPLATE_COUNT = 17
EXPECTED_SCRIPT_COUNT = 4
EXPECTED_TEAM_COUNT = 0

# --- Schema expectations ---

EXPECTED_SCHEMA_VERSION = "v3.0"
EXPECTED_SCHEMA_PHASES = 7

# --- Directory paths ---

DEFAULT_SOURCE_DIR = Path("nWave")
DEFAULT_OUTPUT_DIR = Path("dist/ide")
DEFAULT_DEPLOY_TARGET = Path.home() / ".claude"

# --- Subdirectory layout within the bundle ---

AGENTS_SUBDIR = "agents/nw"
COMMANDS_SUBDIR = "commands/nw"
TEMPLATES_SUBDIR = "templates"
SCRIPTS_SUBDIR = "scripts"
