#!/usr/bin/env python3
"""
nWave Step File Migration Script

Migrates existing step files to include pre-populated 14-phase TDD execution log.

Usage:
    python migrate_step_files.py [--dry-run] [--backup] [path/to/steps/]

Options:
    --dry-run    Show what would be changed without modifying files
    --backup     Create .bak files before modifying
    path         Directory containing step files (default: auto-detect from docs/feature/*/steps/)

Exit Codes:
    0 - Success (all files migrated or already compliant)
    1 - Errors occurred during migration
    2 - No step files found
"""

import argparse
import glob
import json
import os
import shutil
import sys
from datetime import datetime
from typing import Any, Dict, List, Tuple


# Required TDD phases in order (14 total)
REQUIRED_PHASES = [
    "PREPARE",
    "RED_ACCEPTANCE",
    "RED_UNIT",
    "GREEN_UNIT",
    "CHECK_ACCEPTANCE",
    "GREEN_ACCEPTANCE",
    "REVIEW",
    "REFACTOR_L1",
    "REFACTOR_L2",
    "REFACTOR_L3",
    "REFACTOR_L4",
    "POST_REFACTOR_REVIEW",
    "FINAL_VALIDATE",
    "COMMIT",
]


def create_phase_skeleton() -> List[Dict[str, Any]]:
    """Create the pre-populated phase skeleton with all 14 phases."""
    return [
        {
            "phase_name": phase,
            "phase_index": i,
            "status": "NOT_EXECUTED",
            "started_at": None,
            "ended_at": None,
            "duration_minutes": None,
            "outcome": None,
            "outcome_details": None,
            "artifacts_created": [],
            "artifacts_modified": [],
            "test_results": {
                "total": None,
                "passed": None,
                "failed": None,
                "skipped": None,
            },
            "notes": None,
            "blocked_by": None,
            "history": [],
        }
        for i, phase in enumerate(REQUIRED_PHASES)
    ]


def needs_migration(step_data: Dict[str, Any]) -> Tuple[bool, str]:
    """
    Check if a step file needs migration.

    Returns:
        Tuple of (needs_migration, reason)
    """
    tdd_cycle = step_data.get("tdd_cycle", {})

    # Check if phase_execution_log exists
    phase_log = tdd_cycle.get("phase_execution_log", [])

    if not phase_log:
        # Check old location
        phase_log = tdd_cycle.get("tdd_phase_tracking", {}).get(
            "phase_execution_log", []
        )

    if not phase_log:
        return True, "No phase_execution_log found"

    if len(phase_log) < len(REQUIRED_PHASES):
        return True, f"Only {len(phase_log)} phases (need {len(REQUIRED_PHASES)})"

    # Check if all required phases are present
    phase_names = {p.get("phase_name") for p in phase_log}
    missing = set(REQUIRED_PHASES) - phase_names
    if missing:
        return True, f"Missing phases: {', '.join(sorted(missing))}"

    # Check if phases have required fields
    for phase in phase_log:
        if "history" not in phase:
            return True, f"Phase {phase.get('phase_name')} missing 'history' field"
        if "phase_index" not in phase:
            return True, f"Phase {phase.get('phase_name')} missing 'phase_index' field"

    return False, "Already compliant"


def migrate_step_file(step_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Migrate a step file to include pre-populated 14-phase skeleton.

    Preserves existing phase data while ensuring all 14 phases exist.
    """
    # Ensure tdd_cycle section exists
    if "tdd_cycle" not in step_data:
        step_data["tdd_cycle"] = {}

    tdd_cycle = step_data["tdd_cycle"]

    # Get existing phase log (check both locations)
    existing_log = tdd_cycle.get("phase_execution_log", [])
    if not existing_log:
        existing_log = tdd_cycle.get("tdd_phase_tracking", {}).get(
            "phase_execution_log", []
        )

    # Create new skeleton
    new_log = create_phase_skeleton()

    # Preserve existing phase data
    existing_by_name = {
        p.get("phase_name"): p for p in existing_log if p.get("phase_name")
    }

    for phase in new_log:
        phase_name = phase["phase_name"]
        if phase_name in existing_by_name:
            existing = existing_by_name[phase_name]
            # Merge existing data into new skeleton
            for key, value in existing.items():
                if value is not None and key != "phase_index":
                    phase[key] = value
            # Ensure history array exists
            if "history" not in phase:
                phase["history"] = []

    # Update tdd_cycle with new log
    tdd_cycle["phase_execution_log"] = new_log

    # Ensure tdd_phase_tracking exists with current_phase
    if "tdd_phase_tracking" not in tdd_cycle:
        tdd_cycle["tdd_phase_tracking"] = {}

    tracking = tdd_cycle["tdd_phase_tracking"]
    if "current_phase" not in tracking:
        tracking["current_phase"] = "NOT_STARTED"
    if "phases_completed" not in tracking:
        tracking["phases_completed"] = []

    # Remove old nested location if it exists
    if "phase_execution_log" in tracking:
        del tracking["phase_execution_log"]

    # Add quality_gates if missing
    if "quality_gates" not in step_data:
        step_data["quality_gates"] = {
            "acceptance_test_must_fail_first": True,
            "unit_tests_must_fail_first": True,
            "no_mocks_inside_hexagon": True,
            "business_language_required": True,
            "refactor_level": 4,
            "in_memory_test_ratio_target": 0.8,
            "validation_after_each_phase": True,
            "validation_after_each_review": True,
            "validation_after_each_refactor": True,
            "all_14_phases_mandatory": True,
            "phase_documentation_required": True,
        }

    # Add phase_validation_rules if missing
    if "phase_validation_rules" not in step_data:
        step_data["phase_validation_rules"] = {
            "description": "Rules for validating phase execution status before commit",
            "all_phases_required": True,
            "total_phases": 14,
            "valid_statuses": ["NOT_EXECUTED", "IN_PROGRESS", "EXECUTED", "SKIPPED"],
            "commit_acceptance_matrix": {
                "EXECUTED": {"allows_commit": True, "requires_outcome": True},
                "SKIPPED": {
                    "allows_commit": "conditional",
                    "requires_blocked_by": True,
                    "valid_blocked_by_prefixes": [
                        "BLOCKED_BY_DEPENDENCY:",
                        "NOT_APPLICABLE:",
                        "APPROVED_SKIP:",
                    ],
                    "blocks_commit_prefixes": ["DEFERRED:"],
                },
                "IN_PROGRESS": {"allows_commit": False},
                "NOT_EXECUTED": {"allows_commit": False},
            },
        }

    # Add migration metadata
    step_data["_migration"] = {
        "migrated_at": datetime.utcnow().isoformat() + "Z",
        "migrated_by": "migrate_step_files.py",
        "migration_version": "2.0.0",
        "previous_phase_count": len(existing_log),
    }

    return step_data


def find_step_files(base_path: str = ".") -> List[str]:
    """Find all step files in the project."""
    patterns = [
        os.path.join(base_path, "docs/feature/*/steps/*.json"),
        os.path.join(base_path, "docs/workflow/*/steps/*.json"),
        os.path.join(base_path, "steps/*.json"),
    ]

    step_files = []
    for pattern in patterns:
        step_files.extend(glob.glob(pattern))

    return sorted(set(step_files))


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Migrate step files to 14-phase TDD format",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be changed without modifying files",
    )
    parser.add_argument(
        "--backup", action="store_true", help="Create .bak files before modifying"
    )
    parser.add_argument(
        "path",
        nargs="?",
        default=".",
        help="Directory containing step files (default: auto-detect)",
    )

    args = parser.parse_args()

    print("nWave Step File Migration")
    print("=" * 50)

    # Find step files
    if os.path.isfile(args.path):
        step_files = [args.path]
    elif os.path.isdir(args.path):
        step_files = find_step_files(args.path)
    else:
        print(f"Error: Path not found: {args.path}", file=sys.stderr)
        return 1

    if not step_files:
        print("No step files found.")
        print("\nSearched patterns:")
        print("  - docs/feature/*/steps/*.json")
        print("  - docs/workflow/*/steps/*.json")
        print("  - steps/*.json")
        return 2

    print(f"\nFound {len(step_files)} step file(s)")

    if args.dry_run:
        print("\n[DRY RUN MODE - No files will be modified]\n")

    # Process each file
    migrated_count = 0
    skipped_count = 0
    error_count = 0

    for step_file in step_files:
        print(f"\nChecking: {step_file}")

        try:
            # Load step file
            with open(step_file, "r", encoding="utf-8") as f:
                step_data = json.load(f)

            # Check if migration needed
            needs_it, reason = needs_migration(step_data)

            if not needs_it:
                print(f"  [SKIP] {reason}")
                skipped_count += 1
                continue

            print(f"  [NEEDS MIGRATION] {reason}")

            if args.dry_run:
                print("  [DRY RUN] Would migrate this file")
                migrated_count += 1
                continue

            # Create backup if requested
            if args.backup:
                backup_path = step_file + ".bak"
                shutil.copy2(step_file, backup_path)
                print(f"  [BACKUP] Created {backup_path}")

            # Migrate
            migrated_data = migrate_step_file(step_data)

            # Write back (atomic: write to temp, then rename)
            temp_path = step_file + ".tmp"
            with open(temp_path, "w", encoding="utf-8") as f:
                json.dump(migrated_data, f, indent=2, ensure_ascii=False)
                f.write("\n")

            os.replace(temp_path, step_file)

            print("  [MIGRATED] Successfully updated")
            migrated_count += 1

        except json.JSONDecodeError as e:
            print(f"  [ERROR] Invalid JSON: {e}", file=sys.stderr)
            error_count += 1
        except Exception as e:
            print(f"  [ERROR] {e}", file=sys.stderr)
            error_count += 1

    # Summary
    print("\n" + "=" * 50)
    print("Migration Summary:")
    print(f"  - Total files: {len(step_files)}")
    print(f"  - Migrated: {migrated_count}")
    print(f"  - Already compliant: {skipped_count}")
    print(f"  - Errors: {error_count}")

    if args.dry_run:
        print("\n[DRY RUN] No files were modified.")
        print("Run without --dry-run to apply changes.")

    return 1 if error_count > 0 else 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\nInterrupted", file=sys.stderr)
        sys.exit(130)
