"""
Pytest-BDD Configuration for DES Installation Bug Acceptance Tests.

This conftest.py at the acceptance level configures pytest-bdd
to discover feature files and step definitions.
"""

import pytest
from pathlib import Path

# Import fixtures from steps/conftest.py to make them available
from .steps.conftest import (
    project_root,
    claude_config_dir,
    installed_des_path,
    temp_claude_dir,
    temp_project_dir,
    test_logger,
    clean_settings_file,
    settings_with_duplicates,
    settings_with_mixed_hooks,
    settings_with_old_format_hook,
    install_context,
    des_plugin,
    clean_env,
    env_with_audit_log_dir,
    test_context,
)


# Re-export fixtures so they're discoverable
__all__ = [
    "project_root",
    "claude_config_dir",
    "installed_des_path",
    "temp_claude_dir",
    "temp_project_dir",
    "test_logger",
    "clean_settings_file",
    "settings_with_duplicates",
    "settings_with_mixed_hooks",
    "settings_with_old_format_hook",
    "install_context",
    "des_plugin",
    "clean_env",
    "env_with_audit_log_dir",
    "test_context",
]


def pytest_configure(config):
    """Register custom markers for DES bug tests."""
    config.addinivalue_line("markers", "bug_1: Bug 1 - Duplicate hooks on install")
    config.addinivalue_line("markers", "bug_2: Bug 2 - Audit logs location")
    config.addinivalue_line("markers", "bug_3: Bug 3 - Import paths")
    config.addinivalue_line("markers", "walking_skeleton: Walking skeleton tests")
    config.addinivalue_line("markers", "failing: Expected to fail until bug is fixed")
