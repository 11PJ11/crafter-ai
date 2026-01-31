# Roadmap Prioritization Anti-Patterns

Documented from incident ROADMAP-2025-12-03-001.
Reference: docs/agent-improvements/2025-12-03_roadmap-prioritization-lessons.md

## Anti-Pattern 1: Architecture Before Measurement

**Description:** Creating detailed solution architecture without quantitative problem analysis.

**Warning Signs:**
- Roadmap has "establish baseline" step AFTER solution is designed
- Acceptance criteria defined without current state measurement
- "Research" phase asks about implementation details, not problem scope

**Example (WRONG):**
```yaml
phases:
  - name: "Acceptance Test Definition"  # Defining WHAT to build
  - name: "Research"  # Finally measuring, but architecture already implied
```

**Correct Pattern:**
```yaml
phases:
  - name: "Baseline Measurement"  # FIRST: What's the problem?
  - name: "Solution Design"  # SECOND: Design based on data
```

**Prevention:** Pre-Planning Measurement Gate (BLOCKING)

---

## Anti-Pattern 2: Constraint-Anchored Architecture

**Description:** Allowing a user-mentioned constraint to dominate solution design regardless of its actual impact.

**Warning Signs:**
- Solution architecture named after the constraint
- No quantification of constraint impact (percentage)
- No "what if we ignored this constraint?" analysis

**Example (WRONG):**
```
User mentioned: "SISTER single-session constraint"
Result: Entire 34-step roadmap organized around credential isolation
Reality: Constraint affects only 20% of the problem
```

**Correct Pattern:**
```markdown
## Constraint Impact Analysis

| Constraint | % Problem Affected | Priority |
|------------|-------------------|----------|
| SISTER single-session | 20% | SECONDARY |
| Test isolation (general) | 80% | PRIMARY |

Architecture should address 80% problem first.
```

**Prevention:** Constraint Prioritization Framework

---

## Anti-Pattern 3: Comprehensiveness Over Correctness

**Description:** Measuring roadmap quality by detail and completeness rather than problem-solution fit.

**Warning Signs:**
- Pride in roadmap length/detail
- Reviews focus on "are steps complete?" not "is this the right problem?"
- No "sanity check" step asking "should we do this at all?"

**Example (WRONG):**
- 34 steps with detailed TDD cycles
- 1300+ lines of review feedback
- Multiple sophisticated abstractions
- ALL addressing the wrong problem

**Correct Pattern:**
```markdown
## Roadmap Validation Checklist

Before detailed planning:
- [ ] Problem is quantified (timing data)
- [ ] This is the LARGEST bottleneck
- [ ] Simpler solutions are insufficient (documented)
- [ ] Proposed approach achieves meaningful improvement (calculated)

Only proceed to detailed steps if ALL boxes checked.
```

**Prevention:** Priority Validation dimension in reviews

---

## Anti-Pattern 4: Qualitative Research Masquerading as Analysis

**Description:** Categorizing and describing without quantifying impact.

**Warning Signs:**
- Categories described by type (SISTER/non-SISTER) not by impact (5 min / 30 sec)
- "Identified tests" without timing data
- Research outputs feed directly to implementation without prioritization

**Example (WRONG):**
```yaml
research_findings:
  categories:
    - name: "Integration.Infrastructure"
      sister_dependency: false
      # Missing: How long does this take? What % of total?
```

**Correct Pattern:**
```yaml
research_findings:
  categories:
    - name: "Integration.Infrastructure"
      test_count: 45
      execution_time: "4m 30s"
      percent_of_total: "51%"
      parallelization_impact: "Saves ~3m with simple config change"
```

**Prevention:** Quantitative Research Requirements

---

## Anti-Pattern 5: Missing Escape Hatch

**Description:** No mechanism to question fundamental assumptions mid-roadmap.

**Warning Signs:**
- Review dimensions all focus on execution quality
- No "premise validation" or "priority check" dimension
- Reviewers assume roadmap goal is correct

**Example (WRONG):**
- Reviews asked "are steps complete?" and "are patterns correct?"
- No review asked "should we be doing this at all?"
- Reviewers improved the roadmap quality without questioning its premise

**Correct Pattern:**
```yaml
review_dimensions:
  premise_validation:  # NEW: Question the goal
    questions:
      - "Is this the most impactful problem to solve?"
      - "Does data support this priority?"
      - "What are we NOT doing by doing this?"
```

**Prevention:** Priority Validation dimension (Q1-Q4)

---

### Anti-Pattern 6: Scenario-Driven Over-Decomposition

**Warning**: Creating one implementation step per acceptance test scenario leads to 30-50% no-op steps where the GREEN phase adds zero production code.

**Symptoms**:
- Step count >> production file count (ratio > 2.5:1)
- Multiple steps targeting the same production file
- Steps named "Verify X works" or "Validate Y behavior"
- GREEN phase completes instantly because code already exists
- REFACTOR_CONTINUOUS frequently skipped ("no refactoring needed")

**Root Cause**: Confusing test scenarios (what to verify) with implementation units (what to build). Acceptance test scenarios describe BEHAVIORS to validate, not units of work to implement.

**Real Example (US-008)**: 13 steps for 4 production files (ratio 3.25). 5 of 13 steps (38%) were no-ops where all production code already existed from prior steps.

**Fix**: Group steps by implementation unit. One step = one cohesive unit of production code. Multiple acceptance criteria can be verified within a single step.

**Detection During Review**:
```
steps_count / estimated_production_files > 2.5 → FLAG
validation_only_steps / total_steps > 0.20 → REJECT
```

**Prevention**: Apply decomposition principle #6 from roadmap.md: "Decompose by IMPLEMENTATION UNIT, not by test scenario"
