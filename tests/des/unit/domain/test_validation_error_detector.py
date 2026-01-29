"""
Unit Tests: ValidationErrorDetector - Step 02-03

Tests for detecting validation errors in step file structure:
- Missing required fields (DES_METADATA, AGENT_IDENTITY, etc.)
- Invalid phase execution sequences
- Missing acceptance criteria
- Specific fix guidance generation

These tests drive the implementation of ValidationErrorDetector domain service.
"""


class TestValidationErrorDetector:
    """Unit tests for ValidationErrorDetector domain service."""

    def test_validation_error_detector_exists(self):
        """
        GIVEN a ValidationErrorDetector class
        WHEN it is instantiated
        THEN it should exist and be callable for validation

        Acceptance Criteria (AC-005.1):
        - Detector can be created and used to validate step files
        """
        from src.des.domain.validation_error_detector import ValidationErrorDetector

        detector = ValidationErrorDetector()
        assert detector is not None
        assert callable(detector.detect_errors)

    def test_detects_missing_required_fields(self):
        """
        GIVEN a step file missing required fields (e.g., step_id, acceptance_criteria)
        WHEN validation detector analyzes the step file
        THEN it should identify and report the missing fields

        Acceptance Criteria (AC-005.1):
        - Identifies missing required step file fields
        - Error message specifies which field is missing
        """
        from src.des.domain.validation_error_detector import ValidationErrorDetector

        detector = ValidationErrorDetector()

        # Incomplete step data missing acceptance_criteria
        incomplete_step = {
            "step_id": "02-03",
            "step_name": "Test step",
            "project_id": "des-us005",
            # Missing: acceptance_criteria
            # Missing: required_acceptance_test
        }

        errors = detector.detect_errors(incomplete_step)

        assert errors is not None, "Should detect missing fields"
        assert isinstance(errors, list), "Errors should be a list"
        assert len(errors) > 0, "Should have at least one error"
        assert any(
            "acceptance_criteria" in err.lower() for err in errors
        ), "Should identify missing acceptance_criteria"

    def test_detects_invalid_phase_sequences(self):
        """
        GIVEN a step file with phases in invalid execution order
        WHEN validation detector analyzes the phase sequence
        THEN it should identify the invalid sequence

        Acceptance Criteria (AC-005.1):
        - Detects invalid phase execution sequences
        - Example: COMMIT before REVIEW is invalid
        - Example: REFACTOR_L2 before RED_UNIT is invalid
        """
        from src.des.domain.validation_error_detector import ValidationErrorDetector

        detector = ValidationErrorDetector()

        # Invalid: COMMIT before REVIEW
        invalid_phases = {
            "phase_execution_log": [
                {"phase_name": "PREPARE", "phase_index": 0},
                {"phase_name": "RED_ACCEPTANCE", "phase_index": 1},
                {"phase_name": "COMMIT", "phase_index": 2},  # Invalid: too early
                {"phase_name": "REVIEW", "phase_index": 3},  # Invalid: after COMMIT
            ]
        }

        errors = detector.detect_phase_sequence_errors(invalid_phases)

        assert errors is not None, "Should detect phase sequence errors"
        assert isinstance(errors, list), "Errors should be a list"
        assert len(errors) > 0, "Should have at least one sequence error"
        assert any(
            "COMMIT" in err or "sequence" in err.lower() for err in errors
        ), "Should mention COMMIT or sequence violation"

    def test_detects_missing_acceptance_criteria(self):
        """
        GIVEN a step file with empty or missing acceptance_criteria field
        WHEN validation detector analyzes the step
        THEN it should identify acceptance criteria completeness issue

        Acceptance Criteria (AC-005.1):
        - Validates acceptance criteria completeness
        - Empty acceptance_criteria is invalid
        - Must have concrete, testable criteria
        """
        from src.des.domain.validation_error_detector import ValidationErrorDetector

        detector = ValidationErrorDetector()

        # Step with missing acceptance criteria
        step_missing_ac = {
            "step_id": "02-03",
            "acceptance_criteria": "",  # Empty criteria
            "tdd_cycle": {},
        }

        errors = detector.detect_acceptance_criteria_errors(step_missing_ac)

        assert errors is not None, "Should detect missing AC"
        assert isinstance(errors, list), "Errors should be a list"
        assert len(errors) > 0, "Should have at least one AC error"
        assert any(
            "acceptance" in err.lower() or "criteria" in err.lower() for err in errors
        ), "Should mention acceptance criteria"

    def test_provides_specific_fix_guidance(self):
        """
        GIVEN a validation error (missing field, invalid sequence, etc.)
        WHEN generating fix guidance
        THEN guidance should be specific and actionable

        Acceptance Criteria (AC-005.4):
        - Fix guidance explains WHAT to add/fix
        - Guidance includes HOW to fix it
        - Guidance references specific field names or phase names

        Example (BAD): "Fix your step file"
        Example (GOOD): "Add 'acceptance_criteria' field with comma-separated AC statements like 'Detects missing fields, Generates recovery suggestions'"
        """
        from src.des.domain.validation_error_detector import ValidationErrorDetector

        detector = ValidationErrorDetector()

        # Error about missing acceptance_criteria
        error = "Missing required field: acceptance_criteria"

        fix_guidance = detector.get_fix_guidance(error)

        assert fix_guidance is not None, "Should provide fix guidance"
        assert isinstance(fix_guidance, str), "Guidance should be a string"
        assert len(fix_guidance) > 0, "Guidance should not be empty"

        # Guidance should be specific and mention the field
        assert (
            "acceptance_criteria" in fix_guidance
        ), "Should mention the specific field"
        # Guidance should include action keywords
        assert any(
            keyword in fix_guidance.lower()
            for keyword in ["add", "include", "update", "with", "should contain"]
        ), "Guidance should include action verbs"

    def test_handles_partial_validation(self):
        """
        GIVEN a step file with some valid and some invalid data
        WHEN validation detector performs partial analysis
        THEN it should identify invalid portions while acknowledging valid portions

        Acceptance Criteria (AC-005.1):
        - Handles partially valid step files
        - Reports only actual errors, not assumptions
        - Distinguishes between valid and invalid phases

        Scenario: Phases 1-3 complete (EXECUTED), phase 4 incomplete (IN_PROGRESS),
                 remaining phases invalid (out of order)
        """
        from src.des.domain.validation_error_detector import ValidationErrorDetector

        detector = ValidationErrorDetector()

        # Partially valid step
        partial_step = {
            "step_id": "02-03",
            "acceptance_criteria": "Detects missing fields",
            "tdd_cycle": {
                "phase_execution_log": [
                    {"phase_name": "PREPARE", "status": "EXECUTED", "phase_index": 0},
                    {
                        "phase_name": "RED_ACCEPTANCE",
                        "status": "EXECUTED",
                        "phase_index": 1,
                    },
                    {"phase_name": "RED_UNIT", "status": "EXECUTED", "phase_index": 2},
                    {
                        "phase_name": "GREEN",
                        "status": "IN_PROGRESS",
                        "phase_index": 3,
                    },  # Valid, but incomplete
                    # Missing phases after GREEN
                ]
            },
        }

        results = detector.validate_partial_state(partial_step)

        assert results is not None, "Should validate partial state"
        assert "valid_phases" in results, "Should report valid phases"
        assert "invalid_phases" in results, "Should report invalid phases"
        assert "incomplete_phases" in results, "Should report incomplete phases"

        # Check that completed phases are marked as valid
        assert len(results["valid_phases"]) >= 3, "First 3 phases should be valid"

        # Check that incomplete phase is reported separately
        assert (
            len(results["incomplete_phases"]) >= 1
        ), "Should identify incomplete phase"
