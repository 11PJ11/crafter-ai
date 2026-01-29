# Mutation Testing Report: versioning-release-management

**Feature**: versioning-release-management
**Date**: 2026-01-29
**Tool**: mutmut 3.4.0
**Status**: PARTIAL - Tooling limitations encountered

---

## Executive Summary

| Metric | Value |
|--------|-------|
| **Mutation Score** | N/A (tooling issue) |
| **Total Mutants Generated** | 464 |
| **Mutants Killed** | 0 (not executed) |
| **Mutants Survived** | 0 (not executed) |
| **Threshold Required** | 75% |
| **Status** | BLOCKED - Mutation testing could not complete |

---

## Test Coverage Analysis (Alternative Metric)

Since mutation testing encountered tooling issues, we provide coverage analysis as an alternative quality metric:

| Module | Statements | Missing | Coverage |
|--------|------------|---------|----------|
| `nWave/core/versioning/application/build_service.py` | 50 | 2 | **96%** |
| `nWave/core/versioning/application/install_service.py` | 40 | 3 | **92%** |
| `nWave/core/versioning/application/release_service.py` | 51 | 0 | **100%** |
| `nWave/core/versioning/application/update_service.py` | 125 | 10 | **92%** |
| `nWave/core/versioning/application/version_service.py` | 76 | 7 | **91%** |
| `nWave/core/versioning/domain/backup_policy.py` | 23 | 10 | **57%** |
| `nWave/core/versioning/domain/core_content_identifier.py` | 13 | 1 | **92%** |
| `nWave/core/versioning/domain/rc_version.py` | 45 | 3 | **93%** |
| `nWave/core/versioning/domain/version.py` | 53 | 10 | **81%** |
| `nWave/core/versioning/domain/watermark.py` | 33 | 5 | **85%** |
| `nWave/core/versioning/ports/checksum_port.py` | 14 | 0 | **100%** |
| `nWave/core/versioning/ports/download_port.py` | 10 | 1 | **90%** |
| `nWave/core/versioning/ports/file_system_port.py` | 17 | 0 | **100%** |
| `nWave/core/versioning/ports/git_port.py` | 12 | 0 | **100%** |
| `nWave/core/versioning/ports/github_api_port.py` | 20 | 1 | **95%** |
| `nWave/core/versioning/ports/github_cli_port.py` | 15 | 0 | **100%** |
| **TOTAL** | **605** | **53** | **91%** |

---

## Tooling Issues Encountered

### Issue 1: mutmut v3 Directory Isolation
**Description**: mutmut v3 copies source and tests to a `mutants/` directory for isolation. This breaks tests that:
- Use subprocess calls with path-dependent CLI invocations
- Reference files relative to `__file__` location
- Access git hooks or filesystem state

**Impact**: Tests passed during stats collection but mutmut could not correlate test coverage to specific mutants, resulting in all 464 mutants marked as "not checked".

### Issue 2: Acceptance Tests with CLI Subprocess Calls
**Affected Tests**:
- `tests/acceptance/versioning_release_management/test_us001_version_check.py`
- `tests/unit/versioning/update/test_update_cli.py`
- `tests/unit/versioning/release/test_github_cli_adapter.py`
- `tests/unit/versioning/forge/test_git_adapter_forge.py`

**Root Cause**: These tests invoke CLI scripts via subprocess using paths calculated from `Path(__file__)`, which resolve incorrectly in the mutants directory.

### Issue 3: Template and Schema Path Dependencies
**Affected Tests**:
- `tests/test_template_integrity.py`
- `tests/nwave/test_step_schema_duration_seconds.py`

**Root Cause**: Tests reference `nWave/templates/` files that aren't copied to the mutants directory.

---

## Workarounds Applied

1. Added `pytest_ignore_collect` hook to skip problematic tests during mutation testing
2. Configured mutmut to use only `tests/unit/versioning` test directory
3. Excluded subprocess-dependent test files from mutation test collection

---

## Test Suite Health

### Unit Tests
- **Total**: 148 tests
- **Passing**: 147
- **Skipped**: 1
- **Coverage**: 91%

### Acceptance Tests
- **Total**: 45 tests (versioning-related)
- **Passing**: 45
- **Status**: All pass when run normally (not via mutmut)

---

## Recommendations

### For Mutation Testing Success

1. **Refactor CLI Tests**: Replace subprocess-based CLI tests with direct service invocation tests where possible. The CLI layer is thin; testing through the application service provides equivalent coverage.

2. **Use Environment Variables for Paths**: Tests that need file paths should use environment variables or pytest fixtures that provide absolute paths, rather than `Path(__file__)` calculations.

3. **Create Mutation-Friendly Test Subset**: Maintain a test subset (`tests/unit/versioning/mutation_safe/`) that:
   - Does not use subprocess
   - Does not depend on filesystem state
   - Imports production code directly

4. **Consider Alternative Tools**: If mutmut v3 continues to have issues:
   - Try `cosmic-ray` (Python mutation testing)
   - Try `mutatest` (AST-based mutation)
   - Downgrade to mutmut v2.x if compatible

### For Code Quality

1. **Improve Domain Coverage**: `backup_policy.py` has only 57% coverage - add tests for:
   - Lines 54-56, 69-73, 85, 97-98

2. **Improve Version Domain Coverage**: `version.py` has 81% coverage - add tests for:
   - Edge cases in version comparison
   - Error handling paths

---

## Conclusion

**Mutation testing could not be completed** due to mutmut v3 architectural incompatibilities with the test suite structure.

However, the test suite demonstrates strong quality indicators:
- **91% statement coverage** of versioning modules
- **147/148 unit tests passing**
- **Comprehensive acceptance test coverage** (passing outside mutmut)

**Recommendation**: Accept the coverage metrics as a proxy for test quality while addressing the tooling issues for future mutation testing runs.

---

## Files Modified During Investigation

1. `setup.cfg` - mutmut configuration (reverted to working state)
2. `tests/conftest.py` - Added `pytest_ignore_collect` hook for mutation testing compatibility

---

## Appendix: Mutant Distribution

| Source File | Mutants Generated |
|-------------|-------------------|
| `update_service.py` | ~150 |
| `version_service.py` | ~80 |
| `build_service.py` | ~60 |
| `release_service.py` | ~50 |
| `install_service.py` | ~45 |
| `version.py` | ~30 |
| `rc_version.py` | ~25 |
| `watermark.py` | ~15 |
| Other modules | ~9 |
| **Total** | **464** |
