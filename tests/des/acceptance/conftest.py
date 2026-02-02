"""
pytest configuration and fixtures for DES hook enforcement acceptance tests.

This module provides test fixtures following hexagonal architecture principles:
- Tests interact with DRIVING PORTS (DESOrchestrator, CLI adapters)
- Internal components accessed only through entry points
- FakeTimeProvider enables deterministic timestamp testing
"""

import json
import subprocess
from pathlib import Path
from typing import Dict, Any, List
import pytest
from datetime import datetime, timezone


class FakeTimeProvider:
    """Test double for TimeProvider enabling deterministic timestamp testing."""

    def __init__(self, fixed_time: datetime):
        self._fixed_time = fixed_time

    def now_utc(self) -> datetime:
        """Return fixed UTC timestamp for testing."""
        return self._fixed_time


class AuditLogReader:
    """Helper for reading and verifying audit log entries."""

    def __init__(self, audit_log_path: Path):
        self.audit_log_path = audit_log_path

    def get_all_entries(self) -> List[Dict[str, Any]]:
        """Read all audit log entries."""
        if not self.audit_log_path.exists():
            return []

        entries = []
        with open(self.audit_log_path, "r") as f:
            for line in f:
                line = line.strip()
                if line:
                    entries.append(json.loads(line))
        return entries

    def get_entries_by_type(self, event_type: str) -> List[Dict[str, Any]]:
        """Filter audit log entries by event type."""
        return [e for e in self.get_all_entries() if e.get("event_type") == event_type]

    def contains_event_type(self, event_type: str) -> bool:
        """Check if audit log contains at least one entry of given type."""
        return len(self.get_entries_by_type(event_type)) > 0

    def clear(self):
        """Clear audit log for test isolation."""
        if self.audit_log_path.exists():
            self.audit_log_path.unlink()


@pytest.fixture
def temp_home(tmp_path, monkeypatch):
    """Create temporary home directory for test isolation."""
    temp_home_dir = tmp_path / "home"
    temp_home_dir.mkdir()
    monkeypatch.setenv("HOME", str(temp_home_dir))
    return temp_home_dir


@pytest.fixture
def claude_config_dir(temp_home):
    """Create .claude directory structure."""
    claude_dir = temp_home / ".claude"
    claude_dir.mkdir()

    des_dir = claude_dir / "des"
    des_dir.mkdir()

    return claude_dir


@pytest.fixture
def settings_local_json_path(claude_config_dir):
    """Return path to .claude/settings.local.json."""
    return claude_config_dir / "settings.local.json"


@pytest.fixture
def des_config_path(claude_config_dir):
    """Return path to ~/.claude/des/config.yaml."""
    return claude_config_dir / "des" / "config.yaml"


@pytest.fixture
def audit_log_path(claude_config_dir):
    """Return path to audit log file."""
    logs_dir = claude_config_dir / "des" / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    return logs_dir / "audit.log"


@pytest.fixture
def audit_log_reader(audit_log_path):
    """Provide audit log reader helper."""
    return AuditLogReader(audit_log_path)


@pytest.fixture
def fixed_utc_time():
    """Provide fixed UTC timestamp for testing."""
    return datetime(2025, 10, 5, 14, 30, 0, tzinfo=timezone.utc)


@pytest.fixture
def fake_time_provider(fixed_utc_time):
    """Provide FakeTimeProvider for deterministic timestamp testing."""
    return FakeTimeProvider(fixed_utc_time)


@pytest.fixture
def clean_des_environment(temp_home, audit_log_reader):
    """Clean DES environment before each test."""
    # Clear audit log
    audit_log_reader.clear()

    # Clean up any existing config files
    des_config = temp_home / ".claude" / "des" / "config.yaml"
    if des_config.exists():
        des_config.unlink()

    settings_local = temp_home / ".claude" / "settings.local.json"
    if settings_local.exists():
        settings_local.unlink()

    yield

    # Cleanup after test
    audit_log_reader.clear()


@pytest.fixture
def enable_audit_logging(des_config_path):
    """Configure audit logging to be enabled."""
    des_config_path.parent.mkdir(parents=True, exist_ok=True)
    config_content = """# DES Configuration
audit_logging_enabled: true  # Enable comprehensive audit trail
"""
    des_config_path.write_text(config_content)


@pytest.fixture
def disable_audit_logging(des_config_path):
    """Configure audit logging to be disabled."""
    des_config_path.parent.mkdir(parents=True, exist_ok=True)
    config_content = """# DES Configuration
audit_logging_enabled: false  # Disable audit logging
"""
    des_config_path.write_text(config_content)


@pytest.fixture
def existing_hooks_in_settings(settings_local_json_path):
    """Create existing non-DES hooks in settings.local.json."""
    existing_config = {
        "hooks": {
            "PreToolUse": [
                {"matcher": "SomeOtherTool", "command": "python3 /some/other/hook.py"}
            ]
        }
    }
    settings_local_json_path.write_text(json.dumps(existing_config, indent=2))


@pytest.fixture
def step_file_complete(tmp_path):
    """Create step file with all phases complete."""
    step_file = tmp_path / "step-01-01.json"
    step_data = {
        "step_id": "01-01",
        "description": "Test step",
        "phases": {
            "RED": {"status": "PASSED"},
            "GREEN": {"status": "PASSED"},
            "REFACTOR": {"status": "PASSED"},
        },
    }
    step_file.write_text(json.dumps(step_data, indent=2))
    return step_file


@pytest.fixture
def step_file_incomplete(tmp_path):
    """Create step file with incomplete phases."""
    step_file = tmp_path / "step-01-01.json"
    step_data = {
        "step_id": "01-01",
        "description": "Test step",
        "phases": {"RED": {"status": "PASSED"}, "GREEN": {"status": "IN_PROGRESS"}},
    }
    step_file.write_text(json.dumps(step_data, indent=2))
    return step_file


@pytest.fixture
def valid_task_json():
    """Provide valid Task tool JSON for hook adapter testing."""
    return {
        "tool": "Task",
        "tool_input": {"prompt": "/nw:execute @developer step-01-01.json"},
    }


@pytest.fixture
def invalid_task_json():
    """Provide invalid Task tool JSON that should be blocked."""
    return {
        "tool": "Task",
        "tool_input": {"prompt": "/nw:execute step-missing-phases.json"},
    }


@pytest.fixture
def hook_adapter_cli():
    """Return path to hook adapter CLI script."""
    # Adjust path based on actual project structure
    return Path("src/des/adapters/drivers/hooks/claude_code_hook_adapter.py")


@pytest.fixture
def installer_cli():
    """Return path to installer CLI script."""
    return Path("scripts/install/install_des_hooks.py")


def run_cli_command(
    cli_path: Path, args: List[str], stdin_data: str = None
) -> subprocess.CompletedProcess:
    """
    Helper to run CLI commands with stdin and capture output.

    Args:
        cli_path: Path to CLI script
        args: Command arguments
        stdin_data: Optional stdin data as string

    Returns:
        CompletedProcess with returncode, stdout, stderr
    """
    cmd = ["python3", str(cli_path)] + args

    result = subprocess.run(
        cmd,
        input=stdin_data.encode() if stdin_data else None,
        capture_output=True,
        text=False,
    )

    return result


@pytest.fixture
def cli_runner():
    """Provide CLI command runner helper."""
    return run_cli_command


@pytest.fixture
def context():
    """Provide test context dictionary for sharing state between steps."""
    return {}
