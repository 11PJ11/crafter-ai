# NW-VERSION: Framework Version Check

**Command**: `/nw:version`

## Purpose

Display the current nWave framework version and build information to verify the installation is up-to-date.

## Usage

```bash
/nw:version
```

## Output

When invoked, display the following information:

```
nWave Framework
===============
Version: 1.6.46
Build: 2026-02-07T00:08:34Z
Agents: 24
Commands: 21

Key Features:
- Task tool delegation for sub-commands
- Complete TDD cycle methodology (tracked in execution-log.yaml)
- step_type support (atdd, research, infrastructure)

Verification Markers:
- execute.md: Contains "Single Source of Truth" reference
- develop.md: Contains "/nw:execute @nw-software-crafter" delegation pattern
```

## Verification Instructions

To verify you have the latest version:

1. **Check TDD Cycle**: The execute command should reference `execution-log.yaml` as phase tracking format
2. **Check Task Delegation**: The develop command should use `Task(subagent_type=..., prompt='/nw:...')` pattern
3. **Check Agent Count**: Should have 24 agents and 21 commands (v1.6.0 includes Luna & Eclipse)

## Quick Test

Ask Claude Code to show:
```
grep "Single Source of Truth" from execute.md
```

Expected result: Reference to `execution-log.yaml` event format
