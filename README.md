# AI-Craft: Intelligent ATDD Pipeline with Specialized Agent Network

<!-- version: 1.2.3 -->

🚀 **A systematic approach to software development using ATDD (Acceptance Test Driven Development) with intelligent AI agent orchestration**

## 🎯 Overview

AI-Craft is a comprehensive development pipeline that implements the 5-stage ATDD workflow through specialized AI agents, each following the Single Responsibility Principle. The system provides intelligent project analysis, automated workflow initiation, and systematic quality assurance.

### Core Philosophy

- **Outside-In Development**: Start with acceptance tests and work inward with mandatory 14-phase TDD discipline
- **Single Responsibility Principle**: Each agent has one focused responsibility
- **Clean Context Isolation**: Agents receive only essential context for their tasks
- **File-Based Handoffs**: Structured communication between pipeline stages
- **Systematic Quality**: Progressive refactoring (L1-L4) with comprehensive validation gates

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone <repository-url> ai-craft
cd ai-craft

# Run installation script
./scripts/install-ai-craft.sh
```

### Basic Usage

```bash
# Develop complete feature (automated DEVELOP wave)
/nw:develop "Build user authentication system"
  # Automatically: baseline → roadmap → split → execute all → finalize
  # Quality gates: 3 + 3N reviews per feature

# Execute specific step (11-phase TDD)
/nw:execute @software-crafter "docs/feature/auth/steps/01-02.json"
  # Automatic: PREPARE → RED → GREEN → REVIEW → REFACTOR → VALIDATE → COMMIT

# Manual workflow control (advanced)
/nw:discuss @requirements.txt
/nw:design "JWT authentication architecture"
/nw:baseline "Implement authentication"
/nw:roadmap @solution-architect "Implement authentication"
/nw:split @devop "authentication"
# ... execute individual steps ...
/nw:finalize @devop "authentication"
```

## 🏗️ ATDD Five-Stage Workflow

```
DISCUSS → DESIGN → DISTILL → DEVELOP → DELIVER
   ↓         ↓         ↓         ↓        ↓
business   solution  acceptance test-first feature
analyst    architect  designer  developer completion
```

The system orchestrates 41+ specialized AI agents across five stages, ensuring comprehensive coverage from requirements analysis to feature completion.

## 📚 Documentation

### 📦 Installation & Setup

- **[Installation Guide](docs/installation/INSTALL.md)** - Detailed installation instructions for all platforms
- **[Uninstallation Guide](docs/installation/UNINSTALL.md)** - Complete removal instructions

### 🔧 Troubleshooting

- **[Troubleshooting Guide](docs/troubleshooting/TROUBLESHOOTING.md)** - Common issues and solutions

### 📋 Additional Documentation

- **[Complete Agent Documentation](docs/)** - Detailed agent specifications and workflows
- **[CI/CD Integration](docs/CI-CD-README.md)** - Continuous integration setup
- **[Project Evolution](docs/evolution/)** - Framework enhancements and methodology integrations

## 🔧 Configuration

All agents reference shared constants for maintainability through the centralized configuration system.

## 🏢 Architecture

### Agent Organization (41+ Specialized Agents)

- **🟦 Requirements Analysis** (5 agents) - Business requirements and validation
- **🟧 Architecture Design** (3 agents) - Solution architecture and technology selection
- **❤️ Test Design** (1 agent) - Acceptance test scenarios
- **💚 Development** (1+ agents) - Test-first implementation
- **🟡 Validation & Quality** (15+ agents) - Comprehensive quality assurance
- **🟣 Coordination** (16+ agents) - Pipeline orchestration and state management

### File Structure

```
ai-craft/
├── nWave/                  # ATDD workflow agents and commands
│   ├── agents/               # Specialized agent definitions
│   ├── commands/             # Slash command definitions
│   └── data/                 # Reference data and research
├── docs/                     # All project documentation
│   ├── installation/         # Setup and installation guides
│   └── troubleshooting/      # Issue resolution guides
├── scripts/                  # Installation and utility scripts
└── README.md                 # This file
```

## 👨‍💻 Development & Build

### Building the Framework

After making changes to agents, commands, or other framework components, rebuild and install:

```bash
# Option 1: Full update (build + uninstall + install + validate)
./scripts/update-ai-craft.sh --force

# Option 2: With backup before update (recommended)
./scripts/update-ai-craft.sh --force --backup

# Option 3: Build only (without installing)
./scripts/build-ide-bundle.sh

# Option 4: Manual install after build
./scripts/install-ai-craft.sh
```

### Build Process Details

The build system (`tools/build_ide_bundle.py`) processes:
- **Agents**: Individual agent files with embedded dependencies → `dist/ide/agents/nw/`
- **Commands**: Task files converted to IDE commands
- **Teams**: Team configurations converted to collaborative agents
- **Workflows**: Workflow orchestrators for multi-phase guidance

### Update Process

The `update-ai-craft.sh` script orchestrates:
1. Build new framework bundle from source (`nWave/`)
2. Uninstall existing AI-Craft installation (cleanly removes from `~/.claude/`)
3. Install newly built framework bundle
4. Validate successful update (agents, commands, configuration)

## 🔧 Essential Scripts

The `scripts/` directory contains critical infrastructure scripts for building, installing, and managing the AI-Craft framework. These scripts are essential for the framework lifecycle.

### Core Scripts (Category 1)

#### 1. `build-ide-bundle.sh` (2.4KB)
**Purpose**: Build wrapper for Python build system

Orchestrates the complete build process, generating the IDE-ready bundle from source files.

**Usage**:
```bash
./scripts/build-ide-bundle.sh
```

**What it does**:
- Invokes Python build system (`tools/build_ide_bundle.py`)
- Processes agents, commands, and templates from `nWave/`
- Generates output in `dist/ide/` with proper IDE structure
- Validates build artifacts and reports statistics

**When to use**: After any modification to agents, commands, or framework components before installation.

---

#### 2. `install-ai-craft.sh` (15KB)
**Purpose**: Framework installation to Claude Code environment

Installs the built AI-Craft framework into Claude Code's agent directory (`~/.claude/`).

**Usage**:
```bash
# Standard installation
./scripts/install-ai-craft.sh

# Dry-run (preview what would be installed)
./scripts/install-ai-craft.sh --dry-run

# With backup before installation
./scripts/install-ai-craft.sh --backup
```

**What it does**:
- Validates build artifacts exist in `dist/ide/`
- Copies agents to `~/.claude/agents/nw/`
- Copies commands to `~/.claude/commands/nw/`
- Installs configuration files
- Verifies installation success
- Optional: Creates timestamped backup before installation

**When to use**: After building the framework or for fresh installations.

---

#### 3. `uninstall-ai-craft.sh` (13KB)
**Purpose**: Clean removal of AI-Craft framework

Completely removes AI-Craft installation from Claude Code environment.

**Usage**:
```bash
# Standard uninstall
./scripts/uninstall-ai-craft.sh

# Dry-run (preview what would be removed)
./scripts/uninstall-ai-craft.sh --dry-run

# With backup before uninstall (recommended)
./scripts/uninstall-ai-craft.sh --backup
```

**What it does**:
- Removes `~/.claude/agents/nw/` directory
- Removes `~/.claude/commands/nw/` directory
- Cleans up configuration files
- Optional: Creates timestamped backup before removal
- Verifies clean uninstallation

**When to use**: Before reinstalling, when switching versions, or for complete removal.

---

#### 4. `update-ai-craft.sh` (16KB)
**Purpose**: Orchestrates complete update workflow

End-to-end update automation: build → uninstall → install → validate.

**Usage**:
```bash
# Standard update
./scripts/update-ai-craft.sh --force

# With backup (recommended for production)
./scripts/update-ai-craft.sh --force --backup

# Dry-run (preview entire update process)
./scripts/update-ai-craft.sh --force --dry-run
```

**What it does**:
1. Validates source files in `nWave/`
2. Builds framework bundle via `build-ide-bundle.sh`
3. Uninstalls existing version via `uninstall-ai-craft.sh`
4. Installs new version via `install-ai-craft.sh`
5. Validates installation success
6. Reports update statistics

**When to use**: Recommended workflow for applying framework changes during development.

---

### Pre-commit Hooks

AI-Craft uses the [pre-commit](https://pre-commit.com/) framework for automated quality gates.

#### Installation (New Machine)

```bash
# Install pre-commit
pip install pre-commit

# OR with pipx (recommended)
pipx install pre-commit

# Activate hooks in repository
cd ai-craft
pre-commit install
```

#### Active Hooks

| Hook | Description |
|------|-------------|
| `nwave-version-bump` | Auto-increments version when nWave/tools files modified |
| `pytest-validation` | Runs full test suite (58 tests) |
| `docs-version-validation` | Validates documentation version sync |
| `ruff` | Python linting (replaces flake8, isort) |
| `ruff-format` | Python formatting (replaces black) |
| `trailing-whitespace` | Removes trailing whitespace |
| `end-of-file-fixer` | Ensures files end with newline |
| `check-yaml` | Validates YAML syntax |
| `check-json` | Validates JSON syntax |
| `check-merge-conflict` | Detects merge conflict markers |
| `detect-private-key` | Prevents committing private keys |

#### Manual Run

```bash
# Run all hooks on all files
pre-commit run --all-files

# Run specific hook
pre-commit run ruff --all-files
```

#### Hook Scripts (Versioned)

- `scripts/hooks/version-bump.sh` - Version auto-increment logic
- `scripts/hooks/validate-tests.sh` - Pytest validation wrapper
- `scripts/hooks/validate-docs.sh` - Documentation version validation

---

### Additional Validation Scripts

#### Validation Scripts (13KB total)
**Purpose**: Agent compliance and structure validation

Scripts:
- `validate-agent-compliance.py` (v1.0)
- `validate-agent-compliance-v2.py` (v2.0)
- `validate-agent-compliance.sh` (shell wrapper)
- `validate-reviewers.py` (reviewer agent validation)

---

#### Adversarial Security Testing (67KB total)
**Purpose**: Security framework validation through adversarial testing

Scripts:
- `run-adversarial-tests.py` (29KB) - 258 security tests across 4 categories
- `execute-adversarial-tests.py` (38KB) - Test execution framework

---

## 📋 Version Tracking System

AI-Craft uses **automated version tracking** to keep documentation synchronized with source configuration files. This system prevents documentation drift by enforcing version consistency through pre-commit validation.

### How It Works

The version tracking system maintains a dependency graph between source configurations and derived documentation:

**Source Files** (with version fields):
- `nWave/framework-catalog.yaml` - Primary framework configuration
- `tools/build_config.yaml` - Build system configuration

**Dependent Files** (synchronized automatically):
- `README.md` - Project documentation (this file)
- `nWave/data/agents_reference/COMMAND-AGENT-MAPPING.md` - Command mappings

**Pre-Commit Validation**:
1. Detects when source files are modified
2. Checks if version field was bumped (semantic versioning: MAJOR.MINOR.PATCH)
3. Checks if dependent files have outdated versions
4. Blocks commit if inconsistencies found
5. Provides structured JSON error messages for LLM-driven updates

### Development Workflow

When modifying framework configuration:

1. **Modify source file** (e.g., add command to `framework-catalog.yaml`)
2. **Bump version** in source file (e.g., `1.0.0` → `1.1.0`)
3. **Update dependent sections** in documentation files
4. **Bump versions** in dependent files to match
5. **Commit** - pre-commit validates automatically ✓

**Example**:
```bash
# 1. Edit framework-catalog.yaml (add new command)
# 2. Update version: "1.0.0" → "1.1.0"
# 3. Update README.md command examples section
# 4. Update README.md version: <!-- version: 1.0.0 --> → <!-- version: 1.1.0 -->
# 5. git commit (validation runs automatically)
```

### LLM-Driven Updates

When pre-commit validation fails, the hook outputs a structured JSON error message that LLMs can interpret:

```json
{
  "error_type": "VERSION_VALIDATION_FAILED",
  "errors": {
    "version_not_bumped": [...],
    "dependents_outdated": [...]
  },
  "resolution_steps": [...],
  "llm_guidance": {
    "files_to_edit": ["README.md"],
    "sections_to_update": [...],
    "validation": "Ensure all version fields updated"
  }
}
```

The LLM reads the error, updates the specified files and sections, bumps versions, and retries the commit.

### System Files

- **`.pre-commit-config.yaml`** - Pre-commit hooks configuration (versioned)
- **`.dependency-map.yaml`** - Dependency relationships and validation rules
- **`scripts/hooks/`** - Hook scripts (version-bump, validate-tests, validate-docs)
- **`scripts/validate-documentation-versions.py`** - Core validation engine

### Emergency Bypass

For emergency situations only:
```bash
git commit --no-verify -m "message"  # Bypasses BOTH test and version validation
```

**⚠️ WARNING**: Use sparingly. Bypassed commits require immediate follow-up to fix validation issues.

### Version Strategy

**Semantic Versioning (MAJOR.MINOR.PATCH)**:
- **MAJOR** - Breaking changes, incompatible API changes
- **MINOR** - New features, backward-compatible additions
- **PATCH** - Bug fixes, documentation corrections

### Adding Tracked Files

To track new files, edit `.dependency-map.yaml`:
```yaml
tracked_files:
  - path: "new-file.md"
    version_format: "markdown_comment"
    version_pattern: "<!-- version: {version} -->"
    triggers_update: [...]
```

---

## 🤝 Contributing

The AI-Craft system follows clean architecture principles with specialized agents. Each agent has a single responsibility and communicates through well-defined file-based interfaces.

## 📄 License

This project is open source. See the individual agent documentation for specific implementation details and usage patterns.

---

**For detailed information, see the comprehensive documentation in the [docs/](docs/) directory.**
