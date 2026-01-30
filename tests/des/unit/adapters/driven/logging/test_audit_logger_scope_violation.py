"""Unit tests for AuditLogger SCOPE_VIOLATION event type support.

Tests the get_entries_by_type() method for filtering audit events
and SCOPE_VIOLATION event structure validation.
"""

from src.des.adapters.driven.logging.audit_logger import AuditLogger


class TestScopeViolationEventType:
    """Test SCOPE_VIOLATION event type support in AuditLogger."""

    def test_get_entries_by_type_filters_scope_violation_events(self, tmp_path):
        """
        GIVEN audit log with multiple event types
        WHEN get_entries_by_type('SCOPE_VIOLATION') is called
        THEN only SCOPE_VIOLATION events are returned

        Business Context:
        Priya needs to filter audit log to see only scope violations
        during PR review, ignoring other events like TASK_INVOCATION.
        """
        # Arrange: Create logger and log multiple event types
        log_dir = tmp_path / ".des/audit"
        audit_logger = AuditLogger(log_dir=str(log_dir))

        # Log different event types
        audit_logger.append({"event": "TASK_INVOCATION", "task": "01-01"})
        audit_logger.append(
            {
                "event": "SCOPE_VIOLATION",
                "severity": "WARNING",
                "step_file": "steps/01-01.json",
                "out_of_scope_file": "src/OrderService.py",
            }
        )
        audit_logger.append({"event": "COMMIT", "sha": "abc123"})
        audit_logger.append(
            {
                "event": "SCOPE_VIOLATION",
                "severity": "WARNING",
                "step_file": "steps/01-02.json",
                "out_of_scope_file": "src/PaymentService.py",
            }
        )

        # Act: Filter by SCOPE_VIOLATION
        scope_violations = audit_logger.get_entries_by_type("SCOPE_VIOLATION")

        # Assert: Only SCOPE_VIOLATION events returned
        assert len(scope_violations) == 2
        assert all(entry["event"] == "SCOPE_VIOLATION" for entry in scope_violations)
        assert scope_violations[0]["out_of_scope_file"] == "src/OrderService.py"
        assert scope_violations[1]["out_of_scope_file"] == "src/PaymentService.py"

    def test_scope_violation_event_has_required_fields(self, tmp_path):
        """
        GIVEN SCOPE_VIOLATION event logged
        WHEN event is retrieved from audit log
        THEN event contains all required fields per AC

        Required Fields (from implementation notes):
        - event_type (stored as 'event'): "SCOPE_VIOLATION"
        - severity: "WARNING"
        - step_file: path to step file
        - out_of_scope_file: path to file that violated scope
        - allowed_patterns: list of glob patterns
        - timestamp: ISO 8601 format (auto-added)
        """
        # Arrange: Create logger
        log_dir = tmp_path / ".des/audit"
        audit_logger = AuditLogger(log_dir=str(log_dir))

        # Act: Log SCOPE_VIOLATION with required fields
        audit_logger.append(
            {
                "event": "SCOPE_VIOLATION",
                "severity": "WARNING",
                "step_file": "steps/01-01.json",
                "out_of_scope_file": "src/services/OrderService.py",
                "allowed_patterns": ["**/UserRepository*", "**/test_user*"],
            }
        )

        entries = audit_logger.get_entries_by_type("SCOPE_VIOLATION")

        # Assert: Required fields present
        violation = entries[0]
        assert violation["event"] == "SCOPE_VIOLATION"
        assert violation["severity"] == "WARNING"
        assert violation["step_file"] == "steps/01-01.json"
        assert violation["out_of_scope_file"] == "src/services/OrderService.py"
        assert violation["allowed_patterns"] == [
            "**/UserRepository*",
            "**/test_user*",
        ]
        assert "timestamp" in violation
        assert violation["timestamp"].endswith("Z")  # ISO 8601 UTC format

    def test_severity_is_warning_not_error(self, tmp_path):
        """
        GIVEN SCOPE_VIOLATION event
        WHEN severity is checked
        THEN severity is WARNING (not ERROR)

        Business Context:
        Scope violations are warnings because the work may be valid
        but just misplaced. Priya decides whether to accept or reject
        during PR review. ERROR would block the workflow inappropriately.
        """
        # Arrange: Create logger
        log_dir = tmp_path / ".des/audit"
        audit_logger = AuditLogger(log_dir=str(log_dir))

        # Act: Log SCOPE_VIOLATION
        audit_logger.append(
            {
                "event": "SCOPE_VIOLATION",
                "severity": "WARNING",
                "step_file": "steps/01-01.json",
                "out_of_scope_file": "config/database.yml",
                "allowed_patterns": ["**/UserRepository*"],
            }
        )

        entries = audit_logger.get_entries_by_type("SCOPE_VIOLATION")

        # Assert: Severity is WARNING
        assert entries[0]["severity"] == "WARNING"
        assert entries[0]["severity"] != "ERROR"

    def test_get_entries_by_type_returns_empty_list_when_no_matches(self, tmp_path):
        """
        GIVEN audit log with no SCOPE_VIOLATION events
        WHEN get_entries_by_type('SCOPE_VIOLATION') is called
        THEN empty list is returned

        Business Context:
        If agent stayed within scope, no violations logged.
        Priya sees empty list, confirming clean PR.
        """
        # Arrange: Create logger and log other events
        log_dir = tmp_path / ".des/audit"
        audit_logger = AuditLogger(log_dir=str(log_dir))

        audit_logger.append({"event": "TASK_INVOCATION", "task": "01-01"})
        audit_logger.append({"event": "COMMIT", "sha": "abc123"})

        # Act: Filter by SCOPE_VIOLATION
        scope_violations = audit_logger.get_entries_by_type("SCOPE_VIOLATION")

        # Assert: Empty list
        assert scope_violations == []
        assert len(scope_violations) == 0
