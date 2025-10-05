---
agent-activation:
  required: true
  agent-id: agent-forger
  agent-name: "Sage"
  agent-command: "*forge"
  auto-activate: true
---

**⚠️ AGENT ACTIVATION REQUIRED**

This task requires the **Sage** agent (agent-forger) for execution.

**To activate**: Type `@agent-forger` in the conversation.

Once activated, use the agent's `*help` command to see available operations.

---

# DW-FORGE: Agent Creation with Research-Validated Patterns

## Overview

Execute agent creation using AGENT_TEMPLATE.yaml with comprehensive safety frameworks, 4-layer testing, structured observability, and production-grade error recovery.

## Mandatory Pre-Execution Steps

1. **Template Availability**: Ensure AGENT_TEMPLATE.yaml is embedded and accessible
2. **Requirements Analysis**: Clear agent purpose, wave/domain, and safety requirements
3. **Agent Type Selection**: Determine archetype (Specialist/Orchestrator/Team/Tool)

## Execution Flow

### Phase 1: Requirements Analysis & Pattern Selection

**Primary Agent**: agent-forger (Sage)
**Command**: `*analyze-requirements`

**Agent Creation Foundation**:

```
🏛️ FORGE - AGENT CREATION WITH RESEARCH-VALIDATED PATTERNS

Transform requirements into production-ready agents using:
- 7 research-validated design patterns (ReAct, Reflection, Router, Planning, Orchestration)
- 14 evidence-based core principles
- 4-layer testing framework (Unit, Integration, Adversarial Security, Adversarial Verification)
- Comprehensive safety framework (4 validation layers + 7 enterprise security layers)
- Production observability (structured logging, metrics, alerting)
- Error recovery (retry strategies, circuit breakers, degraded mode)

All patterns sourced from AGENT_TEMPLATE.yaml - the single source of truth.
```

**Requirements Elicitation**:

```yaml
required_inputs:
  agent_purpose:
    question: "What is the primary responsibility of this agent?"
    validation: "Single, clearly defined purpose (Single Responsibility Principle)"

  wave_domain:
    question: "Which 5D-Wave phase does it support?"
    options: ["DISCUSS", "DESIGN", "DISTILL", "DEVELOP", "DEMO", "CROSS_WAVE"]

  required_tools:
    question: "What tools does it absolutely need?"
    principle: "Least Privilege - minimal necessary only"

  safety_requirements:
    question: "What are the safety and security constraints?"
    framework: "Reference AGENT_TEMPLATE.yaml safety_framework"

  success_criteria:
    question: "How do you measure agent success?"
    requirement: "Measurable, observable criteria"
```

**Pattern Selection Decision Tree** (from AGENT_TEMPLATE.yaml):

```yaml
single_agent_patterns:
  general_purpose: "ReAct Pattern - tool calling, memory, planning"
  quality_critical: "Reflection Pattern - self-evaluation, refinement"
  task_routing: "Router Pattern - classify and delegate"
  complex_planning: "Planning Pattern - decompose, sequence, execute"

multi_agent_patterns:
  sequential_dependencies: "Sequential Orchestration - linear pipeline"
  parallel_execution: "Parallel Orchestration - concurrent workers"
  hierarchical_coordination: "Hierarchical Agent - supervisor-worker"
```

**Output Artifacts**:
- Requirements specification document
- Selected design pattern with rationale
- Agent archetype determination (Specialist/Orchestrator/Team/Tool)
- Risk assessment and safety requirements

---

### Phase 2: Agent Architecture Design

**Agent Command**: `*create-specialist` (or `*create-orchestrator`, `*create-team`, `*create-tool`)

**Architecture Design Process**:

```
📐 ARCHITECTURE DESIGN - TEMPLATE-DRIVEN STRUCTURE

Load AGENT_TEMPLATE.yaml and apply appropriate archetype:

Specialist Agent (lines 34-920):
- Single responsibility domain expert
- ReAct or Reflection pattern typically
- Examples: business-analyst, software-crafter

Orchestrator Agent (lines 956-1016):
- Multi-phase workflow coordinator
- Sequential or Hierarchical pattern
- Examples: 5d-wave-complete-orchestrator

Team Agent (lines 1018-1063):
- Massive collaborative system
- Multiple embedded specialists
- Examples: 5d-wave-core-team

Tool Agent (lines 1065-1157):
- Domain-specific tooling
- Specialized commands and pipeline
- Examples: architecture-diagram-manager
```

**Design Decisions** (AGENT_TEMPLATE.yaml driven):

1. **Base Template Selection**: Choose archetype from AGENT_TEMPLATE.yaml
2. **Persona Definition**: 8-10 core principles derived from template's 14 evidence-based principles (lines 1787-1930)
3. **Command Set Design**: Focused commands per template best_practices (lines 1182-1188)
4. **Tool Selection**: Minimal set using template tool_security_principle (lines 1296-1330)
5. **Contract Definition**: Input/output contract per template (lines 92-169)

**YAML Frontmatter** (AGENT_TEMPLATE.yaml lines 35-39):

```yaml
---
name: {agent-id-kebab-case}
description: Use for {WAVE} wave - {clear purpose and when to invoke}
model: inherit  # or sonnet/opus/haiku based on complexity
tools: {minimal-tool-set}  # optional, inherits all if omitted
---
```

**Output Artifacts**:
- Agent architecture specification
- Design pattern documentation with rationale
- Persona definition with core principles
- Command set design
- Tool access justification

---

### Phase 3: Safety Framework Implementation

**Agent Command**: `*implement-safety`

**Multi-Layer Safety** (AGENT_TEMPLATE.yaml safety_framework lines 171-233):

```yaml
layer_1_input_validation:
  - Schema validation (structure, data types)
  - Content sanitization (SQL injection, command injection, path traversal)
  - Contextual validation (business logic constraints)
  - Security scanning (prompt injection detection)

layer_2_output_filtering:
  - LLM-based guardrails (AI-powered content moderation)
  - Rules-based filters (regex, keyword blocking)
  - Relevance validation (on-topic responses)
  - Safety classification (harmful content blocking)

layer_3_behavioral_constraints:
  - Tool restrictions (least privilege principle)
  - Scope boundaries (allowed/forbidden operations)
  - File access patterns (whitelist/blacklist)
  - Escalation triggers (human oversight requirements)

layer_4_continuous_monitoring:
  - Misevolution detection (safety drift over time)
  - Anomaly detection (unusual patterns)
  - Performance tracking (response time, error rate)
  - Audit logging (comprehensive action tracking)
```

**Enterprise Security Framework** (AGENT_TEMPLATE.yaml 7-layer defense in depth):

```yaml
enterprise_security_layers:
  layer_1_identity: "Authentication, authorization, RBAC"
  layer_2_guardrails: "Input validation, output filtering, behavioral constraints"
  layer_3_evaluations: "Automated safety evaluations, benchmarks, quality metrics"
  layer_4_adversarial: "Red team exercises, attack simulation, vulnerability discovery"
  layer_5_data_protection: "Encryption, sanitization, privacy preservation"
  layer_6_monitoring: "Real-time tracking, anomaly detection, alert systems"
  layer_7_governance: "Policy enforcement, compliance validation, audit trails"
```

**Output Artifacts**:
- Complete safety framework configuration
- Input validation rules
- Output filtering rules
- Behavioral constraint definitions
- Monitoring and alerting configuration

---

### Phase 4: Testing Framework Implementation

**Agent Command**: `*generate-tests`

**4-Layer Testing** (AGENT_TEMPLATE.yaml testing_framework lines 235-531):

```yaml
layer_1_unit_testing:
  description: "Validate individual agent outputs"
  agent_type_adaptations:
    document_agents:
      validation: "Artifact quality (completeness, structure, testability)"
      metrics:
        - completeness_score: "> 0.95"
        - acceptance_criteria_quality: "> 0.90"
    code_agents:
      validation: "Code execution (tests pass, builds succeed)"
      metrics:
        - test_pass_rate: "100%"
        - test_coverage: "> 80%"

layer_2_integration_testing:
  description: "Validate handoffs between agents"
  pattern: "Next agent must consume outputs without clarification"
  examples:
    - "business-analyst → solution-architect: Can architecture be designed?"
    - "solution-architect → acceptance-designer: Can tests be designed?"

layer_3_adversarial_output_validation:
  description: "Challenge output quality, validity, and robustness through adversarial scrutiny"
  agent_type_adaptations:
    research_agents:
      test_categories:
        - source_verification_attacks: "Can sources be independently verified?"
        - bias_detection_attacks: "Are sources cherry-picked? Multiple perspectives?"
        - claim_replication_attacks: "Can findings be replicated?"
        - evidence_quality_challenges: "Is evidence strong or circumstantial?"
    requirements_agents:
      test_categories:
        - adversarial_questioning: "What happens when [edge case]?"
        - ambiguity_attacks: "Can requirements be interpreted multiple ways?"
        - testability_challenges: "How would you test this requirement?"
    code_agents:
      test_categories:
        - output_code_security: "SQL injection, XSS in GENERATED code?"
        - edge_case_attacks: "How does code handle null/boundary conditions?"
        - error_handling_attacks: "Does code fail gracefully?"
  pass_threshold: "All critical adversarial challenges addressed"

  note: "Agent security testing (prompt injection, jailbreak) is in safety_framework.agent_security_validation"

layer_4_adversarial_verification:
  description: "Peer review for bias reduction (NOVEL)"
  validator: "Equal agent (same expertise, different instance)"
  validates: "Bias, completeness, quality, assumptions"
  workflow: "Production → Peer Review → Revision → Approval → Handoff"
  benefits:
    - "Bias Reduction: Fresh perspective not invested in original approach"
    - "Quality Improvement: Identifies gaps original agent missed"
```

**Output Artifacts**:
- Comprehensive test suite (all 4 layers)
- Unit tests for output quality (agent-type-specific)
- Integration tests for handoffs between agents
- Adversarial output validation suite (source verification, bias detection, edge cases)
- Agent security validation suite (prompt injection, jailbreak - separate from output testing)
- Peer review workflow configuration

---

### Phase 5: Observability & Error Recovery

**Agent Command**: `*add-quality-gates`

**Observability Framework** (AGENT_TEMPLATE.yaml observability_framework lines 532-714):

```yaml
structured_logging:
  format: "JSON with universal + agent-type-specific fields"
  universal_fields:
    - timestamp: "ISO 8601 format"
    - agent_id: "Kebab-case identifier"
    - session_id: "Unique session tracking"
    - command: "Command executed"
    - status: "success | failure | degraded"
    - duration_ms: "Execution time"

  agent_specific_fields:
    document_agents: ["artifacts_created", "completeness_score", "handoff_accepted"]
    code_agents: ["tests_run", "tests_passed", "test_coverage", "build_success"]

metrics_collection:
  universal_metrics:
    - command_execution_time: "Histogram by agent_id and command"
    - command_success_rate: "Percentage successful executions"
    - quality_gate_pass_rate: "Percentage gates passed"

  agent_specific_metrics:
    document_agents:
      - completeness_score: "Target > 0.95"
      - handoff_acceptance_rate: "Target > 0.95"
    code_agents:
      - test_pass_rate: "Target 100%"
      - test_coverage: "Target > 80%"

alerting_thresholds:
  critical:
    - safety_alignment_critical: "safety_score < 0.85 → Pause operations"
    - policy_violation_spike: "violations > 5/hour → Security alert"
  warning:
    - performance_degradation: "p95_response > 5s → Investigation"
    - quality_gate_failures: "failure_rate > 10% → Review"
```

**Error Recovery Framework** (AGENT_TEMPLATE.yaml error_recovery_framework lines 716-874):

```yaml
retry_strategies:
  exponential_backoff:
    pattern: "1s, 2s, 4s, 8s, 16s (max 5 attempts)"
    use_when: "Transient failures (network, resources)"

  agent_specific_retries:
    document_agents:
      incomplete_artifact: "Re-elicitation for missing sections (max 3 attempts)"
    code_agents:
      test_failures: "Iterative fix and validate (max 3 attempts)"

circuit_breakers:
  vague_input_breaker:
    threshold: "5 consecutive vague responses"
    action: "Stop automated elicitation, escalate to human"

  handoff_rejection_breaker:
    threshold: "2 consecutive rejections"
    action: "Pause workflow, request human review"

  safety_violation_breaker:
    threshold: "3 violations in 1 hour"
    action: "Immediately halt operations, notify security"

degraded_mode_operation:
  strategy: "Provide partial value when full functionality unavailable"
  output_format: "✅ COMPLETE sections + ❌ MISSING sections with TODO"
  communication: "Clear user message about completeness %, what's missing, next steps"
```

**Output Artifacts**:
- Structured logging configuration
- Metrics collection definitions
- Alerting threshold configurations
- Retry strategy implementations
- Circuit breaker configurations
- Degraded mode output templates

---

### Phase 6: Validation & Deployment Preparation

**Agent Command**: `*validate-specification`

**Validation Checklist** (AGENT_TEMPLATE.yaml validation_rules lines 1335-1394):

```yaml
structural_requirements:
  - yaml_frontmatter_complete: "name, description, model fields present"
  - activation_notice_present: true
  - persona_definition_complete: "role, style, identity, focus, core_principles"
  - contract_defined: "inputs, outputs, side_effects, error_handling"
  - command_list_valid: "help first, exit last, * prefix documented"

safety_requirements:
  - input_validation_implemented: true
  - output_filtering_configured: true
  - tool_restrictions_documented: "Least privilege justified"
  - audit_logging_enabled: true
  - error_handling_safe_defaults: true
  - escalation_triggers_defined: true

testing_requirements:
  - layer_1_unit_tests: "Agent-type-specific output validation present"
  - layer_2_integration_tests: "Handoff validation present"
  - layer_3_adversarial_output_validation: "All adversarial output challenges addressed"
  - layer_4_adversarial_verification: "Peer review workflow configured"
  - agent_security_validation: "Agent security tests (prompt injection, jailbreak) passed"

observability_requirements:
  - structured_logging_configured: true
  - metrics_collection_defined: true
  - alerting_thresholds_set: true
  - error_recovery_implemented: true

quality_gates:
  - single_responsibility_clear: true
  - design_pattern_documented: true
  - agent_template_structure_followed: true
  - all_14_core_principles_addressed: true
  - tool_access_minimal_justified: true
  - success_criteria_measurable: true
```

**Deployment Package**:

```yaml
deliverables:
  - agent_specification: "Complete .md file with embedded dependencies"
  - yaml_configuration: "Validated frontmatter and config block"
  - safety_framework: "Multi-layer validation implemented"
  - test_suite: "Comprehensive 4-layer testing"
  - documentation: "Architecture decisions, operational procedures"
  - monitoring_config: "Observability and alerting setup"
  - operational_runbook: "Deployment, monitoring, troubleshooting, incident response"
```

**Output Artifacts**:
- Validation results report
- Complete deployment package
- Operational runbook
- Monitoring and alerting setup
- Incident response procedures

---

## Success Criteria

**Agent Creation Complete When**:

1. ✅ **AGENT_TEMPLATE.yaml compliance verified**
   - Appropriate archetype used (Specialist/Orchestrator/Team/Tool)
   - Structure follows template exactly
   - All required sections present

2. ✅ **Design Pattern Implementation**
   - Pattern selected from template's 7 validated patterns
   - Pattern choice documented with rationale
   - Implementation follows pattern guidelines

3. ✅ **Core Principles Satisfaction**
   - All 14 evidence-based principles addressed
   - Single responsibility clearly defined
   - Specification compliance validated

4. ✅ **Safety Framework Complete**
   - 4 validation layers implemented
   - 7 enterprise security layers applied
   - Misevolution detection configured
   - Continuous monitoring active

5. ✅ **Testing Framework Complete**
   - Layer 1: Unit tests (agent-type-specific output validation)
   - Layer 2: Integration tests (handoff validation)
   - Layer 3: Adversarial output validation (all challenges addressed)
   - Layer 4: Adversarial verification (peer review workflow)
   - Agent security validation: Separate testing (prompt injection, jailbreak - 100% blocked)

6. ✅ **Observability Operational**
   - Structured JSON logging configured
   - Metrics collection defined
   - Alerting thresholds set
   - Dashboards specified

7. ✅ **Error Recovery Resilient**
   - Retry strategies implemented
   - Circuit breakers configured
   - Degraded mode operation defined
   - Fail-safe defaults established

8. ✅ **Documentation Complete**
   - Architecture decisions documented
   - Operational procedures defined
   - Troubleshooting guide provided
   - Examples included

9. ✅ **Deployment Ready**
   - All quality gates passed
   - Validation checklist complete
   - Monitoring configured
   - Team trained

---

## Quality Gates

- [ ] AGENT_TEMPLATE.yaml loaded and referenced throughout creation
- [ ] Requirements analysis complete with clear single responsibility
- [ ] Design pattern selected and documented from template
- [ ] Agent archetype appropriate for use case
- [ ] Persona defined with 8-10 principles aligned with template's 14 principles
- [ ] Input/Output contract defined with validation
- [ ] Safety framework: 4 validation layers + 7 enterprise security layers
- [ ] Testing framework: 4 layers all implemented and passing
- [ ] Observability framework: logging, metrics, alerting configured
- [ ] Error recovery framework: retry, circuit breakers, degraded mode
- [ ] Tool access minimal and justified (least privilege)
- [ ] All 14 core principles from template addressed
- [ ] Naming conventions followed (kebab-case, * prefix)
- [ ] Documentation comprehensive and reviewed
- [ ] Deployment package complete
- [ ] Production ready and validated

---

## Handoff to Next Wave

**Next Agent**: deployment-coordinator or user testing

**Handoff Package**:
- Complete agent specification file (.md)
- Validation results report
- Deployment checklist completed
- Monitoring and alerting configured
- Operational runbook ready
- Team briefing materials

**Validation**: All quality gates passed, AGENT_TEMPLATE.yaml compliance verified
