"""Unit tests for DES hook installer."""

import json
import subprocess


class TestInstallDESHooks:
    """Test installer merges DES hooks into settings.local.json."""

    def test_install_merges_hooks_into_existing_config(self, tmp_path):
        """Install merges DES hooks into existing .claude/settings.local.json."""
        # Given: existing .claude/settings.local.json with non-DES hooks
        claude_dir = tmp_path / ".claude"
        claude_dir.mkdir()
        settings_file = claude_dir / "settings.local.json"

        existing_config = {
            "hooks": {
                "PreToolUse": [{"matcher": "OtherTool", "command": "other_command"}],
                "SubagentStop": [{"command": "other_stop_command"}],
            }
        }
        settings_file.write_text(json.dumps(existing_config, indent=2))

        # When: run installer
        result = subprocess.run(
            [
                "python3",
                "scripts/install/install_des_hooks.py",
                "--install",
                "--config-dir",
                str(claude_dir),
            ],
            capture_output=True,
            text=True,
        )

        # Then: installer succeeds
        assert result.returncode == 0, f"Installer failed: {result.stderr}"

        # And: DES hooks are added
        config = json.loads(settings_file.read_text())
        assert "hooks" in config
        assert "PreToolUse" in config["hooks"]
        assert "SubagentStop" in config["hooks"]

        # And: DES PreToolUse hook exists
        des_pre_hook = next(
            (
                h
                for h in config["hooks"]["PreToolUse"]
                if "claude_code_hook_adapter.py pre-task" in h.get("command", "")
            ),
            None,
        )
        assert des_pre_hook is not None, "DES PreToolUse hook not found"
        assert des_pre_hook["matcher"] == "Task"

        # And: DES SubagentStop hook exists
        des_stop_hook = next(
            (
                h
                for h in config["hooks"]["SubagentStop"]
                if "claude_code_hook_adapter.py subagent-stop" in h.get("command", "")
            ),
            None,
        )
        assert des_stop_hook is not None, "DES SubagentStop hook not found"

        # And: existing hooks preserved
        assert len(config["hooks"]["PreToolUse"]) == 2
        assert len(config["hooks"]["SubagentStop"]) == 2
        other_pre = next(
            h for h in config["hooks"]["PreToolUse"] if h.get("matcher") == "OtherTool"
        )
        assert other_pre["command"] == "other_command"

    def test_install_creates_settings_file_if_missing(self, tmp_path):
        """Install creates .claude/settings.local.json if it doesn't exist."""
        # Given: .claude directory exists but settings.local.json doesn't
        claude_dir = tmp_path / ".claude"
        claude_dir.mkdir()
        settings_file = claude_dir / "settings.local.json"

        # When: run installer
        result = subprocess.run(
            [
                "python3",
                "scripts/install/install_des_hooks.py",
                "--install",
                "--config-dir",
                str(claude_dir),
            ],
            capture_output=True,
            text=True,
        )

        # Then: installer succeeds
        assert result.returncode == 0, f"Installer failed: {result.stderr}"

        # And: settings file created
        assert settings_file.exists()

        # And: DES hooks configured
        config = json.loads(settings_file.read_text())
        assert "hooks" in config
        assert len(config["hooks"]["PreToolUse"]) == 1
        assert len(config["hooks"]["SubagentStop"]) == 1

    def test_install_is_idempotent(self, tmp_path):
        """Install detects existing DES hooks and doesn't duplicate."""
        # Given: DES hooks already installed
        claude_dir = tmp_path / ".claude"
        claude_dir.mkdir()
        settings_file = claude_dir / "settings.local.json"

        existing_config = {
            "hooks": {
                "PreToolUse": [
                    {
                        "matcher": "Task",
                        "command": "python3 src/des/adapters/drivers/hooks/claude_code_hook_adapter.py pre-task",
                    }
                ],
                "SubagentStop": [
                    {
                        "command": "python3 src/des/adapters/drivers/hooks/claude_code_hook_adapter.py subagent-stop"
                    }
                ],
            }
        }
        settings_file.write_text(json.dumps(existing_config, indent=2))

        # When: run installer again
        result = subprocess.run(
            [
                "python3",
                "scripts/install/install_des_hooks.py",
                "--install",
                "--config-dir",
                str(claude_dir),
            ],
            capture_output=True,
            text=True,
        )

        # Then: installer succeeds
        assert result.returncode == 0, f"Installer failed: {result.stderr}"

        # And: no duplicate hooks created
        config = json.loads(settings_file.read_text())
        assert len(config["hooks"]["PreToolUse"]) == 1
        assert len(config["hooks"]["SubagentStop"]) == 1

    def test_install_configures_pretooluse_hook_correctly(self, tmp_path):
        """Install configures PreToolUse hook with Task matcher and python3 command."""
        # Given: empty config
        claude_dir = tmp_path / ".claude"
        claude_dir.mkdir()

        # When: run installer
        subprocess.run(
            [
                "python3",
                "scripts/install/install_des_hooks.py",
                "--install",
                "--config-dir",
                str(claude_dir),
            ],
            capture_output=True,
            text=True,
        )

        # Then: PreToolUse hook configured correctly
        config = json.loads((claude_dir / "settings.local.json").read_text())
        pre_hook = config["hooks"]["PreToolUse"][0]

        assert pre_hook["matcher"] == "Task"
        assert "python3" in pre_hook["command"]
        assert "claude_code_hook_adapter.py" in pre_hook["command"]
        assert "pre-task" in pre_hook["command"]
        assert "bash" not in pre_hook["command"]
        assert "sh" not in pre_hook["command"]

    def test_install_configures_agentstop_hook_correctly(self, tmp_path):
        """Install configures SubagentStop hook with python3 command."""
        # Given: empty config
        claude_dir = tmp_path / ".claude"
        claude_dir.mkdir()

        # When: run installer
        subprocess.run(
            [
                "python3",
                "scripts/install/install_des_hooks.py",
                "--install",
                "--config-dir",
                str(claude_dir),
            ],
            capture_output=True,
            text=True,
        )

        # Then: SubagentStop hook configured correctly
        config = json.loads((claude_dir / "settings.local.json").read_text())
        stop_hook = config["hooks"]["SubagentStop"][0]

        assert "python3" in stop_hook["command"]
        assert "claude_code_hook_adapter.py" in stop_hook["command"]
        assert "subagent-stop" in stop_hook["command"]
        assert "bash" not in stop_hook["command"]
        assert "sh" not in stop_hook["command"]

    def test_uninstall_removes_only_des_hooks(self, tmp_path):
        """Uninstall removes only DES hooks, preserves others."""
        # Given: settings with DES and non-DES hooks
        claude_dir = tmp_path / ".claude"
        claude_dir.mkdir()
        settings_file = claude_dir / "settings.local.json"

        existing_config = {
            "hooks": {
                "PreToolUse": [
                    {"matcher": "OtherTool", "command": "other_command"},
                    {
                        "matcher": "Task",
                        "command": "python3 src/des/adapters/drivers/hooks/claude_code_hook_adapter.py pre-task",
                    },
                ],
                "SubagentStop": [
                    {"command": "other_stop_command"},
                    {
                        "command": "python3 src/des/adapters/drivers/hooks/claude_code_hook_adapter.py subagent-stop"
                    },
                ],
            }
        }
        settings_file.write_text(json.dumps(existing_config, indent=2))

        # When: run uninstaller
        result = subprocess.run(
            [
                "python3",
                "scripts/install/install_des_hooks.py",
                "--uninstall",
                "--config-dir",
                str(claude_dir),
            ],
            capture_output=True,
            text=True,
        )

        # Then: uninstaller succeeds
        assert result.returncode == 0, f"Uninstaller failed: {result.stderr}"

        # And: DES hooks removed
        config = json.loads(settings_file.read_text())
        des_pre = [
            h
            for h in config["hooks"]["PreToolUse"]
            if "claude_code_hook_adapter.py" in h.get("command", "")
        ]
        des_stop = [
            h
            for h in config["hooks"]["SubagentStop"]
            if "claude_code_hook_adapter.py" in h.get("command", "")
        ]
        assert len(des_pre) == 0
        assert len(des_stop) == 0

        # And: other hooks preserved
        assert len(config["hooks"]["PreToolUse"]) == 1
        assert len(config["hooks"]["SubagentStop"]) == 1
        assert config["hooks"]["PreToolUse"][0]["matcher"] == "OtherTool"

    def test_uninstall_handles_missing_file_gracefully(self, tmp_path):
        """Uninstall succeeds when settings.local.json doesn't exist."""
        # Given: .claude directory exists but settings file doesn't
        claude_dir = tmp_path / ".claude"
        claude_dir.mkdir()

        # When: run uninstaller
        result = subprocess.run(
            [
                "python3",
                "scripts/install/install_des_hooks.py",
                "--uninstall",
                "--config-dir",
                str(claude_dir),
            ],
            capture_output=True,
            text=True,
        )

        # Then: uninstaller succeeds without error
        assert result.returncode == 0, f"Uninstaller failed: {result.stderr}"

    def test_merged_config_is_valid_json(self, tmp_path):
        """Merged configuration validates as valid JSON."""
        # Given: empty config
        claude_dir = tmp_path / ".claude"
        claude_dir.mkdir()

        # When: run installer
        subprocess.run(
            [
                "python3",
                "scripts/install/install_des_hooks.py",
                "--install",
                "--config-dir",
                str(claude_dir),
            ],
            capture_output=True,
            text=True,
        )

        # Then: config file is valid JSON
        settings_file = claude_dir / "settings.local.json"
        config_text = settings_file.read_text()

        # Should not raise exception
        config = json.loads(config_text)
        assert isinstance(config, dict)

    def test_status_detects_installed_state(self, tmp_path):
        """Status command detects whether hooks are installed."""
        # Given: DES hooks installed
        claude_dir = tmp_path / ".claude"
        claude_dir.mkdir()
        settings_file = claude_dir / "settings.local.json"

        config = {
            "hooks": {
                "PreToolUse": [
                    {
                        "matcher": "Task",
                        "command": "python3 src/des/adapters/drivers/hooks/claude_code_hook_adapter.py pre-task",
                    }
                ],
                "SubagentStop": [
                    {
                        "command": "python3 src/des/adapters/drivers/hooks/claude_code_hook_adapter.py subagent-stop"
                    }
                ],
            }
        }
        settings_file.write_text(json.dumps(config, indent=2))

        # When: run status command
        result = subprocess.run(
            [
                "python3",
                "scripts/install/install_des_hooks.py",
                "--status",
                "--config-dir",
                str(claude_dir),
            ],
            capture_output=True,
            text=True,
        )

        # Then: status reports installed
        assert result.returncode == 0
        assert "installed" in result.stdout.lower()

    def test_status_detects_not_installed_state(self, tmp_path):
        """Status command detects when hooks are not installed."""
        # Given: no DES hooks
        claude_dir = tmp_path / ".claude"
        claude_dir.mkdir()

        # When: run status command
        result = subprocess.run(
            [
                "python3",
                "scripts/install/install_des_hooks.py",
                "--status",
                "--config-dir",
                str(claude_dir),
            ],
            capture_output=True,
            text=True,
        )

        # Then: status reports not installed
        assert result.returncode == 0
        assert "not installed" in result.stdout.lower()
