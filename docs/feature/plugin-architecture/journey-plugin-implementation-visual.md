# Plugin System Implementation Journey - Visual Map

**Feature**: Plugin Architecture for nWave Installer
**Team**: Complete (Dev + Architect + PO)
**Status**: Phase 1/6 Complete - Infrastructure Exists
**Date**: 2026-02-03

---

## Emotional Arc

```
START: Anxious            MIDDLE: Focused          END: Confident
"Will this work?"    →    "Design is solid"    →   "DES installable!"
```

---

## Journey Overview: 6 Implementation Milestones

```
┌─ Milestone 1: Infrastructure Foundation ─────────────────┐  Emotion: Uncertain
│ $ Task: Create plugin base classes and registry         │  "Is topological
│                                                          │   sort correct?"
│ ✓ Status: COMPLETE (Fase 1/6)                           │
│ ✓ Files: base.py, registry.py, test_plugin_registry.py  │
│ ✓ Tests: 10/10 passing                                  │
│ ✓ Commit: d86acfa                                       │
│                                                          │
│ Shared Artifacts:                                       │
│   ${version} = "1.2.0" ◄── pyproject.toml              │
│   ${plugin_dir} = "scripts/install/plugins/"            │
│                                                          │
│ Decision: Ready for Phase 2? YES ✓                      │
└──────────────────────────────────────────────────────────┘
          │
          │ ┌─────────────────────────────────────────────┐
          │ │ INTEGRATION CHECKPOINT                      │
          │ │ ✓ Kahn's algorithm correct (topo sort)      │
          │ │ ✓ Circular dependency detection works       │
          │ │ ✓ Priority ordering validated               │
          │ │ ✗ NO installer changes yet (expected)       │
          │ └─────────────────────────────────────────────┘
          ▼

┌─ Milestone 2: Wrap Existing Methods as Plugins ──────────┐  Emotion: Careful
│ $ Task: Create wrapper plugins (Agents, Commands, etc.)  │  "Don't break
│                                                          │   existing logic!"
│ ⧗ Status: NOT STARTED (Fase 2/6)                        │
│ ⧗ Planned: agents_plugin.py, commands_plugin.py, ...    │
│                                                          │
│ Strategy: WRAPPER PATTERN                               │
│   • AgentsPlugin.install() CALLS _install_agents()      │
│   • CommandsPlugin.install() CALLS _install_commands()  │
│   • NO reimplementation - reuse existing logic          │
│                                                          │
│ Shared Artifacts:                                       │
│   ${backup_manager} ◄── install_nwave.py (reused)      │
│   ${installation_verifier} ◄── installation_verifier.py │
│                                                          │
│ Integration Risk: HIGH (circular imports possible)       │
│   → Mitigation: Extract module-level functions          │
│                                                          │
│ Decision: Create 4 wrapper plugins                      │
└──────────────────────────────────────────────────────────┘
          │
          │ ┌─────────────────────────────────────────────┐
          │ │ INTEGRATION CHECKPOINT                      │
          │ │ ⧗ Plugins call existing methods correctly   │
          │ │ ⧗ No behavioral changes (same output)       │
          │ │ ⧗ Circular import prevention validated      │
          │ └─────────────────────────────────────────────┘
          ▼

┌─ Milestone 3: Switchover to PluginRegistry ──────────────┐  Emotion: Tense
│ $ Task: Modify install_framework() to use plugins       │  "This is the big
│                                                          │   change moment"
│ ⧗ Status: NOT STARTED (Fase 3/6)                        │
│ ⧗ Change: install_framework() → PluginRegistry.install_all()
│                                                          │
│ Critical Change:                                         │
│   BEFORE: self._install_agents()                        │
│            self._install_commands()                     │
│   AFTER:  registry.install_all(context)                │
│                                                          │
│ Shared Artifacts:                                       │
│   ${claude_dir} = ~/.claude ◄── PathUtils              │
│   ${dist_dir} = dist/ide ◄── build pipeline            │
│                                                          │
│ Integration Risk: CRITICAL (orchestration path changes) │
│   → Mitigation: Keep existing methods (plugins call)    │
│   → Validation: Compare file trees before/after         │
│                                                          │
│ Decision: Preserve existing methods during migration    │
└──────────────────────────────────────────────────────────┘
          │
          │ ┌─────────────────────────────────────────────┐
          │ │ INTEGRATION CHECKPOINT                      │
          │ │ ⧗ Same files installed (path comparison)    │
          │ │ ⧗ Same verification passes                  │
          │ │ ⧗ Backup manager still works                │
          │ │ ⧗ No regressions detected                   │
          │ └─────────────────────────────────────────────┘
          ▼

┌─ Milestone 4: DES Plugin Implementation ─────────────────┐  Emotion: Excited
│ $ Task: Add DES as plugin (demonstrate extensibility)   │  "Zero installer
│                                                          │   changes needed!"
│ ⧗ Status: NOT STARTED (Fase 4/6)                        │
│ ⧗ File: des_plugin.py (NEW component)                   │
│                                                          │
│ DES Components:                                          │
│   • src/des/ → ~/.claude/lib/python/des/ ✓ (exists)    │
│   • check_stale_phases.py ✗ (must create)              │
│   • scope_boundary_check.py ✗ (must create)            │
│   • .pre-commit-config-nwave.yaml ✗ (must create)      │
│                                                          │
│ Shared Artifacts:                                       │
│   ${des_source} = src/des/ ◄── validated (exists)      │
│   ${templates_dir} = ~/.claude/templates/              │
│                                                          │
│ Integration Risk: MEDIUM (DES scripts missing)          │
│   → Mitigation: Create scripts BEFORE Phase 4          │
│                                                          │
│ Decision: DESPlugin depends on [templates, utilities]   │
└──────────────────────────────────────────────────────────┘
          │
          │ ┌─────────────────────────────────────────────┐
          │ │ INTEGRATION CHECKPOINT                      │
          │ │ ⧗ DES module importable (import test)       │
          │ │ ⧗ DES scripts executable (chmod +x)         │
          │ │ ⧗ DES templates installed                   │
          │ │ ⧗ Dependencies respected (after utilities)  │
          │ └─────────────────────────────────────────────┘
          ▼

┌─ Milestone 5: Testing & Documentation ───────────────────┐  Emotion: Thorough
│ $ Task: Comprehensive test suite + docs                 │  "Make it robust
│                                                          │   and clear"
│ ⧗ Status: NOT STARTED (Fase 5/6)                        │
│                                                          │
│ Testing Strategy:                                        │
│   • Unit tests: Each plugin in isolation                │
│   • Integration: Fresh install + upgrade scenarios      │
│   • Regression: Compare pre-plugin vs post-plugin       │
│   • Adversarial: Error handling, circular deps          │
│                                                          │
│ Documentation:                                           │
│   • docs/installation/installation-guide.md (update)    │
│   • docs/reference/des-audit-trail-guide.md (NEW)       │
│   • docs/development/plugin-development-guide.md (NEW)  │
│                                                          │
│ Shared Artifacts:                                       │
│   ${test_coverage} >= 80% ◄── pytest-cov               │
│   ${verification_report} ◄── InstallationVerifier      │
│                                                          │
│ Quality Gate: All tests pass + docs complete            │
└──────────────────────────────────────────────────────────┘
          │
          │ ┌─────────────────────────────────────────────┐
          │ │ INTEGRATION CHECKPOINT                      │
          │ │ ⧗ Test suite passes (unit + integration)    │
          │ │ ⧗ Documentation reviewed                    │
          │ │ ⧗ Backward compatibility validated          │
          │ └─────────────────────────────────────────────┘
          ▼

┌─ Milestone 6: Deployment & Rollout ──────────────────────┐  Emotion: Confident
│ $ Task: Release v1.7.0 with plugin system               │  "DES is ready
│                                                          │   for the world!"
│ ⧗ Status: NOT STARTED (Fase 6/6)                        │
│                                                          │
│ Release Checklist:                                       │
│   • Version bump: 1.2.0 → 1.7.0 (minor - new feature)  │
│   • CHANGELOG.md updated                                 │
│   • Release notes with migration guide                   │
│   • Gradual rollout: alpha → beta → stable             │
│                                                          │
│ Shared Artifacts:                                       │
│   ${version} = "1.7.0" ◄── pyproject.toml              │
│   ${release_tag} = v1.7.0 ◄── git tag                  │
│                                                          │
│ Backward Compatibility:                                  │
│   ✓ Existing installations upgrade cleanly              │
│   ✓ DES added without breaking existing setup           │
│   ✓ All integration tests pass                          │
│                                                          │
│ Success Criteria: Users install DES with zero friction  │
└──────────────────────────────────────────────────────────┘
          │
          ▼
     ┌──────────┐
     │ SUCCESS! │
     │ Plugin   │
     │ System   │
     │ Live     │
     └──────────┘

---

## Shared Artifact Registry (Cross-Milestone)

| Artifact | Source of Truth | Used In | Risk |
|----------|----------------|---------|------|
| `${version}` | `pyproject.toml` | M1, M6 (installer version) | LOW |
| `${claude_dir}` | `~/.claude` | M2, M3, M4 (install path) | LOW |
| `${dist_dir}` | `dist/ide` | M3, M4 (build output) | LOW |
| `${backup_manager}` | `install_nwave.py` | M2, M4 (backup utility) | MEDIUM |
| `${des_source}` | `src/des/` | M4 (DES module) | HIGH* |

*HIGH risk: DES scripts/templates missing, must create BEFORE M4

---

## Integration Failure Points (What Could Go Wrong)

### 🔴 CRITICAL: Milestone 2 → 3 Transition

**Risk**: Circular import when plugins call installer methods
- **Current**: Plugins import `nWaveInstaller` class
- **Problem**: `install_nwave.py` imports plugins → plugins import installer → CYCLE
- **Solution**: Extract module-level functions (`install_agents_impl()`)
- **Validation**: Import test in isolated Python subprocess

### 🟡 MEDIUM: Milestone 4 Prerequisites

**Risk**: DES scripts don't exist yet
- **Current**: `check_stale_phases.py` NOT CREATED
- **Current**: `scope_boundary_check.py` NOT CREATED
- **Blocker**: DESPlugin.install() assumes these exist
- **Solution**: Create scripts BEFORE Milestone 4 (prerequisite task)
- **Alternative**: Placeholder scripts with TODO (defer to US-009)

### 🟢 LOW: Milestone 3 Behavioral Changes

**Risk**: Plugin orchestration changes behavior
- **Mitigation**: Wrapper pattern (plugins call existing methods)
- **Validation**: File tree comparison (before/after identical)
- **Test**: Integration test with baseline capture

---

## CLI Commands Journey (Developer Perspective)

```bash
# Milestone 1: COMPLETE ✓
$ pytest tests/install/test_plugin_registry.py
10 passed in 0.15s ✓

# Milestone 2: Create wrapper plugins (DEV)
$ # No user-facing commands - internal development

# Milestone 3: Switchover (USER sees no difference)
$ python scripts/install/install_nwave.py
Installing 5 plugins...
[1/5] Installing: agents
[2/5] Installing: commands
[3/5] Installing: templates
[4/5] Installing: utilities
[5/5] Installing: des  ← NEW!
✓ Installation complete

# Milestone 4: DES available (USER)
$ python3 -c "import sys; sys.path.insert(0, '$HOME/.claude/lib/python'); from des.application import DESOrchestrator; print('DES OK')"
DES OK ✓

# Milestone 5: Verification (USER)
$ python scripts/install/install_nwave.py --verify
┌─────────────┬────────┬───────┐
│ Component   │ Status │ Count │
├─────────────┼────────┼───────┤
│ Agents      │ OK     │ 15    │
│ Commands    │ OK     │ 20    │
│ Templates   │ OK     │ 8     │
│ Utilities   │ OK     │ 5     │
│ DES Module  │ OK     │ ✓     │ ← NEW!
└─────────────┴────────┴───────┘

# Milestone 6: Production use (USER)
$ /nw:develop "new feature"
✓ DES audit trail: .des/audit/audit-2026-02-03.log created
```

---

## Decision Points & Trade-offs

### Decision 1: Wrapper vs Rewrite (Milestone 2)
- **Option A**: Rewrite installation logic in plugins (clean architecture)
- **Option B**: Wrapper plugins call existing methods (safe migration)
- **CHOSEN**: Option B (Wrapper)
- **Rationale**: Preserve proven logic, reduce risk, enable gradual refactoring

### Decision 2: Preserve vs Remove Methods (Milestone 3)
- **Option A**: Remove `_install_agents()` etc. immediately (clean break)
- **Option B**: Keep existing methods, plugins call them (gradual migration)
- **CHOSEN**: Option B (Preserve)
- **Rationale**: Enables rollback, reduces blast radius, allows phased refactoring

### Decision 3: DES Scripts Creation Timing (Milestone 4)
- **Option A**: Create scripts before Phase 4 (clean implementation)
- **Option B**: Placeholder scripts with TODO (defer to US-009)
- **RECOMMENDED**: Option A
- **Rationale**: Clean implementation, unblocks Phase 4, demonstrates completeness

---

## Handoff Notes

**To Solution Architect (Morgan)**:
- Phase 1/6 complete: Infrastructure validated and tested
- Phase 2-6 require implementation per design.md
- See `handover-to-solution-architect.md` for architectural gaps and recommendations
- Critical: Create DES scripts BEFORE Phase 4 (see MED-01, MED-02 remediations)

**Next Immediate Step**: Milestone 2 - Create wrapper plugins (4 commits)
