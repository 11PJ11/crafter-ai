# DW-EXECUTE: Atomic Task Execution

**Wave**: EXECUTION_WAVE
**Agent**: Dispatched agent (specified by caller)

## Overview

Dispatch a single roadmap step to an agent for execution. The orchestrator extracts step context from the roadmap and passes it to the agent so the agent never loads the full roadmap (saves ~97k tokens per step).

## Syntax

```
/nw:execute @{agent} "{project-id}" "{step-id}"
```

## Context Files Required

- `docs/feature/{project-id}/roadmap.yaml` - Orchestrator reads once, extracts step context
- `docs/feature/{project-id}/execution-log.yaml` - Agent appends only (never reads)

## Dispatcher Workflow

1. Parse parameters: agent name, project ID, step ID
2. Validate roadmap and execution-log exist for the project
3. Grep roadmap for `step_id: "{step-id}"` with surrounding context (~50 lines)
4. Extract: name, description, acceptance_criteria, test_file, scenario_line, acceptance_test_scenario, quality_gates, implementation_notes, dependencies, estimated_hours, deliverables
5. Invoke Task tool with extracted context (see Agent Invocation below)

## Agent Invocation

@{agent}

Pass extracted step context as a self-contained prompt. The agent receives everything needed to execute without loading the roadmap.

**Prompt structure:**

```
PROJECT: {project-id}
STEP: {step-id}

## Step Context (extracted from roadmap)
[All fields from step 4 above]

## Execution Rules
- Do not load roadmap.yaml (context provided above)
- Append one event per phase to execution-log.yaml (never read it)
- Event format: "{step-id}|{phase}|{status}|{data}|{timestamp}"
- Phases: PREPARE, RED_ACCEPTANCE, RED_UNIT, GREEN, REVIEW, REFACTOR_CONTINUOUS, COMMIT
- After COMMIT, append FILES_MODIFIED events for each changed file
- Target: 30 turns maximum
```

**Configuration:**
- max_turns: 30
- subagent_type: extracted agent name

## Event Format

Append after each phase using Bash:
```bash
timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
echo '  - "{step-id}|{phase}|{status}|{data}|'$timestamp'"' >> docs/feature/{project-id}/execution-log.yaml
```

Status is EXECUTED (data: PASS, FAIL, UNEXPECTED_GREEN) or SKIPPED (data: NOT_APPLICABLE/APPROVED_SKIP/BLOCKED_BY_DEPENDENCY + reason).

## Error Handling

- Invalid agent: report available agents (nw-researcher, nw-software-crafter, nw-solution-architect, nw-product-owner, nw-acceptance-designer, nw-devop)
- Missing roadmap/execution-log: report path not found
- Step not in roadmap: report available step IDs
- Agent reports dependency failure: explain blocking tasks to user

## Examples

```bash
# Implementation step
/nw:execute @nw-software-crafter "des-us007-boundary-rules" "02-01"

# Research step
/nw:execute @nw-researcher "auth-upgrade" "01-01"

# Retry after failure (agent resumes from last completed phase)
/nw:execute @nw-software-crafter "des-us007" "03-01"
```

## TDD_7_PHASES
<!-- Schema v3.0 — canonical source: TDDPhaseValidator.MANDATORY_PHASES_V3 -->
<!-- Build system injects mandatory phases from step-tdd-cycle-schema.json -->
{{MANDATORY_PHASES}}

## Success Criteria

- [ ] Agent invoked via Task tool (dispatcher does not execute the work)
- [ ] Step context extracted from roadmap and passed in prompt
- [ ] Agent appended phase events to execution-log.yaml
- [ ] Agent did not load roadmap.yaml

## Next Wave

**Handoff To**: /nw:review for post-execution review
**Deliverables**: Updated execution-log.yaml, implementation artifacts, git commits
