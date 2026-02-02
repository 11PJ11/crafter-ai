"""QualityGateService for validating CI/CD quality gates.

This module provides the QualityGateService for validating TestPyPI CI quality gates
including wheel build, twine check, upload, install, and health checks.
"""

from dataclasses import dataclass, field


@dataclass
class GateResult:
    """Result of a single quality gate check.

    Attributes:
        check_name: Name of the quality gate check.
        passed: Whether the check passed.
        message: Description of the result.
        suggested_fix: Suggested fix if the check failed, None if passed.
    """

    check_name: str
    passed: bool
    message: str
    suggested_fix: str | None = None


@dataclass
class QualityGateResult:
    """Aggregated result of all quality gate checks.

    Attributes:
        passed: Whether all checks passed.
        gate_results: List of individual gate results.
        summary: Human-readable summary of the results.
    """

    passed: bool
    gate_results: list[GateResult] = field(default_factory=list)
    summary: str = ""


class QualityGateService:
    """Service for validating TestPyPI CI quality gates.

    This service validates all quality gate requirements for TestPyPI publishing:
    - Wheel build validation
    - Twine check validation
    - TestPyPI upload validation
    - TestPyPI install validation
    - Doctor health check validation
    """

    def __init__(self) -> None:
        """Initialize the QualityGateService."""
        self._gate_results: list[GateResult] = []

    def validate_wheel_build(
        self,
        wheel_exists: bool = False,
        wheel_path: str | None = None,
        build_error: str | None = None,
    ) -> GateResult:
        """Validate that wheel build succeeded.

        Args:
            wheel_exists: Whether the wheel file exists.
            wheel_path: Path to the wheel file.
            build_error: Build error message if any.

        Returns:
            GateResult with pass/fail status and details.
        """
        if build_error:
            return GateResult(
                check_name="wheel_build",
                passed=False,
                message=f"Wheel build failed: {build_error}",
                suggested_fix="Check pyproject.toml for syntax errors. "
                "Ensure all required metadata fields are present. "
                "Run 'python -m build' locally to debug.",
            )

        if not wheel_exists:
            return GateResult(
                check_name="wheel_build",
                passed=False,
                message="Wheel file not found in dist/ directory",
                suggested_fix="Run 'python -m build' to generate the wheel. "
                "Check that hatchling is installed: pip install hatchling",
            )

        return GateResult(
            check_name="wheel_build",
            passed=True,
            message=f"Wheel build successful: {wheel_path or 'dist/*.whl'}",
            suggested_fix=None,
        )

    def validate_twine_check(
        self,
        check_passed: bool = False,
        check_output: str | None = None,
        check_error: str | None = None,
    ) -> GateResult:
        """Validate that twine check passed.

        Args:
            check_passed: Whether twine check passed.
            check_output: Output from twine check.
            check_error: Error message from twine check.

        Returns:
            GateResult with pass/fail status and details.
        """
        if check_error:
            return GateResult(
                check_name="twine_check",
                passed=False,
                message=f"Twine check failed: {check_error}",
                suggested_fix="Run 'twine check dist/*' locally to see detailed errors. "
                "Common issues: invalid long_description format, missing metadata. "
                "Ensure README.md is valid markdown.",
            )

        if not check_passed:
            return GateResult(
                check_name="twine_check",
                passed=False,
                message=f"Twine check failed: {check_output or 'Unknown error'}",
                suggested_fix="Run 'twine check dist/*' locally to debug. "
                "Check pyproject.toml for metadata issues.",
            )

        return GateResult(
            check_name="twine_check",
            passed=True,
            message="Twine check passed: package metadata is valid",
            suggested_fix=None,
        )

    def validate_testpypi_upload(
        self,
        upload_success: bool = False,
        version: str | None = None,
        upload_error: str | None = None,
        retry_count: int = 0,
    ) -> GateResult:
        """Validate that TestPyPI upload succeeded.

        Args:
            upload_success: Whether upload succeeded.
            version: Package version that was uploaded.
            upload_error: Upload error message if any.
            retry_count: Number of retry attempts made.

        Returns:
            GateResult with pass/fail status and details.
        """
        if upload_error:
            retry_msg = f" after {retry_count} retries" if retry_count > 0 else ""
            return GateResult(
                check_name="testpypi_upload",
                passed=False,
                message=f"TestPyPI upload failed{retry_msg}: {upload_error}",
                suggested_fix="Check TestPyPI API token is valid and has upload permissions. "
                "Verify the version doesn't already exist on TestPyPI. "
                "If network error, the workflow will auto-retry with backoff.",
            )

        if not upload_success:
            return GateResult(
                check_name="testpypi_upload",
                passed=False,
                message="TestPyPI upload failed: unknown error",
                suggested_fix="Check GitHub Actions logs for detailed error. "
                "Verify TEST_PYPI_API_TOKEN secret is configured.",
            )

        return GateResult(
            check_name="testpypi_upload",
            passed=True,
            message=f"TestPyPI upload successful: version {version or 'unknown'}",
            suggested_fix=None,
        )

    def validate_testpypi_install(
        self,
        install_success: bool = False,
        version: str | None = None,
        install_error: str | None = None,
        retry_count: int = 0,
    ) -> GateResult:
        """Validate that TestPyPI install succeeded.

        Args:
            install_success: Whether install succeeded.
            version: Package version that was installed.
            install_error: Install error message if any.
            retry_count: Number of retry attempts made.

        Returns:
            GateResult with pass/fail status and details.
        """
        if install_error:
            retry_msg = f" after {retry_count} retries" if retry_count > 0 else ""
            return GateResult(
                check_name="testpypi_install",
                passed=False,
                message=f"TestPyPI install failed{retry_msg}: {install_error}",
                suggested_fix="Wait for TestPyPI index to propagate (may take 1-2 minutes). "
                "Check that all dependencies are available on PyPI. "
                "Verify the version exists on TestPyPI.",
            )

        if not install_success:
            return GateResult(
                check_name="testpypi_install",
                passed=False,
                message="TestPyPI install failed: unknown error",
                suggested_fix="Check GitHub Actions logs for detailed error. "
                "Try installing manually: pipx install crafter-ai==VERSION "
                "--pip-args='--index-url https://test.pypi.org/simple/ "
                "--extra-index-url https://pypi.org/simple/'",
            )

        return GateResult(
            check_name="testpypi_install",
            passed=True,
            message=f"TestPyPI install successful: version {version or 'unknown'}",
            suggested_fix=None,
        )

    def validate_doctor_healthy(
        self,
        is_healthy: bool = False,
        health_output: str | None = None,
        health_error: str | None = None,
    ) -> GateResult:
        """Validate that doctor health check passed.

        Args:
            is_healthy: Whether the health check passed.
            health_output: Output from health check.
            health_error: Error message from health check.

        Returns:
            GateResult with pass/fail status and details.
        """
        if health_error:
            return GateResult(
                check_name="doctor_healthy",
                passed=False,
                message=f"Doctor health check failed: {health_error}",
                suggested_fix="Run 'crafter-ai doctor' locally to see detailed health status. "
                "Check that all required components are installed correctly.",
            )

        if not is_healthy:
            return GateResult(
                check_name="doctor_healthy",
                passed=False,
                message=f"Doctor health check unhealthy: {health_output or 'Unknown issue'}",
                suggested_fix="Run 'crafter-ai doctor' to diagnose issues. "
                "Check ~/.claude/ directory has proper permissions and structure.",
            )

        return GateResult(
            check_name="doctor_healthy",
            passed=True,
            message="Doctor health check passed: all components healthy",
            suggested_fix=None,
        )

    def validate_all(
        self,
        wheel_exists: bool = False,
        wheel_path: str | None = None,
        build_error: str | None = None,
        twine_check_passed: bool = False,
        twine_check_output: str | None = None,
        twine_check_error: str | None = None,
        upload_success: bool = False,
        upload_version: str | None = None,
        upload_error: str | None = None,
        upload_retry_count: int = 0,
        install_success: bool = False,
        install_version: str | None = None,
        install_error: str | None = None,
        install_retry_count: int = 0,
        is_healthy: bool = False,
        health_output: str | None = None,
        health_error: str | None = None,
    ) -> QualityGateResult:
        """Run all quality gate validations.

        Args:
            wheel_exists: Whether wheel file exists.
            wheel_path: Path to wheel file.
            build_error: Build error if any.
            twine_check_passed: Whether twine check passed.
            twine_check_output: Twine check output.
            twine_check_error: Twine check error if any.
            upload_success: Whether upload succeeded.
            upload_version: Uploaded version.
            upload_error: Upload error if any.
            upload_retry_count: Number of upload retries.
            install_success: Whether install succeeded.
            install_version: Installed version.
            install_error: Install error if any.
            install_retry_count: Number of install retries.
            is_healthy: Whether health check passed.
            health_output: Health check output.
            health_error: Health check error if any.

        Returns:
            QualityGateResult with aggregated results.
        """
        self._gate_results = []

        # Run all validations
        self._gate_results.append(
            self.validate_wheel_build(wheel_exists, wheel_path, build_error)
        )
        self._gate_results.append(
            self.validate_twine_check(
                twine_check_passed, twine_check_output, twine_check_error
            )
        )
        self._gate_results.append(
            self.validate_testpypi_upload(
                upload_success, upload_version, upload_error, upload_retry_count
            )
        )
        self._gate_results.append(
            self.validate_testpypi_install(
                install_success, install_version, install_error, install_retry_count
            )
        )
        self._gate_results.append(
            self.validate_doctor_healthy(is_healthy, health_output, health_error)
        )

        # Calculate overall result
        all_passed = all(result.passed for result in self._gate_results)
        passed_count = sum(1 for result in self._gate_results if result.passed)
        total_count = len(self._gate_results)

        if all_passed:
            summary = f"All {total_count} quality gates passed"
        else:
            failed_gates = [r.check_name for r in self._gate_results if not r.passed]
            summary = (
                f"{passed_count}/{total_count} quality gates passed. "
                f"Failed: {', '.join(failed_gates)}"
            )

        return QualityGateResult(
            passed=all_passed,
            gate_results=self._gate_results.copy(),
            summary=summary,
        )

    def get_failure_diagnostics(self) -> str:
        """Get detailed failure diagnostics for failed gates.

        Returns:
            Formatted string with failure details and suggested fixes.
        """
        if not self._gate_results:
            return "No quality gate results available. Run validate_all() first."

        failed_results = [r for r in self._gate_results if not r.passed]

        if not failed_results:
            return "All quality gates passed. No failures to diagnose."

        lines = [
            "## Quality Gate Failures",
            "",
            f"**{len(failed_results)} gate(s) failed:**",
            "",
        ]

        for result in failed_results:
            lines.extend(
                [
                    f"### {result.check_name}",
                    "",
                    "**Status:** FAILED",
                    f"**Message:** {result.message}",
                    "",
                    "**Suggested Fix:**",
                    f"{result.suggested_fix or 'No specific fix available.'}",
                    "",
                ]
            )

        return "\n".join(lines)
