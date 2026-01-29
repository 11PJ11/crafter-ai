# Definition of Ready Checklist: Installation Environment Detection

**Feature ID:** APEX-002
**Wave:** DISCUSS -> DESIGN Handoff
**Created:** 2026-01-29
**Status:** READY FOR VALIDATION

---

## DoR Validation Summary

This checklist validates that the DISCUSS wave deliverables are complete and ready for handoff to the DESIGN wave (solution-architect).

---

## Checklist Items

### 1. Problem Statement Clear and Validated

| Item | Status | Evidence |
|------|--------|----------|
| Problem written in domain language | PASS | "Marco... encounters a cryptic ModuleNotFoundError" - describes real user pain |
| Describes real user pain | PASS | 30 minutes wasted searching for solution |
| Stakeholder validated | PASS | Mike provided explicit decisions on all requirements |

**Example (Pass):** "Marco, a developer new to nWave, clones the repository on a fresh machine with only Python 3.10 installed. When he runs the installation script directly, he gets a cryptic ModuleNotFoundError with no guidance on how to fix it."

---

### 2. User/Persona Identified with Specific Characteristics

| Item | Status | Evidence |
|------|--------|----------|
| Real names used | PASS | Marco, Sofia, Kenji, Alex, Vera |
| Specific roles defined | PASS | New user, returning user, methodical user, Claude Code agent |
| Clear context provided | PASS | Each story has "Who" section with characteristics |

**Personas Defined:**
- Marco: Backend developer, new to nWave, MacBook Pro, Python 3.10
- Sofia: Experienced user, returning after system update, stale environment
- Kenji: Methodical user, wants verification
- Vera: Claude Code orchestrator, needs machine-readable errors
- Alex: Documentation follower, literal instruction follower

---

### 3. At Least 3 Domain Examples with Real Data

| Story | Examples | Status |
|-------|----------|--------|
| US-001 | 3 examples (no pipenv, no venv, successful fix) | PASS |
| US-002 | 2 examples (stale env, fixed env) | PASS |
| US-003 | 3 examples (auto verify, standalone pass, detect missing) | PASS |
| US-004 | 2 examples (Claude Code JSON, terminal human) | PASS |
| US-005 | 2 examples (quick start, prerequisites) | PASS |

**Total:** 12 domain examples with real data (names, commands, expected outputs)

---

### 4. UAT Scenarios in Given/When/Then Format

| Criteria | Count | Status |
|----------|-------|--------|
| Total scenarios defined | 28 | PASS |
| Given/When/Then format | All | PASS |
| Happy path covered | Yes | PASS |
| Edge cases covered | Yes | PASS |
| Error scenarios covered | Yes | PASS |

**Scenario Coverage by Acceptance Criteria:**
- AC-01: 2 scenarios (pre-flight, performance)
- AC-02: 3 scenarios (blocked, no bypass, proceeds)
- AC-03: 2 scenarios (no pipenv, pipenv-only messages)
- AC-04: 2 scenarios (terminal error, missing dep)
- AC-05: 3 scenarios (JSON error, context detection, error codes)
- AC-06: 3 scenarios (all deps, one missing, multiple missing)
- AC-07: 4 scenarios (runs after build, file counts, passes, detects issues)
- AC-08: 4 scenarios (exists, passes, fails, not installed)
- AC-09: 4 scenarios (created, success logged, errors logged, preserved)
- AC-10: 3 scenarios (prerequisites, quick start, no hidden deps)

---

### 5. Acceptance Criteria Derived from UAT

| Item | Status | Evidence |
|------|--------|----------|
| AC trace to UAT scenarios | PASS | Each AC has 2-4 scenarios |
| Checkable outcomes | PASS | Exit codes, messages, file counts specified |
| Measurable criteria | PASS | 2-second performance, file counts, etc. |

---

### 6. Story Right-Sized (1-3 Days, 3-7 Scenarios)

| Story | Estimated Effort | Scenarios | Status |
|-------|-----------------|-----------|--------|
| US-001 | 2 days | 3 UAT + 3 AC scenarios | PASS |
| US-002 | 1 day | 2 UAT + 3 AC scenarios | PASS |
| US-003 | 1 day | 3 UAT + 4 AC scenarios | PASS |
| US-004 | 1 day | 2 UAT + 3 AC scenarios | PASS |
| US-005 | 0.5 day | 2 UAT + 3 AC scenarios | PASS |

**Total Feature Effort:** ~5-6 days (right-sized for single feature)

---

### 7. Technical Notes Identify Constraints

| Constraint | Documented | Location |
|------------|------------|----------|
| Python 3 only (no other runtimes) | PASS | requirements.md C-01 |
| Local environment via pipenv | PASS | requirements.md C-02 |
| Dependencies before installer | PASS | requirements.md C-03 |
| No skip flag | PASS | requirements.md C-04 |
| Standard library only for pre-flight | PASS | requirements.md NFR-02 |
| Cross-platform compatibility | PASS | requirements.md NFR-04 |

---

### 8. Dependencies Resolved or Tracked

| Dependency | Status | Notes |
|------------|--------|-------|
| Existing install_nwave.py | Available | scripts/install/install_nwave.py exists |
| Existing installation-guide.md | Available | docs/installation/installation-guide.md exists |
| Pipfile | Available | Pipfile at repository root |
| Claude Code context detection | DESIGN decision | Method TBD in DESIGN wave |

---

## DoR Gate Status

| Gate | Status |
|------|--------|
| All 8 checklist items | PASS |
| Stakeholder sign-off | Pending Mike's review |
| DESIGN wave ready | YES (after sign-off) |

---

## Handoff Package for DESIGN Wave

### Deliverables

| Artifact | Path | Status |
|----------|------|--------|
| Requirements Specification | `docs/feature/installation-environment-detection/discuss/requirements.md` | Complete |
| User Stories | `docs/feature/installation-environment-detection/discuss/user-stories.md` | Complete |
| Acceptance Criteria | `docs/feature/installation-environment-detection/discuss/acceptance-criteria.md` | Complete |
| DoR Checklist | `docs/feature/installation-environment-detection/discuss/dor-checklist.md` | Complete |

### Key Decisions for DESIGN Wave

1. **Error output mode detection:** Determine how to detect Claude Code vs terminal context
2. **Error code enumeration:** Finalize error codes (ENV_NO_VENV, ENV_NO_PIPENV, DEP_MISSING, BUILD_FAILED, VERIFY_FAILED)
3. **Log file location:** Confirm `~/.nwave/install.log` or alternative
4. **File count expectations:** Determine if counts are hardcoded or read from manifest
5. **Verification script location:** Confirm `scripts/install/verify_nwave.py`

### Constraints Carried Forward

- Pre-flight checks: Python standard library ONLY
- Package manager: pipenv ONLY, no fallbacks
- Virtual environment: HARD BLOCK, no bypass
- Documentation: Bundled in this feature scope

---

## Sign-Off

| Role | Name | Status | Date |
|------|------|--------|------|
| Product Owner | Riley | Complete | 2026-01-29 |
| Stakeholder | Mike | Pending | - |
| Solution Architect | (DESIGN wave) | Not Started | - |

---

## Next Steps

1. Mike reviews and approves DISCUSS artifacts
2. Riley (product-owner) invokes peer review via product-owner-reviewer
3. Upon approval, handoff to solution-architect for DESIGN wave
4. DESIGN wave produces technical architecture and component design
