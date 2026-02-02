"""
Journey 1: Build Local Candidate (forge:build-local-candidate)
===============================================================

E2E acceptance tests for the build journey - creating a pipx-compatible
candidate wheel with semantic versioning.

This test file reads like a book:
- Each scenario describes a complete user workflow
- Steps use business language, not technical jargon
- Tests drive implementation through Outside-In TDD

Test Coverage:
- US-010: Pre-flight checks validation
- US-011: Version bumping from conventional commits
- US-012: Build process with progress phases
- US-013: Wheel validation
- US-014: Success summary display
- US-015: Install prompt flow
- US-016: Force version override
- US-017: Daily sequence management
- US-018: CI/CD mode
- US-019: Auto-repair for missing dependencies

Usage:
    pytest test_journey_1_build.py -v --pspec

Port Interfaces (from component-boundaries.md):
- FileSystemPort: File operations
- GitPort: Git operations and conventional commit analysis
- BuildPort: python -m build operations
"""

import pytest
from pytest_bdd import scenarios, given, when, then, parsers

# Load all scenarios from the Journey 1 feature file
scenarios('../features/journey_1_build.feature')


# =============================================================================
# JOURNEY-SPECIFIC GIVEN STEPS
# =============================================================================

@given("a successful build has completed with wheel at \"dist/nwave-1.3.0-dev-20260201-001-py3-none-any.whl\"")
def successful_build_completed_with_wheel(test_context, mock_filesystem, mock_build):
    """Configure context for post-build scenarios."""
    test_context.build_completed = True
    test_context.build_success = True
    test_context.wheel_path = "dist/nwave-1.3.0-dev-20260201-001-py3-none-any.whl"
    mock_filesystem.setup_existing_wheel(test_context.wheel_path)
    mock_build.setup_build_success(wheel_path=test_context.wheel_path)


@given("a successful build has completed")
def successful_build_completed(test_context, mock_filesystem, mock_build):
    """Configure context for post-build scenarios (generic)."""
    test_context.build_completed = True
    test_context.build_success = True
    test_context.wheel_path = "dist/nwave-1.3.0-dev-20260201-001-py3-none-any.whl"
    mock_filesystem.setup_existing_wheel(test_context.wheel_path)


@given("the developer sees \"Install locally now? [Y/n]\"")
def developer_sees_install_prompt(test_context):
    """Developer is at install prompt."""
    test_context.prompts_shown.append("Install locally now? [Y/n]")


@given("the pre-flight check failed for missing build package")
def preflight_failed_missing_build(test_context, mock_build):
    """Configure context for auto-repair scenario."""
    mock_build.setup_unavailable()
    test_context.preflight_passed = False
    test_context.errors.append("Pre-flight check failed: build package missing")


@given("the developer has Python 3.8.10 installed")
def python_old_version(test_context):
    """Configure old Python version."""
    test_context.python_version = "3.8.10"


@given("version resolution completed with candidate \"1.3.0-dev-20260201-001\"")
def version_resolution_completed(test_context):
    """Configure version resolution results."""
    test_context.candidate_version = "1.3.0-dev-20260201-001"
    test_context.new_version = "1.3.0"
    test_context.bump_type = "MINOR"


@given("an old wheel exists at \"dist/nwave-1.2.0-py3-none-any.whl\"")
def old_wheel_exists(mock_filesystem, mock_build):
    """Configure old wheel that needs cleaning."""
    mock_filesystem.setup_existing_wheel("dist/nwave-1.2.0-py3-none-any.whl")
    mock_build.setup_old_wheels(["dist/nwave-1.2.0-py3-none-any.whl"])


@given("a wheel has been built but agents directory was excluded")
def wheel_built_missing_agents(test_context, mock_wheel_validator):
    """Configure wheel missing agents."""
    test_context.wheel_path = "dist/nwave-1.3.0-dev-20260201-001-py3-none-any.whl"
    test_context.build_completed = True
    mock_wheel_validator.setup_missing_agents()


@given("a wheel has been built but entry point is misconfigured")
def wheel_built_bad_entry_point(test_context, mock_wheel_validator):
    """Configure wheel with missing entry point."""
    test_context.wheel_path = "dist/nwave-1.3.0-dev-20260201-001-py3-none-any.whl"
    test_context.build_completed = True
    mock_wheel_validator.setup_missing_entry_points()


@given("wheel validation has passed")
def wheel_validation_passed(test_context):
    """Configure successful wheel validation."""
    test_context.wheel_validated = True
    test_context.wheel_validation_passed = True
    test_context.agent_count = 47
    test_context.command_count = 23
    test_context.template_count = 12


@given("the environment variable CI=true is set")
def ci_env_set(test_context):
    """Configure CI mode."""
    test_context.ci_mode = True
    test_context.environment_vars["CI"] = "true"


@given("the build environment is properly configured")
def build_env_configured(test_context, mock_filesystem, mock_build, mock_git):
    """Configure complete valid build environment."""
    mock_filesystem.setup_valid_repo()
    mock_build.setup_available()
    mock_build.setup_build_success()
    mock_git.setup_feature_commits()
    test_context.preflight_passed = True


@given("a candidate \"1.3.0-dev-20260201-001\" was built earlier today")
def candidate_built_earlier(test_context, mock_filesystem):
    """Configure existing candidate from today."""
    mock_filesystem.setup_existing_wheel("dist/nwave-1.3.0-dev-20260201-001-py3-none-any.whl")
    test_context.current_version = "1.3.0"


@given("yesterday's last build was \"1.3.0-dev-20260131-005\"")
def yesterdays_build(test_context, mock_filesystem):
    """Configure candidate from yesterday."""
    mock_filesystem.setup_existing_wheel("dist/nwave-1.3.0-dev-20260131-005-py3-none-any.whl")
    test_context.current_version = "1.3.0"


@given("forge:build-local-candidate has completed successfully")
def forge_build_completed(test_context, mock_filesystem):
    """Configure successful forge:build-local completion."""
    test_context.build_completed = True
    test_context.build_success = True
    test_context.wheel_path = "dist/nwave-1.3.0-dev-20260201-001-py3-none-any.whl"
    test_context.current_version = "1.3.0"
    test_context.candidate_version = "1.3.0-dev-20260201-001"
    test_context.agent_count = 47
    test_context.command_count = 23
    test_context.template_count = 12
    mock_filesystem.setup_existing_wheel(test_context.wheel_path)


# =============================================================================
# JOURNEY-SPECIFIC WHEN STEPS
# =============================================================================

@when("the build backend encounters an error \"Invalid entry point\"")
def build_backend_error(test_context, mock_build):
    """Simulate build backend error."""
    mock_build.setup_invalid_entry_point()
    raise NotImplementedError(
        "Production code needed: BuildService.build() encounters InvalidEntryPointError"
    )


# =============================================================================
# JOURNEY-SPECIFIC THEN STEPS
# =============================================================================

@then("the Python version check should pass")
def python_version_check_passes(test_context):
    """Assert Python version check passed."""
    raise NotImplementedError(
        "Production code needed: PreflightResult.python_check.passed == True"
    )


@then("the build package check should pass")
def build_package_check_passes(test_context):
    """Assert build package check passed."""
    raise NotImplementedError(
        "Production code needed: PreflightResult.build_check.passed == True"
    )


@then("the pyproject.toml check should pass")
def pyproject_check_passes(test_context):
    """Assert pyproject.toml check passed."""
    raise NotImplementedError(
        "Production code needed: PreflightResult.pyproject_check.passed == True"
    )


@then("the source directory check should pass")
def source_dir_check_passes(test_context):
    """Assert source directory check passed."""
    raise NotImplementedError(
        "Production code needed: PreflightResult.source_dir_check.passed == True"
    )


@then("the dist directory check should pass")
def dist_dir_check_passes(test_context):
    """Assert dist directory check passed."""
    raise NotImplementedError(
        "Production code needed: PreflightResult.dist_dir_check.passed == True"
    )


@then(parsers.parse('the version should be bumped to "{version}"'))
def version_bumped_to(test_context, version):
    """Assert version was bumped correctly."""
    raise NotImplementedError(
        f"Production code needed: VersionBumpResult.new_version == '{version}'"
    )


@then(parsers.parse('the candidate version should be "{version}"'))
def candidate_version_is(test_context, version):
    """Assert candidate version."""
    raise NotImplementedError(
        f"Production code needed: VersionBumpResult.candidate_version == '{version}'"
    )


@then("the build process should complete successfully")
def build_completes_successfully(test_context):
    """Assert build completed successfully."""
    raise NotImplementedError(
        "Production code needed: BuildResult.success == True"
    )


@then(parsers.parse('the wheel should be created at "{wheel_path}"'))
def wheel_created_at(test_context, wheel_path):
    """Assert wheel was created at expected path."""
    raise NotImplementedError(
        f"Production code needed: BuildResult.wheel_path == '{wheel_path}'"
    )


@then(parsers.parse("the wheel should contain {agents:d} agents, {commands:d} commands, and {templates:d} templates"))
def wheel_contains_components(test_context, agents, commands, templates):
    """Assert wheel contains expected components."""
    raise NotImplementedError(
        f"Production code needed: WheelValidation shows {agents} agents, {commands} commands, {templates} templates"
    )


@then(parsers.parse('the success summary should display "{header}"'))
def success_summary_displays(test_context, header):
    """Assert success summary header."""
    raise NotImplementedError(
        f"Production code needed: SummaryDisplay.header == '{header}'"
    )


@then(parsers.parse('the developer should see "{prompt}"'))
def developer_sees_prompt(test_context, prompt):
    """Assert developer sees expected prompt."""
    raise NotImplementedError(
        f"Production code needed: CLI shows prompt '{prompt}'"
    )


@then(parsers.parse('the install command should run "{command}"'))
def install_command_runs(test_context, command):
    """Assert install command runs."""
    raise NotImplementedError(
        f"Production code needed: InstallService executes '{command}'"
    )


@then("the forge:install-local-candidate journey should continue")
def install_journey_continues(test_context):
    """Assert install journey continues."""
    raise NotImplementedError(
        "Production code needed: Transition to forge:install-local-candidate"
    )


@then("the manual install command should be displayed")
def manual_install_displayed(test_context):
    """Assert manual install command shown."""
    raise NotImplementedError(
        "Production code needed: CLI displays manual install command"
    )


@then(parsers.parse('the command should be "{command}"'))
def command_is(test_context, command):
    """Assert specific command is shown."""
    raise NotImplementedError(
        f"Production code needed: Displayed command == '{command}'"
    )


@then(parsers.parse('the command should show "{command}"'))
def command_shows(test_context, command):
    """Assert command shows specific text."""
    raise NotImplementedError(
        f"Production code needed: Displayed command contains '{command}'"
    )


@then(parsers.parse('the development mode alternative "{command}" should be shown'))
def dev_mode_alternative_shown(test_context, command):
    """Assert development mode alternative is shown."""
    raise NotImplementedError(
        f"Production code needed: CLI shows dev mode alternative '{command}'"
    )


@then(parsers.parse('the prompt should ask "{prompt}"'))
def prompt_asks(test_context, prompt):
    """Assert prompt asks expected question."""
    raise NotImplementedError(
        f"Production code needed: CLI shows prompt '{prompt}'"
    )


@then(parsers.parse('the installer should run "{command}"'))
def installer_runs_command(test_context, command):
    """Assert installer runs command."""
    raise NotImplementedError(
        f"Production code needed: Installer executes '{command}'"
    )


@then(parsers.parse('a spinner should show "{message}"'))
def spinner_shows(test_context, message):
    """Assert spinner shows message."""
    raise NotImplementedError(
        f"Production code needed: CLI spinner shows '{message}'"
    )


@then(parsers.parse('the message should display "{message}"'))
def message_displays(test_context, message):
    """Assert message is displayed."""
    raise NotImplementedError(
        f"Production code needed: CLI displays '{message}'"
    )


@then(parsers.parse('the message should show "{message}"'))
def message_shows(test_context, message):
    """Assert message shows specific text."""
    raise NotImplementedError(
        f"Production code needed: CLI shows '{message}'"
    )


@then("pre-flight checks should resume")
def preflight_resumes(test_context):
    """Assert pre-flight checks resume."""
    raise NotImplementedError(
        "Production code needed: PreflightService.resume()"
    )


@then("the build should abort")
def build_aborts(test_context):
    """Assert build aborts."""
    raise NotImplementedError(
        "Production code needed: BuildService.abort() called"
    )


@then("upgrade suggestions should be provided")
def upgrade_suggestions_provided(test_context):
    """Assert upgrade suggestions are provided."""
    raise NotImplementedError(
        "Production code needed: CLI displays upgrade suggestions"
    )


@then(parsers.parse('the bump type should be "{bump_type}"'))
def bump_type_is(test_context, bump_type):
    """Assert bump type."""
    raise NotImplementedError(
        f"Production code needed: VersionBumpResult.bump_type == '{bump_type}'"
    )


@then(parsers.parse('the new version should be "{version}"'))
def new_version_is(test_context, version):
    """Assert new version."""
    raise NotImplementedError(
        f"Production code needed: VersionBumpResult.new_version == '{version}'"
    )


@then("a phase table should display")
def phase_table_displays(test_context):
    """Assert phase table is displayed."""
    raise NotImplementedError(
        "Production code needed: CLI displays build phase table"
    )


@then(parsers.parse('the phase "{phase}" should show progress then checkmark'))
def phase_shows_progress_then_checkmark(test_context, phase):
    """Assert phase shows progress then checkmark."""
    raise NotImplementedError(
        f"Production code needed: Phase '{phase}' shows spinner then checkmark"
    )


@then(parsers.parse('the phase "{phase}" should show "{detail}"'))
def phase_shows_detail(test_context, phase, detail):
    """Assert phase shows specific detail."""
    raise NotImplementedError(
        f"Production code needed: Phase '{phase}' shows '{detail}'"
    )


@then("all phases should complete with checkmarks")
def all_phases_complete(test_context):
    """Assert all phases complete with checkmarks."""
    raise NotImplementedError(
        "Production code needed: All BuildPhases show checkmarks"
    )


@then("the build duration should be displayed")
def build_duration_displayed(test_context):
    """Assert build duration is displayed."""
    raise NotImplementedError(
        "Production code needed: BuildResult.duration is displayed"
    )


@then("the old wheel should be removed")
def old_wheel_removed(test_context, mock_build):
    """Assert old wheel was removed."""
    raise NotImplementedError(
        "Production code needed: BuildService.clean_dist() removed old wheels"
    )


@then(parsers.parse('the phase should show "{phase}"'))
def phase_shows(test_context, phase):
    """Assert phase shows specific status."""
    raise NotImplementedError(
        f"Production code needed: Phase shows '{phase}'"
    )


@then(parsers.parse('the phase "{phase}" should show failure'))
def phase_shows_failure(test_context, phase):
    """Assert phase shows failure."""
    raise NotImplementedError(
        f"Production code needed: Phase '{phase}' shows failure icon"
    )


@then(parsers.parse('the error message should display "{message}"'))
def error_message_displays(test_context, message):
    """Assert error message is displayed."""
    raise NotImplementedError(
        f"Production code needed: CLI displays error '{message}'"
    )


@then("a suggested fix should be provided")
def suggested_fix_provided(test_context):
    """Assert suggested fix is provided."""
    raise NotImplementedError(
        "Production code needed: CLI displays suggested fix"
    )


@then("the wheel filename should be displayed")
def wheel_filename_displayed(test_context):
    """Assert wheel filename is displayed."""
    raise NotImplementedError(
        "Production code needed: WheelValidation displays filename"
    )


@then("the validation table should show all checks")
def validation_table_shows_checks(test_context):
    """Assert validation table shows all checks."""
    raise NotImplementedError(
        "Production code needed: WheelValidation displays check table"
    )


@then(parsers.parse('"{check}" should pass with checkmark'))
def check_passes_with_checkmark(test_context, check):
    """Assert check passes with checkmark."""
    raise NotImplementedError(
        f"Production code needed: WheelValidation.'{check}' shows checkmark"
    )


@then(parsers.parse('"{check}" should pass with "{detail}"'))
def check_passes_with_detail(test_context, check, detail):
    """Assert check passes with detail."""
    raise NotImplementedError(
        f"Production code needed: WheelValidation.'{check}' shows '{detail}'"
    )


@then(parsers.parse('the final status should show "{status}"'))
def final_status_shows(test_context, status):
    """Assert final status shows expected text."""
    raise NotImplementedError(
        f"Production code needed: Final status == '{status}'"
    )


@then(parsers.parse('"{check}" should show failure with "{detail}"'))
def check_shows_failure(test_context, check, detail):
    """Assert check shows failure with detail."""
    raise NotImplementedError(
        f"Production code needed: WheelValidation.'{check}' shows failure with '{detail}'"
    )


@then("the validation should fail")
def validation_fails(test_context):
    """Assert validation fails."""
    raise NotImplementedError(
        "Production code needed: WheelValidation.passed == False"
    )


@then("error should suggest checking pyproject.toml include patterns")
def error_suggests_pyproject_patterns(test_context):
    """Assert error suggests checking pyproject.toml."""
    raise NotImplementedError(
        "Production code needed: Error message mentions pyproject.toml patterns"
    )


@then("error should show where to fix in pyproject.toml")
def error_shows_pyproject_fix(test_context):
    """Assert error shows pyproject.toml fix location."""
    raise NotImplementedError(
        "Production code needed: Error message shows pyproject.toml fix"
    )


@then(parsers.parse('the header should show "{header}"'))
def header_shows(test_context, header):
    """Assert header shows expected text."""
    raise NotImplementedError(
        f"Production code needed: Header == '{header}'"
    )


@then(parsers.parse('the celebration message should show "{message}"'))
def celebration_message_shows(test_context, message):
    """Assert celebration message."""
    raise NotImplementedError(
        f"Production code needed: Celebration message == '{message}'"
    )


@then(parsers.parse('the artifact table should show wheel path "{wheel_path}"'))
def artifact_table_shows_wheel_path(test_context, wheel_path):
    """Assert artifact table shows wheel path."""
    raise NotImplementedError(
        f"Production code needed: Artifact table shows '{wheel_path}'"
    )


@then("the artifact table should show wheel size and timestamp")
def artifact_table_shows_size_timestamp(test_context):
    """Assert artifact table shows size and timestamp."""
    raise NotImplementedError(
        "Production code needed: Artifact table shows size and timestamp"
    )


@then(parsers.parse("the contents table should show {agents:d} agents, {commands:d} commands, and {templates:d} templates"))
def contents_table_shows_counts(test_context, agents, commands, templates):
    """Assert contents table shows component counts."""
    raise NotImplementedError(
        f"Production code needed: Contents table shows {agents}, {commands}, {templates}"
    )


@then(parsers.parse('the wheel path should be "{wheel_path}"'))
def wheel_path_is(test_context, wheel_path):
    """Assert wheel path."""
    raise NotImplementedError(
        f"Production code needed: wheel_path == '{wheel_path}'"
    )


@then("the wheel file should exist at that path")
def wheel_file_exists(test_context):
    """Assert wheel file exists."""
    raise NotImplementedError(
        "Production code needed: FileSystem.exists(wheel_path) == True"
    )


@then("no interactive prompts should appear")
def no_interactive_prompts(test_context):
    """Assert no interactive prompts in CI mode."""
    raise NotImplementedError(
        "Production code needed: CI mode suppresses prompts"
    )


@then("the install prompt should be skipped")
def install_prompt_skipped(test_context):
    """Assert install prompt is skipped."""
    raise NotImplementedError(
        "Production code needed: Install prompt skipped in CI/--no-prompt mode"
    )


@then("the build should complete silently")
def build_completes_silently(test_context):
    """Assert build completes silently."""
    raise NotImplementedError(
        "Production code needed: Build completes without verbose output"
    )


@then("the build should complete normally")
def build_completes_normally(test_context):
    """Assert build completes normally."""
    raise NotImplementedError(
        "Production code needed: BuildResult.success == True"
    )


@then("the wheel path should be printed for scripting")
def wheel_path_printed_for_scripting(test_context):
    """Assert wheel path is printed for scripting."""
    raise NotImplementedError(
        "Production code needed: Only wheel path output for scripting"
    )


@then("the install should proceed automatically without prompting")
def install_proceeds_automatically(test_context):
    """Assert install proceeds automatically."""
    raise NotImplementedError(
        "Production code needed: Install runs without prompts"
    )


@then("the full forge:install-local-candidate flow should complete")
def full_install_flow_completes(test_context):
    """Assert full install flow completes."""
    raise NotImplementedError(
        "Production code needed: Complete install-local-candidate journey"
    )


@then(parsers.parse('a warning should display "{warning}"'))
def warning_displays(test_context, warning):
    """Assert warning is displayed."""
    raise NotImplementedError(
        f"Production code needed: Warning '{warning}' displayed"
    )


@then("the build should proceed with the current version as candidate")
def build_proceeds_with_current_version(test_context):
    """Assert build proceeds with current version."""
    raise NotImplementedError(
        "Production code needed: Build uses current version as candidate"
    )


@then(parsers.parse('the version in pre-flight should be "{version}"'))
def preflight_version_is(test_context, version):
    """Assert pre-flight shows correct version."""
    raise NotImplementedError(
        f"Production code needed: PreflightResult.version == '{version}'"
    )


@then(parsers.parse('the version in wheel filename should be "{version}"'))
def wheel_filename_version_is(test_context, version):
    """Assert wheel filename has correct version."""
    raise NotImplementedError(
        f"Production code needed: Wheel filename contains '{version}'"
    )


@then(parsers.parse('the version in summary should be "{version}"'))
def summary_version_is(test_context, version):
    """Assert summary shows correct version."""
    raise NotImplementedError(
        f"Production code needed: Summary.version == '{version}'"
    )


@then("all versions should derive from pyproject.toml")
def versions_derive_from_pyproject(test_context):
    """Assert all versions derive from pyproject.toml."""
    raise NotImplementedError(
        "Production code needed: All versions consistent with pyproject.toml"
    )


@then(parsers.parse("the agent count in validation should be {count:d}"))
def validation_agent_count_is(test_context, count):
    """Assert validation agent count."""
    raise NotImplementedError(
        f"Production code needed: WheelValidation.agent_count == {count}"
    )


@then(parsers.parse("the agent count in summary should be {count:d}"))
def summary_agent_count_is(test_context, count):
    """Assert summary agent count."""
    raise NotImplementedError(
        f"Production code needed: Summary.agent_count == {count}"
    )


@then("both should match actual files bundled in wheel")
def counts_match_actual_files(test_context):
    """Assert counts match actual files."""
    raise NotImplementedError(
        "Production code needed: Counts match actual wheel contents"
    )


@then("the wheel path in summary should match wheel path in install prompt")
def wheel_paths_match(test_context):
    """Assert wheel paths match."""
    raise NotImplementedError(
        "Production code needed: Summary.wheel_path == InstallPrompt.wheel_path"
    )


@then("the wheel path should point to an existing file")
def wheel_path_exists(test_context):
    """Assert wheel path exists."""
    raise NotImplementedError(
        "Production code needed: FileSystem.exists(wheel_path) == True"
    )
