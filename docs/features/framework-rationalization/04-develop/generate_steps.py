#!/usr/bin/env python3
"""
Generate 68 atomic step files from roadmap.yaml
Each step file follows the TDD cycle schema with 14 phases
"""

import json
import yaml
from pathlib import Path

# Load roadmap
roadmap_path = Path(__file__).parent / "roadmap.yaml"
with open(roadmap_path) as f:
    roadmap = yaml.safe_load(f)

# Output directory
steps_dir = Path(__file__).parent / "steps"
steps_dir.mkdir(exist_ok=True)

# 14-phase template
def create_phase_log_entry(phase_name, phase_index):
    return {
        "phase_name": phase_name,
        "phase_index": phase_index,
        "status": "NOT_EXECUTED",
        "started_at": None,
        "ended_at": None,
        "duration_minutes": None,
        "outcome": None,
        "outcome_details": None,
        "artifacts_created": [],
        "artifacts_modified": [],
        "test_results": {"total": None, "passed": None, "failed": None, "skipped": None},
        "notes": None,
        "blocked_by": None,
        "history": []
    }

# 14 mandatory phases
phases = [
    "PREPARE", "RED_ACCEPTANCE", "RED_UNIT", "GREEN_UNIT",
    "CHECK_ACCEPTANCE", "GREEN_ACCEPTANCE", "REVIEW",
    "REFACTOR_L1", "REFACTOR_L2", "REFACTOR_L3", "REFACTOR_L4",
    "POST_REFACTOR_REVIEW", "FINAL_VALIDATE", "COMMIT"
]

# Extract all steps from all phases
all_steps = []
for phase in roadmap['roadmap']['phases']:
    for group in phase['parallel_groups']:
        for step in group['steps']:
            all_steps.append({
                'phase_id': phase['phase_id'],
                'phase_name': phase['name'],
                'group_id': group['group_id'],
                'step': step
            })

print(f"Total steps found: {len(all_steps)}")

# Generate step files
for idx, step_data in enumerate(all_steps, 1):
    step = step_data['step']
    step_id = step['step_id']

    # Create step file content
    step_file = {
        "task_id": step_id,  # Use step_id as task_id
        "task_description": step['description'].strip(),
        "scenario": step['scenario'],
        "scenario_line": step['scenario_line'],
        "agent": step['agent'],
        "estimated_complexity": step['estimated_complexity'],
        "phase_id": step_data['phase_id'],
        "phase_name": step_data['phase_name'],
        "group_id": step_data['group_id'],
        "requires": step.get('depends_on', []),
        "acceptance_criteria": step['acceptance_criteria'],

        # TDD cycle configuration
        "tdd_cycle": {
            "acceptance_test": {
                "scenario_name": step['scenario'],
                "test_file": "tests/acceptance/acceptance-tests.feature",
                "test_file_format": "feature",
                "scenario_index": idx - 1,
                "initially_ignored": True,
                "is_walking_skeleton": False
            },
            "expected_unit_tests": [],
            "mock_boundaries": {
                "allowed_ports": [],
                "forbidden_domain_classes": [],
                "in_memory_adapters": []
            },
            "tdd_phase_tracking": {
                "current_phase": "NOT_STARTED",
                "active_e2e_test": "",
                "inactive_e2e_tests": "All other @skip scenarios remain disabled",
                "phases_completed": []
            },
            "phase_execution_log": [
                create_phase_log_entry(phase_name, i)
                for i, phase_name in enumerate(phases)
            ]
        },

        # Quality gates
        "quality_gates": {
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
            "phase_documentation_required": True
        },

        # Commit policy
        "commit_policy": "Commit ONLY after ALL 14 PHASES complete. AUTO-PUSH after commit."
    }

    # Write step file
    output_file = steps_dir / f"{step_id}.json"
    with open(output_file, 'w') as f:
        json.dump(step_file, f, indent=2)

    print(f"{idx}. Created: {output_file.name}")

print(f"\n✅ Successfully generated {len(all_steps)} step files")
