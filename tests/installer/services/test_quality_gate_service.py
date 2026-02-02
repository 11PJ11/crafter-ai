"""Tests for QualityGateService.

This module tests the QualityGateService for validating TestPyPI CI quality gates.
"""

from crafter_ai.installer.services.quality_gate_service import (
    GateResult,
    QualityGateResult,
    QualityGateService,
)


class TestGateResult:
    """Tests for GateResult dataclass."""

    def test_gate_result_creation_with_all_fields(self) -> None:
        """Test GateResult can be created with all fields."""
        result = GateResult(
            check_name="test_check",
            passed=True,
            message="Test passed",
            suggested_fix=None,
        )
        assert result.check_name == "test_check"
        assert result.passed is True
        assert result.message == "Test passed"
        assert result.suggested_fix is None

    def test_gate_result_with_suggested_fix(self) -> None:
        """Test GateResult with suggested_fix populated on failure."""
        result = GateResult(
            check_name="failed_check",
            passed=False,
            message="Check failed",
            suggested_fix="Try this fix",
        )
        assert result.passed is False
        assert result.suggested_fix == "Try this fix"

    def test_gate_result_default_suggested_fix_is_none(self) -> None:
        """Test GateResult default suggested_fix is None."""
        result = GateResult(
            check_name="check",
            passed=True,
            message="Passed",
        )
        assert result.suggested_fix is None


class TestQualityGateResult:
    """Tests for QualityGateResult dataclass."""

    def test_quality_gate_result_creation(self) -> None:
        """Test QualityGateResult can be created with all fields."""
        gate_results = [
            GateResult(check_name="check1", passed=True, message="OK"),
            GateResult(check_name="check2", passed=False, message="Failed"),
        ]
        result = QualityGateResult(
            passed=False,
            gate_results=gate_results,
            summary="1/2 passed",
        )
        assert result.passed is False
        assert len(result.gate_results) == 2
        assert result.summary == "1/2 passed"

    def test_quality_gate_result_default_values(self) -> None:
        """Test QualityGateResult default values."""
        result = QualityGateResult(passed=True)
        assert result.passed is True
        assert result.gate_results == []
        assert result.summary == ""


class TestQualityGateServiceValidateWheelBuild:
    """Tests for validate_wheel_build method."""

    def test_validate_wheel_build_success(self) -> None:
        """Test validate_wheel_build returns success when wheel exists."""
        service = QualityGateService()
        result = service.validate_wheel_build(
            wheel_exists=True,
            wheel_path="dist/crafter_ai-1.0.0-py3-none-any.whl",
        )
        assert result.passed is True
        assert result.check_name == "wheel_build"
        assert "successful" in result.message.lower()
        assert result.suggested_fix is None

    def test_validate_wheel_build_failure_no_wheel(self) -> None:
        """Test validate_wheel_build returns failure when wheel doesn't exist."""
        service = QualityGateService()
        result = service.validate_wheel_build(wheel_exists=False)
        assert result.passed is False
        assert result.check_name == "wheel_build"
        assert "not found" in result.message.lower()
        assert result.suggested_fix is not None
        assert "python -m build" in result.suggested_fix

    def test_validate_wheel_build_failure_with_error(self) -> None:
        """Test validate_wheel_build returns failure with build error."""
        service = QualityGateService()
        result = service.validate_wheel_build(
            wheel_exists=False,
            build_error="Invalid pyproject.toml",
        )
        assert result.passed is False
        assert "Invalid pyproject.toml" in result.message
        assert result.suggested_fix is not None
        assert "pyproject.toml" in result.suggested_fix


class TestQualityGateServiceValidateTwineCheck:
    """Tests for validate_twine_check method."""

    def test_validate_twine_check_success(self) -> None:
        """Test validate_twine_check returns success when check passes."""
        service = QualityGateService()
        result = service.validate_twine_check(check_passed=True)
        assert result.passed is True
        assert result.check_name == "twine_check"
        assert "passed" in result.message.lower()
        assert result.suggested_fix is None

    def test_validate_twine_check_failure(self) -> None:
        """Test validate_twine_check returns failure when check fails."""
        service = QualityGateService()
        result = service.validate_twine_check(
            check_passed=False,
            check_output="Invalid metadata",
        )
        assert result.passed is False
        assert result.check_name == "twine_check"
        assert result.suggested_fix is not None
        assert "twine check" in result.suggested_fix.lower()

    def test_validate_twine_check_failure_with_error(self) -> None:
        """Test validate_twine_check returns failure with check error."""
        service = QualityGateService()
        result = service.validate_twine_check(
            check_passed=False,
            check_error="README.md syntax error",
        )
        assert result.passed is False
        assert "README.md syntax error" in result.message
        assert result.suggested_fix is not None


class TestQualityGateServiceValidateTestPyPIUpload:
    """Tests for validate_testpypi_upload method."""

    def test_validate_testpypi_upload_success(self) -> None:
        """Test validate_testpypi_upload returns success when upload succeeds."""
        service = QualityGateService()
        result = service.validate_testpypi_upload(
            upload_success=True,
            version="1.0.0.dev20260201",
        )
        assert result.passed is True
        assert result.check_name == "testpypi_upload"
        assert "successful" in result.message.lower()
        assert "1.0.0.dev20260201" in result.message
        assert result.suggested_fix is None

    def test_validate_testpypi_upload_failure(self) -> None:
        """Test validate_testpypi_upload returns failure when upload fails."""
        service = QualityGateService()
        result = service.validate_testpypi_upload(upload_success=False)
        assert result.passed is False
        assert result.check_name == "testpypi_upload"
        assert result.suggested_fix is not None
        assert "token" in result.suggested_fix.lower()

    def test_validate_testpypi_upload_failure_with_error_and_retries(self) -> None:
        """Test validate_testpypi_upload shows retry count in failure message."""
        service = QualityGateService()
        result = service.validate_testpypi_upload(
            upload_success=False,
            upload_error="Connection timeout",
            retry_count=3,
        )
        assert result.passed is False
        assert "3 retries" in result.message
        assert "Connection timeout" in result.message
        assert result.suggested_fix is not None


class TestQualityGateServiceValidateTestPyPIInstall:
    """Tests for validate_testpypi_install method."""

    def test_validate_testpypi_install_success(self) -> None:
        """Test validate_testpypi_install returns success when install succeeds."""
        service = QualityGateService()
        result = service.validate_testpypi_install(
            install_success=True,
            version="1.0.0.dev20260201",
        )
        assert result.passed is True
        assert result.check_name == "testpypi_install"
        assert "successful" in result.message.lower()
        assert "1.0.0.dev20260201" in result.message
        assert result.suggested_fix is None

    def test_validate_testpypi_install_failure(self) -> None:
        """Test validate_testpypi_install returns failure when install fails."""
        service = QualityGateService()
        result = service.validate_testpypi_install(install_success=False)
        assert result.passed is False
        assert result.check_name == "testpypi_install"
        assert result.suggested_fix is not None
        assert "pipx install" in result.suggested_fix

    def test_validate_testpypi_install_failure_with_retries(self) -> None:
        """Test validate_testpypi_install shows retry count in failure message."""
        service = QualityGateService()
        result = service.validate_testpypi_install(
            install_success=False,
            install_error="Package not found",
            retry_count=2,
        )
        assert result.passed is False
        assert "2 retries" in result.message
        assert "Package not found" in result.message


class TestQualityGateServiceValidateDoctorHealthy:
    """Tests for validate_doctor_healthy method."""

    def test_validate_doctor_healthy_success(self) -> None:
        """Test validate_doctor_healthy returns success when healthy."""
        service = QualityGateService()
        result = service.validate_doctor_healthy(is_healthy=True)
        assert result.passed is True
        assert result.check_name == "doctor_healthy"
        assert "passed" in result.message.lower()
        assert result.suggested_fix is None

    def test_validate_doctor_healthy_failure(self) -> None:
        """Test validate_doctor_healthy returns failure when unhealthy."""
        service = QualityGateService()
        result = service.validate_doctor_healthy(
            is_healthy=False,
            health_output="Component X unhealthy",
        )
        assert result.passed is False
        assert result.check_name == "doctor_healthy"
        assert "Component X unhealthy" in result.message
        assert result.suggested_fix is not None
        assert "doctor" in result.suggested_fix.lower()

    def test_validate_doctor_healthy_failure_with_error(self) -> None:
        """Test validate_doctor_healthy returns failure with error."""
        service = QualityGateService()
        result = service.validate_doctor_healthy(
            is_healthy=False,
            health_error="Command not found",
        )
        assert result.passed is False
        assert "Command not found" in result.message
        assert result.suggested_fix is not None


class TestQualityGateServiceValidateAll:
    """Tests for validate_all method."""

    def test_validate_all_success(self) -> None:
        """Test validate_all returns success when all gates pass."""
        service = QualityGateService()
        result = service.validate_all(
            wheel_exists=True,
            wheel_path="dist/test.whl",
            twine_check_passed=True,
            upload_success=True,
            upload_version="1.0.0",
            install_success=True,
            install_version="1.0.0",
            is_healthy=True,
        )
        assert result.passed is True
        assert len(result.gate_results) == 5
        assert all(r.passed for r in result.gate_results)
        assert "All 5 quality gates passed" in result.summary

    def test_validate_all_partial_failure(self) -> None:
        """Test validate_all returns failure when some gates fail."""
        service = QualityGateService()
        result = service.validate_all(
            wheel_exists=True,
            wheel_path="dist/test.whl",
            twine_check_passed=True,
            upload_success=False,  # This fails
            install_success=False,  # This fails
            is_healthy=True,
        )
        assert result.passed is False
        assert len(result.gate_results) == 5
        passed_count = sum(1 for r in result.gate_results if r.passed)
        assert passed_count == 3
        assert "3/5" in result.summary
        assert "testpypi_upload" in result.summary
        assert "testpypi_install" in result.summary

    def test_validate_all_complete_failure(self) -> None:
        """Test validate_all returns failure when all gates fail."""
        service = QualityGateService()
        result = service.validate_all(
            wheel_exists=False,
            twine_check_passed=False,
            upload_success=False,
            install_success=False,
            is_healthy=False,
        )
        assert result.passed is False
        assert len(result.gate_results) == 5
        assert not any(r.passed for r in result.gate_results)
        assert "0/5" in result.summary


class TestQualityGateServiceGetFailureDiagnostics:
    """Tests for get_failure_diagnostics method."""

    def test_get_failure_diagnostics_no_results(self) -> None:
        """Test get_failure_diagnostics returns message when no results."""
        service = QualityGateService()
        diagnostics = service.get_failure_diagnostics()
        assert "No quality gate results" in diagnostics

    def test_get_failure_diagnostics_all_passed(self) -> None:
        """Test get_failure_diagnostics returns success message when all pass."""
        service = QualityGateService()
        service.validate_all(
            wheel_exists=True,
            twine_check_passed=True,
            upload_success=True,
            install_success=True,
            is_healthy=True,
        )
        diagnostics = service.get_failure_diagnostics()
        assert "All quality gates passed" in diagnostics

    def test_get_failure_diagnostics_with_failures(self) -> None:
        """Test get_failure_diagnostics returns detailed failure info."""
        service = QualityGateService()
        service.validate_all(
            wheel_exists=False,
            twine_check_passed=True,
            upload_success=False,
            upload_error="Auth failed",
            install_success=True,
            is_healthy=True,
        )
        diagnostics = service.get_failure_diagnostics()

        # Check structure
        assert "## Quality Gate Failures" in diagnostics
        assert "2 gate(s) failed" in diagnostics

        # Check failed gates are included
        assert "wheel_build" in diagnostics
        assert "testpypi_upload" in diagnostics
        assert "Auth failed" in diagnostics

        # Check suggested fixes are included
        assert "Suggested Fix" in diagnostics

    def test_get_failure_diagnostics_contains_suggested_fixes(self) -> None:
        """Test get_failure_diagnostics includes suggested fixes for all failures."""
        service = QualityGateService()
        service.validate_all(
            wheel_exists=False,
            build_error="Syntax error",
            twine_check_passed=False,
            twine_check_error="Invalid metadata",
            upload_success=False,
            install_success=False,
            is_healthy=False,
            health_error="Not installed",
        )
        diagnostics = service.get_failure_diagnostics()

        # All 5 gates should be in diagnostics
        assert "5 gate(s) failed" in diagnostics
        assert "wheel_build" in diagnostics
        assert "twine_check" in diagnostics
        assert "testpypi_upload" in diagnostics
        assert "testpypi_install" in diagnostics
        assert "doctor_healthy" in diagnostics

        # All should have suggested fixes
        assert diagnostics.count("**Suggested Fix:**") == 5
