# US-002 Resolution Plan: Framework Process Fixes

**Created**: 2026-01-24
**Status**: PROPOSED - Awaiting User Decision
**Root Cause Analysis**: [root-cause-analysis.md](./root-cause-analysis.md)
**RCA Review Status**: APPROVED

---

## Problem Statement

The current nWave framework allows features to pass all quality gates (tests, coverage, mutation testing) while remaining non-functional because:
1. No enforcement of hexagonal architecture boundaries in acceptance tests
2. No requirement for integration/wiring tests
3. No external validity check in reviews
4. Definition of Done lacks functional integration gate

**This is a framework deficiency, not a single-feature bug.**

---

## Resolution Scope

This plan fixes **agent definitions and command specifications** to prevent recurrence across all future features. US-002 will be fixed as a byproduct of validating the new process.

---

## Countermeasure Implementation Plan

### CM-A: DISTILL Wave - Hexagonal Boundary Enforcement

**Target Files**:
- `nWave/tasks/nw/distill.md` (command specification)
- Agent definition for `acceptance-designer`

**Changes Required**:

1. Add to DISTILL review criteria:
```yaml
hexagonal_boundary_check:
  criterion: "Acceptance tests must exercise driving ports"
  validation:
    - "Tests import entry-point modules (e.g., DESOrchestrator, API client)"
    - "Tests do NOT import internal components directly"
  violation_examples:
    - "from des.validator import TemplateValidator"  # WRONG
    - "from internal.service import BusinessLogic"   # WRONG
  correct_examples:
    - "from des.orchestrator import DESOrchestrator"  # CORRECT
    - "from api.client import FeatureClient"          # CORRECT
```

2. Add acceptance test boundary validation to `acceptance-designer` agent prompt:
```
MANDATORY CHECK: Before writing acceptance tests, verify:
- Test entry point is a DRIVING PORT (user-facing interface)
- Test does NOT directly instantiate internal components
- Test exercises the system from user perspective
```

**Effort**: Low (1-2 hours)

---

### CM-B: ROADMAP Phase - Integration Step Requirement

**Target Files**:
- `nWave/tasks/nw/roadmap.md` (command specification)
- `docs/principles/outside-in-tdd-step-mapping.md`
- Agent definition for `solution-architect`

**Changes Required**:

1. Add to step-to-scenario mapping validation:
```yaml
mapping_types:
  feature:        # Normal acceptance test at driving port
  integration:    # REQUIRED: At least 1 per feature - wiring test
  infrastructure: # DB migrations, env config (may lack scenarios)
  refactoring:    # Code improvement without behavior change

validation_rule: |
  Every feature MUST have at least one step with mapping_type: integration
  This step ensures the component is wired into the system entry point.
```

2. Add to `solution-architect` roadmap creation prompt:
```
MANDATORY: Roadmap must include at least one INTEGRATION step that:
- Wires component into system entry point
- Has acceptance test that invokes through driving port
- Proves end-to-end path works (not just component logic)

If all steps are "feature" type with no "integration" step,
the roadmap is INCOMPLETE.
```

**Effort**: Medium (2-3 hours)

---

### CM-C: REVIEW Phase - External Validity Check

**Target Files**:
- `nWave/tasks/nw/review.md` (command specification)
- All `*-reviewer` agent definitions

**Changes Required**:

1. Add new review criterion to all artifact reviews:
```yaml
external_validity:
  criterion: "Feature delivers working end-to-end capability"
  question: "After completing all steps, can user INVOKE this feature?"
  check:
    - "At least one step targets entry point integration"
    - "Tests verify observable system behavior, not just internal state"
  blocking: true  # Review FAILS if external validity not demonstrated
```

2. Add to reviewer agent prompts:
```
EXTERNAL VALIDITY CHECK (MANDATORY):
Ask yourself: "If I follow these steps exactly, will the feature WORK or just EXIST?"

A feature that:
- Has all tests passing
- Has 100% coverage
- Has high mutation score
- But cannot be invoked by users

...is NOT COMPLETE. It fails external validity.

REJECT any artifact that produces a non-invocable feature.
```

**Effort**: Medium (2-3 hours)

---

### CM-D: DEVELOP Phase - Wiring Test Mandate

**Target Files**:
- `nWave/tasks/nw/develop.md` (command specification)
- `nWave/tasks/nw/execute.md` (step execution)
- Agent definition for `software-crafter`

**Changes Required**:

1. Redefine 90/10 rule in develop.md:
```yaml
test_balance_requirement:
  rule: "90/10 with mandatory wiring"
  breakdown:
    - "90% unit tests: Component isolation, fast feedback"
    - "10% E2E tests: System wiring, integration verification"
  mandatory:
    - "At least 1 acceptance test must invoke through user-facing entry point"
    - "E2E means: entry_point → component → result"
    - "NOT: component → result (this is still a unit test)"

  validation: |
    grep acceptance test imports - at least one must reference entry point module
```

2. Add walking skeleton principle to execute.md:
```
WALKING SKELETON FIRST:
Before implementing component logic, ensure:
1. Entry point exists (even if empty/stubbed)
2. At least one acceptance test invokes entry point
3. Test fails for RIGHT reason (missing implementation, not missing wiring)

This ensures integration is never "forgotten" - it's the first thing built.
```

**Effort**: Medium (2-3 hours)

---

### CM-E: FINALIZE Phase - Functional Integration Gate

**Target Files**:
- `nWave/tasks/nw/finalize.md` (command specification)
- Definition of Done checklist
- Agent definition for `devop`

**Changes Required**:

1. Add to Definition of Done:
```yaml
develop_wave_completion_gates:
  existing:
    - all_tests_passing: required
    - code_coverage_above_80: required
    - mutation_score_above_75: required

  NEW_GATE:
    - functional_integration: REQUIRED
      description: "Feature invocable through documented entry point"
      validation:
        - "At least 1 acceptance test imports entry point module"
        - "grep entry_point in acceptance tests returns matches"
        - "Feature can be demonstrated to user (not just tested)"
      blocking: true  # Cannot finalize without this
```

2. Add to `devop` finalize prompt:
```
FUNCTIONAL INTEGRATION GATE (BLOCKING):
Before marking feature complete, verify:

1. Run: grep -l "entry_point_module" tests/acceptance/test_*.py
   - Must return at least one file

2. Verify at least one acceptance test:
   - Imports the user-facing entry point
   - Invokes feature through that entry point
   - Verifies observable system behavior

3. If no wiring test found:
   - BLOCK finalization
   - Report: "Feature has no integration test - cannot verify it works"
   - Require integration step before completion

A feature with 100% test coverage but 0% wiring tests is NOT COMPLETE.
```

**Effort**: Low (1-2 hours)

---

## Implementation Order

| Priority | Countermeasure | Target | Effort | Rationale |
|----------|---------------|--------|--------|-----------|
| 1 | CM-E | finalize.md, DoD | Low | Last line of defense, catches all gaps |
| 2 | CM-C | review.md, reviewers | Medium | Catches issues before implementation |
| 3 | CM-A | distill.md, acceptance-designer | Low | Prevents wrong boundary from start |
| 4 | CM-D | develop.md, execute.md | Medium | Enforces test balance |
| 5 | CM-B | roadmap.md, step-mapping | Medium | Schema change, more complex |

**Recommended approach**: Implement CM-E and CM-C first (blocking gates), then CM-A, CM-D, CM-B.

---

## Files to Modify

### Commands (nWave/tasks/nw/)

| File | Changes | CM |
|------|---------|-----|
| `distill.md` | Add hexagonal boundary check | CM-A |
| `split.md` | Add integration step requirement | CM-B |
| `review.md` | Add external validity criterion | CM-C |
| `develop.md` | Redefine 90/10 rule | CM-D |
| `execute.md` | Add walking skeleton principle | CM-D |
| `finalize.md` | Add functional integration gate | CM-E |

### Wave-Specific Reviewers (nWave/agents/)

| File | Changes | CM |
|------|---------|-----|
| `acceptance-designer-reviewer.md` | Hexagonal boundary validation | CM-A |
| `solution-architect-reviewer.md` | Integration step check, external validity | CM-B, CM-C |
| `software-crafter-reviewer.md` | External validity, wiring test check | CM-C, CM-D |
| `devop-reviewer.md` | Functional integration gate | CM-E |

**Note**: Domain-specialist reviewers (data-engineer, illustrator, documentarist, etc.) are NOT modified - they don't participate in wave quality gates.

### Principles Documentation (reference only)

| File | Changes | CM |
|------|---------|-----|
| `docs/principles/outside-in-tdd-step-mapping.md` | Add mapping_type field documentation | CM-B |

---

## Validation Plan

After implementing countermeasures:

1. **Retrospective Test**: Run US-002 through updated process
   - Should fail at CM-A (DISTILL) - wrong boundary detected
   - Should fail at CM-B (ROADMAP) - no integration step
   - Should fail at CM-C (REVIEW) - external validity check
   - Should fail at CM-E (FINALIZE) - no wiring test

2. **New Feature Test**: Develop a small feature with new process
   - Verify gates catch boundary violations
   - Verify integration step is required
   - Verify wiring test is mandated

3. **Documentation**: Update framework docs with lessons learned

---

## Success Criteria

The framework fixes are complete when:

- [ ] DISTILL rejects acceptance tests that import internal components
- [ ] ROADMAP requires at least one integration step per feature
- [ ] REVIEW includes external validity as blocking criterion
- [ ] DEVELOP mandates at least one wiring test
- [ ] FINALIZE blocks completion without functional integration

**Verification**: A feature identical to US-002 (wrong boundary, no integration) would be REJECTED at multiple gates.

---

## Decision Required

**Approach**: Implement all 5 countermeasures in priority order

**Estimated Total Effort**: 8-12 hours

**Shall I proceed with implementing these framework fixes?**

After framework fixes are complete, US-002 can be re-executed through the corrected process to validate the fixes work.
