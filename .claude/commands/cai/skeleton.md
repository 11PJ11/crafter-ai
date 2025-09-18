# /cai:skeleton - Walking Skeleton Implementation for Architecture Validation

```yaml
---
command: "/cai:skeleton"
category: "Architecture Validation"
purpose: "Walking Skeleton implementation for architecture validation"
wave-enabled: false
performance-profile: "standard"
---
```

## Overview

Walking Skeleton implementation for architecture validation based on Alistair Cockburn's methodology. Creates minimal end-to-end implementations to validate architecture and reduce risk early in projects through systematic risk reduction and architectural validation.

## Auto-Persona Activation
- **Walking Skeleton Helper**: Methodology implementation (mandatory)
- **Architect**: Architecture validation and design guidance (mandatory)
- **QA**: End-to-end validation and testing (conditional)
- **Technical Stakeholder**: Technical constraints and feasibility (conditional)

## MCP Server Integration
- **Primary**: Sequential (systematic walking skeleton planning and validation)
- **Secondary**: Context7 (walking skeleton patterns and best practices)
- **Tertiary**: Magic (minimal UI skeleton generation)

## Tool Orchestration
- **Task**: Walking skeleton helper agent for methodology implementation
- **Write**: Minimal skeleton implementation creation
- **Read**: Architecture analysis and validation
- **Edit**: Skeleton refinement and validation updates
- **Bash**: End-to-end skeleton testing and validation

## Agent Flow
```yaml
walking-skeleton-helper:
  minimal_implementation:
    - Guides teams through creating minimal end-to-end implementations
    - Validates architecture and reduces risk early in projects
    - Implements smallest possible functionality for architecture validation
    - Focuses on architectural risk reduction through working implementation

  validation_framework:
    - Validates architectural decisions through working implementation
    - Enables iterative skeleton development with stakeholder feedback
    - Identifies and mitigates highest architectural risks
    - Provides progressive enhancement and validation cycles
```

## Command Execution Pattern

### Activation Instructions
When this command is invoked:
1. Parse system description and walking skeleton requirements
2. Invoke walking-skeleton-helper agent for methodology implementation
3. Execute minimal end-to-end implementation creation
4. Return validated walking skeleton with architecture validation

### Agent Invocation Workflow
```yaml
execution-flow:
  step1-skeleton:
    agent: walking-skeleton-helper
    task: |
      Implement Walking Skeleton methodology:
      - System Description: {parsed_system_description}
      - Minimal Mode: {minimal_flag_status}
      - Risk Reduction Focus: {risk_reduction_flag_status}

      Execute skeleton creation including:
      - Minimal end-to-end implementation for architecture validation
      - Systematic risk reduction through implementation
      - Architecture validation and feedback collection
      - Progressive enhancement with stakeholder validation
```

### Arguments Processing
- Parse `[system-description]` argument for skeleton context
- Apply `--minimal`, `--risk-reduction` flags to implementation scope
- Process `--validation`, `--iterative` flags for development approach

### Output Generation
Return walking skeleton including:
- Minimal viable end-to-end implementation for architecture validation
- Risk reduction validation through working implementation
- Architecture validation feedback and recommendations
- Progressive enhancement roadmap with stakeholder validation

## 📖 Complete Documentation

For comprehensive methodology details, implementation patterns, risk reduction strategies, and usage examples:

```bash
/cai:man skeleton                    # Full manual with methodology details
/cai:man skeleton --examples         # Implementation examples only
/cai:man skeleton --flags           # All flags and options
```

The manual includes:
- **Walking Skeleton Methodology**: Alistair Cockburn's approach to architecture validation
- **Implementation Patterns**: `--minimal`, `--risk-reduction`, `--validation`, `--iterative`
- **Risk Reduction**: Systematic architecture risk mitigation through implementation
- **Comprehensive Examples**: Minimal implementations, architecture validation, progressive enhancement