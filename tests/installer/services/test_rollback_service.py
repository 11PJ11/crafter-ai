"""Tests for RollbackService - automatic and manual rollback operations.

This module tests the RollbackService that handles:
1. Automatic rollback on installation failure
2. Manual rollback to a specific backup
3. Listing available backups
"""

from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import MagicMock, create_autospec

import pytest

from crafter_ai.installer.domain.health_checker import HealthChecker
from crafter_ai.installer.domain.health_result import HealthResult, HealthStatus
from crafter_ai.installer.ports.backup_port import (
    BackupInfo,
    BackupPort,
    RestoreResult,
)
from crafter_ai.installer.services.rollback_service import (
    RollbackService,
)


@pytest.fixture
def mock_backup_port() -> MagicMock:
    """Create a mock BackupPort."""
    return create_autospec(BackupPort, instance=True)


@pytest.fixture
def mock_health_checker() -> MagicMock:
    """Create a mock HealthChecker."""
    mock = create_autospec(HealthChecker, instance=True)
    mock.is_healthy.return_value = True
    mock.check_all.return_value = [
        HealthResult(
            component="nwave",
            status=HealthStatus.HEALTHY,
            message="nWave operational",
            details=None,
            timestamp=datetime.now(timezone.utc),
        )
    ]
    return mock


@pytest.fixture
def rollback_service(
    mock_backup_port: MagicMock,
    mock_health_checker: MagicMock,
) -> RollbackService:
    """Create a RollbackService with mocked dependencies."""
    return RollbackService(
        backup_port=mock_backup_port,
        health_checker=mock_health_checker,
        nwave_path=Path("/home/user/.claude"),
    )


@pytest.fixture
def sample_backups() -> list[BackupInfo]:
    """Create sample backup info list."""
    return [
        BackupInfo(
            path=Path("/home/user/.claude/backups/nwave-20260202-150000"),
            timestamp=datetime(2026, 2, 2, 15, 0, 0, tzinfo=timezone.utc),
            size_bytes=1024000,
        ),
        BackupInfo(
            path=Path("/home/user/.claude/backups/nwave-20260201-120000"),
            timestamp=datetime(2026, 2, 1, 12, 0, 0, tzinfo=timezone.utc),
            size_bytes=1000000,
        ),
        BackupInfo(
            path=Path("/home/user/.claude/backups/nwave-20260131-090000"),
            timestamp=datetime(2026, 1, 31, 9, 0, 0, tzinfo=timezone.utc),
            size_bytes=980000,
        ),
    ]


class TestAutoRollback:
    """Tests for auto_rollback method."""

    def test_auto_rollback_restores_from_most_recent_backup(
        self,
        rollback_service: RollbackService,
        mock_backup_port: MagicMock,
        sample_backups: list[BackupInfo],
    ) -> None:
        """Auto rollback should use the most recent backup (first in sorted list)."""
        mock_backup_port.list_backups.return_value = sample_backups
        mock_backup_port.restore_backup.return_value = RestoreResult(
            success=True,
            restored_path=Path("/home/user/.claude"),
            error_message=None,
        )

        error = Exception("Installation failed during file copy")
        result = rollback_service.auto_rollback(error)

        assert result.success is True
        mock_backup_port.restore_backup.assert_called_once()
        call_args = mock_backup_port.restore_backup.call_args
        assert call_args[0][0] == sample_backups[0].path

    def test_auto_rollback_returns_success_with_restored_version(
        self,
        rollback_service: RollbackService,
        mock_backup_port: MagicMock,
        sample_backups: list[BackupInfo],
    ) -> None:
        """Auto rollback should return success result with backup timestamp."""
        mock_backup_port.list_backups.return_value = sample_backups
        mock_backup_port.restore_backup.return_value = RestoreResult(
            success=True,
            restored_path=Path("/home/user/.claude"),
            error_message=None,
        )

        error = Exception("Installation failed")
        result = rollback_service.auto_rollback(error)

        assert result.success is True
        assert result.backup_timestamp == sample_backups[0].timestamp
        assert result.error_message is None

    def test_auto_rollback_returns_error_when_no_backups_exist(
        self,
        rollback_service: RollbackService,
        mock_backup_port: MagicMock,
    ) -> None:
        """Auto rollback should fail gracefully when no backups are available."""
        mock_backup_port.list_backups.return_value = []

        error = Exception("Installation failed")
        result = rollback_service.auto_rollback(error)

        assert result.success is False
        assert "No backups available" in result.error_message
        mock_backup_port.restore_backup.assert_not_called()

    def test_auto_rollback_returns_error_when_restore_fails(
        self,
        rollback_service: RollbackService,
        mock_backup_port: MagicMock,
        sample_backups: list[BackupInfo],
    ) -> None:
        """Auto rollback should handle restore failure gracefully."""
        mock_backup_port.list_backups.return_value = sample_backups
        mock_backup_port.restore_backup.return_value = RestoreResult(
            success=False,
            restored_path=None,
            error_message="Permission denied",
        )

        error = Exception("Installation failed")
        result = rollback_service.auto_rollback(error)

        assert result.success is False
        assert "Permission denied" in result.error_message

    def test_auto_rollback_cleans_partial_files_before_restore(
        self,
        mock_backup_port: MagicMock,
        mock_health_checker: MagicMock,
        sample_backups: list[BackupInfo],
        tmp_path: Path,
    ) -> None:
        """Auto rollback should clean partial install files before restoring.

        This ensures corrupt partial state is removed before restoring a good backup.
        """
        nwave_path = tmp_path / ".claude"
        nwave_path.mkdir(parents=True)

        partial_marker = nwave_path / ".install_in_progress"
        partial_marker.touch()

        partial_dir = nwave_path / ".partial"
        partial_dir.mkdir()
        (partial_dir / "corrupt_file.txt").write_text("partial data")

        rollback_service = RollbackService(
            backup_port=mock_backup_port,
            health_checker=mock_health_checker,
            nwave_path=nwave_path,
        )

        mock_backup_port.list_backups.return_value = sample_backups
        mock_backup_port.restore_backup.return_value = RestoreResult(
            success=True,
            restored_path=nwave_path,
            error_message=None,
        )

        error = Exception("Installation failed during file copy")
        result = rollback_service.auto_rollback(error)

        assert result.success is True
        assert not partial_marker.exists(), "Partial marker should be cleaned"
        assert not partial_dir.exists(), "Partial directory should be cleaned"

        mock_backup_port.restore_backup.assert_called_once()


class TestManualRollback:
    """Tests for manual_rollback method."""

    def test_manual_rollback_restores_specified_backup(
        self,
        rollback_service: RollbackService,
        mock_backup_port: MagicMock,
    ) -> None:
        """Manual rollback should restore the exact backup path specified."""
        backup_path = Path("/home/user/.claude/backups/nwave-20260201-120000")
        mock_backup_port.restore_backup.return_value = RestoreResult(
            success=True,
            restored_path=Path("/home/user/.claude"),
            error_message=None,
        )

        result = rollback_service.manual_rollback(backup_path)

        assert result.success is True
        mock_backup_port.restore_backup.assert_called_once()
        call_args = mock_backup_port.restore_backup.call_args
        assert call_args[0][0] == backup_path

    def test_manual_rollback_runs_health_check_after_restore(
        self,
        rollback_service: RollbackService,
        mock_backup_port: MagicMock,
        mock_health_checker: MagicMock,
    ) -> None:
        """Manual rollback should run health checks after successful restore."""
        backup_path = Path("/home/user/.claude/backups/nwave-20260201-120000")
        mock_backup_port.restore_backup.return_value = RestoreResult(
            success=True,
            restored_path=Path("/home/user/.claude"),
            error_message=None,
        )

        result = rollback_service.manual_rollback(backup_path)

        assert result.success is True
        mock_health_checker.is_healthy.assert_called()
        assert result.health_status is not None

    def test_manual_rollback_reports_unhealthy_status(
        self,
        rollback_service: RollbackService,
        mock_backup_port: MagicMock,
        mock_health_checker: MagicMock,
    ) -> None:
        """Manual rollback should report unhealthy status after restore."""
        backup_path = Path("/home/user/.claude/backups/nwave-20260201-120000")
        mock_backup_port.restore_backup.return_value = RestoreResult(
            success=True,
            restored_path=Path("/home/user/.claude"),
            error_message=None,
        )
        mock_health_checker.is_healthy.return_value = False

        result = rollback_service.manual_rollback(backup_path)

        assert result.success is True
        assert result.health_status == HealthStatus.UNHEALTHY

    def test_manual_rollback_returns_error_when_restore_fails(
        self,
        rollback_service: RollbackService,
        mock_backup_port: MagicMock,
    ) -> None:
        """Manual rollback should handle restore failure gracefully."""
        backup_path = Path("/home/user/.claude/backups/nwave-20260201-120000")
        mock_backup_port.restore_backup.return_value = RestoreResult(
            success=False,
            restored_path=None,
            error_message="Backup not found",
        )

        result = rollback_service.manual_rollback(backup_path)

        assert result.success is False
        assert "Backup not found" in result.error_message


class TestListAvailableBackups:
    """Tests for list_available_backups method."""

    def test_list_available_backups_returns_sorted_list(
        self,
        rollback_service: RollbackService,
        mock_backup_port: MagicMock,
        sample_backups: list[BackupInfo],
    ) -> None:
        """List backups should return backups sorted by timestamp (newest first)."""
        mock_backup_port.list_backups.return_value = sample_backups

        result = rollback_service.list_available_backups()

        assert len(result) == 3
        assert result[0].timestamp > result[1].timestamp
        assert result[1].timestamp > result[2].timestamp
        mock_backup_port.list_backups.assert_called_once()

    def test_list_available_backups_returns_empty_list_when_none_exist(
        self,
        rollback_service: RollbackService,
        mock_backup_port: MagicMock,
    ) -> None:
        """List backups should return empty list when no backups exist."""
        mock_backup_port.list_backups.return_value = []

        result = rollback_service.list_available_backups()

        assert result == []
        mock_backup_port.list_backups.assert_called_once()
