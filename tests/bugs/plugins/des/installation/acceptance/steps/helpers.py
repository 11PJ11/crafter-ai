"""
Helper functions for DES Installation Bug Acceptance Tests.

These utilities are shared across step definition modules.
Separated to avoid circular imports with conftest.py.
"""

import json
from pathlib import Path


def count_des_hooks(settings_file: Path, hook_type: str) -> int:
    """
    Count DES hooks in settings.local.json.

    Args:
        settings_file: Path to settings.local.json
        hook_type: "PreToolUse" or "SubagentStop"

    Returns:
        Number of DES hooks found
    """
    if not settings_file.exists():
        return 0

    with open(settings_file) as f:
        config = json.load(f)

    hooks = config.get("hooks", {}).get(hook_type, [])
    des_hooks = [h for h in hooks if is_des_hook(h.get("command", ""))]
    return len(des_hooks)


def is_des_hook(command: str) -> bool:
    """
    Check if a command is a DES hook command.

    Detects both old and new formats:
    - Old: python3 src/des/.../claude_code_hook_adapter.py
    - New: python3 -m des.adapters.drivers.hooks.claude_code_hook_adapter
    """
    return "claude_code_hook_adapter" in command


def scan_for_bad_imports(des_path: Path) -> list[str]:
    """
    Scan installed DES directory for bad import patterns.

    Returns list of files containing "from src.des" or "import src.des".
    """
    bad_files = []
    if not des_path.exists():
        return bad_files

    for py_file in des_path.rglob("*.py"):
        try:
            content = py_file.read_text()
            if "from src.des" in content or "import src.des" in content:
                bad_files.append(str(py_file))
        except Exception:
            pass

    return bad_files
