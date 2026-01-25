"""Unit tests for DESOrchestrator.execute_step() turn counting integration."""

from des.orchestrator import DESOrchestrator
import json


class TestOrchestratorExecuteStep:
    """Test suite for execute_step() method with TurnCounter integration."""

    def test_execute_step_initializes_turn_counter(self, tmp_path):
        """execute_step() should initialize TurnCounter at phase start."""
        # GIVEN: Orchestrator with step file
        orchestrator = DESOrchestrator()
        step_file = tmp_path / "test_step.json"
        step_data = {
            "tdd_cycle": {
                "phase_execution_log": [
                    {"phase_name": "PREPARE", "status": "NOT_EXECUTED", "turn_count": 0}
                ]
            }
        }
        step_file.write_text(json.dumps(step_data))

        # WHEN: execute_step() is called
        result = orchestrator.execute_step(
            command="/nw:execute",
            agent="@software-crafter",
            step_file=str(step_file),
            project_root=tmp_path,
            simulated_iterations=0,
        )

        # THEN: TurnCounter is initialized
        assert result.turn_count == 0

    def test_execute_step_increments_turn_count(self, tmp_path):
        """execute_step() should increment turn count on each iteration."""
        # GIVEN: Orchestrator with step file
        orchestrator = DESOrchestrator()
        step_file = tmp_path / "test_step.json"
        step_data = {
            "tdd_cycle": {
                "phase_execution_log": [
                    {"phase_name": "PREPARE", "status": "NOT_EXECUTED", "turn_count": 0}
                ]
            }
        }
        step_file.write_text(json.dumps(step_data))

        # WHEN: execute_step() runs with 3 simulated iterations
        result = orchestrator.execute_step(
            command="/nw:execute",
            agent="@software-crafter",
            step_file=str(step_file),
            project_root=tmp_path,
            simulated_iterations=3,
        )

        # THEN: Turn count is 3
        assert result.turn_count == 3

    def test_execute_step_persists_turn_count_to_step_file(self, tmp_path):
        """execute_step() should persist turn_count to step file phase_execution_log."""
        # GIVEN: Orchestrator with step file
        orchestrator = DESOrchestrator()
        step_file = tmp_path / "test_step.json"
        step_data = {
            "tdd_cycle": {
                "phase_execution_log": [
                    {"phase_name": "PREPARE", "status": "NOT_EXECUTED", "turn_count": 0}
                ]
            }
        }
        step_file.write_text(json.dumps(step_data))

        # WHEN: execute_step() runs with 5 simulated iterations
        orchestrator.execute_step(
            command="/nw:execute",
            agent="@software-crafter",
            step_file=str(step_file),
            project_root=tmp_path,
            simulated_iterations=5,
        )

        # THEN: turn_count persisted to step file
        updated_data = json.loads(step_file.read_text())
        phase_log = updated_data["tdd_cycle"]["phase_execution_log"][0]
        assert phase_log["turn_count"] == 5

    def test_execute_step_restores_turn_count_from_step_file(self, tmp_path):
        """execute_step() should restore turn count from step file on resume."""
        # GIVEN: Orchestrator with step file having existing turn count
        orchestrator = DESOrchestrator()
        step_file = tmp_path / "test_step.json"
        step_data = {
            "tdd_cycle": {
                "phase_execution_log": [
                    {"phase_name": "PREPARE", "status": "IN_PROGRESS", "turn_count": 7}
                ]
            }
        }
        step_file.write_text(json.dumps(step_data))

        # WHEN: execute_step() resumes with 2 more iterations
        result = orchestrator.execute_step(
            command="/nw:execute",
            agent="@software-crafter",
            step_file=str(step_file),
            project_root=tmp_path,
            simulated_iterations=2,
        )

        # THEN: Turn count continues from 7 -> 9
        assert result.turn_count == 9
