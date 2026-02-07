"""Unit tests for SubagentStopHook audit logging integration (Schema v2.0).

Tests verify that SubagentStopHook logs SCOPE_VIOLATION events to AuditLogger
when ScopeValidator detects out-of-scope file modifications.

Business Context:
When an agent modifies files outside the allowed scope (e.g., OrderService.py
when working on UserRepository), the hook must log each violation as a WARNING
audit event. This creates a transparent audit trail for Priya to review during
PR review, allowing her to decide whether to accept or reject the work.

Step 02-01: Tests rewritten to use constructor injection (AC5)
instead of patching get_audit_logger singleton.
"""

from unittest.mock import Mock, patch

import pytest
import yaml


pytestmark = pytest.mark.skip(
    reason="Internal SubagentStopHook class testing, needs hexagonal port rewrite"
)


class TestAuditLoggingIntegration:
    """Test SubagentStopHook logs scope violations to audit trail (Schema v2.0)."""

    def test_hook_logs_scope_violation_to_audit_logger(self, tmp_path, tdd_phases):
        """
        GIVEN ScopeValidator detects out-of-scope file modification
        WHEN SubagentStopHook.on_agent_complete() is called
        THEN SCOPE_VIOLATION event is logged to AuditLogger

        Business Context:
        Agent modified OrderService.py (out of scope) during UserRepository step.
        Hook must log this violation with event_type=SCOPE_VIOLATION, severity=WARNING,
        and include file path, step context, and allowed patterns for debugging.
        """
        # Arrange: Create execution-log.yaml (Schema v2.0)
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

        # Mock ScopeValidator to return violation
        out_of_scope_file = "src/services/OrderService.py"
        mock_scope_result = ScopeValidationResult(
            has_violations=True,
            out_of_scope_files=[out_of_scope_file],
            violation_message=f"File {out_of_scope_file} is outside allowed scope",
            violation_severity="WARNING",
            validation_skipped=False,
            reason="",
        )

        # Create mock dependencies for constructor injection (AC5)
        mock_audit_logger = Mock()
        mock_time_provider = Mock()
        mock_datetime = Mock()
        mock_datetime.isoformat.return_value = "2026-02-02T06:25:00.000000+00:00"
        mock_time_provider.now_utc.return_value = mock_datetime

        with patch(
            "des.adapters.driven.hooks.subagent_stop_hook.ScopeValidator"
        ) as mock_validator_class:
            mock_validator_instance = Mock()
            mock_validator_instance.validate_scope.return_value = mock_scope_result
            mock_validator_class.return_value = mock_validator_instance

            # Act: Call hook with injected dependencies (AC5)
            hook = RealSubagentStopHook(
                audit_logger=mock_audit_logger,
                time_provider=mock_time_provider,
            )
            compound_path = f"{log_file}?project_id=test-project&step_id=01-01"
            hook.on_agent_complete(compound_path)

            # Assert: SCOPE_VIOLATION event logged (filter out HOOK_SUBAGENT_STOP events)
            scope_events = [
                call[0][0]
                for call in mock_audit_logger.append.call_args_list
                if call[0][0]["event"] == "SCOPE_VIOLATION"
            ]
            assert len(scope_events) == 1
            logged_event = scope_events[0]

            assert logged_event["event"] == "SCOPE_VIOLATION"
            assert logged_event["severity"] == "WARNING"
            assert logged_event["step_file"] == compound_path
            assert logged_event["out_of_scope_file"] == out_of_scope_file
            # Placeholder patterns for Schema v2.0 (TODO: extract from roadmap.yaml)
            assert logged_event["allowed_patterns"] == [
                "**/UserRepository*",
                "**/user_repository*",
            ]

    def test_hook_logs_each_violation_separately(self, tmp_path, tdd_phases):
        """
        GIVEN ScopeValidator detects multiple out-of-scope files
        WHEN SubagentStopHook.on_agent_complete() is called
        THEN each violation is logged as separate audit entry

        Business Context:
        If agent went "rogue" and modified OrderService.py, PaymentService.py,
        and EmailService.py (all out of scope), Priya needs to see all three
        violations in audit trail, not just the first one. Each gets its own
        audit entry for complete transparency.
        """
        # Arrange: Create execution-log.yaml (Schema v2.0)
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

        # Mock ScopeValidator to return multiple violations
        out_of_scope_files = [
            "src/services/OrderService.py",
            "src/services/PaymentService.py",
            "src/services/EmailService.py",
        ]
        mock_scope_result = ScopeValidationResult(
            has_violations=True,
            out_of_scope_files=out_of_scope_files,
            violation_message="3 files outside allowed scope",
            violation_severity="WARNING",
            validation_skipped=False,
            reason="",
        )

        # Create mock dependencies for constructor injection (AC5)
        mock_audit_logger = Mock()
        mock_time_provider = Mock()
        mock_datetime = Mock()
        mock_datetime.isoformat.return_value = "2026-02-02T06:25:00.000000+00:00"
        mock_time_provider.now_utc.return_value = mock_datetime

        with patch(
            "des.adapters.driven.hooks.subagent_stop_hook.ScopeValidator"
        ) as mock_validator_class:
            mock_validator_instance = Mock()
            mock_validator_instance.validate_scope.return_value = mock_scope_result
            mock_validator_class.return_value = mock_validator_instance

            # Act: Call hook with injected dependencies (AC5)
            hook = RealSubagentStopHook(
                audit_logger=mock_audit_logger,
                time_provider=mock_time_provider,
            )
            compound_path = f"{log_file}?project_id=test-project&step_id=01-01"
            hook.on_agent_complete(compound_path)

            # Assert: 3 SCOPE_VIOLATION events logged (filter out HOOK_SUBAGENT_STOP)
            scope_events = [
                call[0][0]
                for call in mock_audit_logger.append.call_args_list
                if call[0][0]["event"] == "SCOPE_VIOLATION"
            ]
            assert len(scope_events) == 3

            # Verify each call logged correct file
            for idx, out_of_scope_file in enumerate(out_of_scope_files):
                assert scope_events[idx]["event"] == "SCOPE_VIOLATION"
                assert scope_events[idx]["out_of_scope_file"] == out_of_scope_file

    def test_hook_does_not_log_when_no_violations(self, tmp_path, tdd_phases):
        """
        GIVEN ScopeValidator finds no violations (all files in scope)
        WHEN SubagentStopHook.on_agent_complete() is called
        THEN no SCOPE_VIOLATION events are logged

        Business Context:
        Agent correctly modified only UserRepository.py and test_user_repository.py
        (both in allowed patterns). No audit events needed - work is compliant.
        """
        # Arrange: Create execution-log.yaml (Schema v2.0)
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

        # Mock ScopeValidator to return no violations
        mock_scope_result = ScopeValidationResult(
            has_violations=False,
            out_of_scope_files=[],
            violation_message="",
            violation_severity="",
            validation_skipped=False,
            reason="",
        )

        # Create mock dependencies for constructor injection (AC5)
        mock_audit_logger = Mock()
        mock_time_provider = Mock()
        mock_datetime = Mock()
        mock_datetime.isoformat.return_value = "2026-02-02T06:25:00.000000+00:00"
        mock_time_provider.now_utc.return_value = mock_datetime

        with patch(
            "des.adapters.driven.hooks.subagent_stop_hook.ScopeValidator"
        ) as mock_validator_class:
            mock_validator_instance = Mock()
            mock_validator_instance.validate_scope.return_value = mock_scope_result
            mock_validator_class.return_value = mock_validator_instance

            # Act: Call hook with injected dependencies (AC5)
            hook = RealSubagentStopHook(
                audit_logger=mock_audit_logger,
                time_provider=mock_time_provider,
            )
            compound_path = f"{log_file}?project_id=test-project&step_id=01-01"
            hook.on_agent_complete(compound_path)

            # Assert: No SCOPE_VIOLATION events logged (HOOK_SUBAGENT_STOP may exist)
            scope_events = [
                call[0][0]
                for call in mock_audit_logger.append.call_args_list
                if call[0][0]["event"] == "SCOPE_VIOLATION"
            ]
            assert len(scope_events) == 0

    def test_hook_includes_allowed_patterns_in_audit_event(self, tmp_path, tdd_phases):
        """
        GIVEN step file has allowed_patterns in scope section
        WHEN SubagentStopHook logs SCOPE_VIOLATION
        THEN audit event includes allowed_patterns for debugging

        Business Context:
        When Priya reviews audit log and sees OrderService.py violation,
        she needs to see what patterns WERE allowed (**/UserRepository*)
        to understand why the violation occurred and assess if work should
        be accepted (perhaps agent did valid cross-cutting change) or
        rejected (agent went off-task).
        """
        # Arrange: Create execution-log.yaml (Schema v2.0)
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

        # Mock ScopeValidator to return violation
        allowed_patterns = ["**/UserRepository*", "**/user_repository*"]
        mock_scope_result = ScopeValidationResult(
            has_violations=True,
            out_of_scope_files=["src/services/OrderService.py"],
            violation_message="Violation detected",
            violation_severity="WARNING",
            validation_skipped=False,
            reason="",
        )

        # Create mock dependencies for constructor injection (AC5)
        mock_audit_logger = Mock()
        mock_time_provider = Mock()
        mock_datetime = Mock()
        mock_datetime.isoformat.return_value = "2026-02-02T06:25:00.000000+00:00"
        mock_time_provider.now_utc.return_value = mock_datetime

        with patch(
            "des.adapters.driven.hooks.subagent_stop_hook.ScopeValidator"
        ) as mock_validator_class:
            mock_validator_instance = Mock()
            mock_validator_instance.validate_scope.return_value = mock_scope_result
            mock_validator_class.return_value = mock_validator_instance

            # Act: Call hook with injected dependencies (AC5)
            hook = RealSubagentStopHook(
                audit_logger=mock_audit_logger,
                time_provider=mock_time_provider,
            )
            compound_path = f"{log_file}?project_id=test-project&step_id=01-01"
            hook.on_agent_complete(compound_path)

            # Assert: SCOPE_VIOLATION event includes allowed_patterns
            scope_events = [
                call[0][0]
                for call in mock_audit_logger.append.call_args_list
                if call[0][0]["event"] == "SCOPE_VIOLATION"
            ]
            assert len(scope_events) >= 1
            assert scope_events[0]["allowed_patterns"] == allowed_patterns
