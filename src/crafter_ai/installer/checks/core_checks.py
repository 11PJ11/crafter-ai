"""Core pre-flight checks for the installer.

This module provides the fundamental checks that verify the system is ready
for installation. These checks are reused across build, install, and PyPI journeys.
"""

import shutil
import socket
import sys

from crafter_ai.installer.domain.check_registry import CheckRegistry
from crafter_ai.installer.domain.check_result import CheckResult, CheckSeverity


def check_python_version() -> CheckResult:
    """Verify Python version is >= 3.10.

    Returns:
        CheckResult with passed=True if Python >= 3.10, otherwise passed=False
        with remediation guidance.
    """
    major, minor = sys.version_info.major, sys.version_info.minor
    passed = (major, minor) >= (3, 10)

    if passed:
        return CheckResult(
            id="python-version",
            name="Python Version",
            passed=True,
            severity=CheckSeverity.BLOCKING,
            message=f"Python {major}.{minor} meets minimum requirement (>= 3.10)",
        )
    else:
        return CheckResult(
            id="python-version",
            name="Python Version",
            passed=False,
            severity=CheckSeverity.BLOCKING,
            message=f"Python {major}.{minor} does not meet minimum requirement",
            remediation="Please upgrade to Python 3.10 or higher. Visit https://www.python.org/downloads/",
        )


def check_git_available() -> CheckResult:
    """Verify git command is available.

    Returns:
        CheckResult with passed=True if git is found in PATH, otherwise passed=False
        with remediation guidance.
    """
    git_path = shutil.which("git")
    passed = git_path is not None

    if passed:
        return CheckResult(
            id="git-available",
            name="Git Available",
            passed=True,
            severity=CheckSeverity.BLOCKING,
            message=f"Git found at {git_path}",
        )
    else:
        return CheckResult(
            id="git-available",
            name="Git Available",
            passed=False,
            severity=CheckSeverity.BLOCKING,
            message="Git is not installed or not in PATH",
            remediation="Install Git from https://git-scm.com/downloads",
        )


def check_pipx_available() -> CheckResult:
    """Verify pipx command is available.

    This is a WARNING severity check because pipx can be auto-installed.

    Returns:
        CheckResult with passed=True if pipx is found, otherwise passed=False
        with fix_command for auto-installation.
    """
    pipx_path = shutil.which("pipx")
    passed = pipx_path is not None

    if passed:
        return CheckResult(
            id="pipx-available",
            name="Pipx Available",
            passed=True,
            severity=CheckSeverity.WARNING,
            message=f"Pipx found at {pipx_path}",
        )
    else:
        return CheckResult(
            id="pipx-available",
            name="Pipx Available",
            passed=False,
            severity=CheckSeverity.WARNING,
            message="Pipx is not installed or not in PATH",
            remediation="Install pipx using 'pip install pipx'",
            fixable=True,
            fix_command="pip install pipx",
        )


def check_internet_connectivity() -> CheckResult:
    """Verify internet access is available.

    Attempts to connect to a reliable host (Google DNS) to verify connectivity.
    This is a WARNING severity check as some operations may work offline.

    Returns:
        CheckResult with passed=True if connection succeeds, otherwise passed=False.
    """
    try:
        # Try connecting to Google's public DNS server
        conn = socket.create_connection(("8.8.8.8", 53), timeout=3)
        conn.close()
        return CheckResult(
            id="internet-connectivity",
            name="Internet Connectivity",
            passed=True,
            severity=CheckSeverity.WARNING,
            message="Internet connection available",
        )
    except OSError:
        return CheckResult(
            id="internet-connectivity",
            name="Internet Connectivity",
            passed=False,
            severity=CheckSeverity.WARNING,
            message="Cannot connect to the internet",
            remediation="Check your network connection. Some features may not work offline.",
        )


def create_core_check_registry() -> CheckRegistry:
    """Create a registry pre-populated with all core checks.

    Returns:
        CheckRegistry with all 4 core checks registered.
    """
    registry = CheckRegistry()
    registry.register("python-version", check_python_version)
    registry.register("git-available", check_git_available)
    registry.register("pipx-available", check_pipx_available)
    registry.register("internet-connectivity", check_internet_connectivity)
    return registry
