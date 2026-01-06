#!/usr/bin/env python3
"""
Apply adversarial review corrections to step files systematically.
Usage: python apply_corrections.py
"""

import json
from pathlib import Path
from typing import Dict, Any

def deep_merge(base: Dict[Any, Any], updates: Dict[Any, Any]) -> Dict[Any, Any]:
    """Deep merge updates dict into base dict."""
    result = base.copy()
    for key, value in updates.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value
    return result

def apply_phase1_blocker(step_file: Path) -> None:
    """Apply BLOCKER_001 and prerequisites to Phase 1 steps."""
    with open(step_file) as f:
        data = json.load(f)

    blocker = {
        "critical_blocker_status": {
            "BLOCKER_001": {
                "title": "TOON Toolchain Missing",
                "status": "UNRESOLVED",
                "evidence": "tools/toon/ directory does not exist",
                "impact": "Cannot parse TOON files, blocks all Phase 1 steps",
                "resolution_options": [
                    "A: Implement TOON toolchain (16-20h estimated)",
                    "B: Pivot to Markdown templates (8-10h, loses TOON benefits)",
                    "C: Block until external TOON library available"
                ]
            }
        },
        "prerequisites": {
            "blocking": [
                "tools/toon/ directory MUST exist with README.md",
                "TOON format specification v3.0 must be accessible",
                "Parser output schema must be defined before template implementation"
            ],
            "validation": "Run: ls tools/toon/README.md. Must exist. If not: BLOCKER_001"
        }
    }

    data = deep_merge(data, blocker)

    with open(step_file, 'w') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def apply_phase1_time_estimates(step_file: Path, new_hours: str) -> None:
    """Update time estimates for Phase 1 steps."""
    with open(step_file) as f:
        data = json.load(f)

    data["step"]["estimated_hours"] = new_hours

    with open(step_file, 'w') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def update_agent_count(step_file: Path, old_count: str = "28", new_count: str = "26") -> None:
    """Replace agent count references in Phase 7 steps."""
    with open(step_file) as f:
        content = f.read()

    # Replace all instances of "28 agents" with "26 agents (novel-editor and novel-editor-reviewer excluded from build)"
    replacement = "26 agents (novel-editor and novel-editor-reviewer excluded from build)"
    content = content.replace(f"{old_count} agents", replacement)

    with open(step_file, 'w') as f:
        f.write(content)

def add_prerequisite_workflow(step_file: Path) -> None:
    """Add prerequisite check to workflow for Phase 1 steps."""
    with open(step_file) as f:
        data = json.load(f)

    if "execution_guidance" in data and "workflow" in data["execution_guidance"]:
        workflow = data["execution_guidance"]["workflow"]
        if isinstance(workflow, list) and len(workflow) > 0:
            # Add prerequisite check as first step
            new_first_step = "0. PREREQUISITE CHECK: Verify tools/toon/ exists. If not: HALT - refer to BLOCKER_001 resolution"
            # Only add if not already present
            if not any("PREREQUISITE CHECK" in step for step in workflow):
                workflow.insert(0, new_first_step)
                data["execution_guidance"]["workflow"] = workflow

    with open(step_file, 'w') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def main():
    """Apply all corrections systematically."""
    base_path = Path("/mnt/c/Repositories/Projects/ai-craft/docs/workflow/plugin-marketplace-migration/steps")

    print("Applying Phase 1 corrections...")

    # Phase 1: Time estimates already corrected for 01-01 and 01-02
    # Apply to 01-03 through 01-06
    phase1_time_updates = {
        "01-03.json": "3-4",
        "01-04.json": "4-6"
    }

    for filename, new_hours in phase1_time_updates.items():
        step_file = base_path / filename
        if step_file.exists():
            print(f"  Updating {filename} time estimate to {new_hours}h...")
            apply_phase1_time_estimates(step_file, new_hours)
            apply_phase1_blocker(step_file)
            add_prerequisite_workflow(step_file)

    # Apply blocker to 01-05 and 01-06 (they already have good structure)
    for filename in ["01-05.json", "01-06.json"]:
        step_file = base_path / filename
        if step_file.exists():
            print(f"  Adding blocker to {filename}...")
            apply_phase1_blocker(step_file)
            add_prerequisite_workflow(step_file)

    print("\nApplying Phase 7 agent count corrections...")
    for filename in ["07-01.json", "07-02.json", "07-03.json"]:
        step_file = base_path / filename
        if step_file.exists():
            print(f"  Correcting agent count in {filename}...")
            update_agent_count(step_file)

    print("\nCorrections application complete!")
    print("Note: Phase 4 and Phase 6 corrections require manual review due to complexity")

if __name__ == "__main__":
    main()
