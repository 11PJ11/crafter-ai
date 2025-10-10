---
agent-activation:
  required: true
  agent-id: software-crafter
  agent-name: "Crafty"
  agent-command: "*develop"
  auto-activate: true
---

# DW-DEVELOP: Outside-In TDD Implementation with Systematic Refactoring

**Wave**: DEVELOP
**Agent**: Crafty (software-crafter)
**Command**: `*develop`

## Overview

Execute DEVELOP wave of 5D-Wave methodology through Outside-In TDD implementation with double-loop architecture, production service integration, and systematic refactoring using six-level hierarchy.

Research-validated double-loop TDD drives implementation: outer loop (ATDD - customer view) contains inner loops (UTDD - developer view) with continuous refactoring.

## Context Files Required

- tests/acceptance/acceptance-tests.feature - (from DISTILL wave)
- tests/acceptance/step-definitions.cs - (from DISTILL wave)
- docs/architecture/architecture-design.md - (from DESIGN wave)
- docs/architecture/component-boundaries.md - (from DESIGN wave)

## Previous Artifacts (Wave Handoff)

- tests/acceptance/acceptance-tests.feature - (from DISTILL wave)
- tests/acceptance/step-definitions.cs - (from DISTILL wave)
- docs/testing/test-scenarios.md - (from DISTILL wave)

## Agent Invocation

@software-crafter

Execute \*develop for {feature-name}.

**Context Files:**

- tests/acceptance/acceptance-tests.feature
- tests/acceptance/step-definitions.cs
- docs/architecture/architecture-design.md
- docs/architecture/component-boundaries.md

**Previous Artifacts:**

- tests/acceptance/acceptance-tests.feature
- tests/acceptance/step-definitions.cs
- docs/testing/test-scenarios.md

**Configuration:**

- tdd_mode: strict
- refactor_level: 3 # Levels 1-6
- test_framework: nunit # or pytest/jest
- architecture_pattern: hexagonal

## Success Criteria

Refer to Crafty's quality gates in 5d-wave/agents/software-crafter.md.

**Key Validations:**

- [ ] All acceptance tests passing (100% required)
- [ ] Unit test coverage ≥80% for business logic
- [ ] Hexagonal architecture patterns implemented
- [ ] One E2E test at a time strategy followed
- [ ] Handoff accepted by feature-completion-coordinator (DEMO wave)
- [ ] Layer 4 peer review approval obtained

## Next Wave

**Handoff To**: feature-completion-coordinator (DEMO wave)
**Deliverables**: See Crafty's handoff package specification in agent file

# Expected outputs (reference only):

# - src/\* (complete production implementation)

# - tests/unit/\* (comprehensive unit tests)

# - tests/integration/\* (integration tests)
