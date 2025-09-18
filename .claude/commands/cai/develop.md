# /cai:develop - Outside-In TDD Implementation (Wave 4)

```yaml
---
command: "/cai:develop"
category: "Development & Implementation"
purpose: "Outside-In TDD implementation of user stories"
argument-hint: "[story-id] --outside-in --real-system --validate"
wave-enabled: true
performance-profile: "standard"
---
```

## Overview

Comprehensive Outside-In Test-Driven Development implementation following the double-loop TDD architecture for ATDD Wave 4 (DEVELOP phase).

## Auto-Persona Activation
- **Test-First Developer**: Outside-In TDD implementation (mandatory)
- **QA**: Testing strategy and quality validation (conditional)
- **Refactorer**: Code quality and refactoring (automatic)
- **Security**: Security implementation patterns (conditional)

## MCP Server Integration
- **Primary**: Sequential (structured TDD workflow and systematic implementation)
- **Secondary**: Context7 (implementation patterns and framework best practices)
- **Tertiary**: Magic (UI component implementation)

## Tool Orchestration
- **Read**: Story context and acceptance criteria analysis
- **Write**: Test and production code creation
- **Edit**: Code refinement and updates
- **MultiEdit**: Batch code changes across related files
- **Bash**: Test execution and validation
- **Task**: Sub-implementation delegation for complex stories

## Agent Flow
```yaml
test-first-developer:
  outer_loop_atdd:
    - Creates failing E2E acceptance test first (RED)
    - Represents user-facing feature from business perspective
    - Uses given().when().then() fluent API for business language
    - "Write the Code You Wish You Had" interface design

  inner_loop_utdd:
    - Steps down to unit test when E2E test fails
    - Creates failing unit test for smallest behavior (RED)
    - Implements minimal code to make unit test pass (GREEN)
    - Refactors continuously while keeping tests green (REFACTOR)
    - Returns to E2E test to verify progress

systematic-refactorer:
  continuous_refactoring:
    - Level 1-2 refactoring during each GREEN phase
    - Readability and complexity improvements
    - Domain-driven naming and clean code practices
    - Maintains architectural alignment throughout development
```

## Arguments

### Basic Usage
```bash
/cai:develop [story-id]
```

### Advanced Usage
```bash
/cai:develop [story-id] --outside-in --tdd-mode <mode> --one-scenario --validate
```

### Story Identification
- `[story-id]`: Specific story identifier (e.g., "STORY-AUTH-001")
- `@story-path`: Path to story file with embedded context
- `--epic [epic-id]`: Develop all stories within an epic

### TDD Methodology Control
- `--outside-in`: Enforce Outside-In TDD methodology (default)
  - Start with E2E acceptance tests representing user-facing features
  - Step down to unit tests when E2E tests fail (proper inner loop)
  - Focus on business behavior rather than technical implementation details
  - Ensure natural test progression from acceptance to unit level
- `--double-loop`: Explicit double-loop TDD architecture
  - Outer loop: ATDD/E2E tests for customer validation and business outcomes
  - Inner loop: Unit TDD for developer implementation and technical details
  - Systematic progression between loops with clear boundaries and responsibilities
  - Maintains business focus while enabling detailed technical implementation
- `--one-scenario`: Implement one E2E scenario at a time (recommended)
  - Prevents overwhelming NotImplementedException cascades during development
  - Enables clean commits with working implementation at each step
  - Maintains focus and reduces cognitive load for complex features
  - Follows proper Outside-In TDD scope management principles
- `--real-system`: Ensure step methods call production services
  - Prevents test infrastructure deception where tests pass without real implementation
  - Validates that step methods invoke actual production services via dependency injection
  - Ensures production code paths are exercised rather than test doubles
  - Critical for authentic ATDD implementation and production readiness

### Development Approach
- `--tdd-mode strict`: Strict RED→GREEN→REFACTOR cycles with no shortcuts
  - Rigorous TDD with no production code without failing tests first
  - Enforces proper cycle discipline and prevents implementation shortcuts
  - Maximum learning and design benefits from TDD methodology
- `--tdd-mode guided`: Guided TDD with scaffolding support and education
  - Provides TDD mentoring and educational guidance throughout development
  - Includes explanations of TDD decisions and methodology benefits
  - Suitable for teams learning TDD or complex domain modeling
- `--tdd-mode natural`: Natural test progression without forcing artificial failures
  - Allows natural progression when tests would naturally fail
  - Balances TDD benefits with pragmatic development efficiency
  - Suitable for experienced TDD practitioners and well-understood domains

### Quality Control
- `--validate`: Add comprehensive validation steps throughout development
  - Validates step methods call production services not test infrastructure
  - Ensures architectural compliance and hexagonal boundaries
  - Applies quality gates at each development phase with rollback capability
  - Includes continuous validation of test quality and effectiveness
- `--mutation-testing`: Include mutation testing validation for test effectiveness
  - Validates test quality by introducing code mutations and checking test failures
  - Ensures tests actually validate business logic rather than implementation details
  - Achieves target kill rates (≥75-80%) before considering development complete
  - Identifies weak tests and missing edge case coverage
- `--coverage [threshold]`: Set test coverage requirements with business focus
  - Sets minimum code coverage thresholds (default: 80% line, 90% branch)
  - Focuses on meaningful coverage of business logic paths
  - Excludes infrastructure and framework code from coverage requirements
  - Combines with mutation testing for comprehensive test quality assessment
- `--refactor-level [1-3]`: Specify refactoring intensity during development

## Outside-In TDD Process

### Double-Loop TDD Architecture
```yaml
outer_loop_atdd:
  description: "Customer perspective - business behavior validation"
  cycle: "E2E Test (RED) → Implementation → E2E Test (GREEN)"
  focus: "Business outcomes and user workflows"
  language: "Business-focused Given-When-Then scenarios"

inner_loop_utdd:
  description: "Developer perspective - technical implementation"
  cycle: "Unit Test (RED) → Code (GREEN) → Refactor"
  focus: "Technical implementation and design"
  language: "Technical behavior specification"
```

### Implementation Sequence
1. **🔴 Failing E2E Acceptance Test** (Outer Loop Start)
   - Create E2E test representing user-facing feature
   - Use business language and real system integration
   - Test MUST fail initially - acts as executable specification

2. **🔄 Inner Unit Test Loop** (Inner Loop)
   - Step down to unit test when E2E fails
   - Write failing unit test for smallest behavior
   - Implement minimal code to pass unit test
   - **Continuous Refactoring** during GREEN phase
   - Return to E2E test to check progress

3. **✅ E2E Test Passes** (Outer Loop Complete)
   - E2E test passes naturally through implementation
   - Move to next E2E scenario (one at a time)

### ATDD Quality Gates
```yaml
e2e_test_requirements:
  - Must call actual production services via dependency injection
  - Must avoid test infrastructure deception
  - Must use business language in test scenarios
  - Must validate real system behavior, not mocks

step_method_requirements:
  - Must invoke production services: `_serviceProvider.GetRequiredService<T>()`
  - Must avoid direct test infrastructure calls for business logic
  - Must demonstrate production code path coverage
  - Must use NotImplementedException for unimplemented collaborators

scaffolding_patterns:
  - Use NotImplementedException with clear descriptions
  - Apply "Write the Code You Wish You Had" pattern
  - Create natural interfaces during test writing
  - Maintain implementation pressure through proper failures
```

## Story Context Integration

### Hyper-Detailed Story Processing
- **Business Context**: User story and acceptance criteria
- **Architectural Context**: System components and integration points
- **Implementation Guidance**: Step-by-step development approach
- **Validation Criteria**: Detailed acceptance tests and quality gates

### Context Embedding
- **Self-Contained Stories**: All implementation guidance embedded
- **Architectural Integration**: Relevant architecture patterns included
- **Error Prevention**: Common pitfalls and prevention guidance
- **Quality Requirements**: Specific quality gates and validation criteria

## Test Strategy

### E2E Test Management
```yaml
one_scenario_rule:
  description: "Enable ONE E2E test at a time to prevent commit blocks"
  implementation: "Use [Ignore] attribute for unimplemented scenarios"
  rationale: "Maintains clean development workflow and prevents overwhelming failures"
  commit_safety: "Ensures commits always have passing tests"
```

### Test Quality Validation
- **Mutation Testing**: ≥75-80% kill rate for test effectiveness
- **Coverage Requirements**: ≥90% unit test coverage, ≥70% integration coverage
- **Business Validation**: Tests validate business outcomes, not implementation details
- **Refactoring Safety**: Tests survive refactoring without modification

## Quality Gates

### Development Quality
- **TDD Compliance**: Proper RED→GREEN→REFACTOR cycles followed
- **Test Quality**: Comprehensive test coverage with high mutation kill rate
- **Code Quality**: Clean, readable code with domain-driven naming
- **Architectural Alignment**: Code follows architectural patterns and constraints

### Production Integration
- **Real System Calls**: Step methods invoke actual production services
- **Service Integration**: Proper dependency injection and service layer usage
- **Infrastructure Avoidance**: No business logic in test infrastructure
- **Production Readiness**: Implementation works in production environment

### ATDD Compliance
- **Customer Collaboration**: Business stakeholder feedback incorporated
- **Executable Specification**: Tests serve as living documentation
- **Business Language**: Tests use ubiquitous domain language
- **Natural Progression**: Tests pass naturally through sufficient implementation

## Output Artifacts

### Implementation Code
- **Production Code**: Business logic implementation following TDD
- **Test Code**: Comprehensive test suite with E2E and unit tests
- **Integration Code**: Service integrations and external system connections

### Development Documentation
- **Implementation Notes**: Key decisions and trade-offs during development
- **Test Results**: Test execution results and coverage reports
- **Refactoring Log**: Continuous refactoring improvements applied
- **Quality Metrics**: Code quality, complexity, and maintainability metrics

## Examples

### Standard Story Implementation
```bash
/cai:develop "STORY-AUTH-001" --outside-in --one-scenario
```

### High-Quality Implementation
```bash
/cai:develop "STORY-PAYMENT-005" --validate --mutation-testing --coverage 90
```

### UI Component Implementation
```bash
/cai:develop "STORY-DASHBOARD-003" --outside-in --refactor-level 2
```

### Complex Integration Story
```bash
/cai:develop "STORY-INTEGRATION-007" --real-system --double-loop --validate
```

### Epic-Level Development
```bash
/cai:develop --epic "USER-MANAGEMENT" --one-scenario --tdd-mode strict
```

## Comprehensive Usage Examples

### Basic TDD Development
```bash
# Simple story development with Outside-In TDD
/cai:develop "STORY-LOGIN-001" --outside-in

# Strict TDD with comprehensive validation
/cai:develop "STORY-AUTH-002" --tdd-mode strict --validate

# Real system integration with one scenario focus
/cai:develop "STORY-PAYMENT-003" --real-system --one-scenario
```

### Advanced TDD Configurations
```bash
# Double-loop TDD with learning mode and comprehensive validation
/cai:develop "STORY-USER-REG" --double-loop --tdd-mode guided --validate --real-system

# Outside-In with mutation testing and high coverage requirements
/cai:develop "STORY-ORDER-PROCESS" --outside-in --mutation-testing --coverage 95 --one-scenario

# Natural TDD with real system integration and refactoring
/cai:develop "STORY-SEARCH" --tdd-mode natural --real-system --refactor-level 3 --validate
```

### Epic and Feature Development
```bash
# Epic-level development with systematic approach
/cai:develop --epic "USER-MANAGEMENT" --outside-in --one-scenario --tdd-mode strict --validate

# Feature development with comprehensive quality gates
/cai:develop --feature "SHOPPING-CART" --double-loop --validate --real-system --mutation-testing

# Component development with guided TDD and learning focus
/cai:develop --component "PAYMENT-PROCESSOR" --tdd-mode guided --validate --coverage 90
```

### Quality-Focused Development
```bash
# Maximum validation and quality assurance
/cai:develop "STORY-SECURITY-AUTH" --validate --real-system --mutation-testing --one-scenario --tdd-mode strict

# Learning-focused development with comprehensive guidance
/cai:develop "STORY-API-DESIGN" --tdd-mode guided --double-loop --validate --real-system --coverage 85

# Production-ready development with all quality gates
/cai:develop "STORY-CRITICAL-FEATURE" --outside-in --real-system --validate --mutation-testing --refactor-level 3
```

### Specialized Development Scenarios
```bash
# Legacy integration with careful validation
/cai:develop "STORY-LEGACY-INTEGRATION" --tdd-mode natural --real-system --validate --one-scenario

# High-risk feature with maximum quality controls
/cai:develop "STORY-FINANCIAL-CALC" --tdd-mode strict --mutation-testing --coverage 98 --validate --real-system

# UI component with behavior-driven focus
/cai:develop "STORY-USER-DASHBOARD" --outside-in --refactor-level 2 --validate --coverage 85
```

### Integration Workflow Examples
```bash
# Requirements-driven development workflow
/cai:discuss "user authentication requirements" --focus security --stories
/cai:develop "STORY-AUTH-001" --outside-in --real-system --validate --one-scenario

# Architecture-informed development
/cai:architect "authentication system" --focus security --validation
/cai:develop "STORY-AUTH-IMPL" --double-loop --real-system --tdd-mode strict --validate

# Refactoring-supported development cycle
/cai:develop "STORY-LEGACY-MOD" --outside-in --validate --one-scenario --tdd-mode natural
/cai:refactor "auth-module" --level 3 --validate --parallel-change

# Complete ATDD workflow integration
/cai:start "user notification system" --methodology atdd --interactive
/cai:discuss "notification requirements" --focus ux --interactive
/cai:architect "notification architecture" --style event-driven
/cai:develop "STORY-NOTIFY-001" --outside-in --real-system --validate --one-scenario
```

### Team Learning and Development
```bash
# TDD learning with comprehensive guidance
/cai:develop "STORY-LEARNING-001" --tdd-mode guided --double-loop --validate --coverage 80

# Pair programming simulation with validation
/cai:develop "STORY-COMPLEX-LOGIC" --tdd-mode guided --mutation-testing --validate --real-system

# Code review preparation with quality focus
/cai:develop "STORY-REVIEW-READY" --outside-in --validate --mutation-testing --refactor-level 2 --coverage 90
```

## Command Execution Pattern

### Activation Instructions
When this command is invoked:
1. Parse story context and development requirements
2. Invoke test-first-developer agent for Outside-In TDD implementation
3. Chain to systematic-refactorer agent for continuous refactoring
4. Apply double-loop TDD with real system integration
5. Return working implementation with comprehensive test coverage

### Agent Invocation Workflow
```yaml
execution-flow:
  step1-development:
    agent: test-first-developer
    task: |
      Implement feature using Outside-In TDD methodology:
      - Story ID: {parsed_story_id}
      - TDD Mode: {tdd_mode_if_specified}
      - Real System Integration: {real_system_flag_status}

      Execute Outside-In TDD including:
      - Create E2E acceptance test first (outer loop)
      - Step down to unit tests (inner TDD loop)
      - Implement production code to pass tests
      - One E2E test at a time to prevent commit blocks

  step2-refactoring:
    agent: systematic-refactorer
    task: |
      Apply continuous refactoring throughout development:
      - Review implementation from test-first-developer
      - Apply Level 1-3 refactoring during development cycles
      - Maintain clean code throughout TDD cycles
      - Ensure code reveals business intent through naming

  step3-validation:
    agent: production-validator
    task: |
      Validate production service integration:
      - Ensure step methods invoke production services
      - Prevent test infrastructure deception
      - Validate real system integration paths
      - Confirm production code path coverage
```

### Arguments Processing
- Parse `[story-id]` or story context for implementation scope
- Apply `--outside-in`, `--double-loop`, `--tdd-mode` flags to methodology
- Process `--real-system`, `--validate` flags for integration validation
- Enable `--one-scenario` mode for focused E2E test progression

### Output Generation
Return working implementation including:
- Passing E2E acceptance tests with business validation
- Comprehensive unit test coverage with behavior focus
- Production code with systematic refactoring applied
- Real system integration with production service calls