"""Unit tests for SubagentStopHook audit logging (Schema v2.0).

Tests validate that SubagentStopHook (driven adapter) logs audit events
when validating step completion from execution-log.yaml.

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
        "01-01|PREPARE|EXECUTED|PASS|2026-02-02T10:00:00+00:00",
        "01-01|RED_ACCEPTANCE|EXECUTED|PASS|2026-02-02T10:05:00+00:00",
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
    """Test audit logging in SubagentStopHook via constructor injection (AC5)."""

    def test_logs_hook_subagent_stop_passed_on_success(
        self, hook_with_injection, mock_audit_logger, valid_execution_log
    ):
        """AC3: HOOK_SUBAGENT_STOP_PASSED logged when validation succeeds."""
        compound_path = f"{valid_execution_log}?project_id=test-project&step_id=01-01"
        result = hook_with_injection.on_agent_complete(step_file_path=compound_path)

        assert result.validation_status == "PASSED"

        # Verify audit logger received HOOK_SUBAGENT_STOP_PASSED event
        mock_audit_logger.append.assert_called_once()
        audit_entry = mock_audit_logger.append.call_args[0][0]
        assert audit_entry["event"] == "HOOK_SUBAGENT_STOP_PASSED"

    def test_logs_hook_subagent_stop_failed_on_failure(
        self, hook_with_injection, mock_audit_logger, invalid_execution_log
    ):
        """AC3: HOOK_SUBAGENT_STOP_FAILED logged when validation fails."""
        compound_path = f"{invalid_execution_log}?project_id=test-project&step_id=01-01"
        result = hook_with_injection.on_agent_complete(step_file_path=compound_path)

        assert result.validation_status == "FAILED"

        # Verify audit logger received HOOK_SUBAGENT_STOP_FAILED event
        mock_audit_logger.append.assert_called_once()
        audit_entry = mock_audit_logger.append.call_args[0][0]
        assert audit_entry["event"] == "HOOK_SUBAGENT_STOP_FAILED"

    def test_includes_step_id_in_audit_entry(
        self, hook_with_injection, mock_audit_logger, valid_execution_log
    ):
        """Verify step_id included in audit entry."""
        compound_path = f"{valid_execution_log}?project_id=test-project&step_id=01-01"
        hook_with_injection.on_agent_complete(step_file_path=compound_path)

        audit_entry = mock_audit_logger.append.call_args[0][0]
        assert audit_entry["step_id"] == "01-01"

    def test_includes_phases_validated_count(
        self, hook_with_injection, mock_audit_logger, valid_execution_log, tdd_phases
    ):
        """Verify phases_validated count included in audit entry."""
        compound_path = f"{valid_execution_log}?project_id=test-project&step_id=01-01"
        hook_with_injection.on_agent_complete(step_file_path=compound_path)

        audit_entry = mock_audit_logger.append.call_args[0][0]
        assert audit_entry["phases_validated"] == len(tdd_phases)

    def test_includes_validation_errors_on_failure(
        self, hook_with_injection, mock_audit_logger, invalid_execution_log
    ):
        """Verify validation errors included when validation fails."""
        compound_path = f"{invalid_execution_log}?project_id=test-project&step_id=01-01"
        hook_with_injection.on_agent_complete(step_file_path=compound_path)

        audit_entry = mock_audit_logger.append.call_args[0][0]
        assert audit_entry["event"] == "HOOK_SUBAGENT_STOP_FAILED"
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

        # Verify timestamp from injected provider
        audit_entry = mock_audit_logger.append.call_args[0][0]
        assert audit_entry["timestamp"] == "2026-02-02T06:25:00.000000+00:00"


class TestSubagentStopHookDependencyInjectionEnforcement:
    """Test that audit logging fails without injected dependencies (AC5)."""

    def test_raises_runtime_error_when_audit_logger_not_injected(
        self, valid_execution_log
    ):
        """AC5: RuntimeError when audit_logger=None and audit event fires."""
        hook = SubagentStopHook(audit_logger=None, time_provider=Mock())

        compound_path = f"{valid_execution_log}?project_id=test-project&step_id=01-01"

        with pytest.raises(RuntimeError, match="audit_logger and time_provider"):
            hook.on_agent_complete(step_file_path=compound_path)

    def test_raises_runtime_error_when_time_provider_not_injected(
        self, valid_execution_log
    ):
        """AC5: RuntimeError when time_provider=None and audit event fires."""
        hook = SubagentStopHook(audit_logger=Mock(), time_provider=None)

        compound_path = f"{valid_execution_log}?project_id=test-project&step_id=01-01"

        with pytest.raises(RuntimeError, match="audit_logger and time_provider"):
            hook.on_agent_complete(step_file_path=compound_path)

    def test_raises_runtime_error_when_both_not_injected(self, valid_execution_log):
        """AC5: RuntimeError when neither dependency injected."""
        hook = SubagentStopHook()  # No injection

        compound_path = f"{valid_execution_log}?project_id=test-project&step_id=01-01"

        with pytest.raises(RuntimeError, match="audit_logger and time_provider"):
            hook.on_agent_complete(step_file_path=compound_path)
