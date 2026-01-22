# Deterministic Execution System (DES) - Acceptance Criteria

**Version:** 1.0
**Date:** 2026-01-22
**Status:** DISCUSS Wave Complete
**Format:** Gherkin (Given/When/Then)

---

## Overview

This document contains User Acceptance Test (UAT) scenarios for the Deterministic Execution System. Each scenario is written in Gherkin format to enable direct translation to executable acceptance tests.

---

## Feature: Command-Origin Filtering

### Scenario 1: Happy Path - Command Task Gets Validated

```gherkin
Feature: Command-Origin Task Filtering
  As Marcus (Senior Developer)
  I want DES to validate only command-originated Task invocations
  So that ad-hoc exploration is not blocked

  Scenario: Command-originated task triggers validation
    Given Marcus invokes "/nw:execute @software-crafter steps/01-01.json"
    And the orchestrator generates a prompt with DES metadata markers
    When DES processes the Task invocation
    Then the prompt contains "<!-- DES-VALIDATION: required -->" marker
    And the prompt contains "<!-- DES-STEP-FILE: steps/01-01.json -->" marker
    And pre-invocation validation is triggered
    And validation checks for all 8 mandatory sections
    And validation checks for all 14 TDD phases
```

### Scenario 2: Ad-hoc Task Bypasses Validation

```gherkin
  Scenario: Ad-hoc task bypasses DES validation
    Given Marcus uses Task tool for exploration
    And the prompt is "Find all uses of UserRepository in the codebase"
    And no DES markers are present in the prompt
    When DES checks if validation is required
    Then validation is skipped
    And Task tool is invoked immediately
    And no validation delay occurs
```

### Scenario 3: Research Command Skips Full Validation

```gherkin
  Scenario: Research command skips heavy validation
    Given Marcus invokes "/nw:research authentication-patterns"
    And /nw:research is not in the validation-required command list
    When DES checks if validation is required
    Then only basic validation runs (no 14-phase check)
    And Task tool is invoked without blocking
```

---

## Feature: Pre-Invocation Template Validation

### Scenario 4: Complete Prompt Passes Validation

```gherkin
Feature: Pre-Invocation Template Validation
  As Priya (Tech Lead)
  I want DES to validate prompts before Task invocation
  So that sub-agents always receive complete instructions

  Scenario: Complete prompt passes all validation checks
    Given the orchestrator generates a prompt for step "01-01.json"
    And the prompt contains section "DES_METADATA"
    And the prompt contains section "AGENT_IDENTITY"
    And the prompt contains section "TASK_CONTEXT"
    And the prompt contains section "TDD_14_PHASES" with all 14 phases listed:
      # Note: Gates are QUALITY REQUIREMENTS, not phase identifiers:
      # G1=exactly 1 test active, G2=fails for business logic, G3=fails on assertion
      # G5=business language, G6=ALL tests green (applies to multiple phases)
      | Phase | Gate |
      | PREPARE | G1 |
      | RED_ACCEPTANCE | G2 |
      | RED_UNIT | G3 |
      | GREEN_UNIT | - |
      | CHECK_ACCEPTANCE | - |
      | GREEN_ACCEPTANCE | G6 |
      | REVIEW | G5 |
      | REFACTOR_L1 | G6 |
      | REFACTOR_L2 | G6 |
      | REFACTOR_L3 | G6 |
      | REFACTOR_L4 | G6 |
      | POST_REFACTOR_REVIEW | G6 |
      | FINAL_VALIDATE | - |
      | COMMIT | - |
    And the prompt contains section "QUALITY_GATES"
    And the prompt contains section "OUTCOME_RECORDING"
    And the prompt contains section "BOUNDARY_RULES"
    And the prompt contains section "TIMEOUT_INSTRUCTION"
    When pre-invocation validation runs
    Then validation status is "PASSED"
    And no errors are reported
    And Task tool invocation proceeds
    And validation duration is less than 500 milliseconds
```

### Scenario 5: Validation Failure - Missing TDD Phase

```gherkin
  Scenario: Missing TDD phase blocks Task invocation
    Given the orchestrator generates a prompt for step "01-02.json"
    And the prompt is missing the "REFACTOR_L3" phase in TDD_14_PHASES section
    When pre-invocation validation runs
    Then validation status is "FAILED"
    And error message contains "INCOMPLETE: TDD phase 'REFACTOR_L3' not mentioned"
    And Task tool is NOT invoked
    And the orchestrator receives the specific error message
    And audit log records "TASK_INVOCATION_REJECTED" event
```

### Scenario 6: Validation Failure - Missing Mandatory Section

```gherkin
  Scenario: Missing mandatory section blocks Task invocation
    Given the orchestrator generates a prompt for step "01-03.json"
    And the prompt is missing the "TIMEOUT_INSTRUCTION" section
    When pre-invocation validation runs
    Then validation status is "FAILED"
    And error message contains "MISSING: Mandatory section 'TIMEOUT_INSTRUCTION' not found"
    And Task tool is NOT invoked
    And recovery guidance suggests "Add TIMEOUT_INSTRUCTION section with turn budget guidance"
```

### Scenario 7: Multiple Validation Errors Reported

```gherkin
  Scenario: Multiple validation errors are all reported
    Given the orchestrator generates a prompt with multiple issues
    And the prompt is missing "BOUNDARY_RULES" section
    And the prompt is missing "GREEN_ACCEPTANCE" phase
    And the prompt is missing "POST_REFACTOR_REVIEW" phase
    When pre-invocation validation runs
    Then validation status is "FAILED"
    And error count is 3
    And all three errors are listed in the response
    And errors are actionable (each identifies specific missing element)
```

---

## Feature: Post-Execution State Validation

### Scenario 8: Abandoned Phase Detected After Completion

```gherkin
Feature: Post-Execution State Validation
  As Marcus (Senior Developer)
  I want DES to detect abandoned phases after sub-agent completion
  So that I'm immediately alerted to incomplete work

  Scenario: Abandoned IN_PROGRESS phase detected
    Given a software-crafter agent was executing step "01-01.json"
    And the agent crashed during "GREEN_UNIT" phase
    And the step file shows GREEN_UNIT with status "IN_PROGRESS"
    And the step file shows subsequent phases as "NOT_EXECUTED"
    When SubagentStop hook fires
    And post-execution validation runs
    Then validation status is "FAILED"
    And error message contains "Phase GREEN_UNIT left IN_PROGRESS (abandoned)"
    And step file state is updated to "FAILED"
    And recovery_suggestions array is populated
    And recovery_suggestions includes "Reset GREEN_UNIT phase status to NOT_EXECUTED"
    And audit log records "SUBAGENT_STOP_VALIDATION" with status "error"
```

### Scenario 9: Silent Completion Detected

```gherkin
  Scenario: Agent completes without updating step file
    Given a software-crafter agent was assigned step "01-02.json"
    And the agent returned successfully (no crash)
    And all phases in step file still show status "NOT_EXECUTED"
    And task state shows status "IN_PROGRESS"
    When SubagentStop hook fires
    And post-execution validation runs
    Then validation status is "FAILED"
    And error message contains "Agent completed without updating step file"
    And step file state is updated to "FAILED"
    And recovery_suggestions includes "Check agent transcript for errors"
    And recovery_suggestions includes "Verify prompt contained OUTCOME_RECORDING instructions"
```

### Scenario 10: EXECUTED Phase Missing Outcome

```gherkin
  Scenario: Phase marked EXECUTED but missing outcome details
    Given a software-crafter agent completed step "01-03.json"
    And phase "RED_UNIT" shows status "EXECUTED"
    And phase "RED_UNIT" has no "outcome" field
    When SubagentStop hook fires
    And post-execution validation runs
    Then validation status is "FAILED"
    And error message contains "Phase RED_UNIT EXECUTED without outcome"
    And step file is NOT marked as DONE
```

### Scenario 11: SKIPPED Phase Without Valid Reason

```gherkin
  Scenario: Phase marked SKIPPED without blocked_by reason
    Given a software-crafter agent completed step "01-04.json"
    And phase "REFACTOR_L4" shows status "SKIPPED"
    And phase "REFACTOR_L4" has no "blocked_by" field
    When SubagentStop hook fires
    And post-execution validation runs
    Then validation status is "FAILED"
    And error message contains "Phase REFACTOR_L4 SKIPPED without blocked_by"
```

### Scenario 12: DEFERRED Skip Blocks Commit

```gherkin
  Scenario: DEFERRED blocked_by prefix blocks commit readiness
    Given a software-crafter agent completed step "01-05.json"
    And phase "REVIEW" shows status "SKIPPED"
    And phase "REVIEW" has blocked_by "DEFERRED: Need stakeholder input"
    When SubagentStop hook fires
    And post-execution validation runs
    Then validation status is "WARNING"
    And warning message contains "Phase REVIEW has DEFERRED - blocks commit"
    And step file is NOT marked ready for commit
```

### Scenario 13: Clean Completion Passes Validation

```gherkin
  Scenario: Successful execution passes all validation checks
    Given a software-crafter agent completed step "01-06.json"
    And all 14 phases show status "EXECUTED"
    And all phases have "outcome" field populated
    And step file state shows status "DONE"
    When SubagentStop hook fires
    And post-execution validation runs
    Then validation status is "SUCCESS"
    And no errors are reported
    And no warnings are reported
    And audit log records "SUBAGENT_STOP_VALIDATION" with status "success"
```

---

## Feature: Timeout and Turn Discipline

### Scenario 14: Agent Self-Regulates on Turn Budget

```gherkin
Feature: Timeout and Turn Discipline
  As Marcus (Senior Developer)
  I want agents to self-regulate execution time
  So that runaway execution is prevented

  Scenario: Agent respects turn budget and exits gracefully
    Given a software-crafter agent is executing step "01-01.json"
    And the prompt contains TIMEOUT_INSTRUCTION with 50-turn budget
    And the agent has completed PREPARE, RED, and GREEN phases
    And the agent is stuck on REFACTOR_L2 (test keeps failing)
    And the agent has used between 40 and 48 turns
    When the agent evaluates its progress
    Then the agent recognizes it cannot complete within budget
    And the agent saves current progress to step file
    And the agent sets REFACTOR_L2 status to "IN_PROGRESS" with notes
    And the agent sets task state to "PARTIAL"
    And the agent returns with execution result containing "PARTIAL_COMPLETION"
    And remaining work is documented in recovery_suggestions
```

### Scenario 15: Watchdog Detects Stale Execution

```gherkin
  Scenario: External watchdog detects orphaned execution
    Given Marcus started "/nw:execute" 45 minutes ago
    And the process crashed without triggering SubagentStop hook
    And step file "01-07.json" shows phase "RED_UNIT" with status "IN_PROGRESS"
    And phase "RED_UNIT" started_at is 45 minutes ago
    When external watchdog runs with 30-minute stale threshold
    Then orphaned execution is detected
    And watchdog reports:
      """
      Orphaned execution detected:
      - Step: 01-07.json
      - Phase: RED_UNIT
      - Stale for: 45 minutes
      """
    And recovery options are provided
```

---

## Feature: Crash Recovery

### Scenario 16: Crash Recovery with State Preservation

```gherkin
Feature: Crash Recovery
  As Alex (Junior Developer)
  I want clear recovery guidance after failures
  So that I know exactly what to do

  Scenario: Recovery from agent crash preserves partial work
    Given Alex was running "/nw:execute @software-crafter steps/02-01.json"
    And the agent completed phases PREPARE through GREEN_UNIT
    And the agent crashed during REVIEW phase
    When SubagentStop hook fires with error context
    Then recovery handler is invoked
    And completed phases (PREPARE, RED_*, GREEN_*) are preserved
    And REVIEW phase is reset to NOT_EXECUTED
    And crash is recorded in phase history:
      """
      {
        "history": [{
          "status": "CRASHED",
          "ended_at": "2026-01-22T14:30:00Z",
          "notes": "Agent crashed during execution"
        }]
      }
      """
    And step file state is set to "FAILED"
    And recovery_suggestions includes "Run /nw:execute again to resume from REVIEW phase"
```

### Scenario 17: Recovery Guidance for Junior Developer

```gherkin
  Scenario: Alex receives educational recovery guidance
    Given Alex is a junior developer learning TDD
    And Alex's agent crashed with error "Phase GREEN_UNIT left IN_PROGRESS (abandoned)"
    When failure recovery handler runs
    Then recovery_suggestions are populated with actionable steps:
      | Step | Action |
      | 1 | "Review agent transcript at {path} for error details" |
      | 2 | "Reset GREEN_UNIT phase status to NOT_EXECUTED" |
      | 3 | "Run `/nw:execute` again to resume from GREEN_UNIT" |
    And educational context is provided:
      """
      TIP: IN_PROGRESS means the phase was started but not completed.
      This usually indicates the agent encountered an error or was interrupted.
      It's safe to reset and retry - your completed work is preserved.
      """
```

---

## Feature: Audit Trail

### Scenario 18: Complete Execution Audit Trail

```gherkin
Feature: Audit Trail
  As Priya (Tech Lead)
  I want a complete audit trail of all state transitions
  So that I can verify TDD compliance during PR review

  Scenario: Full execution creates complete audit trail
    Given Marcus invokes "/nw:execute @software-crafter steps/03-01.json" on 2026-01-22
    When the execution completes successfully through all 14 phases
    Then daily audit log "audit-2026-01-22.log" contains entries in order:
      | Event | Description |
      | TASK_INVOCATION_STARTED | Task execution initiated |
      | TASK_INVOCATION_VALIDATED | Pre-invocation validation passed |
      | PHASE_STARTED | PREPARE phase started |
      | PHASE_COMPLETED | PREPARE phase completed |
      | PHASE_STARTED | RED_ACCEPTANCE phase started |
      | PHASE_COMPLETED | RED_ACCEPTANCE phase completed |
      # ... (all 14 phases) |
      | SUBAGENT_STOP_VALIDATION | Post-execution validation passed |
    And each entry has ISO 8601 timestamp
    And each entry has step_file path
    And Priya can review daily audit logs for PR evidence
```

### Scenario 19: Audit Trail for Failed Validation

```gherkin
  Scenario: Failed validation is recorded in audit trail
    Given Marcus invokes "/nw:execute" with incomplete prompt on 2026-01-22
    When pre-invocation validation fails
    Then daily audit log "audit-2026-01-22.log" contains:
      | Event | Status |
      | TASK_INVOCATION_STARTED | initiated |
      | TASK_INVOCATION_REJECTED | failed |
    And rejected entry contains error details
    And rejected entry contains timestamp
```

### Scenario 20: Audit Trail Immutability

```gherkin
  Scenario: Audit trail cannot be modified retroactively
    Given daily audit log "audit-2026-01-22.log" contains 10 previous entries
    When a new event is logged on the same day
    Then the new entry is appended (not inserted)
    And previous entries are unchanged
    And daily audit log is append-only
    And tampering would require file-level modification (detectable)
    And new day creates new log file "audit-2026-01-23.log"
```

### Scenario 20b: Daily Log Rotation

```gherkin
  Scenario: Audit logs rotate daily to prevent file bloat
    Given Marcus executes steps on 2026-01-22
    And "audit-2026-01-22.log" accumulates 50 entries
    When Marcus continues work on 2026-01-23
    Then new events are written to "audit-2026-01-23.log"
    And "audit-2026-01-22.log" remains unchanged
    And each daily log file stays manageable in size
    And Priya can query specific dates for PR review
```

---

## Feature: Boundary Rules

### Scenario 21: Agent Stays Within Scope

```gherkin
Feature: Boundary Rules
  As Priya (Tech Lead)
  I want agents to stay within assigned scope
  So that changes are predictable and controlled

  Scenario: Agent respects file modification boundaries
    Given a software-crafter agent is executing step "04-01.json"
    And the task specifies allowed_file_patterns: ["**/UserRepository*", "**/test_user*"]
    And the agent sees an opportunity to "improve" AuthService.py
    When the agent considers modifying AuthService.py
    Then the agent respects BOUNDARY_RULES
    And AuthService.py is NOT modified
    And only files matching allowed patterns are changed
```

### Scenario 22: Scope Violation Detected Post-Execution

```gherkin
  Scenario: Scope violation is detected and logged
    Given a software-crafter agent completed step "04-02.json"
    And the task specifies allowed_file_patterns: ["**/OrderService*"]
    And git diff shows changes to "src/services/PaymentService.py"
    When SubagentStop hook runs scope validation
    Then scope violation is detected
    And warning is logged: "Unexpected modification: src/services/PaymentService.py"
    And audit log records "SCOPE_VIOLATION_WARNING"
    And Priya is alerted to review unexpected changes
```

### Scenario 23: Agent Returns Control After Completion

```gherkin
  Scenario: Agent does not continue to next step automatically
    Given a software-crafter agent successfully completed step "04-03.json"
    And step "04-04.json" is the next step in the sequence
    And the agent could theoretically continue "for efficiency"
    When the agent reaches the COMMIT phase completion
    Then BOUNDARY_RULES require: "Return control IMMEDIATELY"
    And the agent returns with execution summary
    And step "04-04.json" is NOT started
    And Marcus explicitly starts next step when ready
```

---

## Non-Functional Acceptance Criteria

### Scenario 24: Performance - Validation Speed

```gherkin
Feature: Non-Functional Requirements
  Performance, reliability, and usability requirements

  Scenario: Pre-invocation validation completes quickly
    Given a complete prompt with all 8 sections and 14 phases
    When pre-invocation validation runs
    Then validation completes in less than 500 milliseconds
    And validation does not noticeably delay workflow start
```

### Scenario 25: Reliability - Hook Firing

```gherkin
  Scenario: SubagentStop hook fires for every completion
    Given 10 different Task tool invocations
    And varying completion states (success, failure, partial)
    When each sub-agent completes
    Then SubagentStop hook fires 10 times
    And hook firing rate is 100%
    And no completions are missed
```

### Scenario 26: Usability - Error Message Clarity

```gherkin
  Scenario: Error messages are actionable and self-contained
    Given validation fails with error "MISSING: Mandatory section 'TDD_14_PHASES' not found"
    When Alex reads the error message
    Then error message contains the missing element name "TDD_14_PHASES"
    And error message contains remediation guidance "Add TDD_14_PHASES section with all 14 phases"
    And error message does NOT require external documentation lookup
    And error message includes example of correct format
```

---

## Edge Cases

### Scenario 27: Step File Does Not Exist

```gherkin
Feature: Edge Cases
  Handling unusual or error conditions

  Scenario: Referenced step file does not exist
    Given the orchestrator references step file "steps/nonexistent.json"
    And the file does not exist on disk
    When pre-invocation validation runs
    Then validation status is "FAILED"
    And error message contains "Step file not found: steps/nonexistent.json"
    And Task tool is NOT invoked
```

### Scenario 28: Invalid Step File JSON

```gherkin
  Scenario: Step file contains invalid JSON
    Given step file "steps/invalid.json" exists
    And the file content is malformed JSON
    When pre-invocation validation runs
    Then validation status is "FAILED"
    And error message contains "Step file invalid JSON"
    And specific JSON parse error is included
```

### Scenario 29: Step File Missing Required Fields

```gherkin
  Scenario: Step file missing tdd_cycle field
    Given step file "steps/incomplete.json" exists
    And the file is valid JSON
    And the file is missing "tdd_cycle" field
    When pre-invocation validation runs
    Then validation status is "FAILED"
    And error message contains "Step file missing field: tdd_cycle"
```

### Scenario 30: Step File Has Wrong Phase Count

```gherkin
  Scenario: Step file has incorrect number of phases
    Given step file "steps/wrong-phases.json" exists
    And the file has only 10 phases in phase_execution_log
    When pre-invocation validation runs
    Then validation status is "FAILED"
    And error message contains "Step file has 10 phases, expected 14"
```

### Scenario 31: Concurrent Step File Access Prevention

```gherkin
Feature: Concurrent Execution Protection
  As Priya (Tech Lead)
  I want DES to prevent concurrent access to the same step file
  So that state corruption from race conditions is avoided

  Scenario: Second agent blocked when step already in progress
    Given agent A is executing step "01-01.json"
    And step file state is "IN_PROGRESS"
    And phase RED_UNIT is marked IN_PROGRESS with timestamp
    When agent B attempts to execute the same step "01-01.json"
    Then agent B receives error "STEP_LOCKED: Step 01-01.json is already being executed"
    And error includes lock holder info: "Locked by agent A since {timestamp}"
    And agent B does NOT proceed with execution
    And agent A continues uninterrupted
```

### Scenario 32: Watchdog Intervention on Stale Execution

```gherkin
Feature: Watchdog Automatic Intervention
  As Priya (Tech Lead)
  I want the watchdog to take corrective action on stale executions
  So that abandoned work doesn't block future executions

  Scenario: Watchdog marks stale execution as abandoned
    Given step "01-01.json" has phase RED_UNIT marked IN_PROGRESS
    And the IN_PROGRESS timestamp is 45 minutes ago
    And no agent is currently running (session terminated)
    When the external watchdog runs with 30-minute threshold
    Then watchdog detects stale execution for step "01-01.json"
    And watchdog sets phase RED_UNIT status to "ABANDONED"
    And watchdog adds recovery_suggestions to step file:
      | Suggestion |
      | "Review agent transcript for error details" |
      | "Reset RED_UNIT to NOT_EXECUTED to retry" |
      | "Run /nw:execute to resume from RED_UNIT" |
    And watchdog logs "WATCHDOG_INTERVENTION" event to audit trail
    And step file is now unlocked for new execution
```

---

## Summary

| Category | Scenario Count |
|----------|----------------|
| Command-Origin Filtering | 3 |
| Pre-Invocation Validation | 4 |
| Post-Execution Validation | 6 |
| Timeout/Turn Discipline | 2 |
| Crash Recovery | 2 |
| Audit Trail | 4 |
| Boundary Rules | 3 |
| Non-Functional | 3 |
| Edge Cases | 4 |
| Concurrent Execution Protection | 1 |
| Watchdog Intervention | 1 |
| **Total** | **33** |

---

*Acceptance criteria created by Riley (product-owner) during DISCUSS wave.*

---

## Product Owner Review

**Reviewer**: product-owner-reviewer (Sage)
**Date**: 2026-01-22
**Overall Assessment**: NEEDS_REVISION

### Coverage Analysis

| Feature Area | Happy Path | Failure Scenarios | Edge Cases | Status |
|--------------|------------|-------------------|------------|--------|
| Command-Origin Filtering | Sc.1 | Sc.2, Sc.3 | - | Adequate |
| Pre-Invocation Validation | Sc.4 | Sc.5, Sc.6, Sc.7 | Sc.27-30 | Good |
| Post-Execution Validation | Sc.13 | Sc.8, Sc.9, Sc.10, Sc.11, Sc.12 | - | Good |
| Timeout/Turn Discipline | Sc.14 | Sc.15 | - | Needs Work |
| Crash Recovery | Sc.16 | Sc.17 | - | Adequate |
| Audit Trail | Sc.18 | Sc.19 | Sc.20 | Needs Work |
| Boundary Rules | Sc.21 | Sc.22 | Sc.23 | Good |
| Non-Functional | Sc.24, Sc.25 | - | - | Needs Work |
| Edge Cases | - | Sc.27-30 | - | Incomplete |

### Critiques

| # | Scenario | Issue | Severity | Recommendation |
|---|----------|-------|----------|----------------|
| 1 | Sc.4 | Phase/Gate mapping shows G6 for GREEN_ACCEPTANCE (phase 6) AND all REFACTOR phases (8-12). Gate numbering appears inconsistent or erroneous. | HIGH | Verify correct gate numbers. G2 typically maps to RED_ACCEPTANCE, G6 to final REFACTOR gate. Clarify gate semantics or fix numbering. |
| 2 | Sc.26 | "Alex understands what is missing" is subjective and not automatable. Cannot programmatically verify human comprehension. | HIGH | Rewrite to objective criteria: "Then error message contains the missing element name" AND "Then error message contains remediation guidance" |
| 3 | Sc.14 | "approximately 45 turns" is imprecise. Automation cannot reliably test approximate values. | MEDIUM | Define explicit threshold: "And the agent has used between 40-45 turns" or use a concrete value |
| 4 | Sc.15 | Watchdog only DETECTS but never TAKES ACTION. Missing scenario for watchdog intervention (e.g., marking step as TIMED_OUT). | MEDIUM | Add scenario: "Then watchdog sets phase status to ABANDONED" or "Then watchdog notifies orchestrator to intervene" |
| 5 | Sc.20 | "tampering would require file-level modification (detectable)" is vague. No verification mechanism specified. | MEDIUM | Add: "And each entry includes SHA-256 hash of previous entry" or specify detection mechanism |
| 6 | Sc.25 | "10 different Task tool invocations" lacks specificity on what variations matter (success/failure/partial mix). | MEDIUM | Specify: "Given 5 successful, 3 failed, and 2 partial completions" |
| 7 | - | Missing edge case: Concurrent execution (two agents attempt same step file). | MEDIUM | Add scenario: "Given agent A is executing step 01-01.json When agent B attempts to execute same step Then agent B receives STEP_LOCKED error" |
| 8 | - | Missing edge case: Malformed DES marker (present but invalid format). | LOW | Add scenario: "Given prompt contains malformed marker `<!-- DES-VALIDATION: unknown -->` Then validation fails with INVALID_MARKER error" |
| 9 | - | Missing edge case: Audit log write failure (disk full, permissions). | LOW | Add scenario: "Given audit log directory is not writable When validation completes Then execution continues but AUDIT_FAILURE warning is logged to stderr" |

### Strengths

1. **Comprehensive persona coverage**: All three personas (Marcus, Priya, Alex) are represented with scenarios matching their specific concerns
2. **Strong Given/When/Then discipline**: Most scenarios follow proper Gherkin structure with clear preconditions, actions, and outcomes
3. **Good failure scenario coverage**: Each feature area includes multiple failure paths, not just happy paths
4. **Actionable error messages**: Scenarios consistently require specific, actionable error messages (e.g., "MISSING: Mandatory section X")
5. **Clear traceability to user stories**: Scenarios map well to US-001 through US-007
6. **Recovery guidance emphasis**: Multiple scenarios address recovery suggestions, supporting junior developers
7. **Audit trail focus**: Strong coverage of compliance verification needs for Tech Lead persona
8. **Data tables used effectively**: Scenario 4 and 17 use tables to enumerate complex data clearly

### Missing Scenarios

| Priority | Missing Scenario | Rationale |
|----------|-----------------|-----------|
| HIGH | Concurrent step file access | Production systems may have race conditions |
| MEDIUM | Watchdog intervention action | Detection without action is incomplete |
| MEDIUM | Audit log unavailable | Graceful degradation path needed |
| LOW | Malformed DES marker | Defensive validation for corrupted prompts |
| LOW | Step file locked by another process | Real-world file system scenarios |
| LOW | Network timeout during validation | For distributed deployments |

### Traceability Matrix

| User Story | Acceptance Criteria | Scenarios | Coverage |
|------------|--------------------:|-----------|----------|
| US-001 | AC-001.1, AC-001.2, AC-001.3, AC-001.4 | Sc.1, Sc.2, Sc.3 | Complete |
| US-002 | AC-002.1, AC-002.2, AC-002.3, AC-002.4, AC-002.5 | Sc.4, Sc.5, Sc.6, Sc.7, Sc.24 | Complete |
| US-003 | AC-003.1, AC-003.2, AC-003.3, AC-003.4, AC-003.5, AC-003.6 | Sc.8, Sc.9, Sc.10, Sc.11, Sc.12, Sc.13 | Complete |
| US-004 | AC-004.1, AC-004.2, AC-004.3, AC-004.4, AC-004.5 | Sc.18, Sc.19, Sc.20 | Partial (AC-004.2 verification weak) |
| US-005 | AC-005.1, AC-005.2, AC-005.3, AC-005.4, AC-005.5 | Sc.16, Sc.17 | Complete |
| US-006 | AC-006.1, AC-006.2, AC-006.3, AC-006.4, AC-006.5 | Sc.14, Sc.15 | Partial (AC-006.5 action missing) |
| US-007 | AC-007.1, AC-007.2, AC-007.3, AC-007.4, AC-007.5 | Sc.21, Sc.22, Sc.23 | Complete |

### Recommendation

**Status: NEEDS_REVISION before DISTILL wave**

The acceptance criteria document is well-structured with good coverage of happy paths and failure scenarios. However, the following items MUST be addressed before proceeding:

**Must Fix (Blocking)**:
1. **Scenario 4**: Verify and correct phase-to-gate mapping. Current G6 assignment to multiple phases appears erroneous.
2. **Scenario 26**: Rewrite with objective, automatable assertions.

**Should Fix (Non-Blocking but Important)**:
3. **Scenario 14**: Replace "approximately" with precise threshold.
4. **Add concurrent execution edge case** - critical for production reliability.
5. **Add watchdog intervention scenario** - detection without action is incomplete.

**May Fix (Recommended)**:
6. Clarify audit log immutability verification mechanism in Scenario 20.
7. Add edge cases for audit log failure and malformed markers.

Once HIGH severity issues are resolved, scenarios are ready for translation to executable acceptance tests in DISTILL wave.

---

*Review completed by Sage (product-owner-reviewer) on 2026-01-22.*
