Feature: Pre-push Validation
  As a framework creator pushing changes
  I want validation that VERSION file and semantic-release config exist
  So that releases are always properly configured before code reaches the remote

  Background:
    Given I am in the nWave repository
    And pre-push hook is installed

  @pytest.mark.skip(reason="Not implemented yet - will enable one at a time to avoid commit blocks")
  Scenario: Push succeeds when all validations pass
    Given nWave/VERSION file exists with valid semver format
    And .releaserc configuration exists
    When I push to origin
    Then the push succeeds
    And all commits reach the remote

  @pytest.mark.skip(reason="Not implemented yet - will enable one at a time to avoid commit blocks")
  Scenario: Push rejected when VERSION file missing
    Given nWave/VERSION file does not exist
    And .releaserc configuration exists
    When I push to origin
    Then the push is rejected
    And I see error "VERSION file missing"
    And I see suggested action "Create nWave/VERSION with current version (e.g., '1.5.7')"
    And no commits reach the remote
