# AI-Craft: Intelligent ATDD Pipeline with Specialized Agent Network

🚀 **A systematic approach to software development using ATDD (Acceptance Test Driven Development) with intelligent AI agent orchestration**

## 🎯 Overview

AI-Craft is a comprehensive development pipeline that implements the 5-stage ATDD workflow through specialized AI agents, each following the Single Responsibility Principle. The system provides intelligent project analysis, automated workflow initiation, and systematic quality assurance.

### Core Philosophy

- **Outside-In Development**: Start with acceptance tests and work inward with mandatory 11-phase TDD discipline
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

## 🤝 Contributing

The AI-Craft system follows clean architecture principles with specialized agents. Each agent has a single responsibility and communicates through well-defined file-based interfaces.

## 📄 License

This project is open source. See the individual agent documentation for specific implementation details and usage patterns.

---

**For detailed information, see the comprehensive documentation in the [docs/](docs/) directory.**
