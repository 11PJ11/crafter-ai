# Deterministic Execution System (DES) - Technology Stack

**Version:** 1.0
**Date:** 2026-01-22
**Author:** Morgan (Solution Architect)
**Status:** DESIGN Wave Deliverable

---

## 1. Technology Selection Principles

| Principle | Application |
|-----------|-------------|
| **Zero External Dependencies** | No databases, message queues, or daemons |
| **Standard Library Only** | Python 3.11+ stdlib for core functionality |
| **Portable** | Works on Windows, macOS, Linux |
| **No Installation** | No `pip install` required for core DES |
| **Session-Scoped** | All monitoring terminates with user session |

---

## 2. Core Technology: Python 3.11+

### 2.1 Justification

| Criterion | Python 3.11+ |
|-----------|--------------|
| Claude Code hooks | Native support (command type) |
| JSON processing | `json` module in stdlib |
| File operations | `pathlib` module in stdlib |
| Regex parsing | `re` module in stdlib |
| Date/time handling | `datetime` module in stdlib |
| Type hints | Full support with generics |

### 2.2 Standard Library Modules Used

```python
# Core modules - no external dependencies
import json          # Step file and audit log parsing
import re            # DES marker extraction
from pathlib import Path      # File path operations
from datetime import datetime, date, timedelta  # Timestamps
from dataclasses import dataclass  # Data structures
from abc import ABC, abstractmethod  # Interfaces
from enum import Enum         # State enumerations
import sys            # stdin reading for hooks
from typing import Optional   # Type annotations
```

### 2.3 Python Version Requirements

| Feature | Minimum Version | Notes |
|---------|-----------------|-------|
| Type hints generics | 3.9 | `list[str]` instead of `List[str]` |
| `match` statement | 3.10 | Optional, for cleaner FSM logic |
| Exception groups | 3.11 | For aggregated error reporting |
| **Recommended** | **3.11+** | Best performance and error messages |

---

## 3. Data Persistence: JSON/JSONL Files

### 3.1 Step File Format (JSON)

**File Extension:** `.json`
**Encoding:** UTF-8
**Location:** `docs/feature/{project-id}/steps/*.json`

```json
{
  "schema_version": "1.0",
  "task_id": "01-01",
  "project_id": "auth-feature",
  "state": {
    "status": "IN_PROGRESS",
    "created_at": "2026-01-22T10:00:00Z",
    "updated_at": "2026-01-22T14:30:00Z",
    "failure_reason": null,
    "recovery_suggestions": []
  },
  "tdd_cycle": {
    "phase_execution_log": [
      {
        "phase_name": "PREPARE",
        "status": "EXECUTED",
        "started_at": "2026-01-22T10:05:00Z",
        "ended_at": "2026-01-22T10:08:00Z",
        "duration_minutes": 3,
        "outcome": "PASS",
        "outcome_details": "Removed @skip tag, verified single active test"
      }
    ]
  }
}
```

### 3.2 Audit Log Format (JSONL)

**File Extension:** `.log`
**Encoding:** UTF-8
**Location:** `docs/feature/{project-id}/steps/audit-YYYY-MM-DD.log`
**Format:** JSON Lines (one JSON object per line)

```jsonl
{"timestamp":"2026-01-22T10:00:00Z","event":"TASK_INVOCATION_STARTED","step_file":"steps/01-01.json"}
{"timestamp":"2026-01-22T10:00:01Z","event":"TASK_INVOCATION_VALIDATED","step_file":"steps/01-01.json"}
{"timestamp":"2026-01-22T10:05:00Z","event":"PHASE_STARTED","step_file":"steps/01-01.json","phase":"PREPARE"}
{"timestamp":"2026-01-22T10:08:00Z","event":"PHASE_COMPLETED","step_file":"steps/01-01.json","phase":"PREPARE","outcome":"PASS"}
```

### 3.3 Why JSON/JSONL?

| Criterion | JSON/JSONL | Alternatives Rejected |
|-----------|------------|----------------------|
| No dependencies | stdlib `json` | SQLite requires setup |
| Human readable | Yes | Binary formats not debuggable |
| Git friendly | Line-based diffs | Binary files create merge conflicts |
| Portable | Cross-platform | DB files may have platform issues |
| Append-only | JSONL supports | JSON requires full rewrite |

---

## 4. Hook Integration: Claude Code SubagentStop

### 4.1 Hook Configuration

**Location:** `.claude/settings.local.json`

```json
{
  "hooks": {
    "SubagentStop": [
      {
        "matcher": "*",
        "hooks": [
          {
            "type": "command",
            "command": "python nWave/hooks/post_subagent_validation.py",
            "timeout": 30
          }
        ]
      }
    ]
  }
}
```

### 4.2 Hook Input Schema (Verified v1.5.0)

**CORRECTED (v1.5.0)**: Real 6-field SubagentStop hook schema from official Claude Code documentation. Non-existent fields `agent_id` and `agent_transcript_path` removed. See des-discovery-report.md v2.0.

```json
{
  "hook_event_name": "SubagentStop",
  "session_id": "786ebad4-6e5b-42d3-a954-c1df6e6f25b7",
  "transcript_path": "/home/user/.claude/projects/.../session.jsonl",
  "stop_hook_active": false,
  "cwd": "/mnt/c/Repositories/Projects/ai-craft",
  "permission_mode": "bypassPermissions",
  "tool_use_id": "toolu_01ABC123xyz"
}
```

### 4.3 Transcript Format (JSONL)

First line contains original prompt:

```jsonl
{"type":"user","message":{"role":"user","content":"<FULL PROMPT HERE>"},...}
{"type":"assistant","message":{"role":"assistant","content":[...]},...}
```

---

## 5. Template System: Markdown

### 5.1 Template Format

**File Extension:** `.template.md`
**Encoding:** UTF-8
**Location:** `nWave/templates/prompt-templates/`

```markdown
<!-- DES-ORIGIN: command:/nw:execute -->
<!-- DES-STEP-FILE: {step_file_path} -->
<!-- DES-VALIDATION: required -->

# AGENT_IDENTITY

You are the **{agent_name}** agent...

# TDD_14_PHASES

| # | Phase | Gate | Action |
|---|-------|------|--------|
| 0 | PREPARE | G1 | ... |
...
```

### 5.2 Placeholder Syntax

Simple string replacement: `{placeholder_name}`

```python
def render_template(template: str, data: dict) -> str:
    result = template
    for key, value in data.items():
        result = result.replace(f"{{{key}}}", str(value))
    return result
```

### 5.3 Why Markdown Templates?

| Criterion | Markdown | Alternatives Rejected |
|-----------|----------|----------------------|
| Human readable | Yes | Jinja2 requires dependency |
| No dependencies | String replace | YAML templates need parsing |
| Agent-friendly | Native format | JSON templates awkward for prose |
| Validation simple | Section markers | Complex template syntax error-prone |

---

## 6. Configuration: YAML

### 6.1 Configuration Format

**File Extension:** `.yaml`
**Encoding:** UTF-8
**Parser:** `yaml` is NOT in stdlib - use JSON for config instead

**Revised:** Use JSON for all configuration

```json
{
  "des_version": "1.0",
  "validation": {
    "mandatory_sections": [
      "DES_METADATA",
      "AGENT_IDENTITY",
      "TASK_CONTEXT",
      "TDD_14_PHASES",
      "QUALITY_GATES",
      "OUTCOME_RECORDING",
      "BOUNDARY_RULES",
      "TIMEOUT_INSTRUCTION"
    ],
    "required_phases": [
      "PREPARE", "RED_ACCEPTANCE", "RED_UNIT", "GREEN_UNIT",
      "CHECK_ACCEPTANCE", "GREEN_ACCEPTANCE", "REVIEW",
      "REFACTOR_L1", "REFACTOR_L2", "REFACTOR_L3", "REFACTOR_L4",
      "POST_REFACTOR_REVIEW", "FINAL_VALIDATE", "COMMIT"
    ]
  },
  "stale_detection": {
    "threshold_minutes": 30,
    "enabled": true
  },
  "audit": {
    "rotation": "daily",
    "format": "jsonl"
  }
}
```

---

## 7. File System Layout

```
project/
├── .claude/
│   └── settings.local.json          # Hook configuration
│
├── nWave/
│   ├── hooks/
│   │   ├── __init__.py
│   │   ├── post_subagent_validation.py   # Gate 2: SubagentStop
│   │   ├── validate_prompt_template.py    # Gate 1: Pre-invocation
│   │   └── pre_commit_tdd_phases.py       # Gate 3: Pre-commit
│   │
│   ├── ports/                        # Interfaces (hexagonal architecture)
│   │   ├── __init__.py
│   │   ├── command_filter.py
│   │   ├── template_engine.py
│   │   ├── lifecycle_manager.py
│   │   └── validation_gate.py
│   │
│   ├── adapters/                     # Implementations
│   │   ├── __init__.py
│   │   ├── regex_command_filter.py
│   │   ├── markdown_template_engine.py
│   │   ├── fsm_lifecycle_manager.py
│   │   └── gates/
│   │       ├── __init__.py
│   │       ├── pre_invocation_gate.py
│   │       ├── subagent_stop_gate.py
│   │       └── audit_trail.py
│   │
│   ├── templates/
│   │   └── prompt-templates/
│   │       ├── execute-step.template.md
│   │       └── _section-definitions.json
│   │
│   ├── config/
│   │   ├── des-config.json           # DES configuration
│   │   ├── des-commands.json         # Command registration
│   │   └── step-execution-fsm.json   # State machine definition
│   │
│   └── utils/
│       ├── __init__.py
│       ├── audit.py                  # Audit trail utilities
│       └── stale_detection.py        # Stale execution scanner
│
└── docs/
    └── feature/
        └── {project-id}/
            └── steps/
                ├── 01-01.json        # Step file
                ├── 01-02.json
                └── audit-2026-01-22.log  # Daily audit
```

---

## 8. Runtime Requirements

### 8.1 Minimum Requirements

| Requirement | Specification |
|-------------|---------------|
| Python | 3.11 or higher |
| Operating System | Windows 10+, macOS 11+, Linux (glibc 2.17+) |
| Claude Code | Version with SubagentStop hook support |
| File System | Read/write access to project directory |
| Memory | < 50 MB for DES operations |

### 8.2 Optional Requirements

| Requirement | Purpose |
|-------------|---------|
| Git | Pre-commit hook integration |
| pytest | Testing DES components (dev only) |

---

## 9. Performance Characteristics

### 9.1 Time Budgets

| Operation | Target | Implementation |
|-----------|--------|----------------|
| Template validation | < 500ms | String search, no parsing |
| Step file read/write | < 100ms | Single JSON file |
| Stale detection scan | < 1s | Glob + JSON parse |
| Audit log append | < 50ms | Single line write |
| Prompt extraction | < 200ms | Read first line of transcript |

### 9.2 Memory Usage

| Component | Estimated | Notes |
|-----------|-----------|-------|
| Template engine | ~5 MB | Template + step data in memory |
| Step file parsing | ~1 MB | Single file JSON |
| Stale detection | ~10 MB | Multiple file paths in memory |
| Audit logging | ~1 KB | Single entry buffer |

---

## 10. Security Considerations

### 10.1 File Permissions

| File Type | Recommended Permissions | Rationale |
|-----------|------------------------|-----------|
| Step files | 644 (rw-r--r--) | User-editable, team-readable |
| Audit logs | 644 (rw-r--r--) | Append-only by convention |
| Hook scripts | 755 (rwxr-xr-x) | Executable by Claude Code |
| Templates | 644 (rw-r--r--) | Read-only at runtime |

### 10.2 Input Validation

| Input | Validation | Mitigation |
|-------|------------|------------|
| Prompt | Regex exact match | No eval/exec of prompt content |
| Step file path | Path traversal check | Reject `..` sequences |
| JSON data | json.loads() | Stdlib handles malformed input |
| Hook input | Schema validation | Reject unexpected fields |

### 10.3 No Sensitive Data

DES does not handle:
- API keys or credentials
- User authentication
- Network connections
- External service calls

---

## 11. Testing Strategy

### 11.1 Unit Testing

```python
# nWave/tests/test_command_filter.py
import pytest
from nWave.adapters.regex_command_filter import RegexCommandFilter

def test_should_validate_with_marker():
    filter = RegexCommandFilter()
    prompt = "<!-- DES-VALIDATION: required -->\nYou are..."
    assert filter.should_validate(prompt) is True

def test_should_not_validate_without_marker():
    filter = RegexCommandFilter()
    prompt = "You are an exploration agent..."
    assert filter.should_validate(prompt) is False
```

### 11.2 Integration Testing

```python
# nWave/tests/test_subagent_stop_gate.py
import json
import tempfile
from pathlib import Path
from nWave.adapters.gates.subagent_stop_gate import SubagentStopGate

def test_detects_abandoned_phase():
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
        step_data = {
            "tdd_cycle": {
                "phase_execution_log": [
                    {"phase_name": "PREPARE", "status": "IN_PROGRESS"}
                ]
            }
        }
        f.write(json.dumps(step_data).encode())
        f.flush()

        gate = SubagentStopGate()
        result = gate.validate({"step_file": f.name})

        assert result.result == GateResult.FAIL
        assert "IN_PROGRESS (abandoned)" in result.errors[0]
```

---

## 12. Deployment Checklist

### 12.1 Pre-Deployment

- [ ] Python 3.11+ installed
- [ ] Claude Code installed with SubagentStop support
- [ ] Project directory writable

### 12.2 Configuration

- [ ] `.claude/settings.local.json` created with hook config
- [ ] Session restarted after hook configuration
- [ ] Template files present in `nWave/templates/`

### 12.3 Validation

- [ ] Hook fires on test Task invocation
- [ ] Audit log created in step directory
- [ ] Stale detection scan completes

---

## 13. Technology Decisions Log

| Decision | Choice | Rationale | Alternatives Rejected |
|----------|--------|-----------|----------------------|
| Language | Python 3.11+ | Claude Code hook support, stdlib rich | Node.js (heavier runtime) |
| Data format | JSON/JSONL | No dependencies, human readable | SQLite (installation), YAML (no stdlib) |
| Configuration | JSON | Stdlib support | YAML (requires PyYAML) |
| Templates | Markdown | Native for prompts | Jinja2 (dependency) |
| State machine | In-code FSM | Simple, no libraries | python-statemachine (dependency) |
| Stale detection | File scanning | No daemon | SQLite (installation) |
| Audit log | JSONL | Append-only, line-based | SQLite (overkill) |

---

*Technology stack designed by Morgan (solution-architect) during DESIGN wave.*
