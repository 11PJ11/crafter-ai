Feature: Automated Changelog Generation
  As a framework creator releasing a new version
  I want the changelog automatically generated from commit history
  So that users can see what changed without manual documentation effort

  Background:
    Given I am in the nWave repository
    And semantic-release is configured
    And GitHub Actions workflow exists

  Scenario: Changelog generated on release
    Given commits since last release:
      | Commit message                       | Type |
      | feat: add user dashboard             | feat |
      | fix(auth): resolve timeout issue     | fix  |
      | docs: update installation guide      | docs |
    When semantic-release runs on push to main
    Then CHANGELOG.md is updated with new section
    And GitHub Release is created with release notes
    And release notes include Features section with "add user dashboard"
    And release notes include Bug Fixes section with "resolve timeout issue"

  Scenario: Breaking change highlighted in changelog
    Given a commit with message "feat!: redesign API endpoints"
    When semantic-release runs
    Then CHANGELOG.md includes "BREAKING CHANGES" section
    And GitHub Release prominently shows breaking change warning
    And the version is bumped to next major version
