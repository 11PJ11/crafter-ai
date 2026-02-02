# Sequence Diagrams: modern_CLI_installer

**Epic**: modern_CLI_installer
**Wave**: DESIGN
**Architect**: Morgan (Solution Architect)
**Date**: 2026-02-01

---

## 1. Journey 1: forge:build-local-candidate

### 1.1 Happy Path Sequence

```mermaid
sequenceDiagram
    participant U as User
    participant CLI as ForgeBuildCLI
    participant PF as PreflightService
    participant CR as CheckRegistry
    participant CE as CheckExecutor
    participant BS as BuildService
    participant FS as FileSystemPort
    participant Git as GitPort
    participant Build as BuildPort

    U->>CLI: nwave forge:build
    activate CLI

    CLI->>PF: run(journey="build")
    activate PF
    PF->>CR: get_checks_for_journey("build")
    CR-->>PF: [python_version, build_package, pyproject_toml, source_dir, dist_dir]

    loop For each check
        PF->>CE: execute(check)
        CE-->>PF: CheckResult(passed=true)
    end

    PF-->>CLI: PreflightResult(can_proceed=true)
    deactivate PF

    CLI->>BS: build()
    activate BS

    BS->>FS: read_text(pyproject.toml)
    FS-->>BS: version="1.3.0"

    BS->>Git: get_latest_tag()
    Git-->>BS: "v1.2.0"

    BS->>Git: get_commits_since_tag("v1.2.0")
    Git-->>BS: ["feat: new feature", "fix: bug fix"]

    Note over BS: Analyze commits: feat = MINOR bump
    Note over BS: Generate: 1.3.0-dev-20260201-001

    BS->>FS: clean_dist()
    FS-->>BS: ok

    BS->>Build: build_wheel()
    Build-->>BS: wheel_path="dist/nwave-1.3.0.dev20260201.1-py3-none-any.whl"

    BS->>FS: count_files(nWave/agents, "*.md")
    FS-->>BS: 47

    BS->>FS: count_files(nWave/commands, "*.md")
    FS-->>BS: 23

    BS->>FS: count_files(nWave/templates, "*.yaml")
    FS-->>BS: 12

    BS-->>CLI: BuildResult(success=true, wheel_path, counts)
    deactivate BS

    CLI->>U: Display summary
    CLI->>U: Prompt: "Install now? [Y/n]"
    U->>CLI: Y

    CLI->>CLI: Invoke forge:install-local-candidate
    deactivate CLI
```

### 1.2 Pre-flight Failure with Fix

```mermaid
sequenceDiagram
    participant U as User
    participant CLI as ForgeBuildCLI
    participant PF as PreflightService
    participant CE as CheckExecutor
    participant UP as UserPromptPort

    U->>CLI: nwave forge:build
    activate CLI

    CLI->>PF: run(journey="build", interactive=true)
    activate PF

    PF->>CE: execute(build_package_check)
    CE-->>PF: CheckResult(passed=false, fixable=true, fix_command="pip install build")

    PF->>UP: confirm("Install build package now? [Y/n]")
    UP-->>PF: true

    PF->>CE: apply_fix("pip install build")
    CE-->>PF: ok

    PF->>CE: execute(build_package_check)
    CE-->>PF: CheckResult(passed=true)

    PF-->>CLI: PreflightResult(can_proceed=true, fixes_applied=["build_package"])
    deactivate PF

    Note over CLI: Continue with build...
    deactivate CLI
```

---

## 2. Journey 2: forge:install-local-candidate

### 2.1 Happy Path Sequence

```mermaid
sequenceDiagram
    participant U as User
    participant CLI as ForgeInstallCLI
    participant PF as PreflightService
    participant IS as InstallService
    participant DS as DoctorService
    participant Pipx as PipxPort
    participant FS as FileSystemPort
    participant Backup as BackupPort
    participant Config as ConfigPort

    U->>CLI: nwave forge:install
    activate CLI

    CLI->>PF: run(journey="install-local")
    activate PF
    Note over PF: Checks: python, pipx, claude_dir, wheel_exists, pipx_isolation, install_path
    PF-->>CLI: PreflightResult(can_proceed=true)
    deactivate PF

    CLI->>Config: resolve_install_path()
    Config-->>CLI: ~/.claude/agents/nw/

    CLI->>Backup: create_backup(~/.claude/agents/nw/)
    activate Backup
    Backup-->>CLI: BackupResult(backup_path=~/.claude/agents/nw.backup-20260201-143025)
    deactivate Backup

    CLI->>IS: install_local(wheel_path)
    activate IS

    IS->>Pipx: install(wheel_path, force=true)
    Pipx-->>IS: PipxInstallResult(success=true)

    IS->>FS: copy_tree(dist/agents, install_path/agents)
    FS-->>IS: 47 files copied

    IS->>FS: copy_tree(dist/commands, install_path/commands)
    FS-->>IS: 23 files copied

    IS-->>CLI: InstallResult(success=true)
    deactivate IS

    CLI->>DS: run(expected_version="1.3.0-dev-20260201-001", expected_counts={47, 23, 12})
    activate DS

    DS->>FS: exists(~/.claude/agents/nw/)
    FS-->>DS: true

    DS->>FS: count_files(agents)
    FS-->>DS: 47

    DS->>FS: count_files(commands)
    FS-->>DS: 23

    DS->>FS: count_files(templates)
    FS-->>DS: 12

    DS-->>CLI: HealthReport(status=HEALTHY)
    deactivate DS

    CLI->>U: Display doctor report
    CLI->>U: Display release report
    deactivate CLI
```

### 2.2 Install Failure with Rollback

```mermaid
sequenceDiagram
    participant U as User
    participant CLI as ForgeInstallCLI
    participant IS as InstallService
    participant DS as DoctorService
    participant RS as RollbackService
    participant Pipx as PipxPort
    participant Backup as BackupPort
    participant FS as FileSystemPort

    U->>CLI: nwave forge:install
    activate CLI

    Note over CLI: Pre-flight passed...

    CLI->>Backup: create_backup(install_path)
    Backup-->>CLI: BackupResult(backup_path=...)

    CLI->>IS: install_local(wheel_path)
    activate IS

    IS->>Pipx: install(wheel_path, force=true)
    Pipx-->>IS: PipxInstallResult(success=false, error="Permission denied")

    IS-->>CLI: InstallResult(success=false, error_message="pipx install failed")
    deactivate IS

    CLI->>RS: rollback(backup_path)
    activate RS

    RS->>FS: remove_tree(install_path)
    FS-->>RS: ok

    RS->>Backup: restore_backup(backup_path, install_path)
    Backup-->>RS: true

    RS-->>CLI: RollbackResult(success=true, message="Restored from backup")
    deactivate RS

    CLI->>U: Display error
    CLI->>U: "Installation failed. Previous version restored."
    CLI-->>CLI: exit(3)
    deactivate CLI
```

### 2.3 Doctor Failure with Rollback

```mermaid
sequenceDiagram
    participant U as User
    participant CLI as ForgeInstallCLI
    participant IS as InstallService
    participant DS as DoctorService
    participant RS as RollbackService

    U->>CLI: nwave forge:install
    activate CLI

    Note over CLI: Pre-flight passed, backup created...

    CLI->>IS: install_local(wheel_path)
    IS-->>CLI: InstallResult(success=true)

    CLI->>DS: run(expected_counts={47, 23, 12})
    activate DS

    Note over DS: Counts mismatch: found 45 agents, expected 47
    DS-->>CLI: HealthReport(status=UNHEALTHY, checks=[agent_files: FAILED])
    deactivate DS

    CLI->>RS: rollback(backup_path)
    RS-->>CLI: RollbackResult(success=true)

    CLI->>U: Display error
    CLI->>U: "Doctor check failed: agent count mismatch (45 != 47)"
    CLI->>U: "Previous version restored from backup"
    CLI-->>CLI: exit(4)
    deactivate CLI
```

---

## 3. Journey 3: install-nwave (PyPI)

### 3.1 Fresh Install Sequence

```mermaid
sequenceDiagram
    participant U as User
    participant Shell as Terminal
    participant Pipx as pipx
    participant PyPI as PyPI Registry
    participant CLI as PostInstallHook
    participant PF as PreflightService
    participant IS as InstallService
    participant DS as DoctorService
    participant Config as ConfigPort

    U->>Shell: pipx install nwave
    activate Shell

    Shell->>Pipx: install nwave
    activate Pipx

    Pipx->>PyPI: Download nwave package
    PyPI-->>Pipx: nwave-1.3.0.tar.gz

    Pipx->>Pipx: Install in isolated environment
    Pipx-->>Shell: Successfully installed nwave
    deactivate Pipx

    Note over Shell: Post-install runs automatically or user runs nwave doctor

    Shell->>CLI: nwave doctor
    activate CLI

    CLI->>Config: resolve_install_path()
    Config-->>CLI: ~/.claude/agents/nw/

    CLI->>DS: run()
    activate DS

    DS-->>CLI: HealthReport(status=HEALTHY)
    deactivate DS

    CLI->>U: Display celebration message
    CLI->>U: "nWave v1.3.0 installed successfully!"
    CLI->>U: "Verify with: /nw:version in Claude Code"

    deactivate CLI
    deactivate Shell
```

### 3.2 Upgrade Detection Sequence

```mermaid
sequenceDiagram
    participant U as User
    participant CLI as InstallCLI
    participant PF as PreflightService
    participant IS as InstallService
    participant DS as DoctorService
    participant FS as FileSystemPort
    participant Backup as BackupPort

    U->>CLI: nwave install
    activate CLI

    CLI->>FS: exists(~/.claude/agents/nw/)
    FS-->>CLI: true

    CLI->>FS: read_text(~/.claude/agents/nw/VERSION)
    FS-->>CLI: "1.2.0"

    Note over CLI: Detected existing installation v1.2.0
    CLI->>U: "Existing installation detected (v1.2.0)"
    CLI->>U: "Upgrading to v1.3.0..."

    CLI->>Backup: create_backup(install_path)
    Backup-->>CLI: BackupResult(backup_path=...)

    CLI->>IS: install_from_pypi("nwave")
    IS-->>CLI: InstallResult(success=true)

    CLI->>DS: run()
    DS-->>CLI: HealthReport(status=HEALTHY)

    CLI->>U: "Upgrade complete: v1.2.0 -> v1.3.0"
    CLI->>U: "Backup saved at: ~/.claude/agents/nw.backup-..."
    deactivate CLI
```

---

## 4. Shared Infrastructure Sequences

### 4.1 Pre-flight Check Execution

```mermaid
sequenceDiagram
    participant PF as PreflightService
    participant CR as CheckRegistry
    participant CE as CheckExecutor
    participant UP as UserPromptPort

    PF->>CR: get_checks_for_journey(journey)
    CR-->>PF: List[Check]

    loop For each check
        PF->>CE: execute(check)

        alt Check Passed
            CE-->>PF: CheckResult(passed=true)
        else Check Failed
            CE-->>PF: CheckResult(passed=false, fixable=?, remediation=...)

            alt Fixable and Interactive
                PF->>UP: confirm(fix_prompt)
                UP-->>PF: user_confirmed

                alt User Confirmed
                    PF->>CE: apply_fix(fix_command)
                    PF->>CE: execute(check)
                    CE-->>PF: CheckResult (re-check)
                end
            end
        end
    end

    PF->>PF: Aggregate results
    PF-->>PF: PreflightResult(can_proceed, checks, fixes_applied)
```

### 4.2 Doctor Health Check

```mermaid
sequenceDiagram
    participant DS as DoctorService
    participant FS as FileSystemPort
    participant Config as ConfigPort

    DS->>Config: resolve_install_path()
    Config-->>DS: install_path

    DS->>FS: exists(install_path)
    FS-->>DS: true/false
    Note over DS: core_installation check

    DS->>FS: count_files(install_path/agents, "*.md")
    FS-->>DS: agent_count
    Note over DS: agent_files check

    DS->>FS: count_files(install_path/commands, "*.md")
    FS-->>DS: command_count
    Note over DS: command_files check

    DS->>FS: count_files(install_path/templates, "*.yaml")
    FS-->>DS: template_count
    Note over DS: template_files check

    DS->>FS: read_text(install_path/config.yaml)
    DS->>DS: validate_config()
    Note over DS: config_valid check

    DS->>FS: check_permissions(install_path)
    Note over DS: permissions check

    DS->>FS: read_text(install_path/VERSION)
    DS->>DS: compare_version(expected, actual)
    Note over DS: version_match check

    DS->>DS: determine_status(checks)
    Note over DS: HEALTHY | DEGRADED | UNHEALTHY

    DS-->>DS: HealthReport(status, checks, counts)
```

### 4.3 Backup and Rollback

```mermaid
sequenceDiagram
    participant Svc as Service
    participant Backup as BackupPort
    participant FS as FileSystemPort

    Note over Svc: Before destructive operation

    Svc->>Backup: create_backup(source_path)
    activate Backup

    Backup->>FS: ensure_directory(backup_root)
    Backup->>FS: copy_tree(source_path, backup_path)
    FS-->>Backup: files_copied

    Backup->>FS: write_text(backup_path/manifest.txt, metadata)

    Backup-->>Svc: BackupResult(backup_path)
    deactivate Backup

    Note over Svc: Execute operation...

    alt Operation Failed
        Svc->>Backup: restore_backup(backup_path, source_path)
        activate Backup

        Backup->>FS: remove_tree(source_path)
        Backup->>FS: copy_tree(backup_path, source_path)

        Backup-->>Svc: true
        deactivate Backup
    end
```

---

## 5. CI/CD Mode Sequences

### 5.1 CI Mode Build

```mermaid
sequenceDiagram
    participant CI as CI Pipeline
    participant CLI as ForgeBuildCLI
    participant PF as PreflightService
    participant BS as BuildService

    CI->>CLI: nwave forge:build --ci
    activate CLI

    Note over CLI: ci_mode=true, use CIUserPromptAdapter

    CLI->>PF: run(journey="build", interactive=false)
    activate PF

    Note over PF: No fix prompts in CI mode
    alt Any check failed
        PF-->>CLI: PreflightResult(can_proceed=false)
        CLI-->>CI: exit(1) + JSON error
    else All checks passed
        PF-->>CLI: PreflightResult(can_proceed=true)
    end
    deactivate PF

    CLI->>BS: build()
    BS-->>CLI: BuildResult

    CLI->>CLI: format_json(BuildResult)
    CLI-->>CI: JSON output + exit(0)

    deactivate CLI
```

### 5.2 CI JSON Output

```json
{
  "success": true,
  "journey": "forge:build-local-candidate",
  "version": "1.3.0-dev-20260201-001",
  "wheel_path": "dist/nwave-1.3.0.dev20260201.1-py3-none-any.whl",
  "artifacts": {
    "agent_count": 47,
    "command_count": 23,
    "template_count": 12
  },
  "preflight": {
    "passed": true,
    "checks": [
      {"id": "python_version", "passed": true, "message": "Python 3.12.0"},
      {"id": "build_package", "passed": true, "message": "build 1.0.3"}
    ]
  },
  "duration_ms": 4523
}
```

---

## 6. Error Handling Sequences

### 6.1 Blocking Pre-flight Failure

```mermaid
sequenceDiagram
    participant U as User
    participant CLI as CLI
    participant PF as PreflightService

    U->>CLI: nwave forge:build
    activate CLI

    CLI->>PF: run(journey="build")
    activate PF

    Note over PF: python_version check: Python 3.8 (requires 3.10+)
    PF-->>CLI: PreflightResult(can_proceed=false, checks=[python_version: FAILED])
    deactivate PF

    CLI->>U: Display error table
    Note over CLI: [x] Python version too old<br/>Required: 3.10+<br/>Found: 3.8<br/><br/>Upgrade options:<br/>- pyenv install 3.12

    CLI-->>CLI: exit(1)
    deactivate CLI
```

### 6.2 Build Failure

```mermaid
sequenceDiagram
    participant U as User
    participant CLI as CLI
    participant BS as BuildService
    participant Build as BuildPort

    U->>CLI: nwave forge:build
    activate CLI

    Note over CLI: Pre-flight passed...

    CLI->>BS: build()
    activate BS

    BS->>Build: build_wheel()
    Build-->>BS: BuildWheelResult(success=false, error="Invalid pyproject.toml")

    BS-->>CLI: BuildResult(success=false, error_message="Build failed: Invalid pyproject.toml")
    deactivate BS

    CLI->>U: Display error
    Note over CLI: [x] Build failed<br/>Error: Invalid pyproject.toml<br/><br/>Check pyproject.toml syntax and try again.

    CLI-->>CLI: exit(2)
    deactivate CLI
```

---

## 7. References

- [Architecture Design](../architecture-design.md)
- [Component Boundaries](../component-boundaries.md)
- [UX Journeys](/docs/ux/modern-cli-installer/)
