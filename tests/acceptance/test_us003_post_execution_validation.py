"""
E2E Acceptance Test: US-003 Post-Execution State Validation

PERSONA: Marcus (Senior Developer)
STORY: As a senior developer, I want DES to automatically detect when phases are
       left abandoned (IN_PROGRESS) after sub-agent completion, so that I'm
       immediately alerted to incomplete work instead of discovering it hours later.

BUSINESS VALUE:
- Detects crashed agents before developers waste debugging time
- Catches silent completions where agent returned without updating state
- Validates execution integrity with specific, actionable error messages
- Enables immediate intervention instead of hours-later discovery

SCOPE: Covers US-003 Acceptance Criteria (AC-003.1 through AC-003.6)
WAVE: DISTILL (Acceptance Test Creation)
STATUS: RED (Outside-In TDD - awaiting DEVELOP wave implementation)
"""

import pytest
import json
from typing import Protocol, Optional


# =============================================================================
# HOOK INTERFACE DEFINITION (Protocol for implementation guidance)
# =============================================================================


class SubagentStopHookResult(Protocol):
    """Expected interface for SubagentStop hook validation result.

    Developer implementing the hook should return an object matching this protocol.
    """

    validation_status: str  # "PASSED" or "FAILED"
    abandoned_phases: list[str]  # Phases left with IN_PROGRESS status
    incomplete_phases: list[str]  # Phases with EXECUTED but no outcome
    invalid_skips: list[str]  # Phases with SKIPPED but no blocked_by
    error_count: int
    error_type: Optional[str]  # e.g., "ABANDONED_PHASE", "SILENT_COMPLETION"
    error_message: Optional[str]
    recovery_suggestions: list[str]  # Minimum 3 if FAILED


# =============================================================================
# DEVELOP WAVE MAPPING
# =============================================================================
#
# All 8 scenarios map to single DEVELOP step:
#   Step: "Implement SubagentStop validation hook"
#
# Each scenario represents a VALIDATION RULE the hook must enforce:
#   - Scenario 1: Hook fires on completion (AC-003.1)
#   - Scenario 2: Abandoned phases detected (AC-003.2)
#   - Scenario 3: Silent completion flagged (AC-003.3)
#   - Scenario 4: Missing outcome detected (AC-003.4)
#   - Scenario 5: Invalid skip detected (AC-003.5)
#   - Scenario 6: Multiple errors with recovery (AC-003.6)
#   - Scenario 7: Clean completion passes (happy path)
#   - Scenario 8: Valid skip passes (happy path)
#
# Recovery Suggestion Quality Requirements:
#   - Each suggestion >= 1 complete sentence (20+ chars)
#   - At least one explains WHY error occurred
#   - At least one explains HOW to fix
#   - Example: "Phase GREEN_UNIT left IN_PROGRESS because agent crashed.
#              Run `/nw:execute @software-crafter steps/01-01.json` to resume."
# =============================================================================


class TestPostExecutionStateValidation:
    """E2E acceptance tests for US-003: Post-execution state validation."""

    # =========================================================================
    # AC-003.1: SubagentStop hook fires for every sub-agent completion
    # Scenario 1: SubagentStop hook invoked on agent completion
    # =========================================================================

    @pytest.mark.skip(reason="Outside-In TDD RED state - awaiting DEVELOP wave")
    def test_subagent_stop_hook_fires_on_agent_completion(
        self, tmp_project_root, minimal_step_file
    ):
        """
        GIVEN software-crafter agent completes step 01-01 execution
        WHEN the sub-agent returns control to orchestrator
        THEN SubagentStop hook fires and validates step file state

        Business Value: Marcus receives immediate feedback on execution state
                       the moment an agent completes, preventing silent failures
                       from going unnoticed until the next day.

        Domain Example: Software-crafter finishes step 01-01, hook validates
                       that all started phases were properly completed.
        """
        # Arrange: Create step file with completed execution
        step_data = _create_step_file_with_all_phases_executed()
        minimal_step_file.write_text(json.dumps(step_data, indent=2))

        # Act: Trigger SubagentStop hook (simulates agent completion)
        # from des.hooks import SubagentStopHook
        # hook = SubagentStopHook()
        # hook_result = hook.on_agent_complete(step_file_path=str(minimal_step_file))

        # Assert: Hook fired and performed validation
        # assert hook_result.hook_fired is True
        # assert hook_result.step_file_validated is True
        # assert hook_result.validation_timestamp is not None
        # assert "SUBAGENT_STOP_VALIDATION" in audit_log.get_recent_events()

    # =========================================================================
    # AC-003.2: Phases with status "IN_PROGRESS" after completion are flagged
    # Scenario 2: Abandoned phase detected after agent crash
    # =========================================================================

    @pytest.mark.skip(reason="Outside-In TDD RED state - awaiting DEVELOP wave")
    def test_abandoned_in_progress_phase_detected(
        self, tmp_project_root, minimal_step_file
    ):
        """
        GIVEN software-crafter agent crashed during GREEN_UNIT phase
        AND step file shows GREEN_UNIT with status "IN_PROGRESS"
        WHEN SubagentStop hook fires after agent process terminates
        THEN hook detects abandoned phase and flags it with specific error

        Business Value: Marcus is immediately alerted when an agent crashes
                       mid-execution, avoiding 2+ hours of debugging time
                       discovering the issue the next day.

        Domain Example: Agent was implementing GREEN_UNIT, crashed due to
                       network error. GREEN_UNIT left as IN_PROGRESS, which
                       indicates work was started but never completed.

        Error Format: "Phase GREEN_UNIT left IN_PROGRESS (abandoned)"
        """
        # Arrange: Create step file with abandoned IN_PROGRESS phase
        step_data = _create_step_file_with_abandoned_phase(
            abandoned_phase="GREEN_UNIT", last_completed_phase="RED_UNIT"
        )
        minimal_step_file.write_text(json.dumps(step_data, indent=2))

        # Act: Trigger SubagentStop hook
        # from des.hooks import SubagentStopHook
        # hook = SubagentStopHook()
        # hook_result = hook.on_agent_complete(step_file_path=str(minimal_step_file))

        # Assert: Abandoned phase detected with specific error message
        # assert hook_result.validation_status == "FAILED"
        # assert hook_result.abandoned_phases == ["GREEN_UNIT"]
        # assert "Phase GREEN_UNIT left IN_PROGRESS (abandoned)" in hook_result.error_message
        # assert hook_result.step_state_updated_to == "FAILED"
        # assert hook_result.notification_sent is True

    # =========================================================================
    # AC-003.3: Tasks marked "DONE" with "NOT_EXECUTED" phases are flagged
    # Scenario 3: Silent completion detected (agent returned without executing)
    # =========================================================================

    @pytest.mark.skip(reason="Outside-In TDD RED state - awaiting DEVELOP wave")
    def test_done_task_with_not_executed_phases_flagged(
        self, tmp_project_root, minimal_step_file
    ):
        """
        GIVEN software-crafter agent returned without updating step file
        AND task status shows "IN_PROGRESS" but all phases show "NOT_EXECUTED"
        WHEN SubagentStop hook fires
        THEN hook detects mismatch and flags as silent completion error

        Business Value: Marcus catches agents that claimed to work but
                       actually did nothing, preventing false confidence
                       in task completion.

        Domain Example: Agent received step 01-01 but encountered an error
                       early and returned without starting any phases.
                       All 14 phases still show NOT_EXECUTED.

        Error Format: "Agent completed without updating step file"
        """
        # Arrange: Create step file where task is IN_PROGRESS but no phases executed
        step_data = _create_step_file_with_silent_completion()
        minimal_step_file.write_text(json.dumps(step_data, indent=2))

        # Act: Trigger SubagentStop hook
        # from des.hooks import SubagentStopHook
        # hook = SubagentStopHook()
        # hook_result = hook.on_agent_complete(step_file_path=str(minimal_step_file))

        # Assert: Silent completion detected
        # assert hook_result.validation_status == "FAILED"
        # assert hook_result.error_type == "SILENT_COMPLETION"
        # assert "Agent completed without updating step file" in hook_result.error_message
        # assert hook_result.not_executed_phases == 14
        # assert hook_result.recovery_suggestions is not None
        # assert len(hook_result.recovery_suggestions) >= 1

    # =========================================================================
    # AC-003.4: "EXECUTED" phases without outcome field are flagged
    # Scenario 4: Incomplete phase execution detected (no outcome recorded)
    # =========================================================================

    @pytest.mark.skip(reason="Outside-In TDD RED state - awaiting DEVELOP wave")
    def test_executed_phase_without_outcome_flagged(
        self, tmp_project_root, minimal_step_file
    ):
        """
        GIVEN step file shows REFACTOR_L1 phase with status "EXECUTED"
        AND the phase has no outcome field (outcome is None or missing)
        WHEN SubagentStop hook validates the step file
        THEN hook flags the phase as incomplete execution

        Business Value: Marcus ensures all executed phases have documented
                       outcomes, maintaining audit trail for Priya's PR reviews
                       and preventing "I finished but didn't record what I did"
                       situations.

        Domain Example: Agent marked REFACTOR_L1 as EXECUTED but forgot to
                       record what refactoring was actually done. Without
                       outcome, there's no evidence of work.

        Error Format: "Phase REFACTOR_L1 marked EXECUTED but missing outcome"
        """
        # Arrange: Create step file with EXECUTED phase missing outcome
        step_data = _create_step_file_with_missing_outcome(phase_name="REFACTOR_L1")
        minimal_step_file.write_text(json.dumps(step_data, indent=2))

        # Act: Trigger SubagentStop hook
        # from des.hooks import SubagentStopHook
        # hook = SubagentStopHook()
        # hook_result = hook.on_agent_complete(step_file_path=str(minimal_step_file))

        # Assert: Missing outcome detected
        # assert hook_result.validation_status == "FAILED"
        # assert hook_result.incomplete_phases == ["REFACTOR_L1"]
        # assert "Phase REFACTOR_L1 marked EXECUTED but missing outcome" in hook_result.error_message
        # assert hook_result.error_type == "MISSING_OUTCOME"

    # =========================================================================
    # AC-003.5: "SKIPPED" phases must have valid `blocked_by` reason
    # Scenario 5: Skipped phase with missing blocked_by reason flagged
    # =========================================================================

    @pytest.mark.skip(reason="Outside-In TDD RED state - awaiting DEVELOP wave")
    def test_skipped_phase_without_blocked_by_reason_flagged(
        self, tmp_project_root, minimal_step_file
    ):
        """
        GIVEN step file shows REFACTOR_L3 phase with status "SKIPPED"
        AND the phase has no blocked_by reason (blocked_by is None or empty)
        WHEN SubagentStop hook validates the step file
        THEN hook flags the skip as invalid (must have justification)

        Business Value: Marcus ensures all skipped phases have documented
                       reasons, preventing arbitrary phase skipping without
                       justification. Priya can verify during PR review that
                       skips were legitimate.

        Domain Example: Agent skipped REFACTOR_L3 but didn't explain why.
                       Without blocked_by, we can't verify if skip was valid
                       (e.g., "No L3 complexity found") or just laziness.

        Error Format: "Phase REFACTOR_L3 marked SKIPPED but missing blocked_by reason"
        """
        # Arrange: Create step file with SKIPPED phase missing blocked_by
        step_data = _create_step_file_with_invalid_skip(skipped_phase="REFACTOR_L3")
        minimal_step_file.write_text(json.dumps(step_data, indent=2))

        # Act: Trigger SubagentStop hook
        # from des.hooks import SubagentStopHook
        # hook = SubagentStopHook()
        # hook_result = hook.on_agent_complete(step_file_path=str(minimal_step_file))

        # Assert: Invalid skip detected
        # assert hook_result.validation_status == "FAILED"
        # assert hook_result.invalid_skips == ["REFACTOR_L3"]
        # assert "Phase REFACTOR_L3 marked SKIPPED but missing blocked_by reason" in hook_result.error_message
        # assert hook_result.error_type == "INVALID_SKIP"

    # =========================================================================
    # AC-003.6: Validation errors trigger FAILED state with recovery suggestions
    # Scenario 6: Multiple validation errors trigger FAILED state
    # =========================================================================

    @pytest.mark.skip(reason="Outside-In TDD RED state - awaiting DEVELOP wave")
    def test_validation_errors_trigger_failed_state_with_recovery(
        self, tmp_project_root, minimal_step_file
    ):
        """
        GIVEN step file has multiple issues:
          - GREEN_UNIT status "IN_PROGRESS" (abandoned)
          - REVIEW status "EXECUTED" but no outcome
        WHEN SubagentStop hook validates the step file
        THEN step file state is set to FAILED with all errors listed
        AND recovery suggestions are provided for each error type

        Business Value: Marcus receives comprehensive failure report with
                       clear recovery path, enabling immediate resolution
                       without guesswork.

        Domain Example: Agent crashed during GREEN_UNIT and also forgot to
                       record REVIEW outcome. Both issues reported together
                       with specific recovery steps for each.

        Recovery Suggestions Expected:
        - "Review agent transcript for error details"
        - "Reset GREEN_UNIT phase status to NOT_EXECUTED"
        - "Run `/nw:execute` again to resume from GREEN_UNIT"
        - "Add outcome to REVIEW phase from transcript evidence"
        """
        # Arrange: Create step file with multiple validation issues
        step_data = _create_step_file_with_multiple_issues()
        minimal_step_file.write_text(json.dumps(step_data, indent=2))

        # Act: Trigger SubagentStop hook
        # from des.hooks import SubagentStopHook
        # hook = SubagentStopHook()
        # hook_result = hook.on_agent_complete(step_file_path=str(minimal_step_file))

        # Assert: FAILED state set with comprehensive recovery guidance
        # assert hook_result.validation_status == "FAILED"
        # assert hook_result.error_count == 2
        # assert "GREEN_UNIT" in str(hook_result.abandoned_phases)
        # assert "REVIEW" in str(hook_result.incomplete_phases)

        # Assert: Step file updated with FAILED state
        # updated_step = json.loads(minimal_step_file.read_text())
        # assert updated_step["state"]["status"] == "FAILED"
        # assert updated_step["state"]["failure_reason"] is not None

        # Assert: Recovery suggestions provided with explicit format requirements
        # REQUIREMENT: Each suggestion must be actionable and educational
        # assert len(hook_result.recovery_suggestions) >= 3
        #
        # FORMAT REQUIREMENT 1: Each suggestion >= 1 complete sentence
        # for suggestion in hook_result.recovery_suggestions:
        #     assert len(suggestion) >= 20, "Suggestion too short to be actionable"
        #     assert suggestion[0].isupper(), "Suggestion should start with capital"
        #     assert suggestion.rstrip().endswith(('.', '`', '"')), "Suggestion should end properly"
        #
        # FORMAT REQUIREMENT 2: At least one suggestion explains WHY error occurred
        # why_patterns = ["because", "since", "left in", "was not", "missing", "without"]
        # assert any(
        #     any(p in s.lower() for p in why_patterns)
        #     for s in hook_result.recovery_suggestions
        # ), "At least one suggestion must explain WHY error occurred"
        #
        # FORMAT REQUIREMENT 3: At least one suggestion explains HOW to fix
        # how_patterns = ["/nw:execute", "run", "reset", "add", "update", "set"]
        # assert any(
        #     any(p in s.lower() for p in how_patterns)
        #     for s in hook_result.recovery_suggestions
        # ), "At least one suggestion must explain HOW to fix"
        #
        # CONTENT: Specific recovery actions expected
        # assert any("transcript" in s.lower() for s in hook_result.recovery_suggestions)
        # assert any("reset" in s.lower() or "status" in s.lower() for s in hook_result.recovery_suggestions)
        # assert any("/nw:execute" in s or "resume" in s.lower() for s in hook_result.recovery_suggestions)

    # =========================================================================
    # Happy Path: Clean completion passes validation silently
    # Scenario 7: All phases executed correctly - validation passes
    # =========================================================================

    @pytest.mark.skip(reason="Outside-In TDD RED state - awaiting DEVELOP wave")
    def test_clean_completion_passes_validation(
        self, tmp_project_root, minimal_step_file
    ):
        """
        GIVEN software-crafter agent completes all 14 phases successfully
        AND each phase shows "EXECUTED" with valid outcome
        AND step file status is "DONE"
        WHEN SubagentStop hook validates the step file
        THEN validation passes successfully
        AND audit log records successful completion

        Business Value: Marcus confirms that properly completed steps are
                       validated silently without unnecessary alerts, allowing
                       smooth workflow continuation.

        Domain Example: Agent executed all 14 phases (PREPARE through COMMIT),
                       each with recorded outcome. Step status is DONE.
                       Validation confirms integrity and logs success.
        """
        # Arrange: Create step file with clean, complete execution
        step_data = _create_step_file_with_clean_completion()
        minimal_step_file.write_text(json.dumps(step_data, indent=2))

        # Act: Trigger SubagentStop hook
        # from des.hooks import SubagentStopHook
        # hook = SubagentStopHook()
        # hook_result = hook.on_agent_complete(step_file_path=str(minimal_step_file))

        # Assert: Validation passes silently
        # assert hook_result.validation_status == "PASSED"
        # assert hook_result.abandoned_phases == []
        # assert hook_result.incomplete_phases == []
        # assert hook_result.invalid_skips == []
        # assert hook_result.error_message is None

        # Assert: Audit log records success
        # assert "SUBAGENT_STOP_VALIDATION" in audit_log.get_recent_events()
        # recent_event = audit_log.get_last_event()
        # assert recent_event["event_type"] == "SUBAGENT_STOP_VALIDATION"
        # assert recent_event["status"] == "success"

    # =========================================================================
    # Edge Case: Valid skip with proper blocked_by reason passes
    # Scenario 8: Legitimately skipped phases pass validation
    # =========================================================================

    @pytest.mark.skip(reason="Outside-In TDD RED state - awaiting DEVELOP wave")
    def test_valid_skip_with_blocked_by_passes_validation(
        self, tmp_project_root, minimal_step_file
    ):
        """
        GIVEN step file shows REFACTOR_L2 phase with status "SKIPPED"
        AND the phase has valid blocked_by reason: "No L2 complexity detected"
        WHEN SubagentStop hook validates the step file
        THEN validation passes (skip is legitimate)

        Business Value: Marcus confirms that legitimate skips with proper
                       justification are accepted, not flagged as errors.
                       Allows appropriate phase skipping when conditions warrant.

        Domain Example: Agent completed L1 refactoring but found no L2-level
                       complexity issues. Properly documented the reason:
                       "Code already meets L2 quality standards - no complexity,
                       responsibility, or abstraction issues."
        """
        # Arrange: Create step file with legitimately skipped phase
        step_data = _create_step_file_with_valid_skip()
        minimal_step_file.write_text(json.dumps(step_data, indent=2))

        # Act: Trigger SubagentStop hook
        # from des.hooks import SubagentStopHook
        # hook = SubagentStopHook()
        # hook_result = hook.on_agent_complete(step_file_path=str(minimal_step_file))

        # Assert: Valid skip accepted
        # assert hook_result.validation_status == "PASSED"
        # assert hook_result.invalid_skips == []
        # assert "REFACTOR_L2" not in str(hook_result.error_message or "")


# =============================================================================
# Test Data Builders (Helper Functions)
# =============================================================================


def _create_step_file_with_all_phases_executed():
    """Create step file where all 14 phases are EXECUTED with outcomes."""
    phases = [
        "PREPARE",
        "RED_ACCEPTANCE",
        "RED_UNIT",
        "GREEN_UNIT",
        "CHECK_ACCEPTANCE",
        "GREEN_ACCEPTANCE",
        "REVIEW",
        "REFACTOR_L1",
        "REFACTOR_L2",
        "REFACTOR_L3",
        "REFACTOR_L4",
        "POST_REFACTOR_REVIEW",
        "FINAL_VALIDATE",
        "COMMIT",
    ]

    return {
        "task_id": "01-01",
        "project_id": "test-project",
        "workflow_type": "tdd_cycle",
        "state": {
            "status": "DONE",
            "started_at": "2026-01-22T10:00:00Z",
            "completed_at": "2026-01-22T11:30:00Z",
        },
        "tdd_cycle": {
            "phase_execution_log": [
                {
                    "phase_number": i,
                    "phase_name": phase,
                    "status": "EXECUTED",
                    "outcome": "PASS",
                    "outcome_details": f"{phase} completed successfully",
                    "blocked_by": None,
                }
                for i, phase in enumerate(phases)
            ]
        },
    }


def _create_step_file_with_abandoned_phase(
    abandoned_phase: str, last_completed_phase: str
):
    """Create step file with an abandoned IN_PROGRESS phase (simulates crash)."""
    phases = [
        "PREPARE",
        "RED_ACCEPTANCE",
        "RED_UNIT",
        "GREEN_UNIT",
        "CHECK_ACCEPTANCE",
        "GREEN_ACCEPTANCE",
        "REVIEW",
        "REFACTOR_L1",
        "REFACTOR_L2",
        "REFACTOR_L3",
        "REFACTOR_L4",
        "POST_REFACTOR_REVIEW",
        "FINAL_VALIDATE",
        "COMMIT",
    ]

    abandoned_idx = phases.index(abandoned_phase)
    last_completed_idx = phases.index(last_completed_phase)

    phase_log = []
    for i, phase in enumerate(phases):
        if i < abandoned_idx:
            status = "EXECUTED" if i <= last_completed_idx else "NOT_EXECUTED"
            outcome = "PASS" if status == "EXECUTED" else None
        elif i == abandoned_idx:
            status = "IN_PROGRESS"  # Abandoned phase
            outcome = None
        else:
            status = "NOT_EXECUTED"
            outcome = None

        phase_log.append(
            {
                "phase_number": i,
                "phase_name": phase,
                "status": status,
                "outcome": outcome,
                "outcome_details": f"{phase} completed" if outcome else None,
                "blocked_by": None,
            }
        )

    return {
        "task_id": "01-01",
        "project_id": "test-project",
        "workflow_type": "tdd_cycle",
        "state": {
            "status": "IN_PROGRESS",
            "started_at": "2026-01-22T10:00:00Z",
            "completed_at": None,
        },
        "tdd_cycle": {"phase_execution_log": phase_log},
    }


def _create_step_file_with_silent_completion():
    """Create step file where task is IN_PROGRESS but no phases executed."""
    phases = [
        "PREPARE",
        "RED_ACCEPTANCE",
        "RED_UNIT",
        "GREEN_UNIT",
        "CHECK_ACCEPTANCE",
        "GREEN_ACCEPTANCE",
        "REVIEW",
        "REFACTOR_L1",
        "REFACTOR_L2",
        "REFACTOR_L3",
        "REFACTOR_L4",
        "POST_REFACTOR_REVIEW",
        "FINAL_VALIDATE",
        "COMMIT",
    ]

    return {
        "task_id": "01-01",
        "project_id": "test-project",
        "workflow_type": "tdd_cycle",
        "state": {
            "status": "IN_PROGRESS",
            "started_at": "2026-01-22T10:00:00Z",
            "completed_at": None,
        },
        "tdd_cycle": {
            "phase_execution_log": [
                {
                    "phase_number": i,
                    "phase_name": phase,
                    "status": "NOT_EXECUTED",
                    "outcome": None,
                    "outcome_details": None,
                    "blocked_by": None,
                }
                for i, phase in enumerate(phases)
            ]
        },
    }


def _create_step_file_with_missing_outcome(phase_name: str):
    """Create step file with EXECUTED phase missing outcome field."""
    phases = [
        "PREPARE",
        "RED_ACCEPTANCE",
        "RED_UNIT",
        "GREEN_UNIT",
        "CHECK_ACCEPTANCE",
        "GREEN_ACCEPTANCE",
        "REVIEW",
        "REFACTOR_L1",
        "REFACTOR_L2",
        "REFACTOR_L3",
        "REFACTOR_L4",
        "POST_REFACTOR_REVIEW",
        "FINAL_VALIDATE",
        "COMMIT",
    ]

    target_idx = phases.index(phase_name)

    phase_log = []
    for i, phase in enumerate(phases):
        if i <= target_idx:
            status = "EXECUTED"
            # Missing outcome for target phase
            outcome = None if phase == phase_name else "PASS"
            outcome_details = None if phase == phase_name else f"{phase} completed"
        else:
            status = "NOT_EXECUTED"
            outcome = None
            outcome_details = None

        phase_log.append(
            {
                "phase_number": i,
                "phase_name": phase,
                "status": status,
                "outcome": outcome,
                "outcome_details": outcome_details,
                "blocked_by": None,
            }
        )

    return {
        "task_id": "01-01",
        "project_id": "test-project",
        "workflow_type": "tdd_cycle",
        "state": {
            "status": "IN_PROGRESS",
            "started_at": "2026-01-22T10:00:00Z",
            "completed_at": None,
        },
        "tdd_cycle": {"phase_execution_log": phase_log},
    }


def _create_step_file_with_invalid_skip(skipped_phase: str):
    """Create step file with SKIPPED phase missing blocked_by reason."""
    phases = [
        "PREPARE",
        "RED_ACCEPTANCE",
        "RED_UNIT",
        "GREEN_UNIT",
        "CHECK_ACCEPTANCE",
        "GREEN_ACCEPTANCE",
        "REVIEW",
        "REFACTOR_L1",
        "REFACTOR_L2",
        "REFACTOR_L3",
        "REFACTOR_L4",
        "POST_REFACTOR_REVIEW",
        "FINAL_VALIDATE",
        "COMMIT",
    ]

    target_idx = phases.index(skipped_phase)

    phase_log = []
    for i, phase in enumerate(phases):
        if i < target_idx:
            status = "EXECUTED"
            outcome = "PASS"
        elif phase == skipped_phase:
            status = "SKIPPED"
            outcome = "SKIPPED"
        elif i > target_idx:
            status = "EXECUTED"
            outcome = "PASS"
        else:
            status = "EXECUTED"
            outcome = "PASS"

        phase_log.append(
            {
                "phase_number": i,
                "phase_name": phase,
                "status": status,
                "outcome": outcome,
                "outcome_details": f"{phase} completed"
                if status == "EXECUTED"
                else None,
                "blocked_by": None,  # Missing blocked_by for skipped phase!
            }
        )

    return {
        "task_id": "01-01",
        "project_id": "test-project",
        "workflow_type": "tdd_cycle",
        "state": {
            "status": "DONE",
            "started_at": "2026-01-22T10:00:00Z",
            "completed_at": "2026-01-22T11:30:00Z",
        },
        "tdd_cycle": {"phase_execution_log": phase_log},
    }


def _create_step_file_with_multiple_issues():
    """Create step file with multiple validation issues."""
    phases = [
        "PREPARE",
        "RED_ACCEPTANCE",
        "RED_UNIT",
        "GREEN_UNIT",
        "CHECK_ACCEPTANCE",
        "GREEN_ACCEPTANCE",
        "REVIEW",
        "REFACTOR_L1",
        "REFACTOR_L2",
        "REFACTOR_L3",
        "REFACTOR_L4",
        "POST_REFACTOR_REVIEW",
        "FINAL_VALIDATE",
        "COMMIT",
    ]

    phase_log = []
    for i, phase in enumerate(phases):
        if phase == "GREEN_UNIT":
            # Issue 1: Abandoned IN_PROGRESS phase
            status = "IN_PROGRESS"
            outcome = None
            outcome_details = None
        elif phase == "REVIEW":
            # Issue 2: EXECUTED but missing outcome
            status = "EXECUTED"
            outcome = None
            outcome_details = None
        elif phases.index(phase) < phases.index("GREEN_UNIT"):
            status = "EXECUTED"
            outcome = "PASS"
            outcome_details = f"{phase} completed"
        else:
            status = "NOT_EXECUTED"
            outcome = None
            outcome_details = None

        phase_log.append(
            {
                "phase_number": i,
                "phase_name": phase,
                "status": status,
                "outcome": outcome,
                "outcome_details": outcome_details,
                "blocked_by": None,
            }
        )

    return {
        "task_id": "01-01",
        "project_id": "test-project",
        "workflow_type": "tdd_cycle",
        "state": {
            "status": "IN_PROGRESS",
            "started_at": "2026-01-22T10:00:00Z",
            "completed_at": None,
        },
        "tdd_cycle": {"phase_execution_log": phase_log},
    }


def _create_step_file_with_clean_completion():
    """Create step file with all phases properly completed."""
    return _create_step_file_with_all_phases_executed()


def _create_step_file_with_valid_skip():
    """Create step file with legitimately skipped phase (has blocked_by)."""
    phases = [
        "PREPARE",
        "RED_ACCEPTANCE",
        "RED_UNIT",
        "GREEN_UNIT",
        "CHECK_ACCEPTANCE",
        "GREEN_ACCEPTANCE",
        "REVIEW",
        "REFACTOR_L1",
        "REFACTOR_L2",
        "REFACTOR_L3",
        "REFACTOR_L4",
        "POST_REFACTOR_REVIEW",
        "FINAL_VALIDATE",
        "COMMIT",
    ]

    phase_log = []
    for i, phase in enumerate(phases):
        if phase == "REFACTOR_L2":
            # Legitimately skipped with proper reason
            status = "SKIPPED"
            outcome = "SKIPPED"
            outcome_details = "No L2 complexity detected"
            blocked_by = "Code already meets L2 quality standards - no complexity, responsibility, or abstraction issues"
        else:
            status = "EXECUTED"
            outcome = "PASS"
            outcome_details = f"{phase} completed successfully"
            blocked_by = None

        phase_log.append(
            {
                "phase_number": i,
                "phase_name": phase,
                "status": status,
                "outcome": outcome,
                "outcome_details": outcome_details,
                "blocked_by": blocked_by,
            }
        )

    return {
        "task_id": "01-01",
        "project_id": "test-project",
        "workflow_type": "tdd_cycle",
        "state": {
            "status": "DONE",
            "started_at": "2026-01-22T10:00:00Z",
            "completed_at": "2026-01-22T11:30:00Z",
        },
        "tdd_cycle": {"phase_execution_log": phase_log},
    }
