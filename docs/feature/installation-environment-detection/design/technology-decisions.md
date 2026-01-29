# Technology Decisions: Installation Environment Detection

**Feature ID:** APEX-002
**Wave:** DESIGN
**Created:** 2026-01-29

---

## ADR-001: Claude Code Context Detection Method

### Status
**ACCEPTED**

### Context
The installer needs to detect whether it's running in a terminal (human operator) or Claude Code (AI agent) to format output appropriately. Three options were evaluated:

| Option | Method | Description |
|--------|--------|-------------|
| A | Environment Variables | Check for `CLAUDE_CODE` or `CLAUDE_*` env vars |
| B | TTY Detection | Check if stdout is a TTY |
| C | Explicit Flag | Add `--json` command-line argument |

### Decision
**Use Option B (TTY Detection) with Option A as fallback.**

```python
def detect() -> ExecutionContext:
    # Option A: Explicit env var (future-proof)
    if os.environ.get('CLAUDE_CODE'):
        return ExecutionContext.CLAUDE_CODE

    # Option B: TTY detection (works today)
    if sys.stdout.isatty():
        return ExecutionContext.TERMINAL
    else:
        return ExecutionContext.CLAUDE_CODE
```

### Rationale

| Criterion | Option A | Option B | Option C |
|-----------|----------|----------|----------|
| Works today | No (requires Claude Code change) | **Yes** | Yes |
| Standard library only | Yes | **Yes** | Yes |
| No user action required | Yes | **Yes** | No |
| Unix convention | N/A | **Yes** (scripts detect pipes) | No |
| Future-proof | **Yes** | Partial | No |

**Option B wins** because:
1. Works immediately without any Claude Code modifications
2. Follows Unix convention (programs behave differently in pipes)
3. Standard library only (`sys.stdout.isatty()`)
4. Combined with Option A fallback, remains future-proof

### Consequences

**Positive:**
- Zero configuration required
- Works with current Claude Code
- Human users running `python install.py | tee log.txt` get JSON (acceptable)

**Negative:**
- Piped terminal commands get JSON output (rare edge case)
- Cannot distinguish Claude Code from other non-TTY contexts

**Mitigation:**
- Add `CLAUDE_CODE` env var check as primary (future-proof)
- Document behavior for edge cases

---

## ADR-002: Log File Location

### Status
**ACCEPTED**

### Context
Installation logs need a persistent location for debugging across multiple installation attempts. Options considered:

| Option | Location | Description |
|--------|----------|-------------|
| A | `~/.claude/nwave-install.log` | Inside Claude config |
| B | `~/.nwave/install.log` | Dedicated nWave directory |
| C | `./install.log` | Current working directory |
| D | `/tmp/nwave-install.log` | System temp directory |

### Decision
**Use Option B: `~/.nwave/install.log`**

### Rationale

| Criterion | Option A | Option B | Option C | Option D |
|-----------|----------|----------|----------|----------|
| Survives uninstall | No | **Yes** | Yes | No (temp cleaned) |
| User-discoverable | Yes | **Yes** | Depends on cwd | No |
| Cross-platform | Yes | **Yes** | Yes | Partial |
| Separates concerns | No (mixed with Claude) | **Yes** | No | N/A |
| Persistent | Yes | **Yes** | Depends | No |

**Option B wins** because:
1. Survives `uninstall_nwave.py` (useful for debugging reinstalls)
2. Clear separation from Claude Code configuration
3. User can easily find and share for support
4. Dedicated directory allows future expansion (cache, config)

### Consequences

**Positive:**
- Logs preserved after uninstall for troubleshooting
- Clean separation of concerns
- Extensible location for future nWave tooling

**Negative:**
- New directory created in user's home
- Must handle directory creation in preflight

**Implementation:**
```python
log_dir = Path.home() / '.nwave'
log_dir.mkdir(parents=True, exist_ok=True)
log_file = log_dir / 'install.log'
```

---

## ADR-003: Error Code Design

### Status
**ACCEPTED**

### Context
Errors need machine-readable codes for Claude Code self-healing. Design must be:
- Unique and descriptive
- Categorized by error type
- Include metadata (recoverable, remediation)

### Decision
**Use namespaced string codes with central registry.**

```python
# error_codes.py

# Environment errors
ENV_NO_VENV = "ENV_NO_VENV"
ENV_NO_PIPENV = "ENV_NO_PIPENV"
ENV_PYTHON_VERSION = "ENV_PYTHON_VERSION"

# Dependency errors
DEP_MISSING = "DEP_MISSING"

# Build errors
BUILD_FAILED = "BUILD_FAILED"

# Verification errors
VERIFY_FAILED = "VERIFY_FAILED"

ERROR_METADATA = {
    ENV_NO_VENV: {
        "recoverable": True,
        "remediation": "pipenv install --dev && pipenv shell",
        "category": "environment"
    },
    # ...
}
```

### Rationale

**Alternatives considered:**

| Option | Format | Example |
|--------|--------|---------|
| A | Integer codes | `101`, `201`, `301` |
| B | Namespaced strings | `ENV_NO_VENV` |
| C | Hierarchical | `env.venv.missing` |
| D | UUID | `a1b2c3d4-...` |

**Option B selected** because:
1. Human-readable in logs
2. Self-documenting in code
3. Easy grep/search
4. No collision risk (unlike integers)
5. Simpler than hierarchical (no parser needed)

### Error Code Schema

```json
{
  "error_code": "ENV_NO_VENV",
  "category": "environment",
  "recoverable": true,
  "remediation": "pipenv install --dev && pipenv shell",
  "message": "Virtual environment required. You are running in global Python."
}
```

### Consequences

**Positive:**
- Clear, grep-able error identification
- Metadata enables Claude Code automation
- Extensible without breaking changes

**Negative:**
- String comparison slightly slower than integers (negligible)
- Must maintain registry consistency

---

## ADR-004: JSON Schema for Structured Errors

### Status
**ACCEPTED**

### Context
Claude Code needs structured error output to enable self-healing. Schema must include:
- Error identification
- Human-readable message
- Machine-executable remediation
- Recovery possibility indicator

### Decision
**Use simple flat JSON schema with required fields.**

### JSON Error Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "InstallationError",
  "type": "object",
  "required": ["status", "error_code", "message", "recoverable"],
  "properties": {
    "status": {
      "type": "string",
      "enum": ["error"]
    },
    "error_code": {
      "type": "string",
      "description": "Machine-readable error identifier"
    },
    "message": {
      "type": "string",
      "description": "Human-readable error description"
    },
    "remediation": {
      "type": "string",
      "description": "Command to fix the issue"
    },
    "recoverable": {
      "type": "boolean",
      "description": "Whether automated remediation is possible"
    },
    "details": {
      "type": "object",
      "description": "Additional context for debugging",
      "additionalProperties": true
    }
  }
}
```

### Example Outputs

**Environment Error:**
```json
{
  "status": "error",
  "error_code": "ENV_NO_VENV",
  "message": "Virtual environment required. You are running in global Python.",
  "remediation": "pipenv install --dev && pipenv shell",
  "recoverable": true,
  "details": {
    "python_version": "3.10.11",
    "sys_prefix": "/usr/local",
    "sys_base_prefix": "/usr/local"
  }
}
```

**Missing Dependency:**
```json
{
  "status": "error",
  "error_code": "DEP_MISSING",
  "message": "Missing required modules: yaml, toml",
  "remediation": "pipenv install --dev",
  "recoverable": true,
  "details": {
    "missing_modules": ["yaml", "toml"],
    "checked_modules": ["yaml", "toml", "pathlib", "subprocess"]
  }
}
```

**Build Failure:**
```json
{
  "status": "error",
  "error_code": "BUILD_FAILED",
  "message": "Build phase failed with exit code 1",
  "remediation": null,
  "recoverable": false,
  "details": {
    "exit_code": 1,
    "stderr": "Error: Unable to find build script",
    "log_file": "~/.nwave/install.log"
  }
}
```

### JSON Success Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "InstallationSuccess",
  "type": "object",
  "required": ["status", "message"],
  "properties": {
    "status": {
      "type": "string",
      "enum": ["success"]
    },
    "message": {
      "type": "string"
    },
    "details": {
      "type": "object",
      "properties": {
        "agents_installed": {"type": "integer"},
        "commands_installed": {"type": "integer"},
        "install_path": {"type": "string"},
        "log_file": {"type": "string"}
      }
    }
  }
}
```

**Success Example:**
```json
{
  "status": "success",
  "message": "nWave Framework installed successfully",
  "details": {
    "agents_installed": 28,
    "commands_installed": 23,
    "install_path": "~/.claude/",
    "log_file": "~/.nwave/install.log"
  }
}
```

### Rationale

**Why flat JSON (not nested)?**
1. Simpler parsing for Claude Code
2. Direct field access without traversal
3. Consistent with CLI tool conventions
4. Easier to log and grep

**Why `details` as catch-all object?**
1. Extensible without schema changes
2. Different error types need different context
3. Optional field doesn't break parsing

### Consequences

**Positive:**
- Claude Code can parse with simple JSON parsing
- Recoverable flag enables automated retry
- Details provide debugging context

**Negative:**
- Schema evolution requires versioning consideration
- JSON output adds ~100 lines of formatting code

---

## ADR-005: Pre-flight Check Architecture

### Status
**ACCEPTED**

### Context
Pre-flight checks need to validate multiple environment conditions. Design must:
- Execute checks in specific order
- Collect all failures (not just first)
- Be extensible for future checks
- Use only standard library

### Decision
**Use Chain of Responsibility pattern with check registration.**

```python
class PreflightChecker:
    def __init__(self):
        self._checks = []
        self._register_default_checks()

    def _register_default_checks(self):
        self.add_check(self._check_virtual_environment)
        self.add_check(self._check_pipenv_installed)
        self.add_check(self._check_dependencies)
        self.add_check(self._check_python_version)

    def add_check(self, check_func):
        self._checks.append(check_func)

    def run_all_checks(self):
        results = []
        for check in self._checks:
            result = check()
            results.append(result)
        return PreflightResult(
            passed=all(r.status == CheckStatus.PASSED for r in results),
            checks=results,
            blocking_errors=[r for r in results if r.status == CheckStatus.FAILED]
        )
```

### Rationale

**Alternatives considered:**

| Option | Pattern | Description |
|--------|---------|-------------|
| A | Single function | One large validation function |
| B | Strategy pattern | Inject check strategies |
| C | Chain of Responsibility | Ordered chain, collect all |
| D | Observer pattern | Broadcast results |

**Option C selected** because:
1. Natural ordering of checks (venv before deps)
2. Extensible (add custom checks)
3. Collects all failures (better UX than fail-fast)
4. Simple implementation with standard library

### Check Execution Order

| Order | Check | Reason for Position |
|-------|-------|---------------------|
| 1 | Virtual Environment | Most common failure, fastest check |
| 2 | Pipenv Installed | Required for dep check, fast subprocess call |
| 3 | Dependencies | Requires venv to be meaningful |
| 4 | Python Version | Informational, rarely fails |

### Consequences

**Positive:**
- Clear extension point for new checks
- All failures reported together
- Order can be customized

**Negative:**
- Slightly more complex than single function
- Must maintain check registration

---

## ADR-006: Verification Module Architecture

### Status
**ACCEPTED**

### Context
Installation verification is needed in two places:
1. Automatic check after installation completes
2. Standalone `verify_nwave.py` script

### Decision
**Extract verification to shared module, thin script wrapper.**

```
InstallationVerifier (shared module)
        ^
        |
    +---+---+
    |       |
    v       v
install_nwave.py   verify_nwave.py
(automatic)        (standalone)
```

### Rationale

**Alternatives:**
1. Duplicate verification logic (violates DRY)
2. verify_nwave.py imports from install_nwave.py (coupling)
3. Shared module (clean separation)

**Option 3 selected** because:
1. Single source of truth for verification logic
2. Both callers use identical checks
3. Easy to test verification in isolation
4. No circular dependencies

### Consequences

**Positive:**
- Consistent verification behavior
- Single place to update expected counts
- Testable in isolation

**Negative:**
- Additional module to maintain
- Must ensure module is importable from both scripts

---

## Summary of Technology Choices

| Decision | Choice | Key Rationale |
|----------|--------|---------------|
| Context Detection | TTY + env var fallback | Works today, future-proof |
| Log Location | `~/.nwave/install.log` | Survives uninstall, user-accessible |
| Error Codes | Namespaced strings | Human-readable, self-documenting |
| JSON Schema | Flat with details object | Simple parsing, extensible |
| Check Architecture | Chain of Responsibility | Ordered, extensible, collects all |
| Verification | Shared module | DRY, consistent, testable |
