# Component Interaction Diagrams: modern_CLI_installer

**Epic**: modern_CLI_installer
**Wave**: DESIGN
**Architect**: Morgan (Solution Architect)
**Date**: 2026-02-01

---

## 1. System Context Diagram

```mermaid
C4Context
    title System Context: modern_CLI_installer

    Person(developer, "Developer", "Builds and tests local candidates")
    Person(enduser, "End User", "Installs nWave from PyPI")
    Person(ci, "CI/CD Pipeline", "Automated build and test")

    System(installer, "nWave Installer", "CLI tools for building, installing, and verifying nWave framework")

    System_Ext(pypi, "PyPI", "Python Package Index")
    System_Ext(git, "Git", "Version control")
    System_Ext(pipx, "pipx", "Python app installer")
    System_Ext(filesystem, "File System", "~/.claude/agents/nw/")

    Rel(developer, installer, "forge:build, forge:install")
    Rel(enduser, installer, "pipx install nwave")
    Rel(ci, installer, "forge:build --ci")

    Rel(installer, pypi, "Download/Upload packages")
    Rel(installer, git, "Read commits, tags, branch")
    Rel(installer, pipx, "Install packages")
    Rel(installer, filesystem, "Read/Write agents, commands")
```

---

## 2. Container Diagram

```mermaid
C4Container
    title Container Diagram: nWave Installer

    Person(user, "User", "Developer or End User")

    Container_Boundary(cli, "CLI Layer") {
        Container(forge_build, "forge:build CLI", "Python/Click", "Build local candidate wheel")
        Container(forge_install, "forge:install CLI", "Python/Click", "Install local candidate")
        Container(install_nwave, "install CLI", "Python/Click", "Install from PyPI")
        Container(doctor, "doctor CLI", "Python/Click", "Verify installation health")
    }

    Container_Boundary(app, "Application Layer") {
        Container(preflight, "PreflightService", "Python", "Environment validation")
        Container(build, "BuildService", "Python", "Wheel building orchestration")
        Container(install, "InstallService", "Python", "Installation orchestration")
        Container(doctor_svc, "DoctorService", "Python", "Health verification")
        Container(rollback, "RollbackService", "Python", "Backup restoration")
    }

    Container_Boundary(domain, "Domain Layer") {
        Container(version, "Version Domain", "Python", "CandidateVersion, Version entities")
        Container(checks, "Check Domain", "Python", "CheckResult, HealthStatus")
        Container(artifacts, "Artifact Domain", "Python", "ArtifactCounts, paths")
    }

    Container_Boundary(infra, "Infrastructure Layer") {
        Container(fs_adapter, "FileSystemAdapter", "Python", "File operations")
        Container(git_adapter, "GitAdapter", "Python", "Git CLI wrapper")
        Container(pipx_adapter, "PipxAdapter", "Python", "pipx CLI wrapper")
        Container(build_adapter, "BuildAdapter", "Python", "python -m build wrapper")
        Container(backup_adapter, "BackupAdapter", "Python", "Backup operations")
    }

    Rel(user, forge_build, "nwave forge:build")
    Rel(user, forge_install, "nwave forge:install")
    Rel(user, install_nwave, "nwave install")
    Rel(user, doctor, "nwave doctor")

    Rel(forge_build, preflight, "validate environment")
    Rel(forge_build, build, "build wheel")
    Rel(forge_install, preflight, "validate environment")
    Rel(forge_install, install, "install wheel")
    Rel(forge_install, doctor_svc, "verify health")
    Rel(forge_install, rollback, "restore on failure")

    Rel(preflight, checks, "uses")
    Rel(build, version, "uses")
    Rel(install, artifacts, "uses")
    Rel(doctor_svc, checks, "uses")

    Rel(preflight, fs_adapter, "check files")
    Rel(preflight, git_adapter, "check repo")
    Rel(preflight, pipx_adapter, "check pipx")
    Rel(build, build_adapter, "build wheel")
    Rel(install, pipx_adapter, "pipx install")
    Rel(install, backup_adapter, "create backup")
    Rel(rollback, backup_adapter, "restore backup")
```

---

## 3. Component Diagram: Application Services

```mermaid
flowchart TB
    subgraph CLI["CLI Adapters (Primary)"]
        FB[forge:build CLI]
        FI[forge:install CLI]
        IN[install CLI]
        DC[doctor CLI]
    end

    subgraph APP["Application Services"]
        PFS[PreflightService]
        BS[BuildService]
        IS[InstallService]
        DS[DoctorService]
        RS[RollbackService]
        VBS[VersionBumpService]
    end

    subgraph DOMAIN["Domain Model"]
        CV[CandidateVersion]
        V[Version]
        CR[CheckResult]
        HS[HealthStatus]
        AC[ArtifactCounts]
    end

    subgraph PORTS["Port Interfaces"]
        FSP[FileSystemPort]
        GP[GitPort]
        PP[PipxPort]
        BP[BuildPort]
        CP[ConfigPort]
        BAP[BackupPort]
        UPP[UserPromptPort]
    end

    FB --> PFS
    FB --> BS
    FI --> PFS
    FI --> IS
    FI --> DS
    FI --> RS
    IN --> PFS
    IN --> IS
    IN --> DS
    DC --> DS

    PFS --> CR
    BS --> CV
    BS --> V
    IS --> AC
    DS --> HS
    DS --> CR
    DS --> AC

    PFS --> FSP
    PFS --> GP
    PFS --> PP
    PFS --> BP
    PFS --> UPP
    BS --> FSP
    BS --> GP
    BS --> BP
    IS --> PP
    IS --> FSP
    IS --> BAP
    IS --> CP
    DS --> FSP
    DS --> CP
    RS --> BAP
    RS --> FSP
    VBS --> GP
    VBS --> FSP
```

---

## 4. Component Diagram: Pre-flight Check Framework

```mermaid
flowchart TB
    subgraph PREFLIGHT["Pre-flight Framework"]
        PFS[PreflightService]
        CReg[CheckRegistry]
        CExec[CheckExecutor]
        CFix[CheckFixer]
    end

    subgraph CHECKS["Check Implementations"]
        subgraph CORE["Core Checks"]
            PV[python_version]
            PA[pipx_available]
            CD[claude_dir_writable]
        end
        subgraph BUILD["Build Checks"]
            BPK[build_package]
            PTE[pyproject_toml_exists]
            PTV[pyproject_toml_valid]
            SD[source_directory]
            DD[dist_directory]
        end
        subgraph INSTALL["Install Checks"]
            WE[wheel_exists]
            PI[pipx_isolation]
            IPR[install_path_resolved]
            CCI[claude_code_installed]
        end
    end

    subgraph DOMAIN["Domain"]
        CR[CheckResult]
        CS[CheckSeverity]
    end

    PFS --> CReg
    PFS --> CExec
    PFS --> CFix

    CReg --> CORE
    CReg --> BUILD
    CReg --> INSTALL

    CExec --> CR
    CR --> CS

    PV --> CR
    PA --> CR
    BPK --> CR
    WE --> CR
```

---

## 5. Component Diagram: Doctor Health Framework

```mermaid
flowchart TB
    subgraph DOCTOR["Doctor Framework"]
        DS[DoctorService]
        HC[HealthChecker]
        HR[HealthReporter]
    end

    subgraph CHECKS["Health Checks"]
        CI[core_installation]
        AF[agent_files]
        CF[command_files]
        TF[template_files]
        CV[config_valid]
        PM[permissions]
        VM[version_match]
    end

    subgraph DOMAIN["Domain"]
        HS[HealthStatus]
        HRep[HealthReport]
        CR[CheckResult]
        AC[ArtifactCounts]
    end

    subgraph OUTPUT["Output Formats"]
        TUI[TUI Table]
        JSON[JSON Output]
    end

    DS --> HC
    DS --> HR

    HC --> CI
    HC --> AF
    HC --> CF
    HC --> TF
    HC --> CV
    HC --> PM
    HC --> VM

    CI --> CR
    AF --> CR
    AF --> AC
    CF --> CR
    CF --> AC
    TF --> CR
    TF --> AC
    VM --> CR

    HC --> HS
    HC --> HRep
    HRep --> CR
    HRep --> AC

    HR --> TUI
    HR --> JSON
```

---

## 6. Data Flow Diagram: Build Journey

```mermaid
flowchart LR
    subgraph INPUT["Input Artifacts"]
        PT[pyproject.toml<br/>version: 1.3.0]
        SRC[nWave/<br/>source files]
        GIT[(Git<br/>commits, tags)]
    end

    subgraph PROCESS["Build Process"]
        PF[Pre-flight<br/>Validation]
        VA[Version<br/>Analysis]
        WB[Wheel<br/>Build]
        WV[Wheel<br/>Validation]
    end

    subgraph OUTPUT["Output Artifacts"]
        WHL[dist/nwave-1.3.0.dev20260201.1-py3-none-any.whl]
        META[Metadata<br/>candidate_version<br/>counts]
    end

    PT --> PF
    SRC --> PF
    PF --> VA

    GIT --> VA
    PT --> VA
    VA --> WB

    SRC --> WB
    WB --> WV
    WV --> WHL
    WV --> META
```

---

## 7. Data Flow Diagram: Install Journey

```mermaid
flowchart LR
    subgraph INPUT["Input Artifacts"]
        WHL[Wheel File<br/>dist/nwave-*.whl]
        CFG[Config<br/>NWAVE_INSTALL_PATH]
        EXIST[Existing Install<br/>~/.claude/agents/nw/]
    end

    subgraph PROCESS["Install Process"]
        PF[Pre-flight<br/>Validation]
        BK[Backup<br/>Creation]
        INS[pipx<br/>Install]
        DOC[Doctor<br/>Verification]
    end

    subgraph OUTPUT["Output Artifacts"]
        INST[Installed<br/>~/.claude/agents/nw/]
        BKUP[Backup<br/>~/.claude/agents/nw.backup-*]
        REPORT[Health<br/>Report]
    end

    WHL --> PF
    CFG --> PF
    PF --> BK

    EXIST --> BK
    BK --> BKUP
    BK --> INS

    WHL --> INS
    INS --> INST
    INS --> DOC

    INST --> DOC
    DOC --> REPORT
```

---

## 8. Hexagonal Architecture Visualization

```mermaid
flowchart TB
    subgraph DRIVING["Driving Adapters (Primary)"]
        direction TB
        CLI1[forge:build CLI]
        CLI2[forge:install CLI]
        CLI3[install CLI]
        CLI4[doctor CLI]
    end

    subgraph CORE["Application Core"]
        direction TB
        subgraph SERVICES["Application Services"]
            PFS[PreflightService]
            BS[BuildService]
            IS[InstallService]
            DS[DoctorService]
            RS[RollbackService]
        end
        subgraph DOMAIN["Domain Model"]
            CV[CandidateVersion]
            CR[CheckResult]
            HS[HealthStatus]
            AC[ArtifactCounts]
        end
    end

    subgraph PORTS["Ports"]
        direction TB
        FSP[FileSystemPort]
        GP[GitPort]
        PP[PipxPort]
        BP[BuildPort]
        CP[ConfigPort]
        BAP[BackupPort]
    end

    subgraph DRIVEN["Driven Adapters (Secondary)"]
        direction TB
        FSA[FileSystemAdapter]
        GA[GitAdapter]
        PA[PipxAdapter]
        BA[BuildAdapter]
        CA[ConfigAdapter]
        BKA[BackupAdapter]
    end

    subgraph EXTERNAL["External Systems"]
        direction TB
        FS[(File System)]
        GIT[(Git)]
        PIPX[(pipx)]
        BUILD[(python -m build)]
        ENV[(Environment)]
    end

    CLI1 --> PFS
    CLI1 --> BS
    CLI2 --> PFS
    CLI2 --> IS
    CLI2 --> DS
    CLI2 --> RS
    CLI3 --> IS
    CLI3 --> DS
    CLI4 --> DS

    PFS --> FSP
    PFS --> GP
    PFS --> PP
    PFS --> BP
    BS --> FSP
    BS --> GP
    BS --> BP
    IS --> PP
    IS --> FSP
    IS --> BAP
    IS --> CP
    DS --> FSP
    DS --> CP
    RS --> BAP
    RS --> FSP

    FSP -.-> FSA
    GP -.-> GA
    PP -.-> PA
    BP -.-> BA
    CP -.-> CA
    BAP -.-> BKA

    FSA --> FS
    GA --> GIT
    PA --> PIPX
    BA --> BUILD
    CA --> ENV
    BKA --> FS
```

---

## 9. Dependency Injection Container

```mermaid
flowchart TB
    subgraph DI["Dependency Injection Container"]
        SC[ServiceContainer]
    end

    subgraph ADAPTERS["Adapter Factory"]
        AF[create_adapters]
        IM[Interactive Mode]
        CM[CI Mode]
    end

    subgraph SERVICES["Service Factory"]
        SF[create_services]
    end

    subgraph INSTANCES["Service Instances"]
        PFS[PreflightService]
        BS[BuildService]
        IS[InstallService]
        DS[DoctorService]
        RS[RollbackService]
    end

    SC --> AF
    SC --> SF

    AF --> IM
    AF --> CM

    IM --> RichPrompt[RichUserPromptAdapter]
    CM --> CIPrompt[CIUserPromptAdapter]

    SF --> PFS
    SF --> BS
    SF --> IS
    SF --> DS
    SF --> RS

    AF -.-> PFS
    AF -.-> BS
    AF -.-> IS
    AF -.-> DS
    AF -.-> RS
```

---

## 10. Journey Flow Overview

```mermaid
flowchart TB
    subgraph J1["Journey 1: forge:build-local-candidate"]
        J1_PF[Pre-flight] --> J1_VA[Version Analysis]
        J1_VA --> J1_BLD[Build Wheel]
        J1_BLD --> J1_VAL[Validate]
        J1_VAL --> J1_SUM[Summary]
        J1_SUM --> J1_PR[Prompt Install?]
    end

    subgraph J2["Journey 2: forge:install-local-candidate"]
        J2_PF[Pre-flight] --> J2_RR[Release Readiness]
        J2_RR --> J2_BK[Backup]
        J2_BK --> J2_INS[Install]
        J2_INS --> J2_DOC[Doctor]
        J2_DOC --> J2_REP[Report]
    end

    subgraph J3["Journey 3: install-nwave (PyPI)"]
        J3_DL[Download] --> J3_PF[Pre-flight]
        J3_PF --> J3_INS[Install]
        J3_INS --> J3_DOC[Doctor]
        J3_DOC --> J3_CEL[Celebration]
    end

    J1_PR -->|Yes| J2_PF

    subgraph SHARED["Shared Infrastructure"]
        PFC[Pre-flight Check Framework]
        DHC[Doctor Health Framework]
        SAR[Shared Artifact Registry]
    end

    J1_PF --> PFC
    J2_PF --> PFC
    J3_PF --> PFC

    J2_DOC --> DHC
    J3_DOC --> DHC

    J1_VAL --> SAR
    J2_INS --> SAR
    J3_INS --> SAR
```

---

## 11. Error Recovery Flow

```mermaid
flowchart TB
    START[Start Operation]
    PF{Pre-flight<br/>Passed?}
    BACKUP[Create Backup]
    OP[Execute Operation]
    DOC{Doctor<br/>Healthy?}
    SUCCESS[Success]
    ROLLBACK[Rollback]
    RESTORE{Restore<br/>OK?}
    FAIL_RESTORE[Critical Error]
    FAIL_CLEAN[Clean Failure]

    START --> PF
    PF -->|No| FAIL_CLEAN
    PF -->|Yes| BACKUP
    BACKUP --> OP
    OP --> DOC
    DOC -->|Yes| SUCCESS
    DOC -->|No| ROLLBACK
    ROLLBACK --> RESTORE
    RESTORE -->|Yes| FAIL_CLEAN
    RESTORE -->|No| FAIL_RESTORE

    FAIL_CLEAN -->|exit 1-4| END1[End]
    FAIL_RESTORE -->|exit 5| END2[End]
    SUCCESS -->|exit 0| END3[End]
```

---

## References

- [Architecture Design](../architecture-design.md)
- [Component Boundaries](../component-boundaries.md)
- [Sequence Diagrams](./sequence-diagrams.md)
