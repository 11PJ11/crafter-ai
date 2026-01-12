---
description: 'Outside-In TDD implementation with refactoring [feature-name] --step [step-id]'
argument-hint: '[feature-name] --step [step-id] - Example: order-management --step 01-02'
agent-activation:
  required: true
  agent-id: software-crafter
  agent-name: "Crafty"
  agent-command: "*develop"
  auto-activate: true
---

# DW-DEVELOP: Disciplined TDD Orchestrator with 11-Phase Inner Loop

**Wave**: DEVELOP
**Agent**: Crafty (software-crafter)
**Command**: `/dw:develop {feature-name} --step {step-id}`

## Overview

Execute DEVELOP wave through a **disciplined TDD orchestrator** that enforces strict Outside-In TDD with the 11-phase inner loop:

```
PREPARE → RED(Acceptance) → RED(Unit) ⇄ GREEN(Unit) → CHECK → GREEN(Acceptance)
→ REVIEW → REFACTOR(L1→L4) → POST-REFACTOR REVIEW → FINAL VALIDATE → COMMIT
```

**Key Principles**:
- One acceptance test at a time (others [Ignored])
- Unit tests MUST fail for the correct reason before implementation
- Test doubles ONLY at hexagonal architecture boundaries
- Progressive refactoring L1→L2→L3→L4 with validation at each level
- NEVER commit with failing tests

---

## Prerequisites Check (PHASE 0)

Before starting development, verify ALL prerequisites exist:

```
VERIFY_PREREQUISITES(feature_name, step_id):
  1. Baseline: docs/feature/{feature_name}/baseline.yaml      [REQUIRED]
  2. Roadmap:  docs/feature/{feature_name}/roadmap.yaml       [REQUIRED]
  3. Step:     docs/feature/{feature_name}/steps/{step_id}.json [REQUIRED]
  4. Architecture: docs/architecture/architecture-design.md   [REQUIRED]

  IF ANY missing:
    ERROR: "Prerequisites incomplete. Run /dw:baseline and /dw:roadmap first."
    EXIT
```

---

## The 11-Phase TDD Inner Loop

### Phase 1: PREPARE
**Goal**: Activate exactly ONE acceptance test

```
PREPARE(step):
  1. Read step.tdd_cycle.acceptance_test from step JSON
  2. Locate test file at step.tdd_cycle.acceptance_test.test_file
  3. Remove [Ignore] from target scenario (scenario_index)
  4. Verify all OTHER scenarios have [Ignore]

  GATE G1: Exactly ONE acceptance test active
  IF gate fails: BLOCK and report

  Update step state: tdd_phase = "PREPARE", log timestamp
```

### Phase 2: RED (Acceptance)
**Goal**: Acceptance test MUST fail

```
RED_ACCEPTANCE(step):
  1. Run acceptance test
  2. Capture result

  IF test PASSES:
    ERROR: "Acceptance test passed immediately - test is invalid"
    ACTION: Review test, it doesn't test new behavior
    RETURN to PREPARE

  IF test FAILS:
    CLASSIFY failure type (see 13.4 in plan):
    - BUSINESS_LOGIC_NOT_IMPLEMENTED → VALID RED
    - MISSING_ENDPOINT → VALID RED
    - DATABASE_CONNECTION → INVALID - fix infrastructure
    - TIMEOUT → INVALID - fix test setup

  GATE G2: Acceptance test fails for valid reason

  Update step state: tdd_phase = "RED_ACCEPTANCE"
```

### Phase 3: RED (Unit)
**Goal**: Write unit test that fails for CORRECT reason

```
RED_UNIT(step):
  1. Write unit test for minimal behavior needed
  2. Follow naming: {BusinessConcept}Should.{Behavior}_When{Condition}
  3. Run test

  VALIDATE failure reason (see 13.3 in plan):
  - ASSERTION_FAILED → CORRECT - proceed
  - COMPILATION_ERROR → WRONG - fix syntax, retry
  - NULL_REFERENCE → WRONG - fix setup, retry
  - TIMEOUT → WRONG - fix infrastructure

  GATE G3: Unit test fails on assertion, not setup/compilation

  CHECK mock usage:
  IF Mock<DomainClass> found (not a Port/Adapter):
    ERROR: "Mocking domain class forbidden"
    GATE G4 FAIL

  Update step state: tdd_phase = "RED_UNIT"
```

### Phase 4: GREEN (Unit)
**Goal**: Implement MINIMAL code to pass unit test

```
GREEN_UNIT(step):
  1. Implement ONLY what test requires
  2. Follow YAGNI - no extra functionality
  3. Run unit test

  IF test FAILS:
    Fix implementation, retry

  IF test PASSES:
    Proceed to CHECK

  Update step state: tdd_phase = "GREEN_UNIT"
```

### Phase 5: CHECK (Acceptance)
**Goal**: Check if acceptance test passes now

```
CHECK_ACCEPTANCE(step):
  1. Run acceptance test

  IF FAILS:
    More behavior needed
    RETURN to Phase 3 (RED_UNIT)

  IF PASSES:
    Proceed to GREEN_ACCEPTANCE

  Update step state: tdd_phase = "CHECK_ACCEPTANCE"
```

### Phase 6: GREEN (Acceptance)
**Goal**: Confirm acceptance test passes

```
GREEN_ACCEPTANCE(step):
  1. Run ALL tests (unit + acceptance)
  2. All must pass

  GATE G6: All tests green

  VERIFY: Acceptance test NOT modified during implementation
  IF modified: WARNING - test should define behavior, not change to match impl

  Update step state: tdd_phase = "GREEN_ACCEPTANCE"
```

### Phase 7: REVIEW LOOP
**Goal**: Review implementation quality with iteration

```
REVIEW_LOOP(step, max_iterations=2):
  FOR iteration IN 1..max_iterations:
    1. Execute: /dw:review @software-crafter-reviewer implementation

    2. VALIDATE: Run ALL tests
       IF any fail: FIX first, then continue

    3. Parse review_result:
       IF approval_status == "approved":
         PROCEED to REFACTOR

       IF approval_status == "rejected_pending_revisions":
         FIX issues by category order:
         - Architecture violations first
         - Domain mock violations second
         - Business language violations last
         VALIDATE after each fix
         CONTINUE loop

       IF iteration == max_iterations AND not approved:
         ESCALATE to user with root cause analysis

  GATE G5: Business language verified in tests

  Update step state: tdd_phase = "REVIEW", review_attempts = iteration
```

### Phase 8: REFACTOR LOOP (L1→L4)
**Goal**: Progressive refactoring with validation at each level

```
REFACTOR_LOOP(step):
  FOR level IN [L1, L2, L3, L4]:
    1. Apply refactoring at level:
       L1: Naming (business language in variables, methods, classes)
       L2: Method extraction (single responsibility at method level)
       L3: Class extraction (single responsibility at class level)
       L4: Type-driven design (domain types, make invalid states unrepresentable)

    2. VALIDATE: Run ALL tests
       IF any fail:
         REVERT changes at this level
         RETRY with smaller refactoring steps
         IF still failing after 2 retries:
           STOP at current level, proceed to review

    3. Update step state: refactor_level_completed = level

  GATE G6: All tests remain green ALWAYS

  Update step state: tdd_phase = "REFACTOR_L{level}"
```

### Phase 9: POST-REFACTOR REVIEW
**Goal**: Review after refactoring is complete

```
POST_REFACTOR_REVIEW(step, max_iterations=2):
  FOR iteration IN 1..max_iterations:
    1. Execute: /dw:review @software-crafter-reviewer refactored_implementation

    2. VALIDATE: Run ALL tests

    3. Parse review_result:
       IF approved:
         PROCEED to FINAL_VALIDATE

       IF major issues found:
         IF issues require re-refactoring:
           RETURN to REFACTOR_LOOP at L1
         ELSE:
           FIX issues, VALIDATE, CONTINUE loop

  Update step state: tdd_phase = "POST_REFACTOR_REVIEW"
```

### Phase 10: FINAL VALIDATE
**Goal**: Confirm all tests pass before commit

```
FINAL_VALIDATE(step):
  1. Run ALL tests (unit, integration, acceptance)
  2. Count results

  IF any test fails:
    ERROR: "Cannot commit with failing tests"
    BLOCK commit
    Report failing tests
    RETURN to appropriate phase to fix

  GATE G7: 100% tests passing

  Update step state: tdd_phase = "FINAL_VALIDATE"
```

### Phase 11: COMMIT
**Goal**: Commit this step's work

```
COMMIT(step):
  1. VERIFY: All tests passing (G7)
  2. Stage all changes
  3. Create commit with message:
     "feat({feature_name}): {scenario_name} - step {step_id}

     - Acceptance test: {scenario_name}
     - Unit tests: {count} new
     - Refactoring level: L{level_completed}

     Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"

  4. DO NOT PUSH (push happens after /dw:finalize)

  Update step state: tdd_phase = "COMMIT", status = "COMPLETED"
```

---

## Testing Strategy

### E2E vs In-Memory Acceptance Tests

| Type | When | Characteristics |
|------|------|-----------------|
| **Real E2E** | Walking skeleton (01-01), wiring verification | Slow, real infrastructure |
| **In-Memory** | Majority of scenarios | Fast, test doubles at boundaries |

**Principles**:
- **Favor fast in-memory tests** (target: 80% of acceptance tests)
- **Walking skeleton CAN be E2E** but doesn't HAVE TO be
- **E2E tests** verify real system wiring with simple logic

### Test Doubles Policy (Hexagonal Architecture)

```
┌─────────────────────────────────────────────────────────────────┐
│                    APPLICATION + DOMAIN (Core)                   │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  Domain Services, Entities, Value Objects               │    │
│  │  Application Services, Use Cases                        │    │
│  │                                                         │    │
│  │  ✅ USE CONCRETE CLASSES - NO TEST DOUBLES             │    │
│  └─────────────────────────────────────────────────────────┘    │
│                           │                                      │
│                     BOUNDARY (Ports)                             │
│                           │                                      │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  Infrastructure Adapters (DB, HTTP, Email, Payment)     │    │
│  │                                                         │    │
│  │  ✅ TEST DOUBLES ALLOWED (Stubs, Fakes, Mocks)         │    │
│  │  ✅ In-Memory Adapters preferred                        │    │
│  └─────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
```

---

## Quality Gates Summary

| Gate | Check | Blocks If |
|------|-------|-----------|
| G1 | Only 1 acceptance test active | != 1 active test |
| G2 | Acceptance test fails first | Passes immediately |
| G3 | Unit test fails for correct reason | Compilation/setup error |
| G4 | No mocks inside hexagon | Mock<DomainClass> found |
| G5 | Business language in tests | Technical naming detected |
| G6 | Tests green after each refactor | Any test fails |
| G7 | Zero failing tests before commit | Any test fails |

---

## Context Files Required

- `docs/feature/{feature-name}/steps/{step-id}.json` - Step specification with TDD cycle
- `docs/feature/{feature-name}/roadmap.yaml` - Feature roadmap
- `docs/architecture/architecture-design.md` - Architecture for mock boundary analysis
- `tests/acceptance/*` - Acceptance test files

## Previous Artifacts (Wave Handoff)

- From DISTILL wave: Acceptance tests with all scenarios [Ignored]
- From DESIGN wave: Architecture design with ports/adapters identified

---

## Usage

```bash
# Execute single step
/dw:develop order-management --step 01-02

# The orchestrator will:
# 1. Verify prerequisites
# 2. Run 11-phase TDD loop
# 3. Commit on success (no push)
```

## Complete Feature Flow

```bash
# Prerequisites (if needed)
/dw:baseline "order-management"
/dw:roadmap @software-crafter "Implement order placement"
/dw:split @software-crafter "order-management"

# Execute each step (commit per step)
/dw:develop order-management --step 01-01
/dw:develop order-management --step 01-02
/dw:develop order-management --step 01-03

# After all steps complete
/dw:finalize @devop "order-management"
/dw:git push
```

---

## Success Criteria

- [ ] All 11 phases executed in order
- [ ] All quality gates passed
- [ ] Acceptance test activated, failed first, then passed
- [ ] Unit tests failed for correct reason before implementation
- [ ] No mocks inside application/domain core
- [ ] Refactoring completed L1→L4 with validation
- [ ] Reviews passed (max 2 iterations)
- [ ] All tests passing at commit
- [ ] Commit created (not pushed)

## Next Wave

**After all steps**: `/dw:finalize` → DEMO wave
**Handoff**: feature-completion-coordinator
