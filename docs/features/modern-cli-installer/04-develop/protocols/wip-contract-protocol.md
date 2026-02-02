# WIP Contract Protocol v0.1 (Experimental)

> **Status:** EXPERIMENTAL - Developed during modern-cli-installer feature
> **Author:** Vera (Orchestrator) with Mike
> **Date:** 2026-02-02
> **Candidate for:** nWave v2.1 or v3.0

## Problem Statement

nWave v2.0 defines a **context extraction protocol** where the orchestrator extracts ~5k tokens per step from roadmap.yaml and passes to agents inline. This works but has limitations:

1. **Invisible context** - The extracted context lives only in the prompt, not inspectable
2. **No completion contract** - Agent reports completion verbally, orchestrator must trust or verify
3. **Drift risk** - Without physical boundaries, agents may read forbidden files
4. **Resume difficulty** - If session breaks mid-step, context must be reconstructed

## Solution: WIP.yaml as Physical Contract

The WIP (Work In Progress) contract is a **physical YAML artifact** that:
- Contains extracted context for exactly ONE step
- Lives at a known location (predictable path)
- Has explicit input/constraints/output sections
- Agent fills the output section upon completion
- Orchestrator verifies output before updating execution-status

## Schema Definition

```yaml
# ═══════════════════════════════════════════════════════════════════════════════
# WIP.yaml - Work In Progress Contract
# Schema Version: 0.1
# ═══════════════════════════════════════════════════════════════════════════════

meta:
  generated_at: "ISO-8601 timestamp"
  generated_by: "orchestrator-name"
  project: "project-id"
  phase: "phase-id"
  phase_name: "human readable phase name"
  schema_version: "0.1"

# ─────────────────────────────────────────────────────────────────────────────
# STEP CONTRACT - What is being executed
# ─────────────────────────────────────────────────────────────────────────────
step:
  id: "XX-YY"                    # Step identifier from roadmap
  name: "Step name"              # Human readable name
  agent: "agent-type"            # software-crafter | devop | researcher | etc.
  estimated_hours: N             # From roadmap
  dependencies_satisfied: bool   # Orchestrator verified dependencies

# ─────────────────────────────────────────────────────────────────────────────
# INPUT - What the agent receives (READ-ONLY for agent)
# ─────────────────────────────────────────────────────────────────────────────
input:
  # File paths for artifacts to create
  source_file: "path/to/source.py"           # Single file
  source_files: ["path1.py", "path2.py"]     # Multiple files
  test_file: "path/to/test.py"

  # Reference to existing code (for patterns, imports)
  existing_code:
    some_reference: "path/to/reference.py"
    imports: |
      from module import Class

  # Requirements extracted from roadmap step
  requirements:
    component_name:
      - "Requirement 1"
      - "Requirement 2"

  # Test requirements
  test_requirements:
    - "Test case 1"
    - "Test case 2"

  # Architecture context
  architecture_notes:
    - "Design decision 1"
    - "Pattern to follow"

# ─────────────────────────────────────────────────────────────────────────────
# CONSTRAINTS - Rules the agent MUST follow
# ─────────────────────────────────────────────────────────────────────────────
constraints:
  # Resource limits
  max_tool_calls: N              # Prevent infinite loops
  must_run_tests: bool           # Require pytest execution
  fail_fast: bool                # Stop on first failure

  # Allowed actions (whitelist)
  allowed_actions:
    - "Create source file at input.source_file"
    - "Create test file at input.test_file"
    - "Run pytest on test file"
    - "Commit changes"

  # Forbidden actions (blacklist) - CRITICAL for preventing drift
  forbidden_actions:
    - "DO NOT read roadmap.yaml"
    - "DO NOT read execution-status.yaml"
    - "DO NOT modify WIP.yaml (orchestrator does this)"
    - "DO NOT implement other steps"
    - "DO NOT add external dependencies"

# ─────────────────────────────────────────────────────────────────────────────
# OUTPUT - What the agent must deliver (AGENT FILLS THIS SECTION)
# ─────────────────────────────────────────────────────────────────────────────
output:
  status: null          # success | failed | blocked
  artifacts_created: [] # list of file paths created/modified
  test_command: null    # exact pytest command used
  test_result: null     # PASS: X tests | FAIL: reason
  commit_hash: null     # git commit hash (short form ok)
  commit_message: null  # conventional commit message used
  notes: null           # any issues, observations, or blockers
```

## Protocol Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│ ORCHESTRATOR                                                        │
├─────────────────────────────────────────────────────────────────────┤
│ 1. Read execution-status.yaml                                       │
│ 2. Identify next step (check dependencies satisfied)                │
│ 3. Extract step context from roadmap.yaml (~5k tokens)              │
│ 4. Generate WIP.yaml with input/constraints/empty output            │
│ 5. Write WIP.yaml to docs/{feature}/04-develop/WIP.yaml             │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│ AGENT INVOCATION                                                    │
├─────────────────────────────────────────────────────────────────────┤
│ Task(                                                               │
│   subagent_type="software-crafter",                                 │
│   prompt="""                                                        │
│     Execute step {step_id} from the WIP contract.                   │
│     Read ONLY: docs/{feature}/04-develop/WIP.yaml                   │
│     Follow TDD, run tests, fill output section, commit.             │
│   """                                                               │
│ )                                                                   │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│ AGENT EXECUTION                                                     │
├─────────────────────────────────────────────────────────────────────┤
│ 1. Read WIP.yaml (ONLY this file for context)                       │
│ 2. Execute step following input.requirements                        │
│ 3. Respect constraints.forbidden_actions                            │
│ 4. Run tests (if constraints.must_run_tests)                        │
│ 5. Fill output section in WIP.yaml                                  │
│ 6. Commit with conventional message                                 │
│ 7. Return summary to orchestrator                                   │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│ ORCHESTRATOR VERIFICATION                                           │
├─────────────────────────────────────────────────────────────────────┤
│ 1. Read WIP.yaml output section                                     │
│ 2. VERIFY tests pass (run pytest independently)                     │
│ 3. If verified:                                                     │
│    - Update execution-status.yaml (step completed)                  │
│    - Update summary statistics                                      │
│    - Generate next WIP.yaml (overwrite)                             │
│ 4. If failed:                                                       │
│    - Keep WIP.yaml with failed output                               │
│    - Report to user for decision                                    │
└─────────────────────────────────────────────────────────────────────┘
```

## File Location Convention

```
docs/features/{feature-name}/04-develop/
├── roadmap.yaml           # Strategic (all steps)
├── execution-status.yaml  # Tactical (progress tracking)
├── WIP.yaml               # Operational (current step only)
└── protocols/             # Experimental protocols
    └── wip-contract-protocol.md
```

**WIP.yaml is a SINGLETON** - Only one exists at a time. Overwritten for each new step.

## Benefits Over Inline Context

| Aspect | Inline (v2.0) | WIP.yaml (v2.1) |
|--------|---------------|-----------------|
| Visibility | Hidden in prompt | Inspectable file |
| Debugging | Reconstruct from logs | Open WIP.yaml |
| Constraints | Verbal instructions | Explicit YAML section |
| Completion | Trust agent report | Verify output section |
| Resume | Rebuild context | Read existing WIP.yaml |
| Audit trail | None | Git history of WIP.yaml |

## Integration with nWave v2.0

This protocol **extends** v2.0, not replaces it:

1. **roadmap.yaml** - Unchanged (source of truth for all steps)
2. **execution-status.yaml** - Unchanged (progress tracking)
3. **WIP.yaml** - NEW (extracted context + completion contract)

The context extraction protocol in develop.md remains valid. WIP.yaml is the **physical manifestation** of that extracted context.

## Metrics from First Usage (modern-cli-installer Phase 01)

| Metric | Value |
|--------|-------|
| Steps completed | 8 |
| Total time | 38 minutes |
| Avg per step | 4.7 minutes |
| Tests written | 115 |
| Agent stuck/loops | 0 |
| Hallucinated results | 0 (all verified) |
| Token savings | ~95% vs full roadmap per agent |

## Open Questions for v1.0

1. **Should WIP.yaml be git-committed?** Currently no (transient), but could be useful for audit
2. **Multi-agent steps?** Current design assumes one agent per step
3. **Reviewer integration?** Should reviewer also use WIP.yaml or separate contract?
4. **Parallel steps?** Could generate multiple WIP-{step_id}.yaml files

## Promotion Path to nWave Core

1. **Phase 1 (Current):** Experimental in feature docs
2. **Phase 2:** Validate with Alessandro on DES project
3. **Phase 3:** If validated, add to `~/.claude/templates/wip-contract-template.yaml`
4. **Phase 4:** Update `develop.md` to reference WIP protocol
5. **Phase 5:** Add schema validation (JSON Schema like TDD cycle)

## Changelog

- **v0.1 (2026-02-02):** Initial experimental protocol from modern-cli-installer Phase 01
