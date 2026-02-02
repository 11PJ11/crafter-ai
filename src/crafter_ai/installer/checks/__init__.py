"""Core pre-flight checks, build checks, and doctor health checks for the installer."""

from crafter_ai.installer.checks.build_checks import (
    check_build_package_installed,
    check_clean_git_status,
    check_pyproject_exists,
    check_src_directory_exists,
    check_version_not_released,
    create_build_check_registry,
)
from crafter_ai.installer.checks.core_checks import (
    check_git_available,
    check_internet_connectivity,
    check_pipx_available,
    check_python_version,
    create_core_check_registry,
)
from crafter_ai.installer.checks.health_checks import (
    check_agent_files,
    check_config_directory,
    check_package_installation,
    check_python_environment,
    check_update_available,
    create_doctor_health_checker,
)

__all__ = [
    # Core pre-flight checks
    "check_python_version",
    "check_git_available",
    "check_pipx_available",
    "check_internet_connectivity",
    "create_core_check_registry",
    # Build-specific checks
    "check_pyproject_exists",
    "check_build_package_installed",
    "check_src_directory_exists",
    "check_clean_git_status",
    "check_version_not_released",
    "create_build_check_registry",
    # Doctor health checks
    "check_python_environment",
    "check_package_installation",
    "check_config_directory",
    "check_agent_files",
    "check_update_available",
    "create_doctor_health_checker",
]
