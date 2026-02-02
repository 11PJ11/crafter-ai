"""Doctor health checks for the 'nw doctor' command.

This module provides health checks that verify the crafter-ai installation
and environment are properly configured.
"""

import sys
from datetime import datetime, timezone
from pathlib import Path

import importlib.metadata as importlib_metadata
import platformdirs

from crafter_ai.installer.domain.health_checker import HealthChecker
from crafter_ai.installer.domain.health_result import HealthResult, HealthStatus

PACKAGE_NAME = "crafter-ai"


def check_python_environment() -> HealthResult:
    """Verify Python version and virtual environment status.

    Returns:
        HealthResult with HEALTHY status if Python meets requirements.
    """
    major = sys.version_info.major
    minor = sys.version_info.minor
    micro = getattr(sys.version_info, "micro", 0)
    version_str = f"{major}.{minor}.{micro}"

    venv_active = sys.prefix != sys.base_prefix

    return HealthResult(
        component="python-environment",
        status=HealthStatus.HEALTHY,
        message=f"Python {major}.{minor} environment is healthy",
        details={
            "version": version_str,
            "venv_active": "true" if venv_active else "false",
            "prefix": sys.prefix,
        },
        timestamp=datetime.now(timezone.utc),
    )


def check_package_installation() -> HealthResult:
    """Verify crafter-ai package is installed.

    Returns:
        HealthResult with HEALTHY if installed, UNHEALTHY if not.
    """
    try:
        version = importlib_metadata.version(PACKAGE_NAME)
        return HealthResult(
            component="package-installation",
            status=HealthStatus.HEALTHY,
            message=f"crafter-ai {version} is installed",
            details={"version": version},
            timestamp=datetime.now(timezone.utc),
        )
    except Exception:
        return HealthResult(
            component="package-installation",
            status=HealthStatus.UNHEALTHY,
            message="crafter-ai package is not installed",
            details=None,
            timestamp=datetime.now(timezone.utc),
        )


def check_config_directory() -> HealthResult:
    """Verify config directory exists.

    Returns:
        HealthResult with HEALTHY if exists, UNHEALTHY if missing.
    """
    config_dir = platformdirs.user_config_dir("crafter-ai")
    config_path = Path(config_dir)

    if config_path.exists():
        return HealthResult(
            component="config-directory",
            status=HealthStatus.HEALTHY,
            message=f"Config directory exists at {config_dir}",
            details={"path": str(config_path)},
            timestamp=datetime.now(timezone.utc),
        )
    else:
        return HealthResult(
            component="config-directory",
            status=HealthStatus.UNHEALTHY,
            message=f"Config directory missing at {config_dir}",
            details={"expected_path": str(config_path)},
            timestamp=datetime.now(timezone.utc),
        )


def check_agent_files() -> HealthResult:
    """Verify agent specification files exist.

    Returns:
        HealthResult with HEALTHY if all files exist, DEGRADED if some missing,
        UNHEALTHY if config directory missing.
    """
    config_dir = platformdirs.user_config_dir("crafter-ai")
    config_path = Path(config_dir)

    if not config_path.exists():
        return HealthResult(
            component="agent-files",
            status=HealthStatus.UNHEALTHY,
            message="Config directory does not exist",
            details={"expected_path": str(config_path)},
            timestamp=datetime.now(timezone.utc),
        )

    # Look for agent specification files (*.yaml, *.md in agents directory)
    agent_files = list(config_path.glob("**/*.yaml")) + list(
        config_path.glob("**/*.md")
    )

    if agent_files:
        return HealthResult(
            component="agent-files",
            status=HealthStatus.HEALTHY,
            message=f"Found {len(agent_files)} agent specification files",
            details={"file_count": str(len(agent_files))},
            timestamp=datetime.now(timezone.utc),
        )
    else:
        return HealthResult(
            component="agent-files",
            status=HealthStatus.DEGRADED,
            message="No agent specification files found",
            details={"path": str(config_path)},
            timestamp=datetime.now(timezone.utc),
        )


def _fetch_pypi_version(package_name: str) -> str | None:
    """Fetch the latest version from PyPI.

    Args:
        package_name: Name of the package to check.

    Returns:
        Latest version string or None if unreachable.
    """
    try:
        import httpx

        response = httpx.get(
            f"https://pypi.org/pypi/{package_name}/json",
            timeout=5.0,
        )
        if response.status_code == 200:
            data = response.json()
            return data.get("info", {}).get("version")
    except Exception:
        pass
    return None


def check_update_available() -> HealthResult:
    """Check if a newer version is available on PyPI.

    Returns:
        HealthResult with HEALTHY if up to date or cannot check,
        DEGRADED if update available.
    """
    try:
        current_version = importlib_metadata.version(PACKAGE_NAME)
    except Exception:
        return HealthResult(
            component="update-available",
            status=HealthStatus.HEALTHY,
            message="Cannot check for updates (package not installed)",
            details=None,
            timestamp=datetime.now(timezone.utc),
        )

    latest_version = _fetch_pypi_version(PACKAGE_NAME)

    if latest_version is None:
        return HealthResult(
            component="update-available",
            status=HealthStatus.HEALTHY,
            message=f"Running version {current_version} (update check unavailable)",
            details={"current_version": current_version},
            timestamp=datetime.now(timezone.utc),
        )

    if latest_version != current_version:
        return HealthResult(
            component="update-available",
            status=HealthStatus.DEGRADED,
            message=f"Update available: {current_version} -> {latest_version}",
            details={
                "current_version": current_version,
                "latest_version": latest_version,
            },
            timestamp=datetime.now(timezone.utc),
        )

    return HealthResult(
        component="update-available",
        status=HealthStatus.HEALTHY,
        message=f"Running latest version {current_version}",
        details={"current_version": current_version},
        timestamp=datetime.now(timezone.utc),
    )


def create_doctor_health_checker() -> HealthChecker:
    """Create a HealthChecker with all doctor health checks registered.

    Returns:
        HealthChecker with all 5 doctor checks.
    """
    checker = HealthChecker()
    checker.register("python-environment", check_python_environment)
    checker.register("package-installation", check_package_installation)
    checker.register("config-directory", check_config_directory)
    checker.register("agent-files", check_agent_files)
    checker.register("update-available", check_update_available)
    return checker
