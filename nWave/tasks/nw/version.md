# NW-VERSION: Framework Version Check

**Command**: `/nw:version`

## Overview

Display the current nWave framework version and build information.

## Output

When invoked, display:

```
nWave Framework
===============
Version: 1.6.46
Build: 2026-02-07T00:08:34Z
Agents: 24
Commands: 21

Key Features:
- Task tool delegation for sub-commands
- TDD cycle methodology (tracked in execution-log.yaml)
- step_type support (atdd, research, infrastructure)

Verification Markers:
- execute.md: Contains "Single Source of Truth" reference
- develop.md: Contains "/nw:execute @nw-software-crafter" delegation pattern
```

## Verification

1. **TDD Cycle**: execute command references `execution-log.yaml` as phase tracking format
2. **Task Delegation**: develop command uses `Task(subagent_type=..., prompt='/nw:...')` pattern
3. **Agent Count**: 24 agents and 21 commands (v1.6.0 includes Luna and Eclipse)
