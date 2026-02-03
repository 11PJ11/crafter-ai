# Architecture Decision Log - Plugin System

**Feature**: Plugin Architecture for nWave Installer
**Solution Architect**: Morgan
**Date**: 2026-02-03

---

## Phase 1: Gap Analysis Decisions

### Decision Context

Luna's comprehensive handover identified 9 gaps (3 architectural, 3 prerequisite, 3 process) and 3 critical decision points. This document records architectural decisions for each gap and decision point, with rationale and implementation guidance.

---

## Architectural Gaps

### GAP-ARCH-00: Version Strategy Undefined

**Status**: RESOLVED
**Decision**: Incremental versioning with semantic versioning compliance
**Rationale**:
- Version discontinuity (1.2.0 → 1.7.0) detected by Luna's data consistency analysis
- Semantic versioning requires clear versioning strategy
- Incremental versions communicate progress to users and enable rollback

**Version Strategy**:
```
Current: 1.2.0 (monolithic installer)
Phase 1 complete: 1.2.1 (infrastructure only - patch release)
Phase 3 complete: 1.3.0 (plugin orchestration active - minor release)
Phase 4 complete: 1.4.0 (DES available - minor release with new feature)
Phase 6 complete: 1.7.0 (production release - skip to 1.7.0 for marketing clarity)
```

**Semantic Versioning Justification**:
- 1.2.0 → 1.2.1: Patch - Infrastructure changes (non-breaking, no user-facing changes)
- 1.2.1 → 1.3.0: Minor - Plugin orchestration (backward compatible, internal refactoring)
- 1.3.0 → 1.4.0: Minor - DES feature added (new functionality, backward compatible)
- 1.4.0 → 1.7.0: Marketing version - Production readiness signal (skipping 1.5.0, 1.6.0 for clarity)

**Implementation**:
- Update pyproject.toml at each phase milestone
- Document in CHANGELOG.md with migration notes
- Update journey TUI mockups to show intermediate versions

**Priority**: MEDIUM (affects release planning, not blocking)
**Timeline**: Before Phase 6 deployment

---

### GAP-ARCH-01: Circular Import Prevention

**Status**: RESOLVED WITH HIGH PRIORITY VALIDATION
**Decision**: Extract module-level functions (Option A from DECISION-02)
**Rationale**:
- Clean separation of concerns - class methods become thin wrappers
- Testable in isolation - functions can be unit tested without class instantiation
- No runtime overhead - static imports, no dynamic loading
- Proven pattern - widely used in Python codebases

**Pattern**:
```python
# install_nwave.py - Extract implementation to module-level function
def install_agents_impl(target_dir, framework_source, logger, backup_manager, dry_run):
    """Extracted implementation (module-level function)."""
    # ... EXACT SAME 80-line implementation moved here ...
    pass

class nWaveInstaller:
    def _install_agents(self):
        """Thin wrapper calling extracted function."""
        return install_agents_impl(
            self.claude_dir,
            self.framework_source,
            self.rich_logger,
            self.backup_manager,
            self.dry_run
        )

# agents_plugin.py - Import function, NOT class
from scripts.install.install_nwave import install_agents_impl  # No circular dependency!

class AgentsPlugin(InstallationPlugin):
    def install(self, context: InstallContext) -> PluginResult:
        return install_agents_impl(
            context.claude_dir,
            context.framework_source,
            context.logger,
            context.backup_manager,
            context.dry_run
        )
```

**Validation Requirement**: Create proof-of-concept for ONE plugin (AgentsPlugin) before implementing all 4
**Test Strategy**: Import test in isolated Python subprocess to verify no circular dependency

**Implementation Order**:
1. Extract `install_agents_impl()` from `nWaveInstaller._install_agents()`
2. Create AgentsPlugin using extracted function
3. Run import test: `python -c "from scripts.install.plugins.agents_plugin import AgentsPlugin"`
4. If successful, repeat for CommandsPlugin, TemplatesPlugin, UtilitiesPlugin

**Priority**: HIGH - BLOCKS Phase 2
**Timeline**: Before Phase 2 starts (estimate: 2-3 hours for proof-of-concept)

---

### GAP-ARCH-02: InstallContext Completeness

**Status**: RESOLVED WITH VALIDATION REQUIREMENT
**Decision**: Validate during Phase 2, add missing fields as discovered
**Rationale**:
- Current InstallContext has 13 fields (including HIGH-03 fixes)
- Wrapper plugins will reveal additional utility dependencies
- Better to discover needs during implementation than speculate

**Current Fields** (after HIGH-03 fix):
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
    framework_source: Optional[Path]  # HIGH-03 fix
    project_root: Optional[Path]      # HIGH-03 fix
    rich_logger: Optional[Any]        # HIGH-03 fix
    current_version: Optional[str]
    target_version: Optional[str]
    plugin_data: Dict[str, Any]
```

**Validation Strategy**:
- During Phase 2 wrapper plugin creation, review ALL existing utilities used by `_install_*()` methods
- Document each utility: name, interface, usage pattern
- Add missing utilities to InstallContext BEFORE Phase 3 switchover

**Potential Missing Fields** (validate during Phase 2):
- `build_manager: Optional['BuildManager']` - If build pipeline coordination needed
- `manifest_writer: Optional['ManifestWriter']` - If manifest generation used
- `preflight_checker: Optional['PreflightChecker']` - If prerequisite validation used

**Implementation**:
1. Phase 2: Create wrapper plugins, identify missing utilities
2. Before Phase 3: Update InstallContext with discovered utilities
3. Update all existing plugins to use new fields if applicable

**Priority**: MEDIUM - Validate during Phase 2, implement before Phase 3
**Timeline**: Continuous during Phase 2, finalize before Phase 3

---

### GAP-ARCH-03: Plugin Verification Strategy

**Status**: RESOLVED WITH FALLBACK PATTERN
**Decision**: Implement fallback verification (Option B from DECISION-03)
**Rationale**:
- Robustness - plugins work even if `installation_verifier` unavailable
- Independent testing - plugins can be tested in isolation
- Graceful degradation - minimal verification better than none

**Verification Pattern**:
```python
class AgentsPlugin(InstallationPlugin):
    def verify(self, context: InstallContext) -> PluginResult:
        # PRIMARY: Use existing verifier
        if context.installation_verifier:
            agents_ok = context.installation_verifier._check_agents()
            if agents_ok:
                return PluginResult(success=True, message="Agents verified via InstallationVerifier")
            else:
                return PluginResult(success=False, message="Agent verification failed")

        # FALLBACK: Minimal file existence check
        target_dir = context.claude_dir / "agents" / "nw"
        if not target_dir.exists():
            return PluginResult(success=False, message=f"Agents directory not found: {target_dir}")

        agent_files = list(target_dir.glob("*.md"))
        expected_min = 10  # Adjust based on actual agent count

        if len(agent_files) < expected_min:
            return PluginResult(
                success=False,
                message=f"Expected at least {expected_min} agents, found {len(agent_files)}"
            )

        return PluginResult(success=True, message=f"Verified {len(agent_files)} agents (fallback)")
```

**Fallback Logic Per Plugin**:
- **AgentsPlugin**: Check `~/.claude/agents/nw/` for ≥10 `.md` files
- **CommandsPlugin**: Check `~/.claude/commands/nw/` for ≥20 `.yaml` files
- **TemplatesPlugin**: Check `~/.claude/templates/` for ≥8 files
- **UtilitiesPlugin**: Check `~/.claude/lib/python/` for utility modules
- **DESPlugin**: Subprocess import test: `python3 -c "import des; print('OK')"`

**Implementation**:
- Define fallback logic during Phase 2 wrapper plugin creation
- Document expected file counts based on current installer behavior
- Test fallback path explicitly (remove `installation_verifier` from context)

**Priority**: MEDIUM - Non-blocking but needed for robustness
**Timeline**: Phase 2 implementation

---

## Prerequisite Gaps

### GAP-PREREQ-01: DES Scripts Missing

**Status**: RESOLVED - CREATE BEFORE PHASE 4
**Decision**: Create DES scripts before Phase 4 starts (Option A from DECISION-01)
**Rationale**:
- Clean implementation without placeholders or technical debt
- Unblocks Phase 4 immediately upon reaching it
- Demonstrates completeness and professionalism
- Effort modest (4-6 hours total for both scripts)

**Missing Scripts**:
1. `nWave/scripts/des/check_stale_phases.py` - Pre-commit hook for stale phase detection
2. `nWave/scripts/des/scope_boundary_check.py` - Pre-commit hook for scope validation

**Implementation Specification**:

**File 1**: `nWave/scripts/des/check_stale_phases.py`
```python
#!/usr/bin/env python3
"""
Pre-commit hook: Detect abandoned IN_PROGRESS phases.

Prevents commits when execution-status.yaml contains stale phases
(phases marked IN_PROGRESS but not updated recently).
"""
import sys
from pathlib import Path

# Add DES module to path (after installation)
sys.path.insert(0, str(Path.home() / ".claude" / "lib" / "python"))

from des.application import StaleExecutionDetector

def main():
    """Run stale phase detection on current repository."""
    detector = StaleExecutionDetector(project_root=Path.cwd())
    result = detector.scan_for_stale_executions()

    if result.is_blocked:
        print("❌ ERROR: Stale IN_PROGRESS phases detected:")
        for stale in result.stale_executions:
            print(f"  - {stale.step_file}: {stale.phase_name} (abandoned {stale.age_hours}h ago)")
        print("\nResolution:")
        print("  1. Complete or mark phases as FAILED")
        print("  2. Or remove execution-status.yaml if workflow abandoned")
        return 1

    print("✓ No stale phases detected")
    return 0

if __name__ == "__main__":
    sys.exit(main())
```

**File 2**: `nWave/scripts/des/scope_boundary_check.py`
```python
#!/usr/bin/env python3
"""
Pre-commit hook: Validate scope boundaries.

Prevents commits when staged files are outside the declared scope
in roadmap.yaml implementation_scope section.
"""
import sys
from pathlib import Path

# Add DES module to path (after installation)
sys.path.insert(0, str(Path.home() / ".claude" / "lib" / "python"))

from des.validation import ScopeValidator

def main():
    """Run scope validation on git staged files."""
    validator = ScopeValidator(project_root=Path.cwd())
    result = validator.validate_git_staged_files()

    if not result.is_valid:
        print("❌ ERROR: Scope violations detected:")
        for violation in result.violations:
            print(f"  - {violation.file}: {violation.reason}")
        print("\nResolution:")
        print("  1. Update roadmap.yaml to include new scope")
        print("  2. Or unstage files outside scope")
        return 1

    print("✓ All staged files within declared scope")
    return 0

if __name__ == "__main__":
    sys.exit(main())
```

**Implementation Steps**:
1. Create directory: `mkdir -p nWave/scripts/des/`
2. Create both Python scripts with executable permissions: `chmod +x *.py`
3. Validate syntax: `python3 -m py_compile check_stale_phases.py scope_boundary_check.py`
4. Test on sample repository (if available) or defer full testing to Phase 4

**Priority**: HIGH - BLOCKS Phase 4
**Timeline**: BEFORE Phase 4 starts (estimate: 4-6 hours)
**Action Owner**: Morgan (Solution Architect) - delegate to developer or implement directly

---

### GAP-PREREQ-02: DES Templates Missing

**Status**: RESOLVED - CREATE BEFORE PHASE 4
**Decision**: Create DES templates before Phase 4 starts
**Rationale**:
- Templates required for complete DESPlugin installation
- Simple static files, low complexity (1-2 hours total)
- Enables complete Phase 4 implementation

**Missing Templates**:
1. `nWave/templates/.pre-commit-config-nwave.yaml` - Pre-commit configuration for nWave projects
2. `nWave/templates/.des-audit-README.md` - Documentation for DES audit trail

**Implementation Specification**:

**File 1**: `nWave/templates/.pre-commit-config-nwave.yaml`
```yaml
# Pre-commit hooks configuration for nWave projects with DES
# Install: pip install pre-commit && pre-commit install
# Manual run: pre-commit run --all-files

repos:
  - repo: local
    hooks:
      # DES: Stale phase detection
      - id: check-stale-phases
        name: DES Stale Phase Detection
        entry: python ~/.claude/scripts/check_stale_phases.py
        language: system
        pass_filenames: false
        always_run: true

      # DES: Scope boundary validation
      - id: scope-boundary-check
        name: DES Scope Boundary Validation
        entry: python ~/.claude/scripts/scope_boundary_check.py
        language: system
        pass_filenames: false
        files: '.*'

      # nWave: Step file validation (if applicable)
      - id: validate-step-file
        name: nWave Step File Validation
        entry: python ~/.claude/scripts/validate_step_file.py
        language: system
        files: 'steps/.*\.json$'

  # Standard hooks (optional - adjust based on project needs)
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v6.0.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-json
```

**File 2**: `nWave/templates/.des-audit-README.md`
```markdown
# DES Audit Trail

Immutable audit logs for nWave workflow traceability.

## Structure

- `audit-YYYY-MM-DD.log`: JSONL format with daily rotation
- Append-only (no modifications to existing entries)
- SHA256 content hashing for immutability verification

## Events Logged

- `TASK_INVOCATION_STARTED`: Agent execution begins
- `TASK_INVOCATION_VALIDATED`: Pre-invocation hooks passed
- `PHASE_STARTED`: TDD phase begins (e.g., RED_UNIT, GREEN, REFACTOR)
- `PHASE_COMPLETED`: TDD phase finishes
- `SCOPE_VIOLATION`: File modified outside declared scope
- `TIMEOUT_WARNING`: Phase execution exceeding threshold

## Query Examples

```bash
# Filter violations
grep '"event":"SCOPE_VIOLATION"' audit-*.log | jq .

# Count events by step
jq -r 'select(.event=="SCOPE_VIOLATION") | .step_path' *.log | sort | uniq -c

# View phase execution timeline
jq -r 'select(.event | startswith("PHASE_")) | "\(.timestamp) \(.step_path) \(.phase_name) \(.event)"' audit-*.log
```

## Retention Policy

- Daily logs retained for 90 days
- Archive to `docs/evolution/audit-archive/` after 90 days
- No automatic deletion (manual cleanup only)
```

**Implementation Steps**:
1. Create both template files in `nWave/templates/`
2. Validate YAML syntax: `yamllint .pre-commit-config-nwave.yaml`
3. Validate Markdown: Visual review of `.des-audit-README.md`

**Priority**: HIGH - BLOCKS Phase 4
**Timeline**: BEFORE Phase 4 starts (estimate: 1-2 hours)
**Action Owner**: Morgan or delegate to documentation specialist

---

### GAP-PREREQ-03: Build Pipeline DES Integration

**Status**: ACCEPTED AS LOW PRIORITY
**Decision**: Validate during Phase 4, fix if needed
**Rationale**:
- DESPlugin has fallback to `src/des/` if `dist/ide/lib/python/des/` unavailable
- Non-blocking - clean implementation preferred but fallback acceptable
- Low effort to validate (30 minutes)

**Validation Steps**:
1. Run build pipeline: `python tools/build.py` or `bash scripts/build-ide-bundle.sh`
2. Check if DES module copied: `ls dist/ide/lib/python/des/`
3. Expected files: `domain/`, `application/`, `ports/`, `adapters/`, `__init__.py`

**If Missing**:
Update build script to copy DES module:
```bash
# In build-ide-bundle.sh (example)
echo "Copying DES module..."
mkdir -p dist/ide/lib/python/des/
cp -r src/des/* dist/ide/lib/python/des/
```

**Priority**: LOW - Cosmetic improvement, not blocking
**Timeline**: Phase 4 validation (estimate: 30 minutes)

---

## Process Gaps

### GAP-PROCESS-01: Integration Checkpoint Automation

**Status**: RESOLVED - IMPLEMENT DURING PHASE 3
**Decision**: Create automated integration test suite for Phase 3 switchover
**Rationale**:
- Increases confidence in switchover correctness
- Automates regression detection (no manual file tree comparison)
- Can be run continuously during development

**Test Specification**:
```python
# tests/install/test_integration_checkpoint.py

def test_switchover_preserves_installation_behavior(tmp_path):
    """
    Validate that plugin-based installation produces identical results
    to pre-plugin baseline.

    This is the critical Phase 3 integration checkpoint ensuring
    no behavioral regressions during switchover.
    """
    # SETUP: Create baseline installation (simulate pre-plugin)
    baseline_dir = tmp_path / "baseline"
    baseline_installer = nWaveInstaller_PrePlugin(target_dir=baseline_dir)
    baseline_installer.install()

    # ACT: Install with plugin system
    plugin_dir = tmp_path / "plugin"
    plugin_installer = nWaveInstaller(target_dir=plugin_dir)
    plugin_installer.install()

    # ASSERT: Compare file trees
    baseline_files = set(get_file_tree(baseline_dir))
    plugin_files = set(get_file_tree(plugin_dir))

    assert baseline_files == plugin_files, "File trees differ after switchover!"

    # ASSERT: Compare verification results
    baseline_verification = run_verification(baseline_dir)
    plugin_verification = run_verification(plugin_dir)

    assert baseline_verification == plugin_verification, "Verification results differ!"

    # ASSERT: Compare file contents (not just paths)
    for file_path in baseline_files:
        baseline_content = (baseline_dir / file_path).read_text()
        plugin_content = (plugin_dir / file_path).read_text()
        assert baseline_content == plugin_content, f"File content differs: {file_path}"
```

**Helper Functions**:
```python
def get_file_tree(directory: Path) -> List[Path]:
    """Recursively get all files in directory (relative paths)."""
    return sorted([
        f.relative_to(directory)
        for f in directory.rglob("*")
        if f.is_file()
    ])

def run_verification(directory: Path) -> Dict[str, bool]:
    """Run InstallationVerifier and return results."""
    verifier = InstallationVerifier(target_dir=directory)
    return {
        "agents": verifier._check_agents(),
        "commands": verifier._check_commands(),
        "templates": verifier._check_templates(),
        "utilities": verifier._check_utilities(),
    }
```

**Implementation**:
- Create test file during Phase 3 implementation
- Run as part of Phase 3 integration checkpoint
- Add to CI/CD pipeline for continuous validation

**Priority**: MEDIUM - Increases confidence, not strictly blocking
**Timeline**: Phase 3 implementation (estimate: 4-6 hours)

---

### GAP-PROCESS-02: Rollback Strategy

**Status**: RESOLVED - DOCUMENT PROCEDURE
**Decision**: Document rollback procedure in installation-guide.md before Phase 3
**Rationale**:
- BackupManager already exists and creates backups
- Just needs clear documentation of rollback steps
- Safety measure for catastrophic failures

**Rollback Procedure**:
```markdown
## Rollback Procedure (Phase 3 Switchover Failure)

If Phase 3 switchover fails or causes regressions:

### Step 1: Detect Failure
- Integration tests fail with "File trees differ" or "Verification results differ"
- Manual installation testing reveals missing components
- User reports broken installation

### Step 2: Stop Deployment
- Do NOT proceed to Phase 4
- Notify team of switchover failure
- Preserve error logs and test output

### Step 3: Restore from Backup
```bash
# BackupManager creates backups in ~/.claude/backups/nwave-{timestamp}/
# Find latest backup before switchover
ls -lt ~/.claude/backups/ | head -n 5

# Restore from backup (replace {timestamp} with actual value)
BACKUP_DIR=~/.claude/backups/nwave-{timestamp}
TARGET_DIR=~/.claude

# Stop any running processes using nWave
# (Optional but recommended)

# Restore agents
rm -rf $TARGET_DIR/agents/nw
cp -r $BACKUP_DIR/agents/nw $TARGET_DIR/agents/

# Restore commands, templates, utilities similarly
# ... (repeat for each component)
```

### Step 4: Roll Back Git Commit
```bash
# If switchover changes were committed
git log --oneline -5  # Find switchover commit hash
git revert <commit-hash>  # Revert switchover changes

# Or if not pushed yet
git reset --hard HEAD~1  # Reset to before switchover
```

### Step 5: Verify Rollback Success
```bash
# Run verification
python scripts/install/install_nwave.py --verify

# Expected: All components verified (pre-plugin behavior)
```

### Step 6: Analyze Failure
- Review test output for specific failures
- Check integration checkpoint logs
- Identify root cause (circular import? Missing utility? Verification logic error?)
- Fix issue before attempting Phase 3 again
```

**Implementation**:
- Add rollback section to `docs/installation/installation-guide.md`
- Include in Phase 3 preparation checklist
- Reference in integration test failure messages

**Priority**: LOW - BackupManager exists, just needs documentation
**Timeline**: Before Phase 3 starts (estimate: 1 hour)

---

### GAP-PROCESS-03: Version Bump Strategy

**Status**: RESOLVED (See GAP-ARCH-00)
**Decision**: Incremental versioning (Option C)
**Rationale**: See GAP-ARCH-00 decision for complete rationale

**Version Strategy Summary**:
- Phase 1: 1.2.0 → 1.2.1 (patch - infrastructure)
- Phase 3: 1.2.1 → 1.3.0 (minor - plugin orchestration)
- Phase 4: 1.3.0 → 1.4.0 (minor - DES feature)
- Phase 6: 1.4.0 → 1.7.0 (marketing version - production release)

**Implementation**:
- Update `pyproject.toml` at each phase completion
- Document in CHANGELOG.md with migration notes
- Update journey TUI mockups to show intermediate versions

**Priority**: LOW - Cosmetic but affects release planning
**Timeline**: Before Phase 6 deployment

---

## Critical Decision Points

### DECISION-01: DES Script Creation Timing

**Decision**: Option A - Create DES scripts BEFORE Phase 4
**Rationale**: (See GAP-PREREQ-01 for complete rationale)
- Clean implementation without placeholders
- Unblocks Phase 4 immediately
- Demonstrates completeness
- Effort modest (4-6 hours)

**Trade-off Accepted**: Adds 6 hours to timeline, but prevents technical debt

**Implementation**: See GAP-PREREQ-01

---

### DECISION-02: Circular Import Mitigation Approach

**Decision**: Option A - Extract module-level functions
**Rationale**: (See GAP-ARCH-01 for complete rationale)
- Clean separation of concerns
- Testable in isolation
- No runtime overhead
- Proven pattern

**Trade-off Accepted**: Requires refactoring existing class methods (1-2 hours per plugin)

**Implementation**: See GAP-ARCH-01

---

### DECISION-03: Wrapper Plugin Verification Strategy

**Decision**: Option B - Fallback to minimal file existence check
**Rationale**: (See GAP-ARCH-03 for complete rationale)
- Robustness if verifier unavailable
- Enables independent plugin testing
- Minimal verification better than none

**Trade-off Accepted**: Slightly more complex plugin code (20 lines per plugin)

**Implementation**: See GAP-ARCH-03

---

## Implementation Readiness Assessment

### Pre-Review Readiness: 7.5/10

**Gaps Remaining**:
- DES scripts not created (blocks Phase 4)
- Circular import mitigation needs validation (Phase 2)
- Integration checkpoints need automation (Phase 3)

### Post-Decision Readiness: 8.5/10

**Improvements**:
- ✅ All 9 gaps analyzed and resolved
- ✅ All 3 decision points resolved with clear rationale
- ✅ Implementation patterns documented
- ✅ Validation strategies defined
- ✅ Version strategy clarified
- ✅ Prerequisites clearly identified

**Remaining Work**:
- Implementation of resolutions (estimated: 15-20 hours total)
- HIGH priority items (DES scripts, circular import POC, DES templates): 8-10 hours
- MEDIUM priority items (verification fallback, integration tests): 6-8 hours
- LOW priority items (documentation, validation): 2-3 hours

**Target Achieved**: ≥8.5/10 implementation readiness ✓

---

## Next Steps Summary

### Immediate Actions (Before Phase 2)
1. ✅ Review handover document - COMPLETE (this document)
2. ⚠️ Create proof-of-concept for circular import mitigation (2-3 hours)
3. ⚠️ Create DES scripts (4-6 hours)
4. ⚠️ Create DES templates (1-2 hours)
5. ⚠️ Update design.md with gap resolutions (next step)

### Phase 2 Actions
- Validate InstallContext completeness
- Extract module-level functions for all 4 components
- Create wrapper plugins
- Define fallback verification logic
- Unit test each plugin

### Phase 3 Actions
- Create integration checkpoint test suite
- Modify install_framework() to use PluginRegistry
- Run integration tests
- Document rollback procedure

### Phase 4 Actions
- Validate DES scripts exist (prerequisite)
- Validate DES templates exist (prerequisite)
- Implement DESPlugin
- Test DES installation

---

**Document Status**: COMPLETE
**Review Status**: Architecture decisions finalized
**Next Document**: Update design.md and nwave-plugin-system-architecture.md with these decisions
