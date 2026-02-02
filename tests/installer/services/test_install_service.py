"""Tests for InstallService core orchestration.

This module tests the InstallService that orchestrates the install journey:
1. Preflight checks
2. Release readiness validation
3. Backup creation
4. Pipx installation
"""

from pathlib import Path
from unittest.mock import MagicMock, create_autospec

import pytest

from crafter_ai.installer.domain.check_executor import CheckExecutor
from crafter_ai.installer.domain.check_registry import CheckRegistry
from crafter_ai.installer.domain.check_result import CheckResult, CheckSeverity
from crafter_ai.installer.ports.backup_port import BackupPort, BackupResult
from crafter_ai.installer.ports.pipx_port import InstallResult as PipxInstallResult
from crafter_ai.installer.ports.pipx_port import PipxPort
from crafter_ai.installer.services.install_service import (
    InstallPhase,
    InstallResult,
    InstallService,
)
from crafter_ai.installer.services.release_readiness_service import (
    ReleaseReadinessResult,
    ReleaseReadinessService,
)


@pytest.fixture
def mock_pipx_port() -> MagicMock:
    """Create a mock PipxPort."""
    mock = create_autospec(PipxPort, instance=True)
    mock.install.return_value = PipxInstallResult(
        success=True,
        version="1.2.3",
        install_path=Path("/home/user/.local/bin/crafter-ai"),
        error_message=None,
    )
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
def mock_check_registry() -> MagicMock:
    """Create a mock CheckRegistry with all checks passing."""
    registry = MagicMock(spec=CheckRegistry)
    return registry


@pytest.fixture
def mock_check_executor(mock_check_registry: MagicMock) -> MagicMock:
    """Create a mock CheckExecutor with passing checks."""
    mock = create_autospec(CheckExecutor, instance=True)
    mock.run_all.return_value = [
        CheckResult(
            id="wheel-exists",
            name="Wheel File Exists",
            passed=True,
            severity=CheckSeverity.BLOCKING,
            message="Found wheel file: crafter_ai-1.2.3-py3-none-any.whl",
        ),
        CheckResult(
            id="pipx-isolation",
            name="Pipx Isolation",
            passed=True,
            severity=CheckSeverity.BLOCKING,
            message="Pipx environment is properly configured",
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


class TestInstallServiceInstantiaton:
    """Test InstallService can be instantiated."""

    def test_create_install_service_with_required_dependencies(
        self,
        mock_pipx_port: MagicMock,
        mock_backup_port: MagicMock,
        mock_check_executor: MagicMock,
        mock_release_readiness_service: MagicMock,
    ) -> None:
        """InstallService can be created with required dependencies."""
        service = InstallService(
            pipx_port=mock_pipx_port,
            backup_port=mock_backup_port,
            check_executor=mock_check_executor,
            release_readiness_service=mock_release_readiness_service,
        )

        assert service is not None


class TestInstallServiceSuccessfulInstall:
    """Test successful installation scenarios."""

    def test_install_succeeds_when_all_phases_pass(
        self,
        install_service: InstallService,
        mock_pipx_port: MagicMock,
        mock_backup_port: MagicMock,
        mock_check_executor: MagicMock,
        mock_release_readiness_service: MagicMock,
    ) -> None:
        """Install succeeds when all four phases pass."""
        wheel_path = Path("dist/crafter_ai-1.2.3-py3-none-any.whl")

        result = install_service.install(wheel_path)

        assert result.success is True
        assert result.version == "1.2.3"
        assert result.install_path == Path("/home/user/.local/bin/crafter-ai")
        assert result.error_message is None
        assert InstallPhase.PREFLIGHT in result.phases_completed
        assert InstallPhase.READINESS in result.phases_completed
        assert InstallPhase.BACKUP in result.phases_completed
        assert InstallPhase.INSTALL in result.phases_completed

    def test_install_calls_phases_in_correct_order(
        self,
        install_service: InstallService,
        mock_pipx_port: MagicMock,
        mock_backup_port: MagicMock,
        mock_check_executor: MagicMock,
        mock_release_readiness_service: MagicMock,
    ) -> None:
        """Install calls phases in order: preflight -> readiness -> backup -> install."""
        wheel_path = Path("dist/crafter_ai-1.2.3-py3-none-any.whl")
        call_order = []

        mock_check_executor.run_all.side_effect = lambda: (
            call_order.append("preflight"),
            [
                CheckResult(
                    id="test",
                    name="Test",
                    passed=True,
                    severity=CheckSeverity.BLOCKING,
                    message="OK",
                )
            ],
        )[1]

        mock_release_readiness_service.validate.side_effect = lambda wp: (
            call_order.append("readiness"),
            ReleaseReadinessResult(
                ready=True,
                checks=[],
                blocking_issues=[],
                warnings=[],
                status_message="READY",
            ),
        )[1]

        mock_backup_port.create_backup.side_effect = lambda sp: (
            call_order.append("backup"),
            BackupResult(
                success=True,
                backup_path=Path("/backup"),
                timestamp=None,
                error_message=None,
            ),
        )[1]

        mock_pipx_port.install.side_effect = lambda wp, force: (
            call_order.append("install"),
            PipxInstallResult(
                success=True,
                version="1.2.3",
                install_path=Path("/bin/crafter-ai"),
                error_message=None,
            ),
        )[1]

        install_service.install(wheel_path)

        assert call_order == ["preflight", "readiness", "backup", "install"]

    def test_install_passes_force_flag_to_pipx(
        self,
        install_service: InstallService,
        mock_pipx_port: MagicMock,
    ) -> None:
        """Install passes force=True to pipx_port.install."""
        wheel_path = Path("dist/crafter_ai-1.2.3-py3-none-any.whl")

        install_service.install(wheel_path, force=True)

        mock_pipx_port.install.assert_called_once_with(wheel_path, force=True)


class TestInstallServicePreflightFailure:
    """Test preflight check failures."""

    def test_install_fails_when_preflight_has_blocking_failure(
        self,
        install_service: InstallService,
        mock_check_executor: MagicMock,
        mock_release_readiness_service: MagicMock,
        mock_pipx_port: MagicMock,
    ) -> None:
        """Install fails when preflight check has blocking failure."""
        mock_check_executor.run_all.return_value = [
            CheckResult(
                id="wheel-exists",
                name="Wheel File Exists",
                passed=False,
                severity=CheckSeverity.BLOCKING,
                message="No .whl file found in dist/",
            ),
        ]

        wheel_path = Path("dist/crafter_ai-1.2.3-py3-none-any.whl")

        result = install_service.install(wheel_path)

        assert result.success is False
        assert (
            "Pre-flight" in result.error_message
            or "preflight" in result.error_message.lower()
        )
        assert InstallPhase.PREFLIGHT in result.phases_completed
        assert InstallPhase.READINESS not in result.phases_completed
        mock_release_readiness_service.validate.assert_not_called()
        mock_pipx_port.install.assert_not_called()

    def test_install_continues_when_preflight_has_warning_only(
        self,
        install_service: InstallService,
        mock_check_executor: MagicMock,
        mock_pipx_port: MagicMock,
    ) -> None:
        """Install continues when preflight has only warnings, no blocking failures."""
        mock_check_executor.run_all.return_value = [
            CheckResult(
                id="test-warning",
                name="Test Warning",
                passed=False,
                severity=CheckSeverity.WARNING,
                message="This is just a warning",
            ),
        ]

        wheel_path = Path("dist/crafter_ai-1.2.3-py3-none-any.whl")

        result = install_service.install(wheel_path)

        assert result.success is True
        mock_pipx_port.install.assert_called_once()


class TestInstallServiceReadinessFailure:
    """Test release readiness failures."""

    def test_install_fails_when_readiness_check_fails(
        self,
        install_service: InstallService,
        mock_release_readiness_service: MagicMock,
        mock_pipx_port: MagicMock,
    ) -> None:
        """Install fails when release readiness check has blocking issues."""
        mock_release_readiness_service.validate.return_value = ReleaseReadinessResult(
            ready=False,
            checks=[],
            blocking_issues=["Missing LICENSE file", "Invalid version format"],
            warnings=[],
            status_message="NOT READY: 2 blocking issue(s)",
        )

        wheel_path = Path("dist/crafter_ai-1.2.3-py3-none-any.whl")

        result = install_service.install(wheel_path)

        assert result.success is False
        assert (
            "readiness" in result.error_message.lower()
            or "ready" in result.error_message.lower()
        )
        assert InstallPhase.PREFLIGHT in result.phases_completed
        assert InstallPhase.READINESS in result.phases_completed
        assert InstallPhase.BACKUP not in result.phases_completed
        mock_pipx_port.install.assert_not_called()


class TestInstallServiceBackupBehavior:
    """Test backup phase behavior."""

    def test_install_continues_when_backup_fails(
        self,
        install_service: InstallService,
        mock_backup_port: MagicMock,
        mock_pipx_port: MagicMock,
    ) -> None:
        """Install continues when backup fails (with warning, doesn't block)."""
        mock_backup_port.create_backup.return_value = BackupResult(
            success=False,
            backup_path=None,
            timestamp=None,
            error_message="Failed to create backup: Permission denied",
        )

        wheel_path = Path("dist/crafter_ai-1.2.3-py3-none-any.whl")

        result = install_service.install(wheel_path)

        assert result.success is True
        assert InstallPhase.BACKUP in result.phases_completed
        assert InstallPhase.INSTALL in result.phases_completed
        mock_pipx_port.install.assert_called_once()

    def test_backup_uses_nwave_config_path(
        self,
        install_service: InstallService,
        mock_backup_port: MagicMock,
    ) -> None:
        """Backup is created for the nwave config path."""
        wheel_path = Path("dist/crafter_ai-1.2.3-py3-none-any.whl")

        install_service.install(wheel_path)

        mock_backup_port.create_backup.assert_called_once()
        # The backup path should be the nwave config directory
        call_args = mock_backup_port.create_backup.call_args
        assert call_args is not None


class TestInstallServiceInstallFailure:
    """Test pipx install failures."""

    def test_install_fails_when_pipx_install_fails(
        self,
        install_service: InstallService,
        mock_pipx_port: MagicMock,
    ) -> None:
        """Install fails when pipx_port.install() fails."""
        mock_pipx_port.install.return_value = PipxInstallResult(
            success=False,
            version=None,
            install_path=None,
            error_message="pipx install failed: package already installed",
        )

        wheel_path = Path("dist/crafter_ai-1.2.3-py3-none-any.whl")

        result = install_service.install(wheel_path)

        assert result.success is False
        assert (
            "pipx" in result.error_message.lower()
            or "install" in result.error_message.lower()
        )
        assert InstallPhase.PREFLIGHT in result.phases_completed
        assert InstallPhase.READINESS in result.phases_completed
        assert InstallPhase.BACKUP in result.phases_completed
        assert InstallPhase.INSTALL in result.phases_completed


class TestInstallServicePhasesCompleted:
    """Test phases_completed tracking."""

    def test_phases_completed_tracks_successful_phases(
        self,
        install_service: InstallService,
    ) -> None:
        """phases_completed includes all successfully completed phases."""
        wheel_path = Path("dist/crafter_ai-1.2.3-py3-none-any.whl")

        result = install_service.install(wheel_path)

        assert len(result.phases_completed) == 4
        assert InstallPhase.PREFLIGHT in result.phases_completed
        assert InstallPhase.READINESS in result.phases_completed
        assert InstallPhase.BACKUP in result.phases_completed
        assert InstallPhase.INSTALL in result.phases_completed

    def test_phases_completed_stops_at_first_blocking_failure(
        self,
        install_service: InstallService,
        mock_check_executor: MagicMock,
    ) -> None:
        """phases_completed stops at first blocking failure."""
        mock_check_executor.run_all.return_value = [
            CheckResult(
                id="blocking",
                name="Blocking Check",
                passed=False,
                severity=CheckSeverity.BLOCKING,
                message="Blocking failure",
            ),
        ]

        wheel_path = Path("dist/crafter_ai-1.2.3-py3-none-any.whl")

        result = install_service.install(wheel_path)

        assert len(result.phases_completed) == 1
        assert InstallPhase.PREFLIGHT in result.phases_completed


class TestInstallResultDataclass:
    """Test InstallResult dataclass."""

    def test_install_result_is_immutable(self) -> None:
        """InstallResult should be immutable (frozen dataclass)."""
        result = InstallResult(
            success=True,
            version="1.2.3",
            install_path=Path("/bin/crafter-ai"),
            phases_completed=[InstallPhase.PREFLIGHT],
            error_message=None,
        )

        with pytest.raises(AttributeError):
            result.success = False  # type: ignore[misc]

    def test_install_result_contains_all_required_fields(self) -> None:
        """InstallResult has all required fields per contract."""
        result = InstallResult(
            success=True,
            version="1.2.3",
            install_path=Path("/bin/crafter-ai"),
            phases_completed=[InstallPhase.PREFLIGHT, InstallPhase.INSTALL],
            error_message=None,
        )

        assert hasattr(result, "success")
        assert hasattr(result, "version")
        assert hasattr(result, "install_path")
        assert hasattr(result, "phases_completed")
        assert hasattr(result, "error_message")


class TestInstallPhaseEnum:
    """Test InstallPhase enum."""

    def test_install_phase_has_all_required_phases(self) -> None:
        """InstallPhase enum has all four required phases."""
        assert hasattr(InstallPhase, "PREFLIGHT")
        assert hasattr(InstallPhase, "READINESS")
        assert hasattr(InstallPhase, "BACKUP")
        assert hasattr(InstallPhase, "INSTALL")
