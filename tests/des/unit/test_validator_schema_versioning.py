"""
Unit tests for template validator schema version support.

Tests validate that validator correctly:
1. Detects schema version from prompt text
2. Validates appropriate phase set for each schema version
3. Validates phase execution log structure matches schema

These tests drive implementation for Step US-005-03 schema versioning in validator.
"""

from src.des.application.validator import (
    TDDPhaseValidator,
    ExecutionLogValidator,
)


class TestTDDPhaseValidatorSchemaDetection:
    """Tests for schema version detection in TDDPhaseValidator."""

    def test_detect_schema_v2_0_from_prompt(self):
        """
        GIVEN prompt with schema v2.0 indicators
        WHEN detect_schema_version_from_prompt() called
        THEN returns "2.0"
        """
        # GIVEN: Prompt with v2.0 indicators
        prompt = """
        Schema v2.0 TDD cycle:
        - PREPARE
        - RED_ACCEPTANCE
        - RED_UNIT
        - GREEN
        - REVIEW
        - REFACTOR_CONTINUOUS
        - REFACTOR_L4
        - COMMIT
        """
        validator = TDDPhaseValidator()

        # WHEN: Schema version detected
        detected_version = validator.detect_schema_version_from_prompt(prompt)

        # THEN: v2.0 detected
        assert detected_version == "2.0"

    def test_detect_schema_v1_0_default_when_not_specified(self):
        """
        GIVEN prompt without explicit schema version
        WHEN detect_schema_version_from_prompt() called
        THEN returns "1.0" (backward compatibility default)
        """
        # GIVEN: Generic prompt without schema indicators
        prompt = """
        Execute these phases:
        1. PREPARE
        2. RED_ACCEPTANCE
        3. RED_UNIT
        """
        validator = TDDPhaseValidator()

        # WHEN: Schema version detected
        detected_version = validator.detect_schema_version_from_prompt(prompt)

        # THEN: v1.0 returned as default
        assert detected_version == "1.0"

    def test_detect_schema_with_8_phases_indicator(self):
        """
        GIVEN prompt mentioning "8-phase" or "8 phases"
        WHEN detect_schema_version_from_prompt() called
        THEN returns "2.0"
        """
        # GIVEN: Prompt with "8-phase" indicator
        prompt = """
        Execute the 8-phase TDD cycle:
        1. PREPARE
        2. RED_ACCEPTANCE
        3. RED_UNIT
        4. GREEN
        5. REVIEW
        6. REFACTOR_CONTINUOUS
        7. REFACTOR_L4
        8. COMMIT
        """
        validator = TDDPhaseValidator()

        # WHEN: Schema version detected
        detected_version = validator.detect_schema_version_from_prompt(prompt)

        # THEN: v2.0 detected
        assert detected_version == "2.0"


class TestTDDPhaseValidatorPhaseValidation:
    """Tests for schema-aware phase validation."""

    def test_validate_v1_0_phases_requires_14_phases(self):
        """
        GIVEN v1.0 schema prompt
        WHEN validate() called
        THEN checks for all 14 legacy phases
        """
        # GIVEN: v1.0 prompt with all 14 phases
        prompt = """
        # TDD_14_PHASES
        Execute these 14 phases:
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
        validator = TDDPhaseValidator()

        # WHEN: Validation performed
        errors = validator.validate(prompt)

        # THEN: No errors for complete 14-phase prompt
        assert len(errors) == 0

    def test_validate_v2_0_phases_requires_8_phases(self):
        """
        GIVEN v2.0 schema prompt with "schema_v2.0" indicator
        WHEN validate() called
        THEN checks for all 8 optimized phases

        Uses shorthand "All 8 phases listed" to pass validation.
        """
        # GIVEN: v2.0 prompt with shorthand indicator
        prompt = """
        # TDD_PHASES
        Schema v2.0 - All 8 phases listed:
        1. PREPARE
        2. RED_ACCEPTANCE
        3. RED_UNIT
        4. GREEN
        5. REVIEW
        6. REFACTOR_CONTINUOUS
        7. REFACTOR_L4
        8. COMMIT
        """
        validator = TDDPhaseValidator()

        # WHEN: Validation performed
        errors = validator.validate(prompt)

        # THEN: No errors when all 8 phases present
        assert len(errors) == 0

    def test_validate_v1_0_accepts_14_phases(self):
        """
        GIVEN v1.0 schema (default when no schema indicator)
        WHEN all 14 phases listed in prompt
        THEN validation passes
        """
        # GIVEN: Prompt with all 14 legacy phases (no v2.0 indicator)
        prompt = """
        # TDD_PHASES
        Execute all phases:
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
        validator = TDDPhaseValidator()

        # WHEN: Validation performed (defaults to v1.0)
        errors = validator.validate(prompt)

        # THEN: No errors when all 14 phases present
        assert len(errors) == 0


class TestExecutionLogValidatorSchemaCompliance:
    """Tests for schema-compliant phase execution log validation."""

    def test_validate_v2_0_requires_8_phases_in_log(self):
        """
        GIVEN v2.0 schema execution log with 8 phases
        WHEN validate() called with schema_version="2.0"
        THEN validates successfully
        """
        # GIVEN: v2.0 phase execution log with exactly 8 phases
        phase_log = [
            {"phase_name": "PREPARE", "status": "EXECUTED", "outcome": "PASS"},
            {"phase_name": "RED_ACCEPTANCE", "status": "EXECUTED", "outcome": "PASS"},
            {"phase_name": "RED_UNIT", "status": "EXECUTED", "outcome": "PASS"},
            {"phase_name": "GREEN", "status": "EXECUTED", "outcome": "PASS"},
            {"phase_name": "REVIEW", "status": "EXECUTED", "outcome": "PASS"},
            {
                "phase_name": "REFACTOR_CONTINUOUS",
                "status": "EXECUTED",
                "outcome": "PASS",
            },
            {
                "phase_name": "REFACTOR_L4",
                "status": "SKIPPED",
                "blocked_by": "NOT_APPLICABLE: Trivial feature",
            },
            {"phase_name": "COMMIT", "status": "EXECUTED", "outcome": "PASS"},
        ]
        validator = ExecutionLogValidator()

        # WHEN: Validation with v2.0 schema
        errors = validator.validate(phase_log, schema_version="2.0")

        # THEN: No errors for valid v2.0 log
        assert len(errors) == 0

    def test_validate_v1_0_requires_14_phases_in_log(self):
        """
        GIVEN v1.0 schema execution log with 14 phases
        WHEN validate() called with schema_version="1.0"
        THEN validates successfully
        """
        # GIVEN: v1.0 phase execution log with exactly 14 legacy phases
        phase_log = [
            {"phase_name": "PREPARE", "status": "EXECUTED", "outcome": "PASS"},
            {"phase_name": "RED_ACCEPTANCE", "status": "EXECUTED", "outcome": "PASS"},
            {"phase_name": "RED_UNIT", "status": "EXECUTED", "outcome": "PASS"},
            {"phase_name": "GREEN_UNIT", "status": "EXECUTED", "outcome": "PASS"},
            {"phase_name": "CHECK_ACCEPTANCE", "status": "EXECUTED", "outcome": "PASS"},
            {"phase_name": "GREEN_ACCEPTANCE", "status": "EXECUTED", "outcome": "PASS"},
            {"phase_name": "REVIEW", "status": "EXECUTED", "outcome": "PASS"},
            {"phase_name": "REFACTOR_L1", "status": "EXECUTED", "outcome": "PASS"},
            {"phase_name": "REFACTOR_L2", "status": "EXECUTED", "outcome": "PASS"},
            {"phase_name": "REFACTOR_L3", "status": "EXECUTED", "outcome": "PASS"},
            {"phase_name": "REFACTOR_L4", "status": "EXECUTED", "outcome": "PASS"},
            {
                "phase_name": "POST_REFACTOR_REVIEW",
                "status": "EXECUTED",
                "outcome": "PASS",
            },
            {"phase_name": "FINAL_VALIDATE", "status": "EXECUTED", "outcome": "PASS"},
            {"phase_name": "COMMIT", "status": "EXECUTED", "outcome": "PASS"},
        ]
        validator = ExecutionLogValidator()

        # WHEN: Validation with v1.0 schema
        errors = validator.validate(phase_log, schema_version="1.0")

        # THEN: No errors for valid v1.0 log (14 phases with correct names)
        assert len(errors) == 0

    def test_validate_v2_0_rejects_14_phase_log(self):
        """
        GIVEN v2.0 schema declared
        WHEN phase log has 14 phases (v1.0 format)
        THEN validation fails with phase count mismatch
        """
        # GIVEN: 14-phase log but v2.0 schema expected
        phase_log = [
            {"phase_name": f"PHASE_{i}", "status": "EXECUTED", "outcome": "PASS"}
            for i in range(14)
        ]
        validator = ExecutionLogValidator()

        # WHEN: Validation with v2.0 schema
        errors = validator.validate(phase_log, schema_version="2.0")

        # THEN: Error about phase count mismatch
        assert len(errors) > 0
        count_errors = [e for e in errors if "has 14 phases" in e and "expected 8" in e]
        assert len(count_errors) > 0

    def test_validate_v2_0_requires_correct_phase_names(self):
        """
        GIVEN v2.0 schema
        WHEN phase log missing required v2.0 phases
        THEN validation fails with missing phase error
        """
        # GIVEN: v2.0 log missing REFACTOR_CONTINUOUS phase
        phase_log = [
            {"phase_name": "PREPARE", "status": "EXECUTED", "outcome": "PASS"},
            {"phase_name": "RED_ACCEPTANCE", "status": "EXECUTED", "outcome": "PASS"},
            {"phase_name": "RED_UNIT", "status": "EXECUTED", "outcome": "PASS"},
            {"phase_name": "GREEN", "status": "EXECUTED", "outcome": "PASS"},
            {"phase_name": "REVIEW", "status": "EXECUTED", "outcome": "PASS"},
            # MISSING: REFACTOR_CONTINUOUS
            {
                "phase_name": "REFACTOR_L4",
                "status": "SKIPPED",
                "blocked_by": "NOT_APPLICABLE",
            },
            {"phase_name": "COMMIT", "status": "EXECUTED", "outcome": "PASS"},
        ]
        validator = ExecutionLogValidator()

        # WHEN: Validation with v2.0 schema
        errors = validator.validate(phase_log, schema_version="2.0")

        # THEN: Error about missing phase
        assert len(errors) > 0
        missing_errors = [e for e in errors if "Missing required phases" in e]
        assert len(missing_errors) > 0
        assert "REFACTOR_CONTINUOUS" in missing_errors[0]
