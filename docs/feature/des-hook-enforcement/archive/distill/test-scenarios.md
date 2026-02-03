# DES Hook Enforcement - Acceptance Test Scenarios

## Overview

This document describes the acceptance test scenarios for the DES hook enforcement feature in plain English. These scenarios validate that hooks fire non-bypassably with tamper-evident audit proof, ensuring execution tracking provides guarantees.

## Test Strategy

### Outside-In TDD Approach
Tests drive implementation through driving ports (entry points):
- **DESOrchestrator** - System entry point for task validation
- **Hook Adapter CLI** - Python script invoked by Claude Code runtime
- **Installer CLI** - Hook installation/uninstallation lifecycle management

### One-at-a-Time Implementation
Only the first scenario is enabled initially. Each scenario is enabled sequentially as implementation progresses, preventing commit blocks from multiple failing tests.

### Hexagonal Architecture Compliance
All tests interact with public interfaces (driving ports). Internal components (DESConfig, AuditLogger, TemplateValidator) are accessed ONLY through entry points, never imported directly in tests.

---

## Scenario Categories

### Category 1: Walking Skeleton (Step 00-01)

#### Scenario: Stub hook adapter executes and proves hook firing
**Business Value**: Prove end-to-end hook firing mechanism works

**Given**: Stub adapter exists and is configured in Claude Code settings
**When**: Task tool is invoked with any prompt
**Then**:
- Stub adapter executes successfully
- Outputs valid JSON with "allow" decision
- Contains proof marker "hook_fired"
- Exits with code 0
- Hook execution is observable

**Success Criteria**:
- Claude Code CAN invoke Python script
- JSON protocol works bidirectionally (stdin/stdout)
- Tool matcher correctly identifies Task tool
- Observable proof of hook firing

---

### Category 2: Hook Audit Event Types (Step 01-01)

#### Scenario: Hook audit event types are defined and validated
**Business Value**: Enable comprehensive audit trail for hook execution

**Given**: EventType enum exists in audit_events module
**When**: EventType is checked for hook event types
**Then**:
- HOOK_PRE_TASK_PASSED exists
- HOOK_PRE_TASK_BLOCKED exists
- HOOK_SUBAGENT_STOP_PASSED exists
- HOOK_SUBAGENT_STOP_FAILED exists
- All return "HOOK" category
- validate_event_type accepts all 4 types
- Existing event types remain unchanged

**Success Criteria**:
- 4 new hook event types defined
- Event categorization works correctly
- No regression in existing event types

---

### Category 3: Rejection Audit Logging (Step 01-02)

#### Scenario: Valid task invocation produces HOOK_PRE_TASK_PASSED audit entry
**Business Value**: Audit trail contains proof of successful validation

**Given**: Hooks configured, audit enabled, fixed UTC timestamp
**When**: validate_prompt called via DESOrchestrator with valid task
**Then**:
- Returns task_invocation_allowed=True
- Audit log contains HOOK_PRE_TASK_PASSED
- Entry includes step_path and agent name
- Timestamp is UTC from TimeProvider

**Success Criteria**:
- Successful validations are audited
- Audit entry contains required context
- Timestamps are deterministic and UTC

#### Scenario: Invalid task invocation produces HOOK_PRE_TASK_BLOCKED audit entry
**Business Value**: Audit trail contains proof of rejection with reason

**Given**: Hooks configured, audit enabled, fixed UTC timestamp
**When**: validate_prompt called via DESOrchestrator with invalid task
**Then**:
- Returns task_invocation_allowed=False
- Audit log contains HOOK_PRE_TASK_BLOCKED
- Entry includes step_path, agent name, rejection reason
- Timestamp is UTC from TimeProvider

**Success Criteria**:
- Rejections are audited with reason
- Audit entry explains why blocked
- Timestamps are deterministic and UTC

---

### Category 4: SubagentStop Audit Logging (Step 01-03)

#### Scenario: Successful post-execution gate produces HOOK_SUBAGENT_STOP_PASSED
**Business Value**: Audit trail proves sub-agent completed successfully

**Given**: Hooks configured, audit enabled, step file complete
**When**: on_agent_complete called via RealSubagentStopHook
**Then**:
- Returns validation_passed=True
- Audit log contains HOOK_SUBAGENT_STOP_PASSED
- Entry includes step_path and phases_validated count
- Timestamp is UTC from TimeProvider

**Success Criteria**:
- Successful completions are audited
- Audit entry contains validation context
- Timestamps are deterministic and UTC

#### Scenario: Failed post-execution gate produces HOOK_SUBAGENT_STOP_FAILED
**Business Value**: Audit trail proves sub-agent validation failed

**Given**: Hooks configured, audit enabled, step file incomplete
**When**: on_agent_complete called via RealSubagentStopHook
**Then**:
- Returns validation_passed=False
- Audit log contains HOOK_SUBAGENT_STOP_FAILED
- Entry includes step_path, phases_validated, errors
- Timestamp is UTC from TimeProvider

**Success Criteria**:
- Failures are audited with errors
- Audit entry explains validation failures
- Orchestrator can be blocked from continuing

---

### Category 5: DES Configuration Infrastructure (Step 02-01)

#### Scenario: DES configuration loads from YAML file with defaults
**Business Value**: User can control audit verbosity via configuration

**Given**: Config file does not exist
**When**: DESConfig is loaded
**Then**:
- Config file created at ~/.claude/des/config.yaml
- audit_logging_enabled defaults to true
- File includes explanatory comments

**Success Criteria**:
- Configuration file created with safe defaults
- Comments explain each setting
- Users can customize behavior

#### Scenario: DES configuration falls back to safe defaults when file is invalid
**Business Value**: Invalid config does not break hook execution

**Given**: Config file contains invalid YAML
**When**: DESConfig is loaded
**Then**:
- audit_logging_enabled defaults to true
- No exception raised
- Fail-safe behavior

**Success Criteria**:
- Invalid/missing config handled gracefully
- Defaults ensure audit trail maintained
- No crashes due to configuration errors

#### Scenario: Hook adapter can check audit logging configuration
**Business Value**: Hooks respect user preferences for audit verbosity

**Given**: Config file with audit_logging_enabled=false
**When**: Hook adapter loads DESConfig
**Then**:
- Adapter reads config.audit_logging_enabled as false
- Can skip audit logging when disabled

**Success Criteria**:
- Adapter can access configuration
- User control over audit logging
- Validation still executes (only logging skipped)

---

### Category 6: Claude Code Hook Adapter (Step 02-02)

#### Scenario: Pre-task hook allows valid task and logs audit entry
**Business Value**: Valid tasks proceed with audit proof

**Given**: Hooks installed, audit enabled, fixed timestamp
**When**: Adapter invoked with pre-task and valid Task JSON
**Then**:
- Exits with code 0 (allow)
- Stdout contains JSON with decision=allow
- Audit log contains HOOK_PRE_TASK_PASSED
- Timestamp is UTC from TimeProvider

**Success Criteria**:
- Valid tasks allowed to proceed
- Audit proof generated
- Claude Code receives allow decision

#### Scenario: Pre-task hook blocks invalid task and logs audit entry
**Business Value**: Invalid tasks blocked with audit proof

**Given**: Hooks installed, audit enabled, fixed timestamp
**When**: Adapter invoked with pre-task and invalid Task JSON
**Then**:
- Exits with code 2 (BLOCK)
- Stdout contains JSON with decision=block and reason
- Audit log contains HOOK_PRE_TASK_BLOCKED
- Timestamp is UTC from TimeProvider

**Success Criteria**:
- Invalid tasks blocked
- Blocking reason communicated to Claude Code
- Audit proof of rejection

#### Scenario: Pre-task hook skips audit logging when disabled in config
**Business Value**: Users can disable verbose audit logging

**Given**: Hooks installed, audit disabled
**When**: Adapter invoked with pre-task and valid Task JSON
**Then**:
- Exits with code 0
- Stdout contains JSON with decision=allow
- Audit log does NOT contain HOOK_PRE_TASK_PASSED

**Success Criteria**:
- Validation still executes
- Audit logging respects configuration
- Exit codes unchanged

#### Scenario: SubagentStop hook passes when validation succeeds
**Business Value**: Orchestrator can continue after successful completion

**Given**: Hooks installed, audit enabled, step file complete
**When**: Adapter invoked with subagent-stop command
**Then**:
- Exits with code 0 (allow continuation)
- Audit log contains HOOK_SUBAGENT_STOP_PASSED
- Entry includes phases_validated count

**Success Criteria**:
- Successful completions allow orchestrator to continue
- Audit proof of validation
- Phase completion verified

#### Scenario: SubagentStop hook blocks when validation fails
**Business Value**: Orchestrator prevented from continuing with incomplete work

**Given**: Hooks installed, audit enabled, step file incomplete
**When**: Adapter invoked with subagent-stop command
**Then**:
- Exits with code 2 (BLOCK orchestrator)
- Audit log contains HOOK_SUBAGENT_STOP_FAILED
- Entry includes validation errors

**Success Criteria**:
- Incomplete work blocks orchestrator
- Audit proof of validation failure
- Errors explain what's incomplete

#### Scenario: Pre-task hook fails closed on invalid JSON input
**Business Value**: Malformed input cannot bypass validation

**Given**: Hooks installed
**When**: Adapter invoked with malformed JSON
**Then**:
- Exits with code 1 (fail-closed error)
- Stdout contains JSON with status=error
- Error reason describes JSON parse failure

**Success Criteria**:
- Malformed input triggers fail-closed
- Cannot proceed with invalid input
- Error clearly communicated

#### Scenario: Pre-task hook fails closed on missing stdin
**Business Value**: Missing input cannot bypass validation

**Given**: Hooks installed
**When**: Adapter invoked with no stdin
**Then**:
- Exits with code 1 (fail-closed error)
- Stdout contains JSON with status=error

**Success Criteria**:
- Missing input triggers fail-closed
- Cannot proceed without input
- Fail-safe behavior

#### Scenario: SubagentStop hook fails closed on unhandled exception
**Business Value**: Unexpected errors cannot bypass validation

**Given**: Hooks installed, orchestrator will raise exception
**When**: Adapter invoked with subagent-stop command
**Then**:
- Exits with code 1 (fail-closed error)
- Stdout contains JSON with status=error and reason

**Success Criteria**:
- Unhandled exceptions trigger fail-closed
- Cannot validate = cannot proceed
- Error context preserved

#### Scenario: Hook adapter works cross-platform via Python entry point
**Business Value**: Hooks work on Windows, macOS, Linux

**Given**: Hooks installed
**When**: Adapter invoked via python3 path
**Then**:
- Executes successfully on current platform
- No shell scripts required
- No OS-specific commands

**Success Criteria**:
- Pure Python implementation
- Cross-platform compatibility
- No bash/shell dependencies

---

### Category 7: Hook Installer/Uninstaller (Step 03-01)

#### Scenario: Installer merges DES hooks into existing settings.local.json
**Business Value**: Installation preserves existing hook configuration

**Given**: settings.local.json exists with non-DES hooks
**When**: Installer run with --install
**Then**:
- Exits with code 0
- settings.local.json contains DES PreToolUse and SubagentStop hooks
- Preserves all existing non-DES hooks
- Valid JSON

**Success Criteria**:
- Existing configuration preserved
- DES hooks added correctly
- No data loss

#### Scenario: Installer creates settings.local.json if it does not exist
**Business Value**: Installation works on clean Claude Code setup

**Given**: settings.local.json does not exist
**When**: Installer run with --install
**Then**:
- Exits with code 0
- settings.local.json created
- Contains DES PreToolUse and SubagentStop hooks
- Valid JSON

**Success Criteria**:
- Fresh installation supported
- Configuration file created
- Hooks properly configured

#### Scenario: Installer is idempotent when DES hooks already installed
**Business Value**: Re-running installer doesn't corrupt configuration

**Given**: DES hooks already installed
**When**: Installer run with --install
**Then**:
- Exits with code 0
- Exactly one DES PreToolUse hook
- Exactly one DES SubagentStop hook
- No duplicates

**Success Criteria**:
- Idempotent installation
- No duplicate hooks
- Safe to re-run

#### Scenario: Installer configures PreToolUse hook with Task tool matcher
**Business Value**: Hook fires automatically on Task tool invocation

**Given**: settings.local.json does not exist
**When**: Installer run with --install
**Then**:
- PreToolUse hook has matcher="Task"
- Command invokes Python adapter with pre-task argument
- Uses python3, not shell

**Success Criteria**:
- Hook correctly targeted to Task tool
- Python entry point configured
- Cross-platform command

#### Scenario: Installer configures SubagentStop hook pointing to Python adapter
**Business Value**: Hook fires automatically after sub-agent completes

**Given**: settings.local.json does not exist
**When**: Installer run with --install
**Then**:
- SubagentStop hook configured
- Command invokes Python adapter with subagent-stop argument
- Uses python3, not shell

**Success Criteria**:
- SubagentStop hook configured
- Python entry point configured
- Cross-platform command

#### Scenario: Uninstaller removes only DES hooks preserving other hooks
**Business Value**: Uninstallation doesn't break other hooks

**Given**: settings.local.json contains DES and non-DES hooks
**When**: Installer run with --uninstall
**Then**:
- Exits with code 0
- DES hooks removed
- Non-DES hooks preserved
- Valid JSON

**Success Criteria**:
- Selective removal
- No data loss for other hooks
- Clean uninstall

#### Scenario: Uninstaller handles missing settings.local.json gracefully
**Business Value**: Uninstallation doesn't crash on missing file

**Given**: settings.local.json does not exist
**When**: Installer run with --uninstall
**Then**:
- Exits with code 0
- No exception raised

**Success Criteria**:
- Graceful handling of missing file
- No errors
- Idempotent uninstall

#### Scenario: After installation hooks fire and produce audit entries
**Business Value**: End-to-end validation of installed hooks

**Given**: Installer run successfully, session restarted, audit enabled
**When**: Task tool invoked via DESOrchestrator
**Then**:
- Audit log contains HOOK_PRE_TASK_PASSED

**Success Criteria**:
- Installed hooks actually fire
- Audit trail generated
- End-to-end integration working

#### Scenario: After uninstallation hooks do not fire
**Business Value**: Uninstallation completely removes hook behavior

**Given**: Hooks installed, then uninstalled, session restarted
**When**: Task tool invoked via DESOrchestrator
**Then**:
- Audit log does NOT contain HOOK_PRE_TASK_PASSED
- No DES hook entries in audit log

**Success Criteria**:
- Hooks completely removed
- No trace of hook execution
- Clean uninstallation

---

## Test Execution Strategy

### Phase 1: Walking Skeleton
Enable and implement first scenario to prove hook firing mechanism works end-to-end. This validates:
- Claude Code can invoke Python scripts
- JSON protocol works
- Tool matcher works
- Observable proof of execution

### Phase 2: Audit Infrastructure
Enable and implement audit event types and logging scenarios. This validates:
- Event type definitions
- Audit log writing
- Timestamp generation via TimeProvider
- Context preservation in audit entries

### Phase 3: Configuration and Adapter
Enable and implement configuration and adapter scenarios. This validates:
- Configuration loading and defaults
- Hook adapter protocol translation
- Fail-closed behavior
- Cross-platform compatibility

### Phase 4: Installation Lifecycle
Enable and implement installer scenarios. This validates:
- Hook installation/uninstallation
- Configuration merging
- Idempotent operations
- End-to-end integration

---

## Success Metrics

### Coverage Metrics
- ✅ All 7 roadmap steps have acceptance scenarios
- ✅ Happy path, error path, and edge cases covered
- ✅ Installation, operation, and uninstallation lifecycle covered

### Quality Metrics
- ✅ All scenarios use Given-When-Then format
- ✅ Business language (no technical jargon)
- ✅ Observable outcomes (audit log, exit codes, file state)
- ✅ Hexagonal architecture compliance (entry points only)

### Implementation Metrics
- ✅ First scenario enabled (no @skip)
- ✅ All other scenarios marked @pytest.mark.skip
- ✅ Step definitions import entry points (DESOrchestrator, CLI adapters)
- ✅ Production services called (no mocks for entry points)
- ✅ FakeTimeProvider enables deterministic testing

---

## Implementation Readiness

### Pre-Implementation Checklist
- [x] Acceptance tests created in Gherkin format
- [x] Step definitions implemented with pytest-bdd
- [x] Fixtures configured for test isolation
- [x] First scenario enabled for Outside-In TDD
- [x] Hexagonal boundary enforcement validated

### Ready for DEVELOP Wave
These acceptance tests provide the foundation for Outside-In TDD implementation. The software-crafter will:
1. Run first acceptance test → RED (fails)
2. Implement minimal code to pass test → GREEN
3. Refactor while keeping tests green → REFACTOR
4. Enable next scenario and repeat

The acceptance tests serve as executable specifications driving implementation through the double-loop TDD cycle.
