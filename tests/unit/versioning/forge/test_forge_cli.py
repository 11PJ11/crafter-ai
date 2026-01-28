"""
Unit tests for forge_cli driving adapter.

Tests for Step 05-01: Install prompt display

forge_cli is the driving adapter for /nw:forge command.
It invokes BuildService and formats output with install prompt.

HEXAGONAL ARCHITECTURE:
- forge_cli is a DRIVING ADAPTER (outside the hexagon)
- Invokes BuildService application service
- Formats output for user display
"""

import pytest
from unittest.mock import Mock


class TestForgeCLIPromptsForInstall:
    """Test that forge_cli displays install prompt after successful build."""

    def test_forge_cli_prompts_for_install(self):
        """
        GIVEN a successful build result
        WHEN format_build_output() is called
        THEN the prompt displays "Install: [Y/n]"
        """
        # Arrange
        from nWave.cli.forge_cli import format_build_output
        from nWave.core.versioning.application.build_service import BuildResult

        build_result = BuildResult(
            success=True,
            version="1.2.3-rc.main.20260127.1",
            dist_cleaned=True,
            tests_passed=True,
            distribution_created=True,
            error_message=None,
        )

        # Act
        output, prompt = format_build_output(build_result)

        # Assert
        assert "Install: [Y/n]" in prompt
