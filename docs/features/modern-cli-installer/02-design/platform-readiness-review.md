# Platform Readiness Review: modern-cli-installer Epic

**Reviewer**: Apex (Platform Architect)
**Date**: 2026-02-01
**Epic**: modern_CLI_installer
**Status**: TECHNICAL READINESS ASSESSMENT

---

## 1. Executive Summary

### Recommendation: CONDITIONAL GO for DEVELOP

The modern-cli-installer epic has strong UX design, comprehensive architecture documentation, and well-defined acceptance tests. However, **critical platform infrastructure gaps must be addressed** before DEVELOP can proceed safely.

| Area | Status | Score |
|------|--------|-------|
| CI/CD Pipeline Design | PARTIAL | 60% |
| Deployment Strategy | MISSING | 20% |
| Infrastructure Requirements | PARTIAL | 50% |
| Observability | UNDERSPECIFIED | 30% |
| UX-Technical Alignment | STRONG | 85% |

**Blocking Issues (must resolve before DEVELOP):**
1. No pyproject.toml exists in the repository (fundamental blocker)
2. No PyPI publishing workflow defined
3. No wheel build validation in current CI/CD
4. Missing secrets management strategy for PyPI credentials

**Non-Blocking Issues (can resolve during DEVELOP):**
1. Doctor health check telemetry not defined
2. Cross-platform testing for pipx installation not validated
3. Rollback mechanism not implemented in CI/CD

---

## 2. CI/CD Pipeline Assessment

### 2.1 Current State Analysis

The existing `.github/workflows/ci-cd.yml` provides a solid foundation with:

**Strengths:**
- 6-stage pipeline architecture (Fast Checks -> Framework Validation -> Tests -> Agent Sync -> Build -> Release)
- Cross-platform testing matrix (Ubuntu, Windows, macOS x Python 3.11, 3.12)
- Intelligent caching and concurrency management
- Slack notifications for RED/GREEN transitions
- Conventional commit validation

**Gaps for modern-cli-installer:**

| UX Journey Requirement | Current CI/CD Support | Gap |
|------------------------|----------------------|-----|
| `forge build --local` | Partial (has IDE bundle build) | No wheel building |
| `forge install --local-candidate` | MISSING | No local install validation |
| `pipx install nwave` | MISSING | No PyPI workflow |
| Semver from commits | MISSING | No version bump automation |
| Release candidate flow | MISSING | No RC tagging strategy |

### 2.2 Required Pipeline Modifications

#### Stage 5 (Build) Needs Enhancement:

```yaml
# CURRENT: Builds IDE bundle only
- name: Build IDE bundle
  run: PYTHONPATH=tools pipenv run python3 tools/core/build_ide_bundle.py

# REQUIRED: Add wheel building
- name: Build Python wheel
  run: |
    pip install build twine
    python -m build
    twine check dist/*.whl

- name: Validate wheel contents
  run: |
    # Validate agent/command/template counts match manifest
    python -c "
    import zipfile
    import sys
    whl = list(Path('dist').glob('*.whl'))[0]
    # ... validation logic
    "
```

#### New Stage Required: PyPI Publishing

```yaml
publish-pypi:
  name: "Publish to PyPI"
  needs: [release]
  if: startsWith(github.ref, 'refs/tags/v') && !contains(github.ref, '-dev')
  runs-on: ubuntu-latest
  steps:
    - name: Download wheel artifact
      uses: actions/download-artifact@v4
      with:
        name: release-packages

    - name: Publish to PyPI
      uses: pypa/gh-action-pypi-publish@release/v1
      with:
        password: ${{ secrets.PYPI_API_TOKEN }}
```

### 2.3 Version Management Strategy Assessment

**Architecture specifies:** `M.m.p-dev-YYYYMMDD-seq` format for candidates

**Gap:** No automation exists for:
- Analyzing conventional commits to determine bump type (MAJOR/MINOR/PATCH)
- Generating candidate versions with daily sequence
- Stripping `-dev` suffix for final release

**Required Implementation:**
```python
# scripts/version/calculate_version.py
# Must be created to support:
# 1. Read current version from pyproject.toml
# 2. Analyze git log for conventional commits
# 3. Calculate bump type
# 4. Generate candidate version string
```

### 2.4 Missing: pyproject.toml

**CRITICAL BLOCKER**: The repository has no `pyproject.toml`. The entire build journey depends on:
- `[project.version]` for base version
- `[project.scripts]` for `nw` CLI entry point
- `[build-system]` for wheel building
- Package metadata for PyPI

**Action Required:** Create `pyproject.toml` with:
```toml
[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "nwave"
version = "0.0.0"  # Managed by release automation
description = "nWave Framework for Claude Code"
requires-python = ">=3.10"
dependencies = ["click", "rich", "pyyaml"]

[project.scripts]
nw = "nwave.cli:main"
```

---

## 3. Deployment & Distribution Strategy Validation

### 3.1 Distribution Path Analysis

| Path | UX Journey | Technical Requirement | Status |
|------|------------|----------------------|--------|
| Local wheel | J1: build-local | `python -m build` | READY (pending pyproject.toml) |
| pipx from local | J2: install-local-candidate | `pipx install ./dist/*.whl --force` | UNTESTED |
| pipx from PyPI | J3: install-nwave | `pipx install nwave` | NOT CONFIGURED |
| TestPyPI staging | Pre-release validation | `twine upload --repository testpypi` | NOT CONFIGURED |

### 3.2 PyPI Strategy Gaps

**Missing Configuration:**
1. No PyPI account/project setup documented
2. No TestPyPI workflow for pre-release validation
3. No PYPI_API_TOKEN secret configured in GitHub
4. No trusted publisher (OIDC) setup for secure publishing

**Recommended PyPI Strategy: PR-Level TestPyPI Validation**

This enhanced strategy validates Luna's Journey 3 (install from remote) **in every PR**, not post-merge:

```
Feature Branch
      │
      ▼
   PR Opens
      │
      ▼
CI builds wheel (version: M.m.p-dev-YYYYMMDD-seq)
      │
      ▼
Publish to TestPyPI ◄─── PR-level publishing
      │
      ▼
E2E Test: pipx install -i test.pypi.org nwave==M.m.p-dev-YYYYMMDD-seq
      │
      ▼
Validate Journey 3 UX (full remote install flow)
      │
      ▼
   PR Green ✓
      │
      ▼
   Merge to main
      │
      ▼
Tag vM.m.p (release)
      │
      ▼
Publish to PyPI (production)
```

**Key Benefits:**
- Journey 3 UX validated before merge, not after
- Each PR gets unique TestPyPI version for isolation
- CI catches remote install issues, not first users
- Merge confidence significantly higher
- Rollback scenarios become rare events

**Version Format Alignment:**
- PR builds: `M.m.p-dev-YYYYMMDD-seq` (TestPyPI)
- Release builds: `M.m.p` (Production PyPI)
- Luna's candidate format enables this pattern perfectly

### 3.3 pipx Installation Path Validation

**Architecture specifies:**
- Default: `~/.claude/agents/nw/`
- Override: `NWAVE_INSTALL_PATH` environment variable
- Config: `config/installer.yaml`

**Gap Analysis:**

| Requirement | Implementation Status |
|-------------|----------------------|
| pipx isolated environment | Conceptually correct |
| Agent file copy to ~/.claude | NOT IMPLEMENTED in package |
| Post-install hook | NOT POSSIBLE with pipx (no hooks) |
| Entry point `nw` | Requires pyproject.toml |

**Critical Issue:** pipx installs to `~/.local/pipx/venvs/nwave/`, NOT to `~/.claude/agents/nw/`. The architecture assumes agent files will be in `~/.claude`, but pipx does not support custom install paths.

**Resolution (ADR-001 Decision):**
- **Primary**: Automatic setup triggered by pipx install (follows Luna's seamless UX)
- **Secondary**: Explicit `nw setup` command for reinstall/repair scenarios
- **Rationale**: Seamless first experience for new users, explicit repair path for troubleshooting

### 3.4 Cross-Platform Considerations

**UX Journeys specify:**
- Unix: `Cmd+Q to restart Claude` (macOS)
- Windows: Not explicitly addressed

**Gap:** The architecture does not address:
- Windows path handling (`~/.claude` vs `%USERPROFILE%\.claude`)
- Windows Claude Code restart mechanism
- PowerShell vs Bash command differences

**Current CI/CD Coverage:** Cross-platform tests exist (Ubuntu, Windows, macOS) but do not test:
- pipx installation flow
- Agent file copy to platform-specific paths
- Doctor health check on Windows

---

## 4. Infrastructure Gaps

### 4.1 What Needs to Be Created

| Component | Priority | Complexity | Blocks |
|-----------|----------|------------|--------|
| `pyproject.toml` | P0-CRITICAL | Low | Everything |
| Version calculation script | P0 | Medium | Build journey |
| Wheel validation script | P0 | Medium | Build journey |
| PyPI publishing workflow | P0 | Medium | Release journey |
| Agent setup command (`nw setup`) | P0 | High | Install journeys |
| Doctor CLI command | P1 | Medium | Verification |
| Rollback infrastructure | P1 | High | Error recovery |
| TestPyPI workflow | P1 | Low | Release validation |

### 4.2 GitHub Actions Workflow Design

**Required New Workflows:**

1. **build-wheel.yml** (reusable)
```yaml
# Builds wheel and validates contents
# Outputs: wheel_path, version, agent_count, command_count, template_count
```

2. **publish-pypi.yml** (reusable)
```yaml
# Publishes to PyPI or TestPyPI
# Inputs: target (pypi|testpypi), version
# Requires: PYPI_API_TOKEN secret
```

3. **validate-install.yml** (reusable)
```yaml
# Validates pipx installation on matrix of OS/Python
# Runs: pipx install, nw doctor, nw --version
```

### 4.3 Secrets Management for PyPI

**Required Secrets:**
| Secret Name | Purpose | Setup Required |
|-------------|---------|----------------|
| `PYPI_API_TOKEN` | Production PyPI upload | Create API token on pypi.org |
| `TEST_PYPI_API_TOKEN` | TestPyPI upload | Create API token on test.pypi.org |

**Recommended:** Use OIDC trusted publisher instead of API tokens for better security.

### 4.4 Environment Isolation

**Current State:** Pipenv used for development
**Required:** Additional isolation for testing install flows

```yaml
# Test matrix should include:
# 1. Clean virtual environment (no nwave installed)
# 2. Fresh pipx installation
# 3. Upgrade from previous version
# 4. Cross-platform (Ubuntu, macOS, Windows)
```

---

## 5. Observability & User Feedback

### 5.1 How Do We Know Installs Succeeded?

**Architecture specifies:**
- Doctor health check with HEALTHY/DEGRADED/UNHEALTHY status
- Exit codes (0=success, 1-5=various failures)
- JSON output for CI/CD parsing

**Gap:** No observability for:
- Installation success rates across user base
- Common failure patterns
- Time-to-first-success metrics

### 5.2 Error Reporting Mechanisms

**Defined in Architecture:**
- Structured error messages with `[x]` icons
- Remediation suggestions
- Fix commands for fixable issues

**Missing:**
- Error aggregation/reporting to maintainers
- Opt-in telemetry for failure patterns
- Sentry/error tracking integration

### 5.3 Health Checks (Doctor Command)

**Architecture Design:** Comprehensive (7 checks)
1. Core installation
2. Agent files
3. Command files
4. Template files
5. Config valid
6. Permissions
7. Version match

**Implementation Gap:** Doctor command does not exist yet. Must be implemented as CLI command.

```python
# nwave/cli/doctor.py
@click.command()
def doctor():
    """Run health checks on nWave installation."""
    # Implementation required
```

### 5.4 Telemetry Considerations

**Recommendation:** Implement opt-in telemetry for:
- Installation success/failure
- Doctor health status on first run
- Version information for support

**Privacy-First Approach:**
```python
# Only send if user opts in via NWAVE_TELEMETRY=1
# Data: {version, os, python_version, health_status, timestamp}
# No PII, no usage tracking, no agent content
```

---

## 6. UX-Technical Alignment Score

### 6.1 Emotional Arc Support

| UX Moment | Technical Support | Alignment |
|-----------|-------------------|-----------|
| **Pre-flight validation** | Architecture defines all checks | STRONG |
| **Progress feedback** | TUI spinners, progress bars | STRONG |
| **Success celebration** | ASCII art, welcome message | STRONG |
| **Error recovery** | Rollback, fix prompts | PARTIAL (rollback not implemented) |
| **Doctor confidence** | Health check framework | STRONG |

### 6.2 Response Time Analysis

| UX Step | Expected Duration | Technical Constraint |
|---------|-------------------|---------------------|
| Pre-flight checks | < 2 seconds | Local checks only |
| Build wheel | < 30 seconds | Depends on source size |
| pipx install | < 60 seconds | Network + disk I/O |
| Doctor verification | < 5 seconds | File counting |

**Assessment:** Response times achievable with current design.

### 6.3 Error Recovery Flow Analysis

**UX defines comprehensive error paths. Technical implementation status:**

| Error Path | UX Defined | Technical Support |
|------------|------------|-------------------|
| Missing Python | Yes | Pre-flight check |
| Missing pipx | Yes | Pre-flight check |
| Missing build package | Yes | Fixable check with auto-install |
| Missing wheel (chain to build) | Yes | NEEDS IMPLEMENTATION |
| Version mismatch | Yes | Doctor check |
| Permission denied | Yes | Pre-flight check |
| Rollback on failure | Yes | NEEDS IMPLEMENTATION |

### 6.4 The Doctor Command Capability

**UX Journey Step 4 (J2) and Step 5 (J3) depend on doctor:**

```
Doctor Verification Flow:
  1. Check core installation exists
  2. Count agent files (must match wheel)
  3. Count command files (must match wheel)
  4. Count template files (must match wheel)
  5. Validate config file parses
  6. Check file permissions
  7. Verify nw --version matches expected

Output:
  - Table format with [check] or [x] icons
  - Status: HEALTHY | DEGRADED | UNHEALTHY
  - JSON option for CI/CD
```

**Implementation Required:** Full doctor command implementation.

---

## 7. Risks & Mitigations

### 7.1 Blocking Risks (Must Resolve Before DEVELOP)

| Risk | Impact | Mitigation | Owner |
|------|--------|------------|-------|
| No pyproject.toml | Cannot build wheel | Create pyproject.toml immediately | DEVELOP |
| No PyPI credentials | Cannot publish | Configure PYPI_API_TOKEN secret | DevOps |
| pipx doesn't copy to ~/.claude | Install journey broken | Implement `nw setup` post-install | DEVELOP |
| No version calculation | Manual version management | Implement version script | DEVELOP |

### 7.2 Non-Blocking Risks

| Risk | Impact | Mitigation | Priority |
|------|--------|------------|----------|
| No rollback in CI | Manual recovery on failure | Implement rollback command | P1 |
| Windows path handling | Cross-platform issues | Add platform detection | P1 |
| No TestPyPI workflow | Risky production releases | Add staging environment | P1 |
| No telemetry | Blind to user issues | Consider opt-in telemetry | P2 |

### 7.3 Technical Debt Assessment

**Pre-existing debt that affects this epic:**
1. Scripts in `scripts/install/` should be migrated to hexagonal architecture as designed
2. Current `install_utils.py` and `preflight_checker.py` need refactoring
3. No existing CLI infrastructure (click commands not set up)

---

## 8. Recommendations

### 8.1 Prioritized Action Items

**P0 - BLOCKING (Before DEVELOP starts):**

1. **Create pyproject.toml** - Without this, nothing works
   - Define package metadata
   - Configure entry points (`nw` CLI)
   - Set up build system (setuptools)
   - Declare dependencies

2. **Configure PyPI secrets** - Required for release flow
   - Create PyPI account and project
   - Generate API token
   - Add `PYPI_API_TOKEN` to GitHub secrets

3. **Implement `nw setup` command** - Critical for agent installation
   - Post-install command to copy agents to ~/.claude
   - First-run detection in CLI
   - Path resolution (env var > config > default)

4. **Add wheel build to CI/CD** - Required for validation
   - Build wheel in Stage 5
   - Validate wheel contents
   - Upload as artifact

**P1 - HIGH (During DEVELOP Sprint 1):**

5. **Implement doctor command** - UX journeys depend on this
6. **Add version calculation script** - Conventional commit analysis
7. **Create PyPI publishing workflow** - Release automation
8. **Implement rollback mechanism** - Error recovery

**P1 - HIGH (Updated - PR-Level TestPyPI now critical path):**

9. **Add TestPyPI PR workflow** - Enables Journey 3 validation in PR (elevated from P2)
10. **Add E2E remote install test** - Validates `pipx install -i test.pypi.org` in CI

**P2 - MEDIUM (During DEVELOP Sprint 2+):**

11. Implement cross-platform path handling
12. Consider opt-in telemetry

### 8.2 Sprint 0 Checklist

Before DEVELOP Sprint 1 can begin, complete:

- [ ] `pyproject.toml` created and committed (single source of truth for version)
- [ ] `PYPI_API_TOKEN` and `TEST_PYPI_API_TOKEN` secrets configured in GitHub
- [ ] Basic `nw` CLI entry point working
- [ ] Wheel builds successfully with `python -m build`
- [ ] `twine check` passes on built wheel
- [ ] TestPyPI publishing workflow added to PR pipeline
- [ ] Version sync quality gate added (agents must match pyproject.toml version)

### 8.3 Architecture Decision Records (DECIDED)

| ADR | Topic | Decision | Rationale |
|-----|-------|----------|-----------|
| ADR-001 | Post-install agent setup | **Automatic setup on pipx install + explicit `nw setup` command** | Seamless UX per Luna's design; explicit repair path for troubleshooting |
| ADR-002 | Version management | **Phased: pyproject.toml as single source → quality gates → semver automation + force override** | Prevents agent spec drift; centralized truth; escape hatch for edge cases |
| ADR-003 | PyPI publishing | **PR-level TestPyPI validation → merge → production PyPI** | Validates Journey 3 UX in PR; CI catches issues before users; high merge confidence |
| ADR-004 | Telemetry | Deferred to P2 | Focus on core functionality first |

**ADR-003 Enhancement (PR-Level TestPyPI):**
This decision enables a powerful validation pattern:
- Every PR publishes a dev version to TestPyPI
- E2E tests validate `pipx install -i test.pypi.org nwave==M.m.p-dev-YYYYMMDD-seq`
- Luna's Journey 3 (install from remote) is validated before merge, not after
- Unique version per PR ensures test isolation

---

## 9. Conclusion

The modern-cli-installer epic has **excellent UX design** and **comprehensive architecture documentation**. The acceptance tests provide clear validation criteria. However, **foundational platform infrastructure is missing**.

**The most critical gap is the absence of `pyproject.toml`** - this is a fundamental Python packaging requirement that blocks all three user journeys.

Once the P0 blocking items are addressed (estimated 1-2 days of focused work), the epic is ready for DEVELOP. The hexagonal architecture and port/adapter design will enable clean implementation and testability.

**Final Assessment:**

| Criterion | Status |
|-----------|--------|
| UX-to-Technical Handoff | COMPLETE |
| Architecture Documentation | COMPLETE |
| Acceptance Tests | COMPLETE |
| CI/CD Infrastructure | NEEDS WORK |
| Deployment Infrastructure | NEEDS WORK |
| **Overall Readiness** | CONDITIONAL GO |

---

## Appendix A: File Structure Validation

**Expected after DEVELOP:**
```
nWave/
  core/
    installer/
      domain/          # CandidateVersion, CheckResult, HealthStatus
      application/     # BuildService, InstallService, DoctorService
      ports/           # PipxPort, BuildPort, ConfigPort
      preflight/       # CheckRegistry, CheckExecutor
      doctor/          # HealthChecker, HealthReporter
  infrastructure/
    installer/         # Adapters for ports
  cli/
    forge_cli.py       # forge build, forge install
    install_cli.py     # nw setup
    doctor_cli.py      # nw doctor

pyproject.toml         # Package configuration (MUST CREATE)
```

## Appendix B: CI/CD Workflow Modification Summary

**ci-cd.yml changes required:**

1. Add `python -m build` to Stage 5 (Build)
2. Add `twine check dist/*.whl` validation
3. Add wheel artifact upload
4. Create new Stage 7: PyPI Publishing (tag-triggered)
5. Add installation validation job in test matrix

---

**Document Version**: 1.0
**Reviewed By**: Apex (Platform Architect)
**Next Review**: After P0 items completed
