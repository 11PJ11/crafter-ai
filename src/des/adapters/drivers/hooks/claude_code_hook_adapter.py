#!/usr/bin/env python3
"""Claude Code hook adapter with DES integration.

This adapter bridges Claude Code's hook protocol (JSON stdin/stdout, exit codes)
to DES domain logic (DESOrchestrator, RealSubagentStopHook).

Commands:
  python3 -m src.des.adapters.drivers.hooks.claude_code_hook_adapter pre-task
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
import re
import sys
from pathlib import Path


# Add project root to sys.path for standalone script execution
if __name__ == "__main__":
    project_root = str(Path(__file__).resolve().parent.parent.parent.parent.parent)
    if project_root not in sys.path:
        sys.path.insert(0, project_root)

from src.des.adapters.driven.config.des_config import DESConfig
from src.des.adapters.driven.filesystem.real_filesystem import RealFileSystem
from src.des.adapters.driven.time.system_time import SystemTimeProvider
from src.des.adapters.drivers.hooks.real_hook import RealSubagentStopHook
from src.des.application.orchestrator import DESOrchestrator
from src.des.application.validator import TemplateValidator


def create_orchestrator() -> DESOrchestrator:
    """Create DESOrchestrator with production dependencies.

    Factory function to encapsulate orchestrator creation with all required
    production implementations. This makes testing easier by allowing mock
    injection at the factory level.

    Returns:
        DESOrchestrator configured with production dependencies
    """
    hook = RealSubagentStopHook()
    validator = TemplateValidator()
    filesystem = RealFileSystem()
    time_provider = SystemTimeProvider()

    return DESOrchestrator(
        hook=hook,
        validator=validator,
        filesystem=filesystem,
        time_provider=time_provider,
    )


def handle_pre_task() -> int:
    """Handle pre-task command: validate Task tool invocation.

    Returns:
        0 if validation passes (allow)
        1 if error occurs (fail-closed)
        2 if validation fails (block)
    """
    try:
        # Read JSON from stdin
        input_data = sys.stdin.read()

        if not input_data and not input_data.strip():
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

        # Extract tool_input parameters
        tool_input = hook_input.get("tool_input", {})
        prompt = tool_input.get("prompt", "")
        max_turns = tool_input.get("max_turns")

        # Validate max_turns parameter (CRITICAL requirement from CLAUDE.md)
        # This is a tool-level requirement, not DES-specific
        if max_turns is None:
            response = {
                "decision": "block",
                "reason": "MISSING_MAX_TURNS: The max_turns parameter is required for all Task invocations. "
                "Add max_turns parameter (e.g., max_turns=30) to prevent unbounded execution.",
            }
            print(json.dumps(response))
            return 2

        # Validate max_turns value is within acceptable range
        if not isinstance(max_turns, int) or max_turns < 10 or max_turns > 100:
            response = {
                "decision": "block",
                "reason": f"INVALID_MAX_TURNS: max_turns must be an integer between 10 and 100 (got: {max_turns}). "
                "Recommended values: quick edit=15, background task=25, standard=30, research=35, complex=50.",
            }
            print(json.dumps(response))
            return 2

        # Check if this is a DES task (has DES-VALIDATION marker)
        # Non-DES tasks (ad-hoc, exploration) should skip prompt validation
        des_marker_pattern = r"<!--\s*DES-VALIDATION\s*:\s*required\s*-->"
        is_des_task = bool(re.search(des_marker_pattern, prompt))

        if not is_des_task:
            # Ad-hoc task: max_turns validated above, no prompt validation needed
            response = {"decision": "allow"}
            print(json.dumps(response))
            return 0

        # Check for DES-MODE marker (orchestrator vs execution)
        des_mode_pattern = r"<!--\s*DES-MODE\s*:\s*orchestrator\s*-->"
        is_orchestrator_mode = bool(re.search(des_mode_pattern, prompt))

        if is_orchestrator_mode:
            # Orchestrator mode: relaxed validation
            # Only verify DES markers present, skip 8-section validation
            # max_turns already validated above
            response = {"decision": "allow"}
            print(json.dumps(response))
            return 0

        # DES task (execution mode): validate full prompt structure
        # Initialize DES components with production implementations
        DESConfig()
        hook = RealSubagentStopHook()
        validator = TemplateValidator()
        filesystem = RealFileSystem()
        time_provider = SystemTimeProvider()

        orchestrator = DESOrchestrator(
            hook=hook,
            validator=validator,
            filesystem=filesystem,
            time_provider=time_provider,
        )

        # Validate prompt
        validation_result = orchestrator.validate_prompt(prompt)

        # Audit logging is handled by orchestrator.validate_prompt()
        # No manual logging needed here - orchestrator creates proper AuditEvent

        # Return decision
        if validation_result.task_invocation_allowed:
            response = {"decision": "allow"}
            print(json.dumps(response))
            return 0
        else:
            response = {
                "decision": "block",
                "reason": "; ".join(validation_result.errors),
            }
            print(json.dumps(response))
            return 2

    except Exception as e:
        # Fail-closed: any error blocks execution
        response = {"status": "error", "reason": f"Unexpected error: {e!s}"}
        print(json.dumps(response))
        return 1


def _verify_step_from_append_only_log(
    log_path: str, project_id: str, step_id: str
) -> tuple[bool, str, list[str]]:
    """Verify step completion from append-only execution-log.yaml.

    Args:
        log_path: Absolute path to execution-log.yaml
        project_id: Project identifier (must match log file)
        step_id: Step identifier to validate

    Returns:
        Tuple of (is_valid, error_message, recovery_suggestions)
    """
    from src.des.domain.tdd_schema import get_tdd_schema
    import yaml

    schema = get_tdd_schema()

    # Read execution log
    try:
        with open(log_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
    except FileNotFoundError:
        return (
            False,
            f"Execution log not found: {log_path}",
            ["Create execution-log.yaml file", "Run orchestrator to initialize log"],
        )
    except yaml.YAMLError as e:
        return (
            False,
            f"Invalid YAML in execution log: {e}",
            ["Fix YAML syntax errors in execution-log.yaml"],
        )

    # Verify project_id matches
    log_project_id = data.get("project_id")
    if log_project_id != project_id:
        return (
            False,
            f"Project ID mismatch: expected '{project_id}', found '{log_project_id}'",
            [
                f"Verify you're working on project '{project_id}'",
                "Check DES-PROJECT-ID marker in prompt",
            ],
        )

    # Extract events for this step
    events = data.get("events", [])
    step_events = {}

    for event_str in events:
        # Format: "step_id|phase|status|data|timestamp"
        parts = event_str.split("|")
        if len(parts) >= 5 and parts[0] == step_id:
            phase_name = parts[1]
            status = parts[2]
            outcome_data = parts[3]
            step_events[phase_name] = {"status": status, "data": outcome_data}

    # Validate all required phases are present
    missing_phases = []
    invalid_phases = []
    recovery_suggestions = []

    for phase in schema.tdd_phases:
        if phase not in step_events:
            missing_phases.append(phase)
            continue

        event = step_events[phase]
        status = event["status"]
        data = event["data"]

        # Validate EXECUTED phases
        if status == "EXECUTED":
            if data not in ["PASS", "FAIL"]:
                invalid_phases.append(
                    f"{phase}: Invalid outcome '{data}' (must be PASS or FAIL)"
                )
            elif phase == "COMMIT" and data != "PASS":
                invalid_phases.append(f"{phase}: COMMIT must have outcome PASS")

        # Validate SKIPPED phases
        elif status == "SKIPPED":
            # Check if skip reason has valid prefix
            valid_prefix_found = any(
                data.startswith(prefix) for prefix in schema.valid_skip_prefixes
            )
            if not valid_prefix_found:
                invalid_phases.append(
                    f"{phase}: Invalid skip reason '{data}' (must start with: {', '.join(schema.valid_skip_prefixes)})"
                )

            # Check if skip reason blocks commit
            blocking_prefix_found = any(
                data.startswith(prefix) for prefix in schema.blocking_skip_prefixes
            )
            if blocking_prefix_found:
                invalid_phases.append(
                    f"{phase}: Skip reason '{data}' blocks commit (DEFERRED not allowed)"
                )

        # Invalid status
        elif status not in schema.valid_statuses:
            invalid_phases.append(
                f"{phase}: Invalid status '{status}' (must be: {', '.join(schema.valid_statuses)})"
            )

    # Build error message and recovery suggestions
    if missing_phases or invalid_phases:
        error_parts = []
        if missing_phases:
            error_parts.append(f"Missing phases: {', '.join(missing_phases)}")
            recovery_suggestions.extend(
                [
                    f"Append events for missing phases: {', '.join(missing_phases)}",
                    "Format: step_id|phase|status|data|timestamp",
                ]
            )

        if invalid_phases:
            error_parts.append(f"Invalid phases: {'; '.join(invalid_phases)}")
            recovery_suggestions.extend(
                [
                    "Fix invalid phase entries in execution-log.yaml",
                    "Ensure EXECUTED phases have PASS/FAIL outcome",
                    "Ensure SKIPPED phases have valid reason prefix",
                ]
            )

        return False, "; ".join(error_parts), recovery_suggestions

    return True, "", []


def handle_subagent_stop() -> int:
    """Handle subagent-stop command: validate step completion.

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

        # Validate input format
        if not (execution_log_path and project_id and step_id):
            response = {
                "status": "error",
                "reason": "Missing required fields: executionLogPath, projectId, and stepId are all required"
            }
            print(json.dumps(response))
            return 1

        # Validate absolute path
        if not os.path.isabs(execution_log_path):
            response = {
                "status": "error",
                "reason": f"executionLogPath must be absolute (got: {execution_log_path})"
            }
            print(json.dumps(response))
            return 1

        # Verify step from append-only log
        is_valid, error_message, recovery_suggestions = _verify_step_from_append_only_log(
            execution_log_path, project_id, step_id
        )

        # Return decision based on validation
        if is_valid:
            response = {"decision": "allow"}
            print(json.dumps(response))
            return 0
        else:
            # Build recovery steps for notification
            recovery_steps = "\n".join(
                [f"  {i+1}. {suggestion}" for i, suggestion in enumerate(recovery_suggestions)]
            )

            notification = f"""🚨 STOP HOOK VALIDATION FAILED 🚨

Step: {project_id}/{step_id}
Execution Log: {execution_log_path}
Status: FAILED
Error: {error_message}

RECOVERY REQUIRED:
{recovery_steps}

The step validation failed. You MUST fix these issues before proceeding."""

            response = {
                "decision": "block",
                "reason": f"Append-only log validation failed: {error_message}",
                "hookSpecificOutput": {
                    "hookEventName": "SubagentStop",
                    "additionalContext": notification
                },
                "systemMessage": f"⚠️ Validation failed: {error_message}"
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
                    "reason": "Missing command argument (pre-task or subagent-stop)",
                }
            )
        )
        sys.exit(1)

    command = sys.argv[1]

    if command == "pre-task":
        exit_code = handle_pre_task()
    elif command == "subagent-stop":
        exit_code = handle_subagent_stop()
    else:
        print(json.dumps({"status": "error", "reason": f"Unknown command: {command}"}))
        exit_code = 1

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
