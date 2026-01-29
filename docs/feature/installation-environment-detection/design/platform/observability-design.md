# Observability Design: Installation Environment Detection

**Feature ID:** APEX-002
**Wave:** DESIGN (Platform Perspective)
**Created:** 2026-01-29

---

## 1. Observability Overview

### 1.1 Three Pillars for Installation

| Pillar | Application to Installation |
|--------|----------------------------|
| **Logs** | Installation events, errors, diagnostics |
| **Metrics** | Counts, durations, success rates |
| **Traces** | Not applicable (single process) |

Given the installation is a local, single-process operation, observability focuses primarily on structured logging with embedded metrics.

### 1.2 Observability Goals

| Goal | Approach |
|------|----------|
| Troubleshooting | Structured logs with context |
| Support | Diagnostic data collection |
| Improvement | Aggregate metrics (optional telemetry) |
| Compliance | Audit trail of installation actions |

---

## 2. Structured Logging Strategy

### 2.1 Log Format Specification

**Format:** `[TIMESTAMP] [LEVEL] [COMPONENT] MESSAGE | key=value key=value`

```
[2026-01-29T14:23:45.123Z] [INFO]  [PREFLIGHT] Starting environment validation | checks=4
[2026-01-29T14:23:45.125Z] [INFO]  [PREFLIGHT] Check completed | check=virtual_env status=PASS duration_ms=2
[2026-01-29T14:23:45.275Z] [INFO]  [PREFLIGHT] Check completed | check=pipenv_installed status=PASS duration_ms=150
[2026-01-29T14:23:45.280Z] [ERROR] [PREFLIGHT] Check failed | check=dependencies status=FAIL error_code=DEP_MISSING missing=yaml
[2026-01-29T14:23:45.280Z] [INFO]  [PREFLIGHT] Validation complete | passed=false failed=1 total_duration_ms=157
```

### 2.2 Log Components

| Component | Prefix | Purpose |
|-----------|--------|---------|
| PREFLIGHT | `[PREFLIGHT]` | Environment validation checks |
| BUILD | `[BUILD]` | IDE bundle building |
| DEPLOY | `[DEPLOY]` | File installation |
| VERIFY | `[VERIFY]` | Post-install verification |
| BACKUP | `[BACKUP]` | Backup operations |
| CONTEXT | `[CONTEXT]` | Context detection |
| OUTPUT | `[OUTPUT]` | User output formatting |

### 2.3 Log Levels

| Level | When to Use | Example |
|-------|-------------|---------|
| DEBUG | Detailed flow for troubleshooting | Function entry, variable values |
| INFO | Normal operational events | Check started, check passed |
| WARN | Recoverable issues, non-blocking | Low agent count, optional missing |
| ERROR | Failures that block progress | Check failed, build error |
| CRITICAL | System-level failures | Cannot write log, permission denied |

### 2.4 Structured Fields

Standard fields included in log entries:

| Field | Type | Example | When Included |
|-------|------|---------|---------------|
| timestamp | ISO 8601 | 2026-01-29T14:23:45.123Z | Always |
| level | string | INFO | Always |
| component | string | PREFLIGHT | Always |
| message | string | Check completed | Always |
| check | string | virtual_env | Check operations |
| status | string | PASS/FAIL | Check results |
| duration_ms | int | 150 | Timed operations |
| error_code | string | DEP_MISSING | Error events |
| count | int | 28 | Count operations |
| path | string | ~/.claude/agents/nw | File operations |

---

## 3. Log File Management

### 3.1 Log File Location

**Primary:** `~/.nwave/install.log`

**Rationale:**
- Survives uninstall (unlike ~/.claude/)
- User-accessible for support
- Dedicated directory for nWave tooling
- Cross-platform via pathlib

### 3.2 Log Session Markers

Each installation session starts with a header:

```
================================================================================
nWave Installation Session
================================================================================
Session ID:     f8a3c2d1-1234-5678-9abc-def012345678
Start Time:     2026-01-29T14:23:45.123Z
Platform:       darwin (macOS 14.3.1)
Python:         3.12.1 (/opt/homebrew/bin/python3)
User:           mike
Working Dir:    /Users/mike/ProgettiGit/crafter-ai
Virtual Env:    /Users/mike/.local/share/virtualenvs/crafter-ai-abc123
CI Environment: None
================================================================================
```

### 3.3 Log Rotation

```python
MAX_LOG_SIZE = 1024 * 1024  # 1 MB
MAX_LOG_FILES = 5           # Keep 5 rotated files

def rotate_log_if_needed(log_path: Path) -> None:
    """Rotate log file if it exceeds size limit."""
    if not log_path.exists():
        return

    if log_path.stat().st_size < MAX_LOG_SIZE:
        return

    # Rotate: install.log -> install.log.1 -> install.log.2 ...
    for i in range(MAX_LOG_FILES - 1, 0, -1):
        old_path = log_path.with_suffix(f'.log.{i}')
        new_path = log_path.with_suffix(f'.log.{i+1}')
        if old_path.exists():
            old_path.rename(new_path)

    log_path.rename(log_path.with_suffix('.log.1'))
```

### 3.4 Log Retention

| Log Type | Retention | Rationale |
|----------|-----------|-----------|
| install.log | 5 rotations (~5MB total) | Debugging recent issues |
| install.log.1-5 | Until rotated out | Historical reference |

---

## 4. Diagnostic Collection

### 4.1 Diagnostic Data Structure

On error, collect comprehensive diagnostics:

```python
def collect_diagnostics() -> Dict[str, Any]:
    """Collect system diagnostics for error reporting."""
    import platform
    import sys
    from pathlib import Path

    diagnostics = {
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'platform': {
            'system': platform.system(),
            'release': platform.release(),
            'version': platform.version(),
            'machine': platform.machine(),
            'processor': platform.processor(),
        },
        'python': {
            'version': sys.version,
            'version_info': list(sys.version_info),
            'executable': sys.executable,
            'prefix': sys.prefix,
            'base_prefix': sys.base_prefix,
            'path': sys.path[:5],  # First 5 entries
        },
        'environment': {
            'in_virtual_env': sys.prefix != sys.base_prefix,
            'pipenv_active': bool(os.environ.get('PIPENV_ACTIVE')),
            'virtual_env': os.environ.get('VIRTUAL_ENV'),
            'ci_platform': detect_ci_platform(),
            'shell': os.environ.get('SHELL'),
            'term': os.environ.get('TERM'),
        },
        'paths': {
            'home': str(Path.home()),
            'cwd': str(Path.cwd()),
            'claude_config': str(Path.home() / '.claude'),
            'nwave_log': str(Path.home() / '.nwave' / 'install.log'),
        },
        'files': {
            'pipfile_exists': (Path.cwd() / 'Pipfile').exists(),
            'pipfile_lock_exists': (Path.cwd() / 'Pipfile.lock').exists(),
            'nwave_dir_exists': (Path.cwd() / 'nWave').exists(),
        },
    }

    # Add pipenv info if available
    try:
        result = subprocess.run(
            ['pipenv', '--venv'],
            capture_output=True,
            text=True,
            timeout=5
        )
        diagnostics['pipenv'] = {
            'venv_path': result.stdout.strip() if result.returncode == 0 else None,
            'available': result.returncode == 0,
        }
    except Exception as e:
        diagnostics['pipenv'] = {
            'available': False,
            'error': str(e),
        }

    return diagnostics
```

### 4.2 Diagnostic Output Format

For support troubleshooting, format diagnostics as YAML:

```yaml
# Diagnostic Report
# Generated: 2026-01-29T14:23:45Z
# Error: DEP_MISSING

platform:
  system: Darwin
  release: 24.3.0
  machine: arm64

python:
  version: 3.12.1
  executable: /opt/homebrew/bin/python3
  in_virtual_env: true

environment:
  pipenv_active: true
  virtual_env: /Users/mike/.local/share/virtualenvs/crafter-ai-abc123
  ci_platform: null

paths:
  home: /Users/mike
  cwd: /Users/mike/ProgettiGit/crafter-ai

files:
  pipfile_exists: true
  pipfile_lock_exists: true

error:
  code: DEP_MISSING
  message: Missing required module 'yaml'
  recoverable: true
  remediation: pipenv install --dev
```

### 4.3 Diagnostic Collection Triggers

| Trigger | Data Collected | Destination |
|---------|---------------|-------------|
| Any ERROR | Full diagnostics | Log file |
| Any CRITICAL | Full diagnostics + stack trace | Log file + stdout |
| --debug flag | Verbose logging | Log file |
| --diagnose flag | Full diagnostics only | stdout (support) |

---

## 5. Debug Mode

### 5.1 Debug Flag Behavior

```bash
# Enable debug logging
python scripts/install/install_nwave.py --debug
```

Debug mode enables:
- DEBUG level logging
- Function entry/exit logging
- Variable value logging
- Timing for all operations
- Stack traces on any exception

### 5.2 Debug Log Format

```
[2026-01-29T14:23:45.123Z] [DEBUG] [PREFLIGHT] Entering run_all_checks | checks_registered=4
[2026-01-29T14:23:45.123Z] [DEBUG] [PREFLIGHT] Executing check | index=0 name=virtual_env
[2026-01-29T14:23:45.124Z] [DEBUG] [PREFLIGHT] sys.prefix=/Users/mike/.local/share/virtualenvs/crafter-ai-abc123
[2026-01-29T14:23:45.124Z] [DEBUG] [PREFLIGHT] sys.base_prefix=/opt/homebrew/Cellar/python@3.12/3.12.1/Frameworks/Python.framework/Versions/3.12
[2026-01-29T14:23:45.125Z] [DEBUG] [PREFLIGHT] Check result | name=virtual_env passed=true duration_ms=2
```

---

## 6. Support Troubleshooting Guide

### 6.1 Common Issues and Log Patterns

| Issue | Log Pattern | Resolution |
|-------|-------------|------------|
| No virtual env | `[ERROR] [PREFLIGHT] Check failed \| check=virtual_env` | `pipenv shell` |
| Missing deps | `[ERROR] [PREFLIGHT] Check failed \| check=dependencies missing=yaml` | `pipenv install --dev` |
| Build failed | `[ERROR] [BUILD] Build script failed \| exit_code=1` | Check build logs |
| Low agent count | `[WARN] [VERIFY] Agent count below expected \| count=15 expected=28` | Rebuild |

### 6.2 Diagnostic Commands

```bash
# Run installer with full diagnostics
pipenv run python scripts/install/install_nwave.py --debug

# Collect diagnostic report only
pipenv run python scripts/install/install_nwave.py --diagnose

# View recent log entries
tail -100 ~/.nwave/install.log

# Search for errors in log
grep '\[ERROR\]' ~/.nwave/install.log

# View last installation session
sed -n '/^===.*Session/,/^===.*Session/p' ~/.nwave/install.log | head -n -1
```

### 6.3 Support Request Template

When users request support, guide them to provide:

```
## Installation Issue Report

### Environment
- OS: [macOS/Linux/Windows version]
- Python: [version and installation method]
- Pipenv: [version]

### Error Message
[Paste the error output here]

### Diagnostic Report
[Run: pipenv run python scripts/install/install_nwave.py --diagnose]
[Paste output here]

### Log Excerpt
[Last 50 lines of ~/.nwave/install.log]
```

---

## 7. Metrics Collection (Optional Telemetry)

### 7.1 Telemetry Design Decision

**Status:** NOT IMPLEMENTED (see PADR-004)

If opt-in telemetry is implemented in the future:

### 7.2 Proposed Metrics

| Metric | Type | Purpose |
|--------|------|---------|
| installation_count | counter | Total installations |
| installation_success_rate | gauge | Success percentage |
| preflight_check_duration_ms | histogram | Performance monitoring |
| error_by_code | counter | Most common errors |
| platform_distribution | counter | OS/Python breakdown |

### 7.3 Privacy Considerations

If telemetry is implemented:
- Strictly opt-in (explicit user consent)
- No PII collected (no usernames, paths, IPs)
- Aggregate data only
- Local collection with batch upload
- Easy opt-out at any time

---

## 8. Alerting (CI/CD Context)

### 8.1 CI Alerting Strategy

| Event | Alert Type | Destination |
|-------|-----------|-------------|
| Test failure | GitHub Actions | PR comments |
| Build failure | GitHub Actions | PR comments |
| Installation test failure | GitHub Actions | PR comments |
| Release failure | GitHub Actions | Repository admins |

### 8.2 Alert Content

```
## Installation Test Failed

**OS:** ubuntu-latest
**Python:** 3.12
**Error Code:** DEP_MISSING

### Error Message
Missing required module: yaml

### Remediation
Run: pipenv install --dev

### Logs
[View workflow run](link-to-run)
```

---

## 9. Implementation Classes

### 9.1 Structured Logger

```python
class StructuredLogger:
    """Logger with structured output format."""

    def __init__(self, log_path: Path, debug: bool = False):
        self.log_path = log_path
        self.debug = debug
        self._session_id = str(uuid.uuid4())[:8]
        self._ensure_log_dir()
        self._write_session_header()

    def _ensure_log_dir(self):
        self.log_path.parent.mkdir(parents=True, exist_ok=True)

    def _write_session_header(self):
        header = self._format_session_header()
        self._write(header)

    def _format_entry(
        self,
        level: str,
        component: str,
        message: str,
        **fields
    ) -> str:
        timestamp = datetime.now(timezone.utc).isoformat()
        field_str = ' | '.join(f'{k}={v}' for k, v in fields.items())
        entry = f'[{timestamp}] [{level:5}] [{component}] {message}'
        if field_str:
            entry += f' | {field_str}'
        return entry

    def _write(self, content: str):
        with open(self.log_path, 'a', encoding='utf-8') as f:
            f.write(content + '\n')

    def debug(self, component: str, message: str, **fields):
        if self.debug:
            entry = self._format_entry('DEBUG', component, message, **fields)
            self._write(entry)

    def info(self, component: str, message: str, **fields):
        entry = self._format_entry('INFO', component, message, **fields)
        self._write(entry)

    def warn(self, component: str, message: str, **fields):
        entry = self._format_entry('WARN', component, message, **fields)
        self._write(entry)

    def error(self, component: str, message: str, **fields):
        entry = self._format_entry('ERROR', component, message, **fields)
        self._write(entry)

    def critical(self, component: str, message: str, **fields):
        entry = self._format_entry('CRIT', component, message, **fields)
        self._write(entry)
```

### 9.2 Diagnostic Collector

```python
class DiagnosticCollector:
    """Collects system diagnostics for troubleshooting."""

    @staticmethod
    def collect() -> Dict[str, Any]:
        """Collect comprehensive system diagnostics."""
        return {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'platform': DiagnosticCollector._collect_platform(),
            'python': DiagnosticCollector._collect_python(),
            'environment': DiagnosticCollector._collect_environment(),
            'paths': DiagnosticCollector._collect_paths(),
            'files': DiagnosticCollector._collect_files(),
            'pipenv': DiagnosticCollector._collect_pipenv(),
        }

    @staticmethod
    def format_as_yaml(diagnostics: Dict[str, Any]) -> str:
        """Format diagnostics as YAML for human reading."""
        import yaml
        return yaml.dump(diagnostics, default_flow_style=False, sort_keys=False)

    @staticmethod
    def format_as_json(diagnostics: Dict[str, Any]) -> str:
        """Format diagnostics as JSON for machine processing."""
        import json
        return json.dumps(diagnostics, indent=2)
```

---

## 10. Traceability

| Requirement | Observability Element | Section |
|-------------|----------------------|---------|
| FR-08: Logging | Structured logging | 2, 3 |
| FR-04: Context errors | Log levels | 2.3 |
| NFR-03: Performance | Duration metrics | 2.4 |
| NFR-04: Cross-platform | Platform diagnostics | 4.1 |
