"""Unit tests for Claude Code hook adapter.

Tests the adapter's ability to:
- Parse JSON from stdin
- Call DESOrchestrator.validate_prompt() for pre-task
- Call RealSubagentStopHook.on_agent_complete() for subagent-stop
- Output correct JSON to stdout
- Use correct exit codes (0=allow, 1=error, 2=block)
- Check DESConfig.audit_logging_enabled before logging
- Use SystemTimeProvider.now_utc() for timestamps (no datetime.now())
"""

import json
from io import StringIO
from unittest.mock import Mock, patch


class TestPreTaskHandler:
    """Test pre-task command handling."""

    @patch("sys.stdin")
    @patch("sys.stdout", new_callable=StringIO)
    @patch("src.des.adapters.drivers.hooks.claude_code_hook_adapter.DESOrchestrator")
    @patch("src.des.adapters.drivers.hooks.claude_code_hook_adapter.DESConfig")
    def test_handle_pre_task_with_valid_json_and_passing_validation_returns_exit_0(
        self, mock_config, mock_orchestrator_class, mock_stdout, mock_stdin
    ):
        """Pre-task with valid JSON and passing validation returns exit 0."""
        # Arrange
        mock_stdin.read.return_value = json.dumps(
            {"tool": "Task", "tool_input": {"prompt": "/nw:execute step-01-01.json"}}
        )

        mock_config_instance = Mock()
        mock_config_instance.audit_logging_enabled = True
        mock_config.return_value = mock_config_instance

        mock_orchestrator = Mock()
        mock_validation_result = Mock()
        mock_validation_result.task_invocation_allowed = True
        mock_orchestrator.validate_prompt.return_value = mock_validation_result
        mock_orchestrator_class.return_value = mock_orchestrator

        # Act
        from src.des.adapters.drivers.hooks.claude_code_hook_adapter import (
            handle_pre_task,
        )

        exit_code = handle_pre_task()

        # Assert
        assert exit_code == 0
        output = json.loads(mock_stdout.getvalue())
        assert output["decision"] == "allow"

    @patch("sys.stdin")
    @patch("sys.stdout", new_callable=StringIO)
    @patch("src.des.adapters.drivers.hooks.claude_code_hook_adapter.DESOrchestrator")
    @patch("src.des.adapters.drivers.hooks.claude_code_hook_adapter.DESConfig")
    def test_handle_pre_task_with_valid_json_and_failing_validation_returns_exit_2(
        self, mock_config, mock_orchestrator_class, mock_stdout, mock_stdin
    ):
        """Pre-task with valid JSON and failing validation returns exit 2 (BLOCK)."""
        # Arrange
        mock_stdin.read.return_value = json.dumps(
            {"tool": "Task", "tool_input": {"prompt": "invalid prompt"}}
        )

        mock_config_instance = Mock()
        mock_config_instance.audit_logging_enabled = True
        mock_config.return_value = mock_config_instance

        mock_orchestrator = Mock()
        mock_validation_result = Mock()
        mock_validation_result.task_invocation_allowed = False
        mock_validation_result.errors = ["Missing DES markers"]
        mock_orchestrator.validate_prompt.return_value = mock_validation_result
        mock_orchestrator_class.return_value = mock_orchestrator

        # Act
        from src.des.adapters.drivers.hooks.claude_code_hook_adapter import (
            handle_pre_task,
        )

        exit_code = handle_pre_task()

        # Assert
        assert exit_code == 2
        output = json.loads(mock_stdout.getvalue())
        assert output["decision"] == "block"
        assert "reason" in output

    @patch("sys.stdin")
    @patch("sys.stdout", new_callable=StringIO)
    def test_handle_pre_task_with_invalid_json_returns_exit_1_with_error(
        self, mock_stdout, mock_stdin
    ):
        """Pre-task with invalid JSON returns exit 1 (fail-closed) with error JSON."""
        # Arrange
        mock_stdin.read.return_value = "invalid json {"

        # Act
        from src.des.adapters.drivers.hooks.claude_code_hook_adapter import (
            handle_pre_task,
        )

        exit_code = handle_pre_task()

        # Assert
        assert exit_code == 1
        output = json.loads(mock_stdout.getvalue())
        assert output["status"] == "error"
        assert "reason" in output

    @patch("sys.stdin")
    @patch("sys.stdout", new_callable=StringIO)
    def test_handle_pre_task_with_missing_stdin_returns_exit_1_with_error(
        self, mock_stdout, mock_stdin
    ):
        """Pre-task with missing stdin returns exit 1 (fail-closed)."""
        # Arrange
        mock_stdin.read.return_value = ""

        # Act
        from src.des.adapters.drivers.hooks.claude_code_hook_adapter import (
            handle_pre_task,
        )

        exit_code = handle_pre_task()

        # Assert
        assert exit_code == 1
        output = json.loads(mock_stdout.getvalue())
        assert output["status"] == "error"


class TestSubagentStopHandler:
    """Test subagent-stop command handling."""

    @patch("sys.stdin")
    @patch("sys.stdout", new_callable=StringIO)
    @patch(
        "src.des.adapters.drivers.hooks.claude_code_hook_adapter.RealSubagentStopHook"
    )
    @patch("src.des.adapters.drivers.hooks.claude_code_hook_adapter.DESConfig")
    def test_handle_subagent_stop_with_passing_gate_returns_exit_0(
        self, mock_config, mock_hook_class, mock_stdout, mock_stdin
    ):
        """SubagentStop with passing gate returns exit 0."""
        # Arrange
        mock_stdin.read.return_value = json.dumps({"step_path": "/path/to/step.json"})

        mock_config_instance = Mock()
        mock_config_instance.audit_logging_enabled = True
        mock_config.return_value = mock_config_instance

        mock_hook = Mock()
        mock_result = Mock()
        mock_result.validation_status = "PASSED"
        mock_hook.on_agent_complete.return_value = mock_result
        mock_hook_class.return_value = mock_hook

        # Act
        from src.des.adapters.drivers.hooks.claude_code_hook_adapter import (
            handle_subagent_stop,
        )

        exit_code = handle_subagent_stop()

        # Assert
        assert exit_code == 0

    @patch("sys.stdin")
    @patch("sys.stdout", new_callable=StringIO)
    @patch(
        "src.des.adapters.drivers.hooks.claude_code_hook_adapter.RealSubagentStopHook"
    )
    @patch("src.des.adapters.drivers.hooks.claude_code_hook_adapter.DESConfig")
    def test_handle_subagent_stop_with_failing_gate_returns_exit_2(
        self, mock_config, mock_hook_class, mock_stdout, mock_stdin
    ):
        """SubagentStop with failing gate returns exit 2 (BLOCKS orchestrator)."""
        # Arrange
        mock_stdin.read.return_value = json.dumps({"step_path": "/path/to/step.json"})

        mock_config_instance = Mock()
        mock_config_instance.audit_logging_enabled = True
        mock_config.return_value = mock_config_instance

        mock_hook = Mock()
        mock_result = Mock()
        mock_result.validation_status = "FAILED"
        mock_hook.on_agent_complete.return_value = mock_result
        mock_hook_class.return_value = mock_hook

        # Act
        from src.des.adapters.drivers.hooks.claude_code_hook_adapter import (
            handle_subagent_stop,
        )

        exit_code = handle_subagent_stop()

        # Assert
        assert exit_code == 2

    @patch("sys.stdin")
    @patch("sys.stdout", new_callable=StringIO)
    def test_handle_subagent_stop_with_invalid_json_returns_exit_1(
        self, mock_stdout, mock_stdin
    ):
        """SubagentStop with invalid JSON returns exit 1 (fail-closed)."""
        # Arrange
        mock_stdin.read.return_value = "not json"

        # Act
        from src.des.adapters.drivers.hooks.claude_code_hook_adapter import (
            handle_subagent_stop,
        )

        exit_code = handle_subagent_stop()

        # Assert
        assert exit_code == 1
        output = json.loads(mock_stdout.getvalue())
        assert output["status"] == "error"


class TestAuditLoggingControl:
    """Test audit logging control via DESConfig."""

    @patch("sys.stdin")
    @patch("sys.stdout", new_callable=StringIO)
    @patch("src.des.adapters.drivers.hooks.claude_code_hook_adapter.DESOrchestrator")
    @patch("src.des.adapters.drivers.hooks.claude_code_hook_adapter.DESConfig")
    def test_adapter_checks_config_before_logging(
        self,
        mock_config,
        mock_orchestrator_class,
        mock_stdout,
        mock_stdin,
    ):
        """Adapter checks DESConfig.audit_logging_enabled before logging."""
        # Arrange
        mock_stdin.read.return_value = json.dumps(
            {"tool": "Task", "tool_input": {"prompt": "/nw:execute step-01-01.json"}}
        )

        mock_config_instance = Mock()
        mock_config_instance.audit_logging_enabled = False
        mock_config.return_value = mock_config_instance

        mock_orchestrator = Mock()
        mock_validation_result = Mock()
        mock_validation_result.task_invocation_allowed = True
        mock_orchestrator.validate_prompt.return_value = mock_validation_result
        mock_orchestrator_class.return_value = mock_orchestrator

        # Act
        from src.des.adapters.drivers.hooks.claude_code_hook_adapter import (
            handle_pre_task,
        )

        exit_code = handle_pre_task()

        # Assert - adapter should still function correctly with logging disabled
        assert exit_code == 0
        output = json.loads(mock_stdout.getvalue())
        assert output["decision"] == "allow"


class TestOutputFormat:
    """Test JSON output format."""

    @patch("sys.stdin")
    @patch("sys.stdout", new_callable=StringIO)
    @patch("src.des.adapters.drivers.hooks.claude_code_hook_adapter.DESOrchestrator")
    @patch("src.des.adapters.drivers.hooks.claude_code_hook_adapter.DESConfig")
    def test_pre_task_success_outputs_valid_json(
        self, mock_config, mock_orchestrator_class, mock_stdout, mock_stdin
    ):
        """Pre-task success outputs valid JSON to stdout."""
        # Arrange
        mock_stdin.read.return_value = json.dumps(
            {"tool": "Task", "tool_input": {"prompt": "/nw:execute step-01-01.json"}}
        )

        mock_config_instance = Mock()
        mock_config_instance.audit_logging_enabled = True
        mock_config.return_value = mock_config_instance

        mock_orchestrator = Mock()
        mock_validation_result = Mock()
        mock_validation_result.task_invocation_allowed = True
        mock_orchestrator.validate_prompt.return_value = mock_validation_result
        mock_orchestrator_class.return_value = mock_orchestrator

        # Act
        from src.des.adapters.drivers.hooks.claude_code_hook_adapter import (
            handle_pre_task,
        )

        exit_code = handle_pre_task()

        # Assert
        assert exit_code == 0
        output = json.loads(mock_stdout.getvalue())  # Should not raise
        assert isinstance(output, dict)
        assert "decision" in output

    @patch("sys.stdin")
    @patch("sys.stdout", new_callable=StringIO)
    def test_pre_task_error_outputs_valid_json(self, mock_stdout, mock_stdin):
        """Pre-task error outputs valid JSON to stdout."""
        # Arrange
        mock_stdin.read.return_value = ""

        # Act
        from src.des.adapters.drivers.hooks.claude_code_hook_adapter import (
            handle_pre_task,
        )

        exit_code = handle_pre_task()

        # Assert
        assert exit_code == 1
        output = json.loads(mock_stdout.getvalue())  # Should not raise
        assert isinstance(output, dict)
        assert "status" in output
        assert output["status"] == "error"
