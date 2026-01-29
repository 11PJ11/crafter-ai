# Step File Generation Summary

**Project:** des-us006
**Generated:** 2026-01-29
**Total Steps:** 19
**Acceptance Tests:** 12
**Schema Version:** 2.0 (8-phase TDD cycle)

## Generation Complete ✓

All 19 atomic task files have been successfully generated from the roadmap.

### Files Created

```
docs/feature/des-us006/steps/
├── 01-01.json  ✓
├── 01-02.json  ✓
├── 01-03.json  ✓
├── 01-04.json  ✓
├── 01-05.json  ✓
├── 02-00.json  ✓  [CRITICAL - Entry Point]
├── 02-01.json  ✓  [CRITICAL - Implementation]
├── 02-02.json  ✓
├── 02-03.json  ✓
├── 02-04.json  ✓
├── 03-01.json  ✓
├── 03-02.json  ✓
├── 03-03.json  ✓  [CRITICAL - Wiring Verification]
├── 04-01.json  ✓
├── 04-02.json  ✓
├── 04-03.json  ✓
├── 04-04.json  ✓
├── 05-01.json  ✓
├── 05-02.json  ✓
├── 05-03.json  ✓
└── 05-04.json  ✓
```

## Step-to-Scenario Mapping

Each step maps to ONE specific acceptance test scenario (or N/A for infrastructure):

| Step ID | Step Name | Acceptance Test Scenario | Scenario Function |
|---------|-----------|-------------------------|-------------------|
| 01-01 | Design TIMEOUT_INSTRUCTION content structure | test_scenario_009 | test_scenario_009_timeout_instruction_has_complete_structure |
| 01-02 | Create helper method _render_turn_budget() | test_scenario_002 | test_scenario_002_timeout_instruction_specifies_turn_budget |
| 01-03 | Create helper method _render_progress_checkpoints() | test_scenario_003 | test_scenario_003_timeout_instruction_defines_progress_checkpoints |
| 01-04 | Create helper method _render_early_exit_protocol() | test_scenario_004 | test_scenario_004_timeout_instruction_documents_early_exit_protocol |
| 01-05 | Create helper method _render_turn_logging_instruction() | test_scenario_005 | test_scenario_005_timeout_instruction_requires_turn_count_logging |
| 02-00 | Create render_full_prompt() public entry point | test_scenario_001 | test_scenario_001_des_validated_prompt_includes_timeout_instruction_section |
| 02-01 | Integrate TIMEOUT_INSTRUCTION into render_prompt() | test_scenario_001 | Makes scenarios 001-005 GREEN |
| 02-02 | Verify /nw:develop command includes TIMEOUT_INSTRUCTION | test_scenario_010 | test_scenario_010_develop_command_also_includes_timeout_instruction |
| 02-03 | Verify ad-hoc tasks have NO TIMEOUT_INSTRUCTION | test_scenario_006 | test_scenario_006_ad_hoc_task_has_no_timeout_instruction |
| 02-04 | Verify research commands have NO TIMEOUT_INSTRUCTION | test_scenario_007 | test_scenario_007_research_command_has_no_timeout_instruction |
| 03-01 | Verify missing TIMEOUT_INSTRUCTION blocks invocation | test_scenario_008 | test_scenario_008_missing_timeout_instruction_blocks_invocation |
| 03-02 | Verify complete TIMEOUT_INSTRUCTION passes validation | test_scenario_009 | test_scenario_009_timeout_instruction_has_complete_structure |
| 03-03 | Verify end-to-end wiring integration | test_scenario_009 | test_scenario_009_timeout_instruction_has_complete_structure |
| 04-01 | Refactor helper methods for DRY principle | N/A - refactoring | All existing tests must remain GREEN |
| 04-02 | Add comprehensive unit tests for helper methods | N/A - infrastructure | Unit test coverage |
| 04-03 | Verify orchestrator.py LOC within target (750) | N/A - infrastructure | LOC target verification |
| 04-04 | Update DES documentation with TIMEOUT_INSTRUCTION spec | N/A - infrastructure | Documentation update |
| 05-01 | Verify all 12 acceptance tests GREEN | test_scenario_001 | All 12 scenarios (final validation) |
| 05-02 | Validate baseline metrics achieved | N/A - infrastructure | Baseline metrics validation |
| 05-03 | Run full DES test suite regression check | N/A - infrastructure | Regression testing |
| 05-04 | Create production readiness checklist and sign-off | N/A - infrastructure | Production readiness checklist |

## Acceptance Test Coverage

All 12 acceptance test scenarios are mapped to steps:

1. **test_scenario_001** - Section presence → Steps: 02-00, 02-01, 05-01
2. **test_scenario_002** - Turn budget → Steps: 01-02, 02-00, 02-01, 05-01
3. **test_scenario_003** - Progress checkpoints → Steps: 01-03, 02-00, 02-01, 05-01
4. **test_scenario_004** - Early exit protocol → Steps: 01-04, 02-00, 02-01, 05-01
5. **test_scenario_005** - Turn count logging → Steps: 01-05, 02-00, 02-01, 05-01
6. **test_scenario_006** - Ad-hoc no timeout → Steps: 02-03, 05-01
7. **test_scenario_007** - Research no timeout → Steps: 02-04, 05-01
8. **test_scenario_008** - Missing blocks invocation → Steps: 03-01, 05-01
9. **test_scenario_009** - Complete structure → Steps: 01-01, 03-02, 03-03, 05-01
10. **test_scenario_010** - Develop command timeout → Steps: 02-02, 05-01
11. **test_scenario_013** - Timeout warnings at thresholds → Steps: 05-01
12. **test_scenario_014** - Warnings in prompt → Steps: 05-01

## Schema Compliance

All step files use the canonical TDD cycle schema v2.0 with:

- **8 mandatory phases**: PREPARE, RED_ACCEPTANCE, RED_UNIT, GREEN, REVIEW, REFACTOR_CONTINUOUS, REFACTOR_L4, COMMIT
- **phase_execution_log**: Empty initially, populated during execution
- **acceptance_test mapping**: Each step maps to specific scenario
- **quality_gates**: Standard gates (acceptance tests, unit tests, mutation score, coverage)
- **validation status**: All start as "pending"

## Critical Path Steps

Three CRITICAL steps identified in roadmap:

1. **02-00** - Create render_full_prompt() entry point
   - Fixes external validity failure (missing method acceptance tests invoke)
   - Makes 5 acceptance tests GREEN (scenarios 001-005)

2. **02-01** - Integrate TIMEOUT_INSTRUCTION rendering
   - Closes validation gap (validator requires section, orchestrator now generates it)
   - Core implementation that makes acceptance tests GREEN

3. **03-03** - Verify end-to-end wiring
   - Validates complete call chain: render_full_prompt() → render_prompt() → helpers → content
   - Proves external validity (feature accessible and functional)

## Parallel Execution Groups

**Phase 01 - Helper Methods (Parallel Group):**
- Steps 01-02, 01-03, 01-04, 01-05 can execute in parallel after 01-01 completes
- Time savings: ~6 hours (8 hours sequential → 2 hours parallel)

**Phase 02 - Command Validation (Parallel Group):**
- Steps 02-02, 02-03, 02-04 can execute in parallel after 02-01 completes
- Time savings: ~2 hours (3 hours sequential → 1 hour parallel)

## Validation

All JSON files validated:
- ✓ Valid JSON syntax
- ✓ Required fields present
- ✓ Schema v2.0 compliance
- ✓ Acceptance test mapping complete
- ✓ Dependencies correctly specified

## Next Steps

The step files are ready for execution via `/nw:execute` command:

```bash
# Execute steps sequentially or in parallel groups
/nw:execute @software-crafter steps/01-01.json
/nw:execute @software-crafter steps/01-02.json
# ... continue through all 19 steps
```

## Notes

- **Infrastructure steps** (04-01 through 04-04, 05-02 through 05-04) do not create new acceptance tests
- **Refactoring steps** (04-01) must keep all existing tests GREEN
- **Final validation** (05-01) ensures all 12 acceptance tests pass
- **Baseline metrics** (05-02) validates achievement of 6 metrics from baseline.yaml
