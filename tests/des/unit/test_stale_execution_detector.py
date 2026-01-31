"""
Unit Tests: StaleExecutionDetector Application Service

LAYER: Application Layer (Hexagonal Architecture)
DEPENDENCIES:
- Domain: StaleExecution (value object)
- Domain: StaleDetectionResult (entity)

BUSINESS RULES UNDER TEST:
- Scan steps directory for IN_PROGRESS phases
- Compare phase age against configurable threshold (default 30 min)
- Return StaleDetectionResult with list of stale executions
- Pure file scanning (no DB, HTTP, or external services)
- Environment variable DES_STALE_THRESHOLD_MINUTES overrides default

TEST STRATEGY: Classical TDD (real domain objects, no mocking inside hexagon)
"""

import json
from datetime import datetime, timedelta
from src.des.application.stale_execution_detector import StaleExecutionDetector


class TestStaleExecutionDetectorInitialization:
    """Test service initialization and configuration."""

    def test_detector_initializes_with_project_root(self, tmp_path):
        """
        GIVEN a valid project root path
        WHEN StaleExecutionDetector is initialized
        THEN detector stores project root correctly
        """
        detector = StaleExecutionDetector(project_root=tmp_path)
        assert detector is not None

    def test_detector_uses_default_threshold_30_minutes(self, tmp_path):
        """
        GIVEN no environment variable set
        WHEN StaleExecutionDetector is initialized
        THEN threshold defaults to 30 minutes
        """
        detector = StaleExecutionDetector(project_root=tmp_path)
        assert detector.threshold_minutes == 30

    def test_detector_respects_environment_variable_threshold(
        self, tmp_path, monkeypatch
    ):
        """
        GIVEN DES_STALE_THRESHOLD_MINUTES=10 environment variable
        WHEN StaleExecutionDetector is initialized
        THEN threshold is set to 10 minutes
        """
        monkeypatch.setenv("DES_STALE_THRESHOLD_MINUTES", "10")
        detector = StaleExecutionDetector(project_root=tmp_path)
        assert detector.threshold_minutes == 10


class TestStaleExecutionDetectorScanningLogic:
    """Test core scanning and detection logic."""

    def test_scan_returns_empty_result_when_no_step_files(self, tmp_path):
        """
        GIVEN steps directory is empty
        WHEN scan_for_stale_executions is called
        THEN result has is_blocked=False and empty stale_executions list
        """
        steps_dir = tmp_path / "steps"
        steps_dir.mkdir()

        detector = StaleExecutionDetector(project_root=tmp_path)
        result = detector.scan_for_stale_executions()

        assert result.is_blocked is False
        assert len(result.stale_executions) == 0

    def test_scan_ignores_completed_steps(self, tmp_path):
        """
        GIVEN step file with status="DONE"
        WHEN scan_for_stale_executions is called
        THEN step is not flagged as stale
        """
        steps_dir = tmp_path / "steps"
        steps_dir.mkdir()

        completed_step = {
            "task_id": "01-01",
            "state": {"status": "DONE", "completed_at": datetime.now().isoformat()},
        }
        (steps_dir / "01-01.json").write_text(json.dumps(completed_step))

        detector = StaleExecutionDetector(project_root=tmp_path)
        result = detector.scan_for_stale_executions()

        assert result.is_blocked is False
        assert len(result.stale_executions) == 0

    def test_scan_detects_stale_in_progress_phase_exceeding_threshold(self, tmp_path):
        """
        GIVEN step with IN_PROGRESS phase started 45 minutes ago
        AND threshold is 30 minutes
        WHEN scan_for_stale_executions is called
        THEN step is flagged as stale (45 > 30)
        """
        steps_dir = tmp_path / "steps"
        steps_dir.mkdir()

        stale_timestamp = (datetime.now() - timedelta(minutes=45)).isoformat()
        stale_step = {
            "task_id": "01-01",
            "state": {"status": "IN_PROGRESS", "started_at": stale_timestamp},
            "tdd_cycle": {
                "phase_execution_log": [
                    {
                        "phase_name": "RED_UNIT",
                        "status": "IN_PROGRESS",
                        "started_at": stale_timestamp,
                    }
                ]
            },
        }
        (steps_dir / "01-01.json").write_text(json.dumps(stale_step))

        detector = StaleExecutionDetector(project_root=tmp_path)
        result = detector.scan_for_stale_executions()

        assert result.is_blocked is True
        assert len(result.stale_executions) == 1
        assert result.stale_executions[0].step_file == "steps/01-01.json"
        assert result.stale_executions[0].phase_name == "RED_UNIT"
        assert result.stale_executions[0].age_minutes >= 45

    def test_scan_ignores_recent_in_progress_within_threshold(self, tmp_path):
        """
        GIVEN step with IN_PROGRESS phase started 15 minutes ago
        AND threshold is 30 minutes
        WHEN scan_for_stale_executions is called
        THEN step is NOT flagged as stale (15 < 30)
        """
        steps_dir = tmp_path / "steps"
        steps_dir.mkdir()

        recent_timestamp = (datetime.now() - timedelta(minutes=15)).isoformat()
        recent_step = {
            "task_id": "01-01",
            "state": {"status": "IN_PROGRESS", "started_at": recent_timestamp},
            "tdd_cycle": {
                "phase_execution_log": [
                    {
                        "phase_name": "GREEN_UNIT",
                        "status": "IN_PROGRESS",
                        "started_at": recent_timestamp,
                    }
                ]
            },
        }
        (steps_dir / "01-01.json").write_text(json.dumps(recent_step))

        detector = StaleExecutionDetector(project_root=tmp_path)
        result = detector.scan_for_stale_executions()

        assert result.is_blocked is False
        assert len(result.stale_executions) == 0

    def test_scan_detects_multiple_stale_executions(self, tmp_path):
        """
        GIVEN two step files with stale IN_PROGRESS phases
        WHEN scan_for_stale_executions is called
        THEN both steps are flagged as stale
        """
        steps_dir = tmp_path / "steps"
        steps_dir.mkdir()

        stale_timestamp = (datetime.now() - timedelta(minutes=45)).isoformat()

        # First stale step
        stale_step_1 = {
            "task_id": "01-01",
            "state": {"status": "IN_PROGRESS", "started_at": stale_timestamp},
            "tdd_cycle": {
                "phase_execution_log": [
                    {
                        "phase_name": "RED_UNIT",
                        "status": "IN_PROGRESS",
                        "started_at": stale_timestamp,
                    }
                ]
            },
        }
        (steps_dir / "01-01.json").write_text(json.dumps(stale_step_1))

        # Second stale step
        stale_step_2 = {
            "task_id": "02-01",
            "state": {"status": "IN_PROGRESS", "started_at": stale_timestamp},
            "tdd_cycle": {
                "phase_execution_log": [
                    {
                        "phase_name": "GREEN_UNIT",
                        "status": "IN_PROGRESS",
                        "started_at": stale_timestamp,
                    }
                ]
            },
        }
        (steps_dir / "02-01.json").write_text(json.dumps(stale_step_2))

        detector = StaleExecutionDetector(project_root=tmp_path)
        result = detector.scan_for_stale_executions()

        assert result.is_blocked is True
        assert len(result.stale_executions) == 2

    def test_scan_uses_custom_threshold_from_environment(self, tmp_path, monkeypatch):
        """
        GIVEN DES_STALE_THRESHOLD_MINUTES=10
        AND step with IN_PROGRESS phase started 15 minutes ago
        WHEN scan_for_stale_executions is called
        THEN step is flagged as stale (15 > 10)
        """
        monkeypatch.setenv("DES_STALE_THRESHOLD_MINUTES", "10")
        steps_dir = tmp_path / "steps"
        steps_dir.mkdir()

        stale_timestamp = (datetime.now() - timedelta(minutes=15)).isoformat()
        stale_step = {
            "task_id": "01-01",
            "state": {"status": "IN_PROGRESS", "started_at": stale_timestamp},
            "tdd_cycle": {
                "phase_execution_log": [
                    {
                        "phase_name": "RED_ACCEPTANCE",
                        "status": "IN_PROGRESS",
                        "started_at": stale_timestamp,
                    }
                ]
            },
        }
        (steps_dir / "01-01.json").write_text(json.dumps(stale_step))

        detector = StaleExecutionDetector(project_root=tmp_path)
        result = detector.scan_for_stale_executions()

        assert result.is_blocked is True
        assert len(result.stale_executions) == 1


class TestStaleExecutionDetectorStaleDetectionResult:
    """Test that scan returns proper StaleDetectionResult with domain entities."""

    def test_scan_returns_stale_detection_result_instance(self, tmp_path):
        """
        GIVEN any project state
        WHEN scan_for_stale_executions is called
        THEN returns StaleDetectionResult instance
        """
        steps_dir = tmp_path / "steps"
        steps_dir.mkdir()

        detector = StaleExecutionDetector(project_root=tmp_path)
        result = detector.scan_for_stale_executions()

        from src.des.domain.stale_detection_result import StaleDetectionResult

        assert isinstance(result, StaleDetectionResult)

    def test_scan_result_contains_stale_execution_instances(self, tmp_path):
        """
        GIVEN stale step file
        WHEN scan_for_stale_executions is called
        THEN result contains StaleExecution instances
        """
        steps_dir = tmp_path / "steps"
        steps_dir.mkdir()

        stale_timestamp = (datetime.now() - timedelta(minutes=45)).isoformat()
        stale_step = {
            "task_id": "01-01",
            "state": {"status": "IN_PROGRESS", "started_at": stale_timestamp},
            "tdd_cycle": {
                "phase_execution_log": [
                    {
                        "phase_name": "RED_UNIT",
                        "status": "IN_PROGRESS",
                        "started_at": stale_timestamp,
                    }
                ]
            },
        }
        (steps_dir / "01-01.json").write_text(json.dumps(stale_step))

        detector = StaleExecutionDetector(project_root=tmp_path)
        result = detector.scan_for_stale_executions()

        from src.des.domain.stale_execution import StaleExecution

        assert len(result.stale_executions) == 1
        assert isinstance(result.stale_executions[0], StaleExecution)


class TestStaleExecutionDetectorEdgeCases:
    """Test edge cases and error handling."""

    def test_scan_handles_missing_steps_directory(self, tmp_path):
        """
        GIVEN steps directory does not exist
        WHEN scan_for_stale_executions is called
        THEN returns empty result (no crash)
        """
        detector = StaleExecutionDetector(project_root=tmp_path)
        result = detector.scan_for_stale_executions()

        assert result.is_blocked is False
        assert len(result.stale_executions) == 0

    def test_scan_handles_step_file_without_tdd_cycle(self, tmp_path):
        """
        GIVEN step file without tdd_cycle field
        WHEN scan_for_stale_executions is called
        THEN step is safely ignored (no crash)
        """
        steps_dir = tmp_path / "steps"
        steps_dir.mkdir()

        step_without_cycle = {
            "task_id": "01-01",
            "state": {"status": "IN_PROGRESS"},
        }
        (steps_dir / "01-01.json").write_text(json.dumps(step_without_cycle))

        detector = StaleExecutionDetector(project_root=tmp_path)
        result = detector.scan_for_stale_executions()

        assert result.is_blocked is False
        assert len(result.stale_executions) == 0

    def test_scan_handles_phase_without_started_at(self, tmp_path):
        """
        GIVEN IN_PROGRESS phase missing started_at timestamp
        WHEN scan_for_stale_executions is called
        THEN phase is safely ignored (no crash)
        """
        steps_dir = tmp_path / "steps"
        steps_dir.mkdir()

        step_missing_timestamp = {
            "task_id": "01-01",
            "state": {"status": "IN_PROGRESS"},
            "tdd_cycle": {
                "phase_execution_log": [
                    {
                        "phase_name": "RED_UNIT",
                        "status": "IN_PROGRESS",
                        # started_at missing
                    }
                ]
            },
        }
        (steps_dir / "01-01.json").write_text(json.dumps(step_missing_timestamp))

        detector = StaleExecutionDetector(project_root=tmp_path)
        result = detector.scan_for_stale_executions()

        assert result.is_blocked is False
        assert len(result.stale_executions) == 0

    def test_scan_handles_corrupted_json_step_file(self, tmp_path):
        """
        GIVEN step file with invalid JSON
        WHEN scan_for_stale_executions is called
        THEN corrupted file is skipped (no crash)
        """
        steps_dir = tmp_path / "steps"
        steps_dir.mkdir()

        # Create corrupted JSON file
        (steps_dir / "01-01.json").write_text("{ invalid json content")

        # Create valid stale file
        stale_timestamp = (datetime.now() - timedelta(minutes=45)).isoformat()
        valid_step = {
            "task_id": "02-01",
            "state": {"status": "IN_PROGRESS", "started_at": stale_timestamp},
            "tdd_cycle": {
                "phase_execution_log": [
                    {
                        "phase_name": "PREPARE",
                        "status": "IN_PROGRESS",
                        "started_at": stale_timestamp,
                    }
                ]
            },
        }
        (steps_dir / "02-01.json").write_text(json.dumps(valid_step))

        detector = StaleExecutionDetector(project_root=tmp_path)
        result = detector.scan_for_stale_executions()

        # Should detect valid stale file, ignore corrupted file
        assert result.is_blocked is True
        assert len(result.stale_executions) == 1
        assert "02-01" in result.stale_executions[0].step_file
