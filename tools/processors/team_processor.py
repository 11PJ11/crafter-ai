"""
Team Processor

Processes nWave agent-team YAML files and converts them into massive agent files
with embedded team coordination and collaboration logic.
"""

import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
import yaml

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from utils.dependency_resolver import DependencyResolver


class TeamProcessor:
    """Processes team files into massive agent files."""

    def __init__(self, source_dir: Path, output_dir: Path, file_manager):
        self.source_dir = Path(source_dir)
        self.output_dir = Path(output_dir)
        self.file_manager = file_manager
        self.dependency_resolver = DependencyResolver(source_dir, file_manager)

    def load_team_config(self, team_file: Path) -> Optional[Dict[str, Any]]:
        """
        Load team configuration from YAML file.

        Args:
            team_file: Path to team YAML file

        Returns:
            dict: Team configuration or None if loading fails
        """
        try:
            content = self.file_manager.read_file(team_file)
            if not content:
                return None

            return yaml.safe_load(content)

        except yaml.YAMLError as e:
            logging.error(f"Failed to parse team YAML {team_file}: {e}")
            return None
        except Exception as e:
            logging.error(f"Error loading team config {team_file}: {e}")
            return None

    def get_team_info_from_config(self, team_name: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract team information from main config.yaml.

        Args:
            team_name: Name of the team
            config: Full configuration dictionary

        Returns:
            dict: Team information
        """
        agent_teams = config.get('agent_teams', {})

        # Look for exact match first
        if team_name in agent_teams:
            return agent_teams[team_name]

        # Look for team name without extension
        team_base = Path(team_name).stem.replace('-', '_')
        if team_base in agent_teams:
            return agent_teams[team_base]

        # Return default team info
        return {
            'description': f'{team_name} collaborative team',
            'scope': 'general_projects',
            'methodology_focus': '5d_wave'
        }

    def generate_team_agent_header(self, team_name: str, team_config: Dict[str, Any], main_config: Dict[str, Any]) -> str:
        """
        Generate header for team agent.

        Args:
            team_name: Name of the team
            team_config: Team-specific configuration
            main_config: Main configuration dictionary

        Returns:
            str: Formatted team agent header
        """
        team_base = Path(team_name).stem
        team_info = self.get_team_info_from_config(team_name, main_config)

        # Extract team metadata
        team_meta = team_config.get('team', {})

        header_parts = [
            f"# {team_base}-team",
            "",
            "ACTIVATION-NOTICE: This is a massive collaborative team agent that coordinates multiple specialized agents for complex nWave methodology execution.",
            "",
            "CRITICAL: This team agent orchestrates the complete collaboration workflow. Follow the team coordination patterns defined below.",
            "",
            f"## Team Identity",
            f"**Name**: {team_meta.get('name', team_base.replace('-', ' ').title())}",
            f"**Focus**: {team_info.get('methodology_focus', '5d_wave')}",
            f"**Scope**: {team_info.get('scope', 'general_projects')}",
            f"**Description**: {team_info.get('description', 'Collaborative team for nWave methodology')}",
            ""
        ]

        return "\n".join(header_parts)

    def load_agent_content(self, agent_name: str) -> str:
        """
        Load the full content of an agent by name.

        Args:
            agent_name: Name of the agent (like 'business_analyst' or 'solution_architect')

        Returns:
            str: Full agent content or error message if not found
        """
        try:
            # Convert agent name to file name (underscore to hyphen)
            agent_file_name = agent_name.replace('_', '-') + '.md'
            agent_file_path = self.source_dir / "agents" / agent_file_name

            if agent_file_path.exists():
                agent_content = self.file_manager.read_file(agent_file_path)
                if agent_content:
                    return agent_content
                else:
                    return f"ERROR: Could not read agent file: {agent_file_path}"
            else:
                return f"ERROR: Agent file not found: {agent_file_path}"

        except Exception as e:
            return f"ERROR: Failed to load agent '{agent_name}': {e}"

    def generate_team_composition(self, team_config: Dict[str, Any]) -> str:
        """
        Generate team composition section with embedded full agent content.

        Args:
            team_config: Team configuration

        Returns:
            str: Team composition content with embedded agents
        """
        # Get team agents from the team config structure
        team_meta = team_config.get('team', {})
        team_agents = team_meta.get('agents', {})

        if not team_agents:
            return "## Team Composition\n\nNo agents defined for this team.\n"

        composition_parts = [
            "## Team Composition",
            "",
            "This massive collaborative team includes the following specialized agents with their complete specifications embedded:",
            ""
        ]

        # Process agents by wave
        for wave_name, wave_agents in team_agents.items():
            composition_parts.extend([
                f"### {wave_name.upper().replace('_', ' ')}",
                ""
            ])

            for agent_name, agent_info in wave_agents.items():
                role = agent_info.get('role', 'Team Member')
                wave_priority = agent_info.get('wave_priority', 1)
                responsibilities = agent_info.get('responsibilities', [])

                composition_parts.extend([
                    f"#### {agent_name.replace('_', ' ').title()} ({role})",
                    f"**Wave Priority**: {wave_priority}",
                    ""
                ])

                # Add responsibilities
                if responsibilities:
                    composition_parts.append("**Responsibilities**:")
                    for resp in responsibilities:
                        composition_parts.append(f"- {resp}")
                    composition_parts.append("")

                # Embed the full agent content
                composition_parts.extend([
                    f"**EMBEDDED AGENT SPECIFICATION:**",
                    ""
                ])

                agent_content = self.load_agent_content(agent_name)
                # Indent the agent content to make it clearly embedded
                indented_content = "\n".join(f"    {line}" if line.strip() else "" for line in agent_content.split("\n"))
                composition_parts.append(indented_content)
                composition_parts.extend([
                    "",
                    "---",
                    ""
                ])

        return "\n".join(composition_parts)

    def generate_workflow_coordination(self, team_config: Dict[str, Any]) -> str:
        """
        Generate workflow coordination section.

        Args:
            team_config: Team configuration

        Returns:
            str: Workflow coordination content
        """
        workflow = team_config.get('workflow', {})
        if not workflow:
            return "## Workflow Coordination\n\nNo workflow patterns defined.\n"

        coord_parts = [
            "## Workflow Coordination",
            ""
        ]

        # Add coordination strategy
        strategy = workflow.get('coordination_strategy', 'sequential')
        coord_parts.extend([
            f"**Coordination Strategy**: {strategy}",
            ""
        ])

        # Add wave coordination if available
        if 'wave_coordination' in workflow:
            wave_coord = workflow['wave_coordination']
            coord_parts.extend([
                "### Wave Coordination",
                ""
            ])

            for wave, coordination in wave_coord.items():
                coord_parts.extend([
                    f"**{wave} Wave**:",
                    f"- Coordination: {coordination}",
                    ""
                ])

        # Add collaboration patterns
        if 'collaboration_patterns' in workflow:
            patterns = workflow['collaboration_patterns']
            coord_parts.extend([
                "### Collaboration Patterns",
                ""
            ])

            for pattern_name, pattern_info in patterns.items():
                coord_parts.extend([
                    f"**{pattern_name}**:",
                    f"- {pattern_info}",
                    ""
                ])

        return "\n".join(coord_parts)

    def generate_team_configuration_yaml(self, team_config: Dict[str, Any]) -> str:
        """
        Generate embedded YAML configuration for the team.

        Args:
            team_config: Team configuration

        Returns:
            str: YAML configuration block
        """
        try:
            # Create simplified config for embedding
            embedded_config = {
                'team': team_config.get('team', {}),
                'agents': team_config.get('agents', {}),
                'workflow': team_config.get('workflow', {}),
                'integration': team_config.get('integration', {})
            }

            yaml_content = yaml.dump(embedded_config, default_flow_style=False, sort_keys=False)
            return f"## Team Configuration\n\n```yaml\n{yaml_content}```\n"

        except Exception as e:
            logging.error(f"Failed to generate team YAML config: {e}")
            return "## Team Configuration\n\nConfiguration unavailable.\n"

    def generate_team_agent_content(self, team_file: Path, config: Dict[str, Any]) -> str:
        """
        Generate complete team agent content.

        Args:
            team_file: Path to source team file
            config: Main configuration dictionary

        Returns:
            str: Complete team agent content
        """
        try:
            # Load team configuration
            team_config = self.load_team_config(team_file)
            if not team_config:
                raise ValueError(f"Could not load team config: {team_file}")

            team_name = team_file.name

            # Generate content sections
            content_parts = []

            # Header
            header = self.generate_team_agent_header(team_name, team_config, config)
            content_parts.append(header)

            # Team composition
            composition = self.generate_team_composition(team_config)
            content_parts.append(composition)

            # Workflow coordination
            coordination = self.generate_workflow_coordination(team_config)
            content_parts.append(coordination)

            # Embedded configuration
            yaml_config = self.generate_team_configuration_yaml(team_config)
            content_parts.append(yaml_config)

            return "\n".join(content_parts)

        except Exception as e:
            logging.error(f"Error generating team agent content for {team_file}: {e}")
            raise

    def process_team(self, team_file: Path, config: Dict[str, Any]) -> bool:
        """
        Process a single team file into a massive agent.

        Args:
            team_file: Path to team file to process
            config: Configuration dictionary

        Returns:
            bool: True if successful
        """
        try:
            team_name = team_file.stem
            logging.info(f"Processing team: {team_name}")

            # Generate team agent content
            team_content = self.generate_team_agent_content(team_file, config)

            # Determine output path - teams become agents
            output_path = self.output_dir / "agents" / "nw" / f"{team_name}-team.md"

            # Write output file
            success = self.file_manager.write_file(output_path, team_content)

            if success:
                logging.debug(f"Generated team agent: {output_path}")
                return True
            else:
                logging.error(f"Failed to write team agent file: {output_path}")
                return False

        except Exception as e:
            logging.error(f"Error processing team {team_file}: {e}")
            return False

    def get_team_info(self, team_file: Path, config: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Extract team information for configuration generation.

        Args:
            team_file: Path to team file
            config: Configuration dictionary

        Returns:
            dict: Team information or None if extraction fails
        """
        try:
            team_config = self.load_team_config(team_file)
            if not team_config:
                return None

            team_info = self.get_team_info_from_config(team_file.name, config)
            team_meta = team_config.get('team', {})

            return {
                'name': team_file.stem,
                'file': f"{team_file.stem}-team.md",
                'description': team_info.get('description'),
                'scope': team_info.get('scope'),
                'methodology_focus': team_info.get('methodology_focus'),
                'agents': list(team_config.get('agents', {}).keys())
            }

        except Exception as e:
            logging.error(f"Error extracting team info from {team_file}: {e}")
            return None