"""
Audit logging module for DES (Deterministic Execution System).

Provides append-only, immutable audit trail for compliance verification.
Supports ISO 8601 timestamps, event categorization, and daily log rotation.
"""

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class AuditLogger:
    """Append-only audit logger with immutability guarantees.

    Features:
    - Append-only file operations (no modifications to existing entries)
    - SHA256 content hash tracking for immutability verification
    - ISO 8601 timestamps with millisecond precision
    - Daily log rotation with date-based naming
    - JSONL format output (one JSON object per line)
    - Event categorization (TASK_INVOCATION, PHASE, SUBAGENT_STOP, COMMIT)
    """

    def __init__(self, log_dir: str = ".des/audit"):
        """Initialize audit logger.

        Args:
            log_dir: Directory for audit log files (default: .des/audit)
        """
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.current_log_file = self._get_log_file()
        self._entry_hashes: list[str] = []
        self._load_existing_hashes()

    def _get_log_file(self) -> Path:
        """Get today's log file path with date-based naming.

        Format: audit-YYYY-MM-DD.log (e.g., audit-2026-01-27.log)
        """
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        return self.log_dir / f"audit-{today}.log"

    def _load_existing_hashes(self) -> None:
        """Load existing entry hashes from current log file."""
        if self.current_log_file.exists():
            try:
                with open(self.current_log_file) as f:
                    for line in f:
                        if line.strip():
                            entry = json.loads(line)
                            content = json.dumps(
                                entry, sort_keys=True, separators=(",", ":")
                            )
                            entry_hash = hashlib.sha256(content.encode()).hexdigest()
                            self._entry_hashes.append(entry_hash)
            except Exception:
                # If file is corrupted, start fresh
                self._entry_hashes = []

    def append(self, event: dict[str, Any]) -> None:
        """Append a new event to the audit log (append-only operation).

        Args:
            event: Event dictionary to log (should have 'timestamp' and 'event' fields)

        Raises:
            IOError: If append operation fails
        """
        # Ensure log directory exists (handles cases where temp dirs were cleaned up)
        self.log_dir.mkdir(parents=True, exist_ok=True)

        # Ensure timestamp is ISO 8601 format
        if "timestamp" not in event:
            event["timestamp"] = self._get_iso_timestamp()

        # Serialize to JSONL format (one JSON object per line)
        json_line = json.dumps(event, separators=(",", ":"), sort_keys=True)

        # Calculate hash for immutability tracking
        entry_hash = hashlib.sha256(json_line.encode()).hexdigest()
        self._entry_hashes.append(entry_hash)

        # Append to log file
        with open(self.current_log_file, "a") as f:
            f.write(json_line + "\n")

    def _get_iso_timestamp(self) -> str:
        """Get current timestamp in ISO 8601 format with millisecond precision.

        Format: YYYY-MM-DDTHH:MM:SS.sssZ (e.g., 2026-01-27T14:30:45.123Z)
        """
        now = datetime.now(timezone.utc)
        iso_string = now.strftime("%Y-%m-%dT%H:%M:%S")
        milliseconds = now.microsecond // 1000
        return f"{iso_string}.{milliseconds:03d}Z"

    def compute_hash_of_entries(self, start_idx: int, end_idx: int) -> str:
        """Compute combined hash of entries in range [start_idx, end_idx).

        Args:
            start_idx: Starting index (inclusive)
            end_idx: Ending index (exclusive)

        Returns:
            SHA256 hash of combined entry hashes
        """
        selected_hashes = self._entry_hashes[start_idx:end_idx]
        combined = "".join(selected_hashes)
        return hashlib.sha256(combined.encode()).hexdigest()

    def entry_count(self) -> int:
        """Get total number of entries in audit log."""
        return len(self._entry_hashes)

    def read_entries_for_step(self, step_path: str) -> list[dict[str, Any]]:
        """Read audit entries for a specific step.

        Args:
            step_path: Path to the step file

        Returns:
            List of audit entries for the step
        """
        entries = []
        if self.current_log_file.exists():
            try:
                with open(self.current_log_file) as f:
                    for line in f:
                        if line.strip():
                            entry = json.loads(line)
                            if entry.get("step_path") == step_path:
                                entries.append(entry)
            except Exception:
                pass
        return entries

    def get_entries(self) -> list[dict[str, Any]]:
        """Get all entries from current log file.

        Returns:
            List of all audit entries
        """
        entries = []
        if self.current_log_file.exists():
            try:
                with open(self.current_log_file) as f:
                    for line in f:
                        if line.strip():
                            entry = json.loads(line)
                            entries.append(entry)
            except Exception:
                pass
        return entries

    def get_entries_by_type(self, event_type: str) -> list[dict[str, Any]]:
        """Get audit entries filtered by event type.

        Args:
            event_type: Event type to filter by (e.g., 'SCOPE_VIOLATION')

        Returns:
            List of audit entries matching the event type
        """
        all_entries = self.get_entries()
        return [entry for entry in all_entries if entry.get("event") == event_type]

    def rotate_if_needed(self) -> None:
        """Rotate log file if date has changed (daily rotation)."""
        new_log_file = self._get_log_file()
        if new_log_file != self.current_log_file:
            self.current_log_file = new_log_file
            self._entry_hashes = []
            self._load_existing_hashes()


# Global audit logger instance
# TECHNICAL DEBT: Consider refactoring to dependency injection pattern
# Current singleton pattern works but reduces testability and flexibility.
# Future improvement: Inject AuditLogger through constructor parameters.
# See: Progressive Refactoring Level 4 (Abstraction Refinement)
_audit_logger: AuditLogger | None = None


def get_audit_logger() -> AuditLogger:
    """Get the global audit logger instance.

    Note:
        This singleton pattern is functional but could be improved with
        dependency injection for better testability and flexibility.
        Consider refactoring when making broader architectural changes.
    """
    global _audit_logger
    if _audit_logger is None:
        _audit_logger = AuditLogger()
    return _audit_logger


def log_audit_event(event_type: str, **kwargs) -> None:
    """Log an audit event.

    Args:
        event_type: Type of event (e.g., 'TASK_INVOCATION_STARTED')
        **kwargs: Additional event data
    """
    logger = get_audit_logger()
    logger.rotate_if_needed()

    event = {"timestamp": logger._get_iso_timestamp(), "event": event_type, **kwargs}
    logger.append(event)
