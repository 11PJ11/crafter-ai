---
agent-activation:
  required: true
  agent-id: walking-skeleton-helper
  agent-name: "Skelly"
  agent-command: "*help"
  auto-activate: true
---

**⚠️ AGENT ACTIVATION REQUIRED**

This task requires the **Skelly** agent (walking-skeleton-helper) for execution.

**To activate**: Type `@walking-skeleton-helper` in the conversation.

Once activated, use the agent's `*help` command to see available operations.

---

# SKELETON: Walking Skeleton Implementation with E2E Automation

## Overview

Execute Walking Skeleton methodology through minimal end-to-end implementation that validates architecture and reduces risk early in projects. Based on Alistair Cockburn's Walking Skeleton approach.

## Mandatory Pre-Execution Steps

1. **Architecture Foundation**: Complete initial architecture design and component identification
2. **Walking Skeleton Helper Activation**: Activate walking-skeleton-helper (Scout)
3. **DevOps Pipeline Preparation**: Establish basic CI/CD infrastructure for automated validation

## Execution Flow

### Phase 1: Walking Skeleton Strategy Design

**Primary Agent**: walking-skeleton-helper (Scout)
**Command**: `*create-skeleton`

**Walking Skeleton Methodology**:

```
🦴 SKELETON WAVE - MINIMAL E2E IMPLEMENTATION

Implement the thinnest possible slice through the entire system:
- Validates complete architecture end-to-end
- Reduces integration risk through early implementation
- Provides foundation for incremental feature development
- Establishes automated deployment and testing pipeline

Walking Skeleton connects all system components with minimal functionality.
```

**Core Principles**:

```yaml
walking_skeleton_principles:
  minimal_functionality:
    description: "Implement smallest possible feature that exercises entire system"
    implementation: "Single happy path through all architectural layers"
    validation: "Complete system integration with minimal business logic"

  end_to_end_coverage:
    description: "Touch every major component and integration point"
    implementation: "UI → API → Business Logic → Database → External Services"
    validation: "Automated tests verify complete system connectivity"

  architecture_validation:
    description: "Prove architectural decisions work in practice"
    implementation: "Real components, not mocks or stubs"
    validation: "Production-like deployment and operation"

  risk_reduction:
    description: "Identify integration issues early when changes are cheap"
    implementation: "Real infrastructure, real deployment pipeline"
    validation: "Automated monitoring and health checks"
```

### Phase 2: System Slice Identification

**Agent Command**: `*identify-slice`

**Slice Selection Criteria**:

```yaml
slice_identification:
  business_value_validation:
    criteria:
      - "Represents core business capability"
      - "Exercises primary user workflow"
      - "Demonstrates system value proposition"
      - "Validates key business assumptions"

  architectural_coverage:
    criteria:
      - "Touches all major architectural components"
      - "Exercises critical integration points"
      - "Validates technology choices"
      - "Proves deployment strategy"

  technical_risk_mitigation:
    criteria:
      - "Addresses highest technical risks first"
      - "Validates complex integrations"
      - "Proves performance assumptions"
      - "Tests operational procedures"

slice_examples:
  e_commerce_system:
    slice: "User can view product and add to cart"
    components: ["Web UI", "Product API", "Database", "Session Storage"]
    validation: "End-to-end product display with cart functionality"

  banking_system:
    slice: "Customer can check account balance"
    components: ["Mobile App", "Authentication", "Account API", "Core Banking"]
    validation: "Complete authentication and balance retrieval"

  content_management:
    slice: "User can create and publish article"
    components: ["Admin UI", "Content API", "Database", "CDN"]
    validation: "Full content creation and public display workflow"
```

### Phase 3: Minimal Implementation Strategy

**Agent Command**: `*implement-skeleton`

**Implementation Approach**:

```yaml
implementation_strategy:
  layer_by_layer_approach:
    presentation_layer:
      implementation: "Single page/screen with minimal UI elements"
      validation: "Basic user interaction and navigation"
      technology: "Framework basics without complex features"

    api_layer:
      implementation: "Single endpoint with minimal request/response"
      validation: "HTTP communication and basic error handling"
      technology: "REST/GraphQL with minimal data transformation"

    business_layer:
      implementation: "Core business rule with minimal logic"
      validation: "Business validation and processing"
      technology: "Domain model with essential behavior"

    data_layer:
      implementation: "Single entity with basic CRUD operations"
      validation: "Data persistence and retrieval"
      technology: "Database connection with minimal schema"

    integration_layer:
      implementation: "Essential external service integration"
      validation: "Third-party communication and error handling"
      technology: "HTTP client with basic configuration"

  incremental_expansion:
    phase_1: "Static data display without persistence"
    phase_2: "Add basic data persistence"
    phase_3: "Add user interaction and state changes"
    phase_4: "Add external service integration"
    phase_5: "Add error handling and edge cases"
```

### Phase 4: Automated Pipeline Integration

**Agent Command**: `*establish-pipeline`

**CI/CD Pipeline Requirements**:

```yaml
pipeline_automation:
  source_control_integration:
    requirements:
      - "Automated build triggers on code changes"
      - "Branch protection and pull request validation"
      - "Version tagging and release automation"
      - "Code quality gates and security scanning"

  build_automation:
    requirements:
      - "Automated compilation and dependency resolution"
      - "Unit test execution with coverage reporting"
      - "Integration test execution with real components"
      - "Static analysis and security vulnerability scanning"

  deployment_automation:
    requirements:
      - "Automated deployment to staging environment"
      - "Smoke testing and health check validation"
      - "Production deployment with rollback capability"
      - "Infrastructure as code for consistent environments"

  monitoring_integration:
    requirements:
      - "Application performance monitoring setup"
      - "Error tracking and alerting configuration"
      - "Business metric collection and reporting"
      - "Infrastructure monitoring and capacity alerting"
```

### Phase 5: End-to-End Testing Strategy

**Agent Command**: `*validate-skeleton`

**Testing Pyramid Implementation**:

```yaml
testing_strategy:
  end_to_end_tests:
    purpose: "Validate complete user workflows through real system"
    implementation: "Browser-based tests using Playwright or similar"
    coverage: "Happy path scenarios with real data"
    environment: "Production-like environment with real integrations"

  integration_tests:
    purpose: "Validate component interactions and data flow"
    implementation: "API testing with real database and services"
    coverage: "Critical integration points and error scenarios"
    environment: "Containerized environment with test data"

  unit_tests:
    purpose: "Validate individual component behavior"
    implementation: "Fast, isolated tests with minimal dependencies"
    coverage: "Business logic and critical algorithms"
    environment: "In-memory components for fast feedback"

  contract_tests:
    purpose: "Validate API contracts between components"
    implementation: "Schema validation and consumer-driven contracts"
    coverage: "All internal and external API interactions"
    environment: "Mock services with contract validation"
```

### Phase 6: Production Readiness Validation

**Agent Command**: `*validate-production-readiness`

**Production Readiness Checklist**:

```yaml
production_readiness:
  operational_requirements:
    monitoring_and_alerting:
      - "Application health checks and status endpoints"
      - "Performance metrics collection and alerting"
      - "Error rate monitoring and notification"
      - "Business metric tracking and reporting"

    security_requirements:
      - "Authentication and authorization implementation"
      - "Data encryption in transit and at rest"
      - "Security vulnerability scanning and remediation"
      - "Access control and audit logging"

    performance_requirements:
      - "Load testing and performance benchmarking"
      - "Scalability testing and resource optimization"
      - "Database performance tuning and indexing"
      - "Caching strategy and optimization"

    reliability_requirements:
      - "Error handling and graceful degradation"
      - "Backup and disaster recovery procedures"
      - "High availability and failover mechanisms"
      - "Data consistency and integrity validation"
```

## Advanced Walking Skeleton Patterns

### Tracer Bullet Development

```yaml
tracer_bullet_approach:
  concept: "Fire a tracer bullet through entire system to validate path"
  implementation:
    - "Start with hardcoded values to prove connectivity"
    - "Replace hardcoded values with real implementation incrementally"
    - "Maintain working system throughout development"
    - "Add complexity only after proving basic functionality"

  benefits:
    - "Early feedback on architecture decisions"
    - "Continuous integration and deployment validation"
    - "Risk reduction through early problem detection"
    - "Foundation for incremental feature development"

tracer_example:
  initial_implementation:
    user_request: "GET /users/123"
    response: "{ 'name': 'John Doe', 'email': 'john@example.com' }"
    components: "Controller → Hardcoded Response"

  first_evolution:
    user_request: "GET /users/123"
    response: "{ 'name': 'John Doe', 'email': 'john@example.com' }"
    components: "Controller → Service → Hardcoded Repository"

  second_evolution:
    user_request: "GET /users/123"
    response: "Dynamic user data from database"
    components: "Controller → Service → Database Repository"
```

### Steel Thread Implementation

```yaml
steel_thread_approach:
  concept: "Robust implementation path through system with error handling"
  implementation:
    - "Add comprehensive error handling to walking skeleton"
    - "Implement logging and monitoring throughout"
    - "Add input validation and security controls"
    - "Implement graceful degradation and fallbacks"

  production_hardening:
    - "Authentication and authorization integration"
    - "Rate limiting and request validation"
    - "Circuit breakers and timeout handling"
    - "Comprehensive logging and audit trails"

steel_example:
  authentication_layer:
    implementation: "JWT token validation with proper error handling"
    fallback: "Graceful degradation for authentication service failures"
    monitoring: "Authentication attempt logging and failure alerting"

  business_layer:
    implementation: "Input validation with detailed error messages"
    fallback: "Default responses for external service failures"
    monitoring: "Business operation metrics and performance tracking"
```

## Risk Mitigation Strategies

### Technical Risk Assessment

```yaml
risk_categories:
  integration_risks:
    description: "Risks related to component integration and communication"
    mitigation: "Walking skeleton validates all integration points early"
    validation: "End-to-end tests with real components"

  technology_risks:
    description: "Risks related to technology choices and performance"
    mitigation: "Minimal implementation proves technology viability"
    validation: "Performance testing and scalability validation"

  deployment_risks:
    description: "Risks related to deployment and operational procedures"
    mitigation: "Automated pipeline deployment from day one"
    validation: "Production-like environment testing"

  business_risks:
    description: "Risks related to business value and user acceptance"
    mitigation: "Minimal viable feature provides early user feedback"
    validation: "User acceptance testing and business metric validation"
```

### Risk Detection and Response

```yaml
risk_monitoring:
  early_warning_indicators:
    - "Integration test failures or flakiness"
    - "Performance degradation in minimal implementation"
    - "Deployment pipeline failures or complexity"
    - "Negative user feedback on minimal feature"

  response_strategies:
    architecture_issues:
      detection: "Integration problems or performance bottlenecks"
      response: "Architecture review and component redesign"
      validation: "Updated walking skeleton with improved design"

    technology_issues:
      detection: "Technology limitations or poor performance"
      response: "Technology evaluation and potential replacement"
      validation: "Technology spike and proof of concept"

    process_issues:
      detection: "Pipeline failures or deployment problems"
      response: "Process improvement and automation enhancement"
      validation: "Improved deployment success rate"
```

## Output Artifacts

### Walking Skeleton Implementation

1. **WALKING_SKELETON_CODE/** - Minimal end-to-end implementation
2. **E2E_TESTS/** - Automated end-to-end test suite
3. **DEPLOYMENT_PIPELINE/** - CI/CD pipeline configuration
4. **MONITORING_SETUP/** - Monitoring and alerting configuration
5. **PRODUCTION_RUNBOOK/** - Operational procedures and guidelines

### Documentation and Validation

1. **SKELETON_DESIGN.md** - Walking skeleton design and rationale
2. **ARCHITECTURE_VALIDATION.md** - Architectural decision validation
3. **RISK_ASSESSMENT.md** - Risk identification and mitigation strategies
4. **PRODUCTION_READINESS.md** - Production deployment validation
5. **LESSONS_LEARNED.md** - Insights and recommendations for team

### Quality Assurance Deliverables

1. **TEST_STRATEGY.md** - Comprehensive testing approach
2. **PERFORMANCE_BASELINE.md** - Performance metrics and benchmarks
3. **SECURITY_ASSESSMENT.md** - Security implementation validation
4. **OPERATIONAL_PROCEDURES.md** - Support and maintenance guidelines

## Quality Gates

### Walking Skeleton Validation

- [ ] **End-to-End Connectivity**: Complete system integration with minimal functionality
- [ ] **Architecture Validation**: All major components connected and communicating
- [ ] **Deployment Automation**: Automated deployment pipeline operational
- [ ] **Monitoring Integration**: Basic monitoring and alerting functional
- [ ] **Production Readiness**: System deployable to production environment

### Risk Mitigation Validation

- [ ] **Integration Risk**: All component integrations tested and validated
- [ ] **Technology Risk**: Technology choices validated under realistic conditions
- [ ] **Deployment Risk**: Deployment process proven reliable and repeatable
- [ ] **Business Risk**: Minimal feature provides measurable business value
- [ ] **Operational Risk**: Support procedures and documentation complete

### Quality Assurance Validation

- [ ] **Test Coverage**: End-to-end tests cover critical user workflows
- [ ] **Performance Baseline**: Performance benchmarks established and documented
- [ ] **Security Compliance**: Security controls implemented and validated
- [ ] **Error Handling**: Graceful error handling and recovery mechanisms
- [ ] **Monitoring Coverage**: Comprehensive monitoring of system health and performance

## Success Criteria

- Minimal end-to-end functionality implemented and validated
- Complete system architecture proven through working implementation
- Automated deployment pipeline established and operational
- Risk mitigation strategies implemented and tested
- Production-ready foundation established for incremental development
- Team aligned on architecture and development approach
- Early feedback loop established with stakeholders and users

## Failure Recovery

If Walking Skeleton implementation fails:

1. **Architecture Issues**: Simplify architecture and reduce component complexity
2. **Technology Problems**: Evaluate alternative technologies or implementation approaches
3. **Integration Failures**: Focus on individual component validation before end-to-end
4. **Deployment Issues**: Simplify deployment process and infrastructure requirements
5. **Performance Problems**: Profile and optimize critical bottlenecks

## Integration with 5D-Wave Methodology

### Wave Integration Points

```yaml
discuss_integration:
  requirements_validation: "Walking skeleton validates key requirements early"
  risk_identification: "Technical risks identified through minimal implementation"

design_integration:
  architecture_proof: "Architecture design validated through working system"
  technology_validation: "Technology choices proven under realistic conditions"

distill_integration:
  acceptance_testing: "End-to-end tests provide foundation for acceptance criteria"
  business_validation: "Minimal feature enables early business value measurement"

develop_integration:
  implementation_foundation: "Walking skeleton provides development foundation"
  continuous_integration: "Established pipeline supports ongoing development"

demo_integration:
  stakeholder_demonstration: "Working system enables early stakeholder feedback"
  production_readiness: "Infrastructure and procedures established for production"
```

## Methodology Completion

**Walking Skeleton successfully implemented with minimal end-to-end functionality, validated architecture, automated deployment pipeline, and production-ready foundation for incremental feature development.**
