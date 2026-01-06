# Phase 5 Execution Checklist

**Purpose**: Step-by-step checklist for executing Phase 5 with circular dependency fix
**Total Estimated Time**: 14 hours (with parallel execution) | 17 hours (sequential)
**Corrected Version**: 2.0 (2026-01-06)

---

## Pre-Execution Verification

- [ ] Step 1.6 (Integration Tests) is complete
- [ ] TOON compiler is functional
- [ ] software-crafter agent specification is available
- [ ] All corrected step specifications reviewed and approved

**ABORT CONDITIONS**:
- If step 1.6 not complete: Phase 5 cannot start
- If TOON compiler missing: Phase 5 will fail at compilation
- If agent spec unavailable: Methodology references cannot be validated

---

## PHASE A: Prerequisites Resolution (4 hours)

**Step**: 05-01 Phase A
**Goal**: Resolve all blocking unknowns before implementation

### Research Tasks

- [ ] **Task A1**: Research TOON v3.0 skill syntax
  - Review TOON parser code
  - Examine existing templates
  - Identify skill-specific syntax features
  - Document differences between COMMAND and SKILL formats
  - **Output**: `docs/toon-v3-skill-syntax-specification.md`

- [ ] **Task A2**: Research skill invocation mechanism
  - Understand Claude Code auto-invocation
  - Determine if MCP protocol used
  - Identify trigger pattern matching algorithm
  - Document test simulation approach
  - **Output**: `docs/skill-invocation-mechanism.md`

- [ ] **Task A3**: Define constraint embedding format
  - Determine where constraints appear in SKILL.md
  - Define format (YAML metadata? Structured section? Comments?)
  - Show examples of each project constraint embedded
  - **Output**: `docs/constraint-embedding-format.md`

- [ ] **Task A4**: Create SKILL_TEMPLATE.toon
  - Combine syntax from A1, invocation from A2, constraints from A3
  - Create reference template demonstrating all features
  - Include placeholder trigger patterns
  - Include placeholder agent binding
  - Include placeholder methodology reference
  - **Output**: `5d-wave/templates/SKILL_TEMPLATE.toon`

- [ ] **Task A5**: Set up test environment
  - Define test framework (pytest, custom simulator)
  - Document how to simulate user input triggering skills
  - Explain assertion patterns for skill validation
  - Provide setup/teardown instructions
  - **Output**: `tests/skills/skill_test_environment_setup.md`

### Validation Gates (Phase A)

- [ ] **GATE A1**: All 5 documents exist and are complete
- [ ] **GATE A2**: SKILL_TEMPLATE.toon compiles successfully to SKILL.md
- [ ] **GATE A3**: Compiled SKILL.md demonstrates all required features
- [ ] **GATE A4**: Test environment setup instructions are executable

**CHECKPOINT**: Review all Phase A deliverables with team
**DECISION**: GO / NO-GO for Phase B implementation

---

## PHASE B1: develop Skill Implementation (3 hours)

**Step**: 05-01 Phase B
**Prerequisites**: Phase A complete, GATE A1-A4 passed

### Implementation Tasks

- [ ] **Task B1.1**: Copy SKILL_TEMPLATE.toon to `5d-wave/skills/develop/SKILL.toon`

- [ ] **Task B1.2**: Customize develop skill trigger patterns
  - Italian: "implementa", "scrivi codice", "TDD"
  - English: "implement", "write code"
  - **Verify**: No substring overlaps with refactor/mikado patterns (to be defined later)

- [ ] **Task B1.3**: Define develop workflow steps
  - implement -> review -> fix -> refactor
  - Document each step's purpose
  - Reference software-crafter agent commands

- [ ] **Task B1.4**: Embed default constraints using Phase A format
  - DO NOT CREATE NEW REPORT FILES
  - DO NOT COMMIT BEFORE USER APPROVAL
  - FOCUS ON DELIVERABLES ONLY
  - (All 5 project baseline constraints)

- [ ] **Task B1.5**: Compile SKILL.toon to SKILL.md
  - Run TOON compiler
  - Verify output SKILL.md is well-formed
  - **Output**: `5d-wave/skills/develop/SKILL.md`

- [ ] **Task B1.6**: Write E2E test for develop skill triggering
  - Test: User says "implementa questa feature" -> skill triggers
  - Use test environment from Phase A
  - **Output**: E2E test in test suite

- [ ] **Task B1.7**: Run all develop skill tests
  - test_phase_b_skill_compiles
  - test_phase_b_trigger_patterns_multilingual
  - test_phase_b_agent_binding
  - test_phase_b_workflow_steps_present
  - test_phase_b_constraints_embedded

- [ ] **Task B1.8**: Apply refactoring level 2 (if needed)

### Validation Gates (Phase B1)

- [ ] **GATE B1.1**: develop SKILL.toon compiles without errors
- [ ] **GATE B1.2**: develop SKILL.md contains all required sections
- [ ] **GATE B1.3**: All develop skill tests pass (100%)
- [ ] **GATE B1.4**: E2E test passes (skill triggers correctly)

**CHECKPOINT**: develop skill proven functional
**DECISION**: GO / NO-GO for Phase B2/B3 (parallel execution)

---

## PHASE B2/B3: refactor and mikado Skills (3 hours - PARALLEL)

**Steps**: 05-02 (refactor) and 05-03 (mikado) in parallel
**Prerequisites**: 05-01 Phase A+B complete, GATE B1.1-B1.4 passed

### Implementation Tasks - refactor Skill (05-02)

- [ ] **Task B2.1**: Copy SKILL_TEMPLATE.toon to `5d-wave/skills/refactor/SKILL.toon`

- [ ] **Task B2.2**: Customize refactor skill trigger patterns
  - Level-specific: "refactor-level-1", "refactor-level-2", ..., "refactor-level-6"
  - Generic: "progressive-refactoring", "code-structure-improvement", "cleanup-codebase"
  - Italian: "refactoring sistematico"
  - **CRITICAL**: Remove "improve code" (collision with develop)

- [ ] **Task B2.3**: Reference progressive refactoring methodology
  - List all 6 level names
  - Provide one-sentence description per level
  - Add decision guidance: When to use refactor vs develop vs mikado
  - Validate against software-crafter agent specification

- [ ] **Task B2.4**: Embed default constraints using Phase A format

- [ ] **Task B2.5**: Compile SKILL.toon to SKILL.md
  - **Output**: `5d-wave/skills/refactor/SKILL.md`

- [ ] **Task B2.6**: Update trigger pattern conflict matrix
  - Document all refactor patterns
  - Verify no overlaps with develop patterns
  - **Output**: Updated conflict matrix

- [ ] **Task B2.7**: Write E2E test for refactor skill
  - Test: User says "refactoring sistematico livello 2" -> skill triggers

- [ ] **Task B2.8**: Run all refactor skill tests

### Implementation Tasks - mikado Skill (05-03)

- [ ] **Task B3.1**: Copy SKILL_TEMPLATE.toon to `5d-wave/skills/mikado/SKILL.toon`

- [ ] **Task B3.2**: Customize mikado skill trigger patterns
  - Complexity-focused: "mikado-method", "refactoring-complesso", "dependency-mapping", "complex-refactoring-graph"
  - Italian: "metodo-mikado"

- [ ] **Task B3.3**: Reference Mikado method workflow
  - List 4-step cycle: Goal -> Experiment -> Visualize -> Revert
  - Provide brief description of each step
  - Add decision guidance: When to use mikado vs refactor vs develop
  - Validate against software-crafter agent specification

- [ ] **Task B3.4**: Embed default constraints using Phase A format

- [ ] **Task B3.5**: Compile SKILL.toon to SKILL.md
  - **Output**: `5d-wave/skills/mikado/SKILL.md`

- [ ] **Task B3.6**: Update trigger pattern conflict matrix
  - Document all mikado patterns
  - Verify no overlaps with develop or refactor patterns
  - **Output**: Updated conflict matrix

- [ ] **Task B3.7**: Write E2E test for mikado skill
  - Test: User says "metodo mikado per refactoring complesso" -> skill triggers

- [ ] **Task B3.8**: Run all mikado skill tests

### Validation Gates (Phase B2/B3)

- [ ] **GATE B2.1**: refactor SKILL.toon compiles without errors
- [ ] **GATE B2.2**: refactor SKILL.md contains all required sections
- [ ] **GATE B2.3**: All refactor skill tests pass (100%)
- [ ] **GATE B2.4**: E2E test passes (refactor skill triggers correctly)

- [ ] **GATE B3.1**: mikado SKILL.toon compiles without errors
- [ ] **GATE B3.2**: mikado SKILL.md contains all required sections
- [ ] **GATE B3.3**: All mikado skill tests pass (100%)
- [ ] **GATE B3.4**: E2E test passes (mikado skill triggers correctly)

- [ ] **GATE CROSS**: Trigger pattern conflict matrix shows NO OVERLAPS across all 3 skills

**CHECKPOINT**: All three skills exist, compile, and work independently
**DECISION**: GO / NO-GO for Phase C (validation)

---

## PHASE C: Validation (4 hours)

**Step**: 05-04
**Prerequisites**: 05-01/05-02/05-03 all complete, GATE B1-B3 + CROSS passed

### Prerequisite Verification

- [ ] **VERIFY C0.1**: `5d-wave/skills/develop/SKILL.md` exists
- [ ] **VERIFY C0.2**: `5d-wave/skills/refactor/SKILL.md` exists
- [ ] **VERIFY C0.3**: `5d-wave/skills/mikado/SKILL.md` exists
- [ ] **VERIFY C0.4**: All 3 skills compile without errors
- [ ] **VERIFY C0.5**: Trigger pattern conflict matrix reviewed (no overlaps)
- [ ] **VERIFY C0.6**: Test environment from Phase A is functional

**ABORT**: If any prerequisite fails, return to corresponding Phase B step

### Validation Tasks

- [ ] **Task C1**: Create test harness infrastructure
  - Use test environment from 05-01 Phase A
  - **Output**: `tests/skills/test_harness_base.py` (if needed)

- [ ] **Task C2**: Implement trigger pattern validation tests
  - **Output**: `tests/skills/test_skill_triggers.py`
  - Test: develop skill triggers on "implementa", "implement", "TDD", etc.
  - Test: refactor skill triggers on "refactor-level-3", "progressive-refactoring", etc.
  - Test: mikado skill triggers on "mikado-method", "refactoring-complesso", etc.

- [ ] **Task C3**: Implement trigger pattern conflict detection tests
  - **Output**: `tests/skills/test_trigger_pattern_conflicts.py`
  - Test: User says "improve code" -> does NOT trigger multiple skills
  - Test: User says "refactoring" -> correct skill triggers (refactor, not mikado)
  - Test: Cross-skill collision matrix validation

- [ ] **Task C4**: Implement false positive tests
  - **Output**: `tests/skills/test_no_false_positives.py`
  - Test 11 unrelated inputs (see PHASE-5-CIRCULAR-DEPENDENCY-FIX.md for list)
  - Example: "I want to redesign my kitchen" -> NO skill triggers

- [ ] **Task C5**: Implement agent chaining validation tests
  - **Output**: `tests/skills/test_agent_chaining.py`
  - Test: develop skill binds to software-crafter agent
  - Test: refactor skill binds to software-crafter agent
  - Test: mikado skill binds to software-crafter agent

- [ ] **Task C6**: Run comprehensive test suite
  - All trigger pattern tests
  - All conflict detection tests
  - All false positive tests
  - All agent chaining tests

- [ ] **Task C7**: Generate validation report
  - **Output**: `docs/skills/validation-report.md`
  - Summary: All tests passed / X tests failed
  - Details: Test results by category
  - Recommendations: Any issues discovered

### Validation Gates (Phase C)

- [ ] **GATE C1**: All trigger pattern tests pass (100%)
- [ ] **GATE C2**: All conflict detection tests pass (100%)
- [ ] **GATE C3**: All false positive tests pass (100%)
- [ ] **GATE C4**: All agent chaining tests pass (100%)
- [ ] **GATE C5**: Validation report generated and reviewed

**CHECKPOINT**: All skills validated and ready for integration
**DECISION**: GO / NO-GO for Phase 6 (Integration)

---

## Phase 5 Completion Criteria

### All Deliverables Exist

**Phase A** (5 documents):
- [ ] `docs/toon-v3-skill-syntax-specification.md`
- [ ] `docs/skill-invocation-mechanism.md`
- [ ] `docs/constraint-embedding-format.md`
- [ ] `5d-wave/templates/SKILL_TEMPLATE.toon`
- [ ] `tests/skills/skill_test_environment_setup.md`

**Phase B** (3 skills):
- [ ] `5d-wave/skills/develop/SKILL.toon` + `.md`
- [ ] `5d-wave/skills/refactor/SKILL.toon` + `.md`
- [ ] `5d-wave/skills/mikado/SKILL.toon` + `.md`

**Phase C** (4 test suites + 1 report):
- [ ] `tests/skills/test_skill_triggers.py`
- [ ] `tests/skills/test_trigger_pattern_conflicts.py`
- [ ] `tests/skills/test_no_false_positives.py`
- [ ] `tests/skills/test_agent_chaining.py`
- [ ] `docs/skills/validation-report.md`

**Total**: 13 deliverables (5 + 6 + 4 + 1 report)

### All Quality Gates Passed

- [ ] Phase A: All 4 gates passed
- [ ] Phase B1: All 4 gates passed (develop skill)
- [ ] Phase B2: All 4 gates passed (refactor skill)
- [ ] Phase B3: All 4 gates passed (mikado skill)
- [ ] Phase CROSS: No trigger pattern overlaps
- [ ] Phase C: All 5 gates passed (validation)

**Total**: 22 quality gates (4 + 4 + 4 + 4 + 1 + 5)

### All Tests Passing

- [ ] develop skill tests (100%)
- [ ] refactor skill tests (100%)
- [ ] mikado skill tests (100%)
- [ ] Trigger pattern validation tests (100%)
- [ ] Conflict detection tests (100%)
- [ ] False positive tests (100%)
- [ ] Agent chaining tests (100%)

**Total**: 7 test categories (all must be 100%)

---

## Timeline Summary

### Sequential Execution

| Phase | Step | Hours | Cumulative |
|-------|------|-------|------------|
| A | 05-01 Phase A | 4 | 4 |
| B1 | 05-01 Phase B | 3 | 7 |
| B2 | 05-02 | 3 | 10 |
| B3 | 05-03 | 3 | 13 |
| C | 05-04 | 4 | **17** |

**Total**: 17 hours

---

### Parallel Execution (Recommended)

| Phase | Step | Hours | Cumulative |
|-------|------|-------|------------|
| A | 05-01 Phase A | 4 | 4 |
| B1 | 05-01 Phase B | 3 | 7 |
| B2/B3 | 05-02 \|\| 05-03 (parallel) | 3 | 10 |
| C | 05-04 | 4 | **14** |

**Total**: 14 hours
**Time Savings**: 3 hours (18% reduction)

---

## Risk Mitigation

### Checkpoints

1. **After Phase A**: Review all prerequisite documents (GO/NO-GO decision)
2. **After Phase B1**: Verify develop skill works (GO/NO-GO for parallel execution)
3. **After Phase B2/B3**: Verify all 3 skills work independently and no conflicts
4. **After Phase C**: Validation report reviewed and approved

### Abort Conditions

| Checkpoint | Abort Condition | Recovery Action |
|------------|-----------------|-----------------|
| Phase A | Any prerequisite document incomplete | Return to research tasks, complete missing items |
| Phase B1 | develop skill fails to compile or test | Debug TOON syntax, fix compilation errors |
| Phase B2 | refactor skill conflicts with develop | Revise trigger patterns, update conflict matrix |
| Phase B3 | mikado skill conflicts with develop/refactor | Revise trigger patterns, update conflict matrix |
| Phase C | Validation tests fail | Return to corresponding Phase B step, fix issues |

---

## Success Criteria (Phase 5 Complete)

- ✅ All 13 deliverables created
- ✅ All 22 quality gates passed
- ✅ All 7 test categories at 100%
- ✅ Validation report shows complete success
- ✅ No blocking issues for Phase 6
- ✅ Circular dependency eliminated (proven via execution)
- ✅ All skills trigger correctly with no collisions

**Phase 5 Status**: READY FOR INTEGRATION (Phase 6)

---

## Next Phase Handoff

**Handoff to**: Phase 6 (Integration and Delivery)

**Deliverables Provided**:
- 3 working skills (develop, refactor, mikado)
- Complete trigger pattern conflict matrix
- Test harness and validation tests
- Validation report confirming functionality

**Success Criteria Met**:
- SC4: Skills auto-invoked correctly ✅
- SC5: Full workflow functional ✅
- SC6: Default constraints integrated ✅

**Ready for**: Integration with plugin marketplace, user acceptance testing, production deployment
