# /cai:validate - Comprehensive Quality Validation

```yaml
---
command: "/cai:validate"
category: "Quality & Validation"
purpose: "Comprehensive quality validation and compliance checking"
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

## Arguments

### Basic Usage
```bash
/cai:validate [scope]
```

### Advanced Usage
```bash
/cai:validate [scope] --full --focus <domain> --threshold <level> --report
```

### Validation Scope
- `--full`: Complete project validation across all domains
  - Executes comprehensive validation across quality, security, performance, architecture, and tests
  - Provides holistic project health assessment with detailed cross-domain analysis
  - Includes production readiness validation and compliance checking
  - Generates executive summary with critical issues and improvement roadmap
- `--security`: Focus on security compliance and vulnerability assessment
  - Performs comprehensive security vulnerability scanning and threat assessment
  - Validates authentication, authorization, and data protection implementations
  - Checks compliance with security standards (OWASP, NIST, industry-specific)
  - Includes input validation, encryption, and secure coding practice verification
- `--performance`: Focus on performance validation and optimization
  - Executes performance benchmarking and load testing validation
  - Analyzes response times, resource usage, and scalability characteristics
  - Validates performance against defined SLAs and quality gates
  - Includes database performance, caching effectiveness, and optimization recommendations
- `--quality`: Focus on code quality and maintainability
  - Performs static analysis, complexity assessment, and maintainability evaluation
  - Validates coding standards, naming conventions, and formatting compliance
  - Includes code smell detection and refactoring recommendations
  - Analyzes technical debt and provides improvement prioritization
- `--architecture`: Focus on architectural compliance and patterns
  - Validates component boundaries, API contracts, and architectural pattern adherence
  - Checks hexagonal architecture compliance and dependency rule enforcement
  - Verifies integration patterns and data flow compliance
  - Includes architectural decision validation and pattern consistency checking
- `--tests`: Focus on test execution and coverage validation
  - Executes comprehensive test suite with coverage analysis and quality assessment
  - Validates unit, integration, and E2E test effectiveness and reliability
  - Includes mutation testing for test quality validation and improvement suggestions
  - Checks ATDD compliance and business validation effectiveness

### Quality Thresholds
- `--threshold strict`: Highest quality standards (production-ready)
  - Enforces production-ready quality gates with zero tolerance for critical issues
  - Requires ≥90% test coverage, complexity limits, and zero security vulnerabilities
  - Applies strict performance requirements and architectural compliance
  - Suitable for mission-critical systems and production deployments
- `--threshold standard`: Standard quality requirements
  - Applies balanced quality gates suitable for most development scenarios
  - Requires ≥80% test coverage with reasonable complexity and performance limits
  - Allows low-severity issues with improvement recommendations
  - Provides good balance between quality assurance and development velocity
- `--threshold minimal`: Minimum viable quality gates
  - Enforces basic quality requirements for development and testing environments
  - Requires ≥70% test coverage with relaxed complexity and performance limits
  - Focuses on critical issues while allowing minor quality debt
  - Suitable for rapid development phases and experimental features
- `--coverage [percentage]`: Specific test coverage requirements
  - Sets custom test coverage thresholds for line, branch, and function coverage
  - Supports different coverage requirements for unit, integration, and E2E tests
  - Provides detailed coverage analysis and gap identification
  - Examples: --coverage 85 (overall), --coverage unit:90,integration:75
- `--complexity [level]`: Maximum complexity thresholds
  - Sets custom cyclomatic and cognitive complexity limits for methods and classes
  - Provides complexity analysis and refactoring recommendations for violations
  - Supports different complexity thresholds based on component criticality
  - Examples: --complexity 10 (cyclomatic), --complexity cognitive:15

### Validation Control
- `--fail-fast`: Stop validation on first critical failure
  - Terminates validation process immediately upon encountering critical issues
  - Provides rapid feedback for blocking issues requiring immediate attention
  - Optimizes validation time by avoiding unnecessary checks after critical failures
  - Suitable for CI/CD pipelines where early failure detection is preferred
- `--continue-on-error`: Continue validation despite non-critical failures
  - Continues validation process even when non-critical issues are encountered
  - Provides comprehensive validation report with all identified issues
  - Allows assessment of overall project health despite individual component issues
  - Suitable for comprehensive quality assessment and improvement planning
- `--report`: Generate comprehensive validation report
  - Creates detailed validation report with executive summary and technical details
  - Includes quality metrics, compliance status, and improvement recommendations
  - Provides machine-readable results for integration with quality dashboards
  - Generates both human-readable and automated processing formats
- `--fix-suggestions`: Include automated fix suggestions
  - Provides specific, actionable recommendations for identified quality issues
  - Includes code examples and refactoring suggestions for common problems
  - Suggests automated tools and techniques for issue resolution
  - Prioritizes suggestions based on impact and implementation effort

### Domain-Specific Validation
- `--atdd`: ATDD methodology compliance validation
  - Validates outside-in TDD implementation and double-loop architecture compliance
  - Checks customer collaboration evidence and executable specification quality
  - Ensures business language usage and natural test progression
  - Validates real system integration and production service invocation
- `--tdd`: TDD practice validation and test quality assessment
  - Validates proper TDD cycle implementation (RED→GREEN→REFACTOR)
  - Assesses test quality, independence, and effectiveness through mutation testing
  - Checks test-first development evidence and continuous refactoring application
  - Includes test coverage analysis and improvement recommendations
- `--production`: Production readiness validation
  - Comprehensive validation for production deployment readiness
  - Includes security, performance, reliability, and compliance validation
  - Validates monitoring, logging, error handling, and recovery mechanisms
  - Checks deployment automation, rollback procedures, and operational readiness
- `--compliance [standard]`: Specific compliance standard validation
  - Validates against specific industry standards (OWASP, SOC2, HIPAA, PCI-DSS)
  - Includes regulatory compliance checking and audit trail validation
  - Provides compliance gap analysis and remediation recommendations
  - Examples: --compliance OWASP, --compliance SOC2, --compliance GDPR

## Validation Framework

### Code Quality Validation
```yaml
static_analysis:
  tools: ["SonarQube", "ESLint", "RuboCop", "Pylint"]
  metrics:
    - cyclomatic_complexity: "Maximum complexity per method/function"
    - cognitive_complexity: "Human readability complexity assessment"
    - duplication_ratio: "Code duplication percentage"
    - maintainability_index: "Overall maintainability score"

formatting_compliance:
  standards: ["Prettier", "Black", "Go fmt", "Rustfmt"]
  validation:
    - consistent_indentation: "Consistent spacing and indentation"
    - naming_conventions: "Consistent naming patterns"
    - import_organization: "Proper import/require statement organization"
    - comment_standards: "Documentation comment compliance"

code_smell_detection:
  categories: ["Bloaters", "Object-Orientation Abusers", "Change Preventers", "Dispensables", "Couplers"]
  severity_levels: ["Critical", "High", "Medium", "Low"]
  refactoring_recommendations: "Specific refactoring technique suggestions"
```

### Architecture Compliance Validation
```yaml
boundary_enforcement:
  hexagonal_architecture: "Port/adapter pattern compliance"
  layer_violations: "Dependency direction compliance"
  component_isolation: "Component boundary respect"
  api_contract_compliance: "Interface contract adherence"

pattern_adherence:
  design_patterns: "Proper implementation of documented patterns"
  architectural_constraints: "Compliance with architectural decisions"
  integration_patterns: "Proper external system integration"
  data_flow_compliance: "Data flow pattern adherence"

dependency_validation:
  dependency_rules: "Dependency direction and isolation rules"
  circular_dependencies: "Circular dependency detection"
  unused_dependencies: "Unused dependency identification"
  version_compatibility: "Dependency version compatibility"
```

### Security and Performance Validation
```yaml
security_validation:
  vulnerability_scanning: "Known vulnerability detection"
  authentication_patterns: "Authentication implementation validation"
  authorization_enforcement: "Authorization pattern compliance"
  data_protection: "Sensitive data handling validation"
  input_validation: "Input sanitization and validation"

performance_validation:
  response_time_benchmarks: "API response time validation"
  resource_usage_analysis: "Memory and CPU usage assessment"
  scalability_testing: "Load testing and capacity validation"
  database_performance: "Query performance and optimization"
  caching_effectiveness: "Cache hit ratios and effectiveness"
```

### Test Validation Framework
```yaml
test_execution:
  unit_tests: "Individual component behavior validation"
  integration_tests: "Component interaction validation"
  e2e_tests: "End-to-end user workflow validation"
  mutation_tests: "Test quality and effectiveness validation"

coverage_analysis:
  line_coverage: "Code line execution coverage"
  branch_coverage: "Conditional branch coverage"
  function_coverage: "Function/method coverage"
  integration_coverage: "Integration point coverage"

test_quality_assessment:
  test_independence: "Test isolation and independence"
  test_clarity: "Test readability and maintainability"
  test_performance: "Test execution speed and efficiency"
  test_reliability: "Test consistency and reliability"
```

## Quality Gates and Thresholds

### Production-Ready Quality Gates
```yaml
code_quality_gates:
  test_coverage: "≥80% unit tests, ≥70% integration tests"
  complexity_limits: "Cyclomatic complexity ≤10, cognitive complexity ≤15"
  duplication_threshold: "≤3% code duplication"
  security_vulnerabilities: "Zero critical, zero high-severity vulnerabilities"

performance_gates:
  response_time: "≤200ms API responses, ≤3s page load times"
  error_rate: "≤0.1% error rate for critical operations"
  resource_usage: "Memory usage within defined limits"
  scalability_targets: "Meets defined load and concurrency requirements"

architecture_gates:
  boundary_compliance: "100% architectural boundary compliance"
  dependency_compliance: "No circular dependencies, proper layering"
  pattern_adherence: "Consistent implementation of architectural patterns"
  documentation_alignment: "Implementation matches architectural documentation"
```

### ATDD Compliance Validation
```yaml
atdd_methodology_gates:
  customer_collaboration: "Evidence of customer/stakeholder collaboration"
  executable_specifications: "Acceptance tests serve as executable specifications"
  business_language: "Tests use ubiquitous domain language"
  outside_in_evidence: "Evidence of outside-in development approach"

test_quality_gates:
  real_system_integration: "E2E tests call production services, not test doubles"
  production_service_validation: "Step methods invoke actual production services"
  natural_test_progression: "Tests pass through sufficient implementation, not modification"
  business_validation: "Tests validate business outcomes, not implementation details"
```

## Validation Reporting

### Comprehensive Validation Report
- **Executive Summary**: High-level quality assessment and critical issues
- **Quality Metrics**: Detailed metrics across all validation domains
- **Compliance Status**: Compliance with standards and quality gates
- **Risk Assessment**: Identified risks and recommended mitigation strategies
- **Improvement Recommendations**: Specific actions for quality improvement

### Domain-Specific Reports
- **Code Quality Report**: Static analysis results and improvement suggestions
- **Security Assessment**: Vulnerability analysis and security recommendations
- **Performance Report**: Performance metrics and optimization opportunities
- **Architecture Review**: Architectural compliance and pattern adherence
- **Test Quality Report**: Test coverage, quality, and effectiveness analysis

## Output Artifacts

### Validation Results
- `${DOCS_PATH}/validation-report.md`: Comprehensive validation report
- `${DOCS_PATH}/quality-metrics.md`: Detailed quality metrics and trends
- `${DOCS_PATH}/compliance-status.md`: Compliance status and requirements
- `${STATE_PATH}/validation-results.json`: Machine-readable validation results

### Improvement Guidance
- **Quality Improvement Plan**: Prioritized improvement recommendations
- **Refactoring Suggestions**: Specific refactoring techniques and priorities
- **Security Hardening Guide**: Security improvement recommendations
- **Performance Optimization Plan**: Performance improvement strategies

## Examples

### Comprehensive Project Validation
```bash
/cai:validate --full --report --threshold strict
```

### Security-Focused Validation
```bash
/cai:validate --security --compliance OWASP --fail-fast
```

### Performance Validation
```bash
/cai:validate --performance --threshold standard --fix-suggestions
```

### Pre-Production Validation
```bash
/cai:validate --production --atdd --coverage 85 --report
```

### Development Quality Check
```bash
/cai:validate --quality --architecture --continue-on-error
```

## Comprehensive Usage Examples

### Production Readiness Validation
```bash
# Complete production readiness validation with strict requirements
/cai:validate --production --full --threshold strict --report --fail-fast

# Production validation with specific compliance requirements
/cai:validate --production --security --compliance SOC2 --threshold strict --report

# Production readiness with performance and security focus
/cai:validate --production --performance --security --coverage 90 --complexity 8 --report

# ATDD production validation with methodology compliance
/cai:validate --production --atdd --tdd --threshold strict --fix-suggestions --report
```

### Domain-Specific Validation Focus
```bash
# Security-first validation with comprehensive compliance
/cai:validate --security --compliance OWASP --compliance GDPR --threshold strict --fail-fast

# Performance validation with custom thresholds
/cai:validate --performance --threshold standard --coverage 85 --fix-suggestions --report

# Code quality validation with technical debt analysis
/cai:validate --quality --complexity 10 --coverage 80 --continue-on-error --fix-suggestions

# Architecture compliance validation
/cai:validate --architecture --threshold standard --continue-on-error --report

# Comprehensive test validation with mutation testing
/cai:validate --tests --atdd --tdd --coverage 85 --threshold standard --fix-suggestions
```

### Quality Threshold Combinations
```bash
# Strict validation for critical systems
/cai:validate --full --threshold strict --coverage 95 --complexity 8 --fail-fast --report

# Standard development validation
/cai:validate --quality --tests --threshold standard --coverage 80 --continue-on-error --fix-suggestions

# Minimal validation for rapid development
/cai:validate --quality --threshold minimal --coverage 70 --continue-on-error --report

# Custom threshold validation for specific requirements
/cai:validate --full --coverage unit:90,integration:75,e2e:60 --complexity cognitive:12 --report
```

### ATDD and TDD Methodology Validation
```bash
# ATDD methodology compliance validation
/cai:validate --atdd --production --threshold strict --coverage 85 --fail-fast

# TDD practice validation with test quality assessment
/cai:validate --tdd --tests --coverage 90 --fix-suggestions --report --continue-on-error

# Combined ATDD/TDD validation for comprehensive methodology compliance
/cai:validate --atdd --tdd --quality --architecture --threshold standard --report

# Outside-in TDD validation with real system integration check
/cai:validate --atdd --production --security --threshold strict --report --fail-fast
```

### Compliance and Regulatory Validation
```bash
# Financial services compliance validation
/cai:validate --security --compliance PCI-DSS --compliance SOX --threshold strict --report --fail-fast

# Healthcare compliance validation
/cai:validate --full --compliance HIPAA --compliance GDPR --security --threshold strict --report

# General web application security compliance
/cai:validate --security --compliance OWASP --performance --threshold standard --fix-suggestions

# Multi-standard compliance validation
/cai:validate --full --compliance OWASP --compliance SOC2 --compliance ISO27001 --threshold strict --report
```

### Development Workflow Validation
```bash
# Pre-commit validation with fail-fast for rapid feedback
/cai:validate --quality --tests --architecture --fail-fast --threshold standard

# Continuous integration validation
/cai:validate --full --threshold standard --coverage 80 --continue-on-error --report

# Code review preparation validation
/cai:validate --quality --architecture --security --fix-suggestions --report --continue-on-error

# Sprint completion validation
/cai:validate --full --atdd --threshold standard --coverage 85 --report --fix-suggestions
```

### Error Handling and Reporting Strategies
```bash
# Comprehensive validation with detailed reporting
/cai:validate --full --report --fix-suggestions --continue-on-error --threshold standard

# Fail-fast validation for CI/CD pipelines
/cai:validate --quality --tests --security --fail-fast --threshold standard

# Detailed analysis with improvement suggestions
/cai:validate --quality --architecture --performance --fix-suggestions --report --continue-on-error

# Executive reporting for stakeholder review
/cai:validate --full --report --threshold strict --continue-on-error
```

### Performance and Scalability Validation
```bash
# Performance benchmarking with strict requirements
/cai:validate --performance --threshold strict --report --fail-fast

# Scalability validation with load testing
/cai:validate --performance --production --coverage 85 --report --continue-on-error

# Performance optimization validation
/cai:validate --performance --quality --fix-suggestions --threshold standard --report

# Combined performance and security validation
/cai:validate --performance --security --production --threshold strict --report
```

### Legacy System Validation
```bash
# Legacy system quality assessment
/cai:validate --quality --architecture --threshold minimal --continue-on-error --fix-suggestions --report

# Legacy security validation
/cai:validate --security --compliance OWASP --threshold standard --continue-on-error --report

# Legacy modernization readiness validation
/cai:validate --full --threshold standard --coverage 70 --fix-suggestions --report --continue-on-error

# Legacy system production validation
/cai:validate --production --security --performance --threshold standard --report --continue-on-error
```

### Integration Workflow Examples
```bash
# Pre-development validation
/cai:validate --architecture --quality --threshold standard --continue-on-error --report
/cai:develop "new-feature" --outside-in --validate --real-system

# Post-development validation before deployment
/cai:develop "feature-implementation" --validate --tdd-mode strict
/cai:validate --full --production --threshold strict --report --fail-fast

# Refactoring validation workflow
/cai:validate --quality --architecture --threshold standard --report
/cai:refactor "target-code" --level 1-4 --validate --rollback
/cai:validate --quality --tests --threshold standard --report

# Complete ATDD validation workflow
/cai:discuss "requirements" --stories --acceptance --stakeholders business,technical
/cai:develop "implementation" --atdd --outside-in --validate --real-system
/cai:validate --atdd --production --threshold strict --report
```

### Team and Process Validation
```bash
# Team development standards validation
/cai:validate --quality --tests --architecture --threshold standard --fix-suggestions --report

# Code quality mentoring validation
/cai:validate --quality --coverage 80 --complexity 10 --fix-suggestions --continue-on-error

# Process compliance validation
/cai:validate --atdd --tdd --production --threshold standard --report --continue-on-error

# Quality improvement tracking validation
/cai:validate --full --report --fix-suggestions --continue-on-error --threshold standard
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