# /cai:develop - Outside-In TDD Implementation (Wave 4)

```yaml
---
command: "/cai:develop"
category: "Development & Implementation"
purpose: "Outside-In TDD implementation of user stories"
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
- `--double-loop`: Explicit double-loop TDD architecture
- `--one-scenario`: Implement one E2E scenario at a time (recommended)
- `--real-system`: Ensure step methods call production services

### Development Approach
- `--tdd-mode strict`: Strict RED→GREEN→REFACTOR cycles
- `--tdd-mode guided`: Guided TDD with scaffolding support
- `--tdd-mode natural`: Natural test progression without forcing failures

### Quality Control
- `--validate`: Add comprehensive validation steps
- `--mutation-testing`: Include mutation testing validation
- `--coverage [threshold]`: Set test coverage requirements
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

ARGUMENTS: create the commands under the @.claude\commands\cai\ folder so we can install them together with the rest