"""Install-specific pre-flight checks for the installer.

This module provides checks that verify the system is ready for installing
a Python package locally. These checks run before the forge:install-local command.
"""

import os
import re
import subprocess
from pathlib import Path

from crafter_ai.installer.domain.check_registry import CheckRegistry
from crafter_ai.installer.domain.check_result import CheckResult, CheckSeverity


# PEP 427 wheel filename pattern:
# {distribution}-{version}(-{build tag})?-{python tag}-{abi tag}-{platform tag}.whl
PEP_427_WHEEL_PATTERN = re.compile(
    r"^[a-zA-Z0-9_]+-[0-9]+(?:\.[0-9]+)*(?:\.[a-zA-Z0-9]+)*"
    r"(?:-[0-9]+)?"  # Optional build number
    r"-[a-zA-Z0-9_]+-[a-zA-Z0-9_]+-[a-zA-Z0-9_]+\.whl$"
)


def check_wheel_exists() -> CheckResult:
    """Verify a .whl file exists in the dist/ directory.

    Returns:
        CheckResult with passed=True if a wheel file exists in dist/,
        otherwise passed=False with fixable=True and fix_command to chain to forge:build.
    """
    dist_path = Path("dist")

    if not dist_path.exists():
        return CheckResult(
            id="wheel-exists",
            name="Wheel File Exists",
            passed=False,
            severity=CheckSeverity.BLOCKING,
            message="dist/ directory not found",
            remediation="Run 'forge build' to create the wheel file",
            fixable=True,
            fix_command="forge build",
        )

    if not dist_path.is_dir():
        return CheckResult(
            id="wheel-exists",
            name="Wheel File Exists",
            passed=False,
            severity=CheckSeverity.BLOCKING,
            message="dist is not a directory",
            remediation="Remove dist file and run 'forge build' to create the wheel file",
            fixable=True,
            fix_command="forge build",
        )

    wheel_files = list(dist_path.glob("*.whl"))

    if not wheel_files:
        return CheckResult(
            id="wheel-exists",
            name="Wheel File Exists",
            passed=False,
            severity=CheckSeverity.BLOCKING,
            message="No .whl file found in dist/ directory",
            remediation="Run 'forge build' to create the wheel file",
            fixable=True,
            fix_command="forge build",
        )

    wheel_name = wheel_files[0].name
    return CheckResult(
        id="wheel-exists",
        name="Wheel File Exists",
        passed=True,
        severity=CheckSeverity.BLOCKING,
        message=f"Found wheel file: {wheel_name}",
    )


def check_wheel_format() -> CheckResult:
    """Verify wheel filename follows PEP 427 format.

    The wheel filename format is:
    {distribution}-{version}(-{build tag})?-{python tag}-{abi tag}-{platform tag}.whl

    Returns:
        CheckResult with passed=True if wheel filename is valid PEP 427 format,
        otherwise passed=False with remediation guidance.
    """
    dist_path = Path("dist")

    if not dist_path.exists() or not dist_path.is_dir():
        return CheckResult(
            id="wheel-format",
            name="Wheel Format Valid",
            passed=False,
            severity=CheckSeverity.BLOCKING,
            message="dist/ directory not found",
            remediation="Run 'forge build' first to create a wheel file",
        )

    wheel_files = list(dist_path.glob("*.whl"))

    if not wheel_files:
        return CheckResult(
            id="wheel-format",
            name="Wheel Format Valid",
            passed=False,
            severity=CheckSeverity.BLOCKING,
            message="No .whl file found in dist/ directory to validate",
            remediation="Run 'forge build' first to create a wheel file",
        )

    wheel_name = wheel_files[0].name

    if PEP_427_WHEEL_PATTERN.match(wheel_name):
        return CheckResult(
            id="wheel-format",
            name="Wheel Format Valid",
            passed=True,
            severity=CheckSeverity.BLOCKING,
            message=f"Wheel filename '{wheel_name}' follows PEP 427 format",
        )
    else:
        return CheckResult(
            id="wheel-format",
            name="Wheel Format Valid",
            passed=False,
            severity=CheckSeverity.BLOCKING,
            message=f"Wheel filename '{wheel_name}' does not follow PEP 427 format",
            remediation="Wheel filename must be: {{distribution}}-{{version}}(-{{build}})?-{{python}}-{{abi}}-{{platform}}.whl. See PEP 427 for details.",
        )


def check_pipx_isolation() -> CheckResult:
    """Verify pipx can create isolated virtual environments.

    Runs 'pipx environment' to verify pipx is working correctly and can
    create isolated environments.

    Returns:
        CheckResult with passed=True if pipx environment works,
        otherwise passed=False with remediation guidance.
    """
    try:
        result = subprocess.run(
            ["pipx", "environment"],
            capture_output=True,
            text=True,
            check=False,
        )

        if result.returncode == 0:
            return CheckResult(
                id="pipx-isolation",
                name="Pipx Isolation",
                passed=True,
                severity=CheckSeverity.BLOCKING,
                message="Pipx environment is properly configured for isolated installations",
            )
        else:
            return CheckResult(
                id="pipx-isolation",
                name="Pipx Isolation",
                passed=False,
                severity=CheckSeverity.BLOCKING,
                message="Pipx environment check failed",
                remediation="Reinstall pipx: 'pip install --force-reinstall pipx && pipx ensurepath'",
            )

    except FileNotFoundError:
        return CheckResult(
            id="pipx-isolation",
            name="Pipx Isolation",
            passed=False,
            severity=CheckSeverity.BLOCKING,
            message="Pipx is not installed or not in PATH",
            remediation="Install pipx: 'pip install pipx && pipx ensurepath'",
        )


def check_install_path_resolved() -> CheckResult:
    """Verify the target installation path is accessible.

    Checks that the pipx bin directory (typically ~/.local/bin) exists
    and is writable.

    Returns:
        CheckResult with passed=True if path is accessible,
        otherwise passed=False with remediation guidance.
    """
    # Default pipx installation path
    home = Path.home()
    pipx_bin_path = home / ".local" / "bin"

    if not pipx_bin_path.exists():
        return CheckResult(
            id="install-path-resolved",
            name="Install Path Resolved",
            passed=False,
            severity=CheckSeverity.BLOCKING,
            message=f"Installation path {pipx_bin_path} does not exist",
            remediation="Create the directory with: 'mkdir -p ~/.local/bin' and ensure it's in your PATH",
        )

    if not pipx_bin_path.is_dir():
        return CheckResult(
            id="install-path-resolved",
            name="Install Path Resolved",
            passed=False,
            severity=CheckSeverity.BLOCKING,
            message=f"Installation path {pipx_bin_path} is not a directory",
            remediation="Remove the file and create a directory: 'rm ~/.local/bin && mkdir -p ~/.local/bin'",
        )

    if not os.access(pipx_bin_path, os.W_OK):
        return CheckResult(
            id="install-path-resolved",
            name="Install Path Resolved",
            passed=False,
            severity=CheckSeverity.BLOCKING,
            message=f"Installation path {pipx_bin_path} is not writable",
            remediation="Fix permissions: 'chmod u+w ~/.local/bin' or check file ownership",
        )

    return CheckResult(
        id="install-path-resolved",
        name="Install Path Resolved",
        passed=True,
        severity=CheckSeverity.BLOCKING,
        message=f"Installation path {pipx_bin_path} is accessible and writable",
    )


def create_install_check_registry() -> CheckRegistry:
    """Create a registry pre-populated with all install checks.

    Returns:
        CheckRegistry with all 4 install checks registered for 'install-local' journey.
    """
    registry = CheckRegistry()
    registry.register("wheel-exists", check_wheel_exists)
    registry.register("wheel-format", check_wheel_format)
    registry.register("pipx-isolation", check_pipx_isolation)
    registry.register("install-path-resolved", check_install_path_resolved)
    return registry
