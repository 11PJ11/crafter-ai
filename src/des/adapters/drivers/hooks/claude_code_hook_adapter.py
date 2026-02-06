#!/usr/bin/env python3
"""Claude Code hook adapter with DES integration.

This adapter bridges Claude Code's hook protocol (JSON stdin/stdout, exit codes)
to DES application services (PreToolUseService, SubagentStopService).

Protocol-only: no business logic here. All decisions delegated to application layer.

Commands:
  python3 -m src.des.adapters.drivers.hooks.claude_code_hook_adapter pre-tool-use
  python3 -m src.des.adapters.drivers.hooks.claude_code_hook_adapter subagent-stop

Exit Codes:
  0 = allow/continue
  1 = fail-closed error (BLOCKS execution)
  2 = block/reject (validation failed)

Protocol:
  - Input: JSON on stdin
  - Output: JSON on stdout
  - Fail-closed: Any error causes exit 1 (BLOCK)
"""

import json
import os
import sys
from pathlib import Path


# Add project root to sys.path for standalone script execution
if __name__ == "__main__":
    project_root = str(Path(__file__).resolve().parent.parent.parent.parent.parent)
    if project_root not in sys.path:
        sys.path.insert(0, project_root)

from src.des.adapters.driven.hooks.yaml_execution_log_reader import (
    YamlExecutionLogReader,
)
from src.des.adapters.driven.logging.jsonl_audit_log_writer import JsonlAuditLogWriter
from src.des.adapters.driven.time.system_time import SystemTimeProvider
from src.des.adapters.driven.validation.git_scope_checker import GitScopeChecker
from src.des.application.pre_tool_use_service import PreToolUseService
from src.des.application.subagent_stop_service import SubagentStopService
from src.des.application.validator import TemplateValidator
from src.des.domain.des_marker_parser import DesMarkerParser
from src.des.domain.max_turns_policy import MaxTurnsPolicy
from src.des.domain.step_completion_validator import StepCompletionValidator
from src.des.domain.tdd_schema import get_tdd_schema
from src.des.ports.driver_ports.pre_tool_use_port import PreToolUseInput


def create_pre_tool_use_service() -> PreToolUseService:
    """Create PreToolUseService with production dependencies.

    Returns:
        PreToolUseService configured for production use
    """
    time_provider = SystemTimeProvider()
    audit_writer = JsonlAuditLogWriter()

    return PreToolUseService(
        max_turns_policy=MaxTurnsPolicy(),
        marker_parser=DesMarkerParser(),
        prompt_validator=TemplateValidator(),
        audit_writer=audit_writer,
        time_provider=time_provider,
    )


def create_subagent_stop_service() -> SubagentStopService:
    """Create SubagentStopService with production dependencies.

    Returns:
        SubagentStopService configured for production use
    """
    time_provider = SystemTimeProvider()
    audit_writer = JsonlAuditLogWriter()
    schema = get_tdd_schema()

    return SubagentStopService(
        log_reader=YamlExecutionLogReader(),
        completion_validator=StepCompletionValidator(schema=schema),
        scope_checker=GitScopeChecker(),
        audit_writer=audit_writer,
        time_provider=time_provider,
    )


def handle_pre_tool_use() -> int:
    """Handle PreToolUse command: validate Task tool invocation.

    Protocol translation only -- all decisions delegated to PreToolUseService.

    Returns:
        0 if validation passes (allow)
        1 if error occurs (fail-closed)
        2 if validation fails (block)
    """
    try:
        # Read JSON from stdin
        input_data = sys.stdin.read()

        if not input_data or not input_data.strip():
            response = {"status": "error", "reason": "Missing stdin input"}
            print(json.dumps(response))
            return 1

        # Parse JSON
        try:
            hook_input = json.loads(input_data)
        except json.JSONDecodeError as e:
            response = {"status": "error", "reason": f"Invalid JSON: {e!s}"}
            print(json.dumps(response))
            return 1

        # Extract protocol fields
        tool = hook_input.get("tool", {})
        tool_input = tool.get("input", {})
        prompt = tool_input.get("prompt", "")
        max_turns = tool_input.get("max_turns")

        # Delegate to application service
        service = create_pre_tool_use_service()
        decision = service.validate(
            PreToolUseInput(
                prompt=prompt,
                max_turns=max_turns,
                subagent_type=tool_input.get("subagent_type"),
            )
        )

        # Translate HookDecision to protocol response
        if decision.action == "allow":
            response = {"decision": "allow"}
            print(json.dumps(response))
            return 0
        else:
            response = {"decision": "block", "reason": decision.reason or "Validation failed"}
            print(json.dumps(response))
            return decision.exit_code

    except Exception as e:
        # Fail-closed: any error blocks execution
        response = {"status": "error", "reason": f"Unexpected error: {e!s}"}
        print(json.dumps(response))
        return 1


def handle_subagent_stop() -> int:
    """Handle subagent-stop command: validate step completion.

    Protocol translation only -- all decisions delegated to SubagentStopService.

    Schema v2.0 ONLY: {"executionLogPath": "/abs/path", "projectId": "...", "stepId": "..."}

    Returns:
        0 if gate passes
        1 if error occurs (fail-closed)
        2 if gate fails (BLOCKS orchestrator)
    """
    try:
        # Read JSON from stdin
        input_data = sys.stdin.read()

        if not input_data or not input_data.strip():
            response = {"status": "error", "reason": "Missing stdin input"}
            print(json.dumps(response))
            return 1

        # Parse JSON
        try:
            hook_input = json.loads(input_data)
        except json.JSONDecodeError as e:
            response = {"status": "error", "reason": f"Invalid JSON: {e!s}"}
            print(json.dumps(response))
            return 1

        # Schema v2.0 input (ONLY format supported)
        execution_log_path = hook_input.get("executionLogPath")
        project_id = hook_input.get("projectId")
        step_id = hook_input.get("stepId")

        # Validate required fields (protocol-level, not business logic)
        if not (execution_log_path and project_id and step_id):
            response = {
                "status": "error",
                "reason": "Missing required fields: executionLogPath, projectId, and stepId are all required",
            }
            print(json.dumps(response))
            return 1

        # Validate absolute path (protocol-level)
        if not os.path.isabs(execution_log_path):
            response = {
                "status": "error",
                "reason": f"executionLogPath must be absolute (got: {execution_log_path})",
            }
            print(json.dumps(response))
            return 1

        # Delegate to application service
        from src.des.ports.driver_ports.subagent_stop_port import SubagentStopContext

        service = create_subagent_stop_service()
        decision = service.validate(
            SubagentStopContext(
                execution_log_path=execution_log_path,
                project_id=project_id,
                step_id=step_id,
            )
        )

        # Translate HookDecision to protocol response
        if decision.action == "allow":
            response = {"decision": "allow"}
            print(json.dumps(response))
            return 0
        else:
            reason = decision.reason or "Validation failed"

            # Build recovery steps for notification
            recovery_suggestions = decision.recovery_suggestions or []
            recovery_steps = "\n".join(
                [f"  {i + 1}. {s}" for i, s in enumerate(recovery_suggestions)]
            )

            notification = f"""STOP HOOK VALIDATION FAILED

Step: {project_id}/{step_id}
Execution Log: {execution_log_path}
Status: FAILED
Error: {reason}

RECOVERY REQUIRED:
{recovery_steps}

The step validation failed. You MUST fix these issues before proceeding."""

            response = {
                "decision": "block",
                "reason": reason,
                "hookSpecificOutput": {
                    "hookEventName": "SubagentStop",
                    "additionalContext": notification,
                },
                "systemMessage": f"Validation failed: {reason}",
            }
            print(json.dumps(response))
            return 2

    except Exception as e:
        # Fail-closed: any error blocks execution
        response = {"status": "error", "reason": f"Unexpected error: {e!s}"}
        print(json.dumps(response))
        return 1


def main() -> None:
    """Hook adapter entry point - routes command to appropriate handler."""
    if len(sys.argv) < 2:
        print(
            json.dumps(
                {
                    "status": "error",
                    "reason": "Missing command argument (pre-tool-use or subagent-stop)",
                }
            )
        )
        sys.exit(1)

    command = sys.argv[1]

    if command in ("pre-tool-use", "pre-task"):
        # "pre-task" accepted for backward compatibility
        exit_code = handle_pre_tool_use()
    elif command == "subagent-stop":
        exit_code = handle_subagent_stop()
    else:
        print(json.dumps({"status": "error", "reason": f"Unknown command: {command}"}))
        exit_code = 1

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
