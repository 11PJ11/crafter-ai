# Code Quality Critique Dimensions
# For software-crafter self-review mode

## Review Mode Activation Instructions

When invoked in review mode, apply these critique dimensions to production code and tests.

**Persona Shift**: From implementer (build solutions) → independent peer reviewer (critique solutions)
**Focus**: Detect implementation bias, test quality issues, acceptance criteria coverage gaps
**Mindset**: Fresh perspective with critical analysis - assume nothing, verify everything

**CRITICAL OUTPUT REQUIREMENT**: Return complete YAML feedback to calling agent for display to user. NO HIDDEN REVIEWS.

---

## Critique Dimension 1: Implementation Bias Detection

### Over-Engineering (YAGNI Violations)

**Pattern**: Features, abstractions, or infrastructure without corresponding acceptance criteria

**Examples**:
- Caching layer implemented without performance AC
- Generic framework/abstraction for single use case
- Premature abstraction before Rule of Three (need 3 instances before abstracting)
- Design patterns applied without demonstrated complexity need
- Infrastructure (queues, workers, microservices) without scale requirement

**Detection Method**:
- Compare implementation against acceptance criteria
- Check if feature requested by stakeholder or assumed by developer
- Verify performance requirements exist before optimization
- Validate abstractions serve 3+ concrete cases
- Look for speculative future-proofing

**Severity**: Medium to High (adds complexity, maintenance burden, slows delivery)

**Recommendation Template**:
```
Remove {feature} until acceptance criteria prove need. Current AC do not specify {capability}.
Apply YAGNI - implement only what AC require. Add when future AC demand it.
```

---

### Premature Optimization

**Pattern**: Performance optimization without measurement proving necessity

**Examples**:
- Custom caching without latency tests showing sub-optimal performance
- Complex O(log n) algorithms when simple O(n) meets AC
- Memory optimizations without profiling data showing excessive usage
- Database denormalization without query analysis proving slow reads
- Asynchronous processing without throughput AC

**Detection Method**:
- Check for performance tests validating optimization benefit
- Verify AC specify performance thresholds requiring optimization
- Look for profiling/benchmark data justifying added complexity
- Confirm optimization addresses measured bottleneck

**Severity**: Medium (premature complexity, harder maintenance)

**Recommendation Template**:
```
Simplify to straightforward implementation. Add performance tests first.
If tests fail AC thresholds, THEN optimize with measurement-driven approach.
```

---

### Solving Assumed Problems

**Pattern**: Implementing solutions for problems not in acceptance criteria

**Examples**:
- Multi-tenancy support when AC specify single-tenant
- Internationalization when AC require English only
- Audit logging when AC don't mention compliance
- Complex error recovery when AC specify fail-fast

**Detection Method**:
- Map each implementation feature to corresponding AC
- Flag features without AC traceability
- Verify stakeholder requested capability

**Severity**: Medium to High (scope creep, wasted effort)

**Recommendation Template**:
```
Remove {feature} - not in acceptance criteria. If stakeholders need it, they will add AC.
Focus on delivering specified requirements with quality.
```

---

## Critique Dimension 2: Test Quality Validation

### Implementation Coupling (Critical Issue)

**Pattern**: Tests know or depend on implementation details, preventing refactoring

**Examples**:
- Mocking domain objects or application services (violates port-boundary test doubles policy)
- Test asserts on private methods, fields, or internal state
- Test breaks on refactoring despite behavior unchanged
- Test duplicates production logic to verify correctness
- Test knows class structure, method names, internal collaborations

**Detection Method**:
- Check if mocks used inside hexagon (domain/application layers) - VIOLATION
- Verify tests call only public interfaces (API, commands, queries)
- Confirm tests validate observable behavior, not implementation
- Check if refactoring Extract Method would break tests - if yes, COUPLED

**Severity**: CRITICAL (prevents refactoring, blocks continuous improvement)

**Recommendation Template**:
```
CRITICAL: Test coupled to implementation at {location}.
Replace mock with real object - {class} is {domain|application} layer, not port.
Test through public API only - remove assertions on {private method/field}.
Refactor test to validate behavior: GIVEN {context} WHEN {action} THEN {observable outcome}.
```

---

### Shared Mutable State (High Severity)

**Pattern**: Tests share state causing flakiness, order dependencies, parallel execution failures

**Examples**:
- Database state not reset between tests
- Static variables mutated across tests
- File system state persists between tests
- In-memory caches shared across test methods
- Test execution order matters for passing

**Detection Method**:
- Run tests in random order - do they still pass?
- Run tests in parallel - do they fail?
- Check for test setup/teardown creating isolated state
- Look for static fields, shared fixtures, class-level state

**Severity**: HIGH (flaky tests, CI failures, unreliable test suite)

**Recommendation Template**:
```
Tests share mutable state - causes flakiness.
Each test MUST create and destroy own state in setup/teardown.
Isolate: {specific shared resource} - make per-test instance.
Verify tests pass when run in random order and parallel.
```

---

### Port-Boundary Violations

**Pattern**: Mocking domain/application objects instead of only ports (hexagon boundaries)

**Acceptable Mocks** (Port Boundaries Only):
- `Mock<IPaymentGateway>` - External payment service port
- `Mock<IEmailService>` - External email provider port
- `Mock<IDatabaseRepository>` - Infrastructure persistence port
- `Mock<IMessageQueue>` - External messaging port

**VIOLATIONS** (Must Use Real Objects):
- `Mock<Order>` - Domain entity, use real: `new Order(id, customerId)`
- `Mock<OrderProcessor>` - Application service, use real with mocked ports
- `Mock<Money>` - Value object, cheap to create, use real
- `Mock<OrderValidator>` - Domain service, use real

**Detection Method**:
- Check mocks in tests - are they domain/application classes?
- Verify mocks only for interfaces in infrastructure/ports layer
- Confirm domain and application use real objects

**Severity**: HIGH to CRITICAL (test coupling, prevents refactoring)

**Recommendation Template**:
```
Port-boundary violation: {Mock<DomainClass>} at {location}.
{DomainClass} is {domain entity|value object|application service} - use real object.
Only mock at ports: {IPortInterface} for external system integration.
```

---

## Critique Dimension 3: Completeness Validation

### Missing Acceptance Criteria Coverage

**Pattern**: Not all acceptance criteria have corresponding test coverage

**Examples**:
- AC-7 "Handle concurrent payments" - no concurrency test
- AC-12 "Validate against fraud rules" - no fraud test cases
- Error scenarios incompletely covered (only happy path tested)
- Edge cases missing: boundary values, null, empty, malformed input
- Non-functional AC not tested: performance, security, scalability

**Detection Method**:
- Map each acceptance criterion to test cases
- Check coverage report shows 100% AC mapped to tests
- Verify error paths have test coverage
- Confirm edge cases explicitly tested

**Severity**: CRITICAL (untested AC = production bugs, unverified requirements)

**Recommendation Template**:
```
CRITICAL: Acceptance criterion {AC-ID} "{AC description}" not tested.
Add test case: GIVEN {context} WHEN {action} THEN {expected outcome per AC}.
Ensure 100% AC coverage before handoff.
```

---

### Inadequate Error Scenario Coverage

**Pattern**: Only happy path tested, error handling untested

**Examples**:
- No test for network timeout during payment
- No test for database unavailable
- No test for invalid input validation
- No test for business rule violations
- No test for concurrent modification conflicts

**Detection Method**:
- Count happy path vs error path tests
- Check if error handling code has test coverage
- Verify each exception type has test triggering it

**Severity**: HIGH (error handling bugs in production)

**Recommendation Template**:
```
Error scenario not tested: {scenario description}.
Add test: GIVEN {error condition} WHEN {action} THEN {expected error handling}.
Verify all exception types thrown in code have test coverage.
```

---

## Code Readability Issues

### Compose Method Violations

**Pattern**: Long methods doing multiple things instead of composed small methods

**Detection**:
- Methods longer than 10 lines (guideline)
- Multiple levels of indentation (nested logic)
- Comments explaining "what" instead of "why"
- Method name doesn't reveal full intent

**Severity**: LOW to MEDIUM (maintainability, understandability)

**Recommendation Template**:
```
Method {name} at {location} violates Compose Method pattern.
Extract intention-revealing methods: {suggested method names}.
Remove comments explaining "what" - method names should reveal intent.
```

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

## Review Output Format (MANDATORY)

**Every review MUST return YAML in this exact format**:

```yaml
review_id: "code_rev_{YYYYMMDD_HHMMSS}"
reviewer: "software-crafter (review mode)"
artifact: "{file paths reviewed}"
iteration: {1 or 2}

strengths:
  - "{Specific positive observation with file:line reference}"
  - "{Another strength with concrete example}"

issues_identified:
  implementation_bias:
    - issue: "{Specific over-engineering pattern detected}"
      severity: "critical|high|medium|low"
      location: "{file:line-range}"
      recommendation: "{Actionable fix - what to remove/simplify}"

    - issue: "{Premature optimization detected}"
      severity: "medium"
      location: "{file:line}"
      recommendation: "{Remove optimization, add performance test first}"

  test_quality:
    - issue: "{Test coupling to implementation detail}"
      severity: "critical"
      location: "{test_file:line}"
      recommendation: "{Replace mock with real object, test through public API}"

    - issue: "{Shared mutable state between tests}"
      severity: "high"
      location: "{test_file:line}"
      recommendation: "{Isolate state - per-test setup/teardown}"

  completeness:
    - issue: "{Acceptance criterion not tested}"
      severity: "critical"
      location: "Missing test for AC-{number}"
      recommendation: "{Add test: GIVEN... WHEN... THEN... per AC}"

  code_readability:
    - issue: "{Compose method violation}"
      severity: "low"
      location: "{file:line}"
      recommendation: "{Extract methods: {method names}}"

approval_status: "approved|rejected_pending_revisions|conditionally_approved"
critical_issues_count: {number}
high_issues_count: {number}
medium_issues_count: {number}
low_issues_count: {number}
```

---

## Severity Classification Rules

**Critical** (MUST resolve before handoff):
- Test coupling to implementation (prevents refactoring)
- Missing acceptance criteria test coverage (unverified requirements)
- Port-boundary violations in critical paths

**High** (Strongly recommend resolving):
- Shared mutable state in tests (flaky tests)
- Major over-engineering (significant complexity added)
- Inadequate error scenario coverage

**Medium** (Should address if time permits):
- Premature optimization (unnecessary complexity)
- Solving assumed problems (scope creep)
- Minor test quality issues

**Low** (Enhancement suggestions, optional):
- Code readability improvements
- Minor compose method violations
- Naming improvements

---

## Review Iteration Rules

**Iteration 1**: Comprehensive review with all critique dimensions
**Iteration 2** (if needed): Verify critical/high issues resolved, check for new issues
**Max Iterations**: 2
**Escalation**: If not approved after 2 iterations, escalate to human facilitator

---

## Output to Calling Agent

**CRITICAL**: Return this YAML to calling agent so it can display to user.

The calling agent MUST show this review output to user as proof review occurred.

No hidden reviews allowed - transparency required for quality gate accountability.
