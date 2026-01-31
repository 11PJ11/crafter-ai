# DW-EXECUTE: Atomic Task Execution Engine (Schema v2.0 - Token-Minimal Architecture)

---
## ORCHESTRATOR INVOCATION PROTOCOL (MANDATORY)

**When YOU (orchestrator) delegate this command to an agent via Task tool:**

### CRITICAL: You MUST Extract Full Context from Roadmap

**The orchestrator (YOU) is responsible for:**
1. Loading roadmap.yaml ONCE (102k tokens)
2. Extracting step definition context (~5k tokens)
3. Passing complete context explicitly to sub-agent
4. Sub-agent receives context and does NOT load roadmap (saves 97k tokens per step)

### CORRECT Pattern (full context extraction):
```python
# STEP 1: Read roadmap to find step definition
roadmap_content = Read("docs/feature/{project-id}/roadmap.yaml")

# STEP 2: Extract step context (search for step_id: "{step-id}")
# Extract: name, description, acceptance_criteria, test_file, scenario_line,
#          acceptance_test_scenario, dependencies, estimated_hours,
#          implementation_notes, quality_gates

# STEP 3: Pass extracted context explicitly to agent
Task(
    subagent_type="software-crafter",
    prompt="""You are the software-crafter agent.

Task type: execute
PROJECT: {project-id}
STEP: {step-id}

## TASK CONTEXT (EXTRACTED FROM ROADMAP - DO NOT LOAD ROADMAP)

**Step ID**: {step_id}
**Name**: {name}
**Description**: {description}

**Acceptance Criteria**:
{acceptance_criteria}

**Test File**: {test_file}
**Scenario Line**: {scenario_line}
**Acceptance Test Scenario**: {acceptance_test_scenario}

**Quality Gates**:
{quality_gates}

**Implementation Notes**:
{implementation_notes}

**Dependencies**: {dependencies}
**Estimated Hours**: {estimated_hours}

## MANDATORY TDD PHASES

Execute these 7 phases in order:
0. PREPARE - Remove @skip decorators, verify only 1 scenario enabled
1. RED_ACCEPTANCE - Run acceptance test, expect FAIL for valid reason
2. RED_UNIT - Write failing unit tests before implementation
3. GREEN - Implement minimum code to pass all tests
4. REVIEW - Quality review: SOLID, coverage, criteria
5. REFACTOR_CONTINUOUS - L1 (naming) + L2 (complexity) + L3 (organization) [fast-path if <30 LOC]
6. COMMIT - Final validate + commit

## STATE TRACKING

**CRITICAL**: DO NOT load roadmap.yaml (context provided above).
**READ/WRITE ONLY**: docs/feature/{project-id}/execution-status.yaml

Update execution-status.yaml after EACH phase (no batching)."""
)
```

### Why This Works:
- ✅ Orchestrator loads roadmap.yaml ONCE (102k tokens)
- ✅ Orchestrator extracts task context (~5k tokens) and passes explicitly
- ✅ Sub-agent receives full context, does NOT load roadmap (saves 97k tokens per step)
- ✅ Agent has all information needed to execute
- ✅ No ambiguity about what to do
- ✅ Deterministic execution

### WRONG Patterns (avoid):
```python
# ❌ WRONG - Minimal prompt without context (agent forced to load roadmap)
Task(prompt="Execute: des-us007-boundary-rules step 01-01")

# ❌ WRONG - Including conversation context instead of roadmap context
Task(prompt="""Execute 01-01. As we discussed earlier, focus on parallelization.""")

# ❌ WRONG - Old step file path format (no longer used)
Task(prompt="Execute: docs/feature/auth-upgrade/steps/01-01.json")
```

### Key Principle:
**Orchestrator extracts and passes ALL context explicitly. Agent receives self-contained prompt.**

The token savings (97k per step) ONLY work if orchestrator does the extraction.
If agent has to load roadmap, we waste tokens.

---

## CRITICAL: Agent Invocation Protocol

**YOU ARE THE COORDINATOR** - Do NOT execute the task yourself. Your role is to dispatch to the appropriate agent.

### STEP 1: Extract Agent Parameter

Parse the first argument to extract the agent name:
- User provides: `/nw:execute @researcher "steps/01-01.json"`
- Extract agent name: `researcher` (remove @ prefix)
- Validate agent name is one of: researcher, software-crafter, solution-architect, product-owner, acceptance-designer, devop

### STEP 2: Verify Agent Availability

Before proceeding to Task tool invocation:
- Verify the extracted agent name matches an available agent in the system
- Check agent is not at maximum concurrency
- Confirm agent type is compatible with this command

Valid agents: researcher, software-crafter, solution-architect, product-owner, acceptance-designer, devop

If agent unavailable:
- Return error: "Agent '{agent-name}' is not currently available. Available agents: {list}"
- Suggest alternative agents if applicable

### STEP 3: Extract Project ID and Step ID (NEW ARCHITECTURE)

Extract the second and third arguments:
- Second argument: Project ID (e.g., `"des-us007-boundary-rules"`)
- Third argument: Step ID (e.g., `"01-01"`)

### Parameter Parsing Rules

Apply these rules to ALL extracted parameters:
1. Strip leading and trailing whitespace
2. Remove surrounding quotes (single or double) if present
3. Validate parameter is non-empty after stripping
4. Reject if extra parameters provided beyond expected count

Example for execute.md (NEW ARCHITECTURE):
- Input: `/nw:execute  @software-crafter  "des-us007-boundary-rules"  "01-01"`
- After parsing:
  - agent_name = "software-crafter" (whitespace trimmed)
  - project_id = "des-us007-boundary-rules" (quotes removed)
  - step_id = "01-01" (quotes removed)
- Input: `/nw:execute @software-crafter "des-us007" "01-01" extra`
- Error: "Too many parameters. Expected 3, got 4"

### STEP 4: Pre-Invocation Validation Checklist (NEW ARCHITECTURE)

Before invoking Task tool, verify ALL items:
- [ ] Agent name extracted and validated (not empty)
- [ ] Agent name in valid agent list
- [ ] Agent availability confirmed
- [ ] Project ID extracted and validated (kebab-case format)
- [ ] Step ID extracted and validated (format: XX-XX)
- [ ] Roadmap file exists at `docs/feature/{project-id}/roadmap.yaml`
- [ ] Execution status file exists at `docs/feature/{project-id}/execution-status.yaml`
- [ ] Step ID exists in roadmap (orchestrator verifies via `find_step_in_roadmap()`)
- [ ] Parameters contain no secrets or credentials
- [ ] Parameters within reasonable bounds (e.g., IDs < 100 chars)
- [ ] No user input still has surrounding quotes

**ONLY proceed to Task tool invocation if ALL items above are checked.**

If any check fails, return specific error and stop.

### STEP 5: Context Extraction and Agent Invocation (NEW ARCHITECTURE)

**CRITICAL OPTIMIZATION**: Orchestrator loads roadmap ONCE, extracts task context, passes to sub-agent.
Token savings: 102k - 5k = 97k per step × 16 steps = 1.52M tokens saved.

**Orchestrator Actions BEFORE invoking Task tool**:

```python
# 1. Use Grep to find step definition location in roadmap
grep_result = Grep(
    pattern=f'step_id: "{step_id}"',
    path=f"docs/feature/{project_id}/roadmap.yaml",
    output_mode="content",
    context_lines=50  # Get surrounding context
)

# 2. Read the step section from roadmap
# Extract from grep results:
# - name: (string)
# - description: (multi-line string after >)
# - acceptance_criteria: (list of strings)
# - test_file: (string)
# - scenario_line: (number)
# - acceptance_test_scenario: (string)
# - quality_gates: (dict with acceptance_test_must_fail_first, etc.)
# - implementation_notes: (multi-line string after >)
# - dependencies: (list of step IDs)
# - estimated_hours: (number)
# - suggested_agent: (string)

# 3. Read TDD phases from roadmap header (once, reuse for all steps)
# Located in tdd_phases section at top of roadmap

# 4. Read execution config from roadmap header
# Located in execution_config section

# Result: ~5k tokens of extracted context to pass to agent
```

**Extraction Example**:

```
Step found at line 360:
  - step_id: "03-01"
    name: "Create ScopeValidator class with git diff integration"
    description: >
      Implement ScopeValidator in src/des/validation/scope_validator.py...
    acceptance_criteria:
      - "ScopeValidator executes git diff command successfully"
      - "Modified file list extracted from git output"
    test_file: "tests/des/acceptance/test_us007_boundary_rules.py"
    scenario_line: 357
    ...

Extract these fields and format into agent prompt below.
```

**MANDATORY**: Use the Task tool to invoke the specified agent. Do NOT attempt to execute the task yourself.

Invoke the Task tool with this exact pattern:

```
Task: "You are the {agent-name} agent.

Your specific role for this command: Execute atomic tasks with complete state tracking via execution-status.yaml

Task type: execute

PROJECT: {project-id}
STEP: {step-id}

## TASK CONTEXT (EXTRACTED FROM ROADMAP - DO NOT LOAD ROADMAP)

The orchestrator has extracted the following self-contained context for you:

**Step ID**: {task_context[step_id]}
**Name**: {task_context[name]}
**Description**: {task_context[description]}

**Acceptance Criteria**:
{task_context[acceptance_criteria]}

**Test File**: {task_context[test_file]}
**Scenario Line**: {task_context[scenario_line]}
**Acceptance Test Scenario**: {task_context[acceptance_test_scenario]}

**Quality Gates**:
{task_context[quality_gates]}

**Deliverables**:
{task_context[deliverables]}

**Implementation Notes**:
{task_context[implementation_notes]}

**Dependencies** (must be complete before execution):
{task_context[dependencies]}

**Estimated Hours**: {task_context[estimated_hours]}

## MANDATORY TDD PHASES (from roadmap)

Execute these 7 phases in order:
{format_tdd_phases(task_context[tdd_phases])}

## EXECUTION CONFIGURATION

{task_context[execution_config]}

## STATE TRACKING VIA execution-status.yaml

**CRITICAL**: DO NOT load roadmap.yaml (context provided above).
**READ/WRITE ONLY**: docs/feature/{project-id}/execution-status.yaml

Your responsibilities:
1. Load current state from execution-status.yaml
2. Resume from current phase (or start at PREPARE if new step)
3. Execute each phase in order
4. Update execution-status.yaml after EACH phase (no batching)
5. Track turn count for timeout monitoring
6. Update execution-status.yaml with outcomes

## CM-D: Walking Skeleton Principle

In PREPARE phase, verify: entry point exists, acceptance tests invoke entry point (not internal components), component wired into system. If tests import components directly → STOP, report wiring gap.

## INLINE REVIEW CRITERIA (Phase 4: REVIEW)

SOLID principles, coverage >80%, acceptance criteria met, no security vulnerabilities. Also validate post-refactoring quality: tests pass, quality improved, no new duplication. Record findings in execution-status.yaml.

## EXECUTION-STATUS.YAML STRUCTURE

```yaml
execution_status:
  current:
    step_id: "{step-id}"
    phase_index: 3  # Current phase (0-7)
    phase_name: "GREEN"
    started_at: "2026-01-29T15:00:00Z"
    turn_count: 12
  step_checkpoint:
    step_id: "{step-id}"
    phases:
      - phase_index: 0
        phase_name: "PREPARE"
        status: "COMPLETED"  # or IN_PROGRESS, SKIPPED
        outcome: "PASS"  # or FAIL
        duration_minutes: 10
        turn_count: 3
      # ... (7 phases total)
```

If you encounter issues:
- Update execution_status.current with failure reason
- Set can_retry appropriately
- Return error to orchestrator"
```

**Parameter Substitution**:
- Replace `{agent-name}` with the extracted agent name (e.g., "software-crafter")
- Replace `{project-id}` with the project ID (e.g., "des-us007-boundary-rules")
- Replace `{step-id}` with the step ID (e.g., "01-01")
- Replace `{task_context[...]}` with values from extracted context

### Agent Registry

Valid agents are: researcher, software-crafter, solution-architect, product-owner, acceptance-designer, devop

Note: This list is maintained in sync with the agent registry at `~/.claude/agents/nw/`. If you encounter "agent not found" errors, verify the agent is registered in that location.

Each agent has specific capabilities:
- **researcher**: Information gathering, analysis, documentation
- **software-crafter**: Implementation, testing, refactoring, code quality
- **solution-architect**: System design, architecture decisions, planning
- **product-owner**: Requirements, business analysis, stakeholder alignment
- **acceptance-designer**: Test definition, acceptance criteria, BDD
- **devop**: Deployment, operations, infrastructure, lifecycle management

### Example Invocations (NEW ARCHITECTURE)

**For researcher agent**:
```
Task: "You are the researcher agent.

Your specific role for this command: Execute atomic tasks with complete state tracking via execution-status.yaml

Task type: execute

PROJECT: auth-upgrade
STEP: 01-01

## TASK CONTEXT (EXTRACTED FROM ROADMAP - DO NOT LOAD ROADMAP)

[Orchestrator provides ~5k extracted context here]

[... rest of instructions ...]"
```

**For software-crafter agent**:
```
Task: "You are the software-crafter agent.

Your specific role for this command: Execute atomic tasks with complete state tracking via execution-status.yaml

Task type: execute

PROJECT: des-us007-boundary-rules
STEP: 02-01

## TASK CONTEXT (EXTRACTED FROM ROADMAP - DO NOT LOAD ROADMAP)

[Orchestrator provides ~5k extracted context here]

[... rest of instructions ...]"
```

### Error Handling (NEW ARCHITECTURE)

**Invalid Agent Name**:
- If agent name is not in the valid list, respond with error:
  "Invalid agent name: {name}. Must be one of: researcher, software-crafter, solution-architect, product-owner, acceptance-designer, devop"

**Missing Project Files**:
- If roadmap.yaml not found: "Roadmap not found at docs/feature/{project-id}/roadmap.yaml"
- If execution-status.yaml not found: "Execution status not found at docs/feature/{project-id}/execution-status.yaml"

**Step Not Found in Roadmap**:
- If step ID doesn't exist in roadmap: "Step {step-id} not found in roadmap. Available steps: {list_available_steps()}"

**Dependency Not Met**:
- If the invoked agent reports dependency failures, explain the blocking tasks to the user

---

## Overview

Executes a self-contained atomic task by invoking the specified agent with complete context from the step file. Manages state transitions, tracks execution progress, and updates the step file with results.

Designed to work with clean context, ensuring consistent quality by giving each agent a fresh start with all necessary information contained in the step file.

## Agent Instance Isolation Model (NEW ARCHITECTURE)

Each invocation of the Task tool creates a NEW, INDEPENDENT agent instance. The instance receives extracted context from orchestrator (~5k tokens), reads execution-status.yaml for prior progress, executes work, updates execution-status.yaml with results, and terminates. No session state is retained between invocations. State is preserved through execution-status.yaml, not through agent memory. The agent does NOT load the roadmap (orchestrator already extracted context). This isolation ensures clean execution without context degradation from previous instances.

## Usage Examples (NEW ARCHITECTURE - Schema v2.0)

```bash
# Execute a research task
/nw:execute @researcher "auth-upgrade" "01-01"

# Execute implementation task
/nw:execute @software-crafter "des-us007-boundary-rules" "02-01"

# Execute testing task
/nw:execute @devop "auth-upgrade" "04-01"

# Override the suggested agent
/nw:execute @solution-architect "des-us007-boundary-rules" "01-02"

# OLD SIGNATURE (DEPRECATED - DO NOT USE):
# /nw:execute @software-crafter "docs/feature/auth-upgrade/steps/01-01.json"
```

## Complete Workflow Integration

roadmap → split → execute (per step) → review → finalize. See respective command documentation.

## State Transitions

```
TODO → IN_PROGRESS → DONE
         ↓      ↓
      FAILED  IN_REVIEW
         ↓      ↓
      RETRY   REWORK
```

## Context Files Required (NEW ARCHITECTURE)

- `docs/feature/{project-id}/roadmap.yaml` - Loaded by orchestrator (schema v2.0)
- `docs/feature/{project-id}/execution-status.yaml` - Read/written by sub-agent (schema v1.0)
- Any files referenced in step's `deliverables` field

---

## Coordinator Success Criteria

Verify the coordinator performed these tasks:
- [ ] Agent name extracted from parameters correctly
- [ ] Agent name validated against known agents
- [ ] File path(s) extracted and validated
- [ ] Absolute path constructed correctly
- [ ] Pre-invocation validation checklist passed
- [ ] Task tool invocation prepared with correct parameters
- [ ] Task tool returned success status
- [ ] User received confirmation of agent invocation

## Agent Execution Success Criteria

The invoked agent must accomplish (Reference Only):
- [ ] Step file loaded successfully
- [ ] Dependencies verified as complete
- [ ] Agent invoked with full context
- [ ] State transitions properly recorded
- [ ] Execution results captured
- [ ] Step file updated with results
- [ ] State history maintained
- [ ] Metrics tracked for analysis

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

### State Management Across Instances (NEW ARCHITECTURE)

The executing agent does not have access to previous invocations' memory. All prior execution state (from previous agent instances) is captured in execution-status.yaml. The agent READS execution-status.yaml at start, sees what prior instances accomplished (via step_checkpoint.phases), continues from that point, and UPDATES execution-status.yaml with new results. This YAML-based state management allows clean handoff between instances without context pollution. The agent receives task context from orchestrator (~5k tokens) and does NOT load roadmap.yaml (102k tokens).

### MANDATORY: Phase Tracking Protocol (7 Phases - Schema v3.0)

The execution-status.yaml contains `step_checkpoint.phases` with 7 TDD phases (schema v3.0).
You MUST update each phase as you execute it. **DO NOT BATCH UPDATES** - save execution-status.yaml after each phase.

#### The 7 TDD Phases (Execute in Order) - Schema v3.0

**Single Source of Truth**: See `nWave/templates/step-tdd-cycle-schema.json` (schema v3.0)

The phases are (0-6):
0. **PREPARE** - Remove @skip decorators, verify only 1 scenario enabled
1. **RED_ACCEPTANCE** - Run acceptance test, expect FAIL for valid reason
2. **RED_UNIT** - Write failing unit tests before implementation
3. **GREEN** - Implement minimum code to pass all tests (combines GREEN_UNIT + GREEN_ACCEPTANCE validation)
4. **REVIEW** - Quality review: SOLID, coverage, acceptance criteria, post-refactoring quality (expanded scope)
5. **REFACTOR_CONTINUOUS** - Progressive refactoring: L1 (naming) + L2 (complexity) + L3 (organization). Fast-path: if GREEN produced <30 LOC, quick scan only (2-3 min).
6. **COMMIT** - Final validate + commit (absorbs FINAL_VALIDATE metadata checks)
   - **COMMIT phase MUST also record files_modified** in execution-status.yaml (see below)

**NOTE**: L4-L6 architecture refactoring has been moved to orchestrator Phase 2.25 (runs once after all steps complete).

**For non-ATDD steps** (research, infrastructure): Phases 1-4 may be pre-set to `SKIPPED` with `blocked_by: "NOT_APPLICABLE"`.

#### COMMIT Phase: files_modified Tracking (MANDATORY)

After creating the git commit, record files modified in execution-status.yaml:

1. Run: `git diff --name-only HEAD~1`
2. Categorize files:
   - **implementation**: files under `src/` or `lib/` (excluding `__init__.py`)
   - **tests**: files under `tests/`
3. Update execution-status.yaml `completed_steps` entry:
   ```yaml
   files_modified:
     implementation:
       - "src/des/templates/boundary_rules_template.py"
     tests:
       - "tests/des/unit/test_boundary_rules_template.py"
   ```

**Why**: This data is used by the orchestrator during mutation testing (Phase 2.5)
to discover the complete implementation scope. Without it, mutation testing may
miss implementation files, creating false confidence in test quality.

#### TDD Checkpoint Commit Strategy (Schema v3.0 - 7 Phases)

3 strategic checkpoints for rollback capability:

| Checkpoint | After Phase | Commit Prefix | Push? |
|------------|-------------|---------------|-------|
| 1. GREEN | 3 (GREEN) | `feat({step-id}): GREEN` | No |
| 2. REVIEW | 4 (REVIEW) | `review({step-id})` | No |
| 3. FINAL | 6 (COMMIT) | `feat({step-id}): DONE` | Yes |

**Each checkpoint**: Mark pending phases SKIPPED with `blocked_by: "CHECKPOINT_PENDING"`, commit execution-status.yaml + implementation, verify tests pass.

---

##### Checkpoint Rollback (NEW ARCHITECTURE)

`git reset HEAD~1` then edit execution-status.yaml: change completed phases back to SKIPPED with `blocked_by: "CHECKPOINT_PENDING"`, re-execute from that phase.

##### Checkpoint Rules (NEW ARCHITECTURE)

Use CHECKPOINT_PENDING (not DEFERRED), mark pending phases SKIPPED, push only after FINAL, update execution-status.yaml after each commit.

Instances read execution-status.yaml step_checkpoint.phases to understand prior progress, continue from incomplete phases. Before each phase: update entry to IN_PROGRESS with timestamp. After: update to COMPLETED/SKIPPED with outcome, duration, notes. Save execution-status.yaml after EACH phase (no batching).

#### If Phase Cannot Be Completed

If a phase cannot be completed for valid reasons:

```json
{
  "status": "SKIPPED",
  "blocked_by": "NOT_APPLICABLE: No unit tests required for documentation-only task"
}
```

**Valid SKIPPED Prefixes** (allow commit):
- `BLOCKED_BY_DEPENDENCY:` - External dependency unavailable
- `NOT_APPLICABLE:` - Phase not applicable for this task type
- `APPROVED_SKIP:` - Explicitly approved by reviewer

**Invalid SKIPPED Prefixes** (block commit):
- `DEFERRED:` - Indicates incomplete work that must be resolved

#### Phase History for Recovery

Each phase entry has a `history` array for tracking re-execution:

```json
{
  "phase_name": "GREEN_UNIT",
  "status": "EXECUTED",
  "history": [
    {
      "status": "EXECUTED",
      "outcome": "FAIL",
      "ended_at": "2024-01-15T10:20:00Z",
      "notes": "Initial attempt failed - edge case not handled"
    },
    {
      "status": "EXECUTED",
      "outcome": "PASS",
      "ended_at": "2024-01-15T10:35:00Z",
      "notes": "Fixed edge case, all tests passing"
    }
  ]
}
```

#### Phase Tracking Violations

These are CRITICAL violations that will cause the pre-commit hook to block commits:

- **Batching updates** - Saving step file only at the end instead of after each phase
- **Skipping phases** - Leaving phases as NOT_EXECUTED without valid blocked_by
- **Leaving IN_PROGRESS** - Phases left in IN_PROGRESS status indicate abandoned execution
- **Missing outcome** - EXECUTED phases must have outcome (PASS/FAIL)
- **Invalid SKIPPED reason** - SKIPPED without blocked_by or with DEFERRED prefix

#### Validation Before COMMIT Phase (Schema v2.0 - 8 Phases)

Before executing the COMMIT phase (phase 7), verify:
- [ ] All 7 previous phases (0-6) have status "COMPLETED" or valid "SKIPPED"
- [ ] No phase has status "IN_PROGRESS" or "NOT_EXECUTED"
- [ ] All COMPLETED phases have outcome field set
- [ ] All SKIPPED phases have blocked_by with valid prefix
- [ ] No SKIPPED phases have DEFERRED prefix (blocks commit)

```python
# Validation pseudo-code (NEW ARCHITECTURE)
for phase in execution_status["step_checkpoint"]["phases"]:
    if phase["status"] == "NOT_EXECUTED":
        ERROR: f"Phase {phase['phase_name']} not executed"
    elif phase["status"] == "IN_PROGRESS":
        ERROR: f"Phase {phase['phase_name']} left in progress"
    elif phase["status"] == "SKIPPED":
        if not phase.get("blocked_by"):
            ERROR: "SKIPPED without reason"
        if phase["blocked_by"].startswith("DEFERRED:"):
            ERROR: "DEFERRED phases block commit"
    elif phase["status"] == "COMPLETED":
        if not phase.get("outcome"):
            ERROR: "COMPLETED without outcome"
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
      "docs/feature/auth-upgrade/provider-selection.md"
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

### Integration with Other Commands (NEW ARCHITECTURE)

**Pre-execution Review** (roadmap review):
```bash
# Review roadmap before execution
/nw:review @software-crafter-reviewer roadmap "docs/feature/des-us007/roadmap.yaml"
# The review validates step definitions
# Execute steps after roadmap approved
/nw:execute @software-crafter "des-us007" "02-01"
```

**Post-execution Review** (implementation review):
```bash
# Execute task
/nw:execute @researcher "auth-upgrade" "01-01"
# Review implementation (checks execution-status.yaml for completion)
/nw:review @software-crafter-reviewer implementation "docs/feature/auth-upgrade/execution-status.yaml"
```

**Retry After Failure**:
```bash
# Initial attempt fails (orchestrator detects via execution-status.yaml)
/nw:execute @software-crafter "des-us007" "03-01"
# Fix issues, retry (agent resumes from last completed phase)
/nw:execute @software-crafter "des-us007" "03-01"
```

**OLD INTEGRATION PATTERN (DEPRECATED)**:
```bash
# ❌ DO NOT USE - step files no longer exist
/nw:execute @software-crafter "steps/02-01.json"
```

## Output Artifacts (NEW ARCHITECTURE)

- Updated execution-status.yaml with phase completion tracking
- Any outputs specified in acceptance criteria (deliverables)
- Git commits at TDD checkpoints (GREEN, REVIEW, FINAL)
- Execution logs in `docs/feature/{project-id}/logs/{timestamp}-{step-id}.log` (optional)

## Notes

### Clean Context Execution

Each execution starts with a clean context, ensuring:
1. **No contamination** from previous tasks
2. **Consistent quality** across all executions
3. **Predictable behavior** regardless of execution order
4. **Maximum LLM performance** without context degradation

### Parallel Execution Support (NEW ARCHITECTURE)

**IMPORTANT**: With execution-status.yaml as single state file, parallel execution requires careful coordination to avoid conflicts. Each step updates the same execution-status.yaml file.

**Sequential execution recommended** (safest approach):
```bash
# Execute steps in dependency order
/nw:execute @researcher "auth-upgrade" "01-01"  # Wait for completion
/nw:execute @researcher "auth-upgrade" "01-02"  # Then execute next
/nw:execute @software-crafter "auth-upgrade" "02-01"  # Then execute next
```

**Parallel execution possible** (requires file locking):
```bash
# Only for truly independent steps with no shared dependencies
/nw:execute @researcher "auth-upgrade" "01-01" &
/nw:execute @researcher "auth-upgrade" "01-02" &
# WARNING: May cause execution-status.yaml write conflicts
```

**Note**: The old architecture used separate step files (parallel-safe). The new architecture uses shared execution-status.yaml (requires coordination). Trade-off accepted for 94% token reduction.

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
