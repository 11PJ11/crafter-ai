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

import pytest


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
        from des.validator import TemplateValidator

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

    @pytest.mark.skip(reason="Outside-In TDD RED state - awaiting DEVELOP wave")
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
        _prompt_missing_phase = """
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
        # validation_result = des_validator.validate_prompt(prompt_missing_phase)

        # Assert: Validation fails with specific error
        # assert validation_result.status == "FAILED"
        # assert "INCOMPLETE: TDD phase 'REFACTOR_L3' not mentioned" in validation_result.error_message
        # assert validation_result.task_invocation_allowed is False
        # assert "TASK_INVOCATION_REJECTED" in audit_log.get_recent_events()

    # =========================================================================
    # AC-002.3: Validation errors are specific and actionable
    # Scenario 6: Missing mandatory section blocks Task invocation
    # =========================================================================

    @pytest.mark.skip(reason="Outside-In TDD RED state - awaiting DEVELOP wave")
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
        _prompt_missing_section = """
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
        # validation_result = des_validator.validate_prompt(prompt_missing_section)

        # Assert: Validation fails with specific, actionable error
        # assert validation_result.status == "FAILED"
        # assert "MISSING: Mandatory section 'TIMEOUT_INSTRUCTION' not found" in validation_result.error_message
        # assert validation_result.task_invocation_allowed is False
        # assert "Add TIMEOUT_INSTRUCTION section with turn budget guidance" in validation_result.recovery_guidance

    # =========================================================================
    # AC-002.4: Task tool is NOT invoked if validation fails
    # Scenario 7: Multiple validation errors reported together
    # =========================================================================

    @pytest.mark.skip(reason="Outside-In TDD RED state - awaiting DEVELOP wave")
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
        # validation_result = des_validator.validate_prompt(prompt_with_multiple_errors)

        # Assert: All 3 errors reported together, Task NOT invoked
        # assert validation_result.status == "FAILED"
        # assert validation_result.error_count == 3
        # assert "MISSING: Mandatory section 'BOUNDARY_RULES' not found" in validation_result.errors
        # assert "INCOMPLETE: TDD phase 'GREEN_ACCEPTANCE' not mentioned" in validation_result.errors
        # assert "INCOMPLETE: TDD phase 'POST_REFACTOR_REVIEW' not mentioned" in validation_result.errors
        # assert validation_result.task_invocation_allowed is False
        # assert all(error.is_actionable for error in validation_result.errors)

    # =========================================================================
    # AC-002.5: Validation completes in < 500ms
    # Scenario 4 (Performance Aspect): Fast validation for smooth workflow
    # =========================================================================

    @pytest.mark.skip(reason="Outside-In TDD RED state - awaiting DEVELOP wave")
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
        # import time
        # start_time = time.perf_counter()
        # validation_result = des_validator.validate_prompt(complete_prompt)
        # duration_ms = (time.perf_counter() - start_time) * 1000

        # Assert: Validation passes AND completes quickly
        # assert validation_result.status == "PASSED"
        # assert duration_ms < 500, f"Validation took {duration_ms}ms, exceeds 500ms budget"
        # assert validation_result.task_invocation_allowed is True

    # =========================================================================
    # Additional Edge Case: Malformed DES marker validation
    # Ensures robust validation even with corrupted metadata
    # =========================================================================

    @pytest.mark.skip(reason="Outside-In TDD RED state - awaiting DEVELOP wave")
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
        _prompt_malformed_marker = """
        <!-- DES-VALIDATION: unknown -->
        <!-- DES-STEP-FILE: steps/01-06.json -->

        # Complete sections follow...
        """

        # Act: Run pre-invocation validation
        # validation_result = des_validator.validate_prompt(prompt_malformed_marker)

        # Assert: Validation fails with invalid marker error
        # assert validation_result.status == "FAILED"
        # assert "INVALID_MARKER: DES-VALIDATION value must be 'required'" in validation_result.error_message
        # assert validation_result.task_invocation_allowed is False
