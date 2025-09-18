# /cai:root-why - Toyota 5 Whys Multi-Causal Root Cause Analysis

```yaml
---
command: "/cai:root-why"
category: "Analysis & Investigation"
purpose: "Toyota 5 Whys multi-causal root cause analysis"
wave-enabled: false
performance-profile: "complex"
---
```

## Overview

Toyota 5 Whys multi-causal root cause analysis system that applies systematic investigation methodology to identify underlying causes of problems, failures, or unexpected behaviors through structured evidence-based analysis.

## Auto-Persona Activation
- **Root Cause Analyzer**: Systematic Toyota methodology implementation (mandatory)
- **Analyzer**: Evidence-based investigation support (mandatory)
- **QA**: Quality-related root cause analysis (conditional)
- **Security**: Security incident root cause analysis (conditional)
- **Performance**: Performance issue root cause analysis (conditional)

## MCP Server Integration
- **Primary**: Sequential (systematic 5 Whys analysis and multi-causal investigation)
- **Secondary**: Context7 (evidence validation and investigation patterns)
- **Tertiary**: Playwright (system behavior validation and evidence collection)

## Tool Orchestration
- **Task**: Root cause analyzer agent activation for systematic investigation
- **Read**: System analysis and evidence collection
- **Grep**: Pattern detection and evidence gathering
- **Bash**: System validation and evidence verification
- **TodoWrite**: Investigation progress tracking and findings documentation

## Agent Flow
```yaml
root-cause-analyzer:
  systematic_investigation:
    - Applies Toyota 5 Whys methodology with multi-causal investigation
    - Conducts evidence-based analysis with verifiable data collection
    - Implements structured investigation processes for complex problems
    - Provides comprehensive root cause identification and solution recommendations

  evidence_validation:
    - Requires verifiable evidence for each level of analysis
    - Validates root causes explain all symptoms collectively
    - Ensures solutions address all identified root causes
    - Implements backwards validation from root cause to symptoms
```

## Command Execution Pattern

### Activation Instructions
When this command is invoked:
1. Parse problem description and investigation context
2. Invoke root-cause-analyzer agent for systematic Toyota 5 Whys methodology
3. Execute evidence-based multi-causal investigation
4. Return comprehensive root cause analysis with solutions

### Agent Invocation Workflow
```yaml
execution-flow:
  step1-investigation:
    agent: root-cause-analyzer
    task: |
      Execute systematic Toyota 5 Whys root cause analysis:
      - Problem Description: {parsed_problem_description}
      - Evidence Collection: {evidence_flag_status}
      - Multi-Causal Mode: {multi_causal_flag_status}

      Apply Toyota methodology including:
      - Systematic 5 Whys technique for root cause analysis
      - Multi-causal investigation with evidence requirements
      - Structured evidence-based analysis and validation
      - Comprehensive solution recommendations addressing all root causes
```

### Arguments Processing
- Parse `[problem-description]` argument for investigation context
- Apply `--systematic`, `--evidence`, `--multi-causal` flags to investigation depth
- Enable Toyota 5 Whys methodology with evidence requirements

### Output Generation
Return systematic root cause analysis including:
- Multi-causal investigation with evidence-based findings
- Toyota 5 Whys methodology application with all levels documented
- Comprehensive solution recommendations addressing all identified root causes
- Backwards validation ensuring causal chain completeness

## 📖 Complete Documentation

For comprehensive methodology details, investigation frameworks, evidence requirements, and usage examples:

```bash
/cai:man root-why                    # Full manual with methodology details
/cai:man root-why --examples         # Investigation examples only
/cai:man root-why --flags           # All flags and options
```

The manual includes:
- **Toyota 5 Whys Methodology**: Systematic investigation technique with evidence requirements
- **Multi-Causal Investigation**: Multiple root cause identification and validation
- **Evidence Requirements**: Verification standards and backwards validation
- **Comprehensive Examples**: System failures, performance issues, complex problems
- **Investigation Framework**: Structured analysis with evidence-based validation