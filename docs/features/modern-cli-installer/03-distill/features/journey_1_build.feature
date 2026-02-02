# Journey 1: Build Local Candidate (forge:build-local-candidate)
# Epic: modern_CLI_installer
# Acceptance Designer: Quinn
# Date: 2026-02-01

@journey_1 @build @local_dev
Feature: Build nWave Local Candidate
  As a developer modifying or extending nWave
  I want to build a pipx-compatible candidate wheel with semantic versioning
  So that I can test my changes locally before releasing

  Background:
    Given the developer has a terminal open
    And the developer is in the nWave project root directory
    And Python 3.12.1 is installed

  # ==========================================================================
  # HAPPY PATH - Complete Build Journey
  # ==========================================================================

  @US_010 @US_011 @US_012 @US_013 @US_014 @happy_path @P0
  Scenario: Successful local build with all checks passing
    Given the build package v1.2.1 is installed
    And pyproject.toml is valid with version "1.3.0"
    And the nWave/ source directory exists with 47 agents
    And the dist/ directory is writable
    And there are commits with "feat:" prefix since last tag
    When the developer runs "forge:build-local-candidate"
    Then the pre-flight checks should all pass
    And the version should be bumped to "1.3.0"
    And the candidate version should be "1.3.0-dev-20260201-001"
    And the build process should complete successfully
    And the wheel should be created at "dist/nwave-1.3.0-dev-20260201-001-py3-none-any.whl"
    And the wheel should contain 47 agents, 23 commands, and 12 templates
    And the success summary should display "FORGE: BUILD COMPLETE"
    And the developer should see "Install locally now? [Y/n]"

  @US_015 @happy_path @P1
  Scenario: Developer accepts prompted local install
    Given a successful build has completed with wheel at "dist/nwave-1.3.0-dev-20260201-001-py3-none-any.whl"
    And the developer sees "Install locally now? [Y/n]"
    When the developer types "Y" or presses Enter
    Then the install command should run "pipx install dist/nwave-1.3.0-dev-20260201-001-py3-none-any.whl --force"
    And the forge:install-local-candidate journey should continue

  @US_015 @happy_path @P1
  Scenario: Developer declines prompted local install
    Given a successful build has completed
    And the developer sees "Install locally now? [Y/n]"
    When the developer types "n"
    Then the manual install command should be displayed
    And the command should be "pipx install dist/nwave-1.3.0-dev-20260201-001-py3-none-any.whl --force"
    And the development mode alternative "pip install -e ." should be shown

  # ==========================================================================
  # PRE-FLIGHT CHECKS - US-010
  # ==========================================================================

  @US_010 @preflight @P0
  Scenario: Pre-flight check validates Python version
    Given Python 3.12.1 is installed
    When the developer runs "forge:build-local-candidate"
    Then the Python version check should pass
    And the check should display "Python version [check] 3.12.1 (3.10+ OK)"

  @US_010 @preflight @P0
  Scenario: Pre-flight check validates build package
    Given the build package v1.2.1 is installed
    When the pre-flight checks run
    Then the build package check should pass
    And the check should display "build package [check] v1.2.1 installed"

  @US_010 @preflight @P0
  Scenario: Pre-flight check validates pyproject.toml
    Given pyproject.toml exists and is valid with version "1.3.0"
    When the pre-flight checks run
    Then the pyproject.toml check should pass
    And the check should display "pyproject.toml [check] Valid, v1.3.0"

  @US_010 @preflight @P0
  Scenario: Pre-flight check validates source directory
    Given the nWave/ source directory exists
    When the pre-flight checks run
    Then the source directory check should pass
    And the check should display "Source directory [check] nWave/ found"

  @US_010 @preflight @P0
  Scenario: Pre-flight check validates dist directory
    Given the dist/ directory is writable
    When the pre-flight checks run
    Then the dist directory check should pass
    And the check should display "dist/ directory [check] Writable"

  # ==========================================================================
  # PRE-FLIGHT ERRORS - FIXABLE (US-019)
  # ==========================================================================

  @US_019 @preflight @error @fixable @P1
  Scenario: Pre-flight auto-repair for missing build package
    Given the build package is NOT installed
    When the developer runs "forge:build-local-candidate"
    Then the pre-flight check should fail for "build package"
    And the error should display "Pre-flight check failed: build package missing"
    And the prompt should ask "Install it now? [Y/n]"

  @US_019 @preflight @error @fixable @P1
  Scenario: Developer accepts auto-repair for missing build package
    Given the pre-flight check failed for missing build package
    And the developer sees "Install it now? [Y/n]"
    When the developer types "Y"
    Then the installer should run "pip install build"
    And a spinner should show "Installing build package..."
    And the message should display "build v1.2.1 installed successfully"
    And pre-flight checks should resume

  @US_019 @preflight @error @fixable @P1
  Scenario: Developer declines auto-repair for missing build package
    Given the pre-flight check failed for missing build package
    And the developer sees "Install it now? [Y/n]"
    When the developer types "n"
    Then the build should abort
    And the message should display "Build cancelled. Install build package manually:"
    And the command should show "pip install build"

  # ==========================================================================
  # PRE-FLIGHT ERRORS - BLOCKING (US-010)
  # ==========================================================================

  @US_010 @preflight @error @blocking @P0
  Scenario: Pre-flight fails for Python version too old
    Given the developer has Python 3.8.10 installed
    When the developer runs "forge:build-local-candidate"
    Then the pre-flight check should fail for "Python version"
    And the error should display "Python version too old"
    And the message should show "Required: Python 3.10+"
    And the message should show "Found: Python 3.8.10"
    And upgrade suggestions should be provided

  @US_010 @preflight @error @blocking @P0
  Scenario: Pre-flight fails for missing pyproject.toml
    Given pyproject.toml does NOT exist
    When the developer runs "forge:build-local-candidate"
    Then the pre-flight check should fail for "pyproject.toml"
    And the error should display "pyproject.toml not found"
    And the message should show "forge:build-local-candidate must be run from the nWave project root directory"

  @US_010 @preflight @error @blocking @P0
  Scenario: Pre-flight fails for invalid pyproject.toml
    Given pyproject.toml has a syntax error on line 42
    When the developer runs "forge:build-local-candidate"
    Then the pre-flight check should fail for "pyproject.toml"
    And the error should display "pyproject.toml invalid"
    And the error should show "Error at line 42: unexpected token"

  @US_010 @preflight @error @blocking @P1
  Scenario: Pre-flight fails for missing source directory
    Given the nWave/ source directory does NOT exist
    When the developer runs "forge:build-local-candidate"
    Then the pre-flight check should fail for "Source directory"
    And the error should display "nWave/ directory not found"

  # ==========================================================================
  # VERSION BUMPING - US-011
  # ==========================================================================

  @US_011 @versioning @P0
  Scenario: Version bump from conventional commits - MINOR
    Given pre-flight checks have passed
    And the current version in pyproject.toml is "1.2.0"
    And there are commits with "feat:" prefix since last tag
    When the version resolution runs
    Then the bump type should be "MINOR"
    And the new version should be "1.3.0"
    And the candidate version should be "1.3.0-dev-20260201-001"

  @US_011 @versioning @P0
  Scenario: Version bump detects breaking changes - MAJOR
    Given pre-flight checks have passed
    And the current version in pyproject.toml is "1.2.0"
    And there are commits with "BREAKING CHANGE:" since last tag
    When the version resolution runs
    Then the bump type should be "MAJOR"
    And the new version should be "2.0.0"

  @US_011 @versioning @P0
  Scenario: Version bump detects fix commits - PATCH
    Given pre-flight checks have passed
    And the current version in pyproject.toml is "1.2.0"
    And there are only commits with "fix:" prefix since last tag
    When the version resolution runs
    Then the bump type should be "PATCH"
    And the new version should be "1.2.1"

  @US_016 @versioning @P1
  Scenario: Force version override
    Given pre-flight checks have passed
    And the current version is "1.2.0"
    When the developer runs "forge:build-local-candidate --force-version 2.0.0"
    Then the new version should be "2.0.0"
    And the candidate version should be "2.0.0-dev-20260201-001"

  @US_016 @versioning @error @P1
  Scenario: Force version rejected when too low
    Given pre-flight checks have passed
    And the current version is "1.3.0"
    When the developer runs "forge:build-local-candidate --force-version 1.2.0"
    Then the error should display "Force version rejected"
    And the message should show "Force version must be higher than current"

  @US_017 @versioning @P1
  Scenario: Daily sequence increments on same day
    Given a candidate "1.3.0-dev-20260201-001" was built earlier today
    When the developer runs "forge:build-local-candidate" again
    Then the candidate version should be "1.3.0-dev-20260201-002"

  @US_017 @versioning @P1
  Scenario: Daily sequence resets on new day
    Given yesterday's last build was "1.3.0-dev-20260131-005"
    When the developer runs "forge:build-local-candidate" today
    Then the candidate version should be "1.3.0-dev-20260201-001"

  @US_011 @versioning @warning @P1
  Scenario: Warning when no commits since last tag
    Given pre-flight checks have passed
    And there are no commits since the last tag
    When the version resolution runs
    Then a warning should display "No commits since last tag"
    And the build should proceed with the current version as candidate

  # ==========================================================================
  # BUILD PROCESS - US-012
  # ==========================================================================

  @US_012 @build @P0
  Scenario: Build process shows progress phases
    Given pre-flight checks have passed
    And version resolution completed with candidate "1.3.0-dev-20260201-001"
    When the build process runs
    Then a phase table should display
    And the phase "Cleaning dist/" should show progress then checkmark
    And the phase "Processing source" should show "127 files"
    And the phase "Running build backend" should show progress bar
    And all phases should complete with checkmarks
    And the build duration should be displayed

  @US_012 @build @P0
  Scenario: Build cleans old wheel files
    Given pre-flight checks have passed
    And an old wheel exists at "dist/nwave-1.2.0-py3-none-any.whl"
    When the build process runs
    Then the old wheel should be removed
    And the phase should show "Cleaning dist/ [check] Removed old"

  @US_012 @build @error @P0
  Scenario: Build fails due to backend error
    Given pre-flight checks have passed
    When the build process runs
    And the build backend encounters an error "Invalid entry point"
    Then the phase "Running build backend" should show failure
    And the error message should display "Invalid entry point"
    And a suggested fix should be provided
    And the build should abort

  # ==========================================================================
  # WHEEL VALIDATION - US-013
  # ==========================================================================

  @US_013 @validation @P0
  Scenario: Wheel validation checks all required aspects
    Given a wheel has been built at "dist/nwave-1.3.0-dev-20260201-001-py3-none-any.whl"
    When the wheel validation runs
    Then the wheel filename should be displayed
    And the validation table should show all checks
    And "Wheel format" should pass with checkmark
    And "Metadata present" should pass with checkmark
    And "Entry points" should pass with "nw CLI defined"
    And "Agents bundled" should pass with "47"
    And "Commands bundled" should pass with "23"
    And "Templates bundled" should pass with "12"
    And "pipx compatible" should pass with "Verified"
    And the final status should show "Wheel validation passed!"

  @US_013 @validation @error @P0
  Scenario: Wheel validation detects missing agents
    Given a wheel has been built but agents directory was excluded
    When the wheel validation runs
    Then "Agents bundled" should show failure with "0 found"
    And the validation should fail
    And error should suggest checking pyproject.toml include patterns

  @US_013 @validation @error @P0
  Scenario: Wheel validation detects missing entry point
    Given a wheel has been built but entry point is misconfigured
    When the wheel validation runs
    Then "Entry points" should show failure
    And error should show where to fix in pyproject.toml

  # ==========================================================================
  # SUCCESS SUMMARY - US-014
  # ==========================================================================

  @US_014 @summary @P0
  Scenario: Success summary displays complete information
    Given wheel validation has passed
    When the success summary displays
    Then the header should show "FORGE: BUILD COMPLETE"
    And the celebration message should show "nWave v1.3.0 wheel built successfully!"
    And the artifact table should show wheel path "dist/nwave-1.3.0-dev-20260201-001-py3-none-any.whl"
    And the artifact table should show wheel size and timestamp
    And the contents table should show 47 agents, 23 commands, and 12 templates

  @US_014 @summary @P0
  Scenario: Success summary shows correct wheel path
    Given wheel validation has passed
    When the success summary displays
    Then the wheel path should be "dist/nwave-1.3.0-dev-20260201-001-py3-none-any.whl"
    And the wheel file should exist at that path

  # ==========================================================================
  # CI/CD MODE - US-018
  # ==========================================================================

  @US_018 @ci @P1
  Scenario: Build works in non-interactive CI mode
    Given the environment variable CI=true is set
    And the build environment is properly configured
    When the developer runs "forge:build-local-candidate"
    Then no interactive prompts should appear
    And the install prompt should be skipped
    And the build should complete silently
    And exit code should be 0 on success

  @US_018 @ci @P1
  Scenario: Build with --no-prompt flag skips install prompt
    Given the build environment is properly configured
    When the developer runs "forge:build-local-candidate --no-prompt"
    Then the build should complete normally
    And the install prompt should be skipped
    And the wheel path should be printed for scripting

  @US_018 @ci @P1
  Scenario: Build with --install flag auto-installs
    Given the build environment is properly configured
    When the developer runs "forge:build-local-candidate --install"
    Then the build should complete normally
    And the install should proceed automatically without prompting
    And the full forge:install-local-candidate flow should complete

  # ==========================================================================
  # INTEGRATION - ARTIFACT CONSISTENCY
  # ==========================================================================

  @integration @horizontal @P0
  Scenario: Version is consistent across all build steps
    Given forge:build-local-candidate has completed successfully
    Then the version in pre-flight should be "1.3.0"
    And the version in wheel filename should be "1.3.0-dev-20260201-001"
    And the version in summary should be "1.3.0"
    And all versions should derive from pyproject.toml

  @integration @horizontal @P0
  Scenario: Agent count is consistent across validation and summary
    Given forge:build-local-candidate has completed successfully
    Then the agent count in validation should be 47
    And the agent count in summary should be 47
    And both should match actual files bundled in wheel

  @integration @horizontal @P0
  Scenario: Wheel path is consistent across summary and install prompt
    Given forge:build-local-candidate has completed successfully
    Then the wheel path in summary should match wheel path in install prompt
    And the wheel path should point to an existing file
