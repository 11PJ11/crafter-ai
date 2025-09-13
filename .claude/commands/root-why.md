# /root-why - Toyota 5 Whys Root Cause Analysis Command

## Purpose
Execute systematic multi-causal root cause analysis using the Toyota 5 Whys methodology through the root-cause-analyzer agent.

## Command Structure
```yaml
---
command: "/root-why"
category: "Analysis & Investigation"
purpose: "Toyota 5 Whys multi-causal root cause analysis"
wave-enabled: false
performance-profile: "complex"
---
```

## Usage
```
/root-why [problem-description] [--flags]
/root-why @<file-path> [--flags]
/root-why !<command-to-investigate> [--flags]
```

## Arguments
- `problem-description` - Natural language description of the problem/symptom
- `@<file-path>` - Path to file containing error logs, symptoms, or problem context
- `!<command>` - Command that failed or exhibits the problem
- `--evidence <path>` - Additional evidence files or directories
- `--focus <domain>` - Focus area (system, performance, security, integration)
- `--depth <level>` - Analysis depth (standard, deep, comprehensive)
- `--format <type>` - Output format (report, json, markdown)

## Auto-Activation Triggers
- **Keywords**: root cause, why, investigate, failure, problem, issue, bug
- **Context**: System failures, recurring issues, unexpected behaviors
- **File Patterns**: Error logs, stack traces, failure reports
- **Command Failures**: When other commands report systematic issues

## Execution Workflow

### 1. Problem Context Gathering
- Parse problem description and context
- Collect evidence from files, logs, or command outputs
- Identify observable symptoms and conditions
- Establish baseline evidence for investigation

### 2. Agent Delegation
```yaml
agent: "root-cause-analyzer"
prompt: |
  Execute Toyota 5 Whys multi-causal root cause analysis for:
  
  PROBLEM: {problem-description}
  EVIDENCE: {collected-evidence}
  CONTEXT: {file-paths-and-logs}
  
  Apply the enhanced multi-causal investigation methodology:
  - Investigate ALL observable symptoms at each WHY level
  - Follow parallel cause branches through all 5 levels
  - Provide verifiable evidence for each cause
  - Identify multiple root causes when applicable
  - Create comprehensive solution addressing ALL root causes
  
  Output structured analysis with:
  1. Problem Summary with observable symptoms
  2. Multi-causal 5 Whys investigation
  3. Evidence validation for each level
  4. Multiple root causes identified
  5. Comprehensive solution strategy
  6. Prevention recommendations
```

### 3. Analysis Processing
- **Toyota Methodology**: Systematic 5 Whys with multi-causal branching
- **Evidence Validation**: Each WHY level supported by verifiable evidence
- **Parallel Investigation**: Follow ALL cause branches simultaneously
- **Cross-Validation**: Ensure multiple causes don't contradict
- **Completeness Check**: "Are we missing any contributing factors?"

### 4. Result Formatting
- **Executive Summary**: Key findings and root causes
- **Detailed Analysis**: Complete 5 Whys investigation tree
- **Evidence References**: All supporting evidence with validation
- **Solution Strategy**: Comprehensive approach addressing all root causes
- **Prevention Plan**: Kaizen-style improvements to prevent recurrence

## Integration Points

### Persona System
- **Primary**: Analyzer persona (mandatory activation)
- **Secondary**: Domain-specific personas based on problem context
- **Agent**: root-cause-analyzer agent for systematic methodology

### MCP Servers  
- **Sequential**: Primary server for structured investigation
- **Context7**: Evidence validation and pattern recognition
- **Fallback**: Native analysis if MCP servers unavailable

### Tool Orchestration
- **Task**: Delegates to root-cause-analyzer agent
- **Read**: Evidence collection from files and logs
- **Grep**: Pattern analysis in logs and error messages
- **Glob**: Systematic file discovery for evidence
- **TodoWrite**: Progress tracking for complex investigations

## Quality Gates

### Pre-Execution Validation
- ✅ Problem description provided or discoverable
- ✅ Evidence sources accessible and readable
- ✅ root-cause-analyzer agent available
- ✅ Sufficient context for meaningful analysis

### Execution Validation
- ✅ All 5 WHY levels investigated with evidence
- ✅ Multiple causes identified where applicable
- ✅ Evidence supports each causal relationship
- ✅ Root causes explain ALL observable symptoms
- ✅ Solution addresses ALL identified root causes

### Output Validation
- ✅ Complete causal chain from symptoms to root causes
- ✅ Evidence validation for each investigative level
- ✅ Cross-validation between multiple root causes
- ✅ Actionable recommendations with prevention strategy
- ✅ Toyota methodology compliance verified

## Example Usage

### Basic Problem Analysis
```bash
/root-why "Application crashes intermittently in production"
```

### File-Based Investigation
```bash
/root-why @logs/error.log --focus system --depth comprehensive
```

### Command Failure Analysis
```bash
/root-why !"npm test" --evidence tests/ --format report
```

### Multi-Source Evidence
```bash
/root-why "Performance degradation" --evidence @metrics/ @logs/ --focus performance
```

## Expected Output Structure

```markdown
# Root Cause Analysis Report

## Problem Summary
- **Observable Symptoms**: [List all identified symptoms]
- **Evidence Sources**: [Files, logs, commands analyzed]
- **Investigation Scope**: [System boundaries and focus areas]

## Multi-Causal 5 Whys Investigation

### WHY #1: [Direct symptom investigation]
**Causes Identified:**
- A) [Evidence: specific observation]
- B) [Evidence: specific observation]  
- C) [Evidence: specific observation]

### WHY #2: [Context analysis for each cause]
**Cause Branch Analysis:**
- A→ [Evidence: context analysis]
- B→ [Evidence: context analysis]
- C→ [Evidence: context analysis]

[Continue through WHY #3, #4, #5...]

## Root Causes Identified
1. **Root Cause 1**: [Fundamental condition]
2. **Root Cause 2**: [Fundamental condition]
3. **Root Cause 3**: [Fundamental condition]

## Comprehensive Solution Strategy
1. [Address Root Cause 1]
2. [Address Root Cause 2]  
3. [Address Root Cause 3]

## Prevention Recommendations
- [Kaizen improvement 1]
- [Kaizen improvement 2]
- [Process enhancement]

## Evidence Validation
✅ All WHY levels supported by verifiable evidence
✅ Multiple root causes validated independently
✅ Solution completeness verified
```

## Performance Profile

### Resource Requirements
- **Memory**: Medium (analysis trees and evidence storage)
- **CPU**: High (multi-causal investigation processing)
- **Time**: 2-10 minutes depending on complexity and evidence volume
- **Token Usage**: 5-15K tokens for comprehensive analysis

### Optimization Strategies
- **Evidence Caching**: Store analyzed evidence for session reuse
- **Pattern Recognition**: Leverage previous similar investigations
- **Parallel Processing**: Investigate multiple cause branches simultaneously
- **Compression**: Use --uc mode for large evidence sets

## Error Handling

### Common Issues
- **Insufficient Evidence**: Request additional evidence sources
- **Agent Unavailable**: Fallback to native analyzer persona analysis
- **Complex Problems**: Suggest breaking into smaller investigative scopes
- **Evidence Conflicts**: Flag contradictions and request clarification

### Recovery Strategies
- **Evidence Gap**: Guide user to collect missing evidence
- **Analysis Failure**: Provide structured investigation template
- **Complexity Overflow**: Recommend wave mode for enterprise-scale issues
- **Time Constraints**: Offer abbreviated analysis with key findings

## Integration Testing

### Validation Checklist
- ✅ Command parsing and argument handling
- ✅ Agent delegation and communication
- ✅ Evidence collection and validation
- ✅ Toyota methodology compliance
- ✅ Multi-causal investigation accuracy
- ✅ Output formatting and structure
- ✅ Error handling and recovery
- ✅ Performance within acceptable bounds

### Test Scenarios
1. **Simple Problem**: Single cause, clear evidence
2. **Multi-Causal Problem**: Multiple root causes, complex evidence
3. **Evidence-Poor Scenario**: Limited information, requires guidance
4. **Large-Scale Investigation**: Enterprise complexity, multiple systems
5. **Command Failure Analysis**: Technical debugging scenario
6. **Performance Investigation**: System bottleneck analysis
7. **Security Incident**: Vulnerability or breach investigation