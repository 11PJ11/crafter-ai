"""
E2E Acceptance Tests: US-004 Turn Counting Integration

PERSONA: Marcus (Senior Developer)
STORY: As a senior developer, I want TurnCounter integrated into DESOrchestrator
       so that turn counts are tracked and persisted during command execution.

PROBLEM: TurnCounter exists but isn't wired into the orchestrator's execution loop.
         Without integration, turn counts aren't tracked during real command execution.

SOLUTION: Wire TurnCounter into DESOrchestrator.execute_step() method to:
          - Initialize counter at phase start
          - Increment on each agent call iteration
          - Persist to step file in real-time
          - Restore state on resume

BUSINESS VALUE:
- Track execution progress through turn counting
- Persist turn counts for audit trail
- Enable execution resume with preserved state
- Support timeout monitoring

SOURCE:
- docs/feature/des-us006/steps/02-01.json (Step 02-01)
"""


class TestTurnCountingIntegration:
    """
    E2E acceptance tests for TurnCounter integration with DESOrchestrator.

    Validates that turn counting happens during actual command execution
    and persists to step file for audit trail.
    """

    def test_scenario_011_turn_count_increments_during_execution(
        self,
        tmp_project_root,
        minimal_step_file,
        des_orchestrator,
        in_memory_filesystem,
    ):
        """
        AC-004.1: Turn count increments on each agent call during execute_step().

        GIVEN /nw:execute or /nw:develop command invoked
        WHEN orchestrator executes step via execute_step()
        AND sub-agent makes multiple invocation iterations
        THEN turn_count field increments for each iteration
        AND turn_count persisted to step file phase_execution_log

        Business Context:
        Marcus runs `/nw:execute @software-crafter steps/01-01.json`.
        The orchestrator must track how many turns the agent uses during
        execution and persist this to the step file for audit trail.

        This enables:
        1. Progress tracking (agent at turn 15, expected ~25 for this phase)
        2. Timeout monitoring (agent approaching turn limit)
        3. Resume capability (restore turn count on interrupted execution)
        """
        # GIVEN: /nw:execute command with step file

        command = "/nw:execute"
        agent = "@software-crafter"
        step_file_path = str(minimal_step_file.relative_to(tmp_project_root))

        # Create initial step file structure with required fields
        step_data = {
            "task_id": "02-01",
            "project_id": "test-project",
            "state": {
                "status": "IN_PROGRESS",
                "started_at": "2026-01-26T10:00:00Z",
                "completed_at": None,
            },
            "tdd_cycle": {
                "max_turns": 50,
                "duration_minutes": 30,
                "total_extensions_minutes": 0,
                "phase_execution_log": [
                    {
                        "phase_name": "PREPARE",
                        "phase_index": 0,
                        "status": "IN_PROGRESS",
                        "turn_count": 0,
                    }
                ],
            },
        }

        # Write initial data to in-memory filesystem
        in_memory_filesystem.write_json(minimal_step_file, step_data)

        # WHEN: Orchestrator executes step (simulating agent iterations)
        expected_iterations = 3

        result = des_orchestrator.execute_step(
            command=command,
            agent=agent,
            step_file=step_file_path,
            project_root=tmp_project_root,
            simulated_iterations=expected_iterations,  # Test parameter
        )

        # THEN: Turn count incremented for each iteration
        assert result.turn_count == expected_iterations, (
            f"Expected turn_count={expected_iterations} after {expected_iterations} iterations, "
            f"got {result.turn_count}"
        )

        # AND: Turn count persisted to step file
        step_data = in_memory_filesystem.read_json(minimal_step_file)

        # Verify turn_count in phase_execution_log
        phase_log = step_data["tdd_cycle"]["phase_execution_log"]
        current_phase = next(
            (p for p in phase_log if p["status"] == "IN_PROGRESS"), None
        )

        assert current_phase is not None, "No IN_PROGRESS phase found in execution log"
        assert "turn_count" in current_phase, "turn_count field missing from phase log"
        assert current_phase["turn_count"] == expected_iterations, (
            f"turn_count in step file should be {expected_iterations}, "
            f"got {current_phase.get('turn_count')}"
        )

    def test_scenario_012_turn_limit_exceeded_detected_by_hook(
        self, tmp_project_root, minimal_step_file
    ):
        """
        AC-004.2: SubagentStopHook detects turn limit exceeded after execution.

        GIVEN software-crafter agent completes step execution
        AND turn_count exceeds configured max_turns limit
        WHEN SubagentStopHook.on_agent_complete() fires
        THEN hook detects turn_limit_exceeded condition
        AND HookResult includes turn_limit_exceeded boolean field set to True
        AND error message identifies which phase exceeded the limit
        AND recovery suggestions guide user on increasing limit or simplifying step

        Business Context:
        Marcus configured max_turns=50 for a complex refactoring step.
        The agent used 65 turns during GREEN_UNIT phase, exceeding the limit.
        The hook must detect this post-execution and alert Marcus with:
        1. Which phase exceeded the limit (GREEN_UNIT used 65/50 turns)
        2. Suggestions to either increase max_turns or break step into smaller parts

        This enables:
        1. Post-execution turn limit detection (complements runtime monitoring)
        2. Audit trail of limit violations
        3. Actionable recovery guidance
        """
        # Arrange: Create step file with turn count exceeding limit
        import json

        step_data = _create_step_file_with_turn_limit_exceeded(
            phase_name="GREEN_UNIT", turn_count=65, max_turns=50
        )
        minimal_step_file.write_text(json.dumps(step_data, indent=2))

        # Act: Trigger SubagentStop hook
        from src.des.application.hooks import SubagentStopHook

        hook = SubagentStopHook()
        hook_result = hook.on_agent_complete(step_file_path=str(minimal_step_file))

        # Assert: Turn limit exceeded detected
        assert hasattr(hook_result, "turn_limit_exceeded"), (
            "HookResult missing turn_limit_exceeded field"
        )
        assert hook_result.turn_limit_exceeded is True, (
            "turn_limit_exceeded should be True when turn count exceeds max_turns"
        )

        # Assert: Phase identified in error message
        assert hook_result.error_message is not None
        assert "GREEN_UNIT" in hook_result.error_message, (
            "Error message should identify which phase exceeded limit"
        )
        assert (
            "65" in hook_result.error_message
            or "exceeded" in hook_result.error_message.lower()
        ), "Error message should mention turn count or 'exceeded'"

        # Assert: Recovery suggestions provided
        assert hook_result.recovery_suggestions is not None
        assert len(hook_result.recovery_suggestions) >= 2, (
            "At least 2 recovery suggestions expected (increase limit, simplify step)"
        )

        # Verify suggestions include key guidance
        suggestions_text = " ".join(hook_result.recovery_suggestions).lower()
        assert any(
            keyword in suggestions_text
            for keyword in ["increase", "max_turns", "limit", "higher"]
        ), "Should suggest increasing max_turns limit"

        assert any(
            keyword in suggestions_text
            for keyword in ["simplify", "break", "smaller", "split"]
        ), "Should suggest simplifying or splitting step"

    def test_scenario_017_timeout_exceeded_detected_by_hook(
        self, tmp_project_root, minimal_step_file
    ):
        """
        AC-007.1: SubagentStopHook detects timeout exceeded after execution.

        GIVEN software-crafter agent completes step execution
        AND duration_seconds > (duration_minutes * 60 + total_extensions_minutes * 60)
        WHEN SubagentStopHook.on_agent_complete() fires
        THEN hook detects timeout_exceeded condition
        AND HookResult includes timeout_exceeded boolean field set to True
        AND error message identifies timeout with actual vs expected duration
        AND recovery suggestions include requesting extension or simplifying step

        Business Context:
        Marcus configured duration_minutes=30 with total_extensions_minutes=10 for a step.
        The agent used 2700 seconds (45 minutes), exceeding the 40-minute limit (30+10).
        The hook must detect this post-execution and alert Marcus with:
        1. Timeout detection (2700s > 2400s = 40 min timeout exceeded)
        2. Suggestions to request extension or simplify the step

        This enables:
        1. Post-execution timeout detection (complements runtime monitoring)
        2. Audit trail of timeout violations
        3. Actionable recovery guidance
        """
        # Arrange: Create step file with duration exceeding timeout
        import json

        step_data = _create_step_file_with_timeout_exceeded(
            duration_seconds=2700,  # 45 minutes
            duration_minutes=30,
            total_extensions_minutes=10,  # Total allowed: 40 minutes
        )
        minimal_step_file.write_text(json.dumps(step_data, indent=2))

        # Act: Trigger SubagentStop hook
        from src.des.application.hooks import SubagentStopHook

        hook = SubagentStopHook()
        hook_result = hook.on_agent_complete(step_file_path=str(minimal_step_file))

        # Assert: Timeout exceeded detected
        assert hasattr(hook_result, "timeout_exceeded"), (
            "HookResult missing timeout_exceeded field"
        )
        assert hook_result.timeout_exceeded is True, (
            "timeout_exceeded should be True when duration exceeds limit"
        )

        # Assert: Error message identifies timeout and duration
        assert hook_result.error_message is not None
        error_msg = hook_result.error_message.lower()
        assert (
            "timeout" in error_msg or "exceeded" in error_msg or "duration" in error_msg
        ), "Error message should mention timeout/exceeded/duration"
        assert (
            "2700" in hook_result.error_message or "45" in hook_result.error_message
        ), "Error message should mention actual duration (2700s or 45min)"
        assert (
            "2400" in hook_result.error_message or "40" in hook_result.error_message
        ), "Error message should mention expected duration (2400s or 40min)"

        # Assert: Recovery suggestions provided
        assert hook_result.recovery_suggestions is not None
        assert len(hook_result.recovery_suggestions) >= 2, (
            "At least 2 recovery suggestions expected (request extension, simplify step)"
        )

        # Verify suggestions include key guidance
        suggestions_text = " ".join(hook_result.recovery_suggestions).lower()
        assert any(
            keyword in suggestions_text
            for keyword in ["extension", "extend", "request", "more time"]
        ), "Should suggest requesting extension"

        assert any(
            keyword in suggestions_text
            for keyword in ["simplify", "break", "smaller", "split", "reduce"]
        ), "Should suggest simplifying or splitting step"


def _create_step_file_with_timeout_exceeded(
    duration_seconds: int, duration_minutes: int, total_extensions_minutes: int
):
    """Create step file where execution exceeded timeout.

    Args:
        duration_seconds: Actual execution time in seconds
        duration_minutes: Configured duration limit in minutes
        total_extensions_minutes: Total extension time granted in minutes

    Returns:
        Step file data dict with timeout exceeded
    """
    return {
        "task_id": "07-01",
        "project_id": "des-us006",
        "workflow_type": "tdd_cycle",
        "state": {
            "status": "COMPLETED",
            "started_at": "2026-01-25T10:00:00Z",
            "completed_at": "2026-01-25T10:45:00Z",
        },
        "tdd_cycle": {
            "duration_minutes": duration_minutes,
            "total_extensions_minutes": total_extensions_minutes,
            "phase_execution_log": [
                {
                    "phase_number": 0,
                    "phase_name": "PREPARE",
                    "status": "EXECUTED",
                    "outcome": "PASS",
                    "duration_seconds": 300,
                },
                {
                    "phase_number": 1,
                    "phase_name": "RED_ACCEPTANCE",
                    "status": "EXECUTED",
                    "outcome": "PASS",
                    "duration_seconds": duration_seconds - 300,  # Remaining time
                },
            ],
        },
    }


def _create_step_file_with_turn_limit_exceeded(
    phase_name: str, turn_count: int, max_turns: int
):
    """Create step file where phase exceeded turn limit.

    Args:
        phase_name: Name of phase that exceeded limit
        turn_count: Actual turn count used
        max_turns: Configured maximum turns allowed

    Returns:
        Step file data dict with turn limit exceeded
    """
    phases = [
        "PREPARE",
        "RED_ACCEPTANCE",
        "RED_UNIT",
        "GREEN_UNIT",
        "CHECK_ACCEPTANCE",
        "GREEN_ACCEPTANCE",
        "REVIEW",
        "REFACTOR_L1",
        "REFACTOR_L2",
        "REFACTOR_L3",
        "REFACTOR_L4",
        "POST_REFACTOR_REVIEW",
        "FINAL_VALIDATE",
        "COMMIT",
    ]

    target_idx = phases.index(phase_name)

    phase_log = []
    for i, phase in enumerate(phases):
        if i < target_idx:
            status = "EXECUTED"
            outcome = "PASS"
            phase_turn_count = 10  # Normal turn count
        elif phase == phase_name:
            status = "EXECUTED"
            outcome = "PASS"
            phase_turn_count = turn_count  # Exceeded turn count
        else:
            status = "NOT_EXECUTED"
            outcome = None
            phase_turn_count = 0

        phase_entry = {
            "phase_number": i,
            "phase_name": phase,
            "status": status,
            "outcome": outcome,
            "outcome_details": f"{phase} completed" if status == "EXECUTED" else None,
            "blocked_by": None,
        }

        # Add turn_count and max_turns to phase log
        if status != "NOT_EXECUTED":
            phase_entry["turn_count"] = phase_turn_count
            phase_entry["max_turns"] = max_turns

        phase_log.append(phase_entry)

    return {
        "task_id": "02-02",
        "project_id": "des-us006",
        "workflow_type": "tdd_cycle",
        "state": {
            "status": "IN_PROGRESS",
            "started_at": "2026-01-25T10:00:00Z",
            "completed_at": None,
        },
        "tdd_cycle": {
            "phase_execution_log": phase_log,
            "max_turns": max_turns,  # Global max_turns config
        },
    }
