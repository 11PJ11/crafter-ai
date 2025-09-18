# /cai:atdd - Complete ATDD Workflow Orchestration

```yaml
---
command: "/cai:atdd"
category: "ATDD Orchestration"
purpose: "Complete ATDD workflow orchestration and management"
argument-hint: "[description] --analyze-existing --from-stage architect"
wave-enabled: true
performance-profile: "complex"
---
```

## Overview

Complete ATDD workflow orchestration and management system that intelligently analyzes existing project context and determines optimal entry point for the 5-stage ATDD cycle (Discuss → Architect → Distill → Develop → Demo).

## Auto-Persona Activation
- **ATDD Command Processor**: Workflow analysis and initiation (mandatory)
- **ATDD Cycle Coordinator**: 5-stage cycle management (mandatory)
- **Business Analyst**: Requirements analysis (conditional)
- **Architect**: System design coordination (conditional)
- **QA**: Test strategy and validation (conditional)

## MCP Server Integration
- **Primary**: Sequential (systematic ATDD workflow analysis and coordination)
- **Secondary**: Context7 (ATDD methodology patterns and best practices)
- **Tertiary**: Magic (UI component specifications for distill phase)

## Tool Orchestration
- **Task**: Specialized ATDD agents activation and workflow coordination
- **Read**: Project context analysis and existing implementation assessment
- **Grep**: Codebase analysis for ATDD workflow planning
- **Write**: Workflow documentation and progress tracking
- **TodoWrite**: ATDD stage management and progress tracking

## Agent Flow
```yaml
atdd-command-processor:
  workflow_analysis:
    - Analyzes existing project context from documentation, tests, and source code
    - Determines current project state and optimal workflow entry point
    - Sets up appropriate workflow configuration and agent coordination
    - Provides intelligent workflow starting point recommendations

  context_assessment:
    - Evaluates existing codebase for ATDD readiness and current practices
    - Identifies gaps in requirements, tests, or implementation
    - Assesses technical debt and quality factors affecting ATDD workflow
    - Generates baseline understanding for informed workflow decisions

atdd-cycle-coordinator:
  stage_management:
    - Manages the five-stage ATDD cycle coordination and transitions
    - Coordinates agent handoffs between DISCUSS → ARCHITECT → DISTILL → DEVELOP → DEMO phases
    - Ensures proper workflow state management and progress tracking
    - Provides seamless phase transitions with context preservation
```

## Command Execution Pattern

### Activation Instructions
When this command is invoked:
1. Parse ATDD workflow context and requirements
2. Invoke atdd-command-processor agent for project analysis
3. Chain to atdd-cycle-coordinator for stage management
4. Execute intelligent ATDD workflow initiation
5. Return workflow status with next steps and coordination plan

### Agent Invocation Workflow
```yaml
execution-flow:
  step1-analysis:
    agent: atdd-command-processor
    task: |
      Analyze project context and workflow requirements:
      - Feature Description: {parsed_feature_description}
      - Starting Stage: {from_stage_if_specified}
      - Analysis Mode: {analyze_existing_flag_status}

      Execute workflow preparation including:
      - Comprehensive project context analysis from documentation, tests, and source code
      - Optimal workflow entry point determination based on current project state
      - Workflow configuration and preparation for 5-stage ATDD cycle
      - Intelligent routing recommendations for workflow optimization

  step2-coordination:
    agent: atdd-cycle-coordinator
    task: |
      Coordinate ATDD workflow execution:
      - Review analysis results from command processor
      - Initialize 5-stage ATDD cycle management
      - Coordinate agent handoffs between workflow phases
      - Establish workflow state management and progress tracking

  step3-initiation:
    agent: appropriate-stage-agent
    task: |
      Begin ATDD workflow at determined entry point:
      - Execute stage-specific initialization based on analysis
      - Coordinate with other workflow stages as needed
      - Maintain workflow context and state management
      - Provide progress updates and next step recommendations
```

### Arguments Processing
- Parse `[feature-description]` argument for workflow context
- Apply `--analyze-existing`, `--from-stage` flags to workflow planning
- Process `--resume`, `--status` flags for workflow management
- Enable intelligent ATDD workflow coordination

### Output Generation
Return ATDD workflow initiation including:
- Intelligent project context analysis and workflow recommendations
- 5-stage ATDD cycle coordination and management
- Workflow state management with progress tracking
- Next steps and agent coordination plan

## 📖 Complete Documentation

For comprehensive usage examples, workflow management, intelligent routing, and detailed configuration options:

```bash
/cai:man atdd                        # Full manual with all examples
/cai:man atdd --examples             # Usage examples only
/cai:man atdd --flags               # All flags and options
```

The manual includes:
- **Workflow Control**: `--analyze-existing`, `--from-stage`, `--resume`, `--status`, `--help`
- **Project Analysis**: Intelligent context assessment and optimal entry point determination
- **5-Stage ATDD Cycle**: DISCUSS → ARCHITECT → DISTILL → DEVELOP → DEMO coordination
- **Comprehensive Examples**: Basic workflow initiation, project context analysis, stage management
- **Integration Patterns**: Claude Code command integration, agent delegation, workflow resumption
- **Intelligent Routing**: Project analysis with workflow optimization and stage recommendations