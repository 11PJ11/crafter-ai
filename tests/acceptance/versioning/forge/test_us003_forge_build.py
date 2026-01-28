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


class TestBuildFailsWhenTestsFail:
    """
    Scenario: Build fails when tests fail (Step 05-02)

    Given Benedetta is working in the test repository
    And the git branch is "main"
    And the pyproject.toml contains base version "1.2.3"
    And 3 tests fail when the test runner is invoked
    When Benedetta runs the /nw:forge command through the CLI entry point
    Then the build process runs tests first
    And the build aborts with exit code non-zero
    And the error displays "Build failed: 3 test failures. Fix tests before building."
    And the dist/ directory is not modified
    """

    def test_build_fails_when_tests_fail(
        self,
        test_repository,
        mock_git_adapter,
        mock_test_runner,
        mock_date_provider,
        in_memory_file_system_for_forge,
        cli_result,
    ):
        """
        ACCEPTANCE TEST: Build fails when tests fail.

        This test exercises the error handling path:
        CLI -> BuildService -> TestRunner fails -> Build aborts
        """
        # GIVEN: Benedetta is working in the test repository
        repo_root = test_repository["root"]

        # AND: The git branch is "main"
        mock_git_adapter.configure(
            branch="main",
            uncommitted_changes=False,
            repo_root=repo_root,
        )

        # AND: The pyproject.toml contains base version "1.2.3"
        in_memory_file_system_for_forge.configure(base_version="1.2.3")

        # AND: 3 tests fail when the test runner is invoked
        mock_test_runner.configure(tests_pass=False, failure_count=3)

        # AND: Today's date is 2026-01-27
        mock_date_provider.configure(today=date(2026, 1, 27))

        # WHEN: Benedetta runs the /nw:forge command through CLI entry point
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
        cli_result["returncode"] = 0 if result.success else 1

        # THEN: The build process runs tests first
        assert mock_test_runner.was_called, (
            "Expected test runner to be called during build"
        )

        # AND: The build aborts with exit code non-zero
        assert result.success is False, (
            "Expected build to fail when tests fail"
        )
        assert cli_result["returncode"] != 0, (
            "Expected non-zero exit code when build fails"
        )

        # AND: The error displays "Build failed: 3 test failures. Fix tests before building."
        expected_error = "Build failed: 3 test failures. Fix tests before building."
        assert expected_error in result.error_message, (
            f"Expected error message '{expected_error}', got: {result.error_message}"
        )

        # AND: The dist/ directory is not modified
        assert not in_memory_file_system_for_forge.dist_was_modified, (
            "Expected dist/ directory to NOT be modified when build fails"
        )


class TestRCCounterIncrementsOnSameDayBuilds:
    """
    Scenario: RC counter increments on same day builds (Step 05-03)

    Given Carlo is working in the test repository
    And the git branch is "main"
    And the pyproject.toml contains base version "1.2.3"
    And today's date is 2026-01-27
    And a previous build created version "1.2.3-rc.main.20260127.1" in dist/
    And all tests pass when the test runner is invoked
    When Carlo runs the /nw:forge command through the CLI entry point
    Then the version becomes "1.2.3-rc.main.20260127.2"
    And the previous dist/ contents are cleaned before the new build
    """

    def test_rc_counter_increments_on_same_day_builds(
        self,
        test_repository,
        mock_git_adapter,
        mock_test_runner,
        mock_date_provider,
        in_memory_file_system_for_forge,
        cli_result,
    ):
        """
        ACCEPTANCE TEST: RC counter increments on same day builds.

        This test verifies that when building twice on the same day,
        the build counter increments: 20260127.1 -> 20260127.2
        """
        # GIVEN: Carlo is working in the test repository
        repo_root = test_repository["root"]

        # AND: The git branch is "main"
        mock_git_adapter.configure(
            branch="main",
            uncommitted_changes=False,
            repo_root=repo_root,
        )

        # AND: The pyproject.toml contains base version "1.2.3"
        in_memory_file_system_for_forge.configure(base_version="1.2.3")

        # AND: Today's date is 2026-01-27
        mock_date_provider.configure(today=date(2026, 1, 27))

        # AND: A previous build created version "1.2.3-rc.main.20260127.1" in dist/
        in_memory_file_system_for_forge.configure_previous_build(
            version="1.2.3-rc.main.20260127.1"
        )

        # AND: All tests pass when the test runner is invoked
        mock_test_runner.configure(tests_pass=True, failure_count=0)

        # WHEN: Carlo runs the /nw:forge command through CLI entry point
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

        # THEN: The version becomes "1.2.3-rc.main.20260127.2"
        actual_version = in_memory_file_system_for_forge.get_dist_version()
        expected_version = "1.2.3-rc.main.20260127.2"
        assert actual_version == expected_version, (
            f"Expected version '{expected_version}' (counter incremented from .1 to .2), "
            f"got '{actual_version}'"
        )

        # AND: The previous dist/ contents are cleaned before the new build
        assert in_memory_file_system_for_forge.dist_was_cleaned, (
            "Expected dist/ directory to be cleaned before the new build"
        )


# ACTIVE - Step 05-04: RC counter resets on new day
class TestRCCounterResetsOnNewDay:
    """
    Scenario: RC counter resets on new day (Step 05-04)

    Given Carlo is working in the test repository
    And the git branch is "main"
    And the pyproject.toml contains base version "1.2.3"
    And today's date is 2026-01-28
    And a previous build from yesterday created version "1.2.3-rc.main.20260127.3"
    And all tests pass when the test runner is invoked
    When Carlo runs the /nw:forge command through the CLI entry point
    Then the version becomes "1.2.3-rc.main.20260128.1"
    """

    def test_rc_counter_resets_on_new_day(
        self,
        test_repository,
        mock_git_adapter,
        mock_test_runner,
        mock_date_provider,
        in_memory_file_system_for_forge,
        cli_result,
    ):
        """
        ACCEPTANCE TEST: RC counter resets to 1 when building on a new day.

        This test verifies that when building on a different day than previous build,
        the counter resets: 20260127.3 -> 20260128.1 (NOT 20260128.4)
        """
        # GIVEN: Carlo is working in the test repository
        repo_root = test_repository["root"]

        # AND: The git branch is "main"
        mock_git_adapter.configure(
            branch="main",
            uncommitted_changes=False,
            repo_root=repo_root,
        )

        # AND: The pyproject.toml contains base version "1.2.3"
        in_memory_file_system_for_forge.configure(base_version="1.2.3")

        # AND: Today's date is 2026-01-28
        mock_date_provider.configure(today=date(2026, 1, 28))

        # AND: A previous build from yesterday created version "1.2.3-rc.main.20260127.3"
        in_memory_file_system_for_forge.configure_previous_build(
            version="1.2.3-rc.main.20260127.3"
        )

        # AND: All tests pass when the test runner is invoked
        mock_test_runner.configure(tests_pass=True, failure_count=0)

        # WHEN: Carlo runs the /nw:forge command through CLI entry point
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

        # THEN: The version becomes "1.2.3-rc.main.20260128.1"
        # Counter RESETS to 1 because today's date (28) differs from previous build date (27)
        expected_version = "1.2.3-rc.main.20260128.1"
        assert result.version == expected_version, (
            f"Expected version '{expected_version}' (counter reset to 1 on new day), "
            f"got '{result.version}'"
        )


# ACTIVE - Step 05-06: User declines install after successful build
class TestUserDeclinesInstallAfterSuccessfulBuild:
    """
    Scenario: User declines install after successful build (Step 05-06)

    Given Alessandro is working in the test repository
    And all tests pass when the test runner is invoked
    When Alessandro runs the /nw:forge command through the CLI entry point
    And Alessandro responds "n" to the install prompt
    Then the dist/ directory contains the built distribution
    And no installation to ~/.claude/ occurs
    And the CLI exits with success code
    """

    def test_user_declines_install_after_successful_build(
        self,
        test_repository,
        mock_git_adapter,
        mock_test_runner,
        mock_date_provider,
        in_memory_file_system_for_forge,
        cli_result,
        tmp_path,
    ):
        """
        ACCEPTANCE TEST: User declines install after successful build.

        This test exercises the install decline flow:
        CLI -> BuildService -> Build succeeds -> User responds 'n' -> No installation
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

        # AND: A clean test ~/.claude/ directory exists (for verifying no installation)
        test_claude_home = tmp_path / ".claude"
        test_claude_home.mkdir()

        # WHEN: Alessandro runs the /nw:forge command through CLI entry point
        from nWave.core.versioning.application.build_service import BuildService
        from nWave.cli.forge_cli import format_build_output, handle_install_response

        build_service = BuildService(
            git=mock_git_adapter,
            test_runner=mock_test_runner,
            file_system=in_memory_file_system_for_forge,
            date_provider=mock_date_provider,
        )

        result = build_service.build()
        output, prompt = format_build_output(result)

        # AND: Alessandro responds "n" to the install prompt
        user_response = "n"
        install_result = handle_install_response(
            user_response=user_response,
            build_result=result,
            claude_home=test_claude_home,
        )

        cli_result["output"] = output
        cli_result["prompt"] = prompt
        cli_result["returncode"] = install_result.exit_code

        # THEN: The dist/ directory contains the built distribution
        assert in_memory_file_system_for_forge.dist_exists, (
            "Expected dist/ directory to contain built distribution"
        )
        assert result.success is True, (
            "Expected build to succeed"
        )

        # AND: No installation to ~/.claude/ occurs
        assert install_result.installation_performed is False, (
            "Expected no installation when user declines"
        )
        # Verify ~/.claude/ remains unchanged (no nWave directories)
        nwave_agents = test_claude_home / "agents" / "nw"
        nwave_commands = test_claude_home / "commands" / "nw"
        assert not nwave_agents.exists(), (
            f"Expected no nWave agents installed, but found {nwave_agents}"
        )
        assert not nwave_commands.exists(), (
            f"Expected no nWave commands installed, but found {nwave_commands}"
        )

        # AND: The CLI exits with success code
        assert cli_result["returncode"] == 0, (
            f"Expected exit code 0 (success), got {cli_result['returncode']}"
        )


# ACTIVE - Step 05-07: User accepts install after successful build
class TestUserAcceptsInstallAfterSuccessfulBuild:
    """
    Scenario: User accepts install after successful build (Step 05-07)

    Given Alessandro is working in the test repository
    And a clean test ~/.claude/ directory exists
    And all tests pass when the test runner is invoked
    When Alessandro runs the /nw:forge command through the CLI entry point
    And Alessandro responds "Y" to the install prompt
    Then the /nw:forge:install command is invoked
    And the distribution is installed to ~/.claude/
    """

    def test_user_accepts_install_after_successful_build(
        self,
        test_repository,
        mock_git_adapter,
        mock_test_runner,
        mock_date_provider,
        in_memory_file_system_for_forge,
        in_memory_install_file_system,
        cli_result,
    ):
        """
        ACCEPTANCE TEST: User accepts install after successful build.

        This test exercises the complete install-accept flow:
        CLI -> BuildService -> User input "Y" -> InstallService -> Installation complete
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

        # AND: A clean test ~/.claude/ directory exists
        # (configured via in_memory_install_file_system fixture)

        # WHEN: Alessandro runs the /nw:forge command through CLI entry point
        from nWave.core.versioning.application.build_service import BuildService
        from nWave.cli.forge_cli import (
            format_build_output,
            handle_install_response,
        )

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

        # AND: Alessandro responds "Y" to the install prompt
        user_response = "Y"
        install_result = handle_install_response(
            user_response=user_response,
            build_result=result,
            install_file_system=in_memory_install_file_system,
        )

        # THEN: The /nw:forge:install command is invoked
        assert install_result.install_invoked, (
            "Expected /nw:forge:install to be invoked when user responds 'Y'"
        )

        # AND: The distribution is installed to ~/.claude/
        assert in_memory_install_file_system.installation_completed, (
            "Expected distribution to be installed to ~/.claude/"
        )
        assert in_memory_install_file_system.installed_version == result.version, (
            f"Expected installed version to be {result.version}, "
            f"got {in_memory_install_file_system.installed_version}"
        )


class TestFeatureBranchNameIncludedInRCVersion:
    """
    Scenario: Feature branch name included in RC version (Step 05-05)

    Given Daniela is working in the test repository
    And the git branch is "feature/new-agent"
    And the pyproject.toml contains base version "1.2.3"
    And today's date is 2026-01-27
    And all tests pass when the test runner is invoked
    When Daniela runs the /nw:forge command through the CLI entry point
    Then the version becomes "1.2.3-rc.feature-new-agent.20260127.1"
    And special characters in the branch name are normalized to hyphens
    """

    def test_feature_branch_name_included_in_rc_version(
        self,
        test_repository,
        mock_git_adapter,
        mock_test_runner,
        mock_date_provider,
        in_memory_file_system_for_forge,
        cli_result,
    ):
        """
        ACCEPTANCE TEST: Feature branch name included in RC version.

        This test verifies that feature branch names like "feature/new-agent"
        are normalized to "feature-new-agent" in the RC version string.
        """
        # GIVEN: Daniela is working in the test repository
        repo_root = test_repository["root"]

        # AND: The git branch is "feature/new-agent"
        mock_git_adapter.configure(
            branch="feature/new-agent",
            uncommitted_changes=False,
            repo_root=repo_root,
        )

        # AND: The pyproject.toml contains base version "1.2.3"
        in_memory_file_system_for_forge.configure(base_version="1.2.3")

        # AND: All tests pass when the test runner is invoked
        mock_test_runner.configure(tests_pass=True, failure_count=0)

        # AND: Today's date is 2026-01-27
        mock_date_provider.configure(today=date(2026, 1, 27))

        # WHEN: Daniela runs the /nw:forge command through CLI entry point
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

        # THEN: The version becomes "1.2.3-rc.feature-new-agent.20260127.1"
        actual_version = in_memory_file_system_for_forge.get_dist_version()
        expected_version = "1.2.3-rc.feature-new-agent.20260127.1"
        assert actual_version == expected_version, (
            f"Expected version '{expected_version}' with normalized branch name, "
            f"got '{actual_version}'"
        )

        # AND: Special characters in the branch name are normalized to hyphens
        # The "/" in "feature/new-agent" should be replaced with "-"
        assert "feature-new-agent" in actual_version, (
            f"Expected branch name 'feature/new-agent' to be normalized to 'feature-new-agent' "
            f"in version string, got: {actual_version}"
        )
        assert "/" not in actual_version, (
            f"Expected no '/' characters in version string, got: {actual_version}"
        )
