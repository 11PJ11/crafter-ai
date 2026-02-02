"""nw version CLI command for displaying version information.

This module provides the 'nw version' command that shows:
- Installed crafter-ai version
- Python version
- Platform information
- Optional: Latest PyPI version and upgrade availability
"""

import json
import os
import platform
import sys
from importlib.metadata import version as importlib_metadata_version
from typing import Annotated

import typer
from packaging.version import InvalidVersion, Version
from rich.console import Console

from crafter_ai.installer.services.upgrade_detection_service import (
    get_latest_pypi_version,
)


# Package name constant
PACKAGE_NAME = "crafter-ai"


def _is_ci_mode() -> bool:
    """Check if running in CI mode.

    CI mode is detected via CI environment variable set to 'true' or '1'.

    Returns:
        True if in CI mode, False otherwise.
    """
    ci_value = os.environ.get("CI", "").lower()
    return ci_value in ("true", "1")


def _get_installed_version() -> str:
    """Get the installed version of crafter-ai.

    Uses importlib.metadata to get the installed package version.

    Returns:
        Version string, or 'unknown' if not available.
    """
    try:
        return importlib_metadata_version(PACKAGE_NAME)
    except Exception:
        return "unknown"


def _get_python_version() -> str:
    """Get the Python version string.

    Returns:
        Python version in format 'X.Y.Z'.
    """
    return f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"


def _get_platform() -> str:
    """Get the platform name.

    Returns:
        Platform name in lowercase (e.g., 'darwin', 'linux', 'windows').
    """
    return platform.system().lower()


def _is_upgrade_available(installed: str, latest: str | None) -> bool:
    """Check if an upgrade is available.

    Args:
        installed: Currently installed version.
        latest: Latest version from PyPI, or None if unavailable.

    Returns:
        True if upgrade is available, False otherwise.
    """
    if latest is None or installed == "unknown":
        return False

    try:
        installed_ver = Version(installed)
        latest_ver = Version(latest)
        return latest_ver > installed_ver
    except InvalidVersion:
        return False


def _display_version_rich(
    console: Console,
    installed_version: str,
    python_version: str,
    platform_name: str,
    latest_version: str | None = None,
    check_updates: bool = False,
) -> None:
    """Display version information using Rich formatting.

    Args:
        console: Rich Console for output.
        installed_version: Installed crafter-ai version.
        python_version: Python version string.
        platform_name: Platform name.
        latest_version: Latest PyPI version, or None.
        check_updates: Whether to show update check results.
    """
    console.print()
    console.print("[bold cyan]nWave Framework[/bold cyan]")
    console.print()
    console.print(f"  [bold]Installed:[/bold] crafter-ai v{installed_version}")
    console.print(f"  [bold]Python:[/bold]    {python_version}")
    console.print(f"  [bold]Platform:[/bold]  {platform_name}")

    if check_updates:
        console.print()
        if latest_version is None:
            console.print("  [dim]Latest available: Could not reach PyPI[/dim]")
        elif _is_upgrade_available(installed_version, latest_version):
            console.print(f"  [yellow]Latest available: {latest_version}[/yellow]")
            console.print()
            console.print(
                "  [dim]Run 'pip install --upgrade crafter-ai' to upgrade[/dim]"
            )
        else:
            console.print(f"  [green]You are up to date[/green] (v{latest_version})")

    console.print()


def _display_version_ci(
    installed_version: str,
    python_version: str,
    platform_name: str,
    latest_version: str | None = None,
    check_updates: bool = False,
) -> None:
    """Display version information in CI mode (plain text).

    Args:
        installed_version: Installed crafter-ai version.
        python_version: Python version string.
        platform_name: Platform name.
        latest_version: Latest PyPI version, or None.
        check_updates: Whether to show update check results.
    """
    print("")
    print("nWave Framework")
    print("")
    print(f"  Installed: crafter-ai v{installed_version}")
    print(f"  Python:    {python_version}")
    print(f"  Platform:  {platform_name}")

    if check_updates:
        print("")
        if latest_version is None:
            print("  Latest available: Could not reach PyPI")
        elif _is_upgrade_available(installed_version, latest_version):
            print(f"  Latest available: {latest_version}")
            print("")
            print("  Run 'pip install --upgrade crafter-ai' to upgrade")
        else:
            print(f"  You are up to date (v{latest_version})")

    print("")


def version(
    check_updates: Annotated[
        bool,
        typer.Option(
            "--check-updates",
            "-u",
            help="Check PyPI for latest version.",
        ),
    ] = False,
    json_output: Annotated[
        bool,
        typer.Option(
            "--json",
            "-j",
            help="Output in JSON format.",
        ),
    ] = False,
    short: Annotated[
        bool,
        typer.Option(
            "--short",
            "-s",
            help="Show only version number.",
        ),
    ] = False,
) -> None:
    """Show version information for crafter-ai.

    Displays the installed version, Python version, and platform.
    Use --check-updates to check if a newer version is available on PyPI.

    Examples:
        nw version               # Show version info
        nw version --short       # Show only version number
        nw version --check-updates  # Check for updates
        nw version --json        # Output as JSON
    """
    # Gather version information
    installed_version = _get_installed_version()
    python_version = _get_python_version()
    platform_name = _get_platform()

    # Get latest version if checking for updates
    latest_version: str | None = None
    if check_updates:
        latest_version = get_latest_pypi_version(PACKAGE_NAME)

    # Handle --short flag (just version number)
    if short:
        print(installed_version)
        return

    # Handle --json flag
    if json_output:
        data: dict[str, str | bool] = {
            "installed_version": installed_version,
            "python_version": python_version,
            "platform": platform_name,
        }

        if check_updates:
            data["latest_version"] = latest_version if latest_version else "unavailable"
            data["upgrade_available"] = _is_upgrade_available(
                installed_version, latest_version
            )

        print(json.dumps(data, indent=2))
        return

    # Detect CI mode
    ci_mode = _is_ci_mode()

    # Display version information
    if ci_mode:
        _display_version_ci(
            installed_version,
            python_version,
            platform_name,
            latest_version,
            check_updates,
        )
    else:
        console = Console()
        _display_version_rich(
            console,
            installed_version,
            python_version,
            platform_name,
            latest_version,
            check_updates,
        )
