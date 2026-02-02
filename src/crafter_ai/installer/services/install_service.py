"""InstallService for orchestrating the complete install journey.

This module provides the InstallService application service that orchestrates:
- Pre-flight checks via CheckExecutor
- Release readiness validation via ReleaseReadinessService
- Backup creation via BackupPort
- Package installation via PipxPort
- Verification via HealthChecker (post-install health checks)

Used by: forge:install-local CLI command
"""

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

from crafter_ai.installer.domain.check_executor import CheckExecutor
from crafter_ai.installer.domain.check_result import CheckSeverity
from crafter_ai.installer.domain.health_checker import HealthChecker
from crafter_ai.installer.domain.health_result import HealthResult, HealthStatus
from crafter_ai.installer.ports.backup_port import BackupPort
from crafter_ai.installer.ports.pipx_port import PipxPort
from crafter_ai.installer.services.release_readiness_service import (
    ReleaseReadinessService,
)


class InstallPhase(Enum):
    """Phases of the install journey.

    PREFLIGHT: Run install-specific pre-flight checks.
    READINESS: Validate wheel is PyPI-ready.
    BACKUP: Create backup of existing installation.
    INSTALL: Install via pipx.
    VERIFICATION: Run post-install health checks.
    """

    PREFLIGHT = "preflight"
    READINESS = "readiness"
    BACKUP = "backup"
    INSTALL = "install"
    VERIFICATION = "verification"


@dataclass(frozen=True)
class VerificationResult:
    """Immutable result of the verification phase.

    Attributes:
        healthy: Whether the installation is usable (HEALTHY or DEGRADED).
        health_status: Overall health status (HEALTHY, DEGRADED, or UNHEALTHY).
        checks: List of health check results.
        warnings: List of warning messages from non-critical failures.
    """

    healthy: bool
    health_status: HealthStatus
    checks: list[HealthResult]
    warnings: list[str]


@dataclass(frozen=True)
class InstallResult:
    """Immutable result of the install journey.

    Attributes:
        success: Whether the install completed successfully.
        version: Version string of the installed package, None if failed.
        install_path: Path where the package was installed, None if failed.
        phases_completed: List of phases that were completed.
        error_message: Error message if install failed, None if successful.
        health_status: Health status after verification, None if not verified.
        verification_warnings: Warnings from verification, empty if not verified.
    """

    success: bool
    version: str | None
    install_path: Path | None
    phases_completed: list[InstallPhase]
    error_message: str | None
    health_status: HealthStatus | None = None
    verification_warnings: list[str] = field(default_factory=list)


# Default path for nwave configuration
NWAVE_CONFIG_PATH = Path.home() / ".claude"


class InstallService:
    """Application service orchestrating the complete install journey.

    This service coordinates:
    1. Preflight checks - verifying install prerequisites
    2. Readiness validation - ensuring wheel is PyPI-ready
    3. Backup creation - backing up existing installation (non-blocking)
    4. Installation - installing via pipx
    5. Verification - running post-install health checks (if health_checker provided)
    """

    def __init__(
        self,
        pipx_port: PipxPort,
        backup_port: BackupPort,
        check_executor: CheckExecutor,
        release_readiness_service: ReleaseReadinessService,
        nwave_config_path: Path | None = None,
        health_checker: HealthChecker | None = None,
    ) -> None:
        """Initialize InstallService with dependencies.

        Args:
            pipx_port: Port for pipx operations.
            backup_port: Port for backup operations.
            check_executor: Executor for running pre-flight checks.
            release_readiness_service: Service for validating release readiness.
            nwave_config_path: Optional path to nwave config (defaults to ~/.claude).
            health_checker: Optional health checker for verification phase.
        """
        self._pipx_port = pipx_port
        self._backup_port = backup_port
        self._check_executor = check_executor
        self._release_readiness_service = release_readiness_service
        self._nwave_config_path = nwave_config_path or NWAVE_CONFIG_PATH
        self._health_checker = health_checker

    def verify(self, install_path: Path) -> VerificationResult:
        """Run post-install health checks.

        Args:
            install_path: Path where the package was installed.

        Returns:
            VerificationResult with health status and check details.

        Raises:
            RuntimeError: If health_checker was not provided.
        """
        if self._health_checker is None:
            raise RuntimeError("Cannot verify: health_checker was not provided")

        checks = self._health_checker.check_all()
        warnings: list[str] = []

        # Determine overall health status
        has_unhealthy = any(c.status == HealthStatus.UNHEALTHY for c in checks)
        has_degraded = any(c.status == HealthStatus.DEGRADED for c in checks)

        if has_unhealthy:
            health_status = HealthStatus.UNHEALTHY
            healthy = False
        elif has_degraded:
            health_status = HealthStatus.DEGRADED
            healthy = True  # DEGRADED is still usable
            # Collect warnings from degraded checks
            warnings = [c.message for c in checks if c.status == HealthStatus.DEGRADED]
        else:
            health_status = HealthStatus.HEALTHY
            healthy = True

        return VerificationResult(
            healthy=healthy,
            health_status=health_status,
            checks=checks,
            warnings=warnings,
        )

    def install(self, wheel_path: Path, force: bool = False) -> InstallResult:
        """Execute the complete install journey.

        Orchestrates: preflight -> readiness -> backup -> install -> verification

        Args:
            wheel_path: Path to the wheel file to install.
            force: If True, force reinstall even if already installed.

        Returns:
            InstallResult with complete journey state.
        """
        phases_completed: list[InstallPhase] = []

        # Phase 1: Preflight checks
        preflight_results = self._check_executor.run_all()
        phases_completed.append(InstallPhase.PREFLIGHT)

        # Check for blocking failures in preflight
        blocking_failures = [
            r
            for r in preflight_results
            if not r.passed and r.severity == CheckSeverity.BLOCKING
        ]

        if blocking_failures:
            error_messages = [r.message for r in blocking_failures]
            return InstallResult(
                success=False,
                version=None,
                install_path=None,
                phases_completed=phases_completed,
                error_message=f"Pre-flight checks failed: {'; '.join(error_messages)}",
            )

        # Phase 2: Release readiness validation
        readiness_result = self._release_readiness_service.validate(wheel_path)
        phases_completed.append(InstallPhase.READINESS)

        if not readiness_result.ready:
            return InstallResult(
                success=False,
                version=None,
                install_path=None,
                phases_completed=phases_completed,
                error_message=f"Release readiness check failed: {'; '.join(readiness_result.blocking_issues)}",
            )

        # Phase 3: Backup (non-blocking - warn but continue on failure)
        backup_result = self._backup_port.create_backup(self._nwave_config_path)
        phases_completed.append(InstallPhase.BACKUP)

        # Log warning if backup failed, but don't block installation
        if not backup_result.success:
            # In a real implementation, we would log this warning
            # For now, we just continue
            pass

        # Phase 4: Install via pipx
        pipx_result = self._pipx_port.install(wheel_path, force=force)
        phases_completed.append(InstallPhase.INSTALL)

        if not pipx_result.success:
            return InstallResult(
                success=False,
                version=None,
                install_path=None,
                phases_completed=phases_completed,
                error_message=f"Pipx install failed: {pipx_result.error_message}",
            )

        # Phase 5: Verification (only if health_checker provided)
        if self._health_checker is not None and pipx_result.install_path is not None:
            verification_result = self.verify(pipx_result.install_path)
            phases_completed.append(InstallPhase.VERIFICATION)

            return InstallResult(
                success=True,
                version=pipx_result.version,
                install_path=pipx_result.install_path,
                phases_completed=phases_completed,
                error_message=None,
                health_status=verification_result.health_status,
                verification_warnings=verification_result.warnings,
            )

        # No verification (health_checker not provided)
        return InstallResult(
            success=True,
            version=pipx_result.version,
            install_path=pipx_result.install_path,
            phases_completed=phases_completed,
            error_message=None,
            health_status=None,
            verification_warnings=[],
        )
