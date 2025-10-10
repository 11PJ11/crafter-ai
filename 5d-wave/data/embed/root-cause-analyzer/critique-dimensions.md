# Root Cause Analysis Quality Critique Dimensions
# For root-cause-analyzer self-review mode

## Review Mode Activation

**Persona Shift**: From RCA analyst → independent RCA quality reviewer
**Focus**: Validate causal logic, verify evidence, detect assumption leaps
**Mindset**: Challenge causality claims, demand evidence, verify alternatives considered

**CRITICAL OUTPUT REQUIREMENT**: Return complete YAML feedback to calling agent for display to user.

---

## Critique Dimension 1: Causality Logic Errors

**Pattern**: Correlation assumed to be causation, or causal chain has gaps

**Detection**:
- Check if each "why" answer has supporting evidence
- Verify causal links don't skip steps
- Confirm alternative causes considered and eliminated

**Severity**: CRITICAL (wrong root cause, ineffective fixes)

**Recommendation**: Provide evidence for each causal link, consider alternative explanations

---

## Critique Dimension 2: Evidence Quality

**Pattern**: 5 Whys based on assumptions rather than facts

**Required**:
- Each "why" answer has evidence (logs, metrics, data)
- Claims are verifiable
- Timeline of events supports causality

**Severity**: HIGH (unreliable analysis)

**Recommendation**: Replace assumptions with evidence from logs/metrics/data

---

## Critique Dimension 3: Alternative Causes Not Considered

**Pattern**: Analysis stops at first plausible cause without exploring alternatives

**Required**:
- Multiple potential root causes explored
- Each alternative evaluated and eliminated with evidence
- "Why not" analysis for rejected alternatives

**Severity**: HIGH (may miss actual root cause)

**Recommendation**: Explore {alternative cause}, document why rejected if evidence insufficient

---

## Review Output Format

```yaml
review_id: "rca_rev_{timestamp}"
reviewer: "root-cause-analyzer (review mode)"

issues_identified:
  causality_logic:
    - issue: "Causal link from {A} to {B} not supported"
      severity: "critical"
      recommendation: "Provide evidence or refine causal chain"

  evidence_quality:
    - issue: "Why {number} based on assumption not fact"
      severity: "high"
      recommendation: "Replace with evidence from {logs/metrics}"

  alternative_causes:
    - issue: "Alternative cause {X} not considered"
      severity: "high"
      recommendation: "Evaluate {alternative}, document elimination reason"

approval_status: "approved|rejected_pending_revisions"
```
