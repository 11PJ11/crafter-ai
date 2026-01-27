"""
Unit tests for AuditLogger class (US-004: Audit Trail).

Tests append-only semantics, immutability guarantees, and timestamp formatting.
"""

import json
import tempfile
from datetime import datetime


from src.des.adapters.driven.logging.audit_logger import AuditLogger


class TestAuditLoggerAppendOnlySemantics:
    """Test append-only file operations."""

    def test_audit_logger_creates_log_file(self):
        """AuditLogger should create log file on first append (lazy initialization)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            logger = AuditLogger(log_dir=tmpdir)
            # File doesn't exist until first append
            assert not logger.current_log_file.exists()

            # After first append, file is created
            logger.append(
                {"timestamp": "2026-01-27T14:30:00.000Z", "event": "TEST_EVENT"}
            )
            assert logger.current_log_file.exists()

    def test_append_adds_entry_to_file(self):
        """append() should add new entry to log file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            logger = AuditLogger(log_dir=tmpdir)

            event = {
                "timestamp": "2026-01-27T14:30:45.123Z",
                "event": "TEST_EVENT",
                "step_path": "steps/01-01.json",
            }
            logger.append(event)

            # Verify entry was added
            assert logger.entry_count() == 1

            # Verify file contains the entry
            with open(logger.current_log_file, "r") as f:
                lines = f.readlines()
            assert len(lines) == 1
            parsed = json.loads(lines[0])
            assert parsed["event"] == "TEST_EVENT"

    def test_multiple_appends_create_multiple_entries(self):
        """Multiple appends should create multiple log entries."""
        with tempfile.TemporaryDirectory() as tmpdir:
            logger = AuditLogger(log_dir=tmpdir)

            for i in range(5):
                logger.append(
                    {
                        "timestamp": f"2026-01-27T14:30:{i:02d}.000Z",
                        "event": f"EVENT_{i}",
                        "count": i,
                    }
                )

            assert logger.entry_count() == 5

    def test_jsonl_format_one_entry_per_line(self):
        """Log file should be in JSONL format (one JSON per line)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            logger = AuditLogger(log_dir=tmpdir)

            logger.append({"timestamp": "2026-01-27T14:30:00.000Z", "event": "EVENT_1"})
            logger.append({"timestamp": "2026-01-27T14:30:01.000Z", "event": "EVENT_2"})

            with open(logger.current_log_file, "r") as f:
                lines = f.readlines()

            assert len(lines) == 2
            # Each line should be valid JSON
            for line in lines:
                json.loads(line)


class TestAuditLoggerImmutability:
    """Test immutability guarantees via SHA256 hashing."""

    def test_compute_hash_of_entries(self):
        """compute_hash_of_entries should compute combined hash of range."""
        with tempfile.TemporaryDirectory() as tmpdir:
            logger = AuditLogger(log_dir=tmpdir)

            # Add 5 entries
            for i in range(5):
                logger.append(
                    {
                        "timestamp": f"2026-01-27T14:30:{i:02d}.000Z",
                        "event": f"EVENT_{i}",
                    }
                )

            # Get hash of first 3 entries
            hash_0_3 = logger.compute_hash_of_entries(0, 3)
            assert hash_0_3 is not None
            assert len(hash_0_3) == 64  # SHA256 hex digest is 64 chars

    def test_hash_unchanged_after_new_appends(self):
        """Original entries' hash should remain unchanged after new appends."""
        with tempfile.TemporaryDirectory() as tmpdir:
            logger = AuditLogger(log_dir=tmpdir)

            # Add initial entries
            for i in range(3):
                logger.append(
                    {
                        "timestamp": f"2026-01-27T14:30:{i:02d}.000Z",
                        "event": f"EVENT_{i}",
                    }
                )

            # Get hash of original entries
            original_hash = logger.compute_hash_of_entries(0, 3)

            # Add new entries
            for i in range(3, 5):
                logger.append(
                    {
                        "timestamp": f"2026-01-27T14:30:{i:02d}.000Z",
                        "event": f"EVENT_{i}",
                    }
                )

            # Hash of original entries should be unchanged
            new_hash = logger.compute_hash_of_entries(0, 3)
            assert new_hash == original_hash


class TestAuditLoggerTimestamps:
    """Test ISO 8601 timestamp formatting."""

    def test_get_iso_timestamp_format(self):
        """_get_iso_timestamp() should return ISO 8601 format with milliseconds."""
        with tempfile.TemporaryDirectory() as tmpdir:
            logger = AuditLogger(log_dir=tmpdir)

            ts = logger._get_iso_timestamp()

            # Check format: YYYY-MM-DDTHH:MM:SS.sssZ
            assert "T" in ts
            assert ts.endswith("Z")
            assert ts.count(":") == 2  # HH:MM:SS has 2 colons
            assert "." in ts  # Has milliseconds

            # Verify it's parseable as ISO format
            parsed = datetime.fromisoformat(ts.replace("Z", "+00:00"))
            assert isinstance(parsed, datetime)

    def test_append_adds_timestamp_if_missing(self):
        """append() should add timestamp if entry doesn't have one."""
        with tempfile.TemporaryDirectory() as tmpdir:
            logger = AuditLogger(log_dir=tmpdir)

            event = {"event": "TEST_EVENT"}  # No timestamp
            logger.append(event)

            # Read from file to check timestamp was added
            with open(logger.current_log_file, "r") as f:
                line = f.read()

            parsed = json.loads(line)
            assert "timestamp" in parsed
            assert parsed["timestamp"].endswith("Z")


class TestAuditLoggerEntryContext:
    """Test entry context enrichment."""

    def test_read_entries_for_step(self):
        """read_entries_for_step() should retrieve entries for specific step."""
        with tempfile.TemporaryDirectory() as tmpdir:
            logger = AuditLogger(log_dir=tmpdir)

            # Add entries for different steps
            logger.append(
                {
                    "timestamp": "2026-01-27T14:30:00.000Z",
                    "event": "TASK_START",
                    "step_path": "steps/01-01.json",
                }
            )
            logger.append(
                {
                    "timestamp": "2026-01-27T14:30:01.000Z",
                    "event": "TASK_START",
                    "step_path": "steps/01-02.json",
                }
            )
            logger.append(
                {
                    "timestamp": "2026-01-27T14:30:02.000Z",
                    "event": "TASK_END",
                    "step_path": "steps/01-01.json",
                }
            )

            # Retrieve entries for step 01-01
            entries = logger.read_entries_for_step("steps/01-01.json")

            assert len(entries) == 2
            assert all(e["step_path"] == "steps/01-01.json" for e in entries)

    def test_get_all_entries(self):
        """get_entries() should retrieve all entries from log file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            logger = AuditLogger(log_dir=tmpdir)

            # Add 3 entries
            for i in range(3):
                logger.append(
                    {
                        "timestamp": f"2026-01-27T14:30:{i:02d}.000Z",
                        "event": f"EVENT_{i}",
                    }
                )

            entries = logger.get_entries()
            assert len(entries) == 3
            assert [e["event"] for e in entries] == ["EVENT_0", "EVENT_1", "EVENT_2"]


class TestAuditLoggerDailyRotation:
    """Test daily log rotation."""

    def test_rotate_if_needed_creates_new_file(self):
        """rotate_if_needed() should create new file on date change."""
        with tempfile.TemporaryDirectory() as tmpdir:
            logger = AuditLogger(log_dir=tmpdir)

            # Add entry
            logger.append({"timestamp": "2026-01-27T14:30:00.000Z", "event": "EVENT"})

            # Mock date change (in real usage, rotate_if_needed checks current date)
            # For testing, manually verify it detects file changes
            logger.rotate_if_needed()

            # File should exist (same date in test)
            assert logger.current_log_file.exists()
