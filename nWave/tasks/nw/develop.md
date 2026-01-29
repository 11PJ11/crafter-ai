# DW-DEVELOP: Complete DEVELOP Wave Orchestrator

**Wave**: DEVELOP
**Agent**: Main Instance (YOU - the orchestrator reading this)
**Command**: `/nw:develop "{feature-description}"`

> ⚠️ **IMPORTANT**: This command is executed by the **main Claude instance**, NOT by a specialized agent. The main instance orchestrates the workflow by delegating to specialized agents (researcher, software-crafter, solution-architect, etc.) via the Task tool.

---
## 🚨 CRITICAL: ORCHESTRATOR BRIEFING (MANDATORY)

**Sub-agents launched via Task tool have NO ACCESS to the Skill tool.**

They can ONLY use: Read, Write, Edit, Bash, Glob, Grep

### The Architectural Constraint

When you (the orchestrator) delegate to an agent, you MUST:

1. **READ the relevant command file** (e.g., `/nw:baseline`) yourself
2. **EXTRACT the workflow instructions** from that command
3. **CREATE a complete agent prompt** with all instructions embedded inline
4. **DO NOT pass `/nw:*` commands** to agents - they cannot execute them

### WRONG Pattern (Agent receives unusable command reference)

```python
# ❌ BROKEN - Agent cannot invoke /nw:baseline
Task(
    subagent_type="researcher",
    prompt=f'/nw:baseline "{feature_description}"',
)
```

### CORRECT Pattern (Agent receives complete instructions)

```python
# ✅ CORRECT - Agent receives complete instructions inline
Task(
    subagent_type="researcher",
    prompt=f'''
You are a researcher agent creating a measurement baseline.

PROJECT: {project_id}
OUTPUT FILE: docs/feature/{project_id}/baseline.yaml

YOUR TASK: Create a quantitative measurement baseline that captures:
1. Current state metrics (performance, complexity, coverage)
2. Measurement methodology used
3. Target improvement thresholds

DELIVERABLES:
- Create baseline.yaml with measured values
- Document measurement methodology
- Include evidence of measurements

Do NOT continue to roadmap or split - return when baseline is complete.
''',
)
```

### Commands Requiring Translation

When orchestrating these commands, you MUST read the command file and translate:

| Command | Read From | Agent Type |
|---------|-----------|------------|
| `/nw:baseline` | DEPRECATED (Schema v2.0) | N/A |
| `/nw:roadmap` | `nWave/tasks/nw/roadmap.md` | solution-architect |
| `/nw:split` | DEPRECATED (Schema v2.0) | N/A |
| `/nw:execute` | `nWave/tasks/nw/execute.md` | varies by step |
| `/nw:review` | `nWave/tasks/nw/review.md` | *-reviewer variant |

### What NOT to Include in Agent Prompts

- ❌ `/nw:baseline`, `/nw:roadmap`, `/nw:split`, `/nw:execute`, `/nw:review`
- ❌ Any skill or command the agent should "invoke"
- ❌ References to other commands

---

## Overview

The DEVELOP wave orchestrator automates the complete feature development lifecycle from problem measurement to production-ready code through disciplined Test-Driven Development with mandatory quality gates.

### What This Command Does

Execute a **complete DEVELOP wave** that orchestrates:

1. **Phase 1**: Roadmap Creation + Review (strategic planning with 8-phase TDD)
2. **Phase 2**: Execute All Steps (8-phase TDD cycle per step - see canonical schema)
2. **Phase 2.5**: Mutation Testing (test quality validation)
3. **Phase 3**: Finalize (archival and cleanup)
4. **Phase 4**: Report Completion

**Eliminated Phases** (Token-Minimal Architecture):
- ❌ Baseline Creation (eliminated - write-only artifact, saved 300k tokens)
- ❌ Split into Step Files (eliminated - context now in roadmap.yaml, saved 4.8M tokens)
- ❌ Individual Step File Reviews (eliminated - validation moved to execution)

### TDD Cycle Definition

Phases from canonical schema `nWave/templates/step-tdd-cycle-schema.json` (single source of truth, embedded at build time):

{{SCHEMA_TDD_PHASES}}

### Key Features

- **Single Command**: One command executes entire wave (`/nw:develop "{description}"`)
- **Smart Skip Logic**: Skips creation if artifacts exist AND are approved
- **Mandatory Quality Gates**: 3 + 3N reviews per feature (N = number of steps)
- **Automatic Retry**: Max 2 attempts for each rejected review
- **Stop on Failure**: Immediate stop if review rejected after 2 attempts
- **Progress Tracking**: Resume capability via `.develop-progress.json`
- **Zero-Tolerance Validation**: All tests must pass, all reviews must approve

### Target Project Prerequisites

**⚠️ REQUIREMENTS**: The target project where `/nw:develop` is executed must have:

| Prerequisite | Version | Purpose |
|-------------|---------|---------|
| **Python 3** | 3.8+ | Required for hook scripts and validation |
| **pre-commit** | 2.0+ | Framework for git hook management |
| **pip** | Latest | To install pre-commit if missing |

**Installation check** (run in target project):
```bash
# Check Python
python3 --version  # Must be 3.8+

# Check pre-commit
pre-commit --version  # If missing: pip install pre-commit
```

> 💡 **Note**: The orchestrator will prompt to install `pre-commit` if not found, but Python must already be available on the system.

### Breaking Change Notice

**⚠️ BREAKING CHANGE**: This is a complete redesign of the `/nw:develop` command.

**OLD Signature** (DEPRECATED):
```bash
/nw:develop {feature-name} --step {step-id}
```

**NEW Signature**:
```bash
/nw:develop "{feature-description}"
```

**Migration**: For single-step execution, use `/nw:execute` instead (see Migration Guide below).

---

## Token Usage Comparison (Schema v1.x vs v2.0)

**Example Project**: des-us006 (35 steps, moderate complexity)

### Schema v1.x (OLD - DEPRECATED):
```
Baseline.yaml:           300k tokens (write-only, rarely read)
Roadmap.yaml:            102k tokens
Step files (35 steps):   4.8M tokens (35 × 137k avg)
                         ─────────────
TOTAL:                   5.2M tokens
```

### Schema v2.0 (NEW - CURRENT):
```
Roadmap.yaml:            102k tokens (contains all step context)
Execution-status.yaml:   175k tokens (35 × 5k avg)
Context extraction:      5k tokens/step (extracted on-demand from roadmap)
                         ─────────────
TOTAL:                   ~310k tokens (277k static + 5k per execution)
```

**Savings**: **4.9M tokens (94% reduction)**

**Key Insight**: Step files were write-only artifacts. Orchestrator now extracts context directly from roadmap, eliminating the intermediary.

---

## Instance Isolation in Develop Orchestration

Orchestrates multiple Task invocations. Each instance loads step file, executes phases, updates results, terminates. Instances chain via shared step file to complete TDD cycle.

## CRITICAL: Orchestration Protocol

### ⚡ ORCHESTRATOR ROLE (Read This First!)

**YOU are the orchestrator** - the agent reading this specification right now.

**Your responsibilities:**
1. ✅ **YOU** follow these 12 steps directly (don't delegate to another orchestrator)
2. ✅ **YOU** check validation.status for skip logic
3. ✅ **YOU** invoke sub-commands using appropriate agents:
   - For implementation: Use `Task` tool with `@software-crafter`
   - For reviews: Use `Task` tool with `@{reviewer-agent}`
4. ✅ **YOU** manage progress tracking and error handling
5. ✅ **YOU** report completion summary

**Agent Delegation Pattern (with explicit command invocation and BOUNDARY):**

⚠️ **CRITICAL: All Task invocations MUST include boundary instructions to prevent sub-agents from continuing the workflow beyond their assigned task.**

```python
# BOUNDARY TEMPLATE - Include in ALL Task prompts:
BOUNDARY_TEMPLATE = '''
═══════════════════════════════════════════════════════════
⚠️  TASK BOUNDARY - READ BEFORE EXECUTING
═══════════════════════════════════════════════════════════
YOUR ONLY TASK: {task_description}
FORBIDDEN ACTIONS:
  ❌ DO NOT execute other /nw: commands beyond your assigned task
  ❌ DO NOT continue the workflow
  ❌ DO NOT assume orchestrator responsibilities
REQUIRED: Return control to orchestrator after completion
═══════════════════════════════════════════════════════════

{actual_command}
'''

# For baseline creation (STEP 3) - Use RESEARCHER agent
Task(
  subagent_type="researcher",  # NOT software-crafter - per baseline.md spec
  prompt=BOUNDARY_TEMPLATE.format(
      task_description="Create baseline.yaml measurement file",
      actual_command='/nw:baseline "{feature_description}"'
  ),
  description="Create measurement baseline"
)

# For step execution (STEP 10)
Task(
  subagent_type="software-crafter",
  prompt=BOUNDARY_TEMPLATE.format(
      task_description="Execute step {step_id} with complete TDD cycle",
      actual_command='/nw:execute @software-crafter "{step_file}"'
  ),
  description="Execute step 01-03"
)

# For review (STEP 4, 6, 7, 9)
Task(
  subagent_type="software-crafter-reviewer",
  prompt=BOUNDARY_TEMPLATE.format(
      task_description="Review {artifact_type} artifact",
      actual_command='/nw:review @software-crafter-reviewer baseline "{artifact-path}"'
  ),
  description="Review baseline"
)

# For roadmap creation (STEP 5)
Task(
  subagent_type="solution-architect",
  prompt=BOUNDARY_TEMPLATE.format(
      task_description="Create implementation roadmap",
      actual_command='/nw:roadmap @solution-architect "{feature_description}"'
  ),
  description="Create implementation roadmap"
)
```

**DO NOT:**
- ❌ Create a sub-agent to read this specification
- ❌ Delegate orchestration to another agent
- ❌ Skip validation checks or quality gates
- ❌ Invoke Task without boundary instructions (causes workflow continuation bug)

---

### Pre-Requisite: TDD Phase Validation Hook Installation

**MANDATORY**: Install hooks before execution. Run `python3 ~/.claude/scripts/install_nwave_target_hooks.py` (or `--verify-only` to check). If not installed, prompt user to install or skip.

---

### Input Requirements

The command accepts a single parameter:

- `feature-description` (string, required): Natural language description of the feature to develop
  - Example: "Implement user authentication with JWT"
  - Example: "Add shopping cart with checkout validation"
  - Example: "Optimize database query performance for product listings"

### Output Artifacts (Schema v2.0)

The orchestrator generates the following artifacts:

```
docs/feature/{project-id}/
├── roadmap.yaml                     # Phase 1 output (contains all step context)
├── execution-status.yaml            # Phase 2 output (step execution tracking)
├── .develop-progress.json           # Progress tracking
└── (archived to docs/evolution/     # Phase 3 output
     after finalization)
```

**Eliminated Artifacts** (Token savings):
- ❌ baseline.yaml (300k tokens - write-only artifact)
- ❌ steps/*.json (4.8M tokens - replaced by execution-status.yaml at 5k tokens/step)

### Orchestration Flow (Schema v2.0 - Token-Minimal Architecture)

```
INPUT: "{feature-description}"
  ↓
STEP 1: Extract + Validate Input
  ↓
STEP 2: Derive Project ID (kebab-case)
  ↓
STEP 3: Phase 1 - Roadmap Creation + Review (with skip, retry max 2)
  ↓
STEP 4: Phase 2 - Execute-All Steps (8-phase TDD cycle per step, roadmap context extraction)
  ↓
STEP 5: Phase 3 - Finalize (read execution-status.yaml, archive, cleanup)
  ↓
STEP 6: Phase 4 - Report Completion
```

**Eliminated Phases** (Saved 5.1M tokens):
- ❌ STEP 3-4: Baseline Creation + Review (eliminated - write-only artifact, 300k tokens)
- ❌ STEP 7-8: Split into Steps + Review Each Step (eliminated - step files, 4.8M tokens)
- ❌ STEP 10: Mutation Testing (deferred to future enhancement)

**Architecture Change**: Orchestrator extracts context from roadmap.yaml (~5k tokens per step) and passes to sub-agents via Task tool. No intermediate step files created.

---

## Agent Invocation Protocol

### STEP 1: Extract Feature Description and Validate Input

**Objective**: Parse command arguments and validate input completeness.

**Actions**:

1. Parse the command invocation:
   ```bash
   /nw:develop "{feature-description}"
   ```

2. Extract `feature-description` parameter

3. **Validation**:
   ```python
   if not feature_description or len(feature_description.strip()) < 10:
       ERROR: "Feature description too short. Provide detailed description (min 10 chars)"
       EXIT

   if feature_description.strip().startswith("--"):
       ERROR: "Invalid syntax. Use: /nw:develop \"{description}\" (not --step flag)"
       HINT: "For single step execution, use /nw:execute instead"
       EXIT
   ```

4. Log invocation:
   ```
   INFO: "Starting DEVELOP wave orchestration"
   INFO: "Feature: {feature_description}"
   ```

**Success Criteria**:
- Feature description extracted and valid
- No deprecated flags detected

---

### STEP 2: Derive Project ID

**Objective**: Generate consistent project identifier from feature description.

**Actions**:

1. **Transform description to kebab-case**:
   ```python
   import re

   def derive_project_id(description):
       """
       Convert natural language description to kebab-case project ID.

       Examples:
         "Implement user authentication with JWT" → "user-authentication"
         "Add shopping cart checkout" → "shopping-cart-checkout"
         "Optimize DB queries" → "optimize-db-queries"
       """
       # Remove common prefixes
       cleaned = description.lower()
       for prefix in ["implement ", "add ", "create ", "build ", "develop "]:
           if cleaned.startswith(prefix):
               cleaned = cleaned[len(prefix):]

       # Extract key words (remove articles, prepositions, conjunctions)
       stop_words = {"the", "a", "an", "with", "for", "and", "or", "in", "on", "at", "to", "from"}
       words = re.findall(r'\w+', cleaned)
       key_words = [w for w in words if w not in stop_words][:5]  # Max 5 words

       # Join with hyphens
       project_id = "-".join(key_words)

       return project_id
   ```

2. **Invoke transformation**:
   ```python
   project_id = derive_project_id(feature_description)

   INFO: f"Derived project ID: {project_id}"
   ```

3. **Check for existing project**:
   ```python
   project_dir = f"docs/feature/{project_id}"

   if os.path.exists(project_dir):
       INFO: f"Found existing project directory: {project_dir}"
       INFO: "Will use smart skip logic for existing artifacts"
   else:
       INFO: f"Creating new project directory: {project_dir}"
       os.makedirs(project_dir, exist_ok=True)
   ```

**Success Criteria**:
- Project ID derived successfully
- Project directory exists or created

---

### STEP 3: Phase 1 - Baseline Creation (with Skip Logic)

**Objective**: Establish quantitative measurement baseline, skip if already approved.

**Actions**:

1. **Check for existing baseline** (embedded script):
   ```python
   def check_artifact_skip(artifact_path, artifact_type):
       """
       Verify if an artifact can be skipped.

       Returns: (should_skip: bool, reason: str, validation_status: str)
       """
       import os
       import yaml

       if not os.path.exists(artifact_path):
           return False, f"{artifact_type} not found at {artifact_path}", "missing"

       with open(artifact_path, 'r') as f:
           data = yaml.safe_load(f)

       # Check validation status
       validation = data.get('baseline', {}).get('validation', {})
       status = validation.get('status', 'pending')

       if status == 'approved':
           return True, f"{artifact_type} exists and approved - skipping creation", "approved"
       elif status == 'complete':
           return False, f"{artifact_type} exists but not yet approved - needs review", "complete"
       elif status == 'draft':
           return False, f"{artifact_type} exists but is draft - needs completion", "draft"
       else:
           return False, f"{artifact_type} exists with unknown status: {status}", status

   # Execute skip check
   baseline_path = f'docs/feature/{project_id}/baseline.yaml'
   should_skip, reason, status = check_artifact_skip(baseline_path, 'Baseline')

   if should_skip:
       print(f"✓ {reason}")
       print(f"Loading existing baseline for context...")
       # Load baseline content for context
       with open(baseline_path, 'r') as f:
           baseline_data = yaml.safe_load(f)
       # Store in orchestrator context
       # Proceed directly to Phase 2 (review will re-verify approval)
   else:
       print(f"⚠ {reason}")
       if status == 'missing':
           print(f"Creating new baseline...")
           # Proceed with baseline creation
       elif status in ['complete', 'draft']:
           print(f"Baseline exists but needs approval. Skipping creation, proceeding to review...")
           # Skip creation, go directly to Phase 2 (review)
   ```

2. **If baseline creation needed** (status == 'missing'):

   a. Create complete agent prompt and invoke via Task tool:
   ```python
   # CRITICAL: Do NOT pass /nw:baseline to agent - they cannot execute it
   # Instead, read baseline.md and embed instructions inline
   task_result = Task(
       subagent_type="researcher",
       prompt=f'''
You are a researcher agent creating a measurement baseline.

═══════════════════════════════════════════════════════════
⚠️  TASK BOUNDARY - READ BEFORE EXECUTING
═══════════════════════════════════════════════════════════
YOUR ONLY TASK: Create baseline.yaml measurement file
OUTPUT FILE: docs/feature/{project_id}/baseline.yaml
FORBIDDEN ACTIONS:
  ❌ DO NOT continue to roadmap or split
  ❌ DO NOT attempt to execute the full workflow
REQUIRED: Return control to orchestrator after completion
═══════════════════════════════════════════════════════════

PROJECT: {project_id}
DESCRIPTION: {feature_description}

YOUR TASK: Create a quantitative measurement baseline that captures:
1. Current state metrics relevant to: {feature_description}
2. Measurement methodology used (tools, commands, techniques)
3. Target improvement thresholds

BASELINE YAML STRUCTURE:
```yaml
project_id: {project_id}
created_at: <timestamp>
measurements:
  - metric_name: <name>
    current_value: <measured value>
    target_value: <goal>
    methodology: <how measured>
    evidence: <proof of measurement>
```

DELIVERABLES:
- Create baseline.yaml at docs/feature/{project_id}/baseline.yaml
- Document all measurements with evidence
- Return when baseline creation is complete
''',
       description="Create measurement baseline"
   )
   ```

   b. Task tool handles completion automatically

   c. Verify baseline.yaml created:
   ```python
   if not os.path.exists(baseline_path):
       ERROR: "Baseline creation failed - file not found"
       EXIT

   INFO: "✅ Baseline created successfully"
   ```

3. **Update progress tracking**:
   ```python
   update_progress_state(
       project_id,
       current_phase='Phase 1: Baseline Creation',
       skip_flags={'baseline': should_skip}
   )

   if should_skip or status in ['complete', 'draft']:
       # Mark phase complete if skipped or already done
       mark_phase_complete(project_id, 'Phase 1: Baseline Creation')
   ```

**Success Criteria**:
- Baseline exists (either created or pre-existing)
- Baseline file path: `docs/feature/{project-id}/baseline.yaml`
- Progress state updated

---

### STEP 4: Phase 2 - Review Baseline (with Retry)

**Objective**: Ensure baseline quality through mandatory review with automatic retry.

**Actions**:

1. **Execute review with retry loop** (embedded script):

   ```python
   approved, attempts, final_status, rejection_reasons = execute_review_with_retry(
       reviewer_agent='@software-crafter-reviewer',
       artifact_type='Baseline',
       artifact_path=f'docs/feature/{project_id}/baseline.yaml',
       project_description=feature_description,
       project_id=project_id,
       max_attempts=2
   )

   if not approved:
       print("\n" + "="*60)
       print("ERROR: Baseline review failed after 2 attempts")
       print("="*60)
       print("\nRejection history:")
       for rejection in rejection_reasons:
           print(f"\nAttempt {rejection['attempt']}:")
           print(f"  {rejection['reason']}")

       print("\nManual intervention required:")
       print("1. Review rejection feedback above")
       print("2. Fix baseline.yaml manually")
       print("3. Re-run: /nw:develop \"{feature_description}\"")
       print("\nThe command will skip baseline creation and proceed to review again.")

       # Update progress with failure
       update_progress_state(
           project_id,
           current_phase='Phase 2: Review Baseline',
           failed_phase='Phase 2: Review Baseline',
           failure_reason=f"Review rejected after {attempts} attempts"
       )

       EXIT
   else:
       print(f"\n✓ Baseline approved after {attempts} attempt(s)")
       print("Proceeding to Phase 3 (roadmap creation)...")

       # Mark phase complete
       mark_phase_complete(project_id, 'Phase 2: Review Baseline')
   ```

**Success Criteria**:
- Baseline reviewed and approved
- validation.status == "approved" in baseline.yaml
- Progress state updated

---

### STEP 5: Phase 3 - Roadmap Creation (with Skip Logic)

**Objective**: Create strategic implementation roadmap, skip if already approved.

**Actions**:

1. **Check for existing roadmap**:
   ```python
   roadmap_path = f'docs/feature/{project_id}/roadmap.yaml'
   should_skip, reason, status = check_artifact_skip(roadmap_path, 'Roadmap')

   if should_skip:
       print(f"✓ {reason}")
       print(f"Loading existing roadmap for context...")
       with open(roadmap_path, 'r') as f:
           roadmap_data = yaml.safe_load(f)
       # Store in context, proceed to Phase 4
   else:
       print(f"⚠ {reason}")
       if status == 'missing':
           print(f"Creating new roadmap...")
       elif status in ['complete', 'draft']:
           print(f"Roadmap exists but needs approval. Skipping creation, proceeding to review...")
   ```

2. **If roadmap creation needed**:

   a. Create complete agent prompt and invoke via Task tool:
   ```python
   # CRITICAL: Do NOT pass /nw:roadmap to agent - they cannot execute it
   # Instead, embed complete roadmap instructions inline
   task_result = Task(
       subagent_type="solution-architect",
       prompt=f'''
You are a solution-architect agent creating an implementation roadmap.

═══════════════════════════════════════════════════════════
⚠️  TASK BOUNDARY - READ BEFORE EXECUTING
═══════════════════════════════════════════════════════════
YOUR ONLY TASK: Create roadmap.yaml implementation plan
OUTPUT FILE: docs/feature/{project_id}/roadmap.yaml
INPUT FILE: docs/feature/{project_id}/baseline.yaml (read for context)
FORBIDDEN ACTIONS:
  ❌ DO NOT continue to split or execute
  ❌ DO NOT attempt to execute the full workflow
REQUIRED: Return control to orchestrator after completion
═══════════════════════════════════════════════════════════

PROJECT: {project_id}
DESCRIPTION: {feature_description}

YOUR TASK: Create a comprehensive implementation roadmap that:
1. Breaks down the feature into sequential phases
2. Defines atomic steps within each phase
3. Maps dependencies between steps
4. Identifies required agents for each step

ROADMAP YAML STRUCTURE:
```yaml
project_id: {project_id}
created_at: <timestamp>
phases:
  - phase_id: "01"
    name: <phase name>
    steps:
      - step_id: "01-01"
        name: <step name>
        description: <what to implement>
        acceptance_criteria: [<list of criteria>]
        suggested_agent: <researcher|software-crafter|etc>
        dependencies: [<list of step_ids>]
        estimated_hours: <number>
```

DELIVERABLES:
- Create roadmap.yaml at docs/feature/{project_id}/roadmap.yaml
- Ensure all steps are atomic and self-contained
- Return when roadmap creation is complete
''',
       description="Create implementation roadmap"
   )
   ```

   b. Task tool handles completion automatically

   c. Verify roadmap.yaml created:
   ```python
   if not os.path.exists(roadmap_path):
       ERROR: "Roadmap creation failed - file not found"
       EXIT

   INFO: "✅ Roadmap created successfully"
   ```

3. **Update progress tracking**:
   ```python
   update_progress_state(
       project_id,
       current_phase='Phase 3: Roadmap Creation',
       skip_flags={'roadmap': should_skip}
   )

   if should_skip or status in ['complete', 'draft']:
       mark_phase_complete(project_id, 'Phase 3: Roadmap Creation')
   ```

**Success Criteria**:
- Roadmap exists (created or pre-existing)
- Roadmap file path: `docs/feature/{project-id}/roadmap.yaml`
- Progress state updated

---

### STEP 6: Phase 4 - Review Roadmap - Software Crafter (with Retry)

**Objective**: Validate roadmap technical feasibility and implementation approach.

**Actions**:

1. **Execute Software Crafter review with retry**:
   ```python
   approved, attempts, final_status, rejection_reasons = execute_review_with_retry(
       reviewer_agent='@software-crafter-reviewer',
       artifact_type='Roadmap',
       artifact_path=f'docs/feature/{project_id}/roadmap.yaml',
       project_description=feature_description,
       project_id=project_id,
       max_attempts=2
   )

   if not approved:
       print("\n" + "="*60)
       print("ERROR: Roadmap Software Crafter review failed after 2 attempts")
       print("="*60)
       print("\nRejection history:")
       for rejection in rejection_reasons:
           print(f"\nAttempt {rejection['attempt']}:")
           print(f"  {rejection['reason']}")

       print("\nManual intervention required:")
       print("1. Review Software Crafter feedback above")
       print("2. Fix roadmap.yaml manually (technical aspects)")
       print("3. Re-run: /nw:develop \"{feature_description}\"")

       update_progress_state(
           project_id,
           failed_phase='Phase 4: Review Roadmap - Software Crafter',
           failure_reason=f"Software Crafter review rejected after {attempts} attempts"
       )

       EXIT
   else:
       print(f"\n✓ Roadmap approved by Software Crafter after {attempts} attempt(s)")
       print("Proceeding to Phase 5 (split into atomic steps)...")

       mark_phase_complete(project_id, 'Phase 4: Review Roadmap - Software Crafter')
   ```

**Success Criteria**:
- Roadmap approved by Software Crafter
- Technical approach validated
- Progress state updated

---

### STEP 7: Phase 5 - Split into Atomic Steps (with Skip Logic)

**Objective**: Decompose roadmap into atomic, executable steps.

**⚠️ CRITICAL CONSTRAINT: Step-to-Scenario Mapping (Outside-In TDD)**

```
┌────────────────────────────────────────────────────────────────────┐
│  1 ACCEPTANCE TEST SCENARIO = 1 STEP FILE = 1 COMPLETE TDD CYCLE  │
└────────────────────────────────────────────────────────────────────┘

MANDATORY VALIDATION:
  1. Count acceptance test scenarios: grep 'def test_' tests/acceptance/test_*.py
  2. Count roadmap steps: sum of all steps in roadmap.yaml
  3. ENFORCE: num_step_files == num_acceptance_scenarios (with flexibility below)

FLEXIBILITY CLAUSE:
  - Infrastructure steps (DB migrations, env config) may not have scenarios
  - Mark such steps with: "acceptance_test_scenario": "N/A - infrastructure"
  - The principle applies to FEATURE steps, not infrastructure

WHY THIS MATTERS:
  - Each step must turn exactly ONE scenario from RED → GREEN
  - Prevents "architectural" steps that make multiple tests pass at once
  - Ensures clear traceability: scenario → step → commit

See: docs/principles/outside-in-tdd-step-mapping.md
```

**Actions**:

1. **Check for existing step files**:
   ```python
   steps_dir = f'docs/feature/{project_id}/steps'

   if os.path.exists(steps_dir):
       existing_steps = glob.glob(os.path.join(steps_dir, '*.json'))

       if existing_steps:
           print(f"✓ Found {len(existing_steps)} existing step files")

           # Check if ALL steps are approved
           all_approved = True
           for step_file in existing_steps:
               with open(step_file, 'r') as f:
                   step_data = json.load(f)
               validation = step_data.get('validation', {})
               if validation.get('status') != 'approved':
                   all_approved = False
                   break

           if all_approved:
               print(f"✓ All {len(existing_steps)} step files approved - skipping split")
               should_skip = True
           else:
               print(f"⚠ Some step files not approved - skipping split, proceeding to review")
               should_skip = False
       else:
           print(f"⚠ Steps directory exists but empty - creating steps")
           should_skip = False
   else:
       print(f"⚠ No steps directory found - creating steps")
       should_skip = False
   ```

2. **If split needed** (!should_skip):

   a. Create complete agent prompt and invoke via Task tool:
   ```python
   # CRITICAL: Do NOT pass /nw:split to agent - they cannot execute it
   # Instead, embed complete split instructions inline
   task_result = Task(
       subagent_type="software-crafter",
       prompt=f'''
You are a software-crafter agent generating atomic task files from a roadmap.

═══════════════════════════════════════════════════════════
⚠️  TASK BOUNDARY - READ BEFORE EXECUTING
═══════════════════════════════════════════════════════════
YOUR ONLY TASK: Generate step JSON files from roadmap
INPUT FILE: docs/feature/{project_id}/roadmap.yaml
OUTPUT DIRECTORY: docs/feature/{project_id}/steps/
FORBIDDEN ACTIONS:
  ❌ DO NOT execute any steps
  ❌ DO NOT continue to the execute phase
REQUIRED: Return control to orchestrator after completion
═══════════════════════════════════════════════════════════

PROJECT: {project_id}

STEP-TO-SCENARIO MAPPING REQUIREMENT:
Before generating steps, you MUST:
1. Read acceptance tests: tests/acceptance/test_*.py
2. Count scenarios: grep 'def test_' (N scenarios)
3. Each step MUST reference ONE specific scenario it will make pass
4. Exception: Infrastructure steps may use "N/A - infrastructure"

YOUR TASK: Transform each roadmap step into a complete task JSON file that:
1. Includes the complete TDD cycle structure (see canonical schema)
2. Contains self-contained context
3. Has clear acceptance criteria
4. Maps all dependencies
5. References the specific acceptance test scenario it implements

{{MANDATORY_PHASES}}

Read the canonical schema from: nWave/templates/step-tdd-cycle-schema.json

DELIVERABLES:
- Create JSON file for each step in docs/feature/{project_id}/steps/
- Validate each file has correct TDD cycle structure (from canonical schema)
- Return when all step files are generated
''',
       description="Split roadmap into atomic steps"
   )
   ```

   b. Task tool handles completion automatically

   c. Verify step files created:
   ```python
   step_files = glob.glob(f'docs/feature/{project_id}/steps/*.json')

   if not step_files:
       ERROR: "Split command completed but no step files found"
       EXIT

   INFO: f"✅ Split created {len(step_files)} step files"
   ```

3. **Update progress tracking**:
   ```python
   update_progress_state(
       project_id,
       current_phase='Phase 5: Split into Atomic Steps',
       skip_flags={'split': should_skip}
   )

   if should_skip:
       mark_phase_complete(project_id, 'Phase 5: Split into Atomic Steps')
   ```

**Success Criteria**:
- Step files exist in `docs/feature/{project-id}/steps/`
- At least 1 step file created
- Progress state updated

---

### STEP 8: Phase 6 - Review Each Step File (with Retry per File)

**Objective**: Ensure each generated step meets quality standards before execution.

**Actions**:

1. **Get all step files**:
   ```python
   step_files = sorted(glob.glob(f'docs/feature/{project_id}/steps/*.json'))

   print(f"\n{'='*60}")
   print(f"Phase 6: Reviewing {len(step_files)} step files")
   print(f"{'='*60}\n")
   ```

2. **Review each step file with retry**:
   ```python
   failed_reviews = []

   for i, step_file in enumerate(step_files, 1):
       step_id = os.path.basename(step_file).replace('.json', '')

       print(f"\n[{i}/{len(step_files)}] Reviewing step: {step_id}")
       print("-" * 40)

       # Check if already approved (skip logic)
       with open(step_file, 'r') as f:
           step_data = json.load(f)

       validation = step_data.get('validation', {})
       if validation.get('status') == 'approved':
           print(f"✓ Step {step_id} already approved - skipping review")
           continue

       # Execute review with retry
       approved, attempts, final_status, rejection_reasons = execute_review_with_retry(
           reviewer_agent='@software-crafter-reviewer',
           artifact_type=f'Step {step_id}',
           artifact_path=step_file,
           project_description=feature_description,
           project_id=project_id,
           max_attempts=2,
           regenerate_command=f'/nw:split @devop "{project_id}" --regenerate-step {step_id}'
       )

       if not approved:
           failed_reviews.append({
               'step_id': step_id,
               'step_file': step_file,
               'attempts': attempts,
               'rejection_reasons': rejection_reasons
           })
       else:
           print(f"✓ Step {step_id} approved after {attempts} attempt(s)")

   # Check if any reviews failed
   if failed_reviews:
       print("\n" + "="*60)
       print(f"ERROR: {len(failed_reviews)} step file(s) failed review")
       print("="*60)

       for failure in failed_reviews:
           print(f"\nStep {failure['step_id']}:")
           for rejection in failure['rejection_reasons']:
               print(f"  Attempt {rejection['attempt']}: {rejection['reason']}")

       print("\nManual intervention required:")
       print("1. Review rejection feedback above")
       print("2. Fix step files manually OR regenerate with feedback")
       print("3. Re-run: /nw:develop \"{feature_description}\"")

       update_progress_state(
           project_id,
           failed_phase='Phase 6: Review Each Step File',
           failure_reason=f"{len(failed_reviews)} step(s) rejected after 2 attempts"
       )

       EXIT
   else:
       print(f"\n✅ All {len(step_files)} step files approved")
       print("Proceeding to Phase 7 (execute all steps)...")

       mark_phase_complete(project_id, 'Phase 6: Review Each Step File')
   ```

**Success Criteria**:
- All step files reviewed
- All step files approved (validation.status == "approved")
- Progress state updated

---

### STEP 9: Phase 7 - Execute All Steps (Complete TDD Cycle per Step)

#### Cross-Instance Phase Coordination

Instances update phase_execution_log, next instance reads prior progress, continues from incomplete phases. JSON-based coordination, no shared session state.

**Objective**: Execute steps in dependency order using complete TDD cycle (canonical schema).

**Actions**:

1. **Validate all steps approved** (embedded script - see Enforcement Scripts section):
   ```python
   all_approved, unapproved_steps, error_message = validate_all_steps_approved(
       f'docs/feature/{project_id}/steps/'
   )

   if not all_approved:
       print(error_message)
       EXIT
   else:
       print(error_message)  # "✓ All N step files approved"
   ```

2. **Sort steps by dependency order** (embedded script - see Enforcement Scripts section):
   ```python
   sorted_step_files, error = topological_sort_steps(f'docs/feature/{project_id}/steps/')

   if error:
       print(error)
       EXIT
   else:
       print(f"✓ Steps sorted by dependency order:")
       for i, step_file in enumerate(sorted_step_files, 1):
           print(f"  {i}. {os.path.basename(step_file)}")
   ```

3. **Execute each step in order**:
   ```python
   print(f"\n{'='*60}")
   print(f"Executing {len(sorted_step_files)} steps with complete TDD cycle")
   print(f"{'='*60}\n")

   completed_steps = []
   failed_step = None

   for i, step_file in enumerate(sorted_step_files, 1):
       step_id = os.path.basename(step_file).replace('.json', '')

       print(f"\n[{i}/{len(sorted_step_files)}] Executing step: {step_id}")
       print("-" * 40)

       # Check if step already completed (resume capability)
       with open(step_file, 'r') as f:
           step_data = json.load(f)

       tdd_tracking = step_data.get('tdd_cycle', {}).get('tdd_phase_tracking', {})
       phase_log = tdd_tracking.get('phase_execution_log', [])

       commit_phase = next((p for p in phase_log if p['phase_name'] == 'COMMIT'), None)
       if commit_phase and commit_phase.get('outcome') == 'PASS':
           print(f"✓ Step {step_id} already completed - skipping")
           completed_steps.append(step_id)
           continue

       # Between Task invocations, the step file is the ONLY persistence mechanism.
       # No intermediate working files, session variables, or agent memory carries forward.
       # When Instance 2 starts, it loads the step file written by Instance 1, sees all
       # prior accomplishments in structured JSON, and knows exactly where to continue.
       # This clean separation prevents context degradation and ensures each instance
       # operates with full clarity of prior progress.

       # Execute step with complete TDD cycle using Task tool delegation
       print(f"Invoking: Task tool with @software-crafter for step {step_id}")

       # CRITICAL: Do NOT pass /nw:execute to agent - they cannot execute it
       # Read the step file content and embed complete instructions inline
       with open(step_file, 'r') as f:
           step_content = json.load(f)

       task_result = Task(
           subagent_type="software-crafter",
           prompt=f'''
You are a software-crafter agent executing atomic task {step_id}.

═══════════════════════════════════════════════════════════
⚠️  TASK BOUNDARY - READ BEFORE EXECUTING
═══════════════════════════════════════════════════════════
YOUR ONLY TASK: Execute step {step_id} through all TDD phases (defined in canonical schema)
STEP FILE: {step_file}
FORBIDDEN ACTIONS:
  ❌ DO NOT execute other steps
  ❌ DO NOT continue the workflow
REQUIRED: Return control to orchestrator after completion
═══════════════════════════════════════════════════════════

STEP CONTENT:
```json
{json.dumps(step_content, indent=2)}
```

EXECUTE ALL TDD PHASES IN ORDER (from canonical schema):

Reference the current TDD phases from `nWave/templates/step-tdd-cycle-schema.json`.
The phases are embedded at build time - do not hardcode them here.
See the "TDD Cycle Definition" section above for the current phase list.

INLINE REVIEW CRITERIA (Phases 7 and 12):
- SOLID principles followed
- Test coverage adequate (>80%)
- Acceptance criteria met
- Code readable and maintainable
- No security vulnerabilities
- Refactoring did not break tests

After EACH phase, UPDATE the step file:
- Set phase status to EXECUTED or SKIPPED
- Record duration_minutes, outcome, outcome_details
- Commit after green phases

DELIVERABLES:
- Complete all TDD phases (from canonical schema)
- Update step file with execution results
- Return when COMMIT phase completes with PASS
''',
           description=f"Execute step {step_id} with complete TDD cycle"
       )

       # Verify completion by checking step file for COMMIT/PASS
       with open(step_file, 'r') as f:
           updated_step_data = json.load(f)

       tdd_tracking_after = updated_step_data.get('tdd_cycle', {}).get('tdd_phase_tracking', {})
       phase_log_after = tdd_tracking_after.get('phase_execution_log', [])
       commit_phase_after = next((p for p in phase_log_after if p['phase_name'] == 'COMMIT'), None)

       if commit_phase_after and commit_phase_after.get('outcome') == 'PASS':
           print(f"✓ Step {step_id} completed successfully")
           completed_steps.append(step_id)

           # Update progress
           update_progress_state(
               project_id,
               completed_steps=completed_steps
           )
       else:
           # Step did not complete successfully (no COMMIT/PASS in phase log)
           failure_reason = "Step execution did not complete with COMMIT/PASS"
           if commit_phase_after:
               failure_reason = f"COMMIT phase outcome: {commit_phase_after.get('outcome', 'unknown')}"

           print(f"❌ Step {step_id} failed: {failure_reason}")
           failed_step = step_id

           # Update progress with failure
           update_progress_state(
               project_id,
               failed_step=failed_step,
               failed_phase='Phase 7: Execute All Steps',
               failure_reason=f"Step {step_id} execution failed: {failure_reason}"
           )

           print("\n" + "="*60)
           print(f"ERROR: Step execution failed at {step_id}")
           print("="*60)
           print(f"\nCompleted steps: {len(completed_steps)}/{len(sorted_step_files)}")
           print(f"Failed step: {step_id}")
           print(f"Failure reason: {failure_reason}")
           print("\nManual intervention required:")
           print("1. Review error above")
           print("2. Fix implementation issues")
           print("3. Re-run: /nw:develop \"{feature_description}\"")
           print("\nThe command will resume from the failed step.")

           EXIT

   print(f"\n✅ All {len(sorted_step_files)} steps completed successfully")
   print("Proceeding to Phase 7.5 (mutation testing)...")

   mark_phase_complete(project_id, 'Phase 7: Execute All Steps')
   ```

**Success Criteria**:
- All steps executed with complete TDD cycle
- All steps have COMMIT phase with outcome == "PASS"
- All commits created (one per step)
- No steps failed
- Progress state updated

---

### STEP 10: Phase 7.5 - Mutation Testing (Quality Gate)

**Objective**: Validate test suite quality through mutation testing before finalize.

**Gate Threshold**: 75% mutation kill rate (configurable per project)

**Actions**:

1. **Detect project language**:
   ```python
   def detect_project_language(project_root):
       """Detect primary language from project configuration files."""
       detectors = [
           ('pyproject.toml', 'python'),
           ('setup.py', 'python'),
           ('requirements.txt', 'python'),
           ('pom.xml', 'java-maven'),
           ('build.gradle', 'java-gradle'),
           ('build.gradle.kts', 'kotlin-gradle'),
           ('package.json', 'javascript'),
           ('tsconfig.json', 'typescript'),
           ('*.csproj', 'csharp'),
           ('go.mod', 'go'),
           ('Cargo.toml', 'rust'),
       ]

       for pattern, language in detectors:
           if '*' in pattern:
               if glob.glob(os.path.join(project_root, pattern)):
                   return language
           elif os.path.exists(os.path.join(project_root, pattern)):
               return language

       return 'unknown'

   language = detect_project_language('.')
   print(f"Detected language: {language}")
   ```

2. **Select mutation testing tool**:
   ```python
   MUTATION_TOOLS = {
       'python': {
           'tool': 'mutmut',
           'install': 'pip install mutmut',
           'run': 'mutmut run --paths-to-mutate={src}',
           'report': 'mutmut results',
       },
       'java-maven': {
           'tool': 'pitest',
           'install': 'Add org.pitest:pitest-maven-plugin to pom.xml',
           'run': 'mvn org.pitest:pitest-maven:mutationCoverage',
           'report': 'target/pit-reports/*/index.html',
       },
       'java-gradle': {
           'tool': 'pitest',
           'install': 'Add id "info.solidsoft.pitest" to build.gradle plugins',
           'run': 'gradle pitest',
           'report': 'build/reports/pitest/*/index.html',
       },
       'javascript': {
           'tool': 'stryker',
           'install': 'npm install --save-dev @stryker-mutator/core',
           'run': 'npx stryker run',
           'report': 'reports/mutation/mutation.html',
       },
       'typescript': {
           'tool': 'stryker',
           'install': 'npm install --save-dev @stryker-mutator/core @stryker-mutator/typescript-checker',
           'run': 'npx stryker run',
           'report': 'reports/mutation/mutation.html',
       },
       'csharp': {
           'tool': 'stryker.net',
           'install': 'dotnet tool install -g dotnet-stryker',
           'run': 'dotnet stryker',
           'report': 'StrykerOutput/*/reports/mutation-report.html',
       },
       'go': {
           'tool': 'go-mutesting',
           'install': 'go install github.com/zimmski/go-mutesting/cmd/go-mutesting@latest',
           'run': 'go-mutesting ./...',
           'report': 'stdout (JSON format)',
       },
   }

   if language not in MUTATION_TOOLS:
       print(f"⚠️  No mutation testing tool configured for {language}")
       print("Skipping mutation testing (manual review required)")
       mutation_score = None
   else:
       tool_config = MUTATION_TOOLS[language]
       print(f"Using {tool_config['tool']} for mutation testing")
   ```

3. **Check tool installation and run mutation testing**:
   ```python
   def run_mutation_testing(language, src_paths):
       """Run mutation testing and return score."""
       tool = MUTATION_TOOLS.get(language)
       if not tool:
           return None, "No tool configured"

       # Check if tool is installed
       check_cmd = {
           'python': 'mutmut --version',
           'java-maven': 'mvn --version',
           'java-gradle': 'gradle --version',
           'javascript': 'npx stryker --version',
           'typescript': 'npx stryker --version',
           'csharp': 'dotnet stryker --version',
           'go': 'go-mutesting --version',
       }

       try:
           subprocess.run(check_cmd[language], shell=True, check=True,
                         capture_output=True, timeout=30)
       except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
           return None, f"Tool not installed. Run: {tool['install']}"

       # Run mutation testing (may take significant time)
       print("Running mutation testing (this may take several minutes)...")
       run_cmd = tool['run'].format(src=','.join(src_paths) if src_paths else 'src')

       try:
           result = subprocess.run(run_cmd, shell=True, capture_output=True,
                                  text=True, timeout=1800)  # 30 min timeout
           # Parse score from output (tool-specific)
           return parse_mutation_score(result.stdout, language), None
       except subprocess.TimeoutExpired:
           return None, "Mutation testing timed out (>30 min)"

   mutation_score, error = run_mutation_testing(language, ['src', 'lib'])
   ```

4. **Evaluate against threshold**:
   ```python
   MUTATION_THRESHOLD = 75  # Configurable per project

   if mutation_score is None:
       if language == 'unknown':
           print("⚠️  Language not detected, mutation testing skipped")
           print("Manual test quality review required before finalize")
           # Allow proceed with warning
       else:
           print(f"❌ Mutation testing failed: {error}")
           print("Fix the issue and re-run, or document justification")
           EXIT
   elif mutation_score < MUTATION_THRESHOLD:
       print(f"❌ Mutation score {mutation_score}% below threshold {MUTATION_THRESHOLD}%")
       print("\nSurviving mutants indicate gaps in test coverage.")
       print("Options:")
       print("  1. Add tests to kill surviving mutants")
       print("  2. Document equivalent mutants (false positives)")
       print("  3. Adjust threshold in project config (with justification)")

       # Create surviving mutant report
       create_mutation_report(project_id, mutation_score, surviving_mutants)
       EXIT
   else:
       print(f"✅ Mutation score {mutation_score}% meets threshold {MUTATION_THRESHOLD}%")

   mark_phase_complete(project_id, 'Phase 7.5: Mutation Testing')
   print("Proceeding to Phase 8 (finalize)...")
   ```

5. **Create mutation report** (for documentation):
   ```python
   def create_mutation_report(project_id, score, surviving):
       """Create mutation testing report."""
       report_path = f'docs/feature/{project_id}/mutation-report.md'

       with open(report_path, 'w') as f:
           f.write(f"# Mutation Testing Report\n\n")
           f.write(f"**Project**: {project_id}\n")
           f.write(f"**Date**: {datetime.now().isoformat()}\n")
           f.write(f"**Score**: {score}%\n")
           f.write(f"**Threshold**: {MUTATION_THRESHOLD}%\n")
           f.write(f"**Status**: {'PASS' if score >= MUTATION_THRESHOLD else 'FAIL'}\n\n")

           if surviving:
               f.write("## Surviving Mutants\n\n")
               for mutant in surviving:
                   f.write(f"- {mutant['file']}:{mutant['line']} - {mutant['mutation']}\n")
   ```

**Success Criteria**:
- Language detected or explicitly configured
- Mutation testing tool executed successfully
- Mutation score >= 75% threshold
- Mutation report created
- Progress state updated

**Skip Conditions**:
- Unknown language with no mutation tool available (proceeds with warning)
- Project explicitly opts out via `.mutation-config.yaml` with documented justification

---

### STEP 11: Phase 8 - Finalize

**Objective**: Archive results and clean up workflow files.

**Actions**:

1. **Validate commits for completed steps** (embedded script - see Enforcement Scripts section):
   ```python
   all_committed, missing_commits, error_message = validate_commits_for_completed_steps(
       f'docs/feature/{project_id}/steps/'
   )

   if not all_committed:
       print(error_message)
       EXIT
   else:
       print(error_message)  # "✓ All completed steps have git commits"
   ```

2. **Create complete agent prompt and invoke via Task tool**:
   ```python
   # CRITICAL: Do NOT pass /nw:finalize to agent - they cannot execute it
   # Instead, embed complete finalize instructions inline
   task_result = Task(
       subagent_type="devop",
       prompt=f'''
You are a devop agent finalizing and archiving a completed feature.

═══════════════════════════════════════════════════════════
⚠️  TASK BOUNDARY - READ BEFORE EXECUTING
═══════════════════════════════════════════════════════════
YOUR ONLY TASK: Finalize and archive project {project_id}
INPUT DIRECTORY: docs/feature/{project_id}/
OUTPUT FILE: docs/evolution/{yyyy-MM-dd}-{project_id}.md
FORBIDDEN ACTIONS:
  ❌ DO NOT continue to any other phase
REQUIRED: Return control to orchestrator after completion
═══════════════════════════════════════════════════════════

PROJECT: {project_id}

YOUR TASK: Archive the completed feature by:
1. Create evolution document summarizing achievements
2. Move/archive workflow files (baseline.yaml, roadmap.yaml, step files)
3. Update any project tracking documents
4. Clean up temporary files

EVOLUTION DOCUMENT STRUCTURE:
```markdown
# Evolution: {project_id}

## Summary
- Feature description
- Implementation highlights
- Key decisions made

## Metrics
- Steps completed: X
- Total phases executed: Y
- Duration: Z

## Artifacts
- Location of archived files
- Key deliverables
```

DELIVERABLES:
- Create docs/evolution/{project_id}-evolution.md
- Archive or clean up feature files
- Return when finalization is complete
''',
       description="Finalize and archive project"
   )
   ```

3. **Task tool handles completion, then verify**:
   ```python
   evolution_files = glob.glob(f'docs/evolution/*{project_id}*.md')

   if not evolution_files:
       WARN: "Finalize completed but no evolution document found"
   else:
       INFO: f"✅ Evolution document created: {evolution_files[0]}"

   # Verify cleanup
   if os.path.exists(f'docs/feature/{project_id}/.develop-progress.json'):
       INFO: "Progress tracking file archived"

   mark_phase_complete(project_id, 'Phase 8: Finalize')
   ```

**Success Criteria**:
- Finalize command executed successfully
- Evolution document created in `docs/evolution/`
- Workflow files cleaned up or archived
- Progress state updated

---

### STEP 11.5: Post-Finalize Commit and Push

**Objective**: Archive User Story completion with evolution document and cleanup results.

**Actions**:

1. **Verify finalization artifacts exist**:
   ```python
   evolution_files = glob.glob(f'docs/evolution/*{project_id}*.md')

   if not evolution_files:
       ERROR: "Finalize completed but no evolution document found"
       EXIT
   else:
       INFO: f"✅ Evolution document: {evolution_files[0]}"
   ```

2. **Stage all artifacts**:
   ```bash
   git add docs/evolution/{project_id}-evolution.md
   git add docs/feature/{project_id}/.finalized  # Marker file if exists

   # If cleanup deleted feature folder:
   git add docs/feature/{project_id}/  # Stage deletions
   ```

3. **Create commit with summary**:
   ```python
   # Extract metrics from evolution doc
   with open(evolution_file, 'r') as f:
       evolution_content = f.read()

   # Parse metrics (steps completed, duration, etc.)
   steps_match = re.search(r'Steps completed:\s*(\d+)', evolution_content)
   steps_count = steps_match.group(1) if steps_match else "N/A"

   commit_msg = f"""feat({project_id}): Complete User Story - {feature_description}

Implementation Summary:
- User Story: {implements_user_story}
- Steps Completed: {steps_count}
- Evolution Doc: docs/evolution/{project_id}-evolution.md

All acceptance criteria met, feature ready for production.

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"""

   subprocess.run(['git', 'commit', '-m', commit_msg], check=True)
   ```

4. **Push to remote**:
   ```bash
   git push origin {current-branch}
   ```

5. **Handle errors**:
   ```python
   try:
       result = subprocess.run(['git', 'push', 'origin', branch],
                              capture_output=True, text=True, check=True)
       print(f"✅ User Story archived: {result.stdout}")
   except subprocess.CalledProcessError as e:
       if 'rejected' in e.stderr:
           print("⚠️ Push rejected - remote diverged")
           print("Recovery:")
           print("  1. git fetch origin")
           print("  2. git rebase origin/{branch}")
           print("  3. git push origin {branch}")
           EXIT
       else:
           raise
   ```

**Success Criteria**:
- Evolution document committed
- Commit pushed to remote
- Git log shows finalize commit
- Progress state updated

---

### STEP 12: Phase 9 - Report Completion

**Objective**: Provide comprehensive summary of DEVELOP wave execution.

**Actions**:

1. **Load final progress state**:
   ```python
   progress = load_or_create_progress_state(project_id)
   ```

2. **Count final statistics**:
   ```python
   baseline_path = f'docs/feature/{project_id}/baseline.yaml'
   roadmap_path = f'docs/feature/{project_id}/roadmap.yaml'
   steps_dir = f'docs/feature/{project_id}/steps'

   step_files = glob.glob(os.path.join(steps_dir, '*.json'))

   # Count commits
   commit_count = len(progress.get('completed_steps', []))

   # Count reviews
   total_reviews = (
       1 +  # Baseline review
       1 +  # Roadmap review (Software Crafter)
       len(step_files) +  # Step file reviews
       (commit_count * 2)  # TDD phase reviews (REVIEW + POST-REFACTOR REVIEW per step)
   )
   ```

3. **Display comprehensive report**:
   ```python
   print("\n" + "="*60)
   print("🎉 DEVELOP WAVE COMPLETED SUCCESSFULLY!")
   print("="*60)
   print()
   print("Summary:")
   print(f"  - Feature: {feature_description}")
   print(f"  - Project ID: {project_id}")
   print()
   print("Phase Execution:")
   for phase in progress['completed_phases']:
       print(f"  ✓ {phase}")
   print()
   print("Artifacts Created:")
   print(f"  - Baseline: docs/feature/{project_id}/baseline.yaml")
   print(f"  - Roadmap: docs/feature/{project_id}/roadmap.yaml")
   print(f"  - Steps: {len(step_files)} atomic steps")
   print(f"  - Commits: {commit_count} (one per step)")
   print()
   print("Quality Gates Passed:")
   print(f"  - Total reviews: {total_reviews}")
   print(f"    • 1 baseline review")
   print(f"    • 2 roadmap reviews (business + technical)")
   print(f"    • {len(step_files)} step file reviews")
   print(f"    • {commit_count * 2} TDD phase reviews ({commit_count} steps × 2 reviews)")
   print()
   print("💾 All changes committed locally (not pushed)")
   print()
   print("Next Steps:")
   print("  1. Review evolution document:")
   print(f"     docs/evolution/*{project_id}*.md")
   print("  2. Push commits when ready:")
   print("     git push")
   print("  3. Proceed to DEMO wave:")
   print(f"     /nw:demo \"{project_id}\"")
   print()
   print("="*60)
   ```

4. **Mark orchestration complete**:
   ```python
   update_progress_state(
       project_id,
       current_phase=None,
       orchestration_complete=True
   )
   ```

**Success Criteria**:
- Comprehensive report displayed
- All statistics accurate
- Next steps clearly communicated
- Progress state finalized

---

## Usage Examples

### Example 1: Complete Feature Development

Develop a complete feature from natural language description:

```bash
/nw:develop "Implement user authentication with JWT tokens and session management"
```

**What happens**:
1. Creates baseline measurement (`docs/feature/user-authentication/baseline.yaml`)
2. Reviews baseline (1 review)
3. Creates roadmap (`docs/feature/user-authentication/roadmap.yaml`)
4. Reviews roadmap (Software Crafter)
5. Splits into atomic steps (`docs/feature/user-authentication/steps/*.json`)
6. Reviews each step file (N reviews, one per step)
7. Executes all steps with complete TDD cycle (2N reviews: REVIEW + POST-REFACTOR per step)
8. Finalizes and archives to `docs/evolution/`
9. Reports completion

**Total quality gates**: 3 + 3N reviews (where N = number of steps)

---

### Example 2: Resume After Interruption

If the orchestration was interrupted (e.g., review rejection, step failure):

```bash
# Same command - smart resume
/nw:develop "Implement user authentication with JWT tokens and session management"
```

**What happens**:
- Loads `.develop-progress.json`
- Skips completed phases
- Resumes from failure point
- Example: If baseline approved, roadmap approved, but step 01-02 review rejected:
  - Skips baseline creation (approved)
  - Skips roadmap creation (approved)
  - Skips split (completed)
  - Re-reviews step 01-02 (needs approval)
  - Continues from there

---

### Example 3: Fresh Start on Existing Project

If you want to restart from scratch (e.g., requirements changed):

```bash
# Delete progress and artifacts
rm -rf docs/feature/user-authentication/

# Run command - creates everything fresh
/nw:develop "Implement user authentication with JWT tokens and session management"
```

---

## Complete Workflow Integration

### Greenfield Project - Full nWave

```bash
# Wave 1: DISCOVER (optional - market research and validation)
/nw:discover "User authentication market research"

# Wave 2: DISCUSS (optional - can skip if requirements clear)
/nw:discuss "User authentication system requirements"

# Wave 3: DESIGN (optional - can skip if architecture defined)
/nw:design "Microservices with hexagonal architecture for auth"

# Wave 4: DISTILL (optional - acceptance tests from design)
/nw:distill "User can register and login securely"

# Wave 5: DEVELOP (THIS COMMAND - fully automated)
/nw:develop "Implement user authentication with JWT tokens"
# Automatically: baseline → roadmap → split → execute all → finalize

# Wave 6: DELIVER
/nw:deliver "user-authentication"
```

---

### Brownfield Enhancement - DEVELOP Wave Only

```bash
# If you already have baseline and roadmap from previous work:
/nw:develop "Add password reset functionality to existing auth system"

# Smart skip logic:
# - Finds existing baseline.yaml (approved) → skips creation, uses it
# - Finds existing roadmap.yaml (approved) → skips creation, uses it
# - Creates new step files for password reset feature
# - Executes only new steps
# - Commits incrementally
```

---

## Breaking Changes and Migration

**NEW Functionality**:
- ✅ `/nw:develop "{description}"` for complete wave orchestration
- ✅ Automatic baseline → roadmap → split → execute-all → finalize
- ✅ Mandatory quality gates (3 + 3N reviews per feature)
- ✅ Smart skip logic for approved artifacts
- ✅ Automatic retry (max 2 attempts per review)
- ✅ Progress tracking and resume capability

---

### Migration Guide

#### Scenario 1: Single Step Execution with 11-Phase TDD

**NEW** (use `/nw:execute` instead):
```bash
/nw:execute @software-crafter "docs/feature/order-management/steps/01-02.json"
```

**Explanation**: The `/nw:execute` command now provides the complete TDD cycle execution for a single step that `/nw:develop --step` used to provide.

---

#### Scenario 2: Manual Granular Workflow Control

**NEW** (two options):

**Option A - Fully Automated** (recommended):
```bash
/nw:develop "goal description"
# Automatically executes entire workflow with quality gates
```

**Option B - Manual Granular Control** (advanced):
```bash
/nw:baseline "goal description"
/nw:roadmap @solution-architect "goal description"
/nw:split @devop "project-id"
/nw:execute @software-crafter "docs/feature/{id}/steps/01-01.json"  # ✅ NEW
/nw:execute @software-crafter "docs/feature/{id}/steps/01-02.json"  # ✅ NEW
/nw:execute @software-crafter "docs/feature/{id}/steps/01-03.json"  # ✅ NEW
/nw:finalize @devop "project-id"
```

---

#### Scenario 3: Complete Feature Development

**NEW** (single command):
```bash
/nw:develop "Implement shopping cart with checkout validation"
# Automatically orchestrates entire workflow ✓
```

---

### Quality Gates Comparison

**NEW Workflow** (automatic):
- **Mandatory reviews**: 3 + 3N per feature (enforced)
  - 1 baseline review
  - 1 roadmap review (Software Crafter)
  - N step file reviews
  - 2N TDD phase reviews (REVIEW + POST-REFACTOR per step)
- **Automatic retry**: Max 2 attempts per review
- **Zero-tolerance**: All reviews must approve before proceeding
- **Cannot skip**: Quality gates enforced via embedded Python scripts

---

### CM-D: 90/10 Wiring Test Mandate

**CRITICAL**: The 90/10 test balance must include at least one WIRING test.

#### The Problem

A test suite can have:
- 100% test coverage
- 98%+ mutation kill rate
- All tests passing

Yet the feature may still be NON-FUNCTIONAL if all tests are at the component level and no test exercises the system entry point.

#### The Rule

```yaml
test_balance_requirement:
  rule: "90/10 with mandatory wiring"

  breakdown:
    - "90% unit tests: Component isolation, fast feedback"
    - "10% E2E tests: System wiring, integration verification"

  mandatory_wiring:
    - "At least 1 acceptance test must invoke through user-facing entry point"
    - "E2E means: entry_point → component → result"
    - "NOT: component → result (this is still a unit test)"

  validation: |
    # Check acceptance tests import entry point module
    grep -l "from.*orchestrator\|from.*entry_point\|from.*api" tests/acceptance/test_*.py
    # At least one file must match
```

#### Walking Skeleton First

Before implementing component logic, ensure:
1. Entry point exists (even if empty/stubbed)
2. At least one acceptance test invokes entry point
3. Test fails for RIGHT reason (missing implementation, not missing wiring)

This ensures integration is never "forgotten" - it's the first thing built.

#### What Counts as a Wiring Test

**IS a wiring test**:
```python
def test_feature_works_end_to_end():
    orchestrator = DESOrchestrator()  # Entry point
    result = orchestrator.render_prompt("/nw:execute", ...)
    assert result["task_invocation_allowed"] == True
```

**IS NOT a wiring test** (even if called "E2E"):
```python
def test_validation_works():
    validator = TemplateValidator()  # Internal component
    result = validator.validate_prompt(...)
    assert result.task_invocation_allowed == True
```

The second test exercises component logic but NOT system wiring.

---

## Context Files Required

- None initially - command creates all artifacts
- After creation:
  - `docs/feature/{project-id}/baseline.yaml`
  - `docs/feature/{project-id}/roadmap.yaml`
  - `docs/feature/{project-id}/steps/*.json`
  - `docs/feature/{project-id}/.develop-progress.json` (progress tracking)

---

## Success Criteria

### Phase Completion Criteria

- [ ] **Phase 1-2**: Baseline created OR skipped (if approved), reviewed and approved
- [ ] **Phase 3-4**: Roadmap created OR skipped (if approved), dual reviewed and approved
- [ ] **Phase 5-6**: Steps created OR skipped (if all approved), each reviewed and approved
- [ ] **Phase 7**: All steps executed with 14-phase TDD, all commits created
- [ ] **Phase 7.5**: Mutation testing passed (>= 75% kill rate) or documented skip
- [ ] **Phase 8**: Finalize executed, evolution document created
- [ ] **Phase 9**: Completion report displayed

### Overall Success Criteria

- [ ] All quality gates passed (3 + 3N reviews)
- [ ] All artifacts created and approved
- [ ] All step files executed successfully
- [ ] All commits created (one per step, local only)
- [ ] No failing tests
- [ ] Mutation testing gate passed (>= 75% or documented skip)
- [ ] Progress tracking complete
- [ ] Evolution document created

---

## Next Wave

**After DEVELOP completes**: `/nw:deliver "{project-id}"` → DELIVER wave
**Handoff**: feature-completion-coordinator

**Before pushing to remote**:
1. Review evolution document
2. Verify all commits present
3. Run final integration tests (if any)
4. Push when ready: `git push`

---

## Notes

### Design Decisions

1. **Breaking Change Rationale**: Perfect semantics over backwards compatibility - `/nw:develop` should develop the COMPLETE feature, not a single step
2. **Smart Skip Logic**: Enables resume and incremental updates - skip artifact creation if exists AND approved
3. **Mandatory Quality Gates**: Zero-tolerance quality ensures production-ready code - 3 + 3N reviews per feature
4. **Automatic Retry**: Graceful handling of review rejections - max 2 attempts prevents infinite loops
5. **Progress Tracking**: Resume capability for long-running workflows - .develop-progress.json enables recovery
6. **Local Commits Only**: User controls when to push - automatic commits per step, manual push after finalize

### Performance Expectations

- **Baseline + Review**: 10-20 minutes
- **Roadmap + Dual Review**: 20-30 minutes
- **Split + Review Each Step**: 5-10 minutes per step
- **Execute Each Step** (14-phase TDD): 30-60 minutes per step
- **Finalize**: 5-10 minutes

**Total for N steps**: ~60 + (40-70 minutes × N)
- Example: 5 steps = ~5-6 hours total
- Example: 10 steps = ~8-12 hours total

### Error Recovery

If orchestration fails:
1. **Check progress state**: `cat docs/feature/{project-id}/.develop-progress.json`
2. **Review failure reason**: Look for `failed_phase` and `failure_reason`
3. **Fix issue**: Address rejection feedback or implementation error
4. **Re-run command**: `/nw:develop "{description}"` (resumes from failure point)

### Embedded Python Scripts

All enforcement scripts are embedded in this file - **DO NOT** create external .py files. Scripts are executed inline by the devop orchestrator using:
```bash
python3 -c "$(cat << 'SCRIPT'
# Embedded Python script here
SCRIPT
)"
```

This ensures:
- No external dependencies
- Scripts always available
- Version control with command specification
- Runtime enforcement cannot be bypassed

---

**End of DW-DEVELOP Command Specification**
