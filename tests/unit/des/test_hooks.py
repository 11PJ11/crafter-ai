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
