# /cai:help - Interactive Guidance and Agent Transformation

```yaml
---
command: "/cai:help"
category: "Meta & Orchestration"
purpose: "Interactive guidance and agent transformation"
wave-enabled: false
performance-profile: "standard"
---
```

## Overview

Interactive guidance system providing help, agent transformation capabilities, and workflow navigation support for the AI-Craft ATDD framework. Offers comprehensive command catalog, workflow guidance, and agent-specific transformations.

## Auto-Persona Activation
- **Workflow Guidance Agent**: Interactive workflow selection and navigation (mandatory)
- **Mentor**: Educational guidance and knowledge transfer (conditional)
- **Scribe**: Documentation and help content generation (conditional)

## MCP Server Integration
- **Primary**: Sequential (structured help analysis and guidance delivery)
- **Secondary**: Context7 (help patterns and documentation standards)
- **Tertiary**: Magic (interactive UI help elements)

## Tool Orchestration
- **Task**: Workflow guidance agent activation for interactive help
- **Read**: Help documentation and command reference access
- **Write**: Help content generation and guidance documentation
- **Edit**: Help content updates and improvements

## Agent Flow
```yaml
workflow-guidance-agent:
  interactive_guidance:
    - Provides interactive elicitation and refinement capabilities
    - Offers numbered option selection for workflow navigation
    - Delivers comprehensive command catalog with usage examples
    - Enables agent transformation with specialized guidance

  command_reference:
    - Maintains comprehensive CAI command catalog and documentation
    - Provides context-sensitive help and troubleshooting guidance
    - Offers workflow pattern recommendations and best practices
    - Includes integration guidance with other AI-Craft components
```

## Command Execution Pattern

### Activation Instructions
When this command is invoked:
1. Parse help context and agent transformation requirements
2. Invoke workflow-guidance-agent for interactive help delivery
3. Execute agent transformation if specific agent requested
4. Return comprehensive help with interactive guidance options

### Agent Invocation Workflow
```yaml
execution-flow:
  step1-guidance:
    agent: workflow-guidance-agent
    task: |
      Provide comprehensive help and guidance:
      - Agent Name: {agent_name_if_specified}
      - Interactive Mode: {interactive_flag_status}
      - Help Focus: {help_focus_area}

      Execute help delivery including:
      - Interactive guidance with numbered option selection
      - Comprehensive command catalog and examples
      - Workflow navigation support and recommendations
      - Agent transformation capabilities if requested
```

### Arguments Processing
- Parse `[agent-name]` argument for transformation target
- Apply `--interactive`, `--workflow-guidance` flags to help delivery
- Process `--command-reference`, `--troubleshooting` flags for content focus

### Output Generation
Return interactive help including:
- Comprehensive command catalog with usage examples
- Interactive workflow guidance with numbered options
- Agent transformation capabilities with specialized guidance
- Troubleshooting support and problem-solving assistance

## 📖 Complete Documentation

For comprehensive command reference, workflow patterns, agent capabilities, and interactive guidance:

```bash
/cai:man help                        # Full manual with command catalog
/cai:man help --examples             # Usage examples only
/cai:man help --flags               # All flags and options
```

The manual includes:
- **Interactive Features**: `--interactive`, `--workflow-guidance`, `--command-reference`, `--troubleshooting`
- **Agent Transformation**: Specialized agent activation with context-specific guidance
- **Command Catalog**: Complete CAI command reference with examples and patterns
- **Workflow Navigation**: Interactive guidance for AI-Craft ATDD framework