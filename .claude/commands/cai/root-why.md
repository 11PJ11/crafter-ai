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

### Core Arguments
- `problem-description` - Natural language description of the problem/symptom
- `@<file-path>` - Path to file containing error logs, symptoms, or problem context
- `!<command>` - Command that failed or exhibits the problem

### Analysis Configuration Flags
- `--evidence <path>` - Additional evidence files or directories
  - Specifies additional source files, log directories, or evidence repositories
  - Supports multiple paths for comprehensive evidence collection
  - Automatically indexes and categorizes evidence by type (logs, traces, metrics)
  - Validates evidence accessibility and formats for systematic analysis

- `--focus <domain>` - Focus area (system, performance, security, integration)
  - Directs analysis toward specific domain expertise and investigation patterns
  - System: Infrastructure, deployment, configuration, and service dependencies
  - Performance: Response times, resource utilization, bottlenecks, and scalability
  - Security: Authentication, authorization, vulnerabilities, and compliance
  - Integration: API connections, data flow, service communication, and compatibility

- `--depth <level>` - Analysis depth (standard, deep, comprehensive)
  - Standard: Core 5 Whys with primary cause investigation and evidence validation
  - Deep: Multi-causal branching with parallel investigation paths and cross-validation
  - Comprehensive: Exhaustive analysis including edge cases, system interactions, and preventive measures

- `--format <type>` - Output format (report, json, markdown)
  - Report: Executive summary with structured investigation findings and actionable recommendations
  - JSON: Machine-readable format for integration with monitoring and ticketing systems
  - Markdown: Documentation-ready format with detailed analysis and evidence references

- `--detail <level>` - Output detail level (executive, complete, compact)
  - Executive: Full detailed format with all intermediate WHYs and backwards validation (default)
  - Complete: Executive format plus appendices and extended validation matrices
  - Compact: Summary format optimized for quick review and action planning
  - Diagnostic: Technical format with detailed evidence chains for engineering teams

- `--validation-depth <level>` - Backwards validation thoroughness (basic, full, comprehensive)
  - Basic: Simple root cause → symptom validation with evidence references
  - Full: Complete backwards chain with evidence validation at each level (default)
  - Comprehensive: Cross-validation matrix with alternative hypothesis testing

- `--chain-visualization` - Include visual causal chain diagrams (default: true)
  - Generates ASCII-art visualization of cause-effect chains and parallel branches
  - Shows interconnections between multiple root causes and symptoms
  - Includes evidence quality indicators at each WHY level
  - Provides visual backwards validation from root causes to observable effects

## Auto-Activation Triggers
- **Keywords**: root cause, why, investigate, failure, problem, issue, bug
  - Automatic activation when systematic investigation keywords detected
  - Triggers enhanced multi-causal analysis for complex problem scenarios
  - Integrates with other CAI commands when root cause analysis needed
  - Provides fallback investigation when other analysis approaches insufficient

- **Context**: System failures, recurring issues, unexpected behaviors
  - Production outages requiring systematic investigation methodology
  - Intermittent issues that need comprehensive multi-factor analysis
  - Cross-platform compatibility problems requiring parallel cause investigation
  - Performance degradation requiring systematic bottleneck identification

- **File Patterns**: Error logs, stack traces, failure reports
  - Automatically processes .log, .trace, .dump, .crash files for evidence
  - Integrates with monitoring outputs and system diagnostics
  - Parses structured logs and extracts relevant failure indicators
  - Handles multiple evidence sources with automatic correlation

- **Command Failures**: When other commands report systematic issues
  - Triggered by /cai:validate failures requiring deeper investigation
  - Activated by /cai:develop when tests reveal architectural issues
  - Integrates with /cai:refactor when complexity issues need root cause analysis
  - Supports /cai:complete when production readiness issues need systematic resolution

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

## Usage Examples

### Basic Root Cause Analysis
```bash
# Simple problem investigation with automatic evidence collection
/root-why "Application crashes intermittently in production"
# Result: Complete 5 Whys analysis with systematic evidence validation

# Domain-focused analysis with specific output format
/root-why "Database connection failures" --focus system --format report
# Result: System-focused investigation with executive summary report

# Quick analysis with standard depth
/root-why "User login issues" --depth standard
# Result: Core 5 Whys investigation with primary cause identification
```

### File-Based Evidence Analysis
```bash
# Single file evidence analysis with comprehensive depth
/root-why @logs/error.log --focus system --depth comprehensive
# Result: Exhaustive analysis including edge cases and system interactions

# Multiple evidence sources with performance focus
/root-why @metrics/performance.json --evidence @logs/ @traces/ --focus performance
# Result: Performance-focused multi-causal analysis with comprehensive evidence

# Structured output for integration systems
/root-why @crash-reports/latest.dump --format json --depth deep
# Result: Machine-readable analysis for monitoring system integration
```

### Command Failure Investigation
```bash
# Failed command analysis with additional evidence
/root-why !"npm test" --evidence tests/ --format report
# Result: Test failure investigation with comprehensive solution strategy

# Build failure analysis with deep investigation
/root-why !"docker build ." --depth deep --focus integration
# Result: Multi-causal build failure analysis with integration focus

# Deployment command failure with comprehensive evidence
/root-why !"kubectl apply -f deployment.yaml" --evidence @k8s-logs/ --format markdown
# Result: Deployment failure analysis ready for documentation
```

### Advanced Multi-Source Investigation
```bash
# Comprehensive analysis with multiple evidence types
/root-why "Performance degradation in payment service" --evidence @metrics/ @logs/ @traces/ --focus performance --depth comprehensive
# Result: Exhaustive performance analysis with prevention recommendations

# Security incident investigation
/root-why "Unauthorized access attempts" --evidence @security-logs/ @audit-trails/ --focus security --format report
# Result: Security-focused investigation with compliance documentation

# Cross-platform compatibility issue
/root-why "Feature works on dev but fails in staging" --evidence @dev-logs/ @staging-logs/ --focus integration --depth deep
# Result: Platform-specific analysis with environment comparison
```

### Integration with Other CAI Commands
```bash
# Root cause analysis followed by targeted refactoring
/root-why "Code complexity causing maintenance issues" --focus system
# Then: /cai:refactor --level 4 --mikado --validate

# Problem analysis before validation improvements
/root-why "Quality gates failing intermittently" --evidence @ci-logs/
# Then: /cai:validate --full --security --threshold strict

# Investigation followed by systematic development
/root-why "Integration tests failing after refactoring" --focus integration
# Then: /cai:develop --outside-in --validate integration
```

### Workflow-Specific Analysis
```bash
# ATDD workflow investigation with comprehensive backwards validation
/root-why "Acceptance tests not reflecting business requirements" --focus integration --depth comprehensive --validation-depth full
# Result: Analysis of test-business alignment with complete causal chains and solution recommendations

# Architecture decision investigation with detailed intermediate WHYs
/root-why "Microservices communication causing timeouts" --evidence @distributed-traces/ --focus system --detail executive
# Result: System architecture analysis with full 5 WHYs documentation and scalability recommendations

# Quality assurance investigation with comprehensive reporting
/root-why "Code quality metrics declining over time" --evidence @quality-reports/ --focus system --format json --detail complete
# Result: Quality trend analysis with complete evidence chains and systematic improvement strategy
```

### Enhanced Reporting Examples
```bash
# Full detailed report with all intermediate WHYs and backwards validation
/root-why "Production outage lasting 2 hours" --detail executive --validation-depth full --chain-visualization
# Result: Complete Toyota 5 Whys report with visual causal chains and comprehensive backwards validation

# Compact format for quick executive review
/root-why "Database performance degradation" --detail compact --validation-depth basic
# Result: Executive summary with root cause chains and priority actions

# Technical diagnostic format for engineering teams
/root-why "Memory leaks in production service" --detail diagnostic --evidence @heap-dumps/ @metrics/ --validation-depth comprehensive
# Result: Technical report with detailed evidence chains and comprehensive validation matrices

# JSON format for integration with monitoring systems
/root-why "Intermittent API timeout failures" --format json --detail complete --validation-depth full
# Result: Machine-readable comprehensive analysis for automated processing and tracking
```

## Expected Output Structure

### Executive Format (Default: --detail executive)
```markdown
# Root Cause Analysis Report - Toyota 5 Whys Multi-Causal Investigation

## Problem Summary
**Primary Symptoms**:
- [Observable symptom 1 with specific evidence location]
- [Observable symptom 2 with specific evidence location]
- [Observable symptom 3 with specific evidence location]

**Evidence Sources**:
- [File 1: description of evidence type and relevance]
- [File 2: description of evidence type and relevance]
- [Command output: description of failure mode and context]

**Investigation Scope**: [System boundaries, timeframe, focus domain]
**Analysis Depth**: [Standard/Deep/Comprehensive]
**Validation Level**: [Basic/Full/Comprehensive]

---

## Multi-Causal 5 Whys Investigation

### WHY #1: Direct Symptom Investigation
**Question**: Why are we observing these symptoms?

**Identified Causes**:
- **Cause A**: [Direct cause description]
  - **Evidence**: [Specific evidence file:line or observation]
  - **Validation**: [How evidence was verified]
  - **Impact**: [Scope of this cause's contribution to symptoms]
  - **Confidence**: [High/Medium/Low based on evidence quality]

- **Cause B**: [Direct cause description]
  - **Evidence**: [Specific evidence file:line or observation]
  - **Validation**: [How evidence was verified]
  - **Impact**: [Scope of this cause's contribution to symptoms]
  - **Confidence**: [High/Medium/Low based on evidence quality]

- **Cause C**: [Direct cause description]
  - **Evidence**: [Specific evidence file:line or observation]
  - **Validation**: [How evidence was verified]
  - **Impact**: [Scope of this cause's contribution to symptoms]
  - **Confidence**: [High/Medium/Low based on evidence quality]

### WHY #2: Context Analysis
**Question**: Why do these immediate conditions exist?

**Cause Branch Analysis**:
- **Branch A** (from Cause A):
  - **Context Condition**: [Why Cause A exists in this environment]
  - **Evidence**: [Supporting evidence for contextual factors]
  - **System Factor**: [Environmental/systemic contribution]
  - **Timeline**: [When this condition developed or was introduced]
  - **Dependencies**: [What this condition depends on]

- **Branch B** (from Cause B):
  - **Context Condition**: [Why Cause B exists in this environment]
  - **Evidence**: [Supporting evidence for contextual factors]
  - **System Factor**: [Environmental/systemic contribution]
  - **Timeline**: [When this condition developed or was introduced]
  - **Dependencies**: [What this condition depends on]

- **Branch C** (from Cause C):
  - **Context Condition**: [Why Cause C exists in this environment]
  - **Evidence**: [Supporting evidence for contextual factors]
  - **System Factor**: [Environmental/systemic contribution]
  - **Timeline**: [When this condition developed or was introduced]
  - **Dependencies**: [What this condition depends on]

**Cross-Branch Validation**: [How multiple contexts interact, reinforce, or contradict]

### WHY #3: System Analysis
**Question**: Why do these systemic conditions persist?

**System-Level Analysis**:
- **Branch A System Analysis**:
  - **System Condition**: [How system architecture/design enables this failure mode]
  - **Evidence**: [System configuration, architecture documentation, or process evidence]
  - **Interconnections**: [How this connects to other system components or branches]
  - **Persistence Factor**: [Why system hasn't self-corrected or detected this issue]
  - **Scale Impact**: [How this affects system-wide behavior]

- **Branch B System Analysis**:
  - **System Condition**: [How system architecture/design enables this failure mode]
  - **Evidence**: [System configuration, architecture documentation, or process evidence]
  - **Interconnections**: [How this connects to other system components or branches]
  - **Persistence Factor**: [Why system hasn't self-corrected or detected this issue]
  - **Scale Impact**: [How this affects system-wide behavior]

- **Branch C System Analysis**:
  - **System Condition**: [How system architecture/design enables this failure mode]
  - **Evidence**: [System configuration, architecture documentation, or process evidence]
  - **Interconnections**: [How this connects to other system components or branches]
  - **Persistence Factor**: [Why system hasn't self-corrected or detected this issue]
  - **Scale Impact**: [How this affects system-wide behavior]

**System Integration Analysis**: [How multiple system factors combine to create failure conditions]

### WHY #4: Design Analysis
**Question**: Why weren't these systemic issues anticipated in the original design?

**Design Gap Analysis**:
- **Branch A Design Analysis**:
  - **Original Design Decision**: [What was decided and documented]
  - **Design Evidence**: [Architecture documents, code comments, decision records]
  - **Assumption Gap**: [What was assumed that proved incorrect]
  - **Knowledge Gap**: [What wasn't known at design time]
  - **Impact Scope**: [How this design gap enables the entire failure chain]

- **Branch B Design Analysis**:
  - **Original Design Decision**: [What was decided and documented]
  - **Design Evidence**: [Architecture documents, code comments, decision records]
  - **Assumption Gap**: [What was assumed that proved incorrect]
  - **Knowledge Gap**: [What wasn't known at design time]
  - **Impact Scope**: [How this design gap enables the entire failure chain]

- **Branch C Design Analysis**:
  - **Original Design Decision**: [What was decided and documented]
  - **Design Evidence**: [Architecture documents, code comments, decision records]
  - **Assumption Gap**: [What was assumed that proved incorrect]
  - **Knowledge Gap**: [What wasn't known at design time]
  - **Impact Scope**: [How this design gap enables the entire failure chain]

**Common Design Themes**: [Patterns across multiple design gaps]
**Architectural Blind Spots**: [Systematic gaps in design methodology]

### WHY #5: Root Cause Identification
**Question**: Why do these fundamental design/process conditions exist?

**Root Causes Identified**:
- **Root Cause 1** (from Branch A):
  - **Fundamental Condition**: [The deepest underlying issue that initiated this causal chain]
  - **Evidence Trail**: [Complete evidence path from WHY #5 → #4 → #3 → #2 → #1]
  - **Symptom Coverage**: [Which specific symptoms this root cause explains]
  - **Independent Validation**: [How this cause was verified independently]
  - **Organizational Factor**: [Process, culture, or resource issue at root]

- **Root Cause 2** (from Branch B):
  - **Fundamental Condition**: [The deepest underlying issue that initiated this causal chain]
  - **Evidence Trail**: [Complete evidence path from WHY #5 → #4 → #3 → #2 → #1]
  - **Symptom Coverage**: [Which specific symptoms this root cause explains]
  - **Independent Validation**: [How this cause was verified independently]
  - **Organizational Factor**: [Process, culture, or resource issue at root]

- **Root Cause 3** (from Branch C):
  - **Fundamental Condition**: [The deepest underlying issue that initiated this causal chain]
  - **Evidence Trail**: [Complete evidence path from WHY #5 → #4 → #3 → #2 → #1]
  - **Symptom Coverage**: [Which specific symptoms this root cause explains]
  - **Independent Validation**: [How this cause was verified independently]
  - **Organizational Factor**: [Process, culture, or resource issue at root]

**Multi-Causal Interaction Analysis**: [How root causes interact, amplify, or create systemic failure]

---

## Backwards Validation Chain

### Root Cause → Effect Validation
**Purpose**: Verify each root cause can independently explain observable symptoms through complete causal chain

#### Root Cause 1 → Symptom Chain Validation
```
[Root Cause 1: Fundamental organizational/process condition]
    ↓ [Design Impact: How root cause influenced design decisions]
[WHY #4: Design gap that wasn't anticipated]
    ↓ [System Impact: How design gap became systemic issue]
[WHY #3: System condition that persists]
    ↓ [Context Impact: How system condition creates operating context]
[WHY #2: Context condition enabling immediate causes]
    ↓ [Direct Impact: How context enables specific failures]
[WHY #1: Direct cause of symptoms]
    ↓ [Observable Impact: Manifestation in symptoms]
[Primary Symptoms: A, B, C with specific evidence]
```
**Evidence Supporting Each Link**:
- WHY #5→#4: [Evidence connecting root cause to design impact]
- WHY #4→#3: [Evidence connecting design gap to system condition]
- WHY #3→#2: [Evidence connecting system to context condition]
- WHY #2→#1: [Evidence connecting context to direct cause]
- WHY #1→Symptoms: [Evidence connecting direct cause to symptoms]

**Chain Validation Result**: ✅/❌ [Complete causal chain independently verified]
**Confidence Level**: [High/Medium/Low based on evidence quality]

#### Root Cause 2 → Symptom Chain Validation
```
[Root Cause 2: Fundamental organizational/process condition]
    ↓ [Design Impact: How root cause influenced design decisions]
[WHY #4: Design gap that wasn't anticipated]
    ↓ [System Impact: How design gap became systemic issue]
[WHY #3: System condition that persists]
    ↓ [Context Impact: How system condition creates operating context]
[WHY #2: Context condition enabling immediate causes]
    ↓ [Direct Impact: How context enables specific failures]
[WHY #1: Direct cause of symptoms]
    ↓ [Observable Impact: Manifestation in symptoms]
[Primary Symptoms: A, B, C with specific evidence]
```
**Evidence Supporting Each Link**:
- WHY #5→#4: [Evidence connecting root cause to design impact]
- WHY #4→#3: [Evidence connecting design gap to system condition]
- WHY #3→#2: [Evidence connecting system to context condition]
- WHY #2→#1: [Evidence connecting context to direct cause]
- WHY #1→Symptoms: [Evidence connecting direct cause to symptoms]

**Chain Validation Result**: ✅/❌ [Complete causal chain independently verified]
**Confidence Level**: [High/Medium/Low based on evidence quality]

#### Root Cause 3 → Symptom Chain Validation
```
[Root Cause 3: Fundamental organizational/process condition]
    ↓ [Design Impact: How root cause influenced design decisions]
[WHY #4: Design gap that wasn't anticipated]
    ↓ [System Impact: How design gap became systemic issue]
[WHY #3: System condition that persists]
    ↓ [Context Impact: How system condition creates operating context]
[WHY #2: Context condition enabling immediate causes]
    ↓ [Direct Impact: How context enables specific failures]
[WHY #1: Direct cause of symptoms]
    ↓ [Observable Impact: Manifestation in symptoms]
[Primary Symptoms: A, B, C with specific evidence]
```
**Evidence Supporting Each Link**:
- WHY #5→#4: [Evidence connecting root cause to design impact]
- WHY #4→#3: [Evidence connecting design gap to system condition]
- WHY #3→#2: [Evidence connecting system to context condition]
- WHY #2→#1: [Evidence connecting context to direct cause]
- WHY #1→Symptoms: [Evidence connecting direct cause to symptoms]

**Chain Validation Result**: ✅/❌ [Complete causal chain independently verified]
**Confidence Level**: [High/Medium/Low based on evidence quality]

### Cross-Validation Matrix
**Purpose**: Verify that all identified root causes collectively explain all observable symptoms

| Root Cause | Symptom 1 | Symptom 2 | Symptom 3 | Evidence Quality | Chain Integrity |
|------------|-----------|-----------|-----------|------------------|-----------------|
| Root Cause 1 | ✅/❌ Direct | ✅/❌ Indirect | ✅/❌ N/A | High/Med/Low | ✅ Complete |
| Root Cause 2 | ✅/❌ Indirect | ✅/❌ Direct | ✅/❌ Direct | High/Med/Low | ✅ Complete |
| Root Cause 3 | ✅/❌ Contributing | ✅/❌ N/A | ✅/❌ Direct | High/Med/Low | ✅ Complete |

**Coverage Analysis**:
- **Symptom 1**: Explained by [Root Causes X, Y] with [evidence quality]
- **Symptom 2**: Explained by [Root Causes X, Z] with [evidence quality]
- **Symptom 3**: Explained by [Root Causes Y, Z] with [evidence quality]

**Overall Completeness**: ✅/❌ [All symptoms fully explained by identified root causes]
**Gap Analysis**: [Any symptoms not fully explained by current root cause set]

---

## Comprehensive Solution Strategy

### Root Cause Remediation Plan
**Principle**: Address ALL identified root causes systematically to prevent recurrence

#### Solution for Root Cause 1
- **Primary Action**: [Specific action to address fundamental organizational/process condition]
  - **Implementation Plan**: [Detailed steps for implementation]
  - **Timeline**: [Realistic completion timeline with milestones]
  - **Success Criteria**: [Measurable indicators of successful resolution]
  - **Validation Evidence**: [What evidence will demonstrate success]
  - **Risk Mitigation**: [Potential implementation risks and mitigations]
  - **Resource Requirements**: [People, tools, budget needed]

#### Solution for Root Cause 2
- **Primary Action**: [Specific action to address fundamental organizational/process condition]
  - **Implementation Plan**: [Detailed steps for implementation]
  - **Timeline**: [Realistic completion timeline with milestones]
  - **Success Criteria**: [Measurable indicators of successful resolution]
  - **Validation Evidence**: [What evidence will demonstrate success]
  - **Risk Mitigation**: [Potential implementation risks and mitigations]
  - **Resource Requirements**: [People, tools, budget needed]

#### Solution for Root Cause 3
- **Primary Action**: [Specific action to address fundamental organizational/process condition]
  - **Implementation Plan**: [Detailed steps for implementation]
  - **Timeline**: [Realistic completion timeline with milestones]
  - **Success Criteria**: [Measurable indicators of successful resolution]
  - **Validation Evidence**: [What evidence will demonstrate success]
  - **Risk Mitigation**: [Potential implementation risks and mitigations]
  - **Resource Requirements**: [People, tools, budget needed]

### Implementation Sequence and Dependencies
1. **Phase 1 - Immediate Actions**: [Actions that can be implemented immediately without dependencies]
2. **Phase 2 - Systematic Changes**: [Actions requiring Phase 1 completion or parallel coordination]
3. **Phase 3 - Long-term Improvements**: [Foundational changes requiring sustained effort]

**Critical Dependencies**: [Dependencies between solutions that affect implementation sequence]
**Resource Conflicts**: [Potential resource competition between solutions]
**Integration Points**: [Where solutions must work together]

---

## Toyota Kaizen Prevention Plan

### Process Improvements (Prevent Root Cause Recurrence)
- **Process Enhancement 1**: [Systematic change to prevent Root Cause 1 recurrence]
  - **Current Process**: [How the process works now]
  - **Root Cause Connection**: [How current process enables root cause]
  - **Improved Process**: [How the process should work to prevent root cause]
  - **Quality Gates**: [Built-in checks to prevent regression]
  - **Measurement**: [How to measure process effectiveness]
  - **Training Required**: [Skills/knowledge needed for new process]

- **Process Enhancement 2**: [Systematic change to prevent Root Cause 2 recurrence]
  - **Current Process**: [How the process works now]
  - **Root Cause Connection**: [How current process enables root cause]
  - **Improved Process**: [How the process should work to prevent root cause]
  - **Quality Gates**: [Built-in checks to prevent regression]
  - **Measurement**: [How to measure process effectiveness]
  - **Training Required**: [Skills/knowledge needed for new process]

### System Improvements (Prevent Systemic Conditions)
- **Design Enhancement**: [Architectural/system changes to prevent design gaps]
- **Monitoring Addition**: [New monitoring to detect early warning signs]
- **Automation Implementation**: [Automation to reduce human error opportunities]
- **Feedback Loops**: [Systematic feedback to catch issues earlier]

### Cultural/Organizational Improvements (Address Fundamental Conditions)
- **Training Program**: [Systematic training to address knowledge gaps]
- **Communication Protocol**: [Improved information sharing to prevent isolation]
- **Review Process**: [Regular evaluation of solution effectiveness]
- **Learning Culture**: [Systematic learning from failures and near-misses]

---

## Evidence Validation Summary

### Evidence Quality Assessment
- **High-Quality Evidence**: [Count and description of strongest evidence]
- **Medium-Quality Evidence**: [Count and description of supporting evidence]
- **Low-Quality Evidence**: [Count and description with acknowledged limitations]
- **Evidence Gaps**: [What additional evidence would strengthen the analysis]
- **Alternative Explanations**: [Other possible explanations considered and ruled out]

### Validation Results Checklist
- ✅/❌ **All 5 WHY levels supported by independently verifiable evidence**
- ✅/❌ **Multiple root causes validated through separate evidence chains**
- ✅/❌ **Complete evidence chains from root causes to observable symptoms**
- ✅/❌ **Cross-validation confirms no contradictions between root causes**
- ✅/❌ **Backwards validation successful for all identified root causes**
- ✅/❌ **Solution completeness verified against comprehensive root cause set**
- ✅/❌ **Toyota 5 Whys methodology compliance confirmed throughout**
- ✅/❌ **Multi-causal investigation completed with parallel branch analysis**

### Investigation Confidence Assessment
- **Overall Confidence Level**: [High/Medium/Low with specific percentage if quantifiable]
- **Primary Confidence Drivers**: [What evidence and validation results support confidence]
- **Uncertainty Areas**: [Specific areas where additional investigation might strengthen conclusions]
- **Confidence Limitations**: [Known limitations in evidence or methodology]
- **Recommended Follow-up**: [Additional analysis or validation if confidence could be improved]

### Toyota Methodology Compliance Verification
- ✅ **Systematic 5 Whys Process**: Each WHY level properly addresses the previous level
- ✅ **Evidence-Based Investigation**: Every conclusion supported by verifiable evidence
- ✅ **Multi-Causal Recognition**: Parallel investigation of all contributing factors
- ✅ **Root Cause Focus**: Investigation continued to fundamental organizational conditions
- ✅ **Preventive Orientation**: Solution focuses on preventing recurrence through Kaizen
- ✅ **Backwards Validation**: Root cause → symptom chains independently verified
- ✅ **Completeness Check**: "Are we missing any contributing factors?" systematically applied

---

## Appendices

### Appendix A: Complete Evidence Inventory
[Detailed catalog of all evidence sources with file paths, timestamps, relevance scores, and quality assessments]

### Appendix B: Investigation Timeline
[Chronological development of the problem, investigation process, and evidence discovery]

### Appendix C: Methodology Notes
[Specific Toyota 5 Whys techniques applied, adaptations made for this context, and rationale]

### Appendix D: Alternative Hypotheses Considered
[Other possible explanations that were investigated and ruled out with evidence]

### Appendix E: Related Issues and Dependencies
[Connected problems or systemic issues that weren't directly addressed but may need follow-up]
```

### Compact Format (--detail compact)
```markdown
# RCA Report: [Problem Title]

## Executive Summary
**Problem**: [Brief problem description]
**Root Causes**: [#] identified | **Evidence Quality**: [High/Med/Low] | **Confidence**: [High/Med/Low]

### Multi-Causal Chain Summary
1. **RC1**: [Root cause] → **Chain**: [RC→Design→System→Context→Direct→Symptoms] → **Evidence**: [Key evidence]
2. **RC2**: [Root cause] → **Chain**: [RC→Design→System→Context→Direct→Symptoms] → **Evidence**: [Key evidence]
3. **RC3**: [Root cause] → **Chain**: [RC→Design→System→Context→Direct→Symptoms] → **Evidence**: [Key evidence]

### Solutions Required (Priority Order)
1. [Action 1 for RC1] - [Timeline] - [Success Criteria]
2. [Action 2 for RC2] - [Timeline] - [Success Criteria]
3. [Action 3 for RC3] - [Timeline] - [Success Criteria]

### Prevention Measures
- [Prevention measure 1 targeting process/system improvement]
- [Prevention measure 2 targeting organizational/cultural improvement]

**Validation Status**: ✅ Backwards chains verified | ✅ Evidence complete | ✅ Toyota compliance | ✅ Multi-causal coverage
```

### JSON Format (--format json)
```json
{
  "investigation": {
    "problem_summary": {
      "symptoms": ["symptom1", "symptom2", "symptom3"],
      "evidence_sources": ["file1", "file2", "command1"],
      "scope": "system_boundaries"
    },
    "five_whys": {
      "why_1": {
        "question": "Why are symptoms occurring?",
        "causes": [
          {"cause": "A", "evidence": "evidence_A", "confidence": "high"},
          {"cause": "B", "evidence": "evidence_B", "confidence": "medium"}
        ]
      },
      "why_2": {
        "question": "Why do immediate causes exist?",
        "branches": [
          {"from_cause": "A", "context": "context_A", "evidence": "evidence_A2"},
          {"from_cause": "B", "context": "context_B", "evidence": "evidence_B2"}
        ]
      },
      "why_3": { "question": "...", "system_analysis": [...] },
      "why_4": { "question": "...", "design_analysis": [...] },
      "why_5": {
        "question": "Why do fundamental conditions exist?",
        "root_causes": [
          {
            "id": "RC1",
            "condition": "fundamental_condition_1",
            "evidence_trail": ["why5_evidence", "why4_evidence", "why3_evidence", "why2_evidence", "why1_evidence"],
            "symptom_coverage": ["symptom1", "symptom3"],
            "confidence": "high"
          }
        ]
      }
    },
    "backwards_validation": {
      "root_cause_1": {
        "chain": ["RC1", "Design_Gap", "System_Condition", "Context_Condition", "Direct_Cause", "Symptoms"],
        "evidence_links": ["evidence1", "evidence2", "evidence3", "evidence4", "evidence5"],
        "validation_result": true,
        "confidence": "high"
      }
    },
    "validation_summary": {
      "all_whys_evidenced": true,
      "multiple_causes_validated": true,
      "backwards_chains_verified": true,
      "toyota_compliance": true,
      "overall_confidence": "high"
    }
  }
}
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

## Command Execution Pattern

### Activation Instructions
When this command is invoked:
1. Parse problem description and evidence sources
2. Invoke root-cause-analyzer agent for systematic Toyota 5 Whys analysis
3. Apply enhanced multi-causal investigation methodology
4. Execute comprehensive root cause analysis with evidence validation
5. Return structured analysis with multiple root causes and comprehensive solutions

### Agent Invocation Workflow
```yaml
execution-flow:
  step1-analysis:
    agent: root-cause-analyzer
    task: |
      Execute Toyota 5 Whys multi-causal root cause analysis:
      - Problem: {parsed_problem_description}
      - Evidence: {collected_evidence_sources}
      - Focus: {focus_domain_if_specified}

      Apply enhanced multi-causal investigation including:
      - Investigate ALL observable symptoms at each WHY level
      - Follow parallel cause branches through all 5 levels
      - Provide verifiable evidence for each cause relationship
      - Identify multiple root causes when applicable
      - Create comprehensive solution addressing ALL root causes

  step2-evidence-validation:
    agent: root-cause-analyzer
    task: |
      Validate evidence and causal relationships:
      - Cross-validate evidence supporting each WHY level
      - Ensure multiple root causes don't contradict each other
      - Apply backwards chain validation from root cause to symptoms
      - Verify completeness with "Are we missing contributing factors?" check

  step3-solution-generation:
    agent: root-cause-analyzer
    task: |
      Generate comprehensive solution strategy:
      - Address ALL identified root causes systematically
      - Apply Toyota Kaizen principles for prevention
      - Create implementation roadmap with priorities
      - Document prevention recommendations
```

### Arguments Processing
- Parse `[problem-description]` or evidence files for analysis scope
- Apply `@<file-path>`, `!<command>` arguments for evidence collection
- Process `--focus`, `--depth`, `--format` flags for analysis customization
- Enable systematic multi-causal investigation methodology

### Output Generation
Return systematic root cause analysis including:
- Complete multi-causal 5 Whys investigation with evidence
- Multiple root causes identified and validated
- Comprehensive solution strategy addressing all causes
- Prevention recommendations using Toyota Kaizen methodology