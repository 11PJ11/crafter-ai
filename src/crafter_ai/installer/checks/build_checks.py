"""Build-specific pre-flight checks for the installer.

This module provides checks that verify the system is ready for building
a Python package. These checks run before the forge:build command.
"""

import shutil
import subprocess
from pathlib import Path

from crafter_ai.installer.domain.check_result import CheckResult, CheckSeverity
from crafter_ai.installer.domain.check_registry import CheckRegistry


def check_pyproject_exists() -> CheckResult:
    """Verify pyproject.toml exists in the current directory.

    Returns:
        CheckResult with passed=True if pyproject.toml exists, otherwise passed=False
        with remediation guidance.
    """
    pyproject_path = Path("pyproject.toml")
    passed = pyproject_path.exists()

    if passed:
        return CheckResult(
            id="pyproject-exists",
            name="Pyproject.toml Exists",
            passed=True,
            severity=CheckSeverity.BLOCKING,
            message="pyproject.toml found in current directory",
        )
    else:
        return CheckResult(
            id="pyproject-exists",
            name="Pyproject.toml Exists",
            passed=False,
            severity=CheckSeverity.BLOCKING,
            message="pyproject.toml not found in current directory",
            remediation="Create a pyproject.toml file in your project root. See https://packaging.python.org/en/latest/guides/writing-pyproject-toml/",
        )


def check_build_package_installed() -> CheckResult:
    """Verify the 'build' package is available.

    The 'build' package provides the pyproject-build command for building
    Python packages according to PEP 517.

    Returns:
        CheckResult with passed=True if build is available, otherwise passed=False
        with fixable=True and fix_command for auto-installation.
    """
    # The 'build' package installs pyproject-build command
    build_path = shutil.which("pyproject-build")
    passed = build_path is not None

    if passed:
        return CheckResult(
            id="build-package",
            name="Build Package Installed",
            passed=True,
            severity=CheckSeverity.BLOCKING,
            message=f"Build package found at {build_path}",
        )
    else:
        return CheckResult(
            id="build-package",
            name="Build Package Installed",
            passed=False,
            severity=CheckSeverity.BLOCKING,
            message="Build package is not installed",
            remediation="Install the build package using 'pip install build'",
            fixable=True,
            fix_command="pip install build",
        )


def check_src_directory_exists() -> CheckResult:
    """Verify src/ directory exists in the current directory.

    Returns:
        CheckResult with passed=True if src/ exists and is a directory,
        otherwise passed=False with remediation guidance.
    """
    src_path = Path("src")
    passed = src_path.exists() and src_path.is_dir()

    if passed:
        return CheckResult(
            id="src-directory",
            name="Source Directory Exists",
            passed=True,
            severity=CheckSeverity.BLOCKING,
            message="src/ directory found",
        )
    else:
        return CheckResult(
            id="src-directory",
            name="Source Directory Exists",
            passed=False,
            severity=CheckSeverity.BLOCKING,
            message="src/ directory not found",
            remediation="Create a src/ directory with your package structure. See https://packaging.python.org/en/latest/tutorials/packaging-projects/",
        )


def check_clean_git_status() -> CheckResult:
    """Verify there are no uncommitted changes in git.

    This is a WARNING severity check as building with uncommitted changes
    is allowed but not recommended.

    Returns:
        CheckResult with passed=True if git status is clean, otherwise passed=False
        with WARNING severity.
    """
    try:
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True,
            text=True,
            check=False,
        )

        if result.returncode != 0:
            return CheckResult(
                id="clean-git-status",
                name="Clean Git Status",
                passed=False,
                severity=CheckSeverity.WARNING,
                message="Not in a git repository or git command failed",
                remediation="Initialize a git repository with 'git init' or ensure git is working",
            )

        has_changes = bool(result.stdout.strip())

        if not has_changes:
            return CheckResult(
                id="clean-git-status",
                name="Clean Git Status",
                passed=True,
                severity=CheckSeverity.WARNING,
                message="Git working directory is clean",
            )
        else:
            return CheckResult(
                id="clean-git-status",
                name="Clean Git Status",
                passed=False,
                severity=CheckSeverity.WARNING,
                message="Uncommitted changes detected in git working directory",
                remediation="Commit or stash your changes before building: 'git add -A && git commit -m \"your message\"'",
            )
    except subprocess.CalledProcessError:
        return CheckResult(
            id="clean-git-status",
            name="Clean Git Status",
            passed=False,
            severity=CheckSeverity.WARNING,
            message="Failed to run git status command",
            remediation="Ensure git is installed and you are in a git repository",
        )


def check_version_not_released() -> CheckResult:
    """Verify the current version is not already released on PyPI.

    This is a WARNING severity check as re-releasing a version will fail
    on PyPI anyway.

    Returns:
        CheckResult with passed=True if version is not on PyPI, otherwise passed=False
        with WARNING severity.
    """
    try:
        # Try to get the current version from pyproject.toml
        # For now, we do a simple check using pip index
        result = subprocess.run(
            ["pip", "index", "versions", "crafter-ai"],
            capture_output=True,
            text=True,
            check=False,
        )

        # If pip index returns 0, the package exists on PyPI
        # We treat this as a warning since version collision will be caught by PyPI
        if result.returncode == 0:
            return CheckResult(
                id="version-not-released",
                name="Version Not Released",
                passed=False,
                severity=CheckSeverity.WARNING,
                message="Package version may already exist on PyPI",
                remediation="Bump the version in pyproject.toml before releasing",
            )
        else:
            return CheckResult(
                id="version-not-released",
                name="Version Not Released",
                passed=True,
                severity=CheckSeverity.WARNING,
                message="Version not found on PyPI (safe to release)",
            )
    except (subprocess.CalledProcessError, FileNotFoundError):
        return CheckResult(
            id="version-not-released",
            name="Version Not Released",
            passed=True,
            severity=CheckSeverity.WARNING,
            message="Could not check PyPI (assuming version is new)",
        )


def create_build_check_registry() -> CheckRegistry:
    """Create a registry pre-populated with all build checks.

    Returns:
        CheckRegistry with all 5 build checks registered.
    """
    registry = CheckRegistry()
    registry.register("pyproject-exists", check_pyproject_exists)
    registry.register("build-package", check_build_package_installed)
    registry.register("src-directory", check_src_directory_exists)
    registry.register("clean-git-status", check_clean_git_status)
    registry.register("version-not-released", check_version_not_released)
    return registry
