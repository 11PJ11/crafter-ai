# Plugin System Implementation Prerequisites

**Feature**: Plugin Architecture for nWave Installer
**Solution Architect**: Morgan
**Date**: 2026-02-03

---

## Overview

This document provides phase-specific prerequisites that MUST be completed before starting each implementation phase. Prerequisites are derived from gap analysis (architecture-decisions.md) and ensure smooth phase transitions.

---

## Phase 1: Infrastructure Foundation

### Status: ✅ COMPLETE

**Prerequisites**: None (baseline phase)

**Deliverables Achieved**:
- ✅ base.py (InstallationPlugin interface)
- ✅ registry.py (PluginRegistry with Kahn's algorithm)
- ✅ test_plugin_registry.py (10/10 tests passing)
- ✅ Commit: d86acfa

**Exit Criteria Met**:
- ✅ 10/10 plugin infrastructure tests passing
- ✅ Topological sort validated
- ✅ Circular dependency detection validated
- ✅ Priority ordering validated

---

## Phase 2: Wrapper Plugins

### Status: ⚠️ NOT STARTED - Prerequisites Required

### Mandatory Prerequisites

#### PREREQ-2.1: Circular Import Mitigation Proof-of-Concept ⚠️ HIGH PRIORITY
**Status**: NOT STARTED
**Estimated Effort**: 2-3 hours
**Blocking**: Cannot start Phase 2 without this

**What to Do**:
1. Extract `install_agents_impl()` from `nWaveInstaller._install_agents()` in `install_nwave.py`
2. Create `AgentsPlugin` in `scripts/install/plugins/agents_plugin.py`
3. Import extracted function: `from scripts.install.install_nwave import install_agents_impl`
4. Run import test: `python3 -c "from scripts.install.plugins.agents_plugin import AgentsPlugin; print('SUCCESS')"`
5. Verify NO circular import error

**Success Criteria**:
- ✅ Import test passes without circular import error
- ✅ AgentsPlugin calls `install_agents_impl()` successfully
- ✅ Existing `nWaveInstaller._install_agents()` calls `install_agents_impl()` (thin wrapper)

**Reference**: architecture-decisions.md GAP-ARCH-01

---

#### PREREQ-2.2: InstallContext Validation ⚠️ MEDIUM PRIORITY
**Status**: NOT STARTED (continuous during Phase 2)
**Estimated Effort**: 1-2 hours (during Phase 2 work)

**What to Do**:
1. Review ALL existing utilities used by `_install_agents()`, `_install_commands()`, `_install_templates()`, `_install_utilities()`
2. Document each utility: name, interface, current usage
3. Verify all required utilities are in InstallContext
4. Add missing utilities to InstallContext BEFORE Phase 3

**Current InstallContext Fields** (validate completeness):
```python
@dataclass
class InstallContext:
    claude_dir: Path
    scripts_dir: Path
    templates_dir: Path
    logger: logging.Logger
    dry_run: bool
    backup_manager: Optional['BackupManager']
    installation_verifier: Optional['InstallationVerifier']
    dist_dir: Optional[Path]
    source_dir: Optional[Path]
    framework_source: Optional[Path]
    project_root: Optional[Path]
    rich_logger: Optional[Any]
    current_version: Optional[str]
    target_version: Optional[str]
    plugin_data: Dict[str, Any]
```

**Potential Missing Fields** (validate):
- `build_manager: Optional['BuildManager']` - If build pipeline coordination needed
- `manifest_writer: Optional['ManifestWriter']` - If manifest generation used
- `preflight_checker: Optional['PreflightChecker']` - If prerequisite validation used

**Success Criteria**:
- ✅ All utilities used by installation methods documented
- ✅ InstallContext contains ALL required utilities
- ✅ No missing utilities discovered during wrapper plugin implementation

**Reference**: architecture-decisions.md GAP-ARCH-02

---

### Recommended Prerequisites

#### PREREQ-2.3: Verification Fallback Logic Definition ℹ️ MEDIUM PRIORITY
**Status**: NOT STARTED
**Estimated Effort**: 2 hours
**Blocking**: Not blocking, but needed for robustness

**What to Do**:
Define fallback verification logic for each plugin if `installation_verifier` unavailable:

**AgentsPlugin Fallback**:
- Check `~/.claude/agents/nw/` exists
- Count agent `.md` files
- Expected: ≥10 agents
- Return success if count meets threshold

**CommandsPlugin Fallback**:
- Check `~/.claude/commands/nw/` exists
- Count command `.yaml` files
- Expected: ≥20 commands
- Return success if count meets threshold

**TemplatesPlugin Fallback**:
- Check `~/.claude/templates/` exists
- Count template files
- Expected: ≥8 templates
- Return success if count meets threshold

**UtilitiesPlugin Fallback**:
- Check `~/.claude/lib/python/` exists
- Verify utility modules present
- Expected: PathUtils, Logger, etc.
- Return success if modules found

**Success Criteria**:
- ✅ Fallback logic documented for all 4 plugins
- ✅ Expected file counts based on current installer behavior
- ✅ Fallback verification pattern implemented consistently

**Reference**: architecture-decisions.md GAP-ARCH-03

---

### Phase 2 Entry Checklist

Before starting Phase 2 implementation:

- [ ] PREREQ-2.1: Circular import proof-of-concept COMPLETE
- [ ] PREREQ-2.2: InstallContext validation plan defined
- [ ] PREREQ-2.3: Verification fallback logic designed (recommended)
- [ ] Phase 1 exit criteria met (10/10 tests passing)
- [ ] Architecture decisions reviewed and approved

**Phase 2 Ready?**: NO - Complete PREREQ-2.1 first

---

## Phase 3: Switchover to PluginRegistry

### Status: ⚠️ NOT STARTED - Prerequisites Required

### Mandatory Prerequisites

#### PREREQ-3.1: Phase 2 Complete ⚠️ CRITICAL
**Status**: NOT STARTED
**Blocking**: Phase 3 cannot start without Phase 2 completion

**Phase 2 Exit Criteria**:
- ✅ 4 wrapper plugins created (AgentsPlugin, CommandsPlugin, TemplatesPlugin, UtilitiesPlugin)
- ✅ All plugins call existing `*_impl()` functions successfully
- ✅ Unit tests pass for each plugin
- ✅ Circular import prevention validated
- ✅ InstallContext complete (no missing utilities discovered)

---

#### PREREQ-3.2: Integration Checkpoint Test Suite ⚠️ HIGH PRIORITY
**Status**: NOT STARTED
**Estimated Effort**: 4-6 hours
**Blocking**: Should be ready before switchover

**What to Do**:
1. Create `tests/install/test_integration_checkpoint.py`
2. Implement baseline vs plugin installation comparison test
3. Implement file tree comparison helper
4. Implement verification results comparison helper
5. Run test to establish baseline before switchover

**Test Specification**:
```python
def test_switchover_preserves_installation_behavior(tmp_path):
    """
    Validate plugin-based installation produces identical results
    to pre-plugin baseline.
    """
    # Compare file trees
    assert baseline_files == plugin_files

    # Compare verification results
    assert baseline_verification == plugin_verification

    # Compare file contents
    for file_path in baseline_files:
        assert baseline_content == plugin_content
```

**Success Criteria**:
- ✅ Integration test created and passing
- ✅ Baseline installation captured before switchover
- ✅ Test can detect file tree differences
- ✅ Test can detect verification result differences

**Reference**: architecture-decisions.md GAP-PROCESS-01

---

#### PREREQ-3.3: Rollback Procedure Documented ℹ️ MEDIUM PRIORITY
**Status**: NOT STARTED
**Estimated Effort**: 1 hour
**Blocking**: Not blocking, but recommended for safety

**What to Do**:
1. Add rollback section to `docs/installation/installation-guide.md`
2. Document backup restoration procedure using BackupManager
3. Document git commit reversion procedure
4. Document verification after rollback
5. Document failure analysis steps

**Rollback Procedure Outline**:
```
1. Detect Failure (integration tests fail)
2. Stop Deployment (do not proceed to Phase 4)
3. Restore from Backup (use BackupManager backups)
4. Roll Back Git Commit (revert switchover changes)
5. Verify Rollback Success (run verification)
6. Analyze Failure (identify root cause)
```

**Success Criteria**:
- ✅ Rollback procedure documented in installation-guide.md
- ✅ Procedure references BackupManager backup locations
- ✅ Git rollback steps clear and testable

**Reference**: architecture-decisions.md GAP-PROCESS-02

---

### Phase 3 Entry Checklist

Before starting Phase 3 implementation:

- [ ] PREREQ-3.1: Phase 2 complete (4 wrapper plugins working)
- [ ] PREREQ-3.2: Integration checkpoint test suite ready
- [ ] PREREQ-3.3: Rollback procedure documented (recommended)
- [ ] InstallContext complete (all utilities available)
- [ ] Backup created before switchover

**Phase 3 Ready?**: NO - Complete Phase 2 first

---

## Phase 4: DES Plugin Implementation

### Status: ⚠️ NOT STARTED - Prerequisites Required

### Mandatory Prerequisites

#### PREREQ-4.1: DES Scripts Created ⚠️ CRITICAL - HIGH PRIORITY
**Status**: NOT STARTED
**Estimated Effort**: 4-6 hours
**Blocking**: Phase 4 CANNOT START without these scripts

**Missing Scripts**:
1. `nWave/scripts/des/check_stale_phases.py` - Pre-commit hook for stale phase detection
2. `nWave/scripts/des/scope_boundary_check.py` - Pre-commit hook for scope validation

**Implementation Steps**:
1. Create directory: `mkdir -p nWave/scripts/des/`
2. Create `check_stale_phases.py` (see architecture-decisions.md for code)
3. Create `scope_boundary_check.py` (see architecture-decisions.md for code)
4. Set executable permissions: `chmod +x nWave/scripts/des/*.py`
5. Validate syntax: `python3 -m py_compile nWave/scripts/des/*.py`

**Success Criteria**:
- ✅ Both scripts exist in `nWave/scripts/des/`
- ✅ Scripts have executable permissions
- ✅ Scripts have valid Python syntax
- ✅ Scripts can import DES module after installation

**Reference**: architecture-decisions.md GAP-PREREQ-01

---

#### PREREQ-4.2: DES Templates Created ⚠️ CRITICAL - HIGH PRIORITY
**Status**: NOT STARTED
**Estimated Effort**: 1-2 hours
**Blocking**: Phase 4 incomplete without templates

**Missing Templates**:
1. `nWave/templates/.pre-commit-config-nwave.yaml` - Pre-commit configuration
2. `nWave/templates/.des-audit-README.md` - DES audit trail documentation

**Implementation Steps**:
1. Create `.pre-commit-config-nwave.yaml` in `nWave/templates/` (see architecture-decisions.md)
2. Create `.des-audit-README.md` in `nWave/templates/` (see architecture-decisions.md)
3. Validate YAML syntax: `yamllint nWave/templates/.pre-commit-config-nwave.yaml`
4. Review Markdown: Visual inspection of `.des-audit-README.md`

**Success Criteria**:
- ✅ Both templates exist in `nWave/templates/`
- ✅ `.pre-commit-config-nwave.yaml` has valid YAML syntax
- ✅ `.pre-commit-config-nwave.yaml` references DES scripts correctly
- ✅ `.des-audit-README.md` has clear documentation

**Reference**: architecture-decisions.md GAP-PREREQ-02

---

#### PREREQ-4.3: Phase 3 Complete ⚠️ CRITICAL
**Status**: NOT STARTED
**Blocking**: Phase 4 requires working plugin orchestration

**Phase 3 Exit Criteria**:
- ✅ `install_framework()` switched to `PluginRegistry.install_all()`
- ✅ Integration checkpoint tests passing
- ✅ File tree comparison shows identical installations
- ✅ Verification results identical (baseline vs plugin)
- ✅ No regressions detected

---

### Recommended Prerequisites

#### PREREQ-4.4: Build Pipeline DES Integration Validated ℹ️ LOW PRIORITY
**Status**: NOT STARTED
**Estimated Effort**: 30 minutes
**Blocking**: Not blocking (DESPlugin has fallback)

**What to Do**:
1. Run build pipeline: `python tools/build.py` or `bash scripts/build-ide-bundle.sh`
2. Check if DES module copied: `ls dist/ide/lib/python/des/`
3. Expected files: `domain/`, `application/`, `ports/`, `adapters/`, `__init__.py`
4. If missing, update build script to copy DES module

**Success Criteria**:
- ✅ DES module exists in `dist/ide/lib/python/des/` after build
- ✅ All DES submodules present

**Reference**: architecture-decisions.md GAP-PREREQ-03

---

### Phase 4 Entry Checklist

Before starting Phase 4 implementation:

- [ ] PREREQ-4.1: DES scripts created and validated ⚠️ CRITICAL
- [ ] PREREQ-4.2: DES templates created and validated ⚠️ CRITICAL
- [ ] PREREQ-4.3: Phase 3 complete (plugin orchestration working) ⚠️ CRITICAL
- [ ] PREREQ-4.4: Build pipeline validated (recommended)
- [ ] DES module exists in `src/des/` (already validated 2026-02-01)

**Phase 4 Ready?**: NO - Complete PREREQ-4.1, PREREQ-4.2, and Phase 3 first

---

## Phase 5: Testing & Documentation

### Status: ⚠️ NOT STARTED - Prerequisites Required

### Mandatory Prerequisites

#### PREREQ-5.1: Phase 4 Complete ⚠️ CRITICAL
**Status**: NOT STARTED
**Blocking**: Cannot test incomplete implementation

**Phase 4 Exit Criteria**:
- ✅ DESPlugin implemented with dependencies ["templates", "utilities"]
- ✅ DES module importable after installation
- ✅ DES scripts executable (chmod +x)
- ✅ DES templates installed correctly
- ✅ Dependencies respected (DES after utilities)

---

#### PREREQ-5.2: Test Coverage Target Defined ℹ️ MEDIUM PRIORITY
**Status**: NOT STARTED
**Estimated Effort**: 30 minutes
**Blocking**: Not blocking, but establishes quality gate

**What to Define**:
- Target test coverage: ≥80% (recommended)
- Coverage measurement tool: pytest-cov
- Coverage exclusions: (if any)
- Coverage reporting: HTML + terminal

**Success Criteria**:
- ✅ Coverage target agreed upon
- ✅ pytest-cov configured in test suite
- ✅ Coverage reports generated successfully

---

### Phase 5 Entry Checklist

Before starting Phase 5 implementation:

- [ ] PREREQ-5.1: Phase 4 complete (DES installable)
- [ ] PREREQ-5.2: Test coverage target defined
- [ ] All plugins (agents, commands, templates, utilities, DES) working
- [ ] Integration checkpoint tests passing

**Phase 5 Ready?**: NO - Complete Phase 4 first

---

## Phase 6: Deployment & Rollout

### Status: ⚠️ NOT STARTED - Prerequisites Required

### Mandatory Prerequisites

#### PREREQ-6.1: Phase 5 Complete ⚠️ CRITICAL
**Status**: NOT STARTED
**Blocking**: Cannot deploy untested implementation

**Phase 5 Exit Criteria**:
- ✅ Test suite passes (unit + integration + regression + adversarial)
- ✅ Test coverage ≥ 80%
- ✅ Documentation complete (installation-guide.md, des-audit-trail-guide.md, plugin-development-guide.md)
- ✅ Documentation reviewed and approved

---

#### PREREQ-6.2: Version Bump Strategy Decided ⚠️ HIGH PRIORITY
**Status**: RESOLVED (see architecture-decisions.md GAP-ARCH-00)
**Estimated Effort**: 30 minutes (documentation only)

**Version Strategy** (DECIDED):
```
Phase 1 complete: 1.2.0 → 1.2.1 (patch - infrastructure)
Phase 3 complete: 1.2.1 → 1.3.0 (minor - plugin orchestration)
Phase 4 complete: 1.3.0 → 1.4.0 (minor - DES feature)
Phase 6 complete: 1.4.0 → 1.7.0 (marketing version - production release)
```

**What to Do**:
1. Update `pyproject.toml` to 1.7.0
2. Update CHANGELOG.md with full version history
3. Create release notes with migration guide
4. Tag git commit: `git tag v1.7.0`

**Success Criteria**:
- ✅ Version updated in pyproject.toml
- ✅ CHANGELOG.md comprehensive
- ✅ Release notes published
- ✅ Git tag created

**Reference**: architecture-decisions.md GAP-ARCH-00

---

#### PREREQ-6.3: Backward Compatibility Validated ⚠️ HIGH PRIORITY
**Status**: NOT STARTED
**Estimated Effort**: 2 hours
**Blocking**: Critical for production deployment

**What to Validate**:
1. Existing installations upgrade cleanly (1.2.0 → 1.7.0)
2. DES added without breaking existing setup
3. All integration tests pass on upgrade scenario
4. User data preserved (agents, commands, templates)
5. Backup created before upgrade

**Test Scenarios**:
- Fresh installation (no previous version)
- Upgrade from 1.2.0 (monolithic)
- Upgrade from 1.3.0 (plugin orchestration)
- Upgrade from 1.4.0 (DES available)

**Success Criteria**:
- ✅ All upgrade scenarios pass
- ✅ No data loss during upgrade
- ✅ Backward compatibility verified

---

### Phase 6 Entry Checklist

Before starting Phase 6 deployment:

- [ ] PREREQ-6.1: Phase 5 complete (tests passing, docs complete)
- [ ] PREREQ-6.2: Version bump strategy documented
- [ ] PREREQ-6.3: Backward compatibility validated
- [ ] Release notes prepared
- [ ] Gradual rollout plan defined (alpha → beta → stable)

**Phase 6 Ready?**: NO - Complete Phase 5 first

---

## Summary: Critical Path Prerequisites

### Before ANY Phase Work Begins

**Documentation**:
- [x] architecture-decisions.md (gap analysis decisions) - COMPLETE
- [x] prerequisites.md (this document) - COMPLETE
- [ ] design.md updates (incorporate gap resolutions) - NEXT
- [ ] nwave-plugin-system-architecture.md updates (architectural refinements) - NEXT

**HIGH Priority (MUST DO before Phase 2)**:
- [ ] PREREQ-2.1: Circular import proof-of-concept (2-3 hours)
- [ ] PREREQ-4.1: DES scripts creation (4-6 hours) - Can be done in parallel with Phase 2
- [ ] PREREQ-4.2: DES templates creation (1-2 hours) - Can be done in parallel with Phase 2

**MEDIUM Priority (Important but not immediately blocking)**:
- [ ] PREREQ-2.2: InstallContext validation (continuous during Phase 2)
- [ ] PREREQ-2.3: Verification fallback logic (during Phase 2)
- [ ] PREREQ-3.2: Integration checkpoint test suite (before Phase 3 switchover)

**LOW Priority (Nice to have)**:
- [ ] PREREQ-3.3: Rollback procedure documentation (before Phase 3)
- [ ] PREREQ-4.4: Build pipeline validation (during Phase 4)
- [ ] PREREQ-5.2: Test coverage target definition (before Phase 5)

### Estimated Total Prerequisite Effort

- HIGH priority: 8-10 hours
- MEDIUM priority: 6-8 hours
- LOW priority: 2-3 hours
- **Total**: 16-21 hours

---

## Prerequisites Status Dashboard

| Phase | Prerequisites Status | Ready to Start? | Blocking Items |
|-------|---------------------|-----------------|----------------|
| Phase 1 | ✅ COMPLETE | ✅ YES | None |
| Phase 2 | ⚠️ INCOMPLETE | ❌ NO | PREREQ-2.1 (circular import POC) |
| Phase 3 | ⚠️ INCOMPLETE | ❌ NO | Phase 2 completion, PREREQ-3.2 |
| Phase 4 | ⚠️ INCOMPLETE | ❌ NO | PREREQ-4.1 (DES scripts), PREREQ-4.2 (DES templates), Phase 3 completion |
| Phase 5 | ⚠️ INCOMPLETE | ❌ NO | Phase 4 completion |
| Phase 6 | ⚠️ INCOMPLETE | ❌ NO | Phase 5 completion, PREREQ-6.2, PREREQ-6.3 |

**Current Phase**: Phase 1 COMPLETE, Phase 2 NOT READY

**Next Immediate Action**: Complete PREREQ-2.1 (circular import proof-of-concept)

---

**Document Status**: COMPLETE
**Review Status**: Prerequisites clearly defined
**Next Document**: Update design.md with gap resolutions
