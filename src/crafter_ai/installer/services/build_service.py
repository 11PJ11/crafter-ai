"""BuildService for orchestrating the complete build journey.

This module provides the BuildService application service that orchestrates:
- Pre-flight checks via CheckExecutor
- Version determination via VersionBumpService
- Wheel building via BuildPort
- Wheel validation via WheelValidationService
- Artifact registration via ArtifactRegistry
- IDE bundle building via IdeBundleBuildService (optional)

Used by: forge:build CLI command
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

from crafter_ai.installer.domain.artifact_registry import ArtifactRegistry

if TYPE_CHECKING:
    from rich.console import Console
from crafter_ai.installer.domain.candidate_version import CandidateVersion
from crafter_ai.installer.domain.check_executor import CheckExecutor
from crafter_ai.installer.domain.check_result import CheckResult, CheckSeverity
from crafter_ai.installer.domain.ide_bundle_build_result import IdeBundleBuildResult
from crafter_ai.installer.domain.ide_bundle_constants import (
    DEFAULT_OUTPUT_DIR,
    DEFAULT_SOURCE_DIR,
)
from crafter_ai.installer.ports.build_port import BuildError, BuildPort
from crafter_ai.installer.services.ide_bundle_build_service import IdeBundleBuildService
from crafter_ai.installer.services.version_bump_service import VersionBumpService
from crafter_ai.installer.services.wheel_validation_service import (
    WheelValidationResult,
    WheelValidationService,
)


@dataclass(frozen=True)
class BuildResult:
    """Immutable result of the build journey.

    Attributes:
        success: Whether the build completed successfully.
        wheel_path: Path to the built wheel file, None if build failed.
        version: Version string of the built wheel, None if build failed.
        pre_flight_results: List of pre-flight check results.
        validation_result: Wheel validation result, None if build didn't reach validation.
        error_message: Error message if build failed, None if successful.
        ide_bundle_result: IDE bundle build result, None if not requested or not reached.
    """

    success: bool
    wheel_path: Path | None
    version: str | None
    pre_flight_results: list[CheckResult]
    validation_result: WheelValidationResult | None
    error_message: str | None
    ide_bundle_result: IdeBundleBuildResult | None = None


class BuildService:
    """Application service orchestrating the complete build journey.

    This service coordinates:
    1. Pre-flight checks - verifying build prerequisites
    2. Version determination - calculating next version from commits
    3. Wheel building - creating the wheel artifact
    4. Wheel validation - verifying the built wheel
    5. IDE bundle building - creating IDE assets (optional)

    On success, stores artifacts in the registry for downstream consumers.
    """

    def __init__(
        self,
        check_executor: CheckExecutor,
        build_port: BuildPort,
        version_bump_service: VersionBumpService,
        wheel_validation_service: WheelValidationService,
        artifact_registry: ArtifactRegistry,
        ide_bundle_build_service: IdeBundleBuildService | None = None,
    ) -> None:
        """Initialize BuildService with dependencies.

        Args:
            check_executor: Executor for running pre-flight checks.
            build_port: Port for building wheel artifacts.
            version_bump_service: Service for determining version bumps.
            wheel_validation_service: Service for validating wheel files.
            artifact_registry: Registry for storing build artifacts.
            ide_bundle_build_service: Optional service for building IDE bundles.
                When None (default), IDE bundle step is skipped.
        """
        self._check_executor = check_executor
        self._build_port = build_port
        self._version_bump_service = version_bump_service
        self._wheel_validation_service = wheel_validation_service
        self._artifact_registry = artifact_registry
        self._ide_bundle_build_service = ide_bundle_build_service

    def run_pre_flight_checks(self) -> list[CheckResult]:
        """Run all pre-flight checks.

        Returns:
            List of CheckResult from all registered checks.
        """
        return self._check_executor.run_all()

    def determine_version(
        self,
        current_version: str,
        prerelease: str | None = None,
    ) -> CandidateVersion:
        """Determine the next version based on commits.

        Args:
            current_version: Current version string (e.g., '1.0.0').
            prerelease: Optional prerelease suffix (e.g., 'dev1', 'rc1').

        Returns:
            CandidateVersion with calculated next version.
        """
        self._version_bump_service.analyze_commits()
        return self._version_bump_service.create_version_candidate(
            current_version, prerelease=prerelease
        )

    def build_wheel(self, output_dir: Path) -> Path:
        """Build a wheel package.

        Args:
            output_dir: Directory where the wheel should be placed.

        Returns:
            Path to the built .whl file.

        Raises:
            BuildError: If the build fails.
        """
        return self._build_port.build_wheel(output_dir)

    def validate_wheel(self, wheel_path: Path) -> WheelValidationResult:
        """Validate a wheel file.

        Args:
            wheel_path: Path to the wheel file to validate.

        Returns:
            WheelValidationResult with validation outcome and metadata.
        """
        return self._wheel_validation_service.validate(wheel_path)

    def execute(
        self,
        current_version: str,
        output_dir: Path,
        prerelease: str | None = None,
        console: "Console | None" = None,
        spinner_style: str = "aesthetic",
    ) -> BuildResult:
        """Execute the complete build journey.

        Orchestrates: pre_flight -> version -> build -> validate

        Args:
            current_version: Current version string.
            output_dir: Directory for wheel output.
            prerelease: Optional prerelease suffix.
            console: Optional Rich console for displaying spinners.
            spinner_style: Spinner style (aesthetic, dots, earth, runner).

        Returns:
            BuildResult with complete journey state.
        """
        # Step 1: Run pre-flight checks
        pre_flight_results = self.run_pre_flight_checks()

        # Check for blocking failures
        blocking_failures = [
            r
            for r in pre_flight_results
            if not r.passed and r.severity == CheckSeverity.BLOCKING
        ]

        if blocking_failures:
            return BuildResult(
                success=False,
                wheel_path=None,
                version=None,
                pre_flight_results=pre_flight_results,
                validation_result=None,
                error_message="Pre-flight checks failed with blocking errors",
            )

        # Step 2: Determine version
        candidate = self.determine_version(current_version, prerelease=prerelease)

        # Step 3: Build wheel
        try:
            if console is not None:
                with console.status("⏳ Compiling wheel...", spinner=spinner_style):
                    wheel_path = self.build_wheel(output_dir)
            else:
                wheel_path = self.build_wheel(output_dir)
        except BuildError as e:
            return BuildResult(
                success=False,
                wheel_path=None,
                version=None,
                pre_flight_results=pre_flight_results,
                validation_result=None,
                error_message=str(e),
            )

        # Step 4: Validate wheel
        validation_result = self.validate_wheel(wheel_path)

        if not validation_result.is_valid:
            return BuildResult(
                success=False,
                wheel_path=wheel_path,
                version=None,
                pre_flight_results=pre_flight_results,
                validation_result=validation_result,
                error_message="; ".join(validation_result.errors),
            )

        # Step 5: Store artifacts on success
        self._artifact_registry.set(ArtifactRegistry.WHEEL_PATH, wheel_path)
        self._artifact_registry.set(ArtifactRegistry.VERSION, candidate.next_version)

        # Step 5.5: Build IDE bundle (optional)
        ide_bundle_result: IdeBundleBuildResult | None = None
        if self._ide_bundle_build_service is not None:
            if console is not None:
                with console.status("⏳ Processing nWave assets...", spinner=spinner_style):
                    ide_bundle_result = self._ide_bundle_build_service.build(
                        source_dir=DEFAULT_SOURCE_DIR,
                        output_dir=DEFAULT_OUTPUT_DIR,
                    )
            else:
                ide_bundle_result = self._ide_bundle_build_service.build(
                    source_dir=DEFAULT_SOURCE_DIR,
                    output_dir=DEFAULT_OUTPUT_DIR,
                )
            if not ide_bundle_result.success:
                return BuildResult(
                    success=False,
                    wheel_path=wheel_path,
                    version=candidate.next_version,
                    pre_flight_results=pre_flight_results,
                    validation_result=validation_result,
                    error_message=f"IDE bundle build failed: {ide_bundle_result.error_message}",
                    ide_bundle_result=ide_bundle_result,
                )

        return BuildResult(
            success=True,
            wheel_path=wheel_path,
            version=candidate.next_version,
            pre_flight_results=pre_flight_results,
            validation_result=validation_result,
            error_message=None,
            ide_bundle_result=ide_bundle_result,
        )
