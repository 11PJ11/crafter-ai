# Implementation Plan: Phase 08 - Error Handling for Forge TUI

## Overview

Phase 08 implements comprehensive error display patterns for all failure scenarios in the forge build and install commands. The design follows Luna's UX specification for clean, emoji-based error displays without Rich borders or panels.

## Current State Analysis

**Current Implementation:**
- `/Users/mike/ProgettiGit/Undeadgrishnackh/crafter-ai/src/crafter_ai/installer/cli/forge_build.py` - Has basic success path, minimal error handling
- `/Users/mike/ProgettiGit/Undeadgrishnackh/crafter-ai/src/crafter_ai/installer/cli/forge_install.py` - Has basic success path, minimal error handling
- `/Users/mike/ProgettiGit/Undeadgrishnackh/crafter-ai/src/crafter_ai/installer/cli/forge_tui.py` - Shared TUI components, currently only handles success cases

**What's Missing:**
1. Error display functions for all failure scenarios
2. Proper error state detection and branching logic
3. Remediation display with "Fix:" lines
4. Degraded health state handling with warning emoji
5. Exit code 1 enforcement for all failure paths

## Error Scenarios to Implement

### 1. Blocking Build Pre-flight Failures
**Location:** `forge_build.py`
**Trigger:** Pre-flight checks return blocking failures
**Display Pattern:**
```
  🔍 Pre-flight checks
  ❌ pyproject.toml not found
  ✅ Build toolchain ready
  ❌ Source directory not found
  ⚠️  Uncommitted changes detected
  ✅ Version available for release

  Build blocked: 2 checks failed

  ❌ pyproject.toml not found
     Fix: Create pyproject.toml in project root

  ❌ Source directory not found
     Fix: Create a src/ directory with your package structure
```
**Exit Code:** 1

### 2. Blocking Install Pre-flight Failures
**Location:** `forge_install.py`
**Trigger:** Pre-flight checks return blocking failures
**Display Pattern:**
```
  🔍 Pre-flight checks
  ❌ No wheel file found in dist/
  ❌ pipx is not installed
  ✅ Install path writable

  Install blocked: 2 checks failed

  ❌ No wheel file found in dist/
     Fix: Run 'nw forge build' first

  ❌ pipx is not installed
     Fix: pip install pipx && pipx ensurepath
```
**Exit Code:** 1

### 3. Build Compilation Failure
**Location:** `forge_build.py`
**Trigger:** `BuildService.execute()` returns `success=False` after pre-flight passes
**Display Pattern:**
```
  [Pre-flight passed, version displayed]

  ❌ Build failed

  Error: Invalid package metadata in pyproject.toml
  Fix: Check [project] section in pyproject.toml
```
**Exit Code:** 1

### 4. IDE Bundle Build Failure
**Location:** `forge_build.py`
**Trigger:** `BuildResult.ide_bundle_result` indicates failure
**Display Pattern:**
```
  [Pre-flight passed, version displayed, wheel built]

  ❌ IDE bundle build failed

  Error: nWave/ source directory is missing or empty
  Fix: Ensure nWave/ directory exists with agent and command source files
```
**Exit Code:** 1

### 5. pipx Install Failure
**Location:** `forge_install.py`
**Trigger:** `InstallService.install()` returns `success=False`
**Display Pattern:**
```
  [Pre-flight passed, backup shown]

  ❌ Installation failed

  Error: pipx install failed: dependency conflict
  Fix: Try 'pipx install --force' or check dependency versions
```
**Exit Code:** 1

### 6. Asset Deployment Failure
**Location:** `forge_install.py`
**Trigger:** `InstallResult.asset_deployment_result` indicates failure
**Display Pattern:**
```
  [Pre-flight passed, CLI installed]

  ❌ Asset deployment failed

  Error: Permission denied writing to ~/.claude/agents/nw/
  Fix: Check write permissions on ~/.claude/ directory
```
**Exit Code:** 1

### 7. Deployment Validation Failure
**Location:** `forge_install.py`
**Trigger:** `InstallResult.deployment_validation_result.valid == False`
**Display Pattern:**
```
  🔍 Validating deployment
  ✅ Agents verified (30)
  ❌ Commands verification failed (expected 23, found 21)
  ✅ Templates verified (17)
  ✅ Scripts verified (4)

  Deployment validation failed: 1 check failed

  ❌ Commands verification failed (expected 23, found 21)
     Fix: Re-run 'crafter-ai forge install' or check ~/.claude/commands/nw/
```
**Exit Code:** 1

### 8. Degraded Health State
**Location:** `forge_install.py`
**Trigger:** `InstallResult.health_status == HealthStatus.DEGRADED`
**Display Pattern:**
```
  [Health check section with mixed results]

  ⚠️ crafter-ai 0.2.0 installed with warnings

  Some features may be limited. Run crafter-ai doctor for details.
```
**Exit Code:** 0 (success with warnings)

## Implementation Steps

### Step 1: Extract and Enhance Pre-flight Display in `forge_tui.py`

**Changes needed:**
- Modify `display_pre_flight_results()` to:
  - Return whether blocking failures exist
  - Still display all checks (pass and fail)
  - NOT print "Pre-flight passed" if blocking failures exist

**New function to add:**
```python
def display_blocking_failure_summary(
    phase_name: str,  # "Build" or "Install"
    failures: list[CheckResult]
) -> None:
    """Display blocking failure summary with remediation."""
```

### Step 2: Enhance Build Command Error Handling in `forge_build.py`

**Modify existing code:**
- Line 216-217: After `display_pre_flight_results()`, check for blocking failures
- Line 221-223: Replace `display_failure_summary()` with detailed error display
- Add detection for IDE bundle build failures
- Ensure all error paths exit with code 1

**New functions to add:**
```python
def display_build_compilation_failure(error_message: str) -> None:
    """Display build compilation failure with error and fix."""

def display_ide_bundle_failure(error_message: str) -> None:
    """Display IDE bundle build failure with error and fix."""
```

### Step 3: Enhance Install Command Error Handling in `forge_install.py`

**Modify existing code:**
- Line 388: After `display_pre_flight_results()`, check for blocking failures
- Line 392-394: Use new blocking failure display function
- Line 520-524: Replace `display_failure()` with scenario-specific error display
- Add detection for asset deployment and validation failures
- Add degraded health display (lines 512-518)

**New functions to add:**
```python
def display_install_failure(error_message: str) -> None:
    """Display installation failure with error and fix."""

def display_asset_deployment_failure(error_message: str) -> None:
    """Display asset deployment failure with error and fix."""

def display_deployment_validation_failure(
    validation_result: DeploymentValidationResult
) -> None:
    """Display deployment validation failure with all checks and remediation."""

def display_degraded_health_celebration(version: str) -> None:
    """Display degraded health celebration with warning emoji."""
```

### Step 4: Update Error Detection Logic

**Build flow (forge_build.py):**
```python
# After pre-flight display
blocking_failures = get_blocking_failures(result.pre_flight_results)
if blocking_failures:
    display_blocking_failure_summary("Build", blocking_failures)
    raise typer.Exit(code=1)

# Display version only if pre-flight passed
display_version_info(candidate)

# Check for compilation failure
if not result.success and result.wheel_path is None:
    display_build_compilation_failure(result.error_message)
    raise typer.Exit(code=1)

# Check for IDE bundle failure
if result.ide_bundle_result and not result.ide_bundle_result.success:
    display_ide_bundle_failure(result.error_message)
    raise typer.Exit(code=1)
```

**Install flow (forge_install.py):**
```python
# After pre-flight display
blocking_failures = get_blocking_failures(pre_flight_results)
if blocking_failures:
    display_blocking_failure_summary("Install", blocking_failures)
    raise typer.Exit(code=1)

# After install execution
if not install_result.success:
    # Determine failure type
    if InstallPhase.INSTALL not in install_result.phases_completed:
        display_install_failure(install_result.error_message)
    elif install_result.asset_deployment_result and not install_result.asset_deployment_result.success:
        display_asset_deployment_failure(install_result.error_message)
    elif install_result.deployment_validation_result and not install_result.deployment_validation_result.valid:
        display_deployment_validation_failure(install_result.deployment_validation_result)
    else:
        display_failure(install_result.error_message)
    raise typer.Exit(code=1)

# Handle degraded health
if install_result.health_status == HealthStatus.DEGRADED:
    display_degraded_health_celebration(install_result.version)
else:
    display_healthy_celebration(install_result.version)
```

### Step 5: Add Remediation Extraction Logic

**Create helper in `forge_tui.py`:**
```python
def extract_remediation_from_error(error_message: str) -> str | None:
    """Extract or generate remediation hint from error message.

    Maps common error patterns to actionable fixes.
    """
    # Pattern matching for common errors
    # Returns "Fix: <specific action>" or None
```

### Step 6: Test Coverage Validation

**Verify each test passes:**
- `TestBlockingBuildPreFlight` (3 tests)
- `TestBlockingInstallPreFlight` (1 test)
- `TestBuildCompilationFailure` (3 tests)
- `TestInstallFailure` (3 tests)
- `TestDegradedHealth` (4 tests)
- `TestIdeBundleBuildFailure` (3 tests)
- `TestAssetDeploymentFailure` (3 tests)
- `TestDeploymentValidationFailure` (2 tests)

**Total:** 22 test scenarios to satisfy

## File-by-File Changes

### `/Users/mike/ProgettiGit/Undeadgrishnackh/crafter-ai/src/crafter_ai/installer/cli/forge_tui.py`

**Add:**
1. `display_blocking_failure_summary()` - Displays "Phase blocked: N checks failed" with remediation
2. `get_blocking_failures()` - Extracts blocking failures from check results
3. Enhanced `display_pre_flight_results()` - Return boolean indicating blocking failures

**Modify:**
- Line 44-47: Don't print "Pre-flight passed" if there are blocking failures

### `/Users/mike/ProgettiGit/Undeadgrishnackh/crafter-ai/src/crafter_ai/installer/cli/forge_build.py`

**Add:**
1. `display_build_compilation_failure()` - Error + Fix lines for compilation failures
2. `display_ide_bundle_failure()` - Error + Fix lines for IDE bundle failures
3. Error branching logic after pre-flight, after build, after IDE bundle

**Modify:**
- Line 142-150: Replace with proper error display functions
- Line 216-224: Add blocking failure detection and display
- Line 232-236: Add IDE bundle failure detection

### `/Users/mike/ProgettiGit/Undeadgrishnackh/crafter-ai/src/crafter_ai/installer/cli/forge_install.py`

**Add:**
1. `display_install_failure()` - Error + Fix lines for pipx failures
2. `display_asset_deployment_failure()` - Error + Fix lines for asset deployment
3. `display_deployment_validation_failure()` - Show all checks + summary + remediation
4. `display_degraded_health_celebration()` - Warning emoji celebration
5. Error branching logic to detect failure types

**Modify:**
- Line 222-236: Move to forge_tui.py and use shared function
- Line 249-257: Replace with scenario-specific error displays
- Line 388-394: Use shared blocking failure display
- Line 520-524: Add failure type detection and appropriate display
- Line 526-530: Add degraded health check and alternate celebration

## Remediation Mapping

**Common error patterns and their fixes:**

| Error Pattern | Fix Message |
|---------------|-------------|
| "pyproject.toml not found" | "Create pyproject.toml in project root" |
| "Source directory not found" | "Create a src/ directory with your package structure" |
| "No wheel file found" | "Run 'crafter-ai forge build' first" |
| "pipx is not installed" | "pip install pipx && pipx ensurepath" |
| "IDE bundle not found" | "Run 'crafter-ai forge build' to generate the IDE bundle" |
| "Permission denied" | "Check write permissions on ~/.claude/ directory" |
| "dependency conflict" | "Try 'pipx install --force' or check dependency versions" |
| "Invalid package metadata" | "Check [project] section in pyproject.toml" |
| "Commands verification failed" | "Re-run 'crafter-ai forge install' or check ~/.claude/commands/nw/" |

## Design Constraints

**MUST:**
1. Use only plain text with emojis (❌, ✅, ⚠️)
2. Use 2-space indentation for check results
3. Use 5-space indentation for "Fix:" lines
4. Show ALL checks (pass and fail) before summary
5. Repeat ONLY failures below summary with remediation
6. Exit with code 1 for all errors except degraded health
7. No Rich Tables, Panels, or border characters

**MUST NOT:**
1. Use any box-drawing characters (╭╮╰╯┏┓┗┛━─┃│┡┩╇╈┼┤├)
2. Leave spinners hanging (always resolve to ✅ or ❌)
3. Show "Pre-flight passed" when blocking failures exist
4. Use party emoji (🎉) for degraded health (use ⚠️ instead)

## Testing Strategy

**Acceptance tests** (already written, currently failing):
- `/Users/mike/ProgettiGit/Undeadgrishnackh/crafter-ai/tests/acceptance/forge_tui/test_error_scenarios.py`

**Test execution:**
```bash
pytest tests/acceptance/forge_tui/test_error_scenarios.py -v
```

**Success criteria:**
- All 22 test scenarios pass
- No forbidden border characters in output
- All error scenarios exit with code 1 (except degraded health = 0)
- All failures show remediation with "Fix:" label

## Dependencies and Integration Points

**Domain objects:**
- `CheckResult` - Already has `remediation` field
- `BuildResult` - Already has `error_message` field
- `InstallResult` - Already has `error_message` and `health_status` fields
- `HealthStatus` - Already has DEGRADED enum value

**Services:**
- `BuildService.execute()` - Already returns failure states
- `InstallService.install()` - Already returns failure states
- No service changes needed

**Shared components:**
- `display_pre_flight_results()` - Needs enhancement
- New error display functions - Need creation

## Risk Assessment

**Low Risk:**
- Pure display logic additions
- No changes to domain models or services
- Tests already define expected behavior

**Medium Risk:**
- Multiple branching paths in error detection
- Need to maintain display consistency across 8 scenarios
- Exit code enforcement in all paths

**Mitigation:**
- Follow exact test specifications
- Use shared helper functions for common patterns
- Run acceptance tests continuously during implementation
