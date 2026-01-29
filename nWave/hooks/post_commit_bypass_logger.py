#!/usr/bin/env python3
"""
nWave-TDD-BYPASS-DETECTOR
Post-commit hook to detect and log when pre-commit validation was bypassed.

This hook runs after every commit and checks if the pre-commit validation
marker file exists. If it doesn't exist for a commit that includes step files,
it means --no-verify was used to bypass validation.

Cross-platform: Works on Windows, Mac, and Linux.
No external dependencies beyond Python standard library.

Installed alongside pre_commit_tdd_phases.py by /nw:develop command.
"""

import json
import os
import re
import subprocess
import sys
from datetime import datetime
from typing import Dict, List, Optional


# Configuration
VALIDATION_MARKER_FILE = ".git/nwave-validation-marker"
BYPASS_LOG_FILE = ".git/nwave-bypass.log"


def get_git_info() -> Dict[str, str]:
    """Get current git user, branch, and commit information."""
    info = {
        "user": "unknown",
        "email": "unknown",
        "branch": "unknown",
        "commit_hash": "unknown",
        "commit_message": "",
    }

    try:
        result = subprocess.run(
            ["git", "config", "user.name"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0:
            info["user"] = result.stdout.strip() or "unknown"

        result = subprocess.run(
            ["git", "config", "user.email"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0:
            info["email"] = result.stdout.strip() or "unknown"

        result = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0:
            info["branch"] = result.stdout.strip() or "unknown"

        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0:
            info["commit_hash"] = result.stdout.strip()[:12] or "unknown"

        result = subprocess.run(
            ["git", "log", "-1", "--format=%s"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0:
            info["commit_message"] = result.stdout.strip()[:100]

    except Exception:
        pass

    return info


def get_committed_step_files() -> List[str]:
    """Get list of step files in the most recent commit."""
    try:
        result = subprocess.run(
            ["git", "diff-tree", "--no-commit-id", "--name-only", "-r", "HEAD"],
            capture_output=True,
            text=True,
            check=True,
            timeout=10,
        )
        files = result.stdout.strip().split("\n")

        # Filter for step files
        step_patterns = [
            re.compile(r"steps/\d+-\d+\.json$"),
            re.compile(r"steps/step-\d+-\d+\.json$"),
            re.compile(r"docs/.*/steps/\d+-\d+\.json$"),
        ]

        step_files = []
        for f in files:
            if f and any(pattern.search(f) for pattern in step_patterns):
                step_files.append(f)

        return step_files
    except Exception:
        return []


def check_validation_marker() -> Optional[Dict]:
    """
    Check if validation marker exists and is recent.

    Returns:
        Marker data if valid, None if missing or stale
    """
    try:
        if not os.path.exists(VALIDATION_MARKER_FILE):
            return None

        with open(VALIDATION_MARKER_FILE, "r", encoding="utf-8") as f:
            marker_data = json.load(f)

        # Check if marker is recent (within last 5 minutes)
        timestamp_str = marker_data.get("timestamp", "")
        if timestamp_str:
            marker_time = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
            now = datetime.now(marker_time.tzinfo)
            age_seconds = (now - marker_time).total_seconds()

            # If marker is older than 5 minutes, consider it stale
            if age_seconds > 300:
                return None

        return marker_data
    except Exception:
        return None


def log_bypass(step_files: List[str], reason: str) -> None:
    """Log a bypass event."""
    try:
        git_info = get_git_info()

        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "event": "BYPASS_DETECTED",
            "reason": reason,
            "user": git_info["user"],
            "email": git_info["email"],
            "branch": git_info["branch"],
            "commit_hash": git_info["commit_hash"],
            "commit_message": git_info["commit_message"],
            "step_files": step_files,
            "severity": "WARNING",
        }

        # Ensure directory exists
        log_dir = os.path.dirname(BYPASS_LOG_FILE)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)

        with open(BYPASS_LOG_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry) + "\n")

        # Print warning to stderr
        print(f"\n{'=' * 60}", file=sys.stderr)
        print("  WARNING: Pre-commit validation was bypassed!", file=sys.stderr)
        print(f"{'=' * 60}", file=sys.stderr)
        print(f"  Reason: {reason}", file=sys.stderr)
        print(f"  User: {git_info['user']} <{git_info['email']}>", file=sys.stderr)
        print(f"  Branch: {git_info['branch']}", file=sys.stderr)
        print(f"  Commit: {git_info['commit_hash']}", file=sys.stderr)
        print(f"  Step files: {', '.join(step_files)}", file=sys.stderr)
        print(f"\n  This bypass has been logged to: {BYPASS_LOG_FILE}", file=sys.stderr)
        print(f"{'=' * 60}\n", file=sys.stderr)

    except Exception as e:
        print(f"Warning: Could not log bypass: {e}", file=sys.stderr)


def cleanup_marker() -> None:
    """Remove the validation marker file after checking."""
    try:
        if os.path.exists(VALIDATION_MARKER_FILE):
            os.unlink(VALIDATION_MARKER_FILE)
    except Exception:
        pass


def main() -> int:
    """Main entry point."""
    # Get step files in this commit
    step_files = get_committed_step_files()

    if not step_files:
        # No step files in commit - nothing to check
        cleanup_marker()
        return 0

    # Check validation marker
    marker = check_validation_marker()

    if marker is None:
        # No marker found - pre-commit hook was bypassed
        log_bypass(
            step_files, "Pre-commit hook bypassed (--no-verify or hook not installed)"
        )
    elif not marker.get("validation_passed", False):
        # Marker exists but validation failed - this shouldn't happen normally
        # (pre-commit would block), so likely a race condition or manual file edit
        log_bypass(step_files, "Validation marker indicates failed validation")
    else:
        # Validation passed - check if the same files were validated
        validated_files = set(marker.get("step_files_validated", []))
        committed_files = set(step_files)

        unvalidated = committed_files - validated_files
        if unvalidated:
            log_bypass(
                list(unvalidated),
                f"Step files committed without validation: {', '.join(unvalidated)}",
            )

    # Clean up marker
    cleanup_marker()

    # Post-commit hook should always return 0 (commit already done)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        sys.exit(0)
    except Exception as e:
        print(f"Post-commit hook error: {e}", file=sys.stderr)
        sys.exit(0)  # Don't fail the commit
