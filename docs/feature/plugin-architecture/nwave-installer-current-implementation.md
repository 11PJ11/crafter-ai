# nWave Installer - Current Implementation

**Version:** 1.0
**Date:** 2026-02-03
**Status:** Current Implementation Documentation
**Installer Version:** 1.2.0

---

## Executive Summary

This document describes the **actual current implementation** of the nWave installer as of 2026-02-03. The installer is a **monolithic Python application** with extracted utility classes for code organization.

**Key Characteristics:**
- ✅ Single `NWaveInstaller` class handles all installation logic
- ✅ Separate standalone script for DES hook management
- ✅ Helper utilities extracted to `install_utils.py`
- ✅ Sequential installation of all components (no selective installation)
- ✅ All-or-nothing uninstallation approach

**Contrast with Future Design:**
- ❌ No plugin system (see `nwave-plugin-system-architecture.md` for future design)
- ❌ No selective component installation/uninstallation
- ❌ No dependency resolution system
- ❌ No plugin registry or discovery mechanism

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [File Structure](#file-structure)
3. [Installation Flow](#installation-flow)
4. [Component Installation](#component-installation)
5. [DES Hook Installation](#des-hook-installation)
6. [Uninstallation Process](#uninstallation-process)
7. [Utility Classes](#utility-classes)
8. [Command-Line Interface](#command-line-interface)
9. [Verification and Validation](#verification-and-validation)
10. [Limitations](#limitations)
11. [Future Evolution](#future-evolution)

---

## Architecture Overview

### High-Level Structure

```
┌─────────────────────────────────────────────────────────┐
│              NWaveInstaller (Monolithic)                │
│                                                         │
│  ┌──────────────────────────────────────────────────┐  │
│  │  Preflight Checks                                │  │
│  │  - Python version                                │  │
│  │  - Dependencies (git, build tools)               │  │
│  │  - Claude config directory                       │  │
│  └──────────────────────────────────────────────────┘  │
│                        ↓                                │
│  ┌──────────────────────────────────────────────────┐  │
│  │  Build Process (if needed)                       │  │
│  │  - Run embed_sources.py                          │  │
│  │  - Build framework bundle                        │  │
│  │  - Create distribution in dist/ide/              │  │
│  └──────────────────────────────────────────────────┘  │
│                        ↓                                │
│  ┌──────────────────────────────────────────────────┐  │
│  │  Sequential Component Installation               │  │
│  │  1. Agents    → ~/.claude/agents/nw/             │  │
│  │  2. Commands  → ~/.claude/commands/nw/           │  │
│  │  3. Utilities → ~/.claude/scripts/               │  │
│  │  4. Templates → ~/.claude/templates/             │  │
│  └──────────────────────────────────────────────────┘  │
│                        ↓                                │
│  ┌──────────────────────────────────────────────────┐  │
│  │  Post-Installation                               │  │
│  │  - Verification checks                           │  │
│  │  - Manifest generation                           │  │
│  │  - Success/failure reporting                     │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘

         Separate Standalone Process
┌─────────────────────────────────────────────────────────┐
│         install_des_hooks.py (DES Hook Installer)       │
│                                                         │
│  - Modifies ~/.claude/settings.local.json               │
│  - Adds pretooluse and subagent-stop hooks              │
│  - Independent from main installer                      │
│  - Can install/uninstall DES hooks separately           │
└─────────────────────────────────────────────────────────┘
```

### Design Principles

The current implementation follows these principles:

1. **Simplicity**: Single-path execution, easy to understand and debug
2. **Reliability**: All components installed atomically, failure rolls back everything
3. **Safety**: Backup creation before modifications, restore capability
4. **Cross-Platform**: Works on Windows, macOS, Linux with platform-specific path handling
5. **Version Awareness**: Only updates files if newer versions available

---

## File Structure

### Installation Scripts

```
scripts/install/
├── install_nwave.py               # Main installer (829 lines)
│   └── NWaveInstaller class       # Monolithic installation logic
├── install_des_hooks.py           # DES hook installer (268 lines)
│   └── DESHookInstaller class     # Standalone hook management
├── uninstall_nwave.py             # Uninstaller (495 lines)
│   └── NWaveUninstaller class     # Complete removal logic
├── install_utils.py               # Shared utilities (464 lines)
│   ├── Logger                     # Cross-platform logging
│   ├── PathUtils                  # Path management
│   ├── BackupManager              # Backup/restore operations
│   ├── VersionUtils               # Version comparison
│   └── ManifestWriter             # Installation manifest
├── preflight_checker.py           # Pre-installation validation
├── installation_verifier.py       # Post-installation verification
├── output_formatter.py            # Rich console output
└── rich_console.py                # Terminal UI components
```

### Source Structure

```
nWave/
├── agents/                        # Agent markdown files
│   ├── agent1.md
│   ├── agent2.md
│   └── ...
├── templates/                     # JSON/YAML templates
│   ├── step-tdd-cycle-schema.json
│   └── ...
└── commands/                      # Command implementations (future)

scripts/
├── install_nwave_target_hooks.py # Target project hook installer
└── validate_step_file.py          # Step file validator

src/des/                           # DES module (hexagonal architecture)
├── domain/                        # Business logic core
├── application/                   # Application services
├── ports/                         # Interfaces
│   ├── driven_ports/              # Outbound ports
│   └── driver_ports/              # Inbound ports
└── adapters/                      # Implementations
    ├── driven/                    # Outbound adapters
    │   ├── config/
    │   ├── filesystem/
    │   ├── logging/
    │   ├── task_invocation/
    │   ├── time/
    │   └── validation/
    └── drivers/                   # Inbound adapters
        └── hooks/                 # Claude Code hook adapters
```

### Target Installation Structure

```
~/.claude/                         # Claude config directory
├── agents/nw/                     # nWave agents
│   ├── acceptance-designer.md
│   ├── solution-architect.md
│   └── ... (15+ agents)
├── commands/nw/                   # nWave commands
│   ├── nw-commit.md
│   ├── nw-design.md
│   └── ... (20+ commands)
├── scripts/                       # Utility scripts
│   ├── install_nwave_target_hooks.py
│   └── validate_step_file.py
├── templates/                     # Template files
│   └── step-tdd-cycle-schema.json
├── settings.local.json            # Claude configuration (modified by DES installer)
└── nwave-install.log              # Installation log
```

---

## Installation Flow

### Main Installation Process

The `NWaveInstaller.run()` method orchestrates the entire installation:

```python
def run(self) -> bool:
    """Main installation workflow."""
    # 1. Preflight checks
    if not self._run_preflight_checks():
        return False

    # 2. Create backup
    self._create_backup()

    # 3. Build framework (if needed)
    if not self._build_framework():
        return False

    # 4. Install components sequentially
    if not self.install_framework():
        return False

    # 5. Verify installation
    if not self._verify_installation():
        return False

    # 6. Write manifest
    self._write_manifest()

    # 7. Report success
    self._report_success()
    return True
```

### Step-by-Step Breakdown

#### Step 1: Preflight Checks (`scripts/install/preflight_checker.py`)

```python
PreflightChecker validates:
- Python version >= 3.8
- Git availability (for version info)
- Claude config directory (~/.claude) exists or can be created
- Write permissions to config directory
- Disk space availability
```

**Result**: If any check fails, installation aborts immediately.

#### Step 2: Backup Creation

```python
BackupManager creates:
- Timestamped backup: ~/.claude/.backup-YYYYMMDD-HHMMSS/
- Backs up existing agents/, commands/, scripts/, templates/
- Stores backup metadata for restoration
```

**Safety**: Allows rollback if installation fails.

#### Step 3: Build Framework

```python
Build process:
1. Run embed_sources.py
   - Embeds Python sources into agent markdown files
   - Updates agent files with latest code

2. Run build-ide-bundle.sh
   - Creates distributable bundle in dist/ide/
   - Copies agents, commands, templates
   - Optimizes for distribution
```

**Optimization**: Build skipped if dist/ide/ contains most agent files and `--force-rebuild` not specified.

#### Step 4: Install Components

Sequential installation of four components:

##### 4.1 Install Agents (`_install_agents()`)

```python
Source: dist/ide/agents/nw/ (or nWave/agents/ as fallback)
Target: ~/.claude/agents/nw/

Process:
- Copy all *.md files (excluding README.md)
- Preserves file metadata (timestamps)
- Counts installed agents for verification

Result: 15-20 agent files installed
```

##### 4.2 Install Commands (`_install_commands()`)

```python
Source: dist/ide/commands/
Target: ~/.claude/commands/

Process:
- Copy entire commands directory tree
- Includes nw/ subdirectory with nWave commands
- Overwrites existing files

Result: 20+ command files installed
```

##### 4.3 Install Utility Scripts (`_install_utility_scripts()`)

```python
Source: scripts/
Target: ~/.claude/scripts/

Installed utilities:
- install_nwave_target_hooks.py  # Target project hook installer
- validate_step_file.py           # Step file validator

Process:
- Version-aware copying (only if source is newer)
- Extracts version from __version__ variable
- Skips if target is same or newer version

Result: 2 utility scripts installed (if newer)
```

##### 4.4 Install Templates (`_install_templates()`)

```python
Source: nWave/templates/
Target: ~/.claude/templates/

Process:
- Copy all *.json, *.yaml, *.yml files
- Validates schema template structure
- Logs each installed template

Result: Template files installed (currently: step-tdd-cycle-schema.json)
```

#### Step 5: Verification (`scripts/install/installation_verifier.py`)

```python
InstallationVerifier checks:
- Agent files present (>= 10 expected)
- Command files present (>= 5 expected)
- Templates present (>= 1 expected)
- File integrity (no empty files)
- Directory structure correct

Result: Verification report with success/failure status
```

#### Step 6: Manifest Generation

```python
ManifestWriter creates: ~/.claude/nwave-manifest.json

Manifest contains:
{
  "version": "1.2.0",
  "installed_at": "2026-02-03T10:30:00",
  "components": {
    "agents": 15,
    "commands": 20,
    "scripts": 2,
    "templates": 1
  },
  "paths": {
    "agents": "~/.claude/agents/nw",
    "commands": "~/.claude/commands/nw",
    ...
  }
}
```

**Purpose**: Enables verification, updates, and uninstallation tracking.

#### Step 7: Success Reporting

```python
Rich console output:
✓ nWave Framework installed successfully
✓ 15 agents installed
✓ 20 commands installed
✓ 2 utility scripts installed
✓ 1 templates installed

Next steps:
- Run: python scripts/install/install_des_hooks.py
  (To enable DES enforcement hooks)
```

---

## Component Installation

### Agents Installation

**Purpose**: Install specialized AI agents for nWave methodology phases.

**Source Files**: Agent markdown files with embedded Python code.

**Examples**:
- `solution-architect.md` - DESIGN wave architect
- `software-crafter.md` - DEVELOP wave implementation
- `acceptance-designer.md` - DISTILL wave test designer
- `devop.md` - DELIVER wave deployment coordinator

**Installation Logic**:
```python
def _install_agents(self):
    source_agent_dir = self.project_root / "nWave" / "agents"
    dist_agent_dir = self.framework_source / "agents" / "nw"
    target_agent_dir = self.claude_config_dir / "agents" / "nw"

    # Prefer dist/ if build is complete (>50% of source agents)
    dist_count = count_files(dist_agent_dir, "*.md")
    source_count = count_files(source_agent_dir, "*.md")

    if dist_count >= (source_count // 2) and dist_count > 5:
        copy_tree_with_filter(dist_agent_dir, target_agent_dir)
    else:
        # Fallback to source if build incomplete
        copy_tree_with_filter(source_agent_dir, target_agent_dir)
```

**Verification**: Counts installed `.md` files, expects >= 10 agents.

### Commands Installation

**Purpose**: Install nWave methodology commands (skills).

**Source Files**: Command markdown files defining slash commands.

**Examples**:
- `nw-design.md` - Initiate architecture design
- `nw-develop.md` - Start development cycle
- `nw-distill.md` - Create acceptance tests
- `nw-deliver.md` - Deployment coordination

**Installation Logic**:
```python
def _install_commands(self):
    commands_source = self.framework_source / "commands"
    commands_target = self.claude_config_dir / "commands"

    # Copy entire directory tree
    for item in commands_source.iterdir():
        target = commands_target / item.name
        if item.is_dir():
            shutil.copytree(item, target)  # Replace existing
        else:
            shutil.copy2(item, target)
```

**Verification**: Counts installed command files in `commands/nw/`.

### Utility Scripts Installation

**Purpose**: Install helper scripts for target projects.

**Version-Aware Installation**:
```python
def _install_utility_scripts(self):
    utility_scripts = [
        "install_nwave_target_hooks.py",
        "validate_step_file.py"
    ]

    for script_name in utility_scripts:
        source_ver = extract_version_from_file(source_script)
        target_ver = extract_version_from_file(target_script) if exists(target_script) else "0.0.0"

        if source_ver > target_ver:
            shutil.copy2(source_script, target_script)
            logger.info(f"Updated {script_name}: {target_ver} → {source_ver}")
        else:
            logger.info(f"Skipped {script_name} (current: {target_ver})")
```

**Key Scripts**:
1. **install_nwave_target_hooks.py**: Installs nWave hooks in target projects
2. **validate_step_file.py**: Validates step file JSON schema compliance

### Templates Installation

**Purpose**: Install JSON/YAML templates for structured artifacts.

**Current Templates**:
- `step-tdd-cycle-schema.json` - Schema for TDD cycle step files

**Installation Logic**:
```python
def _install_templates(self):
    templates_source = self.project_root / "nWave" / "templates"
    templates_target = self.claude_config_dir / "templates"

    template_patterns = ["*.json", "*.yaml", "*.yml"]
    for pattern in template_patterns:
        for template_file in templates_source.glob(pattern):
            shutil.copy2(template_file, templates_target / template_file.name)
```

**Validation**: Checks `step-tdd-cycle-schema.json` for required fields (`schema_version`, `phases`).

---

## DES Hook Installation

### Separate Installation Process

**Script**: `scripts/install/install_des_hooks.py`

**Purpose**: Install Claude Code hooks for DES enforcement without modifying main installer.

### DES Hook Installer Class

```python
class DESHookInstaller:
    """Manages DES hook installation and uninstallation."""

    DES_PRETOOLUSE_HOOK = {
        "matcher": "Task",
        "command": "python3 src/des/adapters/drivers/hooks/claude_code_hook_adapter.py pre-task"
    }

    DES_SUBAGENT_STOP_HOOK = {
        "command": "python3 src/des/adapters/drivers/hooks/claude_code_hook_adapter.py subagent-stop"
    }
```

### Installation Flow

```
1. Load settings.local.json (or create if missing)
   └─> Preserve existing hooks

2. Check if DES hooks already installed
   └─> If yes: Skip (idempotent)

3. Add DES hooks to configuration
   ├─> hooks.pretooluse[] += DES_PRETOOLUSE_HOOK
   └─> hooks.subagent_stop[] += DES_SUBAGENT_STOP_HOOK

4. Save settings.local.json
   └─> Pretty-printed JSON with indent=2

5. Report success
   └─> "Restart Claude Code session to activate hooks"
```

### Hook Configuration Result

After installation, `~/.claude/settings.local.json` contains:

```json
{
  "hooks": {
    "pretooluse": [
      {
        "matcher": "Task",
        "command": "python3 src/des/adapters/drivers/hooks/claude_code_hook_adapter.py pre-task"
      }
    ],
    "subagent_stop": [
      {
        "command": "python3 src/des/adapters/drivers/hooks/claude_code_hook_adapter.py subagent-stop"
      }
    ]
  }
}
```

### Hook Functionality

**Pre-Task Hook** (`pretooluse` with `matcher: "Task"`):
- Triggered before Task tool invocation
- Validates Definition of Ready (DoR) checklist
- Blocks agent execution if DoR validation fails
- Enforces nWave methodology compliance

**Subagent-Stop Hook** (`subagent_stop`):
- Triggered when subagent completes
- Records execution metadata
- Updates task status tracking
- Archives artifacts

### Uninstallation

```python
def uninstall(self) -> bool:
    """Remove only DES hooks, preserve other hooks."""
    config = self._load_config()

    # Remove DES pretooluse hook
    if "hooks" in config and "pretooluse" in config["hooks"]:
        config["hooks"]["pretooluse"] = [
            h for h in config["hooks"]["pretooluse"]
            if not self._is_des_pretooluse_hook(h)
        ]

    # Remove DES subagent_stop hook
    if "hooks" in config and "subagent_stop" in config["hooks"]:
        config["hooks"]["subagent_stop"] = [
            h for h in config["hooks"]["subagent_stop"]
            if not self._is_des_subagent_stop_hook(h)
        ]

    self._save_config(config)
```

**Key Feature**: Surgical removal - preserves all non-DES hooks.

### Why Separate Installer?

1. **Modularity**: DES hooks are optional, not all users need enforcement
2. **Independence**: Can update DES hooks without reinstalling framework
3. **Safety**: Avoids main installer touching Claude configuration files
4. **Testability**: DES hook installer can be tested independently
5. **User Control**: Explicit opt-in for enforcement

---

## Uninstallation Process

**Script**: `scripts/install/uninstall_nwave.py`

### Uninstaller Architecture

```python
class NWaveUninstaller:
    """Complete removal of nWave framework."""

    def uninstall(self) -> bool:
        """All-or-nothing uninstallation."""
        # 1. Remove agents
        self.remove_agents()

        # 2. Remove commands
        self.remove_commands()

        # 3. Remove utility scripts
        self.remove_utility_scripts()

        # 4. Remove templates
        self.remove_templates()

        # 5. Remove config files
        self.remove_config_files()

        # 6. Report success
        return True
```

### Uninstallation Steps

#### 1. Remove Agents
```python
def remove_agents(self):
    agent_dir = self.claude_config_dir / "agents" / "nw"
    if agent_dir.exists():
        shutil.rmtree(agent_dir)
        logger.info("Removed nWave agents")
```

#### 2. Remove Commands
```python
def remove_commands(self):
    commands_dir = self.claude_config_dir / "commands" / "nw"
    if commands_dir.exists():
        shutil.rmtree(commands_dir)
        logger.info("Removed nWave commands")
```

#### 3. Remove Utility Scripts
```python
def remove_utility_scripts(self):
    scripts_to_remove = [
        "install_nwave_target_hooks.py",
        "validate_step_file.py"
    ]
    for script_name in scripts_to_remove:
        script_path = self.claude_config_dir / "scripts" / script_name
        if script_path.exists():
            script_path.unlink()
```

#### 4. Remove Templates
```python
def remove_templates(self):
    templates = [
        "step-tdd-cycle-schema.json"
    ]
    for template in templates:
        template_path = self.claude_config_dir / "templates" / template
        if template_path.exists():
            template_path.unlink()
```

#### 5. Remove Config Files
```python
def remove_config_files(self):
    config_files = [
        "nwave-manifest.json",
        "nwave-install.log"
    ]
    for config_file in config_files:
        path = self.claude_config_dir / config_file
        if path.exists():
            path.unlink()
```

### Uninstallation Result

After uninstallation, the following are removed:
```
~/.claude/
├── agents/nw/           [REMOVED]
├── commands/nw/         [REMOVED]
├── scripts/
│   ├── install_nwave_target_hooks.py  [REMOVED]
│   └── validate_step_file.py          [REMOVED]
├── templates/
│   └── step-tdd-cycle-schema.json     [REMOVED]
├── nwave-manifest.json  [REMOVED]
└── nwave-install.log    [REMOVED]
```

**Note**: DES hooks in `settings.local.json` are NOT automatically removed. Use `install_des_hooks.py --uninstall` separately.

---

## Utility Classes

### Logger (`scripts/install/install_utils.py`)

```python
class Logger:
    """Cross-platform logging to file and console."""

    def __init__(self, log_file: Path | None):
        self.log_file = log_file

    def info(self, message: str):
        """Log info message."""
        self._log("INFO", message)

    def warn(self, message: str):
        """Log warning message."""
        self._log("WARN", message)

    def error(self, message: str):
        """Log error message."""
        self._log("ERROR", message)
```

**Features**:
- Writes to log file if specified
- Outputs to console with color codes
- Thread-safe file operations
- Timestamps all messages

### PathUtils (`scripts/install/install_utils.py`)

```python
class PathUtils:
    """Cross-platform path operations."""

    @staticmethod
    def get_project_root(start_path: Path) -> Path:
        """Find project root (contains .git or pyproject.toml)."""
        ...

    @staticmethod
    def get_claude_config_dir() -> Path:
        """Get Claude config directory (~/.claude)."""
        return Path.home() / ".claude"

    @staticmethod
    def copy_tree_with_filter(source: Path, target: Path, exclude_patterns: list[str]):
        """Copy directory tree with exclusion patterns."""
        ...

    @staticmethod
    def count_files(directory: Path, pattern: str) -> int:
        """Count files matching glob pattern."""
        ...
```

**Key Operations**:
- Project root detection (searches for `.git`, `pyproject.toml`)
- Claude config directory resolution (handles `~/.claude` expansion)
- Filtered tree copying (excludes README.md, etc.)
- File counting for verification

### BackupManager (`scripts/install/install_utils.py`)

```python
class BackupManager:
    """Manages backups and restoration."""

    def create_backup(self, target_dir: Path) -> Path:
        """Create timestamped backup."""
        backup_dir = target_dir / f".backup-{timestamp}"
        # Copy existing files to backup
        return backup_dir

    def restore_backup(self, backup_dir: Path):
        """Restore from backup."""
        # Copy backup files back to original location
        ...
```

**Backup Strategy**:
- Timestamped backups: `.backup-YYYYMMDD-HHMMSS/`
- Preserves file metadata (timestamps, permissions)
- Enables rollback on installation failure

### VersionUtils (`scripts/install/install_utils.py`)

```python
class VersionUtils:
    """Version comparison and extraction."""

    @staticmethod
    def extract_version_from_file(file_path: Path) -> str:
        """Extract __version__ = "x.y.z" from Python file."""
        ...

    @staticmethod
    def compare_versions(v1: str, v2: str) -> int:
        """Compare semantic versions."""
        # Returns: -1 (v1 < v2), 0 (equal), 1 (v1 > v2)
        ...
```

**Version Format**: Semantic versioning (`MAJOR.MINOR.PATCH`)

**Usage**: Skip utility script installation if target is same or newer version.

### ManifestWriter (`scripts/install/install_utils.py`)

```python
class ManifestWriter:
    """Generates installation manifest JSON."""

    def write_manifest(self, manifest_data: dict):
        """Write nwave-manifest.json."""
        manifest_path = self.claude_config_dir / "nwave-manifest.json"
        with open(manifest_path, "w") as f:
            json.dump(manifest_data, f, indent=2)
```

**Manifest Purpose**:
- Track installed components
- Record installation timestamp
- Enable version checking for updates
- Support selective uninstallation (future)

---

## Command-Line Interface

### Main Installer (`install_nwave.py`)

```bash
python scripts/install/install_nwave.py [OPTIONS]

Options:
  --backup-only        Create backup without installing
  --restore            Restore from most recent backup
  --dry-run            Simulate installation (no changes)
  --force-rebuild      Force framework rebuild even if dist/ exists
  --help               Show help message

Examples:
  # Standard installation
  python install_nwave.py

  # Dry-run to preview changes
  python install_nwave.py --dry-run

  # Force rebuild of framework
  python install_nwave.py --force-rebuild

  # Create backup only
  python install_nwave.py --backup-only

  # Restore from backup
  python install_nwave.py --restore
```

### DES Hook Installer (`install_des_hooks.py`)

```bash
python scripts/install/install_des_hooks.py [OPTIONS]

Options:
  --install           Install DES hooks (default action)
  --uninstall         Uninstall DES hooks
  --verify            Verify DES hooks are installed
  --config-dir PATH   Claude config directory (default: ~/.claude)
  --help              Show help message

Examples:
  # Install DES hooks
  python install_des_hooks.py
  python install_des_hooks.py --install

  # Uninstall DES hooks
  python install_des_hooks.py --uninstall

  # Verify installation
  python install_des_hooks.py --verify

  # Custom config directory
  python install_des_hooks.py --config-dir=/custom/path/.claude
```

### Uninstaller (`uninstall_nwave.py`)

```bash
python scripts/install/uninstall_nwave.py [OPTIONS]

Options:
  --force             Skip confirmation prompt
  --keep-logs         Keep nwave-install.log after uninstall
  --dry-run           Simulate uninstallation (no changes)
  --help              Show help message

Examples:
  # Interactive uninstallation (asks for confirmation)
  python uninstall_nwave.py

  # Force uninstall without prompt
  python uninstall_nwave.py --force

  # Dry-run to preview removal
  python uninstall_nwave.py --dry-run

  # Keep logs after uninstall
  python uninstall_nwave.py --keep-logs
```

---

## Verification and Validation

### Preflight Checks (`scripts/install/preflight_checker.py`)

**Executed Before Installation**:

```python
class PreflightChecker:
    def check_python_version(self) -> bool:
        """Require Python >= 3.8"""
        ...

    def check_git_available(self) -> bool:
        """Git needed for version info"""
        ...

    def check_claude_config_dir(self) -> bool:
        """~/.claude must exist or be creatable"""
        ...

    def check_write_permissions(self) -> bool:
        """Must have write access to ~/.claude"""
        ...

    def check_disk_space(self) -> bool:
        """Require at least 50MB free space"""
        ...
```

**Failure Handling**: Any failed check aborts installation with clear error message.

### Post-Installation Verification (`scripts/install/installation_verifier.py`)

**Executed After Installation**:

```python
class InstallationVerifier:
    def verify_agents(self) -> VerificationResult:
        """Verify agents/ contains >= 10 .md files"""
        ...

    def verify_commands(self) -> VerificationResult:
        """Verify commands/nw/ contains >= 5 .md files"""
        ...

    def verify_templates(self) -> VerificationResult:
        """Verify templates/ contains >= 1 template file"""
        ...

    def verify_file_integrity(self) -> VerificationResult:
        """Check no empty files, no corruption"""
        ...
```

**Verification Report**:
```
✓ Agents: 15 files installed
✓ Commands: 20 files installed
✓ Templates: 1 file installed
✓ File integrity: All files valid
✓ Directory structure: Correct

Overall: PASSED
```

---

## Limitations

### Current Implementation Limitations

#### 1. No Selective Installation
- **Limitation**: Cannot install individual components
- **Impact**: Users must install all components even if they only need agents
- **Example**: Cannot run `python install_nwave.py --plugin=des`
- **Future**: Plugin system will enable `--plugin=` and `--exclude=` flags

#### 2. No Selective Uninstallation
- **Limitation**: All-or-nothing removal
- **Impact**: Cannot remove just DES while keeping agents/commands
- **Example**: Cannot run `python uninstall_nwave.py --component=des`
- **Future**: Plugin system will enable per-component uninstallation

#### 3. No Dependency Management
- **Limitation**: Installation order is hardcoded
- **Impact**: Cannot express dependencies between components
- **Example**: If utilities depend on templates, order must be manually maintained
- **Future**: Plugin registry with topological sort

#### 4. DES Hooks Separate from Main Installation
- **Limitation**: DES hooks require separate installation step
- **Impact**: Users might forget to run `install_des_hooks.py`
- **Example**: Framework installed but enforcement not active
- **Future**: DES as plugin will integrate hook installation

#### 5. Monolithic Installer Class
- **Limitation**: All installation logic in single `NWaveInstaller` class
- **Impact**: Difficult to test components in isolation
- **Example**: Cannot unit test agent installation without full installer setup
- **Future**: Plugin architecture with isolated, testable components

#### 6. No Plugin Discovery
- **Limitation**: Cannot discover or install third-party plugins
- **Impact**: Community cannot extend nWave with custom plugins
- **Future**: Plugin discovery mechanism and marketplace

#### 7. Limited Update Strategy
- **Limitation**: Only version-aware for utility scripts, not for agents/commands
- **Impact**: Agents always overwritten even if unchanged
- **Future**: Content hashing and selective updates

#### 8. No Configuration Management Per Component
- **Limitation**: No per-component configuration
- **Impact**: Cannot configure component behavior at install time
- **Example**: Cannot specify DES strictness level during installation
- **Future**: Plugin configuration system

---

## Future Evolution

### Path to Plugin System

This section describes how the current implementation will evolve into the plugin system described in `nwave-plugin-system-architecture.md`.

### Phase 1: Current State (✅ COMPLETED)

**Status**: This document describes the completed Phase 1.

**Characteristics**:
- ✅ Monolithic installer with helper methods
- ✅ Separate DES hook installer
- ✅ Utility classes extracted (`install_utils.py`)
- ✅ Sequential component installation
- ✅ All-or-nothing approach

### Phase 2: Plugin Infrastructure (❌ NOT STARTED)

**Goal**: Create plugin system foundation.

**Tasks**:
1. **Create Plugin Base Classes**
   - `InstallationPlugin` abstract base class
   - `PluginResult` dataclass for return values
   - `InstallContext` dataclass for dependency injection

2. **Implement Plugin Registry**
   - `PluginRegistry` class with dependency resolution
   - Topological sort using Kahn's algorithm
   - Plugin discovery mechanism

3. **Convert Existing Components to Plugins**
   - `AgentsPlugin` (extract from `_install_agents()`)
   - `CommandsPlugin` (extract from `_install_commands()`)
   - `UtilitiesPlugin` (extract from `_install_utility_scripts()`)
   - `TemplatesPlugin` (extract from `_install_templates()`)

4. **Implement DES Plugin**
   - `DESPlugin` integrating `install_des_hooks.py` logic
   - Declare dependencies on core plugins
   - Implement install/verify/uninstall

**Estimated Effort**: 2-3 weeks

### Phase 3: Integration (❌ NOT STARTED)

**Goal**: Replace monolithic logic with plugin system.

**Tasks**:
1. **Modify NWaveInstaller**
   - Replace `install_framework()` with `PluginRegistry.install_all()`
   - Add `--plugin=` and `--exclude=` CLI flags
   - Implement selective installation

2. **Modify NWaveUninstaller**
   - Add per-plugin uninstallation
   - Dependency checking for uninstall
   - Preserve dependent plugins

3. **Integration Testing**
   - Test selective installation
   - Test dependency resolution
   - Test plugin uninstallation

**Estimated Effort**: 1-2 weeks

### Phase 4: Advanced Features (⏳ FUTURE)

**Goal**: Enable ecosystem growth.

**Potential Features**:
- Dynamic plugin discovery from directories
- Plugin versioning and update system
- Plugin marketplace integration
- Third-party plugin packaging (.nwave format)
- Plugin configuration UI
- Remote plugin installation

**Timeline**: To be determined based on user demand.

---

## See Also

- **Future Design**: [nwave-plugin-system-architecture.md](./nwave-plugin-system-architecture.md) - Complete plugin system architecture
- **Development Guide**: [nwave-plugin-development-guide.md](./nwave-plugin-development-guide.md) - How to create plugins (future)
- **Summary**: [nwave-plugin-system-summary.md](./nwave-plugin-system-summary.md) - Executive summary of plugin system

---

**Document Status**: This document reflects the actual implementation as of 2026-02-03. It will be updated as the installer evolves toward the plugin system.
