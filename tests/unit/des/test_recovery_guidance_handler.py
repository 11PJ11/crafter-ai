"""
Unit tests for RecoveryGuidanceHandler.

Tests the core recovery guidance generation and persistence functionality.
"""

import pytest
import json
from src.des.application.recovery_guidance_handler import RecoveryGuidanceHandler


class TestRecoveryGuidanceHandlerInstantiation:
    """Test RecoveryGuidanceHandler instantiation."""

    def test_instantiate_without_errors(self):
        """Should instantiate RecoveryGuidanceHandler without errors."""
        handler = RecoveryGuidanceHandler()
        assert handler is not None
        assert isinstance(handler, RecoveryGuidanceHandler)


class TestGenerateRecoverySuggestions:
    """Test generate_recovery_suggestions method."""

    def test_generate_suggestions_for_abandoned_phase(self):
        """Should generate suggestions for abandoned_phase failure mode."""
        handler = RecoveryGuidanceHandler()
        suggestions = handler.generate_recovery_suggestions(
            failure_type="abandoned_phase",
            context={
                "phase": "GREEN_UNIT",
                "step_file": "steps/01-01.json",
            },
        )

        assert suggestions is not None
        assert isinstance(suggestions, list)
        assert len(suggestions) > 0
        # Each suggestion should be a string
        assert all(isinstance(s, str) for s in suggestions)

    def test_generate_suggestions_for_silent_completion(self):
        """Should generate suggestions for silent_completion failure mode."""
        handler = RecoveryGuidanceHandler()
        suggestions = handler.generate_recovery_suggestions(
            failure_type="silent_completion",
            context={
                "step_file": "steps/01-01.json",
                "transcript_path": "/tmp/transcript.log",
            },
        )

        assert suggestions is not None
        assert isinstance(suggestions, list)
        assert len(suggestions) > 0
        assert all(isinstance(s, str) for s in suggestions)

    def test_suggestions_include_actionable_elements_abandoned_phase(self):
        """Suggestions should include actionable elements for abandoned phase."""
        handler = RecoveryGuidanceHandler()
        suggestions = handler.generate_recovery_suggestions(
            failure_type="abandoned_phase",
            context={
                "phase": "RED_UNIT",
                "step_file": "steps/01-01.json",
            },
        )

        # At least one should mention transcript
        has_transcript_ref = any("transcript" in s.lower() for s in suggestions)
        assert has_transcript_ref, "Should reference transcript"

        # At least one should mention phase name
        has_phase_ref = any("RED_UNIT" in s for s in suggestions)
        assert has_phase_ref, "Should reference the phase name"

        # At least one should mention NOT_EXECUTED or execution command
        has_execution_ref = any(
            "NOT_EXECUTED" in s or "/nw:execute" in s or "execute" in s.lower()
            for s in suggestions
        )
        assert has_execution_ref, "Should reference execution or phase status"

    def test_suggestions_include_actionable_elements_with_transcript_path(self):
        """Suggestions should include specific transcript path when provided."""
        handler = RecoveryGuidanceHandler()
        transcript_path = "/tmp/transcripts/agent-123.log"
        suggestions = handler.generate_recovery_suggestions(
            failure_type="abandoned_phase",
            context={
                "phase": "GREEN_UNIT",
                "transcript_path": transcript_path,
            },
        )

        # At least one should include the specific transcript path
        has_path = any(transcript_path in s for s in suggestions)
        assert has_path, f"Should reference specific transcript path: {transcript_path}"


class TestFormatSuggestion:
    """Test format_suggestion method."""

    def test_format_suggestion_creates_formatted_string(self):
        """Should create properly formatted suggestion from components."""
        handler = RecoveryGuidanceHandler()

        formatted = handler.format_suggestion(
            why_text="The agent crashed during phase execution",
            how_text="Reset the phase status to NOT_EXECUTED and retry",
            actionable_command="/nw:execute @software-crafter 'steps/01-01.json'",
        )

        assert formatted is not None
        assert isinstance(formatted, str)
        assert len(formatted) > 0

    def test_formatted_suggestion_includes_all_components(self):
        """Formatted suggestion should include WHY, HOW, and actionable elements."""
        handler = RecoveryGuidanceHandler()

        why_text = "Phase left in IN_PROGRESS state indicates interruption"
        how_text = "Resetting allows framework to retry from clean state"
        command = "/nw:execute @software-crafter 'steps/01-01.json'"

        formatted = handler.format_suggestion(
            why_text=why_text,
            how_text=how_text,
            actionable_command=command,
        )

        # Should contain Why
        assert why_text in formatted or any(
            word in formatted for word in why_text.split()
        )
        # Should contain How
        assert how_text in formatted or any(
            word in formatted for word in how_text.split()
        )
        # Should contain actionable command
        assert command in formatted


class TestHandleFailure:
    """Test handle_failure method."""

    def test_handle_failure_returns_dict(self, tmp_path):
        """Should return a dictionary with recovery suggestions."""
        handler = RecoveryGuidanceHandler()

        # Create a simple step file
        step_file_path = tmp_path / "step.json"
        step_data = {
            "task_id": "01-01",
            "state": {
                "status": "IN_PROGRESS",
            },
        }
        step_file_path.write_text(json.dumps(step_data))

        result = handler.handle_failure(
            step_file_path=str(step_file_path),
            failure_type="abandoned_phase",
            context={
                "phase": "GREEN_UNIT",
                "failure_reason": "Agent crashed during GREEN_UNIT phase",
            },
        )

        assert result is not None
        assert isinstance(result, dict)
        assert "recovery_suggestions" in result
        assert isinstance(result["recovery_suggestions"], list)
        assert len(result["recovery_suggestions"]) > 0

    def test_handle_failure_persists_to_step_file(self, tmp_path):
        """Should persist recovery suggestions to step file JSON."""
        handler = RecoveryGuidanceHandler()

        # Create a step file
        step_file_path = tmp_path / "step.json"
        step_data = {
            "task_id": "01-01",
            "state": {
                "status": "IN_PROGRESS",
            },
        }
        step_file_path.write_text(json.dumps(step_data))

        # Handle failure
        handler.handle_failure(
            step_file_path=str(step_file_path),
            failure_type="abandoned_phase",
            context={
                "phase": "GREEN_UNIT",
                "failure_reason": "Agent crashed during GREEN_UNIT phase",
            },
        )

        # Verify step file was updated
        updated_data = json.loads(step_file_path.read_text())
        assert "recovery_suggestions" in updated_data["state"]
        assert isinstance(updated_data["state"]["recovery_suggestions"], list)
        assert len(updated_data["state"]["recovery_suggestions"]) > 0

    def test_handle_failure_includes_failure_reason(self, tmp_path):
        """Should include failure reason in updated state."""
        handler = RecoveryGuidanceHandler()

        step_file_path = tmp_path / "step.json"
        step_data = {
            "task_id": "01-01",
            "state": {
                "status": "IN_PROGRESS",
            },
        }
        step_file_path.write_text(json.dumps(step_data))

        result = handler.handle_failure(
            step_file_path=str(step_file_path),
            failure_type="abandoned_phase",
            context={
                "phase": "RED_UNIT",
                "failure_reason": "Agent crashed during RED_UNIT phase",
            },
        )

        assert "failure_reason" in result or "failure_reason" in str(result)


class TestSupportedFailureModes:
    """Test support for all defined failure modes."""

    @pytest.mark.parametrize(
        "failure_type",
        [
            "abandoned_phase",
            "silent_completion",
            "missing_section",
            "invalid_outcome",
        ],
    )
    def test_generate_suggestions_for_all_supported_modes(self, failure_type):
        """Should generate suggestions for all supported failure modes."""
        handler = RecoveryGuidanceHandler()
        suggestions = handler.generate_recovery_suggestions(
            failure_type=failure_type,
            context={
                "phase": "GREEN_UNIT",
                "step_file": "steps/01-01.json",
            },
        )

        assert suggestions is not None
        assert isinstance(suggestions, list)
        assert len(suggestions) > 0
