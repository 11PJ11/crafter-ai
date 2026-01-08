# TOON Toolchain - Walking Skeleton

Minimal viable TOON parser and compiler demonstrating the architecture.

## Components

- **parser.py**: Parses TOON v1.0 files into structured data
- **parser_schema.py**: Output dataclass definition
- **compiler.py**: Orchestrates parse → template → output pipeline
- **templates/agent.md.j2**: Jinja2 template for agent output

## Usage

```python
from tools.toon.compiler import compile_toon

# Compile a TOON file to Claude Code agent format
compile_toon('agents/novel-editor-chatgpt-toon.txt', 'output/')
```

## Scope (Walking Skeleton)

- TOON v1.0 format only
- Happy path parsing (no advanced validation)
- Agent templates only (no command/skill templates)
- Basic YAML frontmatter generation

## Out of Scope (Future)

- TOON v3.0 support
- Security validation (path traversal, size limits)
- Advanced YAML escaping
- Command and Skill templates
