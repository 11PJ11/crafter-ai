"""JsonlAuditLogWriter - driven adapter for writing audit events.

Implements the AuditLogWriter port by appending events to JSONL files.
Replaces the AuditLogger singleton with a proper dependency-injected adapter.

Features retained from legacy AuditLogger:
- Append-only file operations (no modifications to existing entries)
- JSONL format output (one JSON object per line)
- Daily log rotation with date-based naming
- Configurable log directory

Features removed (no longer needed):
- Singleton pattern (replaced by dependency injection)
- SHA256 hash tracking (not required by port contract)
- File permission hardening (orthogonal concern, can be added back)
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path

from src.des.ports.driven_ports.audit_log_writer import AuditEvent, AuditLogWriter


class JsonlAuditLogWriter(AuditLogWriter):
    """Writes audit events to JSONL files.

    Each event is serialized as one JSON line, appended to a daily log file.
    File format: audit-YYYY-MM-DD.log in the configured log directory.
    """

    def __init__(self, log_dir: str | Path | None = None) -> None:
        """Initialize with a log directory.

        Log directory priority (highest to lowest):
        1. Explicit log_dir parameter
        2. DES_AUDIT_LOG_DIR environment variable
        3. Project-local .nwave/logs/des/ (default)
        4. Global ~/.claude/des/logs/ (fallback)

        Args:
            log_dir: Directory for audit log files (default: follows priority above)
        """
        if log_dir is None:
            log_dir = self._resolve_log_directory()

        self._log_dir = Path(log_dir)
        self._log_dir.mkdir(parents=True, exist_ok=True)

    def log_event(self, event: AuditEvent) -> None:
        """Append a single audit event to the log.

        Serializes the AuditEvent to a JSON line and appends to today's log file.
        Must be append-only: no modification of existing entries.

        Args:
            event: The audit event to log
        """
        # Ensure log directory exists (handles temp dir cleanup)
        self._log_dir.mkdir(parents=True, exist_ok=True)

        # Build the JSON entry from the port-defined AuditEvent
        entry = {
            "event": event.event_type,
            "timestamp": event.timestamp,
        }

        # Add optional traceability fields (exclude None values)
        if event.feature_name is not None:
            entry["feature_name"] = event.feature_name
        if event.step_id is not None:
            entry["step_id"] = event.step_id

        # Merge additional event-specific data
        entry.update(event.data)

        # Serialize to compact JSONL
        json_line = json.dumps(entry, separators=(",", ":"), sort_keys=True)

        # Append to today's log file
        log_file = self._get_log_file()
        with open(log_file, "a") as f:
            f.write(json_line + "\n")

    def _get_log_file(self) -> Path:
        """Get today's log file path with date-based naming.

        Format: audit-YYYY-MM-DD.log
        """
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        return self._log_dir / f"audit-{today}.log"

    def _resolve_log_directory(self) -> Path:
        """Resolve audit log directory using configuration hierarchy.

        Priority:
        1. DES_AUDIT_LOG_DIR environment variable
        2. Project-local .nwave/logs/des/
        3. Global ~/.claude/des/logs/ (fallback)

        Returns:
            Path to audit log directory
        """
        # Priority 1: Environment variable
        env_dir = os.environ.get("DES_AUDIT_LOG_DIR")
        if env_dir:
            log_path = Path(env_dir)
            try:
                log_path.mkdir(parents=True, exist_ok=True)
                return log_path
            except (OSError, PermissionError):
                pass  # Fall through to next priority

        # Priority 2: Project-local
        cwd = Path.cwd()
        home = Path.home()
        if cwd != home and str(cwd) not in ("/", "/usr", "/bin", "/etc", "/var", "/tmp"):
            return cwd / ".nwave" / "logs" / "des"

        # Priority 3: Global fallback
        return home / ".claude" / "des" / "logs"
