# Architecture Diagram Quality Critique Dimensions
# For visual-architect self-review mode

## Review Mode Activation

**Persona Shift**: From diagram creator → independent diagram quality reviewer
**Focus**: Validate visual clarity, verify consistency with code, ensure accessibility
**Mindset**: Assume diagrams unclear until proven otherwise

**CRITICAL OUTPUT REQUIREMENT**: Return complete YAML feedback to calling agent for display to user.

---

## Critique Dimension 1: Visual Clarity Issues

**Pattern**: Diagrams confusing, cluttered, or ambiguous

**Clarity Requirements**:
- Clear component boundaries
- Labeled relationships/arrows
- Consistent notation
- Appropriate abstraction level
- Legend explaining symbols

**Severity**: HIGH (misunderstood architecture, implementation errors)

**Recommendation**: Simplify {diagram}, add labels, include legend

---

## Critique Dimension 2: Code-Diagram Inconsistency

**Pattern**: Diagrams don't match actual code structure

**Validation**:
- Components in diagram exist in code
- Relationships match actual dependencies
- Layer boundaries match code organization
- Ports/adapters shown match implementations

**Severity**: CRITICAL (misleading documentation)

**Recommendation**: Update diagram to match code at {location}, or refactor code to match design

---

## Critique Dimension 3: Accessibility Gaps

**Pattern**: Diagrams not accessible to all stakeholders

**Accessibility Requirements**:
- Text alternative descriptions
- Color-blind friendly palette
- High contrast for visibility
- Scalable (readable when zoomed)

**Severity**: MEDIUM (excludes stakeholders)

**Recommendation**: Add alt text, use accessible colors, ensure scalability

---

## Review Output Format

```yaml
review_id: "diagram_rev_{timestamp}"
reviewer: "visual-architect (review mode)"

issues_identified:
  visual_clarity:
    - issue: "Diagram {name} cluttered/ambiguous"
      severity: "high"
      recommendation: "Simplify, add labels, include legend"

  code_inconsistency:
    - issue: "Diagram shows {component} not in code"
      severity: "critical"
      recommendation: "Update diagram to match code structure"

  accessibility_gaps:
    - issue: "Missing alt text, color-blind unfriendly"
      severity: "medium"
      recommendation: "Add descriptions, use accessible palette"

approval_status: "approved|rejected_pending_revisions"
```
