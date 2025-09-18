# /cai:brownfield - Brownfield Project Analysis and Technical Debt Assessment

```yaml
---
command: "/cai:brownfield"
category: "Legacy Analysis"
purpose: "Brownfield project analysis and technical debt assessment"
wave-enabled: false
performance-profile: "complex"
---
```

## Overview

Brownfield project analysis and technical debt assessment system for existing codebases. Provides comprehensive analysis of legacy systems, identifies technical debt, and creates modernization roadmaps with systematic improvement strategies.

## Auto-Persona Activation
- **Technical Debt Tracker**: Debt analysis and prioritization (mandatory)
- **Architect**: Legacy system architecture analysis (mandatory)
- **Analyzer**: Systematic codebase investigation (mandatory)
- **Security**: Legacy security assessment (conditional)
- **Performance**: Legacy performance analysis (conditional)

## MCP Server Integration
- **Primary**: Sequential (systematic legacy analysis and improvement planning)
- **Secondary**: Context7 (modernization patterns and best practices)
- **Tertiary**: Playwright (legacy system testing and validation)

## Tool Orchestration
- **Task**: Technical debt tracker and specialized analysis agents
- **Read**: Legacy codebase analysis and documentation assessment
- **Grep**: Pattern detection and technical debt identification
- **Bash**: Legacy system validation and testing
- **Write**: Assessment reports and modernization roadmaps

## Agent Flow
```yaml
technical-debt-tracker:
  debt_assessment:
    - Identifies, prioritizes, and tracks technical debt items systematically
    - Provides impact assessment and improvement recommendations
    - Manages debt accumulation and resolution tracking
    - Creates prioritized modernization roadmaps

  modernization_planning:
    - Analyzes legacy systems for modernization opportunities
    - Identifies architectural patterns and refactoring strategies
    - Provides systematic improvement strategies with risk assessment
    - Creates implementation roadmaps with prioritized improvements
```

## Command Execution Pattern

### Activation Instructions
When this command is invoked:
1. Parse target system and analysis focus
2. Invoke technical-debt-tracker agent for comprehensive legacy analysis
3. Execute systematic brownfield assessment with modernization planning
4. Return comprehensive analysis with improvement roadmap

### Agent Invocation Workflow
```yaml
execution-flow:
  step1-assessment:
    agent: technical-debt-tracker
    task: |
      Execute comprehensive brownfield analysis:
      - Target System: {parsed_target_system}
      - Focus Area: {focus_domain_if_specified}
      - Assessment Mode: {assessment_flag_status}

      Conduct legacy analysis including:
      - Technical debt identification and prioritization
      - Legacy system architecture analysis
      - Modernization opportunity assessment
      - Systematic improvement roadmap creation
```

### Arguments Processing
- Parse `[target]` argument for system scope
- Apply `--focus`, `--roadmap`, `--assessment` flags to analysis depth
- Process `--prioritize` flag for improvement ranking

### Output Generation
Return brownfield analysis including:
- Comprehensive technical debt assessment with impact analysis
- Legacy system architecture evaluation and modernization opportunities
- Prioritized improvement roadmap with systematic implementation strategies
- Risk assessment and mitigation recommendations

## 📖 Complete Documentation

For comprehensive analysis frameworks, modernization strategies, technical debt assessment, and detailed examples:

```bash
/cai:man brownfield                  # Full manual with analysis frameworks
/cai:man brownfield --examples       # Analysis examples only
/cai:man brownfield --flags         # All flags and options
```

The manual includes:
- **Analysis Focus**: `--focus debt|architecture|security|performance|maintainability`
- **Assessment Control**: `--roadmap`, `--assessment`, `--prioritize`
- **Comprehensive Examples**: Legacy system analysis, technical debt assessment, modernization planning
- **Brownfield Framework**: Systematic assessment with improvement prioritization