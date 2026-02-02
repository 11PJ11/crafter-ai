# DES Hook Enforcement - DISTILL Wave Deliverables

## Overview

This directory contains the acceptance test suite for the **des-hook-enforcement** feature, implementing BDD/ATDD methodology with Outside-In TDD workflow.

## Feature Summary

**Problem**: DES hooks are purely advisory — no proof they fire, no enforcement, easily bypassed.

**Solution**: Non-bypassable hooks with tamper-evident audit proof of every execution via Claude Code native hook integration.

## Deliverables

### 1. acceptance-tests.feature
Gherkin scenarios covering all 7 roadmap steps:
- **Step 00-01**: Walking skeleton proving hook firing end-to-end
- **Step 01-01**: Hook audit event type definitions
- **Step 01-02**: Pre-task rejection audit logging
- **Step 01-03**: SubagentStop post-execution audit logging
- **Step 02-01**: DES configuration infrastructure
- **Step 02-02**: Claude Code hook adapter implementation
- **Step 03-01**: Hook installer/uninstaller lifecycle

**Total Scenarios**: 27 comprehensive acceptance tests

### 2. step_definitions.py
pytest-bdd step implementations following hexagonal architecture:
- **Entry Points Used**: DESOrchestrator, hook adapter CLI, installer CLI
- **Internal Components**: Accessed ONLY through entry points
- **Implementation Strategy**: First scenario enabled, all others marked `@pytest.mark.skip`
- **Production Service Integration**: All step methods call production services (no mocks)

### 3. conftest.py
pytest fixtures for test setup and isolation:
- **FakeTimeProvider**: Deterministic timestamp testing
- **AuditLogReader**: Audit log verification helper
- **Temporary Environment**: Isolated home directory, config files, audit logs
- **CLI Runner**: Helper for invoking adapter and installer CLIs
- **Test Data Builders**: Step files (complete/incomplete), task JSON (valid/invalid)

### 4. test-scenarios.md
Plain English descriptions of all test scenarios:
- Business value statements for each scenario
- Given-When-Then explanations
- Success criteria
- Test execution strategy
- Implementation readiness checklist

## Test Execution

### Run All Tests (Most Will Skip)
```bash
cd /mnt/c/Repositories/Projects/ai-craft
pytest docs/feature/des-hook-enforcement/distill/step_definitions.py -v
```

### Run First Scenario Only
```bash
pytest docs/feature/des-hook-enforcement/distill/step_definitions.py::test_stub_hook_adapter_executes -v
```

### Expected Initial State
- **First scenario**: `test_stub_hook_adapter_executes` — ENABLED (will fail until implemented)
- **All other scenarios**: Marked `@pytest.mark.skip("Not implemented yet")`

## Outside-In TDD Workflow

### Double-Loop TDD Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ OUTER LOOP: Acceptance Tests (Business View)                               │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │ INNER LOOP: Unit Tests (Developer View)                              │  │
│  │  🔴 RED → 🟢 GREEN → 🔵 REFACTOR                                      │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Implementation Process

1. **RED**: Run first acceptance test → Fails (not implemented)
2. **Step Down**: Write unit tests for required components
3. **GREEN**: Implement minimal code to pass unit tests
4. **REFACTOR**: Improve code while keeping tests green
5. **Step Up**: Return to acceptance test → Verify it passes
6. **COMMIT**: Commit working implementation
7. **NEXT**: Remove `@skip` from next scenario and repeat

### One-at-a-Time Strategy

**Purpose**: Prevent commit blocks from multiple failing E2E tests

**Workflow**:
1. Enable ONE scenario (remove `@pytest.mark.skip`)
2. Implement through Outside-In TDD until scenario passes
3. Commit working implementation (all tests green)
4. Enable NEXT scenario
5. Repeat until all scenarios implemented

## Hexagonal Architecture Compliance

### CRITICAL: Entry Points Only

**Driving Ports (USE THESE)**:
- `DESOrchestrator` — System entry point for task validation
- `claude_code_hook_adapter.py` — Hook adapter CLI
- `install_des_hooks.py` — Installer/uninstaller CLI

**Internal Components (DO NOT IMPORT DIRECTLY)**:
- `DESConfig` — Accessed through adapter
- `AuditLogger` — Accessed through orchestrator
- `TemplateValidator` — Internal component

**Validation Rule**: Tests MUST invoke through entry points, NOT internal components.

### Example: CORRECT Test

```python
from des.application.orchestrator import DESOrchestrator  # ENTRY POINT ✅

def test_hook_fires_and_logs():
    orchestrator = DESOrchestrator()  # System entry point
    result = orchestrator.validate_prompt("/nw:execute", "step-01-01.json")
    # Verify audit log contains HOOK_PRE_TASK_PASSED
```

### Example: WRONG Test

```python
from des.adapters.driven.config.des_config import DESConfig  # WRONG ❌

def test_config_loads():
    config = DESConfig()  # Direct instantiation of internal component
```

## Quality Gates

### MANDATORY Requirements

- [x] All 7 roadmap steps have corresponding acceptance scenarios
- [x] Step definitions import entry points (DESOrchestrator, CLI adapters)
- [x] All scenarios use Given-When-Then format
- [x] First scenario enabled, all others marked `@pytest.mark.skip`
- [x] Step definitions call production services (no mocks for entry points)
- [x] Tests verify observable behavior (audit log, exit codes, file state)
- [x] Timestamps verified via TimeProvider (FakeTimeProvider fixture)
- [x] Cross-platform compatibility (Python only, no shell scripts)

### Acceptance Criteria Coverage

**Happy Paths**: Valid task allowed, successful validation, clean install/uninstall
**Error Paths**: Invalid task blocked, validation failures, fail-closed errors
**Edge Cases**: Missing config, invalid JSON, idempotent install, cross-platform

## Handoff to DEVELOP Wave

### Deliverables for software-crafter

1. **acceptance-tests.feature** — Executable specifications
2. **step_definitions.py** — Step implementations with entry point integration
3. **conftest.py** — Test fixtures and helpers
4. **test-scenarios.md** — Plain English descriptions

### Implementation Guidance

**Entry Points**:
- Use `DESOrchestrator` for system-level behavior
- Use CLI scripts for adapter and installer testing
- Access internal components ONLY through entry points

**Test-Driven Workflow**:
- Start with first acceptance test (walking skeleton)
- Implement through Outside-In TDD
- Natural test progression: RED → Implementation → GREEN
- Commit when scenario passes
- Enable next scenario

**Production Service Integration**:
- All step methods call real production services
- FakeTimeProvider for deterministic timestamps
- Test data builders for realistic scenarios

**Quality Focus**:
- Business language throughout
- Observable outcomes (audit log entries, exit codes)
- Cross-platform compatibility (Python, no shell)
- Fail-closed behavior (cannot validate = cannot proceed)

## Success Metrics

### Test Coverage
- **27 scenarios** covering all roadmap steps
- **Happy paths**: 12 scenarios
- **Error paths**: 10 scenarios
- **Edge cases**: 5 scenarios

### Architecture Compliance
- ✅ Entry points enforced (DESOrchestrator, CLI adapters)
- ✅ No internal component imports in tests
- ✅ Production service integration patterns established

### ATDD Methodology
- ✅ Given-When-Then format for all scenarios
- ✅ Business language (no technical jargon)
- ✅ One-at-a-time implementation strategy
- ✅ Outside-In TDD workflow enabled

## Next Steps

1. **software-crafter** receives this handoff
2. Run first acceptance test → Observe RED state
3. Implement stub hook adapter (walking skeleton)
4. Verify first scenario passes → GREEN state
5. Commit working implementation
6. Remove `@skip` from next scenario
7. Repeat Outside-In TDD cycle

---

**DISTILL Wave Status**: ✅ COMPLETE

**Ready for DEVELOP Wave**: ✅ YES

**Acceptance Test Framework**: ✅ OPERATIONAL
