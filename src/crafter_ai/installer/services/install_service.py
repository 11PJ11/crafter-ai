"""InstallService for orchestrating the complete install journey.

This module provides the InstallService application service that orchestrates:
- Pre-flight checks via CheckExecutor
- Release readiness validation via ReleaseReadinessService
- Upgrade path detection (FRESH_INSTALL, UPGRADE, REINSTALL, DOWNGRADE)
- Backup creation via BackupPort
- Package installation via PipxPort
- Verification via HealthChecker (post-install health checks)

Used by: forge:install-local CLI command
"""

import re
from collections.abc import Callable
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

from packaging.version import InvalidVersion, Version

# Type alias for progress callback: (phase: InstallPhase, message: str) -> None
ProgressCallback = Callable[["InstallPhase", str], None]

from crafter_ai.installer.domain.asset_deployment_result import AssetDeploymentResult
from crafter_ai.installer.domain.check_executor import CheckExecutor
from crafter_ai.installer.domain.check_result import CheckSeverity
from crafter_ai.installer.domain.deployment_validation_result import (
    DeploymentValidationResult,
)
from crafter_ai.installer.domain.health_checker import HealthChecker
from crafter_ai.installer.domain.health_result import HealthResult, HealthStatus
from crafter_ai.installer.domain.ide_bundle_constants import (
    DEFAULT_OUTPUT_DIR,
    EXPECTED_AGENT_COUNT,
    EXPECTED_COMMAND_COUNT,
    EXPECTED_SCRIPT_COUNT,
    EXPECTED_TEMPLATE_COUNT,
)
from crafter_ai.installer.ports.backup_port import BackupPort
from crafter_ai.installer.ports.pipx_port import PipxPort
from crafter_ai.installer.services.asset_deployment_service import (
    AssetDeploymentService,
)
from crafter_ai.installer.services.deployment_validation_service import (
    DeploymentValidationService,
)
from crafter_ai.installer.services.release_readiness_service import (
    ReleaseReadinessService,
)


class UpgradePath(Enum):
    """Upgrade path classification for install scenarios.

    FRESH_INSTALL: No existing version installed.
    UPGRADE: Target version > installed version.
    REINSTALL: Target version == installed version.
    DOWNGRADE: Target version < installed version.
    """

    FRESH_INSTALL = "fresh_install"
    UPGRADE = "upgrade"
    REINSTALL = "reinstall"
    DOWNGRADE = "downgrade"


class InstallPhase(Enum):
    """Phases of the install journey.

    PREFLIGHT: Run install-specific pre-flight checks.
    READINESS: Validate wheel is PyPI-ready.
    BACKUP: Create backup of existing installation.
    INSTALL: Install via pipx.
    ASSET_DEPLOYMENT: Deploy IDE bundle assets to ~/.claude/.
    DEPLOYMENT_VALIDATION: Validate deployed assets match expected counts.
    VERIFICATION: Run post-install health checks.
    """

    PREFLIGHT = "preflight"
    READINESS = "readiness"
    BACKUP = "backup"
    INSTALL = "install"
    ASSET_DEPLOYMENT = "asset_deployment"
    DEPLOYMENT_VALIDATION = "deployment_validation"
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
        asset_deployment_result: Result of asset deployment, None if skipped.
        deployment_validation_result: Result of deployment validation, None if skipped.
    """

    success: bool
    version: str | None
    install_path: Path | None
    phases_completed: list[InstallPhase]
    error_message: str | None
    health_status: HealthStatus | None = None
    verification_warnings: list[str] = field(default_factory=list)
    asset_deployment_result: AssetDeploymentResult | None = None
    deployment_validation_result: DeploymentValidationResult | None = None


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
        asset_deployment_service: AssetDeploymentService | None = None,
        deployment_validation_service: DeploymentValidationService | None = None,
    ) -> None:
        """Initialize InstallService with dependencies.

        Args:
            pipx_port: Port for pipx operations.
            backup_port: Port for backup operations.
            check_executor: Executor for running pre-flight checks.
            release_readiness_service: Service for validating release readiness.
            nwave_config_path: Optional path to nwave config (defaults to ~/.claude).
            health_checker: Optional health checker for verification phase.
            asset_deployment_service: Optional service for deploying IDE bundle assets.
            deployment_validation_service: Optional service for validating deployment.
        """
        self._pipx_port = pipx_port
        self._backup_port = backup_port
        self._check_executor = check_executor
        self._release_readiness_service = release_readiness_service
        self._nwave_config_path = nwave_config_path or NWAVE_CONFIG_PATH
        self._health_checker = health_checker
        self._asset_deployment_service = asset_deployment_service
        self._deployment_validation_service = deployment_validation_service

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

    def _get_installed_version(self) -> str | None:
        """Query pipx for the currently installed crafter-ai version.

        Returns:
            Version string if installed, None if not installed.
        """
        packages = self._pipx_port.list_packages()
        for pkg in packages:
            if pkg.name == "crafter-ai":
                return pkg.version
        return None

    def _extract_version_from_wheel(self, wheel_path: Path) -> str | None:
        """Extract version from wheel filename.

        Args:
            wheel_path: Path to wheel file.

        Returns:
            Version string extracted from filename, or None if extraction fails.
        """
        # Wheel filename format: {distribution}-{version}(-{build tag})?-{python}-{abi}-{platform}.whl
        # Example: crafter_ai-1.3.0-py3-none-any.whl
        filename = wheel_path.name
        match = re.match(r"[^-]+-([^-]+)-", filename)
        if match:
            return match.group(1)
        return None

    def _compare_versions(
        self, installed: str | None, target: str | None
    ) -> UpgradePath:
        """Compare installed and target versions.

        Args:
            installed: Currently installed version, or None.
            target: Target version to install, or None.

        Returns:
            UpgradePath classification.
        """
        if installed is None:
            return UpgradePath.FRESH_INSTALL

        if target is None:
            return UpgradePath.FRESH_INSTALL

        try:
            installed_ver = Version(installed)
            target_ver = Version(target)

            if target_ver > installed_ver:
                return UpgradePath.UPGRADE
            elif target_ver < installed_ver:
                return UpgradePath.DOWNGRADE
            else:
                return UpgradePath.REINSTALL
        except InvalidVersion:
            # If version parsing fails, treat as fresh install
            return UpgradePath.FRESH_INSTALL

    def detect_upgrade_path(self, target_version: str) -> UpgradePath:
        """Detect the upgrade path based on installed vs target version.

        Args:
            target_version: Version to be installed.

        Returns:
            UpgradePath classification (FRESH_INSTALL, UPGRADE, REINSTALL, DOWNGRADE).
        """
        installed_version = self._get_installed_version()
        return self._compare_versions(installed_version, target_version)

    def should_create_backup(self, upgrade_path: UpgradePath) -> bool:
        """Determine if a backup should be created for the given upgrade path.

        Args:
            upgrade_path: The detected upgrade path.

        Returns:
            True if backup should be created, False otherwise.
        """
        # Fresh install doesn't need backup (nothing to back up)
        # All other paths (UPGRADE, REINSTALL, DOWNGRADE) need backup
        return upgrade_path != UpgradePath.FRESH_INSTALL

    def get_upgrade_message(
        self, upgrade_path: UpgradePath, from_ver: str | None, to_ver: str
    ) -> str:
        """Get a human-readable message for the upgrade path.

        Args:
            upgrade_path: The detected upgrade path.
            from_ver: Currently installed version (None for fresh install).
            to_ver: Target version to install.

        Returns:
            Human-readable message describing the upgrade path.
        """
        if upgrade_path == UpgradePath.FRESH_INSTALL:
            return f"Installing crafter-ai {to_ver} (fresh install)"

        if upgrade_path == UpgradePath.UPGRADE:
            return f"Upgrading crafter-ai from {from_ver} to {to_ver}"

        if upgrade_path == UpgradePath.REINSTALL:
            return f"crafter-ai {to_ver} is already installed. Reinstall?"

        if upgrade_path == UpgradePath.DOWNGRADE:
            return f"Warning: Downgrading crafter-ai from {from_ver} to {to_ver} (older version)"

        return f"Installing crafter-ai {to_ver}"

    def install(
        self,
        wheel_path: Path,
        force: bool = False,
        ci_mode: bool = False,
        on_progress: ProgressCallback | None = None,
    ) -> InstallResult:
        """Execute the complete install journey.

        Orchestrates: upgrade detection -> preflight -> readiness -> backup -> install -> verification

        Args:
            wheel_path: Path to the wheel file to install.
            force: If True, force reinstall even if already installed.
            ci_mode: If True, auto-proceed without interactive prompts.
            on_progress: Optional callback for progress updates (phase, message).

        Returns:
            InstallResult with complete journey state.
        """
        phases_completed: list[InstallPhase] = []

        def report_progress(phase: InstallPhase, message: str) -> None:
            """Report progress if callback is provided."""
            if on_progress:
                on_progress(phase, message)

        # Detect upgrade path before proceeding
        target_version = self._extract_version_from_wheel(wheel_path)
        needs_backup = False
        if target_version:
            upgrade_path = self.detect_upgrade_path(target_version)
            needs_backup = self.should_create_backup(upgrade_path)

        # Phase 1: Preflight checks
        report_progress(InstallPhase.PREFLIGHT, "Running pre-flight checks...")
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
        report_progress(
            InstallPhase.READINESS, "Validating wheel for release readiness..."
        )
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

        # Phase 3: Backup (non-blocking - only for upgrades/reinstalls, not fresh installs)
        if needs_backup:
            report_progress(
                InstallPhase.BACKUP, "Creating backup of existing configuration..."
            )
            backup_result = self._backup_port.create_backup(self._nwave_config_path)
            phases_completed.append(InstallPhase.BACKUP)
        else:
            report_progress(InstallPhase.BACKUP, "Fresh install, skipping backup")
            phases_completed.append(InstallPhase.BACKUP)

        # Phase 4: Install via pipx
        report_progress(
            InstallPhase.INSTALL,
            "Installing via pipx (downloading dependencies, may take 30-60 seconds)...",
        )
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

        # Resolve version and install_path via list_packages() when pipx
        # stdout doesn't include them (e.g. "already installed" scenario).
        version = pipx_result.version
        install_path = pipx_result.install_path
        if version is None or install_path is None:
            for pkg in self._pipx_port.list_packages():
                if pkg.name == "crafter-ai":
                    version = version or pkg.version
                    install_path = install_path or pkg.path
                    break

        # Phase 4.5: Asset deployment (only if asset_deployment_service provided)
        asset_deployment_result: AssetDeploymentResult | None = None
        deployment_validation_result: DeploymentValidationResult | None = None

        if self._asset_deployment_service is not None:
            report_progress(
                InstallPhase.ASSET_DEPLOYMENT,
                "Deploying IDE bundle assets to ~/.claude/...",
            )
            asset_deployment_result = self._asset_deployment_service.deploy(
                source_dir=DEFAULT_OUTPUT_DIR,
                target_dir=self._nwave_config_path,
            )

            if not asset_deployment_result.success:
                return InstallResult(
                    success=False,
                    version=version,
                    install_path=install_path,
                    phases_completed=phases_completed,
                    error_message=f"Asset deployment failed: {asset_deployment_result.error_message}",
                    asset_deployment_result=asset_deployment_result,
                )

            phases_completed.append(InstallPhase.ASSET_DEPLOYMENT)

            # Phase 4.6: Deployment validation (only if validation service provided
            # AND asset deployment succeeded)
            if self._deployment_validation_service is not None:
                report_progress(
                    InstallPhase.DEPLOYMENT_VALIDATION,
                    "Validating deployed assets...",
                )
                deployment_validation_result = (
                    self._deployment_validation_service.validate(
                        target_dir=self._nwave_config_path,
                        expected_agents=EXPECTED_AGENT_COUNT,
                        expected_commands=EXPECTED_COMMAND_COUNT,
                        expected_templates=EXPECTED_TEMPLATE_COUNT,
                        expected_scripts=EXPECTED_SCRIPT_COUNT,
                    )
                )

                if not deployment_validation_result.valid:
                    mismatch_detail = "; ".join(deployment_validation_result.mismatches)
                    return InstallResult(
                        success=False,
                        version=version,
                        install_path=install_path,
                        phases_completed=phases_completed,
                        error_message=f"Deployment validation failed: {mismatch_detail}",
                        asset_deployment_result=asset_deployment_result,
                        deployment_validation_result=deployment_validation_result,
                    )

                phases_completed.append(InstallPhase.DEPLOYMENT_VALIDATION)

        # Phase 5: Verification (only if health_checker provided)
        if self._health_checker is not None and install_path is not None:
            report_progress(
                InstallPhase.VERIFICATION, "Verifying installation health..."
            )
            verification_result = self.verify(install_path)
            phases_completed.append(InstallPhase.VERIFICATION)

            return InstallResult(
                success=True,
                version=version,
                install_path=install_path,
                phases_completed=phases_completed,
                error_message=None,
                health_status=verification_result.health_status,
                verification_warnings=verification_result.warnings,
                asset_deployment_result=asset_deployment_result,
                deployment_validation_result=deployment_validation_result,
            )

        # No verification (health_checker not provided)
        return InstallResult(
            success=True,
            version=version,
            install_path=install_path,
            phases_completed=phases_completed,
            error_message=None,
            health_status=None,
            verification_warnings=[],
            asset_deployment_result=asset_deployment_result,
            deployment_validation_result=deployment_validation_result,
        )
