# nWave IDE Integration Bundling Algorithm

## Overview

This document defines the algorithm for generating IDE-compatible distributions from nWave methodology source files. The algorithm focuses on creating individual agent and command files suitable for IDE integration, specifically designed for Claude Code and similar development environments.

## Goals

- **Generate individual agent files** with embedded dependencies for IDE consumption
- **Convert tasks to commands** for direct IDE execution
- **Transform workflows into orchestrator agents** for multi-phase guidance
- **Process agent-teams into collaborative configurations** for team-based development
- **Language-agnostic implementation** suitable for any programming language

## Core Processing Components

### 1. Agents (Primary Output)

- **Input**: `nWave/agents/{agent}.md`
- **Output**: Individual `.md` files with all dependencies embedded
- **Purpose**: Self-contained agent files ready for IDE integration

### 2. Commands (Secondary Output)

- **Input**: `nWave/tasks/{task}.md`
- **Output**: Command files with embedded dependencies
- **Purpose**: Direct task execution through IDE commands

### 3. Orchestrator Agents (Workflow-Based)

- **Input**: `nWave/workflows/{workflow}.yaml`
- **Output**: Agent files that guide multi-phase processes
- **Purpose**: Coordinate complex multi-wave processes

### 4. Agent Teams (Collaborative Configurations)

- **Input**: `nWave/agent-teams/{team}.yaml`
- **Output**: Team configuration files for collaborative development
- **Purpose**: Enable coordinated multi-agent workflows

### 5. Configuration Processing

- **Input**: `nWave/config.yaml`
- **Output**: IDE-compatible configuration with agent mappings
- **Purpose**: Central configuration for methodology execution

## Algorithm Implementation

### Step 1: Agent Processing

```pseudocode
FOR each agent_file in nWave/agents/*.md:
    1. Parse agent embedded YAML configuration block
    2. Extract dependencies section from YAML
    3. FOR each dependency_type in [tasks, templates, checklists, data]:
        a. Load all referenced files of dependency_type from nWave/{type}/
        b. Embed content directly in agent file
        c. Preserve original format (YAML as code blocks, MD as sections)
    4. Replace {root} placeholders with nWave-specific paths
    5. Generate output file: dist/ide/dw/agents/{agent-id}.md
```

**Example Input Dependencies**:

```yaml
dependencies:
  tasks:
    - requirements-gathering.md
    - stakeholder-facilitation.md
  templates:
    - requirements-document-tmpl.yaml
    - user-story-tmpl.yaml
  checklists:
    - requirements-completeness-checklist.md
  data:
    - methodology-guide.md
```

**Example Output Structure**:

````markdown
# business-analyst

[Original agent content...]

## Embedded Tasks

### requirements-gathering.md

[Full task content embedded here...]

### stakeholder-facilitation.md

[Full task content embedded here...]

## Embedded Templates

### requirements-document-tmpl.yaml

```yaml
[Full YAML template content...]
```
````

### user-story-tmpl.yaml

```yaml
[Full YAML template content...]
```

## Embedded Checklists

### requirements-completeness-checklist.md

[Full checklist content...]

## Embedded Data

### methodology-guide.md

[Full data content...]

````

### Step 2: Command Processing

```pseudocode
FOR each task_file in nWave/tasks/*.md:
    1. Load task file content
    2. Parse any task dependencies (if present)
    3. FOR each dependency:
        a. Load and embed dependency content from nWave/{type}/
        b. Maintain content type formatting
    4. Add command header wrapper with wave assignment from config.yaml
    5. Generate output file: dist/nWave/ide/commands/{task-id}.md
````

**Command Header Template**:

```markdown
# /{task-id} Command

## Command Description

[Task description and usage...]

## Implementation

[Original task content with embedded dependencies...]
```

### Step 3: Workflow to Orchestrator Agent Conversion

```pseudocode
FOR each workflow_file in expansion-packs/{pack}/workflows/*.yaml:
    1. Parse workflow YAML structure
    2. Extract phases, agents, and orchestration logic
    3. Generate agent personality that can guide workflow execution
    4. Embed workflow definition as agent knowledge
    5. Create agent instructions for each workflow phase
    6. Generate output file: {pack}/ide/agents/{workflow-name}-orchestrator.md
```

**Orchestrator Agent Template**:

````markdown
# {workflow-name}-orchestrator

## Agent Identity

You are a workflow orchestrator for the {workflow-name} methodology...

## Workflow Definition

```yaml
[Embedded workflow YAML...]
```
````

## Phase Guidance

[Generated guidance for each workflow phase...]

## Available Agents

[List of agents involved in this workflow...]

`````

## Content Embedding Rules

### YAML Content Embedding
- **Source**: Files with `.yaml` extension
- **Format**: Embedded as fenced code blocks
- **Syntax**: ````yaml ... ````
- **Preservation**: Maintain full YAML structure and formatting

### Markdown Content Embedding
- **Source**: Files with `.md` extension
- **Format**: Embedded directly as markdown sections
- **Headers**: Add appropriate section headers for organization
- **Structure**: Preserve original markdown formatting

### Mixed Dependencies Organization
```markdown
## Embedded Tasks
[All task dependencies...]

## Embedded Templates
[All template dependencies...]

## Embedded Checklists
[All checklist dependencies...]

## Embedded Data
[All data dependencies...]
`````

## Output Directory Structure

```
dist/expansion-packs/{pack-name}/ide/
├── agents/
│   ├── business-analyst.md              # Agent with embedded dependencies
│   ├── solution-architect.md            # Agent with embedded dependencies
│   ├── acceptance-designer.md           # Agent with embedded dependencies
│   ├── nWave-complete-orchestrator.md # Workflow converted to agent
│   ├── atdd-focused-orchestrator.md     # Workflow converted to agent
│   └── visual-architecture-orchestrator.md
├── commands/
│   ├── dw-start.md                      # Task converted to command
│   ├── dw-discuss.md                    # Task converted to command
│   ├── dw-design.md                     # Task converted to command
│   ├── dw-distill.md                    # Task converted to command
│   ├── dw-develop.md                    # Task converted to command
│   ├── dw-demo.md                       # Task converted to command
│   ├── mikado.md                        # Specialized command
│   ├── skeleton.md                      # Specialized command
│   └── root-why.md                      # Specialized command
└── install-guide.md                     # Installation instructions for IDE
```

## Key Differences from Web Builder

| Aspect            | Web Builder               | IDE Builder                      |
| ----------------- | ------------------------- | -------------------------------- |
| **Output Format** | Monolithic `.txt` bundles | Individual `.md` files           |
| **Teams**         | Aggregated team bundles   | Discarded concept                |
| **Workflows**     | Embedded resources        | Converted to orchestrator agents |
| **Dependencies**  | Section separators        | Clean markdown embedding         |
| **Resolution**    | Runtime via separators    | Build-time embedding             |
| **File Access**   | Bundle sections           | File system access               |

## Implementation Requirements

### Language-Agnostic Dependencies

- **YAML Parser**: For parsing agent configurations and workflow definitions
- **File System Operations**: For reading source files and writing output
- **Text Processing**: For content manipulation and template generation
- **Markdown Generation**: For creating well-formatted output files

### Core Algorithm Components

1. **Dependency Resolver**: Parse YAML dependencies and locate files
2. **Content Embedder**: Embed referenced content with proper formatting
3. **Path Resolver**: Replace placeholders with appropriate paths
4. **File Generator**: Create output files with proper structure

### Error Handling

- **Missing Dependencies**: Log warnings for missing referenced files
- **Invalid YAML**: Handle malformed agent configurations gracefully
- **File Access**: Handle permission and path issues
- **Content Validation**: Ensure embedded content maintains integrity

## Validation and Testing

### Output Validation

- **File Structure**: Verify correct directory structure creation
- **Content Integrity**: Ensure all dependencies are properly embedded
- **Format Compliance**: Validate markdown and YAML formatting
- **Path Resolution**: Confirm all {root} placeholders are resolved

### Integration Testing

- **IDE Compatibility**: Test with Claude Code and similar IDEs
- **Agent Functionality**: Verify agents work with embedded dependencies
- **Command Execution**: Ensure commands execute properly in IDE context
- **Orchestrator Behavior**: Validate workflow orchestration agents

## Future Considerations

### Extensibility

- **Custom Dependency Types**: Support for additional dependency categories
- **Template Customization**: Configurable output templates
- **Format Variants**: Support for different IDE-specific formats

### Optimization

- **Incremental Builds**: Only process changed files
- **Parallel Processing**: Process agents and commands concurrently
- **Caching**: Cache resolved dependencies for faster rebuilds

### Monitoring

- **Build Metrics**: Track processing time and output sizes
- **Dependency Analysis**: Report on dependency usage patterns
- **Quality Metrics**: Measure embedding success rates

---

This algorithm provides a complete framework for generating IDE-compatible AI-Craft framework distributions, focusing on individual file generation with embedded dependencies while discarding web-specific concepts.
