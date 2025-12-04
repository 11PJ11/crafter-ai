# Acceptance Test Quality Critique Dimensions
# For acceptance-designer self-review mode

## Review Mode Activation

**Persona Shift**: From test designer → independent test quality reviewer
**Focus**: Detect happy path bias, validate GWT format, ensure business language purity, verify coverage
**Mindset**: Critical analysis - assume tests incomplete until proven comprehensive

**CRITICAL OUTPUT REQUIREMENT**: Return complete YAML feedback to calling agent for display to user.

---

## Critique Dimension 1: Happy Path Bias

**Pattern**: Tests only cover successful scenarios, error paths missing

**Examples**:
- Login success tested but invalid password not covered
- Payment processing tested but decline/timeout/fraud scenarios missing
- Search results tested but empty results, errors, pagination edge cases absent

**Detection**: Count success vs error scenario tests - should be roughly balanced

**Severity**: CRITICAL (production error handling untested)

**Recommendation**: Add error scenarios for each feature - minimum 50% of tests should cover failure paths

---

## Critique Dimension 2: GWT Format Compliance

**Pattern**: Scenarios don't follow strict Given-When-Then structure or use technical language

**Violations**:
- Missing GIVEN context setup
- Multiple WHEN actions (should be single action per scenario)
- THEN with technical assertions instead of business outcomes

**Detection**: Verify each scenario has GIVEN (context), WHEN (single action), THEN (observable outcome)

**Severity**: HIGH (tests not behavior-driven, coupled to implementation)

**Recommendation**: Refactor to strict GWT, single action per scenario, business language only

---

## Critique Dimension 3: Business Language Purity

**Pattern**: Technical terms leak into acceptance tests

**Technical Terms to Avoid**:
- Database, API, HTTP, REST, JSON
- Classes, methods, services, controllers
- Technical error codes (500, 404)
- Infrastructure terms (Redis, Kafka, Lambda)

**Business Alternatives**:
- "Customer data is stored" not "Database persists record"
- "Order is confirmed" not "API returns 200 OK"
- "Payment fails" not "Gateway throws exception"

**Severity**: HIGH (tests coupled to implementation, not stakeholder-readable)

**Recommendation**: Replace all technical terms with business domain language

---

## Critique Dimension 4: Coverage Completeness

**Pattern**: Not all user stories have acceptance tests

**Validation**:
- Map each user story to acceptance test scenarios
- Verify all acceptance criteria have corresponding tests
- Confirm edge cases and boundaries tested

**Severity**: CRITICAL (unverified requirements, production bugs)

**Recommendation**: Add missing scenarios - ensure 100% user story to test traceability

---

## Critique Dimension: Priority Validation (CRITICAL)

### Purpose
Validate that the roadmap/artifact addresses the LARGEST bottleneck first,
not a secondary concern that happened to be salient.

**This dimension catches the "wrong problem" anti-pattern.**

### Questions to Ask

**Q1: Is this the largest bottleneck?**
- Does timing data show this is the PRIMARY problem?
- Is there a larger problem being ignored?
- Evidence: {timing data or "NOT PROVIDED" - flag if missing}
- Assessment: YES / NO / UNCLEAR

**Q2: Were simpler alternatives considered?**
- Does roadmap include "Rejected Simple Alternatives" section?
- Are rejection reasons specific and evidence-based?
- Could a simpler solution achieve 80% of the benefit?
- Assessment: ADEQUATE / INADEQUATE / MISSING

**Q3: Is constraint prioritization correct?**
- Are user-mentioned constraints quantified by impact?
- Does architecture address constraint-FREE opportunities first?
- Is a minority constraint dominating the solution? (flag if >50% of solution for <30% of problem)
- Assessment: CORRECT / INVERTED / NOT_ANALYZED

**Q4: Is architecture data-justified?**
- Is the key architectural decision supported by quantitative data?
- Would different data lead to different architecture?
- Assessment: JUSTIFIED / UNJUSTIFIED / NO_DATA

### Severity
- **CRITICAL** if roadmap addresses secondary concern while larger exists
- **HIGH** if no measurement data provided
- **HIGH** if simple alternatives not documented
- **MEDIUM** if constraint prioritization not explicit

### Output Template
```yaml
priority_validation:
  q1_largest_bottleneck:
    evidence: "{timing data or 'NOT PROVIDED'}"
    assessment: "YES|NO|UNCLEAR"
    concern: "{specific concern if NO/UNCLEAR}"

  q2_simple_alternatives:
    alternatives_documented: ["list or 'NONE'"]
    rejection_justified: "YES|NO|MISSING"
    assessment: "ADEQUATE|INADEQUATE|MISSING"

  q3_constraint_prioritization:
    constraints_quantified: "YES|NO"
    constraint_free_first: "YES|NO|NA"
    minority_constraint_dominating: "YES|NO"
    assessment: "CORRECT|INVERTED|NOT_ANALYZED"

  q4_data_justified:
    key_decision: "{main architectural decision}"
    supporting_data: "{data or 'NONE'}"
    assessment: "JUSTIFIED|UNJUSTIFIED|NO_DATA"

  verdict: "PASS|FAIL"
  blocking_issues:
    - "{issue 1 if FAIL}"
```

### Failure Conditions
- **FAIL** if Q1 = NO (wrong problem being addressed)
- **FAIL** if Q2 = MISSING (no alternatives considered)
- **FAIL** if Q3 = INVERTED (minority constraint dominating)
- **FAIL** if Q4 = NO_DATA and this is performance optimization

### Recommendation if FAIL
```
Priority Validation FAILED: {reason}

This roadmap may address the wrong problem.

Recommended action:
1. Measure the actual problem (timing breakdown)
2. Identify the LARGEST bottleneck
3. Document why simple alternatives are insufficient
4. Re-design roadmap to address primary bottleneck first

Do NOT proceed with implementation until priority is validated.
```

---

## Review Output Format

```yaml
review_id: "accept_rev_{timestamp}"
reviewer: "acceptance-designer (review mode)"

issues_identified:
  happy_path_bias:
    - issue: "Feature {name} only tests success - no error scenarios"
      severity: "critical"
      recommendation: "Add scenarios: invalid input, timeout, external service failure"

  gwt_format_violations:
    - issue: "Scenario has multiple WHEN actions"
      severity: "high"
      recommendation: "Split into separate scenarios - one action each"

  business_language_purity:
    - issue: "Technical term '{term}' in scenario"
      severity: "high"
      recommendation: "Replace with business language: '{business alternative}'"

  coverage_gaps:
    - issue: "User story {US-ID} has no acceptance tests"
      severity: "critical"
      recommendation: "Create scenarios covering all AC for {US-ID}"

approval_status: "approved|rejected_pending_revisions"
```
