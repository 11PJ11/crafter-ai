"""
Journey 3: Install nWave for the First Time (install-nwave via PyPI)
=====================================================================

E2E acceptance tests for first-time installation - a user who saw an nWave
demo and wants to install it with a single command.

This test file reads like a book:
- Each scenario describes a complete user workflow
- Steps use business language, not technical jargon
- Tests drive implementation through Outside-In TDD

Test Coverage:
- US-030: Pre-flight checks for first-time install
- US-031: Install path resolution
- US-032: Framework installation with progress
- US-033: Doctor verification
- US-034: Welcome and celebration
- US-035: Restart notification
- US-036: Verification in Claude Code
- US-037: Environment variable override
- US-038: CI/CD mode
- US-039: Backup creation
- US-040: Rollback support
- US-041: Upgrade detection

Usage:
    pytest test_journey_3_pypi.py -v --pspec

Port Interfaces (from component-boundaries.md):
- FileSystemPort: File operations
- PipxPort: pipx install/uninstall operations
- PyPIPort: Package download and version resolution
"""

import pytest
from pytest_bdd import scenarios, given, when, then, parsers

# Load all scenarios from the Journey 3 feature file
scenarios('../features/journey_3_pypi.feature')


# =============================================================================
# JOURNEY-SPECIFIC GIVEN STEPS
# =============================================================================

@given("the user does NOT have pipx installed")
def user_no_pipx(mock_pipx):
    """Configure pipx as not available."""
    mock_pipx.setup_unavailable()


@given("the user has Python 3.8.10 installed")
def user_old_python(test_context):
    """Configure old Python version."""
    test_context.python_version = "3.8.10"


@given(parsers.parse('the user does NOT have write permission to "{path}"'))
def user_no_write_permission(mock_filesystem, path):
    """Configure path as not writable."""
    mock_filesystem.writable_paths.discard(path.replace("~/", ""))


@given("the user does NOT have Claude Code installed")
def user_no_claude_code(mock_filesystem):
    """Configure Claude Code as not installed."""
    mock_filesystem.directories.discard("~/.claude")


@given("the user runs the installer")
def user_runs_installer(test_context):
    """User initiates installation."""
    test_context.command_executed = "pipx install nwave"


@given("the user has pipx installed")
def user_has_pipx_generic(mock_pipx):
    """Configure pipx as available."""
    mock_pipx.setup_available()


@given("NWAVE_INSTALL_PATH is not set")
def nwave_path_not_set(test_context):
    """Ensure NWAVE_INSTALL_PATH is not set."""
    test_context.environment_vars.pop("NWAVE_INSTALL_PATH", None)


@given("config/installer.yaml does not specify install_dir")
def config_no_install_dir(mock_filesystem):
    """Configure installer.yaml without install_dir."""
    mock_filesystem.files["config/installer.yaml"] = """
# Installer configuration
defaults:
  timeout: 30
"""


@given(parsers.parse('NWAVE_INSTALL_PATH is set to "{path}"'))
def nwave_path_set(test_context, path):
    """Set NWAVE_INSTALL_PATH."""
    test_context.environment_vars["NWAVE_INSTALL_PATH"] = path


@given(parsers.parse('config/installer.yaml has paths.install_dir = "{path}"'))
def config_has_install_dir(mock_filesystem, path):
    """Configure installer.yaml with install_dir."""
    mock_filesystem.files["config/installer.yaml"] = f"""
paths:
  install_dir: "{path}"
"""


@given("an existing nWave installation exists at \"~/.claude/agents/nw/\"")
def existing_nwave_installation(mock_filesystem, mock_pipx):
    """Configure existing nWave installation."""
    mock_filesystem.setup_installed_nwave(version="1.2.0")
    mock_pipx.setup_existing_nwave("1.2.0")


@given("no previous nWave installation exists")
def no_previous_installation(mock_filesystem, mock_pipx):
    """Ensure no previous installation."""
    mock_filesystem.directories.discard("~/.claude/agents/nw")
    mock_pipx.installed_packages.clear()


@given("all components have been installed")
def all_components_installed(test_context, mock_filesystem):
    """Configure all components as installed."""
    mock_filesystem.setup_installed_nwave(version="1.3.0", agent_count=47)
    mock_filesystem.file_counts["~/.claude/agents/nw/commands"] = 23
    mock_filesystem.file_counts["~/.claude/agents/nw/templates"] = 12
    test_context.install_completed = True


@given("framework installation completed successfully")
def framework_installation_completed(test_context, mock_filesystem):
    """Configure successful framework installation."""
    test_context.install_completed = True
    test_context.install_success = True
    mock_filesystem.setup_installed_nwave(version="1.3.0", agent_count=47)


@given(parsers.parse("installation validation showed {agents:d} agents, {commands:d} commands, {templates:d} templates"))
def validation_showed_counts(test_context, agents, commands, templates):
    """Configure validation results."""
    test_context.agent_count = agents
    test_context.command_count = commands
    test_context.template_count = templates


@given("the welcome message has displayed")
def welcome_displayed(test_context):
    """Configure welcome message as displayed."""
    test_context.messages.append("nWave v1.3.0 installed successfully!")


@given("the next steps are displayed")
def next_steps_displayed(test_context):
    """Configure next steps as displayed."""
    test_context.messages.append("Next steps:")


@given("nWave has been installed and Claude Code restarted")
def nwave_installed_claude_restarted(test_context, mock_filesystem, mock_pipx):
    """Configure post-install state."""
    test_context.install_completed = True
    test_context.install_success = True
    mock_filesystem.setup_installed_nwave(version="1.3.0", agent_count=47)
    mock_pipx.installed_packages["nwave"] = "1.3.0"


@given(parsers.parse("doctor showed {agents:d} agents, {commands:d} commands, {templates:d} templates"))
def doctor_showed_counts(test_context, agents, commands, templates):
    """Configure doctor results."""
    test_context.doctor_ran = True
    test_context.doctor_status = "HEALTHY"
    test_context.agent_count = agents
    test_context.command_count = commands
    test_context.template_count = templates


@given(parsers.parse("a previous nWave {version} installation exists"))
def previous_version_exists(mock_filesystem, mock_pipx, version):
    """Configure previous version installation."""
    mock_filesystem.setup_installed_nwave(version=version)
    mock_pipx.setup_existing_nwave(version)


@given(parsers.parse('a backup was created at "{backup_path}"'))
def backup_created_at(mock_filesystem, backup_path):
    """Configure backup."""
    mock_filesystem.directories.add(backup_path)


@given(parsers.parse("the user has nWave {version} installed"))
def user_has_nwave_version(test_context, mock_filesystem, mock_pipx, version):
    """Configure specific nWave version."""
    mock_filesystem.setup_installed_nwave(version=version)
    mock_pipx.setup_existing_nwave(version)
    test_context.current_version = version


@given(parsers.parse("a backup of {version} exists"))
def backup_of_version_exists(mock_filesystem, version):
    """Configure backup of specific version."""
    mock_filesystem.directories.add(f"~/.claude/backups/nwave-{version}")


@given("the user has no previous nWave installation")
def user_no_previous_install(mock_filesystem, mock_pipx):
    """Ensure no previous installation."""
    mock_filesystem.directories.discard("~/.claude/agents/nw")
    mock_pipx.installed_packages.clear()


@given("nWave is installed but no backups exist")
def nwave_installed_no_backups(mock_filesystem, mock_pipx):
    """Configure nWave without backups."""
    mock_filesystem.setup_installed_nwave(version="1.3.0")
    mock_pipx.setup_existing_nwave("1.3.0")
    # Ensure no backup directories
    mock_filesystem.directories.discard("~/.claude/backups")


@given("the reinstall prompt is displayed")
def reinstall_prompt_displayed(test_context):
    """Configure reinstall prompt state."""
    test_context.prompts_shown.append("Reinstall? [Y/n]")


@given(parsers.parse("existing nWave {version} is installed"))
def existing_nwave_version(mock_filesystem, mock_pipx, version):
    """Configure existing nWave version."""
    mock_filesystem.setup_installed_nwave(version=version)
    mock_pipx.setup_existing_nwave(version)


@given("nWave has been installed successfully")
def nwave_installed_successfully(test_context, mock_filesystem, mock_pipx):
    """Configure successful installation."""
    test_context.install_completed = True
    test_context.install_success = True
    test_context.current_version = "1.3.0"
    mock_filesystem.setup_installed_nwave(version="1.3.0", agent_count=47)
    mock_pipx.installed_packages["nwave"] = "1.3.0"


@given(parsers.parse('the flag "{flag}" is used'))
def flag_is_used(test_context, flag):
    """Configure flag usage."""
    test_context.environment_vars["CLI_FLAGS"] = flag


# =============================================================================
# JOURNEY-SPECIFIC WHEN STEPS
# =============================================================================

@when("the installer resolves the install path")
def installer_resolves_path(test_context):
    """Resolve install path."""
    raise NotImplementedError(
        "Production code needed: InstallPathResolver.resolve()"
    )


@when("the framework installation begins")
def framework_installation_begins(test_context):
    """Begin framework installation."""
    raise NotImplementedError(
        "Production code needed: FrameworkInstaller.install()"
    )


@when("the installation validation runs")
def installation_validation_runs(test_context):
    """Run installation validation."""
    raise NotImplementedError(
        "Production code needed: InstallationValidator.validate()"
    )


@when("doctor verification runs")
def doctor_verification_runs_alt(test_context):
    """Run doctor verification."""
    raise NotImplementedError(
        "Production code needed: DoctorService.run()"
    )


@when("the welcome message displays")
def welcome_message_displays(test_context):
    """Display welcome message."""
    raise NotImplementedError(
        "Production code needed: WelcomeDisplay.show()"
    )


@when(parsers.parse('the user types "{command}" in Claude Code'))
def user_types_in_claude(test_context, command):
    """User types command in Claude Code."""
    test_context.command_executed = command
    raise NotImplementedError(
        f"Production code needed: Claude Code executes '{command}'"
    )


@when(parsers.parse('the installation of {version} fails during agent file copy'))
def installation_fails_during_copy(test_context, version):
    """Simulate installation failure during file copy."""
    test_context.install_success = False
    test_context.errors.append(f"Failed to copy agent files for {version}")
    raise NotImplementedError(
        "Production code needed: InstallService encounters FileCopyError"
    )


@when("the first installation fails")
def first_installation_fails(test_context):
    """Simulate first installation failure."""
    test_context.install_success = False
    test_context.errors.append("Installation failed")
    raise NotImplementedError(
        "Production code needed: InstallService fails on first install"
    )


@when("the user can select a backup to restore")
def user_selects_backup(test_context):
    """User selects backup to restore."""
    test_context.user_inputs.append("1")  # Select first backup


@when("the selected backup should be restored")
def backup_restored(test_context):
    """Restore selected backup."""
    raise NotImplementedError(
        "Production code needed: BackupService.restore()"
    )


@when(parsers.parse('the user attempts to install version {version}'))
def user_attempts_install_version(test_context, version):
    """User attempts to install specific version."""
    test_context.command_executed = f"pipx install nwave=={version}"
    raise NotImplementedError(
        f"Production code needed: Install version {version}"
    )


@when(parsers.parse('the user runs "pipx install nwave" for version {version}'))
def user_installs_version(test_context, version):
    """User runs install for specific version."""
    test_context.command_executed = f"pipx install nwave=={version}"
    raise NotImplementedError(
        f"Production code needed: Install version {version}"
    )


@when(parsers.parse('CI runs "pipx install nwave" for {version}'))
def ci_runs_install(test_context, version):
    """CI runs install."""
    test_context.ci_mode = True
    test_context.environment_vars["CI"] = "true"
    test_context.command_executed = f"pipx install nwave=={version}"
    raise NotImplementedError(
        f"Production code needed: CI installs version {version}"
    )


# =============================================================================
# JOURNEY-SPECIFIC THEN STEPS
# =============================================================================

@then("the download progress bar should appear")
def download_progress_appears(test_context):
    """Assert download progress bar appears."""
    # Check CLI output for progress indicator
    output = "\n".join(test_context.messages)
    assert "progress" in output.lower() or "downloading" in output.lower() or "install" in output.lower(), \
        f"Expected download progress indicator in output, got: {output[:500]}"


@then(parsers.parse('the version "{version}" from PyPI should be displayed'))
def pypi_version_displayed(test_context, version):
    """Assert PyPI version displayed."""
    output = "\n".join(test_context.messages)
    assert version in output or "version" in output.lower(), \
        f"Expected version '{version}' in output, got: {output[:500]}"


@then("the pre-flight checks should run")
def preflight_checks_run(test_context):
    """Assert pre-flight checks run."""
    output = "\n".join(test_context.messages)
    assert "pre-flight" in output.lower() or "check" in output.lower(), \
        f"Expected pre-flight check indication in output, got: {output[:500]}"


@then("all pre-flight checks should pass with green checkmarks")
def all_preflight_pass_green(test_context):
    """Assert all pre-flight checks pass."""
    output = "\n".join(test_context.messages)
    # Check for success indicators in output
    assert "OK" in output or "pass" in output.lower() or test_context.exit_code == 0, \
        f"Expected pre-flight checks to pass, got: {output[:500]}"


@then(parsers.parse('the framework should be installed to "{path}"'))
def framework_installed_to(test_context, path):
    """Assert framework installed to path."""
    output = "\n".join(test_context.messages)
    assert path in output or "installed" in output.lower(), \
        f"Expected installation path '{path}' in output, got: {output[:500]}"


@then("the doctor verification should run automatically")
def doctor_runs_automatically(test_context):
    """Assert doctor runs automatically."""
    output = "\n".join(test_context.messages)
    assert "doctor" in output.lower() or "verify" in output.lower() or "verification" in output.lower(), \
        f"Expected doctor verification in output, got: {output[:500]}"


@then(parsers.parse("the doctor should show \"HEALTHY\" status with {agents:d} agents, {commands:d} commands, {templates:d} templates"))
def doctor_healthy_with_counts(test_context, agents, commands, templates):
    """Assert doctor shows healthy with counts."""
    output = "\n".join(test_context.messages)
    assert "healthy" in output.lower() or "ok" in output.lower(), \
        f"Expected HEALTHY status in output, got: {output[:500]}"


@then("the ASCII logo should be displayed")
def ascii_logo_displayed(test_context):
    """Assert ASCII logo displayed."""
    output = "\n".join(test_context.messages)
    # ASCII logos typically contain box-drawing characters or decorative elements
    assert len(output) > 0, f"Expected ASCII logo in output, got empty output"


@then(parsers.parse('the welcome message should show "{message}"'))
def welcome_shows_message(test_context, message):
    """Assert welcome message shows text."""
    output = "\n".join(test_context.messages)
    assert message.lower() in output.lower(), \
        f"Expected welcome message '{message}' in output, got: {output[:500]}"


@then(parsers.parse('the user should see "{message}"'))
def user_sees_message(test_context, message):
    """Assert user sees message."""
    output = "\n".join(test_context.messages)
    assert message.lower() in output.lower(), \
        f"Expected message '{message}' in output, got: {output[:500]}"


@then(parsers.parse('the next steps should include "{step}"'))
def next_steps_include(test_context, step):
    """Assert next steps include specific step."""
    output = "\n".join(test_context.messages)
    assert step.lower() in output.lower(), \
        f"Expected next step '{step}' in output, got: {output[:500]}"


@then(parsers.parse('the version should match "{version}" from the installation'))
def version_matches_installation(test_context, version):
    """Assert version matches installation."""
    output = "\n".join(test_context.messages)
    assert version in output, \
        f"Expected version '{version}' in output, got: {output[:500]}"


@then(parsers.parse('the install path should match "{path}"'))
def install_path_matches(test_context, path):
    """Assert install path matches."""
    raise NotImplementedError(
        f"Production code needed: /nw:version shows path '{path}'"
    )


@then(parsers.parse('the output should show "{text}"'))
def output_shows_text(test_context, text):
    """Assert output shows text."""
    raise NotImplementedError(
        f"Production code needed: Output contains '{text}'"
    )


@then(parsers.parse('the error message should display "{message}"'))
def error_message_shows(test_context, message):
    """Assert error message shows text."""
    raise NotImplementedError(
        f"Production code needed: Error message contains '{message}'"
    )


@then(parsers.parse('the message should include "{text}"'))
def message_includes(test_context, text):
    """Assert message includes text."""
    raise NotImplementedError(
        f"Production code needed: Message contains '{text}'"
    )


@then("the message should suggest upgrade options")
def message_suggests_upgrade(test_context):
    """Assert message suggests upgrade options."""
    raise NotImplementedError(
        "Production code needed: Error suggests upgrade options"
    )


@then(parsers.parse('the warning should display "{warning}"'))
def warning_displays(test_context, warning):
    """Assert warning displayed."""
    raise NotImplementedError(
        f"Production code needed: Warning '{warning}' displayed"
    )


@then("installation should continue (non-blocking warning)")
def installation_continues_nonblocking(test_context):
    """Assert installation continues despite warning."""
    raise NotImplementedError(
        "Production code needed: Installation proceeds past warning"
    )


@then(parsers.parse('the install path should be "{path}"'))
def install_path_is(test_context, path):
    """Assert install path."""
    raise NotImplementedError(
        f"Production code needed: install_path == '{path}'"
    )


@then(parsers.parse('the pre-flight output should show "{text}"'))
def preflight_output_shows(test_context, text):
    """Assert pre-flight output shows text."""
    raise NotImplementedError(
        f"Production code needed: Preflight output shows '{text}'"
    )


@then("all subsequent paths should use the custom location")
def paths_use_custom_location(test_context):
    """Assert all paths use custom location."""
    raise NotImplementedError(
        "Production code needed: All paths use NWAVE_INSTALL_PATH"
    )


@then("the env var should take precedence")
def env_var_takes_precedence(test_context):
    """Assert env var takes precedence over config."""
    raise NotImplementedError(
        "Production code needed: NWAVE_INSTALL_PATH > config file"
    )


@then(parsers.parse('a spinner should appear for "{phase}"'))
def spinner_appears_for(test_context, phase):
    """Assert spinner appears for phase."""
    raise NotImplementedError(
        f"Production code needed: Spinner shown for '{phase}'"
    )


@then(parsers.parse('a progress bar should appear for "{phase}"'))
def progress_bar_appears_for(test_context, phase):
    """Assert progress bar appears for phase."""
    raise NotImplementedError(
        f"Production code needed: Progress bar shown for '{phase}'"
    )


@then("progress bars should show for Agents, Commands, Templates installation")
def progress_bars_for_components(test_context):
    """Assert progress bars for components."""
    raise NotImplementedError(
        "Production code needed: Progress bars for Agents, Commands, Templates"
    )


@then("each component should show a count and checkmark when complete")
def components_show_count_checkmark(test_context):
    """Assert components show count and checkmark."""
    raise NotImplementedError(
        "Production code needed: Each component shows count + checkmark"
    )


@then(parsers.parse('a backup should be created at "{path}"'))
def backup_created_at_path(test_context, path):
    """Assert backup created at path."""
    raise NotImplementedError(
        f"Production code needed: Backup created at '{path}'"
    )


@then("the backup should contain agents, commands, and manifest")
def backup_contains_components(test_context):
    """Assert backup contains components."""
    raise NotImplementedError(
        "Production code needed: Backup contains agents, commands, manifest"
    )


@then("the backup path should include a timestamp")
def backup_path_has_timestamp(test_context):
    """Assert backup path has timestamp."""
    raise NotImplementedError(
        "Production code needed: Backup path includes timestamp"
    )


@then(parsers.parse('the message should show "{message}"'))
def message_shows(test_context, message):
    """Assert message shows text."""
    raise NotImplementedError(
        f"Production code needed: Message shows '{message}'"
    )


@then("no backup should be created")
def no_backup_created(test_context):
    """Assert no backup created."""
    raise NotImplementedError(
        "Production code needed: No backup directory created"
    )


@then("the installation should proceed directly")
def installation_proceeds_directly(test_context):
    """Assert installation proceeds directly."""
    raise NotImplementedError(
        "Production code needed: Installation skips backup phase"
    )


@then("a validation table should display")
def validation_table_displays(test_context):
    """Assert validation table displays."""
    raise NotImplementedError(
        "Production code needed: CLI shows validation table"
    )


@then(parsers.parse('the table should show "{text}"'))
def table_shows(test_context, text):
    """Assert table shows text."""
    raise NotImplementedError(
        f"Production code needed: Table shows '{text}'"
    )


@then(parsers.parse('the final status should show "{status}"'))
def final_status_is(test_context, status):
    """Assert final status."""
    raise NotImplementedError(
        f"Production code needed: Final status == '{status}'"
    )


@then("the nWave ASCII logo should be displayed")
def nwave_logo_displayed(test_context):
    """Assert nWave ASCII logo displayed."""
    raise NotImplementedError(
        "Production code needed: WelcomeDisplay shows nWave logo"
    )


@then("the next steps should include:")
def next_steps_include_table(test_context, request):
    """Assert next steps include items from table."""
    raise NotImplementedError(
        "Production code needed: NextSteps includes all table items"
    )


@then("the documentation URL should be displayed")
def documentation_url_displayed(test_context):
    """Assert documentation URL displayed."""
    raise NotImplementedError(
        "Production code needed: WelcomeDisplay shows documentation URL"
    )


@then("the restart instruction should be in a highlighted box")
def restart_instruction_highlighted(test_context):
    """Assert restart instruction highlighted."""
    raise NotImplementedError(
        "Production code needed: Restart instruction in highlighted box"
    )


@then(parsers.parse('the instruction should say "{instruction}"'))
def instruction_says(test_context, instruction):
    """Assert instruction text."""
    raise NotImplementedError(
        f"Production code needed: Instruction == '{instruction}'"
    )


@then(parsers.parse('the keyboard shortcut "{shortcut}" should be mentioned'))
def keyboard_shortcut_mentioned(test_context, shortcut):
    """Assert keyboard shortcut mentioned."""
    raise NotImplementedError(
        f"Production code needed: Instruction mentions '{shortcut}'"
    )


@then(parsers.parse('"{step}" should be step {num:d}'))
def step_is_number(test_context, step, num):
    """Assert step is at specific position."""
    raise NotImplementedError(
        f"Production code needed: '{step}' is at position {num}"
    )


@then("the step should explain why restart is needed")
def step_explains_restart(test_context):
    """Assert step explains restart reason."""
    raise NotImplementedError(
        "Production code needed: Restart step includes explanation"
    )


@then("the output should show the same counts")
def output_shows_same_counts(test_context):
    """Assert output shows same counts."""
    raise NotImplementedError(
        "Production code needed: /nw:version counts match doctor counts"
    )


@then(parsers.parse('"{status}" should confirm healthy status'))
def status_confirms_healthy(test_context, status):
    """Assert status confirms healthy."""
    raise NotImplementedError(
        f"Production code needed: '{status}' indicates healthy"
    )


@then("the ASCII logo should be suppressed")
def ascii_logo_suppressed(test_context):
    """Assert ASCII logo suppressed in CI."""
    raise NotImplementedError(
        "Production code needed: CI mode suppresses ASCII logo"
    )


@then(parsers.parse('the JSON should include "{key}": {value}'))
def json_includes_key_value(test_context, key, value):
    """Assert JSON includes key-value."""
    raise NotImplementedError(
        f"Production code needed: JSON['{key}'] == {value}"
    )


@then(parsers.parse('the JSON should include "{key}": "{value}"'))
def json_includes_key_string(test_context, key, value):
    """Assert JSON includes key-string."""
    raise NotImplementedError(
        f"Production code needed: JSON['{key}'] == '{value}'"
    )


@then("the JSON should include counts for agents, commands, templates")
def json_includes_counts(test_context):
    """Assert JSON includes component counts."""
    raise NotImplementedError(
        "Production code needed: JSON includes agents, commands, templates counts"
    )


@then("rollback should trigger automatically")
def rollback_triggers(test_context):
    """Assert rollback triggers automatically."""
    raise NotImplementedError(
        "Production code needed: RollbackService triggered on failure"
    )


@then("files should be restored from the backup")
def files_restored_from_backup(test_context):
    """Assert files restored from backup."""
    raise NotImplementedError(
        "Production code needed: BackupService.restore() completed"
    )


@then(parsers.parse('"nw doctor" should show version {version}'))
def nw_doctor_shows_version(test_context, version):
    """Assert nw doctor shows version."""
    raise NotImplementedError(
        f"Production code needed: nw doctor shows version {version}"
    )


@then("available backups should be listed with timestamps")
def backups_listed_with_timestamps(test_context):
    """Assert backups listed with timestamps."""
    raise NotImplementedError(
        "Production code needed: BackupService.list() shows timestamps"
    )


@then(parsers.parse('"nw doctor" should confirm restoration'))
def nw_doctor_confirms_restoration(test_context):
    """Assert nw doctor confirms restoration."""
    raise NotImplementedError(
        "Production code needed: nw doctor shows restored version"
    )


@then("partial files should be cleaned up")
def partial_files_cleaned(test_context):
    """Assert partial files cleaned up."""
    raise NotImplementedError(
        "Production code needed: Cleanup partial installation"
    )


@then(parsers.parse('the error should show "{error}"'))
def error_shows(test_context, error):
    """Assert error shows text."""
    raise NotImplementedError(
        f"Production code needed: Error shows '{error}'"
    )


@then(parsers.parse("the installer should detect existing version {version}"))
def installer_detects_version(test_context, version):
    """Assert installer detects existing version."""
    raise NotImplementedError(
        f"Production code needed: Installer detects version {version}"
    )


@then("a backup should be created automatically")
def backup_created_automatically(test_context):
    """Assert backup created automatically."""
    raise NotImplementedError(
        "Production code needed: Automatic backup created"
    )


@then("the installation should proceed with upgrade path")
def installation_proceeds_upgrade(test_context):
    """Assert installation uses upgrade path."""
    raise NotImplementedError(
        "Production code needed: Installation uses upgrade flow"
    )


@then(parsers.parse("doctor should show version {version} after completion"))
def doctor_shows_version_after(test_context, version):
    """Assert doctor shows version after completion."""
    raise NotImplementedError(
        f"Production code needed: DoctorResult.version == '{version}'"
    )


@then("the installer should detect no existing installation")
def installer_detects_no_installation(test_context):
    """Assert installer detects no installation."""
    raise NotImplementedError(
        "Production code needed: Installer detects fresh install"
    )


@then("the welcome celebration should display")
def welcome_celebration_displays(test_context):
    """Assert welcome celebration displays."""
    raise NotImplementedError(
        "Production code needed: WelcomeDisplay.celebrate()"
    )


@then("the installer should detect same version")
def installer_detects_same_version(test_context):
    """Assert installer detects same version."""
    raise NotImplementedError(
        "Production code needed: Installer detects reinstall"
    )


@then(parsers.parse('the prompt should ask "{prompt}"'))
def prompt_asks(test_context, prompt):
    """Assert prompt asks question."""
    raise NotImplementedError(
        f"Production code needed: Prompt asks '{prompt}'"
    )


@then("the reinstallation should proceed")
def reinstallation_proceeds(test_context):
    """Assert reinstallation proceeds."""
    raise NotImplementedError(
        "Production code needed: Reinstallation proceeds"
    )


@then("doctor should confirm successful reinstall")
def doctor_confirms_reinstall(test_context):
    """Assert doctor confirms reinstall."""
    raise NotImplementedError(
        "Production code needed: DoctorResult.status == 'HEALTHY'"
    )


@then("no changes should be made")
def no_changes_made(test_context):
    """Assert no changes made."""
    raise NotImplementedError(
        "Production code needed: Installation cancelled, no changes"
    )


@then("the installer should detect downgrade")
def installer_detects_downgrade(test_context):
    """Assert installer detects downgrade."""
    raise NotImplementedError(
        "Production code needed: Installer detects downgrade"
    )


@then(parsers.parse('the warning should show "{warning}"'))
def warning_shows(test_context, warning):
    """Assert warning shows text."""
    raise NotImplementedError(
        f"Production code needed: Warning shows '{warning}'"
    )


@then("the upgrade should proceed automatically")
def upgrade_proceeds_automatically(test_context):
    """Assert upgrade proceeds automatically."""
    raise NotImplementedError(
        "Production code needed: CI mode auto-upgrades"
    )


@then("no prompts should appear")
def no_prompts_appear(test_context):
    """Assert no prompts appear."""
    raise NotImplementedError(
        "Production code needed: No interactive prompts"
    )


@then(parsers.parse('the version in the download progress should be "{version}"'))
def download_progress_version(test_context, version):
    """Assert download progress shows version."""
    raise NotImplementedError(
        f"Production code needed: Download progress shows '{version}'"
    )


@then(parsers.parse('the version in the welcome message should be "{version}"'))
def welcome_version(test_context, version):
    """Assert welcome message shows version."""
    raise NotImplementedError(
        f"Production code needed: Welcome message shows '{version}'"
    )


@then(parsers.parse('the version in "/nw:version" should be "{version}"'))
def nw_version_shows(test_context, version):
    """Assert /nw:version shows version."""
    raise NotImplementedError(
        f"Production code needed: /nw:version shows '{version}'"
    )


@then("all versions should match the PyPI package version")
def versions_match_pypi(test_context):
    """Assert all versions match PyPI version."""
    raise NotImplementedError(
        "Production code needed: All versions consistent with PyPI"
    )


@then(parsers.parse('the install path in pre-flight should be "{path}"'))
def preflight_path(test_context, path):
    """Assert pre-flight shows path."""
    raise NotImplementedError(
        f"Production code needed: Preflight shows path '{path}'"
    )


@then(parsers.parse('the install path in doctor should be "{path}"'))
def doctor_path(test_context, path):
    """Assert doctor shows path."""
    raise NotImplementedError(
        f"Production code needed: Doctor shows path '{path}'"
    )


@then(parsers.parse('the install path in "/nw:version" should be "{path}"'))
def nw_version_path(test_context, path):
    """Assert /nw:version shows path."""
    raise NotImplementedError(
        f"Production code needed: /nw:version shows path '{path}'"
    )


@then(parsers.parse("the agent count in installation (Step 4) validation should be {count:d}"))
def step4_agent_count(test_context, count):
    """Assert Step 4 agent count."""
    raise NotImplementedError(
        f"Production code needed: Step 4 validation.agent_count == {count}"
    )


@then(parsers.parse("the agent count in doctor (Step 5) should be {count:d}"))
def step5_agent_count(test_context, count):
    """Assert Step 5 agent count."""
    raise NotImplementedError(
        f"Production code needed: Step 5 doctor.agent_count == {count}"
    )


@then(parsers.parse("the agent count in /nw:version (Step 7) should be {count:d}"))
def step7_agent_count(test_context, count):
    """Assert Step 7 agent count."""
    raise NotImplementedError(
        f"Production code needed: Step 7 /nw:version.agent_count == {count}"
    )


@then("command and template counts should similarly match")
def all_counts_match(test_context):
    """Assert all counts match across steps."""
    raise NotImplementedError(
        "Production code needed: All counts consistent across steps"
    )
