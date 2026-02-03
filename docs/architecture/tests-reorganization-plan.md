# Tests Directory Reorganization Plan
## Aligning with DES Plugin Hexagonal Architecture Structure

**Date**: 2026-02-03
**Status**: Proposed Plan - Awaiting Review
**Scope**: Complete reorganization of `/tests/` directory to mirror DES hexagonal architecture

---

## Executive Summary

This plan reorganizes the entire `/tests/` directory to align with the hexagonal architecture structure implemented in the DES plugin (`src/des/`). The current test organization is fragmented, with tests scattered across multiple locations and no clear organizational principle. The new structure will:

1. **Mirror the source code structure** - Tests follow the same hexagonal layers as production code
2. **Separate concerns by test type** - Clear boundaries between unit, integration, acceptance, and e2e tests
3. **Consolidate duplicated test infrastructure** - Share test doubles and fixtures efficiently
4. **Enable better test discovery** - Developers can easily find tests for any component

---

## Understanding the DES Plugin Structure

### What is the DES Plugin?

The **DES (Deterministic Execution System)** plugin is a post-execution validation system that follows **hexagonal architecture** (also known as ports and adapters pattern). It validates that sub-agents complete execution properly, tracks phase progression, and detects deviations from expected behavior.

### DES Hexagonal Architecture Layers

```
┌─────────────────────────────────────────────────────────────────┐
│                        EXTERNAL WORLD                            │
│  (Hooks, Validators, File System, Time, Logging, Config)        │
└────────────────┬────────────────────────────────────────────────┘
                 │
    ┌────────────┴────────────┐
    │                         │
    ▼ (PRIMARY ADAPTERS)      ▼ (SECONDARY ADAPTERS)
┌──────────────────┐    ┌──────────────────────────┐
│ ADAPTERS/DRIVERS │    │ ADAPTERS/DRIVEN          │
├──────────────────┤    ├──────────────────────────┤
│ hooks/           │    │ filesystem/              │
│ validators/      │    │ time/                    │
└────────┬─────────┘    │ logging/                 │
         │              │ config/                  │
         │              │ task_invocation/         │
         │              │ validation/              │
         │              └──────────┬───────────────┘
         │                         │
         │ (implements)            │ (implements)
         │                         │
         ▼                         ▼
    ┌────────────────────────────────────────┐
    │          PORTS (Abstractions)          │
    ├────────────────────────────────────────┤
    │ DRIVER_PORTS (Inbound)                 │
    │  • hook_port                           │
    │  • validator_port                      │
    │                                        │
    │ DRIVEN_PORTS (Outbound)                │
    │  • filesystem_port                     │
    │  • time_provider_port                  │
    │  • logging_port                        │
    │  • config_port                         │
    │  • task_invocation_port                │
    └────────────────┬──────────────────────┘
                     │
                     │ (uses)
                     │
    ┌────────────────▼──────────────────────┐
    │     APPLICATION LAYER                 │
    ├───────────────────────────────────────┤
    │ • orchestrator.py                     │
    │ • hooks.py                            │
    │ • validator.py                        │
    │ • config_loader.py                    │
    │ • boundary_rules_generator.py         │
    │ • prompt_validator.py                 │
    │ • recovery_guidance_handler.py        │
    │ • schema_rollback_handler.py          │
    │ • stale_execution_detector.py         │
    │ • stale_resolver.py                   │
    │ • tdd_template_loader.py              │
    └────────────────┬──────────────────────┘
                     │
                     │ (uses)
                     │
    ┌────────────────▼──────────────────────┐
    │      DOMAIN LAYER (Core Logic)        │
    ├───────────────────────────────────────┤
    │ • turn_counter.py                     │
    │ • timeout_monitor.py                  │
    │ • turn_config.py                      │
    │ • invocation_limits_validator.py      │
    │ • phase_state_validator.py            │
    │ • abandoned_phase_detector.py         │
    │ • silent_completion_detector.py       │
    │ • stale_detection_result.py           │
    │ • stale_execution.py                  │
    │ • timeout_instruction_template.py     │
    │ • validation_error_detector.py        │
    └───────────────────────────────────────┘
```

**Key Layers:**
- **Domain**: Pure business logic with no external dependencies
- **Application**: Orchestration and use cases, uses ports
- **Ports**: Abstract interfaces (driver ports = inbound, driven ports = outbound)
- **Adapters**: Concrete implementations
  - **drivers/**: PRIMARY adapters (entry points - how external code calls us)
  - **driven/**: SECONDARY adapters (dependencies - how we call external systems)

---

## Current Test Directory Organization

### Current Structure

```
tests/
├── __init__.py
├── conftest.py (root-level fixtures)
│
├── acceptance/ (MIXED - versioning, installation, des features)
│   ├── features/
│   │   ├── version-update-experience/
│   │   └── versioning-release-management/
│   ├── installation/
│   ├── versioning/
│   ├── versioning_release_management/
│   ├── test_us004_audit_trail.py (DES)
│   ├── test_us004_turn_counting.py (DES)
│   └── test_validator_acceptance.py (DES)
│
├── des/ (PARTIALLY ORGANIZED - follows hexagonal structure partially)
│   ├── acceptance/ (12 user story tests)
│   ├── adapters/ (4 test doubles - mocked_hook, mocked_validator, etc.)
│   ├── e2e/ (2 scenario tests)
│   ├── integration/ (3 integration tests)
│   ├── unit/ (extensive - mirrors src/des structure)
│   │   ├── adapters/
│   │   │   ├── driven/
│   │   │   │   ├── config/
│   │   │   │   ├── logging/
│   │   │   │   └── task_invocation/
│   │   │   └── drivers/
│   │   │       ├── hooks/
│   │   │       └── validators/
│   │   ├── application/
│   │   ├── domain/
│   │   ├── install/
│   │   └── ports/
│   └── conftest.py
│
├── cli/ (CLI tests - small)
├── e2e/ (single test)
├── install/ (3 plugin tests)
├── installer/ (comprehensive installer tests - mirrors src/installer)
│   ├── adapters/
│   ├── checks/
│   ├── cli/
│   ├── config/
│   ├── domain/
│   └── services/
├── integration/ (empty directory)
├── nwave/ (2 template/schema tests)
├── unit/ (MIXED - various features)
│   ├── backup/
│   ├── cli/
│   ├── des/ (DES-specific unit tests NOT in tests/des/)
│   ├── domain/
│   ├── git_workflow/
│   ├── ports/
│   ├── update/
│   ├── version/
│   ├── version_management/
│   └── versioning/
└── validation/ (single file)
```

### Problems with Current Structure

1. **Scattered Test Organization**:
   - DES tests in 3 locations: `tests/des/`, `tests/unit/des/`, `tests/acceptance/test_us004_*`
   - Versioning tests scattered: `tests/acceptance/versioning/`, `tests/unit/versioning/`, `tests/acceptance/versioning_release_management/`
   - No consistent pattern for where tests should live

2. **Incomplete Hexagonal Mirroring**:
   - `tests/des/unit/` partially mirrors `src/des/` but inconsistent
   - Other features don't follow hexagonal structure at all
   - Test doubles scattered (some in `tests/des/adapters/`, some inline in tests)

3. **Confusing Test Type Boundaries**:
   - "acceptance" directory contains both feature tests and user story tests
   - "unit" directory contains tests for multiple unrelated features
   - No clear separation between unit, integration, acceptance, e2e for non-DES code

4. **Duplication and Fragmentation**:
   - Multiple `conftest.py` files with overlapping fixtures
   - Test data builders and helpers duplicated across directories
   - Shared test utilities not centralized

5. **Poor Discoverability**:
   - Developer question: "Where do I put tests for a new versioning feature?" - unclear
   - Developer question: "Where are all the installer tests?" - scattered
   - No single source of truth for test organization

---

## Proposed Test Directory Structure

### Top-Level Organization Principle

**Mirror the source structure at the top level, then organize by test type within each feature/plugin.**

```
tests/
├── __init__.py
├── conftest.py (root-level shared fixtures)
│
├── shared/                          # NEW - Shared test infrastructure
│   ├── __init__.py
│   ├── builders/                    # Test data builders
│   │   ├── __init__.py
│   │   ├── des_builders.py
│   │   ├── installer_builders.py
│   │   └── versioning_builders.py
│   ├── fixtures/                    # Shared fixtures
│   │   ├── __init__.py
│   │   ├── filesystem_fixtures.py
│   │   ├── git_fixtures.py
│   │   └── time_fixtures.py
│   └── matchers/                    # Custom test matchers
│       ├── __init__.py
│       └── custom_matchers.py
│
├── des/                             # DES Plugin Tests (hexagonal structure)
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_doubles/                # RENAMED from adapters/ - clearer purpose
│   │   ├── __init__.py
│   │   ├── mocked_hook.py
│   │   ├── mocked_validator.py
│   │   ├── mocked_time.py
│   │   ├── in_memory_filesystem.py
│   │   └── mocked_config.py
│   │
│   ├── unit/                        # Isolated component tests
│   │   ├── __init__.py
│   │   ├── domain/                  # Domain logic tests
│   │   │   ├── __init__.py
│   │   │   ├── test_turn_counter.py
│   │   │   ├── test_timeout_monitor.py
│   │   │   ├── test_turn_config.py
│   │   │   ├── test_invocation_limits_validator.py
│   │   │   ├── test_phase_state_validator.py
│   │   │   ├── test_abandoned_phase_detector.py
│   │   │   ├── test_silent_completion_detector.py
│   │   │   ├── test_validation_error_detector.py
│   │   │   ├── test_timeout_instruction_template_helpers.py
│   │   │   ├── test_stale_detection_result.py
│   │   │   └── test_stale_execution.py
│   │   │
│   │   ├── application/             # Application service tests
│   │   │   ├── __init__.py
│   │   │   ├── test_orchestrator.py
│   │   │   ├── test_hooks.py
│   │   │   ├── test_boundary_rules_generator.py
│   │   │   ├── test_boundary_rules_template.py
│   │   │   ├── test_config_loader.py (MOVED from test_orchestrator_schema_versioning)
│   │   │   ├── test_prompt_validator.py (MOVED from adapters/drivers/validators)
│   │   │   ├── test_recovery_guidance_handler.py
│   │   │   ├── test_schema_rollback_handler.py
│   │   │   ├── test_stale_execution_detector.py
│   │   │   ├── test_stale_resolver.py
│   │   │   ├── test_tdd_template_loader.py
│   │   │   ├── test_timeout_instruction_template.py
│   │   │   ├── test_orchestrator_execute_step.py
│   │   │   ├── test_orchestrator_e2e_wiring.py
│   │   │   ├── test_orchestrator_prompt_warnings.py
│   │   │   ├── test_orchestrator_recovery_integration.py
│   │   │   ├── test_orchestrator_research_command.py
│   │   │   ├── test_orchestrator_stale_check.py
│   │   │   ├── test_orchestrator_timeout_instruction.py
│   │   │   ├── test_orchestrator_validate_prompt_audit.py
│   │   │   ├── test_orchestrator_schema_versioning.py (config-related)
│   │   │   └── test_validator_schema_versioning.py
│   │   │
│   │   ├── ports/                   # Port interface tests
│   │   │   ├── __init__.py
│   │   │   ├── test_config_port.py
│   │   │   ├── test_logging_port.py
│   │   │   └── test_task_invocation_port.py
│   │   │
│   │   └── adapters/                # Adapter implementation tests
│   │       ├── __init__.py
│   │       ├── driven/
│   │       │   ├── __init__.py
│   │       │   ├── config/
│   │       │   │   ├── __init__.py
│   │       │   │   └── test_des_config.py
│   │       │   ├── filesystem/
│   │       │   │   └── __init__.py
│   │       │   ├── logging/
│   │       │   │   ├── __init__.py
│   │       │   │   ├── test_audit_events_hook_types.py
│   │       │   │   ├── test_audit_logger_scope_violation.py
│   │       │   │   ├── test_audit_logger_01_01.py (MOVED from tests/unit/des/)
│   │       │   │   └── test_audit_logger_unit.py (MOVED from tests/unit/des/)
│   │       │   ├── task_invocation/
│   │       │   │   └── __init__.py
│   │       │   ├── time/
│   │       │   │   └── __init__.py
│   │       │   └── validation/
│   │       │       ├── __init__.py
│   │       │       └── test_scope_validator.py (MOVED from test_unit/)
│   │       │
│   │       └── drivers/
│   │           ├── __init__.py
│   │           ├── hooks/
│   │           │   ├── __init__.py
│   │           │   ├── test_claude_code_hook_adapter.py
│   │           │   ├── test_real_hook_audit.py
│   │           │   ├── test_audit_logging_integration.py
│   │           │   ├── test_clean_execution_silence.py
│   │           │   └── test_scope_validation_integration.py
│   │           │
│   │           └── validators/
│   │               ├── __init__.py
│   │               └── test_des_marker_validator.py
│   │
│   ├── integration/                 # Component interaction tests
│   │   ├── __init__.py
│   │   ├── test_orchestrator_execute_step.py (component interaction)
│   │   ├── test_orchestrator_e2e_wiring.py (component interaction)
│   │   ├── test_orchestrator_prompt_warnings.py (component interaction)
│   │   └── test_turn_discipline.py (NEW - turn counting + persistence)
│   │
│   ├── acceptance/                  # User story acceptance tests
│   │   ├── __init__.py
│   │   ├── conftest.py
│   │   ├── test_us001_command_filtering.py
│   │   ├── test_us002_template_validation.py
│   │   ├── test_us003_post_execution_validation.py
│   │   ├── test_us004_audit_trail.py (MOVED from tests/acceptance/)
│   │   ├── test_us004_e2e_wiring.py
│   │   ├── test_us004_pre_invocation_limits.py
│   │   ├── test_us004_turn_counting.py (MOVED from tests/acceptance/)
│   │   ├── test_us005_failure_recovery.py
│   │   ├── test_us006_turn_discipline.py
│   │   ├── test_us006a_turn_counting.py
│   │   ├── test_us006b_pre_invocation_limits.py
│   │   ├── test_us006c_e2e_wiring.py
│   │   ├── test_us007_boundary_rules.py
│   │   ├── test_us008_stale_detection.py
│   │   ├── test_validator_acceptance.py (MOVED from tests/acceptance/)
│   │   └── test_hook_enforcement_steps.py
│   │
│   └── e2e/                         # End-to-end scenario tests
│       ├── __init__.py
│       ├── test_scenario_013_timeout_warnings.py
│       ├── test_scenario_014_agent_receives_timeout_warnings_in_prompt.py
│       ├── test_scenario_013_timeout_warnings.py (MOVED from tests/ root)
│       └── test_scenario_014_agent_timeout_warnings.py (MOVED from tests/ root)
│
├── installer/                       # Installer/Setup Tests (already well-organized)
│   ├── __init__.py
│   ├── conftest.py
│   ├── unit/                        # RENAMED from flat structure
│   │   ├── adapters/
│   │   ├── checks/
│   │   ├── cli/
│   │   ├── config/
│   │   ├── domain/
│   │   └── services/
│   ├── integration/                 # NEW - installer integration tests
│   │   └── __init__.py
│   ├── acceptance/                  # MOVED from tests/acceptance/installation/
│   │   ├── __init__.py
│   │   ├── conftest.py
│   │   ├── step_defs/
│   │   │   ├── __init__.py
│   │   │   ├── steps_ci_environment.py
│   │   │   ├── steps_dependency.py
│   │   │   ├── steps_documentation.py
│   │   │   ├── steps_error_messages.py
│   │   │   ├── steps_logging.py
│   │   │   ├── steps_preflight.py
│   │   │   └── steps_verification.py
│   │   ├── test_ci_environment.py
│   │   ├── test_dependency.py
│   │   ├── test_documentation.py
│   │   ├── test_error_messages.py
│   │   ├── test_logging.py
│   │   ├── test_preflight.py
│   │   └── test_verification.py
│   └── e2e/                         # NEW - installer e2e tests
│       └── __init__.py
│
├── versioning/                      # Versioning/Release Management Tests
│   ├── __init__.py
│   ├── conftest.py
│   ├── unit/                        # CONSOLIDATED from tests/unit/versioning/
│   │   ├── __init__.py
│   │   ├── domain/
│   │   │   ├── __init__.py
│   │   │   ├── test_version.py (MOVED from tests/unit/domain/)
│   │   │   ├── test_rc_version.py (MOVED from tests/unit/domain/)
│   │   │   ├── test_version_comparator.py (MOVED from tests/unit/version_management/)
│   │   │   └── test_changelog_parser.py (MOVED from tests/unit/version_management/)
│   │   ├── cli/
│   │   │   ├── __init__.py
│   │   │   ├── test_version_cli.py
│   │   │   └── test_version.py (MOVED from tests/unit/cli/)
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── test_version_service.py
│   │   │   ├── test_version_service_offline.py (MOVED from tests/unit/version/)
│   │   │   ├── test_version_manager.py (MOVED from tests/unit/version/)
│   │   │   └── test_install_service.py
│   │   ├── adapters/
│   │   │   ├── __init__.py
│   │   │   ├── test_file_system_adapter.py
│   │   │   └── test_github_adapter.py
│   │   ├── forge/                   # Build subsystem
│   │   │   ├── __init__.py
│   │   │   ├── test_build_service.py
│   │   │   ├── test_forge_cli.py
│   │   │   └── test_git_adapter_forge.py
│   │   ├── release/                 # Release subsystem
│   │   │   ├── __init__.py
│   │   │   ├── test_forge_release_cli.py
│   │   │   ├── test_github_cli_adapter.py
│   │   │   └── test_release_service.py
│   │   └── update/                  # Update subsystem
│   │       ├── __init__.py
│   │       ├── test_backup_manager.py (MOVED from tests/unit/update/)
│   │       ├── test_update_orchestrator.py (MOVED from tests/unit/)
│   │       ├── test_checksum_adapter.py
│   │       ├── test_checksum_validation_failure.py
│   │       ├── test_download_adapter.py
│   │       ├── test_update_cli.py
│   │       └── test_update_service.py
│   │
│   ├── integration/                 # NEW - versioning integration tests
│   │   └── __init__.py
│   │
│   ├── acceptance/                  # CONSOLIDATED from multiple locations
│   │   ├── __init__.py
│   │   ├── conftest.py
│   │   ├── test_us001_version_check.py (CONSOLIDATED from multiple)
│   │   ├── test_us002_update.py
│   │   ├── test_us002_backup_rotation.py
│   │   ├── test_us003_forge_build.py
│   │   ├── test_us004_forge_install.py
│   │   ├── test_us005_forge_release.py
│   │   ├── test_git_workflow_steps.py (MOVED from version-update-experience)
│   │   ├── test_update_steps.py (MOVED from version-update-experience)
│   │   └── test_version_steps.py (MOVED from version-update-experience)
│   │
│   └── e2e/                         # NEW - versioning e2e tests
│       ├── __init__.py
│       ├── test_testpypi_validation.py (MOVED from tests/e2e/)
│       ├── test_release_packaging.py (MOVED from tests/ root)
│       └── test_release_validation.py (MOVED from tests/ root)
│
├── nwave/                           # nWave Core Tests
│   ├── __init__.py
│   ├── conftest.py
│   ├── unit/
│   │   ├── __init__.py
│   │   ├── test_step_schema_duration_seconds.py
│   │   ├── test_template_validation.py
│   │   ├── test_step_schema_turn_count.py (MOVED from tests/ root)
│   │   └── test_validate_documentation_versions.py (MOVED from tests/ root)
│   ├── integration/
│   │   └── __init__.py
│   ├── acceptance/
│   │   └── __init__.py
│   └── e2e/
│       └── __init__.py
│
├── cli/                             # CLI Tests (General)
│   ├── __init__.py
│   ├── conftest.py
│   └── unit/
│       └── __init__.py
│
├── plugins/                         # NEW - Plugin System Tests
│   ├── __init__.py
│   ├── unit/
│   │   ├── __init__.py
│   │   ├── test_des_plugin.py (MOVED from tests/install/)
│   │   ├── test_plugin_registry.py (MOVED from tests/install/)
│   │   └── test_wrapper_plugins.py (MOVED from tests/install/)
│   ├── integration/
│   │   └── __init__.py
│   └── acceptance/
│       └── __init__.py
│
├── core/                            # NEW - Core Domain/Infrastructure Tests
│   ├── __init__.py
│   ├── unit/
│   │   ├── __init__.py
│   │   ├── domain/                  # Core domain tests
│   │   │   ├── __init__.py
│   │   │   ├── test_backup_policy.py (MOVED from tests/unit/domain/)
│   │   │   ├── test_core_content_identifier.py (MOVED from tests/unit/domain/)
│   │   │   └── test_watermark.py (MOVED from tests/unit/domain/)
│   │   ├── ports/                   # Core port tests
│   │   │   ├── __init__.py
│   │   │   ├── test_checksum_port.py (MOVED from tests/unit/ports/)
│   │   │   ├── test_download_port.py
│   │   │   ├── test_file_system_port.py
│   │   │   ├── test_git_port.py
│   │   │   └── test_github_api_port.py
│   │   ├── git_workflow/            # Git workflow tests
│   │   │   ├── __init__.py
│   │   │   ├── test_commit_msg_hook.py (MOVED from tests/unit/git_workflow/)
│   │   │   ├── test_commitlint_config.py
│   │   │   └── test_prepush_validation.py
│   │   ├── backup/                  # Backup tests
│   │   │   ├── __init__.py
│   │   │   ├── test_backup_cleanup.py (MOVED from tests/unit/backup/)
│   │   │   └── test_backup_creation.py (MOVED from tests/unit/)
│   │   └── utilities/               # Utility tests
│   │       ├── __init__.py
│   │       ├── test_context_detector.py (MOVED from tests/unit/)
│   │       ├── test_error_codes.py (MOVED from tests/unit/)
│   │       ├── test_output_formatter.py (MOVED from tests/unit/)
│   │       ├── test_output_formatter_ci.py (MOVED from tests/unit/)
│   │       ├── test_output_formatter_json.py (MOVED from tests/unit/)
│   │       ├── test_rich_console.py (MOVED from tests/unit/)
│   │       └── test_suggestion_formatter.py (MOVED from tests/unit/)
│   │
│   ├── integration/
│   │   └── __init__.py
│   └── acceptance/
│       └── __init__.py
│
├── security/                        # NEW - Security/Validation Tests
│   ├── __init__.py
│   └── unit/
│       ├── __init__.py
│       ├── test_path_traversal.py (MOVED from tests/ root)
│       ├── test_config_timeout_thresholds.py (MOVED from tests/ root)
│       └── test_config_turn_limits.py (MOVED from tests/ root)
│
└── cross_cutting/                   # NEW - Cross-cutting validation tests
    ├── __init__.py
    └── validation/
        ├── __init__.py
        └── cross_phase_validation.py (MOVED from tests/validation/)
```

---

## Detailed Migration Mapping

### DES Plugin Tests

#### From `tests/des/` (Current)
- `tests/des/acceptance/*` → `tests/des/acceptance/*` (STAY - already correct)
- `tests/des/adapters/*` → `tests/des/test_doubles/*` (RENAME for clarity)
- `tests/des/e2e/*` → `tests/des/e2e/*` (STAY - already correct)
- `tests/des/integration/*` → `tests/des/integration/*` (STAY - already correct)
- `tests/des/unit/*` → `tests/des/unit/*` (STAY - already mirrors src/des/)

#### From `tests/unit/des/` (Scattered DES tests)
- `test_audit_logger_01_01.py` → `tests/des/unit/adapters/driven/logging/test_audit_logger_01_01.py`
- `test_audit_logger_unit.py` → `tests/des/unit/adapters/driven/logging/test_audit_logger_unit.py`
- `test_recovery_guidance_handler.py` → `tests/des/unit/application/test_recovery_guidance_handler.py` (DUPLICATE - merge with existing)
- `test_recovery_suggestions.py` → `tests/des/unit/application/test_recovery_suggestions.py`
- `test_schema_rollback_handler.py` → `tests/des/unit/application/test_schema_rollback_handler.py` (DUPLICATE - merge with existing)
- `test_validation_error_formatting.py` → `tests/des/unit/domain/test_validation_error_formatting.py`

#### From `tests/acceptance/` (Root-level DES tests)
- `test_us004_audit_trail.py` → `tests/des/acceptance/test_us004_audit_trail.py` (DUPLICATE - merge with existing)
- `test_us004_turn_counting.py` → `tests/des/acceptance/test_us004_turn_counting.py` (DUPLICATE - merge)
- `test_validator_acceptance.py` → `tests/des/acceptance/test_validator_acceptance.py`

#### From `tests/` (Root-level DES scenario tests)
- `test_scenario_013_timeout_warnings.py` → `tests/des/e2e/test_scenario_013_timeout_warnings.py` (DUPLICATE - merge)
- `test_scenario_014_agent_receives_timeout_warnings_in_prompt.py` → `tests/des/e2e/test_scenario_014_agent_receives_timeout_warnings_in_prompt.py` (DUPLICATE - merge)

### Installer Tests

#### From `tests/installer/` (Current - mostly correct)
- Flatten one level: `tests/installer/adapters/` → `tests/installer/unit/adapters/`
- Flatten one level: `tests/installer/checks/` → `tests/installer/unit/checks/`
- Flatten one level: `tests/installer/cli/` → `tests/installer/unit/cli/`
- Flatten one level: `tests/installer/config/` → `tests/installer/unit/config/`
- Flatten one level: `tests/installer/domain/` → `tests/installer/unit/domain/`
- Flatten one level: `tests/installer/services/` → `tests/installer/unit/services/`

#### From `tests/acceptance/installation/` (Installation acceptance tests)
- `tests/acceptance/installation/*` → `tests/installer/acceptance/*` (MOVE to collocate with installer tests)

### Versioning Tests

#### From `tests/unit/versioning/` (Versioning unit tests)
- `tests/unit/versioning/*` → `tests/versioning/unit/*` (MOVE to consolidated location)

#### From `tests/unit/version/` (Version-specific tests)
- `test_version_service_offline.py` → `tests/versioning/unit/services/test_version_service_offline.py`
- `test_version_manager.py` → `tests/versioning/unit/services/test_version_manager.py`

#### From `tests/unit/version_management/` (Version management utilities)
- `test_version_comparator.py` → `tests/versioning/unit/domain/test_version_comparator.py`
- `test_changelog_parser.py` → `tests/versioning/unit/domain/test_changelog_parser.py`

#### From `tests/unit/domain/` (Version domain models)
- `test_version.py` → `tests/versioning/unit/domain/test_version.py`
- `test_rc_version.py` → `tests/versioning/unit/domain/test_rc_version.py`

#### From `tests/unit/update/` (Update subsystem)
- `test_backup_manager.py` → `tests/versioning/unit/update/test_backup_manager.py`

#### From `tests/unit/` (Root-level update test)
- `test_update_orchestrator.py` → `tests/versioning/unit/update/test_update_orchestrator.py`

#### From `tests/unit/cli/` (CLI version test)
- `test_version.py` → `tests/versioning/unit/cli/test_version.py`

#### From `tests/acceptance/versioning/` (Versioning acceptance tests)
- `tests/acceptance/versioning/*` → `tests/versioning/acceptance/*`

#### From `tests/acceptance/versioning_release_management/` (Duplicate location)
- `tests/acceptance/versioning_release_management/*` → `tests/versioning/acceptance/*` (MERGE with above)

#### From `tests/acceptance/features/versioning-release-management/` (Another duplicate)
- `tests/acceptance/features/versioning-release-management/*` → `tests/versioning/acceptance/*` (MERGE)

#### From `tests/acceptance/features/version-update-experience/` (Update experience tests)
- `test_git_workflow_steps.py` → `tests/versioning/acceptance/test_git_workflow_steps.py`
- `test_update_steps.py` → `tests/versioning/acceptance/test_update_steps.py`
- `test_version_steps.py` → `tests/versioning/acceptance/test_version_steps.py`

#### From `tests/e2e/` (E2E versioning test)
- `test_testpypi_validation.py` → `tests/versioning/e2e/test_testpypi_validation.py`

#### From `tests/` (Root-level release tests)
- `test_release_packaging.py` → `tests/versioning/e2e/test_release_packaging.py`
- `test_release_validation.py` → `tests/versioning/e2e/test_release_validation.py`

### nWave Core Tests

#### From `tests/nwave/` (Current)
- `test_step_schema_duration_seconds.py` → `tests/nwave/unit/test_step_schema_duration_seconds.py`
- `test_template_validation.py` → `tests/nwave/unit/test_template_validation.py`

#### From `tests/` (Root-level nWave tests)
- `test_step_schema_turn_count.py` → `tests/nwave/unit/test_step_schema_turn_count.py`
- `test_validate_documentation_versions.py` → `tests/nwave/unit/test_validate_documentation_versions.py`

### Plugin System Tests

#### From `tests/install/` (Plugin installation tests)
- `test_des_plugin.py` → `tests/plugins/unit/test_des_plugin.py`
- `test_plugin_registry.py` → `tests/plugins/unit/test_plugin_registry.py`
- `test_wrapper_plugins.py` → `tests/plugins/unit/test_wrapper_plugins.py`

### Core Domain/Infrastructure Tests

#### From `tests/unit/domain/` (Core domain tests)
- `test_backup_policy.py` → `tests/core/unit/domain/test_backup_policy.py`
- `test_core_content_identifier.py` → `tests/core/unit/domain/test_core_content_identifier.py`
- `test_watermark.py` → `tests/core/unit/domain/test_watermark.py`

#### From `tests/unit/ports/` (Core port tests)
- `test_checksum_port.py` → `tests/core/unit/ports/test_checksum_port.py`
- `test_download_port.py` → `tests/core/unit/ports/test_download_port.py`
- `test_file_system_port.py` → `tests/core/unit/ports/test_file_system_port.py`
- `test_git_port.py` → `tests/core/unit/ports/test_git_port.py`
- `test_github_api_port.py` → `tests/core/unit/ports/test_github_api_port.py`

#### From `tests/unit/git_workflow/` (Git workflow tests)
- `tests/unit/git_workflow/*` → `tests/core/unit/git_workflow/*`

#### From `tests/unit/backup/` (Backup tests)
- `test_backup_cleanup.py` → `tests/core/unit/backup/test_backup_cleanup.py`

#### From `tests/unit/` (Root-level backup test)
- `test_backup_creation.py` → `tests/core/unit/backup/test_backup_creation.py`

#### From `tests/unit/` (Root-level utility tests)
- `test_context_detector.py` → `tests/core/unit/utilities/test_context_detector.py`
- `test_error_codes.py` → `tests/core/unit/utilities/test_error_codes.py`
- `test_output_formatter.py` → `tests/core/unit/utilities/test_output_formatter.py`
- `test_output_formatter_ci.py` → `tests/core/unit/utilities/test_output_formatter_ci.py`
- `test_output_formatter_json.py` → `tests/core/unit/utilities/test_output_formatter_json.py`
- `test_rich_console.py` → `tests/core/unit/utilities/test_rich_console.py`
- `test_suggestion_formatter.py` → `tests/core/unit/utilities/test_suggestion_formatter.py`

### Security/Validation Tests

#### From `tests/` (Root-level security tests)
- `test_path_traversal.py` → `tests/security/unit/test_path_traversal.py`
- `test_config_timeout_thresholds.py` → `tests/security/unit/test_config_timeout_thresholds.py`
- `test_config_turn_limits.py` → `tests/security/unit/test_config_turn_limits.py`

### Cross-cutting Tests

#### From `tests/validation/` (Cross-phase validation)
- `cross_phase_validation.py` → `tests/cross_cutting/validation/cross_phase_validation.py`

### Remaining Root-Level Tests (Need Investigation)

These tests are at the root `tests/` level and need to be categorized:
- `test_import_debug.py` (at project root) - Delete or move to appropriate location
- `test_token_minimal_architecture.py` (at project root) - Delete or move to appropriate location
- `update_commit_phase.py` (at project root) - Not a test, should be in scripts/
- `update_phase.py` (at project root) - Not a test, should be in scripts/
- `update_phase_with_tests.py` (at project root) - Not a test, should be in scripts/
- `update_step_05_02.py` (at project root) - Not a test, should be in scripts/
- `update_step_phase.py` (at project root) - Not a test, should be in scripts/

---

## Shared Test Infrastructure

### New `tests/shared/` Directory

Create a centralized location for shared test utilities:

#### Test Data Builders (`tests/shared/builders/`)
```python
# tests/shared/builders/des_builders.py
class DESTestBuilder:
    """Builder for DES test data."""

    @staticmethod
    def build_step_file_data(**overrides):
        """Build step file JSON data with defaults."""
        defaults = {
            "step_id": "01-01",
            "feature_id": "test-feature",
            "turn_count": 0,
            "phase": "PREPARE",
            # ... other defaults
        }
        return {**defaults, **overrides}

    @staticmethod
    def build_hook_input(**overrides):
        """Build SubagentStop hook input data."""
        # ... implementation

# tests/shared/builders/installer_builders.py
class InstallerTestBuilder:
    """Builder for installer test data."""
    # ... implementation

# tests/shared/builders/versioning_builders.py
class VersioningTestBuilder:
    """Builder for versioning test data."""
    # ... implementation
```

#### Shared Fixtures (`tests/shared/fixtures/`)
```python
# tests/shared/fixtures/filesystem_fixtures.py
@pytest.fixture
def temp_project_dir(tmp_path):
    """Create a temporary project directory structure."""
    # ... implementation
    return tmp_path

@pytest.fixture
def mock_step_file(tmp_path):
    """Create a mock step file in temporary directory."""
    # ... implementation

# tests/shared/fixtures/git_fixtures.py
@pytest.fixture
def git_repo(tmp_path):
    """Create a temporary git repository."""
    # ... implementation

# tests/shared/fixtures/time_fixtures.py
@pytest.fixture
def frozen_time():
    """Freeze time for testing."""
    # ... implementation
```

#### Custom Matchers (`tests/shared/matchers/`)
```python
# tests/shared/matchers/custom_matchers.py
class CustomMatchers:
    """Custom pytest matchers for domain-specific assertions."""

    @staticmethod
    def assert_valid_step_file(step_file_data):
        """Assert step file data is valid."""
        # ... implementation

    @staticmethod
    def assert_hexagonal_compliance(module):
        """Assert module follows hexagonal architecture."""
        # ... implementation
```

---

## Implementation Strategy

### Phase 1: Create New Structure (Non-Breaking)
**Duration**: 1-2 hours
**Impact**: No breaking changes

1. Create all new directories with `__init__.py` files
2. Create `tests/shared/` infrastructure (builders, fixtures, matchers)
3. Create placeholder `conftest.py` files in each feature directory
4. **DO NOT** move or delete any existing files yet

### Phase 2: Consolidate Test Doubles (DES)
**Duration**: 2-3 hours
**Impact**: DES test imports only

1. Rename `tests/des/adapters/` → `tests/des/test_doubles/`
2. Update all imports in `tests/des/` to use new path
3. Run DES tests to verify no breakage: `pytest tests/des/`

### Phase 3: Migrate DES Tests
**Duration**: 3-4 hours
**Impact**: DES tests only

1. Move scattered DES tests from `tests/unit/des/` → `tests/des/unit/`
2. Move scattered DES acceptance tests from `tests/acceptance/` → `tests/des/acceptance/`
3. Merge duplicate tests (resolve conflicts manually)
4. Update imports in moved files
5. Run DES test suite: `pytest tests/des/`
6. Fix any broken imports or test failures

### Phase 4: Migrate Installer Tests
**Duration**: 2-3 hours
**Impact**: Installer tests only

1. Restructure `tests/installer/` to add `unit/` layer
2. Move acceptance tests from `tests/acceptance/installation/` → `tests/installer/acceptance/`
3. Update imports
4. Run installer test suite: `pytest tests/installer/`

### Phase 5: Migrate Versioning Tests
**Duration**: 4-5 hours
**Impact**: Versioning tests (most scattered)

1. Create `tests/versioning/` structure
2. Consolidate tests from:
   - `tests/unit/versioning/`
   - `tests/unit/version/`
   - `tests/unit/version_management/`
   - `tests/acceptance/versioning/`
   - `tests/acceptance/versioning_release_management/`
   - `tests/acceptance/features/versioning-release-management/`
   - `tests/acceptance/features/version-update-experience/`
3. Merge duplicate tests
4. Update imports
5. Run versioning test suite: `pytest tests/versioning/`

### Phase 6: Migrate Remaining Features
**Duration**: 3-4 hours
**Impact**: nWave, plugins, core, security tests

1. Migrate nWave tests → `tests/nwave/`
2. Migrate plugin tests → `tests/plugins/`
3. Migrate core domain/infrastructure tests → `tests/core/`
4. Migrate security tests → `tests/security/`
5. Migrate cross-cutting tests → `tests/cross_cutting/`
6. Update imports
7. Run full test suite: `pytest tests/`

### Phase 7: Clean Up Old Structure
**Duration**: 1-2 hours
**Impact**: Remove empty/obsolete directories

1. Delete empty directories:
   - `tests/acceptance/features/`
   - `tests/acceptance/versioning/`
   - `tests/acceptance/versioning_release_management/`
   - `tests/unit/versioning/`
   - `tests/unit/version/`
   - `tests/unit/version_management/`
   - `tests/unit/des/`
   - `tests/unit/update/`
   - `tests/unit/backup/`
   - `tests/unit/git_workflow/`
2. Remove non-test files from `tests/` root (move to `scripts/`)
3. Update documentation (README, architecture docs)
4. Run full test suite one final time: `pytest tests/`

### Phase 8: Documentation and CI/CD Updates
**Duration**: 2-3 hours
**Impact**: Documentation, CI configuration

1. Update `/README.md` with new test structure
2. Update `/docs/architecture/` documentation
3. Update CI/CD configuration (GitHub Actions, pytest configurations)
4. Create developer guide: "Where do I put my tests?"
5. Update contribution guidelines

---

## Benefits of Reorganization

### 1. Clear Test Discoverability
**Before**: Developer asks "Where are the installer tests?" - scattered in 3 locations
**After**: All installer tests in `tests/installer/` with clear separation by test type

### 2. Hexagonal Architecture Visibility
**Before**: Test structure doesn't reflect hexagonal architecture principles
**After**: Tests mirror hexagonal layers (domain, application, ports, adapters)

### 3. Reduced Duplication
**Before**: DES tests in 3 locations, versioning tests in 8 locations
**After**: Each feature has ONE canonical location for all its tests

### 4. Better Test Organization
**Before**: Flat `tests/unit/` with 20+ subdirectories of mixed concerns
**After**: Tests grouped by feature/plugin, then by test type (unit/integration/acceptance/e2e)

### 5. Improved Developer Experience
**Before**:
- "Where do I put tests for a new DES domain class?" - unclear
- "Where are all the versioning acceptance tests?" - scattered
- "Which test doubles can I reuse?" - hard to find

**After**:
- "Where do I put tests for a new DES domain class?" - `tests/des/unit/domain/`
- "Where are all the versioning acceptance tests?" - `tests/versioning/acceptance/`
- "Which test doubles can I reuse?" - `tests/des/test_doubles/` for DES, `tests/shared/` for cross-cutting

### 6. Test Type Clarity
**Before**: Blurred boundaries - "acceptance" contains both feature tests and user story tests
**After**: Clear hierarchy:
- **unit/**: Isolated component tests
- **integration/**: Component interaction tests
- **acceptance/**: User story acceptance criteria tests
- **e2e/**: Full system scenario tests

### 7. Easier Maintenance
**Before**: Renaming a feature requires updating tests in 5+ locations
**After**: All tests for a feature in one location - rename once

### 8. Better CI/CD Segmentation
**Before**: Hard to run "just installer tests" or "just DES tests"
**After**:
```bash
pytest tests/des/          # Run all DES tests
pytest tests/installer/    # Run all installer tests
pytest tests/versioning/   # Run all versioning tests
pytest tests/des/unit/     # Run only DES unit tests
pytest tests/*/acceptance/ # Run all acceptance tests
```

---

## Risk Mitigation

### Risk 1: Breaking Import Changes
**Mitigation**:
- Migrate one feature at a time
- Run tests after each migration phase
- Use automated refactoring tools where possible
- Create backward compatibility imports in `__init__.py` files temporarily

### Risk 2: Merge Conflicts with Duplicate Tests
**Mitigation**:
- Identify duplicates before migration (see mapping above)
- Manually review and merge duplicate tests
- Ensure all test cases are preserved
- Run coverage reports before and after to verify completeness

### Risk 3: CI/CD Pipeline Breakage
**Mitigation**:
- Update CI configuration BEFORE deleting old directories
- Test CI pipeline on feature branch before merging
- Keep old structure temporarily until CI validated

### Risk 4: Developer Confusion During Transition
**Mitigation**:
- Create clear migration documentation
- Communicate changes to team before implementation
- Provide "where things moved" reference guide
- Update IDE/editor project configurations

### Risk 5: Lost Test Coverage
**Mitigation**:
- Run coverage reports before migration: `pytest --cov=src tests/`
- Run coverage reports after migration: `pytest --cov=src tests/`
- Compare coverage delta - should be identical or improved
- Manually verify all test files accounted for in migration mapping

---

## Success Criteria

### Must-Have (Mandatory)
1. ✅ All existing tests pass after reorganization
2. ✅ Test coverage maintained or improved (no regression)
3. ✅ No duplicate test files remaining
4. ✅ All tests grouped by feature/plugin
5. ✅ DES tests fully mirror `src/des/` hexagonal structure
6. ✅ CI/CD pipeline runs successfully with new structure
7. ✅ Documentation updated with new test organization

### Should-Have (Highly Desirable)
1. ✅ Shared test infrastructure centralized in `tests/shared/`
2. ✅ Clear separation: unit/integration/acceptance/e2e for each feature
3. ✅ Test doubles consolidated and reusable
4. ✅ Empty directories removed
5. ✅ Developer guide created: "Where do I put my tests?"

### Nice-to-Have (Future Enhancements)
1. Automated test for hexagonal architecture compliance
2. Pre-commit hook validating test placement
3. Test coverage badges per feature
4. Test execution time optimization based on new structure

---

## Timeline Estimate

| Phase | Duration | Dependencies |
|-------|----------|--------------|
| Phase 1: Create Structure | 1-2 hours | None |
| Phase 2: DES Test Doubles | 2-3 hours | Phase 1 |
| Phase 3: Migrate DES Tests | 3-4 hours | Phase 2 |
| Phase 4: Migrate Installer Tests | 2-3 hours | Phase 1 |
| Phase 5: Migrate Versioning Tests | 4-5 hours | Phase 1 |
| Phase 6: Migrate Remaining Features | 3-4 hours | Phase 1 |
| Phase 7: Clean Up | 1-2 hours | Phases 3-6 complete |
| Phase 8: Documentation & CI | 2-3 hours | Phase 7 |
| **TOTAL** | **18-26 hours** | Sequential execution |

**Recommended Approach**: Execute phases 3-6 in parallel if multiple team members available (reduces total time to ~12-16 hours).

---

## Next Steps

1. **Review this plan** - Gather team feedback and approval
2. **Create feature branch** - `feat/reorganize-tests-hexagonal-structure`
3. **Execute Phase 1** - Create new directory structure (non-breaking)
4. **Validate Phase 1** - Ensure tests still run with new directories present
5. **Execute remaining phases** - Follow migration plan sequentially
6. **Create PR** - Submit for review with before/after test coverage reports
7. **Update documentation** - Architecture guides, README, contribution docs

---

## Questions for Review

1. **Approval**: Is the proposed structure acceptable?
2. **Timeline**: Is the 18-26 hour estimate reasonable?
3. **Risks**: Are there additional risks we should consider?
4. **Scope**: Should we include anything else in this reorganization?
5. **Priorities**: Should any phases be prioritized or deferred?

---

## Appendix A: Directory Structure Comparison

### Current Structure (Simplified)
```
tests/
├── acceptance/         # MIXED - versioning, installation, des
├── des/                # PARTIALLY ORGANIZED
├── installer/          # GOOD (but needs unit/ layer)
├── unit/               # MIXED - everything
├── e2e/                # SCATTERED
└── integration/        # EMPTY
```

### Proposed Structure (Simplified)
```
tests/
├── shared/             # NEW - shared test infrastructure
├── des/                # COMPLETE HEXAGONAL MIRROR
│   ├── test_doubles/   # Shared test doubles
│   ├── unit/           # Mirrors src/des/
│   ├── integration/    # Component interactions
│   ├── acceptance/     # User stories
│   └── e2e/            # Full scenarios
├── installer/          # ORGANIZED BY TEST TYPE
├── versioning/         # CONSOLIDATED
├── nwave/              # ORGANIZED BY TEST TYPE
├── plugins/            # NEW - plugin system tests
├── core/               # NEW - core domain/infrastructure
├── security/           # NEW - security tests
└── cross_cutting/      # NEW - cross-cutting validation
```

---

**End of Reorganization Plan**
