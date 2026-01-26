#!/usr/bin/env python3
"""Documentation Version Validation Hook

Ensures documentation versions are synchronized.
"""

import os
import subprocess
import sys
from pathlib import Path

# Color codes
RED = "\033[0;31m"
GREEN = "\033[0;32m"
YELLOW = "\033[1;33m"
BLUE = "\033[0;34m"
NC = "\033[0m"


def clear_git_environment():
    """Clear git environment variables that pre-commit sets.

    These can cause git commands to fail or behave unexpectedly.
    """
    git_vars = ["GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE"]
    for var in git_vars:
        os.environ.pop(var, None)


def main():
    """Run documentation version validation."""
    clear_git_environment()

    print(f"{BLUE}Running documentation version validation...{NC}")

    # Check if validation infrastructure exists
    dependency_map = Path(".dependency-map.yaml")
    validation_script = Path("scripts/validation/validate-documentation-versions.py")

    if not dependency_map.exists():
        print(
            f"{YELLOW}Warning: .dependency-map.yaml not found, skipping version validation{NC}"
        )
        return 0

    if not validation_script.exists():
        print(
            f"{YELLOW}Warning: validation script not found, skipping version validation{NC}"
        )
        return 0

    # Use sys.executable for cross-platform compatibility (Windows uses 'python', Unix uses 'python3')
    python_cmd = sys.executable

    # Check if Python is available
    try:
        subprocess.run(
            [python_cmd, "--version"], check=True, capture_output=True, text=True
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        print(f"{YELLOW}Warning: Python not available, skipping validation{NC}")
        return 0

    # Run validation
    try:
        result = subprocess.run(
            [python_cmd, str(validation_script)], check=False, capture_output=False
        )

        if result.returncode == 0:
            print(f"{GREEN}Documentation version validation passed{NC}")
            return 0
        elif result.returncode == 2:
            print(f"{RED}Configuration error in version validation{NC}")
            print(f"{RED}Check .dependency-map.yaml for errors{NC}")
            return 1
        else:
            # Error report already printed by Python script
            print()
            print(f"{YELLOW}Emergency bypass: git commit --no-verify{NC}")
            return 1
    except Exception as e:
        print(f"{RED}Unexpected error running validation: {e}{NC}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
