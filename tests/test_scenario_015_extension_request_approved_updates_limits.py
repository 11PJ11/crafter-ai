"""
Acceptance test for scenario 015: Extension request approved updates limits.

This test validates that when an extension request is approved, it properly
updates the turn and timeout limits in the step file and these updated limits
are enforced during subsequent execution.
"""

from datetime import datetime, timezone, timedelta
from pathlib import Path
import json
import tempfile
from des.orchestrator import DESOrchestrator


class TestScenario015ExtensionRequestApprovedUpdatesLimits:
    """
    Test that approved extension requests update turn and timeout limits.

    Acceptance Criteria (from roadmap step 06-01):
    - DESOrchestrator.request_extension(reason, additional_turns, additional_minutes) method exists
    - Method invokes ExtensionApprovalEngine for decision
    - Approved extensions update TurnCounter and TimeoutMonitor limits
    - Extension record persisted to step file extensions_granted list
    - Extension API CALLABLE when /nw:execute or /nw:develop invoked
    """

    def test_approved_turn_extension_increases_max_turns_limit(self):
        """Approved turn extension should increase max_turns in step file."""
        # Given: DESOrchestrator with a step file containing turn limits
        orchestrator = DESOrchestrator()

        with tempfile.TemporaryDirectory() as tmpdir:
            step_file_path = Path(tmpdir) / "test_step.json"

            # Step file with 10 turn limit, currently at turn 8
            step_data = self._create_step_file_with_turn_config(
                current_turn=8, max_turns=10
            )

            with open(step_file_path, "w") as f:
                json.dump(step_data, f, indent=2)

            orchestrator._step_file_path = step_file_path

            # When: Agent requests extension for 5 additional turns
            result = orchestrator.request_extension(
                reason="Complex refactoring requires more iterations",
                additional_turns=5,
                additional_minutes=None,
            )

            # Then: Extension should be approved
            assert result.approved is True

            # And: max_turns should be updated to 15 (10 + 5)
            updated_data = json.loads(step_file_path.read_text())
            phase = updated_data["tdd_cycle"]["phase_execution_log"][0]
            assert phase["max_turns"] == 15

            # And: Current turn count should remain unchanged
            assert phase["turn_count"] == 8

    def test_approved_timeout_extension_increases_timeout_minutes(self):
        """Approved timeout extension should increase timeout_minutes in step file."""
        # Given: DESOrchestrator with a step file containing timeout limits
        orchestrator = DESOrchestrator()

        with tempfile.TemporaryDirectory() as tmpdir:
            step_file_path = Path(tmpdir) / "test_step.json"

            # Step file with 15 minute timeout, started 12 minutes ago
            started_at = (datetime.now(timezone.utc) - timedelta(minutes=12)).isoformat()
            step_data = self._create_step_file_with_timeout_config(
                started_at=started_at, timeout_minutes=15
            )

            with open(step_file_path, "w") as f:
                json.dump(step_data, f, indent=2)

            orchestrator._step_file_path = step_file_path

            # When: Agent requests extension for 10 additional minutes
            result = orchestrator.request_extension(
                reason="Database migrations taking longer than expected",
                additional_turns=None,
                additional_minutes=10,
            )

            # Then: Extension should be approved
            assert result.approved is True

            # And: timeout_minutes should be updated to 25 (15 + 10)
            updated_data = json.loads(step_file_path.read_text())
            phase = updated_data["tdd_cycle"]["phase_execution_log"][0]
            assert phase["timeout_minutes"] == 25

    def test_extension_record_persisted_to_extensions_granted_list(self):
        """Extension records should be persisted with all required fields."""
        # Given: DESOrchestrator with a step file
        orchestrator = DESOrchestrator()

        with tempfile.TemporaryDirectory() as tmpdir:
            step_file_path = Path(tmpdir) / "test_step.json"

            step_data = self._create_step_file_with_turn_config(
                current_turn=5, max_turns=10
            )

            with open(step_file_path, "w") as f:
                json.dump(step_data, f, indent=2)

            orchestrator._step_file_path = step_file_path

            # When: Extension request approved
            result = orchestrator.request_extension(
                reason="Need more time for comprehensive testing",
                additional_turns=8,
                additional_minutes=12,
            )

            # Then: Extension approved
            assert result.approved is True

            # And: Extension record added to extensions_granted list
            updated_data = json.loads(step_file_path.read_text())
            extensions = updated_data["tdd_cycle"]["phase_execution_log"][0][
                "extensions_granted"
            ]

            assert len(extensions) == 1
            extension = extensions[0]

            # And: Record contains all required fields
            assert extension["reason"] == "Need more time for comprehensive testing"
            assert extension["additional_turns"] == 8
            assert extension["additional_minutes"] == 12
            assert "granted_at" in extension

            # And: Timestamp is valid ISO 8601 format
            datetime.fromisoformat(extension["granted_at"].replace("Z", "+00:00"))

    def test_multiple_extensions_accumulate_in_history(self):
        """Multiple approved extensions should accumulate in extensions_granted list."""
        # Given: DESOrchestrator with a step file
        orchestrator = DESOrchestrator()

        with tempfile.TemporaryDirectory() as tmpdir:
            step_file_path = Path(tmpdir) / "test_step.json"

            step_data = self._create_step_file_with_turn_config(
                current_turn=5, max_turns=10
            )

            with open(step_file_path, "w") as f:
                json.dump(step_data, f, indent=2)

            orchestrator._step_file_path = step_file_path

            # When: First extension approved
            result1 = orchestrator.request_extension(
                reason="First extension for initial complexity",
                additional_turns=3,
                additional_minutes=None,
            )

            # And: Second extension approved
            result2 = orchestrator.request_extension(
                reason="Second extension for unexpected issues",
                additional_turns=5,
                additional_minutes=None,
            )

            # Then: Both extensions approved
            assert result1.approved is True
            assert result2.approved is True

            # And: max_turns updated cumulatively (10 + 3 + 5 = 18)
            updated_data = json.loads(step_file_path.read_text())
            phase = updated_data["tdd_cycle"]["phase_execution_log"][0]
            assert phase["max_turns"] == 18

            # And: Both extension records in history
            extensions = phase["extensions_granted"]
            assert len(extensions) == 2
            assert extensions[0]["additional_turns"] == 3
            assert extensions[1]["additional_turns"] == 5

    def _create_step_file_with_turn_config(
        self, current_turn: int, max_turns: int
    ) -> dict:
        """Create minimal step file with turn count configuration."""
        return {
            "task_specification": {
                "task_id": "06-01",
                "project_id": "des-us004",
                "name": "Test extension request",
            },
            "state": {
                "status": "IN_PROGRESS",
                "started_at": datetime.now(timezone.utc).isoformat(),
                "ended_at": None,
            },
            "tdd_cycle": {
                "phase_execution_log": [
                    {
                        "phase_name": "PREPARE",
                        "phase_index": 0,
                        "status": "IN_PROGRESS",
                        "started_at": datetime.now(timezone.utc).isoformat(),
                        "ended_at": None,
                        "turn_count": current_turn,
                        "max_turns": max_turns,
                        "timeout_minutes": 15,
                        "extensions_granted": [],
                    }
                ]
            },
        }

    def _create_step_file_with_timeout_config(
        self, started_at: str, timeout_minutes: int
    ) -> dict:
        """Create minimal step file with timeout configuration."""
        return {
            "task_specification": {
                "task_id": "06-01",
                "project_id": "des-us004",
                "name": "Test extension request",
            },
            "state": {
                "status": "IN_PROGRESS",
                "started_at": started_at,
                "ended_at": None,
            },
            "tdd_cycle": {
                "phase_execution_log": [
                    {
                        "phase_name": "PREPARE",
                        "phase_index": 0,
                        "status": "IN_PROGRESS",
                        "started_at": started_at,
                        "ended_at": None,
                        "turn_count": 0,
                        "max_turns": 10,
                        "timeout_minutes": timeout_minutes,
                        "extensions_granted": [],
                    }
                ]
            },
        }
