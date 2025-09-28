# 5D-WAVE IDE Bundle Builder

Python build system that transforms 5D-WAVE methodology source files into IDE-compatible distributions organized under the "dw" category.

## Overview

This build system processes the complete 5D-WAVE methodology structure and generates IDE-compatible bundles:

- **Agents**: Individual agent files with embedded dependencies → `dist/ide/agents/dw/`
- **Commands**: Task files converted to IDE commands → `dist/ide/commands/dw/`
- **Teams**: Team configurations converted to massive agents → `dist/ide/agents/dw/{team}-team.md`
- **Workflows**: Workflow orchestrators → `dist/ide/agents/dw/{workflow}-orchestrator.md`
- **Configuration**: Central IDE configuration → `dist/ide/agents/dw/config.json`

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
python build.py --source-dir ../5d-wave --output-dir ../dist/ide

# Clean build
python build.py --clean

# Dry run (show what would be built)
python build.py --dry-run

# Verbose output
python build.py --verbose
```

## Architecture

### Core Components

#### Main Orchestrator (`build_ide_bundle.py`)

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
- **ConfigManager**: Manages 5D-WAVE configuration loading and IDE config generation
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

### Build Configuration (`build_config.yaml`)

Comprehensive configuration file controlling all aspects of the build process:

```yaml
build:
  source_dir: "5d-wave"
  output_dir: "dist/ide"
  incremental: true
  validate_dependencies: true

processing:
  agents:
    embed_dependencies: true
    resolve_placeholders: true
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

### 5D-WAVE Configuration (`5d-wave/config.yaml`)

Source configuration defining the methodology structure:

- **Agents**: Wave assignments, roles, priorities
- **Commands**: Descriptions, wave mappings, expected outputs
- **Teams**: Collaboration patterns, agent compositions
- **Workflows**: Phase definitions, orchestration logic

## Output Structure

```
dist/ide/
├── agents/dw/
│   ├── business-analyst.md              # Individual agents
│   ├── solution-architect.md
│   ├── 5d-wave-core-team.md           # Teams as massive agents
│   ├── greenfield-orchestrator.md      # Workflow orchestrators
│   └── config.json                     # Central configuration
└── commands/dw/
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

- Processes 5D-WAVE methodology phases: DISCUSS → DESIGN → DISTILL → DEVELOP → DEMO
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
- Organizes all components under "dw" category
- Provides central configuration for IDE consumption

## Command Line Options

```bash
python build.py [options]

Options:
  --source-dir PATH     Source directory (default: 5d-wave)
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
2. Update `build_config.yaml` with new source directory
3. Add format handling in `format_content_for_embedding()`

### Testing

```bash
# Run with dry-run to test without file creation
python build.py --dry-run --verbose

# Test specific components
python -m pytest tests/ --cov=processors/

# Validate configuration
python -c "from utils.config_manager import ConfigManager; cm = ConfigManager('5d-wave/config.yaml'); print(cm.validate_configuration())"
```

## Troubleshooting

### Build Failures

1. **Check Prerequisites**: Ensure Python 3.8+ and PyYAML are installed
2. **Verify Source Structure**: Confirm 5d-wave/ directory contains required files
3. **Check Permissions**: Ensure write access to output directory
4. **Review Logs**: Check `build.log` for detailed error information

### Validation Errors

1. **Missing Sections**: Add required sections to `5d-wave/config.yaml`
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
5. Maintain backward compatibility with existing 5D-WAVE structures
