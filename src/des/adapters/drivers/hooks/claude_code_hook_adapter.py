#!/usr/bin/env python3
"""Stub Claude Code hook adapter for walking skeleton validation.

This is a minimal stub implementation to prove:
1. Claude Code can invoke Python scripts as hooks
2. JSON protocol works (stdin/stdout)
3. Exit codes work
4. Tool matchers work

This stub will be replaced with full DES implementation in step 02-02.
"""

import json
import sys


def main() -> None:
    """Stub hook adapter entry point."""
    try:
        # Read JSON from stdin
        input_data = sys.stdin.read()

        # Parse JSON (validates protocol works)
        if input_data.strip():
            json.loads(input_data)

        # Output success JSON with proof marker
        response = {
            "decision": "allow",
            "proof": "hook_fired"
        }

        print(json.dumps(response))
        sys.exit(0)

    except Exception as e:
        # Fail gracefully on any error
        error_response = {
            "status": "error",
            "reason": str(e)
        }
        print(json.dumps(error_response))
        sys.exit(1)


if __name__ == "__main__":
    main()
