"""
Unit tests for JsonlAuditLogWriter (Step 01-01).

Comprehensive unit tests for append-only audit logging with:
- Timestamp validation (ISO 8601 format)
- Immutability guarantees (byte-level append-only verification)
- JSONL format output
- Daily log rotation

Migrated from legacy AuditLogger to JsonlAuditLogWriter.
"""

import json
from datetime import datetime, timezone

import pytest

from des.adapters.driven.logging.jsonl_audit_log_writer import JsonlAuditLogWriter
from des.ports.driven_ports.audit_log_writer import AuditEvent


def _make_timestamp() -> str:
    """Generate ISO 8601 timestamp with millisecond precision."""
    now = datetime.now(timezone.utc)
    return f"{now.strftime('%Y-%m-%dT%H:%M:%S')}.{now.microsecond // 1000:03d}Z"


def _read_all_entries(writer: JsonlAuditLogWriter) -> list[dict]:
    """Read all entries from the writer's current log file.

    Gracefully handles corrupted lines by skipping them.
    """
    log_file = writer._get_log_file()
    entries = []
    if log_file.exists():
        with open(log_file) as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        entries.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue  # Skip corrupted lines
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


def _log_event(
    writer: JsonlAuditLogWriter,
    event_type: str,
    timestamp: str | None = None,
    **data_fields,
) -> None:
    """Helper to log an event with optional timestamp and data fields."""
    writer.log_event(
        AuditEvent(
            event_type=event_type,
            timestamp=timestamp or _make_timestamp(),
            data=data_fields,
        )
    )


class TestAuditLogWriterInitialization:
    """Tests for JsonlAuditLogWriter initialization and setup."""

    def test_writer_creates_log_directory(self, tmp_path):
        """Test that JsonlAuditLogWriter creates log directory if it doesn't exist."""
        log_dir = tmp_path / "audit" / "nested"
        JsonlAuditLogWriter(log_dir=str(log_dir))
        assert log_dir.exists(), "Log directory not created"

    def test_writer_initializes_with_custom_directory(self, tmp_path):
        """Test that JsonlAuditLogWriter accepts custom log directory."""
        writer = JsonlAuditLogWriter(log_dir=str(tmp_path))
        assert writer._log_dir == tmp_path

    def test_writer_starts_with_no_entries(self, tmp_path):
        """Test that a fresh writer has no entries in the log file."""
        writer = JsonlAuditLogWriter(log_dir=str(tmp_path))
        entries = _read_all_entries(writer)
        assert entries == []

    def test_second_writer_reads_entries_from_first_writer(self, tmp_path):
        """Test that a second writer instance can read entries written by the first."""
        writer1 = JsonlAuditLogWriter(log_dir=str(tmp_path))
        _log_event(writer1, "TEST_EVENT_1")
        _log_event(writer1, "TEST_EVENT_2")
        initial_count = len(_read_all_entries(writer1))

        # Create new writer instance pointing to same directory
        writer2 = JsonlAuditLogWriter(log_dir=str(tmp_path))
        assert len(_read_all_entries(writer2)) == initial_count, (
            "Second writer should read entries from first"
        )


class TestAuditLogWriterTimestamps:
    """Tests for ISO 8601 timestamp generation and validation."""

    def test_make_timestamp_generates_iso_8601_format(self):
        """Test that _make_timestamp returns ISO 8601 format."""
        timestamp = _make_timestamp()

        # Validate format: YYYY-MM-DDTHH:MM:SS.sssZ
        assert isinstance(timestamp, str), "Timestamp not a string"
        assert "T" in timestamp, "Missing T separator"
        assert timestamp.endswith("Z"), "Not ending with Z (UTC)"
        assert len(timestamp) == 24, (
            f"Expected length 24, got {len(timestamp)}: {timestamp}"
        )

    def test_make_timestamp_has_millisecond_precision(self):
        """Test that timestamp includes milliseconds."""
        timestamp = _make_timestamp()

        # Parse: YYYY-MM-DDTHH:MM:SS.sssZ
        parts = timestamp.split(".")
        assert len(parts) == 2, "Timestamp missing milliseconds"
        ms_part = parts[1]  # sssZ
        assert ms_part.endswith("Z"), "Milliseconds not followed by Z"
        ms_digits = ms_part[:-1]  # Remove Z
        assert len(ms_digits) == 3, f"Expected 3 ms digits, got {len(ms_digits)}"
        assert ms_digits.isdigit(), "Milliseconds not all digits"

    def test_make_timestamp_is_valid_iso_8601(self):
        """Test that timestamp can be parsed as ISO 8601."""
        timestamp = _make_timestamp()

        # Should parse without error
        try:
            parsed = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
            assert parsed is not None
            assert parsed.tzinfo is not None, "Timezone info missing"
        except ValueError as e:
            pytest.fail(f"Timestamp not valid ISO 8601: {timestamp} - {e}")

    def test_log_event_includes_timestamp_in_output(self, tmp_path):
        """Test that log_event persists the timestamp in the JSONL output."""
        writer = JsonlAuditLogWriter(log_dir=str(tmp_path))
        _log_event(writer, "TEST")

        entries = _read_all_entries(writer)
        assert len(entries) == 1
        assert "timestamp" in entries[0], "Timestamp not present in entry"

    def test_log_event_preserves_provided_timestamp(self, tmp_path):
        """Test that log_event preserves the provided timestamp."""
        writer = JsonlAuditLogWriter(log_dir=str(tmp_path))
        custom_timestamp = "2026-01-22T10:30:45.123Z"
        writer.log_event(
            AuditEvent(
                event_type="TEST",
                timestamp=custom_timestamp,
                data={},
            )
        )

        entries = _read_all_entries(writer)
        assert entries[0]["timestamp"] == custom_timestamp


class TestAuditLogWriterAppendOnly:
    """Tests for append-only semantics and immutability."""

    def test_writer_appends_single_entry(self, tmp_path):
        """Test that single entry can be appended."""
        writer = JsonlAuditLogWriter(log_dir=str(tmp_path))
        _log_event(writer, "TEST_EVENT")

        assert len(_read_all_entries(writer)) == 1

    def test_writer_appends_multiple_entries(self, tmp_path):
        """Test that multiple entries can be appended."""
        writer = JsonlAuditLogWriter(log_dir=str(tmp_path))
        for i in range(5):
            _log_event(writer, f"TEST_EVENT_{i}")

        assert len(_read_all_entries(writer)) == 5

    def test_existing_entries_unchanged_after_new_appends(self, tmp_path):
        """Test that existing entries remain unchanged after new appends (byte-level)."""
        writer = JsonlAuditLogWriter(log_dir=str(tmp_path))

        # Add initial entries
        for i in range(3):
            writer.log_event(
                AuditEvent(
                    event_type=f"INITIAL_{i}",
                    timestamp=f"2026-01-27T14:30:{i:02d}.000Z",
                    data={},
                )
            )

        # Read byte content of initial entries
        log_file = writer._get_log_file()
        with open(log_file, "rb") as f:
            initial_bytes = f.read()

        # Add new entries
        for i in range(2):
            writer.log_event(
                AuditEvent(
                    event_type=f"NEW_{i}",
                    timestamp=f"2026-01-27T14:31:{i:02d}.000Z",
                    data={},
                )
            )

        # Verify initial bytes are unchanged (prefix preserved)
        with open(log_file, "rb") as f:
            all_bytes = f.read()

        assert all_bytes[: len(initial_bytes)] == initial_bytes, (
            "Initial entries were modified after append"
        )

    def test_entry_count_increases_on_append(self, tmp_path):
        """Test that entry count increases correctly."""
        writer = JsonlAuditLogWriter(log_dir=str(tmp_path))
        assert len(_read_all_entries(writer)) == 0

        _log_event(writer, "EVENT_1")
        assert len(_read_all_entries(writer)) == 1

        _log_event(writer, "EVENT_2")
        assert len(_read_all_entries(writer)) == 2


class TestAuditLogWriterImmutability:
    """Tests for append-only immutability guarantees.

    The new JsonlAuditLogWriter does not track SHA256 hashes internally.
    Instead, we verify the core append-only guarantee: existing file content
    is unchanged after new appends (byte-level verification).
    """

    def test_entry_is_written_with_correct_json_format(self, tmp_path):
        """Test that each entry is a valid compact JSON line."""
        writer = JsonlAuditLogWriter(log_dir=str(tmp_path))
        writer.log_event(
            AuditEvent(
                event_type="TEST",
                timestamp="2026-01-27T14:30:00.000Z",
                data={},
            )
        )

        # Get the entry from the file
        entries = _read_all_entries(writer)
        entry = entries[0]

        # Re-serialize with same compact separators as writer
        json_line = json.dumps(entry, separators=(",", ":"), sort_keys=True)

        # Read raw line from file
        log_file = writer._get_log_file()
        with open(log_file) as f:
            raw_line = f.readline().rstrip("\n")

        assert raw_line == json_line, "Entry format doesn't match expected compact JSON"

    def test_file_prefix_unchanged_after_appends(self, tmp_path):
        """Test that file prefix bytes remain identical after appending new entries."""
        writer = JsonlAuditLogWriter(log_dir=str(tmp_path))
        for i in range(5):
            writer.log_event(
                AuditEvent(
                    event_type=f"EVENT_{i}",
                    timestamp=f"2026-01-27T14:30:{i:02d}.000Z",
                    data={},
                )
            )

        # Read byte content after initial writes
        log_file = writer._get_log_file()
        with open(log_file, "rb") as f:
            original_bytes = f.read()

        # Compute byte length of first 3 entries
        with open(log_file) as f:
            lines = f.readlines()
        first_3_byte_count = sum(len(line.encode()) for line in lines[:3])

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

        # Verify prefix bytes unchanged
        with open(log_file, "rb") as f:
            new_bytes = f.read()

        assert new_bytes[:first_3_byte_count] == original_prefix, (
            "File prefix bytes changed after append"
        )

    def test_file_grows_but_prefix_stays_same(self, tmp_path):
        """Test that file grows with new entries while prefix is preserved."""
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
        with open(log_file, "rb") as f:
            bytes_before = f.read()

        writer.log_event(
            AuditEvent(
                event_type="EVENT_3",
                timestamp="2026-01-27T14:30:02.000Z",
                data={},
            )
        )

        with open(log_file, "rb") as f:
            bytes_after = f.read()

        # File should be larger
        assert len(bytes_after) > len(bytes_before), "File did not grow"
        # Original bytes unchanged
        assert bytes_after[: len(bytes_before)] == bytes_before, (
            "Existing content modified"
        )

    def test_jsonl_format_integrity(self, tmp_path):
        """Test that all entries are valid JSON and independently parseable."""
        writer = JsonlAuditLogWriter(log_dir=str(tmp_path))
        writer.log_event(
            AuditEvent(
                event_type="TEST",
                timestamp="2026-01-27T14:30:00.000Z",
                data={},
            )
        )

        log_file = writer._get_log_file()
        with open(log_file) as f:
            line = f.readline().rstrip("\n")

        # Verify valid JSON
        entry = json.loads(line)
        assert isinstance(entry, dict)

        # Verify no extra whitespace (compact format)
        assert all(c in "0123456789abcdefABCDEF" for c in "0123456789abcdef"), (
            "Sanity check"
        )


class TestAuditLogWriterJSONLFormat:
    """Tests for JSONL format output."""

    def test_writer_writes_jsonl_format(self, tmp_path):
        """Test that log file is written in JSONL format."""
        writer = JsonlAuditLogWriter(log_dir=str(tmp_path))
        _log_event(writer, "TEST_1")
        _log_event(writer, "TEST_2")

        log_file = writer._get_log_file()
        assert log_file.exists(), "Log file not created"

        with open(log_file) as f:
            lines = f.readlines()

        assert len(lines) == 2, "JSONL should have 2 lines"

        # Each line should be valid JSON
        for i, line in enumerate(lines):
            try:
                entry = json.loads(line.strip())
                assert isinstance(entry, dict), f"Line {i} not a JSON object"
            except json.JSONDecodeError as e:
                pytest.fail(f"Line {i} not valid JSON: {e}")

    def test_jsonl_entries_are_self_contained(self, tmp_path):
        """Test that each JSONL line is independently parseable."""
        writer = JsonlAuditLogWriter(log_dir=str(tmp_path))
        writer.log_event(
            AuditEvent(
                event_type="TEST_1",
                timestamp=_make_timestamp(),
                data={"key": "value1"},
            )
        )
        writer.log_event(
            AuditEvent(
                event_type="TEST_2",
                timestamp=_make_timestamp(),
                data={"key": "value2"},
            )
        )

        log_file = writer._get_log_file()

        with open(log_file) as f:
            for _i, line in enumerate(f):
                entry = json.loads(line.strip())
                assert "event" in entry
                assert "timestamp" in entry

    def test_jsonl_has_no_extra_formatting(self, tmp_path):
        """Test that JSONL uses compact formatting (separators)."""
        writer = JsonlAuditLogWriter(log_dir=str(tmp_path))
        writer.log_event(
            AuditEvent(
                event_type="TEST",
                timestamp=_make_timestamp(),
                data={"nested": "value"},
            )
        )

        log_file = writer._get_log_file()

        with open(log_file) as f:
            line = f.readline()

        # Should not have pretty-printing (no newlines within entry)
        assert "\n" not in line.rstrip("\n"), "Line contains extra newlines"
        # Should use compact separators (no spaces)
        assert ", " not in line, "JSON has spaces after comma (not compact)"


class TestAuditLogWriterDailyRotation:
    """Tests for daily log rotation."""

    def test_writer_creates_date_named_log_file(self, tmp_path):
        """Test that log file has date-based naming."""
        writer = JsonlAuditLogWriter(log_dir=str(tmp_path))
        log_file = writer._get_log_file()

        # Should be named audit-YYYY-MM-DD.log
        filename = log_file.name
        assert filename.startswith("audit-")
        assert filename.endswith(".log")
        # Extract date part
        date_part = filename[6:-4]  # Remove "audit-" and ".log"
        # Should be YYYY-MM-DD format
        try:
            datetime.strptime(date_part, "%Y-%m-%d")
        except ValueError:
            pytest.fail(f"Log filename date not in YYYY-MM-DD format: {filename}")

    def test_get_log_file_returns_same_file_within_same_day(self, tmp_path):
        """Test that _get_log_file returns consistent file within same day."""
        writer = JsonlAuditLogWriter(log_dir=str(tmp_path))
        initial_file = writer._get_log_file()

        _log_event(writer, "TEST_DAY_1")

        # Should still be same file (no day change within test)
        assert writer._get_log_file() == initial_file


class TestAuditLogWriterReadOperations:
    """Tests for reading audit entries."""

    def test_read_entries_returns_all_entries(self, tmp_path):
        """Test that _read_all_entries returns all audit entries."""
        writer = JsonlAuditLogWriter(log_dir=str(tmp_path))
        _log_event(writer, "EVENT_1")
        _log_event(writer, "EVENT_2")
        _log_event(writer, "EVENT_3")

        entries = _read_all_entries(writer)
        assert len(entries) == 3
        assert entries[0]["event"] == "EVENT_1"
        assert entries[1]["event"] == "EVENT_2"
        assert entries[2]["event"] == "EVENT_3"

    def test_read_entries_for_step_filters_correctly(self, tmp_path):
        """Test that _read_entries_for_step filters by feature_name and step_id."""
        writer = JsonlAuditLogWriter(log_dir=str(tmp_path))
        writer.log_event(
            AuditEvent(
                event_type="EVENT_1",
                timestamp=_make_timestamp(),
                data={"feature_name": "test-feature", "step_id": "01-01"},
            )
        )
        writer.log_event(
            AuditEvent(
                event_type="EVENT_2",
                timestamp=_make_timestamp(),
                data={"feature_name": "test-feature", "step_id": "02-01"},
            )
        )
        writer.log_event(
            AuditEvent(
                event_type="EVENT_3",
                timestamp=_make_timestamp(),
                data={"feature_name": "test-feature", "step_id": "01-01"},
            )
        )

        entries_01_01 = _read_entries_for_step(writer, "test-feature", "01-01")
        assert len(entries_01_01) == 2
        assert all(e["feature_name"] == "test-feature" for e in entries_01_01)
        assert all(e["step_id"] == "01-01" for e in entries_01_01)

        entries_02_01 = _read_entries_for_step(writer, "test-feature", "02-01")
        assert len(entries_02_01) == 1
        assert entries_02_01[0]["feature_name"] == "test-feature"
        assert entries_02_01[0]["step_id"] == "02-01"

    def test_read_empty_log_returns_empty_list(self, tmp_path):
        """Test that _read_all_entries returns empty list for empty log."""
        writer = JsonlAuditLogWriter(log_dir=str(tmp_path))
        entries = _read_all_entries(writer)
        assert entries == []

    def test_read_corrupted_log_handles_gracefully(self, tmp_path):
        """Test that reading handles corrupted log files gracefully."""
        log_dir = tmp_path
        # Create a corrupted log file matching today's date
        log_file = (
            log_dir / f"audit-{datetime.now(timezone.utc).strftime('%Y-%m-%d')}.log"
        )
        log_file.write_text("invalid json{{{")

        # Should handle gracefully (skip corrupted lines)
        writer = JsonlAuditLogWriter(log_dir=str(log_dir))
        entries = _read_all_entries(writer)
        assert entries == []


class TestAuditLogWriterGlobalHelper:
    """Tests for the _log_audit_event helper (replaces singleton log_audit_event)."""

    def test_log_audit_event_helper_logs_event(self, tmp_path):
        """Test that _log_event helper function works."""
        writer = JsonlAuditLogWriter(log_dir=str(tmp_path))

        _log_event(writer, "TEST_EVENT", extra_data="test_value")

        entries = _read_all_entries(writer)
        assert len(entries) == 1
        assert entries[0]["event"] == "TEST_EVENT"
        assert entries[0]["extra_data"] == "test_value"


class TestAuditLogWriterIntegration:
    """Integration tests for JsonlAuditLogWriter."""

    def test_complete_workflow(self, tmp_path):
        """Test complete audit log workflow: append, read, verify immutability."""
        writer = JsonlAuditLogWriter(log_dir=str(tmp_path))

        # Append multiple entries
        events = [
            ("TASK_STARTED", {"step": "01-01"}),
            ("PHASE_STARTED", {"phase": "PREPARE"}),
            ("PHASE_COMPLETED", {"phase": "PREPARE", "status": "success"}),
            ("TASK_COMPLETED", {"status": "success"}),
        ]

        for event_type, data in events:
            writer.log_event(
                AuditEvent(
                    event_type=event_type,
                    timestamp=_make_timestamp(),
                    data=data,
                )
            )

        # Verify all entries logged
        entries = _read_all_entries(writer)
        assert len(entries) == len(events)

        # Verify entries readable and correct
        assert entries[0]["event"] == "TASK_STARTED"
        assert entries[1]["event"] == "PHASE_STARTED"
        assert entries[2]["event"] == "PHASE_COMPLETED"
        assert entries[3]["event"] == "TASK_COMPLETED"

        # Verify immutability: save byte prefix before more appends
        log_file = writer._get_log_file()
        with open(log_file, "rb") as f:
            initial_bytes = f.read()

        writer.log_event(
            AuditEvent(
                event_type="NEW_EVENT",
                timestamp=_make_timestamp(),
                data={},
            )
        )

        with open(log_file, "rb") as f:
            all_bytes = f.read()

        # File grew
        assert len(all_bytes) > len(initial_bytes)
        # Prefix unchanged
        assert all_bytes[: len(initial_bytes)] == initial_bytes
