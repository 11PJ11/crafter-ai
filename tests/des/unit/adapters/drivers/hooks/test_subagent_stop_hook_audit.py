"""Unit tests for SubagentStopHook audit logging (Schema v2.0)."""

from unittest.mock import Mock, patch

import pytest
import yaml
from src.des.adapters.driven.hooks.subagent_stop_hook import SubagentStopHook


@pytest.fixture
def valid_execution_log(tmp_path, tdd_phases):
    """Create execution-log.yaml with all phases complete."""
    log_file = tmp_path / "execution-log.yaml"

    events = []
    for phase in tdd_phases:
        events.append(f"01-01|{phase}|EXECUTED|PASS|2026-02-02T10:00:00+00:00")

    log_data = {
        "project_id": "test-project",
        "created_at": "2026-02-02T09:00:00+00:00",
        "total_steps": 1,
        "events": events,
    }

    log_file.write_text(yaml.dump(log_data, default_flow_style=False))
    return log_file


@pytest.fixture
def invalid_execution_log(tmp_path):
    """Create execution-log.yaml with incomplete phases."""
    log_file = tmp_path / "execution-log.yaml"

    # Only 2 phases, missing remaining 5
    events = [
        "01-02|PREPARE|EXECUTED|PASS|2026-02-02T10:00:00+00:00",
        "01-02|RED_ACCEPTANCE|EXECUTED|PASS|2026-02-02T10:05:00+00:00",
    ]

    log_data = {
        "project_id": "test-project",
        "created_at": "2026-02-02T09:00:00+00:00",
        "total_steps": 1,
        "events": events,
    }

    log_file.write_text(yaml.dump(log_data, default_flow_style=False))
    return log_file


class TestSubagentStopHookAudit:
    """Test audit logging in SubagentStopHook (Schema v2.0).

    Tests verify that SubagentStopHook logs HOOK_SUBAGENT_STOP_PASSED and
    HOOK_SUBAGENT_STOP_FAILED events to AuditLogger when validating step completion.
    """

    @patch("src.des.adapters.driven.hooks.subagent_stop_hook.get_audit_logger")
    def test_logs_hook_subagent_stop_passed_on_success(
        self, mock_get_audit_logger, valid_execution_log
    ):
        """Verify HOOK_SUBAGENT_STOP_PASSED logged when validation succeeds."""
        mock_audit_logger = Mock()
        mock_get_audit_logger.return_value = mock_audit_logger

        hook = SubagentStopHook()

        # Build compound path (Schema v2.0 format)
        compound_path = f"{valid_execution_log}?project_id=test-project&step_id=01-01"
        result = hook.on_agent_complete(step_file_path=compound_path)

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

    @patch("src.des.adapters.driven.hooks.subagent_stop_hook.get_audit_logger")
    def test_logs_hook_subagent_stop_failed_on_failure(
        self, mock_get_audit_logger, invalid_execution_log
    ):
        """Verify HOOK_SUBAGENT_STOP_FAILED logged when validation fails."""
        mock_audit_logger = Mock()
        mock_get_audit_logger.return_value = mock_audit_logger

        hook = SubagentStopHook()

        # Build compound path (Schema v2.0 format)
        compound_path = f"{invalid_execution_log}?project_id=test-project&step_id=01-02"
        result = hook.on_agent_complete(step_file_path=compound_path)

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

    @patch("src.des.adapters.driven.hooks.subagent_stop_hook.get_audit_logger")
    def test_includes_step_id_in_audit_entry(
        self, mock_get_audit_logger, valid_execution_log
    ):
        """Verify step_id included in audit entry."""
        mock_audit_logger = Mock()
        mock_get_audit_logger.return_value = mock_audit_logger

        hook = SubagentStopHook()

        # Build compound path (Schema v2.0 format)
        compound_path = f"{valid_execution_log}?project_id=test-project&step_id=01-01"
        hook.on_agent_complete(step_file_path=compound_path)

        # Find HOOK_SUBAGENT_STOP event in calls
        hook_calls = [
            call[0][0]
            for call in mock_audit_logger.append.call_args_list
            if "HOOK_SUBAGENT_STOP" in call[0][0]["event"]
        ]
        assert len(hook_calls) == 1, "Expected exactly one HOOK_SUBAGENT_STOP event"
        audit_entry = hook_calls[0]
        # Schema v2.0: step_id comes from compound path parameter
        assert audit_entry["step_id"] == "01-01"

    @patch("src.des.adapters.driven.hooks.subagent_stop_hook.get_audit_logger")
    def test_includes_phases_validated_count(
        self, mock_get_audit_logger, valid_execution_log
    ):
        """Verify phases_validated count included in audit entry."""
        mock_audit_logger = Mock()
        mock_get_audit_logger.return_value = mock_audit_logger

        hook = SubagentStopHook()

        # Build compound path (Schema v2.0 format)
        compound_path = f"{valid_execution_log}?project_id=test-project&step_id=01-01"
        hook.on_agent_complete(step_file_path=compound_path)

        # Find HOOK_SUBAGENT_STOP event in calls
        hook_calls = [
            call[0][0]
            for call in mock_audit_logger.append.call_args_list
            if "HOOK_SUBAGENT_STOP" in call[0][0]["event"]
        ]
        assert len(hook_calls) == 1, "Expected exactly one HOOK_SUBAGENT_STOP event"
        audit_entry = hook_calls[0]
        assert audit_entry["phases_validated"] == 7  # All 7 phases

    @patch("src.des.adapters.driven.hooks.subagent_stop_hook.get_audit_logger")
    def test_includes_validation_errors_on_failure(
        self, mock_get_audit_logger, invalid_execution_log
    ):
        """Verify validation errors included when validation fails."""
        mock_audit_logger = Mock()
        mock_get_audit_logger.return_value = mock_audit_logger

        hook = SubagentStopHook()

        # Build compound path (Schema v2.0 format)
        compound_path = f"{invalid_execution_log}?project_id=test-project&step_id=01-02"
        hook.on_agent_complete(step_file_path=compound_path)

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

    @patch("src.des.adapters.driven.hooks.subagent_stop_hook.SystemTimeProvider")
    @patch("src.des.adapters.driven.hooks.subagent_stop_hook.get_audit_logger")
    def test_uses_time_provider_for_timestamp(
        self, mock_get_audit_logger, mock_system_time_provider, valid_execution_log
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

        hook = SubagentStopHook()

        # Build compound path (Schema v2.0 format)
        compound_path = f"{valid_execution_log}?project_id=test-project&step_id=01-01"
        hook.on_agent_complete(step_file_path=compound_path)

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
