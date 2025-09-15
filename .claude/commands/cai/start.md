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
- `--guided`: Step-by-step workflow configuration
- `--assessment`: Detailed project assessment before workflow selection

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

ARGUMENTS: create the commands under the @.claude\commands\cai\ folder so we can install them together with the rest