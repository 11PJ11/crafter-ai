# Enhanced Agent Specification Template

## Standard Agent Header
```yaml
---
name: agent-name
description: Agent purpose and responsibility
tools: [Read, Write, Edit, Grep, Glob, Bash, Task]
references: ["@constants.md"]
validation_enabled: true
---
```

## MANDATORY CONSTRAINTS Section
**CRITICAL**: These constraints are ENFORCED during agent execution and CANNOT be violated.

```yaml
mandatory_constraints:
  # Production Service Integration (ATDD/TDD Agents)
  production_service_calls:
    rule: "Step methods MUST call production services via GetRequiredService pattern"
    pattern: "_serviceProvider\\.GetRequiredService<[^>]+>\\(\\)"
    forbidden_patterns: ["execAsync", "CLI calls", "direct infrastructure access"]
    violation_severity: "CRITICAL"

  # Business Language Requirements
  business_language:
    rule: "MUST use domain terminology, not technical implementation details"
    required_patterns: ["business outcome", "domain validation", "user behavior"]
    forbidden_words: ["CLI", "execAsync", "infrastructure", "technical artifact"]
    violation_severity: "HIGH"

  # Architectural Compliance
  architectural_compliance:
    rule: "MUST follow hexagonal architecture patterns"
    required_patterns: ["port interface", "adapter implementation", "domain service"]
    forbidden_patterns: ["direct database access", "UI in business logic"]
    violation_severity: "HIGH"

  # Test Focus Requirements
  test_focus:
    rule: "MUST validate business outcomes, not technical artifacts"
    required_patterns: ["business assertion", "outcome validation", "behavior verification"]
    forbidden_patterns: ["implementation testing", "infrastructure verification"]
    violation_severity: "MEDIUM"
```

## VALIDATION RULES Section
**Specific patterns and rules for automated compliance checking**

```yaml
validation_rules:
  # Code Pattern Validation
  step_method_validation:
    pattern: "Given|When|Then.*async Task.*\\("
    must_contain: "_serviceProvider\\.GetRequiredService"
    must_not_contain: ["execAsync\\(", "Process\\.Start", "CLI\\."]
    context_check: "within step methods only"

  # Language Pattern Validation
  business_terminology:
    required_ratio: 0.7  # 70% business terms vs technical terms
    business_terms: ["user", "customer", "order", "product", "service", "business", "domain"]
    technical_terms: ["database", "API", "CLI", "infrastructure", "deployment", "build"]
    context: "test names and descriptions"

  # Architecture Pattern Validation
  hexagonal_patterns:
    port_interface_check: "interface I[A-Za-z]+Service"
    adapter_pattern_check: "class [A-Za-z]+Adapter implements I"
    domain_service_check: "class [A-Za-z]+Service.*domain"
    layering_check: "no direct database access from domain"
```

## ENFORCEMENT MECHANISM Section
**How constraints are validated and enforced**

```yaml
enforcement_mechanism:
  validation_stage: "pre_output_generation"
  failure_action: "block_and_report"

  validation_pipeline:
    - stage: "syntax_validation"
      description: "Check output structure and format"
      blocking: true
    - stage: "pattern_validation"
      description: "Verify required patterns are present"
      blocking: true
    - stage: "constraint_validation"
      description: "Validate mandatory constraints compliance"
      blocking: true
    - stage: "quality_assessment"
      description: "Assess overall output quality"
      blocking: false

  violation_handling:
    critical_violations:
      action: "immediate_block"
      message: "Output violates CRITICAL constraint: {constraint_name}"
      remediation: "Required pattern: {required_pattern}"
    high_violations:
      action: "block_with_guidance"
      message: "Output violates HIGH priority constraint: {constraint_name}"
      remediation: "Please revise to include: {remediation_guidance}"
    medium_violations:
      action: "warning_with_review"
      message: "Output has MEDIUM priority violation: {constraint_name}"
      remediation: "Consider improving: {improvement_suggestion}"
```

## REMEDIATION GUIDANCE Section
**Specific instructions for fixing constraint violations**

```yaml
remediation_guidance:
  production_service_calls:
    violation_type: "Missing GetRequiredService pattern"
    fix_instruction: |
      Replace infrastructure calls with production service calls:

      ❌ Wrong:
      var result = await execAsync('forge deploy');

      ✅ Correct:
      var deployService = _serviceProvider.GetRequiredService<IDeploymentService>();
      var result = await deployService.DeployAsync();

    example_template: |
      [When("the system is deployed successfully")]
      public async Task WhenSystemIsDeployedSuccessfully()
      {
          var deploymentService = _serviceProvider.GetRequiredService<IDeploymentService>();
          _deploymentResult = await deploymentService.DeployAsync(_testEnvironment);
      }

  business_language:
    violation_type: "Technical terminology instead of business language"
    fix_instruction: |
      Use domain language instead of technical implementation:

      ❌ Wrong: "CLI execution completes"
      ✅ Correct: "Deployment succeeds for user"

      ❌ Wrong: "Database update successful"
      ✅ Correct: "Customer order is saved"

    domain_vocabulary:
      user_interactions: ["user registers", "customer orders", "admin approves"]
      business_outcomes: ["order fulfilled", "payment processed", "notification sent"]
      domain_concepts: ["user account", "product catalog", "order workflow"]

  architectural_compliance:
    violation_type: "Hexagonal architecture violation"
    fix_instruction: |
      Follow hexagonal architecture patterns:

      ❌ Wrong: Direct database access in tests
      var user = _dbContext.Users.Find(id);

      ✅ Correct: Through port interface
      var userService = _serviceProvider.GetRequiredService<IUserService>();
      var user = await userService.FindByIdAsync(id);

    architecture_patterns:
      ports: "Define business interfaces (IUserService, IOrderService)"
      adapters: "Implement infrastructure adapters (DatabaseUserRepository)"
      domain_services: "Pure business logic with no infrastructure dependencies"
```

## COGNITIVE LOAD MANAGEMENT Section
**System for managing agent cognitive processing**

```yaml
cognitive_load_management:
  attention_allocation:
    constraint_validation: 30  # 30% of cognitive resources
    problem_solving: 50        # 50% of cognitive resources
    output_generation: 20      # 20% of cognitive resources

  processing_stages:
    stage_1_constraint_understanding:
      focus: "Parse and internalize mandatory constraints"
      time_allocation: "15% of total processing"
      success_criteria: "All constraints understood and prioritized"

    stage_2_problem_analysis_with_constraints:
      focus: "Analyze problem while keeping constraints active"
      time_allocation: "35% of total processing"
      success_criteria: "Solution approach respects all constraints"

    stage_3_solution_generation_with_validation:
      focus: "Generate solution with real-time constraint checking"
      time_allocation: "35% of total processing"
      success_criteria: "Solution complies with all mandatory constraints"

    stage_4_output_compliance_verification:
      focus: "Final validation before output submission"
      time_allocation: "15% of total processing"
      success_criteria: "100% constraint compliance verified"

  cognitive_simplification:
    max_constraints_per_agent: 3
    constraint_complexity: "one_clear_requirement_per_constraint"
    layered_validation: "progressive_checking_through_stages"
    attention_anchoring: "constraints_always_in_working_memory"
```

## AGENT TEMPLATE SECTIONS

### Core Responsibilities
[Standard agent responsibilities section]

### Pipeline Integration
[Standard pipeline integration section]

### Implementation Guidance
[Standard implementation guidance with constraint compliance examples]

---

**VALIDATION STATUS**: This template includes mandatory constraint enforcement, validation rules, cognitive load management, and detailed remediation guidance to prevent agent directive non-compliance.