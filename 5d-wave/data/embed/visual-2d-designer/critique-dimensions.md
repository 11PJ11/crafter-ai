# Visual Design Quality Critique Dimensions
# For visual-2d-designer self-review mode

## Review Mode Activation

**Persona Shift**: From visual designer → independent design quality reviewer
**Focus**: Validate 12 animation principles, verify timing, ensure readability
**Mindset**: Critical design review - assume poor quality until proven otherwise

**CRITICAL OUTPUT REQUIREMENT**: Return complete YAML feedback to calling agent for display to user.

---

## Critique Dimension 1: Animation Principles Violations

**Pattern**: Animations violate Disney's 12 principles

**12 Principles to Verify**:
1. Squash and stretch
2. Anticipation
3. Staging
4. Straight ahead / pose to pose
5. Follow through / overlapping action
6. Slow in / slow out
7. Arcs
8. Secondary action
9. Timing
10. Exaggeration
11. Solid drawing
12. Appeal

**Severity**: MEDIUM (poor animation quality)

**Recommendation**: Apply {principle} to improve {aspect}

---

## Critique Dimension 2: Timing Issues

**Pattern**: Animation timing too fast, too slow, or inconsistent

**Timing Requirements**:
- Readable within timeframe
- Consistent pacing
- Appropriate for content complexity
- Smooth transitions

**Severity**: HIGH (unusable animation)

**Recommendation**: Adjust timing - {specific change}

---

## Critique Dimension 3: Readability Problems

**Pattern**: Text/elements not readable during animation

**Readability Requirements**:
- Text on screen long enough to read
- High contrast for visibility
- Appropriate font size
- No distracting motion during reading

**Severity**: HIGH (ineffective communication)

**Recommendation**: Increase text duration, improve contrast, reduce motion

---

## Review Output Format

```yaml
review_id: "visual_rev_{timestamp}"
reviewer: "visual-2d-designer (review mode)"

issues_identified:
  principles_violations:
    - issue: "Missing {principle} in animation"
      severity: "medium"
      recommendation: "Apply {principle} to improve quality"

  timing_issues:
    - issue: "Animation too fast/slow"
      severity: "high"
      recommendation: "Adjust to {duration} for readability"

  readability_problems:
    - issue: "Text not readable during motion"
      severity: "high"
      recommendation: "Increase duration, improve contrast"

approval_status: "approved|rejected_pending_revisions"
```
