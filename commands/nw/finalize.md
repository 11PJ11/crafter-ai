---
description: 'Summarize achievements, archive to docs/evolution, clean up feature files [agent] [project-id] - Example: @devop "auth-upgrade"'
argument-hint: '[agent] [project-id] - Example: @devop "auth-upgrade"'
---

# /finalize Command

**Wave**: UNKNOWN
**Description**: Summarize achievements, archive to docs/evolution, clean up feature files

**Expected Outputs**: evolution_document

## Implementation
# DW-FINALIZE: Feature Completion, Archive, and Prepare for Push

---
## ORCHESTRATOR BRIEFING (MANDATORY)

**CRITICAL ARCHITECTURAL CONSTRAINT**: Sub-agents launched via Task tool have NO ACCESS to the Skill tool. They can ONLY use: Read, Write, Edit, Bash, Glob, Grep.

### What Orchestrator Must Do

When delegating this command to an agent via Task tool:

1. **Do NOT pass `/nw:finalize`** to the agent - they cannot execute it
2. **Create a complete agent prompt** with all instructions embedded inline
3. **Include**: project ID, feature directory path, evolution document path
4. **Embed**: archival steps, evolution document structure, cleanup requirements

### Agent Prompt Template

```text
You are a devop agent finalizing and archiving a completed feature.

PROJECT: {project_id}
INPUT DIRECTORY: docs/feature/{project_id}/
OUTPUT FILE: docs/evolution/{project_id}-evolution.md

YOUR TASK: Archive the completed feature by:
1. Create evolution document summarizing achievements
2. Move/archive workflow files (baseline.yaml, roadmap.yaml, step files)
3. Update any project tracking documents
4. Clean up temporary files

[Include evolution document structure and deliverables]
```

### What NOT to Include in Agent Prompts

- ❌ `/nw:finalize`
- ❌ Any skill or command reference
- ❌ References to continuing to other commands

---

## CRITICAL: Agent Invocation Protocol

**YOU ARE THE COORDINATOR** - Do NOT finalize the project yourself. Your role is to dispatch to the appropriate agent.

### STEP 1: Extract Agent Parameter

Parse the first argument to extract the agent name:
- User provides: `/nw:finalize @devop "auth-upgrade"`
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
- This should match the project-id in the feature directory

### Parameter Parsing Rules

Apply these rules to ALL extracted parameters:
1. Strip leading and trailing whitespace
2. Remove surrounding quotes (single or double) if present
3. Validate parameter is non-empty after stripping
4. Reject if extra parameters provided beyond expected count

Example for finalize.md:
- Input: `/nw:finalize  @devop  "auth-upgrade"`
- After parsing:
  - agent_name = "devop" (whitespace trimmed)
  - project_id = "auth-upgrade" (quotes removed)
- Input: `/nw:finalize @devop "auth-upgrade" extra`
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

### STEP 4.5: CRITICAL INVARIANT - All Steps Must Be Complete (HARD BLOCKER)

**THIS IS A NON-NEGOTIABLE GATE. IF IT FAILS, FINALIZE MUST NOT PROCEED.**

Before any finalization work begins, verify the critical invariant:

```
∀ step ∈ docs/feature/{project-id}/steps/*.json:
    step.tdd_cycle.phase_execution_log[COMMIT].outcome == "PASS"
```

**Validation via Python script**:

```python
import json
import glob
import os
import sys

def validate_all_steps_complete(project_id):
    """CRITICAL INVARIANT GATE: Verify ALL steps complete."""
    steps_dir = f"docs/feature/{project_id}/steps"

    if not os.path.exists(steps_dir):
        return False, [], f"BLOCKER: Steps directory not found"

    step_files = sorted(glob.glob(os.path.join(steps_dir, "*.json")))

    if not step_files:
        return False, [], f"BLOCKER: No step files found"

    incomplete_steps = []

    for step_file in step_files:
        try:
            with open(step_file, 'r') as f:
                step_data = json.load(f)
        except Exception as e:
            incomplete_steps.append({'file': os.path.basename(step_file), 'reason': f'Error: {str(e)}'})
            continue

        task_id = step_data.get('task_specification', {}).get('task_id', 'unknown')
        tdd_cycle = step_data.get('tdd_cycle', {})
        phase_log = tdd_cycle.get('phase_execution_log', [])

        if not phase_log:
            incomplete_steps.append({'task_id': task_id, 'reason': 'Invalid: empty phase_execution_log'})
            continue

        commit_phase = next((p for p in phase_log if p.get('phase_name') == 'COMMIT'), None)

        if not commit_phase:
            incomplete_steps.append({'task_id': task_id, 'reason': 'Missing COMMIT phase'})
            continue

        if commit_phase.get('outcome') != 'PASS':
            incomplete_steps.append({'task_id': task_id, 'reason': f"COMMIT outcome={commit_phase.get('outcome')} (expected PASS)"})

    if incomplete_steps:
        error_lines = [
            "",
            "=" * 70,
            "🛑 CRITICAL INVARIANT VIOLATION - FINALIZE BLOCKED",
            "=" * 70,
            "",
            f"Project: {project_id}",
            f"Incomplete steps: {len(incomplete_steps)} / {len(step_files)}",
            "",
            "The following steps do NOT have COMMIT phase with outcome=PASS:",
            ""
        ]

        for step in incomplete_steps:
            error_lines.append(f"  ❌ {step.get('task_id')}: {step['reason']}")

        error_lines.extend([
            "",
            "RESOLUTION REQUIRED:",
            "  1. Execute all incomplete steps through full 14-phase TDD",
            "  2. Ensure each step reaches COMMIT phase with outcome=PASS",
            "  3. Re-run /nw:finalize after all steps complete",
            "",
            "This gate exists to prevent 'silent completion' where features",
            "are archived without actually being implemented.",
            "",
            "=" * 70,
        ])

        return False, incomplete_steps, "\n".join(error_lines)

    return True, [], f"✅ CRITICAL INVARIANT PASSED: All {len(step_files)} steps complete"
```

**Gate Execution**:

1. **RUN the validation** with actual project ID
2. **IF FAILS**: STOP IMMEDIATELY - do NOT invoke agent
   - Report error to user
   - User must complete incomplete steps first
3. **IF PASSES**: Proceed to STEP 5

---

### STEP 5: Invoke Agent Using Task Tool

**MANDATORY**: Use the Task tool to invoke the specified agent. Do NOT attempt to finalize the project yourself.

## Overview

Invokes an agent to create a comprehensive summary of completed workflow, archive it for historical tracking, and clean up all intermediary working files.

---

**Document Owner**: nWave Framework
**Reviewed**: 2026-01-24
