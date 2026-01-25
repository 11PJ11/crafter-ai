"""Unit tests for DESOrchestrator.request_extension() method."""

from des.orchestrator import DESOrchestrator
from datetime import datetime, timezone
import json


class TestRequestExtensionMethodExists:
    """Test that request_extension method exists with correct signature."""

    def test_request_extension_method_exists(self):
        """DESOrchestrator should have request_extension method."""
        orchestrator = DESOrchestrator()
        assert hasattr(orchestrator, "request_extension")
        assert callable(getattr(orchestrator, "request_extension"))

    def test_request_extension_accepts_required_parameters(self):
        """request_extension should accept reason, additional_turns, additional_minutes."""
        import inspect

        orchestrator = DESOrchestrator()

        sig = inspect.signature(orchestrator.request_extension)
        params = list(sig.parameters.keys())

        assert "reason" in params
        assert "additional_turns" in params
        assert "additional_minutes" in params


class TestRequestExtensionInvokesApprovalEngine:
    """Test that request_extension invokes ExtensionApprovalEngine."""

    def test_request_extension_creates_extension_request(self, tmp_path):
        """request_extension should create ExtensionRequest from parameters."""
        # GIVEN: Orchestrator with step file
        orchestrator = DESOrchestrator()
        step_file = tmp_path / "test_step.json"
        step_data = {
            "tdd_cycle": {
                "phase_execution_log": [
                    {
                        "phase_name": "PREPARE",
                        "status": "IN_PROGRESS",
                        "turn_count": 0,
                        "max_turns": 10,
                        "timeout_minutes": 15,
                        "extensions_granted": [],
                    }
                ]
            }
        }
        step_file.write_text(json.dumps(step_data))

        # Set step file context
        orchestrator._step_file_path = step_file

        # WHEN: request_extension called
        result = orchestrator.request_extension(
            reason="Need more time", additional_turns=5, additional_minutes=10
        )

        # THEN: Returns ApprovalResult
        assert hasattr(result, "approved")
        assert hasattr(result, "reason")

    def test_request_extension_calls_approval_engine_evaluate(self, tmp_path):
        """request_extension should invoke approval engine's evaluate method."""
        # GIVEN: Orchestrator with step file
        orchestrator = DESOrchestrator()
        step_file = tmp_path / "test_step.json"
        step_data = {
            "tdd_cycle": {
                "phase_execution_log": [
                    {
                        "phase_name": "PREPARE",
                        "status": "IN_PROGRESS",
                        "turn_count": 0,
                        "started_at": datetime.now(timezone.utc).isoformat(),
                        "max_turns": 10,
                        "timeout_minutes": 15,
                        "extensions_granted": [],
                    }
                ]
            }
        }
        step_file.write_text(json.dumps(step_data))
        orchestrator._step_file_path = step_file

        # WHEN: request_extension called with valid reason
        result = orchestrator.request_extension(
            reason="Valid reason exceeding 20 characters minimum",
            additional_turns=3,
            additional_minutes=None,
        )

        # THEN: Approval engine evaluates and approves
        assert result.approved is True


class TestRequestExtensionUpdatesLimits:
    """Test that approved extensions update TurnCounter and TimeoutMonitor."""

    def test_approved_turn_extension_updates_max_turns(self, tmp_path):
        """Approved turn extension should increase max_turns in step file."""
        # GIVEN: Orchestrator with step file (10 turn limit)
        orchestrator = DESOrchestrator()
        step_file = tmp_path / "test_step.json"
        step_data = {
            "tdd_cycle": {
                "phase_execution_log": [
                    {
                        "phase_name": "PREPARE",
                        "status": "IN_PROGRESS",
                        "turn_count": 5,
                        "max_turns": 10,
                        "timeout_minutes": 15,
                        "extensions_granted": [],
                    }
                ]
            }
        }
        step_file.write_text(json.dumps(step_data))
        orchestrator._step_file_path = step_file

        # WHEN: Approved extension requests 5 additional turns
        orchestrator.request_extension(
            reason="Need more turns for testing",
            additional_turns=5,
            additional_minutes=None,
        )

        # THEN: max_turns updated to 15 (10 + 5)
        updated_data = json.loads(step_file.read_text())
        phase = updated_data["tdd_cycle"]["phase_execution_log"][0]
        assert phase["max_turns"] == 15

    def test_approved_time_extension_updates_timeout_minutes(self, tmp_path):
        """Approved time extension should increase timeout_minutes in step file."""
        # GIVEN: Orchestrator with step file (15 minute timeout)
        orchestrator = DESOrchestrator()
        step_file = tmp_path / "test_step.json"
        step_data = {
            "tdd_cycle": {
                "phase_execution_log": [
                    {
                        "phase_name": "PREPARE",
                        "status": "IN_PROGRESS",
                        "turn_count": 0,
                        "started_at": datetime.now(timezone.utc).isoformat(),
                        "max_turns": 10,
                        "timeout_minutes": 15,
                        "extensions_granted": [],
                    }
                ]
            }
        }
        step_file.write_text(json.dumps(step_data))
        orchestrator._step_file_path = step_file

        # WHEN: Approved extension requests 10 additional minutes
        orchestrator.request_extension(
            reason="Need more time for complex refactoring",
            additional_turns=None,
            additional_minutes=10,
        )

        # THEN: timeout_minutes updated to 25 (15 + 10)
        updated_data = json.loads(step_file.read_text())
        phase = updated_data["tdd_cycle"]["phase_execution_log"][0]
        assert phase["timeout_minutes"] == 25


class TestRequestExtensionPersistsRecord:
    """Test that extension records are persisted to step file."""

    def test_approved_extension_added_to_extensions_granted_list(self, tmp_path):
        """Approved extension should be added to extensions_granted array."""
        # GIVEN: Orchestrator with step file
        orchestrator = DESOrchestrator()
        step_file = tmp_path / "test_step.json"
        step_data = {
            "tdd_cycle": {
                "phase_execution_log": [
                    {
                        "phase_name": "PREPARE",
                        "status": "IN_PROGRESS",
                        "turn_count": 0,
                        "max_turns": 10,
                        "timeout_minutes": 15,
                        "extensions_granted": [],
                    }
                ]
            }
        }
        step_file.write_text(json.dumps(step_data))
        orchestrator._step_file_path = step_file

        # WHEN: Extension approved
        orchestrator.request_extension(
            reason="Valid extension reason", additional_turns=3, additional_minutes=5
        )

        # THEN: Extension record persisted
        updated_data = json.loads(step_file.read_text())
        extensions = updated_data["tdd_cycle"]["phase_execution_log"][0][
            "extensions_granted"
        ]

        assert len(extensions) == 1
        assert extensions[0]["additional_turns"] == 3
        assert extensions[0]["additional_minutes"] == 5
        assert "Valid extension reason" in extensions[0]["reason"]

    def test_extension_record_includes_timestamp(self, tmp_path):
        """Extension record should include granted_at timestamp."""
        # GIVEN: Orchestrator with step file
        orchestrator = DESOrchestrator()
        step_file = tmp_path / "test_step.json"
        step_data = {
            "tdd_cycle": {
                "phase_execution_log": [
                    {
                        "phase_name": "PREPARE",
                        "status": "IN_PROGRESS",
                        "turn_count": 0,
                        "max_turns": 10,
                        "timeout_minutes": 15,
                        "extensions_granted": [],
                    }
                ]
            }
        }
        step_file.write_text(json.dumps(step_data))
        orchestrator._step_file_path = step_file

        # WHEN: Extension granted
        orchestrator.request_extension(
            reason="Time-tracked extension", additional_turns=2, additional_minutes=None
        )

        # THEN: Record has timestamp
        updated_data = json.loads(step_file.read_text())
        extension = updated_data["tdd_cycle"]["phase_execution_log"][0][
            "extensions_granted"
        ][0]

        assert "granted_at" in extension
        # Validate ISO 8601 format
        datetime.fromisoformat(extension["granted_at"].replace("Z", "+00:00"))
