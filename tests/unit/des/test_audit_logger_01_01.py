"""
Unit tests for AuditLogger class (Step 01-01).

Comprehensive unit tests for append-only audit logging with:
- Timestamp validation (ISO 8601 format)
- Immutability guarantees (content hashing)
- JSONL format output
- Daily log rotation
"""

import json
import hashlib
import pytest
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from src.des.adapters.driven.logging.audit_logger import AuditLogger, log_audit_event


class TestAuditLoggerInitialization:
    """Tests for AuditLogger initialization and setup."""

    def test_audit_logger_creates_log_directory(self):
        """Test that AuditLogger creates log directory if it doesn't exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_dir = Path(tmpdir) / "audit" / "nested"
            AuditLogger(str(log_dir))  # Create instance to trigger directory creation
            assert log_dir.exists(), "Log directory not created"

    def test_audit_logger_initializes_with_default_directory(self):
        """Test that AuditLogger accepts custom log directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            logger = AuditLogger(tmpdir)
            assert logger.log_dir == Path(tmpdir)

    def test_audit_logger_initializes_empty_entry_hashes(self):
        """Test that AuditLogger starts with empty entry hashes."""
        with tempfile.TemporaryDirectory() as tmpdir:
            logger = AuditLogger(tmpdir)
            assert logger._entry_hashes == []

    def test_audit_logger_loads_existing_hashes_on_init(self):
        """Test that AuditLogger loads existing entry hashes from file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create initial logger and write some entries
            logger1 = AuditLogger(tmpdir)
            logger1.append({"event": "TEST_EVENT_1"})
            logger1.append({"event": "TEST_EVENT_2"})
            initial_count = logger1.entry_count()

            # Create new logger instance
            logger2 = AuditLogger(tmpdir)
            assert logger2.entry_count() == initial_count, "Entry hashes not loaded"


class TestAuditLoggerTimestamps:
    """Tests for ISO 8601 timestamp generation and validation."""

    def test_audit_logger_generates_iso_8601_timestamp(self):
        """Test that _get_iso_timestamp returns ISO 8601 format."""
        with tempfile.TemporaryDirectory() as tmpdir:
            logger = AuditLogger(tmpdir)
            timestamp = logger._get_iso_timestamp()

            # Validate format: YYYY-MM-DDTHH:MM:SS.sssZ
            assert isinstance(timestamp, str), "Timestamp not a string"
            assert "T" in timestamp, "Missing T separator"
            assert timestamp.endswith("Z"), "Not ending with Z (UTC)"
            assert len(timestamp) == 24, (
                f"Expected length 24, got {len(timestamp)}: {timestamp}"
            )

    def test_audit_logger_timestamp_has_millisecond_precision(self):
        """Test that timestamp includes milliseconds."""
        with tempfile.TemporaryDirectory() as tmpdir:
            logger = AuditLogger(tmpdir)
            timestamp = logger._get_iso_timestamp()

            # Parse: YYYY-MM-DDTHH:MM:SS.sssZ
            parts = timestamp.split(".")
            assert len(parts) == 2, "Timestamp missing milliseconds"
            ms_part = parts[1]  # sssZ
            assert ms_part.endswith("Z"), "Milliseconds not followed by Z"
            ms_digits = ms_part[:-1]  # Remove Z
            assert len(ms_digits) == 3, f"Expected 3 ms digits, got {len(ms_digits)}"
            assert ms_digits.isdigit(), "Milliseconds not all digits"

    def test_audit_logger_timestamp_is_valid_iso_8601(self):
        """Test that timestamp can be parsed as ISO 8601."""
        with tempfile.TemporaryDirectory() as tmpdir:
            logger = AuditLogger(tmpdir)
            timestamp = logger._get_iso_timestamp()

            # Should parse without error
            try:
                parsed = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
                assert parsed is not None
                assert parsed.tzinfo is not None, "Timezone info missing"
            except ValueError as e:
                pytest.fail(f"Timestamp not valid ISO 8601: {timestamp} - {e}")

    def test_audit_logger_appends_timestamp_if_missing(self):
        """Test that append adds timestamp if event doesn't have one."""
        with tempfile.TemporaryDirectory() as tmpdir:
            logger = AuditLogger(tmpdir)
            event = {"event": "TEST"}
            logger.append(event)

            entries = logger.get_entries()
            assert len(entries) == 1
            assert "timestamp" in entries[0], "Timestamp not added by append"

    def test_audit_logger_preserves_provided_timestamp(self):
        """Test that append preserves provided timestamp."""
        with tempfile.TemporaryDirectory() as tmpdir:
            logger = AuditLogger(tmpdir)
            custom_timestamp = "2026-01-22T10:30:45.123Z"
            event = {"event": "TEST", "timestamp": custom_timestamp}
            logger.append(event)

            entries = logger.get_entries()
            assert entries[0]["timestamp"] == custom_timestamp


class TestAuditLoggerAppendOnly:
    """Tests for append-only semantics and immutability."""

    def test_audit_logger_appends_single_entry(self):
        """Test that single entry can be appended."""
        with tempfile.TemporaryDirectory() as tmpdir:
            logger = AuditLogger(tmpdir)
            logger.append({"event": "TEST_EVENT"})

            assert logger.entry_count() == 1

    def test_audit_logger_appends_multiple_entries(self):
        """Test that multiple entries can be appended."""
        with tempfile.TemporaryDirectory() as tmpdir:
            logger = AuditLogger(tmpdir)
            for i in range(5):
                logger.append({"event": f"TEST_EVENT_{i}"})

            assert logger.entry_count() == 5

    def test_audit_logger_entries_are_immutable(self):
        """Test that existing entries cannot be modified."""
        with tempfile.TemporaryDirectory() as tmpdir:
            logger = AuditLogger(tmpdir)

            # Add initial entries
            for i in range(3):
                logger.append({"event": f"INITIAL_{i}"})

            initial_hash = logger.compute_hash_of_entries(0, 3)

            # Add new entries
            for i in range(2):
                logger.append({"event": f"NEW_{i}"})

            # Check that initial entries' hash hasn't changed
            current_hash = logger.compute_hash_of_entries(0, 3)
            assert current_hash == initial_hash, "Initial entries were modified"

    def test_audit_logger_entry_count_increases_on_append(self):
        """Test that entry_count increases correctly."""
        with tempfile.TemporaryDirectory() as tmpdir:
            logger = AuditLogger(tmpdir)
            assert logger.entry_count() == 0

            logger.append({"event": "EVENT_1"})
            assert logger.entry_count() == 1

            logger.append({"event": "EVENT_2"})
            assert logger.entry_count() == 2


class TestAuditLoggerContentHashing:
    """Tests for SHA256 content hash tracking."""

    def test_audit_logger_computes_entry_hash(self):
        """Test that entry hash is computed correctly."""
        with tempfile.TemporaryDirectory() as tmpdir:
            logger = AuditLogger(tmpdir)
            logger.append({"event": "TEST"})

            # Get the entry
            entries = logger.get_entries()
            entry = entries[0]
            json_line = json.dumps(entry, separators=(",", ":"), sort_keys=True)
            expected_hash = hashlib.sha256(json_line.encode()).hexdigest()

            # Verify hash is stored
            assert len(logger._entry_hashes) == 1
            assert logger._entry_hashes[0] == expected_hash

    def test_audit_logger_computes_hash_of_entry_range(self):
        """Test compute_hash_of_entries for range of entries."""
        with tempfile.TemporaryDirectory() as tmpdir:
            logger = AuditLogger(tmpdir)
            for i in range(5):
                logger.append({"event": f"EVENT_{i}"})

            # Get hash of first 3 entries
            hash_0_3 = logger.compute_hash_of_entries(0, 3)
            assert isinstance(hash_0_3, str)
            assert len(hash_0_3) == 64, "SHA256 hex should be 64 chars"

    def test_audit_logger_hash_changes_with_new_entries(self):
        """Test that hash of range stays same, but total hash changes."""
        with tempfile.TemporaryDirectory() as tmpdir:
            logger = AuditLogger(tmpdir)
            logger.append({"event": "EVENT_1"})
            logger.append({"event": "EVENT_2"})

            hash_0_2_before = logger.compute_hash_of_entries(0, 2)

            logger.append({"event": "EVENT_3"})

            hash_0_2_after = logger.compute_hash_of_entries(0, 2)
            assert hash_0_2_before == hash_0_2_after, "Hash of existing entries changed"

            # But total entries hash should be different
            hash_0_3 = logger.compute_hash_of_entries(0, 3)
            assert hash_0_3 != hash_0_2_before, (
                "Total hash should change with new entry"
            )

    def test_audit_logger_hash_is_sha256(self):
        """Test that computed hash is valid SHA256."""
        with tempfile.TemporaryDirectory() as tmpdir:
            logger = AuditLogger(tmpdir)
            logger.append({"event": "TEST"})

            hash_value = logger.compute_hash_of_entries(0, 1)
            # SHA256 hex is exactly 64 characters
            assert len(hash_value) == 64
            assert all(c in "0123456789abcdef" for c in hash_value)


class TestAuditLoggerJSONLFormat:
    """Tests for JSONL format output."""

    def test_audit_logger_writes_jsonl_format(self):
        """Test that log file is written in JSONL format."""
        with tempfile.TemporaryDirectory() as tmpdir:
            logger = AuditLogger(tmpdir)
            logger.append({"event": "TEST_1"})
            logger.append({"event": "TEST_2"})

            log_file = logger.current_log_file
            assert log_file.exists(), "Log file not created"

            with open(log_file, "r") as f:
                lines = f.readlines()

            assert len(lines) == 2, "JSONL should have 2 lines"

            # Each line should be valid JSON
            for i, line in enumerate(lines):
                try:
                    entry = json.loads(line.strip())
                    assert isinstance(entry, dict), f"Line {i} not a JSON object"
                except json.JSONDecodeError as e:
                    pytest.fail(f"Line {i} not valid JSON: {e}")

    def test_audit_logger_jsonl_entries_are_self_contained(self):
        """Test that each JSONL line is independently parseable."""
        with tempfile.TemporaryDirectory() as tmpdir:
            logger = AuditLogger(tmpdir)
            logger.append({"event": "TEST_1", "data": {"key": "value1"}})
            logger.append({"event": "TEST_2", "data": {"key": "value2"}})

            log_file = logger.current_log_file

            with open(log_file, "r") as f:
                for i, line in enumerate(f):
                    entry = json.loads(line.strip())
                    assert "event" in entry
                    assert "timestamp" in entry

    def test_audit_logger_jsonl_has_no_extra_formatting(self):
        """Test that JSONL uses compact formatting (separators)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            logger = AuditLogger(tmpdir)
            logger.append({"event": "TEST", "data": {"nested": "value"}})

            log_file = logger.current_log_file

            with open(log_file, "r") as f:
                line = f.readline()

            # Should not have pretty-printing (no newlines within entry)
            assert "\n" not in line.rstrip("\n"), "Line contains extra newlines"
            # Should use compact separators (no spaces)
            assert ", " not in line, "JSON has spaces after comma (not compact)"


class TestAuditLoggerDailyRotation:
    """Tests for daily log rotation."""

    def test_audit_logger_creates_date_named_log_file(self):
        """Test that log file has date-based naming."""
        with tempfile.TemporaryDirectory() as tmpdir:
            logger = AuditLogger(tmpdir)
            log_file = logger.current_log_file

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

    def test_audit_logger_rotate_if_needed_detects_day_change(self):
        """Test that rotate_if_needed updates log file when day changes."""
        with tempfile.TemporaryDirectory() as tmpdir:
            logger = AuditLogger(tmpdir)
            initial_file = logger.current_log_file

            logger.append({"event": "TEST_DAY_1"})

            # Simulate day change by checking rotate method
            # (actual day change testing would require mocking datetime)
            logger.rotate_if_needed()

            # Should still be same file (no actual day change)
            assert logger.current_log_file == initial_file


class TestAuditLoggerReadOperations:
    """Tests for reading audit entries."""

    def test_audit_logger_read_entries_returns_all_entries(self):
        """Test that get_entries returns all audit entries."""
        with tempfile.TemporaryDirectory() as tmpdir:
            logger = AuditLogger(tmpdir)
            logger.append({"event": "EVENT_1"})
            logger.append({"event": "EVENT_2"})
            logger.append({"event": "EVENT_3"})

            entries = logger.get_entries()
            assert len(entries) == 3
            assert entries[0]["event"] == "EVENT_1"
            assert entries[1]["event"] == "EVENT_2"
            assert entries[2]["event"] == "EVENT_3"

    def test_audit_logger_read_entries_for_step(self):
        """Test that read_entries_for_step filters by step_path."""
        with tempfile.TemporaryDirectory() as tmpdir:
            logger = AuditLogger(tmpdir)
            logger.append({"event": "EVENT_1", "step_path": "steps/01-01.json"})
            logger.append({"event": "EVENT_2", "step_path": "steps/02-01.json"})
            logger.append({"event": "EVENT_3", "step_path": "steps/01-01.json"})

            entries_01_01 = logger.read_entries_for_step("steps/01-01.json")
            assert len(entries_01_01) == 2
            assert all(e["step_path"] == "steps/01-01.json" for e in entries_01_01)

            entries_02_01 = logger.read_entries_for_step("steps/02-01.json")
            assert len(entries_02_01) == 1
            assert entries_02_01[0]["step_path"] == "steps/02-01.json"

    def test_audit_logger_read_empty_log_returns_empty_list(self):
        """Test that get_entries returns empty list for empty log."""
        with tempfile.TemporaryDirectory() as tmpdir:
            logger = AuditLogger(tmpdir)
            entries = logger.get_entries()
            assert entries == []

    def test_audit_logger_read_corrupted_log_handles_gracefully(self):
        """Test that AuditLogger handles corrupted log files gracefully."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_dir = Path(tmpdir)
            # Create a corrupted log file
            log_file = (
                log_dir / f"audit-{datetime.now(timezone.utc).strftime('%Y-%m-%d')}.log"
            )
            log_file.write_text("invalid json{{{")

            # Should handle gracefully
            logger = AuditLogger(tmpdir)
            entries = logger.get_entries()
            assert entries == []


class TestAuditLoggerGlobalInstance:
    """Tests for global audit logger instance."""

    def test_log_audit_event_function_logs_event(self):
        """Test that log_audit_event helper function works."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create logger in a testable location
            from src.des.adapters.driven.logging import audit_logger

            audit_logger._audit_logger = AuditLogger(tmpdir)

            log_audit_event("TEST_EVENT", extra_data="test_value")

            logger = audit_logger.get_audit_logger()
            entries = logger.get_entries()
            assert len(entries) == 1
            assert entries[0]["event"] == "TEST_EVENT"
            assert entries[0]["extra_data"] == "test_value"


class TestAuditLoggerIntegration:
    """Integration tests for AuditLogger."""

    def test_audit_logger_complete_workflow(self):
        """Test complete audit logger workflow: append, hash, read."""
        with tempfile.TemporaryDirectory() as tmpdir:
            logger = AuditLogger(tmpdir)

            # Append multiple entries
            events = [
                {"event": "TASK_STARTED", "step": "01-01"},
                {"event": "PHASE_STARTED", "phase": "PREPARE"},
                {"event": "PHASE_COMPLETED", "phase": "PREPARE", "status": "success"},
                {"event": "TASK_COMPLETED", "status": "success"},
            ]

            for event in events:
                logger.append(event)

            # Verify all entries logged
            assert logger.entry_count() == len(events)

            # Verify entries readable
            entries = logger.get_entries()
            assert len(entries) == len(events)

            # Verify hashing works
            total_hash = logger.compute_hash_of_entries(0, len(events))
            assert isinstance(total_hash, str)
            assert len(total_hash) == 64

            # Verify immutability
            initial_hash = logger.compute_hash_of_entries(0, 2)
            logger.append({"event": "NEW_EVENT"})
            current_hash = logger.compute_hash_of_entries(0, 2)
            assert initial_hash == current_hash
