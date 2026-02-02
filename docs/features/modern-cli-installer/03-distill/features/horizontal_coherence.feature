# Horizontal Coherence Across Journeys
# Epic: modern_CLI_installer
# Acceptance Designer: Quinn
# Date: 2026-02-01
# Focus: Cross-journey artifact consistency and format alignment

@horizontal @integration @cross_journey
Feature: Horizontal Coherence Across Journeys
  As a developer using nWave installer
  I want consistent experience across build, install, and PyPI journeys
  So that I can trust the tooling regardless of which journey I'm on

  # ==========================================================================
  # INTEGRATION CHECKPOINTS - Artifact Consistency Verification
  # ==========================================================================

  @checkpoint @critical @P0
  Scenario: Integration checkpoint displays at build-to-install transition
    Given forge:build-local-candidate completed with version "1.3.0-dev-20260201-001"
    And the wheel was created at "dist/nwave-1.3.0.dev20260201001-py3-none-any.whl"
    When the developer proceeds to forge:install-local-candidate
    Then an integration checkpoint box displays
    And the checkpoint header shows "INTEGRATION CHECKPOINT"
    And the checkpoint shows "version matches build" with checkmark
    And the checkpoint shows "wheel path verified" with checkmark
    And the checkpoint shows "artifact counts consistent" with checkmark

  @checkpoint @critical @P0
  Scenario: Integration checkpoint verifies version consistency
    Given forge:build-local-candidate produced candidate version "1.3.0-dev-20260201-001"
    When forge:install-local-candidate starts
    Then the integration checkpoint displays version verification
    And it shows "Built: 1.3.0-dev-20260201-001"
    And it shows "Installing: 1.3.0-dev-20260201-001"
    And both versions match exactly

  @checkpoint @critical @P0
  Scenario: Integration checkpoint verifies count consistency
    Given forge:build-local-candidate validated wheel with 47 agents, 23 commands, 12 templates
    When forge:install-local-candidate starts
    Then the integration checkpoint displays count verification
    And it shows "Agents: 47 (matches build)"
    And it shows "Commands: 23 (matches build)"
    And it shows "Templates: 12 (matches build)"

  @checkpoint @P1
  Scenario: Integration checkpoint blocks on version mismatch
    Given forge:build-local-candidate completed with version "1.3.0-dev-20260201-001"
    But the wheel file has been replaced with version "1.2.0"
    When forge:install-local-candidate attempts to start
    Then the integration checkpoint fails
    And the error shows "Version mismatch detected"
    And it shows "Expected: 1.3.0-dev-20260201-001"
    And it shows "Found: 1.2.0"
    And installation is blocked until resolved

  # ==========================================================================
  # ARTIFACT FLOW - Build to Install to Doctor
  # ==========================================================================

  @artifact_flow @critical @P0
  Scenario: Artifacts flow correctly from build to install to doctor
    Given forge:build-local-candidate completed successfully
    And the wheel path is "dist/nwave-1.3.0.dev20260201001-py3-none-any.whl"
    And wheel validation showed 47 agents, 23 commands, 12 templates
    When the developer runs forge:install-local-candidate
    Then the install uses the exact wheel path "dist/nwave-1.3.0.dev20260201001-py3-none-any.whl"
    And pipx install receives that exact path
    And doctor verification shows version "1.3.0-dev-20260201-001"
    And doctor shows 47 agents, 23 commands, 12 templates
    And all counts match the build validation counts

  @artifact_flow @critical @P0
  Scenario: Wheel path preserved through entire install journey
    Given a wheel exists at "dist/nwave-1.3.0.dev20260201001-py3-none-any.whl"
    When forge:install-local-candidate runs
    Then the wheel path appears in pre-flight check output
    And the wheel path appears in release readiness output
    And the wheel path appears in install command
    And the wheel path appears in release report
    And all four occurrences are identical

  @artifact_flow @P0
  Scenario: Version string format consistent through build-install flow
    Given forge:build-local-candidate produces version "1.3.0-dev-20260201-001"
    When forge:install-local-candidate completes
    Then the version format is identical in:
      | Location                    | Expected Version          |
      | Build summary               | 1.3.0-dev-20260201-001   |
      | Install pre-flight          | 1.3.0-dev-20260201-001   |
      | Release readiness           | 1.3.0-dev-20260201-001   |
      | Doctor verification         | 1.3.0-dev-20260201-001   |
      | Release report              | 1.3.0-dev-20260201-001   |

  @artifact_flow @P1
  Scenario: Component counts consistent through build-install-doctor flow
    Given forge:build-local-candidate wheel validation shows:
      | Component | Count |
      | Agents    | 47    |
      | Commands  | 23    |
      | Templates | 12    |
    When forge:install-local-candidate completes with doctor verification
    Then doctor verification shows identical counts:
      | Component | Count |
      | Agents    | 47    |
      | Commands  | 23    |
      | Templates | 12    |
    And the release report shows identical counts:
      | Component | Count |
      | Agents    | 47    |
      | Commands  | 23    |
      | Templates | 12    |

  # ==========================================================================
  # PRE-FLIGHT FORMAT CONSISTENCY
  # ==========================================================================

  @preflight_consistency @horizontal @P0
  Scenario: Pre-flight table format identical across all three journeys
    Given the pre-flight check system is initialized
    When pre-flight runs for "forge:build-local-candidate"
    And pre-flight runs for "forge:install-local-candidate"
    And pre-flight runs for "pipx install nwave"
    Then all three display identical table structure
    And all three use column headers "Check" and "Status"
    And all three use the same column widths
    And all three use the same row spacing

  @preflight_consistency @horizontal @P0
  Scenario: Pre-flight status icons identical across journeys
    Given pre-flight checks run across all three journeys
    Then the success icon is identical: "[check]" (green checkmark)
    And the failure icon is identical: "[x]" (red x)
    And the warning icon is identical: "[!]" (yellow warning)
    And the spinner icon is identical during check execution

  @preflight_consistency @horizontal @P0
  Scenario: Python version check format identical across journeys
    Given Python 3.12.1 is installed
    When pre-flight runs for each journey
    Then the Python check displays identically:
      | Journey                      | Display                              |
      | forge:build-local-candidate  | Python version [check] 3.12.1 (3.10+ OK) |
      | forge:install-local-candidate| Python version [check] 3.12.1 (3.10+ OK) |
      | pipx install nwave           | Python version [check] 3.12.1 (3.10+ OK) |

  @preflight_consistency @horizontal @P1
  Scenario: Pre-flight error format identical across journeys
    Given Python 3.8.10 is installed (too old)
    When pre-flight runs for each journey
    Then the Python error displays identically across all three:
      | Field            | Value                        |
      | Icon             | [x]                          |
      | Message          | Python version too old       |
      | Required         | Python 3.10+                 |
      | Found            | Python 3.8.10                |
    And the error format structure is identical

  @preflight_consistency @horizontal @P1
  Scenario: Pre-flight pipx check format identical between Journey 2 and 3
    Given pipx v1.4.3 is installed
    When pre-flight runs for "forge:install-local-candidate"
    And pre-flight runs for "pipx install nwave"
    Then the pipx check displays identically:
      | Journey                      | Display                         |
      | forge:install-local-candidate| pipx available [check] v1.4.3 installed |
      | pipx install nwave           | pipx available [check] v1.4.3 installed |

  # ==========================================================================
  # DOCTOR FORMAT CONSISTENCY
  # ==========================================================================

  @doctor_consistency @horizontal @P0
  Scenario: Doctor output format identical between Journey 2 and Journey 3
    Given nWave is installed with 47 agents, 23 commands, 12 templates
    When doctor runs after forge:install-local-candidate
    And doctor runs after pipx install nwave
    Then both doctor outputs use identical table format
    And both use identical section headers
    And both use identical status terminology
    And both display checks in the same order

  @doctor_consistency @horizontal @P0
  Scenario: Doctor check order identical between local and PyPI install
    Given nWave is installed
    When doctor verification runs
    Then the checks display in this exact order:
      | Order | Check Name       |
      | 1     | Core installation|
      | 2     | Agent files      |
      | 3     | Command files    |
      | 4     | Template files   |
      | 5     | Config valid     |
      | 6     | Permissions      |
      | 7     | Version match    |
    And this order is identical for both Journey 2 and Journey 3

  @doctor_consistency @horizontal @P0
  Scenario: Doctor status levels use identical terminology
    Given doctor verification runs
    Then the status levels are:
      | Status    | Display   | Color  |
      | Healthy   | HEALTHY   | Green  |
      | Warning   | WARNING   | Yellow |
      | Unhealthy | UNHEALTHY | Red    |
    And these are identical between Journey 2 and Journey 3

  @doctor_consistency @horizontal @P0
  Scenario: Doctor component display format identical
    Given nWave is installed with 47 agents
    When doctor runs for Journey 2 (forge:install-local-candidate)
    And doctor runs for Journey 3 (pipx install nwave)
    Then "Agent files" check displays identically:
      | Journey   | Display              |
      | Journey 2 | Agent files [check] 47 OK |
      | Journey 3 | Agent files [check] 47 OK |
    And format is: "{check_name} {icon} {count} {status}"

  @doctor_consistency @horizontal @P1
  Scenario: Doctor version display identical between journeys
    Given nWave version "1.3.0" is installed
    When doctor runs
    Then "Version match" displays identically:
      | Journey   | Display                        |
      | Journey 2 | Version match [check] 1.3.0    |
      | Journey 3 | Version match [check] 1.3.0    |

  @doctor_consistency @horizontal @P1
  Scenario: Doctor install path display identical between journeys
    Given nWave is installed at "~/.claude/agents/nw/"
    When doctor runs
    Then "Core installation" displays identically:
      | Journey   | Display                                    |
      | Journey 2 | Core installation [check] ~/.claude/agents/nw/ |
      | Journey 3 | Core installation [check] ~/.claude/agents/nw/ |

  # ==========================================================================
  # SUMMARY FORMAT CONSISTENCY
  # ==========================================================================

  @summary_consistency @horizontal @P1
  Scenario: Success summary header format consistent
    Given a journey completes successfully
    Then the summary header format is:
      | Journey                      | Header                      |
      | forge:build-local-candidate  | FORGE: BUILD COMPLETE       |
      | forge:install-local-candidate| FORGE: CANDIDATE INSTALLED  |
      | pipx install nwave           | nWave v{version} installed successfully! |
    And all use the same box/border styling

  @summary_consistency @horizontal @P1
  Scenario: Component count table format identical in summaries
    Given a journey completes with 47 agents, 23 commands, 12 templates
    Then the component count table uses identical format:
      | Column 1   | Column 2 |
      | Agents     | 47       |
      | Commands   | 23       |
      | Templates  | 12       |
    And column alignment is identical across journeys
    And spacing is identical across journeys

  # ==========================================================================
  # ERROR FORMAT CONSISTENCY
  # ==========================================================================

  @error_consistency @horizontal @P1
  Scenario: Error message format identical across journeys
    Given an error occurs during any journey
    Then the error format structure is:
      | Element      | Format                          |
      | Icon         | [x] (red)                       |
      | Title        | Bold, descriptive               |
      | Details      | Indented explanation            |
      | Suggestion   | "Try:" or "Fix:" prefix         |
    And this structure is identical across all three journeys

  @error_consistency @horizontal @P1
  Scenario: Permission error format identical across journeys
    Given ~/.claude is not writable
    When the error displays for each journey
    Then all three show identical error format:
      | Field      | Value                              |
      | Icon       | [x]                                |
      | Message    | Cannot write to ~/.claude/         |
      | Suggestion | Check permissions or use NWAVE_INSTALL_PATH |
