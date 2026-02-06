"""
TDD Template Loader - Single Source of Truth

Loads TDD phase definitions from canonical template (nWave/templates/step-tdd-cycle-schema.json)
instead of hardcoding them in validators/tests.

This ensures when template changes, all consumers update automatically.
"""

import json
from functools import lru_cache
from pathlib import Path


# Path to canonical template
# Environment-aware: works in both source and installed locations
#
# Source location:
#   __file__ = /mnt/c/.../ai-craft/src/des/application/tdd_template_loader.py
#   Resolves to: /mnt/c/.../ai-craft/nWave/templates/step-tdd-cycle-schema.json
#
# Installed location:
#   __file__ = ~/.claude/lib/python/des/application/tdd_template_loader.py
#   Resolves to: ~/.claude/templates/step-tdd-cycle-schema.json


def _get_template_path() -> Path:
    """Resolve template path for current environment.

    Handles both:
    - Symlink paths: /home/user/.claude/lib/python/des/...
    - Real paths: /mnt/c/Users/user/.claude/lib/python/des/...
    - Source paths: /path/to/project/src/des/...
    """
    import sys
    module_file = Path(__file__)

    # Debug output
    print(f"[DEBUG tdd_template_loader] __file__: {module_file}", file=sys.stderr)
    print(f"[DEBUG tdd_template_loader] __file__.resolve(): {module_file.resolve()}", file=sys.stderr)

    # Check both symlink and resolved paths for .claude
    module_str = str(module_file)
    module_resolved_str = str(module_file.resolve())

    # Detect installed location by checking for .claude AND lib/python/des in path
    is_installed = (
        (".claude" in module_str or ".claude" in module_resolved_str) and
        ("lib/python/des" in module_str or "lib/python/des" in module_resolved_str)
    )

    print(f"[DEBUG tdd_template_loader] is_installed: {is_installed}", file=sys.stderr)

    if is_installed:
        # Installed location - find .claude directory in parents
        # Check both symlink and resolved paths
        for search_path in [module_file, module_file.resolve()]:
            print(f"[DEBUG tdd_template_loader] Searching path: {search_path}", file=sys.stderr)
            for parent in search_path.parents:
                print(f"[DEBUG tdd_template_loader]   Checking parent: {parent} (name='{parent.name}')", file=sys.stderr)
                # Match if parent name is exactly .claude OR path ends with .claude
                if parent.name == ".claude" or str(parent).endswith("/.claude") or str(parent).endswith("\\.claude"):
                    template_path = parent / "templates" / "step-tdd-cycle-schema.json"
                    print(f"[DEBUG tdd_template_loader]   Found .claude! Template path: {template_path}", file=sys.stderr)
                    print(f"[DEBUG tdd_template_loader]   Exists: {template_path.exists()}", file=sys.stderr)
                    if template_path.exists():
                        return template_path
                    # Try resolved version too
                    template_path_resolved = parent.resolve() / "templates" / "step-tdd-cycle-schema.json"
                    print(f"[DEBUG tdd_template_loader]   Trying resolved: {template_path_resolved}", file=sys.stderr)
                    print(f"[DEBUG tdd_template_loader]   Exists: {template_path_resolved.exists()}", file=sys.stderr)
                    if template_path_resolved.exists():
                        return template_path_resolved

    # Source location: navigate to project root
    # __file__/../../../../nWave/templates/step-tdd-cycle-schema.json
    fallback_path = (
        module_file.parent.parent.parent.parent
        / "nWave"
        / "templates"
        / "step-tdd-cycle-schema.json"
    )
    print(f"[DEBUG tdd_template_loader] Fallback to source mode: {fallback_path}", file=sys.stderr)
    return fallback_path


# For backward compatibility - template path is now evaluated lazily
# instead of at module import time
def get_template_path() -> Path:
    """Get template path (lazily evaluated at call time)."""
    return _get_template_path()


# Deprecated: TEMPLATE_PATH constant removed - use get_template_path() instead
# This ensures path resolution works correctly in installed location
TEMPLATE_PATH = None  # Kept for API compatibility but not used


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
    template_path = _get_template_path()
    if not template_path.exists():
        raise FileNotFoundError(
            f"Canonical TDD template not found at: {template_path}. "
            f"Expected location: nWave/templates/step-tdd-cycle-schema.json"
        )

    with open(template_path) as f:
        return json.load(f)


def get_schema_version() -> str:
    """Get schema version from template."""
    template = load_tdd_template()
    return template.get("schema_version", "3.0")


def get_valid_tdd_phases() -> list[str]:
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


def get_phase_execution_log_template() -> list[dict]:
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
