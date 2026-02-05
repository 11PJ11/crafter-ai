"""
Audit logging module for DES (Deterministic Execution System).

Provides append-only, immutable audit trail for compliance verification.
Supports ISO 8601 timestamps, event categorization, and daily log rotation.
"""

import hashlib
import json
import os
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

    def __init__(self, log_dir: str | Path | None = None):
        """Initialize audit logger.

        Log directory priority (highest to lowest):
        1. Explicit log_dir parameter
        2. DES_AUDIT_LOG_DIR environment variable
        3. audit_log_dir from .nwave/des-config.json
        4. Project-local .nwave/logs/des/ (default)
        5. Global ~/.claude/des/logs/ (fallback)

        Args:
            log_dir: Directory for audit log files (default: follows priority above)
        """
        if log_dir is None:
            log_dir = self._resolve_log_directory()

        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.current_log_file = self._get_log_file()
        self._entry_hashes: list[str] = []
        self._load_existing_hashes()

    def _resolve_log_directory(self) -> Path:
        """Resolve audit log directory using configuration hierarchy.

        Priority:
        1. DES_AUDIT_LOG_DIR environment variable (validated for writability)
        2. audit_log_dir from .nwave/des-config.json (validated for writability)
        3. Project-local .nwave/logs/des/ (default)
        4. Global ~/.claude/des/logs/ (fallback)

        Returns:
            Path to audit log directory
        """
        # Priority 1: Environment variable (with writability validation)
        env_dir = os.environ.get("DES_AUDIT_LOG_DIR")
        if env_dir:
            log_path = Path(env_dir)
            if self._validate_log_directory(log_path, "DES_AUDIT_LOG_DIR"):
                return log_path
            # Fall through to next priority if not writable

        # Priority 2: Config file (with writability validation)
        config_dir = self._load_config_log_dir()
        if config_dir:
            if self._validate_log_directory(config_dir, "config file"):
                return config_dir
            # Fall through to next priority if not writable

        # Priority 3: Project-local default
        project_local = self._get_project_local_dir()
        if project_local:
            return project_local

        # Priority 4: Global fallback
        return Path.home() / ".claude" / "des" / "logs"

    def _validate_log_directory(self, log_path: Path, source: str) -> bool:
        """Validate that a log directory is writable.

        Args:
            log_path: Path to validate
            source: Description of where the path came from (for logging)

        Returns:
            True if directory is writable, False otherwise
        """
        try:
            # Try to create directory if it doesn't exist
            log_path.mkdir(parents=True, exist_ok=True)

            # Test writability by creating and removing a test file
            test_file = log_path / ".write_test"
            test_file.touch()
            test_file.unlink()
            return True

        except (OSError, PermissionError) as e:
            # Log warning and return False to fall through to next priority
            import sys
            print(
                f"Warning: Audit log directory from {source} is not writable: "
                f"{log_path} ({e}). Falling back to next priority.",
                file=sys.stderr
            )
            return False

    def _load_config_log_dir(self) -> Path | None:
        """Load audit_log_dir from .nwave/des-config.json if it exists.

        Returns:
            Path from config file, or None if not found
        """
        config_file = Path.cwd() / ".nwave" / "des-config.json"
        if not config_file.exists():
            return None

        try:
            with open(config_file) as f:
                config = json.load(f)
                log_dir = config.get("audit_log_dir")
                if log_dir:
                    return Path(log_dir)
        except (OSError, json.JSONDecodeError, KeyError):
            pass

        return None

    def _get_project_local_dir(self) -> Path | None:
        """Get project-local audit log directory.

        Uses project-local directory unless we're clearly in the home directory
        or a system directory.

        Returns:
            Project-local log directory, or None if should use global fallback
        """
        cwd = Path.cwd()
        home = Path.home()

        # If we're in home directory itself (not a subdirectory), use global
        if cwd == home:
            return None

        # If we're in a system directory, use global
        system_dirs = ["/", "/usr", "/bin", "/etc", "/var", "/tmp"]
        if str(cwd) in system_dirs:
            return None

        # Otherwise, use project-local (includes /tmp/test-project subdirs)
        return cwd / ".nwave" / "logs" / "des"

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

        # Security: Harden file permissions if log file exists
        # Prevent unauthorized modifications by restricting to owner read/write, group read
        if self.current_log_file.exists():
            current_perms = self.current_log_file.stat().st_mode & 0o777
            # Check if file has group or other write permissions (security risk)
            if current_perms & 0o022:  # Group or other write bits set
                try:
                    self.current_log_file.chmod(0o640)  # rw-r----- (owner rw, group r)
                except (OSError, PermissionError):
                    # If we can't change permissions, continue anyway
                    # (better to have logs than fail)
                    pass

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

        # Security: Set restrictive permissions on newly created log files
        if not (self.current_log_file.stat().st_mode & 0o777) == 0o640:
            try:
                self.current_log_file.chmod(0o640)  # rw-r----- (owner rw, group r)
            except (OSError, PermissionError):
                # If we can't change permissions, continue anyway
                pass

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

    def read_entries_for_step(
        self, feature_name: str | None, step_id: str | None
    ) -> list[dict[str, Any]]:
        """Read audit entries for a specific step.

        Args:
            feature_name: Feature/project name (e.g., 'audit-log-refactor')
            step_id: Step identifier (e.g., '01-01')

        Returns:
            List of audit entries for the step. Returns empty list if either
            feature_name or step_id is None.
        """
        # AC3: Return empty list if either parameter is None
        if feature_name is None or step_id is None:
            return []

        entries = []
        if self.current_log_file.exists():
            try:
                with open(self.current_log_file) as f:
                    for line in f:
                        if line.strip():
                            entry = json.loads(line)
                            # AC2: Filter by feature_name AND step_id (both must match)
                            # AC5: Legacy step_path field ignored in filtering
                            if (
                                entry.get("feature_name") == feature_name
                                and entry.get("step_id") == step_id
                            ):
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
_audit_logger_cwd: Path | None = None


def get_audit_logger() -> AuditLogger:
    """Get the global audit logger instance.

    Note:
        This singleton pattern is functional but could be improved with
        dependency injection for better testability and flexibility.
        Consider refactoring when making broader architectural changes.

    Project isolation:
        Automatically creates new logger instance when working directory changes
        to ensure each project gets its own audit trail.
    """
    global _audit_logger, _audit_logger_cwd
    current_cwd = Path.cwd()

    # Reset logger if working directory has changed (project isolation)
    if _audit_logger_cwd is not None and _audit_logger_cwd != current_cwd:
        _audit_logger = None
        _audit_logger_cwd = None

    if _audit_logger is None:
        _audit_logger = AuditLogger()
        _audit_logger_cwd = current_cwd
    return _audit_logger


def reset_audit_logger() -> None:
    """Reset the global audit logger instance.

    Useful for testing and when switching between projects.
    Forces creation of a new logger with current working directory.
    """
    global _audit_logger, _audit_logger_cwd
    _audit_logger = None
    _audit_logger_cwd = None


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
