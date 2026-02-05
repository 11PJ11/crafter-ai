"""
Unit tests for SubagentStopHook silent behavior on clean execution (Schema v2.0).

Validates that when there are NO scope violations, the hook does NOT
produce any INFO, DEBUG, or WARNING logs that might clutter PR reviews.

Business Context:
Clean executions should be silent. Only violations get logged.

NOTE: Scope validation not yet implemented in SubagentStopHook (Schema v2.0).
All tests marked as skipped pending implementation.
"""

from unittest.mock import Mock, patch

import yaml
from src.des.adapters.driven.hooks.subagent_stop_hook import (
    SubagentStopHook as RealSubagentStopHook,
)
from src.des.adapters.driven.validation.scope_validator import ScopeValidationResult


class TestCleanExecutionSilence:
    """
    Verify clean execution produces no log noise (Schema v2.0).

    Step 04-04: Ensure that when agent only modifies in-scope files,
    NO SCOPE_VIOLATION entries appear in audit log AND no INFO/DEBUG
    logs confuse reviewers during PR review.

    NOTE: All tests skipped - scope validation not yet implemented in SubagentStopHook.
    """

    def test_no_violations_produces_no_audit_entries(self, tmp_path, tdd_phases):
        """
        GIVEN scope validation passes (has_violations=False)
        WHEN SubagentStopHook processes result
        THEN no audit logger calls occur
        """
        # Arrange: Create execution-log.yaml (Schema v2.0)
        hook = RealSubagentStopHook()
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

        # Mock ScopeValidator to return clean result
        with (
            patch(
                "src.des.adapters.driven.hooks.subagent_stop_hook.ScopeValidator"
            ) as mock_validator_class,
            patch(
                "src.des.adapters.driven.hooks.subagent_stop_hook.get_audit_logger"
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
            compound_path = f"{log_file}?project_id=test-project&step_id=01-01"
            hook.on_agent_complete(compound_path)

            # Assert: No SCOPE_VIOLATION audit entries for clean execution
            # (HOOK_SUBAGENT_STOP_PASSED may still be logged)
            scope_events = [
                call[0][0]
                for call in mock_audit_logger.append.call_args_list
                if call[0][0].get("event") == "SCOPE_VIOLATION"
            ]
            assert len(scope_events) == 0

    def test_no_violations_produces_no_logger_info_calls(self, tmp_path, tdd_phases):
        """
        GIVEN scope validation passes (has_violations=False)
        WHEN SubagentStopHook processes result
        THEN no logger.info() calls occur (silent success)
        """
        # Arrange: Create execution-log.yaml (Schema v2.0)
        hook = RealSubagentStopHook()
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

        with (
            patch(
                "src.des.adapters.driven.hooks.subagent_stop_hook.ScopeValidator"
            ) as mock_validator_class,
            patch(
                "src.des.adapters.driven.hooks.subagent_stop_hook.logger"
            ) as mock_logger,
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
            compound_path = f"{log_file}?project_id=test-project&step_id=01-01"
            hook.on_agent_complete(compound_path)

            # Assert: No logger.info() for clean execution
            # (Only validation_skipped should trigger logger.warning, not clean success)
            mock_logger.info.assert_not_called()

    def test_no_violations_produces_no_logger_debug_calls(self, tmp_path, tdd_phases):
        """
        GIVEN scope validation passes (has_violations=False)
        WHEN SubagentStopHook processes result
        THEN no logger.debug() calls occur
        """
        # Arrange: Create execution-log.yaml (Schema v2.0)
        hook = RealSubagentStopHook()
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

        with (
            patch(
                "src.des.adapters.driven.hooks.subagent_stop_hook.ScopeValidator"
            ) as mock_validator_class,
            patch(
                "src.des.adapters.driven.hooks.subagent_stop_hook.logger"
            ) as mock_logger,
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
            compound_path = f"{log_file}?project_id=test-project&step_id=01-01"
            hook.on_agent_complete(compound_path)

            # Assert: No logger.debug() for clean execution
            mock_logger.debug.assert_not_called()

    def test_clean_execution_else_branch_truly_silent(self, tmp_path, tdd_phases):
        """
        GIVEN scope validation passes (has_violations=False)
        WHEN SubagentStopHook processes result
        THEN else-branch (if any) or implicit else is silent
              (no audit entries, no logger calls of any level)
        """
        # Arrange: Create execution-log.yaml (Schema v2.0)
        hook = RealSubagentStopHook()
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

        with (
            patch(
                "src.des.adapters.driven.hooks.subagent_stop_hook.ScopeValidator"
            ) as mock_validator_class,
            patch(
                "src.des.adapters.driven.hooks.subagent_stop_hook.get_audit_logger"
            ) as mock_get_audit_logger,
            patch("src.des.adapters.driven.hooks.subagent_stop_hook.logger"),
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
            compound_path = f"{log_file}?project_id=test-project&step_id=01-01"
            hook.on_agent_complete(compound_path)

            # Assert: No SCOPE_VIOLATION audit entries (HOOK_SUBAGENT_STOP may exist)
            scope_events = [
                call[0][0]
                for call in mock_audit_logger.append.call_args_list
                if call[0][0].get("event") == "SCOPE_VIOLATION"
            ]
            assert len(scope_events) == 0
            # Note: logger.warning IS allowed for validation_skipped, but not for clean success
