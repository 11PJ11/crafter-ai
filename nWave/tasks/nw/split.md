---
description: 'Generate atomic task files from roadmap [agent] [project-id] - Example:
  @software-crafter "auth-upgrade"'
argument-hint: '[agent] [project-id] - Example: @software-crafter "auth-upgrade"'
---

# /split Command

**Wave**: UNKNOWN
**Description**: Generate atomic task files from roadmap

**Primary Agents**: software_crafter
**Expected Outputs**: task_files

## Implementation
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
- ✅ Agent knows 8-phase TDD structure (schema v2.0) and review criteria
- ✅ No conversation context needed

### WRONG Patterns (avoid):
```python
# ❌ Embedding step schema (agent already knows canonical schema)
Task(prompt="Split auth-upgrade. Use this step schema: [full schema JSON]")

# ❌ Listing 8 phases (agent has internal knowledge)
Task(prompt="Split auth-upgrade. Generate steps with 8 phases: PREPARE, RED_ACCEPTANCE...")

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
- Pre-populate ALL 8 phases in phase_execution_log (schema v2.0)
- Step type determines which phases are NOT_APPLICABLE

AVOID:
- ❌ Using deprecated fields (step_id, phase_id, tdd_phase at top level)
- ❌ Generating < 8 phases (must have all 8, even if SKIPPED - schema v2.0)
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
- **Default/Recommended agent**: software-crafter (optimized for TDD step generation with 8-phase enforcement - schema v2.0)

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
3. Copy the `tdd_cycle.phase_execution_log` array with all 8 phases (schema v2.0)

## MANDATORY 8-PHASE TDD STRUCTURE (Schema v2.0)

Every step file MUST include `tdd_cycle.phase_execution_log` with EXACTLY these 8 phases (in order):

1. PREPARE - Remove @skip tags, verify scenario setup
2. RED_ACCEPTANCE - Run acceptance test, expect FAIL
3. RED_UNIT - Write failing unit tests
4. GREEN - Implement minimum code + verify acceptance (combines GREEN_UNIT + CHECK_ACCEPTANCE + GREEN_ACCEPTANCE)
5. REVIEW - Self-review: SOLID, coverage, acceptance criteria, refactoring quality (covers both implementation AND post-refactoring)
6. REFACTOR_CONTINUOUS - Progressive refactoring: L1 (naming) + L2 (complexity) + L3 (organization)
7. REFACTOR_L4 - Architecture patterns (OPTIONAL: can use CHECKPOINT_PENDING or NOT_APPLICABLE for skip)
8. COMMIT - Commit with detailed message (absorbs FINAL_VALIDATE metadata checks)

**NOTE**: Phase 5 (REVIEW) uses inline self-review criteria because agents cannot invoke /nw:review

## WRONG FORMATS TO REJECT - DO NOT USE THESE

❌ NEVER use 'step_id' - use 'task_id' instead
❌ NEVER use 'phase_id' - each step has ALL 8 phases
❌ NEVER use 'tdd_phase' at top level - use 'tdd_cycle.phase_execution_log' array
❌ NEVER use phase names with parentheses like 'RED (Acceptance)' - use 'RED_ACCEPTANCE'
❌ NEVER use phase names with spaces like 'REFACTOR L1' - use 'REFACTOR_L1'
❌ NEVER use legacy 14-phase names like 'GREEN_UNIT', 'CHECK_ACCEPTANCE', 'GREEN_ACCEPTANCE', 'POST_REFACTOR_REVIEW', 'FINAL_VALIDATE'

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
- tdd_cycle: **MANDATORY** - COPY FROM SCHEMA with 8 phases in phase_execution_log (schema v2.0)
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

Regenerates a single step file after review rejection, incorporating feedback without affecting other approved steps.

**Usage**:
```bash
/nw:split @software-crafter "{project-id}" --regenerate-step {step-id} --feedback "{feedback}"
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
/nw:split @software-crafter "auth-upgrade" --regenerate-step 01-02 --feedback "Missing acceptance criteria for error handling"

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
  Invoke: /nw:split @software-crafter "{project-id}"
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

### Self-Containment and Instance Isolation

Each generated step file is self-contained because it will be executed by a FRESH agent instance that has no prior context. The instance cannot ask 'what was in the previous file?' or reference session memory. Therefore, self_contained_context must include ALL background needed: architecture documents, dependency outputs, business context, technical constraints. The instance reads this file and has everything needed to execute completely independently.

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
      // MANDATORY: All 8 phases (copy from step-tdd-cycle-schema.json - schema v2.0):
      // PREPARE, RED_ACCEPTANCE, RED_UNIT, GREEN, REVIEW, REFACTOR_CONTINUOUS, REFACTOR_L4, COMMIT
      // For ATDD: all 8 phases with status "NOT_EXECUTED"
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

**DESIGN PRINCIPLE**: Each step file represents ONE COMPLETE BDD SCENARIO containing ALL 14 TDD phases. Different steps are DIFFERENT SCENARIOS, NOT different phases of the same scenario.

**CORRECT**: Step 01-01 = Scenario A (all 8 phases), Step 01-02 = Scenario B (all 8 phases)
**WRONG**: Step 01-01 = Phase RED, Step 01-02 = Phase GREEN (THIS IS FUNDAMENTALLY WRONG)

### FORMAT VALIDATION - REJECT INVALID FILES

**BEFORE WRITING ANY STEP FILE**, validate it contains:

1. ✅ `"task_id"` (NOT `"step_id"` or `"phase_id"`)
2. ✅ `"tdd_cycle"` object with nested `"phase_execution_log"` array
3. ✅ `"phase_execution_log"` containing EXACTLY 8 phase entries (schema v2.0)
4. ✅ Each phase has `"phase_name"`, `"phase_index"`, `"status": "NOT_EXECUTED"`

**IMMEDIATELY REJECT files with these WRONG patterns:**

❌ `"tdd_phase": "RED"` at top level → WRONG (phases go in phase_execution_log)
❌ `"step_id"` instead of `"task_id"` → WRONG
❌ `"phase_id"` field → WRONG (this format doesn't exist)
❌ Missing `tdd_cycle.phase_execution_log` → WRONG
❌ Less than 8 phases in phase_execution_log (schema v2.0) → WRONG

**If you generate a file with any of these patterns, DELETE IT and regenerate using the template below.**

**NOTE ON INSTANCE EXECUTION**: The step file generated by /nw:split will be executed by multiple independent agent instances (one per phase, or grouped phases). Each instance loads this JSON file completely, executes one or more phases, and updates phase_execution_log with detailed results. No instance shares context with another. The step file is the only mechanism connecting these instances.

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
  "schema_version": "2.0",
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
        "duration_seconds": null,
        "turn_count": 0,
        "outcome": null,
        "notes": null,
        "blocked_by": null,
        "extensions_granted": []
      },
      {
        "phase_name": "RED_ACCEPTANCE",
        "phase_index": 1,
        "status": "NOT_EXECUTED",
        "started_at": null,
        "ended_at": null,
        "duration_minutes": null,
        "duration_seconds": null,
        "turn_count": 0,
        "outcome": null,
        "notes": null,
        "blocked_by": null,
        "extensions_granted": []
      },
      {
        "phase_name": "RED_UNIT",
        "phase_index": 2,
        "status": "NOT_EXECUTED",
        "started_at": null,
        "ended_at": null,
        "duration_minutes": null,
        "duration_seconds": null,
        "turn_count": 0,
        "outcome": null,
        "notes": null,
        "blocked_by": null,
        "extensions_granted": []
      },
      {
        "phase_name": "GREEN",
        "phase_index": 3,
        "status": "NOT_EXECUTED",
        "started_at": null,
        "ended_at": null,
        "duration_minutes": null,
        "duration_seconds": null,
        "turn_count": 0,
        "outcome": null,
        "notes": "Combines implementation (GREEN_UNIT) + acceptance validation (GREEN_ACCEPTANCE). Green acceptance is consequence of green unit.",
        "blocked_by": null,
        "extensions_granted": []
      },
      {
        "phase_name": "REVIEW",
        "phase_index": 4,
        "status": "NOT_EXECUTED",
        "started_at": null,
        "ended_at": null,
        "duration_minutes": null,
        "duration_seconds": null,
        "turn_count": 0,
        "outcome": null,
        "notes": "Expanded scope: covers both implementation quality AND post-refactoring quality (merges POST_REFACTOR_REVIEW)",
        "blocked_by": null,
        "extensions_granted": []
      },
      {
        "phase_name": "REFACTOR_CONTINUOUS",
        "phase_index": 5,
        "status": "NOT_EXECUTED",
        "started_at": null,
        "ended_at": null,
        "duration_minutes": null,
        "duration_seconds": null,
        "turn_count": 0,
        "outcome": null,
        "notes": "Combines L1 (naming clarity) + L2 (complexity reduction) + L3 (class responsibilities and organization)",
        "blocked_by": null,
        "extensions_granted": []
      },
      {
        "phase_name": "REFACTOR_L4",
        "phase_index": 6,
        "status": "NOT_EXECUTED",
        "started_at": null,
        "ended_at": null,
        "duration_minutes": null,
        "duration_seconds": null,
        "turn_count": 0,
        "outcome": null,
        "notes": "Architecture patterns - OPTIONAL (can use CHECKPOINT_PENDING or NOT_APPLICABLE prefix for skip)",
        "blocked_by": null,
        "extensions_granted": []
      },
      {
        "phase_name": "COMMIT",
        "phase_index": 7,
        "status": "NOT_EXECUTED",
        "started_at": null,
        "ended_at": null,
        "duration_minutes": null,
        "duration_seconds": null,
        "turn_count": 0,
        "outcome": null,
        "notes": "Absorbs FINAL_VALIDATE (metadata checks only)",
        "blocked_by": null,
        "extensions_granted": []
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
    "all_8_phases_mandatory": true,
    "phase_documentation_required": true
  },
  "phase_validation_rules": {
    "description": "Rules for validating phase execution status before commit",
    "all_phases_required": true,
    "total_phases": 8,
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
          "APPROVED_SKIP:",
          "CHECKPOINT_PENDING:"
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
        "CHECKPOINT_PENDING:": {
          "allows_commit": true,
          "example": "CHECKPOINT_PENDING: Will complete in REFACTOR checkpoint"
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
    "commit_policy": "Commit ONLY after ALL 8 PHASES complete. AUTO-PUSH after commit.",
    "mandatory_phases": [
      "PREPARE - Remove @skip, verify only 1 scenario enabled",
      "RED_ACCEPTANCE - Test must FAIL initially",
      "RED_UNIT - Write failing unit tests",
      "GREEN - Implement minimum code + verify acceptance (green acceptance is consequence of green unit)",
      "REVIEW - Self-review: SOLID, coverage, acceptance criteria, refactoring quality (MANDATORY, covers both implementation AND post-refactoring)",
      "REFACTOR_CONTINUOUS - Progressive refactoring: L1 (naming) + L2 (complexity) + L3 (organization)",
      "REFACTOR_L4 - Architecture patterns (OPTIONAL: can use CHECKPOINT_PENDING or NOT_APPLICABLE for skip)",
      "COMMIT - Commit with detailed message (absorbs FINAL_VALIDATE metadata checks)"
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

**CRITICAL**: Every generated step file MUST include the complete `phase_execution_log` with all 8 phases pre-populated with status `NOT_EXECUTED` (schema v2.0).

This is **NON-NEGOTIABLE**. The agent executing the step cannot add phases - they must already exist. The agent can only UPDATE existing phase entries.

**8 Required Phases (Schema v2.0)** (in order):
1. PREPARE (phase_index: 0)
2. RED_ACCEPTANCE (phase_index: 1)
3. RED_UNIT (phase_index: 2)
4. GREEN (phase_index: 3) - Combines implementation + acceptance validation
5. REVIEW (phase_index: 4) - Covers both implementation AND post-refactoring
6. REFACTOR_CONTINUOUS (phase_index: 5) - Combines L1 + L2 + L3
7. REFACTOR_L4 (phase_index: 6) - Architecture patterns (OPTIONAL)
8. COMMIT (phase_index: 7) - Absorbs FINAL_VALIDATE

**Each Phase Entry Schema (v2.0)**:
```json
{
  "phase_name": "PREPARE",
  "phase_index": 0,
  "status": "NOT_EXECUTED",
  "started_at": null,
  "ended_at": null,
  "duration_minutes": null,
  "duration_seconds": null,
  "turn_count": 0,
  "outcome": null,
  "notes": null,
  "blocked_by": null,
  "extensions_granted": []
}
```

**Per-Step Validation (MANDATORY)**:

**CRITICAL**: After writing EACH step file, you MUST validate immediately:

```bash
# Validate EACH step file right after writing it
python3 ~/.claude/scripts/validate_step_file.py docs/feature/{project-id}/steps/{step-id}.json

# If validation fails:
# 1. DO NOT proceed to next step
# 2. Fix the step file immediately
# 3. Re-validate until it passes
```

**Common Validation Failures to Avoid**:
- ❌ Wrong phase names: "RED (Acceptance)" → ✅ Use "RED_ACCEPTANCE"
- ❌ Missing `tdd_cycle.phase_execution_log` → ✅ Copy from schema template
- ❌ Less than 8 phases → ✅ Include ALL 8 phases (schema v2.0)
- ❌ Wrong fields: `step_id`, `phase_id` → ✅ Use `task_id`, no `phase_id`
- ❌ Legacy phase names: `GREEN_UNIT`, `CHECK_ACCEPTANCE`, `GREEN_ACCEPTANCE`, `POST_REFACTOR_REVIEW`, `FINAL_VALIDATE` → ✅ Use `GREEN`, `REVIEW`, `REFACTOR_CONTINUOUS`, `COMMIT`

**Single Source of Truth**: `nWave/templates/step-tdd-cycle-schema.json`

**Post-Generation Verification (MANDATORY)**:

After generating ALL step files, run validation on entire directory:

```bash
python3 ~/.claude/scripts/validate_step_file.py --all docs/feature/{project-id}/steps/
```

**Manual Checklist** (for each step file - schema v2.0):
- [ ] `phase_execution_log` exists in `tdd_cycle` section
- [ ] Exactly 8 entries present (schema v2.0)
- [ ] All entries have `status: "NOT_EXECUTED"` (or `SKIPPED` for research steps)
- [ ] All entries have correct `phase_index` (0-7)
- [ ] All entries have correct `phase_name` matching the 8 required phases
- [ ] No duplicate phase names
- [ ] Sequential order matches phase_index

**If Validation Script Fails**:
- DO NOT proceed to /nw:execute
- Fix the step file(s) with missing/invalid phase_execution_log
- Re-run validation until it passes
- Error message will indicate specific issues

**If Validation Script Not Available**:
- Run from nwave project: `python3 scripts/validate_step_file.py --all <steps_dir>`
- Or manually verify each step file has the complete tdd_cycle structure

**CRITICAL**: Step files WITHOUT phase_execution_log will cause /nw:execute to fail.
The executing agent can only UPDATE existing phase entries, not create new ones.

### Step Generation Rules

1. **One Scenario = One Step**: For ATDD steps, each maps exactly ONE acceptance test scenario
2. **First Step Walking Skeleton**: Step 01-01 has `is_walking_skeleton: true` (if ATDD)
3. **Test File Agnostic**: Supports .feature, .cs, .py, .js, .java, .ts, etc.
4. **Mock Boundaries from Architecture**: Analyze docs/architecture to populate allowed_ports
5. **TDD Phase Tracking**: Initialize all 8 phases (schema v2.0) in `tdd_cycle.phase_execution_log` with status `"NOT_EXECUTED"`
6. **Step Type Handling**: Process `step_type` from roadmap (atdd, research, infrastructure)
7. **Integration Step Required (CM-B)**: At least one step must wire component into entry point

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

When generating step files, verify:

```bash
# Check if any step has integration type or targets entry point
grep -l "step_type.*integration\|entry_point\|orchestrator" docs/feature/{project-id}/steps/*.json

# If no results: WARN user about missing integration step
```

### Missing Integration Step Response

If no integration step found:

```
⚠️ WARNING: No integration step detected in roadmap

The roadmap has {N} steps but none wire the component into the system entry point.

After completing all steps:
- Component will exist and pass all tests
- But users cannot invoke it (not connected to system)

Recommended Action:
1. Add an integration step to roadmap before splitting
2. Or document that integration is handled externally

Example integration step:
  - step_id: "{N+1}-01"
    name: "Wire {component} into {entry_point}"
    step_type: "integration"
```

### Step Type Processing (COME - How to Execute)

The split command enriches roadmap steps based on their `step_type`:

**ATDD Steps** (`step_type: "atdd"`):
- Full 8-phase TDD cycle required (schema v2.0)
- Validate `suggested_scenario` against actual test files
- If test file not found: Create placeholder or request test creation
- All TDD phases enabled (status: "NOT_EXECUTED")

**Research Steps** (`step_type: "research"`):
- TDD phases 1-3 (RED_ACCEPTANCE through GREEN) set to "SKIPPED"
- `blocked_by: "NOT_APPLICABLE: Research step without acceptance test"`
- Only PREPARE, REVIEW, REFACTOR_CONTINUOUS, REFACTOR_L4, COMMIT phases active
- No acceptance test mapping required

**Infrastructure Steps** (`step_type: "infrastructure"`):
- TDD phases 1-3 set to "SKIPPED"
- `blocked_by: "NOT_APPLICABLE: Infrastructure step without acceptance test"`
- Focus on PREPARE, execution, REVIEW, and COMMIT phases
- May include verification scripts instead of tests

### Suggested Scenario Validation

When processing ATDD steps with `suggested_scenario`:

1. **File Existence Check**:
   ```
   IF test_file exists:
     Validate scenario_name or scenario_index
   ELSE IF test creation is pending:
     Mark scenario as "pending_creation"
     Set tdd_cycle.acceptance_test.initially_ignored: true
   ELSE:
     WARN: "Test file not found: {test_file}"
     Request user decision: create placeholder or provide path
   ```

2. **Scenario Validation** (format-dependent):
   - `.feature`: Parse Gherkin, find matching Scenario/Scenario Outline
   - `.py`: Find test function matching name pattern
   - `.cs`: Find [Test] or [Fact] method with matching name
   - `.js/.ts`: Find test()/it() with matching description
   - `.java`: Find @Test method with matching name

3. **Validation Failure Handling**:
   ```
   IF scenario not found in test_file:
     WARN: "Scenario '{scenario_name}' not found in {test_file}"
     OPTIONS:
       1. Create scenario stub (if test creation: "flexible")
       2. Update roadmap with correct scenario
       3. Proceed with placeholder (execution will create test)
   ```

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
      {"phase_name": "PREPARE", "phase_index": 0, "status": "NOT_EXECUTED", ...},
      {"phase_name": "RED_ACCEPTANCE", "phase_index": 1, "status": "SKIPPED", "blocked_by": "NOT_APPLICABLE: Research step"},
      {"phase_name": "RED_UNIT", "phase_index": 2, "status": "SKIPPED", "blocked_by": "NOT_APPLICABLE: Research step"},
      {"phase_name": "GREEN", "phase_index": 3, "status": "SKIPPED", "blocked_by": "NOT_APPLICABLE: Research step"},
      {"phase_name": "REVIEW", "phase_index": 4, "status": "NOT_EXECUTED", ...},
      {"phase_name": "REFACTOR_CONTINUOUS", "phase_index": 5, "status": "NOT_EXECUTED", ...},
      {"phase_name": "REFACTOR_L4", "phase_index": 6, "status": "NOT_EXECUTED", ...},
      {"phase_name": "COMMIT", "phase_index": 7, "status": "NOT_EXECUTED", ...}
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

### 8-Phase TDD Enforcement (Schema v2.0)

**CRITICAL**: All generated step files MUST include the 8-phase tracking structure (schema v2.0), pre-populated at generation time.

The phase_execution_log is embedded in the step JSON to persist state across multiple agent instances. Instance 1 (PREPARE phase) starts with all phases in NOT_EXECUTED status, executes PREPARE, updates the log, and writes the file. Instance 2 reads this file, sees PREPARE is EXECUTED in the log, skips PREPARE, and executes RED_ACCEPTANCE. This JSON-based state handoff continues through all 8 phases, with each instance reading prior results from the log and adding its own.

**Phase Execution Requirements**:
1. Each phase MUST be pre-populated in `phase_execution_log` at step file creation (by /nw:split)
2. The executing agent can only UPDATE existing phase entries, not add new ones
3. `current_phase` must track progress through the 8 phases
4. Commit is BLOCKED until all 8 phases have status "EXECUTED" or valid "SKIPPED"
5. Pre-commit hook validates phase completeness before allowing commit
6. Each phase log entry fields (schema v2.0):
   - `phase_name`: Name of the phase (e.g., "PREPARE", "RED_ACCEPTANCE")
   - `phase_index`: Sequential index (0-7)
   - `status`: "NOT_EXECUTED" | "IN_PROGRESS" | "EXECUTED" | "SKIPPED"
   - `started_at`: ISO 8601 timestamp when phase started
   - `ended_at`: ISO 8601 timestamp when phase completed
   - `duration_minutes`: Time spent in phase
   - `duration_seconds`: Time spent in phase (seconds)
   - `turn_count`: Number of agent turns used
   - `outcome`: "PASS" or "FAIL" (required for EXECUTED status)
   - `notes`: Observations and decisions
   - `blocked_by`: Required if status is "SKIPPED" (must have valid prefix)
   - `extensions_granted`: Array for tracking phase extensions

**Valid SKIPPED Prefixes** (allow commit):
- `BLOCKED_BY_DEPENDENCY:` - External dependency unavailable
- `NOT_APPLICABLE:` - Phase not applicable for this task
- `APPROVED_SKIP:` - Skip explicitly approved by reviewer

**Invalid SKIPPED Prefixes** (block commit):
- `DEFERRED:` - Indicates incomplete work, must be resolved before commit

**Phase Execution Log Example (Schema v2.0)** (showing all 8 phases):

⚠️ **CRITICAL**: The `phase_execution_log` is at `tdd_cycle.phase_execution_log`, NOT nested inside `tdd_phase_tracking`.

```json
{
  "tdd_cycle": {
    "tdd_phase_tracking": {
      "current_phase": "REVIEW",
      "active_e2e_test": "Place new order - 01-01",
      "inactive_e2e_tests": "All other @skip scenarios remain disabled",
      "phases_completed": ["PREPARE", "RED_ACCEPTANCE", "RED_UNIT", "GREEN"]
    },
    "phase_execution_log": [
      {
        "phase_name": "PREPARE",
        "phase_index": 0,
        "status": "EXECUTED",
        "started_at": "2024-01-15T10:00:00Z",
        "ended_at": "2024-01-15T10:05:00Z",
        "duration_minutes": 5,
        "duration_seconds": 300,
        "turn_count": 2,
        "outcome": "PASS",
        "notes": "Removed @skip from scenario 'Place new order'. 1 scenario enabled, 3 remain skipped.",
        "blocked_by": null,
        "extensions_granted": []
      },
      {
        "phase_name": "RED_ACCEPTANCE",
        "phase_index": 1,
        "status": "EXECUTED",
        "started_at": "2024-01-15T10:05:00Z",
        "ended_at": "2024-01-15T10:08:00Z",
        "duration_minutes": 3,
        "duration_seconds": 180,
        "turn_count": 1,
        "outcome": "PASS",
        "notes": "Valid RED: 'OrderService' is not defined - test failed as expected",
        "blocked_by": null,
        "extensions_granted": []
      },
      {
        "phase_name": "RED_UNIT",
        "phase_index": 2,
        "status": "EXECUTED",
        "started_at": "2024-01-15T10:08:00Z",
        "ended_at": "2024-01-15T10:20:00Z",
        "duration_minutes": 12,
        "duration_seconds": 720,
        "turn_count": 4,
        "outcome": "PASS",
        "notes": "3 failing unit tests written for OrderService.PlaceOrder. Valid RED: NotImplementedException",
        "blocked_by": null,
        "extensions_granted": []
      },
      {
        "phase_name": "GREEN",
        "phase_index": 3,
        "status": "EXECUTED",
        "started_at": "2024-01-15T10:20:00Z",
        "ended_at": "2024-01-15T10:45:00Z",
        "duration_minutes": 25,
        "duration_seconds": 1500,
        "turn_count": 8,
        "outcome": "PASS",
        "notes": "Implemented minimum OrderService logic. All unit tests pass + acceptance test passes (GREEN acceptance is consequence of GREEN unit)",
        "blocked_by": null,
        "extensions_granted": []
      },
      {
        "phase_name": "REVIEW",
        "phase_index": 4,
        "status": "NOT_EXECUTED",
        "started_at": null,
        "ended_at": null,
        "duration_minutes": null,
        "duration_seconds": null,
        "turn_count": 0,
        "outcome": null,
        "notes": "Expanded scope: covers both implementation quality AND post-refactoring quality",
        "blocked_by": null,
        "extensions_granted": []
      },
      {
        "phase_name": "REFACTOR_CONTINUOUS",
        "phase_index": 5,
        "status": "NOT_EXECUTED",
        "started_at": null,
        "ended_at": null,
        "duration_minutes": null,
        "duration_seconds": null,
        "turn_count": 0,
        "outcome": null,
        "notes": "Combines L1 (naming) + L2 (complexity) + L3 (organization)",
        "blocked_by": null,
        "extensions_granted": []
      },
      {
        "phase_name": "REFACTOR_L4",
        "phase_index": 6,
        "status": "NOT_EXECUTED",
        "started_at": null,
        "ended_at": null,
        "duration_minutes": null,
        "duration_seconds": null,
        "turn_count": 0,
        "outcome": null,
        "notes": "Architecture patterns - OPTIONAL (can use CHECKPOINT_PENDING or NOT_APPLICABLE for skip)",
        "blocked_by": null,
        "extensions_granted": []
      },
      {
        "phase_name": "COMMIT",
        "phase_index": 7,
        "status": "NOT_EXECUTED",
        "started_at": null,
        "ended_at": null,
        "duration_minutes": null,
        "duration_seconds": null,
        "turn_count": 0,
        "outcome": null,
        "notes": "Absorbs FINAL_VALIDATE (metadata checks only)",
        "blocked_by": null,
        "extensions_granted": []
      }
    ]
  }
}
```

**NOTE**: A complete step file MUST have all 8 phases (PREPARE through COMMIT). See the embedded schema v2.0 for the complete structure.

**8-Phase Command Mapping (Schema v2.0)**:

Each step file generated by `/nw:split` is designed to be executed through the 8-phase TDD workflow using `/nw:develop` and related commands:

| Phase | Phase Name | Command | Invoked By |
|-------|------------|---------|------------|
| 0 | PREPARE | Internal TDD loop | `/nw:develop {feature} --step {step-id}` |
| 1 | RED_ACCEPTANCE | Internal TDD loop | `/nw:develop {feature} --step {step-id}` |
| 2 | RED_UNIT | Internal TDD loop | `/nw:develop {feature} --step {step-id}` |
| 3 | GREEN | Internal TDD loop | `/nw:develop {feature} --step {step-id}` (combines unit impl + acceptance validation) |
| 4 | REVIEW | Explicit invocation | `/nw:review @software-crafter-reviewer implementation {step-file}` (covers impl AND post-refactoring) |
| 5 | REFACTOR_CONTINUOUS | Explicit invocation | `/nw:refactor --level 1-3` (combines L1 + L2 + L3) |
| 6 | REFACTOR_L4 | Explicit invocation | `/nw:refactor --level 4` OR `/nw:mikado --goal "{goal}"` (OPTIONAL) |
| 7 | COMMIT | Explicit git commit | `git commit -m "feat({feature}): {scenario} - step {step-id}"` (absorbs FINAL_VALIDATE) |

**NOTE**: Pre-commit hook validates all 8 phases before allowing commit. The hook is installed in the target project by `/nw:develop`.

**Alternative: Fully Automated Execution**:

Instead of manually invoking each phase, use:
```bash
/nw:execute @software-crafter "{step-file}"
```

This will automatically:
- Execute phases 0-3 through the TDD loop
- Invoke `/nw:review` for phase 4
- Invoke `/nw:refactor` or `/nw:mikado` for phases 5-6
- Commit for phase 7 if all validations pass

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
