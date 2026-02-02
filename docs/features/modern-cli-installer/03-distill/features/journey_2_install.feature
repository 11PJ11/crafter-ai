# Journey 2: Install Local Candidate (forge:install-local-candidate)
# Epic: modern_CLI_installer
# Acceptance Designer: Quinn
# Date: 2026-02-01

@journey_2 @install @release @local_dev
Feature: Install Local Candidate
  As a developer preparing release or testing installation
  I want to install and validate a locally-built nWave candidate
  So that I can verify the release is ready for CI/CD and PyPI

  Background:
    Given the developer has a terminal open
    And the developer is in the nWave project root directory
    And Python 3.12.1 is installed
    And pipx v1.4.3 is installed and in PATH

  # ==========================================================================
  # HAPPY PATH - Complete Install Journey
  # ==========================================================================

  @US_020 @US_021 @US_022 @US_023 @US_024 @happy_path @P0
  Scenario: Successful candidate installation with all checks passing
    Given a wheel exists at "dist/nwave-1.3.0-dev-20260201-001-py3-none-any.whl"
    And the wheel has valid metadata and entry points
    And ~/.claude is writable
    And CHANGELOG.md has an entry for version "1.3.0"
    When the developer runs "forge:install-local-candidate"
    Then the pre-flight checks should all pass
    And the release readiness validation should pass with "READY FOR PYPI"
    And the candidate should be installed via pipx
    And the doctor verification should show "HEALTHY" status
    And the release report should display "FORGE: CANDIDATE INSTALLED"
    And the test checklist should be shown

  @US_021 @happy_path @P0
  Scenario: Release readiness shows all PyPI requirements met
    Given a wheel exists with valid metadata
    And the wheel includes LICENSE and README.md
    And CHANGELOG.md has an entry for version "1.3.0"
    When the release readiness validation runs
    Then "twine check" should pass with checkmark
    And "Metadata complete" should pass with checkmark
    And "Entry points" should pass with "nw CLI defined"
    And "CHANGELOG exists" should pass with "Recent entry OK"
    And "Version format" should pass with "PEP 440 valid"
    And "License bundled" should pass with checkmark
    And "README bundled" should pass with checkmark
    And the status should show "READY FOR PYPI"

  @US_023 @happy_path @P0
  Scenario: Doctor verification matches install-nwave pattern
    Given the candidate has been installed successfully
    When the doctor verification runs
    Then "Core installation" should show the install path
    And "Agent files" should show "47 OK"
    And "Command files" should show "23 OK"
    And "Template files" should show "12 OK"
    And "Config valid" should show "nwave.yaml OK"
    And "Permissions" should show "All accessible"
    And "Version match" should show "1.3.0-dev-20260201-001"
    And the status should show "HEALTHY"

  @US_024 @happy_path @P0
  Scenario: Release report provides complete summary
    Given doctor verification has passed
    When the release report displays
    Then the header should show "FORGE: CANDIDATE INSTALLED"
    And the release summary should show version "1.3.0-dev-20260201-001"
    And the release summary should show branch and timestamps
    And the install manifest should show 47 agents, 23 commands, 12 templates
    And the release readiness section should show all checks passed
    And the test checklist should list verification steps

  # ==========================================================================
  # PRE-FLIGHT CHECKS - US-020
  # ==========================================================================

  @US_020 @preflight @P0
  Scenario: Pre-flight validates Python version
    Given the developer runs "forge:install-local-candidate"
    When the pre-flight checks run
    Then the Python version check should verify 3.10+
    And the check should display "Python version [check] 3.12.1 (3.10+ OK)"

  @US_020 @preflight @P0
  Scenario: Pre-flight validates pipx availability
    Given pipx v1.4.3 is installed
    When the pre-flight checks run
    Then the pipx check should pass
    And the check should display "pipx available [check] v1.4.3 installed"

  @US_020 @preflight @P0
  Scenario: Pre-flight validates install path writable
    Given ~/.claude directory is writable
    When the pre-flight checks run
    Then the permission check should pass
    And the check should display "~/.claude writable [check] Permissions OK"

  @US_020 @preflight @P0
  Scenario: Pre-flight validates wheel exists
    Given a wheel exists at "dist/nwave-1.3.0-dev-20260201-001-py3-none-any.whl"
    When the pre-flight checks run
    Then the wheel existence check should pass
    And the check should display "Wheel exists [check] dist/nwave-1.3.0-dev-20260201-001-py3-none-any.whl"

  @US_020 @preflight @P0
  Scenario: Pre-flight validates wheel format
    Given a valid wheel file exists at "dist/nwave-1.3.0-dev-20260201-001-py3-none-any.whl"
    When the pre-flight checks run
    Then the wheel format check should pass
    And the check should display "Wheel format [check] Valid .whl"

  # ==========================================================================
  # PRE-FLIGHT ERRORS - FIXABLE (US-025)
  # ==========================================================================

  @US_025 @preflight @error @fixable @P1
  Scenario: Pre-flight offers to build when no wheel found
    Given no wheel exists in dist/
    When the developer runs "forge:install-local-candidate"
    Then the pre-flight check should fail for "Wheel exists"
    And the error should display "No wheel found in dist/"
    And the prompt should ask "Run forge:build-local now? [Y/n]"

  @US_025 @preflight @error @fixable @P1
  Scenario: Developer accepts auto-chain to build-local
    Given the pre-flight check failed for no wheel
    And the developer sees "Run forge:build-local now? [Y/n]"
    When the developer types "Y"
    Then forge:build-local should run
    And after successful build, install-local-candidate should resume
    And the message should display "Resuming install-local-candidate..."

  @US_025 @preflight @error @fixable @P1
  Scenario: Developer declines auto-chain to build-local
    Given the pre-flight check failed for no wheel
    And the developer sees "Run forge:build-local now? [Y/n]"
    When the developer types "n"
    Then the install should abort
    And the message should display "Build a wheel first with: forge:build-local"

  @US_026 @preflight @warning @P1
  Scenario: Pre-flight prompts when multiple wheels found
    Given multiple wheels exist in dist/:
      | wheel                                           |
      | dist/nwave-1.2.0-py3-none-any.whl              |
      | dist/nwave-1.3.0-dev-20260201-001-py3-none-any.whl |
      | dist/nwave-1.3.0-dev-20260201-002-py3-none-any.whl |
    When the developer runs "forge:install-local-candidate"
    Then a warning should display "Multiple wheels found in dist/"
    And the list of wheels should be shown with numbers
    And the prompt should ask "Select wheel to install [1-3, or 'c' to cancel]:"

  @US_026 @preflight @warning @P1
  Scenario: Developer selects wheel from multiple options
    Given the developer sees multiple wheel options numbered 1-3
    When the developer types "2"
    Then the second wheel should be selected
    And the message should display "Selected: nwave-1.3.0-dev-20260201-001-py3-none-any.whl"
    And the installation should continue

  @US_026 @preflight @warning @P1
  Scenario: Developer cancels wheel selection
    Given the developer sees multiple wheel options
    When the developer types "c"
    Then the installation should be cancelled
    And the message should display "Selection cancelled"

  # ==========================================================================
  # PRE-FLIGHT ERRORS - BLOCKING (US-020)
  # ==========================================================================

  @US_020 @preflight @error @blocking @P0
  Scenario: Pre-flight fails for missing pipx
    Given pipx is NOT installed
    When the developer runs "forge:install-local-candidate"
    Then the pre-flight check should fail for "pipx available"
    And the error should display "pipx not installed"
    And instructions should show "pip install pipx && pipx ensurepath"

  @US_020 @preflight @error @blocking @P0
  Scenario: Pre-flight fails for Python version too old
    Given the developer has Python 3.8.10 installed
    When the developer runs "forge:install-local-candidate"
    Then the pre-flight check should fail for "Python version"
    And the error should display "Python version too old"
    And upgrade suggestions should be provided

  @US_020 @preflight @error @blocking @P1
  Scenario: Pre-flight fails for permission denied
    Given ~/.claude directory is NOT writable
    When the developer runs "forge:install-local-candidate"
    Then the pre-flight check should fail for "~/.claude writable"
    And the error should display "Cannot write to ~/.claude/"
    And permission fix suggestions should be provided
    And NWAVE_INSTALL_PATH alternative should be mentioned

  # ==========================================================================
  # RELEASE READINESS VALIDATION - US-021
  # ==========================================================================

  @US_021 @release_readiness @P0
  Scenario: Release readiness runs twine check
    Given a wheel exists with complete metadata
    When the release readiness validation runs
    Then twine check should execute against the wheel
    And "twine check" should pass with checkmark

  @US_021 @release_readiness @P0
  Scenario: Release readiness validates entry points
    Given a wheel exists with nw CLI entry point
    When the release readiness validation runs
    Then "Entry points" should pass with "nw CLI defined"

  @US_021 @release_readiness @P0
  Scenario: Release readiness validates version format
    Given a wheel exists with PEP 440 compliant version "1.3.0-dev-20260201-001"
    When the release readiness validation runs
    Then "Version format" should pass with "PEP 440 valid"

  @US_021 @release_readiness @warning @P1
  Scenario: Release readiness warns for missing CHANGELOG entry
    Given a wheel exists with valid metadata
    And CHANGELOG.md has NO entry for version "1.3.0"
    When the release readiness validation runs
    Then "CHANGELOG exists" should show warning with "No recent entry"
    And the status should show "WARNINGS (non-blocking)"
    And the prompt should ask "Continue anyway? [Y/n]"

  @US_021 @release_readiness @warning @P1
  Scenario: Developer continues despite CHANGELOG warning
    Given the CHANGELOG warning is displayed
    When the developer types "Y"
    Then the installation should continue
    And the warning should be noted in the release report

  @US_021 @release_readiness @error @blocking @P0
  Scenario: Release readiness fails for invalid wheel
    Given a wheel exists with invalid metadata
    When the release readiness validation runs
    Then "twine check" should fail with "Invalid metadata"
    And the status should show "FAILED"
    And fix instructions should mention pyproject.toml

  # ==========================================================================
  # INSTALL CANDIDATE - US-022
  # ==========================================================================

  @US_022 @install @P0
  Scenario: Install shows progress phases
    Given release readiness has passed
    When the install process runs
    Then a phase table should display
    And the phase "Uninstalling previous" should show progress then checkmark
    And the phase "Installing from wheel" should show progress bar
    And the phase "Symlinking nw" should show checkmark when complete
    And the install duration should be displayed

  @US_022 @install @P0
  Scenario: Install removes previous installation first
    Given a previous version of nwave is installed
    And release readiness has passed
    When the install process runs
    Then "Uninstalling previous" should show "Removed"
    And the new version should be installed

  @US_022 @install @P0
  Scenario: Install uses pipx with force flag
    Given release readiness has passed
    When the install process runs
    Then the command should be "pipx install dist/nwave-1.3.0-dev-20260201-001-py3-none-any.whl --force"
    And the --force flag should ensure replacement of existing install

  @US_022 @install @P0
  Scenario: Install verifies nw command is available
    Given the wheel has been installed
    When the symlink verification runs
    Then "which nw" should return a valid path
    And "Symlinking nw" should show "Available"

  @US_022 @install @error @blocking @P0
  Scenario: Install fails due to dependency conflict
    Given release readiness has passed
    When the install process runs
    And a dependency version conflict occurs
    Then the phase "Installing from wheel" should show failure
    And the error should display the dependency issue
    And suggested fixes should be provided

  # ==========================================================================
  # DOCTOR VERIFICATION - US-023
  # ==========================================================================

  @US_023 @doctor @P0
  Scenario: Doctor verifies core installation
    Given the candidate has been installed
    When the doctor verification runs
    Then "Core installation" should verify the install path exists

  @US_023 @doctor @P0
  Scenario: Doctor verifies agent files installed
    Given the candidate has been installed
    When the doctor verification runs
    Then "Agent files" should count files in the install path agents directory
    And the count should be 47
    And the count should match the wheel bundled count

  @US_023 @doctor @P0
  Scenario: Doctor verifies version matches wheel
    Given the candidate has been installed
    And the wheel version was "1.3.0-dev-20260201-001"
    When the doctor verification runs
    Then "Version match" should verify "nw --version" output
    And the output should match "1.3.0-dev-20260201-001"

  @US_023 @doctor @P0
  Scenario: Doctor shows nw version output
    Given the candidate has been installed
    When the doctor verification runs
    Then the nw --version output should be displayed
    And it should show "nWave Framework v1.3.0-dev-20260201-001"
    And it should show the install path

  @US_023 @doctor @error @blocking @P0
  Scenario: Doctor fails for missing agents
    Given the candidate has been installed
    But agent files were not copied to ~/.claude
    When the doctor verification runs
    Then "Agent files" should show failure with "0 found"
    And the status should show "UNHEALTHY"
    And repair instructions should be provided

  @US_023 @doctor @error @blocking @P1
  Scenario: Doctor fails for version mismatch
    Given the candidate has been installed
    But "nw --version" shows a different version
    When the doctor verification runs
    Then "Version match" should show failure
    And the wheel version vs installed version should be shown
    And reinstall instructions should be provided

  # ==========================================================================
  # RELEASE REPORT - US-024
  # ==========================================================================

  @US_024 @report @P0
  Scenario: Release report shows release summary
    Given doctor verification has passed
    When the release report displays
    Then the release summary should show:
      | Field       | Value                         |
      | Version     | 1.3.0-dev-20260201-001       |
      | Branch      | installer                     |
      | Built       | 2026-02-01 14:30:25          |
      | Installed   | 2026-02-01 14:30:47          |

  @US_024 @report @P0
  Scenario: Release report shows install manifest
    Given doctor verification has passed
    When the release report displays
    Then the install manifest should show:
      | Component | Count              |
      | Agents    | 47                 |
      | Commands  | 23                 |
      | Templates | 12                 |
      | Location  | ~/.claude/agents/nw/ |

  @US_024 @report @P0
  Scenario: Release report includes test checklist
    Given doctor verification has passed
    When the release report displays
    Then the test checklist should include:
      | Step                                    |
      | Restart Claude Code (Cmd+Q then reopen) |
      | Run: /nw:version                        |
      | Run: /nw:help                           |
      | Test an agent: /nw:product-owner        |
      | Run: nw doctor                          |

  @US_024 @report @P0
  Scenario: Release report shows next steps
    Given doctor verification has passed
    When the release report displays
    Then local testing instructions should be shown
    And CI/CD readiness confirmation should be shown
    And the release command should show "twine upload dist/nwave-1.3.0-dev-20260201-001-py3-none-any.whl"

  # ==========================================================================
  # CI/CD MODE - US-027, US-028
  # ==========================================================================

  @US_027 @ci @P1
  Scenario: Install works in non-interactive CI mode
    Given the environment variable CI=true is set
    And a wheel exists in dist/
    When the developer runs "forge:install-local-candidate"
    Then no interactive prompts should appear
    And if multiple wheels exist, the newest should be selected automatically
    And the installation should complete automatically
    And exit code should be 0 on success

  @US_027 @ci @P1
  Scenario: CI mode auto-selects newest wheel
    Given CI=true is set
    And multiple wheels exist in dist/
    When the developer runs "forge:install-local-candidate"
    Then the newest wheel should be selected automatically
    And no selection prompt should appear

  @US_028 @ci @P1
  Scenario: Install with --json flag outputs machine-readable report
    Given a wheel exists in dist/
    When the developer runs "forge:install-local-candidate --json"
    Then the output should be valid JSON
    And it should include release_summary with version and timestamps
    And it should include install_manifest with counts
    And it should include release_readiness with check results

  @US_028 @ci @P1
  Scenario: Install writes release report to file
    Given a wheel exists in dist/
    When the developer runs "forge:install-local-candidate --output release-report.md"
    Then the release report should be written to release-report.md
    And CI/CD can archive the report as an artifact

  @US_029 @strict @P2
  Scenario: Install with --strict fails on any warnings
    Given a wheel exists without CHANGELOG entry
    When the developer runs "forge:install-local-candidate --strict"
    Then the CHANGELOG warning should become a failure
    And the installation should abort
    And exit code should be non-zero

  @US_029 @strict @P2
  Scenario: Strict mode passes when all clean
    Given a wheel exists with all requirements met
    When the developer runs "forge:install-local-candidate --strict"
    Then the installation should complete successfully
    And exit code should be 0

  # ==========================================================================
  # INTEGRATION - ARTIFACT CONSISTENCY
  # ==========================================================================

  @integration @horizontal @P0
  Scenario: Candidate version is consistent across all steps
    Given forge:install-local-candidate has completed successfully
    Then the version in release readiness should be "1.3.0-dev-20260201-001"
    And the version in doctor verification should be "1.3.0-dev-20260201-001"
    And the version in release report should be "1.3.0-dev-20260201-001"
    And all versions should match the wheel filename

  @integration @horizontal @P0
  Scenario: Agent count is consistent across doctor and report
    Given forge:install-local-candidate has completed successfully
    Then agent count in doctor should be 47
    And agent count in report should be 47
    And agent count should match actual files in install path

  @integration @cross_journey @P0
  Scenario: forge:install-local-candidate consumes wheel from build-local
    Given forge:build-local has completed with wheel at "dist/nwave-1.3.0-dev-20260201-001-py3-none-any.whl"
    When the developer runs "forge:install-local-candidate"
    Then the wheel from forge:build-local should be detected
    And the same version "1.3.0-dev-20260201-001" should be used throughout

  @integration @cross_journey @P0
  Scenario: Doctor verification matches install-nwave pattern
    Given forge:install-local-candidate doctor verification runs
    Then the checks should match install-nwave doctor checks
    And the health check format should be identical
    And the component list should be identical
