"""PostToolUseService - checks audit log for sub-agent failures.

Concrete service (no abstract port) per ADR-2: only one consumer,
only one implementation. Extracting an interface is trivial if needed later.

Called by: ClaudeCodeHookAdapter when PostToolUse hook fires after Task returns.
"""

from __future__ import annotations

from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from des.ports.driven_ports.audit_log_reader import AuditLogReader


class PostToolUseService:
    """Checks if the last sub-agent run failed DES validation.

    Reads the most recent HOOK_SUBAGENT_STOP_FAILED entry from the audit log.
    If found (with allowed_despite_failure=True), builds an additionalContext
    string for the parent orchestrator.

    If the last entry is HOOK_SUBAGENT_STOP_PASSED or no entry exists,
    returns None (clean passthrough).
    """

    def __init__(self, audit_reader: AuditLogReader) -> None:
        self._audit_reader = audit_reader

    def check_completion_status(self) -> str | None:
        """Check if the last sub-agent run had a DES failure.

        Returns:
            additionalContext string if failure detected, None otherwise.
        """
        # Look for the most recent FAILED entry
        failed_entry = self._audit_reader.read_last_entry(
            event_type="HOOK_SUBAGENT_STOP_FAILED",
        )

        if failed_entry is None:
            return None

        # Only report if this was an allowed-despite-failure (Layer 1 gave up)
        if not failed_entry.get("allowed_despite_failure"):
            return None

        # Check if a PASSED entry came after this FAILED entry
        # (meaning the sub-agent was retried and succeeded)
        passed_entry = self._audit_reader.read_last_entry(
            event_type="HOOK_SUBAGENT_STOP_PASSED",
        )
        if passed_entry is not None:
            # A passed entry exists - compare timestamps to see if it's more recent
            passed_ts = passed_entry.get("timestamp", "")
            failed_ts = failed_entry.get("timestamp", "")
            if passed_ts >= failed_ts:
                return None

        # Build notification for parent
        feature_name = failed_entry.get("feature_name", "unknown")
        step_id = failed_entry.get("step_id", "unknown")
        errors = failed_entry.get("validation_errors", [])
        error_text = "; ".join(errors) if errors else "Unknown validation failure"

        return (
            f"DES STEP INCOMPLETE [{feature_name}/{step_id}]\n"
            f"Status: FAILED\n"
            f"Errors: {error_text}\n"
            f"\n"
            f"The sub-agent failed to complete all required TDD phases.\n"
            f"You should resume or retry the step to complete the missing work."
        )
