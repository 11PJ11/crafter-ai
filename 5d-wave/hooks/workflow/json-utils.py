#!/usr/bin/env python3
# AI-Craft Framework - Managed File
# Part of Claude Code SuperClaude modular hook system
"""
JSON utilities for Craft-AI hooks
Replaces jq commands for cross-platform compatibility
"""

import json
import os
import sys
from datetime import datetime


def load_json_safe(file_path, default=None):
    """Load JSON file safely, return default if file doesn't exist or invalid"""
    try:
        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                return json.load(f)
    except Exception:
        pass
    return default or {}


def get_json_field(file_path, field, default=""):
    """Get a field value from JSON file"""
    data = load_json_safe(file_path, {})
    return data.get(field, default)


def update_json_file(file_path, updates):
    """Update JSON file with new values"""
    # Ensure directory exists (only if file has a directory)
    dir_path = os.path.dirname(file_path)
    if dir_path:
        os.makedirs(dir_path, exist_ok=True)

    # Load existing data
    data = load_json_safe(file_path, {})

    # Apply updates
    data.update(updates)

    # Write back to file
    with open(file_path, "w") as f:
        json.dump(data, f, indent=2)


def update_pipeline_state(stage, agent):
    """Update pipeline state with new stage and agent"""
    state_file = "state/craft-ai/pipeline-state.json"
    updates = {
        "stage": stage,
        "agent": agent,
        "last_transition": datetime.now().isoformat(),
        "status": "active",
    }
    update_json_file(state_file, updates)


def update_wave_progress(stage, agent):
    """Update wave progress if file exists"""
    wave_file = "state/craft-ai/wave-progress.json"
    if os.path.exists(wave_file):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        updates = {
            "current_stage": stage,
            "current_agent": agent,
            "last_transition": timestamp,
        }
        update_json_file(wave_file, updates)


def main():
    """Command line interface for JSON operations"""
    if len(sys.argv) < 2:
        print("Usage: json-utils.py <command> [args...]", file=sys.stderr)
        sys.exit(1)

    command = sys.argv[1]

    try:
        if command == "get":
            # json-utils.py get <file> <field> [default]
            file_path = sys.argv[2]
            field = sys.argv[3]
            default = sys.argv[4] if len(sys.argv) > 4 else ""
            value = get_json_field(file_path, field, default)
            print(value)

        elif command == "update":
            # json-utils.py update <file> <field> <value>
            file_path = sys.argv[2]
            field = sys.argv[3]
            value = sys.argv[4]
            update_json_file(file_path, {field: value})

        elif command == "update-pipeline":
            # json-utils.py update-pipeline <stage> <agent>
            stage = sys.argv[2]
            agent = sys.argv[3]
            update_pipeline_state(stage, agent)

        elif command == "update-wave":
            # json-utils.py update-wave <stage> <agent>
            stage = sys.argv[2]
            agent = sys.argv[3]
            update_wave_progress(stage, agent)

        else:
            print(f"Unknown command: {command}", file=sys.stderr)
            sys.exit(1)

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
