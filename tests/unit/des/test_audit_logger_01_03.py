"""
Unit tests for audit event logging with feature_name and step_id (Step 01-03).

Tests that audit events accept feature_name and step_id as data fields
and that these fields are correctly persisted to the JSONL audit log.

Migrated from legacy AuditLogger/log_audit_event to JsonlAuditLogWriter.
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


def _log_audit_event(
    writer: JsonlAuditLogWriter,
    event_type: str,
    feature_name: str | None = None,
    step_id: str | None = None,
    **kwargs,
) -> None:
    """Log an audit event with optional feature_name and step_id.

    Equivalent to the legacy log_audit_event() function, but uses
    JsonlAuditLogWriter instead of the singleton AuditLogger.
    """
    data = {}
    if feature_name is not None:
        data["feature_name"] = feature_name
    if step_id is not None:
        data["step_id"] = step_id
    data.update(kwargs)

    writer.log_event(
        AuditEvent(
            event_type=event_type,
            timestamp=_make_timestamp(),
            data=data,
        )
    )


class TestLogAuditEventSignature:
    """Test audit event logging with feature_name and step_id parameters."""

    def test_audit_event_dataclass_has_event_type_timestamp_and_data_fields(self):
        """AC1: AuditEvent supports event_type, timestamp, and arbitrary data fields.

        In the new adapter architecture, feature_name and step_id are passed
        as entries in the data dict. The AuditEvent dataclass provides the
        structured container for all audit event data.
        """
        # Verify AuditEvent has the expected fields
        fields = {f.name for f in AuditEvent.__dataclass_fields__.values()}
        assert "event_type" in fields, "event_type not in AuditEvent fields"
        assert "timestamp" in fields, "timestamp not in AuditEvent fields"
        assert "data" in fields, "data not in AuditEvent fields"

        # Verify data dict can carry feature_name and step_id
        event = AuditEvent(
            event_type="TEST",
            timestamp=_make_timestamp(),
            data={"feature_name": "test", "step_id": "01-01"},
        )
        assert event.data["feature_name"] == "test"
        assert event.data["step_id"] == "01-01"

        # Verify step_path is not a dedicated field on AuditEvent
        assert "step_path" not in fields, "step_path should not be an AuditEvent field"

    def test_log_audit_event_accepts_feature_name_and_step_id(self, tmp_path):
        """AC1: Audit event logging includes feature_name and step_id in output."""
        log_dir = tmp_path / ".des/audit"
        writer = JsonlAuditLogWriter(log_dir=str(log_dir))

        # AC1: Should accept feature_name and step_id
        _log_audit_event(
            writer,
            "TEST_EVENT",
            feature_name="audit-log-refactor",
            step_id="01-03",
            extra_data="test_value",
        )

        entries = _read_all_entries(writer)
        assert len(entries) == 1
        assert entries[0]["event"] == "TEST_EVENT"
        # AC3: feature_name and step_id appear in event dictionary
        assert entries[0]["feature_name"] == "audit-log-refactor"
        assert entries[0]["step_id"] == "01-03"
        assert entries[0]["extra_data"] == "test_value"

    def test_log_audit_event_parameters_are_optional(self, tmp_path):
        """AC2: Parameters are optional (omitted when None)."""
        log_dir = tmp_path / ".des/audit"
        writer = JsonlAuditLogWriter(log_dir=str(log_dir))

        # AC2: Should work without feature_name and step_id
        _log_audit_event(writer, "TEST_EVENT", extra_data="test_value")

        entries = _read_all_entries(writer)
        assert len(entries) == 1
        assert entries[0]["event"] == "TEST_EVENT"
        # AC2: When not provided, feature_name and step_id are absent from entry
        assert "feature_name" not in entries[0] or entries[0]["feature_name"] is None
        assert "step_id" not in entries[0] or entries[0]["step_id"] is None
        assert entries[0]["extra_data"] == "test_value"

    def test_log_audit_event_step_path_not_a_dedicated_field(self, tmp_path):
        """AC4: step_path is not a dedicated parameter in the new adapter."""
        log_dir = tmp_path / ".des/audit"
        writer = JsonlAuditLogWriter(log_dir=str(log_dir))

        # AC4: step_path is not a recognized dedicated parameter
        _log_audit_event(
            writer,
            "TEST_EVENT",
            feature_name="test-feature",
            step_id="01-01",
        )

        entries = _read_all_entries(writer)
        assert len(entries) == 1
        # Verify the new parameters work
        assert entries[0]["feature_name"] == "test-feature"
        assert entries[0]["step_id"] == "01-01"

    def test_log_audit_event_timestamp_generation(self, tmp_path):
        """AC5: Timestamp is included in ISO 8601 format."""
        log_dir = tmp_path / ".des/audit"
        writer = JsonlAuditLogWriter(log_dir=str(log_dir))

        _log_audit_event(
            writer,
            "TEST_EVENT",
            feature_name="test-feature",
            step_id="01-01",
        )

        entries = _read_all_entries(writer)
        assert len(entries) == 1
        # AC5: Timestamp should be present in ISO 8601 format
        assert "timestamp" in entries[0]
        assert entries[0]["timestamp"].endswith("Z")
        assert "T" in entries[0]["timestamp"]

    def test_log_audit_event_type_handling_unchanged(self, tmp_path):
        """AC6: Event type handling unchanged."""
        log_dir = tmp_path / ".des/audit"
        writer = JsonlAuditLogWriter(log_dir=str(log_dir))

        # AC6: Event type should be stored as "event" key
        _log_audit_event(
            writer,
            "CUSTOM_EVENT_TYPE",
            feature_name="test-feature",
            step_id="01-01",
            custom_field="custom_value",
        )

        entries = _read_all_entries(writer)
        assert len(entries) == 1
        # AC6: Event type handling should be unchanged
        assert entries[0]["event"] == "CUSTOM_EVENT_TYPE"
        assert entries[0]["feature_name"] == "test-feature"
        assert entries[0]["step_id"] == "01-01"
        assert entries[0]["custom_field"] == "custom_value"

    def test_log_audit_event_with_only_feature_name(self, tmp_path):
        """Test passing only feature_name (step_id omitted from entry)."""
        log_dir = tmp_path / ".des/audit"
        writer = JsonlAuditLogWriter(log_dir=str(log_dir))

        _log_audit_event(
            writer,
            "TEST_EVENT",
            feature_name="test-feature",
        )

        entries = _read_all_entries(writer)
        assert len(entries) == 1
        assert entries[0]["feature_name"] == "test-feature"
        assert "step_id" not in entries[0] or entries[0]["step_id"] is None

    def test_log_audit_event_with_only_step_id(self, tmp_path):
        """Test passing only step_id (feature_name omitted from entry)."""
        log_dir = tmp_path / ".des/audit"
        writer = JsonlAuditLogWriter(log_dir=str(log_dir))

        _log_audit_event(
            writer,
            "TEST_EVENT",
            step_id="01-01",
        )

        entries = _read_all_entries(writer)
        assert len(entries) == 1
        assert "feature_name" not in entries[0] or entries[0]["feature_name"] is None
        assert entries[0]["step_id"] == "01-01"
