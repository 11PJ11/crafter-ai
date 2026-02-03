"""Walking skeleton E2E acceptance test for the Forge TUI redesign.

This is the OUTER test in Outside-In TDD. It defines the target behavior
for the complete build-to-install flow as described in Luna's UX design:
  docs/ux/modern-cli-installer/journey-forge-tui-visual.md

EXPECTED STATE: This test FAILS against the current implementation.
The current TUI uses Rich Tables, Panels, and "FORGE:" prefix shouting.
Luna's design specifies a seamless emoji stream with no borders.

Making this test pass IS the implementation work.

Design source: journey-forge-tui.feature lines 241-334 (walking skeleton)
Design system: journey-forge-tui-visual.md (mockups + anti-patterns)
Structured schema: journey-forge-tui.yaml (step definitions)
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
    )


@pytest.fixture
def successful_install_result() -> InstallResult:
    """Successful install with HEALTHY status."""
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
    )


@pytest.fixture
def install_pre_flight_results() -> list[CheckResult]:
    """Install pre-flight results matching the walking skeleton scenario."""
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
    """Complete build-to-install flow as one continuous journey.

    Corresponds to: journey-forge-tui.feature @walking-skeleton scenario
    (lines 241-334).

    This is the outside-in OUTER test. It will FAIL until the TUI
    redesign is implemented. Each assertion below maps to a specific
    step in the walking skeleton scenario.
    """

    # ── DESIGN SYSTEM: No tables, panels, or borders ──────────────────

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
            "Luna's design uses emoji phase headers instead:\n"
            "  Current: 'FORGE: BUILD COMPLETE'\n"
            "  Target:  'Build complete: crafter_ai-0.2.0-py3-none-any.whl'"
        )

    # ── BUILD PHASE ───────────────────────────────────────────────────

    def test_build_header_is_emoji_stream(
        self,
        runner: CliRunner,
        candidate_version: CandidateVersion,
        successful_build_result: BuildResult,
        successful_install_result: InstallResult,
        install_pre_flight_results: list[CheckResult],
    ) -> None:
        """Step 1: Build header uses hammer emoji, bold, no panel.

        Feature step: 'Then the first non-blank output line is
                       "Building crafter-ai" in bold'
        """
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
            f"First non-blank line should contain hammer emoji.\n"
            f"Got: '{first_line}'"
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
        """Step 2: Pre-flight checks display as streaming emoji list.

        Feature steps:
          'And I see "Pre-flight checks" indented 2 spaces'
          'And I see "pyproject.toml found"'
          'And I see "Build toolchain ready"'
          'And I see "Source directory found"'
          'And I see "Uncommitted changes detected" as a non-blocking warning'
          'And I see "Version available for release"'
          'And I see "Pre-flight passed"'
        """
        output = invoke_full_flow(
            runner,
            candidate_version,
            successful_build_result,
            successful_install_result,
            install_pre_flight_results,
        )

        # Sub-phase header
        assert "\U0001f50d" in output, "Missing magnifying glass emoji for pre-flight"
        assert "Pre-flight checks" in output

        # Individual check results with correct emoji
        assert "\u2705" in output, "Missing checkmark emoji"
        assert "pyproject.toml found" in output
        assert "Build toolchain ready" in output
        assert "Source directory found" in output
        assert "Version available for release" in output

        # Warning check uses warning emoji
        assert "\u26a0\ufe0f" in output or "\u26a0" in output, (
            "Missing warning emoji for uncommitted changes"
        )
        assert "Uncommitted changes detected" in output

        # Summary line
        assert "Pre-flight passed" in output

    def test_version_display_is_minimal(
        self,
        runner: CliRunner,
        candidate_version: CandidateVersion,
        successful_build_result: BuildResult,
        successful_install_result: InstallResult,
        install_pre_flight_results: list[CheckResult],
    ) -> None:
        """Step 3: Version display is minimal, no panel or box.

        Feature steps:
          'And I see "Version"'
          'And I see "0.1.0 -> 0.2.0 (minor)"'
        """
        output = invoke_full_flow(
            runner,
            candidate_version,
            successful_build_result,
            successful_install_result,
            install_pre_flight_results,
        )

        assert "\U0001f4d0" in output, "Missing ruler emoji for version section"
        assert "Version" in output

        # Version transition line: "0.1.0 -> 0.2.0 (minor)"
        # The arrow can be either "->" or the unicode arrow
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

        Feature step: 'And the spinner resolves to a persistent line
                       "Wheel built" with duration'

        Note: We cannot test the spinner animation in CliRunner, but we
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
            "Missing persistent line 'Wheel built' after compilation spinner.\n"
            "Luna's Step 4 specifies: spinner resolves to 'Wheel built ({duration})'"
        )

    def test_wheel_validation_checks(
        self,
        runner: CliRunner,
        candidate_version: CandidateVersion,
        successful_build_result: BuildResult,
        successful_install_result: InstallResult,
        install_pre_flight_results: list[CheckResult],
    ) -> None:
        """Step 5: Wheel validation displays as check list.

        Feature steps:
          'And I see "Validating wheel"'
          'And I see "PEP 427 format valid"'
          'And I see "Metadata complete"'
          'And I see "Wheel validated"'
        """
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

    def test_build_complete_line_is_concise(
        self,
        runner: CliRunner,
        candidate_version: CandidateVersion,
        successful_build_result: BuildResult,
        successful_install_result: InstallResult,
        install_pre_flight_results: list[CheckResult],
    ) -> None:
        """Step 6: Build complete is a single line with wheel name.

        Feature step: 'And I see "Build complete: crafter_ai-0.2.0-py3-none-any.whl"'
        """
        output = invoke_full_flow(
            runner,
            candidate_version,
            successful_build_result,
            successful_install_result,
            install_pre_flight_results,
        )

        assert "\U0001f528" in output, (
            "Missing hammer emoji in build complete line.\n"
            "Luna's Step 6 specifies: 'hammer_emoji Build complete: {wheel_filename}'"
        )
        assert "Build complete: crafter_ai-0.2.0-py3-none-any.whl" in output, (
            "Missing concise build complete line.\n"
            "Expected: 'Build complete: crafter_ai-0.2.0-py3-none-any.whl'\n"
            "The current code uses a Panel with 'FORGE: BUILD COMPLETE' instead."
        )

    # ── TRANSITION: CONFIRMATION PROMPT ───────────────────────────────

    def test_install_prompt_format_and_version(
        self,
        runner: CliRunner,
        candidate_version: CandidateVersion,
        successful_build_result: BuildResult,
        successful_install_result: InstallResult,
        install_pre_flight_results: list[CheckResult],
    ) -> None:
        """Step 7: Install prompt shows version from wheel METADATA.

        Feature steps:
          'And I see "Install crafter-ai 0.2.0? [Y/n]: "'
          'And the version "0.2.0" in the prompt matches the wheel METADATA'
        """
        output = invoke_full_flow(
            runner,
            candidate_version,
            successful_build_result,
            successful_install_result,
            install_pre_flight_results,
        )

        # Prompt must include package emoji, name, version, and Y/n format
        assert "Install crafter-ai 0.2.0?" in output, (
            "Missing redesigned install prompt.\n"
            "Expected: 'Install crafter-ai 0.2.0? [Y/n]:'\n"
            "Current code uses: 'Install locally now?'"
        )
        assert "[Y/n]" in output, (
            "Install prompt must use [Y/n] format with Y as default."
        )

    # ── INSTALL PHASE ─────────────────────────────────────────────────

    def test_install_header_is_emoji_stream(
        self,
        runner: CliRunner,
        candidate_version: CandidateVersion,
        successful_build_result: BuildResult,
        successful_install_result: InstallResult,
        install_pre_flight_results: list[CheckResult],
    ) -> None:
        """Step 8: Install header uses package emoji, bold, no panel.

        Feature step: 'Then I see "Installing crafter-ai" in bold'
        """
        output = invoke_full_flow(
            runner,
            candidate_version,
            successful_build_result,
            successful_install_result,
            install_pre_flight_results,
        )

        assert "\U0001f4e6" in output, "Missing package emoji in install phase"
        assert "Installing crafter-ai" in output, (
            "Missing install phase header 'Installing crafter-ai'.\n"
            "Current code uses Panel with 'FORGE: INSTALL' instead."
        )

    def test_install_preflight_checks_as_streaming_list(
        self,
        runner: CliRunner,
        candidate_version: CandidateVersion,
        successful_build_result: BuildResult,
        successful_install_result: InstallResult,
        install_pre_flight_results: list[CheckResult],
    ) -> None:
        """Step 9: Install pre-flight checks as streaming emoji list.

        Feature steps:
          'And I see "Wheel file found"'
          'And I see "Wheel format valid"'
          'And I see "pipx environment ready"'
          'And I see "Install path writable"'
          'And I see "Pre-flight passed"' (second occurrence)
        """
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

        # Pre-flight passed appears in both build and install phases
        preflight_count = output.count("Pre-flight passed")
        assert preflight_count >= 2, (
            f"Expected 'Pre-flight passed' at least twice "
            f"(build + install), found {preflight_count} times."
        )

    def test_fresh_install_skips_backup(
        self,
        runner: CliRunner,
        candidate_version: CandidateVersion,
        successful_build_result: BuildResult,
        successful_install_result: InstallResult,
        install_pre_flight_results: list[CheckResult],
    ) -> None:
        """Step 10: Fresh install skips backup with message.

        Feature step: 'And I see "Fresh install, skipping backup"'
        """
        output = invoke_full_flow(
            runner,
            candidate_version,
            successful_build_result,
            successful_install_result,
            install_pre_flight_results,
        )

        assert "Fresh install, skipping backup" in output, (
            "Missing fresh install backup skip message.\n"
            "Expected: 'Fresh install, skipping backup'"
        )

    def test_install_spinner_resolves_to_persistent_line(
        self,
        runner: CliRunner,
        candidate_version: CandidateVersion,
        successful_build_result: BuildResult,
        successful_install_result: InstallResult,
        install_pre_flight_results: list[CheckResult],
    ) -> None:
        """Step 11: pipx install spinner resolves to persistent line.

        Feature step: 'And the spinner resolves to a persistent line
                       "Installed via pipx" with duration'

        Note: We cannot test the spinner animation in CliRunner, but we
        CAN verify the persistent result line exists in output.
        """
        output = invoke_full_flow(
            runner,
            candidate_version,
            successful_build_result,
            successful_install_result,
            install_pre_flight_results,
        )

        assert "Installed via pipx" in output, (
            "Missing persistent line 'Installed via pipx' after install spinner."
        )

    def test_health_verification_as_check_list(
        self,
        runner: CliRunner,
        candidate_version: CandidateVersion,
        successful_build_result: BuildResult,
        successful_install_result: InstallResult,
        install_pre_flight_results: list[CheckResult],
    ) -> None:
        """Step 12: Health verification displays as streaming check list.

        Feature steps:
          'And I see "Verifying installation"'
          'And I see "CLI responds to --version"'
          'And I see "Core modules loadable"'
          'And I see "Health: HEALTHY"'
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
        assert "Health: HEALTHY" in output

    # ── CELEBRATION ───────────────────────────────────────────────────

    def test_celebration_message_format(
        self,
        runner: CliRunner,
        candidate_version: CandidateVersion,
        successful_build_result: BuildResult,
        successful_install_result: InstallResult,
        install_pre_flight_results: list[CheckResult],
    ) -> None:
        """Step 13: The celebration moment with version and health.

        Feature steps:
          'And I see "crafter-ai 0.2.0 installed and healthy!" in bold green'
          'And I see "Ready to use in Claude Code." in dim'
        """
        output = invoke_full_flow(
            runner,
            candidate_version,
            successful_build_result,
            successful_install_result,
            install_pre_flight_results,
        )

        assert "\U0001f389" in output, (
            "Missing party popper emoji in celebration.\n"
            "The celebration is the ONLY place where this emoji appears."
        )
        assert "crafter-ai 0.2.0 installed and healthy!" in output, (
            "Missing celebration message with version and health status."
        )
        assert "Ready to use in Claude Code." in output, (
            "Missing 'Ready to use in Claude Code.' follow-up line."
        )

    # ── SHARED ARTIFACT CONSISTENCY ───────────────────────────────────

    def test_version_consistency_across_all_displays(
        self,
        runner: CliRunner,
        candidate_version: CandidateVersion,
        successful_build_result: BuildResult,
        successful_install_result: InstallResult,
        install_pre_flight_results: list[CheckResult],
    ) -> None:
        """Version "0.2.0" must appear consistently in 4 locations.

        Feature steps (shared artifact consistency table):
          | Location        | Expected                                    |
          | Version display | 0.1.0 -> 0.2.0 (minor)                     |
          | Wheel filename  | crafter_ai-0.2.0-py3-none-any.whl           |
          | Install prompt  | Install crafter-ai 0.2.0?                   |
          | Celebration     | crafter-ai 0.2.0 installed and healthy!     |

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
        assert f"0.1.0" in output and f"{version}" in output, (
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

        # Location 4: Celebration
        assert f"crafter-ai {version} installed and healthy!" in output, (
            f"Celebration missing version {version}"
        )

    # ── CONTINUOUS STREAM VALIDATION ──────────────────────────────────

    def test_output_reads_as_continuous_stream(
        self,
        runner: CliRunner,
        candidate_version: CandidateVersion,
        successful_build_result: BuildResult,
        successful_install_result: InstallResult,
        install_pre_flight_results: list[CheckResult],
    ) -> None:
        """The output reads as a continuous top-to-bottom stream.

        Feature step: 'And the output reads as a continuous
                       top-to-bottom stream with no visual breaks'

        Validates correct phase ordering by checking that key markers
        appear in the expected sequence.
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
            "Building crafter-ai",          # Step 1: Build header
            "Pre-flight checks",            # Step 2: Build pre-flight
            "Pre-flight passed",            # Step 2: Build pre-flight summary
            "\U0001f4d0",                   # Step 3: Version display (ruler emoji)
            "0.2.0",                        # Step 3: Version number
            "Wheel built",                  # Step 4: Compilation persistent line
            "Build complete",               # Step 6: Build complete
            "Install crafter-ai 0.2.0?",    # Step 7: Install prompt
            "Installing crafter-ai",        # Step 8: Install header
            "Wheel file found",             # Step 9: Install pre-flight
            "Verifying installation",       # Step 12: Health verification
            "installed and healthy!",       # Step 13: Celebration
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

    # ── ABSENCE OF OLD TUI ARTIFACTS ──────────────────────────────────

    def test_no_version_analysis_panel(
        self,
        runner: CliRunner,
        candidate_version: CandidateVersion,
        successful_build_result: BuildResult,
        successful_install_result: InstallResult,
        install_pre_flight_results: list[CheckResult],
    ) -> None:
        """Old TUI wrapped version info in a Panel titled 'Version Analysis'.

        The new TUI uses a minimal inline display with ruler emoji.
        """
        output = invoke_full_flow(
            runner,
            candidate_version,
            successful_build_result,
            successful_install_result,
            install_pre_flight_results,
        )

        assert "Version Analysis" not in output, (
            "Old 'Version Analysis' panel title found.\n"
            "New TUI uses minimal version display with ruler emoji."
        )
        assert "Version Bump:" not in output, (
            "Old 'Version Bump:' label found.\n"
            "New TUI shows version transition as '0.1.0 -> 0.2.0 (minor)'."
        )

    def test_no_build_summary_panel(
        self,
        runner: CliRunner,
        candidate_version: CandidateVersion,
        successful_build_result: BuildResult,
        successful_install_result: InstallResult,
        install_pre_flight_results: list[CheckResult],
    ) -> None:
        """Old TUI had a 'Build Summary' panel with multi-line receipt.

        The new TUI replaces it with a single concise line.
        """
        output = invoke_full_flow(
            runner,
            candidate_version,
            successful_build_result,
            successful_install_result,
            install_pre_flight_results,
        )

        assert "Build Summary" not in output, (
            "Old 'Build Summary' panel title found.\n"
            "New TUI uses: 'Build complete: crafter_ai-0.2.0-py3-none-any.whl'"
        )

    def test_no_installation_panel(
        self,
        runner: CliRunner,
        candidate_version: CandidateVersion,
        successful_build_result: BuildResult,
        successful_install_result: InstallResult,
        install_pre_flight_results: list[CheckResult],
    ) -> None:
        """Old TUI had an 'Installation' panel header.

        The new TUI uses emoji-based phase header.
        """
        output = invoke_full_flow(
            runner,
            candidate_version,
            successful_build_result,
            successful_install_result,
            install_pre_flight_results,
        )

        # The old panel title (not the phase content)
        assert "FORGE: INSTALL" not in output, (
            "Old 'FORGE: INSTALL' panel content found.\n"
            "New TUI uses: 'Installing crafter-ai'"
        )
