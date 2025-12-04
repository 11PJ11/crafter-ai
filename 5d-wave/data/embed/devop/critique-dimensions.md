# Feature Completion Quality Critique Dimensions
# For devop self-review mode

## Review Mode Activation

**Persona Shift**: From completion coordinator → independent deployment readiness reviewer
**Focus**: Validate deployment readiness, verify phase completeness, ensure handoff quality
**Mindset**: Critical validation - assume nothing ready until proven

**CRITICAL OUTPUT REQUIREMENT**: Return complete YAML feedback to calling agent for display to user.

---

## Critique Dimension 1: Incomplete Phase Handoffs

**Pattern**: Phase handoffs missing required artifacts or approvals

**Required per Phase**:
- DISCUSS: Requirements document + peer review approval
- DESIGN: Architecture document + ADRs + peer review approval
- DISTILL: Acceptance tests + peer review approval
- DEVELOP: Production code + tests (100% passing) + peer review approval

**Severity**: CRITICAL (incomplete deliverables, quality gate bypass)

**Recommendation**: Verify all artifacts present and peer-reviewed before phase transition

---

## Critique Dimension 2: Deployment Readiness Gaps

**Pattern**: Feature marked "ready" but missing production prerequisites

**Required**:
- All tests passing (100%)
- Production configuration complete
- Monitoring/alerting configured
- Runbook/operational docs created
- Rollback plan documented

**Severity**: CRITICAL (production deployment risk)

**Recommendation**: Complete missing prerequisite {item} before marking deployment-ready

---

## Critique Dimension 3: Traceability Violations

**Pattern**: Can't trace production code back to requirements

**Required**:
- User stories map to acceptance tests
- Acceptance tests map to production code
- Code changes traceable to commits
- All AC verified in production

**Severity**: HIGH (unverified requirements, compliance risk)

**Recommendation**: Establish traceability: {US-ID} → {AC-tests} → {code commits}

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
review_id: "completion_rev_{timestamp}"
reviewer: "devop (review mode)"

issues_identified:
  handoff_completeness:
    - issue: "Phase {name} missing {artifact}"
      severity: "critical"
      recommendation: "Complete {artifact} and obtain peer review"

  deployment_readiness:
    - issue: "Missing production {prerequisite}"
      severity: "critical"
      recommendation: "Complete {prerequisite} before deployment"

  traceability_gaps:
    - issue: "User story {US-ID} not traceable to code"
      severity: "high"
      recommendation: "Map {US-ID} → tests → commits"

approval_status: "approved|rejected_pending_revisions"
```
