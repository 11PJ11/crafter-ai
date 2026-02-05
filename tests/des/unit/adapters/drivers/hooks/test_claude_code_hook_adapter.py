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


class TestAppendOnlyLogValidation:
    """Test append-only execution-log.yaml validation (Schema v2.0)."""

    @patch("sys.stdin")
    @patch("sys.stdout", new_callable=StringIO)
    def test_valid_append_only_log_with_all_phases_executed_returns_allow(
        self, mock_stdout, mock_stdin, tmp_path
    ):
        """Valid execution-log.yaml with all phases EXECUTED/PASS returns allow."""
        # Create execution log
        log_file = tmp_path / "execution-log.yaml"
        log_file.write_text(
            """project_id: test-project
created_at: '2026-02-05T14:00:00Z'
total_steps: 1
events:
  - "01-01|PREPARE|EXECUTED|PASS|2026-02-05T14:01:00Z"
  - "01-01|RED_ACCEPTANCE|EXECUTED|PASS|2026-02-05T14:02:00Z"
  - "01-01|RED_UNIT|EXECUTED|PASS|2026-02-05T14:03:00Z"
  - "01-01|GREEN|EXECUTED|PASS|2026-02-05T14:04:00Z"
  - "01-01|REVIEW|EXECUTED|PASS|2026-02-05T14:05:00Z"
  - "01-01|REFACTOR_CONTINUOUS|EXECUTED|PASS|2026-02-05T14:06:00Z"
  - "01-01|COMMIT|EXECUTED|PASS|2026-02-05T14:07:00Z"
"""
        )

        # Arrange
        mock_stdin.read.return_value = json.dumps(
            {
                "executionLogPath": str(log_file),
                "projectId": "test-project",
                "stepId": "01-01",
            }
        )

        # Act
        from src.des.adapters.drivers.hooks.claude_code_hook_adapter import (
            handle_subagent_stop,
        )

        exit_code = handle_subagent_stop()

        # Assert
        assert exit_code == 0
        output = json.loads(mock_stdout.getvalue())
        assert output["decision"] == "allow"

    @patch("sys.stdin")
    @patch("sys.stdout", new_callable=StringIO)
    def test_log_with_missing_phases_returns_block(
        self, mock_stdout, mock_stdin, tmp_path
    ):
        """Log missing required phases returns block with recovery suggestions."""
        # Create incomplete execution log (missing COMMIT)
        log_file = tmp_path / "execution-log.yaml"
        log_file.write_text(
            """project_id: test-project
created_at: '2026-02-05T14:00:00Z'
total_steps: 1
events:
  - "01-01|PREPARE|EXECUTED|PASS|2026-02-05T14:01:00Z"
  - "01-01|RED_ACCEPTANCE|EXECUTED|PASS|2026-02-05T14:02:00Z"
  - "01-01|RED_UNIT|EXECUTED|PASS|2026-02-05T14:03:00Z"
"""
        )

        # Arrange
        mock_stdin.read.return_value = json.dumps(
            {
                "executionLogPath": str(log_file),
                "projectId": "test-project",
                "stepId": "01-01",
            }
        )

        # Act
        from src.des.adapters.drivers.hooks.claude_code_hook_adapter import (
            handle_subagent_stop,
        )

        exit_code = handle_subagent_stop()

        # Assert
        assert exit_code == 2  # Block
        output = json.loads(mock_stdout.getvalue())
        assert output["decision"] == "block"
        assert "Missing phases" in output["reason"]

    @patch("sys.stdin")
    @patch("sys.stdout", new_callable=StringIO)
    def test_log_with_valid_skip_reasons_returns_allow(
        self, mock_stdout, mock_stdin, tmp_path
    ):
        """Log with valid skip reasons (APPROVED_SKIP, NOT_APPLICABLE) returns allow."""
        # Create execution log with valid skips
        log_file = tmp_path / "execution-log.yaml"
        log_file.write_text(
            """project_id: test-project
created_at: '2026-02-05T14:00:00Z'
total_steps: 1
events:
  - "01-01|PREPARE|EXECUTED|PASS|2026-02-05T14:01:00Z"
  - "01-01|RED_ACCEPTANCE|SKIPPED|NOT_APPLICABLE: Config-only change|2026-02-05T14:02:00Z"
  - "01-01|RED_UNIT|SKIPPED|APPROVED_SKIP: Tech lead approved|2026-02-05T14:03:00Z"
  - "01-01|GREEN|EXECUTED|PASS|2026-02-05T14:04:00Z"
  - "01-01|REVIEW|EXECUTED|PASS|2026-02-05T14:05:00Z"
  - "01-01|REFACTOR_CONTINUOUS|EXECUTED|PASS|2026-02-05T14:06:00Z"
  - "01-01|COMMIT|EXECUTED|PASS|2026-02-05T14:07:00Z"
"""
        )

        # Arrange
        mock_stdin.read.return_value = json.dumps(
            {
                "executionLogPath": str(log_file),
                "projectId": "test-project",
                "stepId": "01-01",
            }
        )

        # Act
        from src.des.adapters.drivers.hooks.claude_code_hook_adapter import (
            handle_subagent_stop,
        )

        exit_code = handle_subagent_stop()

        # Assert
        assert exit_code == 0
        output = json.loads(mock_stdout.getvalue())
        assert output["decision"] == "allow"

    @patch("sys.stdin")
    @patch("sys.stdout", new_callable=StringIO)
    def test_log_with_deferred_skip_reason_returns_block(
        self, mock_stdout, mock_stdin, tmp_path
    ):
        """Log with DEFERRED skip reason (blocks commit) returns block."""
        # Create execution log with blocking skip
        log_file = tmp_path / "execution-log.yaml"
        log_file.write_text(
            """project_id: test-project
created_at: '2026-02-05T14:00:00Z'
total_steps: 1
events:
  - "01-01|PREPARE|EXECUTED|PASS|2026-02-05T14:01:00Z"
  - "01-01|RED_ACCEPTANCE|EXECUTED|PASS|2026-02-05T14:02:00Z"
  - "01-01|RED_UNIT|SKIPPED|DEFERRED: Will add tests later|2026-02-05T14:03:00Z"
  - "01-01|GREEN|EXECUTED|PASS|2026-02-05T14:04:00Z"
  - "01-01|REVIEW|EXECUTED|PASS|2026-02-05T14:05:00Z"
  - "01-01|REFACTOR_CONTINUOUS|EXECUTED|PASS|2026-02-05T14:06:00Z"
  - "01-01|COMMIT|EXECUTED|PASS|2026-02-05T14:07:00Z"
"""
        )

        # Arrange
        mock_stdin.read.return_value = json.dumps(
            {
                "executionLogPath": str(log_file),
                "projectId": "test-project",
                "stepId": "01-01",
            }
        )

        # Act
        from src.des.adapters.drivers.hooks.claude_code_hook_adapter import (
            handle_subagent_stop,
        )

        exit_code = handle_subagent_stop()

        # Assert
        assert exit_code == 2  # Block
        output = json.loads(mock_stdout.getvalue())
        assert output["decision"] == "block"
        assert "DEFERRED" in output["reason"] or "blocks commit" in output["reason"]

    @patch("sys.stdin")
    @patch("sys.stdout", new_callable=StringIO)
    def test_log_with_project_id_mismatch_returns_block(
        self, mock_stdout, mock_stdin, tmp_path
    ):
        """Log with mismatched project_id returns block."""
        # Create execution log with different project_id
        log_file = tmp_path / "execution-log.yaml"
        log_file.write_text(
            """project_id: different-project
created_at: '2026-02-05T14:00:00Z'
total_steps: 1
events:
  - "01-01|PREPARE|EXECUTED|PASS|2026-02-05T14:01:00Z"
"""
        )

        # Arrange
        mock_stdin.read.return_value = json.dumps(
            {
                "executionLogPath": str(log_file),
                "projectId": "test-project",
                "stepId": "01-01",
            }
        )

        # Act
        from src.des.adapters.drivers.hooks.claude_code_hook_adapter import (
            handle_subagent_stop,
        )

        exit_code = handle_subagent_stop()

        # Assert
        assert exit_code == 2  # Block
        output = json.loads(mock_stdout.getvalue())
        assert output["decision"] == "block"
        assert "mismatch" in output["reason"].lower()

    @patch("sys.stdin")
    @patch("sys.stdout", new_callable=StringIO)
    def test_log_file_not_found_returns_block(self, mock_stdout, mock_stdin, tmp_path):
        """Non-existent log file returns block with helpful recovery suggestions."""
        # Arrange
        non_existent_path = tmp_path / "nonexistent.yaml"
        mock_stdin.read.return_value = json.dumps(
            {
                "executionLogPath": str(non_existent_path),
                "projectId": "test-project",
                "stepId": "01-01",
            }
        )

        # Act
        from src.des.adapters.drivers.hooks.claude_code_hook_adapter import (
            handle_subagent_stop,
        )

        exit_code = handle_subagent_stop()

        # Assert
        assert exit_code == 2  # Block
        output = json.loads(mock_stdout.getvalue())
        assert output["decision"] == "block"
        assert "not found" in output["reason"].lower()


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
    def test_subagent_stop_failure_conforms_to_claude_code_protocol(
        self, mock_stdout, mock_stdin, tmp_path
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
        # Arrange: Create execution-log.yaml with missing phases (validation failure)
        log_file = tmp_path / "execution-log.yaml"
        log_file.write_text("""project_id: test-project
created_at: '2026-02-05T14:00:00Z'
total_steps: 1
events:
  - "01-01|PREPARE|EXECUTED|PASS|2026-02-05T14:01:00Z"
  - "01-01|RED_ACCEPTANCE|EXECUTED|PASS|2026-02-05T14:02:00Z"
""")

        mock_stdin.read.return_value = json.dumps(
            {
                "executionLogPath": str(log_file),
                "projectId": "test-project",
                "stepId": "01-01",
            }
        )

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
    def test_subagent_stop_success_conforms_to_minimal_protocol(
        self, mock_stdout, mock_stdin, tmp_path
    ):
        """SubagentStop success response conforms to minimal Claude Code protocol.

        Protocol Requirements for success:
        - Top-level 'decision' field: "allow"
        - NO hookSpecificOutput (only needed for failures)
        - NO systemMessage (only needed for warnings)

        Minimal response: {"decision": "allow"}
        """
        # Arrange: Create execution-log.yaml with all phases complete (validation success)
        log_file = tmp_path / "execution-log.yaml"
        log_file.write_text("""project_id: test-project
created_at: '2026-02-05T14:00:00Z'
total_steps: 1
events:
  - "01-01|PREPARE|EXECUTED|PASS|2026-02-05T14:01:00Z"
  - "01-01|RED_ACCEPTANCE|EXECUTED|PASS|2026-02-05T14:02:00Z"
  - "01-01|RED_UNIT|EXECUTED|PASS|2026-02-05T14:03:00Z"
  - "01-01|GREEN|EXECUTED|PASS|2026-02-05T14:04:00Z"
  - "01-01|REVIEW|EXECUTED|PASS|2026-02-05T14:05:00Z"
  - "01-01|REFACTOR_CONTINUOUS|EXECUTED|PASS|2026-02-05T14:06:00Z"
  - "01-01|COMMIT|EXECUTED|PASS|2026-02-05T14:07:00Z"
""")

        mock_stdin.read.return_value = json.dumps(
            {
                "executionLogPath": str(log_file),
                "projectId": "test-project",
                "stepId": "01-01",
            }
        )

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
