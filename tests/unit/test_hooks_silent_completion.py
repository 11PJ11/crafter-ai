"""Unit tests for SubagentStopHook silent completion detection.

Tests the specific logic for detecting when a task is marked IN_PROGRESS
but no phases have been executed (all phases are NOT_EXECUTED).
"""

from src.des.hooks import SubagentStopHook


class TestSilentCompletionDetection:
    """Unit tests for silent completion validation logic."""

    def test_detect_silent_completion_when_all_phases_not_executed(self):
        """
        GIVEN phase log with all 14 phases showing NOT_EXECUTED status
        AND task state is IN_PROGRESS
        WHEN _detect_silent_completion is called
        THEN it returns True indicating silent completion
        """
        # Arrange
        phase_log = [
            {"phase_name": f"PHASE_{i}", "status": "NOT_EXECUTED"} for i in range(14)
        ]
        hook = SubagentStopHook()

        # Act
        is_silent = hook._detect_silent_completion(phase_log)

        # Assert
        assert is_silent is True

    def test_no_silent_completion_when_at_least_one_phase_executed(self):
        """
        GIVEN phase log where at least one phase is EXECUTED
        WHEN _detect_silent_completion is called
        THEN it returns False (not silent completion)
        """
        # Arrange
        phase_log = [
            {"phase_name": "PREPARE", "status": "EXECUTED"},
            {"phase_name": "RED_ACCEPTANCE", "status": "NOT_EXECUTED"},
        ]
        hook = SubagentStopHook()

        # Act
        is_silent = hook._detect_silent_completion(phase_log)

        # Assert
        assert is_silent is False

    def test_count_not_executed_phases(self):
        """
        GIVEN phase log with mix of statuses
        WHEN _count_not_executed_phases is called
        THEN it returns accurate count of NOT_EXECUTED phases
        """
        # Arrange
        phase_log = [
            {"phase_name": "PREPARE", "status": "EXECUTED"},
            {"phase_name": "RED_ACCEPTANCE", "status": "NOT_EXECUTED"},
            {"phase_name": "RED_UNIT", "status": "NOT_EXECUTED"},
            {"phase_name": "GREEN_UNIT", "status": "IN_PROGRESS"},
        ]
        hook = SubagentStopHook()

        # Act
        count = hook._count_not_executed_phases(phase_log)

        # Assert
        assert count == 2

    def test_count_not_executed_phases_for_all_not_executed(self):
        """
        GIVEN phase log with all 14 phases NOT_EXECUTED
        WHEN _count_not_executed_phases is called
        THEN it returns 14
        """
        # Arrange
        phase_log = [
            {"phase_name": f"PHASE_{i}", "status": "NOT_EXECUTED"} for i in range(14)
        ]
        hook = SubagentStopHook()

        # Act
        count = hook._count_not_executed_phases(phase_log)

        # Assert
        assert count == 14

    def test_populate_silent_completion_failure(self):
        """
        GIVEN a HookResult object
        WHEN _populate_silent_completion_failure is called with phase count
        THEN result is updated with SILENT_COMPLETION error details
        """
        # Arrange
        from src.des.hooks import HookResult

        result = HookResult(validation_status="PASSED")
        hook = SubagentStopHook()

        # Act
        hook._populate_silent_completion_failure(result, not_executed_count=14)

        # Assert
        assert result.validation_status == "FAILED"
        assert result.error_type == "SILENT_COMPLETION"
        assert "Agent completed without updating step file" in result.error_message
        assert result.error_count == 1
        assert len(result.recovery_suggestions) >= 1
