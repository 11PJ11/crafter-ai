# /cai:help - Interactive Guidance and Agent Transformation

```yaml
---
command: "/cai:help"
category: "Meta & Orchestration"
purpose: "Interactive guidance and ATDD wave coordinator transformation"
wave-enabled: false
performance-profile: "standard"
---
```

## Overview

Interactive guidance system providing help, agent transformation capabilities, and workflow navigation support for the AI-Craft ATDD framework.

## Auto-Persona Activation
- **Mentor**: Educational guidance and knowledge transfer (conditional)
- **Analyzer**: Context analysis and recommendation generation (conditional)
- **Wave Coordinator**: Agent transformation and workflow guidance (default)

## MCP Server Integration
- **Primary**: Sequential (structured guidance and interactive decision-making)
- **Secondary**: Context7 (help patterns and guidance best practices)
- **Avoided**: Magic and Playwright (focus on guidance over generation/testing)

## Tool Orchestration
- **Task**: Interactive elicitation agent activation
- **Read**: Context analysis and project state assessment
- **Write**: Guidance documentation and help artifacts
- **TodoWrite**: Help session progress and guidance tracking

## Agent Flow
```yaml
without_agent_name:
  comprehensive_help:
    - Shows complete command catalog with descriptions
    - Offers workflow guidance based on current project context
    - Provides agent directory with specializations and capabilities
    - Assesses current project state and recommends next steps

with_agent_name:
  agent_transformation:
    - Transforms ATDD wave coordinator into specified agent
    - Provides agent-specific command reference and capabilities
    - Enables agent-focused interactive mode with specialized guidance
    - Maintains agent context for subsequent interactions

interactive_mode:
  guided_assistance:
    - Launches interactive elicitation with numbered options
    - Provides contextual guidance for current wave and development phase
    - Offers step-by-step workflow navigation and decision support
    - Adapts guidance based on project complexity and user experience
```

## Arguments

### Basic Usage
```bash
/cai:help
```

### Agent Transformation Usage
```bash
/cai:help [agent-name]
```

### Advanced Usage
```bash
/cai:help [agent-name] --interactive --context-analysis --recommendations
```

### Agent Transformation
- `[agent-name]`: Specific agent to transform into (e.g., "architect", "business-analyst")
- Available agents: `business-analyst`, `solution-architect`, `acceptance-designer`, `test-first-developer`, `systematic-refactorer`, etc.

### Guidance Control
- `--interactive`: Enable interactive elicitation mode with numbered options
- `--workflow-guidance`: Focus on workflow selection and navigation guidance
- `--command-reference`: Provide comprehensive command reference and examples
- `--troubleshooting`: Focus on problem-solving and troubleshooting guidance

### Context Analysis
- `--context-analysis`: Analyze current project state and provide recommendations
- `--next-steps`: Recommend optimal next steps based on project context
- `--wave-status`: Analyze current wave progress and provide wave-specific guidance
- `--recommendations`: Generate personalized recommendations based on project analysis

## Help System Framework

### Comprehensive Help Display
```yaml
command_catalog:
  essential_commands:
    - cai:analyze: "Brownfield project analysis and technical debt assessment"
    - cai:refactor: "Systematic refactoring from Level 1-6 or Mikado Method"
    - cai:start: "Initialize ATDD workflow with intelligent workflow selection"
    - cai:discuss: "Requirements gathering and stakeholder collaboration"
    - cai:architect: "System architecture design and technology decisions"
    - cai:develop: "Outside-In TDD implementation of user stories"
    - cai:transition: "Bridge planning phase to execution with context preservation"
    - cai:validate: "Comprehensive quality validation and compliance checking"
    - cai:complete: "Feature finalization and production readiness validation"
    - cai:help: "Interactive guidance and agent transformation"

workflow_guidance:
  atdd_waves:
    wave_1_discuss: "Requirements clarification and stakeholder collaboration"
    wave_2_architect: "System design and technology decision-making"
    wave_3_distill: "Acceptance criteria and detailed story creation"
    wave_4_develop: "Outside-In TDD implementation"
    wave_5_demo: "Stakeholder validation and production preparation"

  workflow_patterns:
    greenfield_full_stack: "Complete ATDD for new full-stack applications (2-4 weeks)"
    brownfield_enhancement: "Feature enhancement for existing systems (1-2 weeks)"
    rapid_prototype: "Quick validation and MVP development (2-5 days)"
    api_service: "Backend service and API development (1-3 weeks)"
    ui_component: "Frontend component and interface development (1-2 weeks)"
```

### Agent Directory and Specializations
```yaml
coordination_agents:
  atdd-wave-coordinator: "Overall ATDD workflow orchestration and agent transformation"
  phase-transition-manager: "Planning to execution bridge with context preservation"
  story-context-manager: "Hyper-detailed story creation with embedded context"
  workflow-guidance-agent: "Interactive workflow selection and configuration"

domain_experts:
  business-analyst: "Requirements capture, stakeholder collaboration, business constraints"
  solution-architect: "System design, architectural patterns, technology decisions"
  user-experience-designer: "User journey mapping, interface design, accessibility"
  security-expert: "Security requirements, threat modeling, compliance validation"
  technical-stakeholder: "Technical constraints, feasibility assessment, integration requirements"

implementation_agents:
  acceptance-designer: "Acceptance criteria, test scenarios, validation requirements"
  test-first-developer: "Outside-In TDD, double-loop development, production code"
  systematic-refactorer: "Level 1-6 refactoring, code quality improvement"
  mikado-refactoring-specialist: "Complex architectural refactoring using Mikado Method"

quality_validation_agents:
  commit-readiness-coordinator: "Comprehensive validation orchestration"
  code-quality-validator: "Static analysis, complexity metrics, maintainability"
  architecture-compliance-validator: "Architectural pattern adherence, boundary enforcement"
  security-performance-validator: "Security compliance, performance validation"
```

## Agent Transformation System

### Transformation Commands
```yaml
agent_transformation_commands:
  help: "Show numbered list of available commands and agent transformation options"
  agent: "Transform into specialized agent (list options if name not specified)"
  wave: "Execute specific wave with embodied coordination capabilities"
  guidance: "Start interactive workflow guidance mode with numbered options"
  status: "Show current workflow status and wave progression"
  compress: "Enable context compression for efficient wave transitions"
  exit: "Return to standard ATDD wave coordinator mode"
```

### Agent-Specific Command Sets
```yaml
business-analyst_commands:
  requirements: "Start requirements elicitation workshop with stakeholder simulation"
  stakeholder: "Simulate different stakeholder perspectives for requirements gathering"
  constraints: "Document business constraints and limitations"
  stories: "Create user stories with comprehensive acceptance criteria"

solution-architect_commands:
  design: "Create comprehensive architectural design with component analysis"
  decisions: "Make and document architectural decisions with trade-off analysis"
  patterns: "Apply and document architectural patterns and design principles"
  technology: "Evaluate and select technology stack with rationale"

test-first-developer_commands:
  tdd: "Start Outside-In TDD implementation with double-loop architecture"
  scaffold: "Create test scaffolding with NotImplementedException pattern"
  implement: "Implement production code following RED-GREEN-REFACTOR cycles"
  validate: "Validate implementation against acceptance criteria and business requirements"
```

## Interactive Elicitation Integration

### Interactive Guidance Modes
```yaml
workflow_selection_guidance:
  assessment_questions:
    project_type: "New project, existing system enhancement, or prototype?"
    technical_focus: "Full-stack, backend, frontend, or integration focus?"
    complexity_level: "Simple, moderate, complex, or highly complex implementation?"
    timeline_expectations: "Days, weeks, or months for completion?"

  intelligent_recommendations:
    fuzzy_matching: "≥85% confidence threshold for direct workflow recommendations"
    context_analysis: "Project keyword analysis and complexity assessment"
    interactive_refinement: "Numbered option selection for decision refinement"
    customization_guidance: "Workflow adaptation based on specific project needs"

troubleshooting_guidance:
  common_issues:
    context_loss: "How to preserve context during wave transitions"
    test_failures: "Debugging ATDD test failures and implementation issues"
    refactoring_complexity: "Choosing appropriate refactoring level and techniques"
    production_readiness: "Addressing production deployment blockers"

  step_by_step_solutions:
    numbered_options: "Clear numbered options for problem resolution"
    escalation_paths: "When to involve specific agents or additional expertise"
    validation_steps: "How to validate that problems are properly resolved"
```

## Context-Aware Guidance

### Project State Analysis
```yaml
current_wave_analysis:
  wave_progress_assessment: "Analysis of current wave completion status"
  next_step_recommendations: "Optimal next actions based on current state"
  blocker_identification: "Identification of current blockers and resolution strategies"
  quality_gate_status: "Status of quality gates and validation requirements"

project_health_assessment:
  technical_debt_analysis: "Current technical debt levels and priority recommendations"
  test_coverage_status: "Test coverage analysis and improvement recommendations"
  architecture_alignment: "Implementation alignment with architectural decisions"
  stakeholder_satisfaction: "Business stakeholder feedback and satisfaction assessment"
```

### Personalized Recommendations
- **Experience-Based Guidance**: Recommendations based on user experience level
- **Project-Specific Advice**: Guidance tailored to current project context and challenges
- **Learning Opportunities**: Educational recommendations for skill development
- **Best Practice Integration**: Recommendations for adopting ATDD best practices

## Quality Gates

### Guidance Quality
- **Relevance**: Guidance is relevant to current project context and user needs
- **Clarity**: Information is clear, actionable, and easy to understand
- **Completeness**: All necessary information provided for decision-making
- **Accuracy**: Guidance reflects current best practices and framework capabilities

### User Experience
- **Responsiveness**: Quick response to help requests with minimal latency
- **Interactivity**: Engaging interactive experience with numbered options
- **Progression**: Clear progression through guidance and decision-making processes
- **Satisfaction**: User satisfaction with guidance quality and effectiveness

## Examples

### General Help and Command Reference
```bash
/cai:help
```

### Agent Transformation Examples
```bash
# Transform into solution architect
/cai:help architect

# Transform into business analyst with interactive mode
/cai:help business-analyst --interactive

# Transform into test-first developer
/cai:help test-first-developer
```

### Context-Aware Guidance
```bash
# Get recommendations based on current project state
/cai:help --context-analysis --recommendations

# Interactive workflow guidance
/cai:help --workflow-guidance --interactive

# Troubleshooting assistance
/cai:help --troubleshooting --next-steps
```

### Specialized Guidance
```bash
# Focus on command reference
/cai:help --command-reference

# Wave-specific guidance
/cai:help --wave-status --next-steps

# Interactive project guidance
/cai:help --interactive --context-analysis
```

ARGUMENTS: create the commands under the @.claude\commands\cai\ folder so we can install them together with the rest