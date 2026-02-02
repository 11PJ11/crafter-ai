Feature: Hook Enforcement
  As a DES user
  I want hooks to fire non-bypassably with tamper-evident audit proof
  So that execution tracking provides guarantees and audit trail is trustworthy

  Background:
    Given a clean DES environment
    And the audit log is cleared

  # Step 00-01: Walking Skeleton
  Scenario: Stub hook adapter executes and proves hook firing
    Given stub adapter exists at src/des/adapters/drivers/hooks/claude_code_hook_adapter.py
    And stub adapter configured in .claude/settings.local.json for PreToolUse on Task tool
    And Claude Code session has been restarted
    When I invoke Task tool with any prompt
    Then stub adapter executes successfully
    And stdout contains valid JSON with decision allow
    And stdout contains proof marker hook_fired
    And stub exits with code 0
    And hook execution is observable via stdout or log

  # Step 01-01: Add hook audit event types
  Scenario: Hook audit event types are defined and validated
    Given EventType enum exists in audit_events module
    When I check EventType for hook event types
    Then EventType contains HOOK_PRE_TASK_PASSED
    And EventType contains HOOK_PRE_TASK_BLOCKED
    And EventType contains HOOK_SUBAGENT_STOP_PASSED
    And EventType contains HOOK_SUBAGENT_STOP_FAILED
    And get_event_category returns HOOK for HOOK_PRE_TASK_PASSED
    And get_event_category returns HOOK for HOOK_PRE_TASK_BLOCKED
    And get_event_category returns HOOK for HOOK_SUBAGENT_STOP_PASSED
    And get_event_category returns HOOK for HOOK_SUBAGENT_STOP_FAILED
    And validate_event_type accepts all 4 new hook event types
    And all existing event types remain unchanged

  # Step 01-02: Add rejection audit logging to orchestrator
  Scenario: Valid task invocation produces HOOK_PRE_TASK_PASSED audit entry
    Given DES hooks are configured
    And audit logging is enabled in config
    And TimeProvider is configured to return fixed UTC timestamp
    When I invoke validate_prompt via DESOrchestrator with valid task prompt
    Then validate_prompt returns task_invocation_allowed True
    And audit log contains HOOK_PRE_TASK_PASSED entry
    And audit entry includes step_path from task prompt
    And audit entry includes agent name from task prompt
    And audit entry timestamp is UTC from TimeProvider

  Scenario: Invalid task invocation produces HOOK_PRE_TASK_BLOCKED audit entry
    Given DES hooks are configured
    And audit logging is enabled in config
    And TimeProvider is configured to return fixed UTC timestamp
    When I invoke validate_prompt via DESOrchestrator with invalid task prompt
    Then validate_prompt returns task_invocation_allowed False
    And audit log contains HOOK_PRE_TASK_BLOCKED entry
    And audit entry includes step_path from task prompt
    And audit entry includes agent name from task prompt
    And audit entry includes rejection reason
    And audit entry timestamp is UTC from TimeProvider

  # Step 01-03: Add audit logging to SubagentStop hook
  Scenario: Successful post-execution gate produces HOOK_SUBAGENT_STOP_PASSED
    Given DES hooks are configured
    And audit logging is enabled in config
    And TimeProvider is configured to return fixed UTC timestamp
    And step file has all phases complete with passing status
    When I invoke on_agent_complete via RealSubagentStopHook with completed step
    Then on_agent_complete returns validation success
    And audit log contains HOOK_SUBAGENT_STOP_PASSED entry
    And audit entry includes step_path
    And audit entry includes phases_validated count
    And audit entry timestamp is UTC from TimeProvider

  Scenario: Failed post-execution gate produces HOOK_SUBAGENT_STOP_FAILED
    Given DES hooks are configured
    And audit logging is enabled in config
    And TimeProvider is configured to return fixed UTC timestamp
    And step file has incomplete phases
    When I invoke on_agent_complete via RealSubagentStopHook with incomplete step
    Then on_agent_complete returns validation failure
    And audit log contains HOOK_SUBAGENT_STOP_FAILED entry
    And audit entry includes step_path
    And audit entry includes phases_validated count
    And audit entry includes validation errors
    And audit entry timestamp is UTC from TimeProvider

  # Step 02-01: Create DES configuration infrastructure
  Scenario: DES configuration loads from YAML file with defaults
    Given DES configuration file does not exist at ~/.claude/des/config.yaml
    When I load DESConfig
    Then config file is created at ~/.claude/des/config.yaml
    And config.audit_logging_enabled defaults to true
    And config file includes explanatory comments for each setting

  Scenario: DES configuration falls back to safe defaults when file is invalid
    Given DES configuration file exists but contains invalid YAML
    When I load DESConfig
    Then config.audit_logging_enabled defaults to true
    And no exception is raised

  Scenario: Hook adapter can check audit logging configuration
    Given DES configuration file exists with audit_logging_enabled set to false
    When hook adapter loads DESConfig
    Then adapter can read config.audit_logging_enabled as false

  # Step 02-02: Create Claude Code hook adapter with config checking
  Scenario: Pre-task hook allows valid task and logs audit entry
    Given DES hooks are installed
    And audit logging is enabled in config
    And TimeProvider returns fixed UTC timestamp
    When I invoke hook adapter CLI with pre-task command and valid Task JSON via stdin
    Then adapter exits with code 0
    And stdout contains JSON with decision allow
    And audit log contains HOOK_PRE_TASK_PASSED entry
    And audit entry timestamp is UTC from TimeProvider

  Scenario: Pre-task hook blocks invalid task and logs audit entry
    Given DES hooks are installed
    And audit logging is enabled in config
    And TimeProvider returns fixed UTC timestamp
    When I invoke hook adapter CLI with pre-task command and invalid Task JSON via stdin
    Then adapter exits with code 2
    And stdout contains JSON with decision block
    And stdout contains rejection reason in JSON
    And audit log contains HOOK_PRE_TASK_BLOCKED entry
    And audit entry includes rejection reason
    And audit entry timestamp is UTC from TimeProvider

  Scenario: Pre-task hook skips audit logging when disabled in config
    Given DES hooks are installed
    And audit logging is disabled in config
    When I invoke hook adapter CLI with pre-task command and valid Task JSON via stdin
    Then adapter exits with code 0
    And stdout contains JSON with decision allow
    And audit log does not contain HOOK_PRE_TASK_PASSED entry

  Scenario: SubagentStop hook passes when validation succeeds
    Given DES hooks are installed
    And audit logging is enabled in config
    And TimeProvider returns fixed UTC timestamp
    And step file has all phases complete
    When I invoke hook adapter CLI with subagent-stop command and step context via stdin
    Then adapter exits with code 0
    And audit log contains HOOK_SUBAGENT_STOP_PASSED entry
    And audit entry includes phases_validated count
    And audit entry timestamp is UTC from TimeProvider

  Scenario: SubagentStop hook blocks when validation fails
    Given DES hooks are installed
    And audit logging is enabled in config
    And TimeProvider returns fixed UTC timestamp
    And step file has incomplete phases
    When I invoke hook adapter CLI with subagent-stop command and step context via stdin
    Then adapter exits with code 2
    And audit log contains HOOK_SUBAGENT_STOP_FAILED entry
    And audit entry includes validation errors
    And audit entry timestamp is UTC from TimeProvider

  Scenario: Pre-task hook fails closed on invalid JSON input
    Given DES hooks are installed
    When I invoke hook adapter CLI with pre-task command and malformed JSON via stdin
    Then adapter exits with code 1
    And stdout contains JSON with status error
    And stdout contains error reason describing JSON parse failure

  Scenario: Pre-task hook fails closed on missing stdin
    Given DES hooks are installed
    When I invoke hook adapter CLI with pre-task command and no stdin
    Then adapter exits with code 1
    And stdout contains JSON with status error

  Scenario: SubagentStop hook fails closed on unhandled exception
    Given DES hooks are installed
    And orchestrator.on_agent_complete will raise unexpected exception
    When I invoke hook adapter CLI with subagent-stop command via stdin
    Then adapter exits with code 1
    And stdout contains JSON with status error
    And stdout contains error reason

  Scenario: Hook adapter works cross-platform via Python entry point
    Given DES hooks are installed
    When I invoke hook adapter via python3 src/des/adapters/drivers/hooks/claude_code_hook_adapter.py pre-task
    Then adapter executes successfully on current platform
    And no shell scripts are required
    And no OS-specific commands are used

  # Step 03-01: Create hook installer with install/uninstall lifecycle
  Scenario: Installer merges DES hooks into existing settings.local.json
    Given .claude/settings.local.json exists with existing non-DES hooks
    When I run installer via python3 scripts/install/install_des_hooks.py --install
    Then installer exits with code 0
    And .claude/settings.local.json contains DES PreToolUse hook for Task tool
    And .claude/settings.local.json contains DES SubagentStop hook
    And .claude/settings.local.json preserves all existing non-DES hooks
    And .claude/settings.local.json is valid JSON

  Scenario: Installer creates settings.local.json if it does not exist
    Given .claude/settings.local.json does not exist
    When I run installer via python3 scripts/install/install_des_hooks.py --install
    Then installer exits with code 0
    And .claude/settings.local.json is created
    And .claude/settings.local.json contains DES PreToolUse hook
    And .claude/settings.local.json contains DES SubagentStop hook
    And .claude/settings.local.json is valid JSON

  Scenario: Installer is idempotent when DES hooks already installed
    Given DES hooks are already installed in .claude/settings.local.json
    When I run installer via python3 scripts/install/install_des_hooks.py --install
    Then installer exits with code 0
    And .claude/settings.local.json contains exactly one DES PreToolUse hook
    And .claude/settings.local.json contains exactly one DES SubagentStop hook

  Scenario: Installer configures PreToolUse hook with Task tool matcher
    Given .claude/settings.local.json does not exist
    When I run installer via python3 scripts/install/install_des_hooks.py --install
    Then .claude/settings.local.json contains PreToolUse hook
    And PreToolUse hook has matcher for Task tool
    And PreToolUse hook command invokes Python adapter with pre-task argument
    And PreToolUse hook command uses python3 not shell

  Scenario: Installer configures SubagentStop hook pointing to Python adapter
    Given .claude/settings.local.json does not exist
    When I run installer via python3 scripts/install/install_des_hooks.py --install
    Then .claude/settings.local.json contains SubagentStop hook
    And SubagentStop hook command invokes Python adapter with subagent-stop argument
    And SubagentStop hook command uses python3 not shell

  Scenario: Uninstaller removes only DES hooks preserving other hooks
    Given .claude/settings.local.json contains DES hooks and other non-DES hooks
    When I run installer via python3 scripts/install/install_des_hooks.py --uninstall
    Then installer exits with code 0
    And .claude/settings.local.json does not contain DES PreToolUse hook
    And .claude/settings.local.json does not contain DES SubagentStop hook
    And .claude/settings.local.json preserves all non-DES hooks
    And .claude/settings.local.json is valid JSON

  Scenario: Uninstaller handles missing settings.local.json gracefully
    Given .claude/settings.local.json does not exist
    When I run installer via python3 scripts/install/install_des_hooks.py --uninstall
    Then installer exits with code 0
    And no exception is raised

  Scenario: After installation hooks fire and produce audit entries
    Given installer has been run successfully
    And Claude Code session has been restarted
    And audit logging is enabled in config
    When I invoke Task tool with valid prompt via DESOrchestrator
    Then audit log contains HOOK_PRE_TASK_PASSED entry

  Scenario: After uninstallation hooks do not fire
    Given DES hooks were installed
    And installer uninstall has been run successfully
    And Claude Code session has been restarted
    When I invoke Task tool with valid prompt via DESOrchestrator
    Then audit log does not contain HOOK_PRE_TASK_PASSED entry
    And no DES hook entries appear in audit log
