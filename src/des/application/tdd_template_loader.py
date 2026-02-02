"""
TDD Template Loader - Single Source of Truth

Loads TDD phase definitions from canonical template (nWave/templates/step-tdd-cycle-schema.json)
instead of hardcoding them in validators/tests.

This ensures when template changes, all consumers update automatically.
"""

import json
from pathlib import Path
from typing import List, Dict
from functools import lru_cache

# Path to canonical template (relative to project root)
# __file__ = /mnt/c/.../ai-craft/src/des/application/tdd_template_loader.py
# parent = /mnt/c/.../ai-craft/src/des/application
# parent.parent = /mnt/c/.../ai-craft/src/des
# parent.parent.parent = /mnt/c/.../ai-craft/src
# parent.parent.parent.parent = /mnt/c/.../ai-craft (project root)
TEMPLATE_PATH = Path(__file__).parent.parent.parent.parent / "nWave" / "templates" / "step-tdd-cycle-schema.json"


@lru_cache(maxsize=1)
def load_tdd_template() -> dict:
    """
    Load canonical TDD template from JSON file.

    Cached for performance - template loaded once per process.

    Returns:
        dict: Complete template structure

    Raises:
        FileNotFoundError: If template not found at expected path
        json.JSONDecodeError: If template has invalid JSON
    """
    if not TEMPLATE_PATH.exists():
        raise FileNotFoundError(
            f"Canonical TDD template not found at: {TEMPLATE_PATH}. "
            f"Expected location: nWave/templates/step-tdd-cycle-schema.json"
        )

    with open(TEMPLATE_PATH, 'r') as f:
        return json.load(f)


def get_schema_version() -> str:
    """Get schema version from template."""
    template = load_tdd_template()
    return template.get("schema_version", "3.0")


def get_valid_tdd_phases() -> List[str]:
    """
    Get valid TDD phase names from canonical template.

    Excludes meta-phases (NOT_STARTED, COMPLETED).

    Returns:
        List of valid phase names for step execution:
        ["PREPARE", "RED_ACCEPTANCE", "RED_UNIT", "GREEN", "REVIEW", "REFACTOR_CONTINUOUS", "COMMIT"]
    """
    template = load_tdd_template()
    all_phases = template.get("valid_tdd_phases", [])

    # Exclude meta-phases (not actual execution phases)
    execution_phases = [p for p in all_phases if p not in ["NOT_STARTED", "COMPLETED"]]

    return execution_phases


def get_phase_execution_log_template() -> List[dict]:
    """
    Get phase execution log structure from template.

    Returns:
        List of phase definitions with metadata (phase_name, phase_index, notes, etc.)
    """
    template = load_tdd_template()
    return template.get("tdd_cycle", {}).get("phase_execution_log", [])


def get_expected_phase_count() -> int:
    """Get expected number of phases for current schema version."""
    return len(get_valid_tdd_phases())
