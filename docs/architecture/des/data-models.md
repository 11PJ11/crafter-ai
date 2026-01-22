# Deterministic Execution System (DES) - Data Models

**Version:** 1.0
**Date:** 2026-01-22
**Author:** Morgan (Solution Architect)
**Status:** DESIGN Wave Deliverable

---

## 1. Overview

This document defines the JSON schemas for all data structures used by DES. All schemas use JSON Schema draft-07 for validation.

---

## 2. Step File Schema

### 2.1 Complete Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://nwave.ai/schemas/step-file.json",
  "title": "DES Step File",
  "description": "Step file for Deterministic Execution System",
  "type": "object",
  "required": ["schema_version", "task_id", "project_id", "state", "tdd_cycle"],
  "properties": {
    "schema_version": {
      "type": "string",
      "const": "1.0",
      "description": "Schema version for compatibility checking"
    },
    "task_id": {
      "type": "string",
      "pattern": "^[0-9]{2}-[0-9]{2}$",
      "description": "Step identifier in XX-YY format",
      "examples": ["01-01", "02-03"]
    },
    "project_id": {
      "type": "string",
      "minLength": 1,
      "description": "Project identifier",
      "examples": ["auth-feature", "payment-integration"]
    },
    "state": {
      "$ref": "#/definitions/TaskState"
    },
    "task_specification": {
      "$ref": "#/definitions/TaskSpecification"
    },
    "self_contained_context": {
      "$ref": "#/definitions/SelfContainedContext"
    },
    "tdd_cycle": {
      "$ref": "#/definitions/TDDCycle"
    },
    "execution_history": {
      "type": "array",
      "items": {
        "$ref": "#/definitions/ExecutionAttempt"
      },
      "description": "History of execution attempts"
    }
  },
  "definitions": {
    "TaskState": {
      "type": "object",
      "required": ["status"],
      "properties": {
        "status": {
          "type": "string",
          "enum": ["TODO", "IN_PROGRESS", "DONE", "FAILED", "PARTIAL"],
          "description": "Current task execution status"
        },
        "created_at": {
          "type": "string",
          "format": "date-time",
          "description": "ISO 8601 timestamp of task creation"
        },
        "updated_at": {
          "type": "string",
          "format": "date-time",
          "description": "ISO 8601 timestamp of last update"
        },
        "failure_reason": {
          "type": ["string", "null"],
          "description": "Description of failure if status is FAILED"
        },
        "recovery_suggestions": {
          "type": "array",
          "items": {"type": "string"},
          "description": "Actionable recovery steps for failures",
          "examples": [
            ["Reset GREEN_UNIT phase to NOT_EXECUTED", "Run /nw:execute again"]
          ]
        },
        "can_retry": {
          "type": "boolean",
          "default": true,
          "description": "Whether task can be retried"
        }
      }
    },
    "TaskSpecification": {
      "type": "object",
      "required": ["name", "description"],
      "properties": {
        "name": {
          "type": "string",
          "description": "Human-readable task name"
        },
        "description": {
          "type": "string",
          "description": "Detailed task description"
        },
        "motivation": {
          "type": "string",
          "description": "Why this task is needed"
        },
        "acceptance_criteria": {
          "type": "array",
          "items": {"type": "string"},
          "description": "Criteria for task completion"
        },
        "allowed_file_patterns": {
          "type": "array",
          "items": {"type": "string"},
          "description": "Glob patterns for allowed file modifications",
          "examples": [["**/UserRepository*", "**/test_user*"]]
        }
      }
    },
    "SelfContainedContext": {
      "type": "object",
      "properties": {
        "background": {
          "type": "string",
          "description": "Project background context"
        },
        "technical_context": {
          "type": "string",
          "description": "Technical environment details"
        },
        "domain_glossary": {
          "type": "object",
          "additionalProperties": {"type": "string"},
          "description": "Domain-specific term definitions"
        }
      }
    },
    "TDDCycle": {
      "type": "object",
      "required": ["phase_execution_log"],
      "properties": {
        "methodology": {
          "type": "string",
          "const": "outside-in-tdd-14-phase",
          "description": "TDD methodology identifier"
        },
        "phase_execution_log": {
          "type": "array",
          "minItems": 14,
          "maxItems": 14,
          "items": {
            "$ref": "#/definitions/PhaseExecution"
          },
          "description": "Log of all 14 TDD phase executions"
        }
      }
    },
    "PhaseExecution": {
      "type": "object",
      "required": ["phase_name", "status"],
      "properties": {
        "phase_name": {
          "type": "string",
          "enum": [
            "PREPARE",
            "RED_ACCEPTANCE",
            "RED_UNIT",
            "GREEN_UNIT",
            "CHECK_ACCEPTANCE",
            "GREEN_ACCEPTANCE",
            "REVIEW",
            "REFACTOR_L1",
            "REFACTOR_L2",
            "REFACTOR_L3",
            "REFACTOR_L4",
            "POST_REFACTOR_REVIEW",
            "FINAL_VALIDATE",
            "COMMIT"
          ],
          "description": "Name of the TDD phase"
        },
        "status": {
          "type": "string",
          "enum": ["NOT_EXECUTED", "IN_PROGRESS", "EXECUTED", "SKIPPED", "FAILED"],
          "description": "Current phase status"
        },
        "started_at": {
          "type": "string",
          "format": "date-time",
          "description": "ISO 8601 timestamp when phase started"
        },
        "ended_at": {
          "type": "string",
          "format": "date-time",
          "description": "ISO 8601 timestamp when phase ended"
        },
        "duration_minutes": {
          "type": "number",
          "minimum": 0,
          "description": "Phase duration in minutes"
        },
        "outcome": {
          "type": "string",
          "enum": ["PASS", "FAIL"],
          "description": "Phase outcome (required if EXECUTED)"
        },
        "outcome_details": {
          "type": "string",
          "description": "Detailed description of what happened"
        },
        "blocked_by": {
          "type": "string",
          "pattern": "^(BLOCKED_BY_DEPENDENCY:|NOT_APPLICABLE:|APPROVED_SKIP:|DEFERRED:).+",
          "description": "Reason for skip (required if SKIPPED)"
        },
        "artifacts_created": {
          "type": "array",
          "items": {"type": "string"},
          "description": "Files created during this phase"
        },
        "test_results": {
          "$ref": "#/definitions/TestResults"
        },
        "notes": {
          "type": "string",
          "description": "Additional observations or context"
        },
        "educational_note": {
          "type": "string",
          "description": "Learning context for junior developers"
        },
        "history": {
          "type": "array",
          "items": {
            "$ref": "#/definitions/PhaseHistoryEntry"
          },
          "description": "Previous execution attempts for this phase"
        }
      },
      "allOf": [
        {
          "if": {"properties": {"status": {"const": "EXECUTED"}}},
          "then": {"required": ["outcome"]}
        },
        {
          "if": {"properties": {"status": {"const": "SKIPPED"}}},
          "then": {"required": ["blocked_by"]}
        }
      ]
    },
    "TestResults": {
      "type": "object",
      "properties": {
        "total": {
          "type": "integer",
          "minimum": 0
        },
        "passed": {
          "type": "integer",
          "minimum": 0
        },
        "failed": {
          "type": "integer",
          "minimum": 0
        },
        "skipped": {
          "type": "integer",
          "minimum": 0
        }
      }
    },
    "PhaseHistoryEntry": {
      "type": "object",
      "required": ["status", "ended_at"],
      "properties": {
        "status": {
          "type": "string",
          "enum": ["EXECUTED", "FAILED", "CRASHED", "ABANDONED"],
          "description": "How this attempt ended"
        },
        "ended_at": {
          "type": "string",
          "format": "date-time"
        },
        "notes": {
          "type": "string"
        }
      }
    },
    "ExecutionAttempt": {
      "type": "object",
      "properties": {
        "attempt_number": {
          "type": "integer",
          "minimum": 1
        },
        "started_at": {
          "type": "string",
          "format": "date-time"
        },
        "ended_at": {
          "type": "string",
          "format": "date-time"
        },
        "agent_id": {
          "type": "string"
        },
        "result": {
          "type": "string",
          "enum": ["SUCCESS", "FAILED", "PARTIAL", "CRASHED"]
        }
      }
    }
  }
}
```

### 2.2 Minimal Valid Step File

```json
{
  "schema_version": "1.0",
  "task_id": "01-01",
  "project_id": "auth-feature",
  "state": {
    "status": "TODO"
  },
  "tdd_cycle": {
    "phase_execution_log": [
      {"phase_name": "PREPARE", "status": "NOT_EXECUTED"},
      {"phase_name": "RED_ACCEPTANCE", "status": "NOT_EXECUTED"},
      {"phase_name": "RED_UNIT", "status": "NOT_EXECUTED"},
      {"phase_name": "GREEN_UNIT", "status": "NOT_EXECUTED"},
      {"phase_name": "CHECK_ACCEPTANCE", "status": "NOT_EXECUTED"},
      {"phase_name": "GREEN_ACCEPTANCE", "status": "NOT_EXECUTED"},
      {"phase_name": "REVIEW", "status": "NOT_EXECUTED"},
      {"phase_name": "REFACTOR_L1", "status": "NOT_EXECUTED"},
      {"phase_name": "REFACTOR_L2", "status": "NOT_EXECUTED"},
      {"phase_name": "REFACTOR_L3", "status": "NOT_EXECUTED"},
      {"phase_name": "REFACTOR_L4", "status": "NOT_EXECUTED"},
      {"phase_name": "POST_REFACTOR_REVIEW", "status": "NOT_EXECUTED"},
      {"phase_name": "FINAL_VALIDATE", "status": "NOT_EXECUTED"},
      {"phase_name": "COMMIT", "status": "NOT_EXECUTED"}
    ]
  }
}
```

### 2.3 Complete Step File Example

```json
{
  "schema_version": "1.0",
  "task_id": "01-01",
  "project_id": "auth-feature",
  "state": {
    "status": "DONE",
    "created_at": "2026-01-22T10:00:00Z",
    "updated_at": "2026-01-22T11:30:00Z",
    "failure_reason": null,
    "recovery_suggestions": []
  },
  "task_specification": {
    "name": "Implement user authentication",
    "description": "Add login endpoint with JWT token generation",
    "motivation": "Users need to authenticate to access protected resources",
    "acceptance_criteria": [
      "User can login with valid credentials",
      "JWT token is returned on successful login",
      "Invalid credentials return 401 error"
    ],
    "allowed_file_patterns": [
      "**/auth/**",
      "**/test_auth*"
    ]
  },
  "tdd_cycle": {
    "methodology": "outside-in-tdd-14-phase",
    "phase_execution_log": [
      {
        "phase_name": "PREPARE",
        "status": "EXECUTED",
        "started_at": "2026-01-22T10:05:00Z",
        "ended_at": "2026-01-22T10:08:00Z",
        "duration_minutes": 3,
        "outcome": "PASS",
        "outcome_details": "Removed @skip tag from login acceptance test",
        "notes": "Single acceptance test now active"
      },
      {
        "phase_name": "RED_ACCEPTANCE",
        "status": "EXECUTED",
        "started_at": "2026-01-22T10:08:00Z",
        "ended_at": "2026-01-22T10:12:00Z",
        "duration_minutes": 4,
        "outcome": "PASS",
        "outcome_details": "Acceptance test fails with 404 - endpoint not implemented",
        "test_results": {"total": 1, "passed": 0, "failed": 1, "skipped": 0}
      },
      {
        "phase_name": "RED_UNIT",
        "status": "EXECUTED",
        "started_at": "2026-01-22T10:12:00Z",
        "ended_at": "2026-01-22T10:20:00Z",
        "duration_minutes": 8,
        "outcome": "PASS",
        "outcome_details": "Unit test for AuthService.login() fails on assertion"
      },
      {
        "phase_name": "GREEN_UNIT",
        "status": "EXECUTED",
        "started_at": "2026-01-22T10:20:00Z",
        "ended_at": "2026-01-22T10:35:00Z",
        "duration_minutes": 15,
        "outcome": "PASS",
        "outcome_details": "Minimal implementation passes unit test",
        "artifacts_created": ["src/auth/service.py"]
      },
      {
        "phase_name": "CHECK_ACCEPTANCE",
        "status": "EXECUTED",
        "started_at": "2026-01-22T10:35:00Z",
        "ended_at": "2026-01-22T10:37:00Z",
        "duration_minutes": 2,
        "outcome": "FAIL",
        "outcome_details": "Acceptance test still fails - need endpoint"
      },
      {
        "phase_name": "GREEN_ACCEPTANCE",
        "status": "EXECUTED",
        "started_at": "2026-01-22T10:37:00Z",
        "ended_at": "2026-01-22T10:50:00Z",
        "duration_minutes": 13,
        "outcome": "PASS",
        "outcome_details": "All tests green after adding endpoint",
        "test_results": {"total": 5, "passed": 5, "failed": 0, "skipped": 0}
      },
      {
        "phase_name": "REVIEW",
        "status": "EXECUTED",
        "started_at": "2026-01-22T10:50:00Z",
        "ended_at": "2026-01-22T10:55:00Z",
        "duration_minutes": 5,
        "outcome": "PASS",
        "outcome_details": "Code passes SOLID principles check"
      },
      {
        "phase_name": "REFACTOR_L1",
        "status": "EXECUTED",
        "started_at": "2026-01-22T10:55:00Z",
        "ended_at": "2026-01-22T11:00:00Z",
        "duration_minutes": 5,
        "outcome": "PASS",
        "outcome_details": "Renamed variables to use business language"
      },
      {
        "phase_name": "REFACTOR_L2",
        "status": "EXECUTED",
        "started_at": "2026-01-22T11:00:00Z",
        "ended_at": "2026-01-22T11:05:00Z",
        "duration_minutes": 5,
        "outcome": "PASS",
        "outcome_details": "Extracted token generation to separate method"
      },
      {
        "phase_name": "REFACTOR_L3",
        "status": "SKIPPED",
        "blocked_by": "NOT_APPLICABLE: Single class, no SRP violations"
      },
      {
        "phase_name": "REFACTOR_L4",
        "status": "SKIPPED",
        "blocked_by": "NOT_APPLICABLE: No architecture pattern changes needed"
      },
      {
        "phase_name": "POST_REFACTOR_REVIEW",
        "status": "EXECUTED",
        "started_at": "2026-01-22T11:05:00Z",
        "ended_at": "2026-01-22T11:10:00Z",
        "duration_minutes": 5,
        "outcome": "PASS",
        "outcome_details": "All tests still pass after refactoring"
      },
      {
        "phase_name": "FINAL_VALIDATE",
        "status": "EXECUTED",
        "started_at": "2026-01-22T11:10:00Z",
        "ended_at": "2026-01-22T11:15:00Z",
        "duration_minutes": 5,
        "outcome": "PASS",
        "outcome_details": "Complete test suite passes",
        "test_results": {"total": 25, "passed": 25, "failed": 0, "skipped": 2}
      },
      {
        "phase_name": "COMMIT",
        "status": "EXECUTED",
        "started_at": "2026-01-22T11:15:00Z",
        "ended_at": "2026-01-22T11:20:00Z",
        "duration_minutes": 5,
        "outcome": "PASS",
        "outcome_details": "Committed with message: feat(auth): add user login endpoint"
      }
    ]
  }
}
```

---

## 3. Audit Log Entry Schema

### 3.1 Complete Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://nwave.ai/schemas/audit-entry.json",
  "title": "DES Audit Log Entry",
  "description": "Single entry in the DES audit trail",
  "type": "object",
  "required": ["timestamp", "event", "step_file"],
  "properties": {
    "timestamp": {
      "type": "string",
      "format": "date-time",
      "description": "ISO 8601 timestamp of the event"
    },
    "event": {
      "type": "string",
      "enum": [
        "TASK_INVOCATION_STARTED",
        "TASK_INVOCATION_VALIDATED",
        "TASK_INVOCATION_REJECTED",
        "PHASE_STARTED",
        "PHASE_COMPLETED",
        "PHASE_SKIPPED",
        "PHASE_FAILED",
        "SUBAGENT_STOP_VALIDATION",
        "STALE_RESOLUTION",
        "SCOPE_VIOLATION_WARNING",
        "COMMIT_VALIDATION_PASSED",
        "COMMIT_VALIDATION_FAILED"
      ],
      "description": "Type of event"
    },
    "step_file": {
      "type": "string",
      "description": "Path to the step file"
    },
    "phase": {
      "type": "string",
      "description": "Phase name (for PHASE_* events)"
    },
    "outcome": {
      "type": "string",
      "enum": ["PASS", "FAIL"],
      "description": "Outcome (for PHASE_COMPLETED)"
    },
    "status": {
      "type": "string",
      "enum": ["success", "error", "warning"],
      "description": "Validation status (for *_VALIDATION events)"
    },
    "errors": {
      "type": "array",
      "items": {"type": "string"},
      "description": "Error messages (for failed events)"
    },
    "warnings": {
      "type": "array",
      "items": {"type": "string"},
      "description": "Warning messages"
    },
    "duration_ms": {
      "type": "integer",
      "minimum": 0,
      "description": "Duration in milliseconds"
    },
    "agent_id": {
      "type": "string",
      "description": "Identifier of the agent (for SubagentStop)"
    },
    "recovery_action": {
      "type": "string",
      "description": "Action taken for recovery"
    }
  }
}
```

### 3.2 Event Examples

**Task Invocation Started:**
```json
{"timestamp":"2026-01-22T10:00:00Z","event":"TASK_INVOCATION_STARTED","step_file":"steps/01-01.json"}
```

**Task Invocation Validated:**
```json
{"timestamp":"2026-01-22T10:00:01Z","event":"TASK_INVOCATION_VALIDATED","step_file":"steps/01-01.json","duration_ms":450}
```

**Task Invocation Rejected:**
```json
{"timestamp":"2026-01-22T10:00:01Z","event":"TASK_INVOCATION_REJECTED","step_file":"steps/01-01.json","errors":["MISSING: Mandatory section 'TDD_14_PHASES' not found"]}
```

**Phase Started:**
```json
{"timestamp":"2026-01-22T10:05:00Z","event":"PHASE_STARTED","step_file":"steps/01-01.json","phase":"PREPARE"}
```

**Phase Completed:**
```json
{"timestamp":"2026-01-22T10:08:00Z","event":"PHASE_COMPLETED","step_file":"steps/01-01.json","phase":"PREPARE","outcome":"PASS","duration_ms":180000}
```

**Phase Skipped:**
```json
{"timestamp":"2026-01-22T11:00:00Z","event":"PHASE_SKIPPED","step_file":"steps/01-01.json","phase":"REFACTOR_L3","blocked_by":"NOT_APPLICABLE: Single class"}
```

**SubagentStop Validation (Success):**
```json
{"timestamp":"2026-01-22T11:30:00Z","event":"SUBAGENT_STOP_VALIDATION","step_file":"steps/01-01.json","status":"success","agent_id":"ab7af5b"}
```

**SubagentStop Validation (Error):**
```json
{"timestamp":"2026-01-22T11:30:00Z","event":"SUBAGENT_STOP_VALIDATION","step_file":"steps/01-01.json","status":"error","agent_id":"ab7af5b","errors":["Phase GREEN_UNIT left IN_PROGRESS (abandoned)"]}
```

**Stale Resolution:**
```json
{"timestamp":"2026-01-22T12:00:00Z","event":"STALE_RESOLUTION","step_file":"steps/01-01.json","phase":"RED_UNIT","recovery_action":"marked_abandoned"}
```

**Scope Violation Warning:**
```json
{"timestamp":"2026-01-22T11:35:00Z","event":"SCOPE_VIOLATION_WARNING","step_file":"steps/01-01.json","warnings":["Unexpected modification: src/services/PaymentService.py"]}
```

---

## 4. DES Metadata Markers Schema

### 4.1 Marker Format

DES markers are embedded in prompts as HTML comments:

```markdown
<!-- DES-ORIGIN: command:/nw:execute -->
<!-- DES-STEP-FILE: docs/feature/auth/steps/01-01.json -->
<!-- DES-VALIDATION: required -->
<!-- DES-VERSION: 1.0 -->
```

### 4.2 Marker Definitions

| Marker | Format | Required | Description |
|--------|--------|----------|-------------|
| `DES-ORIGIN` | `command:{command}` or `ad-hoc` | Yes | Source of Task invocation |
| `DES-STEP-FILE` | Path to step file | If command | Step file being executed |
| `DES-VALIDATION` | `required` or `optional` | Yes | Whether validation gates apply |
| `DES-VERSION` | Semver string | No | DES schema version |

### 4.3 Extraction Pattern

```python
import re

MARKER_PATTERNS = {
    "origin": re.compile(r'<!-- DES-ORIGIN: (.+?) -->'),
    "step_file": re.compile(r'<!-- DES-STEP-FILE: (.+?) -->'),
    "validation": re.compile(r'<!-- DES-VALIDATION: (.+?) -->'),
    "version": re.compile(r'<!-- DES-VERSION: (.+?) -->')
}

def extract_markers(prompt: str) -> dict:
    result = {}
    for name, pattern in MARKER_PATTERNS.items():
        match = pattern.search(prompt)
        result[name] = match.group(1) if match else None
    return result
```

---

## 5. Hook Input Schema

### 5.1 SubagentStop Hook Input

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://nwave.ai/schemas/subagent-stop-input.json",
  "title": "SubagentStop Hook Input",
  "description": "Input received by SubagentStop hook via stdin",
  "type": "object",
  "required": ["session_id", "hook_event_name", "agent_id", "agent_transcript_path"],
  "properties": {
    "session_id": {
      "type": "string",
      "format": "uuid",
      "description": "Parent session identifier"
    },
    "transcript_path": {
      "type": "string",
      "description": "Path to parent session transcript"
    },
    "cwd": {
      "type": "string",
      "description": "Current working directory"
    },
    "permission_mode": {
      "type": "string",
      "description": "Permission mode of the session"
    },
    "hook_event_name": {
      "type": "string",
      "const": "SubagentStop",
      "description": "Event that triggered the hook"
    },
    "stop_hook_active": {
      "type": "boolean",
      "description": "Whether stop hook is active"
    },
    "agent_id": {
      "type": "string",
      "description": "Identifier of the sub-agent"
    },
    "agent_transcript_path": {
      "type": "string",
      "description": "Path to sub-agent transcript file"
    }
  }
}
```

### 5.2 Example Input

```json
{
  "session_id": "786ebad4-6e5b-42d3-a954-c1df6e6f25b7",
  "transcript_path": "/home/user/.claude/projects/-mnt-c-Projects-ai-craft/session.jsonl",
  "cwd": "/mnt/c/Repositories/Projects/ai-craft",
  "permission_mode": "bypassPermissions",
  "hook_event_name": "SubagentStop",
  "stop_hook_active": false,
  "agent_id": "ab7af5b",
  "agent_transcript_path": "/home/user/.claude/projects/-mnt-c-Projects-ai-craft/subagents/agent-ab7af5b.jsonl"
}
```

---

## 6. Hook Output Schema

### 6.1 Validation Result Output

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://nwave.ai/schemas/validation-result.json",
  "title": "DES Validation Result",
  "description": "Output from DES validation hooks",
  "type": "object",
  "required": ["status"],
  "properties": {
    "status": {
      "type": "string",
      "enum": ["success", "warning", "error", "skipped"],
      "description": "Overall validation status"
    },
    "step_file": {
      "type": "string",
      "description": "Path to validated step file"
    },
    "errors": {
      "type": "array",
      "items": {"type": "string"},
      "description": "List of error messages"
    },
    "warnings": {
      "type": "array",
      "items": {"type": "string"},
      "description": "List of warning messages"
    },
    "recovery_suggestions": {
      "type": "array",
      "items": {"type": "string"},
      "description": "Actionable recovery steps"
    },
    "timestamp": {
      "type": "string",
      "format": "date-time",
      "description": "When validation was performed"
    },
    "reason": {
      "type": "string",
      "description": "Reason for skipped status"
    }
  }
}
```

### 6.2 Example Outputs

**Success:**
```json
{
  "status": "success",
  "step_file": "steps/01-01.json",
  "errors": [],
  "warnings": [],
  "timestamp": "2026-01-22T11:30:00Z"
}
```

**Warning:**
```json
{
  "status": "warning",
  "step_file": "steps/01-01.json",
  "errors": [],
  "warnings": ["Phase REFACTOR_L4 has DEFERRED - blocks commit"],
  "timestamp": "2026-01-22T11:30:00Z"
}
```

**Error:**
```json
{
  "status": "error",
  "step_file": "steps/01-01.json",
  "errors": [
    "Phase GREEN_UNIT left IN_PROGRESS (abandoned)",
    "Phase REVIEW NOT_EXECUTED but task marked DONE"
  ],
  "warnings": [],
  "recovery_suggestions": [
    "Reset GREEN_UNIT phase status to NOT_EXECUTED",
    "Run /nw:execute again to resume from GREEN_UNIT"
  ],
  "timestamp": "2026-01-22T11:30:00Z"
}
```

**Skipped:**
```json
{
  "status": "skipped",
  "reason": "no_step_file",
  "timestamp": "2026-01-22T11:30:00Z"
}
```

---

## 7. Configuration Schema

### 7.1 DES Configuration

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://nwave.ai/schemas/des-config.json",
  "title": "DES Configuration",
  "type": "object",
  "properties": {
    "des_version": {
      "type": "string",
      "pattern": "^[0-9]+\\.[0-9]+$",
      "description": "DES schema version"
    },
    "validation": {
      "type": "object",
      "properties": {
        "mandatory_sections": {
          "type": "array",
          "items": {"type": "string"}
        },
        "required_phases": {
          "type": "array",
          "items": {"type": "string"},
          "minItems": 14,
          "maxItems": 14
        }
      }
    },
    "stale_detection": {
      "type": "object",
      "properties": {
        "enabled": {"type": "boolean", "default": true},
        "threshold_minutes": {"type": "integer", "minimum": 1, "default": 30}
      }
    },
    "audit": {
      "type": "object",
      "properties": {
        "rotation": {"type": "string", "enum": ["daily", "weekly", "none"]},
        "format": {"type": "string", "enum": ["jsonl", "json"]}
      }
    }
  }
}
```

### 7.2 Default Configuration

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
      "PREPARE",
      "RED_ACCEPTANCE",
      "RED_UNIT",
      "GREEN_UNIT",
      "CHECK_ACCEPTANCE",
      "GREEN_ACCEPTANCE",
      "REVIEW",
      "REFACTOR_L1",
      "REFACTOR_L2",
      "REFACTOR_L3",
      "REFACTOR_L4",
      "POST_REFACTOR_REVIEW",
      "FINAL_VALIDATE",
      "COMMIT"
    ]
  },
  "stale_detection": {
    "enabled": true,
    "threshold_minutes": 30
  },
  "audit": {
    "rotation": "daily",
    "format": "jsonl"
  }
}
```

---

## 8. Python Type Definitions

For implementation, use these Python dataclasses:

```python
# nWave/models/des_types.py
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional

class TaskStatus(Enum):
    TODO = "TODO"
    IN_PROGRESS = "IN_PROGRESS"
    DONE = "DONE"
    FAILED = "FAILED"
    PARTIAL = "PARTIAL"

class PhaseStatus(Enum):
    NOT_EXECUTED = "NOT_EXECUTED"
    IN_PROGRESS = "IN_PROGRESS"
    EXECUTED = "EXECUTED"
    SKIPPED = "SKIPPED"
    FAILED = "FAILED"

class PhaseOutcome(Enum):
    PASS = "PASS"
    FAIL = "FAIL"

@dataclass
class TestResults:
    total: int
    passed: int
    failed: int
    skipped: int = 0

@dataclass
class PhaseExecution:
    phase_name: str
    status: PhaseStatus
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    duration_minutes: Optional[float] = None
    outcome: Optional[PhaseOutcome] = None
    outcome_details: Optional[str] = None
    blocked_by: Optional[str] = None
    artifacts_created: list[str] = field(default_factory=list)
    test_results: Optional[TestResults] = None
    notes: Optional[str] = None

@dataclass
class TaskState:
    status: TaskStatus
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    failure_reason: Optional[str] = None
    recovery_suggestions: list[str] = field(default_factory=list)
    can_retry: bool = True

@dataclass
class TDDCycle:
    phase_execution_log: list[PhaseExecution]
    methodology: str = "outside-in-tdd-14-phase"

@dataclass
class StepFile:
    schema_version: str
    task_id: str
    project_id: str
    state: TaskState
    tdd_cycle: TDDCycle
    task_specification: Optional[dict] = None
    self_contained_context: Optional[dict] = None
```

---

*Data models defined by Morgan (solution-architect) during DESIGN wave.*
