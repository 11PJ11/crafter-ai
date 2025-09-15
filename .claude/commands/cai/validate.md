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
- `--security`: Focus on security compliance and vulnerability assessment
- `--performance`: Focus on performance validation and optimization
- `--quality`: Focus on code quality and maintainability
- `--architecture`: Focus on architectural compliance and patterns
- `--tests`: Focus on test execution and coverage validation

### Quality Thresholds
- `--threshold strict`: Highest quality standards (production-ready)
- `--threshold standard`: Standard quality requirements
- `--threshold minimal`: Minimum viable quality gates
- `--coverage [percentage]`: Specific test coverage requirements
- `--complexity [level]`: Maximum complexity thresholds

### Validation Control
- `--fail-fast`: Stop validation on first critical failure
- `--continue-on-error`: Continue validation despite non-critical failures
- `--report`: Generate comprehensive validation report
- `--fix-suggestions`: Include automated fix suggestions

### Domain-Specific Validation
- `--atdd`: ATDD methodology compliance validation
- `--tdd`: TDD practice validation and test quality assessment
- `--production`: Production readiness validation
- `--compliance [standard]`: Specific compliance standard validation

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

ARGUMENTS: create the commands under the @.claude\commands\cai\ folder so we can install them together with the rest