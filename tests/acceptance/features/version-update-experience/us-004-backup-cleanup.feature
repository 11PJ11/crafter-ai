Feature: Automatic Backup Cleanup
  As an nWave user who updates regularly
  I want old backups automatically cleaned up
  So that my disk doesn't fill with stale backup directories

  Background:
    Given nWave is installed at ~/.claude/
    And the update CLI entry point exists at ~/.claude/nWave/cli/update_cli.py

  Scenario: Cleanup backups older than 30 days
    Given these backup directories exist:
      | Directory                   | Age (days) |
      | ~/.claude_bck_20251201/     | 53         |
      | ~/.claude_bck_20251215/     | 39         |
      | ~/.claude_bck_20260110/     | 13         |
    And nWave version 1.5.7 is installed
    And GitHub latest release is 1.6.0
    When I run the update command through the CLI entry point
    And I confirm the update
    Then ~/.claude_bck_20251201/ is deleted
    And ~/.claude_bck_20251215/ is deleted
    And ~/.claude_bck_20260110/ is preserved
    And a new backup ~/.claude_bck_YYYYMMDD/ is created
    And the command exits with code 0

  Scenario: Backup directory is locked or in-use
    Given ~/.claude_bck_20251201/ exists and is older than 30 days
    And the directory is locked by another process
    And nWave version 1.5.7 is installed
    And GitHub latest release is 1.6.0
    When I run the update command through the CLI entry point
    And I confirm the update
    Then the log contains warning "Could not delete ~/.claude_bck_20251201/: directory in use"
    And the update proceeds normally
    And other eligible backups are cleaned up
    And the command exits with code 0

  Scenario: Insufficient permissions to delete backup
    Given ~/.claude_bck_20251201/ exists and is older than 30 days
    And the user lacks delete permissions for that directory
    And nWave version 1.5.7 is installed
    And GitHub latest release is 1.6.0
    When I run the update command through the CLI entry point
    And I confirm the update
    Then the log contains warning "Could not delete ~/.claude_bck_20251201/: permission denied"
    And the update proceeds normally
    And the command exits with code 0

  Scenario: Large number of backups (performance)
    Given 50 backup directories exist spanning 6 months
    And nWave version 1.5.7 is installed
    And GitHub latest release is 1.6.0
    When I run the update command through the CLI entry point
    And I confirm the update
    Then backups older than 30 days are cleaned up
    And cleanup completes within 10 seconds
    And I see cleanup summary for old backups
    And the command exits with code 0
