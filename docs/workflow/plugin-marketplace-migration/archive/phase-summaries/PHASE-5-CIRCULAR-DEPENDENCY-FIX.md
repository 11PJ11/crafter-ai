# Phase 5 Circular Dependency Fix

**Date**: 2026-01-06
**Risk Score (Original)**: 8.5/10 CRITICAL BLOCKER
**Risk Score (Corrected)**: 4.5/10 MANAGEABLE
**Blast Radius Reduction**: ENTIRE_PROJECT → PHASE_5_ONLY

---

## Executive Summary

Phase 5 had a **CRITICAL CIRCULAR DEPENDENCY** that made the workflow unexecutable:

**Original (Broken) Flow:**
```
05-01 (CONDITIONAL_APPROVAL) →
05-02 (CONDITIONAL_APPROVAL) →
05-03 (CONDITIONAL_APPROVAL) →
05-04 (validates skills) ← CIRCULAR DEPENDENCY
```

**Problem**: Step 05-04 attempts to validate skills that have CONDITIONAL_APPROVAL status. Conditional approval means "not yet proven to work" - you cannot validate artifacts that don't exist or aren't proven functional.

**Solution**: Split 05-01 into two phases (Prerequisites + Implementation) and enforce sequential completion:

**Corrected Flow:**
```
05-01 Phase A (Prerequisites Resolution) →
05-01 Phase B (develop skill implementation) →
[05-02 (refactor skill) || 05-03 (mikado skill)] (parallel) →
05-04 (validation of PROVEN artifacts)
```

---

## Root Cause Analysis

### Why Circular Dependency Existed

1. **Steps 05-01, 05-02, 05-03** had CONDITIONAL_APPROVAL status because:
   - TOON v3.0 skill syntax undefined
   - Skill invocation mechanism undefined
   - Constraint embedding format undefined
   - Test environment for skill triggering undefined

2. **Step 05-04** depended on 05-01/05-02/05-03 but those steps weren't complete

3. **Circular Logic**:
   - "Validate skills" requires skills to exist
   - Skills can't be created without prerequisites
   - Prerequisites weren't in any step specification
   - Result: **validation before implementation paradox**

### Adversarial Review Findings

From `ADVERSARIAL_REVIEW_05-02_SUMMARY.md` (risk 8.2/10):
- "Step 05-02 has CRITICAL BLOCKERS that prevent implementation from starting"
- "Cannot implement without resolving 6 blocking dependencies from step 05-01"
- "Recommendation: DO NOT START step 05-02. Block implementation until 05-01 gaps are resolved."

From step 05-04 adversarial review (risk 9.2/10):
- "CIRCULAR DEPENDENCY: 5.4 validates skills that 5.1-5.3 haven't created"
- "Step 5.4 description assumes 5.1-5.3 will complete successfully. But if 5.1 hits the documented blockers... 5.4 inherits complete failure."

---

## Solution: Two-Phase Execution Model

### Phase A: Prerequisites Resolution (05-01 only)

**Purpose**: Resolve ALL blocking unknowns before any skill implementation starts

**Deliverables** (NEW - didn't exist in original):
1. `docs/toon-v3-skill-syntax-specification.md` - Complete TOON v3.0 syntax for skills
2. `docs/skill-invocation-mechanism.md` - How Claude Code triggers skills
3. `docs/constraint-embedding-format.md` - How constraints appear in SKILL.md
4. `5d-wave/templates/SKILL_TEMPLATE.toon` - Reference template all skills copy
5. `tests/skills/skill_test_environment_setup.md` - Test environment documentation

**Time Estimate**: 4 hours (research + documentation)

**Acceptance Criteria**:
- All 5 documents created and reviewed
- SKILL_TEMPLATE.toon compiles successfully to SKILL.md
- Test environment can simulate skill triggering

**Blocking**: 05-01 Phase B, 05-02, 05-03, 05-04 CANNOT START until Phase A complete

---

### Phase B: Implementation (05-01, 05-02, 05-03)

**05-01 Phase B**: develop skill implementation
- Uses SKILL_TEMPLATE.toon from Phase A
- Time: 2-4 hours
- Deliverable: `5d-wave/skills/develop/SKILL.md`

**05-02**: refactor skill implementation (AFTER 05-01 complete)
- Uses 05-01 Phase A specifications
- Uses 05-01 Phase B as reference example
- Time: 2.5-3 hours
- Deliverable: `5d-wave/skills/refactor/SKILL.md`

**05-03**: mikado skill implementation (parallel with 05-02)
- Uses same 05-01 outputs as 05-02
- Can run parallel with 05-02 (both use same prerequisites)
- Time: 2.5-3 hours
- Deliverable: `5d-wave/skills/mikado/SKILL.md`

---

### Phase C: Validation (05-04)

**Purpose**: Validate ALL THREE skills trigger correctly - ONLY AFTER they're proven to work

**Prerequisites** (BLOCKING):
- [ ] 05-01 Phase A+B fully complete
- [ ] 05-02 fully complete
- [ ] 05-03 fully complete
- [ ] All three SKILL.md files exist and compile
- [ ] Trigger pattern conflict matrices show no overlaps

**Time Estimate**: 3-4 hours (comprehensive integration testing)

**Deliverables**:
- `tests/skills/test_skill_triggers.py` - Trigger pattern validation
- `tests/skills/test_trigger_pattern_conflicts.py` - Collision detection
- `tests/skills/test_agent_chaining.py` - Agent binding validation
- `docs/skills/validation-report.md` - Test results summary

---

## Execution Order (Corrected)

### Sequential Execution Timeline

```
PHASE 5 START
│
├─ Step 05-01 Phase A (4 hours)
│  └─ Deliverables: 5 prerequisite documents
│     ├─ TOON syntax specification
│     ├─ Invocation mechanism documentation
│     ├─ Constraint format definition
│     ├─ SKILL_TEMPLATE.toon
│     └─ Test environment setup
│
├─ CHECKPOINT: Review Phase A deliverables
│  └─ ABORT if any missing or incomplete
│
├─ Step 05-01 Phase B (2-4 hours)
│  └─ Deliverable: develop skill (SKILL.toon + SKILL.md)
│
├─ CHECKPOINT: develop skill compiles and works
│  └─ ABORT if compilation fails or tests fail
│
├─ PARALLEL EXECUTION BEGINS
│  ├─ Step 05-02 (2.5-3 hours)
│  │  └─ Deliverable: refactor skill (SKILL.toon + SKILL.md)
│  │
│  └─ Step 05-03 (2.5-3 hours)
│     └─ Deliverable: mikado skill (SKILL.toon + SKILL.md)
│
├─ CHECKPOINT: All three skills exist and compile
│  └─ ABORT if any skill missing or non-functional
│
├─ Step 05-04 (3-4 hours)
│  └─ Deliverables:
│     ├─ test_skill_triggers.py
│     ├─ test_trigger_pattern_conflicts.py
│     ├─ test_agent_chaining.py
│     └─ validation-report.md
│
└─ PHASE 5 COMPLETE
   └─ All skills validated and ready for integration
```

**Total Time**:
- Sequential path: 4h (05-01A) + 3h (05-01B) + 3h (05-02) + 3h (05-03) + 4h (05-04) = **17 hours**
- Parallel optimized: 4h + 3h + 3h (05-02||05-03) + 4h = **14 hours**

**Original Estimate**: 5.5 hours (UNREALISTIC - didn't account for prerequisites)
**Correction Factor**: 2.5x-3x increase (realistic accounting for unknowns)

---

## Key Changes by Step

### 05-01 Changes

**BEFORE**:
- Single-phase implementation
- Estimated 2 hours
- CONDITIONAL_APPROVAL status
- Assumed TOON syntax known
- Assumed test environment exists

**AFTER**:
- Two-phase execution (Prerequisites + Implementation)
- Estimated 6-8 hours (4h + 2-4h)
- Phase A explicitly resolves ALL blockers
- Provides specifications for 05-02/05-03
- Creates reusable SKILL_TEMPLATE.toon

**Blocking Dependency Resolution**:
```
BEFORE: 05-01 depends on [1.6]
AFTER:  05-01 Phase A depends on [1.6]
        05-01 Phase B depends on [05-01 Phase A complete]
        05-02/05-03 depend on [05-01 Phase A+B complete]
```

---

### 05-02 Changes

**BEFORE**:
- Parallel execution with 05-01
- Trigger pattern "improve code" (COLLISION with develop skill)
- Estimated 1.5 hours
- REJECTED status due to blockers

**AFTER**:
- Sequential after 05-01 (or parallel with 05-03)
- Trigger patterns changed to "refactor-level-N", "progressive-refactoring" (NO COLLISION)
- Estimated 2.5-3 hours
- Uses 05-01 outputs as prerequisites
- Trigger pattern conflict matrix required

**Critical Fix**: Removed "improve code" pattern to prevent dual-skill firing

---

### 05-03 Changes

**BEFORE**:
- Sequential after 05-02
- Estimated 1.5 hours
- Inherited all 05-01 blockers

**AFTER**:
- Parallel with 05-02 (both use same 05-01 outputs)
- Estimated 2.5-3 hours
- Trigger patterns emphasize complexity: "mikado-method", "refactoring-complesso", "dependency-mapping"
- Uses 05-01 outputs (same as 05-02)

**Parallelization Optimization**: 05-02 and 05-03 can execute simultaneously after 05-01 complete

---

### 05-04 Changes

**BEFORE**:
- Depends on 05-01/05-02/05-03 (CONDITIONAL_APPROVAL)
- Estimated 1 hour
- Risk score 9.2/10
- Validation before artifacts exist (CIRCULAR DEPENDENCY)

**AFTER**:
- Depends on 05-01/05-02/05-03 (FULL COMPLETION - proven artifacts)
- Estimated 3-4 hours
- Risk score 4.5/10
- Prerequisite verification checklist (7 items)
- Validation AFTER artifacts proven to work

**Critical Fix**: Explicit prerequisite verification prevents validation-before-implementation

---

## Trigger Pattern Conflict Resolution

### Original (BROKEN)

| Skill | Patterns | Collision |
|-------|----------|-----------|
| develop | "implementa", "implement", "improve code" | ✗ |
| refactor | "refactoring", "improve code", "migliora codice" | ✗ COLLISION with develop |
| mikado | "refactoring complesso", "complex refactoring" | ✗ COLLISION with refactor |

**Result**: User says "improve code" → both develop and refactor trigger → SESSION FAILURE

---

### Corrected (FIXED)

| Skill | Patterns | Collision Check |
|-------|----------|-----------------|
| develop | "implementa", "scrivi codice", "TDD", "implement", "write code" | ✓ UNIQUE |
| refactor | "refactor-level-1", "refactor-level-2", ..., "refactor-level-6", "progressive-refactoring", "code-structure-improvement", "cleanup-codebase", "refactoring sistematico" | ✓ UNIQUE (level-specific) |
| mikado | "mikado-method", "refactoring-complesso", "dependency-mapping", "complex-refactoring-graph", "metodo-mikado" | ✓ UNIQUE (complexity-focused) |

**Result**: No substring overlaps. Each skill has distinct semantic focus.

**Conflict Resolution Rule**:
- **develop**: Generic implementation ("write code", "implement")
- **refactor**: Level-based improvement ("refactor-level-3", "progressive")
- **mikado**: Complexity and dependencies ("complex", "dependency-mapping")

---

## Risk Reduction Summary

### Original Risk Assessment

| Step | Original Risk | Blocker Count | Blast Radius |
|------|--------------|---------------|--------------|
| 05-01 | 7.0/10 | 8 CRITICAL | PHASE_5_6_7_8 |
| 05-02 | 8.2/10 | 7 CRITICAL | MULTIPLE_PHASES |
| 05-03 | 8.2/10 | 5 CRITICAL | ENTIRE_PROJECT |
| 05-04 | 9.2/10 | 6 CRITICAL | ENTIRE_PHASE_5_AND_BEYOND |

**Average Risk**: 8.15/10 (HIGH - PROJECT BLOCKER)

---

### Corrected Risk Assessment

| Step | Corrected Risk | Blockers Resolved | Blast Radius |
|------|---------------|-------------------|--------------|
| 05-01 Phase A | 3.5/10 | ALL (prerequisite resolution) | PHASE_5_ONLY |
| 05-01 Phase B | 4.0/10 | Uses Phase A outputs | PHASE_5_ONLY |
| 05-02 | 4.5/10 | Uses 05-01 outputs | PHASE_5_ONLY |
| 05-03 | 4.5/10 | Uses 05-01 outputs | PHASE_5_ONLY |
| 05-04 | 4.5/10 | Validates proven artifacts | PHASE_5_ONLY |

**Average Risk**: 4.2/10 (MANAGEABLE - PHASE-CONTAINED)

**Risk Reduction**: **48% decrease** (from 8.15 to 4.2)

---

## Circular Dependency Elimination (Proof)

### Original Dependency Graph (CIRCULAR)

```
05-01 (CONDITIONAL) ──┐
                      ├──> 05-04 (validates)
05-02 (CONDITIONAL) ──┤
                      │
05-03 (CONDITIONAL) ──┘
         ▲
         └─────────────────┐
                           │
         CIRCULAR: 05-04 needs complete skills,
                   but skills have conditional approval
                   (not proven to work)
```

**Cycle Detection**: 05-04 → validates → 05-01/05-02/05-03 → CONDITIONAL → 05-04 (needs proof)

**Result**: **DEADLOCK** - cannot validate before proven, cannot prove without validation

---

### Corrected Dependency Graph (ACYCLIC)

```
05-01 Phase A (prerequisite resolution)
  └──> PROVEN OUTPUT: 5 documents + SKILL_TEMPLATE.toon
       │
       └──> 05-01 Phase B (develop skill)
            └──> PROVEN OUTPUT: SKILL.md (compiled and working)
                 │
                 ├──> 05-02 (refactor skill)
                 │    └──> PROVEN OUTPUT: SKILL.md
                 │
                 └──> 05-03 (mikado skill)
                      └──> PROVEN OUTPUT: SKILL.md
                           │
                           └──> 05-04 (validation)
                                └──> OUTPUT: validation-report.md
```

**Cycle Detection**: **NO CYCLES** - each step depends only on PROVEN outputs from predecessors

**Result**: **EXECUTABLE** - validation occurs AFTER proven artifacts exist

---

## Approval Status Changes

### Before Correction

| Step | Status | Can Execute? |
|------|--------|--------------|
| 05-01 | CONDITIONAL_APPROVAL | ❌ Blockers unresolved |
| 05-02 | REJECTED | ❌ Blocked by 05-01 |
| 05-03 | CONDITIONAL_APPROVAL | ❌ Blocked by 05-01 |
| 05-04 | CONDITIONAL_APPROVAL | ❌ Circular dependency |

**Execution Capability**: **0/4 steps can execute** (100% blocked)

---

### After Correction

| Step | Status | Can Execute? |
|------|--------|--------------|
| 05-01 Phase A | CORRECTED_PENDING_REVIEW | ✅ Can start (depends on 1.6) |
| 05-01 Phase B | CORRECTED_PENDING_REVIEW | ✅ After Phase A complete |
| 05-02 | CORRECTED_PENDING_REVIEW | ✅ After 05-01 A+B complete |
| 05-03 | CORRECTED_PENDING_REVIEW | ✅ After 05-01 A+B complete (parallel with 05-02) |
| 05-04 | CORRECTED_PENDING_REVIEW | ✅ After 05-01/05-02/05-03 complete |

**Execution Capability**: **5/5 steps can execute** (100% unblocked after prerequisites)

---

## Implementation Recommendations

### Option A: Full Sequential (Conservative)

**Timeline**: 17 hours total
- 05-01 Phase A: 4 hours
- 05-01 Phase B: 3 hours
- 05-02: 3 hours
- 05-03: 3 hours
- 05-04: 4 hours

**Advantages**:
- Each step proven before next starts
- Minimal rework risk
- Clear checkpoint validation

**Disadvantages**:
- Slower (no parallelization)

---

### Option B: Parallel After Prerequisites (Recommended)

**Timeline**: 14 hours total
- 05-01 Phase A: 4 hours
- 05-01 Phase B: 3 hours
- 05-02 || 05-03: 3 hours (parallel)
- 05-04: 4 hours

**Advantages**:
- Faster (21% time savings)
- 05-02 and 05-03 use same prerequisites (no coupling between them)
- Maintains quality checkpoints

**Disadvantages**:
- Requires coordination if 05-02/05-03 done by different people

---

## Validation Criteria (Updated)

### Phase A Completion Criteria

- [ ] `docs/toon-v3-skill-syntax-specification.md` exists with examples
- [ ] `docs/skill-invocation-mechanism.md` explains Claude Code triggering
- [ ] `docs/constraint-embedding-format.md` defines constraint representation
- [ ] `5d-wave/templates/SKILL_TEMPLATE.toon` compiles to valid SKILL.md
- [ ] `tests/skills/skill_test_environment_setup.md` documents test approach

**Checkpoint**: Review all 5 documents. ABORT if any incomplete.

---

### Phase B Completion Criteria (per skill)

- [ ] SKILL.toon file created
- [ ] SKILL.toon compiles to SKILL.md without errors
- [ ] Trigger patterns documented and conflict matrix updated
- [ ] Methodology reference complete (with decision guidance)
- [ ] E2E test written and passing
- [ ] Agent binding validated

**Checkpoint**: Each skill proven functional before proceeding.

---

### Phase C Completion Criteria (validation)

- [ ] All 3 skills trigger on documented patterns
- [ ] No false positives (11 test cases pass)
- [ ] No trigger pattern collisions detected
- [ ] Skills chain correctly to software-crafter agent
- [ ] Validation report generated

**Checkpoint**: All skills validated. Ready for integration (Phase 6).

---

## Conclusion

**Original Problem**: Circular dependency made Phase 5 unexecutable (risk 8.5/10)

**Root Cause**: Validation step (05-04) depended on conditionally-approved artifacts (05-01/05-02/05-03)

**Solution**: Two-phase execution with explicit prerequisite resolution (05-01 Phase A) before any implementation (Phase B)

**Result**:
- ✅ Circular dependency eliminated
- ✅ Risk reduced from 8.5/10 to 4.5/10 (48% reduction)
- ✅ Blast radius contained (ENTIRE_PROJECT → PHASE_5_ONLY)
- ✅ All steps executable with clear prerequisites
- ✅ Parallel execution optimized (14 hours vs 17 hours sequential)

**Recommendation**: Approve corrected step specifications and execute in order:
1. 05-01 Phase A (prerequisites)
2. 05-01 Phase B (develop skill)
3. 05-02 || 05-03 (refactor and mikado skills in parallel)
4. 05-04 (validation)

---

**Next Steps**:
1. Review corrected step specifications (`05-01-CORRECTED.json` through `05-04-CORRECTED.json`)
2. Approve Phase A prerequisite resolution approach
3. Execute Phase 5 with corrected workflow
4. Generate validation report after 05-04 complete
