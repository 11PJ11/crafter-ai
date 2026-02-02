"""
Test Data Registry for modern_CLI_installer Epic
=================================================

Standardized test data values from the shared artifacts registry.
All acceptance tests use these values for consistency.

Source: docs/ux/modern-cli-installer/shared-artifacts-registry-installer.md
"""

from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Optional


@dataclass(frozen=True)
class TestArtifacts:
    """
    Standardized test artifacts for all journeys.

    These values must match the shared artifacts registry to ensure
    horizontal consistency across journeys.
    """

    # Version artifacts
    version: str = "1.3.0"
    candidate_version: str = "1.3.0-dev-20260201-001"
    base_version: str = "1.2.0"  # Previous version for bump scenarios

    # Wheel artifacts
    wheel_filename: str = "nwave-1.3.0-dev-20260201-001-py3-none-any.whl"
    wheel_path: str = "dist/nwave-1.3.0-dev-20260201-001-py3-none-any.whl"

    # Install path artifacts
    install_path: str = "~/.claude/agents/nw/"
    install_path_expanded: str = "/Users/developer/.claude/agents/nw/"
    backup_path: str = "~/.claude/backups/nwave-20260201-143025/"

    # Component counts
    agent_count: int = 47
    command_count: int = 23
    template_count: int = 12

    # Build metadata
    build_date: str = "20260201"
    build_sequence: str = "001"
    build_timestamp: str = "2026-02-01 14:30:25"
    install_timestamp: str = "2026-02-01 14:30:47"

    # Tool versions
    python_version: str = "3.12.1"
    python_version_old: str = "3.8.10"
    build_package_version: str = "1.2.1"
    pipx_version: str = "1.4.3"

    # Branch info
    branch: str = "installer"

    # File counts
    source_file_count: int = 127


@dataclass(frozen=True)
class PreflightCheckData:
    """Test data for pre-flight check scenarios."""

    # Python version check
    python_pass_display: str = "Python version [check] 3.12.1 (3.10+ OK)"
    python_fail_display: str = "Python version [x] 3.8.10 (3.10+ required)"

    # Build package check
    build_pass_display: str = "build package [check] v1.2.1 installed"
    build_fail_display: str = "Pre-flight check failed: build package missing"
    build_fix_prompt: str = "Install it now? [Y/n]"
    build_fix_command: str = "pip install build"

    # Pyproject.toml check
    pyproject_pass_display: str = "pyproject.toml [check] Valid, v1.3.0"
    pyproject_not_found: str = "pyproject.toml not found"
    pyproject_invalid: str = "pyproject.toml invalid"

    # Source directory check
    source_pass_display: str = "Source directory [check] nWave/ found"
    source_fail_display: str = "nWave/ directory not found"

    # Dist directory check
    dist_pass_display: str = "dist/ directory [check] Writable"

    # Pipx check
    pipx_pass_display: str = "pipx available [check] v1.4.3 installed"
    pipx_fail_display: str = "pipx not installed"
    pipx_fix_instructions: str = "pip install pipx && pipx ensurepath"

    # Claude directory check
    claude_dir_pass_display: str = "~/.claude writable [check] Permissions OK"
    claude_dir_fail_display: str = "Cannot write to ~/.claude/"

    # Wheel check
    wheel_pass_display: str = "Wheel exists [check] dist/nwave-1.3.0-dev-20260201-001-py3-none-any.whl"
    wheel_fail_display: str = "No wheel found in dist/"


@dataclass(frozen=True)
class DoctorCheckData:
    """Test data for doctor health check scenarios."""

    # Core installation
    core_pass: str = "Core [check] Installed"

    # Agent files
    agents_pass: str = "Agent files [check] 47 OK"
    agents_fail: str = "Agent files [x] 0 found"

    # Command files
    commands_pass: str = "Command files [check] 23 OK"

    # Template files
    templates_pass: str = "Template files [check] 12 OK"

    # Config
    config_pass: str = "Config valid [check] nwave.yaml OK"

    # Permissions
    permissions_pass: str = "Permissions [check] All accessible"

    # Version
    version_pass: str = "Version match [check] 1.3.0-dev-20260201-001"
    version_mismatch: str = "Version match [x] mismatch"

    # Health status
    status_healthy: str = "HEALTHY"
    status_degraded: str = "DEGRADED"
    status_unhealthy: str = "UNHEALTHY"


@dataclass(frozen=True)
class ReleaseReadinessData:
    """Test data for release readiness validation."""

    # Twine check
    twine_pass: str = "twine check [check] Passed"
    twine_fail: str = "twine check [x] Invalid metadata"

    # Metadata
    metadata_pass: str = "Metadata complete [check] All fields set"

    # Entry points
    entry_points_pass: str = "Entry points [check] nw CLI defined"
    entry_points_fail: str = "Entry points [x] nw CLI not found"

    # Changelog
    changelog_pass: str = "CHANGELOG exists [check] Recent entry OK"
    changelog_warn: str = "CHANGELOG exists [warn] No recent entry"

    # Version format
    version_format_pass: str = "Version format [check] PEP 440 valid"

    # License
    license_pass: str = "License bundled [check] LICENSE in wheel"

    # README
    readme_pass: str = "README bundled [check] README.md OK"

    # Status
    status_ready: str = "READY FOR PYPI"
    status_warnings: str = "WARNINGS (non-blocking)"
    status_failed: str = "FAILED"


@dataclass(frozen=True)
class BuildPhaseData:
    """Test data for build process phases."""

    clean_pass: str = "Cleaning dist/ [check] Removed old"
    clean_empty: str = "Cleaning dist/ [check] Already clean"

    process_pass: str = "Processing source [check] 127 files"

    backend_pass: str = "Running build backend [check] Complete"
    backend_fail: str = "Running build backend [x] Failed"


@dataclass(frozen=True)
class WheelValidationData:
    """Test data for wheel validation."""

    format_pass: str = "Wheel format [check]"
    metadata_pass: str = "Metadata present [check]"
    entry_points_pass: str = "Entry points [check] nw CLI defined"
    agents_pass: str = "Agents bundled [check] 47"
    commands_pass: str = "Commands bundled [check] 23"
    templates_pass: str = "Templates bundled [check] 12"
    pipx_compatible_pass: str = "pipx compatible [check] Verified"

    final_status_pass: str = "Wheel validation passed!"
    final_status_fail: str = "Wheel validation failed!"


@dataclass(frozen=True)
class VersionBumpData:
    """Test data for version bumping scenarios."""

    # Bump types
    bump_major: str = "MAJOR"
    bump_minor: str = "MINOR"
    bump_patch: str = "PATCH"

    # Commit patterns
    feat_commit: str = "feat: add Luna agent"
    fix_commit: str = "fix: correct typo in config"
    breaking_commit: str = "BREAKING CHANGE: redesign API"

    # Version calculations
    from_1_2_0_minor: str = "1.3.0"
    from_1_2_0_major: str = "2.0.0"
    from_1_2_0_patch: str = "1.2.1"

    # Warnings
    no_commits_warning: str = "No commits since last tag"
    force_rejected: str = "Force version rejected"
    force_rejected_reason: str = "Force version must be higher than current"


# Singleton instances for easy import
ARTIFACTS = TestArtifacts()
PREFLIGHT = PreflightCheckData()
DOCTOR = DoctorCheckData()
RELEASE_READINESS = ReleaseReadinessData()
BUILD_PHASES = BuildPhaseData()
WHEEL_VALIDATION = WheelValidationData()
VERSION_BUMP = VersionBumpData()


# Helper functions for test setup
def get_wheel_path_for_version(version: str, date_str: str = "20260201", seq: str = "001") -> str:
    """Generate wheel path for a given version."""
    candidate = f"{version}-dev-{date_str}-{seq}"
    return f"dist/nwave-{candidate}-py3-none-any.whl"


def get_candidate_version(base_version: str, date_str: str = "20260201", seq: str = "001") -> str:
    """Generate candidate version string."""
    return f"{base_version}-dev-{date_str}-{seq}"


def get_backup_path(date_str: str = "20260201", time_str: str = "143025") -> str:
    """Generate backup path with timestamp."""
    return f"~/.claude/backups/nwave-{date_str}-{time_str}/"
