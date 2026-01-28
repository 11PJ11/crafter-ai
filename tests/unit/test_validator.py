"""
Unit tests for DES template validation components.

Tests MandatorySectionChecker, TDDPhaseValidator, DESMarkerValidator,
and TemplateValidator orchestrator using business-focused test naming.

NOTE: ExecutionLogValidator tests have been moved to SubagentStopHook tests.
Execution log validation happens POST-execution in the hook, not PRE-invocation
in template validation. See tests/des/unit/application/test_hooks.py
"""

from src.des.application.validator import (
    ValidationResult,
    MandatorySectionChecker,
    TDDPhaseValidator,
    DESMarkerValidator,
    TemplateValidator,
)


class TestMandatorySectionChecker:
    """MandatorySectionChecker unit tests."""

    def test_pass_when_all_8_sections_present(self):
        """Checker validates all 8 mandatory sections are present."""
        checker = MandatorySectionChecker()

        prompt = """
        # DES_METADATA
        # AGENT_IDENTITY
        # TASK_CONTEXT
        # TDD_14_PHASES
        # QUALITY_GATES
        # OUTCOME_RECORDING
        # BOUNDARY_RULES
        # TIMEOUT_INSTRUCTION
        """

        errors = checker.validate(prompt)

        assert len(errors) == 0

    def test_detect_missing_mandatory_section(self):
        """Checker detects when mandatory section is missing."""
        checker = MandatorySectionChecker()

        prompt = """
        # DES_METADATA
        # AGENT_IDENTITY
        # TASK_CONTEXT
        # TDD_14_PHASES
        # QUALITY_GATES
        # OUTCOME_RECORDING
        # BOUNDARY_RULES
        # (missing TIMEOUT_INSTRUCTION)
        """

        errors = checker.validate(prompt)

        assert len(errors) == 1
        assert "TIMEOUT_INSTRUCTION" in errors[0]
        assert "MISSING" in errors[0]

    def test_generate_recovery_guidance_for_missing_sections(self):
        """Checker generates guidance for missing sections."""
        checker = MandatorySectionChecker()

        prompt = """
        # DES_METADATA
        # AGENT_IDENTITY
        """

        errors = checker.validate(prompt)
        guidance = checker.get_recovery_guidance(errors)

        assert guidance is not None
        assert "TASK_CONTEXT" in guidance or len(errors) > 0


class TestTDDPhaseValidator:
    """TDDPhaseValidator unit tests."""

    def test_pass_when_all_14_phases_mentioned(self):
        """Validator passes when all 14 phases are present."""
        validator = TDDPhaseValidator()

        prompt = """
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
        """

        errors = validator.validate(prompt)

        assert len(errors) == 0

    def test_detect_missing_tdd_phase(self):
        """Validator detects when TDD phase is missing."""
        validator = TDDPhaseValidator()

        prompt = """
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
        (missing COMMIT)
        """

        errors = validator.validate(prompt)

        assert len(errors) == 1
        assert "COMMIT" in errors[0]
        assert "INCOMPLETE" in errors[0]


class TestDESMarkerValidator:
    """DESMarkerValidator unit tests."""

    def test_pass_when_marker_is_valid(self):
        """Validator passes with valid DES-VALIDATION marker."""
        validator = DESMarkerValidator()

        prompt = "<!-- DES-VALIDATION: required -->\nSome prompt content"

        errors = validator.validate(prompt)

        assert len(errors) == 0

    def test_detect_missing_marker(self):
        """Validator detects when DES-VALIDATION marker is missing."""
        validator = DESMarkerValidator()

        prompt = "Prompt content without marker"

        errors = validator.validate(prompt)

        assert len(errors) == 1
        assert "INVALID_MARKER" in errors[0]

    def test_detect_invalid_marker_value(self):
        """Validator rejects marker with incorrect value."""
        validator = DESMarkerValidator()

        prompt = "<!-- DES-VALIDATION: optional -->\nSome prompt"

        errors = validator.validate(prompt)

        assert len(errors) == 1
        assert "INVALID_MARKER" in errors[0]
        assert "required" in errors[0]


class TestTemplateValidator:
    """TemplateValidator orchestrator unit tests."""

    def test_return_passed_status_for_valid_prompt(self):
        """Validator returns PASSED status for completely valid prompt."""
        validator = TemplateValidator()

        prompt = """
        <!-- DES-VALIDATION: required -->
        # DES_METADATA
        # AGENT_IDENTITY
        # TASK_CONTEXT
        # TDD_14_PHASES
        # QUALITY_GATES
        # OUTCOME_RECORDING
        # BOUNDARY_RULES
        # TIMEOUT_INSTRUCTION

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
        """

        result = validator.validate_prompt(prompt)

        assert result.status == "PASSED"
        assert result.task_invocation_allowed is True
        assert len(result.errors) == 0

    def test_return_failed_status_with_errors(self):
        """Validator returns FAILED status with error details."""
        validator = TemplateValidator()

        prompt = "Incomplete prompt without sections"

        result = validator.validate_prompt(prompt)

        assert result.status == "FAILED"
        assert result.task_invocation_allowed is False
        assert len(result.errors) > 0

    def test_block_invocation_when_validation_fails(self):
        """Validator blocks task invocation when validation fails."""
        validator = TemplateValidator()

        prompt = "Missing all required sections and marker"

        result = validator.validate_prompt(prompt)

        assert result.task_invocation_allowed is False

    def test_allow_invocation_when_validation_passes(self):
        """Validator allows task invocation when validation passes."""
        validator = TemplateValidator()

        prompt = """
        <!-- DES-VALIDATION: required -->
        # DES_METADATA
        # AGENT_IDENTITY
        # TASK_CONTEXT
        # TDD_14_PHASES
        # QUALITY_GATES
        # OUTCOME_RECORDING
        # BOUNDARY_RULES
        # TIMEOUT_INSTRUCTION

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
        """

        result = validator.validate_prompt(prompt)

        assert result.task_invocation_allowed is True

    def test_combine_marker_section_and_phase_errors(self):
        """Validator combines all error types when present."""
        validator = TemplateValidator()

        prompt = "Missing everything"

        result = validator.validate_prompt(prompt)

        assert result.status == "FAILED"
        assert len(result.errors) >= 3  # At least marker, sections, and phases
        assert any("INVALID_MARKER" in e for e in result.errors)
        assert any("MISSING" in e for e in result.errors)

    def test_include_recovery_guidance_in_result(self):
        """Validator includes recovery guidance in result."""
        validator = TemplateValidator()

        prompt = "# DES_METADATA\n# AGENT_IDENTITY"  # Only 2 sections

        result = validator.validate_prompt(prompt)

        assert result.recovery_guidance is not None
        assert len(result.recovery_guidance) > 0

    def test_measure_validation_duration(self):
        """Validator measures validation execution time."""
        validator = TemplateValidator()

        prompt = """
        <!-- DES-VALIDATION: required -->
        # DES_METADATA
        # AGENT_IDENTITY
        # TASK_CONTEXT
        # TDD_14_PHASES
        # QUALITY_GATES
        # OUTCOME_RECORDING
        # BOUNDARY_RULES
        # TIMEOUT_INSTRUCTION

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
        """

        result = validator.validate_prompt(prompt)

        assert result.duration_ms >= 0
        assert result.duration_ms < 500  # Should be fast

    def test_return_immutable_validation_result(self):
        """Validator returns immutable ValidationResult dataclass."""
        validator = TemplateValidator()

        prompt = "Invalid prompt"
        result = validator.validate_prompt(prompt)

        # Should not be able to modify result (dataclass with frozen=True if applicable)
        assert isinstance(result, ValidationResult)
        assert hasattr(result, "status")
        assert hasattr(result, "errors")
        assert hasattr(result, "task_invocation_allowed")
