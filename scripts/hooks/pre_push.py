#!/usr/bin/env python3
"""
pre-push hook - Validates VERSION file and semantic-release config.

This hook validates that critical release configuration files exist
before allowing code to be pushed to remote repositories.

Validates:
- nWave/VERSION file exists (contains semantic version)
- .releaserc or release.config.js exists (semantic-release config)

Cross-platform compatible (Windows, macOS, Linux).
"""

import subprocess
import sys
from pathlib import Path


def get_repo_root() -> Path:
    """
    Get the git repository root directory.

    Returns:
        Path to the repository root

    Raises:
        RuntimeError: If not in a git repository
    """
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True,
            check=True,
        )
        return Path(result.stdout.strip())
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Not in a git repository: {e.stderr}") from e


def validate_version_file(repo_root: Path) -> bool:
    """
    Validate that VERSION file exists.

    Args:
        repo_root: Path to the repository root

    Returns:
        True if valid, False otherwise
    """
    version_file = repo_root / "nWave" / "VERSION"

    if not version_file.exists():
        print("ERROR: Pre-push validation failed.")
        print("")
        print("[FAIL] VERSION file missing")
        print("       Expected: nWave/VERSION")
        print(
            "       Action: Create nWave/VERSION with current version (e.g., '1.5.7')"
        )
        print("")
        return False

    return True


def validate_semantic_release_config(repo_root: Path) -> bool:
    """
    Validate that semantic-release configuration exists.

    Args:
        repo_root: Path to the repository root

    Returns:
        True if valid, False otherwise
    """
    releaserc = repo_root / ".releaserc"
    release_config_js = repo_root / "release.config.js"

    if not releaserc.exists() and not release_config_js.exists():
        print("ERROR: Pre-push validation failed.")
        print("")
        print("[FAIL] semantic-release not configured")
        print("       Expected: .releaserc or release.config.js")
        print(
            "       Action: Run 'npx semantic-release-cli setup' or create config manually"
        )
        print("")
        return False

    return True


def main() -> int:
    """
    Main entry point for pre-push hook.

    Returns:
        0 on success, 1 on failure
    """
    try:
        repo_root = get_repo_root()
    except RuntimeError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1

    # Check VERSION file
    if not validate_version_file(repo_root):
        return 1

    # Check semantic-release config
    if not validate_semantic_release_config(repo_root):
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
