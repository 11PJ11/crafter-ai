# Phase 2 Step Corrections Summary

**Date**: 2026-01-06
**Corrected By**: Lyra
**Steps Corrected**: 02-01, 02-02, 02-03, 02-04

## Overview

All Phase 2 steps have been systematically corrected based on adversarial review findings. The corrections address critical blocking issues, inconsistencies, and missing specifications that would have caused execution failures.

---

## Step 02-01: Convert software-crafter.md to TOON

### Critical Corrections

1. **Added Token Baseline Capture** (CRITICAL for Phase 8 SC7)
   - NEW deliverable: `baseline/token-measurements/02-01-pre-conversion.json`
   - Measurement method: tiktoken library with cl100k_base encoding
   - Required fields: step_id, file_path, measurement_date, tokenizer, total_tokens, file_size_bytes, line_count
   - **Impact**: Phase 8 can now validate SC7 (token count improvements)

2. **Added Phase 1 Completion Prerequisites**
   - Blocking conditions verify compiler exists and passes tests
   - Pre-flight checks validate Phase 1 completion before starting
   - **Impact**: Prevents execution when dependencies not ready

3. **Added Embedded Knowledge Marker Preservation**
   - Explicit acceptance criterion for BUILD:INJECT sections
   - New test: `test_toon_preserves_embedded_knowledge_markers`
   - **Impact**: Prevents silent data loss during conversion

4. **Revised Time Estimate**
   - Changed from 3-4 hours to 5-6 hours
   - Based on realistic task breakdown
   - **Impact**: More accurate project timeline

### Remediations Applied

- **CONT-01**: Added blocking_conditions requiring Phase 1 complete
- **CONT-02**: Token baseline capture added with full specification
- **ASS-03**: Realistic time estimate (5-6 hours vs 3-4 hours)
- **TEST-GAP-04**: Removed token savings test (savings calculated in Phase 8)
- **TEST-GAP-05**: Added embedded knowledge marker preservation test

---

## Step 02-02: Round-Trip Validation

### Critical Corrections

1. **Added Pattern Discovery Requirement**
   - NEW deliverable: `baseline/patterns/02-02-discovered-patterns.json`
   - Minimum 5 conversion patterns and 3 edge cases
   - **Impact**: Step 2.3 now has explicit input for documentation

2. **Defined Semantic Equivalence Formula**
   - Weighted scoring: commands (30%) + dependencies (30%) + frontmatter (20%) + sections (10%) + embedded knowledge (10%)
   - Pass threshold: >= 95%
   - Acceptable vs unacceptable differences documented
   - **Impact**: Objective validation criteria, no ambiguity

3. **Specified Validation Script Contract**
   - Function signature: `validate_roundtrip(original_md_path: str, compiled_md_path: str) -> dict`
   - Complete return schema with all required fields
   - **Impact**: Implementation now has clear specification

4. **Defined Critical Sections**
   - Explicit 5-category list: commands, dependencies, agent_metadata, persona_definition, embed_knowledge_paths
   - **Impact**: No guesswork on what "critical" means

5. **Revised Time Estimate**
   - Changed from 1-2 hours to 2-3 hours
   - Accounts for validator complexity and pattern enumeration
   - **Impact**: Realistic schedule

### Remediations Applied

- **CONTRA-3**: Semantic equivalence formula with weighted scoring
- **CONTRA-4**: Embedded knowledge preservation as explicit criterion
- **C1**: Complete validation script specification
- **C3**: Critical sections defined with 5 categories
- **MISSING_CONTEXT**: Pattern discovery specification added

---

## Step 02-03: Document Conversion Patterns

### Critical Corrections

1. **Added Input Dependency Validation**
   - Blocking condition: `baseline/patterns/02-02-discovered-patterns.json` MUST exist
   - Minimum content requirement: 5 patterns, 3 edge cases
   - **Impact**: Prevents documentation without source data

2. **Made Acceptance Criteria Measurable**
   - Changed from "documents syntax" to ">= 10 TOON syntax features"
   - Changed from "includes examples" to ">= 10 conversion examples"
   - Changed from "lists edge cases" to ">= 5 edge cases with strategies"
   - **Impact**: Objective completion validation

3. **Added Example Validation Tests**
   - `test_readme_examples_are_valid_toon_syntax` - compiler validation
   - `test_readme_examples_use_generic_placeholders` - portability check
   - **Impact**: Examples proven correct, not assumed

4. **Added Genericization Requirements**
   - Explicit rules: replace agent names with `<agent-name>`, paths with `<path-to-X>`
   - Test validates no software-crafter-specific references
   - **Impact**: Examples portable to Phase 3 batch conversions

5. **Revised Time Estimate**
   - Changed from 0.5 hours to 1.5-2 hours
   - Accounts for thorough documentation and validation
   - **Impact**: Realistic timeline

### Remediations Applied

- **CONTRADICTION-1**: Input dependency explicitly required with validation
- **CONTRADICTION-3**: Measurable acceptance criteria with thresholds
- **ASSUMPTION-5**: Validation tests prove examples valid
- **BLOCKING-ISSUE-4**: Numeric thresholds for all criteria

---

## Step 02-04: Archive Original MD Files

### Critical Corrections

1. **Clarified Source Directories** (CRITICAL)
   - Agents: `nWave/agents/*.md` (28 files - source files)
   - Commands: `dist/ide/commands/dw/*.md` (20 files)
   - Explicitly documented: DO NOT archive `dist/ide/agents/dw/` (compiled output)
   - **Impact**: Correct files archived, no confusion

2. **Added SHA256 Checksum Verification**
   - MANIFEST.txt with checksums for all 48 files
   - Test validates byte-for-byte integrity
   - **Impact**: Prevents silent corruption, ensures archive usability

3. **Added Phase 8 Integration Documentation**
   - Documented how archive is used for validation
   - Specified restoration procedure
   - **Impact**: Archive purpose clear, rollback mechanism defined

4. **Removed .gitkeep Contradiction**
   - Removed .gitkeep from deliverables (directory contains 48 files)
   - **Impact**: No confusion about empty directory placeholders

5. **Revised Time Estimate**
   - Changed from 0.5 hours to 0.5-1 hours
   - Accounts for checksum validation complexity
   - **Impact**: Realistic with contingency

### Remediations Applied

- **C1-SOURCE-AMBIGUITY**: Explicit source directories with rationale
- **H1-INCOMPLETE-CRITERIA**: File count and checksum verification
- **M1-PHASE-8-REFERENCE**: Phase 8 integration documented
- **GITKEEP-CONTRADICTION**: Removed unnecessary .gitkeep

---

## Cross-Step Improvements

### Token Baseline Capture (Phase 8 SC7 Validation)

**Problem**: Phase 8 SC7 requires token count improvements measurement, but no baseline existed.

**Solution**:
- Step 02-01 now captures token baseline BEFORE conversion
- Storage: `baseline/token-measurements/02-01-pre-conversion.json`
- Methodology: tiktoken/cl100k_base (GPT-4 tokenizer)
- Required fields: total_tokens, file_size_bytes, line_count, timestamp

**Impact**: Phase 8 can now objectively measure token improvements.

---

### Pattern Discovery Chain (Step 2.2 → 2.3)

**Problem**: Step 2.3 documentation had no input source for patterns.

**Solution**:
- Step 02-02 now produces `baseline/patterns/02-02-discovered-patterns.json`
- Minimum 5 patterns and 3 edge cases required
- Step 02-03 validates this file exists before starting
- Step 02-03 tests verify all patterns documented

**Impact**: Phase 3 batch migration has validated, concrete patterns to follow.

---

### Blocking Conditions Throughout

All steps now include explicit blocking conditions:

**02-01**:
- Phase 1 complete
- Compiler exists and passes tests
- TOON v3.0 spec accessible

**02-02**:
- Step 2.1 complete (software-crafter.toon exists)
- Token baseline exists
- Compiler functional

**02-03**:
- Step 2.2 complete
- Patterns file exists with minimum content

**02-04**:
- Step 2.3 complete

**Impact**: No step starts without validated prerequisites.

---

## Time Estimate Adjustments

| Step | Original | Corrected | Change | Rationale |
|------|----------|-----------|--------|-----------|
| 02-01 | 3-4h | 5-6h | +2h | Token baseline capture, comprehensive testing |
| 02-02 | 1-2h | 2-3h | +1h | Pattern enumeration, validator complexity |
| 02-03 | 0.5h | 1.5-2h | +1.5h | Thorough documentation, validation, genericization |
| 02-04 | 0.5h | 0.5-1h | +0.5h | Checksum verification, potential edge cases |
| **Total** | **5.5-8h** | **9.5-12h** | **+4-5h** | **More realistic estimates** |

---

## Risk Reduction

### Before Corrections

- **Step 02-01**: Risk Score 8.5/10 (multiple blocking issues)
- **Step 02-02**: Risk Score 8.5/10 (vague specifications)
- **Step 02-03**: Risk Score 8/10 (no input, unmeasurable criteria)
- **Step 02-04**: Risk Score 8/10 (source ambiguity, no verification)

### After Corrections

- **Step 02-01**: Estimated 4/10 (blocking conditions clear, token baseline defined)
- **Step 02-02**: Estimated 3.5/10 (validation specified, patterns required)
- **Step 02-03**: Estimated 3/10 (measurable criteria, input validated)
- **Step 02-04**: Estimated 2.5/10 (sources explicit, checksums verify)

**Overall Phase 2 Risk Reduction**: From HIGH RISK to MEDIUM-LOW RISK

---

## Validation Checklist for Corrected Steps

Before executing Phase 2, verify:

- [ ] Phase 1 complete (steps 1.1-1.6 with passing tests)
- [ ] TOON compiler exists: `tools/toon/compiler.py`
- [ ] Compiler version validated: `python tools/toon/compiler.py --version` returns v3.0+
- [ ] TOON v3.0 specification accessible
- [ ] tiktoken library available: `pip install tiktoken`
- [ ] Baseline directories created: `baseline/token-measurements/`, `baseline/patterns/`
- [ ] Archive directory ready: `archive/pre-toon-migration/`
- [ ] All blocking conditions understood and verifiable

---

## Next Actions

1. **Review corrected JSON files** with stakeholders
2. **Validate Phase 1 completion** before starting Phase 2
3. **Execute steps sequentially** with blocking condition checks
4. **Monitor time estimates** against actuals for future calibration

---

## Files Modified

- `/mnt/c/Repositories/Projects/ai-craft/docs/workflow/plugin-marketplace-migration/steps/02-01.json`
- `/mnt/c/Repositories/Projects/ai-craft/docs/workflow/plugin-marketplace-migration/steps/02-02.json`
- `/mnt/c/Repositories/Projects/ai-craft/docs/workflow/plugin-marketplace-migration/steps/02-03.json`
- `/mnt/c/Repositories/Projects/ai-craft/docs/workflow/plugin-marketplace-migration/steps/02-04.json`

**All corrections applied systematically based on adversarial review findings.**
