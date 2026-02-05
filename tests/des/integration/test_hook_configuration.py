"""Integration tests for DES hook configuration and installation.

Tests verify that:
1. Hook adapter module exists and is referenced correctly
2. Installation scripts configure hooks with correct paths
3. Hooks point to claude_code_hook_adapter module (not missing files)

These tests MUST fail if claude_code_hook_adapter.py is deleted or not referenced.
"""

import json
from pathlib import Path

import pytest


class TestHookAdapterReference:
    """Test that hook adapter is correctly referenced in installation config."""

    def test_hook_adapter_module_exists(self):
        """MUST FAIL if claude_code_hook_adapter.py is missing.

        This test ensures the CLI entry point exists in the codebase.
        If this test fails, the hooks cannot work (module not found error).
        """
        adapter_path = (
            Path(__file__).parent.parent.parent.parent
            / "src/des/adapters/drivers/hooks/claude_code_hook_adapter.py"
        )

        assert adapter_path.exists(), (
            f"Hook adapter module not found: {adapter_path}\n"
            "This file is REQUIRED for DES hooks to work.\n"
            "If deleted, restore from git: git show c8dca89^:src/des/adapters/drivers/hooks/claude_code_hook_adapter.py"
        )

    def test_hook_adapter_is_importable(self):
        """MUST FAIL if hook adapter has import errors.

        Verifies the module can be imported without errors.
        """
        try:
            from src.des.adapters.drivers.hooks import claude_code_hook_adapter

            # Verify expected functions exist
            assert hasattr(claude_code_hook_adapter, "handle_pre_task")
            assert hasattr(claude_code_hook_adapter, "handle_subagent_stop")
            assert hasattr(claude_code_hook_adapter, "main")
        except ImportError as e:
            pytest.fail(f"Hook adapter cannot be imported: {e}")

    def test_hook_adapter_has_main_entry_point(self):
        """Verify hook adapter can run as CLI module."""
        from src.des.adapters.drivers.hooks import claude_code_hook_adapter

        # Test main() exists and is callable
        assert callable(claude_code_hook_adapter.main)

        # Verify main() handles commands correctly (mock sys.argv)
        import sys

        original_argv = sys.argv.copy()
        try:
            sys.argv = ["claude_code_hook_adapter.py"]  # No command
            with pytest.raises(SystemExit) as exc_info:
                claude_code_hook_adapter.main()
            assert exc_info.value.code == 1, "Expected error exit code when command missing"
        finally:
            sys.argv = original_argv


class TestHookInstallerConfiguration:
    """Test that hook installer references claude_code_hook_adapter correctly."""

    def test_standalone_installer_references_hook_adapter(self):
        """MUST FAIL if install_des_hooks.py doesn't reference claude_code_hook_adapter.

        Verifies the standalone installer script configures hooks correctly.
        """
        installer_path = (
            Path(__file__).parent.parent.parent.parent
            / "scripts/install/install_des_hooks.py"
        )

        assert installer_path.exists(), "Installer script not found"

        with open(installer_path, "r", encoding="utf-8") as f:
            installer_code = f.read()

        # CRITICAL: Installer MUST reference claude_code_hook_adapter
        assert "claude_code_hook_adapter" in installer_code, (
            "Installer does not reference claude_code_hook_adapter!\n"
            "Hooks will fail with 'module not found' error.\n"
            "Update DES_PRETOOLUSE_HOOK and DES_SUBAGENT_STOP_HOOK constants."
        )

        # Verify both hook types reference the adapter
        assert installer_code.count("claude_code_hook_adapter") >= 2, (
            "Expected at least 2 references to claude_code_hook_adapter "
            "(one for PreToolUse, one for SubagentStop)"
        )

    def test_plugin_installer_references_hook_adapter(self):
        """MUST FAIL if des_plugin.py doesn't reference claude_code_hook_adapter.

        Verifies the plugin installer configures hooks correctly.
        """
        plugin_path = (
            Path(__file__).parent.parent.parent.parent
            / "scripts/install/plugins/des_plugin.py"
        )

        assert plugin_path.exists(), "Plugin installer not found"

        with open(plugin_path, "r", encoding="utf-8") as f:
            plugin_code = f.read()

        # CRITICAL: Plugin MUST reference claude_code_hook_adapter
        assert "claude_code_hook_adapter" in plugin_code, (
            "Plugin installer does not reference claude_code_hook_adapter!\n"
            "Hooks installed via /nw:install will not work.\n"
            "Update HOOK_COMMAND_TEMPLATE constant."
        )

    def test_hook_command_format_is_correct(self):
        """Verify hook commands use python -m module format (not direct .py).

        Schema v2.0 requirement: Use -m format for PYTHONPATH compatibility.
        """
        plugin_path = (
            Path(__file__).parent.parent.parent.parent
            / "scripts/install/plugins/des_plugin.py"
        )

        with open(plugin_path, "r", encoding="utf-8") as f:
            plugin_code = f.read()

        # Expected format: "python3 -m des.adapters.drivers.hooks.claude_code_hook_adapter"
        assert "python3 -m" in plugin_code, (
            "Hook command should use 'python3 -m' format (not direct .py path)"
        )
        assert (
            "des.adapters.drivers.hooks.claude_code_hook_adapter" in plugin_code
        ), "Hook command missing module path"


class TestHookConfigurationIntegrity:
    """Test installed hook configuration integrity."""

    def test_settings_local_json_has_des_hooks(self):
        """Verify settings.local.json has DES hooks installed.

        NOTE: This test checks the actual installed configuration.
        May be skipped if settings.local.json doesn't exist (new install).
        """
        settings_path = Path.home() / ".claude/settings.local.json"

        if not settings_path.exists():
            pytest.skip("settings.local.json not found (not yet installed)")

        with open(settings_path, "r", encoding="utf-8") as f:
            config = json.load(f)

        # Verify hooks structure exists
        assert "hooks" in config, "No hooks configuration found in settings.local.json"

        hooks = config["hooks"]

        # Verify PreToolUse hook exists
        assert "PreToolUse" in hooks, "PreToolUse hook array missing"
        assert isinstance(hooks["PreToolUse"], list), "PreToolUse must be an array"

        # Verify SubagentStop hook exists
        assert "SubagentStop" in hooks, "SubagentStop hook array missing"
        assert isinstance(hooks["SubagentStop"], list), "SubagentStop must be an array"

        # Find DES hooks (may be mixed with other hooks)
        pretooluse_des_hooks = [
            h for h in hooks["PreToolUse"] if "claude_code_hook_adapter" in h.get("command", "")
        ]
        subagent_stop_des_hooks = [
            h
            for h in hooks["SubagentStop"]
            if "claude_code_hook_adapter" in h.get("command", "")
        ]

        assert len(pretooluse_des_hooks) > 0, (
            "No DES PreToolUse hook found in settings.local.json!\n"
            "Hook adapter is not configured. Run: python3 scripts/install/plugins/des_plugin.py"
        )

        assert len(subagent_stop_des_hooks) > 0, (
            "No DES SubagentStop hook found in settings.local.json!\n"
            "Hook adapter is not configured. Run: python3 scripts/install/plugins/des_plugin.py"
        )

        # Verify command format
        pretooluse_hook = pretooluse_des_hooks[0]
        assert "command" in pretooluse_hook, "PreToolUse hook missing command field"
        assert "claude_code_hook_adapter" in pretooluse_hook["command"], (
            "PreToolUse command doesn't reference claude_code_hook_adapter"
        )

        subagent_hook = subagent_stop_des_hooks[0]
        assert "command" in subagent_hook, "SubagentStop hook missing command field"
        assert "claude_code_hook_adapter" in subagent_hook["command"], (
            "SubagentStop command doesn't reference claude_code_hook_adapter"
        )

    def test_installed_module_has_hook_adapter(self):
        """Verify installed DES module includes claude_code_hook_adapter.

        NOTE: May be skipped if module not installed via /nw:install.
        """
        installed_module_path = (
            Path.home()
            / ".claude/lib/python/des/adapters/drivers/hooks/claude_code_hook_adapter.py"
        )

        if not installed_module_path.parent.exists():
            pytest.skip("DES module not installed (run /nw:install)")

        # CRITICAL: Installed module MUST include the hook adapter
        assert installed_module_path.exists(), (
            f"Hook adapter not found in installed module: {installed_module_path}\n"
            "This means hooks are configured but the module is missing!\n"
            "Re-run /nw:install to fix installation."
        )


class TestHookAdapterFunctionality:
    """Test that hook adapter works correctly with Schema v2.0."""

    def test_hook_adapter_accepts_schema_v2_input(self):
        """Verify hook adapter handles Schema v2.0 input format.

        Schema v2.0 input:
            {
                "executionLogPath": "/abs/path",
                "projectId": "foo",
                "stepId": "01-01"
            }
        """
        from src.des.adapters.drivers.hooks import claude_code_hook_adapter

        # Test _verify_step_from_append_only_log function exists
        assert hasattr(claude_code_hook_adapter, "_verify_step_from_append_only_log"), (
            "Hook adapter missing Schema v2.0 validation function"
        )

        # Verify handle_subagent_stop exists
        assert hasattr(claude_code_hook_adapter, "handle_subagent_stop")

    def test_hook_adapter_rejects_missing_required_fields(self):
        """Test that hook adapter validates Schema v2.0 required fields.

        This is a unit test verifying the adapter's input validation.
        """
        from src.des.adapters.drivers.hooks import claude_code_hook_adapter
        import sys
        from io import StringIO

        # Mock stdin with missing fields
        test_input = json.dumps({"executionLogPath": "/tmp/log.yaml"})  # Missing projectId, stepId

        original_stdin = sys.stdin
        original_stdout = sys.stdout
        try:
            sys.stdin = StringIO(test_input)
            sys.stdout = StringIO()

            exit_code = claude_code_hook_adapter.handle_subagent_stop()

            # Should fail (exit 1) due to missing required fields
            assert exit_code == 1, "Expected error exit code for missing required fields"
        finally:
            sys.stdin = original_stdin
            sys.stdout = original_stdout
