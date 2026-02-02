"""Tests for BuildService orchestrating the complete build journey.

This module tests the BuildService application service that orchestrates:
- Pre-flight checks via CheckExecutor
- Version determination via VersionBumpService
- Wheel building via BuildPort
- Wheel validation via WheelValidationService
- Artifact registration via ArtifactRegistry
"""

from pathlib import Path
from unittest.mock import Mock, create_autospec

import pytest

from crafter_ai.installer.domain.artifact_registry import ArtifactRegistry
from crafter_ai.installer.domain.candidate_version import BumpType, CandidateVersion
from crafter_ai.installer.domain.check_executor import CheckExecutor
from crafter_ai.installer.domain.check_result import CheckResult, CheckSeverity
from crafter_ai.installer.ports.build_port import BuildError, BuildPort
from crafter_ai.installer.services.build_service import BuildResult, BuildService
from crafter_ai.installer.services.version_bump_service import VersionBumpService
from crafter_ai.installer.services.wheel_validation_service import (
    WheelValidationResult,
    WheelValidationService,
)


# ═══════════════════════════════════════════════════════════════════════════════
# Fixtures
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.fixture
def mock_check_executor() -> Mock:
    """Create a mock CheckExecutor."""
    return create_autospec(CheckExecutor, instance=True)


@pytest.fixture
def mock_build_port() -> Mock:
    """Create a mock BuildPort."""
    return create_autospec(BuildPort, instance=True)


@pytest.fixture
def mock_version_bump_service() -> Mock:
    """Create a mock VersionBumpService."""
    return create_autospec(VersionBumpService, instance=True)


@pytest.fixture
def mock_wheel_validation_service() -> Mock:
    """Create a mock WheelValidationService."""
    return create_autospec(WheelValidationService, instance=True)


@pytest.fixture
def artifact_registry() -> ArtifactRegistry:
    """Create a real ArtifactRegistry for testing."""
    return ArtifactRegistry()


@pytest.fixture
def build_service(
    mock_check_executor: Mock,
    mock_build_port: Mock,
    mock_version_bump_service: Mock,
    mock_wheel_validation_service: Mock,
    artifact_registry: ArtifactRegistry,
) -> BuildService:
    """Create a BuildService with mocked dependencies."""
    return BuildService(
        check_executor=mock_check_executor,
        build_port=mock_build_port,
        version_bump_service=mock_version_bump_service,
        wheel_validation_service=mock_wheel_validation_service,
        artifact_registry=artifact_registry,
    )


@pytest.fixture
def passing_check_result() -> CheckResult:
    """Create a passing CheckResult."""
    return CheckResult(
        id="test_check",
        name="Test Check",
        passed=True,
        severity=CheckSeverity.BLOCKING,
        message="Check passed",
    )


@pytest.fixture
def failing_blocking_check_result() -> CheckResult:
    """Create a failing BLOCKING CheckResult."""
    return CheckResult(
        id="blocking_check",
        name="Blocking Check",
        passed=False,
        severity=CheckSeverity.BLOCKING,
        message="Blocking check failed",
    )


@pytest.fixture
def failing_warning_check_result() -> CheckResult:
    """Create a failing WARNING CheckResult."""
    return CheckResult(
        id="warning_check",
        name="Warning Check",
        passed=False,
        severity=CheckSeverity.WARNING,
        message="Warning check failed",
    )


@pytest.fixture
def candidate_version() -> CandidateVersion:
    """Create a CandidateVersion for testing."""
    return CandidateVersion(
        current_version="1.0.0",
        bump_type=BumpType.MINOR,
        next_version="1.1.0",
        commit_messages=["feat: add feature"],
        is_prerelease=False,
        prerelease_suffix=None,
    )


@pytest.fixture
def wheel_path(tmp_path: Path) -> Path:
    """Create a mock wheel path."""
    return tmp_path / "crafter_ai-1.1.0-py3-none-any.whl"


@pytest.fixture
def valid_wheel_validation_result(wheel_path: Path) -> WheelValidationResult:
    """Create a valid WheelValidationResult."""
    return WheelValidationResult(
        wheel_path=wheel_path,
        is_valid=True,
        version="1.1.0",
        package_name="crafter_ai",
        errors=[],
    )


@pytest.fixture
def invalid_wheel_validation_result(wheel_path: Path) -> WheelValidationResult:
    """Create an invalid WheelValidationResult."""
    return WheelValidationResult(
        wheel_path=wheel_path,
        is_valid=False,
        version=None,
        package_name=None,
        errors=["Invalid wheel format"],
    )


# ═══════════════════════════════════════════════════════════════════════════════
# BuildResult Tests
# ═══════════════════════════════════════════════════════════════════════════════


class TestBuildResult:
    """Tests for BuildResult dataclass."""

    def test_build_result_creation_success(
        self,
        wheel_path: Path,
        passing_check_result: CheckResult,
        valid_wheel_validation_result: WheelValidationResult,
    ) -> None:
        """Test creating a successful BuildResult."""
        result = BuildResult(
            success=True,
            wheel_path=wheel_path,
            version="1.1.0",
            pre_flight_results=[passing_check_result],
            validation_result=valid_wheel_validation_result,
            error_message=None,
        )

        assert result.success is True
        assert result.wheel_path == wheel_path
        assert result.version == "1.1.0"
        assert result.pre_flight_results == [passing_check_result]
        assert result.validation_result == valid_wheel_validation_result
        assert result.error_message is None

    def test_build_result_creation_failure(
        self,
        failing_blocking_check_result: CheckResult,
    ) -> None:
        """Test creating a failed BuildResult."""
        result = BuildResult(
            success=False,
            wheel_path=None,
            version=None,
            pre_flight_results=[failing_blocking_check_result],
            validation_result=None,
            error_message="Pre-flight check failed",
        )

        assert result.success is False
        assert result.wheel_path is None
        assert result.version is None
        assert result.error_message == "Pre-flight check failed"

    def test_build_result_is_frozen(self, wheel_path: Path) -> None:
        """Test that BuildResult is immutable (frozen)."""
        result = BuildResult(
            success=True,
            wheel_path=wheel_path,
            version="1.0.0",
            pre_flight_results=[],
            validation_result=None,
            error_message=None,
        )

        with pytest.raises(AttributeError):
            result.success = False  # type: ignore[misc]


# ═══════════════════════════════════════════════════════════════════════════════
# BuildService Tests - Individual Methods
# ═══════════════════════════════════════════════════════════════════════════════


class TestBuildServicePreFlightChecks:
    """Tests for run_pre_flight_checks method."""

    def test_run_pre_flight_checks_uses_check_executor(
        self,
        build_service: BuildService,
        mock_check_executor: Mock,
        passing_check_result: CheckResult,
    ) -> None:
        """Test that run_pre_flight_checks uses the CheckExecutor."""
        mock_check_executor.run_all.return_value = [passing_check_result]

        results = build_service.run_pre_flight_checks()

        mock_check_executor.run_all.assert_called_once()
        assert results == [passing_check_result]


class TestBuildServiceDetermineVersion:
    """Tests for determine_version method."""

    def test_determine_version_uses_version_bump_service(
        self,
        build_service: BuildService,
        mock_version_bump_service: Mock,
        candidate_version: CandidateVersion,
    ) -> None:
        """Test that determine_version uses VersionBumpService."""
        mock_version_bump_service.analyze_commits.return_value = ["feat: add feature"]
        mock_version_bump_service.create_version_candidate.return_value = (
            candidate_version
        )

        result = build_service.determine_version("1.0.0")

        mock_version_bump_service.analyze_commits.assert_called_once()
        mock_version_bump_service.create_version_candidate.assert_called_once_with(
            "1.0.0", prerelease=None
        )
        assert result == candidate_version

    def test_determine_version_with_prerelease(
        self,
        build_service: BuildService,
        mock_version_bump_service: Mock,
    ) -> None:
        """Test determine_version with prerelease suffix."""
        prerelease_candidate = CandidateVersion(
            current_version="1.0.0",
            bump_type=BumpType.MINOR,
            next_version="1.1.0.dev1",
            commit_messages=["feat: add feature"],
            is_prerelease=True,
            prerelease_suffix="dev1",
        )
        mock_version_bump_service.analyze_commits.return_value = []
        mock_version_bump_service.create_version_candidate.return_value = (
            prerelease_candidate
        )

        result = build_service.determine_version("1.0.0", prerelease="dev1")

        mock_version_bump_service.create_version_candidate.assert_called_once_with(
            "1.0.0", prerelease="dev1"
        )
        assert result == prerelease_candidate


class TestBuildServiceBuildWheel:
    """Tests for build_wheel method."""

    def test_build_wheel_uses_build_port(
        self,
        build_service: BuildService,
        mock_build_port: Mock,
        wheel_path: Path,
        tmp_path: Path,
    ) -> None:
        """Test that build_wheel uses the BuildPort."""
        mock_build_port.build_wheel.return_value = wheel_path

        result = build_service.build_wheel(tmp_path)

        mock_build_port.build_wheel.assert_called_once_with(tmp_path)
        assert result == wheel_path


class TestBuildServiceValidateWheel:
    """Tests for validate_wheel method."""

    def test_validate_wheel_uses_wheel_validation_service(
        self,
        build_service: BuildService,
        mock_wheel_validation_service: Mock,
        wheel_path: Path,
        valid_wheel_validation_result: WheelValidationResult,
    ) -> None:
        """Test that validate_wheel uses WheelValidationService."""
        mock_wheel_validation_service.validate.return_value = (
            valid_wheel_validation_result
        )

        result = build_service.validate_wheel(wheel_path)

        mock_wheel_validation_service.validate.assert_called_once_with(wheel_path)
        assert result == valid_wheel_validation_result


# ═══════════════════════════════════════════════════════════════════════════════
# BuildService Tests - Execute Orchestration
# ═══════════════════════════════════════════════════════════════════════════════


class TestBuildServiceExecute:
    """Tests for execute method that orchestrates the full build flow."""

    def test_execute_orchestrates_full_flow_on_success(
        self,
        build_service: BuildService,
        mock_check_executor: Mock,
        mock_build_port: Mock,
        mock_version_bump_service: Mock,
        mock_wheel_validation_service: Mock,
        passing_check_result: CheckResult,
        candidate_version: CandidateVersion,
        wheel_path: Path,
        valid_wheel_validation_result: WheelValidationResult,
        tmp_path: Path,
    ) -> None:
        """Test execute orchestrates: pre_flight -> version -> build -> validate."""
        # Setup mocks
        mock_check_executor.run_all.return_value = [passing_check_result]
        mock_version_bump_service.analyze_commits.return_value = ["feat: add feature"]
        mock_version_bump_service.create_version_candidate.return_value = (
            candidate_version
        )
        mock_build_port.build_wheel.return_value = wheel_path
        mock_wheel_validation_service.validate.return_value = (
            valid_wheel_validation_result
        )

        # Execute
        result = build_service.execute(current_version="1.0.0", output_dir=tmp_path)

        # Verify orchestration order
        mock_check_executor.run_all.assert_called_once()
        mock_version_bump_service.analyze_commits.assert_called_once()
        mock_version_bump_service.create_version_candidate.assert_called_once()
        mock_build_port.build_wheel.assert_called_once_with(tmp_path)
        mock_wheel_validation_service.validate.assert_called_once_with(wheel_path)

        # Verify result
        assert result.success is True
        assert result.wheel_path == wheel_path
        assert result.version == "1.1.0"
        assert result.pre_flight_results == [passing_check_result]
        assert result.validation_result == valid_wheel_validation_result
        assert result.error_message is None

    def test_execute_returns_failure_on_pre_flight_blocking_errors(
        self,
        build_service: BuildService,
        mock_check_executor: Mock,
        mock_build_port: Mock,
        failing_blocking_check_result: CheckResult,
        tmp_path: Path,
    ) -> None:
        """Test execute returns failure when pre-flight has blocking errors."""
        mock_check_executor.run_all.return_value = [failing_blocking_check_result]

        result = build_service.execute(current_version="1.0.0", output_dir=tmp_path)

        # Verify build was not attempted
        mock_build_port.build_wheel.assert_not_called()

        # Verify failure result
        assert result.success is False
        assert result.wheel_path is None
        assert result.version is None
        assert result.pre_flight_results == [failing_blocking_check_result]
        assert "pre-flight" in result.error_message.lower()

    def test_execute_continues_with_warnings_only(
        self,
        build_service: BuildService,
        mock_check_executor: Mock,
        mock_build_port: Mock,
        mock_version_bump_service: Mock,
        mock_wheel_validation_service: Mock,
        failing_warning_check_result: CheckResult,
        candidate_version: CandidateVersion,
        wheel_path: Path,
        valid_wheel_validation_result: WheelValidationResult,
        tmp_path: Path,
    ) -> None:
        """Test execute continues when only warnings are present (no blocking errors)."""
        mock_check_executor.run_all.return_value = [failing_warning_check_result]
        mock_version_bump_service.analyze_commits.return_value = []
        mock_version_bump_service.create_version_candidate.return_value = (
            candidate_version
        )
        mock_build_port.build_wheel.return_value = wheel_path
        mock_wheel_validation_service.validate.return_value = (
            valid_wheel_validation_result
        )

        result = build_service.execute(current_version="1.0.0", output_dir=tmp_path)

        # Verify build was attempted despite warning
        mock_build_port.build_wheel.assert_called_once()

        # Verify success
        assert result.success is True

    def test_execute_returns_failure_on_build_error(
        self,
        build_service: BuildService,
        mock_check_executor: Mock,
        mock_build_port: Mock,
        mock_version_bump_service: Mock,
        passing_check_result: CheckResult,
        candidate_version: CandidateVersion,
        tmp_path: Path,
    ) -> None:
        """Test execute returns failure when build fails."""
        mock_check_executor.run_all.return_value = [passing_check_result]
        mock_version_bump_service.analyze_commits.return_value = []
        mock_version_bump_service.create_version_candidate.return_value = (
            candidate_version
        )
        mock_build_port.build_wheel.side_effect = BuildError("Build failed")

        result = build_service.execute(current_version="1.0.0", output_dir=tmp_path)

        # Verify failure result
        assert result.success is False
        assert result.wheel_path is None
        assert "Build failed" in result.error_message

    def test_execute_stores_wheel_path_in_artifact_registry(
        self,
        build_service: BuildService,
        mock_check_executor: Mock,
        mock_build_port: Mock,
        mock_version_bump_service: Mock,
        mock_wheel_validation_service: Mock,
        artifact_registry: ArtifactRegistry,
        passing_check_result: CheckResult,
        candidate_version: CandidateVersion,
        wheel_path: Path,
        valid_wheel_validation_result: WheelValidationResult,
        tmp_path: Path,
    ) -> None:
        """Test execute stores wheel_path in artifact_registry on success."""
        mock_check_executor.run_all.return_value = [passing_check_result]
        mock_version_bump_service.analyze_commits.return_value = []
        mock_version_bump_service.create_version_candidate.return_value = (
            candidate_version
        )
        mock_build_port.build_wheel.return_value = wheel_path
        mock_wheel_validation_service.validate.return_value = (
            valid_wheel_validation_result
        )

        build_service.execute(current_version="1.0.0", output_dir=tmp_path)

        # Verify artifact was stored
        assert artifact_registry.has(ArtifactRegistry.WHEEL_PATH)
        assert artifact_registry.get(ArtifactRegistry.WHEEL_PATH) == wheel_path

    def test_execute_stores_version_in_artifact_registry(
        self,
        build_service: BuildService,
        mock_check_executor: Mock,
        mock_build_port: Mock,
        mock_version_bump_service: Mock,
        mock_wheel_validation_service: Mock,
        artifact_registry: ArtifactRegistry,
        passing_check_result: CheckResult,
        candidate_version: CandidateVersion,
        wheel_path: Path,
        valid_wheel_validation_result: WheelValidationResult,
        tmp_path: Path,
    ) -> None:
        """Test execute stores version in artifact_registry on success."""
        mock_check_executor.run_all.return_value = [passing_check_result]
        mock_version_bump_service.analyze_commits.return_value = []
        mock_version_bump_service.create_version_candidate.return_value = (
            candidate_version
        )
        mock_build_port.build_wheel.return_value = wheel_path
        mock_wheel_validation_service.validate.return_value = (
            valid_wheel_validation_result
        )

        build_service.execute(current_version="1.0.0", output_dir=tmp_path)

        # Verify version was stored
        assert artifact_registry.has(ArtifactRegistry.VERSION)
        assert artifact_registry.get(ArtifactRegistry.VERSION) == "1.1.0"

    def test_execute_does_not_store_artifacts_on_failure(
        self,
        build_service: BuildService,
        mock_check_executor: Mock,
        artifact_registry: ArtifactRegistry,
        failing_blocking_check_result: CheckResult,
        tmp_path: Path,
    ) -> None:
        """Test execute does not store artifacts when build fails."""
        mock_check_executor.run_all.return_value = [failing_blocking_check_result]

        build_service.execute(current_version="1.0.0", output_dir=tmp_path)

        # Verify no artifacts were stored
        assert not artifact_registry.has(ArtifactRegistry.WHEEL_PATH)
        assert not artifact_registry.has(ArtifactRegistry.VERSION)

    def test_execute_returns_failure_on_invalid_wheel(
        self,
        build_service: BuildService,
        mock_check_executor: Mock,
        mock_build_port: Mock,
        mock_version_bump_service: Mock,
        mock_wheel_validation_service: Mock,
        artifact_registry: ArtifactRegistry,
        passing_check_result: CheckResult,
        candidate_version: CandidateVersion,
        wheel_path: Path,
        invalid_wheel_validation_result: WheelValidationResult,
        tmp_path: Path,
    ) -> None:
        """Test execute returns failure when wheel validation fails."""
        mock_check_executor.run_all.return_value = [passing_check_result]
        mock_version_bump_service.analyze_commits.return_value = []
        mock_version_bump_service.create_version_candidate.return_value = (
            candidate_version
        )
        mock_build_port.build_wheel.return_value = wheel_path
        mock_wheel_validation_service.validate.return_value = (
            invalid_wheel_validation_result
        )

        result = build_service.execute(current_version="1.0.0", output_dir=tmp_path)

        # Verify failure result
        assert result.success is False
        assert result.wheel_path == wheel_path
        assert "Invalid wheel format" in result.error_message

        # Verify no artifacts were stored on validation failure
        assert not artifact_registry.has(ArtifactRegistry.WHEEL_PATH)
