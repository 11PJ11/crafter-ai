# nWave Versioning and Release Management - Acceptance Tests
#
# DISTILL Wave Deliverable
# Author: Quinn (acceptance-designer)
# Date: 2026-01-28
#
# Implementation Strategy: One E2E test at a time
# - First scenario in each feature is ACTIVE (no @skip tag)
# - Remaining scenarios are tagged @skip until prior scenarios pass
# - Enable one scenario at a time to prevent commit blocks
#
# Hexagonal Boundary: ALL tests invoke through CLI entry points only
# - CORRECT: subprocess.run(["python", "nwave_cli.py", "version"])
# - FORBIDDEN: from nWave.core.version_management import VersionComparator

# ==============================================================================
# FEATURE: VERSION CHECK
# User Story: US-001 - Check Installed Version
# ==============================================================================

@us-001
Feature: Check Installed Version
  As an nWave user
  I want to check my installed version and see if updates are available
  So that I can make informed decisions about updating my installation

  Background:
    Given a clean test environment with isolated ~/.claude/ directory
    And the nWave CLI is available at the driving port entry point

  # ACTIVE - Implement this scenario first
  Scenario: Display version with update available
    Given Marco has nWave v1.2.3 installed in the test ~/.claude/ directory
    And the VERSION file contains "1.2.3"
    And the GitHub API returns v1.3.0 as the latest release
    When Marco runs the /nw:version command through the CLI entry point
    Then the output displays "nWave v1.2.3 (update available: v1.3.0)"
    And the watermark file ~/.claude/nwave.update is updated with current timestamp
    And the watermark file contains latest_version "1.3.0"

  # ACTIVE - Step 03-02: Up-to-date version display
  Scenario: Display version when up-to-date
    Given Sofia has nWave v1.3.0 installed in the test ~/.claude/ directory
    And the VERSION file contains "1.3.0"
    And the GitHub API returns v1.3.0 as the latest release
    When Sofia runs the /nw:version command through the CLI entry point
    Then the output displays "nWave v1.3.0 (up to date)"

  # ACTIVE - Step 03-03: Offline version display
  Scenario: Display version when offline
    Given Luca has nWave v1.2.3 installed in the test ~/.claude/ directory
    And the VERSION file contains "1.2.3"
    And network connectivity is unavailable for GitHub API
    When Luca runs the /nw:version command through the CLI entry point
    Then the output displays "nWave v1.2.3 (Unable to check for updates)"
    And no error is thrown
    And the CLI exit code is 0

  # ACTIVE - Step 03-04: Stale watermark triggers GitHub check
  Scenario: Daily auto-check updates watermark when stale
    Given Elena has nWave v1.2.3 installed in the test ~/.claude/ directory
    And the watermark file shows last_check was 25 hours ago
    And the GitHub API returns v1.3.0 as the latest release
    When Elena runs the /nw:version command through the CLI entry point
    Then the system checks GitHub Releases
    And the watermark file is updated with new timestamp
    And the watermark file contains latest_version "1.3.0"

  # ACTIVE - Step 03-05: Skip update check when watermark is fresh
  Scenario: Skip update check when watermark is fresh
    Given Marco has nWave v1.2.3 installed in the test ~/.claude/ directory
    And the watermark file shows last_check was 1 hour ago
    And the watermark file contains latest_version "1.3.0"
    When Marco runs the /nw:version command through the CLI entry point
    Then no GitHub API call is made
    And the output displays "nWave v1.2.3 (update available: v1.3.0)"

  # ACTIVE - Step 03-06: Handle missing VERSION file gracefully
  Scenario: Handle missing VERSION file gracefully
    Given a user has an incomplete installation in the test ~/.claude/ directory
    And the VERSION file does not exist
    When the user runs the /nw:version command through the CLI entry point
    Then an error displays "VERSION file not found. nWave may be corrupted."
    And the CLI exit code is non-zero

  # ACTIVE - Step 03-07: Rate limit handling
  Scenario: Handle GitHub API rate limit gracefully
    Given Marco has nWave v1.2.3 installed in the test ~/.claude/ directory
    And the GitHub API returns HTTP 403 with rate limit headers
    When Marco runs the /nw:version command through the CLI entry point
    Then the output displays "nWave v1.2.3 (Unable to check for updates)"
    And no error is thrown


# ==============================================================================
# FEATURE: UPDATE TO LATEST RELEASE
# User Story: US-002 - Update nWave to Latest Release
# ==============================================================================

@us-002
Feature: Update nWave to Latest Release
  As an nWave user
  I want to safely update to the latest official release
  So that I can benefit from bug fixes and new features without losing my customizations

  Background:
    Given a clean test environment with isolated ~/.claude/ directory
    And the nWave CLI is available at the driving port entry point
    And a mock download server is available for release assets

  # ACTIVE - Implement this scenario first
  Scenario: Successful update with backup creation
    Given Giulia has nWave v1.2.3 installed in the test ~/.claude/ directory
    And the GitHub API returns v1.3.0 as the latest release with SHA256 checksum "abc123def456"
    And the download server provides a valid release asset matching the checksum
    When Giulia runs the /nw:update command through the CLI entry point
    And she confirms the update when prompted
    Then a full backup is created at ~/.claude.backup.{timestamp}/
    And the release asset is downloaded from the mock server
    And the download is validated against SHA256 checksum "abc123def456"
    And nWave is updated to v1.3.0 in the test ~/.claude/ directory
    And the VERSION file now contains "1.3.0"
    And the output displays "Update complete."

  @skip
  Scenario: Major version change requires confirmation
    Given Paolo has nWave v1.3.0 installed in the test ~/.claude/ directory
    And the GitHub API returns v2.0.0 as the latest release
    When Paolo runs the /nw:update command through the CLI entry point
    Then a warning displays "Major version change detected (1.x to 2.x). This may break existing workflows."
    And the prompt displays "Continue? [y/N]"
    And the update waits for confirmation before proceeding

  @skip
  Scenario: Major version update proceeds with confirmation
    Given Paolo has nWave v1.3.0 installed in the test ~/.claude/ directory
    And the GitHub API returns v2.0.0 as the latest release with valid checksum
    And the download server provides a valid release asset
    When Paolo runs the /nw:update command through the CLI entry point
    And Paolo confirms with "y" when prompted about major version change
    Then the update proceeds
    And nWave is updated to v2.0.0

  # ACTIVE - Step 04-04: Major version update cancellation (denial path)
  Scenario: Major version update cancelled with denial
    Given Paolo has nWave v1.3.0 installed in the test ~/.claude/ directory
    And the GitHub API returns v2.0.0 as the latest release
    When Paolo runs the /nw:update command through the CLI entry point
    And Paolo denies with "n" when prompted about major version change
    Then the update is cancelled
    And the VERSION file still contains "1.3.0"
    And no backup was created

  # ACTIVE - Step 04-05: Local RC version triggers customization warning
  Scenario: Local RC version triggers customization warning
    Given Francesca has a local RC version v1.2.3-rc.main.20260127.1 installed
    And the VERSION file contains "1.2.3-rc.main.20260127.1"
    And the GitHub API returns v1.3.0 as the latest release
    When Francesca runs the /nw:update command through the CLI entry point
    Then a warning displays "Local customizations detected. Update will overwrite."
    And Francesca can choose to proceed or cancel

  @skip
  Scenario: Network failure during download leaves installation unchanged
    Given Antonio has nWave v1.2.3 installed in the test ~/.claude/ directory
    And the GitHub API returns v1.3.0 as the latest release
    And the download server simulates a network failure mid-download
    When Antonio runs the /nw:update command through the CLI entry point
    And Antonio confirms the update when prompted
    Then an error displays "Download failed: network error. Your nWave installation is unchanged."
    And the test ~/.claude/ directory contains the original v1.2.3 installation
    And the VERSION file still contains "1.2.3"
    And no partial download files remain

  @skip
  Scenario: Checksum validation failure aborts update
    Given Chiara has nWave v1.2.3 installed in the test ~/.claude/ directory
    And the GitHub API returns v1.3.0 as the latest release with SHA256 checksum "expected123"
    And the download server provides a corrupted file with different checksum
    When Chiara runs the /nw:update command through the CLI entry point
    And Chiara confirms the update when prompted
    Then an error displays "Download corrupted (checksum mismatch). Update aborted. Your nWave installation is unchanged."
    And the corrupted download is deleted
    And the test ~/.claude/ directory is unchanged
    And the VERSION file still contains "1.2.3"

  @skip
  Scenario: Backup rotation maintains exactly 3 copies
    Given Roberto has nWave v1.2.3 installed in the test ~/.claude/ directory
    And 3 existing backups exist at ~/.claude.backup.20260124120000/
    And ~/.claude.backup.20260125120000/
    And ~/.claude.backup.20260126120000/
    And the GitHub API returns v1.3.0 as the latest release with valid checksum
    And the download server provides a valid release asset
    When Roberto runs the /nw:update command through the CLI entry point
    And Roberto confirms the update when prompted
    Then a new backup is created with current timestamp
    And the oldest backup ~/.claude.backup.20260124120000/ is deleted
    And exactly 3 backups remain

  # ACTIVE - Step 04-09
  Scenario: Non-nWave user content is preserved during update
    Given Maria has nWave v1.2.3 installed in the test ~/.claude/ directory
    And Maria has custom agents in ~/.claude/agents/my-custom-agent/
    And Maria has custom commands in ~/.claude/commands/my-custom-command/
    And the GitHub API returns v1.3.0 as the latest release with valid checksum
    And the download server provides a valid release asset
    When Maria runs the /nw:update command through the CLI entry point
    And Maria confirms the update when prompted
    Then her custom agent at ~/.claude/agents/my-custom-agent/ remains untouched
    And her custom command at ~/.claude/commands/my-custom-command/ remains untouched
    And only nWave-prefixed content in ~/.claude/agents/nw/ is replaced
    And only nWave-prefixed content in ~/.claude/commands/nw/ is replaced

  # ACTIVE - Step 04-10: Already up-to-date shows message without update
  Scenario: Already up-to-date shows message without update
    Given Sofia has nWave v1.3.0 installed in the test ~/.claude/ directory
    And the GitHub API returns v1.3.0 as the latest release
    When Sofia runs the /nw:update command through the CLI entry point
    Then the output displays "Already up to date (v1.3.0)."
    And no backup is created
    And no download occurs


# ==============================================================================
# FEATURE: BUILD CUSTOM LOCAL DISTRIBUTION
# User Story: US-003 - Build Custom Local Distribution
# ==============================================================================

@us-003
Feature: Build Custom Local Distribution
  As an nWave power user
  I want to build a custom distribution from my local modifications
  So that I can test changes before deploying them

  Background:
    Given a clean test environment with isolated repository directory
    And the nWave CLI is available at the driving port entry point
    And a mock test runner is configured

  # ACTIVE - Implement this scenario first
  Scenario: Successful build with install prompt on main branch
    Given Alessandro is working in the test repository
    And the git branch is "main"
    And the pyproject.toml contains base version "1.2.3"
    And all tests pass when the test runner is invoked
    And today's date is 2026-01-27
    When Alessandro runs the /nw:forge command through the CLI entry point
    Then the dist/ directory is cleaned before build
    And the build process runs all tests first
    And dist/ is created with the built distribution
    And the version is set to "1.2.3-rc.main.20260127.1"
    And the prompt displays "Install: [Y/n]"

  @skip
  Scenario: Build fails when tests fail
    Given Benedetta is working in the test repository
    And the git branch is "main"
    And the pyproject.toml contains base version "1.2.3"
    And 3 tests fail when the test runner is invoked
    When Benedetta runs the /nw:forge command through the CLI entry point
    Then the build process runs tests first
    And the build aborts with exit code non-zero
    And the error displays "Build failed: 3 test failures. Fix tests before building."
    And the dist/ directory is not modified

  @skip
  Scenario: RC counter increments on same day builds
    Given Carlo is working in the test repository
    And the git branch is "main"
    And the pyproject.toml contains base version "1.2.3"
    And today's date is 2026-01-27
    And a previous build created version "1.2.3-rc.main.20260127.1" in dist/
    And all tests pass when the test runner is invoked
    When Carlo runs the /nw:forge command through the CLI entry point
    Then the version becomes "1.2.3-rc.main.20260127.2"
    And the previous dist/ contents are cleaned before the new build

  @skip
  Scenario: RC counter resets on new day
    Given Carlo is working in the test repository
    And the git branch is "main"
    And the pyproject.toml contains base version "1.2.3"
    And today's date is 2026-01-28
    And a previous build from yesterday created version "1.2.3-rc.main.20260127.3"
    And all tests pass when the test runner is invoked
    When Carlo runs the /nw:forge command through the CLI entry point
    Then the version becomes "1.2.3-rc.main.20260128.1"

  # ACTIVE - Step 05-05: Feature branch name included in RC version
  Scenario: Feature branch name included in RC version
    Given Daniela is working in the test repository
    And the git branch is "feature/new-agent"
    And the pyproject.toml contains base version "1.2.3"
    And today's date is 2026-01-27
    And all tests pass when the test runner is invoked
    When Daniela runs the /nw:forge command through the CLI entry point
    Then the version becomes "1.2.3-rc.feature-new-agent.20260127.1"
    And special characters in the branch name are normalized to hyphens

  @skip
  Scenario: User declines install after successful build
    Given Alessandro is working in the test repository
    And all tests pass when the test runner is invoked
    When Alessandro runs the /nw:forge command through the CLI entry point
    And Alessandro responds "n" to the install prompt
    Then the dist/ directory contains the built distribution
    And no installation to ~/.claude/ occurs
    And the CLI exits with success code

  @skip
  Scenario: User accepts install after successful build
    Given Alessandro is working in the test repository
    And a clean test ~/.claude/ directory exists
    And all tests pass when the test runner is invoked
    When Alessandro runs the /nw:forge command through the CLI entry point
    And Alessandro responds "Y" to the install prompt
    Then the /nw:forge:install command is invoked
    And the distribution is installed to ~/.claude/


# ==============================================================================
# FEATURE: INSTALL BUILT DISTRIBUTION
# User Story: US-004 - Install Built Distribution
# ==============================================================================

@us-004
Feature: Install Built Distribution
  As an nWave user who has built a custom distribution
  I want to install it to my ~/.claude/ directory
  So that I can use my customized version of nWave

  Background:
    Given a clean test environment with isolated ~/.claude/ directory
    And a clean test repository directory
    And the nWave CLI is available at the driving port entry point

  # ACTIVE - Implement this scenario first
  Scenario: Successful installation with smoke test
    Given Elena has a valid dist/ directory from a previous /nw:forge build
    And the dist/ directory contains all required nWave structure
    And the dist/ VERSION file contains "1.2.3-rc.main.20260127.1"
    When Elena runs the /nw:forge:install command through the CLI entry point
    Then the contents of dist/ are copied to the test ~/.claude/ directory
    And nWave-prefixed content in ~/.claude/agents/nw/ is replaced
    And nWave-prefixed content in ~/.claude/commands/nw/ is replaced
    And the smoke test runs /nw:version successfully
    And the success message displays "Installation complete."

  @skip
  Scenario: Installation preserves non-nWave user content
    Given Elena has a valid dist/ directory from a previous /nw:forge build
    And she has custom agents in ~/.claude/agents/my-agent/
    And she has custom commands in ~/.claude/commands/my-command/
    When Elena runs the /nw:forge:install command through the CLI entry point
    Then her custom agent at ~/.claude/agents/my-agent/ remains untouched
    And her custom command at ~/.claude/commands/my-command/ remains untouched

  @skip
  Scenario: Installation fails when dist/ directory does not exist
    Given Fabio has no dist/ directory in the repository
    When Fabio runs the /nw:forge:install command through the CLI entry point
    Then the error displays "No distribution found. Run /nw:forge first to build."
    And the test ~/.claude/ directory is unchanged
    And the CLI exit code is non-zero

  @skip
  Scenario: Installation fails when dist/ is missing required files
    Given Greta has a dist/ directory that is missing required files
    And the dist/ directory exists but is empty
    When Greta runs the /nw:forge:install command through the CLI entry point
    Then the error displays "Invalid distribution: missing required files. Rebuild with /nw:forge."
    And the test ~/.claude/ directory is unchanged
    And the CLI exit code is non-zero

  @skip
  Scenario: Smoke test failure reports error
    Given Elena has a dist/ directory with corrupted files
    And the smoke test for /nw:version will fail
    When Elena runs the /nw:forge:install command through the CLI entry point
    Then installation proceeds
    And the smoke test fails
    And a warning displays "Installation complete but smoke test failed. Verify with /nw:version."


# ==============================================================================
# FEATURE: CREATE OFFICIAL RELEASE
# User Story: US-005 - Create Official Release
# ==============================================================================

@us-005
Feature: Create Official Release
  As a repository administrator
  I want to create an official release through a controlled CI/CD process
  So that users can safely update to validated new versions

  Background:
    Given a clean test environment with mock Git and GitHub CLI
    And the nWave CLI is available at the driving port entry point

  # ACTIVE - Implement this scenario first
  Scenario: Successful release PR creation from development branch
    Given Matteo has repository admin access configured
    And the git branch is "development"
    And there are no uncommitted changes
    When Matteo runs the /nw:forge:release command through the CLI entry point
    Then a PR is created from development to main via gh CLI
    And the output displays the PR number and URL
    And the output indicates "PR created. Pipeline running..."

  @skip
  Scenario: Release command fails on main branch
    Given Paola is on the main branch
    When Paola runs the /nw:forge:release command through the CLI entry point
    Then the error displays "Release must be initiated from the development branch."
    And no PR is created
    And the CLI exit code is non-zero

  @skip
  Scenario: Release command fails on feature branch
    Given Paola is on a feature/test branch
    When Paola runs the /nw:forge:release command through the CLI entry point
    Then the error displays "Release must be initiated from the development branch."
    And no PR is created
    And the CLI exit code is non-zero

  @skip
  Scenario: Permission denied for non-admin user
    Given Oscar does not have repository write access configured
    And the git branch is "development"
    And the gh CLI returns a permission denied error
    When Oscar runs the /nw:forge:release command through the CLI entry point
    Then the error displays "Permission denied. You don't have access to create releases for this repository."
    And no PR is created
    And the CLI exit code is non-zero

  # ACTIVE - Step 07-05: Release fails with uncommitted changes
  Scenario: Release fails with uncommitted changes
    Given Matteo has repository admin access configured
    And the git branch is "development"
    And there are uncommitted changes in the working directory
    When Matteo runs the /nw:forge:release command through the CLI entry point
    Then the error displays "Uncommitted changes detected. Commit or stash changes before releasing."
    And no PR is created
    And the CLI exit code is non-zero

  @skip
  Scenario: Release shows pipeline status after PR creation
    Given Matteo has repository admin access configured
    And the git branch is "development"
    And there are no uncommitted changes
    And the CI/CD pipeline is configured to run on PR
    When Matteo runs the /nw:forge:release command through the CLI entry point
    Then a PR is created
    And the output displays "PR #123 created."
    And the output displays "CI/CD pipeline triggered. Monitor at: {pr_url}"
