# nWave+DES Installation Integration Summary

**Date:** 2026-01-23
**Author:** Riley (product-owner) under Lyra orchestration
**Purpose:** Integration of Installation/Uninstallation user stories with DES feature set

---

## Executive Summary

The DES (Deterministic Execution System) feature now includes comprehensive installation and lifecycle management user stories. These stories ensure that nWave+DES can be installed, verified, upgraded, and uninstalled with "estremamente semplice e trasparente" (extremely simple and transparent) user experience.

**Key Achievement**: Zero-friction installation enables immediate DES adoption without manual configuration complexity.

---

## Document Locations

### Primary Documentation

| Document | Location | Purpose |
|----------|----------|---------|
| **Installation User Stories** | `docs/feature/des/discuss/installation-user-stories.md` | 4 user stories covering installation, uninstallation, verification, and upgrade |
| **DES User Stories** | `docs/feature/des/discuss/user-stories.md` | 12 user stories covering DES execution, validation, and audit |
| **DES Requirements** | `docs/feature/des/discuss/requirements.md` | Functional and non-functional requirements for DES |
| **Acceptance Criteria** | `docs/feature/des/discuss/acceptance-criteria.md` | BDD Given-When-Then acceptance criteria |
| **DoR Checklist** | `docs/feature/des/discuss/dor-checklist.md` | Definition of Ready validation checklist |

---

## Installation User Stories Overview

### US-INSTALL-001: One-Command Installation
**Priority:** P0 (Blocker for all other stories)
**Story Points:** 5

**What:** Single command (`nwave install`) installs all nWave+DES components with automatic configuration.

**Key Features:**
- Detects Claude Code environment automatically
- Installs CLI, DES validation library, agents, templates, hooks
- Configures SubagentStop hook for DES validation
- Runs health check post-installation
- Supports upgrade mode (preserves user data)
- Supports CI mode (minimal installation without Claude dependencies)

**Domain Examples:**
- Fresh installation on macOS with full component installation
- Upgrade from v0.9.2 → v1.0.0 with data migration
- CI/CD installation with --ci flag (skips hooks/agents)
- Permission failure with recovery guidance

**Acceptance Criteria:** 11 AC covering installation completeness, transparency, safety, and performance

---

### US-INSTALL-002: Clean Uninstallation
**Priority:** P0 (Critical for trial adoption)
**Story Points:** 3

**What:** Single command (`nwave uninstall`) removes all nWave components with backup and optional data deletion.

**Key Features:**
- Creates backup before uninstallation (mandatory unless --no-backup)
- Preserves user data by default (feature docs, step files, audit logs)
- Offers `--delete-data` flag for complete removal with confirmation
- Supports partial uninstallation (--keep-agents, --keep-templates)
- Detects active executions and warns before removal
- Provides rollback capability via backup restoration

**Domain Examples:**
- Standard uninstallation preserving user data
- Complete uninstallation with --delete-data flag
- Restoration from backup after uninstallation
- Partial uninstallation keeping agents/templates

**Acceptance Criteria:** 10 AC covering safety, transparency, data preservation, and restoration

---

### US-INSTALL-003: Installation Verification & Health Check
**Priority:** P1 (Critical for learning experience)
**Story Points:** 2

**What:** Health check command (`nwave health-check`) verifies all components are operational post-installation.

**Key Features:**
- Tests 5 components: CLI, DES library, agents, hooks, templates
- Provides pass/fail status with explanations
- Suggests specific recovery actions for failures
- Runs automatically post-installation
- Educational mode (`--explain`) describes component purposes
- Exit codes support CI integration (0 = healthy, non-zero = unhealthy)

**Domain Examples:**
- Healthy installation with all components passing
- Partial failure (hook not executable) with recovery guidance
- Missing component (agents not installed) with diagnosis
- Educational mode explaining each component's purpose

**Acceptance Criteria:** 10 AC covering component testing, diagnostics, educational value, and CI integration

---

### US-INSTALL-004: Upgrade & Migration
**Priority:** P1 (Critical for production adoption)
**Story Points:** 5

**What:** Upgrade workflow with automatic data migration, validation, and rollback capability.

**Key Features:**
- Detects version differences and lists required migrations
- Creates mandatory backup before upgrade
- Migrates data formats automatically (step files, config, audit logs)
- Preserves custom configuration settings
- Validates data integrity post-migration
- Automatic rollback on ANY migration failure
- Dry-run mode (`--dry-run`) to preview changes
- Manual rollback command for post-upgrade issues

**Domain Examples:**
- Smooth upgrade v0.9.2 → v1.0.0 with step file migration
- Upgrade failure with automatic rollback to pre-upgrade state
- Dry-run preview showing migration impact before commitment
- Manual rollback after upgrade when needed

**Acceptance Criteria:** 11 AC covering migration automation, safety, backward compatibility, and rollback

---

## Integration with DES Execution Stories

### Dependency Chain

```
┌─────────────────────────────────────────────────────────────┐
│ SPRINT 0: Installation Foundation (BLOCKERS)               │
├─────────────────────────────────────────────────────────────┤
│ US-INSTALL-001: One-Command Installation          (5 pts)  │
│ US-INSTALL-003: Health Check                      (2 pts)  │
│                                                             │
│ OUTPUT: nWave+DES installed and verified                   │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│ SPRINT 1: DES Foundation (requires installation)           │
├─────────────────────────────────────────────────────────────┤
│ US-001: Command-Origin Task Filtering             (3 pts)  │
│ US-002: Pre-Invocation Template Validation         (5 pts)  │
│ US-006: Turn Discipline Without max_turns          (3 pts)  │
│                                                             │
│ OUTPUT: DES validation gates operational                   │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│ SPRINT 2: DES Validation (requires foundation)             │
├─────────────────────────────────────────────────────────────┤
│ US-003: Post-Execution State Validation            (8 pts)  │
│ US-004: Audit Trail for Compliance                 (3 pts)  │
│                                                             │
│ OUTPUT: Complete execution audit trail                     │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│ SPRINT 3: Lifecycle Management + Polish                    │
├─────────────────────────────────────────────────────────────┤
│ US-INSTALL-002: Uninstallation                    (3 pts)  │
│ US-INSTALL-004: Upgrade & Migration               (5 pts)  │
│ US-005: Failure Recovery Guidance                 (5 pts)  │
│ US-007: Boundary Rules for Scope                  (2 pts)  │
│ US-008: Stale Execution Detection                 (2 pts)  │
│ US-009: Learning Feedback                         (3 pts)  │
│                                                             │
│ OUTPUT: Production-ready lifecycle management              │
└─────────────────────────────────────────────────────────────┘
```

### Critical Path Analysis

**Blocker Relationship:**
> "All DES execution stories (US-001 through US-009) **require** successful installation (US-INSTALL-001) as a prerequisite."

**Why Installation is Sprint 0:**
1. **Zero execution without installation**: No `/nw:execute` commands work until nWave+DES is installed
2. **Health check validates DES readiness**: US-INSTALL-003 verifies SubagentStop hook is operational
3. **Upgrade enables production adoption**: Teams won't adopt without safe upgrade path (US-INSTALL-004)

**Installation First Principle:**
```
IF installation_status ≠ "HEALTHY"
THEN ALL nWave commands MUST fail with clear error:
  "nWave not installed. Run 'nwave install' to get started."
```

---

## Persona Coverage Analysis

### Installation Stories Persona Distribution

| Persona | Primary Stories | Secondary Stories | Coverage |
|---------|-----------------|-------------------|----------|
| **Marcus** (Senior Dev) | US-INSTALL-001, US-INSTALL-004 | US-INSTALL-003 | ✓ High |
| **Priya** (Tech Lead) | US-INSTALL-002 | US-INSTALL-004 | ✓ High |
| **Alex** (Junior Dev) | US-INSTALL-003 | US-INSTALL-001 | ✓ High |

**Balanced Coverage:** Each persona has at least one primary story addressing their specific pain points.

---

## Acceptance Criteria Totals

| Story | Acceptance Criteria Count | Complexity |
|-------|---------------------------|------------|
| US-INSTALL-001 | 11 AC | High (installation orchestration) |
| US-INSTALL-002 | 10 AC | Medium (safe removal) |
| US-INSTALL-003 | 10 AC | Low (verification only) |
| US-INSTALL-004 | 11 AC | High (migration complexity) |
| **Total** | **42 AC** | - |

**Combined with DES stories:** 112 total acceptance criteria across 16 user stories (12 DES + 4 installation)

---

## Transparency Requirements ("estremamente semplice e trasparente")

### Simplicity Achieved

✅ **Single-command installation**: `nwave install` (no manual configuration)
✅ **Single-command uninstallation**: `nwave uninstall` (no orphaned files)
✅ **Zero external dependencies**: Pure Python stdlib (no pip install X, Y, Z cascade)
✅ **Automatic configuration**: Hooks, agents, templates configured automatically
✅ **Works out-of-the-box**: No config file editing required

### Transparency Achieved

✅ **Visible installation output**: Shows each component being installed with file paths
✅ **Health check verification**: User sees PASS/FAIL for each component
✅ **Educational mode**: `--explain` flag describes what each component does and why
✅ **Installation log**: Detailed trace at `~/.claude/nwave/install-<date>.log`
✅ **Clear error messages**: Failures include diagnosis AND recovery suggestions

**Example Transparency:**
```bash
Installing components...
✓ nWave CLI installed to: /Users/marcus/.claude/nwave/bin/
✓ DES components installed to: /Users/marcus/.claude/nwave/des/
✓ Agent definitions synced to: /Users/marcus/.claude/agents/nw/
✓ Templates synced to: /Users/marcus/.claude/templates/nw/
✓ SubagentStop hook configured at: /Users/marcus/.claude/hooks/subagent-stop.py
```

User knows EXACTLY what was installed and WHERE. No hidden magic.

---

## Safety Guarantees

### Installation Safety

1. **Atomic Installation**: All components installed successfully OR nothing installed (rollback on failure)
2. **No Data Loss**: User data never deleted during installation (only during explicit `uninstall --delete-data`)
3. **Backup Before Modification**: Upgrade and uninstall always create backups first
4. **Validation Before Commitment**: Health checks run before declaring success
5. **Clear Error Messages**: Every failure includes diagnosis and recovery steps

### Failure Scenario Coverage

Installation stories include 8 failure scenarios with detection, error messages, and recovery:

| Failure | Detection | Recovery |
|---------|-----------|----------|
| Claude Code Not Found | Check ~/.claude/ exists | Install Claude Code OR use --ci flag |
| Python < 3.11 | Check sys.version_info | Upgrade Python via pyenv |
| Permission Denied | Check write access | Fix ownership: sudo chown -R $USER ~/.claude/ |
| Disk Space Low | Check available space | Free up space or use different location |
| Corrupted Download | Verify checksum | Clear pip cache, reinstall |
| Conflicting Hook | Check hook source | Backup existing, retry with --force |
| Git Not Found | Check git command | Install Git OR ignore warning |
| Network Timeout | Timeout during pip | Retry OR use offline install |

**Zero unhandled failures:** Every failure mode has documented recovery path.

---

## Success Metrics

### Installation Success Metrics (from US-INSTALL stories)

| Metric | Target | Measurement Method |
|--------|--------|-------------------|
| Installation success rate | > 95% | Telemetry (opt-in) |
| Time to first workflow | < 5 min | Installation to first `/nw:execute` |
| Health check pass rate | > 98% | Post-installation health check results |
| Upgrade success rate | > 99% | Upgrade completion vs. rollback rate |

### User Experience Metrics

| Persona | Target Experience | Success Indicator |
|---------|------------------|-------------------|
| **Marcus** | Installation < 2 minutes, no manual config | Time measurement, config file checks |
| **Priya** | Team onboarding < 15 min per developer | Onboarding time tracking |
| **Alex** | Understands what was installed and why | Survey: "I understand what nWave installed" |

### Safety Metrics

| Metric | Target | Enforcement |
|--------|--------|-------------|
| Zero data loss incidents | 0 incidents | Backup mechanism MANDATORY |
| Rollback success rate | 100% | Automatic rollback on ANY failure |
| Recovery time | < 5 minutes | Failure to working state |

---

## Next Steps: Handoff to DESIGN Wave

### DoR (Definition of Ready) Validation

Installation user stories are ready for DESIGN wave handoff to **Morgan (solution-architect)** when:

- [x] All 4 installation stories written with complete structure
- [x] Domain examples provided (3-4 per story with concrete commands/output)
- [x] Acceptance criteria defined (10-11 AC per story, all testable)
- [x] Personas addressed (Marcus, Priya, Alex all have coverage)
- [x] Integration with DES stories documented
- [x] Failure scenarios identified with recovery paths
- [x] Safety guarantees defined
- [x] Success metrics established

### Handoff Package for Morgan

**Deliverables:**
1. `installation-user-stories.md` - 4 user stories with full domain examples
2. `INSTALLATION-INTEGRATION.md` - This document (integration summary)
3. Link to existing DES documentation:
   - `user-stories.md` - 12 DES execution stories
   - `requirements.md` - Functional requirements
   - `acceptance-criteria.md` - BDD Given-When-Then criteria

**Morgan's Responsibilities (DESIGN Wave):**
1. Design installation architecture (installer components, directory structure)
2. Design health check validation logic (5 component tests)
3. Design upgrade migration strategy (schema versioning, data migration)
4. Design backup/rollback mechanism (atomic operations, state preservation)
5. Design hook integration (SubagentStop configuration during installation)
6. Create architecture diagrams showing installation workflow
7. Document technical constraints and implementation approach

**Blocking Questions for Morgan:**
1. What's the packaging strategy? (pip package, shell script, or both?)
2. Where should nWave be installed? (user-scoped ~/.claude/nwave/ or system-wide?)
3. How to detect Claude Code environment reliably? (check ~/.claude/ or other method?)
4. What's the hook integration mechanism? (file copy, symlink, or registration API?)
5. How to handle multi-user systems? (per-user installation or shared installation?)

---

## Appendix: Story Prioritization Rationale

### Why US-INSTALL-001 is Sprint 0 (Blocker)

**Rationale:** Without installation, no other DES story can be executed or validated.

**Evidence:**
- US-001 (Command Filtering) requires SubagentStop hook → hook installed by US-INSTALL-001
- US-002 (Pre-Invocation Validation) requires DES library → library installed by US-INSTALL-001
- US-003 (Post-Execution Validation) requires SubagentStop hook → hook installed by US-INSTALL-001

**Conclusion:** Installation is not just P0, it's Sprint 0 (execute before Sprint 1 DES stories).

### Why US-INSTALL-003 is Sprint 0 (Also Blocker)

**Rationale:** Teams won't trust installation without verification.

**User Perspective (Alex):**
> "The installer said 'Installation complete!' but I don't know if it actually worked. I need to SEE that each component is operational before I start using it."

**Risk Mitigation:** Health check reduces support burden (users self-diagnose installation issues).

### Why US-INSTALL-002 and US-INSTALL-004 are Sprint 3 (Polish)

**Rationale:** Uninstallation and upgrade are less urgent than core execution functionality.

**Tradeoff Analysis:**
- **Pro (Earlier)**: Trial adoption easier with clear uninstall path
- **Con (Earlier)**: Delays core DES value delivery (execution validation)
- **Decision**: Move to Sprint 3 after DES execution proven valuable

**Upgrade Exception:** May promote US-INSTALL-004 to Sprint 2 if beta users need migration support.

---

## Summary

✅ **4 installation user stories created** covering full lifecycle (install, uninstall, verify, upgrade)
✅ **42 acceptance criteria defined** ensuring completeness and testability
✅ **12 domain examples provided** with concrete commands and expected output
✅ **8 failure scenarios documented** with detection and recovery
✅ **Integration with 12 DES stories** via dependency chain
✅ **Transparency requirements met** ("estremamente semplice e trasparente")
✅ **Safety guarantees established** (atomic operations, mandatory backups, zero data loss)
✅ **Ready for DESIGN wave handoff** to Morgan (solution-architect)

**Next Action:** Morgan receives handoff package and begins architectural design for installation workflows.

---

*Document created by Riley (product-owner) under Lyra orchestration - 2026-01-23*
