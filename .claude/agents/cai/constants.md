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

## Configuration Constants

### Quality Thresholds
```yaml
TEST_COVERAGE_THRESHOLD: 80
PERFORMANCE_SLA_THRESHOLD: 95
ERROR_RATE_THRESHOLD: 0.01
UPTIME_TARGET: 99.9
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