#!/usr/bin/env python3
"""Update phase execution log in step file."""

import json
import sys
from datetime import datetime, timezone


def update_phase(step_file, phase_index, status, outcome, outcome_details, notes=None):
    """Update a specific phase in the step file."""
    with open(step_file, "r") as f:
        data = json.load(f)

    phase = data["tdd_cycle"]["phase_execution_log"][phase_index]
    now = datetime.now(timezone.utc).isoformat()

    if status == "EXECUTED":
        if phase["started_at"] is None:
            phase["started_at"] = now
        phase["ended_at"] = now

        # Calculate duration
        start = datetime.fromisoformat(phase["started_at"])
        end = datetime.fromisoformat(phase["ended_at"])
        duration = (end - start).total_seconds() / 60
        phase["duration_minutes"] = round(duration, 2)

    phase["status"] = status
    phase["outcome"] = outcome
    phase["outcome_details"] = outcome_details
    if notes:
        phase["notes"] = notes

    with open(step_file, "w") as f:
        json.dump(data, f, indent=2)

    print(f"Updated phase {phase_index}: {phase['phase_name']} -> {status}/{outcome}")


if __name__ == "__main__":
    if len(sys.argv) < 6:
        print(
            "Usage: update_phase.py <step_file> <phase_index> <status> <outcome> <outcome_details> [notes]"
        )
        sys.exit(1)

    step_file = sys.argv[1]
    phase_index = int(sys.argv[2])
    status = sys.argv[3]
    outcome = sys.argv[4]
    outcome_details = sys.argv[5]
    notes = sys.argv[6] if len(sys.argv) > 6 else None

    update_phase(step_file, phase_index, status, outcome, outcome_details, notes)
