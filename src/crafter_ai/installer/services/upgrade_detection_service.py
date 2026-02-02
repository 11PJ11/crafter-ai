"""UpgradeDetectionService for comparing installed vs available versions.

This module provides the UpgradeDetectionService that:
- Queries pipx for the currently installed crafter-ai version
- Queries PyPI API for the latest available version
- Compares versions to detect if an upgrade is available

Used by: forge:status CLI command, health checks
"""

import json
import urllib.error
import urllib.request
from dataclasses import dataclass

from packaging.version import InvalidVersion, Version

from crafter_ai.installer.ports.pipx_port import PipxPort


PYPI_API_URL = "https://pypi.org/pypi"
DEFAULT_PACKAGE_NAME = "crafter-ai"


@dataclass(frozen=True)
class UpgradeInfo:
    """Immutable result of upgrade detection.

    Attributes:
        installed_version: Currently installed version, or None if not installed.
        latest_version: Latest version on PyPI, or None if PyPI unreachable.
        is_upgrade_available: True if latest > installed.
        is_major_upgrade: True if major version differs (1.x.x vs 2.x.x).
        is_downgrade: True if installed > latest (e.g., dev version).
    """

    installed_version: str | None
    latest_version: str | None
    is_upgrade_available: bool
    is_major_upgrade: bool
    is_downgrade: bool


def get_installed_version(
    pipx_port: PipxPort, package_name: str = DEFAULT_PACKAGE_NAME
) -> str | None:
    """Query pipx for the currently installed version of a package.

    Args:
        pipx_port: Port for pipx operations.
        package_name: Name of the package to check. Defaults to 'crafter-ai'.

    Returns:
        Version string if installed, None if not installed.
    """
    packages = pipx_port.list_packages()
    for pkg in packages:
        if pkg.name == package_name:
            return pkg.version
    return None


def get_latest_pypi_version(package_name: str = DEFAULT_PACKAGE_NAME) -> str | None:
    """Query PyPI API for the latest version of a package.

    Args:
        package_name: Name of the package to check. Defaults to 'crafter-ai'.

    Returns:
        Latest version string if available, None if PyPI unreachable or package not found.
    """
    try:
        url = f"{PYPI_API_URL}/{package_name}/json"
        request = urllib.request.Request(url)
        with urllib.request.urlopen(request, timeout=10) as response:
            if response.status == 200:
                data = json.loads(response.read().decode("utf-8"))
                return data.get("info", {}).get("version")
    except (
        urllib.error.URLError,
        urllib.error.HTTPError,
        TimeoutError,
        json.JSONDecodeError,
    ):
        pass
    return None


def _parse_version(version_str: str | None) -> Version | None:
    """Parse a version string into a Version object.

    Args:
        version_str: Version string to parse.

    Returns:
        Version object if parseable, None otherwise.
    """
    if version_str is None:
        return None
    try:
        return Version(version_str)
    except InvalidVersion:
        return None


def _get_major_version(version: Version | None) -> int | None:
    """Extract the major version number from a Version object.

    Args:
        version: Version object to extract from.

    Returns:
        Major version number, or None if version is None.
    """
    if version is None:
        return None
    return version.major


def detect_upgrade(
    pipx_port: PipxPort,
    package_name: str = DEFAULT_PACKAGE_NAME,
) -> UpgradeInfo:
    """Detect if an upgrade is available by comparing installed vs PyPI version.

    Args:
        pipx_port: Port for pipx operations.
        package_name: Name of the package to check. Defaults to 'crafter-ai'.

    Returns:
        UpgradeInfo with version comparison details.
    """
    installed_str = get_installed_version(pipx_port, package_name)
    latest_str = get_latest_pypi_version(package_name)

    installed = _parse_version(installed_str)
    latest = _parse_version(latest_str)

    # Default values for edge cases
    is_upgrade_available = False
    is_major_upgrade = False
    is_downgrade = False

    # Both versions available: compare them
    if installed is not None and latest is not None:
        is_upgrade_available = latest > installed
        is_downgrade = installed > latest

        installed_major = _get_major_version(installed)
        latest_major = _get_major_version(latest)

        if installed_major is not None and latest_major is not None:
            is_major_upgrade = is_upgrade_available and latest_major > installed_major

    # Package not installed but PyPI has version: upgrade available (fresh install)
    elif installed is None and latest is not None:
        is_upgrade_available = True
        is_major_upgrade = False
        is_downgrade = False

    return UpgradeInfo(
        installed_version=installed_str,
        latest_version=latest_str,
        is_upgrade_available=is_upgrade_available,
        is_major_upgrade=is_major_upgrade,
        is_downgrade=is_downgrade,
    )
