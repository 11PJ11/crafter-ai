#!/usr/bin/env python3
"""
Fix Agent Framework Format
Adds proper YAML framework structures to all agents
Version: 1.0
Date: 2025-10-05
"""

import re
import sys
from pathlib import Path
from typing import Dict, Tuple

# Agent type classifications
AGENT_TYPES = {
    "document_agents": [
        "business-analyst",
        "solution-architect",
        "acceptance-designer",
        "feature-completion-coordinator"
    ],
    "code_agents": [
        "software-crafter"
    ],
    "research_agents": [
        "knowledge-researcher",
        "data-engineer"
    ],
    "tool_agents": [
        "architecture-diagram-manager",
        "visual-2d-designer",
        "walking-skeleton-helper"
    ],
    "orchestrator_agents": [
        "agent-forger",
        "root-cause-analyzer"
    ]
}


def get_agent_type(agent_name: str) -> str:
    """Determine agent type"""
    for agent_type, agents in AGENT_TYPES.items():
        if agent_name in agents:
            return agent_type
    return "document_agents"  # Default


def get_framework_yaml(agent_name: str, agent_type: str) -> str:
    """Generate framework YAML based on agent type"""

    # Agent-specific customizations
    if agent_type == "document_agents":
        output_examples = '["requirements.md", "architecture.md", "acceptance-tests"]'
        testing_layer1 = "Structural validation (completeness_score > 0.95, acceptance_criteria_quality > 0.90)"
        agent_fields = '["artifacts_created", "completeness_score", "stakeholder_consensus", "handoff_accepted", "quality_gates_passed"]'
        agent_metrics = """
    document_specific:
      requirements_completeness: "> 0.95 (required_sections / total_sections)"
      acceptance_criteria_quality: "> 0.90 (testable_criteria / total_criteria)"
      stakeholder_consensus: "All stakeholders acknowledged"
      handoff_acceptance_rate: "> 0.95 (accepted_handoffs / total_handoffs)" """

    elif agent_type == "code_agents":
        output_examples = '["source_code", "tests", "build_artifacts"]'
        testing_layer1 = "Execution validation (test_pass_rate = 100%, test_coverage > 80%, build_success = true)"
        agent_fields = '["tests_run", "tests_passed", "test_coverage", "build_success", "code_quality_score"]'
        agent_metrics = """
    code_specific:
      test_pass_rate: "100% (passing_tests / total_tests)"
      test_coverage: "> 80% behavior coverage"
      build_success_rate: "true (boolean)"
      code_quality_score: "> 8.0/10.0" """

    elif agent_type == "research_agents":
        output_examples = '["research_reports", "citations", "analysis_documents"]'
        testing_layer1 = "Source verification (all citations verifiable, bias detection, evidence quality)"
        agent_fields = '["sources_verified", "citation_completeness", "bias_checks_passed", "evidence_quality_score"]'
        agent_metrics = """
    research_specific:
      source_verification_rate: "> 95% (verified_sources / total_sources)"
      citation_completeness: "100% (complete_citations / total_citations)"
      bias_detection_score: "> 0.85 (multi-perspective representation)"
      evidence_quality: "> 0.80 (strong_evidence / total_evidence)" """

    elif agent_type == "tool_agents":
        output_examples = '["diagrams", "visualizations", "design_artifacts"]'
        testing_layer1 = "Tool output validation (format correctness, consistency checks, quality standards)"
        agent_fields = '["artifacts_generated", "format_validation_passed", "consistency_score", "quality_rating"]'
        agent_metrics = """
    tool_specific:
      artifact_generation_rate: "100% (successful_generations / total_attempts)"
      format_validation_rate: "100% (valid_formats / total_artifacts)"
      consistency_score: "> 0.90 (consistency_checks_passed / total_checks)"
      quality_rating: "> 8.0/10.0 (human review or automated quality assessment)" """

    else:  # orchestrator_agents
        output_examples = '["workflow_coordination", "delegation_plans", "integration_results"]'
        testing_layer1 = "Workflow validation (phase transitions correct, handoffs complete, coordination successful)"
        agent_fields = '["phases_completed", "handoffs_successful", "coordination_score", "workflow_completion"]'
        agent_metrics = """
    orchestrator_specific:
      phase_completion_rate: "> 95% (completed_phases / total_phases)"
      handoff_success_rate: "> 95% (successful_handoffs / total_handoffs)"
      coordination_score: "> 0.90 (successful_coordinations / total_coordinations)"
      workflow_completion_time: "Track p50, p95, p99 latencies" """

    # Generate complete framework YAML
    framework_yaml = f"""
# Production Frameworks (AGENT_TEMPLATE.yaml v1.2 Compliance)

contract:
  description: "Treat agent as function with explicit inputs and outputs"
  inputs:
    required:
      - type: "user_request"
        format: "Natural language command or question"
        validation: "Non-empty string, valid command syntax"
    optional:
      - type: "configuration"
        format: "YAML or JSON configuration object"
  outputs:
    primary:
      - type: "artifacts"
        format: "Files created or modified"
        examples: {output_examples}
    secondary:
      - type: "validation_results"
        format: "Checklist completion status"
  side_effects:
    allowed:
      - "File creation in designated directories"
      - "File modification with audit trail"
      - "Log entries for audit"
    forbidden:
      - "Deletion without explicit approval"
      - "External API calls without authorization"
      - "Credential access or storage"
      - "Production deployment without validation"
  error_handling:
    on_invalid_input: "Validate inputs before processing, return clear error message"
    on_processing_error: "Log error with context, return to safe state"
    on_validation_failure: "Report which quality gates failed, suggest remediation"

safety_framework:
  input_validation:
    - schema_validation: "Validate structure and data types before processing"
    - content_sanitization: "Remove dangerous patterns (SQL injection, command injection, path traversal)"
    - contextual_validation: "Check business logic constraints and expected formats"
    - security_scanning: "Detect injection attempts and malicious patterns"
  output_filtering:
    - llm_based_guardrails: "AI-powered content moderation for safety"
    - rules_based_filters: "Regex and keyword blocking for sensitive data"
    - relevance_validation: "Ensure on-topic responses aligned with agent purpose"
    - safety_classification: "Block harmful categories (secrets, PII, dangerous code)"
  behavioral_constraints:
    tool_restrictions:
      principle: "Least Privilege - grant only necessary tools"
      allowed_tools: [Read, Write, Edit]
      forbidden_tools: [Bash, WebFetch]
    scope_boundaries:
      allowed_operations: ["{agent_name} domain operations"]
      forbidden_operations: ["credential_access", "data_deletion", "system_modification"]
    file_access:
      allowed_patterns: ["*.md", "*.yaml", "*.py", "*.ts"]
      forbidden_patterns: ["*.env", "credentials.*", "*.key", ".ssh/*"]
  continuous_monitoring:
    misevolution_detection:
      description: "Monitor for safety drift over time"
      metrics: ["safety_alignment_score", "policy_violation_rate", "escalation_frequency"]
      alert_thresholds:
        critical: "safety_score < 0.80, violations > 10/hour"
        warning: "safety_score < 0.90, unusual_patterns"
    anomaly_detection: "Identify unusual patterns in tool usage, outputs, requests"
    performance_tracking: "Monitor effectiveness metrics (response time, error rate, success rate)"
  enterprise_safety_layers:
    layer_1_identity: "Authentication of users and agents, authorization, role-based permissions"
    layer_2_guardrails: "Input validation, output filtering, behavioral constraints"
    layer_3_evaluations: "Automated safety evaluations, performance benchmarks, quality metrics"
    layer_4_adversarial: "Red team exercises, attack simulation, vulnerability discovery"
    layer_5_data_protection: "Encryption, sanitization, privacy preservation"
    layer_6_monitoring: "Real-time tracking, anomaly detection, alert systems"
    layer_7_governance: "Policy enforcement, compliance validation, audit trails"

testing_framework:
  layer_1_unit_testing:
    description: "{testing_layer1}"
    validation_approach: "Automated structural and quality checks"
    pass_criteria:
      - "Output exists and is well-formed"
      - "Required sections/components present"
      - "Quality metrics meet thresholds"
  layer_2_integration_testing:
    description: "Validate handoffs between agents in workflows"
    pattern: "Next agent must be able to consume outputs without clarification"
    validation_steps:
      - "Load handoff package from source agent"
      - "Validate package schema completeness"
      - "Attempt to execute target agent's primary task"
      - "Verify no missing inputs or ambiguities"
  layer_3_adversarial_output_validation:
    description: "Challenge output quality, validity, and robustness through adversarial scrutiny"
    purpose: "Validate OUTPUT quality (distinct from agent security testing)"
    test_categories:
      - "Completeness challenges: What scenarios are missing?"
      - "Ambiguity detection: Can outputs be misinterpreted?"
      - "Edge case validation: How do outputs handle boundaries?"
      - "Quality assessment: Do outputs meet production standards?"
    pass_threshold: "All critical adversarial challenges addressed"
  layer_4_adversarial_verification:
    description: "Peer review by equal agent for bias reduction (NOVEL)"
    reviewer_agent: "{agent_name}-reviewer"
    validates: "Bias, completeness, quality, assumptions - NOT security"
    workflow: "Production → Peer Review → Revision → Approval → Handoff"
    benefits:
      - "Bias Reduction: Fresh perspective not invested in original approach"
      - "Quality Improvement: Identifies gaps original agent missed"
      - "Knowledge Transfer: Best practices shared between agents"

observability_framework:
  structured_logging:
    format: "JSON with universal + agent-specific fields"
    universal_fields:
      - timestamp: "ISO 8601 format (2025-10-03T14:23:45.123Z)"
      - agent_id: "{agent_name}"
      - session_id: "Unique session tracking ID"
      - command: "Command being executed"
      - status: "success | failure | degraded"
      - duration_ms: "Execution time in milliseconds"
    agent_specific_fields: {agent_fields}
    log_levels:
      DEBUG: "Detailed execution flow for troubleshooting"
      INFO: "Normal operational events (command start/end, artifacts created)"
      WARN: "Degraded performance, unusual patterns, quality gate warnings"
      ERROR: "Failures requiring investigation, handoff rejections"
      CRITICAL: "System-level failures, security events requiring immediate attention"
  metrics:
    universal_metrics:
      command_execution_time:
        type: "histogram"
        dimensions: ["agent_id", "command_name"]
        unit: "milliseconds"
      command_success_rate:
        type: "gauge"
        calculation: "count(successful_executions) / count(total_executions)"
        unit: "percentage"
      quality_gate_pass_rate:
        type: "gauge"
        calculation: "count(passed_gates) / count(total_gates)"
        unit: "percentage"
{agent_metrics}
  alerting:
    critical_alerts:
      safety_alignment_critical:
        condition: "safety_alignment_score < 0.85"
        action: "Pause operations, notify security team"
      policy_violation_spike:
        condition: "violations > 5/hour"
        action: "Security team alert, increase monitoring"
      command_error_spike:
        condition: "error_rate > 20%"
        action: "Health check, rollback evaluation"
    warning_alerts:
      performance_degradation:
        condition: "p95_response_time > 5 seconds"
        action: "Performance investigation, resource check"
      quality_gate_failures:
        condition: "failure_rate > 10%"
        action: "Effectiveness review, quality standard validation"

error_recovery_framework:
  retry_strategies:
    exponential_backoff:
      use_when: "Transient failures (network, temporary unavailability)"
      pattern: "1s, 2s, 4s, 8s, 16s (max 5 attempts)"
      jitter: "0-1 second randomization to prevent thundering herd"
    immediate_retry:
      use_when: "Idempotent operations with high success probability"
      pattern: "Up to 3 immediate retries without backoff"
    no_retry:
      use_when: "Permanent failures (validation errors, authorization denied)"
      pattern: "Fail fast and report to user"
  circuit_breakers:
    vague_input_breaker:
      threshold: "5 consecutive vague responses"
      action: "Stop automated elicitation, escalate to human facilitator"
    handoff_rejection_breaker:
      threshold: "2 consecutive rejections"
      action: "Pause workflow, request human review, analyze rejection reasons"
    safety_violation_breaker:
      threshold: "3 violations in 1 hour"
      action: "Immediately halt operations, notify security team, require security clearance"
  degraded_mode:
    strategy: "Provide partial value when full functionality unavailable"
    implementation:
      - "Graceful degradation with reduced feature richness"
      - "Partial results with explicit gaps marked (✅ COMPLETE, ❌ MISSING)"
      - "Clear user communication about completeness %, what's missing, next steps"
    escalation:
      triggers: ["Circuit breaker opens", "Critical quality gate fails", "Unresolvable ambiguity"]
      action: "Human oversight with context and specific guidance needed"
"""

    return framework_yaml


def has_complete_frameworks(content: str) -> bool:
    """Check if agent already has complete frameworks with subsections"""
    yaml_match = re.search(r'```yaml(.*?)```', content, re.DOTALL)
    if not yaml_match:
        return False

    yaml_content = yaml_match.group(1)

    # Check if contract exists AND has subsections
    if not re.search(r'^contract:', yaml_content, re.MULTILINE):
        return False

    # Check for required subsections
    contract_match = re.search(r'^contract:(.*?)(?=^[a-z_]+:|$)', yaml_content, re.MULTILINE | re.DOTALL)
    if contract_match:
        contract_text = contract_match.group(1)
        has_inputs = bool(re.search(r'^\s+inputs:', contract_text, re.MULTILINE))
        has_outputs = bool(re.search(r'^\s+outputs:', contract_text, re.MULTILINE))
        return has_inputs and has_outputs

    return False


def add_frameworks_to_agent(agent_file: Path) -> Tuple[bool, str]:
    """Add frameworks to agent file"""
    agent_name = agent_file.stem
    agent_type = get_agent_type(agent_name)

    print(f"Processing {agent_name} ({agent_type})...")

    with open(agent_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Check if frameworks already exist
    if has_frameworks(content):
        print(f"  ⚠️  {agent_name}: Frameworks already exist, checking structure...")
        # For now, skip agents that already have frameworks
        # In production, we'd validate and update if needed
        return False, "Frameworks already exist"

    # Find YAML block
    yaml_match = re.search(r'(```yaml)(.*?)(```)', content, re.DOTALL)
    if not yaml_match:
        return False, "No YAML block found"

    yaml_prefix = yaml_match.group(1)
    yaml_content = yaml_match.group(2)
    yaml_suffix = yaml_match.group(3)

    # Generate framework YAML
    framework_yaml = get_framework_yaml(agent_name, agent_type)

    # Insert frameworks at end of YAML block (before closing ```)
    new_yaml_content = yaml_content.rstrip() + "\n" + framework_yaml + "\n"

    # Reconstruct file content
    new_content = content[:yaml_match.start()] + yaml_prefix + new_yaml_content + yaml_suffix + content[yaml_match.end():]

    # Write back to file
    with open(agent_file, 'w', encoding='utf-8') as f:
        f.write(new_content)

    print(f"  ✅ {agent_name}: Frameworks added successfully")
    return True, "Success"


def main():
    """Main execution"""
    agents_dir = Path("5d-wave/agents")

    if not agents_dir.exists():
        print(f"❌ Agents directory not found: {agents_dir}")
        sys.exit(1)

    print("=" * 60)
    print("AI-Craft Framework Format Fix")
    print("=" * 60)
    print()

    agent_files = sorted(agents_dir.glob("*.md"))

    if not agent_files:
        print("❌ No agent files found")
        sys.exit(1)

    print(f"Found {len(agent_files)} agent files")
    print()

    results = {
        "total": 0,
        "updated": 0,
        "skipped": 0,
        "failed": 0
    }

    for agent_file in agent_files:
        results["total"] += 1
        success, message = add_frameworks_to_agent(agent_file)

        if success:
            results["updated"] += 1
        elif "already exist" in message:
            results["skipped"] += 1
        else:
            results["failed"] += 1
            print(f"  ❌ Failed: {message}")

    print()
    print("=" * 60)
    print("Fix Complete")
    print("=" * 60)
    print(f"Total Agents: {results['total']}")
    print(f"Updated: {results['updated']}")
    print(f"Skipped (already had frameworks): {results['skipped']}")
    print(f"Failed: {results['failed']}")
    print()

    if results['failed'] > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
