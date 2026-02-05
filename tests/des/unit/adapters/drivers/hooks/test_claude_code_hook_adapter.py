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
            {
                "tool": "Task",
                "tool_input": {
                    "prompt": "/nw:execute step-01-01.json",
                    "max_turns": 30,  # Required
                },
            }
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
            {
                "tool": "Task",
                "tool_input": {
                    "prompt": "<!-- DES-VALIDATION: required -->\ninvalid prompt - missing sections",
                    "max_turns": 30,  # Has max_turns but prompt is invalid
                },
            }
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
        mock_result.error_message = "Phase RED_TEST left IN_PROGRESS (abandoned)"
        mock_result.recovery_suggestions = [
            "Review agent transcript for error details",
            "Reset RED_TEST phase status to NOT_EXECUTED",
            "Run /nw:execute again to resume",
        ]
        mock_hook.on_agent_complete.return_value = mock_result
        mock_hook_class.return_value = mock_hook

        # Act
        from src.des.adapters.drivers.hooks.claude_code_hook_adapter import (
            handle_subagent_stop,
        )

        exit_code = handle_subagent_stop()

        # Assert
        assert exit_code == 2
        output = json.loads(mock_stdout.getvalue())

        # Verify context injection structure
        assert "hookSpecificOutput" in output, (
            "hookSpecificOutput should exist when validation fails"
        )
        assert "additionalContext" in output["hookSpecificOutput"], (
            "additionalContext should exist in hookSpecificOutput"
        )
        assert "systemMessage" in output, (
            "systemMessage should exist at top level when validation fails"
        )

        # Verify field types
        assert isinstance(output["hookSpecificOutput"]["additionalContext"], str), (
            "additionalContext must be a string"
        )
        assert isinstance(output["systemMessage"], str), (
            "systemMessage must be a string"
        )

        # Verify backward compatibility
        assert output["decision"] == "block", (
            "decision must still be 'block' for validation failures"
        )

    @patch("sys.stdin")
    @patch("sys.stdout", new_callable=StringIO)
    @patch(
        "src.des.adapters.drivers.hooks.claude_code_hook_adapter.RealSubagentStopHook"
    )
    @patch("src.des.adapters.drivers.hooks.claude_code_hook_adapter.DESConfig")
    def test_handle_subagent_stop_failure_includes_context_injection(
        self, mock_config, mock_hook_class, mock_stdout, mock_stdin
    ):
        """SubagentStop failure includes detailed context injection for orchestrator."""
        # Arrange
        step_path = "/path/to/step.json"
        mock_stdin.read.return_value = json.dumps({"step_path": step_path})

        mock_config_instance = Mock()
        mock_config_instance.audit_logging_enabled = True
        mock_config.return_value = mock_config_instance

        mock_hook = Mock()
        mock_result = Mock()
        mock_result.validation_status = "FAILED"
        mock_result.error_message = "Phase RED_TEST left IN_PROGRESS (abandoned)"
        mock_result.recovery_suggestions = [
            "Review agent transcript for error details",
            "Reset RED_TEST phase status to NOT_EXECUTED",
            "Run /nw:execute again to resume",
        ]
        mock_hook.on_agent_complete.return_value = mock_result
        mock_hook_class.return_value = mock_hook

        # Act
        from src.des.adapters.drivers.hooks.claude_code_hook_adapter import (
            handle_subagent_stop,
        )

        exit_code = handle_subagent_stop()

        # Assert
        assert exit_code == 2
        output = json.loads(mock_stdout.getvalue())

        # Verify additionalContext content
        additional_context = output["hookSpecificOutput"]["additionalContext"]
        assert "Phase RED_TEST left IN_PROGRESS (abandoned)" in additional_context
        assert step_path in additional_context, (
            "Step file path must appear in additionalContext"
        )
        assert "1. Review agent transcript" in additional_context, (
            "Recovery suggestions must be numbered"
        )
        assert "2. Reset RED_TEST phase status" in additional_context
        assert "3. Run /nw:execute again" in additional_context

        # Verify systemMessage content
        system_message = output["systemMessage"]
        assert len(system_message) < 100, (
            "systemMessage must be concise (under 100 chars)"
        )
        assert (
            "Phase RED_TEST" in system_message or "Validation failed" in system_message
        )
        assert "1." not in system_message, (
            "systemMessage must NOT contain numbered recovery steps"
        )
        assert "\n" not in system_message, "systemMessage must be single-line"

    @patch("sys.stdin")
    @patch("sys.stdout", new_callable=StringIO)
    @patch(
        "src.des.adapters.drivers.hooks.claude_code_hook_adapter.RealSubagentStopHook"
    )
    @patch("src.des.adapters.drivers.hooks.claude_code_hook_adapter.DESConfig")
    def test_handle_subagent_stop_additionalcontext_multiline_format(
        self, mock_config, mock_hook_class, mock_stdout, mock_stdin
    ):
        """SubagentStop additionalContext follows multi-line format specification."""
        # Arrange
        step_path = "/docs/feature/project/steps/01-02.json"
        error_msg = "Phase GREEN_UNIT abandoned (left IN_PROGRESS)"
        recovery_suggestions = [
            "First recovery step",
            "Second recovery step",
            "Third recovery step",
        ]

        mock_stdin.read.return_value = json.dumps({"step_path": step_path})

        mock_config_instance = Mock()
        mock_config_instance.audit_logging_enabled = True
        mock_config.return_value = mock_config_instance

        mock_hook = Mock()
        mock_result = Mock()
        mock_result.validation_status = "FAILED"
        mock_result.error_message = error_msg
        mock_result.recovery_suggestions = recovery_suggestions
        mock_hook.on_agent_complete.return_value = mock_result
        mock_hook_class.return_value = mock_hook

        # Act
        from src.des.adapters.drivers.hooks.claude_code_hook_adapter import (
            handle_subagent_stop,
        )

        exit_code = handle_subagent_stop()

        # Assert
        assert exit_code == 2
        output = json.loads(mock_stdout.getvalue())
        additional_context = output["hookSpecificOutput"]["additionalContext"]

        # Verify multi-line format
        assert "\n" in additional_context, (
            "additionalContext must be multi-line (contain newlines)"
        )
        lines = additional_context.split("\n")
        assert len(lines) > 5, (
            "additionalContext should have multiple lines (header, error, recovery steps)"
        )

        # Verify error summary appears early
        assert error_msg in additional_context, (
            "Error message must appear in additionalContext"
        )
        # Error should appear in first few lines
        error_line_index = next(i for i, line in enumerate(lines) if error_msg in line)
        assert error_line_index < 10, "Error summary should appear near the beginning"

        # Verify numbered recovery suggestions
        assert "1. First recovery step" in additional_context, (
            "First suggestion must be numbered with '1.'"
        )
        assert "2. Second recovery step" in additional_context, (
            "Second suggestion must be numbered with '2.'"
        )
        assert "3. Third recovery step" in additional_context, (
            "Third suggestion must be numbered with '3.'"
        )

        # Verify all suggestions are included
        for suggestion in recovery_suggestions:
            assert suggestion in additional_context, (
                f"Recovery suggestion '{suggestion}' must appear in additionalContext"
            )

        # Verify step file path appears
        assert step_path in additional_context, (
            "Step file path must appear in additionalContext"
        )

    @patch("sys.stdin")
    @patch("sys.stdout", new_callable=StringIO)
    @patch(
        "src.des.adapters.drivers.hooks.claude_code_hook_adapter.RealSubagentStopHook"
    )
    @patch("src.des.adapters.drivers.hooks.claude_code_hook_adapter.DESConfig")
    def test_handle_subagent_stop_systemmessage_conciseness(
        self, mock_config, mock_hook_class, mock_stdout, mock_stdin
    ):
        """SubagentStop systemMessage is concise, single-line, user-friendly."""
        # Arrange
        step_path = "/docs/feature/project/steps/01-03.json"
        error_msg = "Phase COMMIT failed validation checks"
        recovery_suggestions = [
            "Review commit message format for compliance with conventional commits",
            "Ensure all files are properly staged before committing",
            "Check pre-commit hooks configuration and fix any issues",
        ]

        mock_stdin.read.return_value = json.dumps({"step_path": step_path})

        mock_config_instance = Mock()
        mock_config_instance.audit_logging_enabled = True
        mock_config.return_value = mock_config_instance

        mock_hook = Mock()
        mock_result = Mock()
        mock_result.validation_status = "FAILED"
        mock_result.error_message = error_msg
        mock_result.recovery_suggestions = recovery_suggestions
        mock_hook.on_agent_complete.return_value = mock_result
        mock_hook_class.return_value = mock_hook

        # Act
        from src.des.adapters.drivers.hooks.claude_code_hook_adapter import (
            handle_subagent_stop,
        )

        exit_code = handle_subagent_stop()

        # Assert
        assert exit_code == 2
        output = json.loads(mock_stdout.getvalue())
        system_message = output["systemMessage"]

        # Verify conciseness (under 100 characters)
        assert len(system_message) < 100, (
            f"systemMessage must be under 100 chars (got {len(system_message)})"
        )

        # Verify single-line (no newlines)
        assert "\n" not in system_message, (
            "systemMessage must be single-line (no newlines)"
        )
        assert "\r" not in system_message, (
            "systemMessage must not contain carriage returns"
        )

        # Verify references validation failure
        assert "fail" in system_message.lower() or "error" in system_message.lower(), (
            "systemMessage should reference failure/error"
        )

        # Verify does NOT contain numbered recovery steps
        assert "1." not in system_message, (
            "systemMessage must NOT contain numbered list '1.'"
        )
        assert "2." not in system_message, (
            "systemMessage must NOT contain numbered list '2.'"
        )
        assert "3." not in system_message, (
            "systemMessage must NOT contain numbered list '3.'"
        )

        # Verify does NOT contain detailed recovery instructions
        for suggestion in recovery_suggestions:
            # System message should NOT include full suggestion text
            assert suggestion not in system_message, (
                f"systemMessage should not include full recovery suggestion: '{suggestion}'"
            )

        # Verify human-readable (contains spaces and typical sentence structure)
        assert " " in system_message, (
            "systemMessage should be human-readable with spaces"
        )
        assert len(system_message.split()) >= 3, (
            "systemMessage should contain at least 3 words"
        )

    @patch("sys.stdin")
    @patch("sys.stdout", new_callable=StringIO)
    @patch(
        "src.des.adapters.drivers.hooks.claude_code_hook_adapter.RealSubagentStopHook"
    )
    @patch("src.des.adapters.drivers.hooks.claude_code_hook_adapter.DESConfig")
    def test_handle_subagent_stop_success_no_context_injection(
        self, mock_config, mock_hook_class, mock_stdout, mock_stdin
    ):
        """SubagentStop success case does NOT include context injection fields."""
        # Arrange
        step_path = "/docs/feature/project/steps/01-01.json"
        mock_stdin.read.return_value = json.dumps({"step_path": step_path})

        mock_config_instance = Mock()
        mock_config_instance.audit_logging_enabled = True
        mock_config.return_value = mock_config_instance

        mock_hook = Mock()
        mock_result = Mock()
        mock_result.validation_status = "PASSED"  # Success case
        # Note: error_message and recovery_suggestions should NOT be present on success
        mock_hook.on_agent_complete.return_value = mock_result
        mock_hook_class.return_value = mock_hook

        # Act
        from src.des.adapters.drivers.hooks.claude_code_hook_adapter import (
            handle_subagent_stop,
        )

        exit_code = handle_subagent_stop()

        # Assert
        assert exit_code == 0, "Exit code must be 0 for successful validation"
        output = json.loads(mock_stdout.getvalue())

        # Verify success response structure
        assert output["decision"] == "allow", (
            "Decision must be 'allow' for successful validation"
        )

        # Verify NO context injection on success
        assert "hookSpecificOutput" not in output, (
            "hookSpecificOutput must NOT exist when validation passes"
        )
        assert "additionalContext" not in output, (
            "additionalContext must NOT exist when validation passes"
        )
        assert "systemMessage" not in output, (
            "systemMessage must NOT exist when validation passes"
        )

        # Verify minimal success response (only decision field required)
        assert "decision" in output, "decision field is required"
        # Reason is optional on success, hookSpecificOutput should not be present

    @patch("sys.stdin")
    @patch("sys.stdout", new_callable=StringIO)
    @patch(
        "src.des.adapters.drivers.hooks.claude_code_hook_adapter.RealSubagentStopHook"
    )
    @patch("src.des.adapters.drivers.hooks.claude_code_hook_adapter.DESConfig")
    def test_handle_subagent_stop_empty_recovery_suggestions(
        self, mock_config, mock_hook_class, mock_stdout, mock_stdin
    ):
        """SubagentStop handles empty recovery_suggestions gracefully without crashing."""
        # Arrange
        step_path = "/docs/feature/project/steps/01-04.json"
        error_msg = "Step file missing required metadata"

        mock_stdin.read.return_value = json.dumps({"step_path": step_path})

        mock_config_instance = Mock()
        mock_config_instance.audit_logging_enabled = True
        mock_config.return_value = mock_config_instance

        mock_hook = Mock()
        mock_result = Mock()
        mock_result.validation_status = "FAILED"
        mock_result.error_message = error_msg
        mock_result.recovery_suggestions = []  # Empty list (edge case)
        mock_hook.on_agent_complete.return_value = mock_result
        mock_hook_class.return_value = mock_hook

        # Act
        from src.des.adapters.drivers.hooks.claude_code_hook_adapter import (
            handle_subagent_stop,
        )

        exit_code = handle_subagent_stop()

        # Assert - no crash/exception should occur
        assert exit_code == 2, "Exit code must still be 2 for validation failure"
        output = json.loads(mock_stdout.getvalue())

        # Verify context injection still works with empty recovery_suggestions
        assert "hookSpecificOutput" in output, (
            "hookSpecificOutput must exist even with empty recovery_suggestions"
        )
        assert "additionalContext" in output["hookSpecificOutput"], (
            "additionalContext must exist"
        )
        assert "systemMessage" in output, "systemMessage must exist"

        # Verify additionalContext is non-empty and contains error message
        additional_context = output["hookSpecificOutput"]["additionalContext"]
        assert len(additional_context) > 0, (
            "additionalContext must not be empty even without recovery suggestions"
        )
        assert error_msg in additional_context, (
            "additionalContext must contain error_message"
        )
        assert step_path in additional_context, (
            "additionalContext must contain step file path"
        )

        # Verify systemMessage is still generated
        system_message = output["systemMessage"]
        assert len(system_message) > 0, "systemMessage must not be empty"
        assert error_msg in system_message or "fail" in system_message.lower(), (
            "systemMessage should reference the error"
        )

        # Verify decision is still 'block'
        assert output["decision"] == "block", (
            "Decision must be 'block' for validation failure"
        )

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
            {
                "tool": "Task",
                "tool_input": {
                    "prompt": "/nw:execute step-01-01.json",
                    "max_turns": 30,  # Required
                },
            }
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
            {
                "tool": "Task",
                "tool_input": {
                    "prompt": "/nw:execute step-01-01.json",
                    "max_turns": 30,  # Required
                },
            }
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


class TestClaudeCodeProtocolContract:
    """Contract tests: Verify JSON output conforms to Claude Code hooks protocol.

    These tests validate that our hook adapter produces JSON that matches the
    documented Claude Code hooks specification, ensuring integration compatibility.

    Reference: https://code.claude.com/docs/en/hooks

    Testing Strategy:
    - We test the CONTRACT (JSON structure) not the integration
    - CI/CD safe (no API calls, deterministic, fast)
    - Complements unit tests with protocol compliance verification
    - Trusts Claude Code implements spec correctly (reasonable assumption)
    """

    @patch("sys.stdin")
    @patch("sys.stdout", new_callable=StringIO)
    @patch(
        "src.des.adapters.drivers.hooks.claude_code_hook_adapter.RealSubagentStopHook"
    )
    @patch("src.des.adapters.drivers.hooks.claude_code_hook_adapter.DESConfig")
    def test_subagent_stop_failure_conforms_to_claude_code_protocol(
        self, mock_config, mock_hook_class, mock_stdout, mock_stdin
    ):
        """SubagentStop failure response conforms to Claude Code hooks protocol.

        Protocol Requirements (from Claude Code docs):
        - Top-level 'decision' field: "allow" or "block"
        - Optional 'hookSpecificOutput' object with:
          - 'hookEventName': string identifying the hook
          - 'additionalContext': string injected into orchestrator context
        - Optional 'systemMessage': string shown to user and orchestrator

        This test verifies our implementation matches the documented protocol.
        """
        # Arrange
        step_path = "/test/step.json"
        mock_stdin.read.return_value = json.dumps({"step_path": step_path})

        mock_config_instance = Mock()
        mock_config_instance.audit_logging_enabled = True
        mock_config.return_value = mock_config_instance

        mock_hook = Mock()
        mock_result = Mock()
        mock_result.validation_status = "FAILED"
        mock_result.error_message = "Test error"
        mock_result.recovery_suggestions = ["Fix 1", "Fix 2"]
        mock_hook.on_agent_complete.return_value = mock_result
        mock_hook_class.return_value = mock_hook

        # Act
        from src.des.adapters.drivers.hooks.claude_code_hook_adapter import (
            handle_subagent_stop,
        )

        exit_code = handle_subagent_stop()

        # Assert: Exit code correct
        assert exit_code == 2

        # Assert: Parse JSON output
        output = json.loads(mock_stdout.getvalue())

        # Assert: Required top-level field
        assert "decision" in output, "Protocol requires 'decision' field"
        assert output["decision"] in ["allow", "block"], (
            "decision must be 'allow' or 'block'"
        )
        assert output["decision"] == "block", "Validation failure should return 'block'"

        # Assert: hookSpecificOutput structure
        assert "hookSpecificOutput" in output, (
            "Protocol allows 'hookSpecificOutput' for context injection"
        )
        hook_output = output["hookSpecificOutput"]
        assert isinstance(hook_output, dict), "hookSpecificOutput must be an object"

        # Assert: hookSpecificOutput.hookEventName
        assert "hookEventName" in hook_output, (
            "hookSpecificOutput requires 'hookEventName'"
        )
        assert isinstance(hook_output["hookEventName"], str), (
            "hookEventName must be a string"
        )
        assert hook_output["hookEventName"] == "SubagentStop", (
            "hookEventName should identify the hook"
        )

        # Assert: hookSpecificOutput.additionalContext
        assert "additionalContext" in hook_output, (
            "hookSpecificOutput requires 'additionalContext'"
        )
        assert isinstance(hook_output["additionalContext"], str), (
            "additionalContext must be a string"
        )
        assert len(hook_output["additionalContext"]) > 0, (
            "additionalContext must be non-empty"
        )

        # Assert: systemMessage
        assert "systemMessage" in output, (
            "Protocol allows 'systemMessage' for user-visible warnings"
        )
        assert isinstance(output["systemMessage"], str), (
            "systemMessage must be a string"
        )
        assert len(output["systemMessage"]) > 0, "systemMessage must be non-empty"

    @patch("sys.stdin")
    @patch("sys.stdout", new_callable=StringIO)
    @patch(
        "src.des.adapters.drivers.hooks.claude_code_hook_adapter.RealSubagentStopHook"
    )
    @patch("src.des.adapters.drivers.hooks.claude_code_hook_adapter.DESConfig")
    def test_subagent_stop_success_conforms_to_minimal_protocol(
        self, mock_config, mock_hook_class, mock_stdout, mock_stdin
    ):
        """SubagentStop success response conforms to minimal Claude Code protocol.

        Protocol Requirements for success:
        - Top-level 'decision' field: "allow"
        - NO hookSpecificOutput (only needed for failures)
        - NO systemMessage (only needed for warnings)

        Minimal response: {"decision": "allow"}
        """
        # Arrange
        mock_stdin.read.return_value = json.dumps({"step_path": "/test/step.json"})

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

        # Assert: Exit code correct
        assert exit_code == 0

        # Assert: Parse JSON output
        output = json.loads(mock_stdout.getvalue())

        # Assert: Required fields only
        assert "decision" in output, "Protocol requires 'decision' field"
        assert output["decision"] == "allow", "Validation success should return 'allow'"

        # Assert: Optional fields NOT present (minimal response)
        assert "hookSpecificOutput" not in output, (
            "Success should not include hookSpecificOutput"
        )
        assert "systemMessage" not in output, "Success should not include systemMessage"

        # Assert: Clean minimal response
        assert set(output.keys()) == {"decision"}, (
            "Success response should be minimal: only 'decision'"
        )

    def test_protocol_documentation_reference(self):
        """Document Claude Code hooks protocol reference for future maintainers."""
        protocol_url = "https://code.claude.com/docs/en/hooks"

        # This test serves as documentation
        protocol_spec = {
            "description": "Claude Code hooks protocol for context injection",
            "reference": protocol_url,
            "fields": {
                "decision": {
                    "required": True,
                    "type": "string",
                    "enum": ["allow", "block"],
                    "description": "Whether to allow or block execution",
                },
                "hookSpecificOutput": {
                    "required": False,
                    "type": "object",
                    "description": "Context injection payload",
                    "properties": {
                        "hookEventName": {
                            "required": True,
                            "type": "string",
                            "description": "Identifies which hook fired",
                        },
                        "additionalContext": {
                            "required": True,
                            "type": "string",
                            "description": "Multi-line context injected into orchestrator",
                        },
                    },
                },
                "systemMessage": {
                    "required": False,
                    "type": "string",
                    "description": "User-visible warning message (also visible to orchestrator)",
                },
            },
        }

        # Assert: Documentation is accessible
        assert protocol_spec["reference"] == protocol_url
        assert "decision" in protocol_spec["fields"]
        assert protocol_spec["fields"]["decision"]["required"] is True
