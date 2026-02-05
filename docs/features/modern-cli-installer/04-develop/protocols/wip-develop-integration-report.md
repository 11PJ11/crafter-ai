# WIP Contract + /nw:develop Integration Report

> This report documents how to integrate the WIP.yaml contract pattern
> into the /nw:develop command. Implementation should happen in a dedicated
> "WIP" branch, NOT in the installer branch.

## Status

- **Report date:** 2026-02-05
- **Target branch:** WIP (to be created from master)
- **Protocol version:** WIP v0.1 experimental -> v0.2 integrated
- **Validated in:** modern-cli-installer Phases 01 and 07 (17 steps, 0 hallucinations)

## Problem Statement

`/nw:develop` Phase 2 (Execute All Steps) passes step context inline via Task prompt:

```
Orchestrator reads roadmap -> extracts ~5k context -> embeds in Task prompt -> agent executes
```

Issues:
1. **Invisible context**: Hidden in prompt, not inspectable
2. **No resume**: Context lost on session break or context compaction
3. **Agent self-reporting**: Agent updates execution-status.yaml, no independent verification
4. **Drift risk**: Agent can read roadmap and scope-creep to other steps

The WIP contract (validated in 17 steps, 0 hallucinations, 95% token savings) solves all four.

## Integration Point

Only `/nw:develop` Phase 2 changes. All other phases are untouched.

### File to Modify

`~/.claude/commands/nw/develop.md` (the /nw:develop skill definition)

### Section to Modify

Step 7.4 "Execute each step in order" (the core execution loop, approximately lines 1040-1094)

## Current Flow (develop.md Step 7.4)

```
FOR each step in sorted_steps:
  1. Check execution-status.yaml for skip (already completed?)
  2. Extract step context from roadmap.yaml (~5k tokens)
  3. Invoke Task(software-crafter, prompt="...inline context...")
  4. Agent executes, updates execution-status.yaml
  5. Check execution-status.yaml for COMMIT/PASS
  6. Update .develop-progress.json
```

## Proposed Flow (WIP-enhanced Step 7.4)

```
FOR each step in sorted_steps:
  1. Check execution-status.yaml for skip                     <- SAME
  2. Extract step context from roadmap.yaml (~5k tokens)      <- SAME
  3. GENERATE WIP.yaml from extracted context + constraints   <- NEW
  4. Invoke Task(software-crafter, "Read ONLY WIP.yaml")      <- CHANGED
  5. Agent reads WIP.yaml, executes, fills output section     <- CHANGED
  6. VERIFY: run pytest independently, check git log          <- NEW
  7. Read WIP.yaml output section for completion contract     <- NEW
  8. Update execution-status.yaml FROM WIP.yaml output        <- CHANGED
  9. Update .develop-progress.json                            <- SAME
```

## Detailed Changes

### Change 1: WIP Generation Function (NEW)

Insert after context extraction (step 2), before agent invocation:

```python
def generate_wip(project_id, step_def, phase_id, feature_path):
    """Generate WIP.yaml from roadmap step definition.

    Args:
        project_id: kebab-case project identifier
        step_def: step definition extracted from roadmap
        phase_id: current phase identifier
        feature_path: path to feature docs directory

    Returns:
        Path to generated WIP.yaml
    """
    wip = {
        'meta': {
            'generated_at': datetime.now().isoformat(),
            'generated_by': 'nwave-orchestrator',
            'project': project_id,
            'phase': phase_id,
            'schema_version': '0.2'
        },
        'step': {
            'id': step_def['id'],
            'name': step_def['name'],
            'agent': step_def.get('agent', step_def.get('suggested_agent', 'software-crafter')),
            'estimated_hours': step_def.get('estimated_hours', 2),
            'dependencies_satisfied': True
        },
        'input': {
            'source_file': infer_source_path(step_def),
            'test_file': step_def.get('scenario', '').split(' ')[0],  # first token is path
            'requirements': parse_criteria(step_def.get('criteria', '')),
            'architecture_notes': step_def.get('architecture_notes', [])
        },
        'constraints': {
            'max_tool_calls': 15,
            'must_run_tests': True,
            'fail_fast': True,
            'forbidden_actions': [
                'DO NOT read roadmap.yaml',
                'DO NOT read execution-status.yaml',
                'DO NOT implement other steps',
                'DO NOT modify WIP.yaml meta/step/input/constraints sections'
            ]
        },
        'output': {
            'status': None,
            'artifacts_created': [],
            'artifacts_modified': [],
            'test_command': None,
            'test_result': None,
            'commit_hash': None,
            'commit_message': None,
            'notes': None
        }
    }

    wip_path = f'{feature_path}/04-develop/WIP.yaml'
    write_yaml(wip_path, wip)
    return wip_path
```

### Change 2: Agent Invocation (MODIFIED)

Replace inline context prompt with WIP pointer:

```python
# OLD (develop.md lines ~1056-1076):
Task(
    subagent_type="software-crafter",
    prompt=f"""Execute step {step_id} with complete TDD cycle
    PROJECT: {project_id}
    DESCRIPTION: {step['description']}
    ACCEPTANCE CRITERIA: {step['acceptance_criteria']}
    ...(~5k tokens of inline context)..."""
)

# NEW:
wip_path = generate_wip(project_id, step_def, phase_id, feature_path)
Task(
    subagent_type=step_def.get('agent', 'software-crafter'),
    prompt=f"""Execute step {step_id} from the WIP contract.

    Read ONLY: {wip_path}

    Critical rules:
    1. DO NOT read roadmap.yaml or execution-status.yaml
    2. Follow TDD: tests first, then implementation
    3. Run pytest to verify
    4. Commit with conventional format
    5. Fill output section in WIP.yaml"""
)
```

### Change 3: Independent Verification (NEW)

Insert after agent returns, before updating execution-status.yaml:

```python
def verify_step_completion(wip_path):
    """Verify step completion independently.

    Does NOT trust agent's verbal report.
    Reads WIP.yaml output section + runs tests + checks git.

    Returns:
        (success: bool, checks: list[tuple[str, bool]])
    """
    wip = read_yaml(wip_path)
    output = wip.get('output', {})
    test_file = wip.get('input', {}).get('test_file', '')

    checks = []

    # 1. WIP output section filled
    checks.append(('output_filled', output.get('status') is not None))
    checks.append(('status_success', output.get('status') == 'success'))

    # 2. Run tests independently
    if test_file:
        result = run_bash(f'pytest {test_file} -v')
        checks.append(('tests_pass', result.returncode == 0))

    # 3. Check commit exists
    commit_hash = output.get('commit_hash')
    if commit_hash:
        result = run_bash(f'git log --oneline | head -1')
        checks.append(('commit_exists', commit_hash in result.stdout))
    else:
        checks.append(('commit_exists', False))

    success = all(passed for _, passed in checks)
    return success, checks
```

### Change 4: execution-status.yaml Update (MODIFIED)

Change who updates execution-status.yaml:

```python
# OLD: Agent updates execution-status.yaml during execution
# The agent writes to the file directly

# NEW: Orchestrator reads WIP output, updates execution-status.yaml
def update_execution_status_from_wip(exec_status_path, step_id, wip_path):
    """Update execution-status from verified WIP output.

    Trust boundary: orchestrator verifies first, then records.
    Agent never writes to execution-status.yaml.
    """
    wip = read_yaml(wip_path)
    output = wip['output']

    exec_status = read_yaml(exec_status_path)

    exec_status['completed_steps'].append({
        'step_id': step_id,
        'status': 'COMPLETED',
        'commit_hash': output.get('commit_hash'),
        'artifacts_created': output.get('artifacts_created', []),
        'artifacts_modified': output.get('artifacts_modified', []),
        'test_result': output.get('test_result'),
        'completed_at': datetime.now().isoformat()
    })

    write_yaml(exec_status_path, exec_status)
```

## What Does NOT Change

| Component | Status | Reason |
|-----------|--------|--------|
| Phase 1: Roadmap Creation + Review | Unchanged | WIP only affects step execution |
| Phase 2.25: Refactoring + Mutation | Unchanged | Runs after all steps, reads execution-status |
| Phase 3: Finalize + Cleanup | Unchanged | Reads execution-status (now Vera-verified) |
| Phase 3.5: Retrospective | Unchanged | Post-execution analysis |
| Phase 4: Report | Unchanged | Summary display |
| .develop-progress.json | Unchanged | Orchestrator-level tracking |
| roadmap.yaml structure | Unchanged | Still source of truth for step definitions |
| execution-status.yaml schema | Unchanged | Same fields, different writer |

## Parallel Steps Enhancement

Current WIP is singleton. For parallel steps, use named files:

```
docs/feature/{project-id}/04-develop/
  WIP-01-03.yaml   # Step 01-03
  WIP-01-04.yaml   # Step 01-04 (parallel with 01-03)
```

Agent invocation points to specific file:
```python
Task(..., prompt=f"Read ONLY: {feature_path}/04-develop/WIP-{step_id}.yaml")
```

Orchestrator generates multiple WIPs, launches multiple Tasks, verifies each independently.

## Path Convention

Current mismatch between /nw:develop and this project:
- `/nw:develop` uses: `docs/feature/{project-id}/` (singular)
- This project uses: `docs/features/{project-id}/` (plural)

Recommendation: Make path configurable in roadmap.yaml:
```yaml
execution_config:
  feature_path: "docs/features/modern-cli-installer"  # project-specific
  status_tracking_file: "execution-status.yaml"
```

## Token Impact Analysis

| Metric | Current /nw:develop | WIP-enhanced |
|--------|---------------------|--------------|
| Prompt per step | ~5k (inline context) | ~500 (WIP pointer) |
| Roadmap reads by agent | 1 per step (agent reads) | 0 (forbidden) |
| Total for 8 steps | ~40k agent context | ~4k agent context |
| Drift risk | Medium (agent sees full roadmap) | None (forbidden_actions) |
| Verification cost | 0 (trusts agent) | ~200 tokens (independent pytest) |

## Validation Plan

After implementing in WIP branch:

1. Execute a single step (e.g., 09-01) using WIP-enhanced flow
2. Verify WIP.yaml generated correctly from roadmap
3. Verify agent reads only WIP.yaml (check forbidden_actions work)
4. Verify independent verification catches real failures
5. Verify execution-status.yaml updated from WIP output (not agent)
6. Compare token usage vs inline approach
7. Run 3+ steps to validate consistency

## Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| WIP.yaml generation misses context | Medium | High | Extract from roadmap + architecture doc |
| Agent ignores forbidden_actions | Low | Medium | Verify WIP.yaml output matches actual git |
| Parallel WIP files conflict | Low | Low | Named files prevent overwrites |
| Path convention mismatch | High | Low | Add feature_path to execution_config |

## Implementation Checklist (for WIP branch)

- [ ] Create WIP branch from master
- [ ] Modify develop.md Step 7.4 with WIP generation
- [ ] Add generate_wip() function (or pseudocode pattern)
- [ ] Add verify_step_completion() function
- [ ] Add update_execution_status_from_wip() function
- [ ] Update agent invocation template
- [ ] Add parallel WIP file convention
- [ ] Add feature_path to execution_config schema
- [ ] Test with one step end-to-end
- [ ] Validate token savings measurement
- [ ] Update wip-contract-protocol.md to v0.2
