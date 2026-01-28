"""
Acceptance tests for US-003: Build Custom Local Distribution (Forge).

ACTIVE SCENARIO: Successful build with install prompt on main branch (Step 05-01)
- Alessandro is working in the test repository
- Git branch is "main"
- pyproject.toml contains base version "1.2.3"
- All tests pass when the test runner is invoked
- Today's date is 2026-01-27
- Build succeeds with RC version 1.2.3-rc.main.20260127.1
- Prompt displays "Install: [Y/n]"

HEXAGONAL BOUNDARY: Tests invoke through CLI entry point only.
"""

import pytest
from datetime import date


class TestSuccessfulBuildWithInstallPromptOnMainBranch:
    """
    Scenario: Successful build with install prompt on main branch (Step 05-01)

    Given Alessandro is working in the test repository
    And the git branch is "main"
    And the pyproject.toml contains base version "1.2.3"
    And all tests pass when the test runner is invoked
    And today's date is 2026-01-27
    When Alessandro runs the /nw:forge command through the CLI entry point
    Then the dist/ directory is cleaned before build
    And the build process runs all tests first
    And dist/ is created with the built distribution
    And the version is set to "1.2.3-rc.main.20260127.1"
    And the prompt displays "Install: [Y/n]"
    """

    def test_successful_build_with_install_prompt_on_main_branch(
        self,
        test_repository,
        mock_git_adapter,
        mock_test_runner,
        mock_date_provider,
        in_memory_file_system_for_forge,
        cli_result,
    ):
        """
        ACCEPTANCE TEST: Successful build with install prompt on main branch.

        This test exercises the complete system path:
        CLI -> BuildService -> GitAdapter + TestRunner + FileSystemAdapter -> RCVersion creation
        """
        # GIVEN: Alessandro is working in the test repository
        repo_root = test_repository["root"]

        # AND: The git branch is "main"
        mock_git_adapter.configure(
            branch="main",
            uncommitted_changes=False,
            repo_root=repo_root,
        )

        # AND: The pyproject.toml contains base version "1.2.3"
        in_memory_file_system_for_forge.configure(base_version="1.2.3")

        # AND: All tests pass when the test runner is invoked
        mock_test_runner.configure(tests_pass=True, failure_count=0)

        # AND: Today's date is 2026-01-27
        mock_date_provider.configure(today=date(2026, 1, 27))

        # WHEN: Alessandro runs the /nw:forge command through CLI entry point
        # Import BuildService from application layer
        from nWave.core.versioning.application.build_service import BuildService
        from nWave.cli.forge_cli import format_build_output

        build_service = BuildService(
            git=mock_git_adapter,
            test_runner=mock_test_runner,
            file_system=in_memory_file_system_for_forge,
            date_provider=mock_date_provider,
        )

        result = build_service.build()
        output, prompt = format_build_output(result)

        cli_result["output"] = output
        cli_result["prompt"] = prompt

        # THEN: The dist/ directory is cleaned before build
        assert in_memory_file_system_for_forge.dist_was_cleaned, (
            "Expected dist/ directory to be cleaned before build"
        )

        # AND: The build process runs all tests first
        assert mock_test_runner.was_called, (
            "Expected test runner to be called during build"
        )

        # AND: dist/ is created with the built distribution
        assert in_memory_file_system_for_forge.dist_exists, (
            "Expected dist/ directory to contain built distribution"
        )

        # AND: The version is set to "1.2.3-rc.main.20260127.1"
        actual_version = in_memory_file_system_for_forge.get_dist_version()
        expected_version = "1.2.3-rc.main.20260127.1"
        assert actual_version == expected_version, (
            f"Expected version '{expected_version}', got '{actual_version}'"
        )

        # AND: The prompt displays "Install: [Y/n]"
        assert "Install: [Y/n]" in prompt, (
            f"Expected prompt to contain 'Install: [Y/n]', got: {prompt}"
        )
