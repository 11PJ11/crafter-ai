# Architecture Design: modern_CLI_installer

**Epic**: modern_CLI_installer
**Wave**: DESIGN
**Architect**: Morgan (Solution Architect)
**Date**: 2026-02-01
**Status**: DRAFT

---

## 1. Executive Summary

This document defines the system architecture for the modern_CLI_installer epic, encompassing three interconnected journeys:

1. **forge:build-local-candidate** - Build pipx-compatible wheel with semantic versioning
2. **forge:install-local-candidate** - Install and validate local wheel before release
3. **install-nwave** - First-time PyPI installation for end users

The architecture follows **hexagonal architecture** principles with clear port/adapter boundaries, enabling testability and maintainability. Shared infrastructure components (pre-flight checks, doctor health checks, artifact registry) ensure consistency across all journeys.

---

## 2. Architecture Principles

### 2.1 Guiding Principles

| Principle | Application |
|-----------|-------------|
| **Hexagonal Architecture** | Business logic isolated from CLI, file system, and external tools (pipx, git, build) |
| **Single Source of Truth** | Shared artifact registry defines version, paths, and counts |
| **Fail Fast, Recover Gracefully** | Pre-flight checks validate environment; rollback on failure |
| **CI/CD First** | All journeys support non-interactive mode with JSON output and exit codes |
| **Reuse Existing Infrastructure** | Extend existing nWave/ hexagonal structure, install_utils.py, preflight_checker.py |

### 2.2 Quality Attributes

| Attribute | Requirement | Design Decision |
|-----------|-------------|-----------------|
| **Testability** | Unit tests without external dependencies | Port interfaces for all external interactions |
| **Reliability** | Rollback on failure | Backup creation before destructive operations |
| **Usability** | Clear progress feedback | Astro-style TUI with spinners and status tables |
| **Maintainability** | Single change point for shared logic | Shared infrastructure modules |
| **Extensibility** | New journeys without core changes | Journey-agnostic check framework |

---

## 3. System Context

```
+------------------------------------------------------------------+
|                        External Actors                            |
+------------------------------------------------------------------+
|                                                                   |
|   [Developer]          [CI/CD Pipeline]       [End User]          |
|       |                       |                    |              |
|       v                       v                    v              |
|   +--------+             +--------+           +--------+          |
|   | forge: |             | forge: |           |install |          |
|   | build  |------------>|install |           | -nwave |          |
|   | local  |  wheel_path | local  |           |(PyPI)  |          |
|   +--------+             +--------+           +--------+          |
|       |                       |                    |              |
+------------------------------------------------------------------+
                               |
                               v
+------------------------------------------------------------------+
|                     nWave Installer Core                          |
|                                                                   |
|   +-----------------+  +------------------+  +------------------+ |
|   | Pre-flight      |  | Doctor Health    |  | Shared Artifact  | |
|   | Check Framework |  | Check Framework  |  | Registry         | |
|   +-----------------+  +------------------+  +------------------+ |
|                                                                   |
+------------------------------------------------------------------+
                               |
                               v
+------------------------------------------------------------------+
|                     External Dependencies                         |
|                                                                   |
|   [pipx]  [python-build]  [git]  [PyPI]  [File System]           |
|                                                                   |
+------------------------------------------------------------------+
```

---

## 4. Hexagonal Architecture Design

### 4.1 Architecture Overview

```
                            PRIMARY ADAPTERS (Driving)
                    +----------------------------------+
                    |                                  |
        +-----------+   CLI Adapter (forge_cli.py)    +----------+
        |           |   - Interactive mode (TUI)       |          |
        |           |   - CI mode (JSON)               |          |
        |           +----------------------------------+          |
        |                          |                              |
        |                          | Commands                     |
        |                          v                              |
        |           +----------------------------------+          |
        |           |        APPLICATION CORE          |          |
        |           |                                  |          |
        |           |  +-----------+  +-----------+   |          |
        |           |  | Build     |  | Install   |   |          |
        |           |  | Service   |  | Service   |   |          |
        |           |  +-----------+  +-----------+   |          |
        |           |                                  |          |
        |           |  +-----------+  +-----------+   |          |
        |           |  | Doctor    |  | Preflight |   |          |
        |           |  | Service   |  | Service   |   |          |
        |           |  +-----------+  +-----------+   |          |
        |           |                                  |          |
        |           |  +--------------------------+   |          |
        |           |  |    DOMAIN MODEL          |   |          |
        |           |  | Version, CandidateVersion|   |          |
        |           |  | CheckResult, HealthStatus|   |          |
        |           |  +--------------------------+   |          |
        |           +----------------------------------+          |
        |                          |                              |
        |                          | Ports                        |
        |                          v                              |
        |           +----------------------------------+          |
        +-----------+     SECONDARY ADAPTERS (Driven)  +----------+
                    |                                  |
                    |  +---------+ +---------+ +----+ |
                    |  |FileSystem| |Git      | |Pipx| |
                    |  |Adapter   | |Adapter  | |Adpt| |
                    |  +---------+ +---------+ +----+ |
                    |                                  |
                    |  +---------+ +---------+ +----+ |
                    |  |Build    | |Config   | |Env | |
                    |  |Adapter  | |Adapter  | |Adpt| |
                    |  +---------+ +---------+ +----+ |
                    +----------------------------------+
```

### 4.2 Layer Responsibilities

| Layer | Responsibility | Examples |
|-------|----------------|----------|
| **Primary Adapters** | Drive the application from external inputs | CLI, API endpoints (future) |
| **Application Services** | Orchestrate business workflows | BuildService, InstallService, DoctorService, PreflightService |
| **Domain Model** | Core business logic and entities | Version, CandidateVersion, CheckResult, HealthStatus |
| **Ports** | Technology-agnostic interfaces | FileSystemPort, GitPort, PipxPort, ConfigPort |
| **Secondary Adapters** | Implement ports with real technology | FileSystemAdapter, GitAdapter, PipxAdapter |

---

## 5. Component Architecture

### 5.1 Domain Model

#### 5.1.1 Version Domain (Existing - Extend)

```
nWave/core/versioning/domain/
+-- version.py           # Version value object (exists)
+-- rc_version.py        # RCVersion value object (exists)
+-- candidate_version.py # NEW: CandidateVersion for M.m.p-dev-YYYYMMDD-seq
```

**CandidateVersion** (New Domain Object):
- Format: `M.m.p-dev-YYYYMMDD-seq`
- Example: `1.3.0-dev-20260201-001`
- Properties: `base_version`, `date`, `sequence`
- Factory: `CandidateVersion.create(base_version, date, sequence)`
- Parser: `CandidateVersion.parse(version_string)`

#### 5.1.2 Check Domain (New)

```
nWave/core/installer/domain/
+-- check_result.py      # CheckResult value object
+-- health_status.py     # HealthStatus enum (HEALTHY, DEGRADED, UNHEALTHY)
+-- check_severity.py    # CheckSeverity enum (BLOCKING, WARNING)
```

**CheckResult** (Domain Object):
```python
@dataclass(frozen=True)
class CheckResult:
    id: str              # e.g., "python_version"
    name: str            # e.g., "Python Version"
    passed: bool
    severity: CheckSeverity
    message: str
    remediation: Optional[str]
    fixable: bool = False
    fix_command: Optional[str] = None
```

**HealthStatus** (Enum):
```python
class HealthStatus(Enum):
    HEALTHY = "HEALTHY"      # All critical checks pass
    DEGRADED = "DEGRADED"    # Critical pass, some warnings
    UNHEALTHY = "UNHEALTHY"  # One or more critical failures
```

### 5.2 Application Services

#### 5.2.1 Service Inventory

| Service | Journey | Responsibility |
|---------|---------|----------------|
| `PreflightService` | All | Run pre-flight checks, offer fixes |
| `BuildService` | J1 | Build wheel with candidate version |
| `InstallService` | J2, J3 | Install wheel/package via pipx |
| `DoctorService` | J2, J3 | Verify installation health |
| `RollbackService` | J2, J3 | Restore backup on failure |
| `VersionBumpService` | J1 | Analyze commits, determine version bump |

#### 5.2.2 Service Location

```
nWave/core/installer/application/
+-- preflight_service.py
+-- build_service.py         # Extend existing
+-- install_service.py       # Extend existing
+-- doctor_service.py        # NEW
+-- rollback_service.py      # NEW
+-- version_bump_service.py  # NEW
```

### 5.3 Port Interfaces

#### 5.3.1 Port Inventory

```
nWave/core/installer/ports/
+-- file_system_port.py      # File operations
+-- git_port.py              # Git operations (exists, extend)
+-- pipx_port.py             # pipx commands
+-- build_port.py            # python -m build
+-- config_port.py           # Configuration resolution
+-- environment_port.py      # Environment variables
+-- backup_port.py           # Backup/restore operations
```

#### 5.3.2 Key Port Definitions

**PipxPort** (New):
```python
class PipxPort(Protocol):
    def is_available(self) -> bool: ...
    def install(self, package: str, force: bool = False) -> InstallResult: ...
    def uninstall(self, package: str) -> bool: ...
    def list_packages(self) -> List[str]: ...
    def run_in_isolation(self, package: str, args: List[str]) -> RunResult: ...
```

**BackupPort** (New):
```python
class BackupPort(Protocol):
    def create_backup(self, source_path: Path) -> BackupResult: ...
    def restore_backup(self, backup_path: Path, target_path: Path) -> bool: ...
    def cleanup_old_backups(self, keep_count: int = 5) -> int: ...
```

**ConfigPort** (New):
```python
class ConfigPort(Protocol):
    def resolve_install_path(self) -> Path: ...
    def get_env_var(self, name: str) -> Optional[str]: ...
    def load_config(self, path: Path) -> Dict[str, Any]: ...
```

### 5.4 Infrastructure Adapters

```
nWave/infrastructure/installer/
+-- file_system_adapter.py
+-- git_adapter.py           # Extend existing
+-- pipx_adapter.py          # NEW
+-- build_adapter.py         # NEW (wraps python -m build)
+-- config_adapter.py        # NEW
+-- environment_adapter.py   # NEW
+-- backup_adapter.py        # NEW (extend existing BackupManager)
```

### 5.5 CLI Adapters (Primary)

```
nWave/cli/
+-- forge_cli.py             # Extend existing
+-- forge_build_cli.py       # NEW: forge:build-local-candidate
+-- forge_install_cli.py     # Extend existing
+-- install_cli.py           # NEW: install-nwave
```

---

## 6. Shared Infrastructure Components

### 6.1 Pre-flight Check Framework

**Purpose**: Validate environment before executing journey steps.

**Design**:
```
nWave/core/installer/preflight/
+-- check_registry.py        # Registry of all checks
+-- check_executor.py        # Executes checks, collects results
+-- check_fixer.py           # Interactive fix prompts
+-- checks/
    +-- core_checks.py       # python_version, pipx_available, claude_dir_writable
    +-- build_checks.py      # build_package, pyproject_toml, source_directory
    +-- install_checks.py    # wheel_exists, pipx_isolation, install_path_resolved
```

**Check Registry Pattern**:
```python
class CheckRegistry:
    _checks: Dict[str, Check] = {}

    @classmethod
    def register(cls, check: Check) -> None: ...

    @classmethod
    def get_checks_for_journey(cls, journey: str) -> List[Check]: ...
```

**Journey Check Groups** (from pre-flight-checks.yaml):

| Journey | Core Checks | Build Checks | Install Checks |
|---------|-------------|--------------|----------------|
| forge:build-local-candidate | python_version | build_package, pyproject_toml_exists, pyproject_toml_valid, source_directory, dist_directory | - |
| forge:install-local-candidate | python_version, pipx_available, claude_dir_writable | - | wheel_exists, pipx_isolation, install_path_resolved |
| install-nwave | python_version, pipx_available, claude_dir_writable | - | pipx_isolation, install_path_resolved, claude_code_installed |

### 6.2 Doctor Health Check Framework

**Purpose**: Verify installation health after install operations.

**Design**:
```
nWave/core/installer/doctor/
+-- health_checker.py        # Orchestrates health checks
+-- health_reporter.py       # Formats output (TUI, JSON)
+-- checks/
    +-- core_check.py        # Core installation verification
    +-- file_checks.py       # Agent, command, template counts
    +-- config_check.py      # Configuration validation
    +-- permission_check.py  # File permissions
    +-- version_check.py     # Version matching
```

**Health Check Flow**:
```
DoctorService.run()
    |
    v
[core_installation] --> [agent_files] --> [command_files] --> [template_files]
    |                        |                  |                    |
    v                        v                  v                    v
[config_valid] --------> [permissions] ----> [version_match]
    |
    v
HealthStatus (HEALTHY | DEGRADED | UNHEALTHY)
```

### 6.3 Shared Artifact Registry

**Purpose**: Single source of truth for cross-journey artifacts.

**Implementation**: Runtime artifact resolution with validation.

```
nWave/core/installer/artifacts/
+-- artifact_registry.py     # Central registry
+-- artifact_resolver.py     # Resolves artifact values
+-- artifact_validator.py    # Validates consistency
```

**Registry Pattern**:
```python
class ArtifactRegistry:
    def get_version(self) -> str:
        """Read from pyproject.toml [project.version]"""

    def get_candidate_version(self, date: date, sequence: int) -> str:
        """Generate M.m.p-dev-YYYYMMDD-seq"""

    def get_wheel_path(self, candidate_version: str) -> Path:
        """Generate dist/nwave-{candidate_version}-py3-none-any.whl"""

    def get_install_path(self) -> Path:
        """Resolve: env var -> config -> default"""

    def get_counts(self, path: Path) -> ArtifactCounts:
        """Count agents, commands, templates at path"""
```

---

## 7. Journey-Specific Architecture

### 7.1 Journey 1: forge:build-local-candidate

**Entry Point**: `nwave forge:build` or `nwave forge build`

**Flow**:
```
CLI Adapter
    |
    v
PreflightService.run(journey="build")
    |
    +-- [Pre-flight checks: python, build, pyproject, source, dist]
    |
    v
VersionBumpService.analyze_commits()
    |
    +-- [Read pyproject.toml version]
    +-- [Analyze conventional commits since last tag]
    +-- [Determine bump type: MAJOR|MINOR|PATCH]
    +-- [Generate candidate_version: M.m.p-dev-YYYYMMDD-seq]
    |
    v
BuildService.build(candidate_version)
    |
    +-- [Clean dist/ directory]
    +-- [Update pyproject.toml with candidate version]
    +-- [Run python -m build]
    +-- [Validate wheel contents]
    |
    v
BuildResult {wheel_path, candidate_version, counts}
    |
    v
CLI: Display summary + prompt for install
```

### 7.2 Journey 2: forge:install-local-candidate

**Entry Point**: `nwave forge:install` or `nwave forge install`

**Flow**:
```
CLI Adapter
    |
    v
PreflightService.run(journey="install-local")
    |
    +-- [Pre-flight checks: python, pipx, claude_dir, wheel, isolation, path]
    |
    v
ReleaseReadinessService.validate()  # Optional pre-release checks
    |
    +-- [twine check]
    +-- [metadata validation]
    +-- [entry points]
    +-- [CHANGELOG entry]
    |
    v
BackupService.create_backup(install_path)
    |
    +-- [Create timestamped backup: ~/.claude/agents/nw.backup-YYYYMMDD-HHMMSS]
    |
    v
InstallService.install(wheel_path)
    |
    +-- [pipx install --force {wheel_path}]
    +-- [Copy agents to install_path]
    |
    v
DoctorService.run()
    |
    +-- [Verify: core, agents, commands, templates, config, permissions, version]
    |
    v
InstallResult {success, health_status, counts, candidate_version}
    |
    v
CLI: Display doctor report + release report
```

### 7.3 Journey 3: install-nwave (PyPI)

**Entry Point**: `pipx install nwave` (user runs directly)

**Flow**:
```
pipx install nwave
    |
    v
[PyPI download nwave package]
    |
    v
[Post-install hook or separate verify command]
    |
    v
PreflightService.run(journey="install-pypi")
    |
    +-- [Pre-flight checks: python, pipx, claude_dir, isolation, path, claude_code]
    |
    v
InstallService.install_from_pypi()
    |
    +-- [pipx installs package]
    +-- [Copy agents to install_path]
    |
    v
DoctorService.run()
    |
    +-- [Verify: core, agents, commands, templates, config, permissions, version]
    |
    v
WelcomeService.display()
    |
    +-- [Display celebration message]
    +-- [Show /nw:version verification step]
    |
    v
InstallResult {success, health_status, version}
```

---

## 8. Data Flow and Artifact Consistency

### 8.1 Artifact Flow Diagram

```
                    forge:build-local-candidate
                              |
                              | Produces:
                              | - wheel_path
                              | - candidate_version
                              | - agent_count, command_count, template_count
                              v
                    +-------------------+
                    | Build Artifacts   |
                    | (wheel + metadata)|
                    +-------------------+
                              |
                              | Handoff via file system
                              v
                    forge:install-local-candidate
                              |
                              | Consumes:
                              | - wheel_path (must exist)
                              | - candidate_version (for doctor validation)
                              | - counts (for doctor validation)
                              |
                              | Produces:
                              | - install_path (resolved)
                              | - backup_path (for rollback)
                              | - installed_counts (must match build counts)
                              v
                    +-------------------+
                    | Installed System  |
                    | (~/.claude/agents)|
                    +-------------------+
```

### 8.2 Consistency Validation Points

| Checkpoint | Artifacts | Validation |
|------------|-----------|------------|
| Build -> Install | wheel_path | Must exist at path derived from candidate_version |
| Build -> Doctor | counts | Wheel manifest counts must match installed counts |
| Install -> Doctor | candidate_version | Installed version must match expected |
| Install -> Doctor | install_path | Path used for install must match doctor target |

---

## 9. Error Handling Strategy

### 9.1 Layered Error Handling

```
Layer 1: Pre-flight Validation
    |
    +-- Run ALL checks, collect ALL failures
    +-- Display summary with all issues
    +-- Offer interactive fixes for fixable issues
    +-- Block if any BLOCKING severity check fails
    |
    v
Layer 2: Operation Execution
    |
    +-- Create backup before destructive operations
    +-- Execute operation with progress feedback
    +-- Catch and classify errors
    |
    v
Layer 3: Recovery
    |
    +-- On failure: trigger rollback
    +-- Restore from backup
    +-- Report what was recovered
    |
    v
Layer 4: Reporting
    |
    +-- Clear error messages with context
    +-- Actionable remediation steps
    +-- Suggested next command
```

### 9.2 Exit Codes

| Code | Meaning | Example |
|------|---------|---------|
| 0 | Success | Build/install completed |
| 1 | Pre-flight failure | Missing pipx |
| 2 | Build failure | Tests failed |
| 3 | Install failure | pipx install failed |
| 4 | Doctor failure | Health check failed |
| 5 | Rollback failure | Could not restore backup |

---

## 10. CI/CD Support

### 10.1 Non-Interactive Mode

All journeys support `--ci` flag:
- Suppress interactive prompts
- Output JSON for parsing
- Use appropriate exit codes
- No color/emoji output

### 10.2 JSON Output Schema

```json
{
  "success": true,
  "journey": "forge:build-local-candidate",
  "version": "1.3.0-dev-20260201-001",
  "artifacts": {
    "wheel_path": "dist/nwave-1.3.0.dev20260201.1-py3-none-any.whl",
    "agent_count": 47,
    "command_count": 23,
    "template_count": 12
  },
  "checks": [
    {"id": "python_version", "passed": true},
    {"id": "build_package", "passed": true}
  ],
  "duration_ms": 4523
}
```

---

## 11. Technology Decisions

### 11.1 Technology Stack

| Component | Technology | Rationale |
|-----------|------------|-----------|
| **Package Manager** | pipx | Isolated Python app installation |
| **Build Tool** | python-build | PEP 517 compliant wheel building |
| **Version Format** | PEP 440 | Standard Python versioning |
| **CLI Framework** | Click (existing) | Already used in nWave |
| **TUI Components** | Rich (existing) | Already used for formatting |
| **Configuration** | YAML/TOML | Human-readable, well-supported |

### 11.2 Open Source Dependencies

| Dependency | License | Purpose |
|------------|---------|---------|
| click | BSD-3 | CLI framework |
| rich | MIT | TUI formatting |
| PyYAML | MIT | YAML parsing |
| tomllib (stdlib) | PSF | TOML parsing |
| build | MIT | Wheel building |
| twine | Apache 2.0 | Package validation |

---

## 12. Integration with Existing Code

### 12.1 Reuse Strategy

| Existing Component | Reuse Strategy |
|-------------------|----------------|
| `scripts/install/install_utils.py` | Extract `BackupManager`, `PathUtils`, `VersionUtils` into nWave infrastructure |
| `scripts/install/preflight_checker.py` | Refactor `CheckResult` pattern into domain; extend check types |
| `nWave/core/versioning/` | Extend with `CandidateVersion`; reuse `Version`, `RCVersion` |
| `nWave/infrastructure/backup_manager.py` | Use as base for `BackupAdapter` |
| `nWave/cli/forge_cli.py` | Extend with build/install subcommands |

### 12.2 Migration Path

1. **Phase 1**: Create new domain objects in `nWave/core/installer/domain/`
2. **Phase 2**: Create ports in `nWave/core/installer/ports/`
3. **Phase 3**: Create services in `nWave/core/installer/application/`
4. **Phase 4**: Create adapters in `nWave/infrastructure/installer/`
5. **Phase 5**: Create CLI adapters, wire up DI
6. **Phase 6**: Deprecate scripts/install/ (keep for reference)

---

## 13. Security Considerations

### 13.1 Security Controls

| Concern | Control |
|---------|---------|
| **Wheel integrity** | Validate wheel checksum before install |
| **Path traversal** | Validate install_path is within expected boundaries |
| **Backup permissions** | Backup directory inherits user permissions |
| **Environment variables** | Sanitize NWAVE_INSTALL_PATH input |
| **No secrets in logs** | Exclude credentials from verbose output |

### 13.2 Rollback Security

- Backups are local only (user home directory)
- No external upload of backup data
- Old backups cleaned up after configurable retention period

---

## 14. Acceptance Criteria for Architecture

| ID | Criterion | Validation |
|----|-----------|------------|
| AC-1 | Hexagonal architecture with clear port/adapter boundaries | Code review of package structure |
| AC-2 | All external dependencies behind ports | No direct imports of pipx/git/build in services |
| AC-3 | Shared infrastructure reused across journeys | Single PreflightService, DoctorService implementation |
| AC-4 | Artifact consistency validation at checkpoints | Unit tests for artifact registry |
| AC-5 | CI mode with JSON output and exit codes | Integration tests for --ci flag |
| AC-6 | Rollback on failure with backup restoration | Integration tests for failure scenarios |

---

## 15. Next Steps

1. **DISTILL Wave**: Create acceptance tests based on this architecture
2. **Component Boundaries**: Define module interfaces in detail
3. **Sequence Diagrams**: Document interaction flows for each journey
4. **ADRs**: Document key architectural decisions

---

## Appendix A: Package Structure

```
nWave/
+-- core/
|   +-- installer/
|   |   +-- domain/
|   |   |   +-- __init__.py
|   |   |   +-- candidate_version.py
|   |   |   +-- check_result.py
|   |   |   +-- health_status.py
|   |   |   +-- check_severity.py
|   |   +-- application/
|   |   |   +-- __init__.py
|   |   |   +-- preflight_service.py
|   |   |   +-- build_service.py
|   |   |   +-- install_service.py
|   |   |   +-- doctor_service.py
|   |   |   +-- rollback_service.py
|   |   |   +-- version_bump_service.py
|   |   +-- ports/
|   |   |   +-- __init__.py
|   |   |   +-- file_system_port.py
|   |   |   +-- git_port.py
|   |   |   +-- pipx_port.py
|   |   |   +-- build_port.py
|   |   |   +-- config_port.py
|   |   |   +-- backup_port.py
|   |   +-- preflight/
|   |   |   +-- check_registry.py
|   |   |   +-- check_executor.py
|   |   |   +-- checks/
|   |   +-- doctor/
|   |       +-- health_checker.py
|   |       +-- health_reporter.py
|   |       +-- checks/
|   +-- versioning/           # Existing, extend with CandidateVersion
+-- infrastructure/
|   +-- installer/
|       +-- __init__.py
|       +-- file_system_adapter.py
|       +-- git_adapter.py
|       +-- pipx_adapter.py
|       +-- build_adapter.py
|       +-- config_adapter.py
|       +-- backup_adapter.py
+-- cli/
    +-- forge_cli.py          # Extend
    +-- forge_build_cli.py    # New
    +-- forge_install_cli.py  # Extend
    +-- install_cli.py        # New
```

---

## Appendix B: References

- [User Stories](/docs/features/modern-cli-installer/01-discuss/user-stories.md)
- [UX Journey: forge:build-local](/docs/ux/modern-cli-installer/journey-forge-build-local.yaml)
- [UX Journey: forge:install-local-candidate](/docs/ux/modern-cli-installer/journey-forge-install-local-candidate.yaml)
- [UX Journey: install-nwave](/docs/ux/modern-cli-installer/journey-install-nwave.yaml)
- [Shared Artifacts Registry](/docs/ux/modern-cli-installer/shared-artifacts-registry-installer.md)
- [Pre-flight Checks Schema](/docs/ux/modern-cli-installer/shared/pre-flight-checks.yaml)
- [Doctor Health Check Schema](/docs/ux/modern-cli-installer/shared/doctor-health-check.yaml)
