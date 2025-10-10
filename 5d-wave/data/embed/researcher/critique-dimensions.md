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
