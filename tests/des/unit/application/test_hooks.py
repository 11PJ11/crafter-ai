"""Unit tests for des.hooks module - SubagentStopHook class."""

import json
from pathlib import Path


class TestSubagentStopHookClass:
    """Tests for SubagentStopHook class existence and basic structure."""

    def test_subagent_stop_hook_class_exists(self):
        """Hook class should be importable from src.des.hooks module."""
        from src.des.application.hooks import SubagentStopHook

        assert SubagentStopHook is not None
        assert hasattr(SubagentStopHook, "__init__")

    def test_subagent_stop_hook_on_agent_complete_method_exists(self):
        """Hook should have on_agent_complete method."""
        from src.des.application.hooks import SubagentStopHook

        hook = SubagentStopHook()
        assert hasattr(hook, "on_agent_complete")
        assert callable(hook.on_agent_complete)

    def test_on_agent_complete_accepts_step_file_path(self):
        """on_agent_complete should accept step_file_path parameter."""
        from src.des.application.hooks import SubagentStopHook

        hook = SubagentStopHook()

        # Create a temporary step file for testing
        step_data = {
            "task_id": "01-01",
            "state": {"status": "DONE"},
            "tdd_cycle": {"phase_execution_log": []},
        }

        import tempfile

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(step_data, f)
            temp_path = f.name

        try:
            result = hook.on_agent_complete(step_file_path=temp_path)
            assert result is not None
        finally:
            Path(temp_path).unlink()

    def test_on_agent_complete_returns_hook_result(self):
        """on_agent_complete should return HookResult object."""
        from src.des.application.hooks import SubagentStopHook, HookResult

        hook = SubagentStopHook()

        step_data = {
            "task_id": "01-01",
            "state": {"status": "DONE"},
            "tdd_cycle": {"phase_execution_log": []},
        }

        import tempfile

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(step_data, f)
            temp_path = f.name

        try:
            result = hook.on_agent_complete(step_file_path=temp_path)
            assert isinstance(result, HookResult)
        finally:
            Path(temp_path).unlink()

    def test_hook_result_has_hook_fired_field(self):
        """HookResult should have hook_fired field."""
        from src.des.application.hooks import HookResult

        result = HookResult(validation_status="PASSED")
        assert hasattr(result, "hook_fired")
        assert result.hook_fired is True

    def test_hook_result_has_validation_status_field(self):
        """HookResult should have validation_status field."""
        from src.des.application.hooks import HookResult

        result = HookResult(validation_status="PASSED")
        assert hasattr(result, "validation_status")
        assert result.validation_status == "PASSED"

    def test_hook_result_has_required_fields(self):
        """HookResult should have all required validation fields."""
        from src.des.application.hooks import HookResult

        result = HookResult(validation_status="PASSED")

        # Verify all expected fields exist
        required_fields = [
            "validation_status",
            "hook_fired",
            "abandoned_phases",
            "incomplete_phases",
            "invalid_skips",
            "error_count",
            "error_type",
            "error_message",
            "recovery_suggestions",
        ]

        for field in required_fields:
            assert hasattr(result, field), f"HookResult missing field: {field}"

    def test_on_agent_complete_returns_true_hook_fired(self):
        """on_agent_complete should return result with hook_fired=True."""
        from src.des.application.hooks import SubagentStopHook

        hook = SubagentStopHook()

        step_data = {
            "task_id": "01-01",
            "state": {"status": "DONE"},
            "tdd_cycle": {"phase_execution_log": []},
        }

        import tempfile

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(step_data, f)
            temp_path = f.name

        try:
            result = hook.on_agent_complete(step_file_path=temp_path)
            assert result.hook_fired is True
        finally:
            Path(temp_path).unlink()


class TestAbandonedPhaseDetection:
    """Tests for detecting abandoned IN_PROGRESS phases."""

    def test_detects_in_progress_phase_as_abandoned(self):
        """Hook should detect phases with IN_PROGRESS status as abandoned."""
        from src.des.application.hooks import SubagentStopHook

        hook = SubagentStopHook()

        # Create step file with GREEN_UNIT left IN_PROGRESS
        step_data = {
            "task_id": "01-01",
            "project_id": "test-project",
            "state": {"status": "IN_PROGRESS"},
            "tdd_cycle": {
                "phase_execution_log": [
                    {
                        "phase_number": 0,
                        "phase_name": "PREPARE",
                        "status": "EXECUTED",
                        "outcome": "PASS",
                    },
                    {
                        "phase_number": 1,
                        "phase_name": "RED_ACCEPTANCE",
                        "status": "EXECUTED",
                        "outcome": "PASS",
                    },
                    {
                        "phase_number": 2,
                        "phase_name": "RED_UNIT",
                        "status": "EXECUTED",
                        "outcome": "PASS",
                    },
                    {
                        "phase_number": 3,
                        "phase_name": "GREEN_UNIT",
                        "status": "IN_PROGRESS",  # Abandoned phase
                        "outcome": None,
                    },
                ]
            },
        }

        import tempfile

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(step_data, f)
            temp_path = f.name

        try:
            result = hook.on_agent_complete(step_file_path=temp_path)
            assert result.validation_status == "FAILED"
            assert "GREEN_UNIT" in result.abandoned_phases
            assert result.error_message is not None
            assert (
                "Phase GREEN_UNIT left IN_PROGRESS (abandoned)" in result.error_message
            )
        finally:
            Path(temp_path).unlink()


class TestSilentCompletionDetection:
    """Tests for detecting silent completion (all phases NOT_EXECUTED)."""

    def test_hook_result_has_not_executed_phases_field(self):
        """HookResult should have not_executed_phases field for diagnostics."""
        from src.des.application.hooks import HookResult

        result = HookResult(validation_status="PASSED")
        assert hasattr(result, "not_executed_phases")

    def test_not_executed_phases_field_is_integer(self):
        """not_executed_phases should be an integer count."""
        from src.des.application.hooks import HookResult

        result = HookResult(validation_status="PASSED", not_executed_phases=14)
        assert isinstance(result.not_executed_phases, int)
        assert result.not_executed_phases == 14

    def test_detects_all_phases_not_executed_as_silent_completion(self):
        """Hook should detect when all 14 phases are NOT_EXECUTED as SILENT_COMPLETION."""
        from src.des.application.hooks import SubagentStopHook

        hook = SubagentStopHook()

        # Create step file where task is IN_PROGRESS but ALL phases NOT_EXECUTED
        step_data = {
            "task_id": "01-03",
            "project_id": "test-project",
            "state": {"status": "IN_PROGRESS"},  # Task marked as started
            "tdd_cycle": {
                "phase_execution_log": [
                    {"phase_number": i, "phase_name": phase, "status": "NOT_EXECUTED"}
                    for i, phase in enumerate(
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

        import tempfile

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(step_data, f)
            temp_path = f.name

        try:
            result = hook.on_agent_complete(step_file_path=temp_path)
            assert result.validation_status == "FAILED"
            assert result.error_type == "SILENT_COMPLETION"
            assert result.not_executed_phases == 14
        finally:
            Path(temp_path).unlink()

    def test_silent_completion_error_message_includes_diagnostic(self):
        """Silent completion error message should mention agent completed without updating."""
        from src.des.application.hooks import SubagentStopHook

        hook = SubagentStopHook()

        step_data = {
            "task_id": "01-03",
            "state": {"status": "IN_PROGRESS"},
            "tdd_cycle": {
                "phase_execution_log": [
                    {
                        "phase_number": i,
                        "phase_name": f"PHASE_{i}",
                        "status": "NOT_EXECUTED",
                    }
                    for i in range(14)
                ]
            },
        }

        import tempfile

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(step_data, f)
            temp_path = f.name

        try:
            result = hook.on_agent_complete(step_file_path=temp_path)
            assert "Agent completed without updating step file" in result.error_message
        finally:
            Path(temp_path).unlink()

    def test_no_silent_completion_when_some_phases_executed(self):
        """Hook should NOT flag silent completion if at least one phase was executed."""
        from src.des.application.hooks import SubagentStopHook

        hook = SubagentStopHook()

        # Task with PREPARE executed but rest NOT_EXECUTED - not silent completion
        step_data = {
            "task_id": "01-03",
            "state": {"status": "IN_PROGRESS"},
            "tdd_cycle": {
                "phase_execution_log": [
                    {
                        "phase_number": 0,
                        "phase_name": "PREPARE",
                        "status": "EXECUTED",
                        "outcome": "PASS",
                    },
                    *[
                        {
                            "phase_number": i,
                            "phase_name": f"PHASE_{i}",
                            "status": "NOT_EXECUTED",
                        }
                        for i in range(1, 14)
                    ],
                ]
            },
        }

        import tempfile

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(step_data, f)
            temp_path = f.name

        try:
            result = hook.on_agent_complete(step_file_path=temp_path)
            # Should pass - not silent completion if any phase was executed
            assert result.validation_status == "PASSED"
        finally:
            Path(temp_path).unlink()

    def test_no_silent_completion_when_task_status_done(self):
        """Hook should NOT flag silent completion if task status is DONE (even if phases NOT_EXECUTED)."""
        from src.des.application.hooks import SubagentStopHook

        hook = SubagentStopHook()

        # Task DONE with all phases NOT_EXECUTED - edge case, but not silent completion
        step_data = {
            "task_id": "01-03",
            "state": {"status": "DONE"},  # Task completed normally
            "tdd_cycle": {
                "phase_execution_log": [
                    {
                        "phase_number": i,
                        "phase_name": f"PHASE_{i}",
                        "status": "NOT_EXECUTED",
                    }
                    for i in range(14)
                ]
            },
        }

        import tempfile

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(step_data, f)
            temp_path = f.name

        try:
            result = hook.on_agent_complete(step_file_path=temp_path)
            # Silent completion only applies when task is IN_PROGRESS
            assert result.error_type != "SILENT_COMPLETION"
        finally:
            Path(temp_path).unlink()


class TestMissingOutcomeDetection:
    """Tests for detecting EXECUTED phases without outcome field."""

    def test_detects_executed_phase_without_outcome(self):
        """Hook should detect phases with EXECUTED status but no outcome."""
        from src.des.application.hooks import SubagentStopHook

        hook = SubagentStopHook()

        # Create step file with REFACTOR_L1 marked EXECUTED but missing outcome
        step_data = {
            "task_id": "01-04",
            "project_id": "test-project",
            "state": {"status": "IN_PROGRESS"},
            "tdd_cycle": {
                "phase_execution_log": [
                    {
                        "phase_number": 0,
                        "phase_name": "PREPARE",
                        "status": "EXECUTED",
                        "outcome": "PASS",
                    },
                    {
                        "phase_number": 7,
                        "phase_name": "REFACTOR_L1",
                        "status": "EXECUTED",
                        "outcome": None,  # Missing outcome!
                    },
                ]
            },
        }

        import tempfile

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(step_data, f)
            temp_path = f.name

        try:
            result = hook.on_agent_complete(step_file_path=temp_path)
            assert result.validation_status == "FAILED"
            assert "REFACTOR_L1" in result.incomplete_phases
            assert result.error_type == "MISSING_OUTCOME"
            assert (
                "Phase REFACTOR_L1 marked EXECUTED but missing outcome"
                in result.error_message
            )
        finally:
            Path(temp_path).unlink()


class TestInvalidSkipDetection:
    """Tests for detecting SKIPPED phases without blocked_by reason."""

    def test_detects_skipped_phase_without_blocked_by(self):
        """Hook should detect phases with SKIPPED status but no blocked_by reason."""
        from src.des.application.hooks import SubagentStopHook

        hook = SubagentStopHook()

        # Create step file with REFACTOR_L3 marked SKIPPED but missing blocked_by
        step_data = {
            "task_id": "01-05",
            "project_id": "test-project",
            "state": {"status": "DONE"},
            "tdd_cycle": {
                "phase_execution_log": [
                    {
                        "phase_number": 0,
                        "phase_name": "PREPARE",
                        "status": "EXECUTED",
                        "outcome": "PASS",
                    },
                    {
                        "phase_number": 9,
                        "phase_name": "REFACTOR_L3",
                        "status": "SKIPPED",
                        "outcome": "SKIPPED",
                        "blocked_by": None,  # Missing blocked_by reason!
                    },
                ]
            },
        }

        import tempfile

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(step_data, f)
            temp_path = f.name

        try:
            result = hook.on_agent_complete(step_file_path=temp_path)
            assert result.validation_status == "FAILED"
            assert "REFACTOR_L3" in result.invalid_skips
            assert result.error_type == "INVALID_SKIP"
            assert (
                "Phase REFACTOR_L3 marked SKIPPED but missing blocked_by reason"
                in result.error_message
            )
        finally:
            Path(temp_path).unlink()

    def test_skipped_phase_with_blocked_by_is_valid(self):
        """Hook should NOT flag SKIPPED phases that have blocked_by reason."""
        from src.des.application.hooks import SubagentStopHook

        hook = SubagentStopHook()

        # SKIPPED phase with valid blocked_by reason - should pass
        step_data = {
            "task_id": "01-05",
            "project_id": "test-project",
            "state": {"status": "DONE"},
            "tdd_cycle": {
                "phase_execution_log": [
                    {
                        "phase_number": 9,
                        "phase_name": "REFACTOR_L3",
                        "status": "SKIPPED",
                        "outcome": "SKIPPED",
                        "blocked_by": "No L3 complexity found - all methods single responsibility",
                    },
                ]
            },
        }

        import tempfile

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(step_data, f)
            temp_path = f.name

        try:
            result = hook.on_agent_complete(step_file_path=temp_path)
            assert result.validation_status == "PASSED"
            assert result.invalid_skips == []
        finally:
            Path(temp_path).unlink()

    def test_detects_skipped_phase_with_empty_string_blocked_by(self):
        """Hook should detect SKIPPED phases with empty string blocked_by."""
        from src.des.application.hooks import SubagentStopHook

        hook = SubagentStopHook()

        # SKIPPED phase with empty string blocked_by - should fail
        step_data = {
            "task_id": "01-05",
            "project_id": "test-project",
            "state": {"status": "DONE"},
            "tdd_cycle": {
                "phase_execution_log": [
                    {
                        "phase_number": 9,
                        "phase_name": "REFACTOR_L3",
                        "status": "SKIPPED",
                        "outcome": "SKIPPED",
                        "blocked_by": "",  # Empty string is invalid!
                    },
                ]
            },
        }

        import tempfile

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(step_data, f)
            temp_path = f.name

        try:
            result = hook.on_agent_complete(step_file_path=temp_path)
            assert result.validation_status == "FAILED"
            assert "REFACTOR_L3" in result.invalid_skips
            assert result.error_type == "INVALID_SKIP"
        finally:
            Path(temp_path).unlink()


class TestMultipleErrorAggregation:
    """Tests for aggregating multiple validation errors instead of early return."""

    def test_aggregates_abandoned_and_missing_outcome_errors(self):
        """Hook should aggregate multiple error types instead of returning on first error."""
        from src.des.application.hooks import SubagentStopHook

        hook = SubagentStopHook()

        # Create step file with BOTH abandoned phase AND missing outcome
        step_data = {
            "task_id": "01-06",
            "project_id": "des-us003",
            "state": {"status": "IN_PROGRESS"},
            "tdd_cycle": {
                "phase_execution_log": [
                    {
                        "phase_number": 0,
                        "phase_name": "PREPARE",
                        "status": "EXECUTED",
                        "outcome": "PASS",
                    },
                    {
                        "phase_number": 3,
                        "phase_name": "GREEN_UNIT",
                        "status": "IN_PROGRESS",  # Error 1: Abandoned
                        "outcome": None,
                    },
                    {
                        "phase_number": 6,
                        "phase_name": "REVIEW",
                        "status": "EXECUTED",  # Error 2: Missing outcome
                        "outcome": None,
                    },
                ]
            },
        }

        import tempfile

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(step_data, f)
            temp_path = f.name

        try:
            result = hook.on_agent_complete(step_file_path=temp_path)

            # Should detect BOTH errors
            assert result.validation_status == "FAILED"
            assert result.error_count == 2
            assert "GREEN_UNIT" in result.abandoned_phases
            assert "REVIEW" in result.incomplete_phases
        finally:
            Path(temp_path).unlink()

    def test_error_message_describes_all_errors(self):
        """Error message should mention both error types when multiple exist."""
        from src.des.application.hooks import SubagentStopHook

        hook = SubagentStopHook()

        step_data = {
            "task_id": "01-06",
            "state": {"status": "IN_PROGRESS"},
            "tdd_cycle": {
                "phase_execution_log": [
                    {
                        "phase_number": 3,
                        "phase_name": "GREEN_UNIT",
                        "status": "IN_PROGRESS",
                    },
                    {
                        "phase_number": 6,
                        "phase_name": "REVIEW",
                        "status": "EXECUTED",
                        "outcome": None,
                    },
                ]
            },
        }

        import tempfile

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(step_data, f)
            temp_path = f.name

        try:
            result = hook.on_agent_complete(step_file_path=temp_path)

            # Error message should mention multiple errors
            assert (
                "2 validation error" in result.error_message.lower()
                or "multiple" in result.error_message.lower()
            )
        finally:
            Path(temp_path).unlink()


class TestRecoverySuggestionGeneration:
    """Tests for generating actionable recovery suggestions."""

    def test_generates_minimum_three_recovery_suggestions(self):
        """Hook should generate at least 3 recovery suggestions for failures."""
        from src.des.application.hooks import SubagentStopHook

        hook = SubagentStopHook()

        step_data = {
            "task_id": "01-06",
            "state": {"status": "IN_PROGRESS"},
            "tdd_cycle": {
                "phase_execution_log": [
                    {
                        "phase_number": 3,
                        "phase_name": "GREEN_UNIT",
                        "status": "IN_PROGRESS",
                    },
                    {
                        "phase_number": 6,
                        "phase_name": "REVIEW",
                        "status": "EXECUTED",
                        "outcome": None,
                    },
                ]
            },
        }

        import tempfile

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(step_data, f)
            temp_path = f.name

        try:
            result = hook.on_agent_complete(step_file_path=temp_path)

            assert len(result.recovery_suggestions) >= 3
        finally:
            Path(temp_path).unlink()

    def test_suggestions_are_complete_sentences(self):
        """Each suggestion should be at least 20 chars and properly formatted."""
        from src.des.application.hooks import SubagentStopHook

        hook = SubagentStopHook()

        step_data = {
            "task_id": "01-06",
            "state": {"status": "IN_PROGRESS"},
            "tdd_cycle": {
                "phase_execution_log": [
                    {
                        "phase_number": 3,
                        "phase_name": "GREEN_UNIT",
                        "status": "IN_PROGRESS",
                    },
                ]
            },
        }

        import tempfile

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(step_data, f)
            temp_path = f.name

        try:
            result = hook.on_agent_complete(step_file_path=temp_path)

            for suggestion in result.recovery_suggestions:
                assert len(suggestion) >= 20, f"Suggestion too short: {suggestion}"
                assert suggestion[
                    0
                ].isupper(), f"Should start with capital: {suggestion}"
                assert suggestion.rstrip().endswith(
                    (".", "`", '"')
                ), f"Should end properly: {suggestion}"
        finally:
            Path(temp_path).unlink()

    def test_includes_why_explanation(self):
        """At least one suggestion should explain WHY error occurred."""
        from src.des.application.hooks import SubagentStopHook

        hook = SubagentStopHook()

        step_data = {
            "task_id": "01-06",
            "state": {"status": "IN_PROGRESS"},
            "tdd_cycle": {
                "phase_execution_log": [
                    {
                        "phase_number": 3,
                        "phase_name": "GREEN_UNIT",
                        "status": "IN_PROGRESS",
                    },
                ]
            },
        }

        import tempfile

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(step_data, f)
            temp_path = f.name

        try:
            result = hook.on_agent_complete(step_file_path=temp_path)

            why_patterns = [
                "because",
                "since",
                "left in",
                "was not",
                "missing",
                "without",
            ]
            has_why = any(
                any(pattern in suggestion.lower() for pattern in why_patterns)
                for suggestion in result.recovery_suggestions
            )
            assert has_why, "At least one suggestion must explain WHY"
        finally:
            Path(temp_path).unlink()

    def test_includes_how_to_fix(self):
        """At least one suggestion should explain HOW to fix."""
        from src.des.application.hooks import SubagentStopHook

        hook = SubagentStopHook()

        step_data = {
            "task_id": "01-06",
            "state": {"status": "IN_PROGRESS"},
            "tdd_cycle": {
                "phase_execution_log": [
                    {
                        "phase_number": 3,
                        "phase_name": "GREEN_UNIT",
                        "status": "IN_PROGRESS",
                    },
                ]
            },
        }

        import tempfile

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(step_data, f)
            temp_path = f.name

        try:
            result = hook.on_agent_complete(step_file_path=temp_path)

            how_patterns = ["/nw:execute", "run", "reset", "add", "update", "set"]
            has_how = any(
                any(pattern in suggestion.lower() for pattern in how_patterns)
                for suggestion in result.recovery_suggestions
            )
            assert has_how, "At least one suggestion must explain HOW to fix"
        finally:
            Path(temp_path).unlink()

    def test_includes_specific_recovery_actions(self):
        """Suggestions should include transcript review, status reset, and resume command."""
        from src.des.application.hooks import SubagentStopHook

        hook = SubagentStopHook()

        step_data = {
            "task_id": "01-06",
            "state": {"status": "IN_PROGRESS"},
            "tdd_cycle": {
                "phase_execution_log": [
                    {
                        "phase_number": 3,
                        "phase_name": "GREEN_UNIT",
                        "status": "IN_PROGRESS",
                    },
                ]
            },
        }

        import tempfile

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(step_data, f)
            temp_path = f.name

        try:
            result = hook.on_agent_complete(step_file_path=temp_path)

            suggestions_text = " ".join(result.recovery_suggestions).lower()
            assert "transcript" in suggestions_text, "Should mention transcript review"
            assert (
                "reset" in suggestions_text or "status" in suggestions_text
            ), "Should mention status reset"
            assert (
                "/nw:execute" in suggestions_text or "resume" in suggestions_text
            ), "Should mention resume command"
        finally:
            Path(temp_path).unlink()


class TestStepFileStateUpdate:
    """Tests for updating step file state to FAILED."""

    def test_updates_step_file_state_to_failed(self):
        """Hook should update step file state.status to FAILED when validation fails."""
        from src.des.application.hooks import SubagentStopHook

        hook = SubagentStopHook()

        step_data = {
            "task_id": "01-06",
            "state": {"status": "IN_PROGRESS"},
            "tdd_cycle": {
                "phase_execution_log": [
                    {
                        "phase_number": 3,
                        "phase_name": "GREEN_UNIT",
                        "status": "IN_PROGRESS",
                    },
                ]
            },
        }

        import tempfile

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(step_data, f)
            temp_path = f.name

        try:
            hook.on_agent_complete(step_file_path=temp_path)

            # Read step file to verify state update
            updated_data = json.loads(Path(temp_path).read_text())
            assert updated_data["state"]["status"] == "FAILED"
        finally:
            Path(temp_path).unlink()

    def test_adds_failure_reason_to_step_file(self):
        """Hook should add failure_reason to step file state."""
        from src.des.application.hooks import SubagentStopHook

        hook = SubagentStopHook()

        step_data = {
            "task_id": "01-06",
            "state": {"status": "IN_PROGRESS"},
            "tdd_cycle": {
                "phase_execution_log": [
                    {
                        "phase_number": 3,
                        "phase_name": "GREEN_UNIT",
                        "status": "IN_PROGRESS",
                    },
                ]
            },
        }

        import tempfile

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(step_data, f)
            temp_path = f.name

        try:
            hook.on_agent_complete(step_file_path=temp_path)

            # Read step file to verify failure_reason added
            updated_data = json.loads(Path(temp_path).read_text())
            assert "failure_reason" in updated_data["state"]
            assert updated_data["state"]["failure_reason"] is not None
            assert len(updated_data["state"]["failure_reason"]) > 0
        finally:
            Path(temp_path).unlink()


class TestTurnLimitValidation:
    """Tests for turn limit validation in SubagentStopHook."""

    def test_hook_result_has_turn_limit_exceeded_field(self):
        """HookResult should have turn_limit_exceeded boolean field."""
        from src.des.application.hooks import HookResult

        result = HookResult(validation_status="PASSED")

        # HookResult should have turn_limit_exceeded field
        assert hasattr(
            result, "turn_limit_exceeded"
        ), "HookResult missing turn_limit_exceeded field"

    def test_turn_limit_exceeded_defaults_to_false(self):
        """HookResult.turn_limit_exceeded should default to False."""
        from src.des.application.hooks import HookResult

        result = HookResult(validation_status="PASSED")
        assert (
            result.turn_limit_exceeded is False
        ), "turn_limit_exceeded should default to False"

    def test_detects_phase_exceeding_turn_limit(self):
        """Hook should detect when phase turn_count exceeds max_turns."""
        from src.des.application.hooks import SubagentStopHook

        hook = SubagentStopHook()

        # Step file with phase exceeding turn limit
        step_data = {
            "task_id": "02-02",
            "state": {"status": "IN_PROGRESS"},
            "tdd_cycle": {
                "max_turns": 50,
                "phase_execution_log": [
                    {
                        "phase_number": 3,
                        "phase_name": "GREEN_UNIT",
                        "status": "EXECUTED",
                        "outcome": "PASS",
                        "turn_count": 65,  # Exceeds max_turns of 50
                        "max_turns": 50,
                    }
                ],
            },
        }

        import tempfile

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(step_data, f)
            temp_path = f.name

        try:
            result = hook.on_agent_complete(step_file_path=temp_path)

            # Should detect turn limit exceeded
            assert (
                result.turn_limit_exceeded is True
            ), "Should detect turn_count (65) exceeds max_turns (50)"

            # Should include phase name in error message
            assert result.error_message is not None
            assert "GREEN_UNIT" in result.error_message

            # Should provide recovery suggestions
            assert len(result.recovery_suggestions) >= 2
        finally:
            Path(temp_path).unlink()

    def test_identifies_which_phase_exceeded_limit(self):
        """Error message should identify which phase exceeded turn limit."""
        from src.des.application.hooks import SubagentStopHook

        hook = SubagentStopHook()

        step_data = {
            "task_id": "02-02",
            "state": {"status": "IN_PROGRESS"},
            "tdd_cycle": {
                "max_turns": 30,
                "phase_execution_log": [
                    {
                        "phase_number": 1,
                        "phase_name": "RED_ACCEPTANCE",
                        "status": "EXECUTED",
                        "outcome": "PASS",
                        "turn_count": 10,
                        "max_turns": 30,
                    },
                    {
                        "phase_number": 2,
                        "phase_name": "RED_UNIT",
                        "status": "EXECUTED",
                        "outcome": "PASS",
                        "turn_count": 45,  # Exceeds limit
                        "max_turns": 30,
                    },
                ],
            },
        }

        import tempfile

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(step_data, f)
            temp_path = f.name

        try:
            result = hook.on_agent_complete(step_file_path=temp_path)

            # Should identify RED_UNIT as the phase that exceeded limit
            assert "RED_UNIT" in result.error_message
            assert (
                "45" in result.error_message
                or "exceeded" in result.error_message.lower()
            )
        finally:
            Path(temp_path).unlink()

    def test_recovery_suggestions_include_increase_limit(self):
        """Recovery suggestions should mention increasing max_turns limit."""
        from src.des.application.hooks import SubagentStopHook

        hook = SubagentStopHook()

        step_data = {
            "task_id": "02-02",
            "state": {"status": "IN_PROGRESS"},
            "tdd_cycle": {
                "max_turns": 20,
                "phase_execution_log": [
                    {
                        "phase_number": 0,
                        "phase_name": "PREPARE",
                        "status": "EXECUTED",
                        "outcome": "PASS",
                        "turn_count": 35,
                        "max_turns": 20,
                    }
                ],
            },
        }

        import tempfile

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(step_data, f)
            temp_path = f.name

        try:
            result = hook.on_agent_complete(step_file_path=temp_path)

            suggestions_text = " ".join(result.recovery_suggestions).lower()
            assert any(
                keyword in suggestions_text
                for keyword in ["increase", "max_turns", "limit", "higher"]
            ), "Should suggest increasing max_turns limit"
        finally:
            Path(temp_path).unlink()

    def test_recovery_suggestions_include_simplify_step(self):
        """Recovery suggestions should mention simplifying or splitting step."""
        from src.des.application.hooks import SubagentStopHook

        hook = SubagentStopHook()

        step_data = {
            "task_id": "02-02",
            "state": {"status": "IN_PROGRESS"},
            "tdd_cycle": {
                "max_turns": 25,
                "phase_execution_log": [
                    {
                        "phase_number": 7,
                        "phase_name": "REFACTOR_L1",
                        "status": "EXECUTED",
                        "outcome": "PASS",
                        "turn_count": 40,
                        "max_turns": 25,
                    }
                ],
            },
        }

        import tempfile

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(step_data, f)
            temp_path = f.name

        try:
            result = hook.on_agent_complete(step_file_path=temp_path)

            suggestions_text = " ".join(result.recovery_suggestions).lower()
            assert any(
                keyword in suggestions_text
                for keyword in ["simplify", "break", "smaller", "split"]
            ), "Should suggest simplifying or splitting step"
        finally:
            Path(temp_path).unlink()


class TestTimeoutDetection:
    """Tests for timeout exceeded detection in SubagentStopHook."""

    def test_hook_result_has_timeout_exceeded_field(self):
        """HookResult should have timeout_exceeded field."""
        from src.des.application.hooks import HookResult

        result = HookResult(validation_status="PASSED")
        assert hasattr(result, "timeout_exceeded")
        assert result.timeout_exceeded is False

    def test_detect_timeout_exceeded_when_duration_exceeds_limit(self):
        """Hook should detect when duration_seconds exceeds configured limit."""
        from src.des.application.hooks import SubagentStopHook

        hook = SubagentStopHook()

        step_data = {
            "task_id": "07-01",
            "state": {"status": "COMPLETED"},
            "tdd_cycle": {
                "duration_minutes": 30,
                "total_extensions_minutes": 10,  # Total allowed: 40 min = 2400s
                "phase_execution_log": [
                    {
                        "phase_number": 0,
                        "phase_name": "PREPARE",
                        "status": "EXECUTED",
                        "outcome": "PASS",
                        "duration_seconds": 300,
                    },
                    {
                        "phase_number": 1,
                        "phase_name": "RED_ACCEPTANCE",
                        "status": "EXECUTED",
                        "outcome": "PASS",
                        "duration_seconds": 2400,  # Total: 2700s = 45 min (exceeds 40 min)
                    },
                ],
            },
        }

        import tempfile

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(step_data, f)
            temp_path = f.name

        try:
            result = hook.on_agent_complete(step_file_path=temp_path)
            assert result.timeout_exceeded is True
        finally:
            Path(temp_path).unlink()

    def test_no_timeout_when_duration_within_limit(self):
        """Hook should not detect timeout when duration is within limit."""
        from src.des.application.hooks import SubagentStopHook

        hook = SubagentStopHook()

        step_data = {
            "task_id": "07-01",
            "state": {"status": "COMPLETED"},
            "tdd_cycle": {
                "duration_minutes": 30,
                "total_extensions_minutes": 10,  # Total allowed: 40 min = 2400s
                "phase_execution_log": [
                    {
                        "phase_number": 0,
                        "phase_name": "PREPARE",
                        "status": "EXECUTED",
                        "outcome": "PASS",
                        "duration_seconds": 300,
                    },
                    {
                        "phase_number": 1,
                        "phase_name": "RED_ACCEPTANCE",
                        "status": "EXECUTED",
                        "outcome": "PASS",
                        "duration_seconds": 2000,  # Total: 2300s < 2400s (within limit)
                    },
                ],
            },
        }

        import tempfile

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(step_data, f)
            temp_path = f.name

        try:
            result = hook.on_agent_complete(step_file_path=temp_path)
            assert result.timeout_exceeded is False
        finally:
            Path(temp_path).unlink()

    def test_timeout_error_message_includes_duration_details(self):
        """Error message should include actual and expected duration."""
        from src.des.application.hooks import SubagentStopHook

        hook = SubagentStopHook()

        step_data = {
            "task_id": "07-01",
            "state": {"status": "COMPLETED"},
            "tdd_cycle": {
                "duration_minutes": 30,
                "total_extensions_minutes": 10,
                "phase_execution_log": [
                    {
                        "phase_number": 0,
                        "phase_name": "PREPARE",
                        "status": "EXECUTED",
                        "outcome": "PASS",
                        "duration_seconds": 2700,  # Exceeds 40 min limit
                    }
                ],
            },
        }

        import tempfile

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(step_data, f)
            temp_path = f.name

        try:
            result = hook.on_agent_complete(step_file_path=temp_path)
            assert result.error_message is not None
            error_msg = result.error_message.lower()
            assert (
                "timeout" in error_msg
                or "exceeded" in error_msg
                or "duration" in error_msg
            )
        finally:
            Path(temp_path).unlink()

    def test_timeout_recovery_suggestions_include_extension_and_simplify(self):
        """Recovery suggestions should include requesting extension and simplifying step."""
        from src.des.application.hooks import SubagentStopHook

        hook = SubagentStopHook()

        step_data = {
            "task_id": "07-01",
            "state": {"status": "COMPLETED"},
            "tdd_cycle": {
                "duration_minutes": 30,
                "total_extensions_minutes": 10,
                "phase_execution_log": [
                    {
                        "phase_number": 0,
                        "phase_name": "PREPARE",
                        "status": "EXECUTED",
                        "outcome": "PASS",
                        "duration_seconds": 2700,  # Exceeds limit
                    }
                ],
            },
        }

        import tempfile

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(step_data, f)
            temp_path = f.name

        try:
            result = hook.on_agent_complete(step_file_path=temp_path)
            suggestions_text = " ".join(result.recovery_suggestions).lower()

            assert any(
                keyword in suggestions_text
                for keyword in ["extension", "extend", "request", "more time"]
            ), "Should suggest requesting extension"

            assert any(
                keyword in suggestions_text
                for keyword in ["simplify", "break", "smaller", "split", "reduce"]
            ), "Should suggest simplifying step"
        finally:
            Path(temp_path).unlink()
