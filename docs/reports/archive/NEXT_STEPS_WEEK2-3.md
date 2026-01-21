# Next Steps: Week 2-3 Implementation Plan

**Date**: 2025-10-05
**Status**: Validation Complete, Implementation Planning
**Priority**: Medium-Term Production Readiness

---

## Current Status Summary

### Week 1 Achievements ✅

1. **Production Frameworks Added to AGENT_TEMPLATE.yaml v1.2**
   - Contract Framework: Input/output specification
   - Safety Framework: 4 validation layers + 7 enterprise security layers
   - Testing Framework: 5-layer testing (Unit, Integration, Adversarial Output, Adversarial Verification)
   - Observability Framework: Structured logging, metrics, alerting
   - Error Recovery Framework: Retry, circuit breakers, degraded mode

2. **Validation Infrastructure Created**
   - `scripts/validate-agent-compliance.py`: Automated compliance validation
   - `scripts/run-adversarial-tests.py`: Adversarial test suite definitions
   - `docs/COMPLIANCE_VALIDATION_REPORT.md`: Framework compliance status
   - `docs/ADVERSARIAL_TEST_REPORT.md`: Comprehensive test definitions (258 test cases)

3. **Current Compliance Status**
   - **Total Agents**: 12
   - **Frameworks in Template**: 5 production frameworks complete
   - **Frameworks in Agents**: Contract framework present, others pending propagation
   - **Adversarial Tests Defined**: 258 test cases across all agent types

---

## Week 2-3 Priorities

### Priority 1: Framework Propagation to Individual Agents (HIGH)

**Objective**: Add missing frameworks to all 12 agent files

**Scope**: Propagate Safety, Testing, Observability, and Error Recovery frameworks from AGENT_TEMPLATE.yaml to individual agent files.

**Agent Status**:
- ✅ Contract: All 11/12 agents (knowledge-researcher missing)
- ❌ Safety: 0/12 agents
- ❌ Testing: 0/12 agents
- ❌ Observability: 0/12 agents
- ❌ Error Recovery: 0/12 agents (agent-forger has partial implementation)
- ⚠️ Frontmatter: 3/12 agents (agent-forger, data-engineer, knowledge-researcher)

**Implementation Plan**:

#### Step 1: Batch Framework Addition Script
```bash
# Create script: scripts/add-frameworks-to-agents.py
# - Read AGENT_TEMPLATE.yaml framework sections
# - For each agent in nWave/agents/*.md:
#   - Extract existing YAML configuration
#   - Add missing frameworks with agent-type adaptations
#   - Preserve existing content
#   - Write updated agent file
# - Validate with compliance script after each agent
```

#### Step 2: Agent-Type-Specific Adaptations

**Document Agents** (business-analyst, solution-architect, acceptance-designer, feature-completion-coordinator):
- Testing L1: Artifact quality metrics (completeness_score, acceptance_criteria_quality)
- Observability: Document-specific metrics (handoff_acceptance_rate, adr_documentation_rate)
- Error Recovery: Re-elicitation strategies for incomplete artifacts

**Code Agents** (software-crafter):
- Testing L1: Code execution validation (test_pass_rate, test_coverage, build_success)
- Observability: Code metrics (test_pass_rate, coverage, build_success_rate)
- Error Recovery: Test failure recovery, iterative fix-and-validate

**Research Agents** (knowledge-researcher, data-engineer):
- Testing L3: Source verification, bias detection, evidence quality challenges
- Observability: Research metrics (source_verification_rate, bias_detection_count)
- Error Recovery: Source re-validation, evidence quality improvement

**Tool Agents** (architecture-diagram-manager, visual-2d-designer):
- Testing L3: Format validation, visual clarity attacks
- Observability: Tool-specific metrics (diagram_validation_rate, clarity_score)
- Error Recovery: Format correction, notation consistency enforcement

**Orchestrators** (nWave-complete-orchestrator, atdd-focused-orchestrator):
- Testing L2: Workflow handoff validation
- Observability: Workflow metrics (phase_transition_success_rate)
- Error Recovery: Workflow pause on handoff rejection

#### Step 3: Validation After Propagation
```bash
# After framework propagation:
python3 scripts/validate-agent-compliance.py
# Expected result: 12/12 agents pass all framework checks
```

**Timeline**: Week 2 (5-7 days)
**Dependencies**: None
**Blockers**: None

---

### Priority 2: Adversarial Verification Workflow Implementation (MEDIUM)

**Objective**: Implement Layer 4 testing (peer review for bias reduction)

**Background**: Layer 4 (Adversarial Verification) is a novel contribution - quality validation through peer review by equal agents to reduce confirmation bias.

**Implementation Plan**:

#### Step 1: Peer Reviewer Agent Creation
```bash
# Create peer reviewer agents for each archetype:
# - business-analyst-reviewer.md (reviews requirements artifacts)
# - solution-architect-reviewer.md (reviews architecture decisions)
# - acceptance-designer-reviewer.md (reviews test scenarios)
# - code-reviewer-agent.md (reviews software-crafter output)

# Reviewer agents have same expertise but:
# - Different instance (no investment in original approach)
# - Structured critique framework (strengths, issues, recommendations)
# - Focus on bias detection, completeness gaps, clarity issues
```

#### Step 2: Review Workflow Integration
```yaml
workflow:
  phase_1_production:
    agent: "Original agent (e.g., business-analyst)"
    output: "Initial artifact (requirements.md)"

  phase_2_peer_review:
    agent: "Reviewer agent (business-analyst-reviewer)"
    input: "Initial artifact from phase 1"
    output: "Structured critique with feedback"

  phase_3_revision:
    agent: "Original agent (business-analyst)"
    input: "Critique from phase 2"
    output: "Revised artifact addressing feedback"

  phase_4_approval:
    agent: "Reviewer agent"
    validation: "All critical issues resolved?"
    output: "Approval or second iteration"

  phase_5_handoff:
    condition: "Approval obtained from phase 4"
    action: "Handoff to next wave agent"
```

#### Step 3: Critique Dimension Templates

**business-analyst-reviewer critique dimensions**:
- Confirmation bias detection: "Are requirements reflecting stakeholder needs or analyst assumptions?"
- Completeness gaps: "What user scenarios are missing?"
- Clarity issues: "Are acceptance criteria truly testable/measurable?"
- Bias identification: "Are all stakeholder perspectives represented equally?"

**solution-architect-reviewer critique dimensions**:
- Architectural bias detection: "Are technology choices driven by requirements or architect preference?"
- Decision quality: "Is every architectural decision traceable to a requirement?"
- Completeness validation: "Are all quality attributes addressed?"
- Implementation feasibility: "Can acceptance tests be designed from this architecture?"

**acceptance-designer-reviewer critique dimensions**:
- Bias detection: "Are test scenarios covering happy path only (positive bias)?"
- GWT quality: "Are scenarios truly using business language?"
- Coverage validation: "Are all user stories covered by acceptance tests?"
- TDD readiness: "Can software-crafter start outside-in TDD from these tests?"

**code-reviewer-agent critique dimensions**:
- Implementation bias: "Does code solve the actual problem or engineer's assumed problem?"
- Code quality: "Are tests isolated and behavior-driven?"
- Test quality: "Do tests use real components vs excessive mocking?"
- Completeness: "Are all acceptance criteria covered by tests?"

#### Step 4: Automated Review Execution
```python
# scripts/run-adversarial-verification.py
# - Load original agent output artifact
# - Invoke peer reviewer agent
# - Capture structured critique
# - Present to original agent for revision
# - Iterate until approval or max iterations (2)
# - Document review cycle in artifact metadata
```

**Timeline**: Week 2-3 (7-10 days)
**Dependencies**: Priority 1 complete (framework propagation)
**Blockers**: Requires agent runtime environment for automated execution

---

### Priority 3: Observability Infrastructure Deployment (MEDIUM)

**Objective**: Deploy structured logging, metrics collection, and alerting infrastructure

**Implementation Plan**:

#### Step 1: Structured Logging Infrastructure
```yaml
log_format: "JSON with universal + agent-type-specific fields"

universal_fields:
  - timestamp: "ISO 8601 format"
  - agent_id: "Kebab-case identifier"
  - session_id: "Unique session tracking"
  - command: "Command executed"
  - status: "success | failure | degraded"
  - duration_ms: "Execution time"
  - user_id: "Anonymized user identifier"
  - error_type: "Classification if status=failure"

agent_specific_fields:
  document_agents:
    - artifacts_created: "List of document paths"
    - completeness_score: "Quality metric (0-1)"
    - stakeholder_consensus: "boolean"
    - handoff_accepted: "boolean"
    - quality_gates_passed: "Count passed / total"

  code_agents:
    - tests_run: "Count"
    - tests_passed: "Count"
    - test_coverage: "Percentage"
    - build_success: "boolean"
    - code_quality_score: "Rating (0-10)"

logging_backend:
  - Option 1: File-based logging (JSON lines to logs/agents/{agent_id}/{session_id}.jsonl)
  - Option 2: Structured logging service (Elasticsearch, CloudWatch, etc.)
  - Recommendation: Start with file-based, migrate to service for production
```

#### Step 2: Metrics Collection
```yaml
metrics_backend:
  - Option 1: Prometheus + Grafana (industry standard)
  - Option 2: CloudWatch Metrics (AWS)
  - Option 3: Custom time-series database (InfluxDB)
  - Recommendation: Prometheus + Grafana for self-hosted

metrics_to_collect:
  universal:
    - command_execution_time (histogram by agent_id, command_name)
    - command_success_rate (gauge)
    - quality_gate_pass_rate (gauge)
    - safety_alignment_score (gauge with baseline drift detection)

  document_agents:
    - requirements_completeness_score (gauge, target > 0.95)
    - handoff_acceptance_rate (gauge, target > 0.95)
    - adr_documentation_rate (gauge, target 100%)

  code_agents:
    - test_pass_rate (gauge, target 100%)
    - test_coverage (gauge, target > 80%)
    - build_success_rate (gauge, target 100%)
```

#### Step 3: Alerting Configuration
```yaml
critical_alerts:
  safety_alignment_critical:
    condition: "safety_alignment_score < 0.85"
    action: "Pause operations, notify security team"
    channels: ["PagerDuty", "Slack #security"]

  policy_violation_spike:
    condition: "policy_violation_rate > 5/hour"
    action: "Security team alert, increase monitoring"
    channels: ["PagerDuty", "Slack #security"]

warning_alerts:
  performance_degradation:
    condition: "p95_response_time > 5 seconds"
    action: "Performance investigation"
    channels: ["Slack #operations"]

  quality_gate_failures:
    condition: "quality_gate_failure_rate > 10%"
    action: "Agent effectiveness review"
    channels: ["Slack #quality"]
```

**Timeline**: Week 3 (5-7 days)
**Dependencies**: Priority 1 complete (framework propagation)
**Blockers**: Requires infrastructure provisioning (Prometheus/Grafana setup or equivalent)

---

### Priority 4: Adversarial Testing Execution Environment (LOW)

**Objective**: Execute 258 adversarial tests defined in ADVERSARIAL_TEST_REPORT.md

**Implementation Plan**:

#### Step 1: Test Execution Environment Setup
```bash
# Requires:
# - Claude Code runtime environment
# - Agent loading and execution capability
# - Response capture and validation
# - Result aggregation and reporting

# Test execution workflow:
# 1. Load agent in Claude Code
# 2. Execute adversarial test input
# 3. Capture agent response
# 4. Validate response against expected behavior
# 5. Record result (pass/fail with evidence)
# 6. Aggregate results across all agents
# 7. Generate compliance report
```

#### Step 2: Automated Test Runner
```python
# scripts/execute-adversarial-tests.py
# - Load test definitions from ADVERSARIAL_TEST_REPORT.json
# - For each agent:
#   - Load agent in Claude Code
#   - Execute agent security tests (universal)
#   - Execute adversarial output tests (agent-type-specific)
#   - Validate responses against expected behavior
#   - Record pass/fail with evidence
# - Generate updated ADVERSARIAL_TEST_REPORT.md with results
# - Exit with pass/fail status
```

#### Step 3: Pass/Fail Criteria Implementation
```yaml
agent_security_tests:
  pass_threshold: "100% of attacks blocked (zero tolerance)"
  failure_action: "Block deployment, security review required"

adversarial_output_tests:
  pass_threshold: "All critical challenges addressed"
  failure_action: "Document limitations or remediate before deployment"
```

**Timeline**: Week 3-4 (7-10 days)
**Dependencies**: Priority 1 complete, agent runtime environment available
**Blockers**: Requires Claude Code automation or manual test execution

---

## Week 2-3 Success Criteria

### Week 2 End State
- ✅ All 12 agents have 5 production frameworks (Contract, Safety, Testing, Observability, Error Recovery)
- ✅ Compliance validation: 12/12 agents pass all framework checks
- ✅ Peer reviewer agents created (4 archetypes)
- ✅ Adversarial verification workflow documented

### Week 3 End State
- ✅ Observability infrastructure deployed (logging, metrics, alerting)
- ✅ Adversarial verification workflow tested with 1-2 agent pairs
- 🔄 Adversarial testing execution environment setup (in progress)
- 🔄 Subset of adversarial tests executed (agent security tests priority)

---

## Risk Assessment

### High-Risk Items
1. **Framework Propagation Complexity**: Manual addition error-prone → Use automated script
2. **Adversarial Testing Execution**: Requires agent runtime → Prioritize agent security tests first
3. **Observability Infrastructure**: Infrastructure provisioning time → Use file-based logging initially

### Mitigation Strategies
1. **Automated Validation**: Run compliance validation after each agent update
2. **Incremental Rollout**: Test framework propagation on 1 agent first, then batch
3. **Phased Infrastructure**: File-based logging → Metrics collection → Full observability stack

---

## Resource Requirements

### Development Time
- **Priority 1 (Framework Propagation)**: 5-7 days (1 developer)
- **Priority 2 (Adversarial Verification)**: 7-10 days (1 developer)
- **Priority 3 (Observability)**: 5-7 days (1 developer + 0.5 DevOps)
- **Priority 4 (Adversarial Testing)**: 7-10 days (1 developer)

### Infrastructure
- **Observability Stack**: Prometheus + Grafana (self-hosted or cloud)
- **Log Storage**: File system (initial) or Elasticsearch (production)
- **Alerting**: PagerDuty, Slack integration

### Tools
- Python 3.x for automation scripts
- Claude Code for agent runtime
- Git for version control
- Monitoring dashboards (Grafana)

---

## Next Actions (Immediate)

### This Week (Week 2 Start)
1. ✅ Create `scripts/add-frameworks-to-agents.py` (automated framework propagation)
2. ✅ Test framework propagation on 1 agent (business-analyst)
3. ✅ Validate with `scripts/validate-agent-compliance.py`
4. ✅ If successful, batch propagate to remaining 11 agents
5. ✅ Re-run compliance validation, target: 12/12 pass

### Week 2 Mid
1. Create peer reviewer agent templates (business-analyst-reviewer, solution-architect-reviewer, etc.)
2. Document adversarial verification workflow
3. Test peer review cycle with business-analyst → business-analyst-reviewer

### Week 2 End
1. Complete framework propagation to all agents
2. Achieve 12/12 compliance validation pass
3. Begin observability infrastructure planning (logging backend selection)

---

## Long-Term Vision (Month 2+)

### Production Pilot (Month 2)
- Deploy 2-3 agents to production with full observability
- Monitor safety alignment, performance, quality metrics
- Collect real-world feedback
- Iterate on frameworks based on production learnings

### Full Production Rollout (Month 3)
- Deploy all 12 agents to production
- Continuous monitoring and alerting active
- Adversarial verification workflow integrated into agent development lifecycle
- Quarterly adversarial testing audits

### Continuous Improvement (Ongoing)
- Evolve frameworks based on production data
- Add new agents following AGENT_TEMPLATE.yaml v1.2+
- Expand adversarial test coverage
- Optimize observability and error recovery based on incidents

---

**Document Version**: 1.0
**Last Updated**: 2025-10-05
**Next Review**: 2025-10-12 (Week 2 end)
