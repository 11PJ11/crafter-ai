# nWave Git Hooks

This directory contains git hooks for the nWave 14-phase TDD methodology.

**IMPORTANT**: These hooks are templates that get installed in target projects when running `/nw:develop`. They are NOT active in this ai-craft repository.

## Build-Time Embedding

The hook scripts in this directory are the **single source of truth**. During the build process, they are automatically embedded into documentation and task files.

### How It Works

1. **Source files**: Edit hooks directly in `nWave/hooks/`
2. **Build step**: Run `python tools/embed_sources.py`
3. **Target files**: Files with embed markers (e.g., `develop.md`) get updated automatically

### Marker Format

Target files use markers to indicate where hooks should be embedded:

```markdown
<!-- EMBED_START:nWave/hooks/pre_commit_tdd_phases.py:python_string -->
(content will be replaced by embedding script)
<!-- EMBED_END:nWave/hooks/pre_commit_tdd_phases.py -->
```

### Supported Formats

| Format | Description |
|--------|-------------|
| `python_string` | Escape as Python multiline string variable |
| `markdown_code` | Wrap in markdown code fence with syntax highlighting |
| `raw` | Insert file content as-is |

### Running the Embedding

```bash
# Embed into all target files
python tools/embed_sources.py

# Preview changes without modifying
python tools/embed_sources.py --dry-run

# Verbose output
python tools/embed_sources.py --verbose

# Specific file only
python tools/embed_sources.py nWave/tasks/nw/develop.md
```

### Workflow

1. Modify hook file in `nWave/hooks/`
2. Run `python tools/embed_sources.py`
3. Commit both source files AND embedded targets
4. Target files will have updated embedded code

## Available Hooks

### pre_commit_tdd_phases.py

**Purpose**: Validates that all TDD phases are completed before allowing commits on step files.

**Language**: Python 3 (cross-platform: Windows, Mac, Linux)

**Dependencies**: None (uses only Python standard library)

**What it validates**:
- All 14 phases present in phase_execution_log
- All phases have status "EXECUTED" or valid "SKIPPED"
- No phases left "IN_PROGRESS" (indicates interrupted execution)
- No phases left "NOT_EXECUTED" (indicates skipped without justification)
- SKIPPED phases have valid blocked_by prefix
- DEFERRED prefix blocks commit

**Installation**:
- **Automatic**: Run `/nw:develop` and accept the hook installation prompt
- **Manual**:
  ```bash
  # Unix/Mac - create wrapper script
  cat > .git/hooks/pre-commit << 'EOF'
  #!/bin/sh
  python3 "path/to/nWave/hooks/pre_commit_tdd_phases.py" "$@"
  EOF
  chmod +x .git/hooks/pre-commit

  # Windows - create .git/hooks/pre-commit (no extension)
  # with content:
  # python3 "path\to\nWave\hooks\pre_commit_tdd_phases.py" %*
  ```

**Bypass** (not recommended - will be logged):
```bash
git commit --no-verify
```

### post_commit_bypass_logger.py

**Purpose**: Detects and logs when pre-commit validation was bypassed using `--no-verify`.

**Language**: Python 3 (cross-platform)

**Dependencies**: None

**What it does**:
- Checks if pre-commit validation marker exists
- If marker missing for commits with step files, logs bypass event
- Writes bypass log to `.git/nwave-bypass.log`
- Displays warning to stderr

**Installation**: Same as pre_commit_tdd_phases.py but for post-commit hook.

## Hook Architecture

```
Commit Attempt
     |
     v
+-----------------------------+
|  .git/hooks/pre-commit      |
|  (shell wrapper)            |
+-------------+---------------+
              |
              v
+-----------------------------+
|  pre_commit_tdd_phases.py   |
|  (Python validation)        |
+-----------------------------+
|  1. Get staged step files   |
|  2. For each step file:     |
|     - Load JSON             |
|     - Check all 14 phases   |
|     - Verify status valid   |
|  3. Block if incomplete     |
|  4. Write validation marker |
+-------------+---------------+
              |
    +---------+---------+
    |                   |
 ALL OK            INCOMPLETE
    |                   |
    v                   v
 COMMIT OK        BLOCKED
                  (exit code 1)
              |
              v
+-----------------------------+
| .git/hooks/post-commit      |
| (if commit succeeded)       |
+-----------------------------+
| post_commit_bypass_logger.py|
| - Check validation marker   |
| - If missing: log bypass    |
+-----------------------------+
```

## Valid SKIPPED Prefixes

When a phase cannot be completed, use status "SKIPPED" with a valid `blocked_by` prefix:

| Prefix | Allows Commit | Description |
|--------|---------------|-------------|
| `BLOCKED_BY_DEPENDENCY:` | Yes | External dependency unavailable |
| `NOT_APPLICABLE:` | Yes | Phase not applicable for this task type |
| `APPROVED_SKIP:` | Yes | Skip explicitly approved by reviewer |
| `DEFERRED:` | **No** | Incomplete work - must be resolved |

Example:
```json
{
  "phase_name": "RED_UNIT",
  "status": "SKIPPED",
  "blocked_by": "NOT_APPLICABLE: Documentation-only change, no unit tests needed"
}
```

## Bypass Log Format

Bypass events are logged to `.git/nwave-bypass.log` as JSON lines:

```json
{
  "timestamp": "2024-01-15T10:30:00Z",
  "event": "BYPASS_DETECTED",
  "reason": "Pre-commit hook bypassed (--no-verify)",
  "user": "developer",
  "email": "dev@example.com",
  "branch": "feature/auth",
  "commit_hash": "abc123def456",
  "step_files": ["docs/feature/auth/steps/01-01.json"]
}
```

## Troubleshooting

### "Python not found"

The hooks require Python 3. Ensure `python3` is in your PATH:
```bash
python3 --version
```

### Hook not running

Verify the hook is executable:
```bash
# Unix/Mac
ls -la .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit

# Windows
# Ensure file exists and has correct shebang
```

### False positives

If the hook blocks a valid commit:
1. Check the step file JSON is valid
2. Verify all phases have correct status
3. Check for typos in phase names
4. Run migration script if file format is outdated:
   ```bash
   python nWave/scripts/migrate_step_files.py
   ```

### "File needs migration"

Step files created before v2.0.0 may not have the 14-phase skeleton. Run:
```bash
python nWave/scripts/migrate_step_files.py --dry-run  # Preview
python nWave/scripts/migrate_step_files.py           # Apply
```

## Related Scripts

- `nWave/scripts/migrate_step_files.py` - Migrate existing step files to 14-phase format
- `nWave/scripts/validate_tdd_phases_ci.py` - CI/CD validation script

## Adding New Hooks

To add a new nWave hook:
1. Create Python script in `nWave/hooks/`
2. Document in this README
3. Add installation logic to relevant `/nw:*` command
4. Update the hook installation functions in `develop.md`
