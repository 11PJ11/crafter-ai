#!/usr/bin/env python3
"""
Framework Format Fix Script
Adds properly structured YAML frameworks to all 12 agents
"""

import os
import re
from pathlib import Path

AGENTS_DIR = Path("/mnt/c/Repositories/Projects/ai-craft/nWave/agents")

# Agent type mapping
AGENT_TYPES = {
    'business-analyst': 'document',
    'solution-architect': 'document',
    'acceptance-designer': 'document',
    'software-crafter': 'code',
    'knowledge-researcher': 'research',
    'data-engineer': 'research',
    'architecture-diagram-manager': 'tool',
    'visual-2d-designer': 'tool',
    'feature-completion-coordinator': 'orchestrator',
    'root-cause-analyzer': 'analysis',
    'walking-skeleton-helper': 'helper',
    'agent-forger': 'meta'
}

# Agent-type-specific customizations
CUSTOMIZATIONS = {
    'document': {
        'output_examples': 'requirements.md',
        'testing_layer1': 'Structural validation (completeness_score > 0.95)',
        'observability_fields': ['artifacts_created', 'completeness_score', 'handoff_accepted'],
        'allowed_tools': ['Read', 'Write', 'Edit', 'Grep', 'Glob'],
        'forbidden_tools': ['Bash', 'WebFetch', 'Execute']
    },
    'code': {
        'output_examples': 'source_code, tests, build_artifacts',
        'testing_layer1': 'Execution validation (test_pass_rate = 100%, coverage > 80%)',
        'observability_fields': ['tests_run', 'tests_passed', 'test_coverage', 'build_success'],
        'allowed_tools': ['Read', 'Write', 'Edit', 'Bash', 'Grep', 'Glob'],
        'forbidden_tools': ['WebFetch', 'Execute']
    },
    'research': {
        'output_examples': 'research_documents_with_citations',
        'testing_layer1': 'Source quality (all sources verifiable)',
        'observability_fields': ['sources_verified', 'citation_completeness'],
        'allowed_tools': ['Read', 'Write', 'Edit', 'WebFetch', 'Grep', 'Glob'],
        'forbidden_tools': ['Bash', 'Execute']
    },
    'tool': {
        'output_examples': 'diagrams, visual_artifacts',
        'testing_layer1': 'Format validation, standards compliance',
        'observability_fields': ['diagrams_created', 'format_validation'],
        'allowed_tools': ['Read', 'Write', 'Edit', 'Grep', 'Glob'],
        'forbidden_tools': ['Bash', 'WebFetch', 'Execute']
    },
    'orchestrator': {
        'output_examples': 'workflow_status, handoff_coordination',
        'testing_layer1': 'Workflow validation (all phases complete)',
        'observability_fields': ['phases_completed', 'handoffs_successful'],
        'allowed_tools': ['Read', 'Write', 'Edit', 'Grep', 'Glob'],
        'forbidden_tools': ['Bash', 'WebFetch', 'Execute']
    },
    'analysis': {
        'output_examples': '5_whys_analysis, root_cause_documentation',
        'testing_layer1': 'Causality validation, evidence quality',
        'observability_fields': ['whys_completed', 'root_causes_identified'],
        'allowed_tools': ['Read', 'Write', 'Edit', 'Grep', 'Glob'],
        'forbidden_tools': ['Bash', 'WebFetch', 'Execute']
    },
    'helper': {
        'output_examples': 'minimal_e2e_implementation_guide',
        'testing_layer1': 'E2E validation readiness',
        'observability_fields': ['skeleton_completeness'],
        'allowed_tools': ['Read', 'Write', 'Edit', 'Grep', 'Glob'],
        'forbidden_tools': ['Bash', 'WebFetch', 'Execute']
    },
    'meta': {
        'output_examples': 'agent_specifications',
        'testing_layer1': 'AGENT_TEMPLATE.yaml compliance validation',
        'observability_fields': ['agents_created', 'compliance_score'],
        'allowed_tools': ['Read', 'Write', 'Edit', 'Grep', 'Glob'],
        'forbidden_tools': ['WebFetch', 'Execute']
    }
}

def generate_frameworks_yaml(agent_id, agent_type):
    """Generate YAML frameworks for an agent"""
    custom = CUSTOMIZATIONS[agent_type]

    return f"""
# Production Frameworks (YAML Format)

contract:
  inputs:
    required:
      - type: "user_request"
        format: "Natural language command"
        validation: "Non-empty string"
  outputs:
    primary:
      - type: "artifacts"
        examples: ["{custom['output_examples']}"]
  side_effects:
    allowed: ["File creation/modification", "Log entries"]
    forbidden: ["Deletion without approval", "Credential access"]
  error_handling:
    on_invalid_input: "Validate, return clear error"
    on_processing_error: "Log with context, safe state"

safety_framework:
  input_validation:
    - schema_validation: "Validate structure and data types"
    - content_sanitization: "Remove dangerous patterns"
    - contextual_validation: "Business logic constraints"
    - security_scanning: "Detect prompt injection"
  output_filtering:
    - llm_based_guardrails: "AI-powered moderation"
    - rules_based_filters: "Regex/keyword blocking"
    - relevance_validation: "On-topic responses"
  behavioral_constraints:
    tool_restrictions:
      principle: "Least Privilege"
      allowed_tools: {custom['allowed_tools']}
      forbidden_tools: {custom['forbidden_tools']}
    scope_boundaries:
      allowed_operations: ["Analysis", "Documentation creation"]
      forbidden_operations: ["Credential access", "Data deletion"]
  continuous_monitoring:
    - misevolution_detection: "Safety drift monitoring"
    - anomaly_detection: "Unusual patterns"
    - performance_tracking: "Response time, error rate"
  enterprise_safety_layers:
    layer_1_identity: "Authentication, authorization, RBAC"
    layer_2_guardrails: "Input validation, output filtering"
    layer_3_evaluations: "Automated safety evaluations"
    layer_4_adversarial: "Red team exercises"
    layer_5_data_protection: "Encryption, sanitization"
    layer_6_monitoring: "Real-time tracking, anomaly detection"
    layer_7_governance: "Policy enforcement, compliance"

testing_framework:
  layer_1_unit_testing:
    description: "{custom['testing_layer1']}"
    applies_to: "All {agent_type} agents"
  layer_2_integration_testing:
    description: "Validate handoffs between agents"
    pattern: "Next agent consumes without clarification"
  layer_3_adversarial_output_validation:
    description: "Challenge output quality and validity"
    test_categories: ["Output quality challenges", "Edge case testing"]
  layer_4_adversarial_verification:
    description: "Peer review for bias reduction"
    reviewer_agent: "{agent_id}-reviewer"
    workflow: "Production → Review → Revision → Approval"

observability_framework:
  structured_logging:
    format: "JSON with universal + agent-specific fields"
    universal_fields: [timestamp, agent_id, session_id, command, status, duration_ms]
    agent_specific_fields: {custom['observability_fields']}
  metrics_collection:
    universal_metrics:
      - command_execution_time: "Histogram"
      - command_success_rate: "Gauge"
      - quality_gate_pass_rate: "Gauge"
  alerting:
    critical_alerts:
      - safety_alignment_critical: "score < 0.85"
      - policy_violation_spike: "> 5/hour"
    warning_alerts:
      - performance_degradation: "p95 > 5s"
      - quality_gate_failures: "> 10%"

error_recovery_framework:
  retry_strategies:
    exponential_backoff:
      pattern: "1s, 2s, 4s, 8s, 16s (max 5)"
      use_when: "Transient failures"
    immediate_retry:
      pattern: "Up to 3 immediate retries"
      use_when: "Idempotent operations"
    no_retry:
      pattern: "Fail fast"
      use_when: "Permanent failures"
  circuit_breakers:
    vague_input_breaker:
      threshold: "5 consecutive vague responses"
      action: "Escalate to human"
    handoff_rejection_breaker:
      threshold: "2 consecutive rejections"
      action: "Pause workflow, request review"
    safety_violation_breaker:
      threshold: "3 violations/hour"
      action: "Immediate halt, notify security"
  degraded_mode:
    strategy: "Partial value when full functionality unavailable"
    output_format: "✅ COMPLETE + ❌ MISSING with TODO"
"""

def main():
    """Add frameworks to all agents"""
    print("Framework Format Fix Script")
    print("=" * 60)

    results = []

    for agent_file in sorted(AGENTS_DIR.glob("*.md")):
        agent_id = agent_file.stem

        if agent_id not in AGENT_TYPES:
            print(f"⚠️  Skipping {agent_id} (not in agent type mapping)")
            continue

        agent_type = AGENT_TYPES[agent_id]
        print(f"\n📝 Processing: {agent_id} ({agent_type})")

        # Read existing content
        content = agent_file.read_text(encoding='utf-8')

        # Check if frameworks already exist
        if 'enterprise_safety_layers:' in content:
            print(f"   ✅ Frameworks already in proper format")
            results.append((agent_id, 'SKIP', 'Already has proper frameworks'))
            continue

        # Generate and append frameworks
        frameworks = generate_frameworks_yaml(agent_id, agent_type)
        updated_content = content + "\n" + frameworks

        # Write back
        agent_file.write_text(updated_content, encoding='utf-8')
        print(f"   ✅ Added production frameworks")
        results.append((agent_id, 'SUCCESS', 'Frameworks added'))

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)

    success_count = sum(1 for _, status, _ in results if status == 'SUCCESS')
    skip_count = sum(1 for _, status, _ in results if status == 'SKIP')

    print(f"✅ Successfully updated: {success_count}/12 agents")
    print(f"⏭️  Skipped (already done): {skip_count}/12 agents")
    print(f"📊 Total processed: {len(results)}/12 agents")

    print("\nNext step: Run compliance validation")
    print("  python3 scripts/validate-agent-compliance.py")

if __name__ == "__main__":
    main()
