# DES Discovery Report: SubagentStop Hook and max_turns Empirical Testing

**Date:** 2026-01-22
**Branch:** `determinism`
**Status:** CRITICAL FINDINGS - Design Assumptions Invalid

---

## Executive Summary

Empirical testing of Claude Code hook mechanisms revealed **two critical findings** that invalidate key assumptions in the DES design:

| Assumption | Reality | Impact |
|------------|---------|--------|
| Task tool accepts `max_turns` parameter | **FALSE** - `max_turns` is CLI flag only | HIGH - No programmatic turn limit |
| SubagentStop hook fires reliably | **UNCLEAR** - Hook did not fire in testing | HIGH - Post-execution validation uncertain |

---

## Discovery 1: max_turns Is NOT a Task Tool Parameter

### Source
Official Claude Code documentation via claude-code-guide agent research.

### Finding

The `--max-turns` flag is a **CLI-only feature** for non-interactive (print) mode:

```bash
# This works - CLI flag
claude -p "Fix errors" --max-turns 3

# This does NOT work - not a Task tool parameter
Task(prompt="...", max_turns=50)  # ❌ INVALID
```

### Documentation Quote

> `--max-turns`: Limit the number of agentic turns (**print mode only**). Exits with an error when the limit is reached. No limit by default.

### Impact on DES Design

All references to `max_turns` in Task tool invocations must be removed:

- ❌ "max_turns limit on Task invocations"
- ❌ "Set max_turns based on expected complexity"
- ❌ Timeout strategy "Mechanism 1: max_turns Parameter"

### See Also
[des-critical-finding-max-turns.md](des-critical-finding-max-turns.md) for detailed analysis and alternative strategies.

---

## Discovery 2: SubagentStop Hook May Not Fire in VSCode Context

### Test Setup

1. Created discovery hook script: `nWave/hooks/discover_subagent_context.py`
2. Configured in `.claude/settings.local.json`:

```json
{
  "hooks": {
    "SubagentStop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "python3 \"$CLAUDE_PROJECT_DIR/nWave/hooks/discover_subagent_context.py\"",
            "timeout": 30
          }
        ]
      }
    ]
  }
}
```

3. Ran multiple Task tool invocations

### Test Results

| Test | Task Type | Result |
|------|-----------|--------|
| Test 1 | Explore agent (haiku) | Hook did NOT fire |
| Test 2 | Explore agent (haiku) | Hook did NOT fire |
| Test 3 | Explore agent (haiku) | Hook did NOT fire |
| Manual | echo JSON \| python3 script | Script works correctly |

### Possible Explanations

1. **Settings require session restart** - Configuration changes may not be hot-reloaded
2. **VSCode extension handles hooks differently** - Environment variable `CLAUDE_CODE_ENTRYPOINT: "claude-vscode"` suggests different execution context
3. **SubagentStop may not fire for Explore agents** - May only fire for certain agent types
4. **Hook path resolution issue** - Even with `$CLAUDE_PROJECT_DIR`, path may not resolve correctly

### Evidence of Script Correctness

Manual test confirms the Python script works:

```bash
echo '{"session_id": "test", "hook_event_name": "SubagentStop"}' | python3 nWave/hooks/discover_subagent_context.py
# Output: {"continue": true}
# Files created in .git/des-discovery/
```

### Impact on DES Design

The SubagentStop hook was planned as **Gate 2** for post-execution validation. If the hook doesn't fire reliably:

- Post-execution validation cannot be guaranteed
- Abandoned IN_PROGRESS phases may go undetected
- State corruption may not be caught until pre-commit

---

## Discovery 3: Hook Input Schema (From Documentation)

Even though the hook didn't fire, documentation confirms the expected input schema:

```json
{
  "session_id": "string",
  "transcript_path": "string",
  "cwd": "string",
  "permission_mode": "string",
  "hook_event_name": "SubagentStop",
  "stop_hook_active": boolean
}
```

### Critical Observation

**The prompt is NOT included in hook input.**

This means:
- We CANNOT identify which step file was being processed from hook input
- We MUST embed identifiers (like `DES-STEP-FILE`) in the prompt AND write to a known location
- The transcript file is the only way to discover what the agent was doing

### Fallback Strategy

If hook doesn't receive step file info directly, we need:

```python
# Before Task invocation, write to known location
ACTIVE_STEP_FILE = ".git/des-active-step.json"

def before_task_invoke(step_path: str):
    with open(ACTIVE_STEP_FILE, "w") as f:
        json.dump({
            "step_file": step_path,
            "started_at": datetime.now().isoformat()
        }, f)

# SubagentStop hook reads from ACTIVE_STEP_FILE
```

---

## Discovery 4: Environment Variables Available

From documentation, hooks receive:

| Variable | Description |
|----------|-------------|
| `CLAUDE_PROJECT_DIR` | Absolute path to project root |
| `CLAUDE_ENV_FILE` | Path to persist env vars (SessionStart only) |
| `CLAUDE_CODE_REMOTE` | "true" if remote session |

Additionally observed in our environment:
- `CLAUDE_CODE_ENABLE_SDK_FILE_CHECKPOINTING`: "true"
- `CLAUDE_AGENT_SDK_VERSION`: "0.2.15"
- `CLAUDE_CODE_ENTRYPOINT`: "claude-vscode"

---

## Recommendations

### Immediate Actions

1. **Test in CLI mode** - Verify if hooks work differently outside VSCode
2. **Restart session** - Test if hooks load after full restart
3. **Try Stop hook instead** - Test if parent `Stop` hook fires (may cascade to subagents)

### Design Revisions Required

| DES Layer | Required Change |
|-----------|-----------------|
| Layer 2 (Templates) | Remove max_turns references |
| Layer 3 (Lifecycle) | Replace max_turns with prompt-based discipline |
| Layer 4 (Validation) | Add fallback if SubagentStop unreliable |

### Alternative Validation Strategy

If SubagentStop proves unreliable, consider:

1. **Pre-Commit as Primary Gate** - Move validation weight to commit time
2. **External Watchdog** - Independent process monitoring step file activity
3. **Checkpoint File Pattern** - Write to known location before/after Task

---

## Test Artifacts

| File | Purpose |
|------|---------|
| `nWave/hooks/discover_subagent_context.py` | Discovery hook script |
| `.claude/settings.local.json` | Hook configuration |
| `docs/design/des-critical-finding-max-turns.md` | max_turns analysis |
| `docs/design/des-discovery-report.md` | This report |

---

## Next Steps

1. **Restart Claude Code session** and re-test hook firing
2. **Test in CLI mode** (`claude -p "..."`) to compare behavior
3. **Contact Anthropic** or search GitHub issues for SubagentStop reliability
4. **Update DES design** with findings and alternative strategies

---

## Conclusion

This empirical testing revealed that our design relied on two mechanisms that either don't exist (`max_turns` for Task tool) or may not work reliably (`SubagentStop` hook in VSCode).

The DES design must be revised to:
1. Use prompt-based execution discipline instead of programmatic turn limits
2. Implement fallback validation strategies that don't depend on SubagentStop
3. Strengthen pre-commit validation as the reliable final gate

**The design is NOT ready for implementation until these issues are resolved.**

---

*Report generated from empirical testing session on determinism branch.*
