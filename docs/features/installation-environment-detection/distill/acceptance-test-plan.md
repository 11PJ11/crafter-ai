# APEX-002: Installation Environment Detection - Acceptance Test Plan

## Executive Summary

This document defines the acceptance test execution strategy for the Installation Environment Detection feature (APEX-002). Tests validate pre-flight environment checks, context-aware error messages, and post-installation verification.

---

## Test Framework

**Framework:** pytest-bdd (Python native)
**Test Location:** `tests/acceptance/installation/`
**Feature Files:** `tests/acceptance/installation/features/`
**Step Definitions:** `tests/acceptance/installation/step_defs/`

---

## Test Execution Commands

### Run All Installation Acceptance Tests

```bash
# From project root
pipenv run pytest tests/acceptance/installation/ -v
```

### Run Specific Feature File

```bash
# Pre-flight checks
pipenv run pytest tests/acceptance/installation/ -v -k "preflight"

# Error messages
pipenv run pytest tests/acceptance/installation/ -v -k "error_messages"

# Dependency verification
pipenv run pytest tests/acceptance/installation/ -v -k "dependency"

# Post-installation verification
pipenv run pytest tests/acceptance/installation/ -v -k "post_installation"

# Logging
pipenv run pytest tests/acceptance/installation/ -v -k "logging"

# Documentation
pipenv run pytest tests/acceptance/installation/ -v -k "documentation"
```

### Run by Acceptance Criteria

```bash
# AC-01: Pre-flight Environment Check
pipenv run pytest tests/acceptance/installation/ -v -m "ac01"

# AC-02: Virtual Environment Hard Block
pipenv run pytest tests/acceptance/installation/ -v -m "ac02"

# AC-03: Pipenv-Only Enforcement
pipenv run pytest tests/acceptance/installation/ -v -m "ac03"

# AC-04: Context-Aware Terminal Errors
pipenv run pytest tests/acceptance/installation/ -v -m "ac04"

# AC-05: Context-Aware Claude Code Errors
pipenv run pytest tests/acceptance/installation/ -v -m "ac05"

# AC-06: Dependency Verification
pipenv run pytest tests/acceptance/installation/ -v -m "ac06"

# AC-07: Automatic Post-Installation Verification
pipenv run pytest tests/acceptance/installation/ -v -m "ac07"

# AC-08: Standalone Verification Command
pipenv run pytest tests/acceptance/installation/ -v -m "ac08"

# AC-09: Installation Logging
pipenv run pytest tests/acceptance/installation/ -v -m "ac09"

# AC-10: Documentation Accuracy
pipenv run pytest tests/acceptance/installation/ -v -m "ac10"
```

### Skip Manual Tests

```bash
pipenv run pytest tests/acceptance/installation/ -v -m "not manual"
```

### Run Only Non-Skipped Tests

```bash
pipenv run pytest tests/acceptance/installation/ -v --ignore-glob="*@skip*"
```

---

## Implementation Sequence

### Phase 1: Core Pre-flight Checks (AC-01, AC-02, AC-03)

**Priority: High**
**Estimated Effort: 2-3 days**

1. **AC-02: Virtual Environment Hard Block** (Start here)
   - Enable scenario: "Installation blocked when not in virtual environment"
   - Implement `_check_virtual_environment()` in installer
   - Implement terminal error output

2. **AC-01: Pre-flight Check Runs First**
   - Enable scenario: "Environment validation runs before any installation action"
   - Integrate pre-flight check call in `main()`

3. **AC-03: Pipenv-Only Enforcement**
   - Enable scenario: "Error when pipenv is not installed"
   - Implement `_check_pipenv()` in installer

### Phase 2: Error Message Formatting (AC-04, AC-05)

**Priority: Medium**
**Estimated Effort: 2 days**

1. **AC-04: Terminal Error Format**
   - Enable scenario: "Terminal error format uses ERROR/FIX/THEN structure"
   - Implement `OutputFormatter.terminal_error()`

2. **AC-05: Claude Code JSON Format**
   - Enable scenario: "Claude Code context outputs JSON error for missing venv"
   - Implement `OutputFormatter.json_error()`
   - Implement context detection

### Phase 3: Dependency Verification (AC-06)

**Priority: High**
**Estimated Effort: 1-2 days**

1. Enable scenario: "Single missing dependency shows module name"
2. Implement `_check_dependencies()` in installer
3. Enable remaining AC-06 scenarios

### Phase 4: Post-Installation Verification (AC-07, AC-08)

**Priority: Medium**
**Estimated Effort: 2-3 days**

1. **AC-07: Automatic Verification**
   - Enable scenario: "Verification runs after successful build"
   - Enhance `validate_installation()` method

2. **AC-08: Standalone Verification**
   - Create `scripts/install/verify_nwave.py`
   - Enable verification scenarios

### Phase 5: Logging (AC-09)

**Priority: Low**
**Estimated Effort: 1 day**

1. Enable scenario: "Log file is created at standard location"
2. Enhance logging to include pre-flight results
3. Enable remaining logging scenarios

### Phase 6: Documentation (AC-10)

**Priority: Low**
**Estimated Effort: 0.5 days**

1. Update `docs/installation/installation-guide.md`
2. Verify documentation scenarios pass
3. Manual verification on clean machine

---

## Test Environment Requirements

### Local Development

- Python 3.8+ (tested with 3.10, 3.11)
- pipenv installed globally
- Active virtual environment
- pytest-bdd installed

### CI/CD Pipeline

- GitHub Actions compatible
- Linux, macOS, and Windows runners
- Matrix testing for Python versions

### Environment Variables for Testing

| Variable | Purpose | Values |
|----------|---------|--------|
| NWAVE_TEST_NO_VENV | Simulate no venv | 1 |
| NWAVE_TEST_NO_PIPENV | Simulate no pipenv | 1 |
| NWAVE_TEST_MISSING_DEPS | Simulate missing deps | comma-separated list |
| NWAVE_OUTPUT_CONTEXT | Output format | terminal, claude_code |
| NWAVE_TEST_PERMISSION_ERROR | Simulate permissions | 1 |
| NWAVE_TEST_BUILD_FAILURE | Simulate build fail | 1 |

---

## Quality Gates

### Before Enabling Next Scenario

- [ ] Current scenario passes (GREEN)
- [ ] All previously enabled scenarios still pass
- [ ] Code quality checks pass (lint, type checks)
- [ ] No regressions in existing functionality

### Before Marking AC Complete

- [ ] All scenarios for AC are enabled and passing
- [ ] Code reviewed and approved
- [ ] Documentation updated if needed
- [ ] Integration tests passing

### Before Feature Release

- [ ] All 10 ACs have passing tests
- [ ] Manual documentation verification complete
- [ ] Cross-platform testing complete (Linux, macOS, Windows)
- [ ] Performance acceptable (installer completes in <30s)

---

## Risk Mitigation

### Risk: Environment Manipulation Complexity

**Mitigation:** Use environment variables for simulation rather than attempting to actually modify system state.

### Risk: Cross-Platform Differences

**Mitigation:**
- Use `sys.executable` for Python paths
- Use `os.environ.copy()` to preserve system environment
- Test on all platforms in CI

### Risk: Test Isolation Failures

**Mitigation:**
- Use pytest `tmp_path` fixture for all file operations
- Reset environment variables between tests
- Use function-scoped fixtures by default

### Risk: Subprocess Timeout

**Mitigation:**
- Set appropriate timeout (30s for build operations)
- Handle timeout exceptions gracefully
- Log timeout errors for debugging

---

## Rollback Plan

If tests reveal fundamental issues with the implementation approach:

1. **Revert to baseline:** All scenarios marked @skip
2. **Identify root cause:** Analyze failing test patterns
3. **Revise approach:** Update implementation strategy
4. **Incremental re-enable:** One scenario at a time

---

## Success Criteria

### Minimum Viable Product (MVP)

- [ ] AC-01: Pre-flight checks run first
- [ ] AC-02: Virtual environment is required
- [ ] AC-04: Terminal errors are readable

### Full Feature Complete

- [ ] All 44 scenarios passing
- [ ] All 10 ACs validated
- [ ] Documentation accurate
- [ ] Cross-platform tested
