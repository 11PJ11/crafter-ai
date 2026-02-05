"""Tests for deployment pre-flight checks.

These checks validate that the IDE bundle exists in dist/ide/ before
the install phase begins. If dist/ide/ is missing or empty, the check
returns a BLOCKING failure with remediation to run 'forge build'.

Unit test strategy: Each test instantiates IdeBundleExistsCheck, calls
its execute() method, and asserts the CheckResult outcome.

All tests use the InMemoryFileSystemAdapter to avoid depending on actual
filesystem state. No actual file system operations, subprocess calls, or
external dependencies.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from crafter_ai.installer.checks.ide_bundle_exists_check import IdeBundleExistsCheck
from crafter_ai.installer.domain.check_result import CheckSeverity
from crafter_ai.installer.domain.ide_bundle_constants import (
    EXPECTED_AGENT_COUNT,
    EXPECTED_COMMAND_COUNT,
    EXPECTED_SCRIPT_COUNT,
    EXPECTED_TEMPLATE_COUNT,
)
from tests.installer.conftest import InMemoryFileSystemAdapter


# ═══════════════════════════════════════════════════════════════════════════════
# Fixtures
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.fixture
def mock_filesystem() -> InMemoryFileSystemAdapter:
    """Provide in-memory filesystem for isolated testing."""
    return InMemoryFileSystemAdapter()


@pytest.fixture
def populated_ide_bundle(mock_filesystem: InMemoryFileSystemAdapter) -> Path:
    """Set up dist/ide/ with correct component counts from design YAML."""
    bundle = Path("dist/ide")
    mock_filesystem.mkdir(bundle / "agents", parents=True)
    mock_filesystem.mkdir(bundle / "tasks" / "nw", parents=True)
    mock_filesystem.mkdir(bundle / "templates", parents=True)
    mock_filesystem.mkdir(bundle / "scripts", parents=True)

    for i in range(EXPECTED_AGENT_COUNT):
        mock_filesystem.write_text(bundle / "agents" / f"agent_{i}.md", f"agent {i}")
    for i in range(EXPECTED_COMMAND_COUNT):
        mock_filesystem.write_text(
            bundle / "tasks" / "nw" / f"cmd_{i}.md", f"command {i}"
        )
    for i in range(EXPECTED_TEMPLATE_COUNT):
        mock_filesystem.write_text(
            bundle / "templates" / f"tpl_{i}.yaml", f"template: {i}"
        )
    for i in range(EXPECTED_SCRIPT_COUNT):
        mock_filesystem.write_text(bundle / "scripts" / f"script_{i}.py", f"script {i}")

    return bundle


# ═══════════════════════════════════════════════════════════════════════════════
# Tests
# ═══════════════════════════════════════════════════════════════════════════════


class TestIdeBundleExistsCheck:
    """Tests for the IDE bundle existence pre-flight check."""

    def test_ide_bundle_exists_check_passes_when_present(
        self,
        mock_filesystem: InMemoryFileSystemAdapter,
        populated_ide_bundle: Path,
    ) -> None:
        """Check should pass when dist/ide/ directory has content."""
        check = IdeBundleExistsCheck(
            filesystem=mock_filesystem, bundle_dir=populated_ide_bundle
        )

        result = check.execute()

        assert result.passed is True
        assert result.severity == CheckSeverity.BLOCKING

    def test_ide_bundle_exists_check_fails_when_missing(
        self,
        mock_filesystem: InMemoryFileSystemAdapter,
    ) -> None:
        """Check should fail with BLOCKING severity when dist/ide/ is absent."""
        missing_bundle = Path("dist/ide")
        assert not mock_filesystem.exists(missing_bundle)

        check = IdeBundleExistsCheck(
            filesystem=mock_filesystem, bundle_dir=missing_bundle
        )

        result = check.execute()

        assert result.passed is False
        assert result.severity == CheckSeverity.BLOCKING

    def test_ide_bundle_check_reports_agent_command_counts(
        self,
        mock_filesystem: InMemoryFileSystemAdapter,
        populated_ide_bundle: Path,
    ) -> None:
        """Pass message should include agent and command counts."""
        check = IdeBundleExistsCheck(
            filesystem=mock_filesystem, bundle_dir=populated_ide_bundle
        )

        result = check.execute()

        assert f"{EXPECTED_AGENT_COUNT} agents" in result.message
        assert f"{EXPECTED_COMMAND_COUNT} commands" in result.message

    def test_ide_bundle_check_remediation_message(
        self,
        mock_filesystem: InMemoryFileSystemAdapter,
    ) -> None:
        """Remediation should say 'forge build'."""
        missing_bundle = Path("dist/ide")
        check = IdeBundleExistsCheck(
            filesystem=mock_filesystem, bundle_dir=missing_bundle
        )

        result = check.execute()

        assert result.passed is False
        assert "forge build" in result.remediation
        assert result.fix_command == "forge build"
