# /cai:brown-analyze - Brownfield Project Analyzer

```yaml
---
command: "/cai:brown-analyze"
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
/cai:brown-analyze [scope]
```

### Advanced Usage
```bash
/cai:brown-analyze [scope] --legacy --interactive --focus <domain>
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
- `--interactive`: Enable numbered option selection
- `--report`: Generate comprehensive analysis report
- `--metrics`: Include quantitative metrics
- `--roadmap`: Generate modernization roadmap

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
/cai:brown-analyze --legacy "monolithic-ecommerce-app" --interactive
```

### Focused Module Analysis
```bash
/cai:brown-analyze "payment-module" --focus security --metrics
```

### Comprehensive System Assessment
```bash
/cai:brown-analyze --full --report --roadmap
```

### Performance-Focused Analysis
```bash
/cai:brown-analyze @src/services/ --focus performance --interactive
```

### Wave-Enabled Analysis
```bash
/cai:brown-analyze --full --wave-mode auto --comprehensive
```

ARGUMENTS: create the commands under the @.claude\commands\cai\ folder so we can install them together with the rest