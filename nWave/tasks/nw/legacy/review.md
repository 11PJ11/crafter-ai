# DW-REVIEW: Expert Critique and Quality Assurance
# LEGACY - preserved 2026-02-08 (692 lines)
# Migrated to v2 format at nWave/tasks/nw/review.md

---
## ORCHESTRATOR INVOCATION PROTOCOL (MANDATORY)

**When YOU (orchestrator) delegate this command to an agent via Task tool:**

### CORRECT Pattern (minimal prompt):
```python
Task(
    subagent_type="software-crafter-reviewer",
    prompt="Review: step docs/feature/auth-upgrade/execution-log.yaml step_id=01-01"
)
```

### Why This Works:
- ✅ execution-log.yaml contains ALL phase tracking (pipe-delimited events per step)
- ✅ Reviewer agent has internal knowledge of review criteria
- ✅ Artifact type ("step") specifies what to review
- ✅ No conversation context needed

### WRONG Patterns (avoid):
```python
# ❌ Embedding review criteria (reviewer already knows this)
Task(prompt="Review task 01-01.json. Check SOLID, test coverage, security...")

# ❌ Listing validation rules (execution-log.yaml has these)
Task(prompt="Review 01-01. Ensure all 7 phases executed, no DEFERRED...")

# ❌ Severity guidance (reviewer knows HIGH/MEDIUM/LOW)
Task(prompt="Review 01-01. Use HIGH for blocking issues, MEDIUM for...")

# ❌ Any context from current conversation
Task(prompt="Review 01-01. As discussed, pay attention to SISTER constraint...")
```

### Key Principle:
**Command invocation = Artifact type + Artifact path ONLY**

The artifact file is self-contained. Your prompt should not duplicate review criteria.

---

## AGENT PROMPT REINFORCEMENT (Command-Specific Guidance)

Reinforce command-specific principles extracted from THIS file (review.md):

### Recommended Prompt Template:
```python
Task(
    subagent_type="software-crafter-reviewer",
    prompt="""Review: step docs/feature/auth-upgrade/execution-log.yaml step_id=01-01

CRITICAL (from review.md):
- Format validation FIRST (execution-log.yaml must have all 7 phases per step)
- External Validity (CM-C): Feature must be invocable, not just exist
- Format errors = HIGH severity = REJECTED
- Update original artifact file (not separate review file)

AVOID:
- ❌ Approving non-invocable features (missing integration step)
- ❌ Ignoring format violations (wrong phase names, missing phases)
- ❌ Creating separate review file (must update original artifact)
- ❌ Skipping external validity check (tests pass but users can't invoke)"""
)
```

### Why Add This Guidance:
- **Source**: Extracted from review.md (not conversation context)
- **Deterministic**: Same principles every time you invoke review
- **Reinforcing**: Prevents approving broken artifacts
- **Token-efficient**: ~100 tokens vs costly rework

### What NOT to Add:
```python
# ❌ WRONG - This uses orchestrator's conversation context
Task(prompt="""Review: task 01-01.json

As we discussed, pay special attention to the SISTER constraint handling.
The implementation should address the tier 2 bottleneck we identified.""")
```

---

## CRITICAL: Agent Invocation Protocol

**YOU ARE THE COORDINATOR** - Do NOT perform the review yourself. Your role is to dispatch to the appropriate expert agent.

### STEP 1: Extract Agent Parameter

Parse the first argument to extract the agent name:
- User provides: `/nw:review @nw-software-crafter step "docs/feature/auth-upgrade/execution-log.yaml" step_id=01-01`
- Extract agent name: `nw-software-crafter` (remove @ prefix)
- **AUTO-APPEND**: Append `-reviewer` suffix to get reviewer agent name
- Result: `nw-software-crafter-reviewer` (optimized for cost-efficient reviews on Haiku)
- Validate base agent name is one of: nw-researcher, nw-software-crafter, nw-solution-architect, nw-product-owner, nw-acceptance-designer, nw-devop, nw-agent-builder, nw-data-engineer, nw-documentarist, nw-troubleshooter, nw-leanux-designer, nw-platform-architect, nw-product-discoverer

### STEP 2: Verify Agent Availability

Before proceeding to Task tool invocation:
- Verify the extracted agent name matches an available agent in the system
- Check agent is not at maximum concurrency
- Confirm agent type is compatible with this command

Valid base agents: nw-researcher, nw-software-crafter, nw-solution-architect, nw-product-owner, nw-acceptance-designer, nw-devop, nw-agent-builder, nw-data-engineer, nw-documentarist, nw-troubleshooter, nw-leanux-designer, nw-platform-architect, nw-product-discoverer

All agents are automatically invoked as their reviewer variants by appending `-reviewer` (e.g., nw-software-crafter → nw-software-crafter-reviewer) using Haiku model for cost efficiency

If agent unavailable:
- Return error: "Agent '{agent-name}' is not currently available. Available agents: {list}"
- Suggest alternative agents if applicable

### STEP 3: Extract Artifact Type and Path

Extract the second argument (artifact type):
- Valid types: `baseline`, `roadmap`, `step`, `task`, `implementation`
- Example: `task`

Extract the third argument (artifact path):
- Example: `"docs/feature/auth-upgrade/execution-log.yaml"`
- Ensure path is absolute or resolve relative to working directory

### Parameter Parsing Rules

Apply these rules to ALL extracted parameters:
1. Strip leading and trailing whitespace
2. Remove surrounding quotes (single or double) if present
3. Validate parameter is non-empty after stripping
4. Reject if extra parameters provided beyond expected count

Example for review.md:
- Input: `/nw:review  @nw-software-crafter  step  "docs/feature/auth-upgrade/execution-log.yaml"`
- After parsing:
  - agent_name = "nw-software-crafter" (whitespace trimmed, append -reviewer → "nw-software-crafter-reviewer")
  - artifact_type = "step" (valid value)
  - artifact_path = "docs/feature/auth-upgrade/execution-log.yaml" (quotes removed)
- Input: `/nw:review @nw-software-crafter step "docs/feature/auth-upgrade/execution-log.yaml" extra`
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

The /nw:review command invokes a NEW, INDEPENDENT reviewer agent instance. This instance loads the artifact file (execution-log.yaml, roadmap YAML, or implementation record), reads all context embedded in the file, performs expert review, and updates the file with review metadata. The reviewer instance does not retain memory from prior reviews. Each review is by a fresh instance that reads the artifact and adds its critique to the structured review field.

**MANDATORY**: Use the Task tool to invoke the specified expert agent. Do NOT attempt to perform the review yourself.

**IMPORTANT**: Always use the reviewer variant by appending `-reviewer` to the agent name.

Invoke the Task tool with this exact pattern:

```
Task: "You are the {agent-name}-reviewer agent acting as an expert reviewer.

Your specific role for this command: Provide expert critique and quality assurance for workflow artifacts

Task type: review

Perform a comprehensive {artifact-type} review of: {artifact-path}

## CRITICAL: VALIDATE execution-log.yaml FORMAT (for step reviews)

**BEFORE reviewing steps:**
1. Read the project's `execution-log.yaml` (at `docs/feature/{project-id}/execution-log.yaml`)
2. Validate that every step has all 7 required phases in the pipe-delimited event format
3. Check for format violations as HIGH severity issues

## execution-log.yaml FORMAT VALIDATION (for step reviews)

Correct format is an append-only event log with pipe-delimited entries:
```yaml
events:
  - "step_id|phase|status|data|timestamp"
```

Each step MUST have exactly 7 phase events:
1. PREPARE
2. RED_ACCEPTANCE
3. RED_UNIT
4. GREEN
5. REVIEW
6. REFACTOR_CONTINUOUS
7. COMMIT

Valid statuses: EXECUTED, SKIPPED (with approved reason)

## WRONG FORMATS TO FLAG AS HIGH SEVERITY

❌ Step JSON files (DEPRECATED - all tracking uses execution-log.yaml) → REJECT
❌ Fewer than 7 phases for a step → REJECT
❌ Phase names with parentheses like 'RED (Acceptance)' → REJECT (correct: RED_ACCEPTANCE)
❌ Phase names with spaces like 'REFACTOR L1' → REJECT (correct: REFACTOR_CONTINUOUS)
❌ Nested YAML phase objects instead of pipe-delimited strings → REJECT
❌ SKIPPED without approved reason → REJECT

Review Types:
- baseline: Review quantitative measurement baseline for metric accuracy, baseline validity, and measurement methodology
- roadmap: Review comprehensive planning document for completeness, sequencing, and feasibility
- step: Review roadmap step definition and its execution-log.yaml phases for CORRECT FORMAT (all 7 phases present), proper status tracking, and dependency completeness
- task: Review atomic task file before execution for CORRECT FORMAT, clarity, context, and achievability
- implementation: Review completed work against task specification and acceptance criteria

Your responsibilities:
1. VALIDATE execution-log.yaml format first (for step reviews) - all 7 phases required per step
2. Read and understand the artifact thoroughly
3. VALIDATE FORMAT COMPLIANCE (for step reviews) - format errors are HIGH severity
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

Valid base agents (append -reviewer to get reviewer agent name):
- nw-researcher, nw-software-crafter, nw-solution-architect, nw-product-owner, nw-acceptance-designer, nw-devop
- nw-agent-builder, nw-data-engineer, nw-documentarist, nw-troubleshooter, nw-leanux-designer, nw-platform-architect, nw-product-discoverer

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

**For nw-software-crafter reviewing task** (automatically invokes software-crafter-reviewer):
```
Task: "You are the software-crafter-reviewer agent acting as an expert reviewer.

Your specific role for this command: Provide expert critique and quality assurance for workflow artifacts

Task type: review

Perform a comprehensive step review of: /mnt/c/Repositories/Projects/nwave/docs/feature/auth-upgrade/execution-log.yaml (step_id=02-01)

[... rest of instructions ...]"
```

**For nw-solution-architect reviewing roadmap** (automatically invokes solution-architect-reviewer):
```
Task: "You are the solution-architect-reviewer agent acting as an expert reviewer.

Your specific role for this command: Provide expert critique and quality assurance for workflow artifacts

Task type: review

Perform a comprehensive roadmap review of: /mnt/c/Repositories/Projects/nwave/docs/feature/auth-upgrade/roadmap.yaml

[... rest of instructions ...]"
```

### Error Handling

**Invalid Agent Name**:
- If base agent name (before adding -reviewer) is not in the valid list, respond with error:
  "Invalid agent name: {name}. Must be one of: nw-researcher, nw-software-crafter, nw-solution-architect, nw-product-owner, nw-acceptance-designer, nw-devop, nw-agent-builder, nw-data-engineer, illustrator, skeleton-builder, troubleshooter, visual-architect"
- Note: The -reviewer suffix is added automatically after validation

**Invalid Artifact Type**:
- If artifact type is not baseline, roadmap, step, task, or implementation, respond with error:
  "Invalid artifact type: {type}. Must be one of: baseline, roadmap, step, task, implementation"

**Missing Artifact File**:
- If artifact file path is not provided or file doesn't exist, respond with error:
  "Artifact file not found: {path}. Please provide valid path to artifact file."

---

## Overview

Invokes an expert agent to critique and review workflow artifacts at any stage. Provides comprehensive feedback on baselines, roadmaps, step definitions (tracked in execution-log.yaml), atomic task files, or implementations to ensure quality and prevent issues before they propagate.

Supports five review modes:
- **baseline**: Review quantitative measurement baseline
- **roadmap**: Review comprehensive planning document
- **step**: Review roadmap step definition and its execution-log.yaml phases
- **task**: Review atomic task file before execution
- **implementation**: Review completed work against task specification

## Usage Examples

```bash
# Review baseline measurements before roadmap creation
/nw:review @nw-software-crafter baseline "docs/feature/auth-upgrade/baseline.yaml"

# Review a roadmap before splitting into tasks
/nw:review @nw-solution-architect roadmap "docs/feature/auth-upgrade/roadmap.yaml"

# Review step definition and execution phases
/nw:review @nw-software-crafter step "docs/feature/auth-upgrade/execution-log.yaml" step_id=01-02

# Review a step before sub-agent execution
/nw:review @nw-software-crafter step "docs/feature/auth-upgrade/execution-log.yaml" step_id=02-01

# Review implementation against requirements
/nw:review @nw-devop implementation "docs/feature/auth-upgrade/execution-log.yaml" step_id=01-01

# Security review of authentication roadmap
/nw:review @security-expert roadmap "docs/feature/auth-upgrade/roadmap.yaml"
```

## Complete Workflow Integration

These commands work together to form a complete workflow:

```bash
# Step 1: Create comprehensive plan
/nw:roadmap @nw-solution-architect "Migrate authentication system"

# Step 2: Decompose into atomic tasks
/nw:split @nw-solution-architect "auth-migration"

# Step 3: Execute first research task
/nw:execute @nw-researcher "docs/feature/auth-migration/execution-log.yaml" step_id=01-01

# Step 4: Review before implementation
/nw:review @nw-software-crafter step "docs/feature/auth-migration/execution-log.yaml" step_id=02-01

# Step 5: Execute implementation
/nw:execute @nw-software-crafter "docs/feature/auth-migration/execution-log.yaml" step_id=02-01

# Step 6: Finalize when all tasks complete
/nw:finalize @nw-devop "auth-migration"
```

For details on each command, see respective sections.

## Context Files Required

- **For roadmap review**: The roadmap.yaml file
- **For task/step review**: The project's `execution-log.yaml` file
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
- **OVER-DECOMPOSITION CHECK** (MANDATORY):
  1. Count implementation steps vs estimated production files
  2. If ratio > 2.5 steps per production file: **FLAG as potential over-decomposition**
  3. Check each step: "Does this step require NEW production code?"
  4. If >20% of steps are validation-only (no new production code): **REJECT with consolidation guidance**
  5. Common anti-pattern: one step per acceptance test scenario instead of per implementation unit

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
6. **Apply External Validity Check (CM-C)** - see below

**CM-C: External Validity Check (MANDATORY)**

For roadmap and step reviews, ask yourself:

> "If I follow these steps exactly, will the feature WORK or just EXIST?"

A feature that:
- Has all tests passing
- Has 100% coverage
- Has high mutation score
- But cannot be invoked by users

...is NOT COMPLETE. It fails external validity.

**External Validity Criteria**:
1. **At least one step targets entry point integration** - Feature must be wired into system
2. **Tests verify observable system behavior** - Not just internal state assertions
3. **User can invoke feature after completion** - Entry point exists and calls the component

**Review Questions to Ask**:
- Does the roadmap include an integration step?
- Do acceptance tests import entry point modules (not internal components)?
- After all steps complete, how does the user invoke this feature?
- Is there at least one wiring test proving end-to-end path works?

**External Validity Failure Response**:
```yaml
external_validity:
  status: FAILED
  reason: "No integration step - feature will exist but not be invocable"
  required_action: "Add step to wire component into entry point"
  blocking: true
```

REJECT any artifact that would produce a non-invocable feature.

**Severity Definitions**:
- **HIGH**: Blocks progress or creates significant risk
- **MEDIUM**: Should be addressed but not blocking
- **LOW**: Nice to have improvement

**Review Outcomes**:
- **APPROVED**: Ready to proceed (including external validity passed)
- **NEEDS_REVISION**: Must address HIGH severity issues
- **REJECTED**: Fundamental flaws requiring restart (including external validity failure)

### Expert Agent Selection

Choose reviewer based on domain expertise:

- `@nw-solution-architect`: Architecture and design reviews
- `@nw-software-crafter`: Code quality and implementation
- `@security-expert`: Security implications
- `@nw-data-engineer`: Data pipeline and architecture
- `@nw-devop`: Deployment and operations readiness
- `@nw-product-owner`: Business alignment and requirements
- `@troubleshooter`: Risk and failure mode analysis

### Processing Flow

1. **Load Artifact**: Read the specified file
2. **Contextual Analysis**: Understand project goals and constraints
3. **Expert Review**: Apply domain expertise to identify issues
4. **Generate Critique**: Create structured feedback
5. **UPDATE ORIGINAL FILE**: Append review section to the artifact
6. **Create Report**: Generate summary for stakeholders

**IMPORTANT**: The review command ALWAYS updates the original artifact file (roadmap.yaml or execution-log.yaml) by appending the review data. This ensures critiques travel with the artifact and are available to all subsequent agents.

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
