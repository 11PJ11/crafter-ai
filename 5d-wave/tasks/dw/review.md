---
description: 'Expert critique and quality review [agent] [artifact-type] [path] - Types: roadmap, task, implementation'
argument-hint: '[agent] [artifact-type] [artifact-path] - Example: @software-crafter task "steps/01-01.json"'
agent-activation:
  required: false
  agent-parameter: true
  agent-command: "*workflow-review"
---

# DW-REVIEW: Expert Critique and Quality Assurance

**Type**: Quality Review Tool
**Agent**: Specified as parameter
**Command**: `/dw:review [agent] [artifact-type] [artifact-path]`

## Overview

Invokes an expert agent to critique and review workflow artifacts at any stage. Provides comprehensive feedback on roadmaps, atomic task files, or implementations to ensure quality and prevent issues before they propagate.

Supports three review modes:
- **roadmap**: Review comprehensive planning document
- **task**: Review atomic task file before execution
- **implementation**: Review completed work against task specification

## Usage Examples

```bash
# Review a roadmap before splitting into tasks
/dw:review @solution-architect roadmap "docs/workflow/auth-upgrade/roadmap.yaml"

# Review a task file before sub-agent execution
/dw:review @software-crafter task "docs/workflow/auth-upgrade/steps/02-01.json"

# Review implementation against requirements
/dw:review @devop implementation "docs/workflow/auth-upgrade/steps/01-01.json"

# Security review of authentication roadmap
/dw:review @security-expert roadmap "docs/workflow/auth-upgrade/roadmap.yaml"
```

## Context Files Required

- **For roadmap review**: The roadmap.yaml file
- **For task review**: The specific task JSON file
- **For implementation review**: Task file + implementation outputs

## CRITICAL: Agent Invocation Protocol

**YOU ARE THE COORDINATOR** - Do NOT perform the review yourself. Your role is to dispatch to the appropriate expert agent.

### STEP 1: Extract Agent Parameter

Parse the first argument to extract the agent name:
- User provides: `/dw:review @software-crafter task "steps/01-01.json"`
- Extract agent name: `software-crafter` (remove @ prefix)
- Validate agent name is one of: researcher, software-crafter, solution-architect, product-owner, acceptance-designer, devop

### STEP 2: Extract Artifact Type

Extract the second argument (artifact type):
- Valid types: `roadmap`, `task`, `implementation`
- Example: `task`

### STEP 3: Extract Artifact Path

Extract the third argument (artifact path):
- Example: `"docs/workflow/auth-upgrade/steps/01-01.json"`
- Ensure path is absolute or resolve relative to working directory

### STEP 4: Invoke Agent Using Task Tool

**MANDATORY**: Use the Task tool to invoke the specified expert agent. Do NOT attempt to perform the review yourself.

Invoke the Task tool with this exact pattern:

```
Task: "You are the {agent-name} agent acting as an expert reviewer.

Perform a comprehensive {artifact-type} review of: {artifact-path}

Review Types:
- roadmap: Review comprehensive planning document for completeness, sequencing, and feasibility
- task: Review atomic task file before execution for clarity, context, and achievability
- implementation: Review completed work against task specification and acceptance criteria

Your responsibilities:
1. Read and understand the artifact thoroughly
2. Apply domain expertise to identify issues and risks
3. Provide structured feedback with severity levels (HIGH/MEDIUM/LOW)
4. Make specific, actionable recommendations
5. Update the original artifact file with review metadata
6. Assign overall approval status: APPROVED, NEEDS_REVISION, or REJECTED

Review Guidelines:
- Be specific and actionable in critiques
- Include positive feedback where appropriate
- Focus on preventing downstream issues
- Consider domain-specific best practices
- For HIGH severity issues, mark ready_for_execution: false

Output Format:
Update the artifact file by appending or updating the reviews section with your structured feedback."
```

**Parameter Substitution**:
- Replace `{agent-name}` with the extracted agent name (e.g., "software-crafter")
- Replace `{artifact-type}` with the artifact type (e.g., "task")
- Replace `{artifact-path}` with the absolute path to the artifact file

### Example Invocations

**For software-crafter reviewing task**:
```
Task: "You are the software-crafter agent acting as an expert reviewer.

Perform a comprehensive task review of: /mnt/c/Repositories/Projects/ai-craft/docs/workflow/auth-upgrade/steps/02-01.json

[... rest of instructions ...]"
```

**For solution-architect reviewing roadmap**:
```
Task: "You are the solution-architect agent acting as an expert reviewer.

Perform a comprehensive roadmap review of: /mnt/c/Repositories/Projects/ai-craft/docs/workflow/auth-upgrade/roadmap.yaml

[... rest of instructions ...]"
```

### Error Handling

**Invalid Agent Name**:
- If agent name is not in the valid list, respond with error:
  "Invalid agent name: {name}. Must be one of: researcher, software-crafter, solution-architect, product-owner, acceptance-designer, devop"

**Invalid Artifact Type**:
- If artifact type is not roadmap, task, or implementation, respond with error:
  "Invalid artifact type: {type}. Must be one of: roadmap, task, implementation"

**Missing Artifact File**:
- If artifact file path is not provided or file doesn't exist, respond with error:
  "Artifact file not found: {path}. Please provide valid path to artifact file."

---

## Agent Invocation (Reference Documentation)

The following section documents what the invoked agent will do. **You (the coordinator) do not execute this - the expert agent does.**

### Primary Task Instructions

**Task**: Provide expert critique and recommendations

**Review Modes**:

#### 1. ROADMAP REVIEW

**Focus Areas**:
- Completeness of phases and steps
- Logical sequencing and dependencies
- Feasibility of time estimates
- Self-containment of each step
- Missing steps or overlooked complexities
- Risk identification
- Parallel execution opportunities

**Output**: Updated roadmap with review comments

```yaml
# Added to roadmap.yaml
reviews:
  - reviewer: "{agent-name}"
    date: "2024-01-15T10:00:00Z"
    overall_assessment: "APPROVED|NEEDS_REVISION|REJECTED"
    risk_level: "LOW|MEDIUM|HIGH"
    estimated_accuracy: "Conservative|Realistic|Optimistic"
    critiques:
      - phase: 1
        step: 2
        issue: "Missing error handling consideration"
        severity: "HIGH"
        recommendation: "Add rollback strategy step"
      - phase: 2
        step: 1
        issue: "Time estimate too optimistic"
        severity: "MEDIUM"
        recommendation: "Increase from 4 to 8 hours"
    missing_steps:
      - "Security audit before deployment"
      - "Performance benchmarking phase"
    dependencies_issues:
      - "Step 2.3 should depend on 1.4"
      - "Steps 3.1 and 3.2 can run in parallel"
```

#### 2. TASK REVIEW

**Focus Areas**:
- Clarity of instructions
- Completeness of context
- Achievability of acceptance criteria
- Resource availability
- Hidden dependencies
- Potential blockers

**Output**: Updated task file with review

```json
{
  "task_id": "02-01",
  "reviews": [{
    "reviewer": "{agent-name}",
    "date": "2024-01-15T10:00:00Z",
    "ready_for_execution": false,
    "critiques": [
      {
        "aspect": "instructions",
        "issue": "Step 3 assumes knowledge of internal API",
        "severity": "HIGH",
        "recommendation": "Add API documentation link and examples"
      },
      {
        "aspect": "acceptance_criteria",
        "issue": "Performance criteria not specified",
        "severity": "MEDIUM",
        "recommendation": "Add 'Response time < 200ms' criterion"
      }
    ],
    "missing_context": [
      "Database schema for user tables",
      "Current authentication flow diagram"
    ],
    "risk_assessment": {
      "technical_risk": "MEDIUM",
      "timeline_risk": "LOW",
      "dependency_risk": "HIGH"
    }
  }]
}
```

#### 3. IMPLEMENTATION REVIEW

**Focus Areas**:
- Acceptance criteria fulfillment
- Code quality and best practices
- Performance considerations
- Security implications
- Test coverage
- Documentation completeness

**Output**: Review report and updated task state

```json
{
  "task_id": "01-01",
  "implementation_review": {
    "reviewer": "{agent-name}",
    "date": "2024-01-15T14:00:00Z",
    "acceptance_status": "PASSED|FAILED|PARTIAL",
    "criteria_results": [
      {
        "criterion": "Comparison matrix includes 5 providers",
        "status": "PASSED",
        "evidence": "Matrix in provider-selection.md has 6 providers"
      },
      {
        "criterion": "Cost projections for 3 years",
        "status": "FAILED",
        "evidence": "Only 2 years projected",
        "required_action": "Add year 3 projections"
      }
    ],
    "quality_assessment": {
      "completeness": 8,
      "clarity": 9,
      "technical_accuracy": 7,
      "follows_best_practices": true
    },
    "issues_found": [
      {
        "type": "incomplete",
        "description": "Missing disaster recovery consideration",
        "severity": "MEDIUM",
        "recommendation": "Add DR capabilities to comparison"
      }
    ],
    "commendations": [
      "Excellent cost breakdown with clear assumptions",
      "Thorough security feature comparison"
    ]
  },
  "state": {
    "status": "IN_REVIEW",
    "needs_rework": true,
    "review_passed": false
  }
}
```

### Review Guidelines

**For All Reviews**:
1. Be specific and actionable in critiques
2. Provide severity levels (HIGH/MEDIUM/LOW)
3. Include positive feedback where appropriate
4. Focus on preventing downstream issues
5. Consider domain-specific best practices

**Severity Definitions**:
- **HIGH**: Blocks progress or creates significant risk
- **MEDIUM**: Should be addressed but not blocking
- **LOW**: Nice to have improvement

**Review Outcomes**:
- **APPROVED**: Ready to proceed
- **NEEDS_REVISION**: Must address HIGH severity issues
- **REJECTED**: Fundamental flaws requiring restart

### Expert Agent Selection

Choose reviewer based on domain expertise:

- `@solution-architect`: Architecture and design reviews
- `@software-crafter`: Code quality and implementation
- `@security-expert`: Security implications
- `@data-engineer`: Data pipeline and architecture
- `@devop`: Deployment and operations readiness
- `@product-owner`: Business alignment and requirements
- `@troubleshooter`: Risk and failure mode analysis

### Processing Flow

1. **Load Artifact**: Read the specified file
2. **Contextual Analysis**: Understand project goals and constraints
3. **Expert Review**: Apply domain expertise to identify issues
4. **Generate Critique**: Create structured feedback
5. **UPDATE ORIGINAL FILE**: Append review section to the artifact
6. **Create Report**: Generate summary for stakeholders

**IMPORTANT**: The review command ALWAYS updates the original artifact file (roadmap.yaml or step JSON) by appending the review data. This ensures critiques travel with the artifact and are available to all subsequent agents.

## Success Criteria

**Validation Checklist**:
- [ ] Review covers all required focus areas
- [ ] Critiques are specific and actionable
- [ ] Severity levels assigned appropriately
- [ ] Recommendations provided for all issues
- [ ] Original file updated with review metadata
- [ ] Clear approval/revision decision made

## Output Artifacts

- Updated artifact file with embedded review
- Optional: `docs/workflow/{project-id}/reviews/{timestamp}-{artifact-type}-review.md`

## Notes

### Review Philosophy

Reviews are not about perfection but about:
1. **Risk Mitigation**: Catching issues early
2. **Knowledge Sharing**: Spreading expertise
3. **Quality Improvement**: Elevating standards
4. **Context Preservation**: Ensuring self-containment

### Integration with Workflow

```
Roadmap → REVIEW → Split → Tasks
           ↓
    Fix Issues First

Task → REVIEW → Sub-Agent Execution
        ↓
   Clarify First

Implementation → REVIEW → State Update
                   ↓
              Rework if Needed
```

### Preventing Context Degradation

Reviews ensure each artifact is truly self-contained by identifying:
- Missing context that would confuse sub-agents
- Implicit assumptions that should be explicit
- Forward references that break atomicity
- Hidden dependencies not documented

This review system acts as quality gates throughout the workflow, ensuring consistent high quality even as tasks are distributed across multiple agents and sessions.