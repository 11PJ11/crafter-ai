# /cai:start - Initialize ATDD Workflow

```yaml
---
command: "/cai:start"
category: "Planning & Orchestration"
purpose: "Initialize ATDD workflow with intelligent workflow selection"
wave-enabled: true
performance-profile: "standard"
---
```

## Overview

Comprehensive ATDD workflow initialization with intelligent workflow pattern selection and project setup.

## Auto-Persona Activation
- **Architect**: System planning and design guidance
- **Analyzer**: Project context assessment
- **Mentor**: Workflow guidance and education

## MCP Server Integration
- **Primary**: Sequential (workflow analysis and systematic planning)
- **Secondary**: Context7 (workflow patterns and best practices)
- **Tertiary**: Magic (UI-focused projects)

## Tool Orchestration
- **Task**: Workflow guidance agent activation
- **Read**: Existing project analysis
- **Write**: Workflow configuration and setup files
- **TodoWrite**: Project planning and task creation

## Agent Flow
```yaml
workflow-guidance-agent:
  - Assesses project type and complexity
  - Recommends optimal workflow pattern
  - Provides interactive workflow selection
  - Configures wave sequence and priorities

atdd-wave-coordinator:
  - Initializes selected workflow
  - Sets up 5-wave progression (DISCUSS→ARCHITECT→DISTILL→DEVELOP→DEMO)
  - Configures agent transformation capabilities
  - Establishes context compression and handoff mechanisms
```

## Arguments

### Basic Usage
```bash
/cai:start [project-description]
```

### Advanced Usage
```bash
/cai:start [project-description] --workflow <type> --interactive --scope <level>
```

### Project Description
- Natural language description of the project or feature
- Examples: "e-commerce checkout feature", "user authentication system", "real-time chat application"

### Workflow Selection
- `--workflow greenfield`: New project from scratch (2-4 weeks)
- `--workflow brownfield`: Existing system enhancement (1-2 weeks)
- `--workflow prototype`: Rapid validation and MVP (2-5 days)
- `--workflow api`: Backend service development (1-3 weeks)
- `--workflow ui`: UI component development (1-2 weeks)
- `--workflow integration`: System integration (2-6 weeks)

### Scope Control
- `--scope feature`: Single feature implementation
- `--scope module`: Module-level development
- `--scope system`: System-wide implementation
- `--scope epic`: Epic-level planning

### Interaction Control
- `--interactive`: Enable numbered option selection and guided setup
  - Provides intelligent workflow recommendations based on project analysis
  - Shows detailed pros/cons for each workflow option with rationale
  - Allows customization of workflow phases and agent coordination
  - Enables iterative refinement of workflow configuration
- `--guided`: Step-by-step workflow configuration with detailed explanations
  - Walks through each workflow phase with comprehensive guidance
  - Configures agent coordination and tool orchestration settings
  - Sets up quality gates and validation checkpoints systematically
  - Provides educational context for workflow decisions
- `--assessment`: Detailed project assessment before workflow selection
  - Analyzes existing codebase and documentation for context
  - Estimates resource requirements and timeline projections
  - Identifies potential risks and mitigation strategies
  - Evaluates team capabilities and tooling requirements

### Workflow Customization
- `--methodology <type>`: Select development methodology approach
  - `atdd`: Full ATDD with 5-wave progression (discuss→architect→distill→develop→demo)
  - `tdd`: Test-driven development focused workflow
  - `bdd`: Behavior-driven development with stakeholder emphasis
  - `lean`: Lean development with waste elimination focus
- `--scope <level>`: Define project scope and boundaries
  - `feature`: Single feature development workflow
  - `epic`: Multi-feature epic coordination with dependency management
  - `system`: System-wide development orchestration
  - `component`: Component-focused development cycle

### Quality and Process Control
- `--validation`: Enable comprehensive workflow validation
  - Validates workflow selection against project requirements
  - Ensures proper agent coordination and tool availability
  - Verifies quality gates and success criteria alignment
  - Checks resource availability and capability requirements
- `--checkpoint`: Set up workflow checkpoints and review gates
  - Creates milestone reviews and validation points
  - Sets up automated quality and progress monitoring
  - Enables workflow course correction and adaptation
  - Provides stakeholder review and approval mechanisms

## Workflow Patterns

### Greenfield Full-Stack Development
```yaml
duration: "2-4 weeks"
complexity: "comprehensive"
waves: ["DISCUSS", "ARCHITECT", "DISTILL", "DEVELOP", "DEMO"]
best_for: ["new projects", "full-stack applications", "comprehensive planning needed"]
agents: ["business-analyst", "solution-architect", "acceptance-designer", "test-first-developer"]
```

### Brownfield Feature Enhancement
```yaml
duration: "1-2 weeks"
complexity: "moderate"
waves: ["DISCUSS (modified)", "ARCHITECT (integration)", "DISTILL", "DEVELOP", "DEMO"]
best_for: ["existing projects", "feature additions", "system extensions"]
agents: ["technical-stakeholder", "solution-architect", "story-context-manager", "test-first-developer"]
```

### Rapid Prototype Development
```yaml
duration: "2-5 days"
complexity: "simple"
waves: ["DISCUSS (brief)", "ARCHITECT (minimal)", "DEVELOP", "DEMO"]
best_for: ["proof of concept", "rapid validation", "MVP development"]
agents: ["business-analyst", "test-first-developer", "walking-skeleton-helper"]
```

### API Service Development
```yaml
duration: "1-3 weeks"
complexity: "moderate"
waves: ["DISCUSS", "ARCHITECT (service focus)", "DISTILL", "DEVELOP", "DEMO"]
best_for: ["backend services", "API development", "microservices"]
agents: ["business-analyst", "solution-architect", "acceptance-designer", "test-first-developer"]
```

## Interactive Workflow Selection

### Assessment Questions
```yaml
project_context:
  question: "What type of project are you working on?"
  options:
    1: "New project starting from scratch (Greenfield)"
    2: "Adding features to existing system (Brownfield)"
    3: "Creating proof of concept or prototype"
    4: "Integrating with existing systems"

technical_scope:
  question: "What is the primary technical focus?"
  options:
    1: "Full-stack web application"
    2: "Backend API or service"
    3: "Frontend UI components or application"
    4: "System integration or data processing"
    5: "Mobile application development"

complexity_assessment:
  question: "How would you describe the project complexity?"
  options:
    1: "Simple - straightforward implementation"
    2: "Moderate - some technical challenges"
    3: "Complex - significant architectural decisions needed"
    4: "Highly complex - enterprise-level with multiple integrations"
```

### Intelligent Matching
- **Fuzzy Matching**: ≥85% confidence threshold for direct recommendations
- **Context Analysis**: Project keywords, scope, and complexity assessment
- **Historical Patterns**: Success rate analysis for similar projects
- **Risk Assessment**: Complexity vs. timeline evaluation

## Wave Configuration

### Standard 5-Wave Process
1. **DISCUSS**: Requirements clarification and stakeholder collaboration
2. **ARCHITECT**: System design and technology decisions
3. **DISTILL**: Acceptance criteria and detailed story creation
4. **DEVELOP**: Outside-In TDD implementation
5. **DEMO**: Stakeholder validation and production preparation

### Wave Customization Options
- **Skip Waves**: Remove unnecessary waves for simple projects
- **Merge Waves**: Combine waves for streamlined workflows
- **Specialized Focus**: Add security, performance, or integration emphasis
- **Parallel Execution**: Enable parallel wave processing where appropriate

## Project Setup

### Configuration Files
```yaml
output_files:
  - "${DOCS_PATH}/workflow-selection.md": Selected workflow with reasoning
  - "${DOCS_PATH}/project-context.md": Project description and requirements
  - "${STATE_PATH}/workflow-config.json": Machine-readable configuration
  - "${STATE_PATH}/wave-progress.json": Wave progression tracking
```

### Context Initialization
- **Project Context**: Description, scope, and objectives
- **Stakeholder Context**: Key stakeholders and communication preferences
- **Technical Context**: Technology stack and architectural constraints
- **Quality Context**: Quality requirements and acceptance criteria

## Quality Gates

### Workflow Selection Validation
- **Appropriateness**: Selected workflow matches project characteristics
- **Feasibility**: Timeline and resource requirements are realistic
- **Completeness**: All necessary waves and agents identified
- **Stakeholder Alignment**: Workflow matches stakeholder expectations

### Project Setup Validation
- **Context Completeness**: All required context information captured
- **Configuration Accuracy**: Workflow configuration matches selection
- **Agent Readiness**: All required agents available and configured
- **Handoff Preparation**: Wave transition mechanisms established

## Examples

### New Feature Initialization
```bash
/cai:start "user authentication with OAuth2 and MFA" --interactive
```

### Brownfield Enhancement
```bash
/cai:start "add real-time notifications to existing app" --workflow brownfield
```

### Rapid Prototype
```bash
/cai:start "AI-powered recommendation engine POC" --workflow prototype --scope feature
```

### Complex System Development
```bash
/cai:start "multi-tenant SaaS platform" --workflow greenfield --guided --scope system
```

### API Development
```bash
/cai:start "payment processing microservice" --workflow api --assessment
```

## Comprehensive Usage Examples

### Quick Start Scenarios
```bash
# Simple feature development startup
/cai:start "user notification system"

# Interactive workflow selection with guidance
/cai:start "shopping cart checkout" --interactive

# Brownfield enhancement with assessment
/cai:start "add OAuth to existing auth" --workflow brownfield --assessment
```

### Methodology-Specific Workflows
```bash
# Full ATDD workflow with interactive configuration
/cai:start "real-time messaging" --methodology atdd --interactive --guided

# TDD-focused development with validation
/cai:start "payment validation service" --methodology tdd --validation --checkpoint

# BDD with stakeholder collaboration emphasis
/cai:start "user dashboard redesign" --methodology bdd --guided --interactive

# Lean development with waste elimination focus
/cai:start "API performance optimization" --methodology lean --assessment
```

### Scope-Specific Initialization
```bash
# Feature-level development with comprehensive setup
/cai:start "user authentication system" --scope feature --validation --checkpoint

# Epic-level coordination with dependency management
/cai:start "e-commerce platform modernization" --scope epic --interactive --assessment

# System-wide development orchestration
/cai:start "microservices migration" --scope system --methodology atdd --guided

# Component-focused development cycle
/cai:start "payment processing component" --scope component --validation
```

### Advanced Configuration Examples
```bash
# Comprehensive project startup with all validations
/cai:start "enterprise CRM system" --interactive --guided --assessment --validation --checkpoint

# Greenfield development with methodology selection
/cai:start "new mobile banking app" --workflow greenfield --methodology atdd --scope system --interactive

# Legacy modernization with detailed assessment
/cai:start "modernize monolithic application" --workflow brownfield --assessment --guided --checkpoint

# Rapid prototyping with lean methodology
/cai:start "AI-powered recommendation engine" --workflow rapid-prototype --methodology lean --interactive
```

### Team and Process Integration
```bash
# Multi-team coordination setup
/cai:start "distributed team collaboration platform" --scope epic --checkpoint --validation --guided

# Quality-focused development with comprehensive gates
/cai:start "financial transaction processing" --validation --checkpoint --assessment --methodology atdd

# Agile integration with continuous validation
/cai:start "customer feedback platform" --methodology bdd --interactive --checkpoint --validation
```

### Integration Workflow Examples
```bash
# Analysis-driven development startup
/cai:brownfield "legacy-system" --focus architecture --roadmap
/cai:start "modernize legacy architecture" --workflow brownfield --assessment --guided

# Architecture-first development workflow
/cai:start "event-driven microservices" --methodology atdd --guided
/cai:architect "event-driven system" --style microservices --interactive

# Requirements-driven BDD workflow
/cai:start "customer portal redesign" --methodology bdd --interactive
/cai:discuss "enhanced customer experience requirements" --focus ux --interactive
```

## Command Execution Pattern

### Activation Instructions
When this command is invoked:
1. Parse project description and workflow requirements
2. Invoke workflow-guidance-agent for intelligent workflow selection
3. Chain to atdd-wave-coordinator for workflow initialization
4. Configure ATDD workflow with appropriate settings
5. Return workflow startup confirmation and next steps

### Agent Invocation Workflow
```yaml
execution-flow:
  step1-guidance:
    agent: workflow-guidance-agent
    task: |
      Assess project and recommend optimal workflow:
      - Project Description: {parsed_project_description}
      - Workflow Type: {workflow_type_if_specified}
      - Scope: {scope_level_if_specified}

      Execute workflow assessment including:
      - Project complexity and type analysis
      - Recommend workflow: greenfield/brownfield/rapid-prototype
      - Provide numbered workflow options with rationale
      - Assess resource and timeline requirements

  step2-coordination:
    agent: atdd-wave-coordinator
    task: |
      Initialize selected ATDD workflow:
      - Review workflow recommendation from workflow-guidance-agent
      - Initialize selected workflow with 5-wave progression
      - Setup DISCUSS→ARCHITECT→DISTILL→DEVELOP→DEMO phases
      - Configure wave-specific agents and coordination patterns

  step3-setup:
    agent: pipeline-state-manager
    task: |
      Configure project pipeline state:
      - Create project state tracking and persistence
      - Setup cross-session continuity mechanisms
      - Initialize context preservation for wave transitions
      - Prepare for resumable workflow execution
```

### Arguments Processing
- Parse `[project-description]` argument for project scope
- Apply `--workflow`, `--scope`, `--methodology` flags to workflow selection
- Process `--interactive`, `--guided` flags for user interaction
- Enable `--assessment` mode for complexity evaluation

### Output Generation
Return workflow initialization confirmation including:
- Selected workflow type with rationale
- Initialized 5-wave ATDD progression setup
- Next steps and first wave preparation
- Project state tracking configuration