"""Unit tests for scope validation integration in SubagentStopHook.

Business Context:
SubagentStopHook must invoke ScopeValidator after agent completion to detect
out-of-scope file modifications. Validation results are stored for audit logging
in Phase 4.

Test Strategy:
- Test hook invokes ScopeValidator.validate_scope() post-execution
- Test validation runs automatically without user interaction
- Test git diff failure logged as WARNING, doesn't block step completion
- Test validation_skipped=True allows step to complete with WARNING log
"""

import json
from unittest.mock import patch


from src.des.adapters.drivers.hooks.real_hook import RealSubagentStopHook
from src.des.validation.scope_validator import ScopeValidationResult


class TestScopeValidationIntegration:
    """Tests for scope validation integration in SubagentStopHook."""

    def test_hook_invokes_scope_validator_post_execution(self, tmp_path):
        """
        GIVEN SubagentStopHook completes agent execution
        WHEN on_agent_complete() is called
        THEN ScopeValidator.validate_scope() is invoked automatically

        Business Context:
        Priya needs automatic scope validation after every agent execution
        to catch out-of-scope modifications before PR review.
        """
        # Arrange: Create step file with scope definition
        step_file = tmp_path / "step.json"
        step_data = {
            "task_id": "01-01",
            "state": {"status": "DONE"},
            "tdd_cycle": {"phase_execution_log": []},
            "scope": {"allowed_patterns": ["**/UserRepository*"]},
        }
        step_file.write_text(json.dumps(step_data, indent=2))

        # Act: Invoke hook with mocked ScopeValidator
        hook = RealSubagentStopHook()

        with patch(
            "src.des.adapters.drivers.hooks.real_hook.ScopeValidator"
        ) as MockValidator:
            mock_validator_instance = MockValidator.return_value
            mock_validator_instance.validate_scope.return_value = ScopeValidationResult(
                has_violations=False
            )

            hook.on_agent_complete(str(step_file))

            # Assert: ScopeValidator.validate_scope() was called
            MockValidator.assert_called_once()
            mock_validator_instance.validate_scope.assert_called_once_with(
                step_file_path=str(step_file),
                project_root=tmp_path.parent,
                git_diff_files=None,
            )

    def test_validation_runs_without_user_interaction(self, tmp_path):
        """
        GIVEN SubagentStopHook completes execution
        WHEN on_agent_complete() is called
        THEN validation runs automatically without requiring user input

        Business Context:
        Automatic validation ensures no manual step needed - reduces
        human error and provides immediate feedback.
        """
        # Arrange
        step_file = tmp_path / "step.json"
        step_data = {
            "task_id": "01-01",
            "state": {"status": "DONE"},
            "tdd_cycle": {"phase_execution_log": []},
            "scope": {"allowed_patterns": ["**/UserRepository*"]},
        }
        step_file.write_text(json.dumps(step_data, indent=2))

        # Act: No user interaction needed - just call hook
        hook = RealSubagentStopHook()

        with patch(
            "src.des.adapters.drivers.hooks.real_hook.ScopeValidator"
        ) as MockValidator:
            mock_validator_instance = MockValidator.return_value
            mock_validator_instance.validate_scope.return_value = ScopeValidationResult(
                has_violations=False
            )

            result = hook.on_agent_complete(str(step_file))

            # Assert: Hook completes successfully without user interaction
            assert result is not None
            assert result.validation_status == "PASSED"
            mock_validator_instance.validate_scope.assert_called_once()

    def test_git_diff_failure_logged_as_warning_doesnt_block_completion(self, tmp_path):
        """
        GIVEN git diff command times out or fails
        WHEN SubagentStopHook validates scope
        THEN WARNING is logged and step completion is NOT blocked

        Business Context:
        Git failures shouldn't prevent agent completion - validation is
        best-effort. Priya will see WARNING in logs but can still proceed.

        Error Handling:
        ScopeValidator returns validation_skipped=True on git failure.
        Hook logs WARNING but returns validation_status="PASSED".
        """
        # Arrange: Create step file
        step_file = tmp_path / "step.json"
        step_data = {
            "task_id": "01-01",
            "state": {"status": "DONE"},
            "tdd_cycle": {"phase_execution_log": []},
            "scope": {"allowed_patterns": ["**/UserRepository*"]},
        }
        step_file.write_text(json.dumps(step_data, indent=2))

        # Act: ScopeValidator returns validation_skipped=True (git failure)
        hook = RealSubagentStopHook()

        with patch(
            "src.des.adapters.drivers.hooks.real_hook.ScopeValidator"
        ) as MockValidator:
            with patch(
                "src.des.adapters.drivers.hooks.real_hook.logger"
            ) as mock_logger:
                mock_validator_instance = MockValidator.return_value
                mock_validator_instance.validate_scope.return_value = (
                    ScopeValidationResult(
                        has_violations=False,
                        validation_skipped=True,
                        reason="Git command timeout after 5 seconds",
                    )
                )

                result = hook.on_agent_complete(str(step_file))

                # Assert: WARNING logged but step completes successfully
                mock_logger.warning.assert_called_once()
                warning_call = mock_logger.warning.call_args[0][0]
                assert "Scope validation skipped" in warning_call
                assert "Git command timeout" in warning_call

                # Step completion NOT blocked
                assert result.validation_status == "PASSED"

    def test_validation_skipped_allows_step_completion_with_warning_log(self, tmp_path):
        """
        GIVEN ScopeValidator returns validation_skipped=True
        WHEN SubagentStopHook processes result
        THEN step completes normally with WARNING log entry

        Business Context:
        When git is unavailable (CI environment without git), validation
        is skipped but work continues. Priya sees WARNING in logs.
        """
        # Arrange
        step_file = tmp_path / "step.json"
        step_data = {
            "task_id": "01-01",
            "state": {"status": "DONE"},
            "tdd_cycle": {"phase_execution_log": []},
            "scope": {"allowed_patterns": ["**/UserRepository*"]},
        }
        step_file.write_text(json.dumps(step_data, indent=2))

        # Act
        hook = RealSubagentStopHook()

        with patch(
            "src.des.adapters.drivers.hooks.real_hook.ScopeValidator"
        ) as MockValidator:
            with patch(
                "src.des.adapters.drivers.hooks.real_hook.logger"
            ) as mock_logger:
                mock_validator_instance = MockValidator.return_value
                mock_validator_instance.validate_scope.return_value = (
                    ScopeValidationResult(
                        has_violations=False,
                        validation_skipped=True,
                        reason="Git command unavailable in environment",
                    )
                )

                result = hook.on_agent_complete(str(step_file))

                # Assert: WARNING logged with specific reason
                mock_logger.warning.assert_called_once()
                warning_call = mock_logger.warning.call_args[0][0]
                assert "validation skipped" in warning_call.lower()
                assert "unavailable in environment" in warning_call.lower()

                # Step completes normally
                assert result.validation_status == "PASSED"

    def test_validation_result_stored_for_audit_logging(self, tmp_path):
        """
        GIVEN scope validation completes (with or without violations)
        WHEN SubagentStopHook processes result
        THEN validation result is stored in HookResult for Phase 4 audit logging

        Business Context:
        Validation results need to be preserved for audit trail in Phase 4.
        HookResult should contain scope_validation_result field.

        Implementation Note:
        This test drives the need for scope_validation_result field in HookResult.
        Phase 4 will use this field for audit logging.
        """
        # Arrange
        step_file = tmp_path / "step.json"
        step_data = {
            "task_id": "01-01",
            "state": {"status": "DONE"},
            "tdd_cycle": {"phase_execution_log": []},
            "scope": {"allowed_patterns": ["**/UserRepository*"]},
        }
        step_file.write_text(json.dumps(step_data, indent=2))

        # Act: Run validation with violations
        hook = RealSubagentStopHook()

        with patch(
            "src.des.adapters.drivers.hooks.real_hook.ScopeValidator"
        ) as MockValidator:
            mock_validator_instance = MockValidator.return_value
            expected_result = ScopeValidationResult(
                has_violations=True,
                out_of_scope_files=["src/services/OrderService.py"],
                violation_message="Out-of-scope file modified: OrderService.py",
                violation_severity="WARNING",
            )
            mock_validator_instance.validate_scope.return_value = expected_result

            result = hook.on_agent_complete(str(step_file))

            # Assert: Validation result stored in HookResult
            assert hasattr(result, "scope_validation_result")
            assert result.scope_validation_result == expected_result
            assert result.scope_validation_result.has_violations is True
            assert len(result.scope_validation_result.out_of_scope_files) == 1
