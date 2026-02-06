"""Unit tests for SubagentStopHook audit logging (Schema v2.0).

Step 02-01: Tests rewritten to use constructor injection (AC5)
instead of patching get_audit_logger singleton.
"""

from unittest.mock import Mock

import pytest
import yaml
from src.des.adapters.driven.hooks.subagent_stop_hook import SubagentStopHook


@pytest.fixture
def mock_audit_logger():
    """Create mock audit logger for injection."""
    return Mock()


@pytest.fixture
def mock_time_provider():
    """Create mock time provider with fixed timestamp."""
    provider = Mock()
    mock_datetime = Mock()
    mock_datetime.isoformat.return_value = "2026-02-02T06:25:00.000000+00:00"
    provider.now_utc.return_value = mock_datetime
    return provider


@pytest.fixture
def hook_with_injection(mock_audit_logger, mock_time_provider):
    """Create SubagentStopHook with injected dependencies (AC5 pattern)."""
    return SubagentStopHook(
        audit_logger=mock_audit_logger,
        time_provider=mock_time_provider,
    )


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
    """Test audit logging in SubagentStopHook via constructor injection (AC5).

    Tests verify that SubagentStopHook logs HOOK_SUBAGENT_STOP_PASSED and
    HOOK_SUBAGENT_STOP_FAILED events to AuditLogger when validating step completion.
    """

    def test_logs_hook_subagent_stop_passed_on_success(
        self, hook_with_injection, mock_audit_logger, valid_execution_log
    ):
        """Verify HOOK_SUBAGENT_STOP_PASSED logged when validation succeeds."""
        compound_path = f"{valid_execution_log}?project_id=test-project&step_id=01-01"
        result = hook_with_injection.on_agent_complete(step_file_path=compound_path)

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

    def test_logs_hook_subagent_stop_failed_on_failure(
        self, hook_with_injection, mock_audit_logger, invalid_execution_log
    ):
        """Verify HOOK_SUBAGENT_STOP_FAILED logged when validation fails."""
        compound_path = f"{invalid_execution_log}?project_id=test-project&step_id=01-02"
        result = hook_with_injection.on_agent_complete(step_file_path=compound_path)

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

    def test_includes_step_id_in_audit_entry(
        self, hook_with_injection, mock_audit_logger, valid_execution_log
    ):
        """Verify step_id included in audit entry."""
        compound_path = f"{valid_execution_log}?project_id=test-project&step_id=01-01"
        hook_with_injection.on_agent_complete(step_file_path=compound_path)

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

    def test_includes_phases_validated_count(
        self, hook_with_injection, mock_audit_logger, valid_execution_log
    ):
        """Verify phases_validated count included in audit entry."""
        compound_path = f"{valid_execution_log}?project_id=test-project&step_id=01-01"
        hook_with_injection.on_agent_complete(step_file_path=compound_path)

        # Find HOOK_SUBAGENT_STOP event in calls
        hook_calls = [
            call[0][0]
            for call in mock_audit_logger.append.call_args_list
            if "HOOK_SUBAGENT_STOP" in call[0][0]["event"]
        ]
        assert len(hook_calls) == 1, "Expected exactly one HOOK_SUBAGENT_STOP event"
        audit_entry = hook_calls[0]
        assert audit_entry["phases_validated"] == 7  # All 7 phases

    def test_includes_validation_errors_on_failure(
        self, hook_with_injection, mock_audit_logger, invalid_execution_log
    ):
        """Verify validation errors included when validation fails."""
        compound_path = f"{invalid_execution_log}?project_id=test-project&step_id=01-02"
        hook_with_injection.on_agent_complete(step_file_path=compound_path)

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

    def test_uses_injected_time_provider_for_timestamp(
        self,
        hook_with_injection,
        mock_audit_logger,
        mock_time_provider,
        valid_execution_log,
    ):
        """AC5: Uses injected time_provider (not self-created) for timestamp."""
        compound_path = f"{valid_execution_log}?project_id=test-project&step_id=01-01"
        hook_with_injection.on_agent_complete(step_file_path=compound_path)

        # Verify injected time_provider was called
        mock_time_provider.now_utc.assert_called()

        # Find HOOK_SUBAGENT_STOP event in calls (may have SCOPE_VIOLATION calls too)
        hook_calls = [
            call[0][0]
            for call in mock_audit_logger.append.call_args_list
            if "HOOK_SUBAGENT_STOP" in call[0][0]["event"]
        ]
        assert len(hook_calls) == 1, "Expected exactly one HOOK_SUBAGENT_STOP event"
        audit_entry = hook_calls[0]
        assert audit_entry["timestamp"] == "2026-02-02T06:25:00.000000+00:00"
