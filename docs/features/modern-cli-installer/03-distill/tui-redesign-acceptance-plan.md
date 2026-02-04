# TUI Redesign Acceptance Test Plan

**Epic**: modern_CLI_installer / TUI Redesign
**Wave**: DISTILL
**Designer**: Quinn (Acceptance Designer)
**Date**: 2026-02-03
**Status**: RED (20/20 tests failing against current implementation)

---

## 1. Overview

This plan covers the TUI redesign for `forge build` and `forge install` commands. The current CLI uses Rich Tables, Panels, and "FORGE:" prefix shouting. Luna's UX design specifies a seamless emoji stream with no borders, reading as one continuous top-to-bottom flow.

A single walking skeleton E2E test file (`tests/acceptance/forge_tui/test_walking_skeleton.py`) contains 20 tests that collectively define the target behavior. All 20 tests are RED. Making them GREEN is the implementation work.

**Approach**: Outside-In TDD. The E2E tests are the outer loop. Implementation proceeds by modifying the CLI presentation layer (`forge_build.py`, `forge_install.py`) while keeping all existing service-layer tests green.

---

## 2. Source Artifacts

| Artifact | Path | Role |
|----------|------|------|
| Walking skeleton feature | `docs/ux/modern-cli-installer/journey-forge-tui.feature` (lines 241-334) | Gherkin scenario defining target behavior |
| Visual design system | `docs/ux/modern-cli-installer/journey-forge-tui-visual.md` | Mockups, emoji vocabulary, anti-patterns |
| Structured step schema | `docs/ux/modern-cli-installer/journey-forge-tui.yaml` | 13 numbered steps with emotional states |
| Walking skeleton test | `tests/acceptance/forge_tui/test_walking_skeleton.py` | 20 E2E tests (all RED) |
| Current build CLI | `src/crafter_ai/installer/cli/forge_build.py` | File to modify |
| Current install CLI | `src/crafter_ai/installer/cli/forge_install.py` | File to modify |
| Existing build tests | `tests/installer/cli/test_forge_build.py` | Anti-regression suite (16 tests) |
| Existing install tests | `tests/installer/cli/test_forge_install.py` | Anti-regression suite (35 tests) |

---

## 3. Walking Skeleton Test Status

**File**: `tests/acceptance/forge_tui/test_walking_skeleton.py`
**Class**: `TestWalkingSkeletonBuildToInstall`
**Marker**: `@pytest.mark.e2e`
**State**: 20/20 RED

All tests invoke the same helper `invoke_full_flow()` which runs `forge build` with mocked services and answers `y` to the install prompt. Each test asserts a specific aspect of the output format.

---

## 4. Test-to-Step Mapping

| # | Test Name | Luna Step | What It Asserts | Primary File to Change | Dependencies |
|---|-----------|-----------|-----------------|----------------------|--------------|
| 1 | `test_output_contains_no_table_or_panel_borders` | Design System | No `FORBIDDEN_BORDER_CHARS` in output | `forge_build.py`, `forge_install.py` | None (gate test) |
| 2 | `test_output_contains_no_forge_prefix_shouting` | Design System | `"FORGE:"` not in output | `forge_build.py`, `forge_install.py` | None (gate test) |
| 3 | `test_build_header_is_emoji_stream` | Step 1 | First non-blank line contains hammer emoji + `"Building crafter-ai"` | `forge_build.py` `build()` | Tests 1,2 |
| 4 | `test_build_preflight_checks_as_streaming_list` | Step 2 | Magnifying glass emoji, individual check messages, warning emoji, `"Pre-flight passed"` | `forge_build.py` `display_pre_flight_results()` | Test 3 |
| 5 | `test_version_display_is_minimal` | Step 3 | Ruler emoji, `"Version"`, version transition `"0.1.0" / "0.2.0" / "minor"` | `forge_build.py` `display_version_info()` | Test 4 |
| 6 | `test_build_spinner_resolves_to_persistent_line` | Step 4 | `"Wheel built"` persistent line after compilation | `forge_build.py` new `display_build_progress()` | Test 5 |
| 7 | `test_wheel_validation_checks` | Step 5 | `"Validating wheel"`, `"PEP 427 format valid"`, `"Metadata complete"`, `"Wheel validated"` | `forge_build.py` new `display_wheel_validation()` | Test 6 |
| 8 | `test_build_complete_line_is_concise` | Step 6 | Hammer emoji + `"Build complete: crafter_ai-0.2.0-py3-none-any.whl"` as single line | `forge_build.py` `display_success_summary()` | Test 7 |
| 9 | `test_install_prompt_format_and_version` | Step 7 | `"Install crafter-ai 0.2.0?"` + `"[Y/n]"` | `forge_build.py` `build()` (prompt logic) | Test 8 |
| 10 | `test_install_header_is_emoji_stream` | Step 8 | Package emoji + `"Installing crafter-ai"` | `forge_install.py` `display_header()` | Test 9 |
| 11 | `test_install_preflight_checks_as_streaming_list` | Step 9 | Check messages + `"Pre-flight passed"` appears at least twice | `forge_install.py` `display_pre_flight_results()` | Test 10 |
| 12 | `test_fresh_install_skips_backup` | Step 10 | `"Fresh install, skipping backup"` | `forge_install.py` `install()` | Test 11 |
| 13 | `test_install_spinner_resolves_to_persistent_line` | Step 11 | `"Installed via pipx"` persistent line | `forge_install.py` `install()` | Test 12 |
| 14 | `test_health_verification_as_check_list` | Step 12 | Stethoscope emoji, `"Verifying installation"`, health check messages, `"Health: HEALTHY"` | `forge_install.py` `install()` | Test 13 |
| 15 | `test_celebration_message_format` | Step 13 | Party popper emoji, `"crafter-ai 0.2.0 installed and healthy!"`, `"Ready to use in Claude Code."` | `forge_install.py` `install()` | Test 14 |
| 16 | `test_version_consistency_across_all_displays` | Shared Artifacts | Version `"0.2.0"` in 4 locations (version display, wheel filename, install prompt, celebration) | `forge_build.py`, `forge_install.py` | Tests 5,8,9,15 |
| 17 | `test_output_reads_as_continuous_stream` | Design System | 12 ordered markers appear in correct sequence | `forge_build.py`, `forge_install.py` | All above |
| 18 | `test_no_version_analysis_panel` | Design System | `"Version Analysis"` and `"Version Bump:"` not in output | `forge_build.py` `display_version_info()` | Test 5 |
| 19 | `test_no_build_summary_panel` | Design System | `"Build Summary"` not in output | `forge_build.py` `display_success_summary()` | Test 8 |
| 20 | `test_no_installation_panel` | Design System | `"FORGE: INSTALL"` not in output | `forge_install.py` `display_header()` | Test 10 |

---

## 5. Implementation Sequence

The sequence is outside-in: start with E2E tests RED, each WIP step makes more GREEN. Group by file and dependency chain.

### Phase TUI-01: Remove Borders (Tests 1, 2, 18, 19, 20)

**Goal**: Eliminate Rich Table, Panel, and "FORGE:" prefix from both files.

**WIP Step TUI-01-01**: Strip Tables and Panels from `forge_build.py`

- **File**: `src/crafter_ai/installer/cli/forge_build.py`
- **Functions to change**: `display_pre_flight_results()`, `display_version_info()`, `display_success_summary()`
- **Change**: Remove `Table()` and `Panel()` calls. Replace with `console.print()` using plain text + emoji. Remove `"FORGE: BUILD COMPLETE"` and `"Version Analysis"` and `"Build Summary"` strings.
- **Remove imports**: `from rich.panel import Panel`, `from rich.table import Table`
- **Tests turned GREEN**: 1 (partial), 2 (partial), 18, 19
- **Breaking existing tests that need updating in this commit**:
  - `TestSuccessSummary::test_displays_forge_build_complete` -- asserts `"FORGE: BUILD COMPLETE"` in output; update to assert new format
  - `TestInstallPrompt::test_prompt_appears_when_not_ci` -- asserts `"Install locally now?"` in output; keep for now (prompt text changes in TUI-03-01)

**WIP Step TUI-01-02**: Strip Tables and Panels from `forge_install.py`

- **File**: `src/crafter_ai/installer/cli/forge_install.py`
- **Functions to change**: `display_header()`, `display_pre_flight_results()`, `display_blocking_failures()`, `run_auto_chain_build()` (uses `Panel()` at lines 118-124 and 127-133)
- **Change**: Remove `Table()` and `Panel()` calls. Replace with `console.print()` using plain text + emoji. Remove `"FORGE: INSTALL"` and `"FORGE: INSTALL BLOCKED"` strings.
- **Remove imports**: `from rich.panel import Panel`, `from rich.table import Table`
- **Tests turned GREEN**: 1 (full), 2 (full), 20
- **Breaking existing tests that need updating in this commit**:
  - `TestHeaderDisplay::test_displays_forge_install_header` -- asserts `"FORGE: INSTALL"` in output; update to assert new header format
  - `TestReleaseReportDisplay::test_displays_release_report_on_success` -- asserts `"FORGE: INSTALL COMPLETE"` in output; update (see Section 5.1 below)

### Phase TUI-02: Build Phase Emoji Stream (Tests 3, 4, 5, 6, 7, 8)

**Goal**: Implement Luna's Steps 1-6 for the build phase.

**CRITICAL: Call order reordering required.** The current `forge_build.py` `build()` function calls `display_version_info()` BEFORE `display_pre_flight_results()` (lines 195 vs 204). Luna's design requires pre-flight FIRST (Step 2), then version (Step 3). The software-crafter must restructure the call order in `build()` to match Luna's step sequence:

```
# CURRENT ORDER (wrong):
display_version_info(candidate)       # Step 3 - called too early
result = service.execute(...)
display_pre_flight_results(result...) # Step 2 - called too late

# REQUIRED ORDER (Luna's design):
# 1. Print build header (Step 1)
# 2. display_pre_flight_results()    # Step 2
# 3. display_version_info()          # Step 3
# 4. display_build_progress()        # Step 4 - new function
# 5. display_wheel_validation()      # Step 5 - new function
# 6. display_success_summary()       # Step 6
```

**WIP Step TUI-02-01**: Build header + pre-flight streaming + call order fix

- **File**: `src/crafter_ai/installer/cli/forge_build.py`
- **Functions**: `build()` (header + reorder calls), `display_pre_flight_results()`
- **Change**:
  - Restructure `build()` call order: pre-flight before version display
  - Print `"hammer_emoji Building crafter-ai"` as first line (bold)
  - Rewrite `display_pre_flight_results()`: print `"magnifying_glass Pre-flight checks"` indented 2 spaces, then each check with checkmark/warning emoji indented 2 spaces, then `"Pre-flight passed"` summary
- **Tests turned GREEN**: 3, 4
- **Breaking existing tests that need updating in this commit**:
  - `TestPreFlightDisplay::test_displays_passing_checks_with_checkmark` -- currently asserts `"pyproject.toml exists"` (the check name); update to assert `"pyproject.toml found"` (the check message, since new format shows messages not names)

**WIP Step TUI-02-02**: Version display + compilation + wheel validation + build complete

- **File**: `src/crafter_ai/installer/cli/forge_build.py`
- **Functions**: `display_version_info()`, new `display_build_progress()`, new `display_wheel_validation()`, `display_success_summary()`
- **Change**:
  - Rewrite `display_version_info()`: print `"ruler_emoji Version"` with `"0.1.0 -> 0.2.0 (minor)"` as minimal lines (no Panel, no "Version Bump:" label, no "Version Analysis" title)
  - Create `display_build_progress()`: print `"Wheel built ({duration})"` as persistent line after compilation
  - Create `display_wheel_validation()`: print `"Validating wheel"` header, then `"PEP 427 format valid"`, `"Metadata complete"`, `"Wheel validated"` as streaming check list
  - Rewrite `display_success_summary()`: print `"hammer_emoji Build complete: {wheel_filename}"` as single concise line (no Panel, no "Build Summary" title)
- **Tests turned GREEN**: 5, 6, 7, 8
- **Breaking existing tests that need updating in this commit**:
  - `TestVersionDisplay::test_displays_version_bump_info` -- currently asserts `"0.1.0"` and `"0.2.0"` (will still pass if version numbers remain; no update needed)
  - `TestSuccessSummary::test_displays_wheel_path_in_summary` -- asserts `"crafter_ai-0.2.0-py3-none-any.whl"` (will still pass if wheel name remains; no update needed)

### Phase TUI-03: Install Prompt Redesign (Test 9)

**Goal**: Implement Luna's Step 7 confirmation prompt.

**WIP Step TUI-03-01**: Redesign install confirmation prompt

- **File**: `src/crafter_ai/installer/cli/forge_build.py`
- **Function**: `build()` (the `typer.confirm("Install locally now?")` call at line 230)
- **Change**: Replace `typer.confirm("Install locally now?", default=True)` with a prompt that shows `"Install crafter-ai {version}? [Y/n]: "` using package emoji. The version must come from `result.version` (wheel METADATA).
- **Tests turned GREEN**: 9
- **Breaking existing tests that need updating in this commit**:
  - `TestInstallPrompt::test_prompt_appears_when_not_ci` -- asserts `"Install locally now?"` in output; update to assert `"Install crafter-ai"` and `"[Y/n]"`
  - `TestInstallPrompt::test_no_prompt_flag_skips_prompt` -- asserts `"Install locally now?" not in output`; update to assert `"Install crafter-ai" not in output`
  - `TestCIModeDetection::test_ci_env_suppresses_prompts` -- asserts `"Install locally now?" not in output`; update to assert `"Install crafter-ai" not in output`
  - `TestInstallPrompt::test_install_flag_triggers_auto_install_message` -- asserts `"Install locally now?" not in output`; update to assert `"Install crafter-ai" not in output`

### Phase TUI-04: Install Phase Emoji Stream (Tests 10, 11, 12, 13, 14, 15)

**Goal**: Implement Luna's Steps 8-13 for the install phase.

**WIP Step TUI-04-01**: Install header + pre-flight streaming

- **File**: `src/crafter_ai/installer/cli/forge_install.py`
- **Functions**: `display_header()`, `display_pre_flight_results()`
- **Change**:
  - Rewrite `display_header()`: print `"package_emoji Installing crafter-ai"` as phase header (bold), no Panel
  - Rewrite `display_pre_flight_results()`: streaming emoji list (same pattern as build phase), with `"Pre-flight passed"` summary
- **Tests turned GREEN**: 10, 11
- **Breaking existing tests that need updating in this commit**:
  - `TestPreFlightDisplay::test_displays_pre_flight_results` -- asserts `"Pre-flight" in result.output or "Wheel file exists" in result.output`; likely still passes, but verify
  - `TestPromptBehavior::test_prompt_appears_when_interactive` -- asserts `"Proceed with install?"` in output; update to match new prompt format if changed in this step

**WIP Step TUI-04-02**: Backup skip + pipx install + health check + celebration (replaces ReleaseReportService output)

- **File**: `src/crafter_ai/installer/cli/forge_install.py`
- **Function**: `install()` (main flow, lines 459-508)
- **Change**:
  - Print `"Fresh install, skipping backup"` when no previous install exists
  - Print `"Installed via pipx"` as persistent line after `service.install()` completes
  - Print health verification as streaming check list with stethoscope emoji: `"Verifying installation"`, `"CLI responds to --version"`, `"Core modules loadable"`, `"Health: HEALTHY"`
  - Print celebration: `"party_popper crafter-ai {version} installed and healthy!"` + `"Ready to use in Claude Code."`
  - **Remove ReleaseReportService output**: Luna's design replaces the `report_service.format_console()` output (which produces `"FORGE: INSTALL COMPLETE"` with `===` borders) with the 2-line celebration pattern above. Remove the `ReleaseReportService` calls from the install flow entirely. The report service can remain in the codebase for other uses, but `install()` no longer calls it for display.
- **Tests turned GREEN**: 12, 13, 14, 15
- **Breaking existing tests that need updating in this commit**:
  - `TestReleaseReportDisplay::test_displays_release_report_on_success` -- asserts `"FORGE: INSTALL COMPLETE"` in output; update to assert celebration format instead
  - `TestPromptBehavior::test_user_declines_install` -- asserts `"Install cancelled"` in output; should still pass if cancellation message text is preserved

### Phase TUI-05: Consistency Validation (Tests 16, 17)

**Goal**: Verify shared artifact consistency and phase ordering.

These tests do not require additional code changes. They pass when all previous phases are implemented correctly.

- **Test 16** (`test_version_consistency_across_all_displays`): Passes when version `"0.2.0"` appears in all 4 locations.
- **Test 17** (`test_output_reads_as_continuous_stream`): Passes when all 12 ordered markers appear in correct sequence (including `"Wheel built"` from Step 4).

**Tests turned GREEN**: 16, 17

---

### 5.1 ReleaseReportService Decision

Luna's design replaces the release report output entirely. The current `install()` function calls:

```python
report_service = ReleaseReportService()
release_report = report_service.generate(...)
formatted_report = report_service.format_console(release_report)
console.print(formatted_report)  # Produces "FORGE: INSTALL COMPLETE" with === borders
```

This is replaced by the 2-line celebration pattern:

```
party_popper crafter-ai 0.2.0 installed and healthy!
   Ready to use in Claude Code.
```

The `ReleaseReportService` class remains in the codebase (other flows may use it), but the `install()` function no longer calls it for console display.

---

## 6. Files to Modify

| File | Changes Required | Existing Tests to Protect |
|------|-----------------|--------------------------|
| `src/crafter_ai/installer/cli/forge_build.py` | Remove Table/Panel/FORGE prefix; reorder calls (pre-flight before version); add emoji headers, streaming check lists, minimal version display, new `display_build_progress()`, new `display_wheel_validation()`, concise build complete with hammer emoji, redesigned prompt | `tests/installer/cli/test_forge_build.py` (16 tests) |
| `src/crafter_ai/installer/cli/forge_install.py` | Remove Table/Panel/FORGE prefix (including in `run_auto_chain_build()`); add emoji headers, streaming check lists, backup skip message, persistent install line, health check list, celebration; remove ReleaseReportService console output | `tests/installer/cli/test_forge_install.py` (35 tests) |

**Files NOT modified** (service layer untouched):
- `src/crafter_ai/installer/services/build_service.py`
- `src/crafter_ai/installer/services/install_service.py`
- `src/crafter_ai/installer/services/release_report_service.py` (kept, just not called from `install()`)
- All domain objects, ports, adapters

---

## 7. Error-Path Functions (Future Migration)

The following error-path display functions use `Panel()` but are NOT covered by the walking skeleton happy-path tests. They should be migrated in a separate future step for full design system consistency:

| Function | File | Current Pattern | Target Pattern |
|----------|------|----------------|----------------|
| `display_failure_summary()` | `forge_build.py` | `Panel("FORGE: BUILD FAILED", border_style="red")` | Error emoji + plain text error message |
| `display_failure()` | `forge_install.py` | `Panel("FORGE: INSTALL FAILED", border_style="red")` | Error emoji + plain text error message |
| `display_blocking_failures()` | `forge_install.py` | `Panel("FORGE: INSTALL BLOCKED", border_style="red")` | Error emoji + plain text failure list |

These are not part of the current walking skeleton scope but should be tracked for a follow-up TUI consistency pass.

---

## 8. Anti-Regression Test Suites

The following existing test suites MUST remain green throughout implementation:

| Suite | File | Tests | What It Covers |
|-------|------|-------|---------------|
| Build CLI | `tests/installer/cli/test_forge_build.py` | 16 | Exit codes, pre-flight blocking, service errors, CI mode, no-prompt flag |
| Install CLI | `tests/installer/cli/test_forge_install.py` | 35 | Exit codes, pre-flight blocking, service errors, CI mode, auto-chain, wheel selection |
| Build Service | `tests/installer/services/test_build_service.py` | 16 | Build orchestration logic |
| Install Service | `tests/installer/services/test_install_service.py` | 27 | Install orchestration logic |
| Domain objects | `tests/installer/domain/` | ~67 | CheckResult, CandidateVersion, HealthChecker, ArtifactRegistry |

### Existing Tests Breaking per WIP Step

Each WIP step may break specific existing tests that assert on old TUI strings. The software-crafter must update these tests in the same commit as the TUI change.

**TUI-01-01** (strip build Panels):
- `test_displays_forge_build_complete` -- asserts `"FORGE: BUILD COMPLETE"`; update assertion

**TUI-01-02** (strip install Panels):
- `test_displays_forge_install_header` -- asserts `"FORGE: INSTALL"`; update assertion
- `test_displays_release_report_on_success` -- asserts `"FORGE: INSTALL COMPLETE"`; update assertion

**TUI-02-01** (build header + pre-flight reorder):
- `test_displays_passing_checks_with_checkmark` -- asserts check name `"pyproject.toml exists"`; may need update if format changes to show message instead of name

**TUI-02-02** (version + validation + build complete):
- No existing tests expected to break (version numbers and wheel name still present)

**TUI-03-01** (install prompt redesign):
- `test_prompt_appears_when_not_ci` -- asserts `"Install locally now?"`; update to `"Install crafter-ai"`
- `test_no_prompt_flag_skips_prompt` -- asserts `"Install locally now?" not in`; update to `"Install crafter-ai" not in`
- `test_ci_env_suppresses_prompts` -- asserts `"Install locally now?" not in`; update to `"Install crafter-ai" not in`
- `test_install_flag_triggers_auto_install_message` -- asserts `"Install locally now?" not in`; update to `"Install crafter-ai" not in`

**TUI-04-01** (install header + pre-flight):
- `test_displays_pre_flight_results` -- asserts `"Pre-flight" or "Wheel file exists"`; likely still passes
- `test_prompt_appears_when_interactive` -- asserts `"Proceed with install?"`; update if prompt text changes

**TUI-04-02** (celebration replaces release report):
- `test_displays_release_report_on_success` -- asserts `"FORGE: INSTALL COMPLETE"`; update to assert celebration format

---

## 9. Verification Commands

```bash
# Run walking skeleton tests (expect 20 RED before implementation)
pytest tests/acceptance/forge_tui/test_walking_skeleton.py -v --tb=line

# Run anti-regression suites (MUST stay green)
pytest tests/installer/cli/test_forge_build.py -v
pytest tests/installer/cli/test_forge_install.py -v

# Run all tests
pytest tests/ -v --tb=short

# Run only E2E tests
pytest -m e2e -v
```

---

## 10. WIP.yaml Contract Mapping

Each WIP step above maps to a WIP.yaml contract for the software-crafter agent:

| WIP Step | Source File | Test File | Breaking Existing Tests | Requirements Summary |
|----------|-----------|-----------|------------------------|---------------------|
| TUI-01-01 | `forge_build.py` | `test_walking_skeleton.py` (1,2,18,19) | `test_displays_forge_build_complete` | Remove Table, Panel, FORGE prefix from build CLI |
| TUI-01-02 | `forge_install.py` | `test_walking_skeleton.py` (1,2,20) | `test_displays_forge_install_header`, `test_displays_release_report_on_success` | Remove Table, Panel, FORGE prefix from install CLI; includes `run_auto_chain_build()` Panels |
| TUI-02-01 | `forge_build.py` | `test_walking_skeleton.py` (3,4) | `test_displays_passing_checks_with_checkmark` (maybe) | Build header + pre-flight as emoji stream; REORDER calls in `build()` |
| TUI-02-02 | `forge_build.py` | `test_walking_skeleton.py` (5,6,7,8) | None expected | Version display + `display_build_progress()` + `display_wheel_validation()` + build complete with hammer emoji |
| TUI-03-01 | `forge_build.py` | `test_walking_skeleton.py` (9) | `test_prompt_appears_when_not_ci`, `test_no_prompt_flag_skips_prompt`, `test_ci_env_suppresses_prompts`, `test_install_flag_triggers_auto_install_message` | Redesign install prompt with version from wheel METADATA |
| TUI-04-01 | `forge_install.py` | `test_walking_skeleton.py` (10,11) | `test_prompt_appears_when_interactive` (maybe) | Install header + pre-flight as emoji stream |
| TUI-04-02 | `forge_install.py` | `test_walking_skeleton.py` (12,13,14,15) | `test_displays_release_report_on_success` | Backup, pipx, health, celebration; remove ReleaseReportService console output |

Tests 16 and 17 are integration validation; they pass when all prior steps complete correctly.

---

## 11. Forbidden Border Characters Reference

```python
FORBIDDEN_BORDER_CHARS = set("╭╮╰╯┏┓┗┛━─┃│┡┩╇╈┼┤├")
```

Any output containing these characters means Rich Tables or Panels are still rendering. Tests 1 and 2 are gate tests that block all other work.

---

*Acceptance Test Plan maintained by Quinn (Acceptance Designer) for the TUI redesign of the modern_CLI_installer forge build+install flow.*
