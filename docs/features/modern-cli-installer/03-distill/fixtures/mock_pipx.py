"""
Mock PipxPort for Acceptance Tests
==================================

Provides controlled pipx behavior for testing installation
scenarios without actually installing packages.

Port Interface: nWave/core/installer/ports/pipx_port.py
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Protocol


@dataclass(frozen=True)
class PipxInstallResult:
    """Result of pipx install operation."""
    success: bool
    package: str
    version: Optional[str]
    error_message: Optional[str] = None


class PipxPort(Protocol):
    """
    Port interface for pipx operations.

    Abstracts pipx commands for testability.
    """

    def is_available(self) -> bool:
        """Check if pipx is available."""
        ...

    def get_version(self) -> str:
        """Get pipx version."""
        ...

    def install(
        self,
        package: str,
        force: bool = False,
        pip_args: Optional[List[str]] = None,
    ) -> PipxInstallResult:
        """Install package via pipx."""
        ...

    def uninstall(self, package: str) -> bool:
        """Uninstall package."""
        ...

    def list_packages(self) -> List[str]:
        """List installed packages."""
        ...


@dataclass
class MockPipxAdapter:
    """
    Mock implementation of PipxPort for testing.

    Provides controlled pipx behavior for installation tests.
    """

    # Pipx availability
    available: bool = True
    version: str = "1.4.3"

    # Installed packages
    installed_packages: Dict[str, str] = field(default_factory=dict)

    # Error simulation
    fail_install: bool = False
    fail_install_message: str = "Dependency conflict detected"

    fail_uninstall: bool = False
    fail_uninstall_message: str = "Package not found"

    # Install call tracking
    install_calls: List[Dict] = field(default_factory=list)
    uninstall_calls: List[str] = field(default_factory=list)

    def is_available(self) -> bool:
        """Return configured availability."""
        return self.available

    def get_version(self) -> str:
        """Return configured version."""
        return self.version

    def install(
        self,
        package: str,
        force: bool = False,
        pip_args: Optional[List[str]] = None,
    ) -> PipxInstallResult:
        """Simulate package installation."""
        # Track the call
        self.install_calls.append({
            "package": package,
            "force": force,
            "pip_args": pip_args,
        })

        if self.fail_install:
            return PipxInstallResult(
                success=False,
                package=package,
                version=None,
                error_message=self.fail_install_message,
            )

        # Extract version from wheel path or use default
        version = "1.3.0-dev-20260201-001"
        if "wheel" in package.lower() or package.endswith(".whl"):
            # Parse version from wheel filename
            # dist/nwave-1.3.0-dev-20260201-001-py3-none-any.whl
            try:
                parts = package.split("-")
                if len(parts) >= 4:
                    version = "-".join(parts[1:4])  # 1.3.0-dev-20260201
                    if len(parts) >= 5:
                        version = f"{version}-{parts[4]}"  # Add sequence
            except Exception:
                pass

        self.installed_packages["nwave"] = version

        return PipxInstallResult(
            success=True,
            package=package,
            version=version,
        )

    def uninstall(self, package: str) -> bool:
        """Simulate package uninstallation."""
        self.uninstall_calls.append(package)

        if self.fail_uninstall:
            return False

        if package in self.installed_packages:
            del self.installed_packages[package]
            return True

        return False

    def list_packages(self) -> List[str]:
        """Return list of installed packages."""
        return list(self.installed_packages.keys())

    # Test setup helpers

    def setup_available(self, version: str = "1.4.3") -> None:
        """Configure pipx as available."""
        self.available = True
        self.version = version

    def setup_unavailable(self) -> None:
        """Configure pipx as unavailable."""
        self.available = False

    def setup_existing_nwave(self, version: str = "1.2.0") -> None:
        """Configure mock with existing nwave installation."""
        self.installed_packages["nwave"] = version

    def setup_install_failure(self, message: str = "Dependency conflict detected") -> None:
        """Configure mock to fail on install."""
        self.fail_install = True
        self.fail_install_message = message

    def setup_install_success(self) -> None:
        """Configure mock for successful install."""
        self.fail_install = False

    def setup_dependency_conflict(self) -> None:
        """Configure mock to fail with dependency conflict."""
        self.fail_install = True
        self.fail_install_message = (
            "ERROR: Cannot install nwave because these package versions have conflicting dependencies:\n"
            "  nwave requires pydantic>=2.0, but you have pydantic 1.10.0 installed"
        )

    def get_last_install_call(self) -> Optional[Dict]:
        """Get the last install call for assertions."""
        return self.install_calls[-1] if self.install_calls else None

    def assert_installed_with_force(self) -> None:
        """Assert last install used --force flag."""
        last_call = self.get_last_install_call()
        assert last_call is not None, "No install calls recorded"
        assert last_call["force"] is True, "Install was not called with force=True"


def create_pipx_mock_available() -> MockPipxAdapter:
    """Factory: Create mock with pipx available."""
    mock = MockPipxAdapter()
    mock.setup_available()
    return mock


def create_pipx_mock_unavailable() -> MockPipxAdapter:
    """Factory: Create mock with pipx unavailable."""
    mock = MockPipxAdapter()
    mock.setup_unavailable()
    return mock


def create_pipx_mock_with_existing_nwave(version: str = "1.2.0") -> MockPipxAdapter:
    """Factory: Create mock with existing nwave installation."""
    mock = MockPipxAdapter()
    mock.setup_existing_nwave(version)
    return mock
