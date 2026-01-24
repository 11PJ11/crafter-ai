# Root Cause Analysis: US-002 Template Validation Integration Failure

**Project**: des-us002
**Analysis Date**: 2026-01-24
**Analyst**: Sage (Root Cause Analysis Specialist)
**Methodology**: Toyota 5 Whys with Multi-Causal Investigation

---

## Executive Summary

US-002 Template Validation was completed with 15 passing tests (6 acceptance + 9 unit), mutation testing showing 98%+ kill rate, and 100% code coverage. Despite these metrics, the feature does not work in production because `TemplateValidator` is never called by `DESOrchestrator`.

This is a case of **"Testing Theatre"** - high test metrics that provide false confidence while the actual feature remains non-functional.

**Root Cause Count**: 5 independent but compounding causes
**Pattern**: Swiss Cheese Model - all defense layers had aligned holes

---

## Problem Statement

### Observed Symptom

The validator module (`des/validator.py`) exists and functions correctly in isolation, but `DESOrchestrator` never calls it. Invalid prompts can still invoke Task tools. Users do not receive recovery guidance. The feature is "done" by all metrics but doesn't actually work end-to-end.

### Business Impact

| Impact Area | Description |
|-------------|-------------|
| User Experience | Invalid prompts execute without validation |
| Error Prevention | Specification gaps not caught early |
| Trust | Metrics suggest quality that doesn't exist |
| Process Credibility | Wave completion doesn't guarantee working features |

### Scope

- **Files Involved**:
  - `tests/acceptance/test_us002_template_validation.py` - Tests at wrong boundary
  - `des/validator.py` - Component works in isolation
  - `des/orchestrator.py` - Missing validation gate
  - `docs/feature/des-us002/roadmap.yaml` - Missing integration step

---

## Evidence Collection

### Evidence E1: Acceptance Tests Import Validator Directly

```python
# test_us002_template_validation.py, lines 51, 104-105, 175-178
from des.validator import TemplateValidator

validator = TemplateValidator()
validation_result = validator.validate_prompt(prompt_with_all_sections)
```

**Significance**: Tests bypass the entry point (DESOrchestrator) entirely.

### Evidence E2: DESOrchestrator Has No Validator Integration

```bash
$ grep -n "TemplateValidator\|validate_prompt" des/orchestrator.py
# (no results)
```

**Significance**: Orchestrator has no reference to validator module.

### Evidence E3: Roadmap Steps Focus Only on Validator

```yaml
# roadmap.yaml step_to_scenario_mapping (lines 201-207)
step_to_scenario_mapping:
  "01-01": "test_complete_prompt_passes_all_validation_checks (AC-002.1)"
  "02-01": "test_missing_tdd_phase_blocks_task_invocation (AC-002.2)"
  "02-02": "test_missing_mandatory_section_provides_actionable_error (AC-002.3)"
  "03-01": "test_multiple_validation_errors_reported_together (AC-002.4)"
  "04-01": "test_validation_completes_within_performance_budget (AC-002.5)"
  "04-02": "test_malformed_des_marker_detected_and_rejected (Edge case)"
```

**Significance**: All 6 steps map to validator tests. Zero steps map to integration.

### Evidence E4: Roadmap Architecture Notes Describe Integration

```yaml
# roadmap.yaml lines 266-269
Integration with DESOrchestrator:
- Pre-invocation hook calls TemplateValidator.validate_prompt()
- If validation fails, Task invocation is blocked
- Validation errors surfaced to user before execution
```

**Significance**: Integration was documented but never implemented - no step created for it.

### Evidence E5: Review Approved Without Integration Check

```yaml
# roadmap.yaml lines 219-225
notes: |
  Roadmap passes all 6 review criteria:
  1. Step Atomicity: All 6 steps sized 1-4h
  2. Dependency Mapping: Linear flow with no cycles
  3. Technical Feasibility: Sound Outside-In TDD approach
  4. TDD Compliance: All 14 phases required
  5. Step-to-Scenario Mapping: Exactly 6 steps with 1:1 mapping verified
  6. Completeness: All 5 AC scenarios + 1 edge case covered
```

**Significance**: Review criteria validated internal consistency. None checked external validity.

### Evidence E6: Evolution Doc Classifies Integration as "Next Steps"

```markdown
# evolution doc, lines 499-507
## Next Steps: DELIVER Wave

1. **Production Deployment**
   - Deploy validator.py to production environment
   - Integrate with DESOrchestrator as pre-invocation hook
   - Monitor validation errors in production
```

**Significance**: Integration treated as deployment task, not implementation task.

### Evidence E7: Test Ratio Imbalance

| Test Type | Count | Percentage |
|-----------|-------|------------|
| Component (unit + acceptance) | 15 | 100% |
| E2E Wiring | 0 | 0% |

**Significance**: 90/10 rule violated - zero wiring tests.

---

## Causal Chain Analysis (Toyota 5 Whys)

### Causal Chain A: Acceptance Test Boundary Error

```
WHY #1A: Why doesn't the validator work in production?
BECAUSE: Validator is not integrated into DESOrchestrator.
[Evidence: E2 - grep shows no validator reference in orchestrator]

WHY #2A: Why wasn't integration code written?
BECAUSE: Acceptance tests pass without integration - they test TemplateValidator directly.
[Evidence: E1 - test imports validator directly]

WHY #3A: Why do acceptance tests test validator directly?
BECAUSE: Tests were written at application layer instead of driving port.
[Evidence: E1 - tests never invoke DESOrchestrator.render_prompt()]

WHY #4A: Why were tests written at wrong boundary?
BECAUSE: DISTILL wave focused on WHAT to validate, not WHEN validation occurs.
[Evidence: Story says "block Task invocation" but tests verify task_invocation_allowed flag]

WHY #5A [ROOT CAUSE]: Why did DISTILL focus on WHAT without WHERE?
BECAUSE: No process gate enforces hexagonal architecture principle:
"Acceptance tests must exercise driving ports, not internal components"
```

**ROOT CAUSE RC-A**: DISTILL Wave lacks hexagonal boundary enforcement

---

### Causal Chain B: Roadmap Step Omission

```
WHY #1B: Why doesn't the validator work in production?
BECAUSE: No roadmap step exists for orchestrator integration.
[Evidence: E3 - all 6 steps map to validator tests]

WHY #2B: Why was integration not a roadmap step?
BECAUSE: Steps were derived from acceptance test scenarios, all at validator level.
[Evidence: E3 - step_to_scenario_mapping shows 6:6 ratio, all validator tests]

WHY #3B: Why did mapping produce only validator-level steps?
BECAUSE: Step-to-scenario mapping requires count equality (N steps = N scenarios).
[Evidence: Reference doc states "number of feature steps MUST equal number of scenarios"]

WHY #4B: Why doesn't mapping require boundary correctness?
BECAUSE: Constraint focuses on COUNT equality, not BOUNDARY placement.
[Evidence: Reference doc validates count but not where acceptance tests are written]

WHY #5B [ROOT CAUSE]: Why isn't boundary correctness part of mapping?
BECAUSE: Step-to-scenario mapping prevents SCOPE CREEP but doesn't enforce
HEXAGONAL ARCHITECTURE - it's necessary but not sufficient.
```

**ROOT CAUSE RC-B**: Step-to-scenario mapping is incomplete constraint

---

### Causal Chain C: Review Process Failure

```
WHY #1C: Why doesn't the validator work in production?
BECAUSE: Reviewers approved artifacts that missed integration.
[Evidence: E5 - review approved with "no issues"]

WHY #2C: Why did reviewers approve without integration step?
BECAUSE: Review criteria don't include "integration coverage" check.
[Evidence: E5 - 6 review criteria listed, none about integration]

WHY #3C: Why don't criteria include integration validation?
BECAUSE: Checklist validates INTERNAL CONSISTENCY (roadmap matches tests)
but not EXTERNAL VALIDITY (roadmap delivers working feature).
[Evidence: Reviews validate "6 scenarios -> 6 step files" count match]

WHY #4C: Why is external validity missing from checklist?
BECAUSE: Review assumes acceptance tests are architecturally correct.
[Evidence: Baseline and roadmap reference tests as authoritative truth]

WHY #5C [ROOT CAUSE]: Why does review assume test correctness?
BECAUSE: No validation step checks "acceptance tests exercise driving ports
per hexagonal architecture" - tests treated as invariant truth.
```

**ROOT CAUSE RC-C**: Review process lacks external validity check

---

### Causal Chain D: 90/10 Rule Violation

```
WHY #1D: Why doesn't the validator work in production?
BECAUSE: Test suite has 0% wiring tests, 100% component tests.
[Evidence: E7 - 15 tests all at component level]

WHY #2D: Why is there no wiring test balance?
BECAUSE: 90/10 rule wasn't interpreted to require WIRING tests.
[Evidence: Coverage is 100% but doesn't detect missing integration paths]

WHY #3D: Why wasn't 90/10 interpreted to require wiring tests?
BECAUSE: "E2E tests" understood as "component chain" not "system chain".
[Evidence: Tests exercise Validator -> Result chain, not Orchestrator -> Validator chain]

WHY #4D: Why was E2E interpreted as component chain?
BECAUSE: User story decomposed into validation LOGIC without INVOCATION context.
[Evidence: Story says "Task is blocked" but tests verify "allowed=False" - different things]

WHY #5D [ROOT CAUSE]: Why was story decomposed without invocation context?
BECAUSE: Decomposition focused on WHAT (rules) without WHERE (invocation point)
and HOW (integration). "Pre-invocation" was descriptive, not architectural.
```

**ROOT CAUSE RC-D**: 90/10 rule missing wiring test mandate

---

### Causal Chain E: Definition of Done Gap

```
WHY #1E: Why doesn't the validator work in production?
BECAUSE: Feature declared "complete" based on metrics without functional verification.
[Evidence: E6 - evolution doc says "complete" with integration in "next steps"]

WHY #2E: Why was metric-based completion sufficient?
BECAUSE: DoD focused on test metrics (pass rate, coverage, mutation) without
"functional integration" criterion.
[Evidence: Quality gates: tests ✓, coverage ✓, mutation ✓ - no integration gate]

WHY #3E: Why doesn't DoD include functional integration?
BECAUSE: DoD designed for isolated feature development, assuming integration obvious.
[Evidence: E6 - integration listed under "DELIVER wave" not "DEVELOP wave"]

WHY #4E: Why is integration considered post-feature work?
BECAUSE: Process separates DEVELOP (implement) from DELIVER (deploy), and integration
was classified as deployment.
[Evidence: E6 - "Integrate with DESOrchestrator" under DELIVER wave]

WHY #5E [ROOT CAUSE]: Why is integration classified with deployment?
BECAUSE: Wave model creates false boundary: DEVELOP builds component, DELIVER connects.
But integration IS implementation - feature that can't be invoked hasn't been implemented.
```

**ROOT CAUSE RC-E**: Definition of Done missing functional integration gate

---

## Root Causes Summary

| ID | Root Cause | Phase Affected | Detection Opportunity |
|----|------------|----------------|----------------------|
| RC-A | DISTILL Wave lacks hexagonal boundary enforcement | DISTILL | Test review should check imports |
| RC-B | Step-to-scenario mapping incomplete constraint | ROADMAP | Mapping should validate boundary |
| RC-C | Review process lacks external validity check | REVIEW | Reviewers should ask "will this work?" |
| RC-D | 90/10 rule missing wiring test mandate | DEVELOP | Test balance should require wiring |
| RC-E | DoD missing functional integration gate | FINALIZE | Completion should verify invocation |

### Swiss Cheese Model

All 5 defense layers had aligned holes:
- DISTILL: Didn't enforce hexagonal boundary
- ROADMAP: Didn't require integration step
- REVIEW: Didn't check external validity
- DEVELOP: Didn't mandate wiring test
- FINALIZE: Didn't verify functional integration

Any single layer catching the issue would have prevented the failure.

---

## Countermeasures

### CM-A: Add Hexagonal Boundary Check to DISTILL Wave

**Action**: Add to DISTILL review criteria:
- "All acceptance tests must exercise driving port, not internal components"
- "Acceptance test imports should reference entry point modules only"

**Implementation**:
```yaml
# Add to distill checklist
- criterion: "Hexagonal Boundary"
  check: "Acceptance tests import entry point module (e.g., DESOrchestrator)"
  violation: "Tests import internal components (e.g., TemplateValidator)"
```

**Owner**: Process team
**Due**: Next DISTILL wave

### CM-B: Extend Step-to-Scenario Mapping with Boundary Requirement

**Action**: Add to step-to-scenario validation:
- "At least one scenario must invoke driving port entry point"
- Add `mapping_type: integration` for wiring scenarios

**Implementation**:
```yaml
# Add to step-template-mapped-scenario-field.md
mapping_types:
  - feature      # Normal acceptance test
  - integration  # REQUIRED: At least 1 per feature - tests entry point
  - infrastructure
  - refactoring
```

**Owner**: nWave framework team
**Due**: Before next feature development

### CM-C: Add External Validity Check to Review Process

**Action**: Add review criterion:
- "Feature delivers end-to-end working capability when all steps complete"
- New review question: "If I follow these steps, will the feature WORK or just EXIST?"

**Implementation**:
```yaml
# Add to roadmap review criteria
- criterion: "External Validity"
  question: "After completing all steps, can user invoke this feature?"
  check: "At least one step targets entry point integration"
```

**Owner**: Review process team
**Due**: Immediate

### CM-D: Mandate Wiring Test in 90/10 Balance

**Action**: Redefine 90/10 rule:
- 90% unit tests (component isolation)
- 10% E2E **WIRING** tests (system chain, not component chain)
- Require at least 1 acceptance test through entry point

**Implementation**: Add to test policy:
```markdown
## Test Balance Requirement
- At least 1 acceptance test must invoke feature through user-facing entry point
- "E2E" means system entry → component → result, not just component → result
```

**Owner**: Quality team
**Due**: Immediate

### CM-E: Add Functional Integration Gate to Definition of Done

**Action**: Add DoD gates:
- "Feature can be invoked through documented entry point"
- "At least one acceptance test exercises full system path"

**Implementation**: Move integration from DELIVER to DEVELOP wave scope:
```yaml
# Update DoD checklist
develop_wave_completion:
  - All tests passing: required
  - Code coverage >80%: required
  - Mutation testing >75%: required
  - Functional integration: REQUIRED  # NEW
    check: "Feature invocable through entry point"
```

**Owner**: Process team
**Due**: Immediate

---

## Prevention Recommendations

### 1. Walking Skeleton First

**Principle**: Always start with minimal wiring test before implementing component logic.

**Application to US-002**: First test should have been:
```python
def test_orchestrator_validates_prompt_before_task_invocation():
    orchestrator = DESOrchestrator()
    result = orchestrator.render_prompt("/nw:execute", step_file="...")
    # This would have forced validator integration from day 1
```

### 2. Entry Point Test Mandate

**Principle**: First acceptance test must invoke system from user perspective.

**Rule**: For any feature "X does Y when Z":
- Test must start at user entry point (command, API, UI)
- Test must exercise full path, not just component

### 3. Integration-Aware Roadmap

**Principle**: Roadmap must include step that connects component to system.

**Checklist addition**:
```yaml
roadmap_review:
  - "At least one step targets integration point"
  - "Final step verifies end-to-end invocation"
```

### 4. Boundary Review in DISTILL

**Principle**: DISTILL review must validate test imports align with hexagonal architecture.

**Automated check**:
```python
# Acceptance tests should NOT import:
forbidden_imports = ["des.validator", "des.internal.*"]

# Acceptance tests SHOULD import:
required_imports = ["des.orchestrator", "des.entry_point"]
```

---

## Validation

### Backwards Chain Validation

Each root cause independently explains the symptom:

| Root Cause | If Fixed | Would Prevent Symptom |
|------------|----------|----------------------|
| RC-A | Tests at driving port | Integration required for test to pass |
| RC-B | Integration step required | Roadmap would include wiring work |
| RC-C | External validity check | Reviewer catches missing integration |
| RC-D | Wiring test mandated | At least one test through orchestrator |
| RC-E | Integration gate in DoD | Can't complete without working invocation |

### Cross-Validation

Root causes are independent and non-contradictory:
- RC-A (DISTILL) could catch issue at test design
- RC-B (ROADMAP) could catch issue at planning
- RC-C (REVIEW) could catch issue at approval
- RC-D (DEVELOP) could catch issue during implementation
- RC-E (FINALIZE) could catch issue at completion

All are valid interception points. None contradicts another.

### Completeness Check

| Phase | Had Opportunity? | Defense Held? | Gap Identified? |
|-------|------------------|---------------|-----------------|
| DISTILL | Yes | No | RC-A |
| ROADMAP | Yes | No | RC-B |
| REVIEW | Yes | No | RC-C |
| DEVELOP | Yes | No | RC-D |
| FINALIZE | Yes | No | RC-E |

All phases had opportunity to catch issue. All failed. Analysis is complete.

---

## Immediate Actions Required

### Action 1: Fix US-002 Integration (Bug Fix)

**Task**: Add orchestrator integration step to US-002
- Create acceptance test that invokes `DESOrchestrator.render_prompt()`
- Modify orchestrator to call `TemplateValidator.validate_prompt()`
- Block Task invocation if validation fails

**Owner**: DEVELOP wave team
**Priority**: High (feature is non-functional)

### Action 2: Update Process Documentation

**Task**: Document countermeasures CM-A through CM-E in:
- DISTILL wave checklist
- ROADMAP phase guidelines
- Review criteria
- Test policy
- Definition of Done

**Owner**: Process team
**Priority**: Medium (prevent recurrence)

### Action 3: Retrospective Review

**Task**: Review other recent features for same pattern:
- Tests at wrong boundary
- Missing integration steps
- High metrics, no working feature

**Owner**: Quality team
**Priority**: Medium (systemic risk)

---

## Appendix: Evidence References

| Evidence ID | File | Lines | Description |
|-------------|------|-------|-------------|
| E1 | test_us002_template_validation.py | 51, 104-105, 175-178 | Direct validator imports |
| E2 | des/orchestrator.py | N/A | No validator reference (grep empty) |
| E3 | roadmap.yaml | 201-207 | step_to_scenario_mapping |
| E4 | roadmap.yaml | 266-269 | Architecture notes mention integration |
| E5 | roadmap.yaml | 219-225 | Review criteria and approval |
| E6 | evolution doc | 499-507 | Integration as "next steps" |
| E7 | Test suite | N/A | 15/15 component tests, 0 wiring |

---

## Sign-Off

| Role | Name | Date |
|------|------|------|
| Root Cause Analyst | Sage (troubleshooter) | 2026-01-24 |
| Methodology | Toyota 5 Whys + Apollo RCA | - |
| Root Causes Identified | 5 | - |
| Countermeasures Proposed | 5 | - |

**Analysis Status**: COMPLETE

---

*This root cause analysis follows Toyota 5 Whys methodology with multi-causal investigation, evidence-based validation, and prevention-focused countermeasures.*
