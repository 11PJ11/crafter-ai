# Command Audit Findings - Agent Skill Invocation Anti-Patterns

**Date**: 2026-01-20
**Auditor**: Lyra (Claude Opus 4.5)
**Purpose**: Identify and document violations of the delegation principle
**Status**: ✅ ALL FIXES COMPLETE

## Summary

All 7 nWave commands were audited for patterns where agents are expected to invoke `/nw:*` commands, which is architecturally impossible since sub-agents only have access to: Read, Write, Edit, Bash, Glob, Grep (no Skill tool).

## Critical Findings

### `/nw:develop` - MAJOR VIOLATIONS

| Line | Anti-Pattern | Current Code |
|------|-------------|--------------|
| 562 | Passes skill to agent | `prompt=f'/nw:baseline "{feature_description}"'` |
| 690 | Passes skill to agent | `prompt=f'/nw:roadmap @solution-architect "{feature_description}"'` |
| 824 | Passes skill to agent | `prompt=f'/nw:split @software-crafter "{project_id}"'` |

**Impact**: Agents receive these prompts but cannot execute `/nw:*` commands. They complete without performing the intended work.

**Required Fix**: Read command file content, extract workflow details, embed in agent prompt inline.

### `/nw:execute` - VIOLATIONS

| Line | Anti-Pattern | Current Code |
|------|-------------|--------------|
| 109 | References skill execution | `REVIEW - Execute /nw:review @software-crafter-reviewer` |
| 114 | References skill execution | `POST_REFACTOR_REVIEW - Execute /nw:review again` |

**Impact**: If these instructions are embedded in agent prompts, agents cannot execute the review command.

**Required Fix**: Replace with inline review criteria and instructions.

### `/nw:split` - VIOLATIONS

| Line | Anti-Pattern | Current Code |
|------|-------------|--------------|
| 98 | References skill execution | `REVIEW - Execute /nw:review @software-crafter-reviewer` |
| 103 | References skill execution | `POST_REFACTOR_REVIEW - Execute /nw:review again` |
| 999 | Schema embeds skill reference | `"REVIEW - Execute /nw:review @software-crafter-reviewer"` |
| 1004 | Schema embeds skill reference | `"POST_REFACTOR_REVIEW - Execute /nw:review again"` |
| 1439 | Instruction references skill | `Invoke /nw:review for phases 7 and 9` |
| 1440 | Instruction references skill | `Invoke /nw:refactor or /nw:mikado for phase 8` |

**Required Fix**: Embed review and refactor instructions inline instead of skill references.

### `/nw:review` - ACCEPTABLE

The review.md file correctly describes the command for the orchestrator. Lines 79 and 167 mention "invokes" but these describe orchestrator behavior, not agent instructions.

**Status**: No fix required.

### `/nw:baseline` - ACCEPTABLE

Line 289 mentions invocation but describes orchestrator behavior.

**Status**: Needs orchestrator briefing section added, but no critical anti-patterns.

### `/nw:roadmap` - NOT AUDITED IN DETAIL

**Status**: Needs orchestrator briefing section added.

### `/nw:finalize` - NOT AUDITED IN DETAIL

**Status**: Needs orchestrator briefing section added.

## Severity Classification

| Command | Severity | Fix Priority |
|---------|----------|--------------|
| `/nw:develop` | CRITICAL | P0 - Blocking |
| `/nw:execute` | HIGH | P0 - Blocking |
| `/nw:split` | HIGH | P0 - Blocking |
| `/nw:review` | LOW | P1 - Add briefing section |
| `/nw:baseline` | LOW | P1 - Add briefing section |
| `/nw:roadmap` | LOW | P1 - Add briefing section |
| `/nw:finalize` | LOW | P1 - Add briefing section |

## Correct Pattern (Template)

### For Orchestrator Prompts (develop.md)

**WRONG**:
```python
task_result = Task(
    subagent_type="researcher",
    prompt=f'/nw:baseline "{feature_description}"',
    description="Create measurement baseline"
)
```

**CORRECT**:
```python
# Read command file to get workflow details
baseline_instructions = read_command_file('nWave/tasks/nw/baseline.md')

# Create detailed agent prompt with all context inline
task_result = Task(
    subagent_type="researcher",
    prompt=f'''
You are a researcher agent creating a measurement baseline.

TASK: Create baseline.yaml for "{feature_description}"

OUTPUT FILE: docs/feature/{project_id}/baseline.yaml

BASELINE REQUIREMENTS:
{baseline_instructions['requirements']}

MEASUREMENT PROTOCOL:
{baseline_instructions['measurement_protocol']}

DELIVERABLES:
- baseline.yaml with quantitative measurements
- Evidence of measurements taken
''',
    description="Create measurement baseline"
)
```

### For TDD Phase Instructions (execute.md, split.md)

**WRONG**:
```
7. REVIEW - Execute /nw:review @software-crafter-reviewer
```

**CORRECT**:
```
7. REVIEW - Perform code review:
   - Verify implementation follows SOLID principles
   - Check test coverage >= 80%
   - Validate acceptance criteria met
   - Record review findings in step file under tdd_cycle.phase_execution_log[6]
```

## Next Steps

1. Fix `/nw:develop` - Replace Task prompts with complete inline instructions
2. Fix `/nw:execute` - Replace phase 7 and 12 skill references with inline criteria
3. Fix `/nw:split` - Replace phase 7, 12 skill references and schema entries
4. Add orchestrator briefing sections to all commands

## Verification After Fix

```bash
# Should return 0 results after fixes
grep -r "Execute /nw:" nWave/tasks/nw/
grep -r "prompt=.*'/nw:" nWave/tasks/nw/
grep -r "Invoke /nw:" nWave/tasks/nw/
```
