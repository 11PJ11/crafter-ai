# AI-Craft Framework Constants

## File Path Constants

### Core Documentation Paths
```yaml
DOCS_PATH: "docs/craft-ai"
STATE_PATH: "state/craft-ai"
AGENT_PATH: ".claude/agents/cai"
WAVE_PROGRESS_FILE: "wave-progress.json"
AGENT_EXECUTION_LOG_FILE: "agent-execution.log"
PIPELINE_STATE_FILE: "pipeline-state.json"
```

### Agent Output File Paths

#### Second Way - Observability Agents
```yaml
# Telemetry Collector
TELEMETRY_COLLECTION_REPORT: "${DOCS_PATH}/telemetry-collection-report.md"
OBSERVABILITY_DATA_CATALOG: "${DOCS_PATH}/observability-data-catalog.md"
TELEMETRY_CONFIGURATION_STATUS: "${DOCS_PATH}/telemetry-configuration-status.md"

# Observability Analyzer
OBSERVABILITY_ANALYSIS_REPORT: "${DOCS_PATH}/observability-analysis-report.md"
SYSTEM_HEALTH_INSIGHTS: "${DOCS_PATH}/system-health-insights.md"
PROACTIVE_RECOMMENDATIONS: "${DOCS_PATH}/proactive-recommendations.md"
OBSERVABILITY_TREND_ANALYSIS: "${DOCS_PATH}/observability-trend-analysis.md"

# User Feedback Aggregator
USER_FEEDBACK_ANALYSIS_REPORT: "${DOCS_PATH}/user-feedback-analysis-report.md"
CUSTOMER_INSIGHTS_SYNTHESIS: "${DOCS_PATH}/customer-insights-synthesis.md"
SATISFACTION_TREND_ANALYSIS: "${DOCS_PATH}/satisfaction-trend-analysis.md"
FEEDBACK_PRIORITIZATION_MATRIX: "${DOCS_PATH}/feedback-prioritization-matrix.md"

# Performance Monitor
PERFORMANCE_MONITORING_REPORT: "${DOCS_PATH}/performance-monitoring-report.md"
PERFORMANCE_ALERTS_DASHBOARD: "${DOCS_PATH}/performance-alerts-dashboard.md"
CAPACITY_PLANNING_FORECAST: "${DOCS_PATH}/capacity-planning-forecast.md"
PERFORMANCE_OPTIMIZATION_RECOMMENDATIONS: "${DOCS_PATH}/performance-optimization-recommendations.md"
```

#### Third Way - Experimentation Agents
```yaml
# Experiment Designer
EXPERIMENT_DESIGN_SPECIFICATION: "${DOCS_PATH}/experiment-design-specification.md"
HYPOTHESIS_CATALOG: "${DOCS_PATH}/hypothesis-catalog.md"
EXPERIMENT_PIPELINE_STATUS: "${DOCS_PATH}/experiment-pipeline-status.md"
EXPERIMENTATION_GUIDELINES: "${DOCS_PATH}/experimentation-guidelines.md"

# Hypothesis Validator
HYPOTHESIS_VALIDATION_REPORT: "${DOCS_PATH}/hypothesis-validation-report.md"
STATISTICAL_ANALYSIS_DETAILS: "${DOCS_PATH}/statistical-analysis-details.md"
EXPERIMENT_INSIGHTS_SUMMARY: "${DOCS_PATH}/experiment-insights-summary.md"
VALIDATION_METHODOLOGY_NOTES: "${DOCS_PATH}/validation-methodology-notes.md"

# Learning Synthesizer
ORGANIZATIONAL_LEARNING_SYNTHESIS: "${DOCS_PATH}/organizational-learning-synthesis.md"
KNOWLEDGE_REPOSITORY_INDEX: "${DOCS_PATH}/knowledge-repository-index.md"
LEARNING_APPLICATION_GUIDANCE: "${DOCS_PATH}/learning-application-guidance.md"
KNOWLEDGE_EVOLUTION_TRACKING: "${DOCS_PATH}/knowledge-evolution-tracking.md"

# Priority Optimizer
STRATEGIC_PRIORITY_OPTIMIZATION: "${DOCS_PATH}/strategic-priority-optimization.md"
RESOURCE_ALLOCATION_OPTIMIZATION: "${DOCS_PATH}/resource-allocation-optimization.md"
PRIORITY_CHANGE_RATIONALE: "${DOCS_PATH}/priority-change-rationale.md"
LEARNING_OPTIMIZATION_PLAN: "${DOCS_PATH}/learning-optimization-plan.md"
```

## Agent Registry

### ATDD Wave Agents
```yaml
DISCUSS:
  - business-analyst
  - user-experience-designer
  - technical-stakeholder
  - security-expert
  - legal-compliance-advisor

ARCHITECT:
  - solution-architect
  - technology-selector
  - architecture-diagram-manager

DISTILL:
  - acceptance-designer

DEVELOP:
  - test-first-developer

DEMO:
  - production-readiness-helper
  - walking-skeleton-helper

COORDINATION:
  - atdd-wave-coordinator
  - atdd-command-processor
  - pipeline-state-manager
  - technical-debt-tracker

QUALITY-VALIDATION:
  - commit-readiness-coordinator
```

### Second Way - Observability Agents
```yaml
OBSERVABILITY:
  - telemetry-collector
  - observability-analyzer
  - user-feedback-aggregator
  - performance-monitor
```

### Third Way - Experimentation Agents
```yaml
EXPERIMENTATION:
  - experiment-designer
  - hypothesis-validator
  - learning-synthesizer
  - priority-optimizer
```

## Integration Constants

### Wave Integration Points
```yaml
WAVE_HANDOFF_CRITERIA: "Defined completion criteria for each wave transition"
WAVE_QUALITY_GATES: "Validation requirements for wave progression"
WAVE_STATE_TRACKING: "Progress tracking across wave execution"
CROSS_WAVE_CONTEXT: "Context preservation between wave transitions"
```

### Pipeline Integration
```yaml
PIPELINE_ORCHESTRATION: "Agent coordination and workflow management"
STATE_MANAGEMENT: "Persistent state across agent executions"
CONTEXT_HANDOFF: "Information transfer between agents"
VALIDATION_CHECKPOINTS: "Quality gates and validation points"
```

### DevOps Three Ways Integration
```yaml
FIRST_WAY_FLOW: "ATDD wave progression with continuous flow optimization"
SECOND_WAY_FEEDBACK: "Observability agents providing real-time feedback loops"
THIRD_WAY_LEARNING: "Experimentation agents driving continuous learning and improvement"
```

## Enhanced Configuration Constants

### Quality Thresholds
```yaml
TEST_COVERAGE_THRESHOLD: 80
PERFORMANCE_SLA_THRESHOLD: 95
ERROR_RATE_THRESHOLD: 0.01
UPTIME_TARGET: 99.9
STORY_CONTEXT_COMPLETENESS_THRESHOLD: 95
WAVE_TRANSITION_VALIDATION_THRESHOLD: 90
```

### Wave Adaptation Rules
```yaml
# Dynamic Wave Configuration Rules (Inspired by BMAD-METHOD patterns)
WAVE_ADAPTATION_RULES:
  # Agent Embodiment Configuration
  AGENT_TRANSFORMATION_MATRIX:
    business-analyst: ["requirements_conflicts", "stakeholder_alignment", "business_process_mapping"]
    solution-architect: ["architecture_decisions", "technology_conflicts", "design_validation"]
    acceptance-designer: ["test_scenario_conflicts", "validation_criteria_issues", "coverage_gaps"]
    test-first-developer: ["implementation_blocking", "tdd_guidance_needed", "quality_validation"]
    feature-completion-coordinator: ["completion_validation", "demo_preparation", "handoff_issues"]

  # Context Compression Templates
  CONTEXT_COMPRESSION_TEMPLATES:
    wave_1_to_2: "{{business_requirements}} + {{stakeholder_constraints}} → {{architectural_context}}"
    wave_2_to_3: "{{architecture_overview}} + {{technology_decisions}} → {{test_design_context}}"
    wave_3_to_4: "{{test_scenarios}} + {{validation_criteria}} → {{implementation_context}}"
    wave_4_to_5: "{{implementation_status}} + {{quality_metrics}} → {{completion_context}}"

  # Interactive Guidance Configuration
  INTERACTIVE_GUIDANCE_RULES:
    decision_confidence_threshold: 85
    fuzzy_matching_threshold: 75
    option_selection_format: "numbered_list"
    max_options_per_decision: 5

  # Workflow Adaptation Patterns
  WORKFLOW_ADAPTATION_PATTERNS:
    greenfield_full_stack:
      waves: ["DISCUSS", "ARCHITECT", "DISTILL", "DEVELOP", "DEMO"]
      complexity: "comprehensive"
      duration_estimate: "2-4 weeks"

    brownfield_enhancement:
      waves: ["DISCUSS_MODIFIED", "ARCHITECT_INTEGRATION", "DISTILL", "DEVELOP", "DEMO"]
      complexity: "moderate"
      duration_estimate: "1-2 weeks"

    rapid_prototype:
      waves: ["DISCUSS_BRIEF", "ARCHITECT_MINIMAL", "DEVELOP", "DEMO"]
      complexity: "simple"
      duration_estimate: "2-5 days"
```

### Story Context Embedding Rules
```yaml
# Story Context Management Configuration
STORY_CONTEXT_RULES:
  # Context Embedding Templates
  CONTEXT_EMBEDDING_TEMPLATES:
    business_context: "{{project_goals}}, {{stakeholder_needs}}, {{business_constraints}}"
    technical_context: "{{architecture_summary}}, {{technology_decisions}}, {{quality_requirements}}"
    implementation_context: "{{acceptance_criteria}}, {{test_scenarios}}, {{development_guidance}}"

  # Hyper-Detailed Story Requirements
  STORY_COMPLETENESS_CRITERIA:
    business_context_required: true
    architectural_context_embedded: true
    implementation_guidance_provided: true
    acceptance_criteria_detailed: true
    validation_requirements_specified: true
    error_prevention_guidance_included: true

  # Context Preservation Rules
  CONTEXT_PRESERVATION_RULES:
    cross_reference_integrity: "maintain_epic_to_story_links"
    architectural_consistency: "embed_relevant_architecture_context"
    acceptance_criteria_integration: "inline_validation_requirements"
    implementation_guidance_depth: "include_specific_technical_approach"
```

### Phase Transition Configuration
```yaml
# Phase Transition Management Rules
PHASE_TRANSITION_RULES:
  # Planning Completeness Validation
  PLANNING_VALIDATION_CRITERIA:
    requirements_completeness: 95
    architecture_completeness: 90
    acceptance_criteria_coverage: 85
    stakeholder_approval_required: true

  # Document Sharding Configuration
  DOCUMENT_SHARDING_RULES:
    epic_level_sharding: "group_related_stories_by_business_value"
    story_level_context_embedding: "include_full_architectural_and_business_context"
    architecture_component_separation: "organize_by_system_components_and_integration"
    cross_reference_maintenance: "preserve_all_document_relationships"

  # Transition State Management
  TRANSITION_STATE_TRACKING:
    transition_phases: ["planning_validation", "document_sharding", "transition_validation", "execution_handoff"]
    rollback_points: ["pre_sharding_documents", "post_sharding_validation", "pre_execution_handoff"]
    state_persistence_file: "${STATE_PATH}/phase-transition-state.json"
```

### Observability Configuration
```yaml
METRICS_RETENTION_DAYS: 90
LOG_RETENTION_DAYS: 30
TRACE_SAMPLING_RATE: 0.1
ALERT_ESCALATION_MINUTES: 15
```

### Experimentation Configuration
```yaml
EXPERIMENT_CONFIDENCE_LEVEL: 95
EXPERIMENT_STATISTICAL_POWER: 80
EXPERIMENT_MIN_SAMPLE_SIZE: 1000
EXPERIMENT_MAX_DURATION_DAYS: 30
```