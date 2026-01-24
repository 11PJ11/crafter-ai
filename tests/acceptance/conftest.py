"""Shared fixtures for acceptance tests."""

import json
import pytest


@pytest.fixture
def tmp_project_root(tmp_path):
    """Create temporary project root with DES directory structure."""
    # Create required directories
    (tmp_path / "steps").mkdir(parents=True)
    (tmp_path / "templates" / "prompt-templates").mkdir(parents=True)
    (tmp_path / "audit").mkdir(parents=True)
    return tmp_path


@pytest.fixture
def minimal_step_file(tmp_project_root):
    """Create a minimal valid step file for testing."""
    step_file = tmp_project_root / "steps" / "test-step.json"

    # Create minimal step structure with 14 TDD phases
    step_data = {
        "task_specification": {
            "task_id": "test-01",
            "project_id": "test-project",
            "step_type": "feature",
            "name": "Test step",
            "description": "Test step for validation",
        },
        "state": {
            "status": "IN_PROGRESS",
            "started_at": "2026-01-01T00:00:00Z",
            "completed_at": None,
        },
        "tdd_cycle": {
            "phase_execution_log": [
                {
                    "phase_name": phase_name,
                    "phase_index": idx,
                    "status": "NOT_EXECUTED",
                    "started_at": None,
                    "ended_at": None,
                    "duration_minutes": None,
                    "outcome": None,
                    "outcome_details": None,
                    "artifacts_created": [],
                    "artifacts_modified": [],
                    "test_results": {
                        "total": None,
                        "passed": None,
                        "failed": None,
                        "skipped": None,
                    },
                    "notes": None,
                    "blocked_by": None,
                    "history": [],
                }
                for idx, phase_name in enumerate(
                    [
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
                )
            ]
        },
    }

    step_file.write_text(json.dumps(step_data, indent=2))
    return step_file


@pytest.fixture
def des_orchestrator():
    """DES orchestrator for testing command execution flow."""
    from des.orchestrator import DESOrchestrator

    return DESOrchestrator()
