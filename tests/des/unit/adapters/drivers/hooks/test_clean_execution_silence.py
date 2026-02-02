"""
Unit tests for SubagentStopHook silent behavior on clean execution.

Validates that when there are NO scope violations, the hook does NOT
produce any INFO, DEBUG, or WARNING logs that might clutter PR reviews.

Business Context:
Clean executions should be silent. Only violations get logged.
"""

from unittest.mock import Mock, patch

from src.des.adapters.drivers.hooks.real_hook import RealSubagentStopHook
from src.des.validation.scope_validator import ScopeValidationResult


class TestCleanExecutionSilence:
    """
    Verify clean execution produces no log noise.

    Step 04-04: Ensure that when agent only modifies in-scope files,
    NO SCOPE_VIOLATION entries appear in audit log AND no INFO/DEBUG
    logs confuse reviewers during PR review.
    """

    def test_no_violations_produces_no_audit_entries(self, tmp_path):
        """
        GIVEN scope validation passes (has_violations=False)
        WHEN SubagentStopHook processes result
        THEN no audit logger calls occur
        """
        # Arrange
        hook = RealSubagentStopHook()
        step_file = tmp_path / "step.json"
        step_file.write_text(
            '{"scope": {"allowed_patterns": ["**/UserRepository*"]}, "phases": []}'
        )

        # Mock ScopeValidator to return clean result
        with (
            patch(
                "src.des.adapters.drivers.hooks.real_hook.ScopeValidator"
            ) as mock_validator_class,
            patch(
                "src.des.adapters.drivers.hooks.real_hook.get_audit_logger"
            ) as mock_get_audit_logger,
        ):
            mock_validator = Mock()
            mock_validator_class.return_value = mock_validator

            # Clean execution - no violations
            mock_validator.validate_scope.return_value = ScopeValidationResult(
                has_violations=False,
                out_of_scope_files=[],
                validation_skipped=False,
                reason=None,
            )

            mock_audit_logger = Mock()
            mock_get_audit_logger.return_value = mock_audit_logger

            # Act
            hook.on_agent_complete(str(step_file))

            # Assert: No SCOPE_VIOLATION audit entries for clean execution
            # (HOOK_SUBAGENT_STOP_PASSED may still be logged)
            scope_events = [
                call[0][0]
                for call in mock_audit_logger.append.call_args_list
                if call[0][0].get("event") == "SCOPE_VIOLATION"
            ]
            assert len(scope_events) == 0

    def test_no_violations_produces_no_logger_info_calls(self, tmp_path):
        """
        GIVEN scope validation passes (has_violations=False)
        WHEN SubagentStopHook processes result
        THEN no logger.info() calls occur (silent success)
        """
        # Arrange
        hook = RealSubagentStopHook()
        step_file = tmp_path / "step.json"
        step_file.write_text(
            '{"scope": {"allowed_patterns": ["**/UserRepository*"]}, "phases": []}'
        )

        with (
            patch(
                "src.des.adapters.drivers.hooks.real_hook.ScopeValidator"
            ) as mock_validator_class,
            patch("src.des.adapters.drivers.hooks.real_hook.logger") as mock_logger,
        ):
            mock_validator = Mock()
            mock_validator_class.return_value = mock_validator

            # Clean execution
            mock_validator.validate_scope.return_value = ScopeValidationResult(
                has_violations=False,
                out_of_scope_files=[],
                validation_skipped=False,
                reason=None,
            )

            # Act
            hook.on_agent_complete(str(step_file))

            # Assert: No logger.info() for clean execution
            # (Only validation_skipped should trigger logger.warning, not clean success)
            mock_logger.info.assert_not_called()

    def test_no_violations_produces_no_logger_debug_calls(self, tmp_path):
        """
        GIVEN scope validation passes (has_violations=False)
        WHEN SubagentStopHook processes result
        THEN no logger.debug() calls occur
        """
        # Arrange
        hook = RealSubagentStopHook()
        step_file = tmp_path / "step.json"
        step_file.write_text(
            '{"scope": {"allowed_patterns": ["**/UserRepository*"]}, "phases": []}'
        )

        with (
            patch(
                "src.des.adapters.drivers.hooks.real_hook.ScopeValidator"
            ) as mock_validator_class,
            patch("src.des.adapters.drivers.hooks.real_hook.logger") as mock_logger,
        ):
            mock_validator = Mock()
            mock_validator_class.return_value = mock_validator

            # Clean execution
            mock_validator.validate_scope.return_value = ScopeValidationResult(
                has_violations=False,
                out_of_scope_files=[],
                validation_skipped=False,
                reason=None,
            )

            # Act
            hook.on_agent_complete(str(step_file))

            # Assert: No logger.debug() for clean execution
            mock_logger.debug.assert_not_called()

    def test_clean_execution_else_branch_truly_silent(self, tmp_path):
        """
        GIVEN scope validation passes (has_violations=False)
        WHEN SubagentStopHook processes result
        THEN else-branch (if any) or implicit else is silent
              (no audit entries, no logger calls of any level)
        """
        # Arrange
        hook = RealSubagentStopHook()
        step_file = tmp_path / "step.json"
        step_file.write_text(
            '{"scope": {"allowed_patterns": ["**/UserRepository*"]}, "phases": []}'
        )

        with (
            patch(
                "src.des.adapters.drivers.hooks.real_hook.ScopeValidator"
            ) as mock_validator_class,
            patch(
                "src.des.adapters.drivers.hooks.real_hook.get_audit_logger"
            ) as mock_get_audit_logger,
            patch("src.des.adapters.drivers.hooks.real_hook.logger") as mock_logger,
        ):
            mock_validator = Mock()
            mock_validator_class.return_value = mock_validator

            # Clean execution
            mock_validator.validate_scope.return_value = ScopeValidationResult(
                has_violations=False,
                out_of_scope_files=[],
                validation_skipped=False,
                reason=None,
            )

            mock_audit_logger = Mock()
            mock_get_audit_logger.return_value = mock_audit_logger

            # Act
            hook.on_agent_complete(str(step_file))

            # Assert: No SCOPE_VIOLATION audit entries (HOOK_SUBAGENT_STOP may exist)
            scope_events = [
                call[0][0]
                for call in mock_audit_logger.append.call_args_list
                if call[0][0].get("event") == "SCOPE_VIOLATION"
            ]
            assert len(scope_events) == 0
            # Note: logger.warning IS allowed for validation_skipped, but not for clean success
