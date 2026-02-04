# CLAUDE.md - Project Instructions

## Task Tool Safety (MANDATORY)

**CRITICAL**: Always include `max_turns` when invoking the Task tool.

```python
# CORRECT - Always specify max_turns
Task(
    subagent_type="...",
    prompt="...",
    max_turns=35  # MANDATORY
)

# WRONG - Never omit max_turns
Task(
    subagent_type="...",
    prompt="..."
    # Missing max_turns = potential runaway!
)
```

### Default Limits

| Task Type | max_turns |
|-----------|-----------|
| Quick edit | 15 |
| Background task | 25 |
| Research | 30 |
| Standard task | 35 |
| Complex refactoring | 50 |

### Why This Matters

An unbounded background agent caused:
- 64 context compactions (ran out of context 64 times)
- 76 redundant file reads (~1M wasted input tokens)
- 5 hours runtime for 5 actual edits
- 60% of daily token budget consumed

### Anti-Patterns to Avoid

1. **Unbounded background agents**: Always set `max_turns` for `run_in_background=True`
2. **Broad file tasks**: Don't ask to "reduce entire file" - specify exact sections/lines
3. **Large file edits**: Split into multiple smaller focused tasks

See: `nWave/data/config/task-safety.yaml` for full configuration.
