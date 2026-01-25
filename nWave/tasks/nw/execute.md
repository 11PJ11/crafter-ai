# DW-EXECUTE: Atomic Task Execution Engine

---
## ORCHESTRATOR INVOCATION PROTOCOL (MANDATORY)

**When YOU (orchestrator) delegate this command to an agent via Task tool:**

### CORRECT Pattern (minimal prompt):
```python
Task(
    subagent_type="software-crafter",
    prompt="Execute: docs/feature/auth-upgrade/steps/01-01.json"
)
```

### Why This Works:
- ✅ Step file contains ALL context (self_contained_context, acceptance_criteria, quality_gates)
- ✅ Agent has internal knowledge of 14-phase TDD
- ✅ No conversation context needed
- ✅ Deterministic execution

### WRONG Patterns (avoid):
```python
# ❌ Including acceptance criteria (already in step file)
Task(prompt="Execute step 01-01. Acceptance criteria: [long list from step file]")

# ❌ Listing 14 phases (agent already knows this)
Task(prompt="Execute using 14 phases: 1. PREPARE, 2. RED_ACCEPTANCE...")

# ❌ Boundary warnings (step file has phase_validation_rules)
Task(prompt="Execute 01-01. CRITICAL: Don't forget POST_REFACTOR_REVIEW!")

# ❌ Any context from current conversation
Task(prompt="Execute 01-01. As we discussed earlier, the SISTER constraint...")
```

### Key Principle:
**Command invocation = Step file path ONLY**

The step file is self-contained. Your prompt should not duplicate what's already in the file.

---

## AGENT PROMPT REINFORCEMENT (Command-Specific Guidance)

Reinforce command-specific principles extracted from THIS file (execute.md):

### Recommended Prompt Template:
```python
Task(
    subagent_type="software-crafter",
    prompt="""Execute: docs/feature/auth-upgrade/steps/01-01.json

CRITICAL (from execute.md):
- Save step file after EACH phase (no batching)
- Verify entry point wiring in PREPARE phase (Walking Skeleton - CM-D)
- DEFERRED blocks commit (use NOT_APPLICABLE or APPROVED_SKIP)
- Read canonical schema first: nWave/templates/step-tdd-cycle-schema.json

AVOID:
- ❌ Batching phase updates (causes incomplete state tracking)
- ❌ Skipping wiring check (features exist but don't work for users)
- ❌ Using DEFERRED: prefix (blocks commit)
- ❌ Leaving phases IN_PROGRESS (indicates abandoned execution)"""
)
```

### Why Add This Guidance:
- **Source**: Extracted from execute.md (not conversation context)
- **Deterministic**: Same principles every time you invoke execute
- **Reinforcing**: Prevents common boundary violations
- **Token-efficient**: ~100 tokens vs 1000s in rework

### What NOT to Add:
```python
# ❌ WRONG - This uses orchestrator's conversation context
Task(prompt="""Execute: 01-01.json

Based on our earlier analysis, the SISTER constraint affects 20% of tests.
The tier 2 tests at 532 seconds are the main bottleneck.
Focus on parallelization as we discussed.""")
```

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

### STEP 3: Extract Step File Path

Extract the second argument (step file path):
- Example: `"docs/feature/auth-upgrade/steps/01-01.json"`
- Ensure path is absolute or resolve relative to working directory

### Parameter Parsing Rules

Apply these rules to ALL extracted parameters:
1. Strip leading and trailing whitespace
2. Remove surrounding quotes (single or double) if present
3. Validate parameter is non-empty after stripping
4. Reject if extra parameters provided beyond expected count

Example for execute.md:
- Input: `/nw:execute  @researcher   "steps/01-01.json"`
- After parsing:
  - agent_name = "researcher" (whitespace trimmed)
  - step_file_path = "steps/01-01.json" (quotes removed)
- Input: `/nw:execute @researcher "steps/01-01.json" extra`
- Error: "Too many parameters. Expected 2, got 3"

### STEP 4: Pre-Invocation Validation Checklist

Before invoking Task tool, verify ALL items:
- [ ] Agent name extracted and validated (not empty)
- [ ] Agent name in valid agent list
- [ ] Agent availability confirmed
- [ ] All file paths are absolute (resolve relative paths to absolute)
- [ ] Referenced files exist and are readable
- [ ] Parameters contain no secrets or credentials
- [ ] Parameters within reasonable bounds (e.g., paths < 500 chars)
- [ ] No user input still has surrounding quotes

**ONLY proceed to Task tool invocation if ALL items above are checked.**

If any check fails, return specific error and stop.

### STEP 5: Invoke Agent Using Task Tool

**MANDATORY**: Use the Task tool to invoke the specified agent. Do NOT attempt to execute the task yourself.

Invoke the Task tool with this exact pattern:

```
Task: "You are the {agent-name} agent.

Your specific role for this command: Execute atomic tasks with complete state tracking and result capture

Task type: execute

Read and execute the atomic task specified in: {step-file-path}

## CRITICAL: READ THE CANONICAL SCHEMA FIRST

**BEFORE processing the step file:**
1. Read the canonical schema: `~/.claude/templates/step-tdd-cycle-schema.json` (or from repo: `nWave/templates/step-tdd-cycle-schema.json`)
2. Understand the exact structure expected for phase_execution_log updates
3. Validate the step file has the correct format before proceeding

## STEP FILE FORMAT REFERENCE

The step file follows the canonical schema. Key structure:
- task_id: The task identifier (e.g., '01-01') - NOT step_id!
- project_id: Project identifier
- self_contained_context: All background and context needed
- task_specification: What to do and acceptance criteria
- dependencies: Prerequisites (must already be complete)
- state: Current task state
- tdd_cycle.phase_execution_log: Array of 14 phases to track progress (MANDATORY)
- quality_gates: TDD quality requirements
- phase_validation_rules: Commit acceptance rules

## MANDATORY 14-PHASE TDD CYCLE

Each step file contains `tdd_cycle.phase_execution_log` with EXACTLY these 14 phases:
1. PREPARE - Remove @skip tags, verify scenario setup
2. RED_ACCEPTANCE - Run acceptance test, expect FAIL
3. RED_UNIT - Write failing unit tests
4. GREEN_UNIT - Implement minimum code to pass unit tests
5. CHECK_ACCEPTANCE - Verify unit implementation
6. GREEN_ACCEPTANCE - Run acceptance test, expect PASS
7. REVIEW - Perform self-review (see INLINE REVIEW CRITERIA below)
8. REFACTOR_L1 - Naming clarity improvements
9. REFACTOR_L2 - Method extraction
10. REFACTOR_L3 - Class responsibilities
11. REFACTOR_L4 - Architecture patterns
12. POST_REFACTOR_REVIEW - Perform post-refactor self-review (see INLINE REVIEW CRITERIA below)
13. FINAL_VALIDATE - Full test suite validation
14. COMMIT - Commit with detailed message

## CM-D: Walking Skeleton Principle

**CRITICAL**: Before implementing component logic, verify system wiring exists.

### Pre-Execution Wiring Check

In the **PREPARE** phase, before removing @skip tags, verify:

1. **Entry point exists** - The system entry point module exists (even if empty/stubbed)
2. **Acceptance test invokes entry point** - At least one acceptance test imports the entry point
3. **Wiring is present** - Component is called from entry point (or will be added in this step)

If acceptance tests directly import internal components instead of entry points, **STOP** and report:

```
WIRING CHECK FAILED

Issue: Acceptance test imports internal component directly
Evidence: from des.validator import TemplateValidator (should be from des.orchestrator)

Required Action:
- This step should add integration OR
- A prior step should have added integration

If no integration step exists in roadmap, this is a ROADMAP GAP that must be addressed.
```

### Why This Matters

A step that:
- Implements component logic
- Has acceptance tests passing
- But component is never called from entry point

...produces a feature that WORKS IN TESTS but DOESN'T WORK FOR USERS.

### Verification Commands

```bash
# Check what acceptance tests import
grep "^from\|^import" tests/acceptance/test_*.py | grep -v "pytest\|fixture"

# Verify entry point references component
grep "ComponentName" src/entry_point/*.py
```

## INLINE REVIEW CRITERIA (Phases 7 and 12)

Since agents cannot invoke /nw:review, perform self-review with these criteria:

### Phase 7 (REVIEW) Checklist:
- [ ] Implementation follows SOLID principles
- [ ] Test coverage is adequate (aim for >80%)
- [ ] Acceptance criteria from task_specification are met
- [ ] Code is readable and maintainable
- [ ] No obvious security vulnerabilities (OWASP Top 10)
- [ ] No hardcoded secrets or credentials

### Phase 12 (POST_REFACTOR_REVIEW) Checklist:
- [ ] Refactoring did not break existing tests
- [ ] Refactoring improved code quality (naming, structure)
- [ ] No new duplication introduced
- [ ] Architecture patterns applied correctly
- [ ] All tests still pass after refactoring

Record review findings in step file under `tdd_cycle.phase_execution_log[N].notes`

## Your responsibilities:
1. READ the canonical schema first
2. Load the step file and validate it has the correct 14-phase structure
3. Update state to IN_PROGRESS
4. Execute EACH PHASE in order, updating phase_execution_log as you go:
   - Set status: IN_PROGRESS while working, then EXECUTED or SKIPPED
   - Record duration_minutes, outcome, outcome_details, notes
5. Execute TDD checkpoint commits:
   - After phase 5 (GREEN_ACCEPTANCE): Mark phases 6-13 SKIPPED with CHECKPOINT_PENDING, commit
   - After phase 6 (REVIEW): Update phase 6 to EXECUTED, mark 7-13 SKIPPED, commit
   - After phase 10 (REFACTOR_L4): Update 7-10 to EXECUTED, mark 11-13 SKIPPED, commit
   - After phase 12 (FINAL_VALIDATE): Update 11-13 to EXECUTED, commit and push
6. Execute the task following the detailed_instructions
7. Validate all acceptance_criteria are met
8. Update state to DONE with execution_result
9. Update the step file with your results

## WRONG FORMATS TO REJECT

If you encounter these in the step file, STOP and report the error:
❌ 'step_id' instead of 'task_id'
❌ 'phase_id' at top level
❌ 'tdd_phase' at top level without 'tdd_cycle.phase_execution_log'
❌ Less than 14 phases in phase_execution_log
❌ Phase names with parentheses like 'RED (Acceptance)'
❌ Phase names with spaces like 'REFACTOR L1'

If you encounter issues:
- Update state to FAILED with failure_reason
- Include recovery_suggestions in execution_result
- Set can_retry appropriately

Commit the updated step file after execution."
```

**Parameter Substitution**:
- Replace `{agent-name}` with the extracted agent name (e.g., "researcher")
- Replace `{step-file-path}` with the absolute path to the step file

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

### Example Invocations

**For researcher agent**:
```
Task: "You are the researcher agent.

Your specific role for this command: Execute atomic tasks with complete state tracking and result capture

Task type: execute

Read and execute the atomic task specified in: /mnt/c/Repositories/Projects/nwave/docs/feature/auth-upgrade/steps/01-01.json

[... rest of instructions ...]"
```

**For software-crafter agent**:
```
Task: "You are the software-crafter agent.

Your specific role for this command: Execute atomic tasks with complete state tracking and result capture

Task type: execute

Read and execute the atomic task specified in: /mnt/c/Repositories/Projects/nwave/docs/feature/auth-upgrade/steps/02-01.json

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

## Overview

Executes a self-contained atomic task by invoking the specified agent with complete context from the step file. Manages state transitions, tracks execution progress, and updates the step file with results.

Designed to work with clean context, ensuring consistent quality by giving each agent a fresh start with all necessary information contained in the step file.

## Agent Instance Isolation Model

Each invocation of the Task tool creates a NEW, INDEPENDENT agent instance. The instance loads the step JSON file, reads all context and prior progress, executes work, updates the step file with results, and terminates. No session state is retained between invocations. State is preserved through the JSON step file, not through agent memory. This isolation ensures clean execution without context degradation from previous instances.

## Usage Examples

```bash
# Execute a research task
/nw:execute @researcher "docs/feature/auth-upgrade/steps/01-01.json"

# Execute implementation task
/nw:execute @software-crafter "docs/feature/auth-upgrade/steps/02-01.json"

# Execute testing task
/nw:execute @devop "docs/feature/auth-upgrade/steps/04-01.json"

# Override the suggested agent
/nw:execute @solution-architect "docs/feature/auth-upgrade/steps/01-02.json"
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

### State Management Across Instances

The executing agent does not have access to previous invocations' memory. All prior execution state (from previous agent instances) is captured in the step JSON file. The agent READS the complete step file at start, sees what prior instances accomplished (via phase_execution_log), continues from that point, and UPDATES the same step file with new results. This JSON-based state management allows clean handoff between instances without context pollution.

### MANDATORY: Phase Tracking Protocol

The step file contains a pre-populated `phase_execution_log` with all 14 TDD phases.
You MUST update each phase as you execute it. **DO NOT BATCH UPDATES** - save the step file after each phase.

#### The 14 TDD Phases (Execute in Order)

**Single Source of Truth**: See `nWave/templates/step-tdd-cycle-schema.json` → `task_specification.mandatory_phases`

The phases are (0-13):
`PREPARE` → `RED_ACCEPTANCE` → `RED_UNIT` → `GREEN_UNIT` → `CHECK_ACCEPTANCE` → `GREEN_ACCEPTANCE` → `REVIEW` → `REFACTOR_L1` → `REFACTOR_L2` → `REFACTOR_L3` → `REFACTOR_L4` → `POST_REFACTOR_REVIEW` → `FINAL_VALIDATE` → `COMMIT`

**For non-ATDD steps** (research, infrastructure): Phases 1-5 are pre-set to `SKIPPED` with `blocked_by: "NOT_APPLICABLE"`.

#### TDD Checkpoint Commit Strategy

The 14-phase TDD cycle supports **4 strategic checkpoint commits** for improved rollback capability and git history clarity:

##### Checkpoint 1: GREEN (After Phase 5 - GREEN_ACCEPTANCE)
**When**: All acceptance tests passing, implementation complete
**Phases Complete**: 0-5 (PREPARE through GREEN_ACCEPTANCE)
**Phases Pending**: 6-13 (REVIEW through COMMIT)

**Pre-Checkpoint Checklist**:
- [ ] All acceptance tests: PASS
- [ ] All unit tests: PASS
- [ ] Implementation meets acceptance criteria
- [ ] No failing tests

**Commit Message Template**:
```
feat({step-id}): GREEN - acceptance tests passing

- Implemented minimal solution for {feature-name}
- All acceptance tests: PASS ({X} scenarios)
- Unit tests: PASS ({Y} tests)

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
```

**Phase Log Actions**:
1. Mark phases 6-13 as SKIPPED with:
   ```json
   "blocked_by": "CHECKPOINT_PENDING: Will complete in REFACTOR checkpoint"
   ```
2. Commit implementation files + step file
3. **DO NOT PUSH** - checkpoint is local only

---

##### Checkpoint 2: REVIEW (After Phase 6 - REVIEW)
**When**: Self-review complete, SOLID principles verified
**Phases Complete**: 0-6 (PREPARE through REVIEW)
**Phases Pending**: 7-13 (REFACTOR_L1 through COMMIT)

**Pre-Checkpoint Checklist**:
- [ ] SOLID principles followed
- [ ] Test coverage >80% verified
- [ ] No security vulnerabilities (OWASP Top 10)
- [ ] Code readable and maintainable
- [ ] Acceptance criteria met

**Commit Message Template**:
```
review({step-id}): SOLID principles and coverage verified

Self-review checklist:
- ✅ SOLID principles followed
- ✅ Test coverage {Z%} (threshold: >80%)
- ✅ No security vulnerabilities
- ✅ Code readable and maintainable

All acceptance criteria met.

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
```

**Phase Log Actions**:
1. Mark phases 7-13 as SKIPPED with:
   ```json
   "blocked_by": "CHECKPOINT_PENDING: Will complete in REFACTOR checkpoint"
   ```
2. Commit reviewed code + step file
3. **DO NOT PUSH** - checkpoint is local only

---

##### Checkpoint 3: REFACTOR (After Phase 10 - REFACTOR_L4)
**When**: All 4 refactoring levels complete
**Phases Complete**: 0-10 (PREPARE through REFACTOR_L4)
**Phases Pending**: 11-13 (POST_REFACTOR_REVIEW through COMMIT)

**Pre-Checkpoint Checklist**:
- [ ] All tests still passing after refactoring
- [ ] L1 (Naming clarity) complete
- [ ] L2 (Method extraction) complete
- [ ] L3 (Class responsibilities) complete
- [ ] L4 (Architecture patterns) complete
- [ ] Code quality improved vs GREEN checkpoint

**Commit Message Template**:
```
refactor({step-id}): L4 architecture patterns applied

Refactoring progression:
- L1: Naming clarity (variables, methods, classes)
- L2: Method extraction (DRY, single responsibility)
- L3: Class responsibilities (cohesion, coupling)
- L4: Architecture patterns (hexagonal, SOLID)

All tests passing.

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
```

**Phase Log Actions**:
1. Update phases 6-10: SKIPPED → EXECUTED with outcomes
2. Mark phases 11-13 as SKIPPED with:
   ```json
   "blocked_by": "CHECKPOINT_PENDING: Will complete in FINAL checkpoint"
   ```
3. Commit refactored files + step file
4. **DO NOT PUSH** - checkpoint is local only

---

##### Checkpoint 4: FINAL (After Phase 12 - FINAL_VALIDATE)
**When**: All 14 phases complete, ready for merge
**Phases Complete**: 0-13 (ALL PHASES)
**Phases Pending**: None

**Pre-Checkpoint Checklist**:
- [ ] POST_REFACTOR_REVIEW: PASS
- [ ] FINAL_VALIDATE: All tests passing
- [ ] Coverage meets threshold (>80%)
- [ ] No test failures or warnings
- [ ] Step file completely updated

**Commit Message Template**:
```
test({step-id}): Full validation - READY FOR MERGE

TDD cycle complete:
- All 14 phases EXECUTED
- Acceptance tests: {X} passed
- Unit tests: {Y} passed
- Coverage: {Z%}

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
```

**Phase Log Actions**:
1. Update phases 11-13: SKIPPED → EXECUTED with outcomes
2. Commit final changes + step file
3. **PUSH TO REMOTE**: `git push origin {branch}`

---

##### CRITICAL: Checkpoint Rollback Procedure

If you need to rollback to a previous checkpoint:

**Rollback to GREEN from REVIEW**:
```bash
git reset HEAD~1  # Undo REVIEW commit

# Edit step file:
# - Phase 6: Change EXECUTED back to SKIPPED
# - Phases 7-13: Already SKIPPED (no change needed)
# - Update blocked_by: "CHECKPOINT_PENDING: Will complete in REVIEW checkpoint"

# Re-execute from phase 6 (REVIEW)
```

**Rollback to REVIEW from REFACTOR**:
```bash
git reset HEAD~1  # Undo REFACTOR commit

# Edit step file:
# - Phases 7-10: Change EXECUTED back to SKIPPED
# - Update blocked_by: "CHECKPOINT_PENDING: Will complete in REFACTOR checkpoint"

# Re-execute from phase 7 (REFACTOR_L1)
```

**Rollback to REFACTOR from FINAL**:
```bash
git reset HEAD~1  # Undo FINAL commit

# Edit step file:
# - Phases 11-13: Change EXECUTED back to SKIPPED
# - Update blocked_by: "CHECKPOINT_PENDING: Will complete in FINAL checkpoint"

# Re-execute from phase 11 (POST_REFACTOR_REVIEW)
```

---

##### WARNING: Common Mistakes

❌ **DO NOT** forget to mark pending phases as SKIPPED
   → Hook will block: "Phase REVIEW: NOT_EXECUTED"

❌ **DO NOT** push after GREEN, REVIEW, or REFACTOR checkpoints
   → Only FINAL checkpoint pushes

❌ **DO NOT** use DEFERRED: instead of CHECKPOINT_PENDING:
   → DEFERRED blocks commit, CHECKPOINT_PENDING allows it

❌ **DO NOT** manually edit git history after checkpoint
   → Phase log becomes inconsistent with commits

✅ **DO** verify all tests pass before each checkpoint
✅ **DO** update step file immediately after commit
✅ **DO** follow commit message templates for consistency

When an agent instance begins execution, it examines phase_execution_log to understand which phases completed in prior instances. Each log entry shows what prior instances accomplished. The current instance may CONTINUE from where the previous left off (if resuming an interrupted phase) or ADVANCE to the next incomplete phase. The phase log serves as a timeline of execution across all instances working on this step.

#### Before Starting a Phase

1. READ the step file
2. LOCATE the phase entry in `tdd_cycle.phase_execution_log` by `phase_name`
3. UPDATE the entry:
   ```json
   {
     "status": "IN_PROGRESS",
     "started_at": "2024-01-15T10:00:00Z"
   }
   ```
4. SAVE the step file (atomic write: temp file + rename)

#### After Completing a Phase

5. UPDATE the entry:
   ```json
   {
     "status": "EXECUTED",
     "ended_at": "2024-01-15T10:05:00Z",
     "duration_minutes": 5,
     "outcome": "PASS",
     "outcome_details": "Test failed as expected with NotImplementedException",
     "artifacts_created": ["tests/unit/OrderServiceTests.cs"],
     "artifacts_modified": [],
     "test_results": {
       "total": 3,
       "passed": 0,
       "failed": 3,
       "skipped": 0
     },
     "notes": "All 3 unit tests failing as expected - ready for GREEN"
   }
   ```
6. SAVE the step file IMMEDIATELY (before starting next phase)

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

#### Validation Before COMMIT Phase

Before executing the COMMIT phase, verify:
- [ ] All 13 previous phases have status "EXECUTED" or valid "SKIPPED"
- [ ] No phase has status "IN_PROGRESS" or "NOT_EXECUTED"
- [ ] All EXECUTED phases have outcome field set
- [ ] All SKIPPED phases have blocked_by with valid prefix
- [ ] No SKIPPED phases have DEFERRED prefix (blocks commit)

```python
# Validation pseudo-code
for phase in phase_execution_log:
    if phase.status == "NOT_EXECUTED":
        ERROR: "Phase {phase.phase_name} not executed"
    elif phase.status == "IN_PROGRESS":
        ERROR: "Phase {phase.phase_name} left in progress"
    elif phase.status == "SKIPPED":
        if not phase.blocked_by:
            ERROR: "SKIPPED without reason"
        if phase.blocked_by.startswith("DEFERRED:"):
            ERROR: "DEFERRED phases block commit"
    elif phase.status == "EXECUTED":
        if not phase.outcome:
            ERROR: "EXECUTED without outcome"
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

### Integration with Other Commands

**Pre-execution Review**:
```bash
# Review before execution
/nw:review @software-crafter task "steps/02-01.json"
# The review updates the step file with critiques
# Execute only if review.ready_for_execution = true
/nw:execute @software-crafter "steps/02-01.json"
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
/nw:execute @researcher "steps/01-01.json"
# Review implementation
/nw:review @product-owner implementation "steps/01-01.json"
```

**Retry After Failure**:
```bash
# Initial attempt fails
/nw:execute @data-engineer "steps/03-01.json"
# Update context and retry
/nw:execute @data-engineer "steps/03-01.json" --retry
```

## Output Artifacts

- Updated step file with execution results
- Any outputs specified in acceptance criteria
- Execution logs in `docs/feature/{project-id}/logs/{timestamp}-{task-id}.log`

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
/nw:execute @researcher "steps/01-01.json" &
/nw:execute @researcher "steps/01-02.json" &
/nw:execute @software-crafter "steps/02-01.json" &
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
