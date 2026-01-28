# Evolution: Recovery Suggestion Formatting (US005 Phase 3)

**Date**: 2026-01-28
**Feature**: Implement recovery suggestion formatting and integration
**Status**: In Development (Phase 7 ongoing, Phases 1-6 complete)

## Summary

Phase 3 of the US005 Failure Recovery feature implements the presentation layer for failure recovery guidance. Users receive clearly formatted, actionable suggestions that explain:
1. **WHY** the failure happened (educational explanation)
2. **HOW** to fix it (specific steps)
3. **Actionable** element (command or path to execute)

## Phases Completed (Phases 1-6)

### ✅ Phase 1-2: Baseline & Review
- Baseline document created documenting existing Phase 3 structure
- All compliance checks passed
- Baseline approved for implementation

### ✅ Phase 3-4: Roadmap & Review
- Comprehensive roadmap created mapping 5-step implementation plan
- Technical decisions documented with rationale
- Roadmap approved by Software Crafter reviewer
- Dependencies properly mapped

### ✅ Phase 5-6: Split & Review Each Step
- 5 atomic step files verified and approved:
  - **03-01**: Format recovery suggestions with WHY + HOW + Actionable structure
  - **03-02**: Include transcript path in crash recovery suggestions
  - **03-03**: Integrate recovery suggestions with validation error messages
  - **03-04**: Integrate RecoveryGuidanceHandler with DES orchestrator
  - **03-05**: Create comprehensive failure mode registry
- All step files use v2.0 schema with 8-phase TDD cycle
- All step files passed structural review

## Phase 7: Execution (In Progress)

Executing all 5 steps with 8-phase TDD cycle (40 phases total):

| Step | Task | Status | Phases |
|------|------|--------|--------|
| 03-01 | WHY + HOW + Actionable formatting | Executing | 1-8 |
| 03-02 | Transcript path inclusion | Pending | 1-8 |
| 03-03 | Validation error integration | Pending | 1-8 |
| 03-04 | DES orchestrator integration | Pending | 1-8 |
| 03-05 | Test suite & failure registry | Pending | 1-8 |

Each step executes:
- 8 TDD phases (PREPARE → RED_ACCEPTANCE → RED_UNIT → GREEN → REVIEW → REFACTOR_CONTINUOUS → REFACTOR_L4 → COMMIT)
- Unit testing and acceptance testing validation in GREEN phase
- Continuous refactoring (L1 naming clarity + L2 complexity reduction + L3 organization)
- Optional L4 architecture refactoring
- Final validation and git commit

## Quality Gates

✅ **Baseline Review**: PASSED (1 attempt)
✅ **Roadmap Review**: PASSED (1 attempt)
✅ **Step File Reviews**: PASSED (5/5 approved)
⏳ **Phase 7 Reviews**: In progress (REVIEW phase per step - covers both implementation and post-refactoring quality)
⏳ **Mutation Testing**: Deferred to Phase 7 implementation

## Artifacts

- **Baseline**: `docs/feature/recovery-suggestion-formatting/baseline.yaml` ✅
- **Roadmap**: `docs/feature/recovery-suggestion-formatting/roadmap.yaml` ✅
- **Step Files**:
  - `docs/feature/recovery-suggestion-formatting/steps/03-01.json` ✅
  - `docs/feature/recovery-suggestion-formatting/steps/03-02.json` ✅
  - `docs/feature/recovery-suggestion-formatting/steps/03-03.json` ✅
  - `docs/feature/recovery-suggestion-formatting/steps/03-04.json` ✅
  - `docs/feature/recovery-suggestion-formatting/steps/03-05.json` ✅

## Key Implementation Details

### WHY + HOW + Actionable Format

Each recovery suggestion follows this structure:

```
WHY: 1-2 sentences explaining failure cause and implications
HOW: 1-2 sentences describing fix mechanism
ACTIONABLE: Specific command or file path to execute fix
```

**Example**:
```
WHY: The agent left GREEN phase in IN_PROGRESS state, indicating implementation
started but did not complete (typically due to unhandled error or timeout).

HOW: Reset the phase status to NOT_EXECUTED and retry the implementation
step to allow the agent another opportunity to complete the phase.

ACTIONABLE: Run: `/nw:execute @software-crafter steps/01-01.json`
```

### Integration Points

1. **Recovery Suggestions**: Displayed during step execution failures
2. **Validation Errors**: Enhanced with fix guidance
3. **Crash Recovery**: Includes transcript path for debugging
4. **Failure Registry**: Comprehensive mapping of all failure types

### Technical Decisions

| Decision | Rationale | Alternative |
|----------|-----------|-------------|
| WHY + HOW + Actionable | Balances learning with action | Just show command (loses learning) |
| Transcript path inclusion | Enables debugging without logs | Manual log search (harder for users) |
| Validation error integration | Immediate fix visibility | Separate documentation (requires search) |
| Junior-dev focused language | Increases accessibility | Technical jargon (excludes beginners) |

## Testing Strategy

- **Unit Tests**: Validate formatting, component completeness, consistency
- **Acceptance Tests**: Verify full recovery workflow end-to-end
- **Integration Tests**: Validate DES orchestrator integration
- **Mutation Testing**: >75% kill rate target for test quality validation

## Next Steps

1. **Phase 7 Continuation**: Execute steps 03-02 through 03-05
2. **Phase 7.5**: Run mutation testing for quality gate validation
3. **Phase 8**: Archive final artifacts and evolution document
4. **Phase 9**: Report completion to user

## Metrics

- **Baseline Review Time**: 1st attempt, approved
- **Roadmap Review Time**: 1st attempt, approved
- **Step Approval Rate**: 5/5 (100%)
- **Lines of Specification**: 675 lines (135 per step)
- **Expected Implementation Time**: ~6-10 hours for complete 40-phase TDD cycle (5 steps × 8 phases)

## Risk Mitigation

| Risk | Severity | Mitigation |
|------|----------|-----------|
| Suggestion formatting consistency | Medium | Step 03-04 includes standardization |
| Validation error integration | Medium | Step 03-03 specifically addresses |
| Transcript path availability | Low | Step 03-02 includes fallback guidance |
| Junior-dev appropriateness | Medium | Step 03-04 includes quality polish |

---

**Phase Status**: Phases 1-6 complete ✅ | Phase 7 in progress ⏳ | Phases 8-9 pending 📋

**For Questions**: Review roadmap.yaml for implementation details or baseline.yaml for quality gates.
