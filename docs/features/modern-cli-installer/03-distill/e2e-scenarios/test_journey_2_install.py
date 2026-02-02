"""
Journey 2: Install Local Candidate (forge:install-local-candidate)
===================================================================

E2E acceptance tests for the install journey - installing and validating
a locally-built nWave candidate for release preparation.

This test file reads like a book:
- Each scenario describes a complete user workflow
- Steps use business language, not technical jargon
- Tests drive implementation through Outside-In TDD

Test Coverage:
- US-020: Pre-flight checks for install
- US-021: Release readiness validation
- US-022: Install candidate via pipx
- US-023: Doctor verification
- US-024: Release report display
- US-025: Auto-chain to build-local
- US-026: Multiple wheel selection
- US-027: CI/CD mode
- US-028: JSON output format
- US-029: Strict mode

Usage:
    pytest test_journey_2_install.py -v --pspec

Port Interfaces (from component-boundaries.md):
- FileSystemPort: File operations
- PipxPort: pipx install/uninstall operations
- BuildPort: Wheel validation
"""

import pytest
from pytest_bdd import scenarios, given, when, then, parsers

# Load all scenarios from the Journey 2 feature file
scenarios('../features/journey_2_install.feature')


# =============================================================================
# JOURNEY-SPECIFIC GIVEN STEPS
# =============================================================================

@given("the wheel has valid metadata and entry points")
def wheel_valid_metadata(mock_wheel_validator):
    """Configure wheel with valid metadata."""
    mock_wheel_validator.fail_validation = False
    mock_wheel_validator.fail_entry_points = False


@given(parsers.parse('CHANGELOG.md has an entry for version "{version}"'))
def changelog_has_entry(mock_filesystem, version):
    """Configure CHANGELOG with version entry."""
    mock_filesystem.files["CHANGELOG.md"] = f"""
# Changelog

## [{version}] - 2026-02-01

### Added
- New Luna agent for UX design
- Enhanced build journey with progress tracking

### Fixed
- Typo in config loading
"""


@given(parsers.parse('CHANGELOG.md has NO entry for version "{version}"'))
def changelog_missing_entry(mock_filesystem, version):
    """Configure CHANGELOG without version entry."""
    mock_filesystem.files["CHANGELOG.md"] = """
# Changelog

## [1.2.0] - 2026-01-15

### Added
- Initial release
"""


@given("a wheel exists with valid metadata")
def wheel_with_valid_metadata(test_context, mock_filesystem, mock_wheel_validator):
    """Configure wheel with valid metadata."""
    test_context.wheel_path = "dist/nwave-1.3.0-dev-20260201-001-py3-none-any.whl"
    mock_filesystem.setup_existing_wheel(test_context.wheel_path)
    mock_wheel_validator.fail_validation = False


@given("the wheel includes LICENSE and README.md")
def wheel_includes_license_readme(mock_filesystem):
    """Configure wheel with LICENSE and README."""
    mock_filesystem.files["LICENSE"] = "MIT License..."
    mock_filesystem.files["README.md"] = "# nWave Framework..."


@given("a previous version of nwave is installed")
def previous_nwave_installed(mock_pipx, mock_filesystem):
    """Configure previous nwave installation."""
    mock_pipx.setup_existing_nwave("1.2.0")
    mock_filesystem.setup_installed_nwave(version="1.2.0")


@given("release readiness has passed")
def release_readiness_passed(test_context):
    """Configure release readiness as passed."""
    test_context.release_readiness_ran = True
    test_context.release_readiness_status = "READY FOR PYPI"


@given("the wheel has been installed")
def wheel_installed(test_context, mock_pipx):
    """Configure wheel as installed."""
    test_context.install_completed = True
    test_context.install_success = True
    mock_pipx.installed_packages["nwave"] = "1.3.0-dev-20260201-001"


@given("the candidate has been installed")
def candidate_installed_setup(test_context, mock_pipx, mock_filesystem):
    """Configure candidate as installed."""
    test_context.install_completed = True
    test_context.install_success = True
    mock_pipx.installed_packages["nwave"] = "1.3.0-dev-20260201-001"
    mock_filesystem.setup_installed_nwave(version="1.3.0-dev-20260201-001", agent_count=47)


@given("doctor verification has passed")
def doctor_passed(test_context):
    """Configure doctor verification as passed."""
    test_context.doctor_ran = True
    test_context.doctor_status = "HEALTHY"
    test_context.agent_count = 47
    test_context.command_count = 23
    test_context.template_count = 12


@given("the pre-flight check failed for no wheel")
def preflight_failed_no_wheel(test_context, mock_filesystem):
    """Configure pre-flight failure for no wheel."""
    test_context.preflight_passed = False
    # Ensure no wheel exists
    to_remove = [f for f in mock_filesystem.files if f.endswith(".whl")]
    for f in to_remove:
        del mock_filesystem.files[f]


@given(parsers.parse('the developer sees "{prompt}"'))
def developer_sees_message(test_context, prompt):
    """Developer sees specific prompt."""
    test_context.prompts_shown.append(prompt)


@given("multiple wheels exist in dist/:")
def multiple_wheels_exist(test_context, mock_filesystem, request):
    """Configure multiple wheels in dist directory."""
    # This will be called with the data table from the scenario
    mock_filesystem.setup_multiple_wheels([
        "dist/nwave-1.2.0-py3-none-any.whl",
        "dist/nwave-1.3.0-dev-20260201-001-py3-none-any.whl",
        "dist/nwave-1.3.0-dev-20260201-002-py3-none-any.whl",
    ])


@given("the developer sees multiple wheel options numbered 1-3")
def multiple_wheel_options(test_context):
    """Developer sees numbered wheel options."""
    test_context.prompts_shown.append("Select wheel to install [1-3]:")


@given("the developer sees multiple wheel options")
def multiple_wheel_options_generic(test_context):
    """Developer sees wheel options."""
    test_context.prompts_shown.append("Multiple wheels found")


@given("a wheel exists with complete metadata")
def wheel_with_complete_metadata(test_context, mock_filesystem, mock_wheel_validator):
    """Configure wheel with complete metadata."""
    test_context.wheel_path = "dist/nwave-1.3.0-dev-20260201-001-py3-none-any.whl"
    mock_filesystem.setup_existing_wheel(test_context.wheel_path)
    mock_wheel_validator.fail_validation = False
    mock_wheel_validator.fail_metadata = False


@given("a wheel exists with nw CLI entry point")
def wheel_with_entry_point(test_context, mock_filesystem, mock_wheel_validator):
    """Configure wheel with entry point."""
    test_context.wheel_path = "dist/nwave-1.3.0-dev-20260201-001-py3-none-any.whl"
    mock_filesystem.setup_existing_wheel(test_context.wheel_path)
    mock_wheel_validator.fail_entry_points = False


@given(parsers.parse('a wheel exists with PEP 440 compliant version "{version}"'))
def wheel_with_pep440_version(test_context, mock_filesystem, version):
    """Configure wheel with PEP 440 version."""
    test_context.wheel_path = f"dist/nwave-{version.replace('.', '-')}-py3-none-any.whl"
    mock_filesystem.setup_existing_wheel(test_context.wheel_path)
    test_context.candidate_version = version


@given("the CHANGELOG warning is displayed")
def changelog_warning_displayed(test_context):
    """Configure CHANGELOG warning state."""
    test_context.prompts_shown.append("CHANGELOG: No recent entry")


@given("a wheel exists with invalid metadata")
def wheel_with_invalid_metadata(test_context, mock_filesystem, mock_wheel_validator):
    """Configure wheel with invalid metadata."""
    test_context.wheel_path = "dist/nwave-1.3.0-dev-20260201-001-py3-none-any.whl"
    mock_filesystem.setup_existing_wheel(test_context.wheel_path)
    mock_wheel_validator.fail_validation = True
    mock_wheel_validator.fail_message = "Invalid metadata"


@given(parsers.parse('the wheel version was "{version}"'))
def wheel_version_was(test_context, version):
    """Set wheel version in context."""
    test_context.candidate_version = version


@given("But agent files were not copied to ~/.claude")
def agents_not_copied(mock_filesystem):
    """Configure missing agent files."""
    mock_filesystem.file_counts["~/.claude/agents/nw/agents"] = 0


@given('But "nw --version" shows a different version')
def nw_shows_different_version(test_context):
    """Configure version mismatch."""
    test_context.errors.append("Version mismatch detected")


@given("a valid wheel file exists at \"dist/nwave-1.3.0-dev-20260201-001-py3-none-any.whl\"")
def valid_wheel_exists(test_context, mock_filesystem, mock_wheel_validator):
    """Configure valid wheel."""
    test_context.wheel_path = "dist/nwave-1.3.0-dev-20260201-001-py3-none-any.whl"
    mock_filesystem.setup_existing_wheel(test_context.wheel_path)
    mock_wheel_validator.fail_validation = False


@given(parsers.parse("CI=true is set"))
def ci_true_set(test_context):
    """Configure CI mode."""
    test_context.ci_mode = True
    test_context.environment_vars["CI"] = "true"


@given("multiple wheels exist in dist/")
def multiple_wheels_exist_generic(mock_filesystem):
    """Configure multiple wheels."""
    mock_filesystem.setup_multiple_wheels([
        "dist/nwave-1.2.0-py3-none-any.whl",
        "dist/nwave-1.3.0-dev-20260201-001-py3-none-any.whl",
    ])


@given("a wheel exists without CHANGELOG entry")
def wheel_without_changelog(test_context, mock_filesystem, mock_wheel_validator):
    """Configure wheel without CHANGELOG entry."""
    test_context.wheel_path = "dist/nwave-1.3.0-dev-20260201-001-py3-none-any.whl"
    mock_filesystem.setup_existing_wheel(test_context.wheel_path)
    mock_filesystem.files["CHANGELOG.md"] = "# Changelog\n\n## [1.2.0] - Old"


@given("a wheel exists with all requirements met")
def wheel_with_all_requirements(test_context, mock_filesystem, mock_wheel_validator):
    """Configure wheel meeting all requirements."""
    test_context.wheel_path = "dist/nwave-1.3.0-dev-20260201-001-py3-none-any.whl"
    mock_filesystem.setup_existing_wheel(test_context.wheel_path)
    mock_filesystem.files["CHANGELOG.md"] = "## [1.3.0] - 2026-02-01"
    mock_filesystem.files["LICENSE"] = "MIT"
    mock_filesystem.files["README.md"] = "# nWave"
    mock_wheel_validator.fail_validation = False


@given("forge:install-local-candidate has completed successfully")
def forge_install_completed(test_context, mock_filesystem, mock_pipx):
    """Configure successful install completion."""
    test_context.install_completed = True
    test_context.install_success = True
    test_context.candidate_version = "1.3.0-dev-20260201-001"
    test_context.agent_count = 47
    test_context.command_count = 23
    test_context.template_count = 12
    test_context.doctor_ran = True
    test_context.doctor_status = "HEALTHY"
    mock_pipx.installed_packages["nwave"] = "1.3.0-dev-20260201-001"
    mock_filesystem.setup_installed_nwave(version="1.3.0-dev-20260201-001")


@given("forge:build-local has completed with wheel at \"dist/nwave-1.3.0-dev-20260201-001-py3-none-any.whl\"")
def forge_build_completed(test_context, mock_filesystem):
    """Configure forge:build-local completion."""
    test_context.build_completed = True
    test_context.wheel_path = "dist/nwave-1.3.0-dev-20260201-001-py3-none-any.whl"
    mock_filesystem.setup_existing_wheel(test_context.wheel_path)


@given("forge:install-local-candidate doctor verification runs")
def doctor_verification_runs(test_context):
    """Configure doctor verification state."""
    test_context.doctor_ran = True


# =============================================================================
# JOURNEY-SPECIFIC WHEN STEPS
# =============================================================================

@when("the release readiness validation runs")
def release_readiness_runs(test_context):
    """Run release readiness validation."""
    raise NotImplementedError(
        "Production code needed: Execute ReleaseReadinessService.validate()"
    )


@when("the install process runs")
def install_process_runs(test_context):
    """Run install process."""
    raise NotImplementedError(
        "Production code needed: Execute InstallService.install()"
    )


@when("the symlink verification runs")
def symlink_verification_runs(test_context):
    """Run symlink verification."""
    raise NotImplementedError(
        "Production code needed: Execute InstallService.verify_symlink()"
    )


@when("a dependency version conflict occurs")
def dependency_conflict_occurs(test_context, mock_pipx):
    """Simulate dependency conflict."""
    mock_pipx.setup_dependency_conflict()
    raise NotImplementedError(
        "Production code needed: InstallService encounters DependencyConflictError"
    )


@when("the release report displays")
def release_report_displays(test_context):
    """Display release report."""
    raise NotImplementedError(
        "Production code needed: Display release report via CLI adapter"
    )


# =============================================================================
# JOURNEY-SPECIFIC THEN STEPS
# =============================================================================

@then("the release readiness validation should pass with \"READY FOR PYPI\"")
def release_readiness_passes(test_context):
    """Assert release readiness passed."""
    raise NotImplementedError(
        "Production code needed: ReleaseReadinessResult.status == 'READY FOR PYPI'"
    )


@then("the candidate should be installed via pipx")
def candidate_installed_via_pipx(test_context):
    """Assert candidate was installed via pipx."""
    raise NotImplementedError(
        "Production code needed: PipxPort.install() called with wheel"
    )


@then("the doctor verification should show \"HEALTHY\" status")
def doctor_shows_healthy(test_context):
    """Assert doctor shows healthy status."""
    raise NotImplementedError(
        "Production code needed: DoctorResult.status == 'HEALTHY'"
    )


@then("the release report should display \"FORGE: CANDIDATE INSTALLED\"")
def release_report_displays_header(test_context):
    """Assert release report header."""
    raise NotImplementedError(
        "Production code needed: ReleaseReport.header == 'FORGE: CANDIDATE INSTALLED'"
    )


@then("the test checklist should be shown")
def test_checklist_shown(test_context):
    """Assert test checklist is shown."""
    raise NotImplementedError(
        "Production code needed: ReleaseReport.test_checklist displayed"
    )


@then(parsers.parse('"{check}" should pass with checkmark'))
def check_passes_checkmark(test_context, check):
    """Assert check passes with checkmark."""
    raise NotImplementedError(
        f"Production code needed: ReleaseReadiness.'{check}' shows checkmark"
    )


@then(parsers.parse('"{check}" should pass with "{detail}"'))
def check_passes_detail(test_context, check, detail):
    """Assert check passes with detail."""
    raise NotImplementedError(
        f"Production code needed: '{check}' shows '{detail}'"
    )


@then(parsers.parse('the status should show "{status}"'))
def status_shows(test_context, status):
    """Assert status shows expected text."""
    raise NotImplementedError(
        f"Production code needed: Status == '{status}'"
    )


@then(parsers.parse('"{check}" should show the install path'))
def check_shows_install_path(test_context, check):
    """Assert check shows install path."""
    raise NotImplementedError(
        f"Production code needed: '{check}' displays install path"
    )


@then(parsers.parse('"{check}" should show "{detail}"'))
def check_shows_detail(test_context, check, detail):
    """Assert check shows specific detail."""
    raise NotImplementedError(
        f"Production code needed: '{check}' shows '{detail}'"
    )


@then("the Python version check should verify 3.10+")
def python_version_check_verify(test_context):
    """Assert Python version check verifies 3.10+."""
    raise NotImplementedError(
        "Production code needed: PreflightResult.python_check verifies >= 3.10"
    )


@then("the pipx check should pass")
def pipx_check_passes(test_context):
    """Assert pipx check passed."""
    raise NotImplementedError(
        "Production code needed: PreflightResult.pipx_check.passed == True"
    )


@then("the permission check should pass")
def permission_check_passes(test_context):
    """Assert permission check passed."""
    raise NotImplementedError(
        "Production code needed: PreflightResult.permission_check.passed == True"
    )


@then("the wheel existence check should pass")
def wheel_existence_check_passes(test_context):
    """Assert wheel existence check passed."""
    raise NotImplementedError(
        "Production code needed: PreflightResult.wheel_check.passed == True"
    )


@then("the wheel format check should pass")
def wheel_format_check_passes(test_context):
    """Assert wheel format check passed."""
    raise NotImplementedError(
        "Production code needed: PreflightResult.wheel_format_check.passed == True"
    )


@then(parsers.parse('instructions should show "{instructions}"'))
def instructions_show(test_context, instructions):
    """Assert instructions are shown."""
    raise NotImplementedError(
        f"Production code needed: CLI shows '{instructions}'"
    )


@then("permission fix suggestions should be provided")
def permission_fix_suggestions(test_context):
    """Assert permission fix suggestions provided."""
    raise NotImplementedError(
        "Production code needed: CLI shows permission fix suggestions"
    )


@then("NWAVE_INSTALL_PATH alternative should be mentioned")
def nwave_install_path_mentioned(test_context):
    """Assert NWAVE_INSTALL_PATH alternative mentioned."""
    raise NotImplementedError(
        "Production code needed: CLI mentions NWAVE_INSTALL_PATH"
    )


@then("forge:build-local should run")
def forge_build_local_runs(test_context):
    """Assert forge:build-local runs."""
    raise NotImplementedError(
        "Production code needed: Transition to forge:build-local journey"
    )


@then("after successful build, install-local-candidate should resume")
def install_resumes_after_build(test_context):
    """Assert install resumes after build."""
    raise NotImplementedError(
        "Production code needed: Journey resumes after build completion"
    )


@then("the install should abort")
def install_aborts(test_context):
    """Assert install aborts."""
    raise NotImplementedError(
        "Production code needed: InstallService.abort() called"
    )


@then("the list of wheels should be shown with numbers")
def wheel_list_with_numbers(test_context):
    """Assert wheel list shown with numbers."""
    raise NotImplementedError(
        "Production code needed: CLI shows numbered wheel list"
    )


@then("the second wheel should be selected")
def second_wheel_selected(test_context):
    """Assert second wheel selected."""
    raise NotImplementedError(
        "Production code needed: Selected wheel index == 1"
    )


@then("the installation should continue")
def installation_continues(test_context):
    """Assert installation continues."""
    raise NotImplementedError(
        "Production code needed: Install proceeds with selected wheel"
    )


@then("the installation should be cancelled")
def installation_cancelled(test_context):
    """Assert installation cancelled."""
    raise NotImplementedError(
        "Production code needed: Installation cancelled, no changes"
    )


@then("twine check should execute against the wheel")
def twine_check_executes(test_context):
    """Assert twine check executes."""
    raise NotImplementedError(
        "Production code needed: TwinePort.check() called with wheel"
    )


@then(parsers.parse('"{check}" should show warning with "{detail}"'))
def check_shows_warning(test_context, check, detail):
    """Assert check shows warning."""
    raise NotImplementedError(
        f"Production code needed: '{check}' shows warning '{detail}'"
    )


@then("the warning should be noted in the release report")
def warning_noted_in_report(test_context):
    """Assert warning noted in report."""
    raise NotImplementedError(
        "Production code needed: ReleaseReport.warnings includes CHANGELOG warning"
    )


@then(parsers.parse('"{check}" should fail with "{detail}"'))
def check_fails_with_detail(test_context, check, detail):
    """Assert check fails with detail."""
    raise NotImplementedError(
        f"Production code needed: '{check}' shows failure '{detail}'"
    )


@then("fix instructions should mention pyproject.toml")
def fix_mentions_pyproject(test_context):
    """Assert fix mentions pyproject.toml."""
    raise NotImplementedError(
        "Production code needed: Error mentions pyproject.toml"
    )


@then(parsers.parse('the phase "{phase}" should show progress then checkmark'))
def phase_progress_checkmark(test_context, phase):
    """Assert phase shows progress then checkmark."""
    raise NotImplementedError(
        f"Production code needed: Phase '{phase}' shows spinner then checkmark"
    )


@then("the install duration should be displayed")
def install_duration_displayed(test_context):
    """Assert install duration displayed."""
    raise NotImplementedError(
        "Production code needed: InstallResult.duration displayed"
    )


@then("the new version should be installed")
def new_version_installed(test_context):
    """Assert new version installed."""
    raise NotImplementedError(
        "Production code needed: PipxPort.list() shows new version"
    )


@then("the --force flag should ensure replacement of existing install")
def force_flag_ensures_replacement(test_context):
    """Assert force flag is used."""
    raise NotImplementedError(
        "Production code needed: PipxPort.install() called with force=True"
    )


@then(parsers.parse('"{command}" should return a valid path'))
def command_returns_valid_path(test_context, command):
    """Assert command returns valid path."""
    raise NotImplementedError(
        f"Production code needed: '{command}' returns valid path"
    )


@then("the error should display the dependency issue")
def error_displays_dependency(test_context):
    """Assert error displays dependency issue."""
    raise NotImplementedError(
        "Production code needed: Error shows dependency conflict details"
    )


@then("suggested fixes should be provided")
def suggested_fixes_provided(test_context):
    """Assert suggested fixes provided."""
    raise NotImplementedError(
        "Production code needed: CLI shows suggested fixes"
    )


@then(parsers.parse('"{check}" should verify the install path exists'))
def check_verifies_install_path(test_context, check):
    """Assert check verifies install path."""
    raise NotImplementedError(
        f"Production code needed: '{check}' verifies install path exists"
    )


@then(parsers.parse('"{check}" should count files in the install path agents directory'))
def check_counts_agent_files(test_context, check):
    """Assert check counts agent files."""
    raise NotImplementedError(
        f"Production code needed: '{check}' counts files in agents directory"
    )


@then(parsers.parse("the count should be {count:d}"))
def count_should_be(test_context, count):
    """Assert count is expected value."""
    raise NotImplementedError(
        f"Production code needed: Count == {count}"
    )


@then("the count should match the wheel bundled count")
def count_matches_wheel(test_context):
    """Assert count matches wheel bundled count."""
    raise NotImplementedError(
        "Production code needed: Installed count == Wheel bundled count"
    )


@then(parsers.parse('"{check}" should verify "nw --version" output'))
def check_verifies_nw_version(test_context, check):
    """Assert check verifies nw --version."""
    raise NotImplementedError(
        f"Production code needed: '{check}' verifies nw --version output"
    )


@then(parsers.parse('the output should match "{version}"'))
def output_matches_version(test_context, version):
    """Assert output matches version."""
    raise NotImplementedError(
        f"Production code needed: Version output matches '{version}'"
    )


@then("the nw --version output should be displayed")
def nw_version_displayed(test_context):
    """Assert nw --version output displayed."""
    raise NotImplementedError(
        "Production code needed: CLI displays nw --version output"
    )


@then(parsers.parse('it should show "{text}"'))
def it_shows_text(test_context, text):
    """Assert output shows text."""
    raise NotImplementedError(
        f"Production code needed: Output shows '{text}'"
    )


@then("repair instructions should be provided")
def repair_instructions_provided(test_context):
    """Assert repair instructions provided."""
    raise NotImplementedError(
        "Production code needed: CLI shows repair instructions"
    )


@then("the wheel version vs installed version should be shown")
def version_comparison_shown(test_context):
    """Assert version comparison shown."""
    raise NotImplementedError(
        "Production code needed: Error shows wheel vs installed version"
    )


@then("reinstall instructions should be provided")
def reinstall_instructions_provided(test_context):
    """Assert reinstall instructions provided."""
    raise NotImplementedError(
        "Production code needed: CLI shows reinstall instructions"
    )


@then("the release summary should show:")
def release_summary_shows_table(test_context, request):
    """Assert release summary table."""
    raise NotImplementedError(
        "Production code needed: ReleaseReport.summary displays table"
    )


@then("the install manifest should show:")
def install_manifest_shows_table(test_context, request):
    """Assert install manifest table."""
    raise NotImplementedError(
        "Production code needed: ReleaseReport.manifest displays table"
    )


@then("the test checklist should include:")
def test_checklist_includes(test_context, request):
    """Assert test checklist contents."""
    raise NotImplementedError(
        "Production code needed: ReleaseReport.checklist includes steps"
    )


@then("local testing instructions should be shown")
def local_testing_shown(test_context):
    """Assert local testing instructions shown."""
    raise NotImplementedError(
        "Production code needed: CLI shows local testing instructions"
    )


@then("CI/CD readiness confirmation should be shown")
def cicd_readiness_shown(test_context):
    """Assert CI/CD readiness confirmation shown."""
    raise NotImplementedError(
        "Production code needed: CLI shows CI/CD readiness"
    )


@then(parsers.parse('the release command should show "{command}"'))
def release_command_shows(test_context, command):
    """Assert release command shown."""
    raise NotImplementedError(
        f"Production code needed: CLI shows '{command}'"
    )


@then("if multiple wheels exist, the newest should be selected automatically")
def newest_wheel_auto_selected(test_context):
    """Assert newest wheel auto-selected in CI."""
    raise NotImplementedError(
        "Production code needed: CI mode auto-selects newest wheel"
    )


@then("the installation should complete automatically")
def installation_completes_automatically(test_context):
    """Assert installation completes automatically."""
    raise NotImplementedError(
        "Production code needed: Install completes without prompts"
    )


@then("the newest wheel should be selected automatically")
def newest_wheel_selected(test_context):
    """Assert newest wheel selected."""
    raise NotImplementedError(
        "Production code needed: Newest wheel selected by timestamp"
    )


@then("no selection prompt should appear")
def no_selection_prompt(test_context):
    """Assert no selection prompt."""
    raise NotImplementedError(
        "Production code needed: No interactive prompt in CI mode"
    )


@then("the output should be valid JSON")
def output_valid_json(test_context):
    """Assert output is valid JSON."""
    raise NotImplementedError(
        "Production code needed: Output parses as valid JSON"
    )


@then("it should include release_summary with version and timestamps")
def json_includes_release_summary(test_context):
    """Assert JSON includes release_summary."""
    raise NotImplementedError(
        "Production code needed: JSON has release_summary field"
    )


@then("it should include install_manifest with counts")
def json_includes_manifest(test_context):
    """Assert JSON includes install_manifest."""
    raise NotImplementedError(
        "Production code needed: JSON has install_manifest field"
    )


@then("it should include release_readiness with check results")
def json_includes_readiness(test_context):
    """Assert JSON includes release_readiness."""
    raise NotImplementedError(
        "Production code needed: JSON has release_readiness field"
    )


@then("the release report should be written to release-report.md")
def report_written_to_file(test_context):
    """Assert report written to file."""
    raise NotImplementedError(
        "Production code needed: Report written to specified file"
    )


@then("CI/CD can archive the report as an artifact")
def cicd_can_archive(test_context):
    """Assert CI/CD can archive report."""
    raise NotImplementedError(
        "Production code needed: Report file exists for archiving"
    )


@then("the CHANGELOG warning should become a failure")
def changelog_warning_becomes_failure(test_context):
    """Assert CHANGELOG warning becomes failure in strict mode."""
    raise NotImplementedError(
        "Production code needed: Strict mode converts warning to failure"
    )


@then("the installation should abort")
def installation_aborts(test_context):
    """Assert installation aborts."""
    raise NotImplementedError(
        "Production code needed: Installation aborted"
    )


@then("exit code should be non-zero")
def exit_code_nonzero(test_context):
    """Assert exit code is non-zero."""
    raise NotImplementedError(
        "Production code needed: Exit code != 0"
    )


@then("the installation should complete successfully")
def installation_completes_successfully(test_context):
    """Assert installation completes successfully."""
    raise NotImplementedError(
        "Production code needed: InstallResult.success == True"
    )


@then(parsers.parse('the version in release readiness should be "{version}"'))
def readiness_version_is(test_context, version):
    """Assert release readiness version."""
    raise NotImplementedError(
        f"Production code needed: ReleaseReadiness.version == '{version}'"
    )


@then(parsers.parse('the version in doctor verification should be "{version}"'))
def doctor_version_is(test_context, version):
    """Assert doctor version."""
    raise NotImplementedError(
        f"Production code needed: DoctorResult.version == '{version}'"
    )


@then(parsers.parse('the version in release report should be "{version}"'))
def report_version_is(test_context, version):
    """Assert release report version."""
    raise NotImplementedError(
        f"Production code needed: ReleaseReport.version == '{version}'"
    )


@then("all versions should match the wheel filename")
def versions_match_wheel_filename(test_context):
    """Assert all versions match wheel filename."""
    raise NotImplementedError(
        "Production code needed: All versions consistent with wheel filename"
    )


@then(parsers.parse("agent count in doctor should be {count:d}"))
def doctor_agent_count_is(test_context, count):
    """Assert doctor agent count."""
    raise NotImplementedError(
        f"Production code needed: DoctorResult.agent_count == {count}"
    )


@then(parsers.parse("agent count in report should be {count:d}"))
def report_agent_count_is(test_context, count):
    """Assert report agent count."""
    raise NotImplementedError(
        f"Production code needed: ReleaseReport.agent_count == {count}"
    )


@then("agent count should match actual files in install path")
def agent_count_matches_files(test_context):
    """Assert agent count matches files."""
    raise NotImplementedError(
        "Production code needed: Agent count matches file system"
    )


@then("the wheel from forge:build-local should be detected")
def build_wheel_detected(test_context):
    """Assert build wheel detected."""
    raise NotImplementedError(
        "Production code needed: Install detects wheel from build"
    )


@then(parsers.parse('the same version "{version}" should be used throughout'))
def same_version_used(test_context, version):
    """Assert same version used throughout."""
    raise NotImplementedError(
        f"Production code needed: All steps use version '{version}'"
    )


@then("the checks should match install-nwave doctor checks")
def checks_match_install_nwave(test_context):
    """Assert checks match install-nwave pattern."""
    raise NotImplementedError(
        "Production code needed: Doctor checks match Journey 3 pattern"
    )


@then("the health check format should be identical")
def health_check_format_identical(test_context):
    """Assert health check format identical."""
    raise NotImplementedError(
        "Production code needed: Health check format matches Journey 3"
    )


@then("the component list should be identical")
def component_list_identical(test_context):
    """Assert component list identical."""
    raise NotImplementedError(
        "Production code needed: Component list matches Journey 3"
    )


@then(parsers.parse('the release summary should show version "{version}"'))
def summary_shows_version(test_context, version):
    """Assert summary shows version."""
    raise NotImplementedError(
        f"Production code needed: Summary.version == '{version}'"
    )


@then("the release summary should show branch and timestamps")
def summary_shows_branch_timestamps(test_context):
    """Assert summary shows branch and timestamps."""
    raise NotImplementedError(
        "Production code needed: Summary shows branch and timestamps"
    )


@then(parsers.parse("the install manifest should show {agents:d} agents, {commands:d} commands, {templates:d} templates"))
def manifest_shows_counts(test_context, agents, commands, templates):
    """Assert manifest shows component counts."""
    raise NotImplementedError(
        f"Production code needed: Manifest shows {agents}, {commands}, {templates}"
    )


@then("the release readiness section should show all checks passed")
def readiness_all_checks_passed(test_context):
    """Assert release readiness all checks passed."""
    raise NotImplementedError(
        "Production code needed: All release readiness checks passed"
    )


@then("the test checklist should list verification steps")
def checklist_lists_steps(test_context):
    """Assert checklist lists verification steps."""
    raise NotImplementedError(
        "Production code needed: Checklist includes verification steps"
    )
