<!-- version: 1.4.0 -->

# nWave IDE Bundle Builder

Python build system that transforms nWave methodology source files into IDE-compatible distributions organized under the "nw" category.

## Overview

This build system processes the complete nWave methodology structure and generates IDE-compatible bundles:

- **Agents**: Individual agent files with embedded dependencies → `dist/ide/agents/nw/`
- **Commands**: Task files converted to IDE commands → `dist/ide/commands/nw/`
- **Teams**: Team configurations converted to massive agents → `dist/ide/agents/nw/{team}-team.md`
- **Workflows**: Workflow orchestrators → `dist/ide/agents/nw/{workflow}-orchestrator.md`
- **Configuration**: Central IDE configuration → `dist/ide/agents/nw/config.json`

## Quick Start

### Prerequisites

- Python 3.8+
- PyYAML package

### Installation

```bash
cd tools/
pip install -r requirements.txt
```

### Basic Usage

```bash
# Build with default settings
python build.py

# Build with custom directories
python build.py --source-dir ../nWave --output-dir ../dist/ide

# Clean build
python build.py --clean

# Dry run (show what would be built)
python build.py --dry-run

# Verbose output
python build.py --verbose
```

## Architecture

### Directory Structure

```
tools/
├── README.md                 # This file
├── build.py                  # Entry point - run this to build
├── requirements.txt          # Python dependencies
├── core/                     # Core build system
│   ├── build_ide_bundle.py   # Main orchestrator
│   ├── embed_sources.py      # Source embedding utility
│   └── build_config.yaml.reference  # Configuration reference (not used)
├── processors/               # Content processors
│   ├── agent_processor.py
│   ├── command_processor.py
│   ├── team_processor.py
│   └── workflow_processor.py
└── utils/                    # Utility modules
    ├── config_manager.py
    ├── dependency_resolver.py
    └── file_manager.py
```

### Core Components

#### Entry Point (`build.py`)

- Simple wrapper that imports and runs the main builder
- Provides clean command-line interface
- Handles Python path setup

#### Main Orchestrator (`core/build_ide_bundle.py`)

- Coordinates the entire build process
- Manages validation, preparation, and processing phases
- Handles error reporting and build statistics

#### Processing Modules (`processors/`)

- **AgentProcessor**: Processes agent `.md` files with embedded YAML configurations
- **CommandProcessor**: Converts task files to IDE commands with wave assignments
- **TeamProcessor**: Transforms team configurations into massive collaborative agents
- **WorkflowProcessor**: Converts workflows into orchestrator agents for multi-phase guidance

#### Utility Modules (`utils/`)

- **FileManager**: Handles all file I/O operations with dry-run support
- **ConfigManager**: Manages nWave configuration loading and IDE config generation
- **DependencyResolver**: Resolves and embeds dependencies with proper formatting

### Processing Flow

1. **Validation**: Verify source directory structure and required files
2. **Preparation**: Create output directory structure
3. **Agent Processing**: Process individual agents with dependency embedding
4. **Command Processing**: Convert tasks to commands with wave metadata
5. **Team Processing**: Transform teams into massive agents
6. **Workflow Processing**: Convert workflows to orchestrator agents
7. **Configuration**: Generate central IDE configuration file

## Configuration

### Framework Catalog (`nWave/framework-catalog.yaml`)

The build system reads its configuration from `nWave/framework-catalog.yaml`, which defines:

```yaml
version: "1.2.26"

wave_phases:
  - discuss
  - design
  - distill
  - develop
  - deliver

agents:
  business-analyst:
    wave: discuss
    role: "Requirements gathering"
  # ... more agents

commands:
    add_wave_headers: true
  teams:
    convert_to_agents: true
  workflows:
    convert_to_orchestrators: true

validation:
  required_sections:
    - "wave_phases"
    - "agents"
    - "commands"
```

### nWave Configuration (`nWave/config.yaml`)

Source configuration defining the methodology structure:

- **Agents**: Wave assignments, roles, priorities
- **Commands**: Descriptions, wave mappings, expected outputs
- **Teams**: Collaboration patterns, agent compositions
- **Workflows**: Phase definitions, orchestration logic

## Output Structure

```
dist/ide/
├── agents/nw/
│   ├── business-analyst.md              # Individual agents
│   ├── solution-architect.md
│   ├── nWave-core-team.md           # Teams as massive agents
│   ├── greenfield-orchestrator.md      # Workflow orchestrators
│   └── config.json                     # Central configuration
└── commands/nw/
    ├── dw-start.md                      # Wave commands
    ├── dw-discuss.md
    ├── dw-design.md
    ├── dw-distill.md
    ├── dw-develop.md
    └── dw-demo.md
```

## Features

### Dependency Embedding

- Automatically resolves and embeds dependencies from tasks/, templates/, checklists/, data/
- Supports multiple content formats (YAML, Markdown, JSON, etc.)
- Resolves {root} placeholders to appropriate paths

### Wave Integration

- Processes nWave methodology phases: DISCUSS → DESIGN → DISTILL → DEVELOP → DEMO
- Assigns agents to waves based on configuration
- Generates wave-specific command headers and metadata

### Team Collaboration

- Converts team configurations into massive agents with embedded coordination logic
- Preserves collaboration patterns and workflow orchestration
- Maintains agent composition and priority information

### Quality Assurance

- Comprehensive validation of source structure and dependencies
- Error handling with detailed reporting
- Configurable quality gates and success criteria

### IDE Compatibility

- Generates clean, individual files suitable for IDE integration
- Organizes all components under "nw" category
- Provides central configuration for IDE consumption

## Command Line Options

```bash
python build.py [options]

Options:
  --source-dir PATH     Source directory (default: nWave)
  --output-dir PATH     Output directory (default: dist/ide)
  --clean              Clean output directory before build
  --verbose, -v        Enable verbose logging
  --dry-run            Show what would be built without creating files
  --help               Show help message
```

## Error Handling

### Common Issues

1. **Missing Dependencies**
   - Identifies missing files referenced in agent configurations
   - Provides specific paths and suggestions for resolution

2. **Invalid YAML Configuration**
   - Reports parsing errors with file and line information
   - Continues processing other files when possible

3. **File Access Errors**
   - Handles permission issues and path problems
   - Provides clear error messages and suggested fixes

### Validation

- **Source Structure**: Verifies required directories and files exist
- **Configuration**: Validates YAML syntax and required sections
- **Dependencies**: Checks that all referenced files can be resolved
- **Output**: Verifies generated files meet IDE requirements

## Development

### Adding New Processors

1. Create new processor in `processors/` directory
2. Inherit from base patterns used by existing processors
3. Implement required methods: `process_*()` and `get_*_info()`
4. Update main orchestrator to include new processor

### Extending Dependency Types

1. Add new type mapping in `DependencyResolver.dependency_mappings`
2. Update `nWave/framework-catalog.yaml` with agent/command definitions
3. Add format handling in `format_content_for_embedding()`

### Testing

```bash
# Run with dry-run to test without file creation
python build.py --dry-run --verbose

# Test specific components
python -m pytest tests/ --cov=processors/

# Validate configuration
python -c "from utils.config_manager import ConfigManager; cm = ConfigManager('nWave/config.yaml'); print(cm.validate_configuration())"
```

## Troubleshooting

### Build Failures

1. **Check Prerequisites**: Ensure Python 3.8+ and PyYAML are installed
2. **Verify Source Structure**: Confirm nWave/ directory contains required files
3. **Check Permissions**: Ensure write access to output directory
4. **Review Logs**: Check `build.log` for detailed error information

### Validation Errors

1. **Missing Sections**: Add required sections to `nWave/config.yaml`
2. **Invalid Wave Assignments**: Ensure agent waves match defined wave_phases
3. **Broken Dependencies**: Fix file paths in agent dependency configurations

### Output Issues

1. **Missing Files**: Check that all processors completed successfully
2. **Invalid Content**: Verify source files have proper formatting
3. **IDE Integration**: Ensure output structure matches expected IDE requirements

## Contributing

1. Follow existing code patterns and documentation standards
2. Add comprehensive error handling and logging
3. Update configuration files when adding new features
4. Test with both clean builds and incremental updates
5. Maintain backward compatibility with existing nWave structures
