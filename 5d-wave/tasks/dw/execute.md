---
description: 'Execute atomic task with state tracking [agent] [step-file-path]'
argument-hint: '[agent] [step-file-path] - Example: @researcher "steps/01-01.json"'
agent-activation:
  required: false
  agent-parameter: true
  agent-command: "*workflow-execute"
---

# DW-EXECUTE: Atomic Task Execution Engine

**Type**: Task Execution Tool
**Agent**: Specified as parameter
**Command**: `/dw:execute [agent] [step-file-path]`

## Overview

Executes a self-contained atomic task by invoking the specified agent with complete context from the step file. Manages state transitions, tracks execution progress, and updates the step file with results.

Designed to work with clean context, ensuring consistent quality by giving each agent a fresh start with all necessary information contained in the step file.

## Usage Examples

```bash
# Execute a research task
/dw:execute @researcher "docs/workflow/auth-upgrade/steps/01-01.json"

# Execute implementation task
/dw:execute @software-crafter "docs/workflow/auth-upgrade/steps/02-01.json"

# Execute testing task
/dw:execute @devop "docs/workflow/auth-upgrade/steps/04-01.json"

# Override the suggested agent
/dw:execute @solution-architect "docs/workflow/auth-upgrade/steps/01-02.json"
```

## State Transitions

```
TODO → IN_PROGRESS → DONE
         ↓      ↓
      FAILED  IN_REVIEW
         ↓      ↓
      RETRY   REWORK
```

## Context Files Required

- Step file (JSON) with complete task specification
- Any files referenced in step's `relevant_files` field

## CRITICAL: Agent Invocation Protocol

**YOU ARE THE COORDINATOR** - Do NOT execute the task yourself. Your role is to dispatch to the appropriate agent.

### STEP 1: Extract Agent Parameter

Parse the first argument to extract the agent name:
- User provides: `/dw:execute @researcher "steps/01-01.json"`
- Extract agent name: `researcher` (remove @ prefix)
- Validate agent name is one of: researcher, software-crafter, solution-architect, product-owner, acceptance-designer, devop

### STEP 2: Extract Step File Path

Extract the second argument (step file path):
- Example: `"docs/workflow/auth-upgrade/steps/01-01.json"`
- Ensure path is absolute or resolve relative to working directory

### STEP 3: Invoke Agent Using Task Tool

**MANDATORY**: Use the Task tool to invoke the specified agent. Do NOT attempt to execute the task yourself.

Invoke the Task tool with this exact pattern:

```
Task: "You are the {agent-name} agent.

Read and execute the atomic task specified in: {step-file-path}

The step file is a complete JSON specification containing:
- self_contained_context: All background and context needed
- task_specification: What to do and acceptance criteria
- dependencies: Prerequisites (must already be complete)
- state: Current task state

Your responsibilities:
1. Load the step file and validate it
2. Update state to IN_PROGRESS
3. Execute the task following the detailed_instructions
4. Validate all acceptance_criteria are met
5. Update state to DONE with execution_result
6. Update the step file with your results

If you encounter issues:
- Update state to FAILED with failure_reason
- Include recovery_suggestions in execution_result
- Set can_retry appropriately

Commit the updated step file after execution."
```

**Parameter Substitution**:
- Replace `{agent-name}` with the extracted agent name (e.g., "researcher")
- Replace `{step-file-path}` with the absolute path to the step file

### Example Invocations

**For researcher agent**:
```
Task: "You are the researcher agent.

Read and execute the atomic task specified in: /mnt/c/Repositories/Projects/ai-craft/docs/workflow/auth-upgrade/steps/01-01.json

[... rest of instructions ...]"
```

**For software-crafter agent**:
```
Task: "You are the software-crafter agent.

Read and execute the atomic task specified in: /mnt/c/Repositories/Projects/ai-craft/docs/workflow/auth-upgrade/steps/02-01.json

[... rest of instructions ...]"
```

### Error Handling

**Invalid Agent Name**:
- If agent name is not in the valid list, respond with error:
  "Invalid agent name: {name}. Must be one of: researcher, software-crafter, solution-architect, product-owner, acceptance-designer, devop"

**Missing Step File**:
- If step file path is not provided or file doesn't exist, respond with error:
  "Step file not found: {path}. Please provide valid path to step JSON file."

**Dependency Not Met**:
- If the invoked agent reports dependency failures, explain the blocking tasks to the user

---

## Agent Invocation (Reference Documentation)

The following section documents what the invoked agent will do. **You (the coordinator) do not execute this - the agent does.**

### Primary Task Instructions

**Task**: Read step file and execute the specified task with full context

**Execution Process**:

#### 1. PRE-EXECUTION PHASE

**Load and Validate**:
```python
1. Read step file JSON
2. Check for existing reviews
   - If reviews exist with ready_for_execution = false, BLOCK
   - Log any unresolved HIGH severity critiques
3. Verify all required fields present
4. Check dependencies are marked complete
5. Validate agent compatibility with task type
6. Load any referenced files
7. Apply any review recommendations to context
```

**State Update**:
```json
{
  "state": {
    "status": "IN_PROGRESS",
    "assigned_to": "{agent-name}",
    "started_at": "2024-01-15T10:00:00Z",
    "updated": "2024-01-15T10:00:00Z"
  }
}
```

#### 2. EXECUTION PHASE

**Agent receives complete context**:
```
Background: {self_contained_context.background}
Technical Context: {self_contained_context.technical_context}
Prerequisites Completed: {self_contained_context.prerequisites_completed}
Relevant Files: {self_contained_context.relevant_files}

TASK: {task_specification.name}
Description: {task_specification.description}
Motivation: {task_specification.motivation}

INSTRUCTIONS:
{task_specification.detailed_instructions}

ACCEPTANCE CRITERIA:
{task_specification.acceptance_criteria}

Execute this task and provide outputs as specified.
```

#### 3. POST-EXECUTION PHASE

**Success State Update**:
```json
{
  "state": {
    "status": "DONE",
    "assigned_to": "{agent-name}",
    "started_at": "2024-01-15T10:00:00Z",
    "completed_at": "2024-01-15T11:30:00Z",
    "updated": "2024-01-15T11:30:00Z"
  },
  "execution_result": {
    "success": true,
    "outputs": [
      "docs/workflow/auth-upgrade/provider-selection.md"
    ],
    "acceptance_criteria_met": [
      {
        "criterion": "Comparison matrix includes 5 providers",
        "met": true,
        "evidence": "Matrix has 6 providers"
      }
    ],
    "metrics": {
      "execution_time_hours": 1.5,
      "tokens_used": 45000
    },
    "agent_notes": "Completed successfully. Added Keycloak as 6th provider."
  }
}
```

**Failure State Update**:
```json
{
  "state": {
    "status": "FAILED",
    "assigned_to": "{agent-name}",
    "started_at": "2024-01-15T10:00:00Z",
    "failed_at": "2024-01-15T10:45:00Z",
    "updated": "2024-01-15T10:45:00Z"
  },
  "execution_result": {
    "success": false,
    "failure_reason": "Unable to access pricing information for 2 providers",
    "partial_completion": true,
    "completed_criteria": ["Comparison matrix created"],
    "blocked_criteria": ["Cost projections incomplete"],
    "recovery_suggestions": [
      "Contact vendor for pricing",
      "Use estimation based on user tiers"
    ],
    "can_retry": true
  }
}
```

**Review Required State**:
```json
{
  "state": {
    "status": "IN_REVIEW",
    "assigned_to": "{agent-name}",
    "started_at": "2024-01-15T10:00:00Z",
    "review_requested_at": "2024-01-15T11:00:00Z",
    "updated": "2024-01-15T11:00:00Z"
  },
  "execution_result": {
    "success": true,
    "outputs_require_review": true,
    "review_reason": "Significant architectural decision needs approval",
    "review_requested_from": "@solution-architect"
  }
}
```

### Error Handling

**Dependency Failures**:
```json
{
  "execution_blocked": {
    "reason": "dependency_not_met",
    "blocking_tasks": ["01-02", "01-03"],
    "message": "Cannot execute until dependencies complete"
  }
}
```

**Context Issues**:
```json
{
  "execution_blocked": {
    "reason": "insufficient_context",
    "missing_information": [
      "Database connection string",
      "API endpoint URL"
    ],
    "resolution": "Update step file with missing context"
  }
}
```

**Agent Errors**:
```json
{
  "execution_error": {
    "type": "agent_error",
    "error_message": "Agent encountered unexpected error",
    "stack_trace": "...",
    "retry_attempts": 1,
    "max_retries": 3
  }
}
```

### State History Tracking

All state changes are appended to history:
```json
{
  "state_history": [
    {
      "status": "TODO",
      "timestamp": "2024-01-15T09:00:00Z",
      "actor": "system"
    },
    {
      "status": "IN_PROGRESS",
      "timestamp": "2024-01-15T10:00:00Z",
      "actor": "@researcher"
    },
    {
      "status": "IN_REVIEW",
      "timestamp": "2024-01-15T11:00:00Z",
      "actor": "@researcher",
      "reason": "Needs architecture approval"
    },
    {
      "status": "DONE",
      "timestamp": "2024-01-15T14:00:00Z",
      "actor": "@solution-architect",
      "note": "Approved with minor suggestions"
    }
  ]
}
```

### Execution Metrics

Track performance for optimization:
```json
{
  "execution_metrics": {
    "attempts": 1,
    "total_execution_time": 1.5,
    "tokens": {
      "input": 12000,
      "output": 33000,
      "total": 45000
    },
    "cost_estimate": "$0.45",
    "complexity_score": 7,
    "rework_count": 0
  }
}
```

### Integration with Other Commands

**Pre-execution Review**:
```bash
# Review before execution
/dw:review @software-crafter task "steps/02-01.json"
# The review updates the step file with critiques
# Execute only if review.ready_for_execution = true
/dw:execute @software-crafter "steps/02-01.json"
```

**Reading Previous Reviews**:
The execute command checks for existing reviews in the step file:
```json
{
  "reviews": [
    {
      "reviewer": "@software-crafter",
      "ready_for_execution": true,
      "critiques": []
    }
  ]
}
```
If `ready_for_execution` is false, execution is blocked until issues are resolved.

**Post-execution Review**:
```bash
# Execute task
/dw:execute @researcher "steps/01-01.json"
# Review implementation
/dw:review @product-owner implementation "steps/01-01.json"
```

**Retry After Failure**:
```bash
# Initial attempt fails
/dw:execute @data-engineer "steps/03-01.json"
# Update context and retry
/dw:execute @data-engineer "steps/03-01.json" --retry
```

## Success Criteria

**Validation Checklist**:
- [ ] Step file loaded successfully
- [ ] Dependencies verified as complete
- [ ] Agent invoked with full context
- [ ] State transitions properly recorded
- [ ] Execution results captured
- [ ] Step file updated with results
- [ ] State history maintained
- [ ] Metrics tracked for analysis

## Output Artifacts

- Updated step file with execution results
- Any outputs specified in acceptance criteria
- Execution logs in `docs/workflow/{project-id}/logs/{timestamp}-{task-id}.log`

## Notes

### Clean Context Execution

Each execution starts with a clean context, ensuring:
1. **No contamination** from previous tasks
2. **Consistent quality** across all executions
3. **Predictable behavior** regardless of execution order
4. **Maximum LLM performance** without context degradation

### Parallel Execution Support

Multiple execute commands can run simultaneously for non-dependent tasks:
```bash
# These can run in parallel
/dw:execute @researcher "steps/01-01.json" &
/dw:execute @researcher "steps/01-02.json" &
/dw:execute @software-crafter "steps/02-01.json" &
```

### State Machine Integrity

The execute command ensures state transitions follow valid paths:
- TODO can only go to IN_PROGRESS
- IN_PROGRESS can go to DONE, FAILED, or IN_REVIEW
- FAILED can go to RETRY
- IN_REVIEW can go to DONE or REWORK
- DONE is terminal (unless explicitly reset)

### Execution Queue Management

For complex projects, executions can be queued:
```json
{
  "execution_queue": {
    "queued_at": "2024-01-15T10:00:00Z",
    "position": 3,
    "estimated_start": "2024-01-15T11:30:00Z"
  }
}
```

This execution engine ensures each atomic task is executed with maximum efficiency and quality, maintaining the integrity of the distributed workflow system while preventing context degradation.