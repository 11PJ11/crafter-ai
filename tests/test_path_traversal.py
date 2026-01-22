#!/usr/bin/env python3
"""
Test path traversal security validation.

This script tests the path security validation mechanism that would be
implemented in a dependency resolver.
"""

from pathlib import Path
from typing import List, Tuple
import re
import sys


def get_project_root() -> Path:
    """Get the project root directory."""
    return Path(__file__).parent


def validate_path_security(path: Path, project_root: Path) -> bool:
    """Validate that path doesn't escape project root (path traversal protection)."""
    try:
        resolved = path.resolve()
        project_root_resolved = project_root.resolve()
        return str(resolved).startswith(str(project_root_resolved))
    except (ValueError, OSError):
        return False


def resolve_path(path_str: str) -> Path:
    """Resolve a path string relative to project root."""
    path_str = path_str.strip()
    project_root = get_project_root()

    if path_str.startswith("/"):
        full_path = Path(path_str)
    else:
        full_path = project_root / path_str

    return full_path


def process_includes(file_path: str, verbose: bool = False) -> Tuple[bool, List[str]]:
    """
    Process a file for BUILD:INCLUDE markers and validate path security.

    Returns: (success: bool, errors: list[str])
    """
    errors = []
    project_root = get_project_root()

    try:
        with open(file_path, "r") as f:
            content = f.read()
    except FileNotFoundError:
        return False, [f"File not found: {file_path}"]

    # Pattern for BUILD:INCLUDE markers
    include_pattern = re.compile(r"\{\{\s*BUILD:INCLUDE\s+([^\}]+)\s*\}\}")

    matches = list(include_pattern.finditer(content))

    if verbose:
        print(f"Processing: {file_path}")
        print(f"Found {len(matches)} BUILD:INCLUDE markers")

    for match in matches:
        include_path_str = match.group(1).strip()
        include_path = resolve_path(include_path_str)

        if verbose:
            print(f"\n  Marker: {include_path_str}")
            print(f"  Resolved: {include_path}")

        # Validate security
        if not validate_path_security(include_path, project_root):
            error_msg = f"Path traversal attempt blocked: {include_path_str}"
            errors.append(error_msg)
            if verbose:
                print(f"  [BLOCKED] {error_msg}")
        else:
            # Check if file exists
            if not include_path.exists():
                error_msg = f"File not found: {include_path_str}"
                errors.append(error_msg)
                if verbose:
                    print(f"  [NOT FOUND] {error_msg}")
            else:
                if verbose:
                    print(f"  [OK] Would include {include_path}")

    return len(errors) == 0, errors


def main():
    """Main test runner."""
    project_root = get_project_root()
    test_dir = project_root / "tests"

    # Find all p2-06 test files
    test_files = sorted(test_dir.glob("test-p206-*.md"))

    if not test_files:
        print("No p2-06 test files found")
        return 1

    total_tests = len(test_files)
    passed = 0
    failed = 0

    print(f"Running {total_tests} path traversal security tests...\n")
    print("=" * 70)

    for test_file in test_files:
        test_name = test_file.stem
        success, errors = process_includes(str(test_file), verbose=True)

        print(f"\n{test_name}:")
        if success:
            print("  Result: PASS (no errors)")
            passed += 1
        else:
            print(f"  Result: {len(errors)} error(s)")
            for error in errors:
                print(f"    - {error}")
            failed += 1

        print("-" * 70)

    print(f"\nSummary: {passed} passed, {failed} failed out of {total_tests} tests")

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
