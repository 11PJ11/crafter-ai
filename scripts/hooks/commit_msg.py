#!/usr/bin/env python3
"""
commit-msg hook - Validates conventional commit format.

This hook validates that commit messages follow the Conventional Commits
specification: https://www.conventionalcommits.org/

Valid formats:
  type: description
  type(scope): description
  type!: breaking change description
  type(scope)!: breaking change description

Valid types: feat, fix, docs, style, refactor, perf, test, build, ci, chore, revert

Cross-platform compatible (Windows, macOS, Linux).
"""

import re
import sys
from pathlib import Path


# Valid commit types per Conventional Commits specification
VALID_TYPES = [
    "feat",
    "fix",
    "docs",
    "style",
    "refactor",
    "perf",
    "test",
    "build",
    "ci",
    "chore",
    "revert",
]

# Pattern for conventional commit format
# type: feat, fix, docs, style, refactor, perf, test, build, ci, chore, revert
# optional scope in parentheses
# optional ! for breaking changes
# colon and space
# description
CONVENTIONAL_COMMIT_PATTERN = re.compile(
    r"^(" + "|".join(VALID_TYPES) + r")(\([a-zA-Z0-9_-]+\))?!?: .+"
)


def validate_commit_message(commit_msg_file: Path) -> bool:
    """
    Validate that the commit message follows Conventional Commits format.

    Args:
        commit_msg_file: Path to the file containing the commit message

    Returns:
        True if valid, False otherwise
    """
    try:
        commit_msg = commit_msg_file.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as e:
        print(f"ERROR: Could not read commit message file: {e}", file=sys.stderr)
        return False

    # Get first line (subject)
    first_line = commit_msg.split("\n")[0].strip()

    if not first_line:
        print_error_message("", "Commit message is empty")
        return False

    if CONVENTIONAL_COMMIT_PATTERN.match(first_line):
        return True

    print_error_message(first_line, "Does not follow Conventional Commits format")
    return False


def print_error_message(commit_msg: str, reason: str) -> None:
    """Print a helpful error message for invalid commit messages."""
    print("")
    print("ERROR: Commit message does not follow Conventional Commits format.")
    print("")
    print("Your commit message:")
    print(f"  {commit_msg}")
    print("")
    print("Expected format:")
    print("  type(scope): description")
    print("")
    print(f"Valid types: {', '.join(VALID_TYPES)}")
    print("")
    print("Examples:")
    print("  feat: add user dashboard")
    print("  fix(auth): resolve login timeout")
    print("  feat!: redesign API endpoints (breaking change)")
    print("  refactor(api)!: remove deprecated endpoints")
    print("")
    print("See: https://www.conventionalcommits.org/")
    print("")


def main() -> int:
    """
    Main entry point for commit-msg hook.

    Returns:
        0 on success, 1 on failure
    """
    if len(sys.argv) < 2:
        print("ERROR: No commit message file provided", file=sys.stderr)
        return 1

    commit_msg_file = Path(sys.argv[1])

    if not commit_msg_file.exists():
        print(
            f"ERROR: Commit message file not found: {commit_msg_file}", file=sys.stderr
        )
        return 1

    if validate_commit_message(commit_msg_file):
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
