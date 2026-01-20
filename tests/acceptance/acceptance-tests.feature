# Feature: nWave Framework Rationalization for Open Source Publication

**Wave:** DISTILL
**Status:** Phase 0 - Agent and Template Rationalization
**Previous Wave:** DESIGN (architecture.md)
**Next Wave:** DEVELOP

---

# Phase 0: Agent and Template Rationalization

## Background: Foundation for Consistent Command/Task Creation
  Given the nWave framework uses agent-builder to create agents
  And the nWave framework uses commands to delegate to specialized agents
  And all commands should follow consistent minimal delegation patterns
  And command template defines the structure for command creation

## Scenario: Command template improved through research-based analysis
  @skip
  Given the researcher agent analyzes all existing commands
  When command template compliance analysis completes
  Then analysis report identifies commands exceeding 60-line limit
  And analysis report lists commands with embedded workflows
  And analysis categorizes patterns by frequency
  And command template is updated based on top violations
  And agent-builder-reviewer validates the updated template

## Scenario: Agent-builder enhanced with command creation capability
  @skip
  Given command template has been improved and validated
  When agent-builder dependencies are updated
  Then command template is referenced in dependencies
  And the forge-command capability is added to agent-builder
  And command creation guidance is added to the builder pipeline
  And documentation explains how to create minimal delegation commands

## Scenario: Agent-builder-reviewer validates command template compliance
  Given agent-builder creates a new command using command template
  When agent-builder-reviewer performs peer review
  Then the reviewer validates command size is 50-60 lines
  And the reviewer ensures zero workflow duplication
  And the reviewer confirms explicit context bundling is present
  And the reviewer verifies agent invocation pattern is used
  And critical violations block approval
  And the reviewer provides actionable feedback for non-compliant commands

## Scenario: New commands follow template structure consistently
  @skip
  Given agent-builder has command template in dependencies
  And agent-builder-reviewer validates template compliance
  When a developer creates a new command via forge capability
  Then the generated command is 50-60 lines in length
  And the command contains zero workflow implementation
  And the command bundles context with pre-discovered file paths
  And the command uses proper agent invocation pattern
  And the command passes reviewer validation

## Scenario: Command template validation fails for non-compliant command
  @skip
  Given agent-builder creates a command with embedded workflow
  When agent-builder-reviewer validates the command
  Then the reviewer detects embedded procedural steps
  And the reviewer blocks approval with actionable feedback
  And the feedback identifies where to move the embedded workflow
  And the feedback provides specific remediation steps

---

# Quality Gates Phase: Comprehensive Validation Before Handoff

## Background: Quality Gate Requirements for Production Readiness
  Given all previous phases have completed their work
  And the framework demonstrates command/task consistency
  And agents have clear delegation boundaries
  And acceptance criteria from all phases must be validated
  And no work can proceed to DEVELOP without passing all quality gates

## Scenario: Phase 0 command template compliance validation passes
  @skip
  Given command template has been analyzed and improved
  And agent-builder uses the improved template
  When quality gate validation runs for Phase 0
  Then all commands comply with the 50-60 line target
  And no command contains embedded orchestration workflows
  And all commands have ORCHESTRATOR BRIEFING sections
  And context bundling is explicit and complete
  And command template compliance checker passes

## Scenario: Phase 1 platform abstraction validation passes
  @skip
  Given the platform abstraction layer has been implemented
  And both JSON and YAML formatters have been created
  When quality gate validation runs for Phase 1
  Then JSON formatter produces valid output structure
  And YAML formatter produces valid output structure
  And formatters handle all tested scenarios correctly
  And shared content library shows no conflicts
  And platform abstraction tests all pass

## Scenario: Phase 2 shared content integration validation passes
  @skip
  Given agent specifications and command files have been created
  And shared content has been embedded in both
  When quality gate validation runs for Phase 2
  Then agent-builder references are consistent across files
  And command task descriptions match agent responsibilities
  And no content duplication exists between agent and command
  And shared content updates propagate correctly
  And integration tests show zero conflicts

## Scenario: Phase 3 wave handoff directory structure validation passes
  @skip
  Given wave handoff infrastructure has been created
  And directory structure follows the defined pattern
  When quality gate validation runs for Phase 3
  Then docs/features/framework-rationalization directories exist
  And all expected subdirectories (00-discuss through 04-develop) exist
  And handoff artifacts are in correct locations
  And index files reference all phases correctly
  And cross-phase traceability is maintained

## Scenario: Phase 4 pre-commit hook validation passes
  @skip
  Given pre-commit hooks have been implemented
  And hooks validate framework structure requirements
  When quality gate validation runs for Phase 4
  Then hooks detect command template violations
  And hooks catch embedded workflow patterns
  And hooks validate ORCHESTRATOR BRIEFING presence
  And hooks warn about non-compliant new files
  And hook validation can be bypassed only with explicit override

## Scenario: Phase 5 release packaging validation passes
  @skip
  Given release packaging has been configured
  And checksums have been generated for artifacts
  When quality gate validation runs for Phase 5
  Then release tarball contains all required files
  And checksum validation passes for all artifacts
  And version information is consistent
  And release notes document changes accurately
  And packaging process is repeatable

## Scenario: Phase 6 CI/CD workflow validation passes
  @skip
  Given CI/CD workflows have been implemented
  And workflows run framework validation automatically
  When quality gate validation runs for Phase 6
  Then GitHub Actions workflows execute successfully
  And command template validation step passes
  And agent specification validation step passes
  And pre-commit hook testing passes
  And CI/CD reports clear success status

## Scenario: All quality gates pass before DEVELOP wave handoff
  @skip
  Given all Phase 0-6 validations have completed successfully
  And all acceptance criteria from all phases are satisfied
  And all tests are executable and initially failing
  And tests use business language understandable by stakeholders
  When the quality gate validator aggregates all results
  Then all 6 phases show PASSED status
  And no critical violations remain
  And DEVELOP wave handoff is authorized
  And framework is ready for outside-in TDD development

---

# Production Integration Validation Phase

## Scenario: Service provider pattern implemented correctly
  @skip
  Given step definitions have been created for acceptance tests
  When step method implementation is validated
  Then each step method contains _serviceProvider.GetRequiredService calls
  And no step method implements business logic directly
  And all service dependencies are properly injected
  And step methods delegate all operations to production services
  And production service call validation passes

## Scenario: Test infrastructure boundaries enforced
  @skip
  Given test infrastructure and step definitions exist
  When test infrastructure validation runs
  Then no business logic exists in test setup/teardown
  And test infrastructure contains only setup and cleanup code
  And test data builders use production services to create data
  And no direct database manipulation in test infrastructure
  And anti-pattern detection confirms no infrastructure deception

## Scenario: Build system uses real implementations
  @skip
  Given build system and platform abstraction have been implemented
  When production integration validation runs
  Then build system is a real implementation, not a mock
  And platform formatters are real implementations, not stubs
  And integration between formatter and build occurs naturally
  And no test doubles replace core domain services
  And production code path execution is verified

## Scenario: External system boundaries properly mocked
  @skip
  Given the test environment has been configured
  When external system integration is validated
  Then only external service boundaries use test doubles
  And external service mocks simulate realistic behavior
  And mock boundaries are clearly documented
  And internal application services use real implementations
  And integration with real services is validated

## Scenario: Tests fail when production services unavailable
  @skip
  Given acceptance tests with production service dependencies
  When production services become unavailable
  Then tests fail with clear error messages
  And failures indicate missing service dependencies
  And test failure provides diagnostic information
  And no tests pass silently with mocked alternatives
  And real system behavior is validated through service availability

## Scenario: Production service integration validated
  Given step methods and test infrastructure have been implemented
  When production integration validation runs
  Then service provider pattern is consistently applied
  And no business logic exists in test infrastructure
  And all production services are real implementations
  And only external boundaries use test doubles
  And tests fail when production services are unavailable
