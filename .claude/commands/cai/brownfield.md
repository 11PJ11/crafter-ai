# /cai:brownfield - Brownfield Project Analyzer

```yaml
---
command: "/cai:brownfield"
category: "Analysis & Investigation"
purpose: "Brownfield project analysis and technical debt assessment"
wave-enabled: true
performance-profile: "complex"
---
```

## Overview

Comprehensive brownfield project analyzer for understanding existing codebase structure, technical debt assessment, and modernization planning.

## Auto-Persona Activation
- **Analyzer**: Root cause analysis and investigation (mandatory)
- **Architect**: System architecture evaluation
- **Security**: Security vulnerability assessment (conditional)
- **Performance**: Performance bottleneck identification (conditional)

## MCP Server Integration
- **Primary**: Sequential (systematic analysis and structured investigation)
- **Secondary**: Context7 (analysis patterns and best practices)
- **Tertiary**: All servers for comprehensive analysis when needed

## Tool Orchestration
- **Read**: Codebase analysis and documentation review
- **Grep**: Pattern detection and code search
- **Glob**: File discovery and structure analysis
- **Bash**: Metrics collection and tool execution
- **TodoWrite**: Analysis progress tracking
- **Task**: Sub-analysis delegation for large codebases

## Agent Flow
```yaml
technical-debt-tracker:
  - Identifies technical debt hotspots
  - Assesses code quality metrics
  - Maps dependency structure
  - Generates debt priority matrix

technical-stakeholder:
  - Evaluates technical constraints
  - Documents integration points
  - Assesses modification risk
  - Provides feasibility assessment

solution-architect:
  - Analyzes architectural patterns
  - Recommends modernization strategy
  - Creates transformation roadmap
  - Documents architectural decisions
```

## Arguments

### Basic Usage
```bash
/cai:brownfield [scope]
```

### Advanced Usage
```bash
/cai:brownfield [scope] --legacy --interactive --focus <domain>
```

### Scope Arguments
- `--legacy`: Focus on legacy system analysis
- `--full`: Complete project scope processing
- `--module <name>`: Focus on specific module
- `--component <name>`: Focus on specific component

### Analysis Focus
- `--focus architecture`: Architectural pattern analysis
- `--focus security`: Security vulnerability assessment
- `--focus performance`: Performance bottleneck identification
- `--focus quality`: Code quality and maintainability
- `--focus debt`: Technical debt prioritization

### Path Arguments
- `@<path>`: Analysis target path
- `@src/`: Source code analysis
- `@tests/`: Test coverage analysis
- `@docs/`: Documentation analysis

### Output Control
- `--interactive`: Enable numbered option selection and guided workflows
  - Provides step-by-step guidance with user choices
  - Shows prioritized recommendations with rationale
  - Allows iterative refinement of analysis scope
- `--report`: Generate comprehensive analysis report
  - Creates detailed technical debt assessment document
  - Includes executive summary and technical details
  - Formats for stakeholder consumption and technical teams
- `--metrics`: Include quantitative metrics and measurements
  - Provides code complexity scores and maintainability indices
  - Shows test coverage percentages and dependency counts
  - Includes performance benchmarks where applicable
- `--roadmap`: Generate modernization roadmap with timelines
  - Creates step-by-step transformation plan
  - Includes effort estimates and resource requirements
  - Provides risk assessment and mitigation strategies

### Wave Control
- `--wave-mode <strategy>`: Control wave orchestration approach
  - `auto`: Automatic wave activation based on complexity (default)
  - `force`: Force wave mode for comprehensive analysis
  - `off`: Disable wave mode for faster execution
- `--wave-strategy <type>`: Select wave orchestration strategy
  - `progressive`: Iterative enhancement approach
  - `systematic`: Methodical comprehensive analysis
  - `adaptive`: Dynamic configuration based on findings

### Quality Control
- `--validate`: Enable comprehensive validation during analysis
  - Validates findings against industry standards
  - Cross-references recommendations with best practices
  - Ensures analysis completeness and accuracy
- `--safe-mode`: Conservative analysis with maximum validation
  - Applies cautious interpretation of findings
  - Includes additional verification steps
  - Provides risk-averse recommendations

## Analysis Dimensions

### Technical Debt Assessment
- **Code Quality**: Complexity, duplication, maintainability
- **Architecture Debt**: Pattern violations, coupling issues
- **Test Debt**: Coverage gaps, test quality
- **Documentation Debt**: Missing or outdated documentation

### Dependency Analysis
- **External Dependencies**: Third-party library analysis
- **Internal Dependencies**: Module coupling assessment
- **Version Analysis**: Outdated dependency identification
- **Security Analysis**: Vulnerability assessment

### Performance Analysis
- **Bottleneck Identification**: Performance hotspot detection
- **Resource Usage**: Memory and CPU analysis
- **Scalability Assessment**: Growth limitation identification
- **Optimization Opportunities**: Performance improvement recommendations

### Security Analysis
- **Vulnerability Assessment**: Security weakness identification
- **Compliance Analysis**: Regulatory requirement evaluation
- **Access Control**: Authentication and authorization review
- **Data Protection**: Sensitive data handling assessment

## Wave System Integration

**Wave Eligibility**: Large codebase analysis (>50 files) or complex system assessment
**Wave Triggers**: complexity ≥0.7 + multiple analysis dimensions + comprehensive scope

### Wave Orchestration
1. **Discovery Wave**: Codebase structure and inventory
2. **Assessment Wave**: Quality, security, and performance analysis
3. **Prioritization Wave**: Technical debt and improvement prioritization
4. **Planning Wave**: Modernization strategy and roadmap creation
5. **Validation Wave**: Analysis verification and stakeholder review

## Output Artifacts

### Analysis Reports
- **Technical Debt Report**: Prioritized improvement recommendations
- **Architecture Assessment**: Current state and target architecture
- **Security Assessment**: Vulnerability analysis and remediation plan
- **Performance Report**: Bottleneck analysis and optimization roadmap

### Modernization Planning
- **Transformation Roadmap**: Step-by-step modernization plan
- **Risk Assessment**: Change impact and mitigation strategies
- **Resource Planning**: Effort estimation and team requirements
- **Technology Recommendations**: Stack modernization suggestions

## Quality Gates

### Analysis Completeness
- **Coverage**: All critical system components analyzed
- **Depth**: Sufficient detail for decision-making
- **Evidence**: Quantitative metrics and qualitative assessments
- **Actionability**: Clear next steps and recommendations

### Report Quality
- **Clarity**: Easy to understand for technical and business stakeholders
- **Prioritization**: Clear importance and urgency rankings
- **Feasibility**: Realistic implementation recommendations
- **Traceability**: Evidence linking to specific code locations

## Examples

### Legacy System Analysis
```bash
/cai:brownfield --legacy "monolithic-ecommerce-app" --interactive
```

### Focused Module Analysis
```bash
/cai:brownfield "payment-module" --focus security --metrics
```

### Comprehensive System Assessment
```bash
/cai:brownfield --full --report --roadmap
```

### Performance-Focused Analysis
```bash
/cai:brownfield @src/services/ --focus performance --interactive
```

### Wave-Enabled Analysis
```bash
/cai:brownfield --full --wave-mode auto --comprehensive
```

## Comprehensive Usage Examples

### Quick Analysis Scenarios
```bash
# Basic brownfield assessment
/cai:brownfield

# Focus on specific module with interactive guidance
/cai:brownfield "user-authentication" --interactive

# Legacy system with comprehensive metrics
/cai:brownfield --legacy --metrics --report
```

### Domain-Focused Analysis
```bash
# Security-focused analysis with validation
/cai:brownfield --focus security --validate --safe-mode

# Performance analysis with roadmap generation
/cai:brownfield @src/api/ --focus performance --roadmap --metrics

# Architecture debt assessment with wave processing
/cai:brownfield --focus architecture --wave-mode force --wave-strategy systematic

# Technical debt prioritization for specific component
/cai:brownfield "payment-processing" --focus debt --interactive --roadmap
```

### Comprehensive Analysis Workflows
```bash
# Full system analysis with all outputs
/cai:brownfield --full --report --metrics --roadmap --interactive --validate

# Legacy modernization planning
/cai:brownfield --legacy --focus architecture --roadmap --wave-mode auto --interactive

# Quality assessment with conservative approach
/cai:brownfield --focus quality --safe-mode --validate --metrics --report
```

### Path-Specific Analysis
```bash
# Source code focused analysis
/cai:brownfield @src/ --focus quality --metrics --interactive

# Multi-path analysis with comprehensive output
/cai:brownfield @src/ @tests/ @docs/ --report --roadmap --validate

# Component-specific deep dive
/cai:brownfield @src/services/payment/ --focus security --wave-mode force
```

### Integration and Workflow Examples
```bash
# Analysis before refactoring planning
/cai:brownfield "core-module" --focus debt --roadmap --validate
# Follow with: /cai:refactor "core-module" --level 4 --validate

# Security audit preparation
/cai:brownfield --focus security --report --metrics --safe-mode --validate
# Follow with: /cai:validate --security --comprehensive

# Modernization planning workflow
/cai:brownfield --legacy --roadmap --interactive --wave-strategy progressive
# Follow with: /cai:architect "modernized-system" --style microservices
```

## Command Execution Pattern

### Activation Instructions
When this command is invoked:
1. Parse arguments and validate scope
2. Invoke technical-debt-tracker agent for initial analysis
3. Chain to technical-stakeholder agent for constraints assessment
4. Complete with solution-architect agent for modernization planning
5. Return comprehensive brownfield analysis report

### Agent Invocation Workflow
```yaml
execution-flow:
  step1-analysis:
    agent: technical-debt-tracker
    task: |
      Analyze brownfield codebase for technical debt assessment:
      - Scope: {parsed_scope_argument}
      - Focus: {focus_domain_if_specified}
      - Legacy Mode: {legacy_flag_status}

      Execute comprehensive technical debt analysis including:
      - Code quality metrics and complexity assessment
      - Dependency structure mapping and vulnerability analysis
      - Architecture pattern evaluation and debt priority matrix
      - Performance bottleneck identification and resource usage analysis

  step2-constraints:
    agent: technical-stakeholder
    task: |
      Evaluate technical constraints and integration requirements:
      - Review analysis from technical-debt-tracker
      - Document critical integration points and dependencies
      - Assess modification risk levels for identified components
      - Provide feasibility assessment for potential changes

  step3-planning:
    agent: solution-architect
    task: |
      Create modernization strategy and transformation roadmap:
      - Synthesize technical debt analysis and constraint evaluation
      - Recommend architectural improvements and modernization approach
      - Generate step-by-step transformation roadmap with priorities
      - Document architectural decisions and trade-off rationale
```

### Arguments Processing
- Parse `[scope]` argument for analysis target
- Apply `--legacy`, `--full`, `--focus` flags to agent tasks
- Process `@<path>` arguments for specific directory targeting
- Enable `--interactive` mode for numbered option selection

### Output Generation
Return structured brownfield analysis including:
- Executive summary with key findings
- Technical debt priority matrix
- Modernization roadmap with timelines
- Risk assessment and mitigation strategies