#!/usr/bin/env python3
"""
Formatter Environment Validation

Checks that code formatting tools (ruff, mypy) are available.
Converted from shell scripts for cross-platform compatibility.
"""

import shutil
import sys


def check_tool_available(tool_name: str) -> tuple[bool, str]:
    """
    Check if a tool is available in PATH.

    Returns:
        Tuple of (is_available, path_or_message)
    """
    tool_path = shutil.which(tool_name)
    if tool_path:
        return True, tool_path
    else:
        return False, f"{tool_name} not found in PATH"


def validate_formatter_environment() -> tuple[bool, list[str]]:
    """
    Validate that all required formatting tools are available.

    Returns:
        Tuple of (all_valid, list_of_issues)
    """
    required_tools = ["ruff", "mypy"]
    issues = []

    for tool in required_tools:
        available, path_or_msg = check_tool_available(tool)
        if not available:
            issues.append(f"❌ {tool}: {path_or_msg}")
        else:
            print(f"✓ {tool}: {path_or_msg}")

    return len(issues) == 0, issues


def main() -> int:
    """Main entry point."""
    print("🔍 Validating formatter environment...")

    all_valid, issues = validate_formatter_environment()

    if all_valid:
        print("\n✓ All formatting tools available")
        return 0
    else:
        print("\n❌ Missing formatting tools:")
        for issue in issues:
            print(f"  {issue}")
        print("\nInstall missing tools:")
        print("  pip install ruff mypy")
        return 1


if __name__ == "__main__":
    sys.exit(main())
