# TestPyPI PR-Level Validation Coherence Tests
# Epic: modern_CLI_installer
# Acceptance Designer: Quinn
# Date: 2026-02-01
# Focus: PR-level TestPyPI validation ensuring Journey 3 works before merge

@testpypi @pr_validation @ci_gate @horizontal
Feature: TestPyPI PR-Level Validation Coherence
  As a CI/CD pipeline
  I want to validate that test versions work correctly on TestPyPI
  So that Journey 3 (remote install) is proven before merge to main

  # ==========================================================================
  # VERSION FORMAT VALIDATION - Pip/Pipx Compatibility
  # ==========================================================================

  @version_format @critical @P0
  Scenario: Dev version format is valid PEP 440 and resolvable by pip
    Given a wheel is built with version "1.3.0-dev-20260201-001"
    When the version is published to TestPyPI
    Then pip should be able to resolve "nwave==1.3.0.dev20260201001"
    And pipx should be able to install "nwave==1.3.0.dev20260201001"
    And the installed version should report "1.3.0-dev-20260201-001"

  @version_format @critical @P0
  Scenario: PEP 440 normalized version format is consistent
    Given the candidate version format is "M.m.p-dev-YYYYMMDD-seq"
    When the wheel is built with version "1.3.0-dev-20260201-001"
    Then the wheel filename should be "nwave-1.3.0.dev20260201001-py3-none-any.whl"
    And the metadata version should be "1.3.0.dev20260201001"
    And pip search should find "1.3.0.dev20260201001"
    And the display version should be "1.3.0-dev-20260201-001"

  @version_format @P0
  Scenario: Sequential dev versions are correctly ordered by pip
    Given the following dev versions exist on TestPyPI:
      | Version                    | Wheel Filename                              |
      | 1.3.0-dev-20260201-001    | nwave-1.3.0.dev20260201001-py3-none-any.whl |
      | 1.3.0-dev-20260201-002    | nwave-1.3.0.dev20260201002-py3-none-any.whl |
      | 1.3.0-dev-20260201-003    | nwave-1.3.0.dev20260201003-py3-none-any.whl |
    When pip queries for the latest 1.3.0.dev* version
    Then version "1.3.0.dev20260201003" should be selected as newest
    And version ordering should be: 001 < 002 < 003

  @version_format @edge_case @P1
  Scenario: Dev version is lower priority than release version
    Given TestPyPI has version "1.3.0" (release)
    And TestPyPI has version "1.3.0.dev20260201001" (candidate)
    When pip installs "nwave" without version specifier
    Then version "1.3.0" should be installed (release takes priority)
    And the dev version should only install with explicit version specifier

  # ==========================================================================
  # TESTPYPI PUBLICATION VALIDATION - Upload Integrity
  # ==========================================================================

  @publication @critical @P0
  Scenario: Wheel uploaded to TestPyPI matches local build
    Given forge:build-local-candidate produced wheel with:
      | Attribute       | Value                                    |
      | Version         | 1.3.0-dev-20260201-001                  |
      | Agent Count     | 47                                       |
      | Command Count   | 23                                       |
      | Template Count  | 12                                       |
      | Wheel Size      | 2.3 MB                                   |
    When the wheel is published to TestPyPI
    Then the TestPyPI package metadata should show version "1.3.0.dev20260201001"
    And the downloadable wheel should have identical checksum
    And twine check should have passed before upload

  @publication @critical @P0
  Scenario: TestPyPI package is immediately installable after upload
    Given a wheel was just published to TestPyPI
    When CI attempts to install within 30 seconds of publication
    Then the package should be found on TestPyPI index
    And pipx install should succeed without "package not found" errors
    And no stale index cache issues should occur

  @publication @P1
  Scenario: TestPyPI upload fails gracefully with clear error
    Given the wheel "1.3.0.dev20260201001" already exists on TestPyPI
    When CI attempts to upload the same version
    Then the upload should fail with "version already exists" error
    And the error message should suggest incrementing the sequence number
    And the PR should be marked as failed with clear explanation

  # ==========================================================================
  # REMOTE INSTALL PARITY - TestPyPI vs Local Wheel
  # ==========================================================================

  @install_parity @critical @P0
  Scenario: TestPyPI install produces identical result to local install
    Given forge:build-local-candidate built version "1.3.0-dev-20260201-001"
    And forge:install-local-candidate installed from local wheel
    And doctor showed 47 agents, 23 commands, 12 templates with HEALTHY status
    When the same wheel is published to TestPyPI
    And a fresh environment installs via "pipx install -i https://test.pypi.org/simple/ nwave==1.3.0.dev20260201001"
    Then doctor should show identical results:
      | Check           | Local Install | TestPyPI Install |
      | Agents          | 47            | 47               |
      | Commands        | 23            | 23               |
      | Templates       | 12            | 12               |
      | Version         | 1.3.0-dev-20260201-001 | 1.3.0-dev-20260201-001 |
      | Status          | HEALTHY       | HEALTHY          |

  @install_parity @critical @P0
  Scenario: File structure identical between local and TestPyPI install
    Given a wheel built locally with version "1.3.0-dev-20260201-001"
    And the same wheel published to TestPyPI
    When I install locally via "pipx install ./dist/nwave-1.3.0.dev20260201001-py3-none-any.whl"
    And I install from TestPyPI via "pipx install -i https://test.pypi.org/simple/ nwave==1.3.0.dev20260201001" in a separate environment
    Then both installations should have identical content:
      | Component           | Validation                           |
      | agents/             | identical file list and content      |
      | commands/           | identical file list and content      |
      | templates/          | identical file list and content      |
      | manifest.json       | identical content                    |
      | version marker      | "1.3.0-dev-20260201-001"             |
      | install scripts     | identical content and permissions    |
    And agent file checksums should match between installations
    And command file checksums should match between installations
    And template file checksums should match between installations

  @install_parity @P0
  Scenario: nw --version output identical between install methods
    Given local wheel installed version "1.3.0-dev-20260201-001"
    And TestPyPI installed version "1.3.0-dev-20260201-001"
    When "nw --version" is run after local install
    And "nw --version" is run after TestPyPI install
    Then both outputs should be byte-for-byte identical
    And both should show "nWave Framework v1.3.0-dev-20260201-001"

  # ==========================================================================
  # CI QUALITY GATE - PR Merge Requirements
  # ==========================================================================

  @ci_gate @critical @P0
  Scenario: PR cannot merge without TestPyPI validation passing
    Given a PR is opened with changes to nWave core
    When CI runs the PR validation pipeline
    Then the following checks must ALL pass before merge is allowed:
      | Check                      | Description                                    |
      | wheel_build                | python -m build completes successfully         |
      | twine_check                | twine check passes on built wheel              |
      | testpypi_upload            | Wheel published to TestPyPI                    |
      | testpypi_install           | pipx install from TestPyPI succeeds            |
      | doctor_healthy             | nw doctor shows HEALTHY status                 |
      | version_match              | Installed version matches wheel version        |
      | component_counts_match     | Agent/command/template counts match wheel      |
    And if any check fails, PR merge should be blocked

  @ci_gate @critical @P0
  Scenario: TestPyPI install test runs in isolated environment
    Given CI is running PR validation
    When the TestPyPI install test executes
    Then a fresh Python virtual environment should be created
    And no prior nWave installation should exist
    And pipx should be freshly installed
    And the test environment should mirror a first-time user setup

  @ci_gate @P0
  Scenario: CI validates TestPyPI install success via outcomes
    Given a fresh CI environment with pipx installed
    And no prior nWave installation exists
    When I run "pipx install -i https://test.pypi.org/simple/ nwave==1.3.0.dev20260201001"
    Then the exit code should be 0
    And "which nw" should return a valid path
    And "nw --version" should output "1.3.0-dev-20260201-001"
    And "nw doctor" should show HEALTHY status
    And if the install fails, stdout and stderr should be captured for diagnostics

  @ci_gate @P0
  Scenario: TestPyPI validation includes full Journey 3 UX
    Given CI is running PR validation
    When TestPyPI install completes
    Then the following Journey 3 elements should be validated via outcomes:
      | Step | Validation                                      | Outcome Check                    |
      | 1    | pipx install command succeeds                   | exit_code == 0                   |
      | 2    | Installation completes                          | which nw returns path            |
      | 3    | Pre-flight checks all pass                      | no ERROR in preflight output     |
      | 4    | Framework installation completes                | ~/.claude/agents/nw/ exists      |
      | 5    | Doctor verification shows HEALTHY               | nw doctor exit_code == 0         |
      | 6    | Version information is accessible               | nw --version matches expected    |
    And all steps must pass for PR to be mergeable

  @ci_gate @P0
  Scenario: CI provides clear failure diagnostics
    Given TestPyPI validation fails
    When the failure is reported
    Then the CI output should include:
      | Information              | Description                              |
      | Failed Step              | Which validation step failed             |
      | Expected Value           | What was expected                        |
      | Actual Value             | What was received                        |
      | Suggested Fix            | How to resolve the issue                 |
      | TestPyPI URL             | Link to the published package            |
    And the PR status check should show the specific failure reason

  @ci_gate @P1
  Scenario: TestPyPI version is unique per PR
    Given PR #123 is created from branch "feature/add-agents"
    And PR #124 is created from branch "feature/fix-commands"
    When both PRs run CI simultaneously
    Then PR #123 should publish version "1.3.0.dev20260201001"
    And PR #124 should publish version "1.3.0.dev20260201002"
    And each PR should test against its own unique version
    And no version collision should occur

  # ==========================================================================
  # SHARED ARTIFACT CONSISTENCY - Cross-Journey Validation
  # ==========================================================================

  @shared_artifacts @horizontal @P0
  Scenario: TestPyPI install produces identical artifacts to local install
    Given a wheel built locally with version "1.3.0-dev-20260201-001"
    And the same wheel published to TestPyPI
    When I install locally via "pipx install ./dist/nwave-1.3.0.dev20260201001-py3-none-any.whl"
    And I install from TestPyPI via "pipx install -i https://test.pypi.org/simple/ nwave==1.3.0.dev20260201001" in a separate environment
    Then both installations should have identical content
    And the local install should contain:
      | Component           | Expected                              |
      | agents/             | 47 agent files with matching content  |
      | commands/           | 23 command files with matching content|
      | templates/          | 12 template files with matching content|
      | manifest.json       | identical JSON structure and values   |
      | version marker      | "1.3.0-dev-20260201-001"              |
    And the TestPyPI install should match exactly

  @shared_artifacts @horizontal @P0
  Scenario: Version flows correctly from pyproject.toml through TestPyPI
    Given pyproject.toml has version "1.3.0"
    And conventional commits indicate MINOR bump
    When forge:build-local-candidate runs on date 20260201 sequence 001
    Then the candidate version should be "1.3.0-dev-20260201-001"
    And the wheel version should be "1.3.0.dev20260201001"
    And TestPyPI should show version "1.3.0.dev20260201001"
    And installed nw --version should show "1.3.0-dev-20260201-001"

  @shared_artifacts @horizontal @P0
  Scenario: Component counts consistent from build through TestPyPI install
    Given forge:build-local-candidate wheel validation shows:
      | Component | Count |
      | Agents    | 47    |
      | Commands  | 23    |
      | Templates | 12    |
    When the wheel is published to TestPyPI
    And a fresh install is performed from TestPyPI
    Then doctor should show:
      | Component | Count |
      | Agents    | 47    |
      | Commands  | 23    |
      | Templates | 12    |
    And these counts should match the original wheel contents exactly

  @shared_artifacts @P0
  Scenario: Pre-flight checks format identical for TestPyPI install
    Given pre-flight checks ran during local wheel install
    When pre-flight checks run during TestPyPI install
    Then the table format should be identical
    And column headers should be identical
    And status icons should be identical
    And the only difference should be the source indicator

  @shared_artifacts @P0
  Scenario: Doctor output format identical for TestPyPI install
    Given doctor ran after local wheel install
    When doctor runs after TestPyPI install
    Then the table format should be identical
    And check order should be identical
    And status terminology should be identical
    And all check results should match

  # ==========================================================================
  # ERROR SCENARIOS - TestPyPI Specific Failures
  # ==========================================================================

  @error @testpypi @P0
  Scenario: Network failure during TestPyPI install
    Given CI is running TestPyPI validation
    When network connectivity to test.pypi.org fails
    Then the error should show "Cannot reach TestPyPI"
    And the CI should retry up to 3 times with exponential backoff
    And after retries exhausted, PR should be marked as infrastructure failure
    And the failure should NOT block PR if tagged as transient

  @error @testpypi @P0
  Scenario: Package not found on TestPyPI
    Given CI expects version "1.3.0.dev20260201001" on TestPyPI
    When pip cannot find the package
    Then the error should show "Package nwave==1.3.0.dev20260201001 not found"
    And the error should suggest checking upload step logs
    And the error should show when the upload step last ran
    And the PR should be blocked until upload succeeds

  @error @testpypi @P1
  Scenario: TestPyPI rate limiting
    Given multiple PRs are running CI simultaneously
    When TestPyPI returns rate limit error (429)
    Then CI should wait and retry with backoff
    And the wait time should be logged
    And if rate limiting persists, escalate to infrastructure alert
    And other PRs should not be affected

  @error @testpypi @P1
  Scenario: Wheel content validation fails after TestPyPI download
    Given wheel was uploaded to TestPyPI successfully
    When the downloaded wheel has different checksum than uploaded
    Then the error should show "Wheel integrity check failed"
    And the expected vs actual checksums should be displayed
    And the PR should be blocked
    And security alert should be triggered for potential tampering

  # ==========================================================================
  # ROLLBACK AND RECOVERY - TestPyPI Context
  # ==========================================================================

  @rollback @testpypi @P1
  Scenario: Failed TestPyPI install does not affect main branch
    Given main branch has release version "1.3.0" on production PyPI
    And PR attempts to publish "1.3.0.dev20260201001" to TestPyPI
    When the TestPyPI publish or install fails
    Then production PyPI should be unaffected
    And main branch users should still get "1.3.0"
    And the failed PR should not corrupt any production state

  @rollback @testpypi @P1
  Scenario: PR author can retry TestPyPI validation
    Given TestPyPI validation failed due to transient issue
    When the PR author pushes an empty commit or triggers re-run
    Then a new sequence number should be generated
    And a fresh TestPyPI publish should occur
    And the new version should be testable independently

  # ==========================================================================
  # PERFORMANCE AND TIMING - CI Efficiency
  # ==========================================================================

  @performance @ci @P1
  Scenario: TestPyPI install uses tenacity retry pattern
    Given CI is running TestPyPI installation
    And the timeout per attempt is 120 seconds
    And the maximum propagation wait is 3 minutes
    When the install command is executed
    Then on timeout or failure, retry with linear backoff (+15s increments):
      | Attempt | Wait Before Retry | Cumulative Wait |
      | 1       | 0 seconds         | 0 seconds       |
      | 2       | 5 seconds         | 5 seconds       |
      | 3       | 15 seconds        | 20 seconds      |
      | 4       | 30 seconds        | 50 seconds      |
      | 5       | 45 seconds        | 95 seconds      |
      | 6       | 60 seconds        | 155 seconds     |
    And each retry should log the attempt number and wait time
    And after cumulative wait exceeds 3 minutes, report consolidated error with all attempt logs
    And on any successful attempt (exit code 0), proceed immediately

  @performance @ci @P1
  Scenario: TestPyPI validation completes within acceptable time
    Given CI is running PR validation
    When TestPyPI validation begins
    Then the complete validation should complete within 10 minutes (including retries)
    And breakdown should be approximately:
      | Step                   | Max Duration | Notes                          |
      | Wheel build            | 30 seconds   | Single attempt                 |
      | Twine check            | 10 seconds   | Single attempt                 |
      | TestPyPI upload        | 60 seconds   | With 3 retries if needed       |
      | Index propagation wait | 30 seconds   | Single wait                    |
      | pipx install           | 120 seconds  | Per attempt, up to 5 retries   |
      | Doctor verification    | 30 seconds   | Single attempt                 |

  @performance @ci @P1
  Scenario: TestPyPI validation runs in parallel with other checks
    Given PR CI pipeline has multiple stages
    When TestPyPI validation runs
    Then it should run in parallel with unit tests
    And it should run in parallel with linting
    And it should NOT block unrelated checks
    And total PR validation time should be optimized
