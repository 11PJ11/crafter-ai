"""
Pytest configuration for DES acceptance tests.

Provides shared fixtures for test setup and teardown.
"""

import pytest
import json


@pytest.fixture
def tmp_project_root(tmp_path):
    """
    Create a temporary project root with DES directory structure.

    Provides:
    - steps/ directory for step files
    - templates/prompt-templates/ for template files
    - audit/ directory for audit logs

    Returns:
        Path: Temporary project root directory
    """
    # Create DES directory structure
    (tmp_path / "steps").mkdir(parents=True)
    (tmp_path / "templates" / "prompt-templates").mkdir(parents=True)
    (tmp_path / "audit").mkdir(parents=True)

    return tmp_path


@pytest.fixture
def minimal_step_file(tmp_project_root):
    """
    Create a minimal valid step file for testing.

    Returns:
        Path: Path to the created step file
    """
    step_file = tmp_project_root / "steps" / "01-01.json"

    # Minimal step file structure per architecture design v1.6.0
    step_data = {
        "task_id": "01-01",
        "project_id": "test-project",
        "workflow_type": "tdd_cycle",  # Default TDD workflow
        "state": {"status": "TODO", "started_at": None, "completed_at": None},
        "tdd_cycle": {
            "phase_execution_log": [
                {
                    "phase_number": i,
                    "phase_name": phase_name,
                    "status": "NOT_EXECUTED",
                    "outcome": None,
                    "blocked_by": None,
                }
                for i, phase_name in enumerate(
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
    """
    Mock DES orchestrator for testing command execution flow.

    This fixture will be implemented in DEVELOP wave.
    For now, returns NotImplemented to make tests fail naturally.
    """
    return NotImplemented
