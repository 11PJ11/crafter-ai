"""Unit tests for des.hooks module - SubagentStopHook class."""

import json
from pathlib import Path


class TestSubagentStopHookClass:
    """Tests for SubagentStopHook class existence and basic structure."""

    def test_subagent_stop_hook_class_exists(self):
        """Hook class should be importable from des.hooks module."""
        from des.hooks import SubagentStopHook

        assert SubagentStopHook is not None
        assert hasattr(SubagentStopHook, "__init__")

    def test_subagent_stop_hook_on_agent_complete_method_exists(self):
        """Hook should have on_agent_complete method."""
        from des.hooks import SubagentStopHook

        hook = SubagentStopHook()
        assert hasattr(hook, "on_agent_complete")
        assert callable(hook.on_agent_complete)

    def test_on_agent_complete_accepts_step_file_path(self):
        """on_agent_complete should accept step_file_path parameter."""
        from des.hooks import SubagentStopHook

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
        from des.hooks import SubagentStopHook, HookResult

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
        from des.hooks import HookResult

        result = HookResult(validation_status="PASSED")
        assert hasattr(result, "hook_fired")
        assert result.hook_fired is True

    def test_hook_result_has_validation_status_field(self):
        """HookResult should have validation_status field."""
        from des.hooks import HookResult

        result = HookResult(validation_status="PASSED")
        assert hasattr(result, "validation_status")
        assert result.validation_status == "PASSED"

    def test_hook_result_has_required_fields(self):
        """HookResult should have all required validation fields."""
        from des.hooks import HookResult

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
        from des.hooks import SubagentStopHook

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
        from des.hooks import SubagentStopHook

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
        from des.hooks import HookResult

        result = HookResult(validation_status="PASSED")
        assert hasattr(result, "not_executed_phases")

    def test_not_executed_phases_field_is_integer(self):
        """not_executed_phases should be an integer count."""
        from des.hooks import HookResult

        result = HookResult(validation_status="PASSED", not_executed_phases=14)
        assert isinstance(result.not_executed_phases, int)
        assert result.not_executed_phases == 14

    def test_detects_all_phases_not_executed_as_silent_completion(self):
        """Hook should detect when all 14 phases are NOT_EXECUTED as SILENT_COMPLETION."""
        from des.hooks import SubagentStopHook

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
        from des.hooks import SubagentStopHook

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
        from des.hooks import SubagentStopHook

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
        from des.hooks import SubagentStopHook

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
        from des.hooks import SubagentStopHook

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
        from des.hooks import SubagentStopHook

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
        from des.hooks import SubagentStopHook

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
        from des.hooks import SubagentStopHook

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
