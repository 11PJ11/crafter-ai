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
Version: 1.2.84
Build: 2026-01-27T22:16:18Z
Agents: 22
Commands: 20

Key Features:
- Task tool delegation for sub-commands
- 14-phase TDD methodology (single source: step-tdd-cycle-schema.json)
- step_type support (atdd, research, infrastructure)

Verification Markers:
- execute.md: Contains "Single Source of Truth" reference
- develop.md: Contains "/nw:execute @software-crafter" delegation pattern
```

## Verification Instructions

To verify you have the latest version:

1. **Check 14 TDD Phases**: The execute command should reference `step-tdd-cycle-schema.json` as single source of truth
2. **Check Task Delegation**: The develop command should use `Task(subagent_type=..., prompt='/nw:...')` pattern
3. **Check Agent Count**: Should have 22 agents and 20 commands

## Quick Test

Ask Claude Code to show:
```
grep "Single Source of Truth" from execute.md
```

Expected result: Reference to `nWave/templates/step-tdd-cycle-schema.json`
