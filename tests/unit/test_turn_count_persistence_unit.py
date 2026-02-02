"""
Unit tests for turn_count persistence functionality.

Tests the implementation of turn_count persistence in SubagentStopHook.
"""

import json

import pytest
from src.des.adapters.drivers.hooks.real_hook import RealSubagentStopHook


class TestTurnCountPersistenceUnit:
    """Unit tests for turn_count persistence in hook."""

    @pytest.fixture
    def hook(self):
        """Create hook instance."""
        return RealSubagentStopHook()

    @pytest.fixture
    def temp_step_file(self, tmp_path):
        """Create a temporary step file for testing."""
        step_data = {
            "task_id": "test-01-03",
            "state": {"status": "IN_PROGRESS"},
            "tdd_cycle": {
                "current_phase": "RED_ACCEPTANCE",
                "current_phase_index": 1,
                "max_turns": 50,
                "phase_execution_log": [
                    {
                        "phase_name": "PREPARE",
                        "phase_index": 0,
                        "status": "EXECUTED",
                        "outcome": "PASS",
                    },
                    {
                        "phase_name": "RED_ACCEPTANCE",
                        "phase_index": 1,
                        "status": "IN_PROGRESS",
                        "outcome": None,
                    },
                ],
            },
        }

        step_file = tmp_path / "step.json"
        with open(step_file, "w") as f:
            json.dump(step_data, f)

        return step_file

    def test_persist_turn_count_updates_current_phase(self, hook, temp_step_file):
        """
        Unit test: persist_turn_count() updates current phase with turn_count.

        GIVEN step file with current_phase set and turn_count not present
        WHEN persist_turn_count() called with turn_count=5
        THEN current phase entry updated with turn_count field
        """
        # GIVEN: step file loaded (in fixture)

        # WHEN: Call persist_turn_count with specific turn count
        hook.persist_turn_count(
            str(temp_step_file), phase_name="RED_ACCEPTANCE", turn_count=5
        )

        # THEN: Step file updated with turn_count in RED_ACCEPTANCE phase
        with open(temp_step_file) as f:
            step_data = json.load(f)

        phase_log = step_data.get("tdd_cycle", {}).get("phase_execution_log", [])
        red_acceptance_phase = next(
            p for p in phase_log if p.get("phase_name") == "RED_ACCEPTANCE"
        )

        assert red_acceptance_phase.get("turn_count") == 5, (
            "turn_count not persisted to phase"
        )

    def test_persist_turn_count_all_phases(self, hook, tmp_path):
        """
        Unit test: persist_turn_count() works for all phases.

        GIVEN step file with multiple phases
        WHEN persist_turn_count() called for multiple phases
        THEN all phases have turn_count updated correctly
        """
        # GIVEN: step file with multiple phases
        step_data = {
            "task_id": "test-01-03",
            "tdd_cycle": {
                "phase_execution_log": [
                    {
                        "phase_name": "PREPARE",
                        "phase_index": 0,
                        "status": "EXECUTED",
                        "outcome": "PASS",
                    },
                    {
                        "phase_name": "RED_ACCEPTANCE",
                        "phase_index": 1,
                        "status": "EXECUTED",
                        "outcome": "FAIL",
                    },
                    {
                        "phase_name": "RED_UNIT",
                        "phase_index": 2,
                        "status": "IN_PROGRESS",
                        "outcome": None,
                    },
                ]
            },
        }

        step_file = tmp_path / "multi_phase.json"
        with open(step_file, "w") as f:
            json.dump(step_data, f)

        # WHEN: Persist turn_count for multiple phases
        hook.persist_turn_count(str(step_file), phase_name="PREPARE", turn_count=2)
        hook.persist_turn_count(
            str(step_file), phase_name="RED_ACCEPTANCE", turn_count=4
        )
        hook.persist_turn_count(str(step_file), phase_name="RED_UNIT", turn_count=6)

        # THEN: All phases updated
        with open(step_file) as f:
            step_data = json.load(f)

        phase_log = step_data.get("tdd_cycle", {}).get("phase_execution_log", [])

        prepare = next(p for p in phase_log if p.get("phase_name") == "PREPARE")
        red_acc = next(p for p in phase_log if p.get("phase_name") == "RED_ACCEPTANCE")
        red_unit = next(p for p in phase_log if p.get("phase_name") == "RED_UNIT")

        assert prepare.get("turn_count") == 2, "PREPARE turn_count incorrect"
        assert red_acc.get("turn_count") == 4, "RED_ACCEPTANCE turn_count incorrect"
        assert red_unit.get("turn_count") == 6, "RED_UNIT turn_count incorrect"

    def test_persist_turn_count_non_negative(self, hook, temp_step_file):
        """
        Unit test: persist_turn_count() rejects negative values.

        GIVEN phase entry
        WHEN persist_turn_count() called with negative turn_count
        THEN raises ValueError or sets to 0
        """
        # GIVEN: temp_step_file

        # WHEN/THEN: Negative turn_count should be rejected or converted to 0
        with pytest.raises((ValueError, AssertionError)):
            hook.persist_turn_count(
                str(temp_step_file), phase_name="RED_ACCEPTANCE", turn_count=-1
            )

    def test_persist_turn_count_writes_to_file(self, hook, temp_step_file):
        """
        Unit test: persist_turn_count() writes changes to step file.

        GIVEN step file on disk
        WHEN persist_turn_count() called
        THEN changes written immediately to disk (not just in memory)
        """
        # GIVEN: temp_step_file exists on disk

        # WHEN: Persist turn_count
        hook.persist_turn_count(str(temp_step_file), phase_name="PREPARE", turn_count=3)

        # THEN: File written to disk (verify by re-reading)
        with open(temp_step_file) as f:
            step_data = json.load(f)

        phase_log = step_data.get("tdd_cycle", {}).get("phase_execution_log", [])
        prepare = next(p for p in phase_log if p.get("phase_name") == "PREPARE")

        assert prepare.get("turn_count") == 3, "Changes not persisted to disk"

    def test_persist_turn_count_handles_missing_phase(self, hook, temp_step_file):
        """
        Unit test: persist_turn_count() handles non-existent phase gracefully.

        GIVEN step file without specific phase
        WHEN persist_turn_count() called for non-existent phase
        THEN raises KeyError or silently skips
        """
        # GIVEN: temp_step_file with only PREPARE and RED_ACCEPTANCE phases

        # WHEN/THEN: Calling for non-existent phase
        # Should either raise KeyError or be skipped gracefully
        try:
            hook.persist_turn_count(
                str(temp_step_file), phase_name="NONEXISTENT_PHASE", turn_count=5
            )
            # If no exception, that's okay - just means it silently skips
        except KeyError:
            # This is expected - phase doesn't exist
            pass

    def test_persist_turn_count_backward_compatibility(self, hook, tmp_path):
        """
        Unit test: persist_turn_count() works with old step files without turn_count.

        GIVEN old step file format without turn_count fields
        WHEN persist_turn_count() called
        THEN turn_count fields added without errors
        """
        # GIVEN: Old step file format
        step_data = {
            "task_id": "test-old",
            "tdd_cycle": {
                "phase_execution_log": [
                    {
                        "phase_name": "PREPARE",
                        "phase_index": 0,
                        "status": "EXECUTED",
                        "outcome": "PASS",
                        # Note: no turn_count field
                    }
                ]
            },
        }

        step_file = tmp_path / "old_format.json"
        with open(step_file, "w") as f:
            json.dump(step_data, f)

        # WHEN: Persist turn_count
        hook.persist_turn_count(str(step_file), phase_name="PREPARE", turn_count=1)

        # THEN: File updated successfully with new field
        with open(step_file) as f:
            step_data = json.load(f)

        prepare = step_data.get("tdd_cycle", {}).get("phase_execution_log", [0])[0]
        assert prepare.get("turn_count") == 1, "Backward compatibility broken"

    def test_persist_turn_count_overwrites_existing(self, hook, tmp_path):
        """
        Unit test: persist_turn_count() overwrites existing turn_count value.

        GIVEN phase with existing turn_count=3
        WHEN persist_turn_count() called with turn_count=7
        THEN turn_count updated to 7 (not accumulated)
        """
        # GIVEN: step file with turn_count already set
        step_data = {
            "task_id": "test-overwrite",
            "tdd_cycle": {
                "phase_execution_log": [
                    {
                        "phase_name": "PREPARE",
                        "phase_index": 0,
                        "status": "EXECUTED",
                        "outcome": "PASS",
                        "turn_count": 3,  # existing value
                    }
                ]
            },
        }

        step_file = tmp_path / "overwrite.json"
        with open(step_file, "w") as f:
            json.dump(step_data, f)

        # WHEN: Persist new turn_count
        hook.persist_turn_count(str(step_file), phase_name="PREPARE", turn_count=7)

        # THEN: turn_count updated to 7 (not 3+7=10)
        with open(step_file) as f:
            step_data = json.load(f)

        prepare = step_data.get("tdd_cycle", {}).get("phase_execution_log", [0])[0]
        assert prepare.get("turn_count") == 7, (
            "turn_count should be overwritten, not accumulated"
        )
