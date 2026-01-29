"""
Unit Tests: RecoveryGuidanceHandler

Tests core functionality of the RecoveryGuidanceHandler class including:
- Instantiation and method existence
- Recovery suggestion generation for different failure modes
- Suggestion formatting with WHY+HOW+ACTION structure
- Step file persistence
- Handling unknown failure types
- Context parameter application
"""

import json
from src.des.application.recovery_guidance_handler import (
    RecoveryGuidanceHandler,
    SuggestionFormatter,
)


class TestRecoveryGuidanceHandlerInstantiation:
    """Tests for RecoveryGuidanceHandler class instantiation."""

    def test_recovery_handler_class_exists(self):
        """RecoveryGuidanceHandler class should be instantiable."""
        handler = RecoveryGuidanceHandler()
        assert handler is not None
        assert isinstance(handler, RecoveryGuidanceHandler)

    def test_recovery_handler_has_generate_recovery_suggestions_method(self):
        """RecoveryGuidanceHandler should have generate_recovery_suggestions method."""
        handler = RecoveryGuidanceHandler()
        assert hasattr(handler, "generate_recovery_suggestions")
        assert callable(handler.generate_recovery_suggestions)

    def test_recovery_handler_has_handle_failure_method(self):
        """RecoveryGuidanceHandler should have handle_failure method."""
        handler = RecoveryGuidanceHandler()
        assert hasattr(handler, "handle_failure")
        assert callable(handler.handle_failure)

    def test_recovery_handler_has_format_suggestion_method(self):
        """RecoveryGuidanceHandler should have format_suggestion method."""
        handler = RecoveryGuidanceHandler()
        assert hasattr(handler, "format_suggestion")
        assert callable(handler.format_suggestion)


class TestGenerateRecoverySuggestions:
    """Tests for generate_recovery_suggestions method."""

    def test_generates_suggestions_for_abandoned_phase(self):
        """Should generate suggestions for abandoned_phase failure mode."""
        handler = RecoveryGuidanceHandler()
        suggestions = handler.generate_recovery_suggestions(
            failure_type="abandoned_phase",
            context={"phase": "GREEN_UNIT"},
        )

        assert suggestions is not None
        assert isinstance(suggestions, list)
        assert len(suggestions) > 0

    def test_generates_suggestions_for_silent_completion(self):
        """Should generate suggestions for silent_completion failure mode."""
        handler = RecoveryGuidanceHandler()
        suggestions = handler.generate_recovery_suggestions(
            failure_type="silent_completion",
            context={"step_file": "steps/01-01.json"},
        )

        assert suggestions is not None
        assert isinstance(suggestions, list)
        assert len(suggestions) > 0

    def test_generates_suggestions_for_timeout_failure(self):
        """Should generate suggestions for timeout_failure failure mode."""
        handler = RecoveryGuidanceHandler()
        suggestions = handler.generate_recovery_suggestions(
            failure_type="timeout_failure",
            context={
                "phase": "GREEN",
                "configured_timeout_minutes": 30,
                "actual_runtime_minutes": 35,
            },
        )

        assert suggestions is not None
        assert isinstance(suggestions, list)
        assert len(suggestions) > 0

    def test_generates_suggestions_for_agent_crash(self):
        """Should generate suggestions for agent_crash failure mode."""
        handler = RecoveryGuidanceHandler()
        suggestions = handler.generate_recovery_suggestions(
            failure_type="agent_crash",
            context={
                "phase": "RED_UNIT",
                "transcript_path": "/tmp/transcript.log",
            },
        )

        assert suggestions is not None
        assert isinstance(suggestions, list)
        assert len(suggestions) > 0

    def test_suggestion_format_includes_why_how_actionable(self):
        """Each suggestion should include WHY, HOW, and ACTION sections."""
        handler = RecoveryGuidanceHandler()
        suggestions = handler.generate_recovery_suggestions(
            failure_type="abandoned_phase",
            context={"phase": "GREEN"},
        )

        # Check that suggestions have WHY/HOW/ACTION structure
        for suggestion in suggestions:
            assert "WHY:" in suggestion
            assert "HOW:" in suggestion
            assert "ACTION:" in suggestion

    def test_context_parameter_affects_suggestion_content(self):
        """Context parameters should be substituted into suggestions."""
        handler = RecoveryGuidanceHandler()

        # Generate with one phase
        suggestions_green = handler.generate_recovery_suggestions(
            failure_type="abandoned_phase",
            context={"phase": "GREEN"},
        )

        # Generate with different phase
        suggestions_red = handler.generate_recovery_suggestions(
            failure_type="abandoned_phase",
            context={"phase": "RED_UNIT"},
        )

        # Suggestions should differ based on context
        green_text = " ".join(suggestions_green)
        red_text = " ".join(suggestions_red)

        assert "GREEN" in green_text
        assert "RED_UNIT" in red_text

    def test_returns_list_of_strings(self):
        """generate_recovery_suggestions should return list of strings."""
        handler = RecoveryGuidanceHandler()
        suggestions = handler.generate_recovery_suggestions(
            failure_type="abandoned_phase",
            context={"phase": "PREPARE"},
        )

        assert isinstance(suggestions, list)
        assert all(isinstance(s, str) for s in suggestions)

    def test_handles_unknown_failure_type(self):
        """Should return helpful message for unknown failure type."""
        handler = RecoveryGuidanceHandler()
        suggestions = handler.generate_recovery_suggestions(
            failure_type="unknown_failure_mode",
            context={},
        )

        assert suggestions is not None
        assert isinstance(suggestions, list)
        assert len(suggestions) > 0
        assert "unknown" in suggestions[0].lower()

    def test_suggestions_contain_actionable_elements(self):
        """Suggestions should contain actionable commands or paths."""
        handler = RecoveryGuidanceHandler()
        suggestions = handler.generate_recovery_suggestions(
            failure_type="abandoned_phase",
            context={
                "phase": "GREEN",
                "step_file": "steps/01-01.json",
                "transcript_path": "/tmp/transcript.log",
            },
        )

        # At least some suggestions should contain commands or paths
        combined = " ".join(suggestions)
        has_actionable = any(
            pattern in combined
            for pattern in [
                "/nw:execute",
                "steps/",
                "transcript",
                "NOT_EXECUTED",
                "path",
            ]
        )
        assert has_actionable, "Suggestions should contain actionable elements"


class TestFormatSuggestion:
    """Tests for format_suggestion method."""

    def test_format_suggestion_combines_why_how_actionable(self):
        """format_suggestion should combine WHY, HOW, and ACTION."""
        handler = RecoveryGuidanceHandler()
        formatted = handler.format_suggestion(
            why_text="Phase is stuck in IN_PROGRESS state",
            how_text="Reset to NOT_EXECUTED to retry",
            actionable_command="Update step file status field",
        )

        assert formatted is not None
        assert isinstance(formatted, str)
        assert "WHY:" in formatted
        assert "HOW:" in formatted
        assert "ACTION:" in formatted
        assert "Phase is stuck" in formatted
        assert "Reset to NOT_EXECUTED" in formatted
        assert "Update step file" in formatted

    def test_format_suggestion_structure_is_readable(self):
        """Formatted suggestion should have proper structure with newlines."""
        handler = RecoveryGuidanceHandler()
        formatted = handler.format_suggestion(
            why_text="Test reason",
            how_text="Test solution",
            actionable_command="Test action",
        )

        # Should have WHY, HOW, ACTION sections separated
        assert "WHY:" in formatted
        assert "\n\nHOW:" in formatted
        assert "\n\nACTION:" in formatted


class TestHandleFailure:
    """Tests for handle_failure method."""

    def test_handle_failure_persists_to_step_file(self, tmp_path):
        """handle_failure should persist suggestions to step file."""
        # Arrange: Create a test step file
        step_file = tmp_path / "step.json"
        step_data = {
            "state": {},
            "tdd_cycle": {"phase_execution_log": []},
        }
        step_file.write_text(json.dumps(step_data))

        # Act: Handle a failure
        handler = RecoveryGuidanceHandler()
        updated_state = handler.handle_failure(
            step_file_path=str(step_file),
            failure_type="abandoned_phase",
            context={"phase": "GREEN"},
        )

        # Assert: Suggestions added to state
        assert "recovery_suggestions" in updated_state
        assert isinstance(updated_state["recovery_suggestions"], list)
        assert len(updated_state["recovery_suggestions"]) > 0

        # Assert: File persisted
        persisted_data = json.loads(step_file.read_text())
        assert "recovery_suggestions" in persisted_data["state"]
        assert isinstance(persisted_data["state"]["recovery_suggestions"], list)

    def test_handle_failure_includes_failure_reason_in_context(self, tmp_path):
        """handle_failure should include failure_reason if provided."""
        # Arrange
        step_file = tmp_path / "step.json"
        step_data = {"state": {}}
        step_file.write_text(json.dumps(step_data))

        # Act
        handler = RecoveryGuidanceHandler()
        updated_state = handler.handle_failure(
            step_file_path=str(step_file),
            failure_type="abandoned_phase",
            context={
                "phase": "GREEN",
                "failure_reason": "Agent crashed unexpectedly",
            },
        )

        # Assert: failure_reason included in state
        assert "failure_reason" in updated_state
        assert "crashed" in updated_state["failure_reason"]

    def test_handle_failure_creates_state_if_missing(self, tmp_path):
        """handle_failure should create state object if missing."""
        # Arrange: Step file without state
        step_file = tmp_path / "step.json"
        step_data = {"tdd_cycle": {}}
        step_file.write_text(json.dumps(step_data))

        # Act
        handler = RecoveryGuidanceHandler()
        updated_state = handler.handle_failure(
            step_file_path=str(step_file),
            failure_type="abandoned_phase",
            context={"phase": "GREEN"},
        )

        # Assert: State created and populated
        assert updated_state is not None
        assert "recovery_suggestions" in updated_state

    def test_handle_failure_returns_updated_state(self, tmp_path):
        """handle_failure should return the updated state dict."""
        # Arrange
        step_file = tmp_path / "step.json"
        step_data = {"state": {"status": "FAILED"}}
        step_file.write_text(json.dumps(step_data))

        # Act
        handler = RecoveryGuidanceHandler()
        result = handler.handle_failure(
            step_file_path=str(step_file),
            failure_type="abandoned_phase",
            context={"phase": "GREEN"},
        )

        # Assert: Returns dict with recovery_suggestions
        assert isinstance(result, dict)
        assert "recovery_suggestions" in result
        assert "status" in result  # Original fields preserved


class TestSuggestionFormatter:
    """Tests for SuggestionFormatter utility class."""

    def test_suggestion_formatter_formats_suggestion(self):
        """SuggestionFormatter should format suggestions correctly."""
        formatter = SuggestionFormatter()
        formatted = formatter.format_suggestion(
            why_text="Phase incomplete",
            how_text="Reset phase status",
            actionable_command="Update JSON file",
        )

        assert "WHY:" in formatted
        assert "HOW:" in formatted
        assert "ACTION:" in formatted
        assert "Phase incomplete" in formatted


class TestRecoveryGuidanceErrorHandling:
    """Tests for error handling in RecoveryGuidanceHandler."""

    def test_handles_missing_context_fields_gracefully(self):
        """Should handle missing context fields with defaults."""
        handler = RecoveryGuidanceHandler()
        suggestions = handler.generate_recovery_suggestions(
            failure_type="abandoned_phase",
            context={},  # Missing required phase field
        )

        assert suggestions is not None
        assert isinstance(suggestions, list)
        assert len(suggestions) > 0
        # Should contain placeholder text since phase is missing
        assert "UNKNOWN_PHASE" in " ".join(suggestions)

    def test_handles_extra_context_fields(self):
        """Should handle extra context fields without error."""
        handler = RecoveryGuidanceHandler()
        suggestions = handler.generate_recovery_suggestions(
            failure_type="abandoned_phase",
            context={
                "phase": "GREEN",
                "extra_field_1": "value1",
                "extra_field_2": "value2",
            },
        )

        assert suggestions is not None
        assert isinstance(suggestions, list)
        assert len(suggestions) > 0
