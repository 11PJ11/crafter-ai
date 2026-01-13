---
description: 'Generate atomic task files from roadmap [agent] [project-id]'
argument-hint: '[agent] [project-id] - Example: @devop "auth-upgrade"'
agent-activation:
  required: false
  agent-parameter: true
  agent-command: "*feature-split"
---

# DW-SPLIT: Atomic Task Generation from Roadmap with TDD Cycle Embedding

## CRITICAL: Agent Invocation Protocol

**YOU ARE THE COORDINATOR** - Do NOT generate task files yourself. Your role is to dispatch to the appropriate agent.

### STEP 1: Extract Agent Parameter

Parse the first argument to extract the agent name:
- User provides: `/dw:split @devop "auth-upgrade"`
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
- Input: `/dw:split  @devop  "auth-upgrade"`
- After parsing:
  - agent_name = "devop" (whitespace trimmed)
  - project_id = "auth-upgrade" (quotes removed)
- Input: `/dw:split @devop "auth-upgrade" extra`
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

Note: This list is maintained in sync with the agent registry at `~/.claude/agents/dw/`. If you encounter "agent not found" errors, verify the agent is registered in that location.

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
  "Project ID is required. Usage: /dw:split @agent 'project-id'"

**Roadmap Not Found**:
- If roadmap file doesn't exist at expected path, respond with error:
  "Roadmap not found: docs/feature/{project-id}/roadmap.yaml. Please run /dw:roadmap first."

---

## Overview

Invokes an agent to parse a comprehensive roadmap and generate self-contained, atomic task files that sub-agents can execute independently without context degradation.

Each generated task file contains all information needed for completion, enabling parallel execution and preventing the accumulation of context that degrades LLM performance over long conversations.

## Usage Examples

```bash
# Split architecture roadmap into tasks
/dw:split @devop "microservices-migration"

# Split data pipeline roadmap
/dw:split @data-engineer "analytics-pipeline"

# Split refactoring roadmap
/dw:split @software-crafter "auth-refactor"
```

## Additional Parameters

### `--regenerate-step {step-id}` (Optional)

Regenerates a single step file after review rejection, incorporating feedback without affecting other approved steps.

**Usage**:
```bash
/dw:split @devop "{project-id}" --regenerate-step {step-id} --feedback "{feedback}"
```

**Purpose**:
- Regenerate rejected step file with reviewer feedback
- Preserve all other approved steps unchanged
- Part of automatic retry logic in `/dw:develop` orchestration

**Parameters**:
- `{step-id}`: Step identifier to regenerate (e.g., "01-02", "02-03")
- `--feedback "{feedback}"`: Rejection reason from review (required)

**Examples**:
```bash
# Regenerate step 01-02 with feedback
/dw:split @devop "auth-upgrade" --regenerate-step 01-02 --feedback "Missing acceptance criteria for error handling"

# Regenerate step 02-01 with technical feedback
/dw:split @software-crafter "shopping-cart" --regenerate-step 02-01 --feedback "Dependencies not specified - requires step 01-03"

# Regenerate step 01-05 with context feedback
/dw:split @solution-architect "microservices" --regenerate-step 01-05 --feedback "Self-contained context insufficient - missing architecture decisions from phase 1"
```

**Behavior**:
1. **Loads existing steps**: Reads all step files from `docs/feature/{project-id}/steps/`
2. **Preserves approved steps**: Keeps all steps except the one being regenerated
3. **Incorporates feedback**: Uses feedback to improve regenerated step
4. **Maintains consistency**: Ensures dependency references remain valid
5. **Updates single file**: Only writes the regenerated step file

**Integration with `/dw:develop` Orchestration**:

This parameter is automatically invoked during Phase 6 (Review Each Step File) when using `/dw:develop`:

```
Phase 6: Review Step Files
  ↓
Step 01-02 Review → REJECTED
  ↓
Automatic retry (attempt 1 of 2):
  Invoke: /dw:split @devop "{project-id}"
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
/dw:roadmap @solution-architect "Migrate authentication system"

# Step 2: Decompose into atomic tasks
/dw:split @solution-architect "auth-migration"

# Step 3: Execute first research task
/dw:execute @researcher "docs/feature/auth-migration/steps/01-01.json"

# Step 4: Review before implementation
/dw:review @software-crafter task "docs/feature/auth-migration/steps/02-01.json"

# Step 5: Execute implementation
/dw:execute @software-crafter "docs/feature/auth-migration/steps/02-01.json"

# Step 6: Finalize when all tasks complete
/dw:finalize @devop "auth-migration"
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
- Return error: "Roadmap lacks measurement data. Run /dw:roadmap with --validate or add measurement_gate section."
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

**Template Location**: `5d-wave/templates/step-tdd-cycle-schema.json`

**Merge Algorithm**:

```
MERGE(existing_step, tdd_template):
  1. PRESERVE all existing fields from existing_step
  2. ADD tdd_cycle section from template
  3. ADD quality_gates section from template
  4. ADD TDD state fields to state section
  5. IF conflict on field name:
     - existing_step value takes precedence
     - Log warning: "Field {name} conflict, keeping existing value"
  6. NEVER overwrite: task_id, project_id, task_specification, dependencies
  7. ALWAYS add: tdd_cycle, quality_gates (if not present)
```

**Conflict Resolution Priority**:
1. User-defined values (highest)
2. Existing step schema values
3. TDD template defaults (lowest)

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

### 11-Phase TDD Enforcement

**CRITICAL**: All generated step files MUST include the 11-phase tracking structure.

**Phase Execution Requirements**:
1. Each phase must be documented in `phase_execution_log`
2. `current_phase` must track progress
3. Commit is BLOCKED until all 11 phases complete
4. Each phase log entry must include:
   - `phase_name`: Name of the phase (e.g., "RED (Acceptance)")
   - `timestamp`: ISO 8601 timestamp when phase started
   - `duration_minutes`: Time spent in phase
   - `outcome`: "PASS" or "FAIL"
   - `notes`: Observations and decisions
   - `artifacts`: Files created/modified
   - `validation_result`: For phases with validation

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

**11-Phase Command Mapping**:

Each step file generated by `/dw:split` is designed to be executed through the 11-phase TDD workflow using `/dw:develop` and related commands:

| Phase | Command | Invoked By |
|-------|---------|------------|
| 1. PREPARE | Internal TDD loop | `/dw:develop {feature} --step {step-id}` |
| 2. RED (Acceptance) | Internal TDD loop | `/dw:develop {feature} --step {step-id}` |
| 3. RED (Unit) | Internal TDD loop | `/dw:develop {feature} --step {step-id}` |
| 4. GREEN (Unit) | Internal TDD loop | `/dw:develop {feature} --step {step-id}` |
| 5. CHECK | Internal TDD loop | `/dw:develop {feature} --step {step-id}` |
| 6. GREEN (Acceptance) | Internal TDD loop | `/dw:develop {feature} --step {step-id}` |
| 7. REVIEW | Explicit invocation | `/dw:review @software-crafter-reviewer implementation {step-file}` |
| 8. REFACTOR | Explicit invocation | `/dw:refactor --level 4` OR `/dw:mikado --goal "{goal}"` |
| 9. POST-REFACTOR REVIEW | Explicit invocation | `/dw:review @software-crafter-reviewer refactored_implementation {step-file}` |
| 10. FINAL VALIDATE | Internal TDD loop | `/dw:develop {feature} --step {step-id}` |
| 11. COMMIT | Explicit git commit | `git commit -m "feat({feature}): {scenario} - step {step-id}"` |

**Alternative: Fully Automated Execution**:

Instead of manually invoking each phase, use:
```bash
/dw:execute @software-crafter "{step-file}"
```

This will automatically:
- Execute phases 1-6, 10 through the TDD loop
- Invoke `/dw:review` for phases 7 and 9
- Invoke `/dw:refactor` or `/dw:mikado` for phase 8
- Commit for phase 11 if all validations pass

**Merge Algorithm Update**: When embedding the TDD template, ensure `tdd_phase_tracking` from `5d-wave/templates/step-tdd-cycle-schema.json` is included in the merged step file.

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
