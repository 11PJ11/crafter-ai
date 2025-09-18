# /cai:man - CAI Command Manual System

```yaml
---
command: "/cai:man"
category: "Meta & Orchestration"
purpose: "Linux-style manual system for CAI commands with comprehensive documentation access"
wave-enabled: false
performance-profile: "standard"
---
```

## Overview

Comprehensive manual system providing detailed documentation for all CAI commands, similar to Linux `man` pages. Offers structured access to command documentation with search, filtering, and example capabilities.

## Auto-Persona Activation
- **Mentor**: Educational guidance and knowledge transfer (default)
- **Scribe**: Documentation specialist for content formatting (conditional)

## MCP Server Integration
- **Primary**: Sequential (structured documentation retrieval and search)
- **Secondary**: Context7 (documentation patterns and formatting best practices)
- **Avoided**: Magic and Playwright (focus on documentation over generation/testing)

## Tool Orchestration
- **Read**: Manual content retrieval and documentation access
- **Grep**: Documentation search and content filtering
- **Write**: Generated manual output and formatted documentation
- **TodoWrite**: Manual session progress and documentation tracking

## Agent Flow
```yaml
documentation_display:
  full_manual:
    - Retrieves complete command documentation from manual files
    - Formats output with structured sections (synopsis, description, arguments, examples)
    - Provides navigation hints and cross-references to related commands
    - Offers context-aware suggestions based on user needs

  filtered_content:
    - Extracts specific sections (--examples, --flags, --arguments)
    - Applies search filters and keyword highlighting
    - Provides focused documentation for specific use cases
    - Maintains consistency with Linux man page conventions

  search_functionality:
    - Searches across all command documentation
    - Provides relevance scoring and context snippets
    - Supports pattern matching and keyword combinations
    - Offers command discovery and suggestion capabilities

  list_commands:
    - Displays command catalog with categories and descriptions
    - Provides quick reference and command discovery
    - Shows command relationships and workflow patterns
    - Offers learning pathways for different user experience levels
```

## Documentation Architecture

### Manual Storage Location
```
.claude/manuals/cai/
├── index.json           # Command catalog and metadata
├── refactor.json        # Individual command documentation
├── start.json
├── develop.json
├── architect.json
├── discuss.json
├── validate.json
├── complete.json
├── transition.json
├── help.json
├── atdd.json
├── root-why.json
├── skeleton.json
└── brownfield.json
```

### Documentation Format
JSON structure for consistent documentation:
```json
{
  "command": "/cai:command",
  "category": "Category Name",
  "purpose": "Brief purpose description",
  "synopsis": "command [arguments] [options]",
  "description": "Detailed description...",
  "arguments": {
    "arg_name": {
      "description": "Argument description",
      "required": true/false,
      "type": "string|number|boolean",
      "values": ["option1", "option2"]
    }
  },
  "flags": {
    "--flag": {
      "description": "Flag description",
      "short": "-f",
      "type": "boolean|string",
      "default": "default_value"
    }
  },
  "examples": [
    {
      "command": "example command",
      "description": "What this example does",
      "context": "When to use this"
    }
  ],
  "sections": {
    "special_section": "Additional documentation sections"
  },
  "see_also": ["related_command1", "related_command2"]
}
```

## Manual Execution Logic

The `cai/man` command will execute through agent delegation to provide comprehensive manual functionality. When invoked, it will:

1. **Parse Arguments**: Determine command name and requested sections
2. **Locate Documentation**: Find manual files in `.claude/manuals/cai/`
3. **Format Output**: Structure documentation according to requested format
4. **Provide Navigation**: Offer cross-references and related commands

### Command Processing
```bash
# Full manual for a command
/cai:man refactor

# Specific sections
/cai:man refactor --examples
/cai:man refactor --flags
/cai:man refactor --arguments

# Search functionality
/cai:man --search "level"
/cai:man --search "systematic"

# Command discovery
/cai:man --list
/cai:man --list --category "Quality"
```

### Agent Integration
The command delegates to appropriate agents based on functionality:
- **Documentation Retrieval**: Reads manual files and formats output
- **Search Operations**: Searches across documentation with relevance scoring
- **Command Discovery**: Provides command listing and categorization
- **Cross-References**: Identifies related commands and workflows

For complete implementation details and manual content, see the extracted documentation files in `.claude/manuals/cai/`.