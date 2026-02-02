# Component Boundaries: modern_CLI_installer

**Epic**: modern_CLI_installer
**Wave**: DESIGN
**Architect**: Morgan (Solution Architect)
**Date**: 2026-02-01
**Status**: DRAFT

---

## 1. Overview

This document defines component boundaries, interface contracts, and dependency rules for the modern_CLI_installer epic. Components are organized following hexagonal architecture principles with clear separation between domain, application, and infrastructure layers.

---

## 2. Component Dependency Rules

### 2.1 Dependency Direction

```
                    ALLOWED DEPENDENCIES

CLI Adapters -----> Application Services -----> Domain Model
      |                    |
      |                    +-----> Ports (Interfaces)
      |                                  ^
      v                                  |
Infrastructure Adapters ------------------+
```

### 2.2 Forbidden Dependencies

| From | To | Reason |
|------|-----|--------|
| Domain | Application | Domain is pure, no orchestration knowledge |
| Domain | Infrastructure | Domain has no technology dependencies |
| Application | Infrastructure | Application depends on ports, not adapters |
| Ports | Adapters | Ports define contracts, not implementations |

---

## 3. Domain Layer Components

### 3.1 CandidateVersion

**Location**: `nWave/core/installer/domain/candidate_version.py`

**Responsibility**: Represent and manipulate candidate version strings in PEP 440 format.

**Interface**:
```python
@dataclass(frozen=True)
class CandidateVersion:
    """
    Candidate version in format: M.m.p-dev-YYYYMMDD-seq

    Attributes:
        base_version: Semantic version (e.g., "1.3.0")
        date: Build date
        sequence: Daily build sequence (1, 2, 3...)
    """
    base_version: str
    date: date
    sequence: int

    @classmethod
    def create(cls, base_version: str, build_date: date, sequence: int) -> "CandidateVersion":
        """Factory method with validation."""

    @classmethod
    def parse(cls, version_string: str) -> "CandidateVersion":
        """Parse from string like '1.3.0-dev-20260201-001'."""

    def to_pep440(self) -> str:
        """Return PEP 440 compliant string: '1.3.0.dev20260201.1'"""

    def to_wheel_filename(self, package_name: str = "nwave") -> str:
        """Return wheel filename: 'nwave-1.3.0.dev20260201.1-py3-none-any.whl'"""

    def __str__(self) -> str:
        """Return display string: '1.3.0-dev-20260201-001'"""
```

**Dependencies**: None (pure domain object)

**Test Strategy**: Unit tests with no mocking required

---

### 3.2 CheckResult

**Location**: `nWave/core/installer/domain/check_result.py`

**Responsibility**: Represent the result of a single pre-flight or health check.

**Interface**:
```python
@dataclass(frozen=True)
class CheckResult:
    """
    Result of a single check operation.

    Attributes:
        id: Unique check identifier (e.g., "python_version")
        name: Human-readable name (e.g., "Python Version")
        passed: Whether the check passed
        severity: BLOCKING or WARNING
        message: Result message
        remediation: Fix instructions (None if passed)
        fixable: Whether automatic fix is available
        fix_command: Command to run for fix (if fixable)
    """
    id: str
    name: str
    passed: bool
    severity: CheckSeverity
    message: str
    remediation: Optional[str] = None
    fixable: bool = False
    fix_command: Optional[str] = None

    def is_blocking(self) -> bool:
        """Return True if failed and severity is BLOCKING."""

    @classmethod
    def success(cls, id: str, name: str, message: str) -> "CheckResult":
        """Factory for successful check."""

    @classmethod
    def failure(cls, id: str, name: str, message: str,
                severity: CheckSeverity, remediation: str,
                fixable: bool = False, fix_command: Optional[str] = None) -> "CheckResult":
        """Factory for failed check."""
```

**Dependencies**: `CheckSeverity` enum

---

### 3.3 HealthStatus

**Location**: `nWave/core/installer/domain/health_status.py`

**Responsibility**: Represent overall health state of an installation.

**Interface**:
```python
class HealthStatus(Enum):
    """
    Installation health status levels.

    HEALTHY: All critical checks pass
    DEGRADED: Critical pass, some warnings
    UNHEALTHY: One or more critical failures
    """
    HEALTHY = "HEALTHY"
    DEGRADED = "DEGRADED"
    UNHEALTHY = "UNHEALTHY"

    @classmethod
    def from_results(cls, results: List[CheckResult]) -> "HealthStatus":
        """Determine status from list of check results."""

@dataclass(frozen=True)
class HealthReport:
    """
    Complete health check report.

    Attributes:
        status: Overall health status
        checks: List of individual check results
        version: Installed version
        install_path: Installation path
        counts: Agent, command, template counts
    """
    status: HealthStatus
    checks: List[CheckResult]
    version: str
    install_path: Path
    counts: ArtifactCounts

    def to_json(self) -> str:
        """Serialize to JSON for CI mode."""
```

---

### 3.4 ArtifactCounts

**Location**: `nWave/core/installer/domain/artifact_counts.py`

**Responsibility**: Track counts of installed artifacts.

**Interface**:
```python
@dataclass(frozen=True)
class ArtifactCounts:
    """
    Counts of installed artifacts for validation.

    Attributes:
        agents: Number of agent files
        commands: Number of command files
        templates: Number of template files
    """
    agents: int
    commands: int
    templates: int

    def matches(self, other: "ArtifactCounts") -> bool:
        """Check if counts match (for build->install validation)."""

    def to_dict(self) -> Dict[str, int]:
        """Serialize to dictionary."""
```

---

## 4. Application Layer Components

### 4.1 PreflightService

**Location**: `nWave/core/installer/application/preflight_service.py`

**Responsibility**: Execute pre-flight checks for a journey, offer fixes, determine proceed/block.

**Interface**:
```python
class PreflightService:
    """
    Orchestrates pre-flight validation for installation journeys.

    Runs checks appropriate for the specified journey, collects results,
    and optionally offers interactive fixes for fixable issues.
    """

    def __init__(
        self,
        check_registry: CheckRegistryPort,
        check_executor: CheckExecutorPort,
        user_prompt: UserPromptPort,
    ) -> None:
        """
        Args:
            check_registry: Registry of available checks
            check_executor: Executes checks and returns results
            user_prompt: Prompts user for fix confirmations
        """

    def run(
        self,
        journey: str,
        interactive: bool = True,
    ) -> PreflightResult:
        """
        Run pre-flight checks for the specified journey.

        Args:
            journey: Journey identifier (e.g., "build", "install-local", "install-pypi")
            interactive: If True, prompt user to fix fixable issues

        Returns:
            PreflightResult with check results and proceed/block decision
        """

    def can_proceed(self, result: PreflightResult) -> bool:
        """Return True if no blocking failures."""

@dataclass(frozen=True)
class PreflightResult:
    """Result of pre-flight validation."""
    checks: List[CheckResult]
    can_proceed: bool
    fixes_applied: List[str]
```

**Depends On (Ports)**:
- `CheckRegistryPort` - Get checks for journey
- `CheckExecutorPort` - Execute individual checks
- `UserPromptPort` - Prompt for fix confirmation

---

### 4.2 BuildService

**Location**: `nWave/core/installer/application/build_service.py`

**Responsibility**: Orchestrate wheel building workflow.

**Interface**:
```python
class BuildService:
    """
    Orchestrates build workflow for forge:build-local-candidate.

    Workflow:
    1. Clean dist/ directory
    2. Read base version from pyproject.toml
    3. Analyze commits for version bump
    4. Generate candidate version
    5. Build wheel
    6. Validate wheel contents
    """

    def __init__(
        self,
        file_system: FileSystemPort,
        git: GitPort,
        build_tool: BuildPort,
        date_provider: DateProviderPort,
    ) -> None:
        """Initialize with required ports."""

    def build(self, force_version: Optional[str] = None) -> BuildResult:
        """
        Execute the build workflow.

        Args:
            force_version: If provided, skip version analysis and use this version

        Returns:
            BuildResult with wheel path and metadata
        """

@dataclass(frozen=True)
class BuildResult:
    """Result of build operation."""
    success: bool
    candidate_version: Optional[CandidateVersion]
    wheel_path: Optional[Path]
    counts: Optional[ArtifactCounts]
    error_message: Optional[str] = None
```

**Depends On (Ports)**:
- `FileSystemPort` - File operations
- `GitPort` - Branch, commit analysis
- `BuildPort` - python -m build
- `DateProviderPort` - Current date

---

### 4.3 InstallService

**Location**: `nWave/core/installer/application/install_service.py`

**Responsibility**: Orchestrate installation workflow (local wheel or PyPI).

**Interface**:
```python
class InstallService:
    """
    Orchestrates installation workflow.

    Supports two modes:
    1. Local wheel installation (forge:install-local-candidate)
    2. PyPI installation (install-nwave)
    """

    def __init__(
        self,
        pipx: PipxPort,
        file_system: FileSystemPort,
        backup: BackupPort,
        config: ConfigPort,
    ) -> None:
        """Initialize with required ports."""

    def install_local(self, wheel_path: Path) -> InstallResult:
        """
        Install from local wheel file.

        Args:
            wheel_path: Path to .whl file

        Returns:
            InstallResult with installation outcome
        """

    def install_from_pypi(self, package: str = "nwave") -> InstallResult:
        """
        Install from PyPI.

        Args:
            package: Package name (default: "nwave")

        Returns:
            InstallResult with installation outcome
        """

@dataclass(frozen=True)
class InstallResult:
    """Result of installation operation."""
    success: bool
    install_path: Path
    version: str
    counts: ArtifactCounts
    backup_path: Optional[Path] = None
    error_message: Optional[str] = None
```

**Depends On (Ports)**:
- `PipxPort` - pipx install/uninstall
- `FileSystemPort` - File operations
- `BackupPort` - Backup creation
- `ConfigPort` - Install path resolution

---

### 4.4 DoctorService

**Location**: `nWave/core/installer/application/doctor_service.py`

**Responsibility**: Verify installation health after install operations.

**Interface**:
```python
class DoctorService:
    """
    Verifies installation health.

    Checks:
    - Core installation present
    - Agent files count matches expected
    - Command files count matches expected
    - Template files count matches expected
    - Configuration valid
    - File permissions correct
    - Version matches expected
    """

    def __init__(
        self,
        file_system: FileSystemPort,
        config: ConfigPort,
    ) -> None:
        """Initialize with required ports."""

    def run(
        self,
        expected_version: Optional[str] = None,
        expected_counts: Optional[ArtifactCounts] = None,
    ) -> HealthReport:
        """
        Run health checks.

        Args:
            expected_version: Expected installed version (for validation)
            expected_counts: Expected artifact counts (for validation)

        Returns:
            HealthReport with status and check details
        """
```

**Depends On (Ports)**:
- `FileSystemPort` - File existence and counting
- `ConfigPort` - Configuration validation

---

### 4.5 RollbackService

**Location**: `nWave/core/installer/application/rollback_service.py`

**Responsibility**: Restore installation from backup on failure.

**Interface**:
```python
class RollbackService:
    """
    Handles rollback operations when installation fails.

    Restores the previous installation state from backup.
    """

    def __init__(
        self,
        backup: BackupPort,
        file_system: FileSystemPort,
    ) -> None:
        """Initialize with required ports."""

    def rollback(self, backup_path: Path) -> RollbackResult:
        """
        Restore from backup.

        Args:
            backup_path: Path to backup directory

        Returns:
            RollbackResult with restoration outcome
        """

@dataclass(frozen=True)
class RollbackResult:
    """Result of rollback operation."""
    success: bool
    restored_path: Path
    message: str
```

**Depends On (Ports)**:
- `BackupPort` - Backup restoration
- `FileSystemPort` - File operations

---

## 5. Port Interfaces

### 5.1 FileSystemPort

**Location**: `nWave/core/installer/ports/file_system_port.py`

**Contract**:
```python
class FileSystemPort(Protocol):
    """
    Port for file system operations.

    Abstracts all file system interactions for testability.
    """

    def exists(self, path: Path) -> bool:
        """Check if path exists."""

    def is_writable(self, path: Path) -> bool:
        """Check if path is writable."""

    def read_text(self, path: Path) -> str:
        """Read file as text."""

    def write_text(self, path: Path, content: str) -> None:
        """Write text to file."""

    def copy_tree(self, src: Path, dst: Path) -> int:
        """Copy directory tree, return file count."""

    def remove_tree(self, path: Path) -> None:
        """Remove directory tree."""

    def count_files(self, path: Path, pattern: str = "*.md") -> int:
        """Count files matching pattern."""

    def ensure_directory(self, path: Path) -> None:
        """Create directory if not exists."""
```

---

### 5.2 GitPort

**Location**: `nWave/core/installer/ports/git_port.py`

**Contract**:
```python
class GitPort(Protocol):
    """
    Port for Git operations.
    """

    def get_current_branch(self) -> str:
        """Get current branch name."""

    def get_commits_since_tag(self, tag: str) -> List[str]:
        """Get commit messages since tag."""

    def get_latest_tag(self) -> Optional[str]:
        """Get latest version tag."""

    def has_uncommitted_changes(self) -> bool:
        """Check for uncommitted changes."""
```

---

### 5.3 PipxPort

**Location**: `nWave/core/installer/ports/pipx_port.py`

**Contract**:
```python
class PipxPort(Protocol):
    """
    Port for pipx operations.
    """

    def is_available(self) -> bool:
        """Check if pipx is available."""

    def install(
        self,
        package: str,
        force: bool = False,
        pip_args: Optional[List[str]] = None,
    ) -> PipxInstallResult:
        """
        Install package via pipx.

        Args:
            package: Package name or path to wheel
            force: If True, reinstall if exists
            pip_args: Additional pip arguments

        Returns:
            PipxInstallResult with outcome
        """

    def uninstall(self, package: str) -> bool:
        """Uninstall package."""

    def list_packages(self) -> List[str]:
        """List installed packages."""

@dataclass(frozen=True)
class PipxInstallResult:
    """Result of pipx install."""
    success: bool
    package: str
    version: Optional[str]
    error_message: Optional[str] = None
```

---

### 5.4 BuildPort

**Location**: `nWave/core/installer/ports/build_port.py`

**Contract**:
```python
class BuildPort(Protocol):
    """
    Port for build operations (python -m build).
    """

    def is_available(self) -> bool:
        """Check if build package is available."""

    def get_version(self) -> str:
        """Get build package version."""

    def build_wheel(
        self,
        output_dir: Path = Path("dist"),
    ) -> BuildWheelResult:
        """
        Build wheel in output directory.

        Args:
            output_dir: Directory for wheel output

        Returns:
            BuildWheelResult with wheel path
        """

    def clean_dist(self, dist_dir: Path = Path("dist")) -> bool:
        """Clean dist directory."""

@dataclass(frozen=True)
class BuildWheelResult:
    """Result of wheel build."""
    success: bool
    wheel_path: Optional[Path]
    error_message: Optional[str] = None
```

---

### 5.5 ConfigPort

**Location**: `nWave/core/installer/ports/config_port.py`

**Contract**:
```python
class ConfigPort(Protocol):
    """
    Port for configuration operations.
    """

    def resolve_install_path(self) -> Path:
        """
        Resolve installation path.

        Resolution order:
        1. NWAVE_INSTALL_PATH environment variable
        2. config/installer.yaml [paths.install_dir]
        3. Default: ~/.claude/agents/nw/
        """

    def get_env_var(self, name: str) -> Optional[str]:
        """Get environment variable value."""

    def load_config(self, path: Path) -> Dict[str, Any]:
        """Load configuration from YAML/TOML file."""

    def read_pyproject_version(self) -> str:
        """Read version from pyproject.toml."""
```

---

### 5.6 BackupPort

**Location**: `nWave/core/installer/ports/backup_port.py`

**Contract**:
```python
class BackupPort(Protocol):
    """
    Port for backup operations.
    """

    def create_backup(self, source_path: Path) -> BackupResult:
        """
        Create backup of source path.

        Args:
            source_path: Path to back up

        Returns:
            BackupResult with backup path
        """

    def restore_backup(self, backup_path: Path, target_path: Path) -> bool:
        """
        Restore backup to target path.

        Args:
            backup_path: Path to backup directory
            target_path: Where to restore

        Returns:
            True if successful
        """

    def cleanup_old_backups(self, keep_count: int = 5) -> int:
        """
        Clean up old backups, keeping most recent.

        Args:
            keep_count: Number of backups to keep

        Returns:
            Number of backups removed
        """

@dataclass(frozen=True)
class BackupResult:
    """Result of backup creation."""
    success: bool
    backup_path: Optional[Path]
    error_message: Optional[str] = None
```

---

### 5.7 UserPromptPort

**Location**: `nWave/core/installer/ports/user_prompt_port.py`

**Contract**:
```python
class UserPromptPort(Protocol):
    """
    Port for user interaction.
    """

    def confirm(self, message: str, default: bool = False) -> bool:
        """
        Ask user for confirmation.

        Args:
            message: Confirmation prompt
            default: Default response for CI mode

        Returns:
            True if confirmed
        """

    def display_progress(self, message: str) -> None:
        """Display progress message."""

    def display_table(self, headers: List[str], rows: List[List[str]]) -> None:
        """Display tabular data."""

    def display_success(self, message: str) -> None:
        """Display success message."""

    def display_error(self, message: str) -> None:
        """Display error message."""
```

---

## 6. Infrastructure Adapters

### 6.1 Adapter Implementations

| Port | Adapter | Technology |
|------|---------|------------|
| `FileSystemPort` | `FileSystemAdapter` | pathlib, shutil |
| `GitPort` | `GitAdapter` | subprocess (git CLI) |
| `PipxPort` | `PipxAdapter` | subprocess (pipx CLI) |
| `BuildPort` | `BuildAdapter` | subprocess (python -m build) |
| `ConfigPort` | `ConfigAdapter` | os.environ, PyYAML, tomllib |
| `BackupPort` | `BackupAdapter` | pathlib, shutil, datetime |
| `UserPromptPort` | `RichUserPromptAdapter` | rich.console, rich.prompt |
| `UserPromptPort` | `CIUserPromptAdapter` | No interaction, uses defaults |

### 6.2 Adapter Selection (DI)

```python
def create_services(ci_mode: bool = False) -> ServiceContainer:
    """
    Create service container with appropriate adapters.

    Args:
        ci_mode: If True, use non-interactive adapters
    """
    file_system = FileSystemAdapter()
    git = GitAdapter()
    pipx = PipxAdapter()
    build = BuildAdapter()
    config = ConfigAdapter()
    backup = BackupAdapter()

    user_prompt = (
        CIUserPromptAdapter() if ci_mode
        else RichUserPromptAdapter()
    )

    return ServiceContainer(
        preflight=PreflightService(
            check_registry=CheckRegistry(),
            check_executor=CheckExecutor(file_system, git, pipx, build, config),
            user_prompt=user_prompt,
        ),
        build=BuildService(file_system, git, build, DateProvider()),
        install=InstallService(pipx, file_system, backup, config),
        doctor=DoctorService(file_system, config),
        rollback=RollbackService(backup, file_system),
    )
```

---

## 7. CLI Adapter Boundaries

### 7.1 CLI Commands

| Command | Entry Point | Services Used |
|---------|-------------|---------------|
| `nwave forge:build` | `forge_build_cli.py` | PreflightService, BuildService |
| `nwave forge:install` | `forge_install_cli.py` | PreflightService, InstallService, DoctorService, RollbackService |
| `nwave install` | `install_cli.py` | PreflightService, InstallService, DoctorService |
| `nwave doctor` | `doctor_cli.py` | DoctorService |

### 7.2 CLI Responsibilities

CLI adapters are responsible for:
1. Parsing command-line arguments
2. Creating service container with appropriate adapters
3. Calling service methods
4. Formatting output (TUI or JSON based on mode)
5. Setting exit codes

CLI adapters must NOT contain:
- Business logic
- Direct file system operations
- Direct subprocess calls

---

## 8. Component Interaction Summary

### 8.1 Build Journey

```
forge_build_cli.py
    |
    +-- create_services(ci_mode=args.ci)
    |
    +-- preflight_service.run(journey="build")
    |       |
    |       +-- CheckRegistry.get_checks_for_journey("build")
    |       +-- CheckExecutor.execute_checks(checks)
    |       +-- [If fixable failures] UserPrompt.confirm(fix?)
    |
    +-- build_service.build(force_version=args.version)
    |       |
    |       +-- file_system.read_text(pyproject.toml)
    |       +-- git.get_commits_since_tag()
    |       +-- build_tool.build_wheel()
    |       +-- file_system.count_files(agents, commands, templates)
    |
    +-- display_result(build_result)
```

### 8.2 Install Journey

```
forge_install_cli.py
    |
    +-- create_services(ci_mode=args.ci)
    |
    +-- preflight_service.run(journey="install-local")
    |
    +-- backup_service.create_backup(install_path)
    |
    +-- install_service.install_local(wheel_path)
    |       |
    |       +-- pipx.install(wheel_path, force=True)
    |       +-- file_system.copy_tree(dist/agents, install_path/agents)
    |
    +-- doctor_service.run(expected_version, expected_counts)
    |       |
    |       +-- [If UNHEALTHY] rollback_service.rollback(backup_path)
    |
    +-- display_result(install_result, health_report)
```

---

## 9. Testing Strategy by Component

| Component Type | Test Strategy | Mocking Required |
|----------------|---------------|------------------|
| Domain Objects | Unit tests | None |
| Application Services | Unit tests | Port interfaces |
| Ports | N/A (interfaces) | N/A |
| Adapters | Integration tests | External tools (pipx, git) |
| CLI | Integration tests | Full service container |

---

## 10. References

- [Architecture Design](./architecture-design.md)
- [Sequence Diagrams](./diagrams/sequence-diagrams.md)
- [User Stories](/docs/features/modern-cli-installer/01-discuss/user-stories.md)
