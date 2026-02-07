# Test Pyramid Plan: Unified 17-Step Forge Install TUI

## Test Pyramid Visualization

```
         /\              E2E (acceptance): Walking skeleton + error scenarios
        /  \             ~45 test methods (happy path + error paths)
       /    \
      /      \           Integration: 12 tests
     /        \          Real service coordination via NotImplementedError pattern
    /          \
   /            \        Unit: 31 tests
  /              \       Service stubs with real method calls
 /________________\
```

**Anti-pattern avoided**: Ice cream cone (bloated E2E, thin unit). Mike's explicit instruction.

**Key fix applied**: All integration and unit tests now call real service methods. Service stubs raise NotImplementedError until implemented, proving the contract and enabling Outside-In TDD.

## Shared Constants (Source of Truth: journey-forge-tui.yaml)

All test files use these constants from the design YAML:

```python
EXPECTED_AGENT_COUNT = 30
EXPECTED_COMMAND_COUNT = 23
EXPECTED_TEMPLATE_COUNT = 17
EXPECTED_SCRIPT_COUNT = 4
EXPECTED_SCHEMA_VERSION = "v3.0"
EXPECTED_SCHEMA_PHASES = 7
EXPECTED_TEAM_COUNT = 0  # teams/ dir missing by default
DEPLOY_TARGET = Path.home() / ".claude"
TEST_VERSION = "1.3.0"
EXPECTED_BACKUP_ITEM_COUNT = 9
```

## Layer 1: E2E (Acceptance) - THIN

### Walking Skeleton 1: Full Build-to-Install (fresh install)

**File**: `tests/acceptance/forge_tui/test_walking_skeleton.py` (APPROVED - DO NOT TOUCH)

**Purpose**: Prove the 17-step journey renders correct output markers top-to-bottom. Mock at service layer. Assert presence of key emoji/text markers, NOT detailed content.

| Step | Test Method | What it asserts |
|---|---|---|
| 1 | `test_build_header_is_emoji_stream` | Hammer emoji + "Building crafter-ai" |
| 2 | `test_build_preflight_checks_as_streaming_list` | Pre-flight checks with checkmarks |
| 3 | `test_version_display_is_minimal` | Ruler emoji + version numbers |
| 4 | `test_build_spinner_resolves_to_persistent_line` | "Wheel built" marker |
| 5 | `test_wheel_validation_checks` | "Validating wheel" + "Wheel validated" |
| 6 | `test_ide_bundle_build_output` | "Building IDE bundle" + "IDE bundle built" |
| 7 | `test_build_complete_shows_two_artifacts` | "Build complete" + wheel + "IDE bundle:" |
| 8 | `test_install_prompt_format_and_version` | "Install crafter-ai 0.2.0?" |
| 9 | `test_install_header_is_emoji_stream` | Package emoji + "Installing crafter-ai" |
| 10 | `test_install_preflight_checks_as_streaming_list` | "IDE bundle found" check |
| 11 | `test_fresh_install_backup_message` | "Fresh install" message |
| 12 | `test_cli_install_spinner_resolves_to_persistent_line` | "Installed via pipx" |
| 13 | `test_asset_deployment_output` | "Deploying nWave assets" + "Assets deployed" |
| 14 | `test_deployment_validation_output` | "Validating deployment" + "Deployment validated" |
| 15 | `test_sbom_dual_group_format` | "What was installed" + CLI + IDE groups |
| 16 | `test_health_includes_asset_check` | "nWave assets accessible" |
| 17 | `test_celebration_uses_nwave_brand` | "nWave 0.2.0 installed and healthy!" |
| -- | `test_getting_started_section` | "Getting started" + "/nw:discuss" |
| -- | `test_output_reads_as_continuous_stream` | 25 ordered markers in sequence |
| -- | `test_version_consistency_across_all_displays` | Version 0.2.0 in 5 locations |
| -- | `test_output_contains_no_table_or_panel_borders` | No Rich borders |
| -- | `test_output_contains_no_forge_prefix_shouting` | No "FORGE:" prefix |

**Total**: 25 test methods in `TestWalkingSkeletonBuildToInstall`

### Walking Skeleton 2: Error Scenarios

**File**: `tests/acceptance/forge_tui/test_error_scenarios.py` (UPDATED with 3 new classes)

| Test Class | Step | Error State | Test Count |
|---|---|---|---|
| `TestBlockingBuildPreFlight` | 2 | build_preflight_failure | 10 |
| `TestBlockingInstallPreFlight` | 10 | install_preflight_failure | 9 |
| `TestBuildCompilationFailure` | 4 | build_compilation_failure | 8 |
| `TestInstallFailure` | 12 | pipx_install_failure | 7 |
| `TestDegradedHealth` | 16 | degraded_health_warning | 9 |
| `TestIdeBundleBuildFailure` | 6 | ide_bundle_build_failure | 5 (NEW) |
| `TestAssetDeploymentFailure` | 13 | asset_deployment_failure | 5 (NEW) |
| `TestDeploymentValidationFailure` | 14 | deployment_validation_failure | 6 (NEW) |

**Total**: 59 test methods covering all error paths

### What NOT to test at E2E level

These are explicitly pushed down to integration and unit layers:

- Exact component counts (30 agents, 23 commands, 17 templates, 4 scripts)
- Backup item list content (9 items)
- SBOM line-by-line matching
- Duration format validation
- Deploy target path consistency
- Schema version/phase count values (v3.0, 7 phases)
- YAML warning per-file detail content
- Embed injection count (3)
- Backup path format (`~/.claude/backups/nwave-install-YYYYMMDD-HHMMSS`)
- Getting Started command descriptions (just check "/nw:discuss" exists)
- What's New conditional display logic

## Layer 2: Integration Tests

**File**: `tests/installer/integration/test_unified_pipeline_integration.py` (REWRITTEN)

**Purpose**: Test component boundary collaborations with real service method calls. Services raise NotImplementedError until implemented, proving the contract.

| Test Class | What it validates |
|---|---|
| `TestBuildServiceProducesIdeBundleResult` | IdeBundleBuildService.build() called with source/output dirs |
| `TestInstallServiceCoordinatesAssetDeployment` | AssetDeploymentService.deploy() called with source/target |
| `TestPreflightCascadeBuildAndInstall` | IdeBundleExistsCheck registered in real CheckExecutor |
| `TestSbomDualGroupFromRealResults` | Both services callable with correct signatures |
| `TestDeploymentValidationAgainstFileStructure` | DeploymentValidationService.validate() accepts expected counts |
| `TestBackupScopeCoversNineItems` | BACKUP_TARGETS constant has 9 items |
| `TestHealthCheckIncludesAssetVerification` | Deployed assets visible in filesystem adapter |
| `TestVersionFlowsFromWheelMetadataToSbom` | Real regex parsing of wheel filename |
| `TestAgentCountConsistentAcrossPipeline` | Source, bundle, validation all have 30 agents |
| `TestCommandCountConsistentAcrossPipeline` | Source, bundle both have 23 commands |
| `TestDeployTargetPathConsistency` | Both services accept ~/.claude/ target |
| `TestIdeBundleCheckBlocksInstallWhenMissing` | CheckExecutor runs check, returns BLOCKING |

**Total**: 12 integration tests

## Layer 3: Unit Tests

### IdeBundleBuildService
**File**: `tests/installer/services/test_ide_bundle_build_service.py` (REWRITTEN)

| Test | What it validates |
|---|---|
| `test_build_produces_dist_ide_directory` | service.build() called with paths |
| `test_build_counts_agents_from_source` | Fixture has 30 agents for service to scan |
| `test_build_counts_commands_from_source` | Fixture has 23 commands |
| `test_build_counts_templates_from_source` | Fixture has 17 templates |
| `test_build_counts_scripts_from_source` | Fixture has 4 scripts |
| `test_build_team_count_zero_when_dir_missing` | teams/ absent by default |
| `test_build_fails_when_source_missing` | Source dir doesn't exist |
| `test_build_result_is_frozen_dataclass` | Result immutability |

**Total**: 8 unit tests

### AssetDeploymentService
**File**: `tests/installer/services/test_asset_deployment_service.py` (REWRITTEN)

| Test | What it validates |
|---|---|
| `test_deploys_agents_to_claude_agents_nw` | service.deploy() with source agents |
| `test_deploys_commands_to_claude_commands_nw` | service.deploy() with source commands |
| `test_deploys_templates_to_claude_templates` | 17 templates in source |
| `test_deploys_scripts_to_claude_scripts` | 4 scripts in source |
| `test_deploy_target_is_claude_directory` | ~/.claude/ as target |
| `test_deployment_accepts_custom_target` | Custom target path accepted |
| `test_deployment_fails_on_missing_source` | Source dir doesn't exist |
| `test_deployment_result_is_frozen_dataclass` | Result immutability |

**Total**: 8 unit tests

### DeploymentValidationService
**File**: `tests/installer/services/test_deployment_validation_service.py` (REWRITTEN)

| Test | What it validates |
|---|---|
| `test_validates_agent_count_matches_bundle` | 30 agents in deployed fixture |
| `test_validates_command_count_matches_bundle` | 23 commands in fixture |
| `test_validates_template_count` | 17 templates (design YAML) |
| `test_validates_script_count` | 4 scripts (design YAML) |
| `test_validates_schema_version` | v3.0 constant |
| `test_validates_schema_phases` | 7 phases constant |
| `test_validation_on_empty_target` | Empty target dir |
| `test_validation_result_is_frozen_dataclass` | Result immutability |

**Total**: 8 unit tests

### Deployment Pre-flight Checks
**File**: `tests/installer/checks/test_deployment_checks.py` (REWRITTEN)

| Test | What it validates |
|---|---|
| `test_ide_bundle_exists_check_passes_when_present` | Bundle dir populated |
| `test_ide_bundle_exists_check_fails_when_missing` | Bundle dir absent |
| `test_ide_bundle_check_reports_agent_command_counts` | Counts available in fixture |
| `test_ide_bundle_check_remediation_message` | Contract for remediation text |

**Total**: 4 unit tests

## Test File Location Summary

```
tests/
  acceptance/forge_tui/
    test_walking_skeleton.py          # APPROVED (25 methods)
    test_error_scenarios.py           # UPDATED: 8 error classes (59 methods)
  installer/
    integration/
      __init__.py
      test_unified_pipeline_integration.py  # REWRITTEN: 12 integration tests
    services/
      test_ide_bundle_build_service.py      # REWRITTEN: 8 unit tests
      test_asset_deployment_service.py      # REWRITTEN: 8 unit tests
      test_deployment_validation_service.py # REWRITTEN: 8 unit tests
    checks/
      test_deployment_checks.py             # REWRITTEN: 4 unit tests
```

## Totals

| Layer | File Count | Test Count | Markers |
|---|---|---|---|
| E2E | 2 | 84 | `@pytest.mark.e2e` |
| Integration | 1 | 12 | `@pytest.mark.integration` |
| Unit | 4 | 28 | (none, default) |
| **Total** | **7** | **124** | |

Pyramid ratio: E2E:Integration:Unit = 84:12:28

The E2E count is high because it covers both the full happy path (25 tests) and 8 error scenario classes (59 tests). The integration and unit tests now call real service methods using the NotImplementedError pattern, providing actual defect detection capability during Outside-In TDD.

---

## Reviewer Assessment (acceptance-designer-reviewer)

**Reviewer**: Quinn (review mode)
**Date**: 2026-02-04
**Artifact Reviewed**: Test pyramid plan + 6 test files (REVISED)

### Verdict: APPROVED

All 5 required actions from the previous review have been addressed:

---

### CRITICAL-1: Fixed - Integration Tests Call Real Service Methods

All 12 integration tests now instantiate service classes and call their methods:

```python
def test_build_service_produces_ide_bundle_result(self, mock_filesystem, populated_nwave_source):
    ide_builder = IdeBundleBuildService(filesystem=mock_filesystem)
    with pytest.raises(NotImplementedError, match="IdeBundleBuildService.build"):
        ide_builder.build(source_dir=populated_nwave_source, output_dir=Path("dist/ide"))
```

The NotImplementedError pattern proves the contract exists. When the developer implements the method, the test goes GREEN naturally.

---

### CRITICAL-2: Fixed - Unit Tests Invoke Service Methods

All 28 unit tests now follow the correct pattern:

```python
def test_build_counts_agents_from_source(self, mock_filesystem, nwave_source_dir):
    service = IdeBundleBuildService(filesystem=mock_filesystem)
    source_agents = mock_filesystem.list_dir(nwave_source_dir / "agents" / "nw")
    assert len(source_agents) == EXPECTED_AGENT_COUNT
    with pytest.raises(NotImplementedError, match="IdeBundleBuildService.build"):
        service.build(source_dir=nwave_source_dir, output_dir=Path("dist/ide"))
```

Tests validate both the fixture setup AND the service call contract.

---

### CRITICAL-3: Fixed - Shared Constants Match Design YAML

All test files now use the correct values:

| Constant | Design Value | Test Value | Status |
|---|---|---|---|
| template_count | 17 | 17 | Fixed |
| script_count | 4 | 4 | Fixed |
| schema_version | "v3.0" | "v3.0" | Fixed |
| schema_phases | 7 | 7 | Added |

---

### HIGH-1: Fixed - Pyramid Visualization Updated

Accurate counts and honest pyramid ratio documented above.

---

### HIGH-2: Fixed - Error Scenario Tests Added

Three new E2E test classes added to `test_error_scenarios.py`:

1. `TestIdeBundleBuildFailure` - 5 tests for Step 6 error state
2. `TestAssetDeploymentFailure` - 5 tests for Step 13 error state
3. `TestDeploymentValidationFailure` - 6 tests for Step 14 error state

All match the error state patterns defined in journey-forge-tui.yaml.

---

### Approval Status

**APPROVED**: The test pyramid is now ready for DEVELOP wave implementation. The NotImplementedError pattern in service stubs enables proper Outside-In TDD where:

1. Tests are written first (RED - NotImplementedError raised)
2. Developer implements service method (GREEN - test passes)
3. Refactor while tests stay green

The tests cannot pass until real implementation exists, which is the core principle of test-driven development.
