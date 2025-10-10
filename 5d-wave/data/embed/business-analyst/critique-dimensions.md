# Requirements Quality Critique Dimensions
# For business-analyst self-review mode

## Review Mode Activation Instructions

When invoked in review mode, apply these critique dimensions to requirements documents.

**Persona Shift**: From requirements analyst → independent requirements reviewer
**Focus**: Detect confirmation bias, validate completeness, ensure clarity and testability
**Mindset**: Fresh perspective - assume nothing, challenge assumptions, verify stakeholder needs

**CRITICAL OUTPUT REQUIREMENT**: Return complete YAML feedback to calling agent for display to user. NO HIDDEN REVIEWS.

---

## Critique Dimension 1: Confirmation Bias Detection

### Technology Bias

**Pattern**: Requirements assume specific technology without stakeholder requirement

**Examples**:
- "System will be deployed to AWS cloud" when deployment not discussed with stakeholders
- "Use PostgreSQL database" in requirements instead of architecture
- "RESTful API" when integration method not specified by stakeholders
- "React frontend" when UI technology stakeholder-neutral

**Detection Method**:
- Check requirements for technology specifics (cloud, database, frameworks)
- Verify stakeholder interviews mentioned deployment/technology constraints
- Confirm technology choices belong in architecture, not requirements

**Severity**: HIGH (constrains solution space unnecessarily)

**Recommendation Template**:
```
Technology bias: Requirement assumes {technology} without stakeholder specification.
Revise to technology-neutral: "{functional requirement without implementation}".
Move technology choice to architecture phase with ADR justification.
```

---

### Happy Path Bias

**Pattern**: Requirements focus on successful scenarios, minimal error/exception coverage

**Examples**:
- User login documented but account lockout scenarios missing
- Payment processing success covered but fraud, timeout, decline not specified
- Data import happy path but malformed data handling absent
- Search results shown but empty results, timeouts not addressed

**Detection Method**:
- Count happy path user stories vs error scenario stories
- Check if each user story has "sad path" alternatives
- Verify edge cases and exceptions documented

**Severity**: CRITICAL (incomplete requirements, production error handling missing)

**Recommendation Template**:
```
Happy path bias: User story {US-ID} lacks error scenarios.
Add scenarios: {error condition 1}, {error condition 2}, {edge case}.
Ensure each user story covers success AND failure paths.
```

---

### Availability Bias

**Pattern**: Requirements reflect recent experiences or familiar patterns over comprehensive analysis

**Examples**:
- "Use same authentication as previous project" without validating fit
- Requirements mirror competitor product without stakeholder validation
- Assuming current process must be preserved digitally

**Detection Method**:
- Check if requirements justified by stakeholder needs or "like previous project"
- Verify assumptions validated with actual stakeholders
- Confirm requirements solve stated problem, not replicate familiar solutions

**Severity**: MEDIUM (sub-optimal solution, missed opportunities)

**Recommendation Template**:
```
Availability bias: Requirement based on {previous project/competitor} not stakeholder need.
Re-elicit: Validate requirement {ID} with stakeholders - is this actually needed?
Focus on problem to solve, not familiar solution to replicate.
```

---

## Critique Dimension 2: Completeness Validation

### Missing Stakeholder Perspectives

**Pattern**: Requirements don't represent all stakeholder groups

**Stakeholder Groups to Verify**:
- End users (primary, secondary, occasional)
- Business owners/sponsors
- Operations/support teams
- Compliance/legal (if regulated)
- Technical teams (deployment, maintenance)

**Detection Method**:
- List stakeholder groups identified in requirements
- Check if each group's needs represented
- Verify conflicting needs documented and resolved

**Severity**: HIGH (incomplete requirements, stakeholder dissatisfaction)

**Recommendation Template**:
```
Missing stakeholder perspective: {stakeholder group} needs not documented.
Interview {stakeholder group}, document requirements from their perspective.
Resolve conflicts between {group1} and {group2} with stakeholder prioritization.
```

---

### Missing Error Scenarios

**Pattern**: Error handling, exceptions, and failure modes not specified

**Required Error Scenarios**:
- Invalid input validation
- Authentication/authorization failures
- Network timeouts and connectivity issues
- External service unavailability
- Data integrity violations
- Concurrent modification conflicts
- Resource exhaustion (rate limits, quotas)

**Detection Method**:
- For each user story, check for corresponding error scenarios
- Verify user stories cover validation failures
- Confirm timeout/unavailability handling specified

**Severity**: CRITICAL (production error handling undefined)

**Recommendation Template**:
```
CRITICAL: Missing error scenarios for {feature}.
Add user stories: Handle {error type 1}, {error type 2}, {edge case}.
Each user story needs: GIVEN error condition WHEN action THEN expected handling.
```

---

### Missing Non-Functional Requirements

**Pattern**: Functional requirements documented but quality attributes absent

**NFRs to Validate**:
- Performance (latency, throughput targets)
- Security (authentication, authorization, data protection)
- Scalability (concurrent users, data volume)
- Reliability (uptime, error rates)
- Compliance (regulatory, legal, audit)
- Accessibility (WCAG, screen readers)

**Detection Method**:
- Check if NFRs section exists and is comprehensive
- Verify each NFR has measurable criteria
- Confirm stakeholders provided performance/security expectations

**Severity**: CRITICAL (system won't meet quality expectations)

**Recommendation Template**:
```
CRITICAL: Non-functional requirement missing - {NFR type}.
Elicit from stakeholders: {specific questions about performance/security/scale}.
Document with measurable criteria: "{NFR} must achieve {quantifiable target}".
```

---

## Critique Dimension 3: Clarity and Measurability

### Vague Performance Requirements

**Pattern**: Qualitative performance terms without quantitative thresholds

**Vague Examples**:
- "System should be fast"
- "User-friendly interface"
- "Handle large volumes"
- "Highly available"
- "Secure system"

**Detection Method**:
- Identify qualitative adjectives: fast, large, friendly, high, secure
- Check if corresponding quantitative threshold specified
- Verify measurement method defined

**Severity**: HIGH (un-testable requirements, ambiguous expectations)

**Recommendation Template**:
```
Vague requirement: "{vague statement}" not measurable.
Quantify: "System responds to {action} within {X seconds} for {percentile} of requests".
Add measurement method: {how to verify compliance}.
```

---

### Ambiguous Requirements

**Pattern**: Requirements interpretable multiple ways by different readers

**Detection Method**:
- Check if two architects could design differently from same requirements
- Look for words with multiple meanings: "user", "system", "process"
- Verify pronouns have clear antecedents
- Confirm requirements specify "what" not "how"

**Severity**: HIGH (inconsistent understanding, rework)

**Recommendation Template**:
```
Ambiguous requirement at {location}: "{ambiguous text}".
Clarify: Specify exact behavior - GIVEN {context} WHEN {action} THEN {single clear outcome}.
Remove ambiguity: Replace "{vague term}" with "{specific definition}".
```

---

## Critique Dimension 4: Testability

### Non-Testable Acceptance Criteria

**Pattern**: Acceptance criteria not observable, measurable, or automatable

**Examples**:
- "System should be easy to use" (not observable)
- "Code should be maintainable" (not measurable)
- "Architecture should be clean" (subjective)

**Testable Alternatives**:
- "User completes checkout in ≤3 clicks, 95% success rate in usability testing"
- "Code has cyclomatic complexity ≤10, test coverage ≥80%"
- "Architecture passes 12-factor app checklist"

**Detection Method**:
- For each AC, ask: Can automated test verify this?
- Check if AC specifies observable system behavior
- Verify AC has measurable pass/fail criteria

**Severity**: CRITICAL (requirements can't be validated)

**Recommendation Template**:
```
CRITICAL: Acceptance criterion "{AC}" not testable.
Revise to observable behavior: GIVEN {context} WHEN {action} THEN {measurable outcome}.
Specify pass/fail criteria: {how to verify AC met}.
```

---

## Review Output Format (MANDATORY)

```yaml
review_id: "req_rev_{YYYYMMDD_HHMMSS}"
reviewer: "business-analyst (review mode)"
artifact: "docs/requirements/requirements.md"
iteration: {1 or 2}

strengths:
  - "{Positive aspect - e.g., comprehensive stakeholder coverage}"

issues_identified:
  confirmation_bias:
    - issue: "{Specific bias detected - technology/happy path/availability}"
      severity: "critical|high|medium|low"
      location: "{Section or US-ID}"
      recommendation: "{How to address bias - re-elicit, add scenarios}"

  completeness_gaps:
    - issue: "{Missing stakeholder/scenario/NFR}"
      severity: "critical|high"
      location: "{Section missing content}"
      recommendation: "{What to add - specific stakeholder interviews, error scenarios}"

  clarity_issues:
    - issue: "{Vague or ambiguous requirement}"
      severity: "high"
      location: "{Requirement ID or section}"
      recommendation: "{Quantify with numbers, clarify with specific language}"

  testability_concerns:
    - issue: "{Acceptance criterion not testable}"
      severity: "critical"
      location: "{AC-ID}"
      recommendation: "{Revise to observable/measurable behavior}"

approval_status: "approved|rejected_pending_revisions|conditionally_approved"
critical_issues_count: {number}
high_issues_count: {number}
```

---

## Severity Classification

**Critical**: Non-testable AC, missing critical error scenarios, missing NFRs
**High**: Technology bias, happy path bias, vague requirements, missing stakeholders
**Medium**: Availability bias, minor completeness gaps, ambiguous wording
**Low**: Documentation formatting, terminology consistency
