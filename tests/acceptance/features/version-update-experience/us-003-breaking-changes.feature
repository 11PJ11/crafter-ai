Feature: Breaking Change Warning
  As an nWave user considering an update
  I want clear warning when a major version update contains breaking changes
  So that I understand migration may be required before I proceed

  Background:
    Given nWave is installed at ~/.claude/nWave/
    And the version CLI entry point exists at ~/.claude/nWave/cli/version_cli.py

  @pytest.mark.skip(reason="Not implemented yet - will enable one at a time to avoid commit blocks")
  Scenario: Major version update warning
    Given nWave version 1.5.7 is installed
    And GitHub latest release is 2.0.0
    And the release changelog contains "BREAKING CHANGES" section
    When I run the version command through the CLI entry point
    Then the update banner includes "⚠️  BREAKING CHANGES"
    And the banner is styled with red/bold formatting
    And changelog highlights show breaking changes prominently
    And the command exits with code 0

  @pytest.mark.skip(reason="Not implemented yet - will enable one at a time to avoid commit blocks")
  Scenario: Minor version update (no warning)
    Given nWave version 1.5.7 is installed
    And GitHub latest release is 1.6.0
    When I run the version command through the CLI entry point
    Then no breaking change warning is shown
    And changelog shows only feature additions and fixes
    And the command exits with code 0
