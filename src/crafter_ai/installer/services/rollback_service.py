"""RollbackService for automatic and manual rollback operations.

This service orchestrates rollback functionality:
1. Automatic rollback when installation fails
2. Manual rollback to a specific backup
3. Listing available backups

Follows hexagonal architecture - depends on BackupPort interface,
not concrete implementations.
"""

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from crafter_ai.installer.domain.health_checker import HealthChecker
from crafter_ai.installer.domain.health_result import HealthStatus
from crafter_ai.installer.ports.backup_port import BackupInfo, BackupPort


@dataclass
class RollbackResult:
    """Result of a rollback operation.

    Attributes:
        success: True if rollback succeeded, False otherwise.
        restored_version: Version string of restored backup, or None if failed.
        backup_timestamp: Timestamp of the restored backup, or None if failed.
        error_message: Error description if rollback failed, None otherwise.
        health_status: Health status after restore, or None if not checked.
    """

    success: bool
    restored_version: str | None
    backup_timestamp: datetime | None
    error_message: str | None
    health_status: HealthStatus | None


class RollbackService:
    """Service for handling automatic and manual rollback operations.

    This service uses BackupPort for restore operations and HealthChecker
    for post-restore validation. It follows the dependency injection pattern
    for testability.

    Used by:
        - InstallService for automatic rollback on failure
        - CLI command (nw rollback) for manual rollback
    """

    def __init__(
        self,
        backup_port: BackupPort,
        health_checker: HealthChecker,
        nwave_path: Path | None = None,
    ) -> None:
        """Initialize the RollbackService.

        Args:
            backup_port: Port for backup/restore operations.
            health_checker: Checker for post-restore health validation.
            nwave_path: Path to nWave installation. Defaults to ~/.claude/
        """
        self._backup_port = backup_port
        self._health_checker = health_checker
        self._nwave_path = nwave_path or Path.home() / ".claude"

    def auto_rollback(self, error: Exception) -> RollbackResult:
        """Perform automatic rollback on installation failure.

        This method is called when an installation fails. It finds the most
        recent backup and restores from it.

        Args:
            error: The exception that caused the installation to fail.

        Returns:
            RollbackResult with success/failure information.
        """
        backups = self._backup_port.list_backups()

        if not backups:
            return RollbackResult(
                success=False,
                restored_version=None,
                backup_timestamp=None,
                error_message="No backups available. Cannot rollback.",
                health_status=None,
            )

        most_recent = backups[0]

        restore_result = self._backup_port.restore_backup(
            most_recent.path,
            self._nwave_path,
        )

        if not restore_result.success:
            return RollbackResult(
                success=False,
                restored_version=None,
                backup_timestamp=None,
                error_message=f"Restore failed: {restore_result.error_message}",
                health_status=None,
            )

        return RollbackResult(
            success=True,
            restored_version=None,
            backup_timestamp=most_recent.timestamp,
            error_message=None,
            health_status=None,
        )

    def manual_rollback(self, backup_path: Path) -> RollbackResult:
        """Perform manual rollback to a specific backup.

        This method is called by the CLI rollback command. It restores
        the specified backup and runs health checks afterward.

        Args:
            backup_path: Path to the backup directory to restore from.

        Returns:
            RollbackResult with success/failure information and health status.
        """
        restore_result = self._backup_port.restore_backup(
            backup_path,
            self._nwave_path,
        )

        if not restore_result.success:
            return RollbackResult(
                success=False,
                restored_version=None,
                backup_timestamp=None,
                error_message=f"Restore failed: {restore_result.error_message}",
                health_status=None,
            )

        is_healthy = self._health_checker.is_healthy()
        health_status = HealthStatus.HEALTHY if is_healthy else HealthStatus.UNHEALTHY

        return RollbackResult(
            success=True,
            restored_version=None,
            backup_timestamp=None,
            error_message=None,
            health_status=health_status,
        )

    def list_available_backups(self) -> list[BackupInfo]:
        """List all available backups.

        Returns backups sorted by timestamp (newest first), as provided
        by the BackupPort.

        Returns:
            List of BackupInfo objects, or empty list if none exist.
        """
        return self._backup_port.list_backups()
