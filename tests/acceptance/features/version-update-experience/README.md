# Version Update Experience - Acceptance Tests

## Overview

Comprehensive acceptance tests for the nWave Version Update Experience feature, following Outside-In TDD principles with strict hexagonal architecture boundary enforcement.

**Framework:** pytest-bdd (Python)
**Methodology:** Acceptance Test Driven Development (ATDD)
**Architecture:** Hexagonal (Ports & Adapters)

---

## 🎯 Critical Principle: Hexagonal Boundary Enforcement

### ✅ CORRECT: Test Through Driving Ports

```python
# CORRECT: Invoke through CLI entry point (driving port)
result = subprocess.run(
    ["python3", "~/.claude/nWave/cli/version_cli.py"],
    capture_output=True
)
```

### ❌ FORBIDDEN: Direct Component Access

```python
# WRONG: Direct import of internal components
from nWave.core.version_manager import VersionManager  # ❌ FORBIDDEN
from nWave.core.update_orchestrator import UpdateOrchestrator  # ❌ FORBIDDEN

version_manager = VersionManager()  # ❌ VIOLATES HEXAGONAL BOUNDARY
```

**Driving Ports (System Entry Points):**
- `~/.claude/nWave/cli/version_cli.py` - Version check command
- `~/.claude/nWave/cli/update_cli.py` - Update command

**Tests invoke ONLY these entry points, never internal components.**

---

## 📁 Structure

```
tests/acceptance/features/version-update-experience/
├── README.md                          # This file
├── pytest.ini                         # pytest configuration
├── conftest.py                        # Shared fixtures and configuration
│
├── Feature Files (Gherkin)
│   ├── us-001-check-version.feature        # US-001: Version check (3 scenarios)
│   ├── us-002-update-safely.feature        # US-002: Safe update (6 scenarios)
│   ├── us-003-breaking-changes.feature     # US-003: Breaking warnings (2 scenarios)
│   ├── us-004-backup-cleanup.feature       # US-004: Backup retention (4 scenarios)
│   ├── us-005-commit-enforcement.feature   # US-005: Conventional commits (4 scenarios)
│   ├── us-006-prepush-validation.feature   # US-006: Pre-push hooks (2 scenarios)
│   └── us-007-changelog-generation.feature # US-007: Changelog automation (2 scenarios)
│
└── Step Definitions (Python)
    ├── test_version_steps.py          # US-001, US-003 (version check)
    ├── test_update_steps.py           # US-002, US-004 (update workflow)
    └── test_git_workflow_steps.py     # US-005, US-006, US-007 (git/CI/CD)
```

---

## 🚀 Running Tests

### Run All Acceptance Tests

```bash
cd tests/acceptance/features/version-update-experience
pytest -v
```

### Run Specific User Story

```bash
# US-001: Version check
pytest -v -k "us-001"

# US-002: Update safely
pytest -v -k "us-002"
```

### Run Specific Scenario

```bash
pytest -v -k "Display installed version when up to date"
```

### Run with Detailed Output

```bash
pytest -vv --tb=long --showlocals
```

### Run Only Active Scenarios (Skip Unimplemented)

```bash
pytest -v -m "not skip"
```

---

## 📊 Test Coverage

| User Story | Scenarios | Status | Notes |
|------------|-----------|--------|-------|
| **US-001** | 3 | **1 Active**, 2 Skipped | Version check (first scenario executable) |
| **US-002** | 6 | All Skipped | Update workflow (implement after US-001) |
| **US-003** | 2 | All Skipped | Breaking changes (implement after US-001) |
| **US-004** | 4 | All Skipped | Backup cleanup (implement after US-002) |
| **US-005** | 4 | All Skipped | Commit enforcement (git hooks) |
| **US-006** | 2 | All Skipped | Pre-push validation (git hooks) |
| **US-007** | 2 | All Skipped | Changelog generation (CI/CD) |
| **TOTAL** | **23** | **1 Active** | One-at-a-time strategy |

---

## 🔄 One-at-a-Time Implementation Strategy

### Current Status

**Active Scenario:**
- ✅ `US-001: Display installed version when up to date`

**All Other Scenarios:**
- ⏸️ Marked with `@pytest.mark.skip(reason="Not implemented yet")`

### Implementation Workflow

1. **Implement US-001, Scenario 1** (Currently Active)
   - Write failing acceptance test ✅ (DONE)
   - Implement through Outside-In TDD
   - Create production service implementations
   - All tests pass → Commit

2. **Enable US-001, Scenario 2**
   - Remove `@pytest.mark.skip` from next scenario
   - Implement through Outside-In TDD
   - All tests pass → Commit

3. **Continue Sequentially**
   - Complete all US-001 scenarios
   - Move to US-002 scenarios
   - Repeat until all 23 scenarios implemented

### Removing Skip Markers

**Before enabling next scenario:**
```python
# Current state
@pytest.mark.skip(reason="Not implemented yet - will enable one at a time to avoid commit blocks")
Scenario: Display installed version with update available
```

**To enable:**
```python
# Remove the skip marker entirely
Scenario: Display installed version with update available
```

---

## 🧪 Test Fixtures

### Core Fixtures (conftest.py)

- **`test_installation`** - Isolated test installation directory
- **`cli_result`** - Shared CLI execution results
- **`mock_github_api`** - Mock GitHub API responses
- **`cli_environment`** - Environment variables for CLI execution
- **`git_repo`** - Temporary git repository for hook testing

### Builders

- **`version_file_builder`** - Create VERSION files with specific content
- **`backup_builder`** - Create backup directories with age simulation

### Utilities

- **`cli_executor`** - Execute CLI scripts with isolation
- **`assert_cli_output`** - Assertion helpers for CLI output
- **`performance_timer`** - Performance testing support

---

## 📝 Writing New Scenarios

### Step 1: Add Scenario to Feature File

```gherkin
Scenario: Your scenario description
  Given precondition
  When action through CLI entry point
  Then observable outcome
```

### Step 2: Implement Step Definitions

```python
@given("precondition")
def precondition_setup(test_installation):
    # Setup test environment
    pass

@when("action through CLI entry point")
def execute_action(test_installation, cli_result):
    # CRITICAL: Invoke through CLI, not direct import
    cli_script = test_installation['cli_dir'] / "version_cli.py"
    result = subprocess.run(["python3", str(cli_script)], ...)
    cli_result.update(result)

@then("observable outcome")
def verify_outcome(cli_result):
    # Assert on observable CLI behavior
    assert "expected output" in cli_result['stdout']
```

### Step 3: Mark as Skipped Until Ready

```python
@pytest.mark.skip(reason="Not implemented yet - will enable one at a time")
Scenario: Your scenario description
```

---

## 🏗️ Architecture Alignment

### Hexagonal Architecture Layers

```
┌─────────────────────────────────────────┐
│ ACCEPTANCE TESTS (This Directory)      │
│                                         │
│ ✅ Invoke CLI Entry Points ONLY        │
│ ❌ Never Import Core Domain             │
└─────────────────────────────────────────┘
                    │
                    ▼ (subprocess call)
┌─────────────────────────────────────────┐
│ DRIVING PORTS (CLI Entry Points)        │
│                                         │
│ • version_cli.py                        │
│ • update_cli.py                         │
└─────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────┐
│ CORE DOMAIN (Business Logic)            │
│                                         │
│ • VersionManager                        │
│ • UpdateDownloadOrchestrator            │
│ • ChangelogProcessor                    │
└─────────────────────────────────────────┘
```

### Test Through Observable Behavior

**What Tests Verify:**
- ✅ CLI output (stdout/stderr)
- ✅ Exit codes
- ✅ File system changes (VERSION file, backups)
- ✅ Observable side effects

**What Tests DON'T Verify:**
- ❌ Internal component state
- ❌ Private method behavior
- ❌ Implementation details

---

## 🔍 Debugging Tests

### View Test Output

```bash
# Capture print statements
pytest -v -s

# Show local variables on failure
pytest -v --showlocals

# Full traceback
pytest -v --tb=long
```

### Run Single Test with Debugging

```bash
# Add breakpoint in test
import pdb; pdb.set_trace()

# Run with pdb
pytest -v --pdb test_version_steps.py::test_scenario_name
```

### Check CLI Script Output

```bash
# Manually execute CLI script
python3 ~/.claude/nWave/cli/version_cli.py

# With test environment
NWAVE_HOME=/tmp/test python3 test-script.py
```

---

## 📚 References

### BDD & Gherkin

- [Cucumber Best Practices](https://cucumber.io/docs/bdd/)
- [pytest-bdd Documentation](https://pytest-bdd.readthedocs.io/)
- [Gherkin Syntax Reference](https://cucumber.io/docs/gherkin/reference/)

### Hexagonal Architecture

- [Hexagonal Architecture Pattern](https://alistair.cockburn.us/hexagonal-architecture/)
- [Ports and Adapters](https://herbertograca.com/2017/09/14/ports-adapters-architecture/)

### ATDD Methodology

- [Acceptance Test Driven Development](https://en.wikipedia.org/wiki/Acceptance_test-driven_development)
- [Three Amigos](https://www.agilealliance.org/glossary/three-amigos/)
- [Specification by Example](https://gojko.net/books/specification-by-example/)

---

## ✅ Quality Gates

### Before Enabling Next Scenario

- [ ] Current active scenario passes completely
- [ ] All supporting unit tests pass
- [ ] Code follows hexagonal architecture (no boundary violations)
- [ ] Production services called via dependency injection
- [ ] Committed to version control

### Before Handoff to DEVELOP Wave

- [ ] All acceptance tests created (23 scenarios total)
- [ ] First scenario of US-001 is executable (not skipped)
- [ ] All other scenarios marked with `@pytest.mark.skip`
- [ ] Step definitions call CLI entry points (driving ports)
- [ ] No direct imports of core domain components
- [ ] Test isolation verified (tests don't interfere with each other)
- [ ] Documentation complete and accurate

---

## 🚨 Common Pitfalls

### ❌ Pitfall 1: Importing Core Components

```python
# WRONG
from nWave.core.version_manager import VersionManager
version_manager = VersionManager()
```

**Fix:** Always invoke through CLI entry points via subprocess.

### ❌ Pitfall 2: Testing Implementation Details

```python
# WRONG
def test_version_manager_internal_state():
    assert version_manager._cached_version == "1.5.7"
```

**Fix:** Test observable behavior only (CLI output, exit codes, file changes).

### ❌ Pitfall 3: Multiple Active E2E Tests

```python
# WRONG - Multiple scenarios without skip markers
Scenario: Test 1
Scenario: Test 2  # Both active = commit blocked if one fails
```

**Fix:** Mark all but current scenario with `@pytest.mark.skip`.

### ❌ Pitfall 4: Hardcoded Paths

```python
# WRONG
version_file = Path("/home/user/.claude/nwave-version.txt")
```

**Fix:** Use test fixtures and isolated directories.

```python
# CORRECT
version_file = test_installation['version_file']
```

---

## 📞 Support

For questions or issues:

1. Check this README
2. Review component-boundaries.md in design documentation
3. Consult architecture-design.md for system overview
4. Ask in team Slack #nwave-development

---

**Last Updated:** 2026-01-25
**Test Framework Version:** pytest-bdd 6.1+
**Python Version:** 3.11+
