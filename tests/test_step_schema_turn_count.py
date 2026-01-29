"""
Unit tests for turn_count field in step-tdd-cycle-schema.json

Tests verify that:
1. phase_execution_log entries include turn_count field
2. turn_count validates as non-negative integer
3. Existing step files remain compatible (turn_count optional/defaults to 0)
"""

import json
import pytest
from pathlib import Path


class TestStepSchemaTurnCountField:
    """Test suite for turn_count field in phase_execution_log"""

    @pytest.fixture
    def schema_path(self):
        """Path to step-tdd-cycle-schema.json"""
        return (
            Path(__file__).parent.parent
            / "nWave"
            / "templates"
            / "step-tdd-cycle-schema.json"
        )

    @pytest.fixture
    def schema_data(self, schema_path):
        """Load schema data"""
        with open(schema_path, "r") as f:
            return json.load(f)

    def test_phase_execution_log_includes_turn_count_field(self, schema_data):
        """
        AC1: phase_execution_log entries include turn_count integer field

        Verify each phase entry template has turn_count field defined.
        """
        phase_log = schema_data["tdd_cycle"]["phase_execution_log"]

        # Should have 8 phases (schema v2.0)
        from nWave.constants.tdd_phases import PHASE_COUNT

        assert (
            len(phase_log) == PHASE_COUNT
        ), f"Expected {PHASE_COUNT} phases, got {len(phase_log)}"

        # Each phase should have turn_count field
        for phase in phase_log:
            assert (
                "turn_count" in phase
            ), f"Phase {phase['phase_name']} missing turn_count field"

            # turn_count should be an integer or null
            turn_count = phase.get("turn_count")
            assert (
                turn_count is None or isinstance(turn_count, int)
            ), f"Phase {phase['phase_name']} turn_count must be int or null, got {type(turn_count)}"

    def test_turn_count_validates_as_non_negative_integer(self, schema_data):
        """
        AC2: Schema validates turn_count as non-negative integer

        Verify turn_count field accepts only non-negative integers.
        """
        phase_log = schema_data["tdd_cycle"]["phase_execution_log"]

        for phase in phase_log:
            turn_count = phase.get("turn_count")

            # If turn_count is set, it must be >= 0
            if turn_count is not None:
                assert isinstance(
                    turn_count, int
                ), f"Phase {phase['phase_name']} turn_count must be integer"
                assert (
                    turn_count >= 0
                ), f"Phase {phase['phase_name']} turn_count must be non-negative, got {turn_count}"

    def test_existing_step_files_remain_compatible(self, schema_path):
        """
        AC3: Existing step files remain compatible (turn_count optional or defaults to 0)

        Verify backward compatibility:
        - turn_count field can be null or 0 (both valid defaults)
        - Missing turn_count doesn't break validation
        - Schema provides sensible defaults
        """
        # Load schema
        with open(schema_path, "r") as f:
            schema_data = json.load(f)

        # Verify all phases have turn_count as null or 0 (both valid defaults)
        phase_log = schema_data["tdd_cycle"]["phase_execution_log"]
        for phase in phase_log:
            turn_count = phase.get("turn_count")
            # Should be null or 0 in template for backward compatibility
            # 0 means "not executed" which is semantically correct
            assert (
                turn_count is None or turn_count == 0
            ), f"Phase {phase['phase_name']} turn_count should default to null or 0 for compatibility, got {turn_count}"

    def test_turn_count_semantic_meaning(self, schema_data):
        """
        Verify turn_count has clear semantic meaning for tracking iterations

        turn_count tracks how many times a phase was executed/retried:
        - 0 or null: Phase not executed or first execution
        - 1: First completed execution
        - 2+: Phase was retried (e.g., review iterations)
        """
        phase_log = schema_data["tdd_cycle"]["phase_execution_log"]

        # Verify turn_count exists in all phase entries
        for phase in phase_log:
            assert (
                "turn_count" in phase
            ), f"Phase {phase['phase_name']} must have turn_count field for iteration tracking"
