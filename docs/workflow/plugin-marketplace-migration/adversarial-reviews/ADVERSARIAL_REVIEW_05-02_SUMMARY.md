# Adversarial Review: Step 05-02 (Create refactor Skill)
**Date**: 2026-01-05
**Reviewer**: adversarial-software-crafter-reviewer
**Risk Score**: 8.2/10 (HIGH RISK)
**Blast Radius**: MULTIPLE_PHASES

---

## Executive Summary

Step 05-02 has **CRITICAL BLOCKERS** that prevent implementation from starting:
- Cannot implement without resolving 6 blocking dependencies from step 05-01
- TOON v3.0 skill syntax is undefined
- Skill invocation mechanism is undefined
- E2E test is untestable without mechanism specification

Additionally, **quality gates are FALSE POSITIVES**:
- "Trigger patterns validated" has no validation logic
- "References progressive refactoring methodology" is ambiguous
- Tests can pass with incomplete implementations

**Recommendation**: DO NOT START step 05-02. Block implementation until 05-01 gaps are resolved.

---

## Critical Blockers (Cannot Start Implementation)

### 1. Blocking Dependency Chain from Step 05-01
**Status**: BLOCKING
**Evidence**: Lines 242-245 state "Resolve 05-01 gaps BEFORE starting 05-02 implementation"

Missing prerequisites:
- TOON v3.0 skill syntax specification
- Skill invocation mechanism documentation
- Test environment definition
- SKILL.toon compiler behavior

**Impact**: Implementation is impossible without these. Step 05-02 inherits all 05-01 gaps.

---

### 2. TOON v3.0 Skill Syntax Undefined
**Status**: BLOCKING
**Evidence**: No TOON syntax examples provided for skill definitions

Without this, implementer must:
- Reverse-engineer syntax from compilation errors
- Guess at language features
- Test with trial-and-error iterations

**Result**: Step 05-02 will fail to compile SKILL.toon files.

---

### 3. Skill Invocation Mechanism Not Documented
**Status**: BLOCKING
**Evidence**: Line 41 E2E test assumes behavior that isn't specified

The test assumes:
```
WHEN user says "refactoring del codice"
THEN skill should trigger software-crafter with refactor workflow
```

But missing: How does Claude Code match user input to skill triggers? Via:
- Substring matching?
- Exact match?
- NLP semantic matching?
- Regex patterns?

**Impact**: E2E test is untestable. Skill invocation behavior is undefined.

---

## Dangerous Contradictions

### 1. Time Estimate vs. Actual Complexity
| Stated | Estimated Hours | Reality |
|--------|-----------------|---------|
| Line 14 | 1.5 hours | 2.5-3 hours MINIMUM |
| Line 186 | Review says 2.5-3.5 if clarifications needed | Plus blockers from 05-01 |

**Impact**: Project planning is off by 1-2 hours. More critically, blockers mean implementation cannot start yet.

---

### 2. Trigger Pattern Overlap: "improve code"
**Status**: HIGH RISK
**Evidence**: Lines 80-83 contradiction

- Step 05-02 defines trigger: "improve code"
- Step 05-01 (develop skill) also targets code improvement
- No conflict resolution mechanism defined

**Failure Mode**: When user says "improve code", BOTH skills trigger:
1. Develop skill triggers (from 05-01)
2. Refactor skill triggers (from 05-02)
3. Two agents load in same session
4. State conflicts, unpredictable behavior
5. Feature is broken despite passing tests

---

### 3. Methodology Scope Contradiction
**Status**: HIGH RISK
**Evidence**: Lines 74-77

Acceptance criteria: "References progressive refactoring methodology"

But methodology size is ambiguous:
- Option A: List just 6 level names (minimal)
- Option B: Embed 8,500+ lines of full spec (unmaintainable)
- Option C: Link to external doc (may not exist)

Test will pass with ANY of these, but skill effectiveness varies wildly.

---

### 4. Skill Role vs. Command Confusion
**Status**: MEDIUM RISK
**Evidence**: Lines 98-101

Contradiction:
- Skill "refactor" auto-invokes software-crafter agent
- software-crafter agent already has "*refactor" command
- Which one does user call? Are they duplicates? Do they conflict?

**Impact**: Skill implementation creates redundancy or confusion.

---

## Dangerous Assumptions (High Failure Probability)

| Assumption | Why Dangerous | Probability | Consequence |
|-----------|---------------|-------------|-------------|
| TOON skill syntax = command syntax | Commands and skills are different constructs | HIGH | Files won't compile or don't function as intended |
| Trigger validation at compile time | May only validate at runtime if at all | HIGH | Overlapping patterns both trigger |
| Methodology can be abbreviated | Methodology is interconnected - abbreviation loses context | MEDIUM | Skill is created but unusable |
| Test definition is sufficient | "References methodology" is too vague to test | HIGH | Test passes but implementation incomplete |
| Levels are deterministic | Humans make judgment calls about level selection | MEDIUM | Skill triggers but doesn't guide correctly |

---

## Unhandled Edge Cases (All High-Medium Risk)

### 1. Multilingual Mixed Input (High Likelihood)
**Input**: "refactor questa classe, pulisci il codice"
**Problem**: Multiple triggers in one input
**Missing**: How skill handles multiple triggers, precedence rules

### 2. Unintended Trigger (High Likelihood)
**Input**: "Tell me about refactoring best practices"
**Problem**: User wants information, not code refactoring
**Missing**: Context analysis to distinguish intent vs. command

### 3. Case Sensitivity & Accents (High Likelihood)
**Input**: User says "Refactor" (capital R)
**Pattern**: "refactor" (lowercase)
**Problem**: Skill doesn't trigger
**Missing**: Pattern matching algorithm specification

### 4. Agent Failure After Trigger (Medium Likelihood)
**Problem**: Skill triggers but software-crafter agent fails to load
**Missing**: Error recovery, fallback guidance, timeout handling

### 5. Wrong Level Order (Medium Likelihood)
**Problem**: User wants Level 5 without Levels 1-2
**Missing**: Skill doesn't enforce sequential application

### 6. Methodology Staleness (Medium Likelihood)
**Problem**: SKILL.md embeds methodology v1.0, but agent updates to v2.0
**Missing**: Versioning, deprecation mechanism, update path

---

## Failure Scenarios (Will Break in Production)

### Scenario 1: Compilation Failure
**Trigger**: TOON skill syntax differs from command syntax
**Cascading Impact**:
1. SKILL.toon file won't compile
2. Quality gate fails
3. Phase 5 blocked
4. Phase 6 blocked
5. Project timeline slips

**Recovery**: No specification means no error recovery path.

---

### Scenario 2: Silent Skill Failure
**Trigger**: Trigger patterns require exact match but user input is paraphrased
**Cascading Impact**:
1. SKILL.md compiles successfully
2. Tests pass
3. Skill deployed to Claude Code
4. Skill NEVER triggers for any user input
5. Feature is delivered but non-functional
6. Users report skill doesn't work
7. Phase 6 blocked by regression

**Recovery**: No debugging guidance, no logging, no verification mechanism.

---

### Scenario 3: Dual-Skill Firing
**Trigger**: User says "improve code" matching both 05-01 and 05-02 patterns
**Cascading Impact**:
1. Both develop and refactor skills trigger
2. Both agents load in session
3. State conflicts
4. Unpredictable behavior
5. Success criteria violated
6. Feature broken despite passing tests

**Recovery**: No conflict detection or resolution documented.

---

### Scenario 4: False Test Positives
**Trigger**: Test "test_refactor_levels_referenced" has vague definition
**Cascading Impact**:
1. Test passes if SKILL.md just lists level names
2. Step marked complete
3. Skill is created but unhelpful
4. User invokes skill, finds no guidance
5. Skill is functionally incomplete

**Recovery**: Test definition is undefined - cannot detect false positive.

---

### Scenario 5: Methodology Rot
**Trigger**: Agent spec updates progressive refactoring methodology
**Cascading Impact**:
1. SKILL.md embedded with old methodology
2. Skill references outdated information
3. User confusion
4. Skill becomes technical debt
5. Future rework required

**Recovery**: No versioning, no deprecation mechanism.

---

### Scenario 6: Environment Mismatch
**Trigger**: E2E test passes in simulator but fails in actual Claude Code
**Cascading Impact**:
1. Step 05-02 passes all tests
2. Phase 5 progresses
3. Feature reaches production
4. Users report skill doesn't work
5. Phase 6 blocked by regression

**Recovery**: Test environment not specified, no validation of parity with production.

---

## False Positive Quality Gates

| Quality Gate | Status | Problem |
|-------------|--------|---------|
| "Skill compiles to valid SKILL.md" | FALSE POSITIVE | Without TOON syntax spec, success is undefined |
| "Trigger patterns for refactoring terminology" | FALSE POSITIVE | "improve code" overlaps with 05-01 |
| "Trigger patterns validated" | FALSE POSITIVE | No validation logic exists |
| "References progressive refactoring methodology" | FALSE POSITIVE | Acceptance criteria too vague |
| "Tests passing" | FALSE POSITIVE | Tests can pass but skill non-functional |

---

## Red Flags Summary (13 Critical Issues)

```
BLOCKER: Depends on 05-01 resolution which isn't complete
BLOCKER: TOON skill syntax undefined - cannot implement without specification
BLOCKER: Skill invocation mechanism undefined - cannot test
CONTRADICTION: Time estimate conflicts with known dependencies
CONTRADICTION: Test assumes behavior that isn't specified
DANGER: Trigger pattern conflicts will cause multi-skill firing
DANGER: Methodology reference scope undefined - test will false-positive
AMBIGUITY: No conflict resolution for overlapping patterns
AMBIGUITY: Methodology embedding scope unclear
AMBIGUITY: Refactor vs Mikado decision logic missing
FALSE POSITIVE: Quality gates will pass even with incomplete implementation
DECAY RISK: Embedded methodology becomes outdated
PRODUCTION RISK: Tests pass but skill non-functional in Claude Code
```

---

## Recommendations (Priority Order)

### CRITICAL
1. **DO NOT START IMPLEMENTATION** - Block until 05-01 gaps resolved
2. **Resolve 05-01 gaps first** - TOON syntax, invocation mechanism, test environment
3. **Change trigger patterns** - Remove "improve code", use refactor-specific: "refactor-level-N", "progressive-refactoring", "code-structure"
4. **Define methodology embedding scope** - Specification with concrete example of what appears in SKILL.md

### HIGH
5. **Create trigger pattern conflict matrix** - Document all patterns across 05-01, 05-02, 05-03 with conflict resolution rules
6. **Create SKILL_REFACTOR_EXAMPLE.toon** - Template showing proper TOON structure
7. **Define test_refactor_levels_referenced precisely** - Specific assertions on what constitutes valid reference
8. **Update time estimate** - 2.5-3 hours MINIMUM after blockers resolved

### MEDIUM
9. **Clarify refactor vs mikado relationship** - When to use each skill, can they combine?
10. **Add error recovery specification** - What happens if agent fails to load after trigger?
11. **Add versioning for methodology** - How does SKILL.md stay synchronized with agent updates?

---

## Blast Radius Analysis

If step 05-02 fails:

**Immediate Impact** (Phase 5):
- Step 05-02 blocks
- Step 05-03 (mikado skill) blocked due to shared TOON/invocation gaps
- Phase 5 cannot complete

**Downstream Impact** (Phase 6):
- Success criteria "Full workflow functional" cannot be met
- Delivery blocked
- Plugin marketplace cannot launch with broken skill system

**Future Impact**:
- Skill system is foundation for plugin marketplace
- Cascading failures into future phases
- Technical debt if skills are patched with workarounds

**Overall**: MULTIPLE_PHASES blast radius

---

## Approval Decision

**Status**: DO NOT APPROVE - BLOCK IMPLEMENTATION

**Prerequisites for Approval**:
1. [ ] Step 05-01 gaps resolved (TOON syntax, invocation mechanism documented)
2. [ ] Trigger patterns changed to avoid conflicts
3. [ ] Methodology embedding scope defined
4. [ ] Test definitions made specific and verifiable
5. [ ] Trigger pattern conflict matrix created
6. [ ] Time estimate updated

**When These Are Met**: Re-submit for approval.

---

## Summary: What Will Go Wrong

**Without intervention**, here's what will happen:

1. **Day 1-2**: Implementer starts, immediately blocked by missing TOON syntax specification
2. **Day 2-3**: Reverse-engineers syntax from compiler errors, creates guess-based SKILL.toon
3. **Day 3**: File compiles (luck), but trigger patterns conflict with develop skill
4. **Day 4**: E2E test passes (but tests undefined behavior), step marked complete
5. **Day 5**: Deployed to production, skill doesn't trigger for user input
6. **Day 6**: Users report non-functional feature, Phase 6 blocked
7. **Day 7+**: Root cause analysis reveals trigger conflicts, syntax incompatibilities, undefined invocation mechanism

**Total Impact**: 6+ days of wasted effort, Phase 6 regression, project delay.

**Prevention**: Stop now. Resolve blockers before implementation starts.

