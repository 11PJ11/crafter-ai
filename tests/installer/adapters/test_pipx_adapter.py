"""Tests for PipxPort Protocol and SubprocessPipxAdapter.

All tests mock subprocess to avoid actual pipx calls.
Tests follow the hexagonal architecture pattern.
"""

import json
from pathlib import Path
from typing import Protocol
from unittest.mock import MagicMock, patch

from crafter_ai.installer.adapters.pipx_adapter import SubprocessPipxAdapter
from crafter_ai.installer.ports.pipx_port import (
    InstalledPackage,
    InstallResult,
    PipxPort,
    UninstallResult,
)


class TestPipxPortProtocol:
    """Tests for PipxPort Protocol definition."""

    def test_pipx_port_is_protocol(self) -> None:
        """PipxPort should be a Protocol class."""
        assert issubclass(PipxPort, Protocol)

    def test_pipx_port_is_runtime_checkable(self) -> None:
        """PipxPort should be runtime_checkable for isinstance checks."""
        assert hasattr(PipxPort, "__protocol_attrs__") or hasattr(
            PipxPort, "_is_runtime_protocol"
        )


class TestDataclasses:
    """Tests for dataclasses used by PipxPort."""

    def test_install_result_has_required_fields(self) -> None:
        """InstallResult should have success, version, install_path, error_message."""
        result = InstallResult(
            success=True,
            version="0.1.0",
            install_path=Path("/home/user/.local/bin/crafter-ai"),
            error_message=None,
        )
        assert result.success is True
        assert result.version == "0.1.0"
        assert result.install_path == Path("/home/user/.local/bin/crafter-ai")
        assert result.error_message is None

    def test_install_result_failure_case(self) -> None:
        """InstallResult should support failure with error message."""
        result = InstallResult(
            success=False,
            version=None,
            install_path=None,
            error_message="Package already installed",
        )
        assert result.success is False
        assert result.version is None
        assert result.install_path is None
        assert result.error_message == "Package already installed"

    def test_uninstall_result_has_required_fields(self) -> None:
        """UninstallResult should have success and error_message."""
        result = UninstallResult(success=True, error_message=None)
        assert result.success is True
        assert result.error_message is None

    def test_uninstall_result_failure_case(self) -> None:
        """UninstallResult should support failure with error message."""
        result = UninstallResult(success=False, error_message="Package not found")
        assert result.success is False
        assert result.error_message == "Package not found"

    def test_installed_package_has_required_fields(self) -> None:
        """InstalledPackage should have name, version, and path."""
        package = InstalledPackage(
            name="crafter-ai",
            version="0.1.0",
            path=Path("/home/user/.local/pipx/venvs/crafter-ai"),
        )
        assert package.name == "crafter-ai"
        assert package.version == "0.1.0"
        assert package.path == Path("/home/user/.local/pipx/venvs/crafter-ai")


class TestSubprocessPipxAdapterImplementsProtocol:
    """Tests that SubprocessPipxAdapter implements PipxPort."""

    def test_adapter_implements_pipx_port(self) -> None:
        """SubprocessPipxAdapter should implement PipxPort protocol."""
        adapter = SubprocessPipxAdapter()
        assert isinstance(adapter, PipxPort)

    def test_adapter_has_is_available_method(self) -> None:
        """SubprocessPipxAdapter should have is_available method."""
        adapter = SubprocessPipxAdapter()
        assert hasattr(adapter, "is_available")
        assert callable(adapter.is_available)

    def test_adapter_has_install_method(self) -> None:
        """SubprocessPipxAdapter should have install method."""
        adapter = SubprocessPipxAdapter()
        assert hasattr(adapter, "install")
        assert callable(adapter.install)

    def test_adapter_has_uninstall_method(self) -> None:
        """SubprocessPipxAdapter should have uninstall method."""
        adapter = SubprocessPipxAdapter()
        assert hasattr(adapter, "uninstall")
        assert callable(adapter.uninstall)

    def test_adapter_has_list_packages_method(self) -> None:
        """SubprocessPipxAdapter should have list_packages method."""
        adapter = SubprocessPipxAdapter()
        assert hasattr(adapter, "list_packages")
        assert callable(adapter.list_packages)


class TestIsAvailable:
    """Tests for is_available method."""

    @patch("subprocess.run")
    def test_returns_true_when_pipx_installed(self, mock_run: MagicMock) -> None:
        """is_available should return True when pipx is installed."""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="1.4.3\n",
        )

        adapter = SubprocessPipxAdapter()
        result = adapter.is_available()

        assert result is True
        mock_run.assert_called_once()

    @patch("subprocess.run")
    def test_returns_false_when_pipx_not_found(self, mock_run: MagicMock) -> None:
        """is_available should return False when pipx is not installed."""
        mock_run.side_effect = FileNotFoundError("pipx not found")

        adapter = SubprocessPipxAdapter()
        result = adapter.is_available()

        assert result is False

    @patch("subprocess.run")
    def test_returns_false_when_pipx_returns_error(self, mock_run: MagicMock) -> None:
        """is_available should return False when pipx returns non-zero exit code."""
        mock_run.return_value = MagicMock(
            returncode=1,
            stderr="error",
        )

        adapter = SubprocessPipxAdapter()
        result = adapter.is_available()

        assert result is False

    @patch("subprocess.run")
    def test_calls_pipx_version(self, mock_run: MagicMock) -> None:
        """is_available should call 'pipx --version'."""
        mock_run.return_value = MagicMock(returncode=0, stdout="1.4.3\n")

        adapter = SubprocessPipxAdapter()
        adapter.is_available()

        call_args = mock_run.call_args
        cmd = call_args[0][0]
        assert "pipx" in cmd
        assert "--version" in cmd


class TestInstall:
    """Tests for install method."""

    @patch("subprocess.run")
    def test_install_returns_success_with_version_and_path(
        self, mock_run: MagicMock
    ) -> None:
        """install should return InstallResult with version and path on success."""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="  installed package crafter-ai 0.1.0, installed using Python 3.11.0\n"
            "  These apps are now globally available\n"
            "    - crafter-ai\n"
            "done! crafter-ai 0.1.0 is installed and available globally\n",
            stderr="",
        )

        adapter = SubprocessPipxAdapter()
        wheel_path = Path("/tmp/dist/crafter_ai-0.1.0-py3-none-any.whl")
        result = adapter.install(wheel_path)

        assert result.success is True
        assert result.version == "0.1.0"
        assert result.error_message is None

    @patch("subprocess.run")
    def test_install_with_force_flag(self, mock_run: MagicMock) -> None:
        """install with force=True should pass --force flag to pipx."""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="done! crafter-ai 0.1.0 is installed\n",
            stderr="",
        )

        adapter = SubprocessPipxAdapter()
        wheel_path = Path("/tmp/dist/crafter_ai-0.1.0-py3-none-any.whl")
        adapter.install(wheel_path, force=True)

        call_args = mock_run.call_args
        cmd = call_args[0][0]
        assert "--force" in cmd

    @patch("subprocess.run")
    def test_install_returns_failure_with_error_message(
        self, mock_run: MagicMock
    ) -> None:
        """install should return InstallResult with error on failure."""
        mock_run.return_value = MagicMock(
            returncode=1,
            stdout="",
            stderr="Error: crafter-ai is already installed. Use --force to reinstall.",
        )

        adapter = SubprocessPipxAdapter()
        wheel_path = Path("/tmp/dist/crafter_ai-0.1.0-py3-none-any.whl")
        result = adapter.install(wheel_path)

        assert result.success is False
        assert result.error_message is not None
        assert "already installed" in result.error_message

    @patch("subprocess.run")
    def test_install_calls_pipx_with_wheel_path(self, mock_run: MagicMock) -> None:
        """install should call 'pipx install <wheel_path>'."""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="done! crafter-ai 0.1.0 is installed\n",
            stderr="",
        )

        adapter = SubprocessPipxAdapter()
        wheel_path = Path("/tmp/dist/crafter_ai-0.1.0-py3-none-any.whl")
        adapter.install(wheel_path)

        call_args = mock_run.call_args
        cmd = call_args[0][0]
        assert "pipx" in cmd
        assert "install" in cmd
        assert str(wheel_path) in cmd


class TestUninstall:
    """Tests for uninstall method."""

    @patch("subprocess.run")
    def test_uninstall_returns_success_when_package_removed(
        self, mock_run: MagicMock
    ) -> None:
        """uninstall should return success when package is removed."""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="uninstalled crafter-ai! \n",
            stderr="",
        )

        adapter = SubprocessPipxAdapter()
        result = adapter.uninstall("crafter-ai")

        assert result.success is True
        assert result.error_message is None

    @patch("subprocess.run")
    def test_uninstall_returns_failure_when_package_not_found(
        self, mock_run: MagicMock
    ) -> None:
        """uninstall should return failure when package not found."""
        mock_run.return_value = MagicMock(
            returncode=1,
            stdout="",
            stderr="Error: 'crafter-ai' is not installed",
        )

        adapter = SubprocessPipxAdapter()
        result = adapter.uninstall("crafter-ai")

        assert result.success is False
        assert result.error_message is not None
        assert "not installed" in result.error_message

    @patch("subprocess.run")
    def test_uninstall_calls_pipx_uninstall(self, mock_run: MagicMock) -> None:
        """uninstall should call 'pipx uninstall <package_name>'."""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="uninstalled crafter-ai!\n",
            stderr="",
        )

        adapter = SubprocessPipxAdapter()
        adapter.uninstall("crafter-ai")

        call_args = mock_run.call_args
        cmd = call_args[0][0]
        assert "pipx" in cmd
        assert "uninstall" in cmd
        assert "crafter-ai" in cmd


class TestListPackages:
    """Tests for list_packages method."""

    @patch("subprocess.run")
    def test_list_packages_returns_installed_packages(
        self, mock_run: MagicMock
    ) -> None:
        """list_packages should return list of InstalledPackage."""
        pipx_list_output = {
            "venvs": {
                "crafter-ai": {
                    "metadata": {
                        "main_package": {
                            "package": "crafter-ai",
                            "package_version": "0.1.0",
                        }
                    },
                    "venv_path": "/home/user/.local/pipx/venvs/crafter-ai",
                }
            }
        }
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout=json.dumps(pipx_list_output),
            stderr="",
        )

        adapter = SubprocessPipxAdapter()
        result = adapter.list_packages()

        assert len(result) == 1
        assert result[0].name == "crafter-ai"
        assert result[0].version == "0.1.0"
        assert result[0].path == Path("/home/user/.local/pipx/venvs/crafter-ai")

    @patch("subprocess.run")
    def test_list_packages_returns_empty_list_when_no_packages(
        self, mock_run: MagicMock
    ) -> None:
        """list_packages should return empty list when no packages installed."""
        pipx_list_output = {"venvs": {}}
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout=json.dumps(pipx_list_output),
            stderr="",
        )

        adapter = SubprocessPipxAdapter()
        result = adapter.list_packages()

        assert result == []

    @patch("subprocess.run")
    def test_list_packages_calls_pipx_list_json(self, mock_run: MagicMock) -> None:
        """list_packages should call 'pipx list --json'."""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout='{"venvs": {}}',
            stderr="",
        )

        adapter = SubprocessPipxAdapter()
        adapter.list_packages()

        call_args = mock_run.call_args
        cmd = call_args[0][0]
        assert "pipx" in cmd
        assert "list" in cmd
        assert "--json" in cmd

    @patch("subprocess.run")
    def test_list_packages_handles_multiple_packages(self, mock_run: MagicMock) -> None:
        """list_packages should handle multiple installed packages."""
        pipx_list_output = {
            "venvs": {
                "crafter-ai": {
                    "metadata": {
                        "main_package": {
                            "package": "crafter-ai",
                            "package_version": "0.1.0",
                        }
                    },
                    "venv_path": "/home/user/.local/pipx/venvs/crafter-ai",
                },
                "black": {
                    "metadata": {
                        "main_package": {
                            "package": "black",
                            "package_version": "23.12.0",
                        }
                    },
                    "venv_path": "/home/user/.local/pipx/venvs/black",
                },
            }
        }
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout=json.dumps(pipx_list_output),
            stderr="",
        )

        adapter = SubprocessPipxAdapter()
        result = adapter.list_packages()

        assert len(result) == 2
        names = [pkg.name for pkg in result]
        assert "crafter-ai" in names
        assert "black" in names

    @patch("subprocess.run")
    def test_list_packages_returns_empty_on_error(self, mock_run: MagicMock) -> None:
        """list_packages should return empty list when pipx list fails."""
        mock_run.return_value = MagicMock(
            returncode=1,
            stdout="",
            stderr="Error running pipx",
        )

        adapter = SubprocessPipxAdapter()
        result = adapter.list_packages()

        assert result == []
