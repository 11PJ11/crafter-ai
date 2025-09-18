# AI-Craft Framework Installation Guide

This guide helps you install the AI-Craft ATDD framework to your global Claude config directory, making all 41+ specialized agents and the `cai/atdd` command available across all your projects.

## Quick Start

### Windows Users

**Option 1: PowerShell (Recommended)**
```powershell
.\install-ai-craft.ps1
```

**Option 2: Command Prompt**
```cmd
install-ai-craft.bat
```

### macOS/Linux Users

```bash
chmod +x install-ai-craft.sh
./install-ai-craft.sh
```

## What Gets Installed

### Framework Components
- **41+ Specialized AI Agents** organized in 9 color-coded categories
- **cai/atdd Command Interface** with intelligent project analysis
- **Wave Processing Architecture** with clean context isolation
- **Centralized Configuration System** (constants.md)
- **Quality Validation Network** with Level 1-6 refactoring
- **Auto-Lint and Format Hooks** for code quality (Python, JavaScript, JSON, etc.)
- **Second Way DevOps**: Observability agents (metrics, logs, traces, performance)
- **Third Way DevOps**: Experimentation agents (A/B testing, hypothesis validation, learning synthesis)

### Agent Categories
- 🟦 **Requirements Analysis** (5 agents) - Business requirements, UX, Security, Legal
- 🟧 **Architecture Design** (3 agents) - System design, technology selection
- ❤️ **Test Design** (1 agent) - Acceptance test creation
- 🟢 **Development** (1 agent) - Outside-in TDD implementation
- ❤️ **Quality Validation** (8 agents) - Comprehensive quality assurance
- 🔵 **Refactoring** (2 agents) - Systematic code improvement
- ⚫ **Coordination** (11 agents) - Workflow orchestration
- 📊 **Observability** (4 agents) - Second Way DevOps monitoring and feedback
- 🧪 **Experimentation** (4 agents) - Third Way DevOps learning and optimization

### Installation Location
```
~/.claude/                           # Global Claude config directory
├── agents/
│   └── cai/                        # AI-Craft agent specifications
│       ├── constants.md            # Centralized configuration
│       ├── requirements-analysis/  # Blue family agents (5)
│       ├── architecture-design/    # Orange family agents (3)
│       ├── test-design/           # Test design agents (1)
│       ├── development/           # Development agents (1)
│       ├── quality-validation/    # Quality validation agents (8)
│       ├── refactoring/           # Refactoring agents (2)
│       ├── coordination/          # Coordination agents (11)
│       ├── observability/         # Second Way DevOps agents (4)
│       ├── experimentation/       # Third Way DevOps agents (4)
│       └── legacy-agents/         # Deprecated agents
└── commands/                       # Command integrations
    └── cai/
        ├── atdd.md               # Main ATDD workflow command
        └── root-why.md           # Root cause analysis command
```

## Installation Options

### Standard Installation
Installs the complete framework with automatic backup:
```bash
./install-ai-craft.sh                    # macOS/Linux
.\install-ai-craft.ps1                   # Windows PowerShell
install-ai-craft.bat                     # Windows Command Prompt
```

### Backup Only
Creates backup without installing (useful before upgrades):
```bash
./install-ai-craft.sh --backup-only      # macOS/Linux
.\install-ai-craft.ps1 -BackupOnly       # Windows PowerShell
install-ai-craft.bat --backup-only       # Windows Command Prompt
```

### Restore Previous Installation
Restores from the most recent backup:
```bash
./install-ai-craft.sh --restore          # macOS/Linux
.\install-ai-craft.ps1 -Restore          # Windows PowerShell
install-ai-craft.bat --restore           # Windows Command Prompt
```

### Help
Shows detailed usage information:
```bash
./install-ai-craft.sh --help             # macOS/Linux
.\install-ai-craft.ps1 -Help             # Windows PowerShell
install-ai-craft.bat --help              # Windows Command Prompt
```

## What Gets Excluded

The installation script **excludes** project-specific files:
- `README.md` (main project documentation)
- `.claude/agents/cai/README.md` (agent overview documentation)
- `docs/craft-ai/` directory (project working files)
- Git configuration and project metadata

This ensures a clean separation between the reusable framework and project-specific documentation.

## Installation Features

### Automatic Backup
- Creates timestamped backup of existing installation
- Preserves customizations and previous versions
- Enables easy rollback if needed

### Validation
- Verifies all framework files are copied correctly
- Checks agent category structure
- Validates core components (constants.md, cai/atdd command)
- Generates installation manifest

### Cross-Platform Compatibility
- **Bash script** for macOS/Linux systems
- **PowerShell script** for modern Windows systems
- **Batch script** for legacy Windows systems
- Consistent behavior across all platforms

### Error Handling
- Comprehensive error checking and reporting
- Graceful failure with helpful messages
- Automatic cleanup on errors
- Rollback capability

## Usage After Installation

### Command Interface
Use the `cai/atdd` command in any project:
```bash
# Basic workflow initiation with project analysis
cai/atdd "implement user authentication system"

# Explicit project analysis
cai/atdd "add payment processing" --analyze-existing

# Start from specific ATDD stage
cai/atdd "OAuth2 integration" --from-stage=architect

# Resume existing workflow
cai/atdd --resume auth-feature-2024-01

# Check workflow status
cai/atdd --status

# Get help
cai/atdd --help
```

### Global Agent Access
All 41+ agents are available globally:
- Access specialized expertise (UX, Security, Legal, DevOps) when needed
- Use centralized configuration across all projects
- Benefit from wave processing architecture
- Apply systematic quality validation
- Leverage Second Way observability and monitoring
- Enable Third Way experimentation and continuous learning

## Troubleshooting

### Permission Issues
If you encounter permission errors:
```bash
# macOS/Linux: Make script executable
chmod +x install-ai-craft.sh

# Windows: Run as Administrator if needed
# Right-click → "Run as administrator"
```

### Path Issues
If the script can't find the framework source:
```bash
# Ensure you're running from the ai-craft project directory
cd /path/to/ai-craft
./install-ai-craft.sh
```

### Existing Installation
If you have an existing installation:
- The script automatically creates a backup
- You can restore with `--restore` option
- Check `~/.claude/backups/` for backup files

### Validation Failures
If installation validation fails:
- Check the installation log: `~/.claude/ai-craft-install.log`
- Verify source framework is complete
- Use `--restore` to rollback
- Report issues with log details

## Uninstallation

To remove the AI-Craft framework:
```bash
# Remove framework directories
rm -rf ~/.claude/agents/
rm -rf ~/.claude/commands/cai/

# Or restore from a pre-installation backup
./install-ai-craft.sh --restore
```

## Updates

To update to a newer version:
1. Download the latest AI-Craft framework
2. Run the installation script (creates automatic backup)
3. The new version overwrites the old installation
4. Use `--restore` if you need to rollback

## Support

- **Documentation**: Complete framework documentation in this repository
- **Issues**: Report problems on GitHub
- **Help**: Use `cai/atdd --help` for command help
- **Logs**: Check `~/.claude/ai-craft-install.log` for installation details

---

**Next Steps**: After installation, navigate to any project and use `cai/atdd "your feature description"` to start your first ATDD workflow with intelligent project analysis!