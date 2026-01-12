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

## CRITICAL: 11-Phase TDD Loop Enforcement

**BLOCKER**: The following validation MUST occur before ANY git commit is allowed.

### Pre-Commit Validation Checklist

Execute these checks before `git commit`:

```python
def validate_11_phases_complete(step_file_path):
    """
    Validates that ALL 11 mandatory phases have been executed and documented.

    Returns: (bool, str) - (is_valid, error_message)
    """
    import json

    with open(step_file_path) as f:
        step_data = json.load(f)

    tracking = step_data['tdd_cycle']['tdd_phase_tracking']
    log = tracking['phase_execution_log']

    MANDATORY_PHASES = [
        "PREPARE",
        "RED (Acceptance)",
        "RED (Unit)",
        "GREEN (Unit)",
        "CHECK",
        "GREEN (Acceptance)",
        "REVIEW",
        "REFACTOR",
        "POST-REFACTOR REVIEW",
        "FINAL VALIDATE",
        "COMMIT"
    ]

    # Check 1: All phases present in log
    logged_phases = {entry['phase_name'] for entry in log}
    missing_phases = set(MANDATORY_PHASES) - logged_phases

    if missing_phases:
        return False, f"Missing phases: {missing_phases}"

    # Check 2: All phases have PASS outcome
    failed_phases = [
        entry['phase_name']
        for entry in log
        if entry['outcome'] != 'PASS'
    ]

    if failed_phases:
        return False, f"Failed phases: {failed_phases}"

    # Check 3: Commit policy field present
    commit_policy = step_data['task_specification'].get('commit_policy')
    if not commit_policy or '11 PHASES' not in commit_policy:
        return False, "Missing or invalid commit_policy"

    # Check 4: Review phases documented
    review_phases = [e for e in log if 'REVIEW' in e['phase_name']]
    if len(review_phases) < 2:
        return False, "Both REVIEW and POST-REFACTOR REVIEW are mandatory"

    # Check 5: Refactor level documented
    refactor_entry = next((e for e in log if e['phase_name'] == 'REFACTOR'), None)
    if not refactor_entry or 'refactor_level' not in refactor_entry.get('notes', ''):
        return False, "REFACTOR phase must document refactor_level (L1-L4)"

    return True, "All 11 phases validated successfully"

# USAGE: Call this function before git commit
is_valid, message = validate_11_phases_complete('docs/feature/{project-id}/steps/{task-id}.json')
if not is_valid:
    print(f"❌ COMMIT BLOCKED: {message}")
    print("Complete all 11 phases before committing.")
    exit(1)
else:
    print(f"✅ {message}")
    # Proceed with commit
```

### Execution Workflow

```
1. PREPARE      → Remove @skip, enable 1 scenario
                  ↓
2. RED (Accept) → Run tests, verify FAIL
                  ↓
3. RED (Unit)   → Write failing unit tests
                  ↓
4. GREEN (Unit) → Implement minimum code
                  ↓
5. CHECK        → Verify unit tests PASS
                  ↓
6. GREEN (Accept)→ Verify acceptance test PASS
                  ↓
7. REVIEW       → /dw:review @software-crafter-reviewer
                  ↓ (wait for approval)
8. REFACTOR     → Apply L1→L4 refactoring
                  ↓ (run tests after each level)
9. POST-REVIEW  → /dw:review @software-crafter-reviewer
                  ↓ (wait for approval)
10. VALIDATE    → Document full test results
                  ↓
11. COMMIT      → git commit + auto-push
```

**CRITICAL GATES**:
- Gate 1: RED (Acceptance) must FAIL before proceeding
- Gate 2: GREEN (Acceptance) must PASS before REVIEW
- Gate 3: REVIEW must approve (ready_for_execution = true)
- Gate 4: REFACTOR must reach L4 (or document exception)
- Gate 5: POST-REFACTOR REVIEW must approve
- Gate 6: VALIDATE must document all test results
- Gate 7: All phases documented in execution_result

**Commit Message Template**:
```
feat(scenario): <scenario_name>

Phase execution summary:
- PREPARE: <duration>min - <notes>
- RED (Acceptance): <duration>min - <notes>
- RED (Unit): <duration>min - <count> tests written
- GREEN (Unit): <duration>min - <implementation summary>
- CHECK: <duration>min - <test results>
- GREEN (Acceptance): <duration>min - <test results>
- REVIEW: <duration>min - <reviewer feedback summary>
- REFACTOR: <duration>min - <refactor levels applied>
- POST-REFACTOR REVIEW: <duration>min - <reviewer feedback>
- FINAL VALIDATE: <duration>min - <validation results>
- COMMIT: <duration>min - <total time for scenario>

Total time: <total_duration>min
Tests: <unit_count> unit, 1 acceptance (all passing)
Refactor level: L<1-4>
Reviews: 2 (pre-refactor, post-refactor)

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
```

---

## 11-Phase Command Invocation Mapping

The following table maps each of the 11 mandatory phases to the specific commands that must be invoked:

| Phase | Command to Invoke | Description | Duration Target |
|-------|------------------|-------------|-----------------|
| **1. PREPARE** | Internal (`/dw:develop`) | Remove `@skip` from target acceptance test, verify only 1 scenario enabled | 3-5 min |
| **2. RED (Acceptance)** | Internal (`/dw:develop`) | Run acceptance test - MUST fail for valid business reason | 3-5 min |
| **3. RED (Unit)** | Internal (`/dw:develop`) | Write unit test that fails for CORRECT reason (assertion, not setup/compilation) | 5-10 min |
| **4. GREEN (Unit)** | Internal (`/dw:develop`) | Implement MINIMAL code to pass unit test (YAGNI principle) | 10-20 min |
| **5. CHECK** | Internal (`/dw:develop`) | Check if acceptance test passes now. If FAILS → RETURN to Phase 3 | 2-3 min |
| **6. GREEN (Acceptance)** | Internal (`/dw:develop`) | Run ALL tests (unit + acceptance) - all must pass | 5-10 min |
| **7. REVIEW** | **`/dw:review @software-crafter-reviewer implementation`** | Mandatory peer review of implementation quality (max 2 iterations) | 10-15 min |
| **8. REFACTOR** | **`/dw:refactor`** (L1-L4) OR **`/dw:mikado`** (complex) | Progressive refactoring with test validation after each level | 15-30 min |
| **9. POST-REFACTOR REVIEW** | **`/dw:review @software-crafter-reviewer refactored_implementation`** | Review after refactoring complete (max 2 iterations) | 10-15 min |
| **10. FINAL VALIDATE** | Internal (`/dw:develop`) | Run ALL tests (unit, integration, acceptance) - 100% must pass | 5-10 min |
| **11. COMMIT** | **`/dw:git commit`** | Commit with detailed message and 11-phase validation | 5 min |

### Command Invocation Protocol

**Phases 1-6, 10** are handled internally by the `/dw:develop` command as part of the main TDD loop.

**Phase 7 (REVIEW)** requires explicit invocation:
```bash
/dw:review @software-crafter-reviewer implementation {step-file-path}
```
- Max 2 iterations allowed
- Must approve before proceeding to REFACTOR
- If rejected after 2 iterations → escalate to tech lead

**Phase 8 (REFACTOR)** requires explicit invocation:

*Simple to moderate refactoring (L1-L4):*
```bash
/dw:refactor --level 4 --scope module
```
- Apply progressive levels L1 → L2 → L3 → L4
- Run tests after EACH level
- Revert if any test fails

*Complex refactoring (requires dependency exploration):*
```bash
/dw:mikado --goal "Replace UserManager with hexagonal architecture"
```
- Use Mikado Method for complex architectural refactorings
- Discovery-tracking commits for exploration
- Execute leaves bottom-up with test validation

**Phase 9 (POST-REFACTOR REVIEW)** requires explicit invocation:
```bash
/dw:review @software-crafter-reviewer refactored_implementation {step-file-path}
```
- Max 2 iterations allowed
- If major issues → may RETURN to REFACTOR at L1
- Must approve before proceeding to FINAL VALIDATE

**Phase 11 (COMMIT)** requires git commit:
```bash
git add .
git commit -m "feat(...): ..."
```
- Pre-commit hook validates 100% test pass rate
- Step file validation ensures all 11 phases documented
- NO PUSH until `/dw:finalize` completes

### Integration Example

Complete execution flow for a single step:

```bash
# Phase 1-6: Main TDD loop (internal to /dw:develop)
/dw:develop order-management --step 01-02

# Phase 7: REVIEW (explicit command)
/dw:review @software-crafter-reviewer implementation "docs/feature/order-management/steps/01-02.json"
# Wait for approval...

# Phase 8: REFACTOR (explicit command - choose one)
/dw:refactor --level 4 --scope module
# OR for complex refactoring:
/dw:mikado --goal "Extract OrderService from OrderController"

# Phase 9: POST-REFACTOR REVIEW (explicit command)
/dw:review @software-crafter-reviewer refactored_implementation "docs/feature/order-management/steps/01-02.json"
# Wait for approval...

# Phase 10: FINAL VALIDATE (internal to /dw:develop)
# Automatically runs all tests

# Phase 11: COMMIT (explicit git command)
git add .
git commit -m "feat(order-management): Place new order - step 01-02

- Acceptance test: Place new order scenario
- Unit tests: 5 new (OrderService, OrderValidator)
- Refactoring level: L4

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

### Alternative: Fully Automated Execution

For fully automated execution with minimal manual intervention:

```bash
/dw:execute @software-crafter "docs/feature/order-management/steps/01-02.json"
```

The `execute` command will:
1. Automatically invoke `/dw:develop` for phases 1-6 and 10
2. Automatically invoke `/dw:review` for phases 7 and 9
3. Automatically invoke `/dw:refactor` or `/dw:mikado` for phase 8
4. Automatically commit for phase 11 if all validations pass

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
