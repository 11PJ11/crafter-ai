# DW-REVIEW: Expert Critique and Quality Assurance

## CRITICAL: Agent Invocation Protocol

**YOU ARE THE COORDINATOR** - Do NOT perform the review yourself. Your role is to dispatch to the appropriate expert agent.

### STEP 1: Extract Agent Parameter

Parse the first argument to extract the agent name:
- User provides: `/nw:review @software-crafter task "steps/01-01.json"`
- Extract agent name: `software-crafter` (remove @ prefix)
- **AUTO-APPEND**: Append `-reviewer` suffix to use Haiku-powered reviewer agents
- Result: `software-crafter-reviewer` (optimized for cost-efficient reviews)
- Validate agent name is one of: researcher, software-crafter, solution-architect, product-owner, acceptance-designer, devop

### STEP 2: Verify Agent Availability

Before proceeding to Task tool invocation:
- Verify the extracted agent name matches an available agent in the system
- Check agent is not at maximum concurrency
- Confirm agent type is compatible with this command

Valid base agents (will auto-append -reviewer): researcher, software-crafter, solution-architect, product-owner, acceptance-designer, devop, agent-builder, data-engineer, illustrator, skeleton-builder, troubleshooter, visual-architect

Note: All agents are automatically invoked as their reviewer variants (e.g., software-crafter → software-crafter-reviewer) using Haiku model for cost efficiency

If agent unavailable:
- Return error: "Agent '{agent-name}' is not currently available. Available agents: {list}"
- Suggest alternative agents if applicable

### STEP 3: Extract Artifact Type and Path

Extract the second argument (artifact type):
- Valid types: `baseline`, `roadmap`, `step`, `task`, `implementation`
- Example: `task`

Extract the third argument (artifact path):
- Example: `"docs/feature/auth-upgrade/steps/01-01.json"`
- Ensure path is absolute or resolve relative to working directory

### Parameter Parsing Rules

Apply these rules to ALL extracted parameters:
1. Strip leading and trailing whitespace
2. Remove surrounding quotes (single or double) if present
3. Validate parameter is non-empty after stripping
4. Reject if extra parameters provided beyond expected count

Example for review.md:
- Input: `/nw:review  @software-crafter  task  "steps/01-01.json"`
- After parsing:
  - agent_name = "software-crafter" (whitespace trimmed)
  - artifact_type = "task" (valid value)
  - artifact_path = "steps/01-01.json" (quotes removed)
- Input: `/nw:review @software-crafter task "steps/01-01.json" extra`
- Error: "Too many parameters. Expected 3, got 4"

### STEP 4: Pre-Invocation Validation Checklist

Before invoking Task tool, verify ALL items:
- [ ] Agent name extracted and validated (not empty)
- [ ] Agent name in valid agent list
- [ ] Agent availability confirmed
- [ ] Artifact type is one of: baseline, roadmap, step, task, implementation
- [ ] All file paths are absolute (resolve relative paths to absolute)
- [ ] Referenced files exist and are readable
- [ ] Parameters contain no secrets or credentials
- [ ] Parameters within reasonable bounds (e.g., paths < 500 chars)
- [ ] No user input still has surrounding quotes

**ONLY proceed to Task tool invocation if ALL items above are checked.**

If any check fails, return specific error and stop.

### STEP 5: Invoke Agent Using Task Tool

#### Review as a New Instance Invocation

The /nw:review command invokes a NEW, INDEPENDENT reviewer agent instance. This instance loads the artifact file (task JSON, roadmap YAML, or implementation record), reads all context embedded in the file, performs expert review, and updates the file with review metadata. The reviewer instance does not retain memory from prior reviews. Each review is by a fresh instance that reads the artifact and adds its critique to the structured review field.

**MANDATORY**: Use the Task tool to invoke the specified expert agent. Do NOT attempt to perform the review yourself.

**IMPORTANT**: Always use the reviewer variant by appending `-reviewer` to the agent name.

Invoke the Task tool with this exact pattern:

```
Task: "You are the {agent-name}-reviewer agent acting as an expert reviewer.

Your specific role for this command: Provide expert critique and quality assurance for workflow artifacts

Task type: review

Perform a comprehensive {artifact-type} review of: {artifact-path}

## CRITICAL: READ THE CANONICAL SCHEMA FIRST (for step/task reviews)

**BEFORE reviewing step or task files:**
1. Read the canonical schema: `~/.claude/templates/step-tdd-cycle-schema.json` (or from repo: `nWave/templates/step-tdd-cycle-schema.json`)
2. Use this as the reference for validating step file format compliance
3. Check for format violations as HIGH severity issues

## STEP FILE FORMAT VALIDATION (for step/task reviews)

Correct step file structure includes:
- task_id: Task identifier (e.g., '01-01') - NOT step_id!
- project_id: Project identifier
- tdd_cycle.phase_execution_log: Array of EXACTLY 14 phases (MANDATORY)
- quality_gates: TDD quality requirements
- phase_validation_rules: Commit acceptance rules

## WRONG FORMATS TO FLAG AS HIGH SEVERITY

❌ 'step_id' instead of 'task_id' → REJECT
❌ 'phase_id' at top level → REJECT
❌ 'tdd_phase' at top level without 'tdd_cycle.phase_execution_log' → REJECT
❌ Less than 14 phases in phase_execution_log → REJECT
❌ Phase names with parentheses like 'RED (Acceptance)' → REJECT
❌ Phase names with spaces like 'REFACTOR L1' → REJECT

Correct 14 phase names (UPPERCASE_UNDERSCORE):
PREPARE, RED_ACCEPTANCE, RED_UNIT, GREEN_UNIT, CHECK_ACCEPTANCE, GREEN_ACCEPTANCE, REVIEW, REFACTOR_L1, REFACTOR_L2, REFACTOR_L3, REFACTOR_L4, POST_REFACTOR_REVIEW, FINAL_VALIDATE, COMMIT

Review Types:
- baseline: Review quantitative measurement baseline for metric accuracy, baseline validity, and measurement methodology
- roadmap: Review comprehensive planning document for completeness, sequencing, and feasibility
- step: Review individual step file generated by split for CORRECT FORMAT, self-contained context, clear acceptance criteria, and dependency completeness
- task: Review atomic task file before execution for CORRECT FORMAT, clarity, context, and achievability
- implementation: Review completed work against task specification and acceptance criteria

Your responsibilities:
1. READ the canonical schema first (for step/task reviews)
2. Read and understand the artifact thoroughly
3. VALIDATE FORMAT COMPLIANCE (for step/task reviews) - format errors are HIGH severity
4. Apply domain expertise to identify issues and risks
5. Provide structured feedback with severity levels (HIGH/MEDIUM/LOW)
6. Make specific, actionable recommendations
7. Update the original artifact file with review metadata
8. Assign overall approval status: APPROVED, NEEDS_REVISION, or REJECTED
9. If format violations found: Mark as REJECTED and specify required corrections

Review Guidelines:
- FORMAT COMPLIANCE is mandatory for step/task files - wrong format = REJECTED
- Be specific and actionable in critiques
- Include positive feedback where appropriate
- Focus on preventing downstream issues
- Consider domain-specific best practices
- For HIGH severity issues, mark ready_for_execution: false

Output Format:
Update the artifact file by appending or updating the reviews section with your structured feedback."
```

**Parameter Substitution**:
- Replace `{agent-name}-reviewer` with the extracted agent name + `-reviewer` suffix (e.g., "software-crafter-reviewer")
- Replace `{artifact-type}` with the artifact type (e.g., "task")
- Replace `{artifact-path}` with the absolute path to the artifact file

Note: The `-reviewer` suffix is automatically appended to route to Haiku-powered reviewer agents for cost efficiency

### Agent Registry

Valid base agents (automatically invoked as reviewer variants):
- researcher, software-crafter, solution-architect, product-owner, acceptance-designer, devop
- agent-builder, data-engineer, illustrator, skeleton-builder, troubleshooter, visual-architect

Note: This list is maintained in sync with the agent registry at `~/.claude/agents/nw/`. All review commands automatically invoke the `-reviewer` variant using Haiku model for cost efficiency.

Each agent has specific review capabilities:
- **researcher-reviewer**: Research quality, evidence validation, citation review
- **software-crafter-reviewer**: Code quality, implementation patterns, test coverage review
- **solution-architect-reviewer**: Architecture design, patterns, scalability review
- **product-owner-reviewer**: Requirements clarity, business alignment, acceptance criteria review
- **acceptance-designer-reviewer**: BDD scenarios, test completeness, acceptance criteria review
- **devop-reviewer**: Deployment readiness, operations concerns, infrastructure review
- **agent-builder-reviewer**: Agent design, quality standards, safety review
- **data-engineer-reviewer**: Data architecture, pipeline design, query optimization review
- **illustrator-reviewer**: Diagram accuracy, visual clarity, documentation review
- **skeleton-builder-reviewer**: E2E completeness, walking skeleton validation review
- **troubleshooter-reviewer**: Risk assessment, failure mode analysis, mitigation review
- **visual-architect-reviewer**: Architecture diagram accuracy, consistency review

All reviewer agents use **Haiku model** for ~50% cost reduction on review operations

### Example Invocations

**For software-crafter reviewing task** (automatically invokes software-crafter-reviewer):
```
Task: "You are the software-crafter-reviewer agent acting as an expert reviewer.

Your specific role for this command: Provide expert critique and quality assurance for workflow artifacts

Task type: review

Perform a comprehensive task review of: /mnt/c/Repositories/Projects/ai-craft/docs/feature/auth-upgrade/steps/02-01.json

[... rest of instructions ...]"
```

**For solution-architect reviewing roadmap** (automatically invokes solution-architect-reviewer):
```
Task: "You are the solution-architect-reviewer agent acting as an expert reviewer.

Your specific role for this command: Provide expert critique and quality assurance for workflow artifacts

Task type: review

Perform a comprehensive roadmap review of: /mnt/c/Repositories/Projects/ai-craft/docs/feature/auth-upgrade/roadmap.yaml

[... rest of instructions ...]"
```

### Error Handling

**Invalid Agent Name**:
- If base agent name (before adding -reviewer) is not in the valid list, respond with error:
  "Invalid agent name: {name}. Must be one of: researcher, software-crafter, solution-architect, product-owner, acceptance-designer, devop, agent-builder, data-engineer, illustrator, skeleton-builder, troubleshooter, visual-architect"
- Note: The -reviewer suffix is added automatically after validation

**Invalid Artifact Type**:
- If artifact type is not baseline, roadmap, step, task, or implementation, respond with error:
  "Invalid artifact type: {type}. Must be one of: baseline, roadmap, step, task, implementation"

**Missing Artifact File**:
- If artifact file path is not provided or file doesn't exist, respond with error:
  "Artifact file not found: {path}. Please provide valid path to artifact file."

---

## Overview

Invokes an expert agent to critique and review workflow artifacts at any stage. Provides comprehensive feedback on baselines, roadmaps, step files, atomic task files, or implementations to ensure quality and prevent issues before they propagate.

Supports five review modes:
- **baseline**: Review quantitative measurement baseline
- **roadmap**: Review comprehensive planning document
- **step**: Review individual step file generated by split
- **task**: Review atomic task file before execution
- **implementation**: Review completed work against task specification

## Usage Examples

```bash
# Review baseline measurements before roadmap creation
/nw:review @software-crafter baseline "docs/feature/auth-upgrade/baseline.yaml"

# Review a roadmap before splitting into tasks
/nw:review @solution-architect roadmap "docs/feature/auth-upgrade/roadmap.yaml"

# Review individual step file after split generation
/nw:review @software-crafter step "docs/feature/auth-upgrade/steps/01-02.json"

# Review a task file before sub-agent execution
/nw:review @software-crafter task "docs/feature/auth-upgrade/steps/02-01.json"

# Review implementation against requirements
/nw:review @devop implementation "docs/feature/auth-upgrade/steps/01-01.json"

# Security review of authentication roadmap
/nw:review @security-expert roadmap "docs/feature/auth-upgrade/roadmap.yaml"
```

## Complete Workflow Integration

These commands work together to form a complete workflow:

```bash
# Step 1: Create comprehensive plan
/nw:roadmap @solution-architect "Migrate authentication system"

# Step 2: Decompose into atomic tasks
/nw:split @solution-architect "auth-migration"

# Step 3: Execute first research task
/nw:execute @researcher "docs/feature/auth-migration/steps/01-01.json"

# Step 4: Review before implementation
/nw:review @software-crafter task "docs/feature/auth-migration/steps/02-01.json"

# Step 5: Execute implementation
/nw:execute @software-crafter "docs/feature/auth-migration/steps/02-01.json"

# Step 6: Finalize when all tasks complete
/nw:finalize @devop "auth-migration"
```

For details on each command, see respective sections.

## Context Files Required

- **For roadmap review**: The roadmap.yaml file
- **For task review**: The specific task JSON file
- **For implementation review**: Task file + implementation outputs

---

## Coordinator Success Criteria

Verify the coordinator performed these tasks:
- [ ] Agent name extracted from parameters correctly
- [ ] Agent name validated against known agents
- [ ] Artifact type extracted and validated (roadmap|task|implementation)
- [ ] File path(s) extracted and validated
- [ ] Absolute path constructed correctly
- [ ] Pre-invocation validation checklist passed
- [ ] Task tool invocation prepared with correct parameters
- [ ] Task tool returned success status
- [ ] User received confirmation of agent invocation

## Agent Execution Success Criteria

The invoked agent must accomplish (Reference Only):
- [ ] Review covers all required focus areas
- [ ] Critiques are specific and actionable
- [ ] Severity levels assigned appropriately
- [ ] Recommendations provided for all issues
- [ ] Original file updated with review metadata
- [ ] Clear approval/revision decision made

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

Review instances update the original artifact by APPENDING review metadata to the file. Because the reviewer instance has no session memory, the review output must be written to the persistent artifact file. Subsequent instances (implementation, deployment, cleanup) read this file and see all accumulated reviews. This ensures review feedback travels with the artifact across all instances and stages.

## Output Artifacts

- Updated artifact file with embedded review
- Optional: `docs/feature/{project-id}/reviews/{timestamp}-{artifact-type}-review.md`

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
