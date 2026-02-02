"""PipxPort Protocol - abstract interface for pipx operations.

This is a hexagonal architecture port that defines how the application
interacts with pipx for package installation/uninstallation. Adapters
implement this protocol for different execution mechanisms (subprocess, etc.).
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol, runtime_checkable


@dataclass
class InstallResult:
    """Result of a pipx install operation.

    Attributes:
        success: True if installation succeeded, False otherwise.
        version: The installed version, or None if installation failed.
        install_path: Path where the package was installed, or None if failed.
        error_message: Error description if installation failed, None otherwise.
    """

    success: bool
    version: str | None
    install_path: Path | None
    error_message: str | None


@dataclass
class UninstallResult:
    """Result of a pipx uninstall operation.

    Attributes:
        success: True if uninstallation succeeded, False otherwise.
        error_message: Error description if uninstallation failed, None otherwise.
    """

    success: bool
    error_message: str | None


@dataclass
class InstalledPackage:
    """Information about an installed pipx package.

    Attributes:
        name: The package name.
        version: The installed version.
        path: Path to the virtual environment where the package is installed.
    """

    name: str
    version: str
    path: Path


@runtime_checkable
class PipxPort(Protocol):
    """Protocol defining pipx operations interface.

    This is a hexagonal port - the application depends on this interface,
    not on concrete implementations. Adapters (like SubprocessPipxAdapter)
    implement this protocol.

    Used by:
        - InstallService for installing packages via pipx
        - UninstallService for removing packages
    """

    def is_available(self) -> bool:
        """Check if pipx is available on the system.

        Returns:
            True if pipx is installed and accessible, False otherwise.
        """
        ...

    def install(self, wheel_path: Path, force: bool = False) -> InstallResult:
        """Install a package from a wheel file using pipx.

        Args:
            wheel_path: Path to the .whl file to install.
            force: If True, reinstall even if already installed.

        Returns:
            InstallResult with success status, version, path, or error message.
        """
        ...

    def uninstall(self, package_name: str) -> UninstallResult:
        """Uninstall a package using pipx.

        Args:
            package_name: Name of the package to uninstall.

        Returns:
            UninstallResult with success status or error message.
        """
        ...

    def list_packages(self) -> list[InstalledPackage]:
        """List all packages installed via pipx.

        Returns:
            List of InstalledPackage objects, empty list if none or on error.
        """
        ...
