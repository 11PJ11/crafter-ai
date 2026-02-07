"""
Unit tests for JsonlAuditLogWriter (US-004: Audit Trail).

Tests append-only semantics, immutability guarantees, and timestamp formatting.

Migrated from legacy AuditLogger to JsonlAuditLogWriter.
"""

import json
from datetime import datetime, timezone

from des.adapters.driven.logging.jsonl_audit_log_writer import JsonlAuditLogWriter
from des.ports.driven_ports.audit_log_writer import AuditEvent


def _make_timestamp() -> str:
    """Generate ISO 8601 timestamp with millisecond precision."""
    now = datetime.now(timezone.utc)
    return f"{now.strftime('%Y-%m-%dT%H:%M:%S')}.{now.microsecond // 1000:03d}Z"


def _read_all_entries(writer: JsonlAuditLogWriter) -> list[dict]:
    """Read all entries from the writer's current log file."""
    log_file = writer._get_log_file()
    entries = []
    if log_file.exists():
        with open(log_file) as f:
            for line in f:
                if line.strip():
                    entries.append(json.loads(line))
    return entries


def _read_entries_for_step(
    writer: JsonlAuditLogWriter,
    feature_name: str | None,
    step_id: str | None,
) -> list[dict]:
    """Read entries filtered by feature_name and step_id."""
    if feature_name is None or step_id is None:
        return []
    return [
        e
        for e in _read_all_entries(writer)
        if e.get("feature_name") == feature_name and e.get("step_id") == step_id
    ]


class TestAuditLogWriterAppendOnlySemantics:
    """Test append-only file operations."""

    def test_writer_creates_log_file_on_first_event(self, tmp_path):
        """Writer should create log file on first log_event (lazy initialization)."""
        writer = JsonlAuditLogWriter(log_dir=str(tmp_path))
        log_file = writer._get_log_file()

        # File doesn't exist until first log_event
        assert not log_file.exists()

        # After first log_event, file is created
        writer.log_event(
            AuditEvent(
                event_type="TEST_EVENT",
                timestamp="2026-01-27T14:30:00.000Z",
                data={},
            )
        )
        assert log_file.exists()

    def test_log_event_adds_entry_to_file(self, tmp_path):
        """log_event() should add new entry to log file."""
        writer = JsonlAuditLogWriter(log_dir=str(tmp_path))

        writer.log_event(
            AuditEvent(
                event_type="TEST_EVENT",
                timestamp="2026-01-27T14:30:45.123Z",
                data={"step_path": "steps/01-01.json"},
            )
        )

        # Verify entry was added
        entries = _read_all_entries(writer)
        assert len(entries) == 1

        # Verify file contains the entry
        log_file = writer._get_log_file()
        with open(log_file) as f:
            lines = f.readlines()
        assert len(lines) == 1
        parsed = json.loads(lines[0])
        assert parsed["event"] == "TEST_EVENT"

    def test_multiple_events_create_multiple_entries(self, tmp_path):
        """Multiple log_event calls should create multiple log entries."""
        writer = JsonlAuditLogWriter(log_dir=str(tmp_path))

        for i in range(5):
            writer.log_event(
                AuditEvent(
                    event_type=f"EVENT_{i}",
                    timestamp=f"2026-01-27T14:30:{i:02d}.000Z",
                    data={"count": i},
                )
            )

        entries = _read_all_entries(writer)
        assert len(entries) == 5

    def test_jsonl_format_one_entry_per_line(self, tmp_path):
        """Log file should be in JSONL format (one JSON per line)."""
        writer = JsonlAuditLogWriter(log_dir=str(tmp_path))

        writer.log_event(
            AuditEvent(
                event_type="EVENT_1",
                timestamp="2026-01-27T14:30:00.000Z",
                data={},
            )
        )
        writer.log_event(
            AuditEvent(
                event_type="EVENT_2",
                timestamp="2026-01-27T14:30:01.000Z",
                data={},
            )
        )

        log_file = writer._get_log_file()
        with open(log_file) as f:
            lines = f.readlines()

        assert len(lines) == 2
        # Each line should be valid JSON
        for line in lines:
            json.loads(line)


class TestAuditLogWriterImmutability:
    """Test append-only immutability guarantees.

    The new JsonlAuditLogWriter does not track SHA256 hashes internally.
    Instead, we verify the core append-only guarantee: existing file content
    is unchanged after new appends.
    """

    def test_existing_entries_unchanged_after_new_appends(self, tmp_path):
        """Existing entries' content should remain unchanged after new appends."""
        writer = JsonlAuditLogWriter(log_dir=str(tmp_path))

        # Add initial entries
        for i in range(3):
            writer.log_event(
                AuditEvent(
                    event_type=f"EVENT_{i}",
                    timestamp=f"2026-01-27T14:30:{i:02d}.000Z",
                    data={},
                )
            )

        # Read original file content
        log_file = writer._get_log_file()
        with open(log_file) as f:
            original_lines = f.readlines()

        assert len(original_lines) == 3

        # Add more entries
        for i in range(3, 5):
            writer.log_event(
                AuditEvent(
                    event_type=f"EVENT_{i}",
                    timestamp=f"2026-01-27T14:30:{i:02d}.000Z",
                    data={},
                )
            )

        # Verify original lines are unchanged
        with open(log_file) as f:
            all_lines = f.readlines()

        assert len(all_lines) == 5
        # First 3 lines must be identical to original
        for i in range(3):
            assert all_lines[i] == original_lines[i], (
                f"Line {i} was modified after append"
            )

    def test_append_only_never_modifies_existing_content(self, tmp_path):
        """Appending new entries must never modify the byte content of existing entries."""
        writer = JsonlAuditLogWriter(log_dir=str(tmp_path))

        # Add 5 entries
        for i in range(5):
            writer.log_event(
                AuditEvent(
                    event_type=f"EVENT_{i}",
                    timestamp=f"2026-01-27T14:30:{i:02d}.000Z",
                    data={},
                )
            )

        # Read byte content of first 3 entries
        log_file = writer._get_log_file()
        with open(log_file, "rb") as f:
            original_bytes = f.read()

        # Compute how many bytes correspond to first 3 entries
        with open(log_file) as f:
            lines = f.readlines()
        first_3_byte_count = sum(len(line.encode()) for line in lines[:3])

        # Verify first 3 entries are valid
        assert len(lines) == 5
        original_prefix = original_bytes[:first_3_byte_count]

        # Append more entries
        for i in range(5, 8):
            writer.log_event(
                AuditEvent(
                    event_type=f"EVENT_{i}",
                    timestamp=f"2026-01-27T14:30:{i:02d}.000Z",
                    data={},
                )
            )

        # Verify original prefix bytes are unchanged
        with open(log_file, "rb") as f:
            new_bytes = f.read()

        assert new_bytes[:first_3_byte_count] == original_prefix


class TestAuditLogWriterTimestamps:
    """Test ISO 8601 timestamp formatting."""

    def test_timestamp_helper_produces_iso_8601_format(self):
        """_make_timestamp() should return ISO 8601 format with milliseconds."""
        ts = _make_timestamp()

        # Check format: YYYY-MM-DDTHH:MM:SS.sssZ
        assert "T" in ts
        assert ts.endswith("Z")
        assert ts.count(":") == 2  # HH:MM:SS has 2 colons
        assert "." in ts  # Has milliseconds

        # Verify it's parseable as ISO format
        parsed = datetime.fromisoformat(ts.replace("Z", "+00:00"))
        assert isinstance(parsed, datetime)

    def test_event_timestamp_is_preserved_in_log(self, tmp_path):
        """Event timestamp should be preserved in the log file."""
        writer = JsonlAuditLogWriter(log_dir=str(tmp_path))

        ts = _make_timestamp()
        writer.log_event(
            AuditEvent(
                event_type="TEST_EVENT",
                timestamp=ts,
                data={},
            )
        )

        # Read from file to verify timestamp
        entries = _read_all_entries(writer)
        assert len(entries) == 1
        assert "timestamp" in entries[0]
        assert entries[0]["timestamp"] == ts
        assert entries[0]["timestamp"].endswith("Z")


class TestAuditLogWriterEntryContext:
    """Test entry context filtering."""

    def test_read_entries_for_step(self, tmp_path):
        """Entries should be filterable by feature_name and step_id."""
        writer = JsonlAuditLogWriter(log_dir=str(tmp_path))

        # Add entries for different steps using new schema (feature_name, step_id)
        writer.log_event(
            AuditEvent(
                event_type="TASK_START",
                timestamp="2026-01-27T14:30:00.000Z",
                data={
                    "feature_name": "audit-log-refactor",
                    "step_id": "01-01",
                    "step_path": "steps/01-01.json",  # Legacy field
                },
            )
        )
        writer.log_event(
            AuditEvent(
                event_type="TASK_START",
                timestamp="2026-01-27T14:30:01.000Z",
                data={
                    "feature_name": "audit-log-refactor",
                    "step_id": "01-02",
                    "step_path": "steps/01-02.json",  # Legacy field
                },
            )
        )
        writer.log_event(
            AuditEvent(
                event_type="TASK_END",
                timestamp="2026-01-27T14:30:02.000Z",
                data={
                    "feature_name": "audit-log-refactor",
                    "step_id": "01-01",
                    "step_path": "steps/01-01.json",  # Legacy field
                },
            )
        )
        writer.log_event(
            AuditEvent(
                event_type="TASK_START",
                timestamp="2026-01-27T14:30:03.000Z",
                data={
                    "feature_name": "other-feature",
                    "step_id": "01-01",
                    "step_path": "steps/other-01-01.json",
                },
            )
        )

        # AC1: Filter by feature_name and step_id
        entries = _read_entries_for_step(writer, "audit-log-refactor", "01-01")

        # AC2: Filter by feature_name AND step_id
        assert len(entries) == 2
        assert all(e["feature_name"] == "audit-log-refactor" for e in entries)
        assert all(e["step_id"] == "01-01" for e in entries)

        # AC3: Return empty list when feature_name is None
        entries_none_feature = _read_entries_for_step(writer, None, "01-01")
        assert len(entries_none_feature) == 0

        # AC3: Return empty list when step_id is None
        entries_none_step = _read_entries_for_step(writer, "audit-log-refactor", None)
        assert len(entries_none_step) == 0

        # AC4: Return all matching entries for feature + step combination
        entries_01_02 = _read_entries_for_step(writer, "audit-log-refactor", "01-02")
        assert len(entries_01_02) == 1
        assert entries_01_02[0]["step_id"] == "01-02"

        # AC5: Legacy step_path field ignored in filtering
        # (entries have step_path but filtering uses feature_name + step_id)

    def test_get_all_entries(self, tmp_path):
        """All entries should be retrievable from the log file."""
        writer = JsonlAuditLogWriter(log_dir=str(tmp_path))

        # Add 3 entries
        for i in range(3):
            writer.log_event(
                AuditEvent(
                    event_type=f"EVENT_{i}",
                    timestamp=f"2026-01-27T14:30:{i:02d}.000Z",
                    data={},
                )
            )

        entries = _read_all_entries(writer)
        assert len(entries) == 3
        assert [e["event"] for e in entries] == ["EVENT_0", "EVENT_1", "EVENT_2"]


class TestAuditLogWriterDailyRotation:
    """Test daily log rotation via date-based file naming."""

    def test_log_file_has_date_based_name(self, tmp_path):
        """Log file should use date-based naming (audit-YYYY-MM-DD.log)."""
        writer = JsonlAuditLogWriter(log_dir=str(tmp_path))

        # Log an event so the file is created
        writer.log_event(
            AuditEvent(
                event_type="EVENT",
                timestamp="2026-01-27T14:30:00.000Z",
                data={},
            )
        )

        log_file = writer._get_log_file()
        # File should exist
        assert log_file.exists()
        # File name should match audit-YYYY-MM-DD.log pattern
        assert log_file.name.startswith("audit-")
        assert log_file.name.endswith(".log")
        # Date part should be parseable
        date_part = log_file.name.replace("audit-", "").replace(".log", "")
        datetime.strptime(date_part, "%Y-%m-%d")
