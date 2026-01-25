"""
Unit tests for DESOrchestrator timeout warning prompt injection.

Tests that timeout warnings are properly injected into agent prompt context
when thresholds are crossed during execution.
"""

from datetime import datetime, timezone, timedelta
from pathlib import Path
import json
import tempfile
from des.orchestrator import DESOrchestrator


class TestOrchestratorPromptWarnings:
    """Unit tests for timeout warning injection in render_prompt()."""

    def test_render_prompt_accepts_timeout_parameters(self):
        """
        GIVEN DESOrchestrator instance
        WHEN render_prompt is called with timeout_thresholds and timeout_budget_minutes
        THEN method should accept parameters without error
        """
        orchestrator = DESOrchestrator()

        with tempfile.TemporaryDirectory() as tmpdir:
            step_file_path = Path(tmpdir) / "test_step.json"
            self._create_step_file(step_file_path, minutes_ago=0)

            # Should not raise TypeError
            prompt = orchestrator.render_prompt(
                command="/nw:execute",
                agent="@software-crafter",
                step_file="test_step.json",
                project_root=tmpdir,
                timeout_thresholds=[5, 10, 15],
                timeout_budget_minutes=40
            )
            assert isinstance(prompt, str)

    def test_render_prompt_loads_warnings_from_step_file(self):
        """
        GIVEN step file with phase that started 7 minutes ago
        WHEN render_prompt is called with threshold at 5 minutes
        THEN orchestrator should detect crossed threshold and generate warning
        """
        orchestrator = DESOrchestrator()

        with tempfile.TemporaryDirectory() as tmpdir:
            step_file_path = Path(tmpdir) / "test_step.json"
            self._create_step_file(step_file_path, minutes_ago=7)

            prompt = orchestrator.render_prompt(
                command="/nw:execute",
                agent="@software-crafter",
                step_file="test_step.json",
                project_root=tmpdir,
                timeout_thresholds=[5],
                timeout_budget_minutes=40
            )

            # Prompt should contain timeout warning
            assert "TIMEOUT WARNING" in prompt

    def test_warning_includes_percentage_elapsed(self):
        """
        GIVEN step file with phase running for 30 minutes with 40 minute budget
        WHEN render_prompt generates warning
        THEN warning should include percentage elapsed (75%)
        """
        orchestrator = DESOrchestrator()

        with tempfile.TemporaryDirectory() as tmpdir:
            step_file_path = Path(tmpdir) / "test_step.json"
            self._create_step_file(step_file_path, minutes_ago=30)

            prompt = orchestrator.render_prompt(
                command="/nw:execute",
                agent="@software-crafter",
                step_file="test_step.json",
                project_root=tmpdir,
                timeout_thresholds=[25],
                timeout_budget_minutes=40
            )

            # Should include percentage
            assert "75%" in prompt or "75 %" in prompt

    def test_warning_includes_remaining_time(self):
        """
        GIVEN step file with phase running for 30 minutes with 40 minute budget
        WHEN render_prompt generates warning
        THEN warning should include remaining time (10 minutes)
        """
        orchestrator = DESOrchestrator()

        with tempfile.TemporaryDirectory() as tmpdir:
            step_file_path = Path(tmpdir) / "test_step.json"
            self._create_step_file(step_file_path, minutes_ago=30)

            prompt = orchestrator.render_prompt(
                command="/nw:execute",
                agent="@software-crafter",
                step_file="test_step.json",
                project_root=tmpdir,
                timeout_thresholds=[25],
                timeout_budget_minutes=40
            )

            # Should include remaining time
            assert "Remaining: 10" in prompt or "remaining: 10" in prompt.lower()

    def test_warning_includes_phase_name(self):
        """
        GIVEN step file with PREPARE phase in progress
        WHEN render_prompt generates warning
        THEN warning should include phase name
        """
        orchestrator = DESOrchestrator()

        with tempfile.TemporaryDirectory() as tmpdir:
            step_file_path = Path(tmpdir) / "test_step.json"
            self._create_step_file(step_file_path, minutes_ago=7)

            prompt = orchestrator.render_prompt(
                command="/nw:execute",
                agent="@software-crafter",
                step_file="test_step.json",
                project_root=tmpdir,
                timeout_thresholds=[5],
                timeout_budget_minutes=40
            )

            # Should include phase name
            assert "PREPARE" in prompt

    def test_no_warning_when_no_threshold_crossed(self):
        """
        GIVEN step file with phase running for 3 minutes
        WHEN render_prompt is called with threshold at 5 minutes
        THEN no warning should be generated
        """
        orchestrator = DESOrchestrator()

        with tempfile.TemporaryDirectory() as tmpdir:
            step_file_path = Path(tmpdir) / "test_step.json"
            self._create_step_file(step_file_path, minutes_ago=3)

            prompt = orchestrator.render_prompt(
                command="/nw:execute",
                agent="@software-crafter",
                step_file="test_step.json",
                project_root=tmpdir,
                timeout_thresholds=[5],
                timeout_budget_minutes=40
            )

            # Should NOT contain warning
            assert "TIMEOUT WARNING" not in prompt

    def test_no_warning_when_no_timeout_thresholds_provided(self):
        """
        GIVEN step file with phase running for 7 minutes
        WHEN render_prompt is called without timeout_thresholds
        THEN no warning should be generated
        """
        orchestrator = DESOrchestrator()

        with tempfile.TemporaryDirectory() as tmpdir:
            step_file_path = Path(tmpdir) / "test_step.json"
            self._create_step_file(step_file_path, minutes_ago=7)

            prompt = orchestrator.render_prompt(
                command="/nw:execute",
                agent="@software-crafter",
                step_file="test_step.json",
                project_root=tmpdir
            )

            # Should NOT contain warning
            assert "TIMEOUT WARNING" not in prompt

    def _create_step_file(self, step_file_path: Path, minutes_ago: int):
        """Create test step file with specified start time."""
        started_at = (datetime.now(timezone.utc) - timedelta(minutes=minutes_ago)).isoformat()

        step_data = {
            "task_specification": {
                "task_id": "test",
                "project_id": "test",
                "name": "Test timeout warnings",
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
                    }
                ]
            },
        }

        with open(step_file_path, "w") as f:
            json.dump(step_data, f, indent=2)
