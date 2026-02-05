"""Walking skeleton E2E acceptance test for the Forge TUI redesign.

This is the OUTER test in Outside-In TDD. It defines the target behavior
for the complete 17-step build-to-install flow as described in Luna's UX design:
  docs/ux/modern-cli-installer/journey-forge-tui-visual.md

EXPECTED STATE: This test FAILS against the current implementation.
The current TUI uses Rich Tables, Panels, and "FORGE:" prefix shouting.
Luna's design specifies a seamless emoji stream with no borders.

Making this test pass IS the implementation work.

Design source: journey-forge-tui.feature (walking skeleton scenarios)
Design system: journey-forge-tui-visual.md (mockups + anti-patterns)
Structured schema: journey-forge-tui.yaml (step definitions)

17-step journey:
  BUILD:   1-Header  2-PreFlight  3-Version  4-Wheel  5-Validation
           6-IDE Bundle  7-Build Complete
  PROMPT:  8-Confirm
  INSTALL: 9-Header  10-PreFlight  11-Backup  12-CLI Install
           13-Asset Deploy  14-Deploy Validation  15-SBOM  16-Health
  CELEBRATE: 17-Celebration
"""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from typer.testing import CliRunner

from crafter_ai.cli import app
from crafter_ai.installer.domain.candidate_version import BumpType, CandidateVersion
from crafter_ai.installer.domain.check_result import CheckResult, CheckSeverity
from crafter_ai.installer.domain.health_result import HealthStatus
from crafter_ai.installer.domain.ide_bundle_build_result import IdeBundleBuildResult
from crafter_ai.installer.services.build_service import BuildResult
from crafter_ai.installer.services.install_service import InstallPhase, InstallResult
from crafter_ai.installer.services.wheel_validation_service import WheelValidationResult


# ============================================================================
# Box-drawing characters that MUST NOT appear in the redesigned TUI output.
# Their presence means Rich Tables or Panels are still being rendered.
# ============================================================================
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
def build_pre_flight_results() -> list[CheckResult]:
    """Build pre-flight results matching the walking skeleton scenario."""
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
def mock_wheel_path(tmp_path: Path) -> Path:
    """Create a real wheel file on disk so path.exists() passes."""
    wheel_file = tmp_path / "crafter_ai-0.2.0-py3-none-any.whl"
    wheel_file.write_bytes(b"fake wheel content for testing")
    return wheel_file


@pytest.fixture
def successful_build_result(
    build_pre_flight_results: list[CheckResult],
    mock_wheel_path: Path,
) -> BuildResult:
    """Successful build producing crafter_ai-0.2.0-py3-none-any.whl."""
    return BuildResult(
        success=True,
        wheel_path=mock_wheel_path,
        version="0.2.0",
        pre_flight_results=build_pre_flight_results,
        validation_result=WheelValidationResult(
            wheel_path=mock_wheel_path,
            is_valid=True,
            version="0.2.0",
            package_name="crafter_ai",
            errors=[],
        ),
        error_message=None,
        ide_bundle_result=IdeBundleBuildResult(
            success=True,
            output_dir=Path("dist/ide"),
            agent_count=30,
            command_count=23,
            template_count=5,
            script_count=2,
            team_count=3,
            yaml_warnings=[],
            embed_injection_count=0,
        ),
    )


@pytest.fixture
def successful_install_result() -> InstallResult:
    """Successful install with HEALTHY status."""
    from crafter_ai.installer.domain.asset_deployment_result import (
        AssetDeploymentResult,
    )
    from crafter_ai.installer.domain.deployment_validation_result import (
        DeploymentValidationResult,
    )

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
        health_status=HealthStatus.HEALTHY,
        verification_warnings=[],
        asset_deployment_result=AssetDeploymentResult(
            success=True,
            agents_deployed=30,
            commands_deployed=23,
            templates_deployed=5,
            scripts_deployed=2,
            target_path=Path.home() / ".claude",
        ),
        deployment_validation_result=DeploymentValidationResult(
            valid=True,
            agent_count_match=True,
            command_count_match=True,
            template_count_match=True,
            script_count_match=True,
            manifest_written=True,
            schema_version="v3.0",
            schema_phases=7,
            mismatches=[],
        ),
    )


@pytest.fixture
def install_pre_flight_results() -> list[CheckResult]:
    """Install pre-flight results matching the 17-step walking skeleton.

    Includes the NEW IDE bundle check (step 10).
    """
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
        CheckResult(
            id="ide_bundle_exists",
            name="IDE bundle exists",
            passed=True,
            severity=CheckSeverity.BLOCKING,
            message="IDE bundle found (30 agents, 23 commands)",
        ),
    ]


# ============================================================================
# Helper: invoke the full build -> confirm -> install flow
# ============================================================================


def invoke_full_flow(
    runner: CliRunner,
    candidate_version: CandidateVersion,
    successful_build_result: BuildResult,
    successful_install_result: InstallResult,
    install_pre_flight_results: list[CheckResult],
) -> str:
    """Run 'forge build', answer 'y' to install prompt, capture full output.

    Mocks the build and install services so the test runs fast and
    deterministic. The CLI presentation layer executes for real.

    Returns:
        The combined stdout output from both build and install phases.
    """
    mock_report = MagicMock()
    mock_report.generate.return_value = MagicMock()
    mock_report.format_console.return_value = ""

    with (
        patch(
            "crafter_ai.installer.cli.forge_build.create_build_service"
        ) as mock_build_factory,
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
        # Wire up build service mock
        mock_build_svc = MagicMock()
        mock_build_svc.execute.return_value = successful_build_result
        mock_build_svc.determine_version.return_value = candidate_version
        mock_build_factory.return_value = mock_build_svc

        # Wire up install service mock
        mock_install_svc = MagicMock()
        mock_install_svc.install.return_value = successful_install_result
        mock_install_factory.return_value = mock_install_svc

        # Install pre-flight passes
        mock_install_preflight.return_value = install_pre_flight_results

        # Report service (current code uses this; new TUI may not)
        mock_report_service.return_value = mock_report

        result = runner.invoke(app, ["forge", "build"], input="y\n")

    assert result.exit_code == 0, (
        f"Expected exit code 0 but got {result.exit_code}.\n"
        f"Output:\n{result.output}\n"
        f"Exception: {result.exception}"
    )
    return result.output


# ============================================================================
# Test class: Walking Skeleton E2E
# ============================================================================


@pytest.mark.e2e
class TestWalkingSkeletonBuildToInstall:
    """Complete 17-step build-to-install flow as one continuous journey.

    Corresponds to: journey-forge-tui.feature @walking-skeleton scenario.

    This is the outside-in OUTER test. It will FAIL until the TUI
    redesign is implemented. Each assertion below maps to a specific
    step in the walking skeleton scenario.
    """

    # -- DESIGN SYSTEM: No tables, panels, or borders --------------------

    def test_output_contains_no_table_or_panel_borders(
        self,
        runner: CliRunner,
        candidate_version: CandidateVersion,
        successful_build_result: BuildResult,
        successful_install_result: InstallResult,
        install_pre_flight_results: list[CheckResult],
    ) -> None:
        """Luna's rule: No borders, no boxes, no panels, no tables. Ever.

        Visual design: journey-forge-tui-visual.md 'Anti-Patterns' section.
        Feature step: 'And no Rich Table or Panel borders appear in the output'
        """
        output = invoke_full_flow(
            runner,
            candidate_version,
            successful_build_result,
            successful_install_result,
            install_pre_flight_results,
        )

        border_chars_found = FORBIDDEN_BORDER_CHARS.intersection(set(output))
        assert not border_chars_found, (
            f"Output contains forbidden border characters: {border_chars_found}\n"
            f"These indicate Rich Tables or Panels are still rendered.\n"
            f"Luna's design requires emoji-based streaming output only."
        )

    def test_output_contains_no_forge_prefix_shouting(
        self,
        runner: CliRunner,
        candidate_version: CandidateVersion,
        successful_build_result: BuildResult,
        successful_install_result: InstallResult,
        install_pre_flight_results: list[CheckResult],
    ) -> None:
        """Luna's rule: No 'FORGE:' prefix shouting.

        Visual design: journey-forge-tui-visual.md anti-pattern #6.
        """
        output = invoke_full_flow(
            runner,
            candidate_version,
            successful_build_result,
            successful_install_result,
            install_pre_flight_results,
        )

        assert "FORGE:" not in output, (
            "Output contains 'FORGE:' prefix shouting.\n"
            "Luna's design uses emoji phase headers instead."
        )

    # -- BUILD PHASE: Steps 1-7 -----------------------------------------

    def test_build_header_is_emoji_stream(
        self,
        runner: CliRunner,
        candidate_version: CandidateVersion,
        successful_build_result: BuildResult,
        successful_install_result: InstallResult,
        install_pre_flight_results: list[CheckResult],
    ) -> None:
        """Step 1: Build header uses hammer emoji, bold, no panel."""
        output = invoke_full_flow(
            runner,
            candidate_version,
            successful_build_result,
            successful_install_result,
            install_pre_flight_results,
        )

        non_blank_lines = [line for line in output.splitlines() if line.strip()]
        assert len(non_blank_lines) > 0, "Output is empty"

        first_line = non_blank_lines[0]
        assert "\U0001f528" in first_line, (
            f"First non-blank line should contain hammer emoji.\nGot: '{first_line}'"
        )
        assert "Building crafter-ai" in first_line, (
            f"First non-blank line should contain 'Building crafter-ai'.\n"
            f"Got: '{first_line}'"
        )

    def test_build_preflight_checks_as_streaming_list(
        self,
        runner: CliRunner,
        candidate_version: CandidateVersion,
        successful_build_result: BuildResult,
        successful_install_result: InstallResult,
        install_pre_flight_results: list[CheckResult],
    ) -> None:
        """Step 2: Pre-flight checks display as streaming emoji list."""
        output = invoke_full_flow(
            runner,
            candidate_version,
            successful_build_result,
            successful_install_result,
            install_pre_flight_results,
        )

        assert "\U0001f50d" in output, "Missing magnifying glass emoji for pre-flight"
        assert "Pre-flight checks" in output
        assert "\u2705" in output, "Missing checkmark emoji"
        assert "pyproject.toml found" in output
        assert "Build toolchain ready" in output
        assert "Source directory found" in output
        assert "Version available for release" in output
        assert "\u26a0\ufe0f" in output or "\u26a0" in output, (
            "Missing warning emoji for uncommitted changes"
        )
        assert "Uncommitted changes detected" in output
        assert "Pre-flight passed" in output

    def test_version_display_is_minimal(
        self,
        runner: CliRunner,
        candidate_version: CandidateVersion,
        successful_build_result: BuildResult,
        successful_install_result: InstallResult,
        install_pre_flight_results: list[CheckResult],
    ) -> None:
        """Step 3: Version display is minimal, no panel or box."""
        output = invoke_full_flow(
            runner,
            candidate_version,
            successful_build_result,
            successful_install_result,
            install_pre_flight_results,
        )

        assert "\U0001f4d0" in output, "Missing ruler emoji for version section"
        assert "Version" in output
        assert "0.1.0" in output
        assert "0.2.0" in output
        assert "minor" in output.lower()

    def test_build_spinner_resolves_to_persistent_line(
        self,
        runner: CliRunner,
        candidate_version: CandidateVersion,
        successful_build_result: BuildResult,
        successful_install_result: InstallResult,
        install_pre_flight_results: list[CheckResult],
    ) -> None:
        """Step 4: Wheel compilation spinner resolves to persistent line.

        Note: We cannot test spinner animation in CliRunner, but we
        CAN verify the persistent result line exists in output.
        """
        output = invoke_full_flow(
            runner,
            candidate_version,
            successful_build_result,
            successful_install_result,
            install_pre_flight_results,
        )

        assert "Wheel built" in output, (
            "Missing persistent line 'Wheel built' after compilation spinner."
        )

    def test_wheel_validation_checks(
        self,
        runner: CliRunner,
        candidate_version: CandidateVersion,
        successful_build_result: BuildResult,
        successful_install_result: InstallResult,
        install_pre_flight_results: list[CheckResult],
    ) -> None:
        """Step 5: Wheel validation displays as check list."""
        output = invoke_full_flow(
            runner,
            candidate_version,
            successful_build_result,
            successful_install_result,
            install_pre_flight_results,
        )

        assert "Validating wheel" in output
        assert "PEP 427 format valid" in output
        assert "Metadata complete" in output
        assert "Wheel validated" in output

    def test_ide_bundle_build_output(
        self,
        runner: CliRunner,
        candidate_version: CandidateVersion,
        successful_build_result: BuildResult,
        successful_install_result: InstallResult,
        install_pre_flight_results: list[CheckResult],
    ) -> None:
        """Step 6 (NEW): IDE bundle build shows header and completion.

        Feature step: 'And I see "Building IDE bundle"'
        Feature step: 'And a spinner resolves to "IDE bundle built" with duration'

        Note: Detailed counts (30 agents, 23 commands, YAML warnings)
        are validated at integration/unit level, not here.
        """
        output = invoke_full_flow(
            runner,
            candidate_version,
            successful_build_result,
            successful_install_result,
            install_pre_flight_results,
        )

        assert "Building IDE bundle" in output, (
            "Missing IDE bundle build section header.\n"
            "Step 6 specifies: 'Building IDE bundle'"
        )
        assert "IDE bundle built" in output, (
            "Missing IDE bundle build completion line.\n"
            "Step 6 specifies: 'IDE bundle built ({duration})'"
        )

    def test_build_complete_shows_two_artifacts(
        self,
        runner: CliRunner,
        candidate_version: CandidateVersion,
        successful_build_result: BuildResult,
        successful_install_result: InstallResult,
        install_pre_flight_results: list[CheckResult],
    ) -> None:
        """Step 7 (MODIFIED): Build complete shows wheel AND IDE bundle.

        Feature step: 'And I see "Build complete"'
        Feature step: 'And I see the wheel filename in dim'
        Feature step: 'And I see "IDE bundle:" in dim'
        """
        output = invoke_full_flow(
            runner,
            candidate_version,
            successful_build_result,
            successful_install_result,
            install_pre_flight_results,
        )

        assert "\U0001f528" in output, "Missing hammer emoji in build complete"
        assert "Build complete" in output, "Missing 'Build complete' header"
        assert "crafter_ai-0.2.0-py3-none-any.whl" in output, (
            "Missing wheel filename in build complete section"
        )
        assert "IDE bundle:" in output, (
            "Missing 'IDE bundle:' detail line in build complete.\n"
            "Build now produces two artifacts: wheel + IDE bundle."
        )

    # -- TRANSITION: Steps 8 -------------------------------------------

    def test_install_prompt_format_and_version(
        self,
        runner: CliRunner,
        candidate_version: CandidateVersion,
        successful_build_result: BuildResult,
        successful_install_result: InstallResult,
        install_pre_flight_results: list[CheckResult],
    ) -> None:
        """Step 8: Install prompt shows version from wheel METADATA."""
        output = invoke_full_flow(
            runner,
            candidate_version,
            successful_build_result,
            successful_install_result,
            install_pre_flight_results,
        )

        assert "Install crafter-ai 0.2.0?" in output, (
            "Missing redesigned install prompt.\n"
            "Expected: 'Install crafter-ai 0.2.0? [Y/n]:'"
        )
        assert "[Y/n]" in output, (
            "Install prompt must use [Y/n] format with Y as default."
        )

    # -- INSTALL PHASE: Steps 9-16 -------------------------------------

    def test_install_header_is_emoji_stream(
        self,
        runner: CliRunner,
        candidate_version: CandidateVersion,
        successful_build_result: BuildResult,
        successful_install_result: InstallResult,
        install_pre_flight_results: list[CheckResult],
    ) -> None:
        """Step 9: Install header uses package emoji, bold, no panel."""
        output = invoke_full_flow(
            runner,
            candidate_version,
            successful_build_result,
            successful_install_result,
            install_pre_flight_results,
        )

        assert "\U0001f4e6" in output, "Missing package emoji in install phase"
        assert "Installing crafter-ai" in output, (
            "Missing install phase header 'Installing crafter-ai'."
        )

    def test_install_preflight_checks_as_streaming_list(
        self,
        runner: CliRunner,
        candidate_version: CandidateVersion,
        successful_build_result: BuildResult,
        successful_install_result: InstallResult,
        install_pre_flight_results: list[CheckResult],
    ) -> None:
        """Step 10 (MODIFIED): Install pre-flight includes IDE bundle check."""
        output = invoke_full_flow(
            runner,
            candidate_version,
            successful_build_result,
            successful_install_result,
            install_pre_flight_results,
        )

        assert "Wheel file found" in output
        assert "Wheel format valid" in output
        assert "pipx environment ready" in output
        assert "Install path writable" in output
        assert "IDE bundle found" in output, (
            "Missing NEW IDE bundle check in install pre-flight.\n"
            "Step 10 specifies: 'IDE bundle found (30 agents, 23 commands)'"
        )

        preflight_count = output.count("Pre-flight passed")
        assert preflight_count >= 2, (
            f"Expected 'Pre-flight passed' at least twice "
            f"(build + install), found {preflight_count} times."
        )

    def test_fresh_install_backup_message(
        self,
        runner: CliRunner,
        candidate_version: CandidateVersion,
        successful_build_result: BuildResult,
        successful_install_result: InstallResult,
        install_pre_flight_results: list[CheckResult],
    ) -> None:
        """Step 11: Fresh install shows single backup skip line.

        Feature step: 'And I see "Fresh install, no backup needed"'
        """
        output = invoke_full_flow(
            runner,
            candidate_version,
            successful_build_result,
            successful_install_result,
            install_pre_flight_results,
        )

        assert "Fresh install" in output, (
            "Missing fresh install backup message.\n"
            "Expected text containing 'Fresh install'"
        )

    def test_cli_install_spinner_resolves_to_persistent_line(
        self,
        runner: CliRunner,
        candidate_version: CandidateVersion,
        successful_build_result: BuildResult,
        successful_install_result: InstallResult,
        install_pre_flight_results: list[CheckResult],
    ) -> None:
        """Step 12: CLI install spinner resolves to persistent line.

        Feature step: 'And the spinner resolves to
                       "nWave CLI installed via pipx" with duration'
        """
        output = invoke_full_flow(
            runner,
            candidate_version,
            successful_build_result,
            successful_install_result,
            install_pre_flight_results,
        )

        # Accept either the new "nWave CLI installed via pipx" or
        # the transitional "Installed via pipx" text
        assert (
            "Installed via pipx" in output or "nWave CLI installed via pipx" in output
        ), "Missing persistent line for CLI install after spinner."

    def test_asset_deployment_output(
        self,
        runner: CliRunner,
        candidate_version: CandidateVersion,
        successful_build_result: BuildResult,
        successful_install_result: InstallResult,
        install_pre_flight_results: list[CheckResult],
    ) -> None:
        """Step 13 (NEW): Asset deployment shows header and completion.

        Feature step: 'And I see "Deploying nWave assets"'
        Feature step: 'And a spinner resolves to "Assets deployed" with duration'

        Note: Detailed per-category lines (30 agents -> ~/.claude/agents/nw/)
        are validated at integration level, not here.
        """
        output = invoke_full_flow(
            runner,
            candidate_version,
            successful_build_result,
            successful_install_result,
            install_pre_flight_results,
        )

        assert "Deploying nWave assets" in output, (
            "Missing asset deployment section header.\n"
            "Step 13 specifies: 'Deploying nWave assets'"
        )
        assert "Assets deployed" in output, (
            "Missing asset deployment completion line.\n"
            "Step 13 specifies: 'Assets deployed ({duration})'"
        )

    def test_deployment_validation_output(
        self,
        runner: CliRunner,
        candidate_version: CandidateVersion,
        successful_build_result: BuildResult,
        successful_install_result: InstallResult,
        install_pre_flight_results: list[CheckResult],
    ) -> None:
        """Step 14 (NEW): Deployment validation as emoji stream, no Rich table.

        Feature step: 'And I see "Validating deployment"'
        Feature step: 'And I see "Deployment validated"'
        """
        output = invoke_full_flow(
            runner,
            candidate_version,
            successful_build_result,
            successful_install_result,
            install_pre_flight_results,
        )

        assert "Validating deployment" in output, (
            "Missing deployment validation section header.\n"
            "Step 14 specifies: 'Validating deployment'"
        )
        assert "Deployment validated" in output, (
            "Missing deployment validation summary.\n"
            "Step 14 specifies: 'Deployment validated'"
        )

    def test_sbom_dual_group_format(
        self,
        runner: CliRunner,
        candidate_version: CandidateVersion,
        successful_build_result: BuildResult,
        successful_install_result: InstallResult,
        install_pre_flight_results: list[CheckResult],
    ) -> None:
        """Step 15 (EXPANDED): SBOM shows CLI package + IDE assets groups.

        Feature step: 'And I see "What was installed"'
        Feature step: 'And the SBOM contains a CLI package group'
        Feature step: 'And the SBOM contains an IDE assets group'

        Note: Exact line-by-line content validated at integration level.
        Here we just check both groups are present.
        """
        output = invoke_full_flow(
            runner,
            candidate_version,
            successful_build_result,
            successful_install_result,
            install_pre_flight_results,
        )

        assert "What was installed" in output, (
            "Missing SBOM manifest header.\nStep 15 specifies: 'What was installed'"
        )
        # CLI group marker
        assert "crafter-ai 0.2.0" in output or "crafter_ai 0.2.0" in output, (
            "Missing CLI package identity in SBOM."
        )
        # IDE assets group marker (at least one deploy target line)
        assert "~/.claude/" in output, "Missing IDE assets deploy target in SBOM."

    def test_health_includes_asset_check(
        self,
        runner: CliRunner,
        candidate_version: CandidateVersion,
        successful_build_result: BuildResult,
        successful_install_result: InstallResult,
        install_pre_flight_results: list[CheckResult],
    ) -> None:
        """Step 16 (MODIFIED): Health verification includes asset accessibility.

        Feature step: 'And I see "nWave assets accessible"'
        """
        output = invoke_full_flow(
            runner,
            candidate_version,
            successful_build_result,
            successful_install_result,
            install_pre_flight_results,
        )

        assert "\U0001fa7a" in output, "Missing stethoscope emoji for health check"
        assert "Verifying installation" in output
        assert "CLI responds to --version" in output
        assert "Core modules loadable" in output
        assert "nWave assets accessible" in output, (
            "Missing NEW asset accessibility check in health verification.\n"
            "Step 16 specifies: 'nWave assets accessible'"
        )
        assert "Health: HEALTHY" in output

    # -- CELEBRATION: Step 17 -------------------------------------------

    def test_celebration_uses_nwave_brand(
        self,
        runner: CliRunner,
        candidate_version: CandidateVersion,
        successful_build_result: BuildResult,
        successful_install_result: InstallResult,
        install_pre_flight_results: list[CheckResult],
    ) -> None:
        """Step 17: Celebration uses "nWave" product brand, not package name.

        Feature step: 'And I see "nWave 0.2.0 installed and healthy!"'
        """
        output = invoke_full_flow(
            runner,
            candidate_version,
            successful_build_result,
            successful_install_result,
            install_pre_flight_results,
        )

        assert "\U0001f389" in output, "Missing party popper emoji in celebration."
        assert "nWave 0.2.0 installed and healthy!" in output, (
            "Celebration should use 'nWave' brand name, not 'crafter-ai'.\n"
            "Step 17 specifies: 'nWave {version} installed and healthy!'"
        )
        assert "Ready to use in Claude Code." in output, (
            "Missing 'Ready to use in Claude Code.' follow-up line."
        )

    def test_getting_started_section(
        self,
        runner: CliRunner,
        candidate_version: CandidateVersion,
        successful_build_result: BuildResult,
        successful_install_result: InstallResult,
        install_pre_flight_results: list[CheckResult],
    ) -> None:
        """Step 17: Getting started section always shows available commands.

        Feature step: 'And I see "Getting started"'
        Feature step: 'And I see "/nw:discuss" in dim'
        """
        output = invoke_full_flow(
            runner,
            candidate_version,
            successful_build_result,
            successful_install_result,
            install_pre_flight_results,
        )

        assert "Getting started" in output, (
            "Missing 'Getting started' section in celebration."
        )
        assert "/nw:discuss" in output, (
            "Missing /nw:discuss command in Getting started section."
        )

    # -- SHARED ARTIFACT CONSISTENCY ------------------------------------

    def test_version_consistency_across_all_displays(
        self,
        runner: CliRunner,
        candidate_version: CandidateVersion,
        successful_build_result: BuildResult,
        successful_install_result: InstallResult,
        install_pre_flight_results: list[CheckResult],
    ) -> None:
        """Version "0.2.0" must appear consistently in 5 locations.

        All version displays originate from wheel METADATA as single
        source of truth.
        """
        output = invoke_full_flow(
            runner,
            candidate_version,
            successful_build_result,
            successful_install_result,
            install_pre_flight_results,
        )

        version = "0.2.0"

        # Location 1: Version display line
        assert "0.1.0" in output and version in output, (
            "Version display missing: expected '0.1.0' and '0.2.0'"
        )
        # Location 2: Wheel filename
        assert f"crafter_ai-{version}-py3-none-any.whl" in output, (
            f"Wheel filename 'crafter_ai-{version}-py3-none-any.whl' not in output"
        )
        # Location 3: Install prompt
        assert f"Install crafter-ai {version}?" in output, (
            f"Install prompt missing version {version}"
        )
        # Location 4: SBOM
        assert f"crafter-ai {version}" in output or f"crafter_ai {version}" in output, (
            f"SBOM missing version {version}"
        )
        # Location 5: Celebration
        assert f"nWave {version} installed and healthy!" in output, (
            f"Celebration missing version {version}"
        )

    # -- CONTINUOUS STREAM VALIDATION -----------------------------------

    def test_output_reads_as_continuous_stream(
        self,
        runner: CliRunner,
        candidate_version: CandidateVersion,
        successful_build_result: BuildResult,
        successful_install_result: InstallResult,
        install_pre_flight_results: list[CheckResult],
    ) -> None:
        """The output reads as a continuous top-to-bottom stream.

        Validates correct phase ordering by checking that key markers
        appear in the expected sequence for ALL 17 steps.
        """
        output = invoke_full_flow(
            runner,
            candidate_version,
            successful_build_result,
            successful_install_result,
            install_pre_flight_results,
        )

        # Define ordered markers that must appear in sequence
        ordered_markers = [
            "Building crafter-ai",  # Step 1: Build header
            "Pre-flight checks",  # Step 2: Build pre-flight
            "Pre-flight passed",  # Step 2: Build pre-flight summary
            "\U0001f4d0",  # Step 3: Version display (ruler emoji)
            "Wheel built",  # Step 4: Compilation persistent line
            "Validating wheel",  # Step 5: Wheel validation
            "Building IDE bundle",  # Step 6: IDE bundle build (NEW)
            "IDE bundle built",  # Step 6: IDE bundle completion (NEW)
            "Build complete",  # Step 7: Build complete
            "Install crafter-ai 0.2.0?",  # Step 8: Install prompt
            "Installing crafter-ai",  # Step 9: Install header
            "Wheel file found",  # Step 10: Install pre-flight
            "IDE bundle found",  # Step 10: IDE bundle check (NEW)
            "Fresh install",  # Step 11: Backup skip
            "Installed via pipx",  # Step 12: CLI install
            "Deploying nWave assets",  # Step 13: Asset deployment (NEW)
            "Assets deployed",  # Step 13: Deploy completion (NEW)
            "Validating deployment",  # Step 14: Deploy validation (NEW)
            "Deployment validated",  # Step 14: Validation summary (NEW)
            "What was installed",  # Step 15: SBOM (EXPANDED)
            "Verifying installation",  # Step 16: Health verification
            "nWave assets accessible",  # Step 16: Asset check (NEW)
            "Health: HEALTHY",  # Step 16: Health summary
            "installed and healthy!",  # Step 17: Celebration
            "Getting started",  # Step 17: Getting started (NEW)
        ]

        last_pos = -1
        for marker in ordered_markers:
            pos = output.find(marker)
            assert pos != -1, (
                f"Marker '{marker}' not found in output.\n"
                f"Phase ordering cannot be validated."
            )
            assert pos > last_pos, (
                f"Marker '{marker}' (pos={pos}) appears before previous "
                f"marker (pos={last_pos}).\n"
                f"Phases are out of order in the output stream."
            )
            last_pos = pos

    # -- ABSENCE OF OLD TUI ARTIFACTS -----------------------------------

    def test_no_version_analysis_panel(
        self,
        runner: CliRunner,
        candidate_version: CandidateVersion,
        successful_build_result: BuildResult,
        successful_install_result: InstallResult,
        install_pre_flight_results: list[CheckResult],
    ) -> None:
        """Old TUI wrapped version info in a Panel titled 'Version Analysis'."""
        output = invoke_full_flow(
            runner,
            candidate_version,
            successful_build_result,
            successful_install_result,
            install_pre_flight_results,
        )

        assert "Version Analysis" not in output, (
            "Old 'Version Analysis' panel title found."
        )
        assert "Version Bump:" not in output, "Old 'Version Bump:' label found."

    def test_no_build_summary_panel(
        self,
        runner: CliRunner,
        candidate_version: CandidateVersion,
        successful_build_result: BuildResult,
        successful_install_result: InstallResult,
        install_pre_flight_results: list[CheckResult],
    ) -> None:
        """Old TUI had a 'Build Summary' panel with multi-line receipt."""
        output = invoke_full_flow(
            runner,
            candidate_version,
            successful_build_result,
            successful_install_result,
            install_pre_flight_results,
        )

        assert "Build Summary" not in output, "Old 'Build Summary' panel title found."

    def test_no_installation_panel(
        self,
        runner: CliRunner,
        candidate_version: CandidateVersion,
        successful_build_result: BuildResult,
        successful_install_result: InstallResult,
        install_pre_flight_results: list[CheckResult],
    ) -> None:
        """Old TUI had a 'FORGE: INSTALL' panel header."""
        output = invoke_full_flow(
            runner,
            candidate_version,
            successful_build_result,
            successful_install_result,
            install_pre_flight_results,
        )

        assert "FORGE: INSTALL" not in output, (
            "Old 'FORGE: INSTALL' panel content found."
        )
