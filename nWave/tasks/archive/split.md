# ARCHIVED: Obsolete in Schema v2.0

**Archive Date**: 2026-01-29
**Reason**: Step files eliminated in Schema v2.0 - execution tracking moved to execution-log.yaml
**Replacement**: Context extraction from roadmap.yaml directly in execute command

---

# DW-SPLIT: Atomic Task Generation from Roadmap with TDD Cycle Embedding

---
## ORCHESTRATOR INVOCATION PROTOCOL (MANDATORY)

**When YOU (orchestrator) delegate this command to an agent via Task tool:**

### CORRECT Pattern (minimal prompt):
```python
Task(
    subagent_type="software-crafter",
    prompt="Split: auth-upgrade (roadmap: docs/feature/auth-upgrade/roadmap.yaml)"
)
```

### Why This Works:
- ✅ Roadmap file contains ALL context (phases, steps, dependencies, acceptance_criteria)
- ✅ Software-crafter agent has internal knowledge of step-template.json (compact format)
- ✅ Agent knows complete TDD cycle structure (from canonical schema) and review criteria
- ✅ No conversation context needed

### WRONG Patterns (avoid):
```python
# ❌ Embedding step schema (agent already knows canonical schema)
Task(prompt="Split auth-upgrade. Use this step schema: [full schema JSON]")

# ❌ Listing 14 phases (agent has internal knowledge)
Task(prompt="Split auth-upgrade. Generate steps with 14 phases: PREPARE, RED_ACCEPTANCE...")

# ❌ Review criteria (agent knows phase 7 and 12 criteria)
Task(prompt="Split auth-upgrade. Include REVIEW checklist: SOLID, test coverage...")

# ❌ Any context from current conversation
Task(prompt="Split auth-upgrade. As we discussed, tier 2 tests are the bottleneck...")
```

### Key Principle:
**Command invocation = Project ID + Roadmap file path ONLY**

The roadmap file contains all phases/steps. Your prompt should not duplicate schema or phase details.

---

## AGENT PROMPT REINFORCEMENT (Command-Specific Guidance)

Reinforce command-specific principles extracted from THIS file (split.md):

### Recommended Prompt Template:
```python
Task(
    subagent_type="software-crafter",
    prompt="""Split: auth-upgrade (roadmap: docs/feature/auth-upgrade/roadmap.yaml)

CRITICAL (from split.md):
- Canonical schema: nWave/templates/step-tdd-cycle-schema.json (for validation)
- Compact template: nWave/templates/step-template.json (for generation)

**IMPORTANT: Use compact format:**
- `acceptance_criteria`: Use semicolon-separated string instead of array
  - Example: `"criterion 1; criterion 2; criterion 3"` (not `["criterion 1", "criterion 2"]`)
- This reduces file size and context consumption while maintaining clarity
- Each step MUST be self-contained (no forward references)
- Pre-populate ALL phases (from canonical schema) in phase_execution_log
- Step type determines which phases are NOT_APPLICABLE

AVOID:
- ❌ Using deprecated fields (step_id, phase_id, tdd_phase at top level)
- ❌ Generating fewer phases than canonical schema defines
- ❌ Forward references to later steps (breaks atomicity)
- ❌ Wrong phase names (must be UPPERCASE_UNDERSCORE like RED_ACCEPTANCE)"""
)
```

### Why Add This Guidance:
- **Source**: Extracted from split.md (not conversation context)
- **Deterministic**: Same principles every time you invoke split
- **Reinforcing**: Prevents schema violations and non-atomic steps
- **Token-efficient**: ~100 tokens vs broken step files

### What NOT to Add:
```python
# ❌ WRONG - This uses orchestrator's conversation context
Task(prompt="""Split: auth-upgrade

As we discussed, tier 2 tests are the bottleneck.
Make sure the steps address parallelization first.""")
```

---

## CRITICAL: Agent Invocation Protocol

**YOU ARE THE COORDINATOR** - Do NOT generate task files yourself. Your role is to dispatch to the appropriate agent.

### STEP 1: Extract Agent Parameter

Parse the first argument to extract the agent name:
- User provides: `/nw:split @software-crafter "auth-upgrade"`
- Extract agent name: `software-crafter` (remove @ prefix)
- Validate agent name is one of: software-crafter, researcher, solution-architect, product-owner, acceptance-designer, devop
- **Default/Recommended agent**: software-crafter (optimized for TDD step generation with 14-phase enforcement)

### STEP 2: Verify Agent Availability

Before proceeding to Task tool invocation:
- Verify the extracted agent name matches an available agent in the system
- Check agent is not at maximum concurrency
- Confirm agent type is compatible with this command

Valid agents: software-crafter (default), researcher, solution-architect, product-owner, acceptance-designer, devop

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
- Input: `/nw:split  @software-crafter  "auth-upgrade"`
- After parsing:
  - agent_name = "software-crafter" (whitespace trimmed)
  - project_id = "auth-upgrade" (quotes removed)
- Input: `/nw:split @software-crafter "auth-upgrade" extra`
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

## CRITICAL FIRST STEP - READ THE CANONICAL SCHEMA

**BEFORE generating ANY step file, you MUST:**
1. Read the canonical schema: `~/.claude/templates/step-tdd-cycle-schema.json` (or from repo: `nWave/templates/step-tdd-cycle-schema.json`)
2. Use the EXACT structure from that schema - do NOT invent your own format
3. Copy the `tdd_cycle.phase_execution_log` array with all phases (from canonical schema)

## MANDATORY TDD CYCLE STRUCTURE

{{SCHEMA_TDD_PHASES}}

**NOTE**: Self-review phases use inline criteria because agents cannot invoke /nw:review

## WRONG FORMATS TO REJECT - DO NOT USE THESE

❌ NEVER use 'step_id' - use 'task_id' instead
❌ NEVER use 'phase_id' - each step has all phases (see canonical schema)
❌ NEVER use 'tdd_phase' at top level - use 'tdd_cycle.phase_execution_log' array
❌ NEVER use phase names with parentheses like 'RED (Acceptance)' - use 'RED_ACCEPTANCE'
❌ NEVER use phase names with spaces like 'REFACTOR L1' - use 'REFACTOR_L1'

## Your responsibilities:
1. READ THE CANONICAL SCHEMA FIRST (critical!)
2. Read the roadmap from: docs/feature/{project-id}/roadmap.yaml
3. Transform each step into a complete, atomic task file USING THE SCHEMA FORMAT
4. Enrich each task with full context so it's self-contained
5. Ensure no task requires prior context or external knowledge
6. Map all dependencies between tasks
7. Generate JSON files for each task
8. VALIDATE each file after writing: `python3 ~/.claude/scripts/validate_step_file.py <file>`

⚠️ CRITICAL: DO NOT COMMIT FILES - REQUEST USER APPROVAL FIRST

Input: docs/feature/{project-id}/roadmap.yaml
Output: docs/feature/{project-id}/steps/*.json

Task File Schema (JSON) - MUST MATCH CANONICAL SCHEMA:
- task_id: Phase-step number (e.g., '01-01') - NOT step_id!
- project_id: From roadmap
- step_type: From roadmap (atdd, research, infrastructure)
- execution_agent: Validated from roadmap's suggested_agent or auto-selected
- self_contained_context: **ENRICHED BY SPLIT** - Complete background, prerequisites, relevant files, technical context
- task_specification: Name, description, motivation, **detailed_instructions (GENERATED BY SPLIT)**, acceptance_criteria, estimated_hours
- dependencies: requires (task-ids), blocking (task-ids) - **EXPANDED BY SPLIT**
- state: status='TODO', assigned_to=null, timestamps
- tdd_cycle: **MANDATORY** - COPY FROM SCHEMA (nWave/templates/step-tdd-cycle-schema.json) with all phases in phase_execution_log
- quality_gates: TDD quality requirements
- phase_validation_rules: Commit acceptance rules

**Split Enrichment Responsibilities (COME - How to Execute):**
1. **self_contained_context**: Generate complete context including:
   - Background from project documentation
   - Prerequisites from completed dependencies
   - Relevant files discovered during analysis
   - Technical context from architecture docs

2. **detailed_instructions**: Expand roadmap description into:
   - Step-by-step execution guide
   - Specific commands and tools to use
   - Expected intermediate outputs
   - Verification checkpoints

3. **execution_agent**: Validate and finalize:
   - Verify suggested_agent is available
   - Auto-select based on step_type if not suggested
   - Default mapping: atdd→software-crafter, research→researcher, infrastructure→devop

4. **TDD phase status**: Configure based on step_type:
   - atdd: All phases NOT_EXECUTED
   - research/infrastructure: Phases 1-5 SKIPPED with NOT_APPLICABLE

Folder Structure:
docs/feature/{project-id}/steps/
├── 01-01.json  (Phase 1, Step 1)
├── 01-02.json  (Phase 1, Step 2)
├── 02-01.json  (Phase 2, Step 1)
└── ...

Key Principles:
- ALWAYS read canonical schema first
- Each file MUST be completely self-contained
- Include ALL context needed for execution
- No forward references to other steps
- Explicit dependency mapping
- Agent auto-selection based on task type
- VALIDATE each file after writing

After generating files, show the user a summary and request approval before committing."
```

**Parameter Substitution**:
- Replace `{agent-name}` with the extracted agent name (e.g., "software-crafter")
- Replace `{project-id}` with the project ID

### Agent Registry

Valid agents are: software-crafter (default), researcher, solution-architect, product-owner, acceptance-designer, devop

Note: This list is maintained in sync with the agent registry at `~/.claude/agents/nw/`. If you encounter "agent not found" errors, verify the agent is registered in that location.

Each agent has specific capabilities:
- **software-crafter** (default): Implementation, testing, refactoring, code quality, TDD step generation
- **researcher**: Information gathering, analysis, documentation
- **solution-architect**: System design, architecture decisions, planning
- **product-owner**: Requirements, business analysis, stakeholder alignment
- **acceptance-designer**: Test definition, acceptance criteria, BDD
- **devop**: Deployment, operations, infrastructure, lifecycle management

### Example Invocations

**For software-crafter splitting auth-upgrade roadmap** (recommended):
```
Task: "You are the software-crafter agent.

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
  "Invalid agent name: {name}. Must be one of: software-crafter, researcher, solution-architect, product-owner, acceptance-designer, devop"

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
# Split architecture roadmap into tasks (recommended: software-crafter)
/nw:split @software-crafter "microservices-migration"

# Split data pipeline roadmap
/nw:split @data-engineer "analytics-pipeline"

# Split refactoring roadmap
/nw:split @software-crafter "auth-refactor"
```

## Additional Parameters

### `--regenerate-step {step-id}` (Optional)

Regenerates single step file with feedback after review rejection. Used in `/nw:develop` automatic retry (max 2 attempts).

## Benefits

Self-contained tasks enable parallel execution, clean context per task, granular progress tracking.

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

### Self-Containment and Instance Isolation

Each step file is self-contained for FRESH agent instances with no prior context. Include ALL background: architecture, dependency outputs, business context, technical constraints.

**Processing**: Parse roadmap → Enrich with context → Document dependencies → Generate atomic task files.

**Generated Atomic Task Schema with TDD Cycle:**

Each file (`{phase:02d}-{step:02d}.json`) is a complete, executable unit with embedded TDD cycle:

```json
{
  "task_id": "{phase:02d}-{step:02d}",
  "project_id": "from-roadmap",
  "step_type": "atdd",  // or "research", "infrastructure"
  "execution_agent": "validated-from-suggested-or-auto-selected",
  "self_contained_context": {
    "background": "ENRICHED: Complete context from project docs and architecture",
    "prerequisites_completed": ["ENRICHED: Outputs from completed dependency steps"],
    "relevant_files": ["ENRICHED: Files discovered during codebase analysis"],
    "technical_context": "ENRICHED: Technical details from architecture docs"
  },
  "task_specification": {
    "name": "from-roadmap-step",
    "description": "From roadmap (COSA)",
    "motivation": "From roadmap",
    "detailed_instructions": "GENERATED BY SPLIT (COME): Step-by-step guide",
    "acceptance_criteria": ["From roadmap, may be expanded"],
    "estimated_hours": "from-roadmap"
  },
  "dependencies": {
    "requires": ["EXPANDED: task-ids with output artifacts listed"],
    "blocking": ["EXPANDED: task-ids with dependency reason"]
  },
  "state": {
    "status": "TODO",
    "assigned_to": null,
    "started_at": null,
    "completed_at": null,
    "updated": "current-timestamp"
  },
  "tdd_cycle": {
    "acceptance_test": {
      "scenario_name": "VALIDATED: from suggested_scenario or generated",
      "test_file": "VALIDATED: path confirmed to exist or marked pending",
      "test_file_format": "AUTO-DETECTED: feature|pytest|jest|nunit|xunit|junit5|none",
      "scenario_index": 0,
      "initially_ignored": true,
      "is_walking_skeleton": false
    },
    "expected_unit_tests": [],
    "mock_boundaries": {
      "allowed_ports": ["ANALYZED: from architecture docs"],
      "forbidden_domain_classes": ["ANALYZED: domain entities"],
      "in_memory_adapters": ["ANALYZED: available test adapters"]
    },
    "phase_execution_log": [
      // MANDATORY: All phases from canonical schema (copy from step-tdd-cycle-schema.json):
      // {{SCHEMA_PHASE_NAMES}}
      // For ATDD: all {{PHASE_COUNT}} phases with status "NOT_EXECUTED"
      // For research/infrastructure: phases 1-3 with status "SKIPPED", blocked_by "NOT_APPLICABLE:..."
    ]
  },
  "quality_gates": {
    "acceptance_test_must_fail_first": true,  // false for non-ATDD
    "unit_tests_must_fail_first": true,       // false for non-ATDD
    "no_mocks_inside_hexagon": true,
    "business_language_required": true,
    "refactor_level": 4,
    "in_memory_test_ratio_target": 0.8,
    "validation_after_each_review": true,
    "validation_after_each_refactor": true
  }
}
```

### MANDATORY: One Step = One Complete BDD Scenario

**DESIGN PRINCIPLE**: Each step file represents ONE COMPLETE BDD SCENARIO containing all phases from the TDD cycle (see canonical schema). Different steps are DIFFERENT SCENARIOS, NOT different phases of the same scenario.

**CORRECT**: Step 01-01 = Scenario A (all phases), Step 01-02 = Scenario B (all phases)
**WRONG**: Step 01-01 = Phase RED, Step 01-02 = Phase GREEN (THIS IS FUNDAMENTALLY WRONG)

### FORMAT VALIDATION - REJECT INVALID FILES

**BEFORE WRITING ANY STEP FILE**, validate it contains:

1. ✅ `"task_id"` (NOT `"step_id"` or `"phase_id"`)
2. ✅ `"tdd_cycle"` object with nested `"phase_execution_log"` array
3. ✅ `"phase_execution_log"` containing the exact phases from canonical schema
4. ✅ Each phase has `"phase_name"`, `"phase_index"`, `"status": "NOT_EXECUTED"`

**IMMEDIATELY REJECT files with these WRONG patterns:**

❌ `"tdd_phase": "RED"` at top level → WRONG (phases go in phase_execution_log)
❌ `"step_id"` instead of `"task_id"` → WRONG
❌ `"phase_id"` field → WRONG (this format doesn't exist)
❌ Missing `tdd_cycle.phase_execution_log` → WRONG
❌ Fewer phases than defined in canonical schema → WRONG

**If you generate a file with any of these patterns, DELETE IT and regenerate using the template below.**

**Instance Execution**: Multiple agent instances execute phases independently. Step JSON file is the only state mechanism.

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
        "status": "NOT_EXECUTED",
        "started_at": null,
        "ended_at": null,
        "outcome": null,
        "notes": null,
        "blocked_by": null,
        "turn_count": 0
      },
      {
        "phase_name": "RED_ACCEPTANCE",
        "status": "NOT_EXECUTED",
        "started_at": null,
        "ended_at": null,
        "outcome": null,
        "notes": null,
        "blocked_by": null,
        "turn_count": 0
      },
      {
        "phase_name": "RED_UNIT",
        "status": "NOT_EXECUTED",
        "started_at": null,
        "ended_at": null,
        "outcome": null,
        "notes": null,
        "blocked_by": null,
        "turn_count": 0
      },
      {
        "phase_name": "GREEN",
        "status": "NOT_EXECUTED",
        "started_at": null,
        "ended_at": null,
        "outcome": null,
        "notes": "Combines: GREEN_UNIT + CHECK_ACCEPTANCE + GREEN_ACCEPTANCE",
        "blocked_by": null,
        "turn_count": 0
      },
      {
        "phase_name": "REVIEW",
        "status": "NOT_EXECUTED",
        "started_at": null,
        "ended_at": null,
        "outcome": null,
        "notes": "Covers both implementation AND post-refactoring quality",
        "blocked_by": null,
        "turn_count": 0
      },
      {
        "phase_name": "REFACTOR_CONTINUOUS",
        "status": "NOT_EXECUTED",
        "started_at": null,
        "ended_at": null,
        "outcome": null,
        "notes": "Combines: L1 (naming) + L2 (complexity) + L3 (organization)",
        "blocked_by": null,
        "turn_count": 0
      },
      {
        "phase_name": "REFACTOR_L4",
        "status": "NOT_EXECUTED",
        "started_at": null,
        "ended_at": null,
        "outcome": null,
        "notes": "Architecture patterns (optional - use NOT_APPLICABLE or CHECKPOINT_PENDING for skip)",
        "blocked_by": null,
        "turn_count": 0
      },
      {
        "phase_name": "COMMIT",
        "status": "NOT_EXECUTED",
        "started_at": null,
        "ended_at": null,
        "outcome": null,
        "notes": "Absorbs FINAL_VALIDATE (metadata checks only)",
        "blocked_by": null,
        "turn_count": 0
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
  "valid_tdd_phases": [
    "NOT_STARTED",
    "PREPARE",
    "RED_ACCEPTANCE",
    "RED_UNIT",
    "GREEN",
    "REVIEW",
    "REFACTOR_CONTINUOUS",
    "REFACTOR_L4",
    "COMMIT",
    "COMPLETED"
  ],
  "valid_transitions": {
    "NOT_STARTED": ["PREPARE"],
    "PREPARE": ["RED_ACCEPTANCE"],
    "RED_ACCEPTANCE": ["RED_UNIT", "PREPARE"],
    "RED_UNIT": ["GREEN"],
    "GREEN": ["REVIEW"],
    "REVIEW": ["REFACTOR_CONTINUOUS", "REVIEW"],
    "REFACTOR_CONTINUOUS": ["REFACTOR_L4"],
    "REFACTOR_L4": ["COMMIT", "REFACTOR_CONTINUOUS"],
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
      "PREPARE - Remove @skip, verify scenario setup",
      "RED_ACCEPTANCE - Test must FAIL initially",
      "RED_UNIT - Write failing unit tests",
      "GREEN - Implement minimum code + verify acceptance",
      "REVIEW - Self-review: SOLID, coverage, acceptance criteria, refactoring (MANDATORY)",
      "REFACTOR_CONTINUOUS - Progressive refactoring: L1 (naming) + L2 (complexity) + L3 (organization)",
      "REFACTOR_L4 - Architecture patterns (OPTIONAL)",
      "COMMIT - Commit with detailed message"
    ]
  }
}
```
<!-- EMBED_END:nWave/templates/step-tdd-cycle-schema.json -->

**Merge**: Preserve existing fields, add tdd_cycle/quality_gates/phase_validation_rules from template. User-defined values take precedence.

### Phase Pre-Population Rule

Pre-populate complete `phase_execution_log` with all phases ({{PHASE_COUNT}} total) from canonical schema, status `NOT_EXECUTED`. Validate after generation: `python3 ~/.claude/scripts/validate_step_file.py --all docs/feature/{project-id}/steps/`

### Step Generation Rules

One scenario per step (ATDD), first step is walking skeleton, initialize all phases from canonical schema with `NOT_EXECUTED`, analyze architecture for mock boundaries, require integration step (CM-B).

---

## CM-B: Integration Step Requirement (MANDATORY)

**CRITICAL**: Every feature MUST have at least one step that wires the component into the system entry point.

### The Problem This Solves

A feature can have:
- 6 steps, all implementing component logic
- 6 acceptance tests, all passing
- 100% coverage

Yet remain NON-FUNCTIONAL because no step integrates the component into the system entry point.

### Validation Rule

```yaml
integration_step_requirement:
  rule: "At least one step must have step_type: integration or target entry point"

  step_types:
    feature:        # Normal feature step with acceptance test at driving port
    integration:    # REQUIRED: Wires component into system entry point
    research:       # Research/investigation (may lack acceptance test)
    infrastructure: # DB migrations, env config (may lack acceptance test)

  validation: |
    count = 0
    for step in roadmap.steps:
      if step.step_type == "integration" OR step.targets_entry_point:
        count += 1

    if count == 0:
      REJECT: "No integration step found - feature will not be wired into system"
```

### What Makes a Step an Integration Step

A step qualifies as `integration` if it:
1. Modifies the system entry point to call the new component
2. Wires component into existing workflow
3. Has acceptance test that invokes through entry point

**Example: Integration Step in Roadmap**

```yaml
steps:
  - step_id: "07-01"
    name: "Wire TemplateValidator into DESOrchestrator"
    step_type: "integration"  # <-- CRITICAL marker
    description: |
      Integrate TemplateValidator into DESOrchestrator.render_prompt()
      as a pre-invocation validation gate.
    acceptance_criteria:
      - "DESOrchestrator calls TemplateValidator.validate_prompt()"
      - "Invalid prompts are rejected before Task invocation"
      - "Validation errors are surfaced to user"
    suggested_scenario:
      test_file: "tests/acceptance/test_us002_template_validation.py"
      scenario_name: "test_orchestrator_rejects_invalid_prompt"
```

### Split Validation

Verify at least one step has `step_type: integration` or targets entry point. If none found, warn user to add integration step to wire component into system.

### Step Type Processing

**ATDD**: All phases from canonical schema enabled (status: NOT_EXECUTED). Validate `suggested_scenario` against test files.

**Research/Infrastructure**: Phases 1-3 (RED_ACCEPTANCE, RED_UNIT, GREEN) SKIPPED with blocked_by="NOT_APPLICABLE". Other phases enabled.

### Suggested Scenario Validation

Validate test_file existence, scenario_name/index match. If not found: warn and request user decision (create stub, update roadmap, or placeholder).

### Non-ATDD Step File Schema

For research/infrastructure steps, the generated JSON differs:

```json
{
  "task_id": "01-01",
  "project_id": "from-roadmap",
  "execution_agent": "researcher",
  "step_type": "research",
  "self_contained_context": {
    "background": "Complete context for this research task",
    "prerequisites_completed": [],
    "relevant_files": ["docs/requirements/", "existing-analysis.md"],
    "technical_context": "Research objectives and scope"
  },
  "task_specification": {
    "name": "Requirements Analysis",
    "description": "Analyze and document requirements",
    "motivation": "Why this research is needed",
    "detailed_instructions": "Step-by-step research guide",
    "acceptance_criteria": ["Output documents specified"],
    "estimated_hours": 4
  },
  "tdd_cycle": {
    "acceptance_test": {
      "scenario_name": "N/A - Research step",
      "test_file": "",
      "test_file_format": "none",
      "scenario_index": -1,
      "initially_ignored": true,
      "is_walking_skeleton": false
    },
    "phase_execution_log": [
      // All 8 phases from canonical schema
      // Research steps: phases 1-3 SKIPPED with blocked_by="NOT_APPLICABLE: Research step"
      // PREPARE, REVIEW, COMMIT remain NOT_EXECUTED
    ]
  }
}
```

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

### TDD Phase Enforcement

**All phases from canonical schema** pre-populated at generation. Agents UPDATE existing entries only. Commit blocked until all phases EXECUTED or valid SKIPPED. See canonical schema for phase structure.
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

**Phase Execution Log Example** (showing first 6 phases - all 14 required):

⚠️ **CRITICAL**: The `phase_execution_log` is at `tdd_cycle.phase_execution_log`, NOT nested inside `tdd_phase_tracking`.

```json
{
  "tdd_cycle": {
    "tdd_phase_tracking": {
      "current_phase": "GREEN",
      "active_e2e_test": "Place new order - 01-01",
      "inactive_e2e_tests": "All other @skip scenarios remain disabled",
      "phases_completed": ["PREPARE", "RED_ACCEPTANCE", "RED_UNIT", "GREEN"]
    },
    "phase_execution_log": [
      // Example: Phases 0-3 marked EXECUTED with timestamps, outcomes, artifacts
      // Phases 4-7 marked NOT_EXECUTED or SKIPPED (checkpoint pattern)
      // Complete structure: see canonical schema at nWave/templates/step-tdd-cycle-schema.json
    ]
  }
}
```

**Execution**: Steps execute via `/nw:execute @software-crafter "{step-file}"` using all phases from canonical schema. Pre-commit hook validates phase completion.

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

### Processing

Enrich roadmap steps with context, expand instructions, resolve dependencies, assign agents, generate self-contained JSON files.

## Output Artifacts

- Individual JSON tracking files in `docs/feature/{project-id}/steps/`
- Each file ready for state tracking and updates
- Consistent structure across all project steps

## Notes

Atomic tasks prevent context degradation - each agent starts fresh. Roadmap → Split → Execute with clean context per task.
