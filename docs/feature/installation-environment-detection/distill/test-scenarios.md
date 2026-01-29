# APEX-002: Installation Environment Detection - Test Scenarios

## Overview

This document provides an overview of all acceptance test scenarios for the Installation Environment Detection feature (APEX-002). Tests are implemented using pytest-bdd with Gherkin syntax.

**Test Location:** `tests/acceptance/installation/`
**Entry Points Under Test:**
- `scripts/install/install_nwave.py` - Main installer (driving port)
- `scripts/install/verify_nwave.py` - Verification script (driving port - to be created)

---

## Acceptance Criteria Summary

| AC | Description | Scenarios | Status |
|----|-------------|-----------|--------|
| AC-01 | Pre-flight Environment Check Runs First | 3 | @skip |
| AC-02 | Virtual Environment Hard Block | 3 | @skip |
| AC-03 | Pipenv-Only Enforcement | 3 | @skip |
| AC-04 | Context-Aware Terminal Errors | 3 | @skip |
| AC-05 | Context-Aware Claude Code Errors | 5 | @skip |
| AC-06 | Dependency Verification Before Build | 6 | @skip |
| AC-07 | Automatic Post-Installation Verification | 5 | @skip |
| AC-08 | Standalone Verification Command | 5 | @skip |
| AC-09 | Installation Logging | 6 | @skip |
| AC-10 | Documentation Accuracy | 5 | @skip |
| **Total** | | **44** | |

---

## Feature File Structure

### 01_preflight_checks.feature

**Purpose:** Validate pre-flight environment checks run before installation

**Scenarios:**
1. Environment validation runs before any installation action
2. Pre-flight check validates virtual environment first
3. Pre-flight results are logged
4. Installation blocked when not in virtual environment
5. Skip-checks flag does not bypass virtual environment requirement
6. Installation proceeds when in virtual environment
7. Error when pipenv is not installed
8. Error messages reference only pipenv for dependency installation
9. Pipenv installation guidance is actionable

### 02_error_messages.feature

**Purpose:** Validate context-aware error message formatting

**Scenarios:**
1. Terminal error format uses ERROR/FIX/THEN structure
2. Missing dependency error shows module name in terminal
3. Permission error provides clear terminal guidance
4. Claude Code context outputs JSON error for missing venv
5. Claude Code context outputs JSON error for missing pipenv
6. Claude Code context outputs JSON error for missing dependency
7. Claude Code JSON includes all required error fields
8. Error code mapping is consistent

### 03_dependency_verification.feature

**Purpose:** Validate dependency verification before build

**Scenarios:**
1. All dependencies present allows check to pass
2. Single missing dependency shows module name
3. Multiple missing dependencies lists all modules
4. Dependency check runs before build attempt
5. Required dependencies list is comprehensive
6. Dependency error provides complete remediation

### 04_post_installation.feature

**Purpose:** Validate post-installation verification

**Scenarios:**
1. Verification runs after successful build
2. Verification reports agent file count
3. Verification reports command file count
4. Verification reports manifest existence
5. Verification detects missing essential files
6. Standalone verification script exists
7. Verification passes when fully installed
8. Verification fails with remediation when files missing
9. Verification checks essential DW commands
10. Verification validates schema template

### 05_logging.feature

**Purpose:** Validate installation logging

**Scenarios:**
1. Log file is created at standard location
2. Successful actions are logged with timestamp
3. Errors are logged with detail
4. Pre-flight check results are logged
5. Log persists across installation attempts
6. Log format is parseable

### 06_documentation.feature

**Purpose:** Validate documentation accuracy

**Scenarios:**
1. Quick start commands work on virgin machine (manual)
2. Prerequisites are correctly stated
3. Quick start section includes virtual environment setup
4. Documentation mentions pipenv requirement
5. Troubleshooting section addresses common errors

---

## Error Code Reference

| Error Code | Condition | Terminal Message |
|------------|-----------|------------------|
| ENV_NO_VENV | Not in virtual environment | "Virtual environment required" |
| ENV_NO_PIPENV | Pipenv not installed | "pipenv is required" |
| DEP_MISSING | Required module not found | "Missing required module: {name}" |
| BUILD_FAILED | Build phase error | "Build failed" |
| VERIFY_FAILED | Verification found issues | "Verification failed" |

---

## Test Tags

| Tag | Description |
|-----|-------------|
| @skip | Scenario not yet enabled for implementation |
| @wip | Work in progress (only one at a time) |
| @requires_no_venv | Needs execution outside virtual environment |
| @requires_venv | Needs active virtual environment |
| @requires_no_pipenv | Needs pipenv to be unavailable |
| @manual | Requires manual verification |
| @ac01 - @ac10 | Acceptance criteria mapping |

---

## One-at-a-Time Implementation Strategy

All scenarios start with `@skip` tag. Implementation follows this pattern:

1. **Remove @skip** from ONE scenario
2. **Run test** - should fail (RED)
3. **Implement production code** to make test pass
4. **Verify GREEN** - test passes
5. **Commit** working increment
6. **Enable next scenario** - repeat

This ensures Outside-In TDD: failing acceptance test drives implementation.

---

## Hexagonal Boundary Enforcement

**CRITICAL:** All tests invoke through DRIVING PORTS only.

**Correct Pattern:**
```python
# Run the actual script via subprocess (user's perspective)
result = subprocess.run(
    [sys.executable, "scripts/install/install_nwave.py"],
    capture_output=True, text=True
)
```

**Incorrect Pattern:**
```python
# DON'T DO THIS - tests internal component directly
from preflight_checker import PreflightChecker
checker = PreflightChecker()
```

---

## Implementation Notes

### Environment Simulation

Tests use environment variables to simulate conditions:
- `NWAVE_TEST_NO_VENV=1` - Simulate not in virtual environment
- `NWAVE_TEST_NO_PIPENV=1` - Simulate pipenv not installed
- `NWAVE_TEST_MISSING_DEPS=yaml,requests` - Simulate missing dependencies
- `NWAVE_OUTPUT_CONTEXT=terminal|claude_code` - Set output format

### Test Isolation

Each test runs in an isolated `tmp_path` with:
- Fake `~/.claude/` directory
- Clean environment variables
- No access to real installation

### Cross-Platform Compatibility

- Uses `sys.executable` for Python interpreter
- Uses `os.environ.copy()` to preserve system PATH
- Handles both Unix and Windows path separators
