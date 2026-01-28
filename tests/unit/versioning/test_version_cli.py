"""
Unit tests for version_cli (driving adapter).

version_cli formats VersionCheckResult into user-facing output.
"""

from nWave.core.versioning.domain.version import Version


class TestVersionCliFormatsOutput:
    """Test that version_cli formats output correctly."""

    def test_version_cli_formats_output_with_update_indicator(self):
        """CLI should format 'nWave v1.2.3 (update available: v1.3.0)'."""
        from nWave.core.versioning.application.version_service import VersionCheckResult
        from nWave.cli.version_cli import format_version_output

        # GIVEN: VersionCheckResult with update available (local < remote)
        result = VersionCheckResult(
            local_version=Version("1.2.3"),
            remote_version=Version("1.3.0"),
        )

        # WHEN: format_version_output is called
        output = format_version_output(result)

        # THEN: Output matches expected format
        assert "nWave v1.2.3 (update available: v1.3.0)" in output

    def test_version_cli_formats_up_to_date_output(self):
        """CLI should format 'nWave v1.3.0 (up to date)' when no update."""
        from nWave.core.versioning.application.version_service import VersionCheckResult
        from nWave.cli.version_cli import format_version_output

        # GIVEN: VersionCheckResult without update available (local == remote)
        result = VersionCheckResult(
            local_version=Version("1.3.0"),
            remote_version=Version("1.3.0"),
        )

        # WHEN: format_version_output is called
        output = format_version_output(result)

        # THEN: Output matches expected format
        assert "nWave v1.3.0 (up to date)" in output


# ============================================================================
# Step 03-06: Handle missing VERSION file gracefully
# ============================================================================


class TestVersionCliHandlesMissingVersionFile:
    """Test that version_cli returns non-zero exit code for missing VERSION file."""

    def test_version_cli_returns_non_zero_exit_code_for_missing_version_file(
        self, tmp_path, monkeypatch, capsys
    ):
        """
        CLI should return exit code 1 and display error message when VERSION file missing.

        Acceptance criteria:
        - Error displays "VERSION file not found. nWave may be corrupted."
        - CLI exit code is non-zero
        """
        from nWave.cli import version_cli

        # GIVEN: NWAVE_HOME points to directory without VERSION file
        nwave_home = tmp_path / ".claude"
        nwave_home.mkdir()
        # Do NOT create VERSION file

        monkeypatch.setenv("NWAVE_HOME", str(nwave_home))
        monkeypatch.setenv("NWAVE_TEST_MODE", "true")
        monkeypatch.setenv("NWAVE_MOCK_GITHUB_VERSION", "1.3.0")
        monkeypatch.setenv("NWAVE_MOCK_GITHUB_REACHABLE", "true")

        # WHEN: main() is called
        exit_code = version_cli.main()

        # THEN: Exit code is non-zero
        assert exit_code != 0, f"Expected non-zero exit code, got {exit_code}"

        # AND: Error message contains the expected text
        captured = capsys.readouterr()
        expected_error = "VERSION file not found. nWave may be corrupted."
        combined_output = captured.out + captured.err

        assert expected_error in combined_output, (
            f"Expected error '{expected_error}' not found in output:\n"
            f"STDOUT: {captured.out!r}\n"
            f"STDERR: {captured.err!r}"
        )


# ============================================================================
# Step 03-07: Handle GitHub API rate limit gracefully - CLI tests
# ============================================================================


class TestVersionCliFormatsUnableToCheckOnRateLimit:
    """
    Step 03-07: Test that version_cli formats "Unable to check for updates" on rate limit.

    Acceptance criteria:
    - Output displays "nWave v1.2.3 (Unable to check for updates)"
    - No error is thrown
    - CLI exit code is 0
    """

    def test_version_cli_formats_unable_to_check_on_rate_limit(self):
        """
        CLI should format rate-limited result as "nWave v1.2.3 (Unable to check for updates)".
        """
        from nWave.core.versioning.application.version_service import VersionCheckResult
        from nWave.cli.version_cli import format_version_output

        # GIVEN: VersionCheckResult indicating rate limit (is_offline=True)
        result = VersionCheckResult(
            local_version=Version("1.2.3"),
            remote_version=None,  # Cannot fetch due to rate limit
            is_offline=True,  # Rate limited treated same as offline
        )

        # WHEN: format_version_output is called
        output = format_version_output(result)

        # THEN: Output shows unable to check message
        assert output == "nWave v1.2.3 (Unable to check for updates)"

    def test_version_cli_returns_zero_exit_code_on_rate_limit(
        self, tmp_path, monkeypatch, capsys
    ):
        """
        CLI should return exit code 0 when rate limited (graceful degradation).

        Rate limiting is NOT an error condition from user perspective.
        """
        from nWave.cli import version_cli

        # GIVEN: NWAVE_HOME with valid VERSION file
        nwave_home = tmp_path / ".claude"
        nwave_home.mkdir()
        version_file = nwave_home / "VERSION"
        version_file.write_text("1.2.3")

        monkeypatch.setenv("NWAVE_HOME", str(nwave_home))
        monkeypatch.setenv("NWAVE_TEST_MODE", "true")
        monkeypatch.setenv(
            "NWAVE_MOCK_GITHUB_REACHABLE", "false"
        )  # Simulates rate limit/offline

        # WHEN: main() is called
        exit_code = version_cli.main()

        # THEN: Exit code is 0 (success, not error)
        assert exit_code == 0, f"Expected exit code 0, got {exit_code}"

        # AND: Output shows unable to check message
        captured = capsys.readouterr()
        assert "Unable to check for updates" in captured.out

    def test_version_cli_no_error_thrown_on_rate_limit(
        self, tmp_path, monkeypatch, capsys
    ):
        """
        CLI should NOT write to stderr when rate limited.

        No error message should be shown - graceful degradation only.
        """
        from nWave.cli import version_cli

        # GIVEN: NWAVE_HOME with valid VERSION file
        nwave_home = tmp_path / ".claude"
        nwave_home.mkdir()
        version_file = nwave_home / "VERSION"
        version_file.write_text("1.2.3")

        monkeypatch.setenv("NWAVE_HOME", str(nwave_home))
        monkeypatch.setenv("NWAVE_TEST_MODE", "true")
        monkeypatch.setenv(
            "NWAVE_MOCK_GITHUB_REACHABLE", "false"
        )  # Simulates rate limit/offline

        # WHEN: main() is called
        version_cli.main()

        # THEN: stderr is empty (no error)
        captured = capsys.readouterr()
        assert captured.err == "", f"Unexpected stderr output: {captured.err!r}"

        # AND: stdout contains the version message
        assert "nWave v1.2.3" in captured.out
