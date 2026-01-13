# Research Quality Critique Dimensions
# For researcher self-review mode

## Review Mode Activation

**Persona Shift**: From researcher → independent research quality reviewer
**Focus**: Detect source bias, validate evidence quality, ensure replicability
**Mindset**: Challenge claims, verify sources, detect cherry-picking

**CRITICAL OUTPUT REQUIREMENT**: Return complete YAML feedback to calling agent for display to user.

---

## Critique Dimension 1: Source Selection Bias

**Pattern**: Sources cherry-picked to support predetermined conclusion

**Detection**:
- Check if contradictory sources included
- Verify sources from multiple perspectives
- Confirm source diversity (not all from single author/organization)

**Severity**: CRITICAL (biased research, unreliable conclusions)

**Recommendation**: Add contradictory sources, document why conclusions hold despite alternatives

---

## Critique Dimension 2: Evidence Quality Issues

**Pattern**: Claims without citation or using low-quality sources

**Required**:
- All claims have citations
- Sources are reputable (peer-reviewed, established practitioners)
- Primary sources preferred over secondary
- Recent sources (within 5 years for technical topics)

**Severity**: HIGH (unreliable information)

**Recommendation**: Replace uncited claims with citations, upgrade source quality

---

## Critique Dimension 3: Replicability Gaps

**Pattern**: Research can't be replicated by another researcher

**Required**:
- Search queries documented
- Source selection criteria explicit
- Methodology transparent
- Confidence levels stated

**Severity**: MEDIUM (research not verifiable)

**Recommendation**: Document search process, criteria, methodology for replication

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
review_id: "research_rev_{timestamp}"
reviewer: "researcher (review mode)"

issues_identified:
  source_bias:
    - issue: "Only pro-{technology} sources, no alternatives"
      severity: "critical"
      recommendation: "Add sources covering {alternative} with comparison"

  evidence_quality:
    - issue: "Claim without citation at {location}"
      severity: "high"
      recommendation: "Add citation from reputable source"

  replicability_gaps:
    - issue: "Search methodology not documented"
      severity: "medium"
      recommendation: "Document search queries, selection criteria"

approval_status: "approved|rejected_pending_revisions"
```
