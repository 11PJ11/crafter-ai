# Acceptance Test Plan: modern_CLI_installer

**Epic**: modern_CLI_installer
**Wave**: DISTILL
**Designer**: Quinn (Acceptance Designer)
**Date**: 2026-02-01
**Status**: READY FOR DEVELOP

---

## 1. Executive Summary

This document defines the E2E acceptance test strategy for the modern_CLI_installer epic. Tests are designed to read like a book, using pytest-bdd with Given-When-Then scenarios that non-technical stakeholders can understand.

**Test Framework Stack**:
- pytest-bdd >= 7.0.0 (Gherkin scenarios)
- pytest-describe / pytest-describe-it (Readable describe blocks)
- pytest-pspec (Spec-style output)
- pytest-mock (Mocking ports/adapters)
- pytest-cov >= 4.0.0 (Coverage reporting)

**Architecture Pattern**: Hexagonal Architecture with Port/Adapter mocking at boundaries.

---

## 2. Test Coverage Matrix

### 2.1 Journey 1: forge:build-local-candidate

| Story ID | Story Name | Priority | Scenarios | Status |
|----------|------------|----------|-----------|--------|
| US-010 | Build Pre-flight Validation | P0 | 3 | Covered |
| US-011 | Conventional Commits Version Bumping | P0 | 3 | Covered |
| US-012 | Wheel Build Process | P0 | 3 | Covered |
| US-013 | Wheel Content Validation | P0 | 3 | Covered |
| US-014 | Build Success Summary | P0 | 2 | Covered |
| US-015 | Local Install Prompt | P1 | 2 | Covered |
| US-016 | Force Version Override | P1 | 2 | Covered |
| US-017 | Daily Build Sequence Tracking | P1 | 3 | Covered |
| US-018 | CI Mode Build Support | P1 | 3 | Covered |
| US-019 | Auto-repair Missing Build Dependencies | P1 | 2 | Covered |

### 2.2 Journey 2: forge:install-local-candidate

| Story ID | Story Name | Priority | Scenarios | Status |
|----------|------------|----------|-----------|--------|
| US-020 | Install Pre-flight Validation | P0 | 3 | Covered |
| US-021 | Release Readiness Validation | P0 | 3 | Covered |
| US-022 | Candidate Installation via pipx | P0 | 3 | Covered |
| US-023 | Post-Install Doctor Verification | P0 | 3 | Covered |
| US-024 | Release Report Generation | P0 | 2 | Covered |
| US-025 | Auto-chain to Build on Missing Wheel | P1 | 2 | Covered |
| US-026 | Multiple Wheel Selection | P1 | 3 | Covered |
| US-027 | CI Mode Install Support | P1 | 3 | Covered |
| US-028 | JSON Output for CI/CD | P1 | 2 | Covered |
| US-029 | Strict Mode for Release Validation | P2 | 2 | Covered |

### 2.3 Journey 3: install-nwave (PyPI)

| Story ID | Story Name | Priority | Scenarios | Status |
|----------|------------|----------|-----------|--------|
| US-030 | PyPI Download and Dependencies | P0 | 2 | Covered |
| US-031 | Install Path Resolution | P0 | 3 | Covered |
| US-032 | Framework Installation with Progress | P0 | 2 | Covered |
| US-033 | Doctor Verification for PyPI Install | P0 | 2 | Covered |
| US-034 | Welcome and Celebration Display | P0 | 2 | Covered |
| US-035 | Restart Claude Code Notification | P0 | 2 | Covered |
| US-036 | Verification in Claude Code | P0 | 2 | Covered |
| US-037 | Custom Install Path via Environment | P1 | 1 | Covered |
| US-038 | CI Mode for PyPI Install | P1 | 2 | Covered |
| US-039 | Backup Creation Before Install | P1 | 2 | Covered |

### 2.4 Cross-Cutting Stories

| Story ID | Story Name | Priority | Scenarios | Status |
|----------|------------|----------|-----------|--------|
| US-040 | Rollback on Installation Failure | P0 | 4 | Covered |
| US-041 | Upgrade Detection and Handling | P0 | 5 | Covered |

---

## 3. Test Architecture

### 3.1 Hexagonal Architecture Testing Pattern

```
+------------------------------------------------------------------+
|                      ACCEPTANCE TESTS                              |
|  pytest-bdd scenarios calling Application Services                 |
+------------------------------------------------------------------+
                              |
                              | Inject Mock Ports
                              v
+------------------------------------------------------------------+
|                    APPLICATION SERVICES                            |
|  PreflightService, BuildService, InstallService, DoctorService    |
|  (Real implementations under test)                                 |
+------------------------------------------------------------------+
                              |
                              | Port Interfaces
                              v
+------------------------------------------------------------------+
|                      MOCK ADAPTERS                                 |
|  MockFileSystemPort, MockGitPort, MockPipxPort, MockBuildPort     |
|  (Controlled behavior for deterministic testing)                   |
+------------------------------------------------------------------+
```

### 3.2 Mock Strategy

**What We Mock (Port Boundaries)**:
- FileSystemPort: File operations, directory creation, file counts
- GitPort: Branch name, commit history, tags
- PipxPort: Install, uninstall, list packages
- BuildPort: Wheel building, dist cleaning
- ConfigPort: Environment variables, config file loading
- BackupPort: Backup creation, restoration

**What We Do NOT Mock**:
- Application Services (BuildService, InstallService, DoctorService)
- Domain Objects (CandidateVersion, CheckResult, HealthStatus)
- Service orchestration logic

### 3.3 Test Data Registry

All tests use standardized values from the shared artifacts registry:

```python
# Standardized test data
TEST_DATA = {
    "version": "1.3.0",
    "candidate_version": "1.3.0-dev-20260201-001",
    "wheel_path": "dist/nwave-1.3.0-dev-20260201-001-py3-none-any.whl",
    "install_path": "~/.claude/agents/nw/",
    "agent_count": 47,
    "command_count": 23,
    "template_count": 12,
    "date": "20260201",
    "sequence": "001",
    "python_version": "3.12.1",
    "build_version": "1.2.1",
    "pipx_version": "1.4.3",
}
```

---

## 4. Test Organization

### 4.1 Directory Structure

```
03-distill/
|-- acceptance-test-plan.md          # This document
|-- e2e-scenarios/
|   |-- conftest.py                  # Shared fixtures, step definitions
|   |-- test_journey_1_build.py      # Journey 1 pytest-bdd tests
|   |-- test_journey_2_install.py    # Journey 2 pytest-bdd tests
|   |-- test_journey_3_pypi.py       # Journey 3 pytest-bdd tests
|-- features/
|   |-- journey_1_build.feature      # Refined Gherkin scenarios
|   |-- journey_2_install.feature    # Refined Gherkin scenarios
|   |-- journey_3_pypi.feature       # Refined Gherkin scenarios
|-- fixtures/
    |-- mock_filesystem.py           # FileSystemPort mock
    |-- mock_git.py                  # GitPort mock
    |-- mock_pipx.py                 # PipxPort mock
    |-- mock_build.py                # BuildPort mock
    |-- test_data.py                 # Shared test data from registry
```

### 4.2 Feature File Organization

Each feature file is organized by:
1. **Background**: Common setup for all scenarios
2. **Happy Path**: Primary successful flow (P0)
3. **Pre-flight Checks**: Environment validation scenarios
4. **Error Scenarios**: Fixable and blocking errors
5. **CI/CD Mode**: Non-interactive scenarios
6. **Cross-Journey Integration**: Handoff validation

---

## 5. Test Execution Strategy

### 5.1 One E2E Test at a Time

Following Outside-In TDD, enable one scenario at a time:

```python
# Initially all scenarios marked as @wip
@pytest.mark.skip(reason="Enable one at a time for Outside-In TDD")
def test_scenario_name():
    pass

# Enable single scenario when ready to implement
# Remove skip marker and implement production code
```

### 5.2 Test Execution Commands

```bash
# Run all acceptance tests
pytest docs/features/modern-cli-installer/03-distill/e2e-scenarios/ -v

# Run with pspec format for readability
pytest docs/features/modern-cli-installer/03-distill/e2e-scenarios/ --pspec

# Run specific journey
pytest docs/features/modern-cli-installer/03-distill/e2e-scenarios/test_journey_1_build.py -v

# Run by story ID tag
pytest -m "US_010" -v

# Run with coverage
pytest docs/features/modern-cli-installer/03-distill/e2e-scenarios/ --cov=nWave --cov-report=html
```

### 5.3 CI/CD Integration

```yaml
# Example GitHub Actions workflow
acceptance-tests:
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v4
    - name: Set up Python
      uses: actions/setup-python@v5
      with:
        python-version: '3.12'
    - name: Install dependencies
      run: pipenv install --dev
    - name: Run acceptance tests
      run: pytest docs/features/modern-cli-installer/03-distill/e2e-scenarios/ --pspec --tb=short
```

---

## 6. Scenario Tagging Convention

| Tag | Purpose | Example |
|-----|---------|---------|
| @US_NNN | Traces to user story | @US_010 |
| @P0, @P1, @P2 | Priority level | @P0 |
| @happy_path | Primary successful flow | @happy_path |
| @error | Error handling scenarios | @error |
| @fixable | Auto-repairable issues | @fixable |
| @blocking | Fatal errors | @blocking |
| @ci | CI/CD mode scenarios | @ci |
| @integration | Cross-journey tests | @integration |
| @wip | Work in progress | @wip |

---

## 7. Handoff Requirements for DEVELOP Wave

### 7.1 Pre-conditions for Software Crafter

1. All feature files syntactically valid Gherkin
2. Step definitions scaffolded with NotImplementedError
3. Mock fixtures implemented with controlled behavior
4. Test data module with standardized values
5. conftest.py with dependency injection setup

### 7.2 Implementation Order

The software crafter should implement in this order:

**Phase 1: Infrastructure (US-001 to US-005)**
- Shared pre-flight check framework
- Shared doctor health check framework
- Shared artifacts registry

**Phase 2: Journey 1 - Build (US-010 to US-019)**
- Enable one scenario at a time
- Implement through Outside-In TDD
- Commit when scenario passes

**Phase 3: Journey 2 - Install Local (US-020 to US-029)**
- Depends on Journey 1 wheel output
- Enable scenarios sequentially

**Phase 4: Journey 3 - PyPI Install (US-030 to US-039)**
- Can run in parallel after infrastructure
- Shares doctor patterns with Journey 2

**Phase 5: Cross-Cutting (US-040 to US-041)**
- Rollback and upgrade detection
- Applies to all journeys

---

## 8. Quality Gates

### 8.1 DISTILL Wave Completion Criteria

- [x] All 37 user stories have corresponding acceptance scenarios
- [x] Scenarios written in business language (no technical jargon)
- [x] Given-When-Then format consistently applied
- [x] Traceability: Every scenario tagged with story ID
- [x] Mock strategy aligned with hexagonal architecture
- [x] Test data uses standardized artifact values

### 8.2 Ready for Outside-In TDD

- [x] Feature files are executable specifications
- [x] Step definitions scaffolded (will raise NotImplementedError)
- [x] Fixtures prepared for port mocking
- [x] Test execution infrastructure ready

---

## 9. References

- User Stories: `/docs/features/modern-cli-installer/01-discuss/user-stories.md`
- Architecture Design: `/docs/features/modern-cli-installer/02-design/architecture-design.md`
- Component Boundaries: `/docs/features/modern-cli-installer/02-design/component-boundaries.md`
- UX Journeys: `/docs/ux/modern-cli-installer/journey-*.feature`
- Shared Artifacts: `/docs/ux/modern-cli-installer/shared-artifacts-registry-installer.md`

---

*Acceptance Test Plan maintained by Quinn (Acceptance Designer) for DISTILL wave of modern_CLI_installer epic.*
