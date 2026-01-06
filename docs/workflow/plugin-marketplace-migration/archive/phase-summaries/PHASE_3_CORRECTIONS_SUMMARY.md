# Phase 3 Step Corrections Summary

**Date**: 2026-01-06
**Corrected By**: Lyra (software-crafter mode)
**Steps Corrected**: 03-01, 03-02, 03-03

## Agent Count Reconciliation

**VERIFIED AGENT COUNT: 28 total agents**

Breakdown:
- **1 pilot agent** (step 2.1): software-crafter
- **10 primary agents** (step 3.1): product-owner, solution-architect, acceptance-designer, skeleton-builder, researcher, devop, troubleshooter, visual-architect, illustrator, data-engineer
- **11 reviewer agents** (step 3.2): acceptance-designer-reviewer, agent-builder-reviewer, data-engineer-reviewer, devop-reviewer, illustrator-reviewer, product-owner-reviewer, skeleton-builder-reviewer, software-crafter-reviewer, solution-architect-reviewer, troubleshooter-reviewer, visual-architect-reviewer
- **6 remaining agents** (step 3.3): agent-builder, avvocato, cv-optimizer, novel-editor, novel-editor-reviewer, researcher-reviewer

**Verification**: 1 + 10 + 11 + 6 = 28 ✓

## Corrections Applied to All Phase 3 Steps

### 1. Agent Count Consistency
- **Fixed**: Clarified Phase 3 purpose statement to "Convert remaining 27 agents to TOON format (28 total including pilot)"
- **Fixed**: All acceptance criteria now reference 28 total agents consistently
- **Fixed**: Added agent count reconciliation section to step 03-03 review metadata

### 2. Prerequisite Validation Framework
**Added to all steps (03-01, 03-02, 03-03):**
- TOON toolchain exists and is functional (blocking)
- Phase 2.4 archive is complete with 28 agents (blocking)
- Conversion patterns documented in tools/toon/README.md (blocking)
- Previous steps complete (03-03 only: blocks on 03-01 and 03-02 completion)

### 3. Token Savings Measurement
**Changed approach:**
- **Before**: Hard threshold "Token savings >= 50% per file" (acceptance criterion)
- **After**: "Token savings measured and documented (no hard threshold - measurement only)"
- **Rationale**: No baseline measurements exist yet, making hard threshold unachievable. Changed to measurement-only to enable validation without blocking on arbitrary threshold.

### 4. Time Estimate Revisions
**Based on adversarial review findings:**
- **Step 03-01**: 5 hours → **10-15 hours** (realistic for 10 agents with validation)
- **Step 03-02**: 5 hours → **10-15 hours** (realistic for 11 reviewers with critique dimension validation)
- **Step 03-03**: 2-3 hours → **5-8 hours** (realistic for final 6 agents with comprehensive validation)

**Total Phase 3 revised estimate**: 25-38 hours (was 12-13 hours)

### 5. Test Specifications Enhanced
**Added concrete test assertions:**
- test_each_agent_compiles_successfully
- test_each_agent_has_all_commands_from_original
- test_each_agent_has_all_dependencies_from_original
- test_token_count_per_agent_vs_baseline
- test_compiled_output_valid_yaml_frontmatter
- test_no_critical_sections_missing
- test_critique_dimensions_preserved_per_reviewer (03-02 only)
- test_total_agent_toon_count_equals_28 (03-03 only)
- test_no_orphan_md_files_in_agents_directory (03-03 only)
- test_archive_integrity_28_agents (03-03 only)

### 6. Error Handling Procedures
**Added comprehensive error handling for:**
- TOON toolchain missing → HALT, complete Phase 1 (16-19 hours)
- Archive incomplete → HALT, verify/re-run step 2.4 (0.5-2 hours)
- Agent compilation fails → Log error, fix syntax, continue with others (15-60 min/agent)
- Round-trip validation fails → Review differences, fix if critical (30-90 min/agent)
- Token savings below expectations → Document actual, no blocking
- Critique dimensions missing (03-02) → Fix TOON structure, recompile (30-90 min/reviewer)
- Orphan .md files found (03-03) → Identify, verify archive, remove (30-60 min)
- Agent count mismatch (03-03) → Investigate, reconcile (1-2 hours)

### 7. Round-Trip Validation
**Added to all steps:**
- Compare compiled output with archived original
- Validate semantic equivalence >= 95%
- Detect information loss during conversion
- Explicit workflow step and acceptance criterion

### 8. Completion Verification (Step 03-03)
**Added explicit verification commands:**
```bash
find 5d-wave/agents/ -name '*.toon' | wc -l  # expect: 28
find 5d-wave/agents/ -name '*.md' | wc -l    # expect: 0
ls archive/pre-toon-migration/agents/ | wc -l # expect: 28
```

## Critical Blocker Mitigations

### From Adversarial Reviews
All critical blockers identified in adversarial reviews have been addressed:

1. **TOON v3.0 Specification Missing**
   - Mitigation: Prerequisite check with blocking validation
   - Resolution if missing: Complete Phase 1 (16-19 hours)

2. **Compiler Tool Unvalidated**
   - Mitigation: Prerequisite check for functional compiler
   - Resolution if missing: Complete Phase 1.2 (6 hours)

3. **Baseline Token Measurements Missing**
   - Mitigation: Changed from hard threshold to measurement documentation
   - Prerequisite check for archive completion

4. **Reference Patterns Undefined**
   - Mitigation: Prerequisite check for tools/toon/README.md with examples
   - Resolution if missing: Document patterns (3 hours)

5. **Test Specifications Too Vague**
   - Mitigation: Expanded test specifications with concrete assertions
   - Added 6-10 specific test cases per step

6. **Critique Dimensions Definition Unclear (Step 03-02)**
   - Mitigation: Added prerequisite check for critique dimensions documentation
   - Added reviewer-specific validation tests
   - Added reviewer-specific notes about dimension preservation

## Files Modified

1. `/mnt/c/Repositories/Projects/ai-craft/docs/workflow/plugin-marketplace-migration/steps/03-01.json`
2. `/mnt/c/Repositories/Projects/ai-craft/docs/workflow/plugin-marketplace-migration/steps/03-02.json`
3. `/mnt/c/Repositories/Projects/ai-craft/docs/workflow/plugin-marketplace-migration/steps/03-03.json`

## Validation Status

- ✅ Agent count consistent across all steps (28 total)
- ✅ Prerequisite checks added to all steps
- ✅ Time estimates revised to realistic values
- ✅ Error handling procedures comprehensive
- ✅ Test specifications concrete and measurable
- ✅ Token savings changed from hard gate to measurement
- ✅ Round-trip validation added to all steps
- ✅ Critical blockers from adversarial reviews mitigated

## Next Actions

1. Review corrected step specifications with user
2. Verify prerequisite checks are appropriate for project context
3. Confirm revised time estimates align with project timeline
4. Proceed with Phase 3 execution when prerequisites are met

## Notes

- All corrections preserve the original intent while addressing identified gaps
- No code implementation changes - only step specification JSON corrections
- Corrections based on adversarial review findings and agent count verification from baseline.yaml
- Prerequisite validation framework ensures systematic blocking on missing dependencies
