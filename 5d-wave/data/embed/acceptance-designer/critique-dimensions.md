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
