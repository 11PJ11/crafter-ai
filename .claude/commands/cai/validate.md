# /cai:validate - Comprehensive Quality Validation

```yaml
---
command: "/cai:validate"
category: "Quality & Validation"
purpose: "Comprehensive quality validation and compliance checking"
argument-hint: "[target] --full --security --performance --threshold strict"
wave-enabled: true
performance-profile: "complex"
---
```

## Overview

Comprehensive quality validation system orchestrating multiple specialized validators for code quality, architecture compliance, security, performance, and production readiness.

## Auto-Persona Activation
- **Commit Readiness Coordinator**: Validation orchestration (mandatory)
- **QA**: Quality assurance and testing validation (mandatory)
- **Security**: Security compliance validation (conditional)
- **Performance**: Performance validation (conditional)
- **Architect**: Architecture compliance validation (conditional)

## MCP Server Integration
- **Primary**: Sequential (systematic validation analysis and reporting)
- **Secondary**: Playwright (E2E testing and performance validation)
- **Tertiary**: Context7 (validation patterns and compliance standards)

## Tool Orchestration
- **Task**: Specialized validator agents activation
- **Bash**: Test execution, static analysis, and build validation
- **Read**: Code analysis and documentation validation
- **Grep**: Pattern detection and compliance checking
- **Write**: Validation reports and compliance documentation

## Agent Flow
```yaml
commit-readiness-coordinator:
  validation_orchestration:
    - Coordinates all validation processes
    - Enforces commit requirements and quality gates
    - Manages validator dependencies and sequencing
    - Provides comprehensive validation reporting

specialized_validators:
  code-quality-validator:
    - Static analysis and code quality metrics
    - Complexity analysis and maintainability assessment
    - Naming conventions and formatting compliance
    - Code smell detection and refactoring recommendations

  architecture-compliance-validator:
    - Component boundary enforcement validation
    - API contract compliance checking
    - Architectural pattern adherence verification
    - Dependency rule compliance validation

  security-performance-validator:
    - Security vulnerability scanning and assessment
    - Performance benchmark validation and regression detection
    - Resource usage analysis and optimization recommendations
    - Compliance with security and performance standards

  test-execution-validator:
    - Comprehensive test suite execution
    - Test coverage analysis and reporting
    - Test quality assessment and improvement recommendations
    - ATDD compliance validation
```

## Command Execution Pattern

### Activation Instructions
When this command is invoked:
1. Parse validation scope and quality requirements
2. Invoke commit-readiness-coordinator agent for orchestration
3. Chain to specialized validators based on focus areas
4. Execute comprehensive quality validation gates
5. Return validation report with commit readiness status

### Agent Invocation Workflow
```yaml
execution-flow:
  step1-coordination:
    agent: commit-readiness-coordinator
    task: |
      Orchestrate comprehensive validation process:
      - Validation Scope: {parsed_scope}
      - Focus Areas: {focus_areas_if_specified}
      - Continue on Error: {continue_flag_status}

      Execute validation coordination including:
      - Orchestrate all validation processes systematically
      - Coordinate specialized validators based on scope
      - Enforce final commit requirements and quality gates
      - Provide commit readiness assessment

  step2-specialized-validators:
    parallel-agents:
      code-quality-validator:
        condition: scope includes quality || comprehensive
        task: |
          Validate code quality standards:
          - Static analysis and formatting compliance
          - Complexity metrics and naming conventions
          - Code quality standards enforcement

      architecture-compliance-validator:
        condition: scope includes architecture || comprehensive
        task: |
          Validate architectural compliance:
          - Component boundaries and API contracts
          - Architectural pattern adherence
          - Hexagonal architecture compliance

      security-performance-validator:
        condition: scope includes security || performance || comprehensive
        task: |
          Validate security and performance standards:
          - Security vulnerability assessment
          - Performance benchmark validation
          - Compliance with security standards

      test-execution-validator:
        condition: scope includes tests || comprehensive
        task: |
          Validate comprehensive test execution:
          - Acceptance, unit, and integration test execution
          - ATDD compliance validation
          - Test coverage and quality assessment

  step3-integration:
    agent: production-service-integrator
    task: |
      Validate production service integration:
      - Ensure step methods call production services
      - Prevent test infrastructure deception
      - Validate production code path coverage
      - Confirm real system integration
```

### Arguments Processing
- Parse `[scope]` argument for validation coverage
- Apply `--full`, `--security`, `--architecture` flags to validator selection
- Process `--continue-on-error`, `--strict` flags for error handling
- Enable parallel validation execution for efficiency

### Output Generation
Return comprehensive validation report including:
- Commit readiness status with detailed validation results
- Specialized validation reports (quality, architecture, security, tests)
- Production service integration validation
- Actionable recommendations for any validation failures

## 📖 Complete Documentation

For comprehensive usage examples, validation frameworks, quality gates, and detailed configuration options:

```bash
/cai:man validate                    # Full manual with all examples
/cai:man validate --examples         # Usage examples only
/cai:man validate --flags           # All flags and options
```

The manual includes:
- **Validation Scopes**: `--full`, `--security`, `--performance`, `--quality`, `--architecture`, `--tests`
- **Quality Thresholds**: `--threshold strict|standard|minimal`, custom coverage and complexity settings
- **Domain-Specific Validation**: `--atdd`, `--tdd`, `--production`, `--compliance [standard]`
- **Comprehensive Examples**: Production readiness, compliance validation, development workflows
- **Quality Gates**: Code quality, architecture compliance, security, performance frameworks
- **Integration Patterns**: Pre-commit validation, CI/CD integration, ATDD workflow validation