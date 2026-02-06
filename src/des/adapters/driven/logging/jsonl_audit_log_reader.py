"""JsonlAuditLogReader - driven adapter for reading audit events.

Implements the AuditLogReader port by reading JSONL files.
Uses the same log directory resolution as JsonlAuditLogWriter.
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from src.des.ports.driven_ports.audit_log_reader import AuditLogReader


class JsonlAuditLogReader(AuditLogReader):
    """Reads audit events from JSONL files.

    Scans today's log file backward to find the most recent matching entry.
    Uses same directory resolution as JsonlAuditLogWriter.
    """

    def __init__(self, log_dir: str | Path | None = None) -> None:
        if log_dir is None:
            log_dir = self._resolve_log_directory()
        self._log_dir = Path(log_dir)

    def read_last_entry(
        self,
        event_type: str | None = None,
        feature_name: str | None = None,
        step_id: str | None = None,
    ) -> dict[str, Any] | None:
        """Read the most recent audit entry matching the given filters.

        Scans today's log file from end to start for efficiency.

        Returns:
            Most recent matching entry as dict, or None if not found.
        """
        log_file = self._get_today_log_file()
        if log_file is None or not log_file.exists():
            return None

        try:
            lines = log_file.read_text().strip().splitlines()
        except (OSError, PermissionError):
            return None

        # Scan backward for most recent match
        for line in reversed(lines):
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
            except json.JSONDecodeError:
                continue

            if self._matches(entry, event_type, feature_name, step_id):
                return entry

        return None

    def _matches(
        self,
        entry: dict,
        event_type: str | None,
        feature_name: str | None,
        step_id: str | None,
    ) -> bool:
        """Check if entry matches all provided filters."""
        if event_type and entry.get("event") != event_type:
            return False
        if feature_name and entry.get("feature_name") != feature_name:
            return False
        return not (step_id and entry.get("step_id") != step_id)

    def _get_today_log_file(self) -> Path | None:
        """Get today's log file path, or None if dir doesn't exist."""
        if not self._log_dir.exists():
            return None
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        return self._log_dir / f"audit-{today}.log"

    def _resolve_log_directory(self) -> Path:
        """Resolve audit log directory using same hierarchy as writer."""
        env_dir = os.environ.get("DES_AUDIT_LOG_DIR")
        if env_dir:
            return Path(env_dir)

        cwd = Path.cwd()
        home = Path.home()
        if cwd != home and str(cwd) not in (
            "/",
            "/usr",
            "/bin",
            "/etc",
            "/var",
            "/tmp",
        ):
            return cwd / ".nwave" / "logs" / "des"

        return home / ".claude" / "des" / "logs"
