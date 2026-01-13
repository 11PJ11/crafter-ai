# Adversarial Review Summary: Step 03-01 (Convert Primary Agents to TOON)

**Review Date**: 2026-01-05
**Reviewer**: Lyra (adversarial mode)
**Verdict**: NO-GO - CRITICAL BLOCKERS

---

## Executive Summary

Step 03-01 (Convert 10 primary agents to TOON v3.0) **cannot proceed** until 5 critical upstream failures are resolved.

**Risk Score**: 9/10 (CRITICAL)
**Blast Radius**: Phases 3-8 (entire batch migration blocked)
**Estimated Delay**: 8-12 hours to complete upstream phases properly

---

## Five Critical Blockers

### 1. TOON v3.0 Specification Missing (CATASTROPHIC)
- **Problem**: Task requires "TOON v3.0 format" but no specification exists in repo
- **Evidence**: Only TOON v1.0 test example exists (novel-editor-chatgpt-toon.txt)
- **Impact**: Developer converts using v1.0 guess. Creates incompatible format. All 10 agents unusable.
- **Resolution**: Complete Phase 1.1 validation (4 hours)

### 2. Compiler Tool Unvalidated (CATASTROPHIC)
- **Problem**: Task says "Compile each TOON file" but compiler tool doesn't exist or is untested
- **Evidence**: tools/toon/ doesn't exist. tools/build.py is IDE bundle builder, not TOON compiler.
- **Impact**: Execution fails immediately on first agent
- **Resolution**: Complete Phase 1.2 compiler validation (6 hours)

### 3. Baseline Measurements Missing (HIGH)
- **Problem**: Cannot measure "50% token savings" without baseline measurements
- **Evidence**: No archive directory. Phase 2.4 apparently not executed.
- **Impact**: 3 agents achieve 48% savings. Acceptance criteria fails.
- **Resolution**: Verify Phase 2.4 completion, measure baselines (2 hours)

### 4. Reference Patterns Undefined (HIGH)
- **Problem**: Task references "tools/toon/README.md" for patterns but file doesn't exist
- **Evidence**: No patterns documentation from Phase 2.2 pilot
- **Impact**: Developer has no guidance. Blindly guesses format.
- **Resolution**: Document patterns from Phase 2.2 (3 hours)

### 5. Test Specifications Too Vague (HIGH)
- **Problem**: Tests named but not implemented. Assertions undefined.
- **Evidence**: test_each_agent_compiles, test_token_savings_per_agent have no implementation or pass/fail criteria
- **Impact**: Tests can pass for wrong reasons. Integration fails downstream.
- **Resolution**: Implement proper test suite (4 hours)

---

## Key Contradictions

| Aspect | Requirement A | Requirement B | Status |
|--------|---|---|---|
| **Format Version** | TOON v3.0 | Only v1.0 example exists | UNDEFINED |
| **Token Target** | ~60% (estimate) | >=50% (hard gate) | AMBIGUOUS |
| **Compiler** | Must compile each agent | Tool doesn't exist | UNACHIEVABLE |
| **Baseline** | Needed for comparison | Phase 2.4 not complete | MISSING |
| **Patterns** | Required reference | Not documented | UNDEFINED |

---

## Most Dangerous Failure Scenario

```
Step 03-01 proceeds with missing v3.0 spec
  ↓
Developer converts using v1.0 guess
  ↓
Tests pass (vague enough to not catch format error)
  ↓
Phase 3.1 appears successful - commit approved
  ↓
Phase 3.2 starts: "Validate compilation"
  ↓
DISCOVERS: All 10 agents have wrong format
  ↓
All 10 agents MUST be reworked
  ↓
16 hours wasted + 16 hours rework = 32 hours total cost
```

This is worse than immediate failure - it appears successful until phase 4, then cascade fails.

---

## Required Actions (Priority Order)

1. **Verify Phase 1 Completion** [4 hrs]
   - Confirm TOON v3.0 spec exists
   - Confirm compiler works on real agents
   - Gate: Must pass before step 03-01 starts

2. **Verify Phase 2.4 Completion** [2 hrs]
   - Confirm archive/pre-toon-migration/ has 26 agents
   - Confirm correct source (nWave/agents/, not dist/ide/)
   - Gate: Must verify baseline data integrity

3. **Measure Baseline Tokens** [1 hr]
   - Record token counts for all agents
   - Validate 50% target is achievable
   - Gate: Clarify if target is 50% or 60%

4. **Document Patterns** [2 hrs]
   - Export Phase 2.2 patterns
   - Create tools/toon/README.md
   - Gate: Developer needs reference guide

5. **Implement Tests** [4 hrs]
   - Write actual test assertions
   - Define compilation success criteria
   - Gate: Tests must be executable, not just names

**Total Remediation**: 13 hours (not 5 hours as estimated)

---

## Evidence

```bash
# No TOON v3.0 spec
find . -name "*3.0*" -o -name "*TOON*spec*" 2>/dev/null
# Result: NO v3.0 specification document

# No TOON compiler
ls tools/toon/ 2>/dev/null
# Result: Directory doesn't exist

# No archive
ls archive/pre-toon-migration/ 2>/dev/null
# Result: Directory doesn't exist

# No TOON files
find . -name "*.toon" -type f 2>/dev/null
# Result: 0 TOON files (only v1.0 test example exists)
```

---

## Detailed Review Documents

- **Full Adversarial Review**: `ADVERSARIAL_REVIEW_03-01.md` (50+ page detailed analysis)
- **Updated Task File**: `steps/03-01.json` with adversarial_review section (lines 84-227)
- **Upstream Issues**: `ADVERSARIAL_REVIEW_01-01.md` (Phase 1 blockers)

---

## Recommendation

**DO NOT START STEP 03-01**

The appearance of "success" (green tests, completed conversion) likely masks catastrophic format incompatibility that cascades into phase 4+. This is worse than immediate failure - it wastes 16 hours and then requires 16 more hours of rework.

Better to pause, complete upstream phases properly (13 hours), then proceed with step 03-01 on solid foundation.

