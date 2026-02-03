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
import sys
import os
from typing import Dict, Any

# Add project root to sys.path for standalone script execution
if __name__ == "__main__":
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../.."))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)

from src.des.application.orchestrator import DESOrchestrator
from src.des.adapters.drivers.hooks.real_hook import RealSubagentStopHook
from src.des.application.validator import TemplateValidator
from src.des.adapters.driven.filesystem.real_filesystem import RealFileSystem
from src.des.adapters.driven.config.des_config import DESConfig
from src.des.adapters.driven.logging.audit_logger import get_audit_logger
from src.des.adapters.driven.time.system_time import SystemTimeProvider


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
        time_provider=time_provider
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
            response = {
                "status": "error",
                "reason": "Missing stdin input"
            }
            print(json.dumps(response))
            return 1

        # Parse JSON
        try:
            hook_input = json.loads(input_data)
        except json.JSONDecodeError as e:
            response = {
                "status": "error",
                "reason": f"Invalid JSON: {str(e)}"
            }
            print(json.dumps(response))
            return 1

        # Extract prompt from tool_input
        tool_input = hook_input.get("tool_input", {})
        prompt = tool_input.get("prompt", "")

        # Initialize DES components with production implementations
        config = DESConfig()
        hook = RealSubagentStopHook()
        validator = TemplateValidator()
        filesystem = RealFileSystem()
        time_provider = SystemTimeProvider()

        orchestrator = DESOrchestrator(
            hook=hook,
            validator=validator,
            filesystem=filesystem,
            time_provider=time_provider
        )

        # Validate prompt
        validation_result = orchestrator.validate_prompt(prompt)

        # Audit logging is handled by orchestrator.validate_prompt()
        # No manual logging needed here - orchestrator creates proper AuditEvent

        # Return decision
        if validation_result.task_invocation_allowed:
            response = {
                "decision": "allow"
            }
            print(json.dumps(response))
            return 0
        else:
            response = {
                "decision": "block",
                "reason": "; ".join(validation_result.errors)
            }
            print(json.dumps(response))
            return 2

    except Exception as e:
        # Fail-closed: any error blocks execution
        response = {
            "status": "error",
            "reason": f"Unexpected error: {str(e)}"
        }
        print(json.dumps(response))
        return 1


def handle_subagent_stop() -> int:
    """Handle subagent-stop command: validate step completion.

    Returns:
        0 if gate passes
        1 if error occurs (fail-closed)
        2 if gate fails (BLOCKS orchestrator)
    """
    try:
        # Read JSON from stdin
        input_data = sys.stdin.read()

        if not input_data or not input_data.strip():
            response = {
                "status": "error",
                "reason": "Missing stdin input"
            }
            print(json.dumps(response))
            return 1

        # Parse JSON
        try:
            hook_input = json.loads(input_data)
        except json.JSONDecodeError as e:
            response = {
                "status": "error",
                "reason": f"Invalid JSON: {str(e)}"
            }
            print(json.dumps(response))
            return 1

        # Extract step path
        step_path = hook_input.get("step_path", "")

        # Initialize DES components
        config = DESConfig()
        hook = RealSubagentStopHook()

        # Execute gate validation
        gate_result = hook.on_agent_complete(step_path)

        # Audit logging is handled by RealSubagentStopHook.on_agent_complete()
        # No manual logging needed here - hook creates proper AuditEvent

        # Return decision
        if gate_result.validation_status == "PASSED":
            response = {
                "decision": "allow"
            }
            print(json.dumps(response))
            return 0
        else:
            response = {
                "decision": "block",
                "reason": f"Gate failed: {gate_result.validation_status}"
            }
            print(json.dumps(response))
            return 2

    except Exception as e:
        # Fail-closed: any error blocks execution
        response = {
            "status": "error",
            "reason": f"Unexpected error: {str(e)}"
        }
        print(json.dumps(response))
        return 1


def main() -> None:
    """Hook adapter entry point - routes command to appropriate handler."""
    if len(sys.argv) < 2:
        print(json.dumps({
            "status": "error",
            "reason": "Missing command argument (pre-task or subagent-stop)"
        }))
        sys.exit(1)

    command = sys.argv[1]

    if command == "pre-task":
        exit_code = handle_pre_task()
    elif command == "subagent-stop":
        exit_code = handle_subagent_stop()
    else:
        print(json.dumps({
            "status": "error",
            "reason": f"Unknown command: {command}"
        }))
        exit_code = 1

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
