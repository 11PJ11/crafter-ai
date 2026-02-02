"""Unit tests for RealSubagentStopHook audit logging."""

import json
import pytest
from unittest.mock import Mock, patch
from src.des.adapters.drivers.hooks.real_hook import RealSubagentStopHook


@pytest.fixture
def valid_step_file(tmp_path):
    """Create step file with all phases complete."""
    step_file = tmp_path / "step-01-01.json"
    step_data = {
        "step_id": "01-01",
        "description": "Test step",
        "tdd_cycle": {
            "phase_execution_log": [
                {"phase_name": "PREPARE", "status": "COMPLETED", "outcome": "PASS"},
                {
                    "phase_name": "RED_ACCEPTANCE",
                    "status": "COMPLETED",
                    "outcome": "PASS",
                },
                {"phase_name": "RED_UNIT", "status": "COMPLETED", "outcome": "PASS"},
                {"phase_name": "GREEN", "status": "COMPLETED", "outcome": "PASS"},
                {"phase_name": "REVIEW", "status": "COMPLETED", "outcome": "PASS"},
                {
                    "phase_name": "REFACTOR_CONTINUOUS",
                    "status": "COMPLETED",
                    "outcome": "PASS",
                },
                {"phase_name": "COMMIT", "status": "COMPLETED", "outcome": "PASS"},
            ],
            "duration_minutes": 60,
        },
        "state": {"status": "DONE"},
    }
    step_file.write_text(json.dumps(step_data, indent=2))
    return step_file


@pytest.fixture
def invalid_step_file(tmp_path):
    """Create step file with abandoned phase."""
    step_file = tmp_path / "step-01-02.json"
    step_data = {
        "step_id": "01-02",
        "description": "Test step",
        "tdd_cycle": {
            "phase_execution_log": [
                {"phase_name": "PREPARE", "status": "COMPLETED", "outcome": "PASS"},
                {"phase_name": "RED_ACCEPTANCE", "status": "IN_PROGRESS"},
            ],
            "duration_minutes": 60,
        },
        "state": {"status": "IN_PROGRESS"},
    }
    step_file.write_text(json.dumps(step_data, indent=2))
    return step_file


class TestRealSubagentStopHookAudit:
    """Test audit logging in RealSubagentStopHook."""

    @patch("src.des.adapters.drivers.hooks.real_hook.get_audit_logger")
    def test_logs_hook_subagent_stop_passed_on_success(
        self, mock_get_audit_logger, valid_step_file
    ):
        """Verify HOOK_SUBAGENT_STOP_PASSED logged when validation succeeds."""
        mock_audit_logger = Mock()
        mock_get_audit_logger.return_value = mock_audit_logger

        hook = RealSubagentStopHook()
        result = hook.on_agent_complete(step_file_path=str(valid_step_file))

        # Verify validation succeeded
        assert result.validation_status == "PASSED"

        # Find HOOK_SUBAGENT_STOP_PASSED event in calls (may have SCOPE_VIOLATION calls too)
        hook_calls = [
            call[0][0]
            for call in mock_audit_logger.append.call_args_list
            if call[0][0]["event"] == "HOOK_SUBAGENT_STOP_PASSED"
        ]
        assert len(hook_calls) == 1, (
            "Expected exactly one HOOK_SUBAGENT_STOP_PASSED event"
        )
        audit_entry = hook_calls[0]

        assert audit_entry["event"] == "HOOK_SUBAGENT_STOP_PASSED"

    @patch("src.des.adapters.drivers.hooks.real_hook.get_audit_logger")
    def test_logs_hook_subagent_stop_failed_on_failure(
        self, mock_get_audit_logger, invalid_step_file
    ):
        """Verify HOOK_SUBAGENT_STOP_FAILED logged when validation fails."""
        mock_audit_logger = Mock()
        mock_get_audit_logger.return_value = mock_audit_logger

        hook = RealSubagentStopHook()
        result = hook.on_agent_complete(step_file_path=str(invalid_step_file))

        # Verify validation failed
        assert result.validation_status == "FAILED"

        # Find HOOK_SUBAGENT_STOP_FAILED event in calls (may have SCOPE_VIOLATION calls too)
        hook_calls = [
            call[0][0]
            for call in mock_audit_logger.append.call_args_list
            if call[0][0]["event"] == "HOOK_SUBAGENT_STOP_FAILED"
        ]
        assert len(hook_calls) == 1, (
            "Expected exactly one HOOK_SUBAGENT_STOP_FAILED event"
        )
        audit_entry = hook_calls[0]

        assert audit_entry["event"] == "HOOK_SUBAGENT_STOP_FAILED"

    @patch("src.des.adapters.drivers.hooks.real_hook.get_audit_logger")
    def test_includes_step_path_in_audit_entry(
        self, mock_get_audit_logger, valid_step_file
    ):
        """Verify step_path included in audit entry."""
        mock_audit_logger = Mock()
        mock_get_audit_logger.return_value = mock_audit_logger

        hook = RealSubagentStopHook()
        hook.on_agent_complete(step_file_path=str(valid_step_file))

        # Find HOOK_SUBAGENT_STOP event in calls
        hook_calls = [
            call[0][0]
            for call in mock_audit_logger.append.call_args_list
            if "HOOK_SUBAGENT_STOP" in call[0][0]["event"]
        ]
        assert len(hook_calls) == 1, "Expected exactly one HOOK_SUBAGENT_STOP event"
        audit_entry = hook_calls[0]
        assert audit_entry["step_path"] == str(valid_step_file)

    @patch("src.des.adapters.drivers.hooks.real_hook.get_audit_logger")
    def test_includes_phases_validated_count(
        self, mock_get_audit_logger, valid_step_file
    ):
        """Verify phases_validated count included in audit entry."""
        mock_audit_logger = Mock()
        mock_get_audit_logger.return_value = mock_audit_logger

        hook = RealSubagentStopHook()
        hook.on_agent_complete(step_file_path=str(valid_step_file))

        # Find HOOK_SUBAGENT_STOP event in calls
        hook_calls = [
            call[0][0]
            for call in mock_audit_logger.append.call_args_list
            if "HOOK_SUBAGENT_STOP" in call[0][0]["event"]
        ]
        assert len(hook_calls) == 1, "Expected exactly one HOOK_SUBAGENT_STOP event"
        audit_entry = hook_calls[0]
        assert audit_entry["phases_validated"] == 7  # All 7 phases

    @patch("src.des.adapters.drivers.hooks.real_hook.get_audit_logger")
    def test_includes_validation_errors_on_failure(
        self, mock_get_audit_logger, invalid_step_file
    ):
        """Verify validation errors included when validation fails."""
        mock_audit_logger = Mock()
        mock_get_audit_logger.return_value = mock_audit_logger

        hook = RealSubagentStopHook()
        hook.on_agent_complete(step_file_path=str(invalid_step_file))

        # Find HOOK_SUBAGENT_STOP_FAILED event in calls (may have SCOPE_VIOLATION calls too)
        hook_calls = [
            call[0][0]
            for call in mock_audit_logger.append.call_args_list
            if call[0][0]["event"] == "HOOK_SUBAGENT_STOP_FAILED"
        ]
        assert len(hook_calls) == 1, (
            "Expected exactly one HOOK_SUBAGENT_STOP_FAILED event"
        )
        audit_entry = hook_calls[0]

        assert "validation_errors" in audit_entry
        assert len(audit_entry["validation_errors"]) > 0

    @patch("src.des.adapters.driven.time.system_time.SystemTimeProvider")
    @patch("src.des.adapters.drivers.hooks.real_hook.get_audit_logger")
    def test_uses_time_provider_for_timestamp(
        self, mock_get_audit_logger, mock_system_time_provider, valid_step_file
    ):
        """Verify SystemTimeProvider used for timestamp."""
        mock_audit_logger = Mock()
        mock_get_audit_logger.return_value = mock_audit_logger

        # Create mock datetime with isoformat method
        mock_datetime = Mock()
        fixed_timestamp = "2026-02-02T06:25:00.000000+00:00"
        mock_datetime.isoformat.return_value = fixed_timestamp

        # Configure mock provider
        mock_provider_instance = Mock()
        mock_provider_instance.now_utc.return_value = mock_datetime
        mock_system_time_provider.return_value = mock_provider_instance

        hook = RealSubagentStopHook()
        hook.on_agent_complete(step_file_path=str(valid_step_file))

        # Verify SystemTimeProvider was instantiated and now_utc called
        mock_system_time_provider.assert_called_once()
        mock_provider_instance.now_utc.assert_called_once()

        # Find HOOK_SUBAGENT_STOP event in calls (may have SCOPE_VIOLATION calls too)
        hook_calls = [
            call[0][0]
            for call in mock_audit_logger.append.call_args_list
            if "HOOK_SUBAGENT_STOP" in call[0][0]["event"]
        ]
        assert len(hook_calls) == 1, "Expected exactly one HOOK_SUBAGENT_STOP event"
        audit_entry = hook_calls[0]
        assert audit_entry["timestamp"] == fixed_timestamp
