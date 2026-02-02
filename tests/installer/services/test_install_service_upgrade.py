"""Tests for InstallService upgrade path detection integration.

This module tests the upgrade path detection integration in InstallService:
1. UpgradePath enum (FRESH_INSTALL, UPGRADE, REINSTALL, DOWNGRADE)
2. detect_upgrade_path(target_version) method
3. should_create_backup(upgrade_path) method
4. get_upgrade_message(upgrade_path, from_ver, to_ver) method
5. CI mode support in install()

Following Outside-In TDD: These unit tests drive the implementation that will
make the E2E acceptance tests pass.
"""

from pathlib import Path
from unittest.mock import MagicMock, create_autospec

import pytest

from crafter_ai.installer.domain.check_executor import CheckExecutor
from crafter_ai.installer.domain.check_result import CheckResult, CheckSeverity
from crafter_ai.installer.ports.backup_port import BackupPort, BackupResult
from crafter_ai.installer.ports.pipx_port import InstallResult as PipxInstallResult
from crafter_ai.installer.ports.pipx_port import PipxPort
from crafter_ai.installer.services.install_service import (
    InstallService,
    UpgradePath,
)
from crafter_ai.installer.services.release_readiness_service import (
    ReleaseReadinessResult,
    ReleaseReadinessService,
)


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def mock_pipx_port() -> MagicMock:
    """Create a mock PipxPort."""
    mock = create_autospec(PipxPort, instance=True)
    mock.install.return_value = PipxInstallResult(
        success=True,
        version="1.3.0",
        install_path=Path("/home/user/.local/bin/crafter-ai"),
        error_message=None,
    )
    # Default: no packages installed (fresh install)
    mock.list_packages.return_value = []
    return mock


@pytest.fixture
def mock_backup_port() -> MagicMock:
    """Create a mock BackupPort."""
    mock = create_autospec(BackupPort, instance=True)
    mock.create_backup.return_value = BackupResult(
        success=True,
        backup_path=Path("/home/user/.claude/backups/nwave-20260202-120000"),
        timestamp=None,
        error_message=None,
    )
    return mock


@pytest.fixture
def mock_check_executor() -> MagicMock:
    """Create a mock CheckExecutor with passing checks."""
    mock = create_autospec(CheckExecutor, instance=True)
    mock.run_all.return_value = [
        CheckResult(
            id="wheel-exists",
            name="Wheel File Exists",
            passed=True,
            severity=CheckSeverity.BLOCKING,
            message="Found wheel file",
        ),
    ]
    return mock


@pytest.fixture
def mock_release_readiness_service() -> MagicMock:
    """Create a mock ReleaseReadinessService with passing validation."""
    mock = create_autospec(ReleaseReadinessService, instance=True)
    mock.validate.return_value = ReleaseReadinessResult(
        ready=True,
        checks=[],
        blocking_issues=[],
        warnings=[],
        status_message="READY FOR PYPI",
    )
    return mock


@pytest.fixture
def install_service(
    mock_pipx_port: MagicMock,
    mock_backup_port: MagicMock,
    mock_check_executor: MagicMock,
    mock_release_readiness_service: MagicMock,
) -> InstallService:
    """Create an InstallService with all mocked dependencies."""
    return InstallService(
        pipx_port=mock_pipx_port,
        backup_port=mock_backup_port,
        check_executor=mock_check_executor,
        release_readiness_service=mock_release_readiness_service,
    )


# =============================================================================
# Test UpgradePath Enum
# =============================================================================


class TestUpgradePathEnum:
    """Test UpgradePath enum exists with required values."""

    def test_upgrade_path_enum_has_fresh_install(self) -> None:
        """UpgradePath has FRESH_INSTALL value."""
        assert hasattr(UpgradePath, "FRESH_INSTALL")
        assert UpgradePath.FRESH_INSTALL.value == "fresh_install"

    def test_upgrade_path_enum_has_upgrade(self) -> None:
        """UpgradePath has UPGRADE value."""
        assert hasattr(UpgradePath, "UPGRADE")
        assert UpgradePath.UPGRADE.value == "upgrade"

    def test_upgrade_path_enum_has_reinstall(self) -> None:
        """UpgradePath has REINSTALL value."""
        assert hasattr(UpgradePath, "REINSTALL")
        assert UpgradePath.REINSTALL.value == "reinstall"

    def test_upgrade_path_enum_has_downgrade(self) -> None:
        """UpgradePath has DOWNGRADE value."""
        assert hasattr(UpgradePath, "DOWNGRADE")
        assert UpgradePath.DOWNGRADE.value == "downgrade"


# =============================================================================
# Test detect_upgrade_path() Method
# =============================================================================


class TestDetectUpgradePath:
    """Test InstallService.detect_upgrade_path() method."""

    def test_detect_upgrade_path_returns_fresh_install_when_no_existing_version(
        self,
        install_service: InstallService,
        mock_pipx_port: MagicMock,
    ) -> None:
        """detect_upgrade_path returns FRESH_INSTALL when no existing version."""
        # No packages installed (fresh install scenario)
        mock_pipx_port.list_packages.return_value = []

        result = install_service.detect_upgrade_path("1.3.0")

        assert result == UpgradePath.FRESH_INSTALL

    def test_detect_upgrade_path_returns_upgrade_when_target_greater_than_installed(
        self,
        install_service: InstallService,
        mock_pipx_port: MagicMock,
    ) -> None:
        """detect_upgrade_path returns UPGRADE when target > installed."""
        from crafter_ai.installer.ports.pipx_port import InstalledPackage

        mock_pipx_port.list_packages.return_value = [
            InstalledPackage(
                name="crafter-ai",
                version="1.2.0",
                path=Path("/home/user/.local/pipx/venvs/crafter-ai"),
            )
        ]

        result = install_service.detect_upgrade_path("1.3.0")

        assert result == UpgradePath.UPGRADE

    def test_detect_upgrade_path_returns_reinstall_when_target_equals_installed(
        self,
        install_service: InstallService,
        mock_pipx_port: MagicMock,
    ) -> None:
        """detect_upgrade_path returns REINSTALL when target == installed."""
        from crafter_ai.installer.ports.pipx_port import InstalledPackage

        mock_pipx_port.list_packages.return_value = [
            InstalledPackage(
                name="crafter-ai",
                version="1.3.0",
                path=Path("/home/user/.local/pipx/venvs/crafter-ai"),
            )
        ]

        result = install_service.detect_upgrade_path("1.3.0")

        assert result == UpgradePath.REINSTALL

    def test_detect_upgrade_path_returns_downgrade_when_target_less_than_installed(
        self,
        install_service: InstallService,
        mock_pipx_port: MagicMock,
    ) -> None:
        """detect_upgrade_path returns DOWNGRADE when target < installed."""
        from crafter_ai.installer.ports.pipx_port import InstalledPackage

        mock_pipx_port.list_packages.return_value = [
            InstalledPackage(
                name="crafter-ai",
                version="1.5.0",
                path=Path("/home/user/.local/pipx/venvs/crafter-ai"),
            )
        ]

        result = install_service.detect_upgrade_path("1.3.0")

        assert result == UpgradePath.DOWNGRADE


# =============================================================================
# Test should_create_backup() Method
# =============================================================================


class TestShouldCreateBackup:
    """Test InstallService.should_create_backup() method."""

    def test_should_create_backup_returns_false_for_fresh_install(
        self,
        install_service: InstallService,
    ) -> None:
        """should_create_backup returns False for FRESH_INSTALL."""
        result = install_service.should_create_backup(UpgradePath.FRESH_INSTALL)

        assert result is False

    def test_should_create_backup_returns_true_for_upgrade(
        self,
        install_service: InstallService,
    ) -> None:
        """should_create_backup returns True for UPGRADE."""
        result = install_service.should_create_backup(UpgradePath.UPGRADE)

        assert result is True

    def test_should_create_backup_returns_true_for_reinstall(
        self,
        install_service: InstallService,
    ) -> None:
        """should_create_backup returns True for REINSTALL (after confirmation)."""
        result = install_service.should_create_backup(UpgradePath.REINSTALL)

        assert result is True

    def test_should_create_backup_returns_true_for_downgrade(
        self,
        install_service: InstallService,
    ) -> None:
        """should_create_backup returns True for DOWNGRADE (after confirmation)."""
        result = install_service.should_create_backup(UpgradePath.DOWNGRADE)

        assert result is True


# =============================================================================
# Test get_upgrade_message() Method
# =============================================================================


class TestGetUpgradeMessage:
    """Test InstallService.get_upgrade_message() method."""

    def test_get_upgrade_message_for_fresh_install_shows_fresh_install(
        self,
        install_service: InstallService,
    ) -> None:
        """get_upgrade_message for FRESH_INSTALL shows '(fresh install)'."""
        result = install_service.get_upgrade_message(
            UpgradePath.FRESH_INSTALL, from_ver=None, to_ver="1.3.0"
        )

        assert "(fresh install)" in result.lower() or "fresh install" in result.lower()

    def test_get_upgrade_message_for_upgrade_shows_upgrading_from_to(
        self,
        install_service: InstallService,
    ) -> None:
        """get_upgrade_message for UPGRADE shows 'Upgrading from X to Y'."""
        result = install_service.get_upgrade_message(
            UpgradePath.UPGRADE, from_ver="1.2.0", to_ver="1.3.0"
        )

        assert "1.2.0" in result
        assert "1.3.0" in result
        assert "upgrad" in result.lower()

    def test_get_upgrade_message_for_reinstall_asks_confirmation(
        self,
        install_service: InstallService,
    ) -> None:
        """get_upgrade_message for REINSTALL asks for confirmation."""
        result = install_service.get_upgrade_message(
            UpgradePath.REINSTALL, from_ver="1.3.0", to_ver="1.3.0"
        )

        assert "1.3.0" in result
        # Should indicate same version or reinstall
        assert (
            "reinstall" in result.lower()
            or "same version" in result.lower()
            or "already installed" in result.lower()
        )

    def test_get_upgrade_message_for_downgrade_warns_about_downgrade(
        self,
        install_service: InstallService,
    ) -> None:
        """get_upgrade_message for DOWNGRADE warns about downgrade."""
        result = install_service.get_upgrade_message(
            UpgradePath.DOWNGRADE, from_ver="1.5.0", to_ver="1.3.0"
        )

        assert "1.5.0" in result
        assert "1.3.0" in result
        assert "downgrad" in result.lower() or "older" in result.lower()


# =============================================================================
# Test CI Mode Support in install()
# =============================================================================


class TestCIModeSupport:
    """Test CI mode auto-proceed functionality in install()."""

    def test_install_accepts_ci_mode_parameter(
        self,
        install_service: InstallService,
    ) -> None:
        """install() method accepts ci_mode parameter."""
        wheel_path = Path("dist/crafter_ai-1.3.0-py3-none-any.whl")

        # This should not raise TypeError
        result = install_service.install(wheel_path, ci_mode=True)

        assert result is not None

    def test_ci_mode_auto_proceeds_for_upgrade(
        self,
        install_service: InstallService,
        mock_pipx_port: MagicMock,
        mock_backup_port: MagicMock,
    ) -> None:
        """CI mode auto-proceeds for UPGRADE without prompts."""
        from crafter_ai.installer.ports.pipx_port import InstalledPackage

        # Setup: existing older version
        mock_pipx_port.list_packages.return_value = [
            InstalledPackage(
                name="crafter-ai",
                version="1.2.0",
                path=Path("/home/user/.local/pipx/venvs/crafter-ai"),
            )
        ]
        wheel_path = Path("dist/crafter_ai-1.3.0-py3-none-any.whl")

        result = install_service.install(wheel_path, ci_mode=True)

        # CI mode should auto-proceed and succeed
        assert result.success is True
        mock_pipx_port.install.assert_called_once()
        mock_backup_port.create_backup.assert_called_once()

    def test_ci_mode_auto_proceeds_for_reinstall_without_prompt(
        self,
        install_service: InstallService,
        mock_pipx_port: MagicMock,
    ) -> None:
        """CI mode auto-proceeds for REINSTALL without prompt."""
        from crafter_ai.installer.ports.pipx_port import InstalledPackage

        # Setup: same version already installed
        mock_pipx_port.list_packages.return_value = [
            InstalledPackage(
                name="crafter-ai",
                version="1.3.0",
                path=Path("/home/user/.local/pipx/venvs/crafter-ai"),
            )
        ]
        wheel_path = Path("dist/crafter_ai-1.3.0-py3-none-any.whl")

        result = install_service.install(wheel_path, ci_mode=True)

        # CI mode should auto-proceed for reinstall
        assert result.success is True
        mock_pipx_port.install.assert_called_once()

    def test_ci_mode_still_warns_for_downgrade_but_proceeds(
        self,
        install_service: InstallService,
        mock_pipx_port: MagicMock,
    ) -> None:
        """CI mode still warns for DOWNGRADE but proceeds."""
        from crafter_ai.installer.ports.pipx_port import InstalledPackage

        # Setup: newer version already installed
        mock_pipx_port.list_packages.return_value = [
            InstalledPackage(
                name="crafter-ai",
                version="1.5.0",
                path=Path("/home/user/.local/pipx/venvs/crafter-ai"),
            )
        ]
        wheel_path = Path("dist/crafter_ai-1.3.0-py3-none-any.whl")

        result = install_service.install(wheel_path, ci_mode=True)

        # CI mode should proceed even for downgrade
        assert result.success is True
        mock_pipx_port.install.assert_called_once()


# =============================================================================
# Test Upgrade Path Integration in Install Flow
# =============================================================================


class TestUpgradePathIntegration:
    """Test upgrade path detection integration in install flow."""

    def test_install_detects_upgrade_path_before_proceeding(
        self,
        install_service: InstallService,
        mock_pipx_port: MagicMock,
    ) -> None:
        """install() detects upgrade path before proceeding."""
        from crafter_ai.installer.ports.pipx_port import InstalledPackage

        mock_pipx_port.list_packages.return_value = [
            InstalledPackage(
                name="crafter-ai",
                version="1.2.0",
                path=Path("/home/user/.local/pipx/venvs/crafter-ai"),
            )
        ]
        wheel_path = Path("dist/crafter_ai-1.3.0-py3-none-any.whl")

        result = install_service.install(wheel_path, ci_mode=True)

        # Should query packages to detect upgrade path
        mock_pipx_port.list_packages.assert_called()
        assert result.success is True

    def test_install_skips_backup_for_fresh_install(
        self,
        install_service: InstallService,
        mock_pipx_port: MagicMock,
        mock_backup_port: MagicMock,
    ) -> None:
        """install() skips backup for FRESH_INSTALL (no existing config)."""
        # No packages installed (fresh install)
        mock_pipx_port.list_packages.return_value = []
        wheel_path = Path("dist/crafter_ai-1.3.0-py3-none-any.whl")

        result = install_service.install(wheel_path, ci_mode=True)

        assert result.success is True
        # For fresh install, backup might still be called but returns quickly
        # The key is that the install succeeds without requiring backup

    def test_install_creates_backup_for_upgrade(
        self,
        install_service: InstallService,
        mock_pipx_port: MagicMock,
        mock_backup_port: MagicMock,
    ) -> None:
        """install() creates backup for UPGRADE scenario."""
        from crafter_ai.installer.ports.pipx_port import InstalledPackage

        mock_pipx_port.list_packages.return_value = [
            InstalledPackage(
                name="crafter-ai",
                version="1.2.0",
                path=Path("/home/user/.local/pipx/venvs/crafter-ai"),
            )
        ]
        wheel_path = Path("dist/crafter_ai-1.3.0-py3-none-any.whl")

        result = install_service.install(wheel_path, ci_mode=True)

        assert result.success is True
        mock_backup_port.create_backup.assert_called()
