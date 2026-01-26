Feature: Update nWave Safely
  As an nWave user
  I want to update to the latest version with automatic backup
  So that I can safely upgrade and recover if something goes wrong

  Background:
    Given nWave is installed at ~/.claude/
    And the update CLI entry point exists at ~/.claude/nWave/cli/update_cli.py

  Scenario: Successful update with backup
    Given nWave version 1.5.7 is installed at ~/.claude/
    And GitHub latest release is 1.6.0
    And the release changelog shows key changes
    When I run the update command through the CLI entry point
    Then a backup is created at ~/.claude_bck_YYYYMMDD/
    And I see "Backup created at ~/.claude_bck_"
    And I see the changelog preview
    And I am prompted "Proceed with update? (Y/N)"
    When I confirm with Y
    Then nWave 1.6.0 is installed
    And the VERSION file shows 1.6.0
    And I see "Updated to 1.6.0"
    And I see key changes in the summary
    And the command exits with code 0

  Scenario: Update cancelled by user
    Given nWave version 1.5.7 is installed
    And GitHub latest release is 1.6.0
    When I run the update command through the CLI entry point
    And I see the confirmation prompt
    And I respond with N
    Then no changes are made to the installation
    And the backup directory is deleted
    And I see "Update cancelled. No changes made."
    And the command exits with code 2

  Scenario: Already up to date
    Given nWave version 1.6.0 is installed
    And GitHub latest release is 1.6.0
    When I run the update command through the CLI entry point
    Then I see "Already running latest version (1.6.0)"
    And no backup is created
    And the command exits with code 0

  Scenario: Update fails mid-process - automatic rollback
    Given nWave version 1.5.7 is installed at ~/.claude/
    And GitHub latest release is 1.6.0
    And a backup has been created at ~/.claude_bck_20260123/
    And the user will confirm the update
    And the download will fail mid-process with network error
    When I run the update command through the CLI entry point
    Then the system automatically restores from ~/.claude_bck_20260123/
    And I see "Update failed: Network error during download. Restored from backup."
    And nWave 1.5.7 remains installed
    And the command exits with code 1

  Scenario: Insufficient permissions during update
    Given nWave version 1.5.7 is installed at ~/.claude/
    And the user lacks write permissions to ~/.claude/
    When I run the update command through the CLI entry point
    Then I see "Permission denied: Cannot write to ~/.claude/"
    And no backup is created
    And no changes are made
    And the command exits with code 1

  Scenario: Insufficient disk space during update
    Given nWave version 1.5.7 is installed at ~/.claude/
    And available disk space is less than 2x installation size
    When I run the update command through the CLI entry point
    Then I see "Insufficient disk space for update"
    And I see "Required: [SIZE] MB (2x installation size for safety backup)"
    And no backup is created
    And the command exits with code 1
