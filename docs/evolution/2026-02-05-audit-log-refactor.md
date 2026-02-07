# Audit Log Refactor: step_path to feature_name + step_id

**Date**: 2026-02-05
**Project ID**: audit-log-refactor
**Status**: COMPLETED
**Phases**: 7 phases, 16 steps

## Motivation

The audit log schema used a single `step_path` field containing a file system path
(e.g., `"docs/feature/my-feature/steps/03-02.yaml"`). This created tight coupling between
the audit event schema and the file system layout:

1. **Implementation-coupled**: Renaming or moving step files would invalidate historical audit entries
2. **Hard to query**: Extracting "which feature?" or "which step?" required parsing a path string
3. **Fragile**: File system refactoring could silently break audit log consumers

The refactoring replaces `step_path` with two semantic fields: `feature_name` and `step_id`.

## Before / After

### Before (v1.x schema)

```json
{
  "event": "PHASE_COMPLETED",
  "timestamp": "2026-02-05T14:30:00Z",
  "step_path": "docs/feature/audit-log-refactor/steps/03-02.yaml",
  "phase_name": "GREEN",
  "data": {"tests_passed": 12}
}
```

### After (v2.0 schema)

```json
{
  "event": "PHASE_COMPLETED",
  "timestamp": "2026-02-05T14:30:00Z",
  "feature_name": "audit-log-refactor",
  "step_id": "03-02",
  "phase_name": "GREEN",
  "data": {"tests_passed": 12}
}
```

### Key Differences

| Aspect | v1.x (`step_path`) | v2.0 (`feature_name` + `step_id`) |
|--------|---------------------|-------------------------------------|
| Coupling | Tied to file system layout | Decoupled, semantic identifiers |
| Querying | Parse path string: `split("/")` | Direct field access: `.feature_name` |
| Stability | Breaks on file moves | Stable across restructuring |
| Filtering | `jq 'select(.step_path \| contains("audit-log"))'` | `jq 'select(.feature_name=="audit-log-refactor")'` |

## Affected Components

### Production Code

| File | Change |
|------|--------|
| `src/des/ports/driven_ports/audit_log_writer.py` | Added `feature_name` and `step_id` as optional fields on `PortAuditEvent` dataclass |
| `src/des/adapters/driven/logging/jsonl_audit_log_writer.py` | Serializes `feature_name` and `step_id` as top-level JSON fields |
| `src/des/application/subagent_stop_service.py` | Passes `feature_name` and `step_id` directly to `PortAuditEvent` instead of embedding in `data` dict |
| `src/des/application/orchestrator.py` | Extracts `feature_name`/`step_id` from kwargs, passes as direct `PortAuditEvent` fields; `render_prompt` and `validate_prompt` updated |

### Test Code

| File | Change |
|------|--------|
| `tests/des/unit/ports/driven_ports/test_audit_log_writer_port.py` | Tests `feature_name`/`step_id` as direct dataclass fields |
| `tests/des/unit/application/test_subagent_stop_service_audit.py` | Asserts `feature_name`/`step_id` passed as direct fields, not in data dict |
| `tests/des/unit/application/test_orchestrator_audit_helper.py` | Verifies `_log_audit_event` extracts and passes feature_name/step_id |
| `tests/des/unit/application/test_orchestrator_validate_prompt_audit.py` | Verifies validate_prompt passes feature_name in audit events |
| `tests/des/unit/application/test_orchestrator_render_prompt_audit.py` | Verifies render_prompt passes feature_name in audit events |
| `tests/des/acceptance/test_hook_enforcement.feature` | BDD scenarios validating feature_name/step_id as direct fields |
| `tests/des/acceptance/test_hook_enforcement_steps.py` | Step definitions for BDD hook enforcement tests |

### Documentation

| File | Change |
|------|--------|
| `nWave/templates/.des-audit-README.md` | Updated jq queries from `.step_path` to `.feature_name`/`.step_id`, added schema section |
| `docs/evolution/2026-02-05-audit-log-refactor.md` | This document |

## Implementation Timeline

### Phase 1: Schema Changes (Steps 01-01, 01-02, 01-03)

Added `feature_name` and `step_id` as optional fields to `PortAuditEvent` dataclass in the port layer.
Updated the JSONL adapter to serialize these fields. Verified backward compatibility (fields are optional).

### Phase 2: Service Layer Updates (Steps 02-01, 02-02)

Updated `SubagentStopService` to pass `feature_name` and `step_id` as direct `PortAuditEvent` constructor
arguments instead of embedding them in the `data` dictionary.

### Phase 3: Orchestrator Updates (Steps 03-01, 03-02)

Updated the orchestrator's `_log_audit_event` helper to extract `feature_name` and `step_id` from kwargs
and pass them as direct fields. Updated `render_prompt` and `validate_prompt` to include `feature_name`.

### Phase 4: Test Migration (Steps 04-01, 04-02)

Migrated legacy tests to assert on `feature_name`/`step_id` as direct fields. Removed tests that
asserted on `step_path` or checked these values inside the `data` dictionary.

### Phase 5: Acceptance Tests (Steps 05-01, 05-02)

Updated acceptance test fixtures to use the new schema. Created BDD scenarios for hook enforcement
that validate `feature_name` and `step_id` as direct fields across all event types.

### Phase 6: Documentation (Steps 06-01, 06-02)

Updated execution log documentation. Updated audit README template with new schema reference and
query examples. Created this evolution document.

### Phase 7: Finalization (Step 07-01)

Final validation that all tests pass, all acceptance criteria met, and documentation complete.

## Test Coverage

- **587 tests passing** across the DES test suite
- **4 BDD scenarios** specifically validating the new schema fields
- **23 hexagonal unit tests** covering port and adapter layers
- **11 orchestrator audit tests** covering service layer integration
- **15 subagent stop service tests** covering event field propagation

## Lessons Learned

1. **Semantic fields over path fields**: File paths as identifiers create unnecessary coupling.
   Semantic identifiers (`feature_name`, `step_id`) are stable, queryable, and human-readable.

2. **Optional fields for backward compatibility**: Making new fields optional allowed incremental
   migration without breaking existing consumers.

3. **Outside-In TDD for schema changes**: Starting from the port layer (acceptance criteria) and
   working inward to adapters and services ensured each layer was tested through its driving port.

---

**Completed**: 2026-02-07
**Steps**: 16 across 7 phases
