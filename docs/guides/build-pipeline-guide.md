# nWave Build Pipeline Developer Guide

This guide explains the nWave build pipeline architecture and how to work with it for development and deployment.

## Pipeline Overview

The nWave framework has a three-stage build and installation pipeline:

```
nWave/ (source files)
    ├── agents/*.md
    ├── tasks/nw/*.md
    └── templates/*.json
         ↓
tools/build.py (main entry point)
         ↓
tools/core/build_ide_bundle.py (orchestrator)
         ↓
dist/ide/ (compiled output)
    ├── agents/nw/*.md
    ├── commands/nw/*.md
    └── templates/*.json
         ↓
scripts/install/install_nwave.py (installer)
         ↓
~/.claude/ (installed location)
    ├── agents/cai/
    └── commands/cai/
```

## File Paths

Understanding the correct file paths is critical for working with the build system:

### Entry Point
- **`tools/build.py`** - Main entry point for CLI usage
  - Simple wrapper that loads configuration and delegates to the builder
  - Use this when running builds from the command line
  - Command: `python3 tools/build.py --clean`

### Internal Builder Module
- **`tools/core/build_ide_bundle.py`** - Internal orchestrator
  - Contains the `IDEBundleBuilder` class
  - Used for programmatic access to build system
  - Referenced in Python code imports
  - Not invoked directly on CLI (use `tools/build.py` instead)

### Output Directory
- **`dist/ide/`** - Compiled output from build process
  - Generated files organized by platform
  - Contents copied by installer to `~/.claude/`
  - Regenerated on each clean build

## Building

### Manual Build

Build the framework from source:

```bash
# From repository root
python3 tools/build.py --clean
```

### Build Options

```bash
# Clean build (remove old output, rebuild from scratch)
python3 tools/build.py --clean

# Regular build (incremental, only process changed files)
python3 tools/build.py

# Verbose build (show detailed progress)
python3 tools/build.py --verbose

# Dry-run (show what would be built without creating files)
python3 tools/build.py --dry-run
```

### What Gets Built

The build process:

1. **Reads source** from `nWave/` directory
   - Agent markdown files (`agents/*.md`)
   - Task/command files (`tasks/nw/*.md`)
   - Framework templates (`templates/*.json`)
   - Shared data files (`data/`)

2. **Processes content** through specialized processors
   - `AgentProcessor` - Parses agent specifications and extracts metadata
   - `CommandProcessor` - Creates executable command tasks
   - `TeamProcessor` - Builds agent team compositions

3. **Generates output** to `dist/ide/` directory
   - `agents/nw/` - Processed agent files
   - `commands/nw/` - Processed command files
   - Maintains directory structure for organization

## Installation

### Automatic Build + Install

The installer automatically detects when sources are newer than the installed version and triggers a build:

```bash
# From repository root
python3 scripts/install/install_nwave.py
```

Installation process:

1. Checks if sources in `nWave/` are newer than `~/.claude/agents/cai/`
2. If sources are newer:
   - Runs `python3 tools/build.py --clean`
   - Waits for build to complete
3. Creates backup of existing installation (if any)
4. Copies `dist/ide/` contents to `~/.claude/agents/cai/` and `~/.claude/commands/cai/`
5. Validates installation
6. Reports success or failure

### Manual Install (Without Build)

If you've already built and just want to install:

```bash
python3 scripts/install/install_nwave.py
```

### Troubleshooting Installation

**Problem:** Installation says build failed
- **Check:** Did the build command complete successfully?
- **Fix:** Run `python3 tools/build.py --verbose` to see detailed errors

**Problem:** Old files still exist after installation
- **Check:** Did the installer copy all files?
- **Fix:** Check the installation log at `~/.claude/nwave-install.log`

## Development Workflow

### When to Rebuild

You need to rebuild (`python3 tools/build.py --clean`) when:

1. **Modifying agents** (`nWave/agents/*.md`)
2. **Modifying commands** (`nWave/tasks/nw/*.md`)
3. **Changing framework catalog** (`nWave/framework-catalog.yaml`)
4. **Adding/removing data files** (`nWave/data/`)
5. **Modifying processor logic** (`tools/processors/*.py`)

You do NOT need to rebuild when:

1. Changing documentation in `docs/`
2. Modifying tests in `tests/`
3. Changing CI/CD workflows in `.github/workflows/`

### Typical Development Loop

```bash
# 1. Make changes to nWave/ files
vim nWave/agents/researcher.md

# 2. Build to apply changes
python3 tools/build.py --clean

# 3. Install to your environment
python3 scripts/install/install_nwave.py

# 4. Test in Claude Code
cai/atdd --help

# 5. If build has issues, check verbose output
python3 tools/build.py --verbose
```

### Pre-commit Validation

The project includes pre-commit hooks that validate:

1. Framework catalog syntax
2. Agent name synchronization
3. Documentation version consistency
4. Python code formatting (ruff)

Install hooks:

```bash
pip install pre-commit
pre-commit install
```

Run validation manually:

```bash
pre-commit run --all-files
```

## Build System Architecture

### Key Components

**Entry Point** (`tools/build.py`)
- Minimal wrapper around the builder
- Parses CLI arguments
- Delegates to `IDEBundleBuilder`
- Handles exit codes and error reporting

**Orchestrator** (`tools/core/build_ide_bundle.py`)
- Contains `IDEBundleBuilder` class
- Coordinates the build workflow
- Manages file I/O and output directories
- Delegates processing to specialized processors

**Processors** (`tools/processors/`)
- `agent_processor.py` - Parses agent markdown and extracts metadata
- `command_processor.py` - Generates executable command tasks
- `team_processor.py` - Builds agent team compositions

**Utilities** (`tools/utils/`)
- `config_manager.py` - Loads and validates framework configuration
- `file_manager.py` - Handles file operations with dry-run support
- `dependency_resolver.py` - Resolves file dependencies and includes

### Data Flow

1. **Load Configuration**
   - Read `nWave/framework-catalog.yaml`
   - Extract version, platforms, agents, commands

2. **Process Agents**
   - Read each `nWave/agents/*.md`
   - Extract YAML frontmatter
   - Validate agent specification
   - Write to `dist/ide/agents/nw/`

3. **Process Commands**
   - Read each `nWave/tasks/nw/*.md`
   - Generate task metadata
   - Write to `dist/ide/commands/nw/`

4. **Process Templates**
   - Copy templates to output
   - Update references as needed

5. **Validate Output**
   - Verify all required files exist
   - Check file integrity
   - Report build statistics

## CI/CD Integration

### Automated Builds

The GitHub Actions CI/CD pipeline automatically:

1. **On every push/PR:**
   - Runs pre-commit validation
   - Executes pytest test suite
   - Validates agent synchronization
   - Checks documentation version consistency

2. **On version tags:**
   - Triggers build: `python3 tools/build.py --clean`
   - Creates release packages
   - Generates checksums
   - Creates GitHub release with artifacts

See [CI-CD-README.md](../CI-CD-README.md) for complete CI/CD documentation.

## Troubleshooting

### Build Fails

**Symptom:** Build command exits with error

```bash
# Get detailed error information
python3 tools/build.py --verbose
```

Common issues:

1. **Agent markdown parsing error**
   - Check YAML frontmatter syntax in agent file
   - Ensure required fields exist

2. **Missing source files**
   - Verify `nWave/` directory exists
   - Check file paths match processor expectations

3. **Permission denied**
   - Ensure write access to `dist/` directory
   - Check filesystem permissions

4. **Python import errors**
   - Verify all processor modules exist
   - Check Python path configuration

### Installation Fails After Build

**Check build output first:**

```bash
# Build succeeded but install failed?
python3 tools/build.py --verbose
ls -la dist/ide/
```

**Common issues:**

1. **Build files not created**
   - Verify build completed successfully
   - Check `dist/ide/` has expected content

2. **Permission denied writing to `~/.claude/`**
   - Check directory permissions
   - Ensure write access to home directory

3. **Installation validation fails**
   - Check installation log: `~/.claude/nwave-install.log`
   - Verify all required directories created

### Installer Triggers Build Automatically

The installer automatically runs a build if needed:

```bash
# This will:
# 1. Check if nWave/ is newer than ~/.claude/agents/cai/
# 2. If yes, run: python3 tools/build.py --clean
# 3. Then install the results
python3 scripts/install/install_nwave.py
```

If you see "Build in progress..." messages, the installer detected source changes and triggered an automatic build.

## Performance Optimization

### Clean vs Incremental Builds

**Clean Build** (slower, safer):
```bash
python3 tools/build.py --clean
```
- Removes all previous output
- Rebuilds everything from scratch
- Guarantees fresh output
- Use when:
  - Upgrading versions
  - After major source changes
  - For releases

**Incremental Build** (faster):
```bash
python3 tools/build.py
```
- Only processes changed files
- Skips unchanged content
- Faster iteration during development
- Use when:
  - Making small changes
  - Testing individual agents
  - During active development

### Build Time Targets

- **Incremental build:** < 5 seconds
- **Clean build:** 10-30 seconds (depends on agent count)
- **Installation:** 5-15 seconds

If builds are taking longer, check:
1. Filesystem performance (SSD vs HDD)
2. System load
3. Antivirus scanning overhead
4. Python startup time

## Common Patterns

### Update a Single Agent

```bash
# 1. Edit the agent
vim nWave/agents/researcher.md

# 2. Build (processes changed files)
python3 tools/build.py

# 3. Install
python3 scripts/install/install_nwave.py

# 4. Test in Claude Code
cai/atdd --help
```

### Create a New Agent

```bash
# 1. Create agent file
cp nWave/agents/template.md nWave/agents/new-agent.md
vim nWave/agents/new-agent.md

# 2. Add to framework catalog
vim nWave/framework-catalog.yaml  # Add entry to agents section

# 3. Build
python3 tools/build.py --clean

# 4. Install
python3 scripts/install/install_nwave.py
```

### Create a New Command

```bash
# 1. Create command task file
touch nWave/tasks/nw/new-command.md
vim nWave/tasks/nw/new-command.md

# 2. Add to framework catalog
vim nWave/framework-catalog.yaml  # Add entry to commands section

# 3. Build
python3 tools/build.py --clean

# 4. Install
python3 scripts/install/install_nwave.py
```

## Environment Variables

Optional environment variables for build customization:

```bash
# Increase logging verbosity
export NWAVE_LOG_LEVEL=DEBUG

# Override source directory
export NWAVE_SOURCE_DIR=/custom/nWave

# Override output directory
export NWAVE_OUTPUT_DIR=/custom/dist

# Disable color output (for CI/CD)
export NWAVE_NO_COLOR=1
```

## Next Steps

- Read [CI-CD-README.md](../CI-CD-README.md) for automated build/release workflows
- See [Creating Agents Guide](creating-agents.md) for agent development
- Check [Creating Commands Guide](creating-commands.md) for command development
- Review [CONTRIBUTING.md](../../CONTRIBUTING.md) for contribution guidelines

---

For questions or issues with the build pipeline, please open an issue on GitHub with:
- Build command used
- Output of `python3 tools/build.py --verbose`
- Python version: `python3 --version`
- Platform: Windows/macOS/Linux
