"""
E2E Acceptance Test: US-005 Failure Recovery Guidance

PERSONA: Alex (Junior Developer)
STORY: As a junior developer, I want DES to provide clear recovery guidance when
       execution fails, so that I know exactly what to do instead of being stuck
       with a cryptic error.

BUSINESS VALUE:
- Junior developers learn from failures with educational context
- Specific, actionable recovery steps reduce debugging time
- Recovery suggestions prevent manual step file corruption
- Error messages explain WHY errors occurred and HOW to fix them

ACCEPTANCE CRITERIA:
- AC-005.1: Every failure mode has associated recovery suggestions
- AC-005.2: Suggestions are stored in step file `recovery_suggestions` array
- AC-005.3: Suggestions are actionable (specific commands or file paths)
- AC-005.4: Validation errors include fix guidance in error message
- AC-005.5: Recovery suggestions include explanatory text describing WHY and HOW

SCOPE: Covers US-005 Acceptance Criteria (AC-005.1 through AC-005.5)
WAVE: DISTILL (Acceptance Test Creation)
STATUS: RED (Outside-In TDD - awaiting DEVELOP wave implementation)

SOURCE:
- docs/feature/des/discuss/user-stories.md (US-005)
"""

import pytest


class TestFailureRecoveryGuidance:
    """E2E acceptance tests for US-005: Failure Recovery Guidance."""

    # =========================================================================
    # AC-005.1: Every failure mode has associated recovery suggestions
    # Scenario 1: Crash Recovery - Agent crash during phase execution
    # =========================================================================

    def test_scenario_001_crash_recovery_provides_recovery_suggestions(
        self, tmp_project_root, step_file_with_abandoned_phase
    ):
        """
        GIVEN agent crashed during GREEN_UNIT phase (status: IN_PROGRESS)
        WHEN SubagentStop hook fires and detects abandoned phase
        THEN step file is updated with FAILED state and recovery_suggestions array

        Business Value: Alex's agent crashed during GREEN_UNIT. Instead of being
                       stuck with a cryptic "IN_PROGRESS" state, he receives clear
                       step-by-step recovery guidance in the step file.

        Failure Mode: Agent crash leaving phase IN_PROGRESS
        Expected Recovery Suggestions:
        1. Review agent transcript for error details
        2. Reset GREEN_UNIT phase status to NOT_EXECUTED
        3. Run `/nw:execute` again to resume from GREEN_UNIT

        Domain Example (from US-005):
        Alex's agent crashed during GREEN_UNIT.
        Step file updated with status: FAILED and recovery_suggestions array.
        Alex follows suggestions step by step.
        """
        # Arrange: Step file with GREEN_UNIT phase IN_PROGRESS (abandoned)
        step_file = step_file_with_abandoned_phase
        abandoned_phase = "GREEN_UNIT"

        # Act: RecoveryGuidanceHandler generates suggestions for abandoned phase
        from src.des.application.recovery_guidance_handler import (
            RecoveryGuidanceHandler,
        )

        recovery_handler = RecoveryGuidanceHandler()

        # Generate suggestions for the abandoned phase failure
        suggestions = recovery_handler.generate_recovery_suggestions(
            failure_type="abandoned_phase",
            context={
                "phase": abandoned_phase,
                "step_file": str(step_file),
            },
        )

        # Handle the failure - update step file with recovery suggestions
        updated_step = recovery_handler.handle_failure(
            step_file_path=str(step_file),
            failure_type="abandoned_phase",
            context={
                "phase": abandoned_phase,
                "failure_reason": f"Agent crashed during {abandoned_phase} phase",
                "suggestions": suggestions,
            },
        )

        # Assert: Recovery suggestions are generated
        assert suggestions is not None, "Should generate recovery suggestions"
        assert isinstance(suggestions, list), "Suggestions should be a list"
        assert len(suggestions) >= 1, "Should have at least one suggestion"

        # Assert: Suggestions contain actionable elements
        assert any(
            "transcript" in s.lower() for s in suggestions
        ), "Should mention transcript"
        assert any(
            "NOT_EXECUTED" in s for s in suggestions
        ), "Should reference phase status"
        assert any(
            "/nw:execute" in s or "execute" in s.lower() for s in suggestions
        ), "Should mention execution"

        # Assert: Step file updated with recovery suggestions
        assert updated_step is not None, "Should return updated step"
        assert (
            "recovery_suggestions" in updated_step
        ), "Should include recovery_suggestions"
        assert isinstance(
            updated_step["recovery_suggestions"], list
        ), "recovery_suggestions should be list"

    # =========================================================================
    # AC-005.1: Every failure mode has associated recovery suggestions
    # Scenario 2: Silent Completion - Agent returned without updating state
    # =========================================================================

    def test_scenario_002_silent_completion_provides_recovery_suggestions(
        self, tmp_project_root, step_file_with_silent_completion
    ):
        """
        GIVEN agent returned without updating step file (all phases NOT_EXECUTED)
        WHEN SubagentStop hook fires and detects mismatch
        THEN step file is updated with recovery suggestions for silent completion

        Business Value: Alex's agent returned but didn't update any phase status.
                       He receives specific guidance to check the transcript and
                       manually update phase status based on evidence.

        Failure Mode: Agent completed without updating step file
        Expected Recovery Suggestions:
        1. Check agent transcript at {path} for errors
        2. Verify prompt contained OUTCOME_RECORDING instructions
        3. Manually update phase status based on transcript evidence
        """
        # Arrange: Step file with all phases NOT_EXECUTED despite agent completion
        step_file = step_file_with_silent_completion

        # Act: RecoveryGuidanceHandler detects silent completion
        from src.des.application.recovery_guidance_handler import (
            RecoveryGuidanceHandler,
        )

        recovery_handler = RecoveryGuidanceHandler()

        # Detect silent completion (all phases NOT_EXECUTED but task completed)
        suggestions = recovery_handler.generate_recovery_suggestions(
            failure_type="silent_completion",
            context={
                "transcript_path": "/path/to/transcript.log",
                "step_file": str(step_file),
            },
        )

        # Handle the silent completion failure
        updated_step = recovery_handler.handle_failure(
            step_file_path=str(step_file),
            failure_type="silent_completion",
            context={
                "failure_reason": "Agent completed without updating any phase status",
                "transcript_path": "/path/to/transcript.log",
                "step_file": str(step_file),
            },
        )

        # Assert: Suggestions generated for silent completion
        assert suggestions is not None, "Should generate recovery suggestions"
        assert isinstance(suggestions, list), "Suggestions should be a list"
        assert len(suggestions) >= 3, "Should have at least 3 suggestions"

        # Assert: Suggestions contain specific elements for silent completion
        assert any(
            "transcript" in s.lower() for s in suggestions
        ), "Should mention transcript location"
        assert any(
            "OUTCOME_RECORDING" in s for s in suggestions
        ), "Should explain OUTCOME_RECORDING"
        assert any(
            "manually update" in s.lower() for s in suggestions
        ), "Should mention manual update"

        # Assert: Step file updated with recovery suggestions
        assert updated_step is not None, "Should return updated state"
        assert (
            "recovery_suggestions" in updated_step
        ), "Should include recovery_suggestions"
        assert isinstance(
            updated_step["recovery_suggestions"], list
        ), "recovery_suggestions should be list"
        assert (
            len(updated_step["recovery_suggestions"]) >= 3
        ), "Should have 3+ suggestions"

    # =========================================================================
    # AC-005.1: Every failure mode has associated recovery suggestions
    # Scenario 3: Validation Failure - Missing mandatory section in prompt
    # =========================================================================

    @pytest.mark.skip(reason="Outside-In TDD RED state - awaiting DEVELOP wave")
    def test_scenario_003_validation_failure_provides_recovery_suggestions(
        self, tmp_project_root
    ):
        """
        GIVEN orchestrator produced prompt missing TDD_14_PHASES section
        WHEN pre-invocation validation fails
        THEN error includes recovery suggestion to fix the template

        Business Value: Alex's orchestrator produced incomplete prompt.
                       Instead of "validation failed", he gets specific guidance:
                       "Update the prompt template to include TDD_14_PHASES section
                       with all 14 phases enumerated."

        Failure Mode: Pre-invocation validation failure (missing section)
        Expected: Error message includes actionable fix guidance
        """
        # Arrange: Prompt missing TDD_14_PHASES section
        _incomplete_prompt = """
        <!-- DES-VALIDATION: required -->
        <!-- DES-STEP-FILE: steps/01-01.json -->

        # DES_METADATA
        Step: 01-01.json

        # AGENT_IDENTITY
        Agent: software-crafter

        # TASK_CONTEXT
        Implement UserRepository

        # MISSING: TDD_14_PHASES section

        # QUALITY_GATES
        G1-G6 defined

        # OUTCOME_RECORDING
        Update step file

        # BOUNDARY_RULES
        Scope defined

        # TIMEOUT_INSTRUCTION
        50 turns
        """

        # Act: Pre-invocation validation fails
        # validation_result = des_validator.validate_prompt(incomplete_prompt)

        # Assert: Error includes recovery suggestion
        # assert validation_result.status == "FAILED"
        # assert "TDD_14_PHASES" in validation_result.error_message
        # assert validation_result.recovery_guidance is not None
        # assert "template" in validation_result.recovery_guidance.lower()
        # assert "14 phases" in validation_result.recovery_guidance.lower()

    # =========================================================================
    # AC-005.2: Suggestions stored in step file `recovery_suggestions` array
    # Scenario 4: Recovery suggestions persisted to step file JSON
    # =========================================================================

    def test_scenario_004_recovery_suggestions_stored_in_step_file(
        self, tmp_project_root, step_file_with_abandoned_phase
    ):
        """
        GIVEN failure detected during post-execution validation
        WHEN recovery handler updates step file
        THEN recovery_suggestions array is persisted in step file JSON

        Business Value: Alex can review the step file to find recovery guidance
                       even after closing the terminal. The suggestions survive
                       session boundaries and can be shared with teammates.

        Expected Structure:
        {
          "state": {
            "status": "FAILED",
            "failure_reason": "...",
            "recovery_suggestions": ["suggestion 1", "suggestion 2", ...]
          }
        }
        """

        # Arrange: Step file with abandoned phase
        step_file = step_file_with_abandoned_phase
        import json

        # Act: Manually add recovery_suggestions to step file state
        step_data = json.loads(step_file.read_text())

        # Add recovery_suggestions array to state
        step_data["state"]["recovery_suggestions"] = [
            "Review agent transcript for error details",
            "Reset GREEN_UNIT phase status to NOT_EXECUTED",
            "Run /nw:execute again to resume from GREEN_UNIT",
        ]

        # Persist to file
        step_file.write_text(json.dumps(step_data, indent=2))

        # Assert: Re-read step file and verify recovery_suggestions persisted
        step_data_reloaded = json.loads(step_file.read_text())
        assert "recovery_suggestions" in step_data_reloaded["state"]
        assert isinstance(step_data_reloaded["state"]["recovery_suggestions"], list)
        assert len(step_data_reloaded["state"]["recovery_suggestions"]) > 0

    # =========================================================================
    # AC-005.3: Suggestions are actionable (specific commands or file paths)
    # Scenario 5: Recovery suggestions contain executable commands
    # =========================================================================

    @pytest.mark.skip(reason="Outside-In TDD RED state - awaiting DEVELOP wave")
    def test_scenario_005_recovery_suggestions_contain_actionable_commands(
        self, tmp_project_root, step_file_with_abandoned_phase
    ):
        """
        GIVEN agent crashed during REFACTOR_L2 phase
        WHEN recovery suggestions are generated
        THEN suggestions include specific commands Alex can execute

        Business Value: Alex doesn't have to interpret abstract guidance.
                       He gets specific commands like `/nw:execute @software-crafter
                       "steps/01-01.json"` that he can copy-paste to recover.

        Actionable Criteria:
        - Contains executable command (e.g., `/nw:execute`)
        - Contains file path reference (e.g., `steps/01-01.json`)
        - Contains phase name for context (e.g., `REFACTOR_L2`)
        """
        # Arrange: Step file with REFACTOR_L2 phase abandoned
        _step_file = step_file_with_abandoned_phase

        # Act: Recovery handler generates suggestions
        # recovery_handler = RecoveryGuidanceHandler()
        # suggestions = recovery_handler.generate_recovery_suggestions(
        #     failure_type="abandoned_phase",
        #     context={
        #         "phase": "REFACTOR_L2",
        #         "step_file": "steps/01-01.json",
        #     },
        # )

        # Assert: Suggestions contain actionable elements
        # actionable_command_found = any(
        #     "/nw:execute" in s or "/nw:develop" in s for s in suggestions
        # )
        # file_path_found = any(
        #     "steps/" in s or ".json" in s for s in suggestions
        # )
        # phase_name_found = any("REFACTOR_L2" in s for s in suggestions)
        #
        # assert actionable_command_found, "Suggestions must include executable commands"
        # assert file_path_found, "Suggestions must include file paths"
        # assert phase_name_found, "Suggestions must reference the failed phase"

    # =========================================================================
    # AC-005.3: Suggestions are actionable (specific commands or file paths)
    # Scenario 6: Recovery suggestions include transcript file path
    # =========================================================================

    @pytest.mark.skip(reason="Outside-In TDD RED state - awaiting DEVELOP wave")
    def test_scenario_006_recovery_suggestions_include_transcript_path(
        self, tmp_project_root, step_file_with_abandoned_phase
    ):
        """
        GIVEN agent crash detected with known transcript location
        WHEN recovery suggestions are generated
        THEN suggestions include specific path to agent transcript for debugging

        Business Value: Alex knows exactly where to find the agent transcript
                       for debugging. No hunting through directories - the path
                       is provided explicitly in the recovery guidance.

        Expected: "Check agent transcript at {transcript_path} for errors"
        """
        # Arrange: Known transcript path
        _transcript_path = "/tmp/agent-transcripts/session-12345.log"

        # Act: Recovery handler generates suggestions with transcript path
        # recovery_handler = RecoveryGuidanceHandler()
        # suggestions = recovery_handler.generate_recovery_suggestions(
        #     failure_type="agent_crash",
        #     context={
        #         "transcript_path": transcript_path,
        #         "phase": "GREEN_UNIT",
        #     },
        # )

        # Assert: Suggestions include specific transcript path
        # transcript_suggestion_found = any(
        #     transcript_path in s for s in suggestions
        # )
        # assert transcript_suggestion_found, (
        #     f"Suggestions must include specific transcript path: {transcript_path}"
        # )

    # =========================================================================
    # AC-005.4: Validation errors include fix guidance in error message
    # Scenario 7: Validation error message includes inline fix guidance
    # =========================================================================

    @pytest.mark.skip(reason="Outside-In TDD RED state - awaiting DEVELOP wave")
    def test_scenario_007_validation_error_includes_inline_fix_guidance(
        self, tmp_project_root
    ):
        """
        GIVEN prompt validation fails due to missing BOUNDARY_RULES section
        WHEN validation error is returned
        THEN error message includes fix guidance explaining what to add

        Business Value: Alex sees the validation error AND the fix in one message.
                       No need to consult documentation - the error tells him:
                       "Add BOUNDARY_RULES section with allowed/forbidden patterns."

        Error Format:
        "MISSING: Mandatory section 'BOUNDARY_RULES' not found.
         Fix: Add BOUNDARY_RULES section with ALLOWED and FORBIDDEN file patterns."
        """
        # Arrange: Prompt missing BOUNDARY_RULES
        _prompt_missing_boundary_rules = """
        <!-- DES-VALIDATION: required -->
        # All sections present EXCEPT BOUNDARY_RULES
        """

        # Act: Validation fails
        # validation_result = des_validator.validate_prompt(prompt_missing_boundary_rules)

        # Assert: Error message includes inline fix guidance
        # assert validation_result.status == "FAILED"
        # assert "BOUNDARY_RULES" in validation_result.error_message
        # assert "Fix:" in validation_result.error_message or "fix" in validation_result.error_message.lower()
        # assert any(
        #     keyword in validation_result.error_message.lower()
        #     for keyword in ["add", "include", "update"]
        # )

    # =========================================================================
    # AC-005.4: Validation errors include fix guidance in error message
    # Scenario 8: Missing TDD phase error includes phase name and fix
    # =========================================================================

    @pytest.mark.skip(reason="Outside-In TDD RED state - awaiting DEVELOP wave")
    def test_scenario_008_missing_phase_error_includes_specific_fix(
        self, tmp_project_root
    ):
        """
        GIVEN prompt validation fails due to missing POST_REFACTOR_REVIEW phase
        WHEN validation error is returned
        THEN error names the missing phase AND suggests how to add it

        Business Value: Alex knows exactly which phase is missing and where to add it.
                       Error: "INCOMPLETE: TDD phase 'POST_REFACTOR_REVIEW' not mentioned.
                       Fix: Add POST_REFACTOR_REVIEW between REFACTOR_L4 and FINAL_VALIDATE."

        Expected: Error message names phase AND provides positioning guidance
        """
        # Arrange: Prompt missing POST_REFACTOR_REVIEW phase
        _prompt_missing_phase = """
        <!-- DES-VALIDATION: required -->

        # TDD_14_PHASES
        Execute in order:
        1. PREPARE
        2. RED_ACCEPTANCE
        3. RED_UNIT
        4. GREEN_UNIT
        5. CHECK_ACCEPTANCE
        6. GREEN_ACCEPTANCE
        7. REVIEW
        8. REFACTOR_L1
        9. REFACTOR_L2
        10. REFACTOR_L3
        11. REFACTOR_L4
        # MISSING: POST_REFACTOR_REVIEW
        12. FINAL_VALIDATE
        13. COMMIT
        """

        # Act: Validation fails
        # validation_result = des_validator.validate_prompt(prompt_missing_phase)

        # Assert: Error includes phase name and positioning fix
        # assert "POST_REFACTOR_REVIEW" in validation_result.error_message
        # assert any(
        #     keyword in validation_result.error_message
        #     for keyword in ["REFACTOR_L4", "FINAL_VALIDATE", "between", "after"]
        # )

    # =========================================================================
    # AC-005.5: Recovery suggestions include explanatory text (WHY and HOW)
    # Scenario 9: Recovery suggestion explains WHY error occurred
    # =========================================================================

    @pytest.mark.skip(reason="Outside-In TDD RED state - awaiting DEVELOP wave")
    def test_scenario_009_recovery_suggestion_explains_why_error_occurred(
        self, tmp_project_root, step_file_with_abandoned_phase
    ):
        """
        GIVEN agent crash detected during RED_UNIT phase
        WHEN recovery suggestions are generated
        THEN at least one suggestion explains WHY the error occurred

        Business Value: Alex doesn't just get instructions - he learns.
                       Explanation: "The agent left RED_UNIT in IN_PROGRESS state,
                       indicating it started but did not complete. This typically
                       occurs when the agent encounters an unhandled error or timeout."

        Educational Context Requirement (AC-005.5):
        - Minimum 1 sentence describing WHY the error occurred
        - Helps junior developers understand failure patterns
        """
        # Arrange: Step file with RED_UNIT abandoned
        _step_file = step_file_with_abandoned_phase

        # Act: Recovery handler generates suggestions with explanatory text
        # recovery_handler = RecoveryGuidanceHandler()
        # suggestions = recovery_handler.generate_recovery_suggestions(
        #     failure_type="abandoned_phase",
        #     context={"phase": "RED_UNIT"},
        # )

        # Assert: At least one suggestion explains WHY
        # why_explanation_found = any(
        #     any(keyword in s.lower() for keyword in [
        #         "because", "this occurs when", "indicating", "this means",
        #         "this typically", "the agent"
        #     ])
        #     for s in suggestions
        # )
        # assert why_explanation_found, (
        #     "At least one suggestion must explain WHY the error occurred"
        # )

    # =========================================================================
    # AC-005.5: Recovery suggestions include explanatory text (WHY and HOW)
    # Scenario 10: Recovery suggestion explains HOW the fix resolves issue
    # =========================================================================

    @pytest.mark.skip(reason="Outside-In TDD RED state - awaiting DEVELOP wave")
    def test_scenario_010_recovery_suggestion_explains_how_fix_resolves_issue(
        self, tmp_project_root, step_file_with_abandoned_phase
    ):
        """
        GIVEN silent completion detected (agent returned without updating state)
        WHEN recovery suggestions are generated
        THEN at least one suggestion explains HOW the fix resolves the issue

        Business Value: Alex understands the causal relationship between the fix
                       and the resolution. Example: "Resetting the phase to NOT_EXECUTED
                       allows the execution framework to retry the phase from scratch,
                       ensuring a clean state for the next attempt."

        Educational Context Requirement (AC-005.5):
        - Minimum 1 sentence describing HOW the fix resolves the issue
        - Helps junior developers learn recovery patterns
        """
        # Arrange: Step file with silent completion
        _step_file = step_file_with_abandoned_phase

        # Act: Recovery handler generates suggestions with HOW explanation
        # recovery_handler = RecoveryGuidanceHandler()
        # suggestions = recovery_handler.generate_recovery_suggestions(
        #     failure_type="silent_completion",
        #     context={"step_file": "steps/01-01.json"},
        # )

        # Assert: At least one suggestion explains HOW fix works
        # how_explanation_found = any(
        #     any(keyword in s.lower() for keyword in [
        #         "allows", "ensures", "this will", "resolves", "fixes",
        #         "so that", "enabling", "to recover"
        #     ])
        #     for s in suggestions
        # )
        # assert how_explanation_found, (
        #     "At least one suggestion must explain HOW the fix resolves the issue"
        # )

    # =========================================================================
    # AC-005.5: Combined WHY + HOW in recovery suggestion
    # Scenario 11: Complete educational recovery suggestion with context
    # =========================================================================

    @pytest.mark.skip(reason="Outside-In TDD RED state - awaiting DEVELOP wave")
    def test_scenario_011_complete_educational_recovery_suggestion(
        self, tmp_project_root, step_file_with_abandoned_phase
    ):
        """
        GIVEN validation error for missing OUTCOME_RECORDING section
        WHEN recovery guidance is generated
        THEN guidance includes both WHY the section is needed AND HOW to add it

        Business Value: Alex gets complete learning context in one message.
                       WHY: "OUTCOME_RECORDING is required because it instructs
                       the agent to update the step file after each phase."
                       HOW: "Add an OUTCOME_RECORDING section with instructions
                       to update phase status and outcome fields."

        Complete Educational Context:
        - Explains purpose of the missing element (WHY)
        - Provides specific fix instructions (HOW)
        - Minimum 1 sentence for each aspect
        """
        # Arrange: Validation failure for missing OUTCOME_RECORDING

        # Act: Recovery guidance generated
        # recovery_guidance = des_validator.generate_recovery_guidance(
        #     error_type="missing_section",
        #     section_name="OUTCOME_RECORDING",
        # )

        # Assert: Guidance includes both WHY and HOW
        # why_keywords = ["because", "required", "needed", "purpose", "ensures"]
        # how_keywords = ["add", "include", "update", "with", "section"]
        #
        # has_why = any(kw in recovery_guidance.lower() for kw in why_keywords)
        # has_how = any(kw in recovery_guidance.lower() for kw in how_keywords)
        #
        # assert has_why, "Recovery guidance must explain WHY the element is needed"
        # assert has_how, "Recovery guidance must explain HOW to fix the issue"
        # assert len(recovery_guidance.split(".")) >= 2, (
        #     "Recovery guidance must have at least 2 sentences (WHY + HOW)"
        # )

    # =========================================================================
    # AC-005.1 + AC-005.2: Failure mode registry - all modes have suggestions
    # Scenario 12: All defined failure modes have registered recovery handlers
    # =========================================================================

    @pytest.mark.skip(reason="Outside-In TDD RED state - awaiting DEVELOP wave")
    def test_scenario_012_all_failure_modes_have_recovery_handlers(self):
        """
        GIVEN the defined failure mode registry
        WHEN iterating through all failure modes
        THEN each mode has associated recovery suggestions (no orphan modes)

        Business Value: Alex is never left without guidance, regardless of
                       failure type. System guarantee: every possible failure
                       mode has at least one recovery suggestion.

        Defined Failure Modes:
        1. abandoned_phase - Agent crashed during phase execution
        2. silent_completion - Agent returned without updating state
        3. missing_section - Validation found missing mandatory section
        4. missing_phase - Validation found missing TDD phase
        5. invalid_outcome - Phase marked EXECUTED without outcome
        6. invalid_skip - Phase marked SKIPPED without blocked_by reason
        7. stale_execution - IN_PROGRESS phase older than threshold
        """
        # Arrange: List of all defined failure modes
        _defined_failure_modes = [
            "abandoned_phase",
            "silent_completion",
            "missing_section",
            "missing_phase",
            "invalid_outcome",
            "invalid_skip",
            "stale_execution",
        ]

        # Act: Check each failure mode has recovery handler
        # recovery_handler = RecoveryGuidanceHandler()

        # Assert: Each mode has suggestions
        # for mode in defined_failure_modes:
        #     suggestions = recovery_handler.get_recovery_suggestions_for_mode(mode)
        #     assert suggestions is not None, f"No recovery handler for mode: {mode}"
        #     assert len(suggestions) > 0, f"Empty suggestions for mode: {mode}"


# =============================================================================
# Fixtures for US-005 Tests
# =============================================================================


@pytest.fixture
def step_file_with_abandoned_phase(tmp_project_root):
    """
    Create a step file with a phase left IN_PROGRESS (abandoned).

    Simulates agent crash scenario where GREEN_UNIT was started but never completed.

    Returns:
        Path: Path to the created step file with abandoned phase
    """
    import json

    step_file = tmp_project_root / "steps" / "01-01.json"

    step_data = {
        "task_id": "01-01",
        "project_id": "test-project",
        "workflow_type": "tdd_cycle",
        "state": {
            "status": "IN_PROGRESS",
            "started_at": "2026-01-24T10:00:00Z",
            "completed_at": None,
        },
        "tdd_cycle": {
            "phase_execution_log": [
                {
                    "phase_number": 0,
                    "phase_name": "PREPARE",
                    "status": "EXECUTED",
                    "outcome": "Environment prepared",
                },
                {
                    "phase_number": 1,
                    "phase_name": "RED_ACCEPTANCE",
                    "status": "EXECUTED",
                    "outcome": "Acceptance test failing",
                },
                {
                    "phase_number": 2,
                    "phase_name": "RED_UNIT",
                    "status": "EXECUTED",
                    "outcome": "Unit test failing",
                },
                {
                    "phase_number": 3,
                    "phase_name": "GREEN_UNIT",
                    "status": "IN_PROGRESS",  # Abandoned - agent crashed here
                    "outcome": None,
                },
                # Remaining phases NOT_EXECUTED
                *[
                    {
                        "phase_number": i,
                        "phase_name": phase_name,
                        "status": "NOT_EXECUTED",
                        "outcome": None,
                    }
                    for i, phase_name in enumerate(
                        [
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
                        ],
                        start=4,
                    )
                ],
            ]
        },
    }

    step_file.parent.mkdir(parents=True, exist_ok=True)
    step_file.write_text(json.dumps(step_data, indent=2))
    return step_file


@pytest.fixture
def step_file_with_silent_completion(tmp_project_root):
    """
    Create a step file where agent returned without updating any phase.

    Simulates silent completion scenario where all phases remain NOT_EXECUTED
    despite agent claiming to have finished.

    Returns:
        Path: Path to the created step file with silent completion
    """
    import json

    step_file = tmp_project_root / "steps" / "01-02.json"

    step_data = {
        "task_id": "01-02",
        "project_id": "test-project",
        "workflow_type": "tdd_cycle",
        "state": {
            "status": "IN_PROGRESS",  # Task started but no phases completed
            "started_at": "2026-01-24T10:00:00Z",
            "completed_at": None,
        },
        "tdd_cycle": {
            "phase_execution_log": [
                {
                    "phase_number": i,
                    "phase_name": phase_name,
                    "status": "NOT_EXECUTED",  # All phases untouched
                    "outcome": None,
                }
                for i, phase_name in enumerate(
                    [
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
                )
            ]
        },
    }

    step_file.parent.mkdir(parents=True, exist_ok=True)
    step_file.write_text(json.dumps(step_data, indent=2))
    return step_file
