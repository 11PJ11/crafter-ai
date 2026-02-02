"""Core pre-flight checks, build checks, install checks, and doctor health checks for the installer."""

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
from crafter_ai.installer.checks.install_checks import (
    check_install_path_resolved,
    check_pipx_isolation,
    check_wheel_exists,
    check_wheel_format,
    create_install_check_registry,
)


__all__ = [
    "check_agent_files",
    "check_build_package_installed",
    "check_clean_git_status",
    "check_config_directory",
    "check_git_available",
    # Install-specific checks
    "check_install_path_resolved",
    "check_internet_connectivity",
    "check_package_installation",
    "check_pipx_available",
    "check_pipx_isolation",
    # Build-specific checks
    "check_pyproject_exists",
    # Doctor health checks
    "check_python_environment",
    # Core pre-flight checks
    "check_python_version",
    "check_src_directory_exists",
    "check_update_available",
    "check_version_not_released",
    "check_wheel_exists",
    "check_wheel_format",
    "create_build_check_registry",
    "create_core_check_registry",
    "create_doctor_health_checker",
    "create_install_check_registry",
]
