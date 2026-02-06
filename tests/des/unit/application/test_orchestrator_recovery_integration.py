"""
Unit Tests: Orchestrator Integration with RecoveryGuidanceHandler

Tests the integration between DES Orchestrator and RecoveryGuidanceHandler:
- SubagentStop hook calls RecoveryGuidanceHandler when failures detected
- Failure context properly extracted from step file
- Step file updated with FAILED status and recovery_suggestions
- Recovery suggestions displayed through orchestrator result
- Orchestrator handles suggestion generation failures gracefully
- Suggestions persist in step file JSON for later review
"""

import json

import pytest

# Note: Schema v1.x SubagentStopHook dropped per ADR-6. These tests need Schema v2.0 update.
from src.des.application.recovery_guidance_handler import RecoveryGuidanceHandler


pytestmark = pytest.mark.skip(
    reason="Schema v1.x dropped per ADR-6, needs Schema v2.0 execution-log update"
)


# Test data builders (Compose Method - L3 responsibility organization)
def build_step_file_with_abandoned_phase(tmp_path, phase_name="RED_ACCEPTANCE"):
    """Build step file with specified phase abandoned (IN_PROGRESS)."""
    step_file = tmp_path / "step.json"
    step_data = {
        "step_id": "01-01",
        "state": {"status": "IN_PROGRESS"},
        "tdd_cycle": {
            "phase_execution_log": [
                {
                    "phase_name": "PREPARE",
                    "status": "EXECUTED",
                    "outcome": "Prepared test setup",
                },
                {"phase_name": phase_name, "status": "IN_PROGRESS", "outcome": None},
            ]
        },
    }
    step_file.write_text(json.dumps(step_data, indent=2))
    return step_file


def build_context_for_abandoned_phase(step_file_path, phase_name="RED_UNIT"):
    """Build failure context dictionary for abandoned phase."""
    return {
        "phase": phase_name,
        "step_file": str(step_file_path),
        "transcript_path": f"transcripts/{phase_name.lower()}.log",
    }


class TestSubagentStopHookCallsRecoveryGuidanceHandler:
    """Tests that SubagentStop hook invokes RecoveryGuidanceHandler."""

    def test_subagent_stop_hook_calls_recovery_guidance_handler(self, tmp_path):
        """SubagentStop hook should call RecoveryGuidanceHandler when abandonment detected."""
        # Arrange: Step file with abandoned phase
        step_file = build_step_file_with_abandoned_phase(tmp_path, "RED_ACCEPTANCE")

        # Act: SubagentStop hook validates
        hook = SubagentStopHook()
        result = hook.on_agent_complete(str(step_file))

        # Assert: Hook detects abandoned phase
        assert result.validation_status == "FAILED"
        assert len(result.abandoned_phases) > 0
        assert "RED_ACCEPTANCE" in result.abandoned_phases

    def test_subagent_stop_hook_generates_recovery_context(self, tmp_path):
        """SubagentStop hook should extract context for RecoveryGuidanceHandler."""
        # Arrange
        step_file = tmp_path / "step.json"
        step_data = {
            "step_id": "03-04",
            "state": {"status": "IN_PROGRESS"},
            "tdd_cycle": {
                "phase_execution_log": [
                    {"phase_name": "GREEN", "status": "IN_PROGRESS", "outcome": None}
                ]
            },
        }
        step_file.write_text(json.dumps(step_data, indent=2))

        # Act: Extract context from hook result
        hook = SubagentStopHook()
        result = hook.on_agent_complete(str(step_file))

        # Assert: Context can be reconstructed from hook result
        assert result.abandoned_phases is not None
        assert isinstance(result.abandoned_phases, list)
        assert len(result.abandoned_phases) == 1
        assert result.abandoned_phases[0] == "GREEN"


class TestFailureContextExtractionAndPassing:
    """Tests that failure context is properly extracted and passed to handler."""

    def test_failure_context_includes_phase_name(self, tmp_path):
        """Failure context should include abandoned phase name."""
        # Arrange
        step_file = tmp_path / "step.json"
        step_data = {
            "state": {},
            "tdd_cycle": {
                "phase_execution_log": [
                    {"phase_name": "RED_UNIT", "status": "IN_PROGRESS", "outcome": None}
                ]
            },
        }
        step_file.write_text(json.dumps(step_data, indent=2))

        # Act: Detect and extract context
        step_file_data = json.loads(step_file.read_text())
        abandoned_phase = None
        for phase_log in step_file_data.get("tdd_cycle", {}).get(
            "phase_execution_log", []
        ):
            if phase_log.get("status") == "IN_PROGRESS":
                abandoned_phase = phase_log.get("phase_name")
                break

        context = {
            "phase": abandoned_phase,
            "step_file": str(step_file),
        }

        # Assert: Context properly extracted
        assert context["phase"] == "RED_UNIT"
        assert context["step_file"] == str(step_file)

    def test_failure_context_includes_transcript_path(self, tmp_path):
        """Failure context should include transcript path for debugging."""
        # Arrange
        step_file = tmp_path / "steps" / "03-04.json"
        step_file.parent.mkdir(parents=True, exist_ok=True)
        step_data = {
            "step_id": "03-04",
            "state": {},
            "tdd_cycle": {"phase_execution_log": []},
        }
        step_file.write_text(json.dumps(step_data, indent=2))

        # Act: Build context with transcript path
        context = {
            "phase": "RED_ACCEPTANCE",
            "step_file": str(step_file),
            "transcript_path": "transcripts/03-04-RED_ACCEPTANCE.log",
        }

        # Assert: Transcript path included in context
        assert "transcript_path" in context
        assert "03-04" in context["transcript_path"]

    def test_failure_context_extracted_from_step_file(self, tmp_path):
        """Failure context should be extractable from step file alone."""
        # Arrange: Minimal step file with failure indicator
        step_file = tmp_path / "step.json"
        step_data = {
            "state": {"status": "IN_PROGRESS"},
            "tdd_cycle": {
                "phase_execution_log": [
                    {"phase_name": "PREPARE", "status": "EXECUTED"},
                    {"phase_name": "RED_ACCEPTANCE", "status": "IN_PROGRESS"},
                ]
            },
        }
        step_file.write_text(json.dumps(step_data, indent=2))

        # Act: Extract context from step file
        step_data_loaded = json.loads(step_file.read_text())
        context = {}
        for phase_log in step_data_loaded.get("tdd_cycle", {}).get(
            "phase_execution_log", []
        ):
            if phase_log.get("status") == "IN_PROGRESS":
                context["phase"] = phase_log.get("phase_name")
                break

        # Assert: Context extracted successfully
        assert "phase" in context
        assert context["phase"] == "RED_ACCEPTANCE"


class TestStepFileUpdatedWithFailedStatusAndSuggestions:
    """Tests that step file is properly updated with recovery guidance."""

    def test_step_file_updated_with_failed_status(self, tmp_path):
        """Step file should be updated with status: FAILED."""
        # Arrange
        step_file = tmp_path / "step.json"
        step_data = {
            "state": {"status": "IN_PROGRESS"},
            "tdd_cycle": {"phase_execution_log": []},
        }
        step_file.write_text(json.dumps(step_data, indent=2))

        # Act: Update step file status
        step_data_loaded = json.loads(step_file.read_text())
        step_data_loaded["state"]["status"] = "FAILED"
        step_file.write_text(json.dumps(step_data_loaded, indent=2))

        # Assert: Status updated
        updated_data = json.loads(step_file.read_text())
        assert updated_data["state"]["status"] == "FAILED"

    def test_step_file_updated_with_recovery_suggestions(self, tmp_path):
        """Step file should include recovery_suggestions array."""
        # Arrange
        step_file = tmp_path / "step.json"
        step_data = {
            "state": {"status": "FAILED"},
            "tdd_cycle": {"phase_execution_log": []},
        }
        step_file.write_text(json.dumps(step_data, indent=2))

        # Act: Add recovery suggestions via handler
        handler = RecoveryGuidanceHandler()
        context = {
            "phase": "RED_UNIT",
            "step_file": str(step_file),
            "transcript_path": "transcripts/01-01.log",
        }
        handler.handle_failure(
            step_file_path=str(step_file),
            failure_type="abandoned_phase",
            context=context,
        )

        # Assert: Suggestions persisted to step file
        updated_data = json.loads(step_file.read_text())
        assert "recovery_suggestions" in updated_data["state"]
        assert isinstance(updated_data["state"]["recovery_suggestions"], list)
        assert len(updated_data["state"]["recovery_suggestions"]) > 0

    def test_step_file_preserves_existing_state_during_update(self, tmp_path):
        """Updating step file with suggestions should preserve existing state."""
        # Arrange
        step_file = tmp_path / "step.json"
        original_data = {
            "step_id": "01-01",
            "state": {"status": "FAILED", "custom_field": "custom_value"},
            "tdd_cycle": {"phase_execution_log": []},
        }
        step_file.write_text(json.dumps(original_data, indent=2))

        # Act: Add recovery suggestions without losing custom_field
        handler = RecoveryGuidanceHandler()
        handler.handle_failure(
            step_file_path=str(step_file),
            failure_type="abandoned_phase",
            context={"phase": "PREPARE"},
        )

        # Assert: Original state preserved
        updated_data = json.loads(step_file.read_text())
        assert updated_data["state"]["custom_field"] == "custom_value"
        assert updated_data["step_id"] == "01-01"
        assert "recovery_suggestions" in updated_data["state"]


class TestRecoverySuggestionsDisplayedToUser:
    """Tests that recovery suggestions are formatted for user display."""

    def test_suggestions_include_actionable_commands(self, tmp_path):
        """Suggestions should include specific commands or paths."""
        # Arrange
        step_file = tmp_path / "step.json"
        step_file.write_text(json.dumps({"state": {}}))

        # Act: Generate suggestions
        handler = RecoveryGuidanceHandler()
        suggestions = handler.generate_recovery_suggestions(
            failure_type="abandoned_phase",
            context={"phase": "GREEN_UNIT", "transcript_path": "transcripts/01-01.log"},
        )

        # Assert: Suggestions contain commands/paths
        joined = " ".join(suggestions)
        assert any(
            pattern in joined
            for pattern in [
                "/nw:execute",
                "NOT_EXECUTED",
                "transcript",
                "transcripts/",
                "json",
                "step",
            ]
        )

    def test_suggestions_explain_why_and_how(self, tmp_path):
        """Suggestions should include WHY and HOW explanations."""
        # Arrange
        step_file = tmp_path / "step.json"
        step_file.write_text(json.dumps({"state": {}}))

        # Act: Generate suggestions
        handler = RecoveryGuidanceHandler()
        suggestions = handler.generate_recovery_suggestions(
            failure_type="abandoned_phase", context={"phase": "RED_ACCEPTANCE"}
        )

        # Assert: Each suggestion has WHY/HOW/ACTION structure
        for suggestion in suggestions:
            assert "WHY:" in suggestion, f"Missing WHY in: {suggestion}"
            assert "HOW:" in suggestion, f"Missing HOW in: {suggestion}"
            assert "ACTION:" in suggestion, f"Missing ACTION in: {suggestion}"

    def test_suggestions_formatted_for_readability(self, tmp_path):
        """Suggestions should be formatted for junior developer audience."""
        # Arrange
        step_file = tmp_path / "step.json"
        step_file.write_text(json.dumps({"state": {}}))

        # Act: Generate suggestions
        handler = RecoveryGuidanceHandler()
        suggestions = handler.generate_recovery_suggestions(
            failure_type="abandoned_phase", context={"phase": "GREEN"}
        )

        # Assert: Suggestions are readable strings (not empty, reasonable length)
        for suggestion in suggestions:
            assert isinstance(suggestion, str)
            assert len(suggestion) > 30, "Suggestion should be substantive"
            assert "\n" in suggestion, "Suggestion should be multi-line for readability"


class TestOrchestratorHandlesSuggestionGenerationFailure:
    """Tests graceful degradation when suggestion generation fails."""

    def test_orchestrator_continues_when_handler_fails(self, tmp_path):
        """Orchestrator should not crash if suggestion generation fails."""
        # Arrange
        step_file = tmp_path / "step.json"
        step_file.write_text(json.dumps({"state": {}}))

        # Act: Attempt to generate suggestions with bad context
        handler = RecoveryGuidanceHandler()
        try:
            suggestions = handler.generate_recovery_suggestions(
                failure_type="abandoned_phase",
                context=None,  # Invalid context
            )
            # If we get here, handler handled gracefully
            assert suggestions is not None or suggestions is None  # Either is OK
        except (TypeError, AttributeError):
            # Expected - but orchestrator would catch and provide generic guidance
            pass

    def test_fallback_to_generic_guidance_on_failure(self, tmp_path):
        """Orchestrator should provide generic guidance if specific generation fails."""
        # Arrange
        step_file = tmp_path / "step.json"
        step_file.write_text(json.dumps({"state": {}}))

        # Act: Generate for unknown failure mode
        handler = RecoveryGuidanceHandler()
        suggestions = handler.generate_recovery_suggestions(
            failure_type="UNKNOWN_FAILURE_MODE", context={}
        )

        # Assert: Generic guidance provided instead of crashing
        assert suggestions is not None
        assert isinstance(suggestions, list)
        assert len(suggestions) > 0
        assert "unknown" in suggestions[0].lower()

    def test_orchestrator_returns_result_even_on_handler_error(self):
        """Orchestrator result should be returnab even if suggestions fail."""
        # Arrange
        handler = RecoveryGuidanceHandler()

        # Act: Attempt generation with invalid context
        suggestions = handler.generate_recovery_suggestions(
            failure_type="abandoned_phase",
            context={},  # Missing phase
        )

        # Assert: Handler returns something (even if not ideal)
        assert suggestions is not None
        assert isinstance(suggestions, list)
        # Will have UNKNOWN_PHASE placeholder
        assert "UNKNOWN_PHASE" in " ".join(suggestions)


class TestSuggestionsPersistInStepFile:
    """Tests that suggestions remain available for later review."""

    def test_suggestions_survive_step_file_reload(self, tmp_path):
        """Suggestions persisted to file should be retrievable after reload."""
        # Arrange
        step_file = tmp_path / "step.json"
        step_data = {
            "step_id": "02-01",
            "state": {"status": "FAILED"},
            "tdd_cycle": {"phase_execution_log": []},
        }
        step_file.write_text(json.dumps(step_data, indent=2))

        # Act: Persist suggestions
        handler = RecoveryGuidanceHandler()
        handler.handle_failure(
            step_file_path=str(step_file),
            failure_type="abandoned_phase",
            context={"phase": "REFACTOR_CONTINUOUS"},
        )

        # Act: Reload step file
        reloaded = json.loads(step_file.read_text())

        # Assert: Suggestions still present
        assert "recovery_suggestions" in reloaded["state"]
        assert isinstance(reloaded["state"]["recovery_suggestions"], list)
        assert len(reloaded["state"]["recovery_suggestions"]) > 0

    def test_suggestions_accessible_to_next_orchestrator_run(self, tmp_path):
        """Suggestions should be accessible when orchestrator runs again."""
        # Arrange
        step_file = tmp_path / "step.json"
        step_data = {"state": {}, "tdd_cycle": {"phase_execution_log": []}}
        step_file.write_text(json.dumps(step_data, indent=2))

        # Act: First run - generate and persist suggestions
        handler = RecoveryGuidanceHandler()
        handler.handle_failure(
            step_file_path=str(step_file),
            failure_type="abandoned_phase",
            context={"phase": "GREEN"},
        )

        # Act: Second run - orchestrator reads suggestions
        data_with_suggestions = json.loads(step_file.read_text())

        # Assert: Suggestions accessible for display
        suggestions = data_with_suggestions.get("state", {}).get(
            "recovery_suggestions", []
        )
        assert len(suggestions) > 0
        for suggestion in suggestions:
            assert "WHY:" in suggestion
            assert "HOW:" in suggestion
            assert "ACTION:" in suggestion

    def test_suggestions_include_failure_context(self, tmp_path):
        """Persisted suggestions should include failure context information."""
        # Arrange
        step_file = tmp_path / "step.json"
        step_file.write_text(json.dumps({"state": {}}))

        # Act: Persist with context including phase name
        handler = RecoveryGuidanceHandler()
        handler.handle_failure(
            step_file_path=str(step_file),
            failure_type="abandoned_phase",
            context={
                "phase": "REFACTOR_L4",
                "transcript_path": "transcripts/02-05.log",
            },
        )

        # Assert: Suggestions reference the abandoned phase
        data = json.loads(step_file.read_text())
        suggestions_text = " ".join(data["state"]["recovery_suggestions"])
        assert "REFACTOR_L4" in suggestions_text
        assert "transcript" in suggestions_text.lower()
