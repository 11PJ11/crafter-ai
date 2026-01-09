# AI-Craft: Intelligent ATDD Pipeline with Specialized Agent Network

🚀 **A systematic approach to software development using ATDD (Acceptance Test Driven Development) with intelligent AI agent orchestration**

## 🎯 Overview

AI-Craft is a comprehensive development pipeline that implements the 5-stage ATDD workflow through specialized AI agents, each following the Single Responsibility Principle. The system provides intelligent project analysis, automated workflow initiation, and systematic quality assurance.

### Core Philosophy

- **Outside-In Development**: Start with acceptance tests and work inward
- **Single Responsibility Principle**: Each agent has one focused responsibility
- **Clean Context Isolation**: Agents receive only essential context for their tasks
- **File-Based Handoffs**: Structured communication between pipeline stages
- **Systematic Quality**: Progressive refactoring and comprehensive validation

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
# Start ATDD workflow
/dw:start "Build user authentication system"

# Or process requirements
/dw:discuss @requirements.txt
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
├── 5d-wave/                  # ATDD workflow agents and commands
│   ├── agents/               # Specialized agent definitions
│   ├── commands/             # Slash command definitions
│   └── data/                 # Reference data and research
├── docs/                     # All project documentation
│   ├── installation/         # Setup and installation guides
│   └── troubleshooting/      # Issue resolution guides
├── scripts/                  # Installation and utility scripts
└── README.md                 # This file
```

## 🤝 Contributing

The AI-Craft system follows clean architecture principles with specialized agents. Each agent has a single responsibility and communicates through well-defined file-based interfaces.

## 📄 License

This project is open source. See the individual agent documentation for specific implementation details and usage patterns.

---

**For detailed information, see the comprehensive documentation in the [docs/](docs/) directory.**
# Test pre-commit hook execution
