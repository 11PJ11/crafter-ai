"""
Unit tests for template validator classes.

Tests the MandatorySectionChecker and TDDPhaseValidator functionality,
including recovery guidance generation for validation errors.
"""

from des.validator import MandatorySectionChecker, ValidationResult, TemplateValidator


class TestMandatorySectionChecker:
    """Unit tests for MandatorySectionChecker class."""

    def test_checker_validates_missing_section_error_message(self):
        """
        GIVEN prompt missing TIMEOUT_INSTRUCTION section
        WHEN MandatorySectionChecker.validate is called
        THEN error message matches expected format
        """
        checker = MandatorySectionChecker()
        prompt_without_timeout = """
        # DES_METADATA
        Step: 01-01.json
        # AGENT_IDENTITY
        Agent: software-crafter
        # TASK_CONTEXT
        Implement UserRepository
        # TDD_14_PHASES
        PREPARE through COMMIT
        # QUALITY_GATES
        G1-G6 defined
        # OUTCOME_RECORDING
        Update step file
        # BOUNDARY_RULES
        Scope defined
        """

        errors = checker.validate(prompt_without_timeout)

        assert len(errors) > 0
        assert any(
            "MISSING: Mandatory section 'TIMEOUT_INSTRUCTION' not found" in error
            for error in errors
        )

    def test_checker_validates_all_sections_present(self):
        """
        GIVEN prompt with all 8 mandatory sections
        WHEN MandatorySectionChecker.validate is called
        THEN errors list is empty
        """
        checker = MandatorySectionChecker()
        complete_prompt = """
        # DES_METADATA
        Step: 01-01.json
        # AGENT_IDENTITY
        Agent: software-crafter
        # TASK_CONTEXT
        Implement UserRepository
        # TDD_14_PHASES
        PREPARE through COMMIT
        # QUALITY_GATES
        G1-G6 defined
        # OUTCOME_RECORDING
        Update step file
        # BOUNDARY_RULES
        Scope defined
        # TIMEOUT_INSTRUCTION
        50 turns
        """

        errors = checker.validate(complete_prompt)

        assert errors == []

    def test_checker_detects_multiple_missing_sections(self):
        """
        GIVEN prompt missing multiple sections
        WHEN MandatorySectionChecker.validate is called
        THEN all missing sections are reported
        """
        checker = MandatorySectionChecker()
        minimal_prompt = """
        # DES_METADATA
        Step: 01-01.json
        # AGENT_IDENTITY
        Agent: software-crafter
        """

        errors = checker.validate(minimal_prompt)

        assert len(errors) >= 6
        missing_sections = [e for e in errors if "MISSING:" in e]
        assert len(missing_sections) >= 6


class TestValidationResultWithRecoveryGuidance:
    """Unit tests for ValidationResult with recovery guidance."""

    def test_validation_result_has_recovery_guidance_field(self):
        """
        GIVEN ValidationResult instantiated
        WHEN checking for recovery_guidance attribute
        THEN attribute exists
        """
        result = ValidationResult(
            status="FAILED",
            errors=["MISSING: Mandatory section 'TIMEOUT_INSTRUCTION' not found"],
            task_invocation_allowed=False,
            duration_ms=10.5,
            recovery_guidance="Add TIMEOUT_INSTRUCTION section with turn budget guidance",
        )

        assert hasattr(result, "recovery_guidance")
        assert result.recovery_guidance is not None

    def test_validation_result_recovery_guidance_for_missing_section(self):
        """
        GIVEN validation fails due to missing section
        WHEN ValidationResult is created with recovery guidance
        THEN guidance contains actionable instruction
        """
        guidance = "Add TIMEOUT_INSTRUCTION section with turn budget guidance"
        result = ValidationResult(
            status="FAILED",
            errors=["MISSING: Mandatory section 'TIMEOUT_INSTRUCTION' not found"],
            task_invocation_allowed=False,
            duration_ms=10.5,
            recovery_guidance=guidance,
        )

        assert "TIMEOUT_INSTRUCTION" in result.recovery_guidance
        assert "Add" in result.recovery_guidance


class TestTemplateValidatorRecoveryGuidance:
    """Unit tests for TemplateValidator recovery guidance generation."""

    def test_validator_includes_recovery_guidance_for_missing_section(self):
        """
        GIVEN prompt missing TIMEOUT_INSTRUCTION section
        WHEN TemplateValidator.validate_prompt is called
        THEN validation result includes recovery_guidance
        """
        validator = TemplateValidator()
        prompt_without_timeout = """
        # DES_METADATA
        Step: 01-01.json
        # AGENT_IDENTITY
        Agent: software-crafter
        # TASK_CONTEXT
        Implement UserRepository
        # TDD_14_PHASES
        PREPARE through COMMIT
        # QUALITY_GATES
        G1-G6 defined
        # OUTCOME_RECORDING
        Update step file
        # BOUNDARY_RULES
        Scope defined
        """

        result = validator.validate_prompt(prompt_without_timeout)

        assert result.recovery_guidance is not None
        assert "TIMEOUT_INSTRUCTION" in result.recovery_guidance

    def test_validator_recovery_guidance_matches_missing_section(self):
        """
        GIVEN prompt missing specific mandatory section
        WHEN validation fails
        THEN recovery_guidance names the missing section
        """
        validator = TemplateValidator()
        prompt_missing_boundary = """
        # DES_METADATA
        Step: 01-01.json
        # AGENT_IDENTITY
        Agent: software-crafter
        # TASK_CONTEXT
        Implement UserRepository
        # TDD_14_PHASES
        PREPARE through COMMIT
        # QUALITY_GATES
        G1-G6 defined
        # OUTCOME_RECORDING
        Update step file
        # TIMEOUT_INSTRUCTION
        50 turns
        """

        result = validator.validate_prompt(prompt_missing_boundary)

        assert result.recovery_guidance is not None
        assert "BOUNDARY_RULES" in result.recovery_guidance

    def test_validator_guidance_for_all_mandatory_sections(self):
        """
        GIVEN all 8 mandatory section types
        WHEN each section is tested for missing status
        THEN recovery guidance exists for each section type
        """
        validator = TemplateValidator()

        mandatory_sections = [
            "DES_METADATA",
            "AGENT_IDENTITY",
            "TASK_CONTEXT",
            "TDD_14_PHASES",
            "QUALITY_GATES",
            "OUTCOME_RECORDING",
            "BOUNDARY_RULES",
            "TIMEOUT_INSTRUCTION",
        ]

        complete_prompt = """
        # DES_METADATA
        Step: 01-01.json
        # AGENT_IDENTITY
        Agent: software-crafter
        # TASK_CONTEXT
        Implement UserRepository
        # TDD_14_PHASES
        PREPARE through COMMIT
        # QUALITY_GATES
        G1-G6 defined
        # OUTCOME_RECORDING
        Update step file
        # BOUNDARY_RULES
        Scope defined
        # TIMEOUT_INSTRUCTION
        50 turns
        """

        # Test each section individually
        for section in mandatory_sections:
            # Create prompt missing this section
            prompt_missing_section = "\n".join(
                [
                    line
                    for line in complete_prompt.split("\n")
                    if f"# {section}" not in line
                    and not (section == "DES_METADATA" and "Step:" in line)
                ]
            )

            result = validator.validate_prompt(prompt_missing_section)

            if result.status == "FAILED":
                assert result.recovery_guidance is not None

    def test_validator_passes_when_all_sections_present(self):
        """
        GIVEN prompt with all 8 mandatory sections
        WHEN validation runs
        THEN status is PASSED and recovery_guidance is None
        """
        validator = TemplateValidator()
        complete_prompt = """
        <!-- DES-VALIDATION: required -->
        # DES_METADATA
        Step: 01-01.json
        # AGENT_IDENTITY
        Agent: software-crafter
        # TASK_CONTEXT
        Implement UserRepository
        # TDD_14_PHASES
        PREPARE RED_ACCEPTANCE RED_UNIT GREEN_UNIT CHECK_ACCEPTANCE GREEN_ACCEPTANCE REVIEW REFACTOR_L1 REFACTOR_L2 REFACTOR_L3 REFACTOR_L4 POST_REFACTOR_REVIEW FINAL_VALIDATE COMMIT
        # QUALITY_GATES
        G1-G6 defined
        # OUTCOME_RECORDING
        Update step file
        # BOUNDARY_RULES
        Scope defined
        # TIMEOUT_INSTRUCTION
        50 turns
        """

        result = validator.validate_prompt(complete_prompt)

        assert result.status == "PASSED"
        assert result.errors == []
