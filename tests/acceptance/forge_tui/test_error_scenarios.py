"""Error scenario E2E acceptance tests for the Forge TUI redesign (Phase 08).

These tests define the TARGET error-handling behavior for build and install
commands as specified in Luna's UX design:
  docs/ux/modern-cli-installer/journey-forge-tui-visual.md
  docs/ux/modern-cli-installer/journey-forge-tui.feature (lines 172-207)

EXPECTED STATE: These tests FAIL against the current implementation.
They define the error display patterns that Phase 08 must implement.

Making these tests pass IS the Phase 08 implementation work.

Design source: journey-forge-tui.feature lines 172-207 (error scenarios)
Design system: journey-forge-tui-visual.md (error mockups)
"""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from typer.testing import CliRunner

from crafter_ai.cli import app
from crafter_ai.installer.domain.candidate_version import BumpType, CandidateVersion
from crafter_ai.installer.domain.check_result import CheckResult, CheckSeverity
from crafter_ai.installer.domain.health_result import HealthStatus
from crafter_ai.installer.services.build_service import BuildResult
from crafter_ai.installer.services.install_service import InstallPhase, InstallResult


# Box-drawing characters that MUST NOT appear in the redesigned TUI output.
FORBIDDEN_BORDER_CHARS = set("╭╮╰╯┏┓┗┛━─┃│┡┩╇╈┼┤├")


# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture
def runner() -> CliRunner:
    """CLI test runner with mixed stdout/stderr capture."""
    return CliRunner(mix_stderr=False)


@pytest.fixture
def candidate_version() -> CandidateVersion:
    """Version bump: 0.1.0 -> 0.2.0 (minor)."""
    return CandidateVersion(
        current_version="0.1.0",
        bump_type=BumpType.MINOR,
        next_version="0.2.0",
        commit_messages=["feat: add new feature"],
        is_prerelease=False,
        prerelease_suffix=None,
    )


@pytest.fixture
def build_preflight_mixed_results() -> list[CheckResult]:
    """Build pre-flight with 2 failures + 2 passes + 1 warning.

    Matches Luna's Step 08-01 mockup:
      - pyproject.toml not found (BLOCKING, FAIL)
      - Build toolchain ready (BLOCKING, PASS)
      - Source directory not found (BLOCKING, FAIL)
      - Uncommitted changes detected (WARNING)
      - Version available for release (WARNING, PASS)
    """
    return [
        CheckResult(
            id="pyproject",
            name="pyproject.toml exists",
            passed=False,
            severity=CheckSeverity.BLOCKING,
            message="pyproject.toml not found",
            remediation="Create pyproject.toml in project root",
        ),
        CheckResult(
            id="build_toolchain",
            name="Build toolchain",
            passed=True,
            severity=CheckSeverity.BLOCKING,
            message="Build toolchain ready",
        ),
        CheckResult(
            id="src_directory",
            name="Source directory",
            passed=False,
            severity=CheckSeverity.BLOCKING,
            message="Source directory not found",
            remediation="Create a src/ directory with your package structure",
        ),
        CheckResult(
            id="git_clean",
            name="Git working tree clean",
            passed=True,
            severity=CheckSeverity.WARNING,
            message="Uncommitted changes detected",
        ),
        CheckResult(
            id="version_available",
            name="Version available",
            passed=True,
            severity=CheckSeverity.WARNING,
            message="Version available for release",
        ),
    ]


@pytest.fixture
def failed_build_result_preflight(
    build_preflight_mixed_results: list[CheckResult],
) -> BuildResult:
    """Build result that failed due to pre-flight blocking checks."""
    return BuildResult(
        success=False,
        wheel_path=None,
        version=None,
        pre_flight_results=build_preflight_mixed_results,
        validation_result=None,
        error_message="Pre-flight checks failed with blocking errors",
    )


@pytest.fixture
def build_preflight_all_pass() -> list[CheckResult]:
    """Build pre-flight where all checks pass."""
    return [
        CheckResult(
            id="pyproject",
            name="pyproject.toml exists",
            passed=True,
            severity=CheckSeverity.BLOCKING,
            message="pyproject.toml found",
        ),
        CheckResult(
            id="build_toolchain",
            name="Build toolchain",
            passed=True,
            severity=CheckSeverity.BLOCKING,
            message="Build toolchain ready",
        ),
        CheckResult(
            id="src_directory",
            name="Source directory",
            passed=True,
            severity=CheckSeverity.BLOCKING,
            message="Source directory found",
        ),
        CheckResult(
            id="git_clean",
            name="Git working tree clean",
            passed=True,
            severity=CheckSeverity.WARNING,
            message="Git status clean",
        ),
        CheckResult(
            id="version_available",
            name="Version available",
            passed=True,
            severity=CheckSeverity.WARNING,
            message="Version available for release",
        ),
    ]


@pytest.fixture
def failed_build_result_compilation(
    build_preflight_all_pass: list[CheckResult],
) -> BuildResult:
    """Build result that failed during compilation (pre-flight passed)."""
    return BuildResult(
        success=False,
        wheel_path=None,
        version=None,
        pre_flight_results=build_preflight_all_pass,
        validation_result=None,
        error_message="Invalid package metadata in pyproject.toml",
    )


@pytest.fixture
def install_preflight_mixed_results() -> list[CheckResult]:
    """Install pre-flight with 2 failures + 1 pass.

    Matches Luna's Step 08-02 mockup:
      - No wheel file found in dist/ (BLOCKING, FAIL)
      - pipx is not installed (BLOCKING, FAIL)
      - Install path writable (BLOCKING, PASS)
    """
    return [
        CheckResult(
            id="wheel_exists",
            name="Wheel file exists",
            passed=False,
            severity=CheckSeverity.BLOCKING,
            message="No wheel file found in dist/",
            remediation="Run 'crafter-ai forge build' first",
        ),
        CheckResult(
            id="pipx_available",
            name="pipx available",
            passed=False,
            severity=CheckSeverity.BLOCKING,
            message="pipx is not installed",
            remediation="pip install pipx && pipx ensurepath",
        ),
        CheckResult(
            id="install_path",
            name="Install path writable",
            passed=True,
            severity=CheckSeverity.BLOCKING,
            message="Install path writable",
        ),
    ]


@pytest.fixture
def install_preflight_all_pass() -> list[CheckResult]:
    """Install pre-flight where all checks pass."""
    return [
        CheckResult(
            id="wheel_exists",
            name="Wheel file exists",
            passed=True,
            severity=CheckSeverity.BLOCKING,
            message="Wheel file found",
        ),
        CheckResult(
            id="wheel_format",
            name="Wheel format valid",
            passed=True,
            severity=CheckSeverity.BLOCKING,
            message="Wheel format valid",
        ),
        CheckResult(
            id="pipx_available",
            name="pipx available",
            passed=True,
            severity=CheckSeverity.BLOCKING,
            message="pipx environment ready",
        ),
        CheckResult(
            id="install_path",
            name="Install path writable",
            passed=True,
            severity=CheckSeverity.BLOCKING,
            message="Install path writable",
        ),
    ]


@pytest.fixture
def mock_wheel_path(tmp_path: Path) -> Path:
    """Create a real wheel file on disk so path.exists() passes."""
    wheel_file = tmp_path / "crafter_ai-0.2.0-py3-none-any.whl"
    wheel_file.write_bytes(b"fake wheel content for testing")
    return wheel_file


@pytest.fixture
def failed_install_result() -> InstallResult:
    """Install result that failed during pipx install."""
    return InstallResult(
        success=False,
        version=None,
        install_path=None,
        phases_completed=[
            InstallPhase.PREFLIGHT,
            InstallPhase.READINESS,
            InstallPhase.BACKUP,
        ],
        error_message="pipx install failed: dependency conflict",
        health_status=None,
        verification_warnings=[],
    )


@pytest.fixture
def degraded_install_result() -> InstallResult:
    """Install result that succeeded but with DEGRADED health."""
    return InstallResult(
        success=True,
        version="0.2.0",
        install_path=Path("/usr/local/bin/crafter-ai"),
        phases_completed=[
            InstallPhase.PREFLIGHT,
            InstallPhase.READINESS,
            InstallPhase.BACKUP,
            InstallPhase.INSTALL,
            InstallPhase.VERIFICATION,
        ],
        error_message=None,
        health_status=HealthStatus.DEGRADED,
        verification_warnings=["Some optional modules not found"],
    )


# ============================================================================
# Helpers
# ============================================================================


def invoke_build(
    runner: CliRunner,
    candidate_version: CandidateVersion,
    build_result: BuildResult,
) -> tuple[str, int]:
    """Run 'forge build --no-prompt' and return (output, exit_code).

    Mocks the build service so the test runs fast and deterministic.
    """
    with (
        patch(
            "crafter_ai.installer.cli.forge_build.create_build_service"
        ) as mock_build_factory,
        patch.dict("os.environ", {"CI": ""}, clear=False),
    ):
        mock_build_svc = MagicMock()
        mock_build_svc.execute.return_value = build_result
        mock_build_svc.determine_version.return_value = candidate_version
        mock_build_factory.return_value = mock_build_svc

        result = runner.invoke(app, ["forge", "build", "--no-prompt"])

    return result.output, result.exit_code


def invoke_install(
    runner: CliRunner,
    mock_wheel_path: Path,
    install_preflight_results: list[CheckResult],
    install_result: InstallResult,
) -> tuple[str, int]:
    """Run 'forge install --wheel <path> --no-prompt' and return (output, exit_code).

    Mocks the install service and pre-flight checks.
    """
    mock_report = MagicMock()
    mock_report.generate.return_value = MagicMock()
    mock_report.format_console.return_value = ""

    with (
        patch(
            "crafter_ai.installer.cli.forge_install.create_install_service"
        ) as mock_install_factory,
        patch(
            "crafter_ai.installer.cli.forge_install.run_pre_flight_checks"
        ) as mock_install_preflight,
        patch(
            "crafter_ai.installer.cli.forge_install.ReleaseReportService"
        ) as mock_report_service,
        patch.dict("os.environ", {"CI": ""}, clear=False),
    ):
        mock_install_svc = MagicMock()
        mock_install_svc.install.return_value = install_result
        mock_install_factory.return_value = mock_install_svc

        mock_install_preflight.return_value = install_preflight_results

        mock_report_service.return_value = mock_report

        result = runner.invoke(
            app,
            ["forge", "install", "--wheel", str(mock_wheel_path), "--no-prompt"],
        )

    return result.output, result.exit_code


# ============================================================================
# 08-01: Blocking Build Pre-flight Failure
# ============================================================================


@pytest.mark.e2e
class TestBlockingBuildPreFlight:
    """Blocking build pre-flight failure display.

    Luna's Step 08-01: When pre-flight has blocking failures, ALL checks
    still display (pass and fail mixed), then a summary line shows
    "Build blocked: N checks failed" in red, followed by each failure
    repeated with remediation. No panels or boxes. Exit code 1.

    Design source: journey-forge-tui.feature lines 172-181
    Design visual: journey-forge-tui-visual.md Step 08-01
    """

    def test_exit_code_is_1(
        self,
        runner: CliRunner,
        candidate_version: CandidateVersion,
        failed_build_result_preflight: BuildResult,
    ) -> None:
        """Build with blocking pre-flight failures exits with code 1."""
        _output, exit_code = invoke_build(
            runner, candidate_version, failed_build_result_preflight
        )
        assert exit_code == 1, f"Expected exit code 1, got {exit_code}"

    def test_build_header_still_appears(
        self,
        runner: CliRunner,
        candidate_version: CandidateVersion,
        failed_build_result_preflight: BuildResult,
    ) -> None:
        """Build header with hammer emoji appears even on failure."""
        output, _code = invoke_build(
            runner, candidate_version, failed_build_result_preflight
        )
        assert "\U0001f528" in output, "Missing hammer emoji in build header"
        assert "Building crafter-ai" in output

    def test_all_checks_display_both_pass_and_fail(
        self,
        runner: CliRunner,
        candidate_version: CandidateVersion,
        failed_build_result_preflight: BuildResult,
    ) -> None:
        """All checks display regardless of pass/fail status.

        Luna's rule: 'all checks still display (both passed and failed)'.
        """
        output, _code = invoke_build(
            runner, candidate_version, failed_build_result_preflight
        )

        # Failed checks
        assert "pyproject.toml not found" in output
        assert "Source directory not found" in output

        # Passed checks still visible
        assert "Build toolchain ready" in output
        assert "Version available for release" in output

    def test_failed_checks_show_red_x_emoji(
        self,
        runner: CliRunner,
        candidate_version: CandidateVersion,
        failed_build_result_preflight: BuildResult,
    ) -> None:
        """Failed blocking checks display with red X emoji."""
        output, _code = invoke_build(
            runner, candidate_version, failed_build_result_preflight
        )
        assert "\u274c" in output, "Missing red X emoji for failed checks"

    def test_passed_checks_show_green_checkmark(
        self,
        runner: CliRunner,
        candidate_version: CandidateVersion,
        failed_build_result_preflight: BuildResult,
    ) -> None:
        """Passed checks display with green checkmark emoji."""
        output, _code = invoke_build(
            runner, candidate_version, failed_build_result_preflight
        )
        assert "\u2705" in output, "Missing green checkmark for passed checks"

    def test_summary_line_shows_build_blocked_with_count(
        self,
        runner: CliRunner,
        candidate_version: CandidateVersion,
        failed_build_result_preflight: BuildResult,
    ) -> None:
        """Summary line: 'Build blocked: 2 checks failed'.

        Luna's rule: summary line in red with exact failure count.
        """
        output, _code = invoke_build(
            runner, candidate_version, failed_build_result_preflight
        )
        assert "Build blocked: 2 checks failed" in output, (
            f"Missing summary line 'Build blocked: 2 checks failed'.\nOutput:\n{output}"
        )

    def test_failures_repeated_below_with_remediation(
        self,
        runner: CliRunner,
        candidate_version: CandidateVersion,
        failed_build_result_preflight: BuildResult,
    ) -> None:
        """Each failure is repeated below the summary with Fix: remediation.

        Luna's design: failures appear twice; once in the check list,
        then again below the summary with 'Fix:' remediation lines.
        """
        output, _code = invoke_build(
            runner, candidate_version, failed_build_result_preflight
        )

        # Summary should appear before the repeated failures
        summary_pos = output.find("Build blocked")
        assert summary_pos != -1, "Missing 'Build blocked' summary line"

        # After the summary, failures should be repeated with remediation
        after_summary = output[summary_pos:]
        assert "pyproject.toml not found" in after_summary, (
            "pyproject.toml failure not repeated after summary"
        )
        assert "Source directory not found" in after_summary, (
            "Source directory failure not repeated after summary"
        )

    def test_remediation_fix_lines_present(
        self,
        runner: CliRunner,
        candidate_version: CandidateVersion,
        failed_build_result_preflight: BuildResult,
    ) -> None:
        """Each repeated failure has a 'Fix:' line with remediation text."""
        output, _code = invoke_build(
            runner, candidate_version, failed_build_result_preflight
        )

        assert "Fix: Create pyproject.toml in project root" in output, (
            "Missing remediation for pyproject.toml failure"
        )
        assert "Fix: Create a src/ directory with your package structure" in output, (
            "Missing remediation for source directory failure"
        )

    def test_no_preflight_passed_line(
        self,
        runner: CliRunner,
        candidate_version: CandidateVersion,
        failed_build_result_preflight: BuildResult,
    ) -> None:
        """When pre-flight has blocking failures, 'Pre-flight passed' must NOT appear."""
        output, _code = invoke_build(
            runner, candidate_version, failed_build_result_preflight
        )
        assert "Pre-flight passed" not in output, (
            "'Pre-flight passed' should not appear when blocking checks fail"
        )

    def test_no_border_characters(
        self,
        runner: CliRunner,
        candidate_version: CandidateVersion,
        failed_build_result_preflight: BuildResult,
    ) -> None:
        """No Rich Table or Panel borders in error output.

        Luna's rule: 'no table or panel is used for error display'.
        """
        output, _code = invoke_build(
            runner, candidate_version, failed_build_result_preflight
        )
        border_chars_found = FORBIDDEN_BORDER_CHARS.intersection(set(output))
        assert not border_chars_found, (
            f"Output contains forbidden border characters: {border_chars_found}\n"
            "Error output must use plain emoji-based display, no panels or tables."
        )


def invoke_install_preflight_only(
    runner: CliRunner,
    mock_wheel_path: Path,
    install_preflight_results: list[CheckResult],
) -> tuple[str, int]:
    """Run 'forge install --wheel <path> --no-prompt' for pre-flight-only scenarios.

    Like invoke_install but does NOT require an install_result parameter,
    since install should never be called when pre-flight blocks.
    """
    mock_report = MagicMock()
    mock_report.generate.return_value = MagicMock()
    mock_report.format_console.return_value = ""

    with (
        patch(
            "crafter_ai.installer.cli.forge_install.create_install_service"
        ) as mock_install_factory,
        patch(
            "crafter_ai.installer.cli.forge_install.run_pre_flight_checks"
        ) as mock_install_preflight,
        patch(
            "crafter_ai.installer.cli.forge_install.ReleaseReportService"
        ) as mock_report_service,
        patch.dict("os.environ", {"CI": ""}, clear=False),
    ):
        mock_install_svc = MagicMock()
        mock_install_factory.return_value = mock_install_svc
        mock_install_preflight.return_value = install_preflight_results
        mock_report_service.return_value = mock_report

        result = runner.invoke(
            app,
            ["forge", "install", "--wheel", str(mock_wheel_path), "--no-prompt"],
        )

    return result.output, result.exit_code


# ============================================================================
# 08-02: Blocking Install Pre-flight Failure
# ============================================================================


@pytest.mark.e2e
class TestBlockingInstallPreFlight:
    """Blocking install pre-flight failure display.

    Luna's Step 08-02: Same pattern as build blocking failure but for
    'forge install'. All checks display, summary line with count,
    failures repeated with remediation. Exit code 1.

    Design source: journey-forge-tui.feature lines 183-189
    Design visual: journey-forge-tui-visual.md Step 08-02
    """

    def test_exit_code_is_1(
        self,
        runner: CliRunner,
        mock_wheel_path: Path,
        install_preflight_mixed_results: list[CheckResult],
    ) -> None:
        """Install with blocking pre-flight failures exits with code 1."""
        _output, exit_code = invoke_install_preflight_only(
            runner, mock_wheel_path, install_preflight_mixed_results
        )
        assert exit_code == 1, f"Expected exit code 1, got {exit_code}"

    def test_install_header_still_appears(
        self,
        runner: CliRunner,
        mock_wheel_path: Path,
        install_preflight_mixed_results: list[CheckResult],
    ) -> None:
        """Install header with package emoji appears even on failure."""
        output, _code = invoke_install_preflight_only(
            runner, mock_wheel_path, install_preflight_mixed_results
        )
        assert "\U0001f4e6" in output, "Missing package emoji in install header"
        assert "Installing crafter-ai" in output

    def test_all_checks_display_both_pass_and_fail(
        self,
        runner: CliRunner,
        mock_wheel_path: Path,
        install_preflight_mixed_results: list[CheckResult],
    ) -> None:
        """All checks display regardless of pass/fail status."""
        output, _code = invoke_install_preflight_only(
            runner, mock_wheel_path, install_preflight_mixed_results
        )

        # Failed checks
        assert "No wheel file found in dist/" in output
        assert "pipx is not installed" in output

        # Passed check still visible
        assert "Install path writable" in output

    def test_summary_line_shows_install_blocked_with_count(
        self,
        runner: CliRunner,
        mock_wheel_path: Path,
        install_preflight_mixed_results: list[CheckResult],
    ) -> None:
        """Summary line: 'Install blocked: 2 checks failed'.

        Luna's rule: same pattern as build, with 'Install blocked:' prefix.
        """
        output, _code = invoke_install_preflight_only(
            runner, mock_wheel_path, install_preflight_mixed_results
        )
        assert "Install blocked: 2 checks failed" in output, (
            "Missing summary line 'Install blocked: 2 checks failed'.\n"
            f"Output:\n{output}"
        )

    def test_remediation_fix_lines_present(
        self,
        runner: CliRunner,
        mock_wheel_path: Path,
        install_preflight_mixed_results: list[CheckResult],
    ) -> None:
        """Each repeated failure has a 'Fix:' line with remediation text."""
        output, _code = invoke_install_preflight_only(
            runner, mock_wheel_path, install_preflight_mixed_results
        )
        assert "Fix: Run 'crafter-ai forge build' first" in output, (
            "Missing remediation for wheel file failure"
        )
        assert "Fix: pip install pipx && pipx ensurepath" in output, (
            "Missing remediation for pipx failure"
        )

    def test_no_border_characters(
        self,
        runner: CliRunner,
        mock_wheel_path: Path,
        install_preflight_mixed_results: list[CheckResult],
    ) -> None:
        """No Rich Table or Panel borders in error output."""
        output, _code = invoke_install_preflight_only(
            runner, mock_wheel_path, install_preflight_mixed_results
        )
        border_chars_found = FORBIDDEN_BORDER_CHARS.intersection(set(output))
        assert not border_chars_found, (
            f"Output contains forbidden border characters: {border_chars_found}"
        )

    def test_failed_checks_show_red_x_emoji(
        self,
        runner: CliRunner,
        mock_wheel_path: Path,
        install_preflight_mixed_results: list[CheckResult],
    ) -> None:
        """Failed blocking checks display with red X emoji."""
        output, _code = invoke_install_preflight_only(
            runner, mock_wheel_path, install_preflight_mixed_results
        )
        assert "\u274c" in output, "Missing red X emoji for failed checks"

    def test_passed_checks_show_green_checkmark(
        self,
        runner: CliRunner,
        mock_wheel_path: Path,
        install_preflight_mixed_results: list[CheckResult],
    ) -> None:
        """Passed checks display with green checkmark emoji."""
        output, _code = invoke_install_preflight_only(
            runner, mock_wheel_path, install_preflight_mixed_results
        )
        assert "\u2705" in output, "Missing green checkmark for passed checks"

    def test_no_preflight_passed_line(
        self,
        runner: CliRunner,
        mock_wheel_path: Path,
        install_preflight_mixed_results: list[CheckResult],
    ) -> None:
        """When pre-flight has blocking failures, 'Pre-flight passed' must NOT appear."""
        output, _code = invoke_install_preflight_only(
            runner, mock_wheel_path, install_preflight_mixed_results
        )
        assert "Pre-flight passed" not in output, (
            "'Pre-flight passed' should not appear when blocking checks fail"
        )


# ============================================================================
# 08-03: Build Compilation Failure
# ============================================================================


@pytest.mark.e2e
class TestBuildCompilationFailure:
    """Build compilation failure display (pre-flight passes, build fails).

    Luna's Step 08-03: Pre-flight passes, version displays, then build
    fails. Output shows 'Build failed' with red X, followed by 'Error:'
    and 'Fix:' lines. Exit code 1.

    Design source: journey-forge-tui.feature lines 191-196
    Design visual: journey-forge-tui-visual.md Step 08-03
    """

    def test_exit_code_is_1(
        self,
        runner: CliRunner,
        candidate_version: CandidateVersion,
        failed_build_result_compilation: BuildResult,
    ) -> None:
        """Build compilation failure exits with code 1."""
        _output, exit_code = invoke_build(
            runner, candidate_version, failed_build_result_compilation
        )
        assert exit_code == 1, f"Expected exit code 1, got {exit_code}"

    def test_preflight_passed_still_shows(
        self,
        runner: CliRunner,
        candidate_version: CandidateVersion,
        failed_build_result_compilation: BuildResult,
    ) -> None:
        """Pre-flight checks pass and are displayed before the failure."""
        output, _code = invoke_build(
            runner, candidate_version, failed_build_result_compilation
        )
        assert "Pre-flight passed" in output, (
            "Pre-flight passed should appear before the build failure"
        )

    def test_version_display_shows_before_failure(
        self,
        runner: CliRunner,
        candidate_version: CandidateVersion,
        failed_build_result_compilation: BuildResult,
    ) -> None:
        """Version display appears between pre-flight and failure."""
        output, _code = invoke_build(
            runner, candidate_version, failed_build_result_compilation
        )
        assert "\U0001f4d0" in output, "Missing ruler emoji for version section"
        assert "0.1.0" in output
        assert "0.2.0" in output

    def test_build_failed_line_with_red_x(
        self,
        runner: CliRunner,
        candidate_version: CandidateVersion,
        failed_build_result_compilation: BuildResult,
    ) -> None:
        """Failure shows 'Build failed' with red X emoji.

        Luna's design: spinner resolves to 'Build failed' with red X.
        """
        output, _code = invoke_build(
            runner, candidate_version, failed_build_result_compilation
        )
        assert "\u274c" in output, "Missing red X emoji for build failure"
        assert "Build failed" in output, (
            f"Missing 'Build failed' line.\nOutput:\n{output}"
        )

    def test_error_line_shows_failure_reason(
        self,
        runner: CliRunner,
        candidate_version: CandidateVersion,
        failed_build_result_compilation: BuildResult,
    ) -> None:
        """An 'Error:' line shows the specific failure reason.

        Luna's design: 'Error: Invalid package metadata in pyproject.toml'
        """
        output, _code = invoke_build(
            runner, candidate_version, failed_build_result_compilation
        )
        assert "Error:" in output, "Missing 'Error:' label in failure output"
        assert "Invalid package metadata in pyproject.toml" in output, (
            "Missing specific error message"
        )

    def test_fix_line_shows_remediation(
        self,
        runner: CliRunner,
        candidate_version: CandidateVersion,
        failed_build_result_compilation: BuildResult,
    ) -> None:
        """A 'Fix:' line shows remediation guidance.

        Luna's design: 'Fix: Check [project] section in pyproject.toml'
        """
        output, _code = invoke_build(
            runner, candidate_version, failed_build_result_compilation
        )
        assert "Fix:" in output, (
            f"Missing 'Fix:' remediation line for build failure.\nOutput:\n{output}"
        )

    def test_failure_appears_after_version_display(
        self,
        runner: CliRunner,
        candidate_version: CandidateVersion,
        failed_build_result_compilation: BuildResult,
    ) -> None:
        """Build failure appears after version display in output stream."""
        output, _code = invoke_build(
            runner, candidate_version, failed_build_result_compilation
        )

        version_pos = output.find("0.2.0")
        failure_pos = output.find("Build failed")

        assert version_pos != -1, "Version not found in output"
        assert failure_pos != -1, "Build failed not found in output"
        assert failure_pos > version_pos, (
            "'Build failed' should appear after version display"
        )

    def test_no_border_characters(
        self,
        runner: CliRunner,
        candidate_version: CandidateVersion,
        failed_build_result_compilation: BuildResult,
    ) -> None:
        """No Rich Table or Panel borders in error output."""
        output, _code = invoke_build(
            runner, candidate_version, failed_build_result_compilation
        )
        border_chars_found = FORBIDDEN_BORDER_CHARS.intersection(set(output))
        assert not border_chars_found, (
            f"Output contains forbidden border characters: {border_chars_found}"
        )


# ============================================================================
# 08-04: Install Failure (pipx error)
# ============================================================================


@pytest.mark.e2e
class TestInstallFailure:
    """Install failure display (pre-flight passes, pipx install fails).

    Luna's Step 08-04: Pre-flight passes, backup skip shown, then install
    fails. Output shows 'Install failed' with red X, followed by 'Error:'
    line. Exit code 1.

    Design source: journey-forge-tui.feature lines 198-203
    Design visual: journey-forge-tui-visual.md Step 08-04
    """

    def test_exit_code_is_1(
        self,
        runner: CliRunner,
        mock_wheel_path: Path,
        install_preflight_all_pass: list[CheckResult],
        failed_install_result: InstallResult,
    ) -> None:
        """Install failure exits with code 1."""
        _output, exit_code = invoke_install(
            runner, mock_wheel_path, install_preflight_all_pass, failed_install_result
        )
        assert exit_code == 1, f"Expected exit code 1, got {exit_code}"

    def test_preflight_passed_shows(
        self,
        runner: CliRunner,
        mock_wheel_path: Path,
        install_preflight_all_pass: list[CheckResult],
        failed_install_result: InstallResult,
    ) -> None:
        """Pre-flight checks pass and display before the failure."""
        output, _code = invoke_install(
            runner, mock_wheel_path, install_preflight_all_pass, failed_install_result
        )
        assert "Pre-flight passed" in output

    def test_backup_skip_shows_before_failure(
        self,
        runner: CliRunner,
        mock_wheel_path: Path,
        install_preflight_all_pass: list[CheckResult],
        failed_install_result: InstallResult,
    ) -> None:
        """Fresh install backup skip message appears before the failure."""
        output, _code = invoke_install(
            runner, mock_wheel_path, install_preflight_all_pass, failed_install_result
        )
        assert "Fresh install, skipping backup" in output

    def test_install_failed_line_with_red_x(
        self,
        runner: CliRunner,
        mock_wheel_path: Path,
        install_preflight_all_pass: list[CheckResult],
        failed_install_result: InstallResult,
    ) -> None:
        """Failure shows 'Installation failed' with red X emoji.

        Luna's design: spinner resolves to 'Installation failed' with red X.
        Visual mockup line 243: 'Installation failed'
        YAML spec line 315: 'Installation failed'
        Feature spec line 204: 'the spinner resolves to "Installation failed"'
        """
        output, _code = invoke_install(
            runner, mock_wheel_path, install_preflight_all_pass, failed_install_result
        )
        assert "\u274c" in output, "Missing red X emoji for install failure"
        assert "Installation failed" in output, (
            f"Missing 'Installation failed' line.\nOutput:\n{output}"
        )

    def test_error_line_shows_failure_reason(
        self,
        runner: CliRunner,
        mock_wheel_path: Path,
        install_preflight_all_pass: list[CheckResult],
        failed_install_result: InstallResult,
    ) -> None:
        """An 'Error:' line shows the specific failure reason.

        Luna's design: 'Error: pipx install failed: dependency conflict'
        """
        output, _code = invoke_install(
            runner, mock_wheel_path, install_preflight_all_pass, failed_install_result
        )
        assert "Error:" in output, "Missing 'Error:' label in failure output"
        assert "pipx install failed: dependency conflict" in output, (
            "Missing specific error message"
        )

    def test_fix_line_shows_remediation(
        self,
        runner: CliRunner,
        mock_wheel_path: Path,
        install_preflight_all_pass: list[CheckResult],
        failed_install_result: InstallResult,
    ) -> None:
        """A 'Fix:' line shows remediation guidance if available.

        Luna's design: 'Fix: Try pipx install --force or check dependency versions'
        Feature spec line 206: 'a Fix: line shows remediation if available'
        """
        output, _code = invoke_install(
            runner, mock_wheel_path, install_preflight_all_pass, failed_install_result
        )
        assert "Fix:" in output, (
            f"Missing 'Fix:' remediation line for install failure.\nOutput:\n{output}"
        )

    def test_no_border_characters(
        self,
        runner: CliRunner,
        mock_wheel_path: Path,
        install_preflight_all_pass: list[CheckResult],
        failed_install_result: InstallResult,
    ) -> None:
        """No Rich Table or Panel borders in error output."""
        output, _code = invoke_install(
            runner, mock_wheel_path, install_preflight_all_pass, failed_install_result
        )
        border_chars_found = FORBIDDEN_BORDER_CHARS.intersection(set(output))
        assert not border_chars_found, (
            f"Output contains forbidden border characters: {border_chars_found}"
        )


# ============================================================================
# 08-05: Degraded Health Warning
# ============================================================================


@pytest.mark.e2e
class TestDegradedHealth:
    """Degraded health warning display (install succeeds, health is DEGRADED).

    Luna's Step 08-05: Installation completes, health verification shows
    mixed results with warning emoji for degraded checks. Celebration
    downgrades from party popper to warning emoji. Message changes from
    'installed and healthy!' to 'installed with warnings'. Exit code 0.

    Design source: journey-forge-tui.feature (degraded health scenario)
    Design visual: journey-forge-tui-visual.md Step 08-05
    """

    def test_exit_code_is_0(
        self,
        runner: CliRunner,
        mock_wheel_path: Path,
        install_preflight_all_pass: list[CheckResult],
        degraded_install_result: InstallResult,
    ) -> None:
        """Degraded health install exits with code 0 (still successful)."""
        _output, exit_code = invoke_install(
            runner, mock_wheel_path, install_preflight_all_pass, degraded_install_result
        )
        assert exit_code == 0, f"Expected exit code 0, got {exit_code}"

    def test_health_verification_section_appears(
        self,
        runner: CliRunner,
        mock_wheel_path: Path,
        install_preflight_all_pass: list[CheckResult],
        degraded_install_result: InstallResult,
    ) -> None:
        """Health verification section with stethoscope emoji appears."""
        output, _code = invoke_install(
            runner, mock_wheel_path, install_preflight_all_pass, degraded_install_result
        )
        assert "\U0001fa7a" in output, "Missing stethoscope emoji for health check"
        assert "Verifying installation" in output

    def test_cli_version_check_passes(
        self,
        runner: CliRunner,
        mock_wheel_path: Path,
        install_preflight_all_pass: list[CheckResult],
        degraded_install_result: InstallResult,
    ) -> None:
        """CLI --version check shows as passed with checkmark."""
        output, _code = invoke_install(
            runner, mock_wheel_path, install_preflight_all_pass, degraded_install_result
        )
        assert "CLI responds to --version" in output

    def test_degraded_check_shows_warning_emoji(
        self,
        runner: CliRunner,
        mock_wheel_path: Path,
        install_preflight_all_pass: list[CheckResult],
        degraded_install_result: InstallResult,
    ) -> None:
        """Degraded checks display with warning emoji, not checkmark.

        Luna's design: 'warning Some optional modules not found'
        """
        output, _code = invoke_install(
            runner, mock_wheel_path, install_preflight_all_pass, degraded_install_result
        )
        assert "Some optional modules not found" in output, (
            "Missing degraded warning message"
        )
        # The warning text should be near a warning emoji, not a checkmark
        warning_line_found = False
        for line in output.splitlines():
            if "Some optional modules not found" in line:
                warning_line_found = True
                assert "\u26a0" in line, (
                    f"Degraded check should use warning emoji, got line: '{line}'"
                )
                break
        assert warning_line_found, "Warning message line not found"

    def test_health_status_shows_degraded(
        self,
        runner: CliRunner,
        mock_wheel_path: Path,
        install_preflight_all_pass: list[CheckResult],
        degraded_install_result: InstallResult,
    ) -> None:
        """Health status line shows 'Health: DEGRADED'.

        Luna's design: checkmark 'Health: DEGRADED' (still passes, but warns).
        """
        output, _code = invoke_install(
            runner, mock_wheel_path, install_preflight_all_pass, degraded_install_result
        )
        assert "Health: DEGRADED" in output, "Missing 'Health: DEGRADED' status line"

    def test_celebration_uses_warning_emoji_not_party(
        self,
        runner: CliRunner,
        mock_wheel_path: Path,
        install_preflight_all_pass: list[CheckResult],
        degraded_install_result: InstallResult,
    ) -> None:
        """Celebration downgrades from party popper to warning emoji.

        Luna's design: When health is DEGRADED, the celebration emoji
        changes from party popper to warning. This is a key UX signal
        that the install succeeded but needs attention.
        """
        output, _code = invoke_install(
            runner, mock_wheel_path, install_preflight_all_pass, degraded_install_result
        )
        # Party popper should NOT appear for degraded health
        assert "\U0001f389" not in output, (
            "Party popper emoji should not appear for DEGRADED health.\n"
            "Luna's design specifies warning emoji for degraded installs."
        )

    def test_celebration_message_says_installed_with_warnings(
        self,
        runner: CliRunner,
        mock_wheel_path: Path,
        install_preflight_all_pass: list[CheckResult],
        degraded_install_result: InstallResult,
    ) -> None:
        """Celebration message says 'installed with warnings' not 'healthy'.

        Luna's design: 'warning crafter-ai 0.2.0 installed with warnings'
        instead of 'party crafter-ai 0.2.0 installed and healthy!'
        """
        output, _code = invoke_install(
            runner, mock_wheel_path, install_preflight_all_pass, degraded_install_result
        )
        assert "crafter-ai 0.2.0 installed with warnings" in output, (
            "Missing degraded celebration message.\n"
            "Expected: 'crafter-ai 0.2.0 installed with warnings'\n"
            f"Output:\n{output}"
        )
        # The healthy message should NOT appear
        assert "installed and healthy!" not in output, (
            "'installed and healthy!' should not appear for DEGRADED health"
        )

    def test_doctor_suggestion_appears(
        self,
        runner: CliRunner,
        mock_wheel_path: Path,
        install_preflight_all_pass: list[CheckResult],
        degraded_install_result: InstallResult,
    ) -> None:
        """Suggestion to run 'crafter-ai doctor' for details.

        Luna's design: 'Some features may be limited. Run crafter-ai doctor for details.'
        """
        output, _code = invoke_install(
            runner, mock_wheel_path, install_preflight_all_pass, degraded_install_result
        )
        assert "crafter-ai doctor" in output, (
            "Missing suggestion to run 'crafter-ai doctor' for details.\n"
            f"Output:\n{output}"
        )

    def test_no_border_characters(
        self,
        runner: CliRunner,
        mock_wheel_path: Path,
        install_preflight_all_pass: list[CheckResult],
        degraded_install_result: InstallResult,
    ) -> None:
        """No Rich Table or Panel borders in degraded health output."""
        output, _code = invoke_install(
            runner, mock_wheel_path, install_preflight_all_pass, degraded_install_result
        )
        border_chars_found = FORBIDDEN_BORDER_CHARS.intersection(set(output))
        assert not border_chars_found, (
            f"Output contains forbidden border characters: {border_chars_found}"
        )
