"""Unit tests for DESOrchestrator.execute_step() turn counting integration."""

from des.orchestrator import DESOrchestrator
from datetime import datetime, timezone, timedelta
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


class TestOrchestratorTimeoutMonitoringIntegration:
    """Test suite for TimeoutMonitor integration in execute_step()."""

    def test_execute_step_accepts_timeout_thresholds_parameter(self, tmp_path):
        """execute_step() should accept timeout_thresholds parameter."""
        # GIVEN: Orchestrator with step file
        orchestrator = DESOrchestrator()
        step_file = tmp_path / "test_step.json"
        step_data = {
            "tdd_cycle": {
                "phase_execution_log": [
                    {
                        "phase_name": "PREPARE",
                        "status": "NOT_EXECUTED",
                        "turn_count": 0,
                        "started_at": datetime.now(timezone.utc).isoformat(),
                    }
                ]
            }
        }
        step_file.write_text(json.dumps(step_data))

        # WHEN: execute_step() is called with timeout_thresholds
        result = orchestrator.execute_step(
            command="/nw:execute",
            agent="@software-crafter",
            step_file=str(step_file),
            project_root=tmp_path,
            simulated_iterations=0,
            timeout_thresholds=[5, 10, 15],
        )

        # THEN: Call succeeds without error
        assert result is not None

    def test_execute_step_initializes_timeout_monitor_with_phase_start_time(
        self, tmp_path
    ):
        """execute_step() should initialize TimeoutMonitor with phase started_at timestamp."""
        # GIVEN: Orchestrator with step file that has started_at timestamp
        orchestrator = DESOrchestrator()
        step_file = tmp_path / "test_step.json"
        started_at = (datetime.now(timezone.utc) - timedelta(minutes=3)).isoformat()
        step_data = {
            "tdd_cycle": {
                "phase_execution_log": [
                    {
                        "phase_name": "PREPARE",
                        "status": "NOT_EXECUTED",
                        "turn_count": 0,
                        "started_at": started_at,
                    }
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
            timeout_thresholds=[5, 10, 15],
        )

        # THEN: TimeoutMonitor is initialized (no error)
        assert result is not None

    def test_execute_step_checks_thresholds_during_execution_loop(self, tmp_path):
        """execute_step() should check thresholds during execution loop."""
        # GIVEN: Step file with phase started 7 minutes ago
        orchestrator = DESOrchestrator()
        step_file = tmp_path / "test_step.json"
        started_at = (datetime.now(timezone.utc) - timedelta(minutes=7)).isoformat()
        step_data = {
            "tdd_cycle": {
                "phase_execution_log": [
                    {
                        "phase_name": "PREPARE",
                        "status": "NOT_EXECUTED",
                        "turn_count": 0,
                        "started_at": started_at,
                    }
                ]
            }
        }
        step_file.write_text(json.dumps(step_data))

        # WHEN: execute_step() runs with threshold checking
        result = orchestrator.execute_step(
            command="/nw:execute",
            agent="@software-crafter",
            step_file=str(step_file),
            project_root=tmp_path,
            simulated_iterations=3,
            timeout_thresholds=[5, 10, 15],
        )

        # THEN: Result includes warnings_emitted attribute
        assert hasattr(result, "warnings_emitted")

    def test_execute_step_emits_warnings_for_crossed_thresholds(self, tmp_path):
        """execute_step() should emit warnings when thresholds are crossed."""
        # GIVEN: Step file with phase started 7 minutes ago (crosses 5-minute threshold)
        orchestrator = DESOrchestrator()
        step_file = tmp_path / "test_step.json"
        started_at = (datetime.now(timezone.utc) - timedelta(minutes=7)).isoformat()
        step_data = {
            "tdd_cycle": {
                "phase_execution_log": [
                    {
                        "phase_name": "PREPARE",
                        "status": "NOT_EXECUTED",
                        "turn_count": 0,
                        "started_at": started_at,
                    }
                ]
            }
        }
        step_file.write_text(json.dumps(step_data))

        # WHEN: execute_step() runs with thresholds [5, 10, 15]
        result = orchestrator.execute_step(
            command="/nw:execute",
            agent="@software-crafter",
            step_file=str(step_file),
            project_root=tmp_path,
            simulated_iterations=3,
            timeout_thresholds=[5, 10, 15],
        )

        # THEN: Warnings are emitted for 5-minute threshold
        assert result.warnings_emitted is not None
        assert len(result.warnings_emitted) > 0

    def test_execute_step_includes_threshold_value_in_warning(self, tmp_path):
        """Emitted warnings should include the crossed threshold value."""
        # GIVEN: Step file with phase started 7 minutes ago
        orchestrator = DESOrchestrator()
        step_file = tmp_path / "test_step.json"
        started_at = (datetime.now(timezone.utc) - timedelta(minutes=7)).isoformat()
        step_data = {
            "tdd_cycle": {
                "phase_execution_log": [
                    {
                        "phase_name": "PREPARE",
                        "status": "NOT_EXECUTED",
                        "turn_count": 0,
                        "started_at": started_at,
                    }
                ]
            }
        }
        step_file.write_text(json.dumps(step_data))

        # WHEN: execute_step() runs
        result = orchestrator.execute_step(
            command="/nw:execute",
            agent="@software-crafter",
            step_file=str(step_file),
            project_root=tmp_path,
            simulated_iterations=3,
            timeout_thresholds=[5, 10, 15],
        )

        # THEN: Warning mentions 5-minute threshold
        assert any("5" in warning for warning in result.warnings_emitted)

    def test_execute_step_includes_remaining_time_in_warning(self, tmp_path):
        """Emitted warnings should include remaining time information."""
        # GIVEN: Step file with phase started 7 minutes ago
        orchestrator = DESOrchestrator()
        step_file = tmp_path / "test_step.json"
        started_at = (datetime.now(timezone.utc) - timedelta(minutes=7)).isoformat()
        step_data = {
            "tdd_cycle": {
                "phase_execution_log": [
                    {
                        "phase_name": "PREPARE",
                        "status": "NOT_EXECUTED",
                        "turn_count": 0,
                        "started_at": started_at,
                    }
                ]
            }
        }
        step_file.write_text(json.dumps(step_data))

        # WHEN: execute_step() runs
        result = orchestrator.execute_step(
            command="/nw:execute",
            agent="@software-crafter",
            step_file=str(step_file),
            project_root=tmp_path,
            simulated_iterations=3,
            timeout_thresholds=[5, 10, 15],
        )

        # THEN: Warning mentions remaining time or elapsed time
        warning_text = " ".join(result.warnings_emitted).lower()
        assert "remaining" in warning_text or "elapsed" in warning_text
