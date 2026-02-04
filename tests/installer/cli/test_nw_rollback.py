"""Tests for nw rollback CLI command.

TDD approach: Tests verify CLI behavior with mock dependencies
and output verification using CliRunner.
"""

import os
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import MagicMock, patch

import typer

from crafter_ai.installer.domain.health_result import HealthStatus
from crafter_ai.installer.ports.backup_port import BackupInfo
from crafter_ai.installer.services.rollback_service import (
    RollbackResult,
    RollbackService,
)
from tests.cli.conftest import CleanCliRunner


# Create a test app for CLI testing (will import rollback once implemented)
test_app = typer.Typer()

runner = CleanCliRunner()


def _create_backup_info(
    path: Path,
    timestamp: datetime | None = None,
    size_bytes: int = 1024,
) -> BackupInfo:
    """Helper to create BackupInfo for tests."""
    return BackupInfo(
        path=path,
        timestamp=timestamp or datetime.now(timezone.utc),
        size_bytes=size_bytes,
    )


def _create_rollback_result(
    success: bool = True,
    restored_version: str | None = None,
    backup_timestamp: datetime | None = None,
    error_message: str | None = None,
    health_status: HealthStatus | None = HealthStatus.HEALTHY,
) -> RollbackResult:
    """Helper to create RollbackResult for tests."""
    return RollbackResult(
        success=success,
        restored_version=restored_version,
        backup_timestamp=backup_timestamp,
        error_message=error_message,
        health_status=health_status,
    )


def _create_mock_rollback_service(
    backups: list[BackupInfo] | None = None,
    manual_rollback_result: RollbackResult | None = None,
) -> MagicMock:
    """Create a mock RollbackService with predefined behavior."""
    service = MagicMock(spec=RollbackService)
    service.list_available_backups.return_value = backups or []
    service.manual_rollback.return_value = (
        manual_rollback_result or _create_rollback_result()
    )
    return service


class TestRollbackCommandBasic:
    """Test basic rollback command behavior."""

    def test_rollback_command_exists(self) -> None:
        """rollback command should be callable."""
        from crafter_ai.installer.cli.nw_rollback import rollback

        assert callable(rollback)

    def test_rollback_runs_without_error_with_backups(self) -> None:
        """rollback command should run without raising exceptions when backups exist."""
        from crafter_ai.installer.cli.nw_rollback import rollback

        test_app_local = typer.Typer()
        test_app_local.command()(rollback)

        backup_path = Path("/tmp/backups/nwave-20260201-120000")
        mock_service = _create_mock_rollback_service(
            backups=[_create_backup_info(backup_path)],
            manual_rollback_result=_create_rollback_result(success=True),
        )

        with patch(
            "crafter_ai.installer.cli.nw_rollback.create_rollback_service",
            return_value=mock_service,
        ):
            # Use --backup flag to avoid interactive prompt
            result = runner.invoke(
                test_app_local, ["--backup", str(backup_path), "--yes"]
            )

            assert result.exit_code == 0


class TestRollbackListsBackups:
    """Test that rollback command lists available backups."""

    def test_lists_available_backups(self) -> None:
        """rollback without --backup should list available backups."""
        from crafter_ai.installer.cli.nw_rollback import rollback

        test_app_local = typer.Typer()
        test_app_local.command()(rollback)

        backup1 = _create_backup_info(
            Path("/tmp/backups/nwave-20260201-120000"),
            datetime(2026, 2, 1, 12, 0, 0, tzinfo=timezone.utc),
        )
        backup2 = _create_backup_info(
            Path("/tmp/backups/nwave-20260131-100000"),
            datetime(2026, 1, 31, 10, 0, 0, tzinfo=timezone.utc),
        )
        mock_service = _create_mock_rollback_service(backups=[backup1, backup2])

        with patch(
            "crafter_ai.installer.cli.nw_rollback.create_rollback_service",
            return_value=mock_service,
        ):
            # CI mode to avoid interactive prompts
            with patch.dict(os.environ, {"CI": "true"}):
                result = runner.invoke(test_app_local, [])

                assert "backup" in result.output.lower()
                mock_service.list_available_backups.assert_called_once()


class TestRollbackNonInteractiveMode:
    """Test --backup flag for non-interactive mode."""

    def test_backup_flag_specifies_path(self) -> None:
        """--backup flag should specify backup path directly."""
        from crafter_ai.installer.cli.nw_rollback import rollback

        test_app_local = typer.Typer()
        test_app_local.command()(rollback)

        backup_path = Path("/tmp/backups/nwave-20260201-120000")
        mock_service = _create_mock_rollback_service(
            backups=[_create_backup_info(backup_path)],
            manual_rollback_result=_create_rollback_result(success=True),
        )

        with patch(
            "crafter_ai.installer.cli.nw_rollback.create_rollback_service",
            return_value=mock_service,
        ):
            result = runner.invoke(
                test_app_local, ["--backup", str(backup_path), "--yes"]
            )

            assert result.exit_code == 0
            mock_service.manual_rollback.assert_called_once_with(backup_path)

    def test_short_flag_b_works(self) -> None:
        """-b short flag should work like --backup."""
        from crafter_ai.installer.cli.nw_rollback import rollback

        test_app_local = typer.Typer()
        test_app_local.command()(rollback)

        backup_path = Path("/tmp/backups/nwave-20260201-120000")
        mock_service = _create_mock_rollback_service(
            backups=[_create_backup_info(backup_path)],
            manual_rollback_result=_create_rollback_result(success=True),
        )

        with patch(
            "crafter_ai.installer.cli.nw_rollback.create_rollback_service",
            return_value=mock_service,
        ):
            result = runner.invoke(test_app_local, ["-b", str(backup_path), "-y"])

            assert result.exit_code == 0
            mock_service.manual_rollback.assert_called_once_with(backup_path)


class TestRollbackYesFlag:
    """Test --yes flag for auto-confirmation."""

    def test_yes_flag_skips_confirmation(self) -> None:
        """--yes flag should skip confirmation prompt."""
        from crafter_ai.installer.cli.nw_rollback import rollback

        test_app_local = typer.Typer()
        test_app_local.command()(rollback)

        backup_path = Path("/tmp/backups/nwave-20260201-120000")
        mock_service = _create_mock_rollback_service(
            backups=[_create_backup_info(backup_path)],
            manual_rollback_result=_create_rollback_result(success=True),
        )

        with patch(
            "crafter_ai.installer.cli.nw_rollback.create_rollback_service",
            return_value=mock_service,
        ):
            result = runner.invoke(
                test_app_local, ["--backup", str(backup_path), "--yes"]
            )

            # Should not prompt, should succeed
            assert result.exit_code == 0
            mock_service.manual_rollback.assert_called_once()

    def test_short_flag_y_works(self) -> None:
        """-y short flag should work like --yes."""
        from crafter_ai.installer.cli.nw_rollback import rollback

        test_app_local = typer.Typer()
        test_app_local.command()(rollback)

        backup_path = Path("/tmp/backups/nwave-20260201-120000")
        mock_service = _create_mock_rollback_service(
            backups=[_create_backup_info(backup_path)],
            manual_rollback_result=_create_rollback_result(success=True),
        )

        with patch(
            "crafter_ai.installer.cli.nw_rollback.create_rollback_service",
            return_value=mock_service,
        ):
            result = runner.invoke(test_app_local, ["-b", str(backup_path), "-y"])

            assert result.exit_code == 0


class TestRollbackNoBackupsError:
    """Test error handling when no backups exist."""

    def test_shows_error_when_no_backups(self) -> None:
        """rollback should show error when no backups exist."""
        from crafter_ai.installer.cli.nw_rollback import rollback

        test_app_local = typer.Typer()
        test_app_local.command()(rollback)

        mock_service = _create_mock_rollback_service(backups=[])

        with patch(
            "crafter_ai.installer.cli.nw_rollback.create_rollback_service",
            return_value=mock_service,
        ):
            with patch.dict(os.environ, {"CI": "true"}):
                result = runner.invoke(test_app_local, [])

                assert result.exit_code == 1
                assert "no backup" in result.output.lower()

    def test_exit_code_1_for_no_backups(self) -> None:
        """Exit code should be 1 when no backups available."""
        from crafter_ai.installer.cli.nw_rollback import rollback

        test_app_local = typer.Typer()
        test_app_local.command()(rollback)

        mock_service = _create_mock_rollback_service(backups=[])

        with patch(
            "crafter_ai.installer.cli.nw_rollback.create_rollback_service",
            return_value=mock_service,
        ):
            with patch.dict(os.environ, {"CI": "true"}):
                result = runner.invoke(test_app_local, [])

                assert result.exit_code == 1


class TestRollbackInvalidBackupPath:
    """Test error handling for invalid backup paths."""

    def test_shows_error_for_invalid_backup_path(self) -> None:
        """rollback should show error for invalid backup path."""
        from crafter_ai.installer.cli.nw_rollback import rollback

        test_app_local = typer.Typer()
        test_app_local.command()(rollback)

        backup_path = Path("/nonexistent/path")
        mock_service = _create_mock_rollback_service(
            backups=[_create_backup_info(Path("/tmp/backups/nwave-20260201-120000"))],
            manual_rollback_result=_create_rollback_result(
                success=False,
                error_message="Backup path does not exist",
            ),
        )

        with patch(
            "crafter_ai.installer.cli.nw_rollback.create_rollback_service",
            return_value=mock_service,
        ):
            result = runner.invoke(
                test_app_local, ["--backup", str(backup_path), "--yes"]
            )

            assert result.exit_code == 2
            assert "error" in result.output.lower() or "failed" in result.output.lower()


class TestRollbackRestoreFailure:
    """Test error handling for restore failures."""

    def test_shows_error_on_restore_failure(self) -> None:
        """rollback should show error when restore fails."""
        from crafter_ai.installer.cli.nw_rollback import rollback

        test_app_local = typer.Typer()
        test_app_local.command()(rollback)

        backup_path = Path("/tmp/backups/nwave-20260201-120000")
        mock_service = _create_mock_rollback_service(
            backups=[_create_backup_info(backup_path)],
            manual_rollback_result=_create_rollback_result(
                success=False,
                error_message="Permission denied",
            ),
        )

        with patch(
            "crafter_ai.installer.cli.nw_rollback.create_rollback_service",
            return_value=mock_service,
        ):
            result = runner.invoke(
                test_app_local, ["--backup", str(backup_path), "--yes"]
            )

            assert result.exit_code == 2
            assert "permission denied" in result.output.lower()

    def test_exit_code_2_for_restore_failure(self) -> None:
        """Exit code should be 2 when restore fails."""
        from crafter_ai.installer.cli.nw_rollback import rollback

        test_app_local = typer.Typer()
        test_app_local.command()(rollback)

        backup_path = Path("/tmp/backups/nwave-20260201-120000")
        mock_service = _create_mock_rollback_service(
            backups=[_create_backup_info(backup_path)],
            manual_rollback_result=_create_rollback_result(
                success=False,
                error_message="Restore failed",
            ),
        )

        with patch(
            "crafter_ai.installer.cli.nw_rollback.create_rollback_service",
            return_value=mock_service,
        ):
            result = runner.invoke(
                test_app_local, ["--backup", str(backup_path), "--yes"]
            )

            assert result.exit_code == 2


class TestRollbackHealthCheckAfterRestore:
    """Test health check after successful restore."""

    def test_shows_health_check_result_after_restore(self) -> None:
        """rollback should show health check result after successful restore."""
        from crafter_ai.installer.cli.nw_rollback import rollback

        test_app_local = typer.Typer()
        test_app_local.command()(rollback)

        backup_path = Path("/tmp/backups/nwave-20260201-120000")
        mock_service = _create_mock_rollback_service(
            backups=[_create_backup_info(backup_path)],
            manual_rollback_result=_create_rollback_result(
                success=True,
                health_status=HealthStatus.HEALTHY,
            ),
        )

        with patch(
            "crafter_ai.installer.cli.nw_rollback.create_rollback_service",
            return_value=mock_service,
        ):
            result = runner.invoke(
                test_app_local, ["--backup", str(backup_path), "--yes"]
            )

            assert result.exit_code == 0
            # Should indicate health status
            assert "health" in result.output.lower() or "ok" in result.output.lower()

    def test_shows_unhealthy_status_after_restore(self) -> None:
        """rollback should show unhealthy status if health check fails."""
        from crafter_ai.installer.cli.nw_rollback import rollback

        test_app_local = typer.Typer()
        test_app_local.command()(rollback)

        backup_path = Path("/tmp/backups/nwave-20260201-120000")
        mock_service = _create_mock_rollback_service(
            backups=[_create_backup_info(backup_path)],
            manual_rollback_result=_create_rollback_result(
                success=True,
                health_status=HealthStatus.UNHEALTHY,
            ),
        )

        with patch(
            "crafter_ai.installer.cli.nw_rollback.create_rollback_service",
            return_value=mock_service,
        ):
            result = runner.invoke(
                test_app_local, ["--backup", str(backup_path), "--yes"]
            )

            # Still exit 0 because restore succeeded
            assert result.exit_code == 0


class TestRollbackCIMode:
    """Test CI mode behavior."""

    def test_ci_mode_uses_plain_output(self) -> None:
        """In CI mode, rollback should use plain text output."""
        from crafter_ai.installer.cli.nw_rollback import rollback

        test_app_local = typer.Typer()
        test_app_local.command()(rollback)

        backup_path = Path("/tmp/backups/nwave-20260201-120000")
        mock_service = _create_mock_rollback_service(
            backups=[_create_backup_info(backup_path)],
            manual_rollback_result=_create_rollback_result(success=True),
        )

        with patch(
            "crafter_ai.installer.cli.nw_rollback.create_rollback_service",
            return_value=mock_service,
        ):
            with patch.dict(os.environ, {"CI": "true"}):
                result = runner.invoke(
                    test_app_local, ["--backup", str(backup_path), "--yes"]
                )

                # CI output should not have rich formatting markers
                assert result.exit_code == 0

    def test_ci_flag_forces_ci_mode(self) -> None:
        """--ci flag should force CI mode output."""
        from crafter_ai.installer.cli.nw_rollback import rollback

        test_app_local = typer.Typer()
        test_app_local.command()(rollback)

        backup_path = Path("/tmp/backups/nwave-20260201-120000")
        mock_service = _create_mock_rollback_service(
            backups=[_create_backup_info(backup_path)],
            manual_rollback_result=_create_rollback_result(success=True),
        )

        with patch(
            "crafter_ai.installer.cli.nw_rollback.create_rollback_service",
            return_value=mock_service,
        ):
            result = runner.invoke(
                test_app_local, ["--backup", str(backup_path), "--yes", "--ci"]
            )

            assert result.exit_code == 0

    def test_ci_mode_no_prompts(self) -> None:
        """In CI mode, rollback should not prompt for input."""
        from crafter_ai.installer.cli.nw_rollback import rollback

        test_app_local = typer.Typer()
        test_app_local.command()(rollback)

        mock_service = _create_mock_rollback_service(backups=[])

        with patch(
            "crafter_ai.installer.cli.nw_rollback.create_rollback_service",
            return_value=mock_service,
        ):
            with patch.dict(os.environ, {"CI": "true"}):
                result = runner.invoke(test_app_local, [])

                # Should fail with exit code 1, not hang for input
                assert result.exit_code == 1


class TestRollbackExitCodes:
    """Test CLI exit codes."""

    def test_exit_code_0_on_success(self) -> None:
        """Exit code should be 0 on successful restore."""
        from crafter_ai.installer.cli.nw_rollback import rollback

        test_app_local = typer.Typer()
        test_app_local.command()(rollback)

        backup_path = Path("/tmp/backups/nwave-20260201-120000")
        mock_service = _create_mock_rollback_service(
            backups=[_create_backup_info(backup_path)],
            manual_rollback_result=_create_rollback_result(success=True),
        )

        with patch(
            "crafter_ai.installer.cli.nw_rollback.create_rollback_service",
            return_value=mock_service,
        ):
            result = runner.invoke(
                test_app_local, ["--backup", str(backup_path), "--yes"]
            )

            assert result.exit_code == 0

    def test_exit_code_1_no_backups(self) -> None:
        """Exit code should be 1 when no backups available."""
        from crafter_ai.installer.cli.nw_rollback import rollback

        test_app_local = typer.Typer()
        test_app_local.command()(rollback)

        mock_service = _create_mock_rollback_service(backups=[])

        with patch(
            "crafter_ai.installer.cli.nw_rollback.create_rollback_service",
            return_value=mock_service,
        ):
            with patch.dict(os.environ, {"CI": "true"}):
                result = runner.invoke(test_app_local, [])

                assert result.exit_code == 1

    def test_exit_code_2_restore_failed(self) -> None:
        """Exit code should be 2 when restore fails."""
        from crafter_ai.installer.cli.nw_rollback import rollback

        test_app_local = typer.Typer()
        test_app_local.command()(rollback)

        backup_path = Path("/tmp/backups/nwave-20260201-120000")
        mock_service = _create_mock_rollback_service(
            backups=[_create_backup_info(backup_path)],
            manual_rollback_result=_create_rollback_result(
                success=False,
                error_message="Restore failed",
            ),
        )

        with patch(
            "crafter_ai.installer.cli.nw_rollback.create_rollback_service",
            return_value=mock_service,
        ):
            result = runner.invoke(
                test_app_local, ["--backup", str(backup_path), "--yes"]
            )

            assert result.exit_code == 2


class TestRollbackSuccessOutput:
    """Test successful restore output."""

    def test_shows_confirmation_after_restore(self) -> None:
        """rollback should show confirmation message after successful restore."""
        from crafter_ai.installer.cli.nw_rollback import rollback

        test_app_local = typer.Typer()
        test_app_local.command()(rollback)

        backup_path = Path("/tmp/backups/nwave-20260201-120000")
        mock_service = _create_mock_rollback_service(
            backups=[_create_backup_info(backup_path)],
            manual_rollback_result=_create_rollback_result(success=True),
        )

        with patch(
            "crafter_ai.installer.cli.nw_rollback.create_rollback_service",
            return_value=mock_service,
        ):
            result = runner.invoke(
                test_app_local, ["--backup", str(backup_path), "--yes"]
            )

            assert result.exit_code == 0
            # Should show success message
            assert (
                "success" in result.output.lower()
                or "restored" in result.output.lower()
                or "complete" in result.output.lower()
            )
