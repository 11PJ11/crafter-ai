#!/usr/bin/env python3
"""Pytest Test Validation Hook

Ensures all tests pass before commit.
"""

import os
import re
import subprocess
import sys
from pathlib import Path


# Windows color support detection
def supports_color() -> bool:
    """Check if the terminal supports ANSI color codes."""
    # Check for NO_COLOR environment variable (https://no-color.org/)
    if os.environ.get("NO_COLOR"):
        return False
    # Check for FORCE_COLOR environment variable
    if os.environ.get("FORCE_COLOR"):
        return True
    # Windows: check for ANSICON, ConEmu, or Windows Terminal
    if sys.platform == "win32":
        return (
            os.environ.get("ANSICON") is not None
            or os.environ.get("WT_SESSION") is not None  # Windows Terminal
            or os.environ.get("ConEmuANSI") == "ON"
            or os.environ.get("TERM_PROGRAM") == "vscode"
        )
    # Unix-like: check if stdout is a tty
    return hasattr(sys.stdout, "isatty") and sys.stdout.isatty()


# Color codes (disabled on unsupported terminals)
if supports_color():
    RED = "\033[0;31m"
    GREEN = "\033[0;32m"
    YELLOW = "\033[1;33m"
    BLUE = "\033[0;34m"
    NC = "\033[0m"
else:
    RED = ""
    GREEN = ""
    YELLOW = ""
    BLUE = ""
    NC = ""


def clear_git_environment():
    """Clear git environment variables that pre-commit sets.

    These can interfere with tests that create temporary git repositories.
    """
    git_vars = [
        "GIT_DIR",
        "GIT_WORK_TREE",
        "GIT_INDEX_FILE",
        "GIT_AUTHOR_DATE",
        "GIT_AUTHOR_NAME",
        "GIT_AUTHOR_EMAIL",
    ]
    for var in git_vars:
        os.environ.pop(var, None)


def get_repo_root() -> Path:
    """Get the git repository root directory."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True,
            check=True,
            timeout=30,
        )
        return Path(result.stdout.strip())
    except subprocess.SubprocessError:
        # Fallback to current directory if not in a git repo
        return Path.cwd()
    except FileNotFoundError:
        # Git not available
        return Path.cwd()


def main():
    """Run test validation."""
    clear_git_environment()

    print(f"{BLUE}Running test validation...{NC}")

    # Detect if running in CI environment
    is_ci = os.environ.get("CI", "false").lower() == "true"

    # Get repository root for proper path resolution
    repo_root = get_repo_root()

    # Use sys.executable to ensure cross-platform compatibility (Windows uses 'python', Unix uses 'python3')
    python_cmd = sys.executable

    # Check if pytest is available
    try:
        subprocess.run(
            [python_cmd, "-m", "pytest", "--version"],
            check=True,
            capture_output=True,
            text=True,
            timeout=30,
        )
    except (subprocess.SubprocessError, FileNotFoundError):
        if is_ci:
            print(f"{RED}ERROR: pytest not available in CI{NC}", file=sys.stderr)
            return 1
        print(f"{YELLOW}Warning: pytest not available, skipping tests{NC}")
        return 0

    # Check if tests directory exists
    tests_dir = repo_root / "tests"
    if not tests_dir.is_dir():
        print(f"{YELLOW}No tests directory found, skipping tests{NC}")
        return 0

    # Run tests and capture output
    try:
        result = subprocess.run(
            [python_cmd, "-m", "pytest", str(tests_dir), "-v", "--tb=short"],
            check=False,
            capture_output=True,
            text=True,
            timeout=300,  # 5 minutes timeout for test execution
        )
        test_output = result.stdout + result.stderr
        test_exit_code = result.returncode
    except subprocess.SubprocessError as e:
        print(f"{RED}Error running tests: {e}{NC}", file=sys.stderr)
        return 1
    except FileNotFoundError as e:
        print(f"{RED}Error running tests: {e}{NC}", file=sys.stderr)
        return 1

    # Count tests using regex
    passed_match = re.search(r"(\d+) passed", test_output)
    failed_match = re.search(r"(\d+) failed", test_output)

    total_tests = int(passed_match.group(1)) if passed_match else 0
    failed_tests = int(failed_match.group(1)) if failed_match else 0

    if test_exit_code == 0:
        print(f"{GREEN}All tests passing ({total_tests}/{total_tests}){NC}")
        return 0
    elif test_exit_code == 5:
        # Exit code 5 = no tests collected
        print(f"{YELLOW}No tests found, skipping test validation{NC}")
        return 0
    else:
        print(file=sys.stderr)
        print(f"{RED}COMMIT BLOCKED: Tests failed{NC}", file=sys.stderr)
        print(file=sys.stderr)
        print(f"{RED}Failed tests:{NC}", file=sys.stderr)

        # Extract and display failed test lines
        for line in test_output.split("\n"):
            if "FAILED" in line or "ERROR" in line:
                print(f"  {line}", file=sys.stderr)

        print(file=sys.stderr)

        if failed_tests > 0:
            passing_tests = total_tests - failed_tests
            print(
                f"{RED}Test Results: {passing_tests}/{total_tests} passing ({failed_tests} failed){NC}",
                file=sys.stderr,
            )

        print(file=sys.stderr)
        print(f"{YELLOW}Fix failing tests before committing.{NC}", file=sys.stderr)
        print(f"{YELLOW}Emergency bypass: git commit --no-verify{NC}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
