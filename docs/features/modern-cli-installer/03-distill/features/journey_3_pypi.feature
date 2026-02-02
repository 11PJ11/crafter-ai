# Journey 3: Install nWave for the First Time (install-nwave via PyPI)
# Epic: modern_CLI_installer
# Acceptance Designer: Quinn
# Date: 2026-02-01

@journey_3 @install @pypi @first_time
Feature: Install nWave for the First Time
  As a developer who saw an nWave demo
  I want to install nWave with a single command
  So that I can start using it in Claude Code immediately

  Background:
    Given the user has a terminal open
    And the user has Python 3.12.1 installed
    And the user has Claude Code installed

  # ==========================================================================
  # HAPPY PATH - Complete First-Time Installation Journey
  # ==========================================================================

  @US_030 @US_031 @US_032 @US_033 @US_034 @US_035 @happy_path @P0
  Scenario: Successful first-time installation
    Given the user has pipx v1.4.3 installed
    And no previous nWave installation exists
    When the user runs "pipx install nwave"
    Then the download progress bar should appear
    And the version "1.3.0" from PyPI should be displayed
    And the pre-flight checks should run
    And all pre-flight checks should pass with green checkmarks
    And the framework should be installed to "~/.claude/agents/nw/"
    And the doctor verification should run automatically
    And the doctor should show "HEALTHY" status with 47 agents, 23 commands, 12 templates
    And the ASCII logo should be displayed
    And the welcome message should show "nWave v1.3.0 installed successfully!"
    And the user should see "IMPORTANT: Restart Claude Code to activate"
    And the next steps should include "/nw:version"

  @US_036 @happy_path @P0
  Scenario: Verify installation in Claude Code
    Given nWave has been installed successfully
    And the user has restarted Claude Code
    When the user types "/nw:version" in Claude Code
    Then the version should match "1.3.0" from the installation
    And the install path should match "~/.claude/agents/nw/"
    And the output should show "Agents: 47 | Commands: 23 | Templates: 12"
    And the output should show "All systems operational"

  # ==========================================================================
  # PRE-FLIGHT CHECKS - US-030, US-031
  # ==========================================================================

  @US_030 @preflight @P0
  Scenario: Pre-flight check validates Python version
    Given the user runs the installer
    When the pre-flight checks run
    Then the Python version check should verify 3.10+
    And the check should display "[check] Python version 3.12.1"

  @US_030 @preflight @P0
  Scenario: Pre-flight check validates pipx isolation
    Given the user has pipx installed
    When the pre-flight checks run
    Then the pipx isolation check should verify isolated environment
    And the check should display "[check] pipx isolation"

  @US_030 @preflight @P0
  Scenario: Pre-flight check validates write permissions
    Given the user runs the installer
    When the pre-flight checks run
    Then the permissions check should verify "~/.claude/" is writable
    And the check should display "[check] Write permissions"

  @US_030 @preflight @P1
  Scenario: Pre-flight check detects Claude Code
    Given the user has Claude Code installed
    When the pre-flight checks run
    Then the Claude Code check should verify installation
    And the check should display "[check] Claude Code" with the path

  # ==========================================================================
  # ERROR PATHS - US-030
  # ==========================================================================

  @US_030 @error @blocking @P0
  Scenario: pipx not installed
    Given the user does NOT have pipx installed
    When the user runs "pipx install nwave"
    Then the error message should display "[x] pipx not found"
    And the message should include "Install it first:"
    And the message should include "pip install pipx"
    And the message should include "pipx ensurepath"

  @US_030 @error @blocking @P0
  Scenario: Python version too old
    Given the user has Python 3.8.10 installed
    When the user runs "pipx install nwave"
    Then the error message should display "Python 3.10+ required"
    And the message should show the current Python version "3.8.10"
    And the message should suggest upgrade options

  @US_030 @error @blocking @P1
  Scenario: Permission denied on install path
    Given the user does NOT have write permission to "~/.claude/"
    When the pre-flight checks run
    Then the error should display "[x] Write permissions"
    And the message should include how to fix permissions
    And the message should mention NWAVE_INSTALL_PATH alternative

  @US_030 @error @warning @P1
  Scenario: Claude Code not found
    Given the user does NOT have Claude Code installed
    When the pre-flight checks run
    Then the warning should display "Claude Code not found"
    And the message should include the installation URL
    And installation should continue (non-blocking warning)

  # ==========================================================================
  # INSTALL PATH RESOLUTION - US-031, US-037
  # ==========================================================================

  @US_031 @config @P0
  Scenario: Install path resolution uses default when no override
    Given NWAVE_INSTALL_PATH is not set
    And config/installer.yaml does not specify install_dir
    When the installer resolves the install path
    Then the install path should be "~/.claude/agents/nw/"
    And the pre-flight output should show "Using default: ~/.claude/agents/nw/"

  @US_037 @config @P0
  Scenario: Install path respects environment variable override
    Given NWAVE_INSTALL_PATH is set to "~/my-claude/agents/nw/"
    When the installer resolves the install path
    Then the install path should be "~/my-claude/agents/nw/"
    And the pre-flight output should show "NWAVE_INSTALL_PATH=~/my-claude/agents/nw/"
    And all subsequent paths should use the custom location

  @US_031 @config @P1
  Scenario: Install path uses config file when env var not set
    Given NWAVE_INSTALL_PATH is not set
    And config/installer.yaml has paths.install_dir = "~/custom-claude/"
    When the installer resolves the install path
    Then the install path should be "~/custom-claude/"

  @US_031 @config @P1
  Scenario: Environment variable takes precedence over config file
    Given NWAVE_INSTALL_PATH is set to "~/env-path/"
    And config/installer.yaml has paths.install_dir = "~/config-path/"
    When the installer resolves the install path
    Then the install path should be "~/env-path/"
    And the env var should take precedence

  # ==========================================================================
  # FRAMEWORK INSTALLATION - US-032
  # ==========================================================================

  @US_032 @install @P0
  Scenario: Framework installation shows progress bars
    Given pre-flight checks have passed
    When the framework installation begins
    Then a spinner should appear for "Checking source files"
    And a progress bar should appear for "Building distribution"
    And progress bars should show for Agents, Commands, Templates installation
    And each component should show a count and checkmark when complete

  @US_039 @install @P1
  Scenario: Backup is created before installation on upgrade
    Given an existing nWave installation exists at "~/.claude/agents/nw/"
    When the framework installation begins
    Then a backup should be created at "~/.claude/backups/nwave-20260201-143025/"
    And the backup should contain agents, commands, and manifest
    And the backup path should include a timestamp
    And the message should show "Backup created"

  @US_039 @install @P1
  Scenario: No backup created for fresh install
    Given no previous nWave installation exists
    When the framework installation begins
    Then no backup should be created
    And the installation should proceed directly

  @US_032 @install @P0
  Scenario: Installation validation shows component counts
    Given all components have been installed
    When the installation validation runs
    Then a validation table should display
    And the table should show "Agents [check] 47"
    And the table should show "Commands [check] 23"
    And the table should show "Templates [check] 12"
    And the table should show "Manifest [check] Created"
    And the final status should show "Validation: PASSED"

  # ==========================================================================
  # DOCTOR VERIFICATION - US-033
  # ==========================================================================

  @US_033 @doctor @P0
  Scenario: Doctor runs after successful install
    Given framework installation completed successfully
    When the doctor verification runs
    Then "Core installation" should show the install path
    And "Agent files" should show "47 OK"
    And "Command files" should show "23 OK"
    And "Template files" should show "12 OK"
    And "Config valid" should show "nwave.yaml OK"
    And "Permissions" should show "All accessible"
    And "Version match" should show "1.3.0"
    And the status should show "HEALTHY"

  @US_033 @doctor @P0
  Scenario: Doctor counts match installation validation
    Given installation validation showed 47 agents, 23 commands, 12 templates
    When doctor verification runs
    Then doctor should show 47 agents, 23 commands, 12 templates
    And the counts should match actual files in install path

  # ==========================================================================
  # WELCOME AND CELEBRATION - US-034
  # ==========================================================================

  @US_034 @celebration @P0
  Scenario: Welcome message displays celebration
    Given doctor verification has passed
    When the welcome message displays
    Then the nWave ASCII logo should be displayed
    And the message should show "nWave v1.3.0 installed successfully!"
    And the message should show "Your Claude is now powered by nWave"

  @US_034 @celebration @P0
  Scenario: Next steps are clear and actionable
    Given the welcome message has displayed
    Then the next steps should include:
      | Step | Description                          |
      | 1    | Restart Claude Code (Cmd+Q then reopen) |
      | 2    | Run /nw:version to verify              |
      | 3    | Run /nw:help to see available agents   |
    And the documentation URL should be displayed

  # ==========================================================================
  # RESTART NOTIFICATION - US-035
  # ==========================================================================

  @US_035 @restart @P0
  Scenario: Restart instruction is prominent
    Given the welcome message displays
    Then the restart instruction should be in a highlighted box
    And the instruction should say "IMPORTANT: Restart Claude Code to activate"
    And the keyboard shortcut "Cmd+Q" should be mentioned

  @US_035 @restart @P0
  Scenario: Restart is first in next steps
    Given the next steps are displayed
    Then "Restart Claude Code" should be step 1
    And the step should explain why restart is needed

  # ==========================================================================
  # VERIFICATION IN CLAUDE CODE - US-036
  # ==========================================================================

  @US_036 @verification @P0
  Scenario: /nw:version shows complete information
    Given nWave has been installed and Claude Code restarted
    When the user runs "/nw:version" in Claude Code
    Then the output should show "nWave Framework v1.3.0"
    And the output should show "Installed: ~/.claude/agents/nw/"
    And the output should show "Agents: 47 | Commands: 23 | Templates: 12"
    And the output should show "All systems operational"

  @US_036 @verification @P0
  Scenario: Version counts match doctor output
    Given doctor showed 47 agents, 23 commands, 12 templates
    When the user runs "/nw:version"
    Then the output should show the same counts
    And "All systems operational" should confirm healthy status

  # ==========================================================================
  # CI/CD MODE - US-038
  # ==========================================================================

  @US_038 @ci @P1
  Scenario: Installation works in non-interactive CI mode
    Given the environment variable CI=true is set
    When the user runs "pipx install nwave"
    Then no interactive prompts should appear
    And the ASCII logo should be suppressed
    And the installation should complete silently
    And exit code should be 0 on success

  @US_038 @ci @P1
  Scenario: Machine-readable output in CI mode
    Given the environment variable CI=true is set
    And the flag "--format json" is used
    When the user runs "pipx install nwave --format json"
    Then the output should be valid JSON
    And the JSON should include "success": true
    And the JSON should include "version": "1.3.0"
    And the JSON should include counts for agents, commands, templates

  # ==========================================================================
  # CROSS-CUTTING: ROLLBACK - US-040
  # ==========================================================================

  @US_040 @rollback @P0
  Scenario: Automatic rollback on installation failure
    Given a previous nWave 1.2.0 installation exists
    And a backup was created at "~/.claude/backups/nwave-20260201-143025/"
    When the installation of 1.3.0 fails during agent file copy
    Then rollback should trigger automatically
    And files should be restored from the backup
    And the message should show "Installation failed. Previous version restored."
    And "nw doctor" should show version 1.2.0
    And the status should show "HEALTHY"

  @US_040 @rollback @P0
  Scenario: Manual rollback command
    Given nWave 1.3.0 is installed but has issues
    And a backup of 1.2.0 exists
    When the user runs "nw rollback"
    Then available backups should be listed with timestamps
    And the user can select a backup to restore
    And the selected backup should be restored
    And "nw doctor" should confirm restoration

  @US_040 @rollback @P0
  Scenario: Fresh install failure with no backup
    Given the user has no previous nWave installation
    When the first installation fails
    Then the message should show "Installation failed. No previous version to restore."
    And the message should show "Please retry: pipx install nwave"
    And partial files should be cleaned up

  @US_040 @rollback @P1
  Scenario: Rollback with no available backups
    Given nWave is installed but no backups exist
    When the user runs "nw rollback"
    Then the error should show "No backups available"
    And the message should show "Reinstall with: pipx install nwave --force"

  # ==========================================================================
  # CROSS-CUTTING: UPGRADE DETECTION - US-041
  # ==========================================================================

  @US_041 @upgrade @P0
  Scenario: Upgrade from older version
    Given the user has nWave 1.2.0 installed
    When the user runs "pipx install nwave" for version 1.3.0
    Then the installer should detect existing version 1.2.0
    And the message should show "Upgrading from 1.2.0 to 1.3.0"
    And a backup should be created automatically
    And the installation should proceed with upgrade path
    And doctor should show version 1.3.0 after completion

  @US_041 @upgrade @P0
  Scenario: Fresh install on clean system
    Given the user has no nWave installation
    When the user runs "pipx install nwave"
    Then the installer should detect no existing installation
    And the message should show "Installing nWave 1.3.0 (fresh install)"
    And no backup should be created
    And the welcome celebration should display

  @US_041 @upgrade @P0
  Scenario: Reinstall same version prompts confirmation
    Given the user has nWave 1.3.0 installed
    When the user runs "pipx install nwave" for version 1.3.0
    Then the installer should detect same version
    And the prompt should ask "nWave 1.3.0 already installed. Reinstall? [Y/n]"

  @US_041 @upgrade @P0
  Scenario: User accepts reinstall
    Given the reinstall prompt is displayed
    When the user types "Y"
    Then a backup should be created
    And the reinstallation should proceed
    And doctor should confirm successful reinstall

  @US_041 @upgrade @P1
  Scenario: User declines reinstall
    Given the reinstall prompt is displayed
    When the user types "n"
    Then the message should show "Installation cancelled. Existing installation unchanged."
    And no changes should be made

  @US_041 @upgrade @warning @P1
  Scenario: Downgrade warning
    Given the user has nWave 1.3.0 installed
    When the user attempts to install version 1.2.0
    Then the installer should detect downgrade
    And the warning should show "Downgrade detected: 1.3.0 -> 1.2.0"
    And the prompt should ask "This may cause issues. Continue? [Y/n]"

  @US_041 @ci @P1
  Scenario: CI mode auto-upgrades without prompts
    Given CI=true is set
    And existing nWave 1.2.0 is installed
    When CI runs "pipx install nwave" for 1.3.0
    Then the upgrade should proceed automatically
    And a backup should be created
    And no prompts should appear
    And exit code should be 0 on success

  # ==========================================================================
  # INTEGRATION - ARTIFACT CONSISTENCY
  # ==========================================================================

  @integration @horizontal @P0
  Scenario: Version is consistent across all displays
    Given nWave has been installed successfully
    Then the version in the download progress should be "1.3.0"
    And the version in the welcome message should be "1.3.0"
    And the version in "/nw:version" should be "1.3.0"
    And all versions should match the PyPI package version

  @integration @horizontal @P0
  Scenario: Install path is consistent across all displays
    Given nWave has been installed successfully
    Then the install path in pre-flight should be "~/.claude/agents/nw/"
    And the install path in doctor should be "~/.claude/agents/nw/"
    And the install path in "/nw:version" should be "~/.claude/agents/nw/"

  @integration @horizontal @P0
  Scenario: Component counts are consistent across Steps 4, 5, and 7
    Given nWave has been installed successfully
    Then the agent count in installation (Step 4) validation should be 47
    And the agent count in doctor (Step 5) should be 47
    And the agent count in /nw:version (Step 7) should be 47
    And command and template counts should similarly match
