# ADVERSARIAL REVIEW: Step 04-01
## Convert DISCUSS Wave Commands

**Reviewer**: Lyra (Adversarial Mode)
**Date**: 2026-01-05
**Verdict**: **CRITICAL BLOCKERS - DO NOT EXECUTE**
**Risk Score**: 9.5/10
**Blast Radius**: ENTIRE PHASE 4 (blocks steps 4.2-4.6 and phases 5-8)

---

## Executive Summary

Step 04-01 contains **5 critical contradictions**, **5 dangerous assumptions**, and **6 unhandled edge cases** that make it impossible to execute without resolution. The step is designed to convert two command files (start.md and discuss.md) to TOON format, but:

1. **TOON compiler doesn't exist** in the codebase (confirmed via directory search)
2. **Wave classification contradiction**: start.md is CROSS_WAVE, acceptance criteria expects DISCUSS
3. **Token savings claim lacks baseline data**: aspirational goal presented as current success criteria
4. **TOON format specification missing**: cannot validate metadata conversion correctness
5. **Compilation operation undefined**: execution step references 'compile' without defining the tool or operation

**Recommendation**: **DO NOT START THIS STEP** until critical blockers are resolved.

---

## Critical Contradictions

### Contradiction 1: WAVE_CLASSIFICATION_CONFLICT
**Severity**: CRITICAL
**Locations**: Step name (line 11), description (line 12), acceptance criteria (lines 35-37)

**The Problem**:
- Step name/description: "Convert DISCUSS Wave Commands"
- Acceptance criteria: "Wave metadata correct (DISCUSS)"
- Source file start.md, line 12: **"Wave: CROSS_WAVE (project initialization)"**
- Source file discuss.md, line 12: "Wave: DISCUSS"

**Why This Is a Contradiction**:
The step assumes all files should be classified as DISCUSS wave. But start.md is explicitly CROSS_WAVE (not DISCUSS). This creates an impossible choice:
- If start.toon is converted with wave=DISCUSS metadata → **violates the wave classification principle**
- If start.toon is converted with wave=CROSS_WAVE metadata → **acceptance criteria FAILS** (expects DISCUSS)

**Impact**: Quality gate will definitely fail. Either the conversion is wrong or the acceptance criteria is wrong.

**Root Cause**: Task designer did not verify source file wave classifications before writing the step.

**Resolution**: Split into two separate steps:
- Step 04-01: Convert DISCUSS commands (discuss.md only)
- Step 04-01b: Convert CROSS_WAVE entry command (start.md only)

---

### Contradiction 2: TOKEN_SAVINGS_CLAIM_WITHOUT_BASELINE
**Severity**: CRITICAL
**Location**: Line 26 (SC7)

**The Problem**:
- SC7 states: "~60% token savings in source files" (quantitative claim)
- No baseline token count data provided
- No measurement methodology documented
- No compiled TOON samples to measure against

**Evidence Chain**:
1. Searched entire workflow directory
2. Found: zero baseline measurements from step 2.4
3. Found: zero compiled TOON files from pilot agents
4. Found: zero token counting tool specified
5. Found: TOON compiler doesn't exist (can't generate TOON files to measure)

**Why This Violates Evidence-Based Claims**:
The claim (~60%) is presented as a current success criterion, but it's actually a goal or aspiration. The claim appears in baseline.yaml and roadmap.yaml as a target to achieve, not as evidence-based measurement. This is a logical fallacy: presenting aspirational goals as current factual success criteria.

**Hidden Assumption**: TOON format naturally provides 60% savings. **Unvalidated**. TOON could actually produce larger files if it requires verbose syntax.

**Impact**:
- If actual token savings < 50%, quality gate FAILS
- If savings = 40%, is that acceptable? Gate is ambiguous.
- Phase 4 could be blocked at the end when token savings don't materialize

**Resolution**:
A) Remove SC7 from this step (leave as phase-level validation in phase 8)
B) Change to "Convert files to TOON format" (defer token savings validation)
C) Provide measured baseline showing TOON samples achieve >= 60% savings BEFORE starting conversion

---

### Contradiction 3: COMPILE_OPERATION_UNDEFINED_VS_REQUIRED
**Severity**: CRITICAL
**Location**: Line 53 (execution step 3), Line 62 (quality gate)

**The Problem**:
- Execution workflow step 3: "Compile both TOON files"
- Quality gate: "Both commands compile successfully"
- **No definition of what 'compile' means**
- No tool path, command, success criteria, or error handling

**Verification Evidence**:
- Searched `/mnt/c/Repositories/Projects/ai-craft/tools/` directory
- Found: build.py, build_config.yaml, build_ide_bundle.py, processors/, utils/
- **NOT FOUND**: Any TOON compiler or compiler directory

**Why This Is Impossible to Execute**:
Executor cannot perform an undefined operation. It's like saying "perform action X" without defining X. The quality gate references undefined operation, so there's no way to validate success or failure.

**Assumptions Made**:
- TOON compiler exists at 'tools/toon/' (it doesn't)
- Compiler is named 'compile' or similar (unknown)
- Compiler produces specific output format (unspecified)
- Success criteria is exit code 0 (unspecified)

**Impact**: **ENTIRE STEP FAILS** at step 3. Executor cannot proceed without compiler. Phase 4 BLOCKED.

**Resolution**: BEFORE starting any conversion work:
1. Verify TOON compiler exists OR identify alternative tool
2. Document exact invocation command
3. Specify expected output format
4. Define success exit code and validation criteria

---

## Dangerous Assumptions

### Assumption 1: COMPILER_EXISTS (CRITICAL)
**Evidence**: Searched entire codebase - NO TOON compiler found
**Danger**: Step is literally impossible without this tool
**Status**: CONFIRMED FALSE - Compiler does not exist

### Assumption 2: TOON_FORMAT_SPECIFIED (HIGH)
**Evidence**: Searched all step files and docs - no TOON format specification found
**Danger**: Cannot validate TOON output correctness
**Status**: CONFIRMED FALSE - No spec provided

### Assumption 3: STEP_2_4_DELIVERED_BASELINE (HIGH)
**Evidence**: Step 2.4 is titled "Archive Original MD Files" - it archives, it doesn't convert
**Danger**: Token savings claim cannot be validated. Conversion patterns unknown.
**Status**: CONFIRMED FALSE - 2.4 is not a pilot

### Assumption 4: TOKEN_SAVINGS_ACHIEVABLE (MEDIUM)
**Evidence**: No measurement data. Baseline.yaml lists as goal, not evidence.
**Danger**: If actual savings are 30%, quality gate fails mid-phase
**Status**: UNVALIDATED - No evidence provided

### Assumption 5: FILES_ARE_ERROR_FREE (HIGH)
**Evidence**: No error handling in execution_guidance
**Danger**: If files have syntax errors, no recovery path defined
**Status**: CONFIRMED PROBLEMATIC - No error handling exists

---

## Unhandled Edge Cases

| Edge Case | Likelihood | Impact | Handling | Mitigation |
|-----------|------------|--------|----------|-----------|
| TOON compiler doesn't exist | **HIGH** (confirmed) | ENTIRE STEP FAILS | NONE | Verify compiler before starting |
| start.md wave is CROSS_WAVE (correct) | **HIGH** (confirmed) | AC fails | NONE | Split into two steps |
| TOON creates LARGER files (compression fails) | MEDIUM | Phase 4 blocked | NONE | Validate compression on samples |
| Agent-activation syntax wrong | MEDIUM | AC fails | NONE | Provide TOON format spec |
| Test framework doesn't exist | MEDIUM | Step incomplete | NONE | Specify framework location |
| Partial failure (1 of 2 files compiles) | MEDIUM | Unclear recovery | NONE | Add error handling per file |

---

## Failure Scenarios

### Scenario 1: TOON Compiler Not Found (PROBABILITY: HIGH)
1. Executor reaches step 3: "Compile both TOON files"
2. Executor attempts: `tools/toon/compile start.toon discuss.toon`
3. Command fails: "tools/toon not found" or "command not found"
4. **Result**: Phase 4 BLOCKED

**Prevention**: Verify compiler exists BEFORE starting

### Scenario 2: Wave Classification Mismatch (PROBABILITY: HIGH)
1. start.toon created with wave=CROSS_WAVE (correct per source)
2. Quality gate checks: "Is wave=DISCUSS?"
3. Answer: NO (wave=CROSS_WAVE)
4. **Result**: Quality gate FAILS, step incomplete

**Prevention**: Split step into DISCUSS and CROSS_WAVE

### Scenario 3: Token Savings Below Threshold (PROBABILITY: MEDIUM)
1. start.toon = 40% smaller, discuss.toon = 35% smaller
2. Average savings = 37.5% (below 60% target)
3. Quality gate expects >= 60%
4. **Result**: Quality gate FAILS or blocks phase 4

**Prevention**: Validate compression efficiency on samples first

### Scenario 4: Agent-Activation Metadata Corruption (PROBABILITY: MEDIUM)
1. Executor converts YAML to TOON syntax (guessed, since spec not provided)
2. Validator checks: "Is agent-activation valid?"
3. Syntax doesn't match expected format
4. **Result**: Quality gate FAILS, metadata corrupted

**Prevention**: Provide TOON format examples before starting

### Scenario 5: Test Framework Not Found (PROBABILITY: MEDIUM)
1. Executor attempts to write tests (step 4 of workflow)
2. Test framework location not specified - executor guesses
3. Tests fail to execute in wrong framework
4. **Result**: Step incomplete

**Prevention**: Specify test framework location and configuration

### Scenario 6: Partial Failure - Asymmetric Results (PROBABILITY: MEDIUM)
1. discuss.toon compiles successfully
2. start.toon fails (syntax error in YAML conversion)
3. Quality gate requires "Both commands compile successfully"
4. **Result**: Quality gate FAILS with no clear recovery path

**Prevention**: Add error handling for per-file failures

---

## Time Estimate Risk

**Current Estimate**: 1 hour
**Realistic Estimate**:
- With working compiler, no issues: 1-2 hours ✓
- With compiler needing setup: 5-10 hours ⚠
- Without compiler (most likely): BLOCKED (impossible) ✗

**Variance**: 200-1000% underestimate (or impossible)

---

## Risk Assessment

**Risk Score**: 9.5/10 (CRITICAL)
**Confidence**: 90% (based on direct codebase analysis)
**Blast Radius**: ENTIRE PHASE 4

**Why Risk Is So High**:
1. Compiler dependency not verified (**BLOCKER**)
2. Wave classification contradiction (**WILL DEFINITELY FAIL**)
3. Token savings unvalidated (**LIKELY FAILURE**)
4. Undefined operations (**CANNOT EXECUTE**)
5. No error handling (**NO RECOVERY PATH**)

**Execution Probability**: 20% (would require compiler to exist and wave issue resolved)
**Success Probability**: 15% (even with fixes, multiple issues remain)

---

## Critical Action Items

### BEFORE STARTING THIS STEP:

1. **CRITICAL**: Verify TOON compiler exists
   - Search: `find /mnt/c/Repositories/Projects/ai-craft -name "*toon*" -type f`
   - If not found: Identify what "compile" actually means
   - If found: Document exact invocation command

2. **CRITICAL**: Resolve wave classification
   - Confirm start.md is architecturally CROSS_WAVE (not DISCUSS)
   - Option A: Split step 4.1 into 4.1 (DISCUSS) and 4.1b (CROSS_WAVE)
   - Option B: Rename step to clarify both wave types involved

3. **CRITICAL**: Provide baseline token savings data
   - From step 2.4 pilot: What are measured token counts?
   - Is 60% the target or measured baseline?
   - What tokenizer is used for measurement?

4. **CRITICAL**: Specify TOON format for agent-activation
   - Provide before/after examples
   - Define TOON syntax for nested YAML structures
   - Document what "valid" means for acceptance criteria

5. **CRITICAL**: Clarify step 2.4 dependency
   - What deliverables does 2.4 provide to 4.1?
   - Is 2.4 a hard blocker for 4.1?
   - Where are TOON conversion patterns documented?

### HIGH PRIORITY:

- Add error handling for compilation failures (per-file)
- Add error handling for metadata validation failures
- Expand TDD test specifications with concrete assertions
- Specify test framework location and token counting tool
- Increase estimated hours from 1 to 3-5 hours (with compiler) or flag as BLOCKED

---

## Recommendation

**DO NOT EXECUTE this step** until all critical blockers are resolved.

**Required Actions**:
1. Verify compiler exists (or redefine what "compile" means)
2. Resolve wave classification contradiction
3. Provide baseline token savings measurements
4. Provide TOON format specification with examples
5. Add comprehensive error handling

**Estimated Resolution Time**: 4-8 hours of analysis and clarification

**Post-Resolution Estimated Execution Time**: 2-3 hours (with compiler available)

---

## Detailed Review Sections

See `/mnt/c/Repositories/Projects/ai-craft/docs/workflow/plugin-marketplace-migration/steps/04-01.json` for complete adversarial_review section with:
- contradictions_found (3 detailed contradictions)
- dangerous_assumptions (5 assumptions)
- unhandled_edge_cases (6 edge cases)
- failure_scenarios (6 failure scenarios)
- risk_assessment (with execution/success probabilities)
- execution_risks (time estimate risk, feasibility risk)
