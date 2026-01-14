# DW-SPLIT: Atomic Task Generation from Roadmap with TDD Cycle Embedding

## CRITICAL: Agent Invocation Protocol

**YOU ARE THE COORDINATOR** - Do NOT generate task files yourself. Your role is to dispatch to the appropriate agent.

### STEP 1: Extract Agent Parameter

Parse the first argument to extract the agent name:
- User provides: `/nw:split @devop "auth-upgrade"`
- Extract agent name: `devop` (remove @ prefix)
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

### STEP 3: Extract Project ID

Extract the second argument (project ID):
- Example: `"auth-upgrade"`
- This should match the project-id in the roadmap

### Parameter Parsing Rules

Apply these rules to ALL extracted parameters:
1. Strip leading and trailing whitespace
2. Remove surrounding quotes (single or double) if present
3. Validate parameter is non-empty after stripping
4. Reject if extra parameters provided beyond expected count

Example for split.md:
- Input: `/nw:split  @devop  "auth-upgrade"`
- After parsing:
  - agent_name = "devop" (whitespace trimmed)
  - project_id = "auth-upgrade" (quotes removed)
- Input: `/nw:split @devop "auth-upgrade" extra`
- Error: "Too many parameters. Expected 2, got 3"

### STEP 4: Pre-Invocation Validation Checklist

Before invoking Task tool, verify ALL items:
- [ ] Agent name extracted and validated (not empty)
- [ ] Agent name in valid agent list
- [ ] Agent availability confirmed
- [ ] Project ID extracted and non-empty
- [ ] Project ID in valid kebab-case format
- [ ] Parameters contain no secrets or credentials
- [ ] Parameters within reasonable bounds (e.g., < 500 chars)
- [ ] No user input still has surrounding quotes

**ONLY proceed to Task tool invocation if ALL items above are checked.**

If any check fails, return specific error and stop.

### STEP 5: Invoke Agent Using Task Tool

**MANDATORY**: Use the Task tool to invoke the specified agent. Do NOT attempt to generate task files yourself.

Invoke the Task tool with this exact pattern:

```
Task: "You are the {agent-name} agent.

Your specific role for this command: Decompose roadmaps into self-contained atomic task files

Task type: split

Generate atomic, self-contained task files from the roadmap for project: {project-id}

Your responsibilities:
1. Read the roadmap from: docs/feature/{project-id}/roadmap.yaml
2. Transform each step into a complete, atomic task file
3. Enrich each task with full context so it's self-contained
4. Ensure no task requires prior context or external knowledge
5. Map all dependencies between tasks
6. Generate JSON files for each task

WarningCRITICAL: DO NOT COMMIT FILES - REQUEST USER APPROVAL FIRST

Input: docs/feature/{project-id}/roadmap.yaml
Output: docs/feature/{project-id}/steps/*.json

Task File Schema (JSON):
- task_id: Phase-step number (e.g., '01-01')
- project_id: From roadmap
- execution_agent: Agent best suited for this task
- self_contained_context: Complete background, prerequisites, relevant files, technical context
- task_specification: Name, description, motivation, detailed_instructions, acceptance_criteria, estimated_hours
- dependencies: requires (task-ids), blocking (task-ids)
- state: status='TODO', assigned_to=null, timestamps
- tdd_cycle: **MANDATORY** - Pre-populated from template with ALL 14 phases in NOT_EXECUTED status (see embedded template below)
- quality_gates: TDD quality requirements
- phase_validation_rules: Commit acceptance rules

Folder Structure:
docs/feature/{project-id}/steps/
├── 01-01.json  (Phase 1, Step 1)
├── 01-02.json  (Phase 1, Step 2)
├── 02-01.json  (Phase 2, Step 1)
└── ...

Key Principles:
- Each file MUST be completely self-contained
- Include ALL context needed for execution
- No forward references to other steps
- Explicit dependency mapping
- Agent auto-selection based on task type

After generating files, show the user a summary and request approval before committing."
```

**Parameter Substitution**:
- Replace `{agent-name}` with the extracted agent name (e.g., "devop")
- Replace `{project-id}` with the project ID

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

**For devop splitting auth-upgrade roadmap**:
```
Task: "You are the devop agent.

Your specific role for this command: Decompose roadmaps into self-contained atomic task files

Task type: split

Generate atomic, self-contained task files from the roadmap for project: auth-upgrade

[... rest of instructions ...]"
```

**For solution-architect splitting microservices roadmap**:
```
Task: "You are the solution-architect agent.

Your specific role for this command: Decompose roadmaps into self-contained atomic task files

Task type: split

Generate atomic, self-contained task files from the roadmap for project: microservices-migration

[... rest of instructions ...]"
```

### Error Handling

**Invalid Agent Name**:
- If agent name is not in the valid list, respond with error:
  "Invalid agent name: {name}. Must be one of: researcher, software-crafter, solution-architect, product-owner, acceptance-designer, devop"

**Missing Project ID**:
- If project ID is not provided, respond with error:
  "Project ID is required. Usage: /nw:split @agent 'project-id'"

**Roadmap Not Found**:
- If roadmap file doesn't exist at expected path, respond with error:
  "Roadmap not found: docs/feature/{project-id}/roadmap.yaml. Please run /nw:roadmap first."

---

## Overview

Invokes an agent to parse a comprehensive roadmap and generate self-contained, atomic task files that sub-agents can execute independently without context degradation.

Each generated task file contains all information needed for completion, enabling parallel execution and preventing the accumulation of context that degrades LLM performance over long conversations.

## Usage Examples

```bash
# Split architecture roadmap into tasks
/nw:split @devop "microservices-migration"

# Split data pipeline roadmap
/nw:split @data-engineer "analytics-pipeline"

# Split refactoring roadmap
/nw:split @software-crafter "auth-refactor"
```

## Additional Parameters

### `--regenerate-step {step-id}` (Optional)

Regenerates a single step file after review rejection, incorporating feedback without affecting other approved steps.

**Usage**:
```bash
/nw:split @devop "{project-id}" --regenerate-step {step-id} --feedback "{feedback}"
```

**Purpose**:
- Regenerate rejected step file with reviewer feedback
- Preserve all other approved steps unchanged
- Part of automatic retry logic in `/nw:develop` orchestration

**Parameters**:
- `{step-id}`: Step identifier to regenerate (e.g., "01-02", "02-03")
- `--feedback "{feedback}"`: Rejection reason from review (required)

**Examples**:
```bash
# Regenerate step 01-02 with feedback
/nw:split @devop "auth-upgrade" --regenerate-step 01-02 --feedback "Missing acceptance criteria for error handling"

# Regenerate step 02-01 with technical feedback
/nw:split @software-crafter "shopping-cart" --regenerate-step 02-01 --feedback "Dependencies not specified - requires step 01-03"

# Regenerate step 01-05 with context feedback
/nw:split @solution-architect "microservices" --regenerate-step 01-05 --feedback "Self-contained context insufficient - missing architecture decisions from phase 1"
```

**Behavior**:
1. **Loads existing steps**: Reads all step files from `docs/feature/{project-id}/steps/`
2. **Preserves approved steps**: Keeps all steps except the one being regenerated
3. **Incorporates feedback**: Uses feedback to improve regenerated step
4. **Maintains consistency**: Ensures dependency references remain valid
5. **Updates single file**: Only writes the regenerated step file

**Integration with `/nw:develop` Orchestration**:

This parameter is automatically invoked during Phase 6 (Review Each Step File) when using `/nw:develop`:

```
Phase 6: Review Step Files
  ↓
Step 01-02 Review → REJECTED
  ↓
Automatic retry (attempt 1 of 2):
  Invoke: /nw:split @devop "{project-id}"
          --regenerate-step 01-02
          --feedback "{rejection-reason}"
  ↓
Re-review Step 01-02
  ↓
If approved → continue
If rejected → attempt 2
  ↓
If rejected after 2 attempts → STOP, manual intervention required
```

**Validation**:
- Step ID must exist in original roadmap
- Feedback must be non-empty
- Project directory must exist
- Other step files must be valid JSON

**Error Handling**:
```bash
# Invalid step ID
ERROR: Step 01-99 not found in roadmap

# Missing feedback
ERROR: --feedback parameter required when using --regenerate-step

# No existing steps
ERROR: No step files found in docs/feature/{project-id}/steps/
```

**Notes**:
- **Idempotent**: Can be called multiple times safely
- **Atomic**: Either completes fully or fails without partial updates
- **Context preservation**: Maintains self-contained context requirement
- **Review loop**: Part of 2-attempt retry strategy in orchestration

## Key Benefits

- **Context Preservation**: Each task is self-contained with all required information
- **Parallel Execution**: Sub-agents can work on tasks independently
- **Progress Tracking**: Individual task state management
- **Quality Consistency**: Each task starts from clean context
- **Scalability**: Handle complex projects without context overflow

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

- docs/feature/{project-id}/roadmap.yaml - Master roadmap document
- Must be created by DW-ROADMAP command first

---

## Coordinator Success Criteria

Verify the coordinator performed these tasks:
- [ ] Agent name extracted from parameters correctly
- [ ] Agent name validated against known agents
- [ ] Project ID extracted and validated
- [ ] Pre-invocation validation checklist passed
- [ ] Task tool invocation prepared with correct parameters
- [ ] Task tool returned success status
- [ ] User received confirmation of agent invocation

## Agent Execution Success Criteria

The invoked agent must accomplish (Reference Only):
- [ ] Roadmap.yaml successfully parsed
- [ ] Project folder structure created: `docs/feature/{project-id}/steps/`
- [ ] All JSON files are syntactically valid
- [ ] File names follow {phase:02d}-{step:02d}.json format
- [ ] All fields from roadmap preserved in JSON files
- [ ] Dependencies correctly mapped from roadmap
- [ ] ISO 8601 datetime format for timestamps
- [ ] Each file contains project_id reference
- [ ] No files committed without user approval

**Measurement Data Validation (REQUIRED):**

Before splitting, verify the source roadmap contains:
- [ ] Baseline metrics in measurement_gate section (or documented exception)
- [ ] Constraint impact analysis (if constraints mentioned)
- [ ] Rejected simple alternatives (if >3 phases)

**If validation fails:**
- DO NOT split the roadmap
- Return error: "Roadmap lacks measurement data. Run /nw:roadmap with --validate or add measurement_gate section."
- Suggest user complete Pre-Planning Measurement Gate

**Exception for process improvements:**
- If roadmap.measurement_gate.gate_type = "process_improvement"
- AND qualitative justification is provided
- Proceed with split (measurement gate not required for non-performance work)

---

## Agent Invocation (Reference Documentation)

The following section documents what the invoked agent will do. **You (the coordinator) do not execute this - the agent does.**

### Primary Task Instructions

**CRITICAL: DO NOT COMMIT FILES - REQUEST APPROVAL FIRST**

**Task**: Transform roadmap into self-contained atomic task files

**Input**: `docs/feature/{project-id}/roadmap.yaml`
**Output**: `docs/feature/{project-id}/steps/*.json`

**Core Principle**: Each generated file must be **completely self-contained** so a sub-agent can execute it without any prior context or knowledge of other steps.

**Processing Steps:**
1. Parse the roadmap.yaml file
2. Extract and enrich each step with complete context
3. Ensure all dependencies are explicitly documented
4. Include all necessary background information
5. Generate atomic task files for sub-agent execution

**Generated Atomic Task Schema with TDD Cycle:**

Each file (`{phase:02d}-{step:02d}.json`) is a complete, executable unit with embedded TDD cycle:

```json
{
  "task_id": "{phase:02d}-{step:02d}",
  "project_id": "from-roadmap",
  "execution_agent": "auto-selected-or-specified",
  "self_contained_context": {
    "background": "Complete context for this specific task",
    "prerequisites_completed": ["List of completed dependencies"],
    "relevant_files": ["Files needed for this task"],
    "technical_context": "Any technical details required"
  },
  "task_specification": {
    "name": "from-roadmap-step",
    "description": "What needs to be done",
    "motivation": "Why this is important",
    "detailed_instructions": "Step-by-step guide with all needed info",
    "acceptance_criteria": ["Clear success conditions"],
    "estimated_hours": "from-roadmap"
  },
  "dependencies": {
    "requires": ["task-ids that must complete first"],
    "blocking": ["task-ids waiting for this"]
  },
  "state": {
    "status": "TODO",
    "assigned_to": null,
    "started_at": null,
    "completed_at": null,
    "updated": "current-timestamp",
    "tdd_phase": "NOT_STARTED",
    "tdd_phase_history": [],
    "review_attempts": 0,
    "refactor_level_completed": 0
  },
  "tdd_cycle": {
    "acceptance_test": {
      "scenario_name": "Business scenario from roadmap",
      "test_file": "tests/acceptance/Feature.feature",
      "test_file_format": "feature",
      "scenario_index": 0,
      "initially_ignored": true,
      "is_walking_skeleton": false
    },
    "expected_unit_tests": [],
    "mock_boundaries": {
      "allowed_ports": ["IOrderRepository", "IPaymentGateway"],
      "forbidden_domain_classes": ["Order", "Money", "Customer"],
      "in_memory_adapters": ["InMemoryOrderRepository"]
    }
  },
  "quality_gates": {
    "acceptance_test_must_fail_first": true,
    "unit_tests_must_fail_first": true,
    "no_mocks_inside_hexagon": true,
    "business_language_required": true,
    "refactor_level": 4,
    "in_memory_test_ratio_target": 0.8,
    "validation_after_each_review": true,
    "validation_after_each_refactor": true
  }
}
```

### TDD Cycle Template Embedding

**CRITICAL**: The TDD cycle section is embedded from template, NOT generated from scratch.

**Template Location**: `nWave/templates/step-tdd-cycle-schema.json`

**Template Content** (embedded at build time - DO NOT EDIT manually):

<!-- EMBED_START:nWave/templates/step-tdd-cycle-schema.json:markdown_code -->
<!-- EMBEDDED FROM: nWave/templates/step-tdd-cycle-schema.json -->
<!-- Generated by: tools/embed_sources.py -->
<!-- DO NOT EDIT BETWEEN MARKERS - changes will be overwritten -->

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "TDD Cycle Extension for Step Files",
  "description": "Template to embed in step JSON files during /nw:split compilation. This schema extends existing step files without overwriting their content.",
  "version": "2.0.0",
  "tdd_cycle": {
    "acceptance_test": {
      "scenario_name": "",
      "test_file": "",
      "test_file_format": "feature",
      "scenario_index": 0,
      "initially_ignored": true,
      "is_walking_skeleton": false
    },
    "expected_unit_tests": [],
    "mock_boundaries": {
      "allowed_ports": [],
      "forbidden_domain_classes": [],
      "in_memory_adapters": []
    },
    "tdd_phase_tracking": {
      "current_phase": "NOT_STARTED",
      "active_e2e_test": "",
      "inactive_e2e_tests": "All other @skip scenarios remain disabled",
      "phases_completed": []
    },
    "phase_execution_log": [
      {
        "phase_name": "PREPARE",
        "phase_index": 0,
        "status": "NOT_EXECUTED",
        "started_at": null,
        "ended_at": null,
        "duration_minutes": null,
        "outcome": null,
        "outcome_details": null,
        "artifacts_created": [],
        "artifacts_modified": [],
        "test_results": {"total": null, "passed": null, "failed": null, "skipped": null},
        "notes": null,
        "blocked_by": null,
        "history": []
      },
      {
        "phase_name": "RED_ACCEPTANCE",
        "phase_index": 1,
        "status": "NOT_EXECUTED",
        "started_at": null,
        "ended_at": null,
        "duration_minutes": null,
        "outcome": null,
        "outcome_details": null,
        "artifacts_created": [],
        "artifacts_modified": [],
        "test_results": {"total": null, "passed": null, "failed": null, "skipped": null},
        "notes": null,
        "blocked_by": null,
        "history": []
      },
      {
        "phase_name": "RED_UNIT",
        "phase_index": 2,
        "status": "NOT_EXECUTED",
        "started_at": null,
        "ended_at": null,
        "duration_minutes": null,
        "outcome": null,
        "outcome_details": null,
        "artifacts_created": [],
        "artifacts_modified": [],
        "test_results": {"total": null, "passed": null, "failed": null, "skipped": null},
        "notes": null,
        "blocked_by": null,
        "history": []
      },
      {
        "phase_name": "GREEN_UNIT",
        "phase_index": 3,
        "status": "NOT_EXECUTED",
        "started_at": null,
        "ended_at": null,
        "duration_minutes": null,
        "outcome": null,
        "outcome_details": null,
        "artifacts_created": [],
        "artifacts_modified": [],
        "test_results": {"total": null, "passed": null, "failed": null, "skipped": null},
        "notes": null,
        "blocked_by": null,
        "history": []
      },
      {
        "phase_name": "CHECK_ACCEPTANCE",
        "phase_index": 4,
        "status": "NOT_EXECUTED",
        "started_at": null,
        "ended_at": null,
        "duration_minutes": null,
        "outcome": null,
        "outcome_details": null,
        "artifacts_created": [],
        "artifacts_modified": [],
        "test_results": {"total": null, "passed": null, "failed": null, "skipped": null},
        "notes": null,
        "blocked_by": null,
        "history": []
      },
      {
        "phase_name": "GREEN_ACCEPTANCE",
        "phase_index": 5,
        "status": "NOT_EXECUTED",
        "started_at": null,
        "ended_at": null,
        "duration_minutes": null,
        "outcome": null,
        "outcome_details": null,
        "artifacts_created": [],
        "artifacts_modified": [],
        "test_results": {"total": null, "passed": null, "failed": null, "skipped": null},
        "notes": null,
        "blocked_by": null,
        "history": []
      },
      {
        "phase_name": "REVIEW",
        "phase_index": 6,
        "status": "NOT_EXECUTED",
        "started_at": null,
        "ended_at": null,
        "duration_minutes": null,
        "outcome": null,
        "outcome_details": null,
        "artifacts_created": [],
        "artifacts_modified": [],
        "test_results": {"total": null, "passed": null, "failed": null, "skipped": null},
        "notes": null,
        "blocked_by": null,
        "history": []
      },
      {
        "phase_name": "REFACTOR_L1",
        "phase_index": 7,
        "status": "NOT_EXECUTED",
        "started_at": null,
        "ended_at": null,
        "duration_minutes": null,
        "outcome": null,
        "outcome_details": null,
        "artifacts_created": [],
        "artifacts_modified": [],
        "test_results": {"total": null, "passed": null, "failed": null, "skipped": null},
        "notes": null,
        "blocked_by": null,
        "history": []
      },
      {
        "phase_name": "REFACTOR_L2",
        "phase_index": 8,
        "status": "NOT_EXECUTED",
        "started_at": null,
        "ended_at": null,
        "duration_minutes": null,
        "outcome": null,
        "outcome_details": null,
        "artifacts_created": [],
        "artifacts_modified": [],
        "test_results": {"total": null, "passed": null, "failed": null, "skipped": null},
        "notes": null,
        "blocked_by": null,
        "history": []
      },
      {
        "phase_name": "REFACTOR_L3",
        "phase_index": 9,
        "status": "NOT_EXECUTED",
        "started_at": null,
        "ended_at": null,
        "duration_minutes": null,
        "outcome": null,
        "outcome_details": null,
        "artifacts_created": [],
        "artifacts_modified": [],
        "test_results": {"total": null, "passed": null, "failed": null, "skipped": null},
        "notes": null,
        "blocked_by": null,
        "history": []
      },
      {
        "phase_name": "REFACTOR_L4",
        "phase_index": 10,
        "status": "NOT_EXECUTED",
        "started_at": null,
        "ended_at": null,
        "duration_minutes": null,
        "outcome": null,
        "outcome_details": null,
        "artifacts_created": [],
        "artifacts_modified": [],
        "test_results": {"total": null, "passed": null, "failed": null, "skipped": null},
        "notes": null,
        "blocked_by": null,
        "history": []
      },
      {
        "phase_name": "POST_REFACTOR_REVIEW",
        "phase_index": 11,
        "status": "NOT_EXECUTED",
        "started_at": null,
        "ended_at": null,
        "duration_minutes": null,
        "outcome": null,
        "outcome_details": null,
        "artifacts_created": [],
        "artifacts_modified": [],
        "test_results": {"total": null, "passed": null, "failed": null, "skipped": null},
        "notes": null,
        "blocked_by": null,
        "history": []
      },
      {
        "phase_name": "FINAL_VALIDATE",
        "phase_index": 12,
        "status": "NOT_EXECUTED",
        "started_at": null,
        "ended_at": null,
        "duration_minutes": null,
        "outcome": null,
        "outcome_details": null,
        "artifacts_created": [],
        "artifacts_modified": [],
        "test_results": {"total": null, "passed": null, "failed": null, "skipped": null},
        "notes": null,
        "blocked_by": null,
        "history": []
      },
      {
        "phase_name": "COMMIT",
        "phase_index": 13,
        "status": "NOT_EXECUTED",
        "started_at": null,
        "ended_at": null,
        "duration_minutes": null,
        "outcome": null,
        "outcome_details": null,
        "artifacts_created": [],
        "artifacts_modified": [],
        "test_results": {"total": null, "passed": null, "failed": null, "skipped": null},
        "notes": null,
        "blocked_by": null,
        "history": []
      }
    ]
  },
  "quality_gates": {
    "acceptance_test_must_fail_first": true,
    "unit_tests_must_fail_first": true,
    "no_mocks_inside_hexagon": true,
    "business_language_required": true,
    "refactor_level": 4,
    "in_memory_test_ratio_target": 0.8,
    "validation_after_each_phase": true,
    "validation_after_each_review": true,
    "validation_after_each_refactor": true,
    "all_14_phases_mandatory": true,
    "phase_documentation_required": true
  },
  "tdd_state": {
    "tdd_phase": "NOT_STARTED",
    "tdd_phase_history": [],
    "review_attempts": 0,
    "refactor_level_completed": 0
  },
  "phase_validation_rules": {
    "description": "Rules for validating phase execution status before commit",
    "all_phases_required": true,
    "total_phases": 14,
    "valid_statuses": ["NOT_EXECUTED", "IN_PROGRESS", "EXECUTED", "SKIPPED"],
    "commit_acceptance_matrix": {
      "EXECUTED": {
        "allows_commit": true,
        "requires_outcome": true,
        "description": "Phase completed successfully"
      },
      "SKIPPED": {
        "allows_commit": "conditional",
        "requires_blocked_by": true,
        "valid_blocked_by_prefixes": [
          "BLOCKED_BY_DEPENDENCY:",
          "NOT_APPLICABLE:",
          "APPROVED_SKIP:"
        ],
        "blocks_commit_prefixes": [
          "DEFERRED:"
        ],
        "description": "Phase skipped with documented reason"
      },
      "IN_PROGRESS": {
        "allows_commit": false,
        "description": "Phase started but not completed - indicates interrupted execution"
      },
      "NOT_EXECUTED": {
        "allows_commit": false,
        "description": "Phase not started - indicates skipped without justification"
      }
    },
    "skip_validation": {
      "description": "Validation rules for SKIPPED phases",
      "blocked_by_required": true,
      "valid_prefixes": {
        "BLOCKED_BY_DEPENDENCY:": {
          "allows_commit": true,
          "example": "BLOCKED_BY_DEPENDENCY: Redis server not running"
        },
        "NOT_APPLICABLE:": {
          "allows_commit": true,
          "example": "NOT_APPLICABLE: No unit tests for config-only change"
        },
        "APPROVED_SKIP:": {
          "allows_commit": true,
          "example": "APPROVED_SKIP: Tech Lead Alice approved"
        },
        "DEFERRED:": {
          "allows_commit": false,
          "example": "DEFERRED: Will address in follow-up PR",
          "note": "DEFERRED indicates incomplete work - blocks commit"
        }
      }
    },
    "sequential_order_required": true,
    "gaps_not_allowed": true,
    "atomic_file_writes": true
  },
  "merge_rules": {
    "description": "Rules for merging this template with existing step JSON files",
    "never_overwrite": [
      "task_id",
      "project_id",
      "execution_agent",
      "self_contained_context",
      "task_specification",
      "dependencies",
      "state.status",
      "state.assigned_to",
      "state.started_at",
      "state.completed_at",
      "state.updated"
    ],
    "always_add_if_missing": [
      "tdd_cycle",
      "tdd_cycle.phase_execution_log",
      "quality_gates",
      "tdd_state",
      "phase_validation_rules"
    ],
    "conflict_resolution": "existing_value_wins",
    "validation_after_merge": [
      "task_id matches filename pattern",
      "tdd_cycle.acceptance_test.scenario_name is non-empty",
      "tdd_cycle.phase_execution_log has exactly 14 entries",
      "quality_gates section present",
      "phase_validation_rules section present",
      "no null required fields"
    ]
  },
  "valid_tdd_phases": [
    "NOT_STARTED",
    "PREPARE",
    "RED_ACCEPTANCE",
    "RED_UNIT",
    "GREEN_UNIT",
    "CHECK_ACCEPTANCE",
    "GREEN_ACCEPTANCE",
    "REVIEW",
    "REFACTOR_L1",
    "REFACTOR_L2",
    "REFACTOR_L3",
    "REFACTOR_L4",
    "POST_REFACTOR_REVIEW",
    "FINAL_VALIDATE",
    "COMMIT",
    "COMPLETED"
  ],
  "valid_transitions": {
    "NOT_STARTED": ["PREPARE"],
    "PREPARE": ["RED_ACCEPTANCE"],
    "RED_ACCEPTANCE": ["RED_UNIT", "PREPARE"],
    "RED_UNIT": ["GREEN_UNIT"],
    "GREEN_UNIT": ["CHECK_ACCEPTANCE"],
    "CHECK_ACCEPTANCE": ["RED_UNIT", "GREEN_ACCEPTANCE"],
    "GREEN_ACCEPTANCE": ["REVIEW"],
    "REVIEW": ["REFACTOR_L1", "REVIEW"],
    "REFACTOR_L1": ["REFACTOR_L2"],
    "REFACTOR_L2": ["REFACTOR_L3"],
    "REFACTOR_L3": ["REFACTOR_L4"],
    "REFACTOR_L4": ["POST_REFACTOR_REVIEW"],
    "POST_REFACTOR_REVIEW": ["FINAL_VALIDATE", "REFACTOR_L1"],
    "FINAL_VALIDATE": ["COMMIT"],
    "COMMIT": ["COMPLETED"]
  },
  "failure_classification": {
    "valid_red": [
      "ASSERTION_FAILED",
      "EXPECTED_EXCEPTION_NOT_THROWN"
    ],
    "invalid_red": [
      "COMPILATION_ERROR",
      "RUNTIME_NULL_REFERENCE",
      "MISSING_DEPENDENCY",
      "TIMEOUT",
      "TEST_FRAMEWORK_ERROR"
    ],
    "acceptance_valid_failures": [
      "BUSINESS_LOGIC_NOT_IMPLEMENTED",
      "MISSING_ENDPOINT",
      "MISSING_UI_ELEMENT"
    ],
    "acceptance_invalid_failures": [
      "DATABASE_CONNECTION_FAILED",
      "TEST_DRIVER_TIMEOUT",
      "EXTERNAL_SERVICE_UNREACHABLE"
    ]
  },
  "test_file_formats": {
    "feature": {
      "ignore_syntax": "@ignore",
      "file_extension": ".feature",
      "framework": "Cucumber/SpecFlow/Behave"
    },
    "cs_nunit": {
      "ignore_syntax": "[Ignore(\"...\")]",
      "file_extension": ".cs",
      "framework": "NUnit"
    },
    "cs_xunit": {
      "ignore_syntax": "[Fact(Skip = \"...\")]",
      "file_extension": ".cs",
      "framework": "xUnit"
    },
    "py_pytest": {
      "ignore_syntax": "@pytest.mark.skip",
      "file_extension": ".py",
      "framework": "pytest"
    },
    "js_jest": {
      "ignore_syntax": "test.skip()",
      "file_extension": ".js",
      "framework": "Jest"
    },
    "java_junit5": {
      "ignore_syntax": "@Disabled",
      "file_extension": ".java",
      "framework": "JUnit 5"
    }
  },
  "task_specification": {
    "commit_policy": "Commit ONLY after ALL 14 PHASES complete. AUTO-PUSH after commit.",
    "mandatory_phases": [
      "PREPARE - Remove @skip, verify only 1 scenario enabled",
      "RED (Acceptance) - Test must FAIL initially",
      "RED (Unit) - Write failing unit tests",
      "GREEN (Unit) - Implement minimum code to pass",
      "CHECK - Verify unit tests pass",
      "GREEN (Acceptance) - All tests PASS",
      "REVIEW - Execute /nw:review @software-crafter-reviewer (MANDATORY)",
      "REFACTOR L1 - Naming clarity",
      "REFACTOR L2 - Method extraction",
      "REFACTOR L3 - Class responsibilities",
      "REFACTOR L4 - Architecture patterns",
      "POST-REFACTOR REVIEW - Execute /nw:review again (MANDATORY)",
      "FINAL VALIDATE - Document full test results (MANDATORY)",
      "COMMIT - Commit with detailed message"
    ]
  }
}
```
<!-- EMBED_END:nWave/templates/step-tdd-cycle-schema.json -->

**Merge Algorithm**:

```
MERGE(existing_step, tdd_template):
  1. PRESERVE all existing fields from existing_step
  2. ADD tdd_cycle section from template (INCLUDING phase_execution_log)
  3. ADD quality_gates section from template
  4. ADD phase_validation_rules section from template
  5. ADD TDD state fields to state section
  6. IF conflict on field name:
     - existing_step value takes precedence
     - Log warning: "Field {name} conflict, keeping existing value"
  7. NEVER overwrite: task_id, project_id, task_specification, dependencies
  8. ALWAYS add: tdd_cycle, quality_gates, phase_validation_rules (if not present)
```

**Conflict Resolution Priority**:
1. User-defined values (highest)
2. Existing step schema values
3. TDD template defaults (lowest)

### Phase Pre-Population Rule (MANDATORY)

**CRITICAL**: Every generated step file MUST include the complete `phase_execution_log` with all 14 phases pre-populated with status `NOT_EXECUTED`.

This is **NON-NEGOTIABLE**. The agent executing the step cannot add phases - they must already exist. The agent can only UPDATE existing phase entries.

**14 Required Phases** (in order):
1. PREPARE (phase_index: 0)
2. RED_ACCEPTANCE (phase_index: 1)
3. RED_UNIT (phase_index: 2)
4. GREEN_UNIT (phase_index: 3)
5. CHECK_ACCEPTANCE (phase_index: 4)
6. GREEN_ACCEPTANCE (phase_index: 5)
7. REVIEW (phase_index: 6)
8. REFACTOR_L1 (phase_index: 7)
9. REFACTOR_L2 (phase_index: 8)
10. REFACTOR_L3 (phase_index: 9)
11. REFACTOR_L4 (phase_index: 10)
12. POST_REFACTOR_REVIEW (phase_index: 11)
13. FINAL_VALIDATE (phase_index: 12)
14. COMMIT (phase_index: 13)

**Each Phase Entry Schema**:
```json
{
  "phase_name": "PREPARE",
  "phase_index": 0,
  "status": "NOT_EXECUTED",
  "started_at": null,
  "ended_at": null,
  "duration_minutes": null,
  "outcome": null,
  "outcome_details": null,
  "artifacts_created": [],
  "artifacts_modified": [],
  "test_results": {"total": null, "passed": null, "failed": null, "skipped": null},
  "notes": null,
  "blocked_by": null,
  "history": []
}
```

**Post-Generation Verification**:
After generating each step file, verify:
- [ ] `phase_execution_log` exists in `tdd_cycle` section
- [ ] Exactly 14 entries present
- [ ] All entries have `status: "NOT_EXECUTED"`
- [ ] All entries have correct `phase_index` (0-13)
- [ ] All entries have correct `phase_name` matching the 14 required phases
- [ ] No duplicate phase names
- [ ] Sequential order matches phase_index

**If Verification Fails**:
- DO NOT create the step file
- Return error: "Step file generation failed: phase_execution_log validation error"
- Include specific issue (missing phases, wrong count, etc.)

### Step Generation Rules

1. **One Scenario = One Step**: Each step maps exactly ONE acceptance test scenario
2. **First Step Walking Skeleton**: Step 01-01 has `is_walking_skeleton: true`
3. **Test File Agnostic**: Supports .feature, .cs, .py, .js, etc.
4. **Mock Boundaries from Architecture**: Analyze docs/architecture to populate allowed_ports
5. **TDD Phase Tracking**: Initialize `tdd_phase: "NOT_STARTED"`

### Scenario-to-Step Mapping

```
Feature: Order Management
├── Scenario 1: Place new order     → Step 01-01 (is_walking_skeleton: true)
├── Scenario 2: Add item to order   → Step 01-02
├── Scenario 3: Calculate total     → Step 01-03
└── Scenario 4: Complete order      → Step 01-04
```

**Naming Convention**:
- `scenario_name`: Business description from feature file
- `test_file`: Path to acceptance test file
- `scenario_index`: 0-based index within test file

### 14-Phase TDD Enforcement

**CRITICAL**: All generated step files MUST include the 14-phase tracking structure, pre-populated at generation time.

**Phase Execution Requirements**:
1. Each phase MUST be pre-populated in `phase_execution_log` at step file creation (by /nw:split)
2. The executing agent can only UPDATE existing phase entries, not add new ones
3. `current_phase` must track progress through the 14 phases
4. Commit is BLOCKED until all 14 phases have status "EXECUTED" or valid "SKIPPED"
5. Pre-commit hook validates phase completeness before allowing commit
6. Each phase log entry fields:
   - `phase_name`: Name of the phase (e.g., "PREPARE", "RED_ACCEPTANCE")
   - `phase_index`: Sequential index (0-13)
   - `status`: "NOT_EXECUTED" | "IN_PROGRESS" | "EXECUTED" | "SKIPPED"
   - `started_at`: ISO 8601 timestamp when phase started
   - `ended_at`: ISO 8601 timestamp when phase completed
   - `duration_minutes`: Time spent in phase
   - `outcome`: "PASS" or "FAIL" (required for EXECUTED status)
   - `outcome_details`: Details if outcome is FAIL
   - `artifacts_created`: Files created during this phase
   - `artifacts_modified`: Files modified during this phase
   - `test_results`: Object with total/passed/failed/skipped counts
   - `notes`: Observations and decisions
   - `blocked_by`: Required if status is "SKIPPED" (must have valid prefix)
   - `history`: Array for tracking phase re-execution (recovery mechanism)

**Valid SKIPPED Prefixes** (allow commit):
- `BLOCKED_BY_DEPENDENCY:` - External dependency unavailable
- `NOT_APPLICABLE:` - Phase not applicable for this task
- `APPROVED_SKIP:` - Skip explicitly approved by reviewer

**Invalid SKIPPED Prefixes** (block commit):
- `DEFERRED:` - Indicates incomplete work, must be resolved before commit

**Phase Execution Log Example**:
```json
{
  "tdd_cycle": {
    "tdd_phase_tracking": {
      "current_phase": "GREEN (Acceptance)",
      "active_e2e_test": "Place new order - 01-01",
      "inactive_e2e_tests": "All other @skip scenarios remain disabled",
      "phases_completed": ["PREPARE", "RED (Acceptance)", "RED (Unit)", "GREEN (Unit)", "CHECK", "GREEN (Acceptance)"],
      "phase_execution_log": [
        {
          "phase_name": "PREPARE",
          "timestamp": "2024-01-15T10:00:00Z",
          "duration_minutes": 5,
          "outcome": "PASS",
          "notes": "Removed @skip from scenario 'Place new order', verified all other scenarios disabled",
          "artifacts": ["tests/acceptance/order_management.feature"],
          "validation_result": "1 scenario enabled, 3 scenarios skipped"
        },
        {
          "phase_name": "RED (Acceptance)",
          "timestamp": "2024-01-15T10:05:00Z",
          "duration_minutes": 3,
          "outcome": "PASS",
          "notes": "Acceptance test fails as expected - OrderService not implemented",
          "artifacts": [],
          "validation_result": "Test failed with: 'OrderService' is not defined"
        },
        {
          "phase_name": "RED (Unit)",
          "timestamp": "2024-01-15T10:08:00Z",
          "duration_minutes": 12,
          "outcome": "PASS",
          "notes": "Written 3 unit tests for OrderService.PlaceOrder - all failing as expected",
          "artifacts": ["tests/unit/OrderServiceTests.cs"],
          "validation_result": "3 tests failing with NotImplementedException"
        },
        {
          "phase_name": "GREEN (Unit)",
          "timestamp": "2024-01-15T10:20:00Z",
          "duration_minutes": 18,
          "outcome": "PASS",
          "notes": "Implemented minimum OrderService logic to pass all unit tests",
          "artifacts": ["src/OrderService.cs"],
          "validation_result": "3/3 unit tests passing"
        },
        {
          "phase_name": "CHECK",
          "timestamp": "2024-01-15T10:38:00Z",
          "duration_minutes": 2,
          "outcome": "PASS",
          "notes": "Verified all unit tests still passing",
          "artifacts": [],
          "validation_result": "3/3 unit tests passing"
        },
        {
          "phase_name": "GREEN (Acceptance)",
          "timestamp": "2024-01-15T10:40:00Z",
          "duration_minutes": 5,
          "outcome": "PASS",
          "notes": "Acceptance test now passes - order placement working end-to-end",
          "artifacts": [],
          "validation_result": "1/1 acceptance test passing, 3/3 unit tests passing"
        }
      ]
    }
  }
}
```

**14-Phase Command Mapping**:

Each step file generated by `/nw:split` is designed to be executed through the 14-phase TDD workflow using `/nw:develop` and related commands:

| Phase | Phase Name | Command | Invoked By |
|-------|------------|---------|------------|
| 0 | PREPARE | Internal TDD loop | `/nw:develop {feature} --step {step-id}` |
| 1 | RED_ACCEPTANCE | Internal TDD loop | `/nw:develop {feature} --step {step-id}` |
| 2 | RED_UNIT | Internal TDD loop | `/nw:develop {feature} --step {step-id}` |
| 3 | GREEN_UNIT | Internal TDD loop | `/nw:develop {feature} --step {step-id}` |
| 4 | CHECK_ACCEPTANCE | Internal TDD loop | `/nw:develop {feature} --step {step-id}` |
| 5 | GREEN_ACCEPTANCE | Internal TDD loop | `/nw:develop {feature} --step {step-id}` |
| 6 | REVIEW | Explicit invocation | `/nw:review @software-crafter-reviewer implementation {step-file}` |
| 7 | REFACTOR_L1 | Explicit invocation | `/nw:refactor --level 1` |
| 8 | REFACTOR_L2 | Explicit invocation | `/nw:refactor --level 2` |
| 9 | REFACTOR_L3 | Explicit invocation | `/nw:refactor --level 3` |
| 10 | REFACTOR_L4 | Explicit invocation | `/nw:refactor --level 4` OR `/nw:mikado --goal "{goal}"` |
| 11 | POST_REFACTOR_REVIEW | Explicit invocation | `/nw:review @software-crafter-reviewer refactored_implementation {step-file}` |
| 12 | FINAL_VALIDATE | Internal TDD loop | `/nw:develop {feature} --step {step-id}` |
| 13 | COMMIT | Explicit git commit | `git commit -m "feat({feature}): {scenario} - step {step-id}"` |

**NOTE**: Pre-commit hook validates all 14 phases before allowing commit. The hook is installed in the target project by `/nw:develop`.

**Alternative: Fully Automated Execution**:

Instead of manually invoking each phase, use:
```bash
/nw:execute @software-crafter "{step-file}"
```

This will automatically:
- Execute phases 1-6, 10 through the TDD loop
- Invoke `/nw:review` for phases 7 and 9
- Invoke `/nw:refactor` or `/nw:mikado` for phase 8
- Commit for phase 11 if all validations pass

**Merge Algorithm Update**: When embedding the TDD template, ensure `tdd_phase_tracking` from `nWave/templates/step-tdd-cycle-schema.json` is included in the merged step file.

### Folder Structure Created:
```
docs/feature/
├── {project-id}/
│   ├── roadmap.yaml          # Source roadmap (already exists)
│   └── steps/                # Generated tracking files
│       ├── 01-01.json        # Phase 1, Step 1
│       ├── 01-02.json        # Phase 1, Step 2
│       ├── 02-01.json        # Phase 2, Step 1
│       └── ...
```

### Processing Logic:

1. **Context Enrichment**: For each step in roadmap:
   - Add complete background information
   - Include all technical context needed
   - List relevant files and resources
   - Document completed prerequisites

2. **Instruction Expansion**: Transform brief roadmap items into:
   - Detailed step-by-step instructions
   - Specific tool and command references
   - Clear output expectations
   - Concrete acceptance criteria

3. **Dependency Resolution**:
   - Map all inter-step dependencies
   - Identify which steps can run in parallel
   - Document blocking relationships

4. **Agent Assignment**:
   - Auto-select appropriate agent based on task type
   - Or use explicitly specified agent
   - Include agent-specific context

5. **File Generation**:
   - Create atomic JSON file per step
   - Ensure complete self-containment
   - No references requiring external context

## Output Artifacts

- Individual JSON tracking files in `docs/feature/{project-id}/steps/`
- Each file ready for state tracking and updates
- Consistent structure across all project steps

## Notes

### Context Degradation Prevention

This two-command system solves the critical problem of context degradation in long-running LLM conversations:

1. **DW-ROADMAP** → Expert agent creates comprehensive plan with full context
2. **DW-SPLIT** → Transforms plan into atomic, self-contained tasks

### Key Benefits of Atomic Task Architecture

**For Sub-Agents:**
- Start with clean context for each task
- No accumulated confusion from previous steps
- Consistent quality across all tasks
- Can execute in parallel without interference

**For Project Management:**
- Track progress at granular level
- Identify bottlenecks quickly
- Reassign tasks between agents easily
- Maintain audit trail of all changes

**For Quality:**
- Each task executed at peak LLM performance
- No context overflow errors
- Reduced hallucination risk
- Consistent output quality

### Implementation Flow

```
Goal → Expert Agent (ROADMAP) → Comprehensive Plan
                ↓
        Agent (SPLIT) → Atomic Tasks
                ↓
     Sub-Agents Execute Tasks (Clean Context Each Time)
```

This architecture enables complex projects to be completed with consistent quality, as each sub-agent operates at maximum effectiveness without the burden of accumulated context.
