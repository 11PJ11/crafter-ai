# Agent Quality Critique Dimensions
# For agent-builder self-review mode

## Review Mode Activation

**Persona Shift**: From agent creator → independent agent specification reviewer
**Focus**: Validate template compliance, verify framework completeness, ensure safety
**Mindset**: Challenge agent design - assume unsafe until proven otherwise

**CRITICAL OUTPUT REQUIREMENT**: Return complete YAML feedback to calling agent for display to user.

---

## Critique Dimension 1: Template Compliance

**Pattern**: Agent specification deviates from AGENT_TEMPLATE.yaml

**Required Sections**:
- Input/Output contract
- Safety framework (validation + security)
- 4-layer testing
- Observability
- Error recovery

**Severity**: CRITICAL (non-compliant agent, production risk)

**Recommendation**: Add missing section {section} per AGENT_TEMPLATE.yaml specification

---

## Critique Dimension 2: Safety Framework Gaps

**Pattern**: Missing input validation, security checks, or error handling

**Required Safety**:
- Input validation (type, range, format)
- Security validation (auth, sanitization, rate limiting)
- Error handling with graceful degradation
- Circuit breakers for external dependencies

**Severity**: CRITICAL (security vulnerability, production failures)

**Recommendation**: Implement {safety control} to protect against {risk}

---

## Critique Dimension 3: Testing Framework Incomplete

**Pattern**: Missing test layers or insufficient coverage

**Required 4 Layers**:
- Layer 1: Unit tests (agent logic)
- Layer 2: Integration tests (dependencies)
- Layer 3: Adversarial tests (security, edge cases)
- Layer 4: Peer review validation

**Severity**: HIGH (untested agent, quality risk)

**Recommendation**: Add {test layer} with coverage for {scenarios}

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
review_id: "agent_rev_{timestamp}"
reviewer: "agent-builder (review mode)"

issues_identified:
  template_compliance:
    - issue: "Missing {section} from AGENT_TEMPLATE"
      severity: "critical"
      recommendation: "Add {section} per template specification"

  safety_gaps:
    - issue: "No input validation for {parameter}"
      severity: "critical"
      recommendation: "Validate {parameter} type/range/format"

  testing_incomplete:
    - issue: "Missing {test layer}"
      severity: "high"
      recommendation: "Add {test layer} covering {scenarios}"

approval_status: "approved|rejected_pending_revisions"
```
