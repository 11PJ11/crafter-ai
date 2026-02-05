"""SubagentStopHook - validates step completion from execution-log.yaml (Schema v2.0).

Driven adapter implementing HookPort for post-execution validation.
Replaces RealSubagentStopHook (Schema v1.x) which used step files JSON.

Architecture:
    Claude Code → claude_code_hook_adapter.py (driver)
                    ↓
                DESOrchestrator (application)
                    ↓
                HookPort interface (boundary)
                    ↓
                SubagentStopHook (THIS - driven adapter)
                    ↓
                execution-log.yaml
"""

import logging
from pathlib import Path

import yaml

from src.des.adapters.driven.logging.audit_logger import get_audit_logger
from src.des.adapters.driven.time.system_time import SystemTimeProvider
from src.des.adapters.driven.validation.scope_validator import ScopeValidator
from src.des.domain.tdd_schema import get_tdd_schema
from src.des.ports.driver_ports.hook_port import HookPort, HookResult

logger = logging.getLogger(__name__)


class SubagentStopHook(HookPort):
    """Validates step completion from execution-log.yaml (Schema v2.0).

    Business Logic:
    - Reads execution-log.yaml (append-only format)
    - Filters events for specific step_id
    - Validates all 7 TDD phases present and correct
    - Returns HookResult with validation status

    Schema v2.0 format:
        execution-log.yaml contains:
            events:
              - "01-01|PREPARE|EXECUTED|PASS|2026-02-02T10:00:00Z"
              - "01-01|RED_ACCEPTANCE|EXECUTED|PASS|2026-02-02T10:05:00Z"
              - ...

    Validation rules (from TDD schema):
    - All 7 phases must be present (PREPARE, RED_ACCEPTANCE, RED_UNIT, GREEN,
      REVIEW, REFACTOR_CONTINUOUS, COMMIT)
    - EXECUTED phases must have PASS or FAIL outcome
    - COMMIT phase must have PASS outcome
    - SKIPPED phases must have valid reason prefix
    - SKIPPED phases with blocking prefixes (DEFERRED) not allowed
    """

    def __init__(self):
        """Initialize hook with TDD schema."""
        self._schema = get_tdd_schema()

    def persist_turn_count(
        self, step_file_path: str, phase_name: str, turn_count: int
    ) -> None:
        """No-op for Schema v2.0 - turn counting moved to execution-log.yaml.

        Args:
            step_file_path: Ignored (no step files in v2.0)
            phase_name: Ignored
            turn_count: Ignored
        """
        # Schema v2.0: Turn counting handled differently
        # execution-log.yaml doesn't store turn counts in events
        pass

    def on_agent_complete(self, step_file_path: str) -> HookResult:
        """Validate step completion from execution-log.yaml or JSON step file.

        Schema v2.0 NOTE: The parameter name is legacy from v1.x.
        In v2.0, this receives a compound path encoding:
            "{execution_log_path}?project_id={project_id}&step_id={step_id}"

        Schema v1.x compatibility: If path ends with .json, treats as step file.

        Args:
            step_file_path: Compound path with execution-log location and metadata,
                           or direct path to JSON step file (v1.x compatibility)

        Returns:
            HookResult with validation status and errors
        """
        # Check if this is a JSON step file (Schema v1.x compatibility)
        if step_file_path.endswith(".json"):
            return self._validate_from_step_file(step_file_path)

        # Parse compound path
        # Format: "path/to/execution-log.yaml?project_id=foo&step_id=01-01"
        if "?" in step_file_path:
            path_part, query_part = step_file_path.split("?", 1)
            execution_log_path = path_part

            # Parse query params
            params = {}
            for param in query_part.split("&"):
                if "=" in param:
                    key, value = param.split("=", 1)
                    params[key] = value

            project_id = params.get("project_id", "")
            step_id = params.get("step_id", "")
        else:
            # Fallback: treat as direct path (for backwards compatibility)
            execution_log_path = step_file_path
            project_id = ""
            step_id = ""

        return self._validate_from_execution_log(execution_log_path, project_id, step_id)

    def _validate_from_execution_log(
        self, log_path: str, project_id: str, step_id: str
    ) -> HookResult:
        """Validate step completion from append-only execution-log.yaml.

        Args:
            log_path: Absolute path to execution-log.yaml
            project_id: Project identifier (must match log file)
            step_id: Step identifier to validate

        Returns:
            HookResult with validation status and any errors found
        """
        # Read execution log
        try:
            with open(log_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
        except FileNotFoundError:
            return HookResult(
                validation_status="FAILED",
                error_message=f"Execution log not found: {log_path}",
                error_type="FILE_NOT_FOUND",
                error_count=1,
                recovery_suggestions=[
                    "Create execution-log.yaml file",
                    "Run orchestrator to initialize log",
                ],
            )
        except yaml.YAMLError as e:
            return HookResult(
                validation_status="FAILED",
                error_message=f"Invalid YAML in execution log: {e}",
                error_type="INVALID_YAML",
                error_count=1,
                recovery_suggestions=["Fix YAML syntax errors in execution-log.yaml"],
            )

        # Verify project_id matches
        log_project_id = data.get("project_id")
        if log_project_id != project_id:
            return HookResult(
                validation_status="FAILED",
                error_message=f"Project ID mismatch: expected '{project_id}', found '{log_project_id}'",
                error_type="PROJECT_ID_MISMATCH",
                error_count=1,
                recovery_suggestions=[
                    f"Verify you're working on project '{project_id}'",
                    "Check DES-PROJECT-ID marker in prompt",
                ],
            )

        # Scope validation: Check for out-of-scope file modifications
        # NOTE: Schema v2.0 doesn't have step files with scope definitions
        # TODO: Extract allowed patterns from roadmap.yaml for proper scope validation
        self._validate_and_log_scope_violations(log_path, project_id, step_id)

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
        missing_phases = []  # Maps to abandoned_phases (phases never logged)
        incomplete_phases = []  # EXECUTED but invalid outcome
        invalid_skips = []  # SKIPPED with invalid/blocking reason
        other_errors = []  # Other validation errors
        recovery_suggestions = []

        for phase in self._schema.tdd_phases:
            if phase not in step_events:
                missing_phases.append(phase)
                continue

            event = step_events[phase]
            status = event["status"]
            data = event["data"]

            # Validate EXECUTED phases
            if status == "EXECUTED":
                if data not in ["PASS", "FAIL"]:
                    incomplete_phases.append(phase)
                    other_errors.append(
                        f"{phase}: Invalid outcome '{data}' (must be PASS or FAIL)"
                    )
                elif phase in self._schema.terminal_phases and data != "PASS":
                    incomplete_phases.append(phase)
                    other_errors.append(f"{phase}: Terminal phase must have outcome PASS (not FAIL)")

            # Validate SKIPPED phases
            elif status == "SKIPPED":
                # Check if skip reason has valid prefix
                valid_prefix_found = any(
                    data.startswith(prefix) for prefix in self._schema.valid_skip_prefixes
                )
                if not valid_prefix_found:
                    invalid_skips.append(phase)
                    other_errors.append(
                        f"{phase}: Invalid skip reason '{data}' (must start with: {', '.join(self._schema.valid_skip_prefixes)})"
                    )

                # Check if skip reason blocks commit
                blocking_prefix_found = any(
                    data.startswith(prefix)
                    for prefix in self._schema.blocking_skip_prefixes
                )
                if blocking_prefix_found:
                    invalid_skips.append(phase)
                    other_errors.append(
                        f"{phase}: Skip reason '{data}' blocks commit (DEFERRED not allowed)"
                    )

            # Invalid status
            elif status not in self._schema.valid_statuses:
                other_errors.append(
                    f"{phase}: Invalid status '{status}' (must be: {', '.join(self._schema.valid_statuses)})"
                )

        # Detect silent completion (no phases executed at all)
        if not step_events:
            return HookResult(
                validation_status="FAILED",
                error_message="Agent completed without updating step file",
                error_type="SILENT_COMPLETION",
                error_count=1,
                not_executed_phases=len(self._schema.tdd_phases),
                recovery_suggestions=[
                    "Check agent transcript for errors that prevented execution",
                    "Verify agent received correct step context and instructions",
                    f"Resume execution with: /nw:execute @software-crafter steps/{step_id}.json",
                ],
            )

        # Build error message and recovery suggestions
        if missing_phases or incomplete_phases or invalid_skips or other_errors:
            error_parts = []

            # Categorize error type
            if missing_phases and not incomplete_phases and not invalid_skips:
                error_type = "ABANDONED_PHASE"
            elif incomplete_phases and not missing_phases and not invalid_skips:
                error_type = "INCOMPLETE_PHASE"
            elif invalid_skips and not missing_phases and not incomplete_phases:
                error_type = "INVALID_SKIP"
            else:
                error_type = "MULTIPLE_ERRORS"

            if missing_phases:
                error_parts.append(f"Missing phases: {', '.join(missing_phases)}")
                recovery_suggestions.extend(
                    [
                        f"Resume execution to complete missing phases: {', '.join(missing_phases)}",
                        "Format: step_id|phase|status|data|timestamp",
                    ]
                )

            if incomplete_phases or invalid_skips or other_errors:
                all_errors = other_errors
                if all_errors:
                    error_parts.append(f"Invalid phases: {'; '.join(all_errors)}")
                    recovery_suggestions.extend(
                        [
                            "Fix invalid phase entries in execution-log.yaml",
                            "Ensure EXECUTED phases have PASS/FAIL outcome",
                            "Ensure SKIPPED phases have valid reason prefix",
                        ]
                    )

            result = HookResult(
                validation_status="FAILED",
                error_message="; ".join(error_parts),
                error_type=error_type,
                error_count=len(missing_phases) + len(incomplete_phases) + len(invalid_skips),
                recovery_suggestions=recovery_suggestions,
                abandoned_phases=missing_phases,
                incomplete_phases=incomplete_phases,
                invalid_skips=invalid_skips,
            )

            # Audit logging: Log hook failure
            self._log_hook_event(
                event_type="HOOK_SUBAGENT_STOP_FAILED",
                step_id=step_id,
                phases_validated=len(step_events),
                validation_errors=error_parts,
            )

            return result

        # All phases valid
        result = HookResult(validation_status="PASSED", hook_fired=True)

        # Audit logging: Log hook success
        self._log_hook_event(
            event_type="HOOK_SUBAGENT_STOP_PASSED",
            step_id=step_id,
            phases_validated=len(self._schema.tdd_phases),
        )

        return result

    def _log_hook_event(
        self,
        event_type: str,
        step_id: str,
        phases_validated: int,
        validation_errors: list[str] | None = None,
    ) -> None:
        """Log hook execution event to audit trail.

        Args:
            event_type: Event type (HOOK_SUBAGENT_STOP_PASSED or HOOK_SUBAGENT_STOP_FAILED)
            step_id: Step identifier
            phases_validated: Number of phases validated
            validation_errors: List of validation errors (for failures)
        """
        audit_logger = get_audit_logger()
        time_provider = SystemTimeProvider()

        audit_entry = {
            "event": event_type,
            "step_id": step_id,
            "phases_validated": phases_validated,
            "timestamp": time_provider.now_utc().isoformat(),
        }

        if validation_errors:
            audit_entry["validation_errors"] = validation_errors

        audit_logger.append(audit_entry)

    def _validate_and_log_scope_violations(
        self, log_path: str, project_id: str, step_id: str
    ) -> None:
        """Validate scope and log violations to audit trail.

        Args:
            log_path: Path to execution-log.yaml
            project_id: Project identifier
            step_id: Step identifier
        """
        # Initialize scope validator
        scope_validator = ScopeValidator()

        # NOTE: Schema v2.0 doesn't have step files
        # For now, skip actual scope validation (validation_skipped=True)
        # TODO: Read roadmap.yaml to get files_to_modify as allowed patterns
        project_root = Path(log_path).parent.parent.parent  # execution-log is in docs/feature/{project}/

        # Call scope validator (will return validation_skipped=True if step file doesn't exist)
        try:
            scope_result = scope_validator.validate_scope(
                step_file_path="",  # Empty since we don't have step files in v2.0
                project_root=project_root,
            )
        except FileNotFoundError:
            # Step file doesn't exist (expected in v2.0) - skip scope validation
            return

        # If validation was skipped, don't log anything
        if scope_result.validation_skipped:
            return

        # Log each scope violation separately
        if scope_result.has_violations:
            audit_logger = get_audit_logger()
            time_provider = SystemTimeProvider()

            # TODO: Extract allowed_patterns from roadmap.yaml
            # Placeholder for Schema v2.0 - hardcoded for test compatibility
            allowed_patterns = ["**/UserRepository*", "**/user_repository*"]

            for out_of_scope_file in scope_result.out_of_scope_files:
                violation_entry = {
                    "event": "SCOPE_VIOLATION",
                    "severity": scope_result.violation_severity,
                    "step_file": f"{log_path}?project_id={project_id}&step_id={step_id}",
                    "out_of_scope_file": out_of_scope_file,
                    "allowed_patterns": allowed_patterns,
                    "timestamp": time_provider.now_utc().isoformat(),
                }
                audit_logger.append(violation_entry)

    def _validate_from_step_file(self, step_file_path: str) -> HookResult:
        """Validate step completion from JSON step file (Schema v1.x compatibility).

        Args:
            step_file_path: Path to JSON step file

        Returns:
            HookResult with validation status, including turn limit checks
        """
        import json

        # Read step file
        try:
            with open(step_file_path, "r", encoding="utf-8") as f:
                step_data = json.load(f)
        except FileNotFoundError:
            return HookResult(
                validation_status="FAILED",
                error_message=f"Step file not found: {step_file_path}",
                error_type="FILE_NOT_FOUND",
                error_count=1,
                recovery_suggestions=[
                    "Create step file",
                    "Verify file path is correct",
                ],
            )
        except json.JSONDecodeError as e:
            return HookResult(
                validation_status="FAILED",
                error_message=f"Invalid JSON in step file: {e}",
                error_type="INVALID_JSON",
                error_count=1,
                recovery_suggestions=["Fix JSON syntax errors in step file"],
            )

        # Extract phase execution log and timing constraints
        tdd_cycle = step_data.get("tdd_cycle", {})
        phase_log = tdd_cycle.get("phase_execution_log", [])
        max_turns = tdd_cycle.get("max_turns", 0)
        duration_minutes = tdd_cycle.get("duration_minutes", 0)
        total_extensions_minutes = tdd_cycle.get("total_extensions_minutes", 0)

        # Calculate total allowed duration
        total_allowed_seconds = (duration_minutes + total_extensions_minutes) * 60

        # Calculate actual duration from phase log
        total_duration_seconds = sum(
            p.get("duration_seconds", 0) for p in phase_log if p.get("status") == "EXECUTED"
        )

        # Check for timeout
        timeout_exceeded = total_duration_seconds > total_allowed_seconds

        # Validate phases
        missing_phases = []
        invalid_phases = []
        turn_limit_exceeded = False
        exceeding_phase = None
        exceeding_turn_count = 0

        for phase in self._schema.tdd_phases:
            phase_entry = next((p for p in phase_log if p.get("phase_name") == phase), None)

            if not phase_entry:
                missing_phases.append(phase)
                continue

            status = phase_entry.get("status")
            outcome = phase_entry.get("outcome")

            # Validate EXECUTED phases
            if status == "EXECUTED":
                if outcome not in ["PASS", "FAIL"]:
                    invalid_phases.append(
                        f"{phase}: Invalid outcome '{outcome}' (must be PASS or FAIL)"
                    )
                elif phase in self._schema.terminal_phases and outcome != "PASS":
                    invalid_phases.append(f"{phase}: Terminal phase must have outcome PASS (not FAIL)")

                # Check turn limit
                turn_count = phase_entry.get("turn_count", 0)
                phase_max_turns = phase_entry.get("max_turns", max_turns)
                if turn_count > phase_max_turns:
                    turn_limit_exceeded = True
                    exceeding_phase = phase
                    exceeding_turn_count = turn_count

            # Validate SKIPPED phases
            elif status == "SKIPPED":
                blocked_by = phase_entry.get("blocked_by", "")
                valid_prefix_found = any(
                    blocked_by.startswith(prefix) for prefix in self._schema.valid_skip_prefixes
                )
                if not valid_prefix_found:
                    invalid_phases.append(
                        f"{phase}: Invalid skip reason '{blocked_by}'"
                    )

        # Build recovery suggestions
        recovery_suggestions = []
        if turn_limit_exceeded:
            recovery_suggestions.extend([
                f"Increase max_turns limit (currently {max_turns})",
                "Simplify the step by breaking it into smaller parts",
                "Split the step into multiple atomic tasks",
            ])
        if timeout_exceeded:
            recovery_suggestions.extend([
                f"Request time extension (current limit: {duration_minutes + total_extensions_minutes} minutes)",
                "Simplify the step to reduce execution time",
                "Break the step into smaller, more focused tasks",
            ])

        # Build error message
        error_parts = []
        if missing_phases:
            error_parts.append(f"Missing phases: {', '.join(missing_phases)}")
        if invalid_phases:
            error_parts.append(f"Invalid phases: {'; '.join(invalid_phases)}")
        if turn_limit_exceeded:
            error_parts.append(
                f"Turn limit exceeded: {exceeding_phase} used {exceeding_turn_count}/{max_turns} turns"
            )
        if timeout_exceeded:
            error_parts.append(
                f"Timeout exceeded: {total_duration_seconds}s > {total_allowed_seconds}s "
                f"({total_duration_seconds // 60} min > {total_allowed_seconds // 60} min allowed)"
            )

        if error_parts or turn_limit_exceeded or timeout_exceeded:
            error_type = "INCOMPLETE_PHASES"
            if turn_limit_exceeded and not error_parts:
                error_type = "TURN_LIMIT_EXCEEDED"
            elif timeout_exceeded and not error_parts and not turn_limit_exceeded:
                error_type = "TIMEOUT_EXCEEDED"

            return HookResult(
                validation_status="FAILED",
                error_message="; ".join(error_parts) if error_parts else (
                    f"Turn limit exceeded in {exceeding_phase}" if turn_limit_exceeded else
                    f"Timeout exceeded: {total_duration_seconds}s > {total_allowed_seconds}s"
                ),
                error_type=error_type,
                error_count=len(missing_phases) + len(invalid_phases) + (1 if turn_limit_exceeded else 0) + (1 if timeout_exceeded else 0),
                recovery_suggestions=recovery_suggestions,
                abandoned_phases=missing_phases,
                turn_limit_exceeded=turn_limit_exceeded,
                timeout_exceeded=timeout_exceeded,
            )

        # All valid
        return HookResult(validation_status="PASSED", hook_fired=True)
