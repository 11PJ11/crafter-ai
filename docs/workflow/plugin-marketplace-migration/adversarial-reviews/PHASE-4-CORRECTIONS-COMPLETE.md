# Phase 4 Command Migration - All Corrections Applied

**Date**: 2026-01-06
**Corrector**: Lyra
**Status**: CORRECTIONS IN PROGRESS
**Files Corrected**: 3 of 7 (04-01, 04-01b NEW, 04-02) + 4 remaining
**Total Time Estimate Change**: Original 10h → Corrected 27-39h (2.7-3.9x increase)

---

## Execution Summary

### Steps CORRECTED (Ready for Execution)

#### ✅ Step 04-01: Convert DISCUSS Command (discuss.md only)
- **Original Risk**: 9.5/10 → **Corrected Risk**: 4.0/10
- **Original Time**: 1h → **Corrected Time**: 4-6h
- **Status**: CORRECTED - Ready after prerequisite verification
- **File**: `steps/04-01.json` (updated)

**Major Corrections**:
1. Split from original 04-01 to handle only DISCUSS wave (removed start.md)
2. Added prerequisite checks for Phase 1 infrastructure
3. Added TOON compiler specification with invocation command
4. Added comprehensive error handling (compiler_not_found, compilation_failure, metadata_validation_failure)
5. Added detailed test specifications with pytest code skeletons
6. Removed unvalidated token savings (SC7) from step-level criteria
7. Updated dependencies to include Phase 1 steps (01-01, 01-02, 01-03)

#### ✅ Step 04-01b: Convert CROSS_WAVE Entry Command (start.md)
- **Risk**: 3.0/10 (NEW STEP - lower risk due to 04-01 patterns)
- **Time**: 2-3h
- **Status**: CORRECTED - Ready after 04-01 complete
- **File**: `steps/04-01b.json` (NEW FILE CREATED)

**Purpose**: Separated from 04-01 to fix wave classification contradiction
- start.md is CROSS_WAVE (project initialization spanning all waves)
- Original step incorrectly claimed all files were DISCUSS wave
- Tests now correctly validate wave: CROSS_WAVE (not DISCUSS)

**Major Additions**:
1. Complete prerequisite checks matching 04-01
2. Dependency on 04-01 completion (use patterns from first conversion)
3. Wave classification rationale section explaining CROSS_WAVE vs DISCUSS
4. Tests validate CROSS_WAVE metadata explicitly
5. Reduced time estimate (2-3h) due to established patterns from 04-01

#### ✅ Step 04-02: Convert DESIGN Commands (design.md, diagram.md)
- **Original Risk**: 7.5/10 → **Corrected Risk**: 3.5/10
- **Original Time**: 1h → **Corrected Time**: 3-4h
- **Status**: CORRECTED - Ready after 04-01/04-01b complete
- **File**: `steps/04-02.json` (updated)

**Major Corrections**:
1. Added prerequisite checks for Phase 1 infrastructure and TOON spec
2. Added dependency on 04-01/04-01b completion (use existing patterns)
3. Added TOON compiler specification for batch compilation
4. Added partial batch failure handling (rollback ALL if one fails)
5. Added test specifications for both design and diagram commands
6. Added agent bindings: design→solution-architect, diagram→architecture-diagram-manager
7. Updated dependencies list to include previous steps

---

### Steps REMAINING (To Be Corrected)

#### ⏳ Step 04-03: Convert DISTILL Commands (distill.md, skeleton.md)
- **Original Risk**: 8.0/10
- **Target Corrected Risk**: ~3.5/10
- **Original Time**: 1h → **Target Time**: 3-4h
- **File**: `steps/04-03.json` (TO BE UPDATED)

**Planned Corrections** (from PHASE-4-CORRECTIONS-SUMMARY.md):
- Add prerequisite checks (Phase 1, TOON spec, prior steps)
- Add TOON compiler specification
- Add comprehensive error handling
- Add test specifications for distill and skeleton
- Update time estimate to 3-4h
- Add agent bindings (if applicable)

#### ⏳ Step 04-04: Convert DEVELOP Commands (8 files)
- **Original Risk**: 6.5/10
- **Target Corrected Risk**: ~3.0/10
- **Original Time**: 4h → **Target Time**: 8-12h
- **File**: `steps/04-04.json` (TO BE UPDATED)

**Planned Corrections**:
- Add prerequisite checks
- Add agent binding table for all 8 commands:
  - baseline → software-crafter
  - roadmap → software-crafter
  - split → software-crafter
  - execute → software-crafter
  - review → software-crafter-reviewer
  - develop → software-crafter
  - refactor → software-crafter
  - mikado → software-crafter
- Add refactoring rules specification (Level 1 consistency)
- Add test specifications for 8 commands
- Update time estimate to 8-12h (8 files, largest batch)

#### ⏳ Step 04-05: Convert DEMO Commands (deliver.md, finalize.md)
- **Original Risk**: 6.0/10
- **Target Corrected Risk**: ~3.0/10
- **Original Time**: 1h → **Target Time**: 3-4h
- **File**: `steps/04-05.json` (TO BE UPDATED)

**Planned Corrections**:
- Add prerequisite checks
- Add finalize-specific test suite:
  - test_finalize_parameter_parsing
  - test_finalize_agent_validation
  - test_finalize_error_handling
  - test_finalize_metadata_preservation (agent-parameter flag)
- Add agent bindings:
  - deliver → feature-completion-coordinator
  - finalize → {special case: agent-parameter dispatch}
- Update time estimate to 3-4h (finalize.md is 17K complex file)

#### ⏳ Step 04-06: Convert Final CROSS_WAVE + Validation (4 commands + all 20 validation)
- **Original Risk**: 9.5/10
- **Target Corrected Risk**: ~4.0/10
- **Original Time**: 2h → **Target Time**: 4-6h
- **File**: `steps/04-06.json` (TO BE UPDATED)

**Planned Corrections**:
- Add prerequisite checks on ALL prior steps (04-01 through 04-05)
- Add 20-command final validation test
- Add zero .md files remaining verification
- Add agent bindings for final CROSS_WAVE commands:
  - research → researcher
  - root-why → problem-analyzer
  - git → git-workflow-manager
  - forge → infrastructure-provisioner
- Update time estimate to 4-6h (final validation is comprehensive)

---

## Standardized Correction Template Applied

All corrected steps include these standardized sections:

### 1. Prerequisite Checks Section
```json
"prerequisite_checks": {
  "phase_1_toon_infrastructure": {
    "requirement": "TOON parser and compiler from Phase 1 must be complete",
    "verification": "Confirm tools/toon/compiler exists and test_toon_parser passes",
    "blocking": true,
    "escalation": "If Phase 1 incomplete, STOP - escalate to project manager"
  },
  "toon_format_specification": {
    "requirement": "TOON v3.0 format specification must be available",
    "verification": "Obtain from tools/toon/TOON-v3.0-SPEC.md or reference implementation",
    "blocking": true,
    "escalation": "If spec unavailable, create from reverse-engineering novel-editor-chatgpt-toon.txt"
  },
  "baseline_measurements": {
    "requirement": "Token count baselines from Phase 2 step 2.4",
    "verification": "Confirm baseline token counts documented",
    "blocking": false,
    "note": "Token savings validation deferred to Phase 8 if unavailable"
  }
}
```

### 2. TOON Compiler Section
```json
"toon_compiler": {
  "tool_location": "tools/toon/compiler (from Phase 1)",
  "invocation": "toon-compiler <input.toon> --validate --output <output.validated>",
  "success_criteria": [
    "Exit code = 0",
    "No errors in stderr",
    "Output file size > 1000 bytes",
    "Metadata validates against TOON v3.0 schema"
  ],
  "error_handling": {
    "compilation_failure": "Log error, do NOT proceed, escalate with error message",
    "metadata_invalid": "Review source file wave classification, retry compilation",
    "partial_failure": "Rollback all conversions, fix issue, restart batch"
  }
}
```

### 3. Error Handling Section
```json
"error_handling": {
  "compiler_not_found": {
    "detection": "Step fails with 'command not found'",
    "action": "STOP immediately, escalate: Phase 1 incomplete",
    "recovery": "Wait for Phase 1 completion, do NOT proceed"
  },
  "compilation_failure": {
    "detection": "Compiler exits with code != 0",
    "action": "Capture error message, log to docs/errors/step-XX-XX-errors.log",
    "recovery": "Review source file, fix metadata/syntax, retry compilation"
  },
  "metadata_validation_failure": {
    "detection": "Test fails on wave metadata assertion",
    "action": "Review source file wave classification, verify correctness",
    "recovery": "If classification wrong: fix source. If test wrong: fix assertion."
  }
}
```

### 4. Test Specifications Section
```json
"test_specifications": {
  "test_<command>_compiles": {
    "framework": "pytest",
    "test_code_skeleton": "def test_<command>_compiles():\n    toon_file = TOONParser().parse('<file>.toon')\n    assert toon_file.metadata['wave'] == '<WAVE>'\n    assert toon_file.compilation_errors == []",
    "assertions": [
      "File parses without errors",
      "Wave metadata == <WAVE>",
      "All required metadata fields present"
    ]
  }
}
```

### 5. Adversarial Review Summary Section
```json
"adversarial_review_summary": {
  "original_risk_score": X.X,
  "corrected_risk_score": X.X,
  "major_corrections_applied": [
    "List of all corrections applied to this step"
  ],
  "remaining_risks": [
    "Residual risks after corrections (with mitigations)"
  ]
}
```

---

## Time Estimate Corrections Summary

| Step | Original | Corrected | Increase | Rationale |
|------|----------|-----------|----------|-----------|
| 04-01 | 1h | 4-6h | 4-6x | First conversion + learning curve + prerequisites |
| 04-01b (NEW) | - | 2-3h | NEW | CROSS_WAVE conversion (split from 04-01) |
| 04-02 | 1h | 3-4h | 3-4x | DESIGN commands + format clarification |
| 04-03 | 1h | 3-4h | 3-4x | DISTILL commands + testing |
| 04-04 | 4h | 8-12h | 2-3x | 8 DEVELOP commands + agent bindings |
| 04-05 | 1h | 3-4h | 3-4x | finalize.md complexity (17K file) |
| 04-06 | 2h | 4-6h | 2-3x | Final validation + 20-command check |
| **TOTAL** | **10h** | **27-39h** | **2.7-3.9x** | Realistic estimates with contingencies |

---

## Critical Blockers Resolved

### Blocker 1: Wave Classification Contradiction
**Original Issue**: Step 04-01 claimed "Convert DISCUSS Wave Commands" but start.md is CROSS_WAVE
**Resolution**: Split into 04-01 (DISCUSS: discuss.md) and 04-01b (CROSS_WAVE: start.md)
**Impact**: Prevents quality gate failures on wave metadata validation

### Blocker 2: TOON Compiler Non-Existence
**Original Issue**: All steps reference compilation without verifying compiler exists
**Resolution**: Added prerequisite checks requiring Phase 1 completion verification
**Impact**: Early detection of missing infrastructure before starting conversion work

### Blocker 3: Unvalidated Token Savings Claims
**Original Issue**: SC7 claims "~60% token savings" without baseline measurements
**Resolution**: Removed SC7 from step-level criteria, deferred to Phase 8 validation
**Impact**: Prevents unrealistic quality gates blocking Phase 4 completion

### Blocker 4: Missing TOON Format Specification
**Original Issue**: No local TOON v3.0 format specification provided
**Resolution**: Added prerequisite requiring tools/toon/TOON-v3.0-SPEC.md or reverse-engineering from reference
**Impact**: Ensures executors have conversion guidance before starting work

### Blocker 5: Undefined Test Specifications
**Original Issue**: Test names listed without implementation details or framework
**Resolution**: Added detailed test specifications with pytest framework, code skeletons, and assertions
**Impact**: Clear testing requirements enable proper validation of conversions

---

## Validation Checklist for Corrected Steps

Each corrected step file MUST include:

- ✅ **Prerequisite Checks** - Phase 1 completion, TOON spec availability, baseline measurements
- ✅ **Compiler Specification** - Tool location, invocation syntax, success criteria
- ✅ **Error Handling** - Detection, action, recovery for all failure scenarios
- ✅ **Test Specifications** - Framework, skeleton code, assertions for each test
- ✅ **Agent Bindings** - Explicit mapping for each command (where applicable)
- ✅ **Time Estimates** - Realistic hours with justification
- ✅ **Wave Classification** - Correct wave type for each command
- ✅ **Refactoring Rules** - Specific rules when refactoring.targets non-empty
- ✅ **Adversarial Review Summary** - Original risk, corrected risk, corrections applied

---

## Next Steps

### Immediate Actions Required
1. Complete corrections for steps 04-03, 04-04, 04-05, 04-06 following the template
2. Validate all corrected steps for internal consistency
3. Create cross-reference validation ensuring dependencies are correctly sequenced
4. Generate final Phase 4 corrections summary for stakeholder review

### Before Executing Any Phase 4 Step
1. Verify Phase 1 (TOON Infrastructure) is 100% complete
2. Confirm tools/toon/compiler exists and passes smoke tests
3. Obtain TOON v3.0 format specification
4. Document or defer token baseline measurements
5. Review all prerequisite checks for BLOCKING items

### Execution Order (After All Corrections Complete)
1. **First**: Step 04-01 (discuss.md DISCUSS) - 4-6h
2. **Second**: Step 04-01b (start.md CROSS_WAVE) - 2-3h
3. **Third**: Step 04-02 (design/diagram DESIGN) - 3-4h
4. **Fourth**: Step 04-03 (distill/skeleton DISTILL) - 3-4h
5. **Fifth**: Step 04-04 (8 DEVELOP commands) - 8-12h
6. **Sixth**: Step 04-05 (deliver/finalize DEMO) - 3-4h
7. **Seventh**: Step 04-06 (final CROSS_WAVE + validation) - 4-6h

**Total Phase 4**: 27-39 hours (realistic estimate with contingencies)

---

## Files Modified/Created

### Updated Files
1. `/steps/04-01.json` - CORRECTED (DISCUSS command only)
2. `/steps/04-02.json` - CORRECTED (DESIGN commands)

### New Files Created
3. `/steps/04-01b.json` - NEW (CROSS_WAVE entry command)

### Pending Updates
4. `/steps/04-03.json` - TO BE CORRECTED
5. `/steps/04-04.json` - TO BE CORRECTED
6. `/steps/04-05.json` - TO BE CORRECTED
7. `/steps/04-06.json` - TO BE CORRECTED

### Documentation
8. `/adversarial-reviews/PHASE-4-CORRECTIONS-SUMMARY.md` - Created earlier (blueprint)
9. `/adversarial-reviews/PHASE-4-CORRECTIONS-COMPLETE.md` - THIS FILE (status tracking)

---

**Corrector**: Lyra
**Date**: 2026-01-06
**Status**: CORRECTIONS IN PROGRESS (3 of 7 complete)
**Confidence**: HIGH (corrections follow evidence-based adversarial review findings)
