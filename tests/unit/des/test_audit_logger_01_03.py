"""
Unit tests for log_audit_event() helper function (Step 01-03).

Tests that log_audit_event() accepts feature_name and step_id parameters
and passes them to the event dictionary correctly.
"""

import inspect
import tempfile

from src.des.adapters.driven.logging.audit_logger import (
    AuditLogger,
    log_audit_event,
    reset_audit_logger,
)


class TestLogAuditEventSignature:
    """Test log_audit_event() signature with feature_name and step_id parameters."""

    def test_log_audit_event_has_explicit_feature_name_and_step_id_parameters(self):
        """AC1: Function signature includes feature_name and step_id as explicit parameters."""
        # Use inspect to verify the signature has explicit parameters
        sig = inspect.signature(log_audit_event)
        params = sig.parameters

        # AC1: feature_name and step_id should be explicit parameters (not just **kwargs)
        assert "feature_name" in params, "feature_name not in signature"
        assert "step_id" in params, "step_id not in signature"

        # AC2: Parameters should be optional (have default values)
        assert params["feature_name"].default is None, (
            "feature_name should default to None"
        )
        assert params["step_id"].default is None, "step_id should default to None"

        # AC4: step_path parameter should be removed
        assert "step_path" not in params, "step_path should be removed from signature"

    def test_log_audit_event_accepts_feature_name_and_step_id(self):
        """AC1: Function signature includes feature_name and step_id parameters."""
        with tempfile.TemporaryDirectory() as tmpdir:
            from src.des.adapters.driven.logging import audit_logger

            audit_logger._audit_logger = AuditLogger(tmpdir)

            # AC1: Should accept feature_name and step_id as keyword arguments
            log_audit_event(
                "TEST_EVENT",
                feature_name="audit-log-refactor",
                step_id="01-03",
                extra_data="test_value",
            )

            logger = audit_logger.get_audit_logger()
            entries = logger.get_entries()
            assert len(entries) == 1
            assert entries[0]["event"] == "TEST_EVENT"
            # AC3: Function passes feature_name and step_id to event dictionary
            assert entries[0]["feature_name"] == "audit-log-refactor"
            assert entries[0]["step_id"] == "01-03"
            assert entries[0]["extra_data"] == "test_value"

            # Cleanup
            reset_audit_logger()

    def test_log_audit_event_parameters_are_optional(self):
        """AC2: Parameters are optional (default to None)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            from src.des.adapters.driven.logging import audit_logger

            audit_logger._audit_logger = AuditLogger(tmpdir)

            # AC2: Should work without feature_name and step_id
            log_audit_event("TEST_EVENT", extra_data="test_value")

            logger = audit_logger.get_audit_logger()
            entries = logger.get_entries()
            assert len(entries) == 1
            assert entries[0]["event"] == "TEST_EVENT"
            # AC2: When not provided, feature_name and step_id default to None
            assert (
                "feature_name" not in entries[0] or entries[0]["feature_name"] is None
            )
            assert "step_id" not in entries[0] or entries[0]["step_id"] is None
            assert entries[0]["extra_data"] == "test_value"

            # Cleanup
            reset_audit_logger()

    def test_log_audit_event_step_path_parameter_removed(self):
        """AC4: step_path parameter removed from function signature."""
        with tempfile.TemporaryDirectory() as tmpdir:
            from src.des.adapters.driven.logging import audit_logger

            audit_logger._audit_logger = AuditLogger(tmpdir)

            # AC4: step_path should not be a recognized parameter
            # (If it were, it would be passed to the event dict)
            # But since we removed it, passing it as a kwarg should just be treated as extra data
            log_audit_event(
                "TEST_EVENT",
                feature_name="test-feature",
                step_id="01-01",
            )

            logger = audit_logger.get_audit_logger()
            entries = logger.get_entries()
            assert len(entries) == 1
            # Verify the new parameters work
            assert entries[0]["feature_name"] == "test-feature"
            assert entries[0]["step_id"] == "01-01"
            # Verify step_path is not in the signature (not automatically added)
            # (it could still be passed as **kwargs but not as a specific parameter)

            # Cleanup
            reset_audit_logger()

    def test_log_audit_event_timestamp_generation_unchanged(self):
        """AC5: Timestamp generation unchanged."""
        with tempfile.TemporaryDirectory() as tmpdir:
            from src.des.adapters.driven.logging import audit_logger

            audit_logger._audit_logger = AuditLogger(tmpdir)

            log_audit_event(
                "TEST_EVENT",
                feature_name="test-feature",
                step_id="01-01",
            )

            logger = audit_logger.get_audit_logger()
            entries = logger.get_entries()
            assert len(entries) == 1
            # AC5: Timestamp should still be automatically generated
            assert "timestamp" in entries[0]
            assert entries[0]["timestamp"].endswith("Z")
            assert "T" in entries[0]["timestamp"]

            # Cleanup
            reset_audit_logger()

    def test_log_audit_event_type_handling_unchanged(self):
        """AC6: Event type handling unchanged."""
        with tempfile.TemporaryDirectory() as tmpdir:
            from src.des.adapters.driven.logging import audit_logger

            audit_logger._audit_logger = AuditLogger(tmpdir)

            # AC6: Event type should still be passed as first positional argument
            log_audit_event(
                "CUSTOM_EVENT_TYPE",
                feature_name="test-feature",
                step_id="01-01",
                custom_field="custom_value",
            )

            logger = audit_logger.get_audit_logger()
            entries = logger.get_entries()
            assert len(entries) == 1
            # AC6: Event type handling should be unchanged
            assert entries[0]["event"] == "CUSTOM_EVENT_TYPE"
            assert entries[0]["feature_name"] == "test-feature"
            assert entries[0]["step_id"] == "01-01"
            assert entries[0]["custom_field"] == "custom_value"

            # Cleanup
            reset_audit_logger()

    def test_log_audit_event_with_only_feature_name(self):
        """Test passing only feature_name (step_id defaults to None)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            from src.des.adapters.driven.logging import audit_logger

            audit_logger._audit_logger = AuditLogger(tmpdir)

            log_audit_event(
                "TEST_EVENT",
                feature_name="test-feature",
            )

            logger = audit_logger.get_audit_logger()
            entries = logger.get_entries()
            assert len(entries) == 1
            assert entries[0]["feature_name"] == "test-feature"
            assert "step_id" not in entries[0] or entries[0]["step_id"] is None

            # Cleanup
            reset_audit_logger()

    def test_log_audit_event_with_only_step_id(self):
        """Test passing only step_id (feature_name defaults to None)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            from src.des.adapters.driven.logging import audit_logger

            audit_logger._audit_logger = AuditLogger(tmpdir)

            log_audit_event(
                "TEST_EVENT",
                step_id="01-01",
            )

            logger = audit_logger.get_audit_logger()
            entries = logger.get_entries()
            assert len(entries) == 1
            assert (
                "feature_name" not in entries[0] or entries[0]["feature_name"] is None
            )
            assert entries[0]["step_id"] == "01-01"

            # Cleanup
            reset_audit_logger()
