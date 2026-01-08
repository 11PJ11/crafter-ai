"""TOON Compiler - Walking Skeleton.

Orchestrates: parse TOON → select template → render → write output.

Scope: Minimal viable compiler demonstrating the architecture.
- Agent templates only
- Happy path (no advanced error handling)
- Basic Jinja2 rendering
"""
from pathlib import Path
from typing import TypedDict, Any
from jinja2 import Environment, FileSystemLoader
from tools.toon.parser import TOONParser
from tools.toon.parser_schema import TOONMetadata


class TemplateContext(TypedDict):
    """Type-safe context for Jinja2 template rendering"""
    metadata: TOONMetadata
    sections: dict[str, Any]


def compile_toon(input_path: str, output_dir: str) -> None:
    """Compile TOON file to Claude Code agent format.

    Args:
        input_path: Path to .toon file
        output_dir: Directory for output .md file

    Pipeline:
        1. Parse TOON file
        2. Detect file type (agent/command/skill)
        3. Select template
        4. Render with Jinja2
        5. Write output

    Walking Skeleton Simplifications:
    - Agent template only
    - No error handling
    - Creates output directory if missing
    - Output filename: {agent_id}.md
    """
    # Parse TOON file
    parser = TOONParser()
    toon_content = Path(input_path).read_text(encoding='utf-8')
    parsed_data = parser.parse(toon_content)

    # Set up Jinja2 environment
    template_dir = Path(__file__).parent / 'templates'
    env = Environment(loader=FileSystemLoader(str(template_dir)))

    # Select template based on type
    template_name = f"{parsed_data['type']}.md.j2"
    template = env.get_template(template_name)

    # Render template with type-safe context
    context: TemplateContext = {
        'metadata': parsed_data['metadata'],
        'sections': parsed_data['sections']
    }
    output_content = template.render(**context)

    # Write output
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    agent_id = parsed_data.get('id') or 'unknown-agent'
    output_file = output_path / f"{agent_id}.md"
    output_file.write_text(output_content, encoding='utf-8')
