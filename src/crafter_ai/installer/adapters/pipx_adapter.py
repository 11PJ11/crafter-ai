"""SubprocessPipxAdapter - subprocess-based implementation of PipxPort.

This adapter implements the PipxPort protocol using subprocess to execute
pipx commands. It provides installation, uninstallation, and package listing
functionality with proper error handling.
"""

import json
import re
import subprocess
from pathlib import Path

from crafter_ai.installer.ports.pipx_port import (
    InstalledPackage,
    InstallResult,
    UninstallResult,
)


class SubprocessPipxAdapter:
    """Subprocess-based pipx adapter implementing PipxPort.

    This adapter executes pipx commands via subprocess.run() and parses
    their output. It handles error cases gracefully.

    Used by:
        - InstallService for installing packages via pipx
        - UninstallService for removing packages
    """

    def is_available(self) -> bool:
        """Check if pipx is available on the system.

        Runs 'pipx --version' to check if pipx is installed and accessible.

        Returns:
            True if pipx is installed and accessible, False otherwise.
        """
        try:
            result = subprocess.run(
                ["pipx", "--version"],
                capture_output=True,
                text=True,
                check=False,
            )
            return result.returncode == 0
        except FileNotFoundError:
            return False

    def install(self, wheel_path: Path, force: bool = False) -> InstallResult:
        """Install a package from a wheel file using pipx.

        Runs 'pipx install <wheel_path>' with optional --force flag.

        Args:
            wheel_path: Path to the .whl file to install.
            force: If True, pass --force flag to reinstall.

        Returns:
            InstallResult with success status, version, path, or error message.
        """
        cmd = ["pipx", "install", str(wheel_path)]
        if force:
            cmd.append("--force")

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=False,
        )

        if result.returncode != 0:
            return InstallResult(
                success=False,
                version=None,
                install_path=None,
                error_message=result.stderr or result.stdout,
            )

        # Parse version from output
        # Example: "done! crafter-ai 0.1.0 is installed"
        version = self._parse_version_from_output(result.stdout)
        install_path = self._parse_install_path_from_output(result.stdout)

        return InstallResult(
            success=True,
            version=version,
            install_path=install_path,
            error_message=None,
        )

    def uninstall(self, package_name: str) -> UninstallResult:
        """Uninstall a package using pipx.

        Runs 'pipx uninstall <package_name>'.

        Args:
            package_name: Name of the package to uninstall.

        Returns:
            UninstallResult with success status or error message.
        """
        result = subprocess.run(
            ["pipx", "uninstall", package_name],
            capture_output=True,
            text=True,
            check=False,
        )

        if result.returncode != 0:
            return UninstallResult(
                success=False,
                error_message=result.stderr or result.stdout,
            )

        return UninstallResult(
            success=True,
            error_message=None,
        )

    def list_packages(self) -> list[InstalledPackage]:
        """List all packages installed via pipx.

        Runs 'pipx list --json' and parses the JSON output.

        Returns:
            List of InstalledPackage objects, empty list if none or on error.
        """
        result = subprocess.run(
            ["pipx", "list", "--json"],
            capture_output=True,
            text=True,
            check=False,
        )

        if result.returncode != 0:
            return []

        try:
            data = json.loads(result.stdout)
            packages = []

            venvs = data.get("venvs", {})
            for _venv_name, venv_info in venvs.items():
                metadata = venv_info.get("metadata", {})
                main_package = metadata.get("main_package", {})

                name = main_package.get("package", "")
                version = main_package.get("package_version", "")
                path_str = venv_info.get("venv_path", "")

                if name and version:
                    packages.append(
                        InstalledPackage(
                            name=name,
                            version=version,
                            path=Path(path_str),
                        )
                    )

            return packages
        except json.JSONDecodeError:
            return []

    def _parse_version_from_output(self, output: str) -> str | None:
        """Parse version from pipx install output.

        Looks for patterns like:
        - "installed package crafter-ai 0.1.0"
        - "done! crafter-ai 0.1.0 is installed"

        Args:
            output: The stdout from pipx install command.

        Returns:
            The version string, or None if not found.
        """
        # Pattern: "installed package <name> <version>"
        match = re.search(r"installed package \S+ (\d+\.\d+\.\d+)", output)
        if match:
            return match.group(1)

        # Pattern: "done! <name> <version> is installed"
        match = re.search(r"done! \S+ (\d+\.\d+\.\d+) is installed", output)
        if match:
            return match.group(1)

        return None

    def _parse_install_path_from_output(self, output: str) -> Path | None:
        """Parse installation path from pipx install output.

        Note: pipx doesn't always output the install path directly.
        This method returns None as pipx install output doesn't typically
        include the full path. Use list_packages() to get paths.

        Args:
            output: The stdout from pipx install command.

        Returns:
            The installation path, or None if not found.
        """
        # pipx install output doesn't include the full path
        # Return None - callers should use list_packages() for paths
        return None
