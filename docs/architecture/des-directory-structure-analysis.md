# DES Module Directory Structure Analysis
## Hexagonal Architecture Organization Guide

**Date**: 2026-01-27
**Status**: Architectural Recommendation
**Scope**: src/des/ and tests/des/ directory reorganization

---

## Executive Summary

The current DES module has mixed concerns at the root level, making it difficult to distinguish between domain logic, application services, and infrastructure adapters. This analysis evaluates two architectural organization approaches and recommends **Option B: Hexagon Layers Organization** as the optimal structure for the DES module.

**Key Finding**: The current structure lacks clear architectural layering, making it hard for new developers to understand where to place new code. The recommended structure explicitly separates concerns by architectural layer, enabling:
- **Clear code discovery** - New developers immediately understand where each concern lives
- **Maintainability** - Changes to infrastructure don't affect domain logic
- **Testing clarity** - Test organization mirrors code organization
- **Hexagonal compliance** - Structure enforces port/adapter pattern discipline

---

## Current State Analysis

### Existing Directory Structure

```
src/des/
├── orchestrator.py                 (APPLICATION LAYER - Orchestration)
├── timeout_monitor.py              (DOMAIN - Timeout Monitoring)
├── turn_counter.py                 (DOMAIN - Turn Tracking)
├── turn_config.py                  (DOMAIN/CONFIG - Configuration)
├── config_loader.py                (APPLICATION - Configuration Loading)
├── validator.py                    (APPLICATION - Validation Service)
├── invocation_limits_validator.py  (APPLICATION - Validation Service)
├── hooks.py                        (INFRASTRUCTURE - Post-Execution Hooks)
├── ports/ (6 port interfaces)
│   ├── config_port.py
│   ├── hook_port.py
│   ├── logging_port.py
│   ├── task_invocation_port.py
│   ├── filesystem_port.py
│   ├── time_provider_port.py
│   └── validator_port.py
└── adapters/ (8 concrete implementations)
    ├── real_hook.py
    ├── real_validator.py
    ├── real_filesystem.py
    ├── system_time.py
    ├── structured_logger.py
    ├── silent_logger.py
    ├── in_memory_config_adapter.py
    ├── environment_config_adapter.py
    ├── claude_code_task_adapter.py
    ├── mocked_task_adapter.py
    └── __init__.py

tests/des/
├── adapters/ (test doubles)
│   ├── mocked_hook.py
│   ├── mocked_validator.py
│   ├── mocked_time.py
│   ├── in_memory_filesystem.py
│   └── __init__.py
└── conftest.py
```

### Problem Analysis

**Architectural Clarity Issues**:
1. **Mixed Layers at Root Level**: Domain logic (turn_counter), application services (orchestrator), and infrastructure (hooks) mixed together
2. **Unclear Adapter Organization**: 8 adapters in flat list, hard to distinguish primary (driver) from secondary (driven) adapters
3. **Port/Adapter Asymmetry**: Ports in one directory, adapters elsewhere, no clear pairing
4. **Test Organization Gaps**:
   - Only test doubles in tests/des/adapters/
   - No unit tests visible
   - No integration tests
   - No clear separation between test types

**Developer Onboarding Pain Points**:
- New developer asks: "Where does a new validation checker go?"
- New developer asks: "Which adapters are production vs test?"
- New developer asks: "How do I distinguish domain logic from infrastructure?"

**Code Discovery Issues**:
- Glob pattern: `src/des/*.py` returns 8 files at root level (unclear purpose)
- No semantic grouping by responsibility
- Hard to trace hexagonal architecture boundaries

---

## Two Architectural Options

### Option A: Domain-First Organization

**Philosophy**: Organize by business domain concepts, with supporting infrastructure

```
src/des/
├── domain/
│   ├── __init__.py
│   ├── turn_management/
│   │   ├── __init__.py
│   │   ├── turn_counter.py          # Turn counting logic
│   │   └── turn_config.py           # Turn configuration
│   ├── phase_execution/
│   │   ├── __init__.py
│   │   ├── timeout_monitor.py       # Phase timeout tracking
│   │   └── invocation_limits_validator.py
│   └── orchestration/
│       ├── __init__.py
│       └── orchestrator.py          # DES orchestration logic
├── application/
│   ├── __init__.py
│   └── services/
│       ├── __init__.py
│       ├── validation_service.py    # Application validation orchestration
│       ├── step_executor.py         # Step execution service
│       └── config_loader.py         # Configuration loading
├── ports/
│   ├── __init__.py
│   ├── hook_port.py
│   ├── validator_port.py
│   ├── filesystem_port.py
│   ├── time_provider_port.py
│   ├── logging_port.py
│   ├── task_invocation_port.py
│   ├── config_port.py
│   └── __init__.py
├── adapters/
│   ├── __init__.py
│   ├── real_hook.py
│   ├── real_validator.py
│   ├── real_filesystem.py
│   ├── system_time.py
│   ├── structured_logger.py
│   ├── silent_logger.py
│   ├── environment_config_adapter.py
│   ├── in_memory_config_adapter.py
│   ├── claude_code_task_adapter.py
│   └── mocked_task_adapter.py
└── __init__.py
```

**Strengths**:
- Domain concepts explicitly grouped (turn_management, phase_execution)
- Business vocabulary in directory names
- Easier to find "where does turn logic go?"

**Weaknesses**:
- Doesn't distinguish between primary and secondary adapters
- Mixes concerns: invocation_limits_validator is really an application service, not domain
- Adapter organization still flat and unclear
- Less aligned with traditional hexagonal architecture visualization
- Port/adapter relationship not visually apparent

**Best For**:
- Teams with strong domain-driven design expertise
- Business logic is primary organizational concern
- When domain concepts are highly complex and varied

---

### Option B: Hexagon Layers Organization (RECOMMENDED)

**Philosophy**: Organize by architectural layers (outside-in), making hexagonal structure explicit

```
src/des/
├── adapters/
│   ├── __init__.py
│   ├── drivers/                     # PRIMARY ADAPTERS (inbound)
│   │   ├── __init__.py
│   │   ├── hooks/
│   │   │   ├── __init__.py
│   │   │   └── real_hook.py
│   │   └── validators/
│   │       ├── __init__.py
│   │       └── real_validator.py
│   └── driven/                      # SECONDARY ADAPTERS (outbound)
│       ├── __init__.py
│       ├── filesystem/
│       │   ├── __init__.py
│       │   └── real_filesystem.py
│       ├── time/
│       │   ├── __init__.py
│       │   └── system_time.py
│       ├── logging/
│       │   ├── __init__.py
│       │   ├── structured_logger.py
│       │   └── silent_logger.py
│       ├── config/
│       │   ├── __init__.py
│       │   ├── environment_config_adapter.py
│       │   └── in_memory_config_adapter.py
│       └── task_invocation/
│           ├── __init__.py
│           ├── claude_code_task_adapter.py
│           └── mocked_task_adapter.py
├── ports/
│   ├── __init__.py
│   ├── driver_ports/                # INBOUND PORT ABSTRACTIONS
│   │   ├── __init__.py
│   │   ├── hook_port.py
│   │   └── validator_port.py
│   └── driven_ports/                # OUTBOUND PORT ABSTRACTIONS
│       ├── __init__.py
│       ├── filesystem_port.py
│       ├── time_provider_port.py
│       ├── logging_port.py
│       ├── task_invocation_port.py
│       └── config_port.py
├── application/
│   ├── __init__.py
│   ├── orchestrator.py              # Main orchestration service
│   └── services.py                  # Supporting application services
├── domain/
│   ├── __init__.py
│   ├── turn_counter.py              # Turn tracking domain logic
│   ├── timeout_monitor.py           # Timeout tracking domain logic
│   ├── turn_config.py               # Turn configuration domain logic
│   └── invocation_limits_validator.py # Validation domain logic
└── __init__.py
```

**Strengths**:
- **Explicit Hexagonal Structure**: Clear visualization of driver/driven adapters
- **Port/Adapter Pairing**: Grouped by ports - easy to find what implements what
- **Primary vs Secondary Distinction**: drivers/ vs driven/ makes entry points clear
- **Scalability**: Easy to add new adapter types (new subdirectory in drivers/ or driven/)
- **Infrastructure Clarity**: All external integrations grouped in adapters/
- **Domain Isolation**: All domain logic at application core
- **Import Patterns Clear**:
  - Domain imports from ports
  - Application imports from domain and ports
  - Adapters import from ports
  - No circular dependencies possible

**Weaknesses**:
- Deeper directory nesting (more levels to traverse)
- More directories to create initially
- Requires discipline: developers must understand driver vs driven distinction

**Best For**:
- Clean/hexagonal architecture implementations
- Teams learning hexagonal patterns
- Systems with clear separation between inbound and outbound interfaces
- Long-lived systems requiring architectural consistency

---

## Test Directory Organization (Common to Both Options)

```
tests/des/
├── __init__.py
├── conftest.py                      # Shared fixtures and configuration
├── adapters/                        # TEST DOUBLES (shared across test types)
│   ├── __init__.py
│   ├── mocked_hook.py
│   ├── mocked_validator.py
│   ├── mocked_time.py
│   ├── mocked_filesystem.py         # Add - currently in_memory_filesystem.py
│   └── mocked_config.py             # Add - test double for config port
├── unit/                            # ISOLATED UNIT TESTS
│   ├── __init__.py
│   ├── domain/
│   │   ├── __init__.py
│   │   ├── test_turn_counter.py
│   │   ├── test_timeout_monitor.py
│   │   └── test_turn_config.py
│   ├── application/
│   │   ├── __init__.py
│   │   ├── test_orchestrator.py
│   │   └── test_services.py
│   └── ports/
│       ├── __init__.py
│       ├── test_hook_port.py        # Port interface contract tests
│       └── test_validator_port.py
├── integration/                     # COMPONENT INTERACTION TESTS
│   ├── __init__.py
│   ├── test_turn_discipline.py      # Turn counting + persistence
│   ├── test_timeout_monitoring.py   # Timeout monitor + filesystem
│   ├── test_orchestrator_integration.py
│   └── test_step_execution.py
├── acceptance/                      # END-TO-END FEATURE TESTS
│   ├── __init__.py
│   ├── test_turn_counting.py        # US-001 acceptance
│   ├── test_invocation_limits.py    # US-002 acceptance
│   ├── test_timeout_warnings.py     # US-003 acceptance
│   └── test_prompt_validation.py    # US-004 acceptance
└── e2e/                             # FULL SYSTEM SCENARIO TESTS
    ├── __init__.py
    ├── test_scenario_013_timeout_warnings.py
    └── test_scenario_014_agent_timeout_warnings.py
```

**Test Organization Philosophy**:
- **Adapters/**: Test doubles used across all test types (DRY principle)
- **Unit/**: Tests for individual components in isolation
- **Integration/**: Tests for interaction between 2-3 components
- **Acceptance/**: Tests validating user story acceptance criteria
- **E2E/**: Full-system scenario tests

**Key Principle**: Test structure mirrors src/ structure for easy navigation

---

## Comparative Analysis

### Developer Onboarding

| Scenario | Option A | Option B |
|----------|----------|----------|
| "Where do I add new validation logic?" | Look in domain/phase_execution/ (might be confused) | Look in domain/ for business logic, application/ for orchestration, adapters/drivers/ for hook logic. Clear. |
| "What's a primary adapter?" | No clear indication | drivers/ = primary adapters (entry points), driven/ = secondary (dependencies) |
| "Where's the timeout logic?" | domain/phase_execution/timeout_monitor.py (need to know the domain concept) | domain/timeout_monitor.py (flat, clear) |
| "How do adapters connect to ports?" | adapters/ and ports/ separate - need to trace imports | adapters/drivers/hooks/ implements ports/driver_ports/hook_port.py - visually paired |

**Winner**: Option B - Clearer mapping for new developers

### Code Discovery

| Query | Option A | Option B |
|-------|----------|----------|
| Find all adapters | grep -r "adapters/\*.py" | ls adapters/drivers adapters/driven (hierarchical) |
| Find filesystem implementations | search through adapters/ (flat list) | ls adapters/driven/filesystem/ (grouped by concern) |
| Find all validators | Find validator.py + search subdirs | adapters/driven/validators/ contains implementations |
| Find application services | Look in application/services/ (named clearly) | application/ contains services (clear) |

**Winner**: Option B - Hierarchical organization enables better browsing

### Maintenance Impact

| Concern | Option A | Option B |
|---------|----------|----------|
| Adding new port/adapter pair | Add port in ports/, add adapter in adapters/ | Add port in ports/driven_ports/ (or driver_ports/), add adapter in adapters/driven/ (or drivers/) - clearer |
| Refactoring domain logic | Modify domain/**/*.py files | Modify domain/ files (clear boundary) |
| Moving functionality | Domain reorganization affects imports | Option B structure is stable regardless of domain reorganization |
| Testing complex scenarios | Integration tests traverse multiple domain modules | Integration tests clearly show component interactions |

**Winner**: Option B - Structural stability and clear boundaries

### Hexagonal Architecture Alignment

| Principle | Option A | Option B |
|-----------|----------|----------|
| Clear core/hexagon | Implicit in domain/ folder | Explicit: domain + application form core |
| Port/Adapter Pairing | Separated geographically | drivers/ and driven/ group with their ports |
| Inbound vs Outbound | Not distinguished | drivers/ = inbound, driven/ = outbound |
| Dependency Inversion | Not visually apparent | Drives imports: adapters → ports → application/domain |
| Scalability | Unclear how to add new domain concepts | Clear: add new subdir in drivers/ or driven/ |

**Winner**: Option B - Explicitly enforces hexagonal principles

---

## Recommendation: Option B (Hexagon Layers Organization)

### Justification

1. **Architectural Clarity**: The directory structure explicitly represents hexagonal architecture, making the layered model visible in file system navigation.

2. **Developer Velocity**: New developers understand immediately:
   - What is a port? Look in `ports/`
   - What is an adapter? Look in `adapters/`
   - Where's the core logic? Look in `application/` and `domain/`
   - What are inbound vs outbound interfaces? Check `driver_ports/` vs `driven_ports/`

3. **Scalability**: Adding new concerns (e.g., new adapter, new port, new domain logic) has a clear location:
   - New filesystem implementation? → `adapters/driven/filesystem/`
   - New hook? → `adapters/drivers/hooks/`
   - New domain concept? → `domain/new_concept.py`

4. **Test Navigation**: Test structure mirrors source structure, making it easy to find tests for any component.

5. **Hexagonal Enforces Discipline**: The structure prevents:
   - Domain logic leaking into adapters (wrong directory)
   - Adapters importing each other (different driver/driven groups)
   - Circular dependencies (clear dependency direction)

### Migration Path

**Phase 1: Create New Structure**
```bash
# Create new directory structure (don't delete old yet)
mkdir -p src/des/{domain,application,ports/driver_ports,ports/driven_ports}
mkdir -p src/des/adapters/{drivers/hooks,drivers/validators,driven/filesystem,driven/time,driven/logging,driven/config,driven/task_invocation}
mkdir -p tests/des/{adapters,unit/domain,unit/application,unit/ports,integration,acceptance,e2e}
```

**Phase 2: Move Files**
- Move domain files: `turn_counter.py`, `timeout_monitor.py`, `turn_config.py`, `invocation_limits_validator.py` → `domain/`
- Move application: `orchestrator.py`, `config_loader.py`, `validator.py` → `application/`
- Reorganize ports:
  - `hook_port.py`, `validator_port.py` → `ports/driver_ports/`
  - `filesystem_port.py`, `time_provider_port.py`, `logging_port.py`, `config_port.py`, `task_invocation_port.py` → `ports/driven_ports/`
- Reorganize adapters:
  - `real_hook.py` → `adapters/drivers/hooks/`
  - `real_validator.py` → `adapters/drivers/validators/`
  - `real_filesystem.py` → `adapters/driven/filesystem/`
  - `system_time.py` → `adapters/driven/time/`
  - `structured_logger.py`, `silent_logger.py` → `adapters/driven/logging/`
  - `environment_config_adapter.py`, `in_memory_config_adapter.py` → `adapters/driven/config/`
  - `claude_code_task_adapter.py`, `mocked_task_adapter.py` → `adapters/driven/task_invocation/`

**Phase 3: Update Imports**
- Use search/replace: `from src.des.orchestrator` → `from src.des.application.orchestrator`
- Use search/replace: `from src.des.turn_counter` → `from src.des.domain.turn_counter`
- Update port imports: `from src.des.ports.hook_port` → `from src.des.ports.driver_ports.hook_port`

**Phase 4: Organize Tests**
- Create test structure mirroring new src/ layout
- Move existing test doubles to `tests/des/adapters/`
- Create unit, integration, acceptance test files

**Phase 5: Clean Up**
- Delete old files after verifying imports work
- Run full test suite to confirm migration

### Impact on Imports

**Before**:
```python
from src.des.orchestrator import DESOrchestrator
from src.des.turn_counter import TurnCounter
from src.des.ports.hook_port import HookPort
from src.des.adapters.real_hook import RealSubagentStopHook
```

**After**:
```python
from src.des.application.orchestrator import DESOrchestrator
from src.des.domain.turn_counter import TurnCounter
from src.des.ports.driver_ports.hook_port import HookPort
from src.des.adapters.drivers.hooks.real_hook import RealSubagentStopHook
```

**Mitigation**: Create convenience imports in `src/des/__init__.py`:
```python
# src/des/__init__.py
from src.des.application.orchestrator import DESOrchestrator
from src.des.domain.turn_counter import TurnCounter
from src.des.ports.driver_ports.hook_port import HookPort
from src.des.adapters.drivers.hooks.real_hook import RealSubagentStopHook

__all__ = ["DESOrchestrator", "TurnCounter", "HookPort", "RealSubagentStopHook"]
```

This allows existing code to use: `from src.des import DESOrchestrator` (no import changes needed)

---

## Implementation Checklist

### Pre-Migration
- [ ] Verify all tests pass in current structure
- [ ] Document current import patterns (grep for `from src.des`)
- [ ] Create backup/branch of current state
- [ ] Run static analysis to find all import locations

### Migration
- [ ] Create new directory structure
- [ ] Move files to new locations
- [ ] Update imports throughout codebase
- [ ] Update test files
- [ ] Create __init__.py files with exports
- [ ] Run full test suite
- [ ] Verify no import errors

### Post-Migration
- [ ] Document new structure in architecture guide
- [ ] Update onboarding documentation
- [ ] Create examples showing where to add new code types
- [ ] Update IDE/editor project structure
- [ ] Verify imports are working with circular dependency analysis

---

## Conclusion

**Option B (Hexagon Layers Organization)** is the recommended structure because it:

1. **Explicitly represents hexagonal architecture** in the file system
2. **Enables clear developer navigation** - each directory has semantic meaning
3. **Scales well** - adding new concerns has a clear location
4. **Enforces architectural discipline** - structure prevents common mistakes
5. **Mirrors testing needs** - test organization naturally follows source organization

The migration effort is moderate and provides significant long-term maintainability and developer velocity benefits.

---

## References

- Cockburn, A. "Hexagonal Architecture". https://alistair.cockburn.us/hexagonal-architecture/
- C4 Model Documentation. https://c4model.com/
- Fowler, M. "Ports and Adapters". https://martinfowler.com/bliki/PaginatedList.html
- DDD Strategic Design Patterns. Domain-Driven Design textbook, Eric Evans
