"""Unit tests for SubagentStopHook audit logging integration.

Tests verify that SubagentStopHook logs SCOPE_VIOLATION events to AuditLogger
when ScopeValidator detects out-of-scope file modifications.

Business Context:
When an agent modifies files outside the allowed scope (e.g., OrderService.py
when working on UserRepository), the hook must log each violation as a WARNING
audit event. This creates a transparent audit trail for Priya to review during
PR review, allowing her to decide whether to accept or reject the work.
"""

import json
from unittest.mock import Mock, patch

from src.des.adapters.drivers.hooks.real_hook import RealSubagentStopHook
from src.des.validation.scope_validator import ScopeValidationResult


class TestAuditLoggingIntegration:
    """Test SubagentStopHook logs scope violations to audit trail."""

    def test_hook_logs_scope_violation_to_audit_logger(self, tmp_path):
        """
        GIVEN ScopeValidator detects out-of-scope file modification
        WHEN SubagentStopHook.on_agent_complete() is called
        THEN SCOPE_VIOLATION event is logged to AuditLogger

        Business Context:
        Agent modified OrderService.py (out of scope) during UserRepository step.
        Hook must log this violation with event_type=SCOPE_VIOLATION, severity=WARNING,
        and include file path, step context, and allowed patterns for debugging.
        """
        # Arrange: Create step file with minimal valid structure
        step_file = tmp_path / "step.json"
        step_data = {
            "step_id": "01-01",
            "scope": {"allowed_patterns": ["**/UserRepository*"]},
            "tdd_cycle": {"phase_execution_log": []},
            "state": {"status": "IN_PROGRESS"},
        }
        step_file.write_text(json.dumps(step_data, indent=2))

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

        # Mock AuditLogger
        mock_audit_logger = Mock()

        with patch(
            "src.des.adapters.drivers.hooks.real_hook.ScopeValidator"
        ) as mock_validator_class:
            mock_validator_instance = Mock()
            mock_validator_instance.validate_scope.return_value = mock_scope_result
            mock_validator_class.return_value = mock_validator_instance

            with patch(
                "src.des.adapters.drivers.hooks.real_hook.get_audit_logger",
                return_value=mock_audit_logger,
            ):
                # Act: Call hook
                hook = RealSubagentStopHook()
                hook.on_agent_complete(str(step_file))

                # Assert: AuditLogger.append() called with SCOPE_VIOLATION event
                mock_audit_logger.append.assert_called_once()
                logged_event = mock_audit_logger.append.call_args[0][0]

                assert logged_event["event"] == "SCOPE_VIOLATION"
                assert logged_event["severity"] == "WARNING"
                assert logged_event["step_file"] == str(step_file)
                assert logged_event["out_of_scope_file"] == out_of_scope_file
                assert logged_event["allowed_patterns"] == ["**/UserRepository*"]

    def test_hook_logs_each_violation_separately(self, tmp_path):
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
        # Arrange: Create step file
        step_file = tmp_path / "step.json"
        step_data = {
            "step_id": "01-01",
            "scope": {"allowed_patterns": ["**/UserRepository*"]},
            "tdd_cycle": {"phase_execution_log": []},
            "state": {"status": "IN_PROGRESS"},
        }
        step_file.write_text(json.dumps(step_data, indent=2))

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

        mock_audit_logger = Mock()

        with patch(
            "src.des.adapters.drivers.hooks.real_hook.ScopeValidator"
        ) as mock_validator_class:
            mock_validator_instance = Mock()
            mock_validator_instance.validate_scope.return_value = mock_scope_result
            mock_validator_class.return_value = mock_validator_instance

            with patch(
                "src.des.adapters.drivers.hooks.real_hook.get_audit_logger",
                return_value=mock_audit_logger,
            ):
                # Act: Call hook
                hook = RealSubagentStopHook()
                hook.on_agent_complete(str(step_file))

                # Assert: AuditLogger.append() called 3 times (once per violation)
                assert mock_audit_logger.append.call_count == 3

                # Verify each call logged correct file
                for idx, out_of_scope_file in enumerate(out_of_scope_files):
                    logged_event = mock_audit_logger.append.call_args_list[idx][0][0]
                    assert logged_event["event"] == "SCOPE_VIOLATION"
                    assert logged_event["out_of_scope_file"] == out_of_scope_file

    def test_hook_does_not_log_when_no_violations(self, tmp_path):
        """
        GIVEN ScopeValidator finds no violations (all files in scope)
        WHEN SubagentStopHook.on_agent_complete() is called
        THEN no SCOPE_VIOLATION events are logged

        Business Context:
        Agent correctly modified only UserRepository.py and test_user_repository.py
        (both in allowed patterns). No audit events needed - work is compliant.
        """
        # Arrange: Create step file
        step_file = tmp_path / "step.json"
        step_data = {
            "step_id": "01-01",
            "scope": {"allowed_patterns": ["**/UserRepository*"]},
            "tdd_cycle": {"phase_execution_log": []},
            "state": {"status": "IN_PROGRESS"},
        }
        step_file.write_text(json.dumps(step_data, indent=2))

        # Mock ScopeValidator to return no violations
        mock_scope_result = ScopeValidationResult(
            has_violations=False,
            out_of_scope_files=[],
            violation_message="",
            violation_severity="",
            validation_skipped=False,
            reason="",
        )

        mock_audit_logger = Mock()

        with patch(
            "src.des.adapters.drivers.hooks.real_hook.ScopeValidator"
        ) as mock_validator_class:
            mock_validator_instance = Mock()
            mock_validator_instance.validate_scope.return_value = mock_scope_result
            mock_validator_class.return_value = mock_validator_instance

            with patch(
                "src.des.adapters.drivers.hooks.real_hook.get_audit_logger",
                return_value=mock_audit_logger,
            ):
                # Act: Call hook
                hook = RealSubagentStopHook()
                hook.on_agent_complete(str(step_file))

                # Assert: AuditLogger.append() NOT called
                mock_audit_logger.append.assert_not_called()

    def test_hook_includes_allowed_patterns_in_audit_event(self, tmp_path):
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
        # Arrange: Create step file with specific patterns
        step_file = tmp_path / "step.json"
        allowed_patterns = ["**/UserRepository*", "**/user_repository*"]
        step_data = {
            "step_id": "01-01",
            "scope": {"allowed_patterns": allowed_patterns},
            "tdd_cycle": {"phase_execution_log": []},
            "state": {"status": "IN_PROGRESS"},
        }
        step_file.write_text(json.dumps(step_data, indent=2))

        # Mock ScopeValidator to return violation
        mock_scope_result = ScopeValidationResult(
            has_violations=True,
            out_of_scope_files=["src/services/OrderService.py"],
            violation_message="Violation detected",
            violation_severity="WARNING",
            validation_skipped=False,
            reason="",
        )

        mock_audit_logger = Mock()

        with patch(
            "src.des.adapters.drivers.hooks.real_hook.ScopeValidator"
        ) as mock_validator_class:
            mock_validator_instance = Mock()
            mock_validator_instance.validate_scope.return_value = mock_scope_result
            mock_validator_class.return_value = mock_validator_instance

            with patch(
                "src.des.adapters.drivers.hooks.real_hook.get_audit_logger",
                return_value=mock_audit_logger,
            ):
                # Act: Call hook
                hook = RealSubagentStopHook()
                hook.on_agent_complete(str(step_file))

                # Assert: Audit event includes allowed_patterns
                logged_event = mock_audit_logger.append.call_args[0][0]
                assert logged_event["allowed_patterns"] == allowed_patterns
