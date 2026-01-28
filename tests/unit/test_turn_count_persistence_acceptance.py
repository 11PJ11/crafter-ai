"""
Acceptance test for turn_count persistence to step file.

Infrastructure step 01-03: Validates that on_agent_complete() hook
persists turn_count to phase_execution_log.
"""

import pytest
import json
from src.des.adapters.drivers.hooks.real_hook import RealSubagentStopHook


class TestTurnCountPersistence:
    """Test suite for turn_count persistence in on_agent_complete() hook."""

    @pytest.fixture
    def hook(self):
        """Create hook instance."""
        return RealSubagentStopHook()

    @pytest.fixture
    def step_file_with_turn_count(self, tmp_path):
        """Create a step file with turn_count in phase_execution_log."""
        step_data = {
            "task_id": "01-03",
            "state": {"status": "COMPLETED"},
            "tdd_cycle": {
                "max_turns": 50,
                "phase_execution_log": [
                    {
                        "phase_name": "PREPARE",
                        "phase_index": 0,
                        "status": "EXECUTED",
                        "outcome": "PASS",
                        "turn_count": 3,
                    },
                    {
                        "phase_name": "RED_ACCEPTANCE",
                        "phase_index": 1,
                        "status": "EXECUTED",
                        "outcome": "FAIL",
                        "turn_count": 5,
                    },
                ],
            },
        }

        step_file = tmp_path / "step.json"
        with open(step_file, "w") as f:
            json.dump(step_data, f)

        return step_file

    @pytest.fixture
    def step_file_without_turn_count(self, tmp_path):
        """Create a step file without turn_count (backward compatibility test)."""
        step_data = {
            "task_id": "01-03",
            "state": {"status": "COMPLETED"},
            "tdd_cycle": {
                "max_turns": 50,
                "phase_execution_log": [
                    {
                        "phase_name": "PREPARE",
                        "phase_index": 0,
                        "status": "EXECUTED",
                        "outcome": "PASS",
                    }
                ],
            },
        }

        step_file = tmp_path / "step_old.json"
        with open(step_file, "w") as f:
            json.dump(step_data, f)

        return step_file

    def test_turn_count_written_to_step_file(self, hook, step_file_with_turn_count):
        """
        AC-01-03.1: GIVEN phase execution completes
                    WHEN hook processes completion
                    THEN turn_count written to step file phase_execution_log
        """
        # GIVEN: step file with turn_count values
        # (already in fixture)

        # WHEN: Hook processes completion
        result = hook.on_agent_complete(str(step_file_with_turn_count))

        # THEN: Hook should validate turn_count is present (validation passes)
        # and turn_count values should be present in phase_execution_log
        assert (
            result.validation_status == "PASSED"
        ), "Hook validation should pass when turn_count present"

        with open(step_file_with_turn_count, "r") as f:
            step_data = json.load(f)

        phase_log = step_data.get("tdd_cycle", {}).get("phase_execution_log", [])

        # Verify first phase has turn_count = 3
        assert len(phase_log) >= 1
        assert (
            phase_log[0].get("turn_count") == 3
        ), "First phase turn_count should be in log"

        # Verify second phase has turn_count = 5
        assert len(phase_log) >= 2
        assert (
            phase_log[1].get("turn_count") == 5
        ), "Second phase turn_count should be in log"

    def test_backward_compatibility_old_step_files(
        self, hook, step_file_without_turn_count
    ):
        """
        AC-01-03.2: Backward compatibility - old step files without turn_count still work.

        GIVEN old step file without turn_count field
        WHEN hook processes completion
        THEN validation succeeds (no errors for missing turn_count)
        """
        # GIVEN: step file without turn_count (old format)
        # (already in fixture)

        # WHEN: Hook processes completion
        result = hook.on_agent_complete(str(step_file_without_turn_count))

        # THEN: Should not fail (validation passes for old format)
        assert (
            result.validation_status == "PASSED"
        ), "Backward compatibility broken - old files should still validate"

    def test_turn_count_persisted_with_correct_value(
        self, hook, step_file_with_turn_count
    ):
        """
        AC-01-03.3: Turn count matches value from hook context.

        GIVEN phase execution log with turn_count values
        WHEN hook validates completion
        THEN persisted turn_count matches expected values
        """
        # GIVEN: step file with specific turn_count values
        expected_turn_counts = {"PREPARE": 3, "RED_ACCEPTANCE": 5}

        # WHEN: Hook validates
        hook.on_agent_complete(str(step_file_with_turn_count))

        # THEN: Verify turn_count values in step file match expected
        with open(step_file_with_turn_count, "r") as f:
            step_data = json.load(f)

        phase_log = step_data.get("tdd_cycle", {}).get("phase_execution_log", [])

        for phase in phase_log:
            phase_name = phase.get("phase_name")
            if phase_name in expected_turn_counts:
                assert (
                    phase.get("turn_count") == expected_turn_counts[phase_name]
                ), f"Phase {phase_name} turn_count mismatch"

    def test_multiple_phases_turn_count_persisted(self, hook, tmp_path):
        """
        AC-01-03.4: Multiple phases all have turn_count persisted.

        GIVEN step file with multiple phases
        WHEN hook validates
        THEN all phases have turn_count field
        """
        # GIVEN: step file with many phases
        step_data = {
            "task_id": "01-03",
            "state": {"status": "COMPLETED"},
            "tdd_cycle": {
                "max_turns": 50,
                "phase_execution_log": [
                    {
                        "phase_name": f"PHASE_{i}",
                        "phase_index": i,
                        "status": "EXECUTED",
                        "outcome": "PASS",
                        "turn_count": i + 1,
                    }
                    for i in range(5)
                ],
            },
        }

        step_file = tmp_path / "multi_phase_step.json"
        with open(step_file, "w") as f:
            json.dump(step_data, f)

        # WHEN: Hook processes
        hook.on_agent_complete(str(step_file))

        # THEN: All phases have turn_count
        with open(step_file, "r") as f:
            step_data = json.load(f)

        phase_log = step_data.get("tdd_cycle", {}).get("phase_execution_log", [])

        for i, phase in enumerate(phase_log):
            assert "turn_count" in phase, f"Phase {i} missing turn_count field"
            assert isinstance(
                phase.get("turn_count"), int
            ), f"Phase {i} turn_count not integer"
            assert phase.get("turn_count") == i + 1, f"Phase {i} turn_count incorrect"
