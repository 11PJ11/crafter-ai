#!/usr/bin/env python3
"""Update COMMIT phase with git commit hash."""

import json
import sys
from datetime import datetime, timezone
import subprocess


def get_latest_commit_hash():
    """Get the latest git commit hash."""
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"], capture_output=True, text=True
    )
    return result.stdout.strip()


def update_commit_phase(step_file, phase_index, commit_hash):
    """Update COMMIT phase with commit hash."""
    with open(step_file, "r") as f:
        data = json.load(f)

    phase = data["tdd_cycle"]["phase_execution_log"][phase_index]
    now = datetime.now(timezone.utc).isoformat()

    if phase["started_at"] is None:
        phase["started_at"] = now
    phase["ended_at"] = now

    # Calculate duration
    start = datetime.fromisoformat(phase["started_at"])
    end = datetime.fromisoformat(phase["ended_at"])
    duration = (end - start).total_seconds() / 60
    phase["duration_minutes"] = round(duration, 2)

    phase["status"] = "EXECUTED"
    phase["outcome"] = "PASS"
    phase["outcome_details"] = f"Step committed successfully - {commit_hash[:8]}"
    phase["notes"] = f"Git commit: {commit_hash}"

    # Update execution result
    data["execution_result"]["commit_hash"] = commit_hash

    with open(step_file, "w") as f:
        json.dump(data, f, indent=2)

    print(f"Updated phase {phase_index}: COMMIT -> EXECUTED/PASS ({commit_hash[:8]})")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: update_commit_phase.py <step_file>")
        sys.exit(1)

    step_file = sys.argv[1]
    commit_hash = get_latest_commit_hash()

    # COMMIT phase is always index 13
    update_commit_phase(step_file, 13, commit_hash)
