# DES Acceptance Tests

E2E acceptance tests for the Deterministic Execution System (DES), following Outside-In TDD principles.

## Purpose

These tests validate DES business requirements from the **DISCUSS** wave and drive implementation in the **DEVELOP** wave through the Outside-In TDD approach.

## Test Structure

```
tests/acceptance/
├── conftest.py                      # Shared pytest fixtures
├── test_us001_command_filtering.py  # US-001: Command-origin filtering
├── test_us002_preinvocation.py      # US-002: Pre-invocation validation (future)
├── test_us003_postexecution.py      # US-003: Post-execution validation (future)
└── README.md                        # This file
```

## Running Tests

### Run All Acceptance Tests
```bash
pytest tests/acceptance/
```

### Run Specific Test File
```bash
pytest tests/acceptance/test_us001_command_filtering.py
```

### Run Single Test
```bash
pytest tests/acceptance/test_us001_command_filtering.py::TestCommandOriginFiltering::test_execute_command_includes_des_validation_marker
```

### Verbose Output
```bash
pytest tests/acceptance/ -v
```

## Current Status

### ✅ Test Files Created

- **test_us001_command_filtering.py** - Command-origin filtering (US-001)
  - 4 test scenarios covering execute, ad-hoc, research, develop commands
  - Tests WILL FAIL initially (no implementation yet - expected!)

### ⏳ Implementation Pending

- **des_orchestrator fixture** - Currently returns `NotImplemented`
- **DES marker injection** - Orchestrator prompt rendering logic
- **Command filtering logic** - Distinguish command vs ad-hoc invocations

### 📋 Next Tests (One at a Time)

Per Outside-In TDD, we implement **ONE E2E test at a time**:

1. **US-001** (Current) - Command-origin filtering
2. **US-002** (Next) - Pre-invocation template validation
3. **US-003** - Post-execution state validation
4. **US-004** - Audit trail logging

## Test Philosophy

### Outside-In TDD Principles

1. **Start with acceptance test** (RED) - Defines "done" from business perspective
2. **Step down to unit tests** (inner loop) - Drive implementation details
3. **Return to acceptance test** (GREEN) - Verify business requirement satisfied
4. **ONE test at a time** - No multiple failing E2E tests blocking commits

### Business-Focused Tests

- **Given-When-Then structure** - Clear business scenarios
- **Domain language** - Uses Marcus, Priya, Alex personas
- **Business value** - Each test documents WHY it matters
- **No implementation details** - Tests validate behavior, not code structure

### Expected Test Lifecycle

```
┌─────────────────────────────────────────┐
│ DISTILL Wave (Now)                      │
│ - Create acceptance test (FAILING)      │
│ - Test documents business requirement   │
└─────────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────────┐
│ DEVELOP Wave (Next)                     │
│ - Implement via Outside-In TDD          │
│ - Unit tests drive implementation       │
│ - Acceptance test turns GREEN naturally │
└─────────────────────────────────────────┘
```

## Test Scenarios by User Story

### US-001: Command-Origin Filtering (Priority: P0 - Must Have)

**Persona**: Marcus (Senior Developer)

**Business Value**: Separation between production work (validated) and exploration (fast)

**Test Scenarios**:
1. ✅ Execute command includes DES validation marker
2. ✅ Ad-hoc Task bypasses DES validation
3. ✅ Research command skips full validation
4. ✅ Develop command includes DES validation marker

**Source Documents**:
- User Story: `docs/feature/des/discuss/user-stories.md` (US-001)
- Acceptance Criteria: `docs/feature/des/discuss/acceptance-criteria.md` (Scenarios 1-3)
- Architecture: `docs/feature/des/design/architecture-design.md` (Section 4.1)

## Fixtures

### `tmp_project_root`
Creates temporary DES directory structure for test isolation.

**Provides**:
- `steps/` - Step file directory
- `templates/prompt-templates/` - Template directory
- `audit/` - Audit log directory

### `minimal_step_file`
Creates a minimal valid step file with 14-phase TDD cycle structure.

**Returns**: Path to created step file

### `des_orchestrator`
Mock DES orchestrator for testing command execution flow.

**Status**: Currently `NotImplemented` - will be implemented in DEVELOP wave

## Architecture Context

Tests validate the 4-layer DES architecture:

```
Layer 1: Command-Origin Filtering  ← US-001 tests this layer
Layer 2: Prompt Template Engine    ← US-002 tests this layer
Layer 3: Execution Lifecycle       ← US-003, US-006 test this layer
Layer 4: Validation Gates          ← US-002, US-003, US-004 test these gates
```

## Success Criteria

### DISTILL Wave Complete When:
- ✅ First acceptance test created (US-001)
- ✅ Test is executable (`pytest tests/acceptance/test_us001_command_filtering.py`)
- ✅ Test FAILS initially (no implementation - expected!)
- ✅ Test clearly documents Given-When-Then
- ✅ Test validates AC-001.1 from requirements
- ✅ conftest.py provides necessary fixtures
- ✅ README documents test philosophy and execution

### DEVELOP Wave Complete When:
- ⏳ Implement `des_orchestrator` fixture with real orchestration logic
- ⏳ All US-001 tests pass (GREEN)
- ⏳ No skipped tests in execution
- ⏳ Implementation satisfies business requirements

## References

- **DISCUSS Wave Deliverables**: `/mnt/c/Repositories/Projects/ai-craft/docs/feature/des/discuss/`
  - `requirements.md` - Functional and non-functional requirements
  - `user-stories.md` - 12 user stories with personas and story points
  - `acceptance-criteria.md` - 33 Given-When-Then scenarios

- **DESIGN Wave Deliverables**: `/mnt/c/Repositories/Projects/ai-craft/docs/feature/des/design/`
  - `architecture-design.md` v1.6.0 - Production-ready architecture
  - `component-boundaries.md` - Validation gate specifications
  - `data-models.md` - Step file and audit log schemas

## Outside-In TDD Resources

- **BDD Methodology**: `nWave/data/embed/acceptance-designer/bdd-methodology.md`
- **ATDD Patterns**: `nWave/data/methodologies/atdd-patterns.md`
- **Outside-In TDD Reference**: `nWave/data/methodologies/outside-in-tdd-reference.md`
