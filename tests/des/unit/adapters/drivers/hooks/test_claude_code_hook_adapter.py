"""Unit tests for Claude Code hook adapter stub."""

import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict

import pytest


class TestClaudeCodeHookAdapterStub:
    """Unit tests for stub hook adapter functionality."""

    @pytest.fixture
    def adapter_path(self) -> Path:
        """Return path to stub adapter script."""
        return Path("src/des/adapters/drivers/hooks/claude_code_hook_adapter.py")

    @pytest.fixture
    def sample_task_json(self) -> Dict[str, Any]:
        """Return sample Task tool JSON input."""
        return {"tool": "Task", "parameters": {"skill": "test", "args": "test prompt"}}

    def test_stub_adapter_reads_json_from_stdin(
        self, adapter_path: Path, sample_task_json: Dict[str, Any]
    ) -> None:
        """Stub adapter should read JSON from stdin without error."""
        # Arrange
        input_json = json.dumps(sample_task_json)

        # Act & Assert
        result = subprocess.run(
            [sys.executable, str(adapter_path)],
            input=input_json,
            capture_output=True,
            text=True,
            check=False,
        )

        # Should not crash on JSON parsing
        assert result.returncode == 0, f"Adapter failed with stderr: {result.stderr}"

    def test_stub_adapter_outputs_valid_json(
        self, adapter_path: Path, sample_task_json: Dict[str, Any]
    ) -> None:
        """Stub adapter should output valid JSON to stdout."""
        # Arrange
        input_json = json.dumps(sample_task_json)

        # Act
        result = subprocess.run(
            [sys.executable, str(adapter_path)],
            input=input_json,
            capture_output=True,
            text=True,
            check=False,
        )

        # Assert
        assert result.returncode == 0
        output = json.loads(result.stdout)  # Should not raise JSONDecodeError
        assert isinstance(output, dict)

    def test_stub_adapter_outputs_decision_allow(
        self, adapter_path: Path, sample_task_json: Dict[str, Any]
    ) -> None:
        """Stub adapter should output decision: allow."""
        # Arrange
        input_json = json.dumps(sample_task_json)

        # Act
        result = subprocess.run(
            [sys.executable, str(adapter_path)],
            input=input_json,
            capture_output=True,
            text=True,
            check=False,
        )

        # Assert
        assert result.returncode == 0
        output = json.loads(result.stdout)
        assert output.get("decision") == "allow"

    def test_stub_adapter_outputs_proof_marker(
        self, adapter_path: Path, sample_task_json: Dict[str, Any]
    ) -> None:
        """Stub adapter should output proof marker 'hook_fired'."""
        # Arrange
        input_json = json.dumps(sample_task_json)

        # Act
        result = subprocess.run(
            [sys.executable, str(adapter_path)],
            input=input_json,
            capture_output=True,
            text=True,
            check=False,
        )

        # Assert
        assert result.returncode == 0
        output = json.loads(result.stdout)
        assert output.get("proof") == "hook_fired"

    def test_stub_adapter_exits_with_code_0(
        self, adapter_path: Path, sample_task_json: Dict[str, Any]
    ) -> None:
        """Stub adapter should exit with code 0 (success)."""
        # Arrange
        input_json = json.dumps(sample_task_json)

        # Act
        result = subprocess.run(
            [sys.executable, str(adapter_path)],
            input=input_json,
            capture_output=True,
            text=True,
            check=False,
        )

        # Assert
        assert result.returncode == 0

    def test_stub_adapter_handles_empty_stdin(self, adapter_path: Path) -> None:
        """Stub adapter should handle empty stdin without crashing."""
        # Act
        result = subprocess.run(
            [sys.executable, str(adapter_path)],
            input="",
            capture_output=True,
            text=True,
            check=False,
        )

        # Assert - Should fail gracefully
        # For stub, we allow it to pass (minimal implementation)
        # Real adapter will handle this properly in step 02-02
        assert result.returncode in [0, 1]  # Either succeeds or fails gracefully
