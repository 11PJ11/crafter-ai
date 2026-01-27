"""
E2E Acceptance Test: US-002 Pre-Invocation Template Validation

PERSONA: Priya (Tech Lead)
STORY: As a tech lead, I want DES to block Task invocation if mandatory sections
       are missing from the prompt, so that sub-agents always receive complete
       instructions and cannot claim ignorance.

BUSINESS VALUE:
- Prevents blame-shifting ("the agent didn't know about X")
- Ensures methodology compliance before execution starts
- Provides specific, actionable error messages
- Validates completeness in < 500ms (non-blocking)

SCOPE: Covers US-002 Acceptance Criteria (AC-002.1 through AC-002.5)
WAVE: DISTILL (Acceptance Test Creation)
STATUS: RED (Outside-In TDD - awaiting DEVELOP wave implementation)
"""


class TestPreInvocationTemplateValidation:
    """E2E acceptance tests for US-002: Pre-invocation template validation."""

    # =========================================================================
    # AC-002.1: All 8 mandatory sections must be present for validation to pass
    # Scenario 4: Complete prompt passes validation
    # =========================================================================

    def test_complete_prompt_passes_all_validation_checks(self):
        """
        GIVEN orchestrator generates prompt for step with all 8 mandatory sections
        WHEN pre-invocation validation runs
        THEN validation status is PASSED and Task invocation proceeds

        Business Value: Priya verifies that correctly formed prompts are not
                       blocked, ensuring smooth workflow for compliant templates.

        Mandatory Sections Verified:
        1. DES_METADATA
        2. AGENT_IDENTITY
        3. TASK_CONTEXT
        4. TDD_14_PHASES
        5. QUALITY_GATES
        6. OUTCOME_RECORDING
        7. BOUNDARY_RULES
        8. TIMEOUT_INSTRUCTION
        """
        import time
        from src.des.application.validator import TemplateValidator

        # Arrange: Create prompt with all 8 mandatory sections
        prompt_with_all_sections = """
        <!-- DES-VALIDATION: required -->
        <!-- DES-STEP-FILE: steps/01-01.json -->

        # DES_METADATA
        Step: 01-01.json
        Command: /nw:execute

        # AGENT_IDENTITY
        Agent: software-crafter

        # TASK_CONTEXT
        Implement UserRepository

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
        12. POST_REFACTOR_REVIEW
        13. FINAL_VALIDATE
        14. COMMIT

        # QUALITY_GATES
        G1: Exactly one test active
        G2: Test fails for business logic
        G3: Test fails on assertion
        G5: Business language used
        G6: All tests green

        # OUTCOME_RECORDING
        Update step file after each phase

        # BOUNDARY_RULES
        Modify only: **/UserRepository*, **/test_user*

        # TIMEOUT_INSTRUCTION
        Target: 50 turns. Exit early if stuck.
        """

        # Act: Run pre-invocation validation
        start_time = time.perf_counter()
        validator = TemplateValidator()
        validation_result = validator.validate_prompt(prompt_with_all_sections)
        duration_ms = (time.perf_counter() - start_time) * 1000

        # Assert: Validation passes, Task invocation proceeds
        assert validation_result.status == "PASSED"
        assert validation_result.errors == []
        assert validation_result.task_invocation_allowed is True
        assert duration_ms < 500  # AC-002.5

    # =========================================================================
    # AC-002.2: All 14 TDD phases must be explicitly mentioned
    # Scenario 5: Missing TDD phase blocks Task invocation
    # =========================================================================

    def test_missing_tdd_phase_blocks_task_invocation(self):
        """
        GIVEN orchestrator generates prompt missing REFACTOR_L3 phase
        WHEN pre-invocation validation runs
        THEN validation FAILS with specific error naming missing phase

        Business Value: Priya ensures all 14 TDD phases are communicated to
                       sub-agents, preventing "I didn't know about L3 refactoring"
                       excuses during PR review.

        Missing Phase: REFACTOR_L3 (one of 14 mandatory phases)
        """
        # Arrange: Create prompt missing REFACTOR_L3 phase
        prompt_missing_phase = """
        <!-- DES-VALIDATION: required -->

        # DES_METADATA
        Step: 01-02.json

        # AGENT_IDENTITY
        Agent: software-crafter

        # TASK_CONTEXT
        Implement OrderService

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
        # MISSING: REFACTOR_L3
        10. REFACTOR_L4
        11. POST_REFACTOR_REVIEW
        12. FINAL_VALIDATE
        13. COMMIT

        # QUALITY_GATES
        G1-G6 defined

        # OUTCOME_RECORDING
        Update step file

        # BOUNDARY_RULES
        Scope defined

        # TIMEOUT_INSTRUCTION
        50 turns
        """

        # Act: Run pre-invocation validation
        from src.des.application.validator import TemplateValidator

        validator = TemplateValidator()
        validation_result = validator.validate_prompt(prompt_missing_phase)

        # Assert: Validation fails with specific error
        assert validation_result.status == "FAILED"
        assert (
            "INCOMPLETE: TDD phase 'REFACTOR_L3' not mentioned"
            in validation_result.errors
        )
        assert validation_result.task_invocation_allowed is False

    # =========================================================================
    # AC-002.3: Validation errors are specific and actionable
    # Scenario 6: Missing mandatory section blocks Task invocation
    # =========================================================================

    def test_missing_mandatory_section_provides_actionable_error(self):
        """
        GIVEN orchestrator generates prompt without TIMEOUT_INSTRUCTION section
        WHEN pre-invocation validation runs
        THEN validation FAILS with error naming missing section AND recovery guidance

        Business Value: Priya receives specific, actionable errors that enable
                       quick template fixes without guesswork.

        Missing Section: TIMEOUT_INSTRUCTION (1 of 8 mandatory)
        Expected Error: "MISSING: Mandatory section 'TIMEOUT_INSTRUCTION' not found"
        Expected Guidance: "Add TIMEOUT_INSTRUCTION section with turn budget guidance"
        """
        # Arrange: Create prompt missing TIMEOUT_INSTRUCTION
        prompt_missing_section = """
        <!-- DES-VALIDATION: required -->

        # DES_METADATA
        Step: 01-03.json

        # AGENT_IDENTITY
        Agent: software-crafter

        # TASK_CONTEXT
        Implement PaymentService

        # TDD_14_PHASES
        All 14 phases listed (PREPARE through COMMIT)

        # QUALITY_GATES
        G1-G6 defined

        # OUTCOME_RECORDING
        Update step file

        # BOUNDARY_RULES
        Scope defined

        # MISSING: TIMEOUT_INSTRUCTION
        """

        # Act: Run pre-invocation validation
        from src.des.application.validator import TemplateValidator

        validator = TemplateValidator()
        validation_result = validator.validate_prompt(prompt_missing_section)

        # Assert: Validation fails with specific, actionable error
        assert validation_result.status == "FAILED"
        assert (
            "MISSING: Mandatory section 'TIMEOUT_INSTRUCTION' not found"
            in validation_result.errors
        )
        assert validation_result.task_invocation_allowed is False
        assert (
            "Add TIMEOUT_INSTRUCTION section with turn budget guidance"
            in validation_result.recovery_guidance
        )

    # =========================================================================
    # AC-002.4: Task tool is NOT invoked if validation fails
    # Scenario 7: Multiple validation errors reported together
    # =========================================================================

    def test_multiple_validation_errors_reported_together(self):
        """
        GIVEN orchestrator generates prompt with 3 issues (missing section + 2 missing phases)
        WHEN pre-invocation validation runs
        THEN validation FAILS with all 3 errors listed AND Task NOT invoked

        Business Value: Priya sees ALL validation failures in one pass, enabling
                       complete fix without multiple trial-and-error cycles.

        Issues:
        1. Missing BOUNDARY_RULES section
        2. Missing GREEN_ACCEPTANCE phase
        3. Missing POST_REFACTOR_REVIEW phase

        Expected: All 3 errors returned together, Task invocation blocked
        """
        # Arrange: Create prompt with multiple issues
        _prompt_with_multiple_errors = """
        <!-- DES-VALIDATION: required -->

        # DES_METADATA
        Step: 01-04.json

        # AGENT_IDENTITY
        Agent: software-crafter

        # TASK_CONTEXT
        Implement InventoryService

        # TDD_14_PHASES
        Execute in order:
        1. PREPARE
        2. RED_ACCEPTANCE
        3. RED_UNIT
        4. GREEN_UNIT
        5. CHECK_ACCEPTANCE
        # MISSING: GREEN_ACCEPTANCE
        6. REVIEW
        7. REFACTOR_L1
        8. REFACTOR_L2
        9. REFACTOR_L3
        10. REFACTOR_L4
        # MISSING: POST_REFACTOR_REVIEW
        11. FINAL_VALIDATE
        12. COMMIT

        # QUALITY_GATES
        G1-G6 defined

        # OUTCOME_RECORDING
        Update step file

        # MISSING: BOUNDARY_RULES section entirely

        # TIMEOUT_INSTRUCTION
        50 turns
        """

        # Act: Run pre-invocation validation
        from src.des.application.validator import TemplateValidator

        validator = TemplateValidator()
        validation_result = validator.validate_prompt(_prompt_with_multiple_errors)

        # Assert: All 3 errors reported together, Task NOT invoked
        assert validation_result.status == "FAILED"
        assert len(validation_result.errors) == 3
        assert (
            "MISSING: Mandatory section 'BOUNDARY_RULES' not found"
            in validation_result.errors
        )
        assert (
            "INCOMPLETE: TDD phase 'GREEN_ACCEPTANCE' not mentioned"
            in validation_result.errors
        )
        assert (
            "INCOMPLETE: TDD phase 'POST_REFACTOR_REVIEW' not mentioned"
            in validation_result.errors
        )
        assert validation_result.task_invocation_allowed is False

    # =========================================================================
    # AC-002.5: Validation completes in < 500ms
    # Scenario 4 (Performance Aspect): Fast validation for smooth workflow
    # =========================================================================

    def test_validation_completes_within_performance_budget(self):
        """
        GIVEN complete prompt with all 8 sections and 14 phases
        WHEN pre-invocation validation runs
        THEN validation completes in less than 500 milliseconds

        Business Value: Priya ensures validation does not create noticeable
                       workflow delays, maintaining developer productivity.

        Performance Requirement: < 500ms validation time (AC-002.5)
        """
        # Arrange: Create complete, valid prompt
        _complete_prompt = """
        <!-- DES-VALIDATION: required -->
        <!-- DES-STEP-FILE: steps/01-05.json -->

        # DES_METADATA
        Step: 01-05.json, Command: /nw:execute

        # AGENT_IDENTITY
        Agent: software-crafter

        # TASK_CONTEXT
        Implement ShippingService with carrier integration

        # TDD_14_PHASES
        Execute all 14 phases in order:
        PREPARE, RED_ACCEPTANCE, RED_UNIT, GREEN_UNIT, CHECK_ACCEPTANCE,
        GREEN_ACCEPTANCE, REVIEW, REFACTOR_L1, REFACTOR_L2, REFACTOR_L3,
        REFACTOR_L4, POST_REFACTOR_REVIEW, FINAL_VALIDATE, COMMIT

        # QUALITY_GATES
        G1: One test active
        G2: Test fails for business logic
        G3: Test fails on assertion
        G5: Business language
        G6: All tests green

        # OUTCOME_RECORDING
        Update step file phase_execution_log after each phase completion

        # BOUNDARY_RULES
        Allowed: **/ShippingService*, **/test_shipping*
        Forbidden: Other files, other steps

        # TIMEOUT_INSTRUCTION
        Target: 50 turns. Checkpoints: 10, 25, 40. Exit early if stuck.
        """

        # Act: Measure validation performance
        import time
        from src.des.application.validator import TemplateValidator

        validator = TemplateValidator()
        start_time = time.perf_counter()
        validation_result = validator.validate_prompt(_complete_prompt)
        duration_ms = (time.perf_counter() - start_time) * 1000

        # Assert: Validation passes AND completes quickly
        assert validation_result.status == "PASSED"
        assert (
            duration_ms < 500
        ), f"Validation took {duration_ms}ms, exceeds 500ms budget"
        assert validation_result.task_invocation_allowed is True

    # =========================================================================
    # Additional Edge Case: Malformed DES marker validation
    # Ensures robust validation even with corrupted metadata
    # =========================================================================

    def test_malformed_des_marker_detected_and_rejected(self):
        """
        GIVEN prompt contains malformed DES marker (invalid format)
        WHEN pre-invocation validation runs
        THEN validation FAILS with INVALID_MARKER error

        Business Value: Priya ensures even corrupted prompts are caught before
                       execution, preventing mysterious agent failures.

        Malformed Marker: <!-- DES-VALIDATION: unknown --> (invalid value)
        Expected: Validation rejection with clear error
        """
        # Arrange: Create prompt with malformed DES marker
        prompt_malformed_marker = """
        <!-- DES-VALIDATION: unknown -->
        <!-- DES-STEP-FILE: steps/01-06.json -->

        # DES_METADATA
        Step: 01-06.json

        # AGENT_IDENTITY
        Agent: software-crafter

        # TASK_CONTEXT
        Test malformed marker handling

        # TDD_14_PHASES
        PREPARE, RED_ACCEPTANCE, RED_UNIT, GREEN_UNIT, CHECK_ACCEPTANCE, GREEN_ACCEPTANCE,
        REVIEW, REFACTOR_L1, REFACTOR_L2, REFACTOR_L3, REFACTOR_L4, POST_REFACTOR_REVIEW, FINAL_VALIDATE, COMMIT

        # QUALITY_GATES
        G1-G6

        # OUTCOME_RECORDING
        Update step file

        # BOUNDARY_RULES
        Minimal scope

        # TIMEOUT_INSTRUCTION
        50 turns
        """

        # Act: Run pre-invocation validation
        from src.des.application.validator import TemplateValidator

        validator = TemplateValidator()
        validation_result = validator.validate_prompt(prompt_malformed_marker)

        # Assert: Validation fails with invalid marker error
        assert validation_result.status == "FAILED"
        assert any("INVALID_MARKER" in error for error in validation_result.errors)
        assert validation_result.task_invocation_allowed is False


# =============================================================================
# WIRING TESTS: Validation through DESOrchestrator Entry Point (CM-A/CM-D)
# =============================================================================
# These tests invoke validation through the system entry point (DESOrchestrator)
# instead of directly instantiating TemplateValidator. This ensures the
# integration is wired correctly and prevents "Testing Theatre" where tests
# pass but the feature is not actually connected to the system.
# =============================================================================


class TestOrchestratorIntegration:
    """
    Integration tests that verify TemplateValidator is wired into DESOrchestrator.

    These tests exercise the ENTRY POINT (DESOrchestrator) rather than the
    internal component (TemplateValidator) directly. This is the 10% E2E test
    that proves the wiring works (per CM-D 90/10 rule).
    """

    def test_orchestrator_validates_prompt_via_entry_point(
        self, in_memory_filesystem, mocked_hook, mocked_time_provider
    ):
        """
        GIVEN a complete prompt with all mandatory sections
        WHEN validation is invoked through DESOrchestrator entry point
        THEN validation passes and task_invocation_allowed is True

        WIRING TEST: Proves TemplateValidator is integrated into orchestrator.
        This test would FAIL if the import or delegation is missing.
        """
        # Arrange: Create orchestrator with REAL validator for integration testing
        from src.des.application.orchestrator import DESOrchestrator
        from src.des.application.validator import TemplateValidator

        orchestrator = DESOrchestrator(
            hook=mocked_hook,
            validator=TemplateValidator(),  # Real validator for integration test
            filesystem=in_memory_filesystem,
            time_provider=mocked_time_provider,
        )

        complete_prompt = """
        <!-- DES-VALIDATION: required -->
        <!-- DES-STEP-FILE: steps/01-01.json -->

        # DES_METADATA
        Step: 01-01.json

        # AGENT_IDENTITY
        Agent: software-crafter

        # TASK_CONTEXT
        Implement feature

        # TDD_14_PHASES
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
        12. POST_REFACTOR_REVIEW
        13. FINAL_VALIDATE
        14. COMMIT

        # QUALITY_GATES
        G1-G6

        # OUTCOME_RECORDING
        Update step file

        # BOUNDARY_RULES
        Modify only allowed files

        # TIMEOUT_INSTRUCTION
        50 turns
        """

        # Act: Invoke validation through ENTRY POINT
        result = orchestrator.validate_prompt(complete_prompt)

        # Assert: Validation passes through wired validator
        assert result.status == "PASSED"
        assert result.task_invocation_allowed is True
        assert result.errors == []

    def test_orchestrator_blocks_invalid_prompt_via_entry_point(
        self, in_memory_filesystem, mocked_hook, mocked_time_provider
    ):
        """
        GIVEN a prompt missing mandatory sections
        WHEN validation is invoked through DESOrchestrator entry point
        THEN validation fails and task_invocation_allowed is False

        WIRING TEST: Proves validation logic is actually being executed
        through the orchestrator, not just returning success by default.
        """
        # Arrange: Create orchestrator with REAL validator for integration testing
        from src.des.application.orchestrator import DESOrchestrator
        from src.des.application.validator import TemplateValidator

        orchestrator = DESOrchestrator(
            hook=mocked_hook,
            validator=TemplateValidator(),  # Real validator for integration test
            filesystem=in_memory_filesystem,
            time_provider=mocked_time_provider,
        )

        # Prompt missing most mandatory sections
        incomplete_prompt = """
        <!-- DES-VALIDATION: required -->
        Some incomplete prompt without mandatory sections.
        """

        # Act: Invoke validation through ENTRY POINT
        result = orchestrator.validate_prompt(incomplete_prompt)

        # Assert: Validation fails (proves validator is actually called)
        assert result.status == "FAILED"
        assert result.task_invocation_allowed is False
        assert len(result.errors) > 0
        assert any("MISSING" in error for error in result.errors)


# =============================================================================
# PHASE EXECUTION LOG VALIDATION TESTS (Steps 01-02 through 01-08)
# =============================================================================
# These tests validate the execution log structure itself, ensuring that
# task orchestration and phase tracking are correct before Task invocation.
# =============================================================================


class TestPhaseExecutionLogValidation:
    """
    Tests for validating phase_execution_log structure within prompts.
    Ensures tasks don't enter incomplete or corrupted states.
    """

    def test_abandoned_in_progress_phase_detected(self):
        """
        GIVEN a prompt with phase_execution_log containing a phase in IN_PROGRESS state
        WHEN pre-invocation validation runs
        THEN validation FAILS and names the abandoned phase

        Business Value: Prevents task invocation when a previous execution abandoned
        a phase mid-execution, ensuring tasks always start from consistent state.
        """
        prompt_with_abandoned_phase = """
        <!-- DES-VALIDATION: required -->

        # DES_METADATA
        Step: 01-02.json

        # AGENT_IDENTITY
        Agent: software-crafter

        # TASK_CONTEXT
        Continue interrupted implementation

        # TDD_14_PHASES
        PREPARE, RED_ACCEPTANCE, RED_UNIT, GREEN_UNIT, CHECK_ACCEPTANCE, GREEN_ACCEPTANCE,
        REVIEW, REFACTOR_L1, REFACTOR_L2, REFACTOR_L3, REFACTOR_L4, POST_REFACTOR_REVIEW, FINAL_VALIDATE, COMMIT

        # QUALITY_GATES
        G1-G6

        # OUTCOME_RECORDING
        Update step file with execution log

        # BOUNDARY_RULES
        Modify only current task files

        # TIMEOUT_INSTRUCTION
        50 turns

        # EXECUTION_LOG_STATUS
        Phase REFACTOR_L2 status: IN_PROGRESS (ABANDONED - never completed or rolled back)
        """

        from src.des.application.validator import TemplateValidator

        validator = TemplateValidator()
        validation_result = validator.validate_prompt(prompt_with_abandoned_phase)

        assert validation_result.status == "FAILED"
        assert any("IN_PROGRESS" in error for error in validation_result.errors)
        assert validation_result.task_invocation_allowed is False
        assert any("REFACTOR_L2" in error for error in validation_result.errors)

    def test_done_task_with_not_executed_phases_flagged(self):
        """
        GIVEN a prompt with status='DONE' but phase_execution_log shows non-executed phases
        WHEN pre-invocation validation runs
        THEN validation FAILS - marks this as inconsistent completion

        Business Value: Detects corrupted task state where task appears finished
        but some phases were never executed or recorded.
        """
        prompt_done_incomplete = """
        <!-- DES-VALIDATION: required -->

        # DES_METADATA
        Step: 01-03.json
        Status: DONE

        # AGENT_IDENTITY
        Agent: software-crafter

        # TASK_CONTEXT
        Supposed to be finished

        # TDD_14_PHASES
        All 14 phases listed

        # QUALITY_GATES
        G1-G6

        # OUTCOME_RECORDING
        Update step file

        # BOUNDARY_RULES
        Scope defined

        # TIMEOUT_INSTRUCTION
        50 turns

        # EXECUTION_LOG_STATUS
        EXECUTED: PREPARE, RED_ACCEPTANCE, RED_UNIT, GREEN_UNIT, CHECK_ACCEPTANCE
        NOT_EXECUTED: GREEN_ACCEPTANCE, REVIEW, REFACTOR_L1-L4, POST_REFACTOR_REVIEW, FINAL_VALIDATE, COMMIT
        Task Status: DONE (but 9 phases not executed!)
        """

        from src.des.application.validator import TemplateValidator

        validator = TemplateValidator()
        validation_result = validator.validate_prompt(prompt_done_incomplete)

        assert validation_result.status == "FAILED"
        assert any(
            "INCOMPLETE" in error or "NOT_EXECUTED" in error
            for error in validation_result.errors
        )
        assert validation_result.task_invocation_allowed is False

    def test_executed_phase_without_outcome_flagged(self):
        """
        GIVEN a phase marked as EXECUTED but has no outcome (outcome=null)
        WHEN pre-invocation validation runs
        THEN validation FAILS - cannot continue without knowing if phase passed/failed

        Business Value: Prevents resumption from unclear state where phase ran
        but outcome was never recorded.
        """
        prompt_missing_outcome = """
        <!-- DES-VALIDATION: required -->

        # DES_METADATA
        Step: 01-04.json

        # AGENT_IDENTITY
        Agent: software-crafter

        # TASK_CONTEXT
        Resume from unclear phase state

        # TDD_14_PHASES
        All 14 phases

        # QUALITY_GATES
        G1-G6

        # OUTCOME_RECORDING
        Update step file

        # BOUNDARY_RULES
        Scope

        # TIMEOUT_INSTRUCTION
        50 turns

        # EXECUTION_LOG_ISSUE
        Phase RED_UNIT: status=EXECUTED, outcome=null (MISSING!)
        Cannot determine if phase passed or failed
        """

        from src.des.application.validator import TemplateValidator

        validator = TemplateValidator()
        validation_result = validator.validate_prompt(prompt_missing_outcome)

        assert validation_result.status == "FAILED"
        assert any("outcome" in error.lower() for error in validation_result.errors)
        assert validation_result.task_invocation_allowed is False

    def test_skipped_phase_without_blocked_by_reason_flagged(self):
        """
        GIVEN a phase marked as SKIPPED but has no blocked_by reason
        WHEN pre-invocation validation runs
        THEN validation FAILS - skipped phases must document why

        Business Value: Prevents silent skipping where phases are bypassed
        without documenting the reason or blocking dependency.
        """
        prompt_skipped_no_reason = """
        <!-- DES-VALIDATION: required -->

        # DES_METADATA
        Step: 01-05.json

        # AGENT_IDENTITY
        Agent: software-crafter

        # TASK_CONTEXT
        Resume with skipped phase

        # TDD_14_PHASES
        All 14

        # QUALITY_GATES
        G1-G6

        # OUTCOME_RECORDING
        Track phases

        # BOUNDARY_RULES
        Defined

        # TIMEOUT_INSTRUCTION
        50 turns

        # EXECUTION_LOG_PROBLEM
        Phase CHECK_ACCEPTANCE: status=SKIPPED, blocked_by=null (INVALID)
        Skipped phases MUST have blocked_by reason documented
        """

        from src.des.application.validator import TemplateValidator

        validator = TemplateValidator()
        validation_result = validator.validate_prompt(prompt_skipped_no_reason)

        assert validation_result.status == "FAILED"
        assert any(
            "SKIPPED" in error and "blocked_by" in error
            for error in validation_result.errors
        )
        assert validation_result.task_invocation_allowed is False

    def test_validation_errors_trigger_failed_state_with_recovery(self):
        """
        GIVEN multiple validation errors in execution log and template
        WHEN pre-invocation validation runs
        THEN validation returns FAILED status with recovery guidance for each error

        Business Value: Priya receives comprehensive error report with recovery steps
        for fixing multiple issues in one pass.
        """
        prompt_multiple_errors = """
        <!-- DES-VALIDATION: required -->

        # DES_METADATA
        Step: 01-06.json

        # AGENT_IDENTITY
        Agent: software-crafter

        # TASK_CONTEXT
        Multiple issues to fix

        # TDD_14_PHASES
        PREPARE, RED_ACCEPTANCE, RED_UNIT, GREEN_UNIT, CHECK_ACCEPTANCE
        (MISSING: GREEN_ACCEPTANCE through COMMIT)

        # QUALITY_GATES
        G1-G6

        # OUTCOME_RECORDING
        Update

        # BOUNDARY_RULES
        (MISSING SECTION)

        # TIMEOUT_INSTRUCTION
        50 turns

        # EXECUTION_LOG_ERRORS
        Phase RED_UNIT: status=EXECUTED, outcome=null
        Phase REFACTOR_L1: status=IN_PROGRESS (abandoned)
        """

        from src.des.application.validator import TemplateValidator

        validator = TemplateValidator()
        validation_result = validator.validate_prompt(prompt_multiple_errors)

        assert validation_result.status == "FAILED"
        assert len(validation_result.errors) > 2
        assert validation_result.task_invocation_allowed is False
        assert hasattr(validation_result, "recovery_guidance")
        assert len(validation_result.recovery_guidance) > 0

    def test_clean_completion_passes_validation(self):
        """
        GIVEN a prompt with all phases EXECUTED and outcomes recorded
        WHEN pre-invocation validation runs
        THEN validation PASSES - task can be marked as truly complete

        Business Value: Validates that completed tasks meet all execution criteria
        before marking as DONE.
        """
        prompt_complete = """
        <!-- DES-VALIDATION: required -->

        # DES_METADATA
        Step: 01-07.json
        Status: PENDING_FINAL_REVIEW

        # AGENT_IDENTITY
        Agent: software-crafter

        # TASK_CONTEXT
        Complete feature with all phases executed

        # TDD_14_PHASES
        1. PREPARE 2. RED_ACCEPTANCE 3. RED_UNIT 4. GREEN_UNIT
        5. CHECK_ACCEPTANCE 6. GREEN_ACCEPTANCE 7. REVIEW
        8. REFACTOR_L1 9. REFACTOR_L2 10. REFACTOR_L3 11. REFACTOR_L4
        12. POST_REFACTOR_REVIEW 13. FINAL_VALIDATE 14. COMMIT

        # QUALITY_GATES
        G1-G6 all satisfied

        # OUTCOME_RECORDING
        All phases logged with outcomes

        # BOUNDARY_RULES
        Scope: UserService, tests related

        # TIMEOUT_INSTRUCTION
        50 turns

        # EXECUTION_LOG_COMPLETE
        All 14 phases: status=EXECUTED, outcome=PASS
        No IN_PROGRESS phases
        No missing outcomes
        Ready for completion
        """

        from src.des.application.validator import TemplateValidator

        validator = TemplateValidator()
        validation_result = validator.validate_prompt(prompt_complete)

        assert validation_result.status == "PASSED"
        assert validation_result.task_invocation_allowed is True
        assert len(validation_result.errors) == 0

    def test_valid_skip_with_blocked_by_passes_validation(self):
        """
        GIVEN a prompt with a SKIPPED phase that has proper blocked_by reason
        WHEN pre-invocation validation runs
        THEN validation PASSES - legitimate skips with reasons are accepted

        Business Value: Allows tasks to skip phases for valid reasons while
        maintaining full transparency about why.
        """
        prompt_valid_skip = """
        <!-- DES-VALIDATION: required -->

        # DES_METADATA
        Step: 01-07.json

        # AGENT_IDENTITY
        Agent: software-crafter

        # TASK_CONTEXT
        Implementation with justified skip

        # TDD_14_PHASES
        All 14 phases listed

        # QUALITY_GATES
        G1-G6

        # OUTCOME_RECORDING
        Update phases

        # BOUNDARY_RULES
        Defined

        # TIMEOUT_INSTRUCTION
        50 turns

        # EXECUTION_LOG_WITH_SKIP
        Phases 1-6: EXECUTED, outcome=PASS
        Phase 7 REVIEW: SKIPPED, blocked_by='Refactoring deferred to L5 pattern application'
        Phases 8-14: EXECUTED, outcome=PASS
        Explanation: REVIEW phase skipped because code already meets SRP - pattern extraction deferred
        """

        from src.des.application.validator import TemplateValidator

        validator = TemplateValidator()
        validation_result = validator.validate_prompt(prompt_valid_skip)

        assert validation_result.status == "PASSED"
        assert validation_result.task_invocation_allowed is True
        assert len(validation_result.errors) == 0


class TestOrchestratorSubagentStopHook:
    """
    Integration test verifying that orchestrator invokes subagent stop hook
    on validation completion, preventing resource leaks.
    """

    def test_orchestrator_invokes_subagent_stop_hook_on_completion(
        self, in_memory_filesystem, mocked_hook, mocked_validator, mocked_time_provider
    ):
        """
        GIVEN a validation flow completes successfully
        WHEN DESOrchestrator.validate_prompt() returns
        THEN orchestrator must invoke subagent.stop() hook for cleanup

        Business Value: Ensures proper resource cleanup preventing memory leaks
        and zombie processes from incomplete subagent lifecycle management.
        """
        from src.des.application.orchestrator import DESOrchestrator

        orchestrator = DESOrchestrator(
            hook=mocked_hook,
            validator=mocked_validator,
            filesystem=in_memory_filesystem,
            time_provider=mocked_time_provider,
        )

        complete_prompt = """
        <!-- DES-VALIDATION: required -->

        # DES_METADATA
        Step: 01-08.json

        # AGENT_IDENTITY
        Agent: software-crafter

        # TASK_CONTEXT
        Integration test for subagent lifecycle

        # TDD_14_PHASES
        All 14 phases listed

        # QUALITY_GATES
        G1-G6

        # OUTCOME_RECORDING
        Update step file

        # BOUNDARY_RULES
        Scope

        # TIMEOUT_INSTRUCTION
        50 turns
        """

        # Act: Validate prompt through orchestrator
        result = orchestrator.validate_prompt(complete_prompt)

        # Assert: Validation completes and lifecycle hook called
        assert result.status == "PASSED"
        assert result.task_invocation_allowed is True
        # Verify stop hook was invoked (check orchestrator internal state or mock)
        assert hasattr(orchestrator, "_subagent_lifecycle_completed")
        assert orchestrator._subagent_lifecycle_completed is True
