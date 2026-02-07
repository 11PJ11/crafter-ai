#!/usr/bin/env python3
"""nWave Version Auto-Increment Hook

DEPRECATED: This hook has been replaced by python-semantic-release (PSR).
PSR now handles version bumping automatically in CI/CD Stage 5 based on
conventional commit types (feat: = minor, fix: = patch, BREAKING CHANGE: = major).
Configuration lives in pyproject.toml under [tool.semantic_release].

This file is retained for reference but is no longer active in .pre-commit-config.yaml.

Original description:
Automatically bumps patch version when nWave files are modified.
"""

import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


# Color codes
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


def get_staged_nwave_files():
    """Get list of staged nWave files (excluding version.md).

    Returns:
        list: List of staged nWave file paths
    """
    try:
        result = subprocess.run(
            ["git", "diff", "--cached", "--name-only"],
            check=True,
            capture_output=True,
            text=True,
        )
        files = result.stdout.strip().split("\n") if result.stdout.strip() else []

        # Filter for nWave files (nWave/ or tools/) excluding version.md
        nwave_files = [
            f
            for f in files
            if (f.startswith("nWave/") or f.startswith("tools/"))
            and "version.md" not in f
        ]
        return nwave_files
    except subprocess.CalledProcessError:
        return []


def parse_version(version_string):
    """Parse semantic version string.

    Args:
        version_string: Version in format "X.Y.Z"

    Returns:
        tuple: (major, minor, patch) as integers, or None if parsing fails
    """
    match = re.match(r"^(\d+)\.(\d+)\.(\d+)$", version_string.strip())
    if match:
        return tuple(int(x) for x in match.groups())
    return None


def increment_patch_version(version_tuple):
    """Increment patch version.

    Args:
        version_tuple: (major, minor, patch)

    Returns:
        str: New version string "major.minor.patch+1"
    """
    major, minor, patch = version_tuple
    return f"{major}.{minor}.{patch + 1}"


def update_file_content(file_path, old_version, new_version, build_timestamp=None):
    """Update version in file content.

    Args:
        file_path: Path to file to update
        old_version: Current version string
        new_version: New version string
        build_timestamp: Optional timestamp for version.md

    Returns:
        bool: True if file was updated, False otherwise
    """
    try:
        content = file_path.read_text(encoding="utf-8")
        updated = False

        # Update version line
        if f'version: "{old_version}"' in content:
            content = content.replace(
                f'version: "{old_version}"', f'version: "{new_version}"'
            )
            updated = True

        # Update Version: line (for version.md)
        if f"Version: {old_version}" in content:
            content = content.replace(
                f"Version: {old_version}", f"Version: {new_version}"
            )
            updated = True

        # Update Build: line (for version.md)
        if build_timestamp and "Build: " in content:
            # Replace any Build: line with new timestamp
            content = re.sub(
                r"Build: \d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z",
                f"Build: {build_timestamp}",
                content,
            )
            updated = True

        # Update version comment (for README.md and COMMAND-AGENT-MAPPING.md)
        if f"<!-- version: {old_version} -->" in content:
            content = content.replace(
                f"<!-- version: {old_version} -->", f"<!-- version: {new_version} -->"
            )
            updated = True

        if updated:
            file_path.write_text(content, encoding="utf-8")

        return updated
    except Exception as e:
        print(f"{YELLOW}Warning: Could not update {file_path}: {e}{NC}")
        return False


def git_add_file(file_path):
    """Add file to git staging area.

    Args:
        file_path: Path to file to add
    """
    try:
        subprocess.run(["git", "add", str(file_path)], check=True, capture_output=True)
    except subprocess.CalledProcessError as e:
        print(f"{YELLOW}Warning: Could not git add {file_path}: {e}{NC}")


def main():
    """Auto-increment version when nWave files are modified."""
    clear_git_environment()

    catalog_file = Path("nWave/framework-catalog.yaml")
    version_file = Path("nWave/tasks/nw/version.md")

    # Check if nWave files are staged (excluding version.md to avoid loops)
    nwave_staged = get_staged_nwave_files()

    if not nwave_staged:
        print(f"{BLUE}No nWave files modified, skipping version bump{NC}")
        return 0

    if not catalog_file.exists() or not version_file.exists():
        print(f"{YELLOW}Warning: Version files not found, skipping version bump{NC}")
        return 0

    # Extract current version from framework-catalog.yaml
    try:
        catalog_content = catalog_file.read_text(encoding="utf-8")
        version_match = re.search(
            r'^version:\s*"([^"]+)"', catalog_content, re.MULTILINE
        )

        if not version_match:
            print(f"{YELLOW}Warning: Could not parse version from {catalog_file}{NC}")
            return 0

        current_version = version_match.group(1)
    except Exception as e:
        print(f"{YELLOW}Warning: Error reading {catalog_file}: {e}{NC}")
        return 0

    # Parse version components
    version_tuple = parse_version(current_version)
    if not version_tuple:
        print(f"{YELLOW}Warning: Invalid version format: {current_version}{NC}")
        return 0

    # Increment patch version
    new_version = increment_patch_version(version_tuple)

    # Get current timestamp in UTC ISO format
    build_timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    # Update framework-catalog.yaml
    update_file_content(catalog_file, current_version, new_version)
    git_add_file(catalog_file)

    # Update version.md
    update_file_content(version_file, current_version, new_version, build_timestamp)
    git_add_file(version_file)

    # Update dependent files
    readme_file = Path("README.md")
    mapping_file = Path("nWave/data/agents_reference/COMMAND-AGENT-MAPPING.md")

    updated_files = []

    if readme_file.exists():
        if update_file_content(readme_file, current_version, new_version):
            git_add_file(readme_file)
            updated_files.append("README.md")

    if mapping_file.exists():
        if update_file_content(mapping_file, current_version, new_version):
            git_add_file(mapping_file)
            updated_files.append("COMMAND-AGENT-MAPPING.md")

    print(f"{GREEN}Version bumped: {current_version} -> {new_version}{NC}")
    if updated_files:
        print(f"{GREEN}  (Also updated: {', '.join(updated_files)}){NC}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
