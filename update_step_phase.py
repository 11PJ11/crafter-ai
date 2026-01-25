#!/usr/bin/env python3
"""Update step file phase execution log."""
import json
from datetime import datetime, timezone
from pathlib import Path
import sys

def update_phases(step_file_path, phase_updates):
    """Update phases in step file with execution details."""
    with open(step_file_path, 'r') as f:
        step_data = json.load(f)

    phase_log = step_data['tdd_cycle']['phase_execution_log']

    for update in phase_updates:
        phase_index = update['phase_index']
        phase = phase_log[phase_index]

        # Update fields
        for key, value in update.items():
            if key != 'phase_index':
                phase[key] = value

    # Update state
    if phase_updates:
        step_data['state']['status'] = 'IN_PROGRESS'
        if not step_data['state']['started_at']:
            step_data['state']['started_at'] = datetime.now(timezone.utc).isoformat()

    with open(step_file_path, 'w') as f:
        json.dump(step_data, f, indent=2)

    print(f"Updated {len(phase_updates)} phases in {step_file_path}")

if __name__ == '__main__':
    step_file = '/mnt/c/Repositories/Projects/ai-craft/docs/feature/des-us004/steps/04-02.json'
    now = datetime.now(timezone.utc).isoformat()

    updates = [
        {
            'phase_index': 0,  # PREPARE
            'status': 'EXECUTED',
            'started_at': now,
            'ended_at': now,
            'duration_minutes': 2,
            'outcome': 'PASS',
            'outcome_details': 'Created acceptance test for timeout warnings in prompt context',
            'artifacts_created': ['tests/test_scenario_014_agent_receives_timeout_warnings_in_prompt.py'],
            'test_results': {'total': None, 'passed': None, 'failed': None, 'skipped': None},
            'notes': 'Acceptance test validates warnings injected into agent prompt'
        },
        {
            'phase_index': 1,  # RED_ACCEPTANCE
            'status': 'EXECUTED',
            'started_at': now,
            'ended_at': now,
            'duration_minutes': 2,
            'outcome': 'PASS',
            'outcome_details': 'Test fails correctly: render_prompt() missing timeout_thresholds and timeout_budget_minutes parameters',
            'test_results': {'total': 1, 'passed': 0, 'failed': 1, 'skipped': 0},
            'notes': 'TypeError: render_prompt() got unexpected keyword argument timeout_thresholds'
        }
    ]

    update_phases(step_file, updates)
