#!/usr/bin/env python3
"""
DES Hook Installer - Manages Claude Code hook lifecycle.

Merges DES hooks into .claude/settings.local.json, preserving existing hooks.
Uninstalls cleanly without traces or configuration corruption.
"""

import argparse
import json
import sys
from pathlib import Path


class DESHookInstaller:
    """Manages DES hook installation and uninstallation."""

    # Hook configuration templates
    DES_PRETOOLUSE_HOOK = {
        "matcher": "Task",
        "command": "python3 src/des/adapters/drivers/hooks/claude_code_hook_adapter.py pre-task",
    }

    DES_SUBAGENT_STOP_HOOK = {
        "command": "python3 src/des/adapters/drivers/hooks/claude_code_hook_adapter.py subagent-stop"
    }

    def __init__(self, config_dir: Path | None = None):
        """
        Initialize installer.

        Args:
            config_dir: Path to .claude directory (default: ~/.claude)
        """
        if config_dir is None:
            config_dir = Path.home() / ".claude"
        self.config_dir = Path(config_dir)
        self.settings_file = self.config_dir / "settings.local.json"

    def install(self) -> bool:
        """
        Install DES hooks into Claude Code configuration.

        Merges DES hooks into existing settings.local.json, preserving other hooks.
        Creates settings.local.json if it doesn't exist.
        Idempotent - detects and avoids duplicate installations.

        Returns:
            bool: True if installation succeeded, False otherwise
        """
        try:
            config = self._load_config()
            self._ensure_hooks_structure(config)

            if self._is_installed(config):
                print("DES hooks already installed")
                return True

            self._add_des_hooks(config)
            self._save_config(config)

            print("DES hooks installed successfully")
            print("Restart Claude Code session to activate hooks")
            return True

        except Exception as e:
            print(f"Installation failed: {e}", file=sys.stderr)
            return False

    def uninstall(self) -> bool:
        """
        Uninstall DES hooks from Claude Code configuration.

        Removes only DES hook entries, preserving all other hooks.
        Handles missing settings.local.json gracefully (no error).

        Returns:
            bool: True if uninstallation succeeded, False otherwise
        """
        try:
            if not self.settings_file.exists():
                print("DES hooks not installed (settings.local.json not found)")
                return True

            config = self._load_config()
            self._remove_des_hooks(config)
            self._save_config(config)

            print("DES hooks uninstalled successfully")
            return True

        except Exception as e:
            print(f"Uninstallation failed: {e}", file=sys.stderr)
            return False

    def status(self) -> bool:
        """
        Check DES hook installation status.

        Returns:
            bool: True if hooks are installed, False otherwise
        """
        try:
            if not self.settings_file.exists():
                print("DES hooks are not installed")
                return True

            config = self._load_config()
            installed = self._is_installed(config)

            if installed:
                print("DES hooks are installed")
            else:
                print("DES hooks are not installed")

            return True

        except Exception as e:
            print(f"Status check failed: {e}", file=sys.stderr)
            return False

    def _load_config(self) -> dict:
        """
        Load configuration from settings.local.json.

        Returns:
            dict: Configuration dictionary (empty if file doesn't exist)
        """
        if not self.settings_file.exists():
            return {}

        try:
            with open(self.settings_file, encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in {self.settings_file}: {e}")

    def _save_config(self, config: dict):
        """
        Save configuration to settings.local.json.

        Args:
            config: Configuration dictionary to save
        """
        # Ensure directory exists
        self.config_dir.mkdir(parents=True, exist_ok=True)

        # Write with proper formatting
        with open(self.settings_file, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2)
            f.write("\n")  # Add trailing newline

    def _is_installed(self, config: dict) -> bool:
        """
        Check if DES hooks are already installed.

        Args:
            config: Configuration dictionary

        Returns:
            bool: True if DES hooks are present
        """
        if "hooks" not in config:
            return False

        # Check for PreToolUse hook
        pre_hooks = config["hooks"].get("PreToolUse", [])
        has_pre = any(self._is_des_hook(h.get("command", "")) for h in pre_hooks)

        # Check for SubagentStop hook
        stop_hooks = config["hooks"].get("SubagentStop", [])
        has_stop = any(self._is_des_hook(h.get("command", "")) for h in stop_hooks)

        return has_pre and has_stop

    def _is_des_hook(self, command: str) -> bool:
        """
        Check if command is a DES hook.

        Args:
            command: Hook command string

        Returns:
            bool: True if command is a DES hook
        """
        return "claude_code_hook_adapter.py" in command

    def _ensure_hooks_structure(self, config: dict):
        """
        Ensure hooks structure exists in config.

        Args:
            config: Configuration dictionary to update
        """
        if "hooks" not in config:
            config["hooks"] = {}
        if "PreToolUse" not in config["hooks"]:
            config["hooks"]["PreToolUse"] = []
        if "SubagentStop" not in config["hooks"]:
            config["hooks"]["SubagentStop"] = []

    def _add_des_hooks(self, config: dict):
        """
        Add DES hooks to configuration.

        Args:
            config: Configuration dictionary to update
        """
        config["hooks"]["PreToolUse"].append(self.DES_PRETOOLUSE_HOOK)
        config["hooks"]["SubagentStop"].append(self.DES_SUBAGENT_STOP_HOOK)

    def _remove_des_hooks(self, config: dict):
        """
        Remove DES hooks from configuration.

        Args:
            config: Configuration dictionary to update
        """
        if "hooks" not in config:
            return

        if "PreToolUse" in config["hooks"]:
            config["hooks"]["PreToolUse"] = [
                h
                for h in config["hooks"]["PreToolUse"]
                if not self._is_des_hook(h.get("command", ""))
            ]

        if "SubagentStop" in config["hooks"]:
            config["hooks"]["SubagentStop"] = [
                h
                for h in config["hooks"]["SubagentStop"]
                if not self._is_des_hook(h.get("command", ""))
            ]


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Install or uninstall DES hooks for Claude Code"
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--install", action="store_true", help="Install DES hooks")
    group.add_argument("--uninstall", action="store_true", help="Uninstall DES hooks")
    group.add_argument(
        "--status", action="store_true", help="Check installation status"
    )
    parser.add_argument(
        "--config-dir", type=Path, help="Path to .claude directory (default: ~/.claude)"
    )

    args = parser.parse_args()

    installer = DESHookInstaller(config_dir=args.config_dir)

    if args.install:
        success = installer.install()
    elif args.uninstall:
        success = installer.uninstall()
    else:  # status
        success = installer.status()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
