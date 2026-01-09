"""Template adapter: Transforms parser output to domain types for template rendering

Level 4 Refactoring: Bridge between parser (raw dicts) and template (domain types)

Business logic:
- Receives TOONParserOutput (raw parser data)
- Transforms to domain types (AgentCommand, YAMLSafeValue, etc.)
- Returns data structure optimized for template rendering

This adapter layer ensures:
1. Template receives validated domain types
2. Parser remains decoupled from template types
3. Type construction validates business rules
"""

from typing import Any
from tools.toon.template_types import (
    AgentCommand,
    YAMLSafeValue,
    EmbeddedKnowledgeMarker,
    AgentTemplateData,
    create_commands_from_dict,
    create_embed_markers,
    escape_yaml_value
)


class TemplateAdapter:
    """Adapts parser output to domain types for template rendering

    Business concept: Transform parser data → template-ready domain model

    Usage:
        adapter = TemplateAdapter(parser_output)
        template_data = adapter.to_template_data()
        rendered = template.render(**template_data)
    """

    def __init__(self, parser_output: dict[str, Any]):
        """Initialize adapter with parser output

        Args:
            parser_output: Raw parser output matching TOONParserOutput structure
        """
        self.parser_output = parser_output

    def to_template_data(self) -> dict[str, Any]:
        """Transform parser output to template-ready data with domain types

        Returns:
            Dict with domain types for template rendering:
            - metadata_safe: Dict with YAMLSafeValue for all string values
            - commands_typed: List of AgentCommand instances
            - embed_markers: List of EmbeddedKnowledgeMarker instances
            - All original data preserved for template access

        Template can use:
        - {{ metadata_safe.name.yaml_safe }} for escaped YAML values
        - {% for cmd in commands_typed %} for AgentCommand instances
        - {% for marker in embed_markers %} for injection markers
        """
        # Start with original parser output
        template_data = dict(self.parser_output)

        # Transform metadata values to YAMLSafeValue domain types
        metadata = self.parser_output.get('metadata', {})
        metadata_safe = {
            key: escape_yaml_value(value) if isinstance(value, str) else value
            for key, value in metadata.items()
        }
        template_data['metadata_safe'] = metadata_safe

        # Transform commands to AgentCommand domain types
        sections = self.parser_output.get('sections', {})
        commands = sections.get('commands', {})

        if isinstance(commands, dict):
            # Commands as dict (name -> description mapping)
            template_data['commands_typed'] = create_commands_from_dict(commands)
        else:
            # Commands as list (no descriptions) - create minimal AgentCommand
            template_data['commands_typed'] = [
                AgentCommand(name=cmd, description=cmd)
                for cmd in (commands if isinstance(commands, list) else [])
            ]

        # Transform embedded knowledge paths to EmbeddedKnowledgeMarker domain types
        dependencies = sections.get('dependencies', {})
        embed_knowledge = dependencies.get('embed_knowledge', [])

        if embed_knowledge:
            template_data['embed_markers'] = create_embed_markers(embed_knowledge)
        else:
            template_data['embed_markers'] = []

        # Keep original data accessible (for backward compatibility during refactoring)
        # Template can use both: metadata.name (original) or metadata_safe.name.yaml_safe (typed)
        return template_data


# ============================================================================
# CONVENIENCE FUNCTION: One-step transformation
# ============================================================================

def adapt_for_template(parser_output: dict[str, Any]) -> dict[str, Any]:
    """One-step transformation from parser output to template data

    Convenience function that creates adapter and returns template-ready data

    Args:
        parser_output: Raw parser output from TOON parser

    Returns:
        Template-ready data with domain types

    Example:
        parser_output = parse_toon_file("agent.toon")
        template_data = adapt_for_template(parser_output)
        rendered = template.render(**template_data).lstrip('\n')  # Strip leading newline from Jinja2
    """
    adapter = TemplateAdapter(parser_output)
    return adapter.to_template_data()


def render_agent_template(jinja_env, parser_output: dict[str, Any]) -> str:
    """Complete workflow: adapt parser output, render template, clean output

    Business logic: End-to-end template rendering with domain types

    Args:
        jinja_env: Jinja2 environment with templates loaded
        parser_output: Raw parser output from TOON parser

    Returns:
        Rendered agent.md content with proper formatting

    Example:
        from jinja2 import Environment, FileSystemLoader
        env = Environment(loader=FileSystemLoader('tools/toon/templates'))
        output = render_agent_template(env, parser_output)
    """
    template = jinja_env.get_template('agent.md.j2')
    template_data = adapt_for_template(parser_output)
    rendered = template.render(**template_data)
    # Strip leading newline that Jinja2 template produces
    # (due to line breaks between set statements and macro definitions)
    return rendered.lstrip('\n')
