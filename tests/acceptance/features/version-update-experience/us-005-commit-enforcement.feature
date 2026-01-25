Feature: Conventional Commit Enforcement
  As a framework creator committing changes
  I want my commit messages validated against Conventional Commits format
  So that semantic-release can automatically determine version bumps and generate changelogs

  Background:
    Given I am in the nWave repository
    And commit-msg hook is installed

  @pytest.mark.skip(reason="Not implemented yet - will enable one at a time to avoid commit blocks")
  Scenario: Valid conventional commit accepted
    Given I have staged changes
    When I commit with message "feat: add user dashboard"
    Then the commit is accepted
    And no error is shown
    And the commit appears in git log

  @pytest.mark.skip(reason="Not implemented yet - will enable one at a time to avoid commit blocks")
  Scenario: Valid scoped commit accepted
    Given I have staged changes
    When I commit with message "fix(auth): resolve login timeout issue"
    Then the commit is accepted
    And no error is shown
    And the commit appears in git log

  @pytest.mark.skip(reason="Not implemented yet - will enable one at a time to avoid commit blocks")
  Scenario: Breaking change commit accepted
    Given I have staged changes
    When I commit with message "feat!: redesign API endpoints"
    Then the commit is accepted
    And no error is shown
    And the commit appears in git log

  @pytest.mark.skip(reason="Not implemented yet - will enable one at a time to avoid commit blocks")
  Scenario: Invalid commit rejected with guidance
    Given I have staged changes
    When I commit with message "fixed the login bug"
    Then the commit is rejected
    And I see error "does not follow Conventional Commits format"
    And I see "Expected format: <type>[scope]: <description>"
    And I see "Examples: feat: add user authentication"
    And I see reference link "https://www.conventionalcommits.org/"
    And the commit does NOT appear in git log
