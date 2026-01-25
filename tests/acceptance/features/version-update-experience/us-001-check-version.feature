Feature: Check Installed Version
  As an nWave user
  I want to see my currently installed version and whether updates are available
  So that I can report issues accurately and know if I'm running the latest version

  Background:
    Given nWave is installed at ~/.claude/nWave/
    And the version CLI entry point exists at ~/.claude/nWave/cli/version_cli.py

  Scenario: Display installed version when up to date
    Given nWave version 1.5.7 is installed locally
    And GitHub latest release is 1.5.7
    When I run the version command through the CLI entry point
    Then I see "nWave v1.5.7 (up to date)"
    And the command exits with code 0

  @pytest.mark.skip(reason="Not implemented yet - will enable one at a time to avoid commit blocks")
  Scenario: Display installed version with update available
    Given nWave version 1.5.7 is installed locally
    And GitHub latest release is 1.6.0
    And the release changelog contains:
      """
      ## What's Changed
      * feat: add user dashboard by @contributor1
      * fix(auth): resolve timeout issue by @contributor2
      * docs: update installation guide by @contributor3
      """
    When I run the version command through the CLI entry point
    Then I see an update banner showing:
      | Field            | Value                      |
      | Current version  | 1.5.7                      |
      | Available update | 1.6.0                      |
      | Update command   | Run /nw:update to upgrade  |
    And I see changelog highlights containing "add user dashboard"
    And I see changelog highlights containing "resolve timeout issue"
    And the command exits with code 0

  @pytest.mark.skip(reason="Not implemented yet - will enable one at a time to avoid commit blocks")
  Scenario: Network failure during version check
    Given nWave version 1.5.7 is installed locally
    And GitHub API is unreachable
    When I run the version command through the CLI entry point
    Then I see "nWave v1.5.7 (installed)"
    And I see "Could not check for updates"
    And I see a link to check releases manually
    And the command exits with code 0
