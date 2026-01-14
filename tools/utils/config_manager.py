"""
Config Manager

Manages nWave configuration loading, parsing, and IDE config generation.
Handles the central framework-catalog.yaml file and generates IDE-compatible configuration.
"""

import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
import yaml
import json
from datetime import datetime


class ConfigManager:
    """Manages configuration for nWave IDE bundle generation."""

    def __init__(self, config_file: Path):
        self.config_file = Path(config_file)
        self._config = None
        self._load_config()

    def _load_config(self) -> None:
        """Load configuration from YAML file."""
        try:
            if not self.config_file.exists():
                logging.error(f"Configuration file not found: {self.config_file}")
                self._config = {}
                return

            with open(self.config_file, 'r', encoding='utf-8') as f:
                self._config = yaml.safe_load(f) or {}

            logging.info(f"Loaded configuration from: {self.config_file}")
            logging.debug(f"Configuration sections: {list(self._config.keys())}")

        except yaml.YAMLError as e:
            logging.error(f"Failed to parse configuration YAML: {e}")
            self._config = {}
        except Exception as e:
            logging.error(f"Error loading configuration: {e}")
            self._config = {}

    def get_config(self) -> Dict[str, Any]:
        """
        Get the complete configuration dictionary.

        Returns:
            dict: Complete configuration
        """
        return self._config or {}

    def get_section(self, section_name: str) -> Dict[str, Any]:
        """
        Get a specific configuration section.

        Args:
            section_name: Name of configuration section

        Returns:
            dict: Configuration section or empty dict if not found
        """
        return self._config.get(section_name, {})

    def get_methodology_info(self) -> Dict[str, Any]:
        """
        Get methodology information.

        Returns:
            dict: Methodology information
        """
        return {
            'name': self._config.get('name', 'nWave'),
            'version': self._config.get('version', '1.0.0'),
            'description': self._config.get('description', 'nWave Methodology'),
            'methodology': self._config.get('methodology', 'nWave'),
            'wave_phases': self._config.get('wave_phases', [])
        }

    def get_agents_config(self) -> Dict[str, Any]:
        """
        Get agents configuration.

        Returns:
            dict: Agents configuration
        """
        return self.get_section('agents')

    def get_commands_config(self) -> Dict[str, Any]:
        """
        Get commands configuration.

        Returns:
            dict: Commands configuration
        """
        return self.get_section('commands')

    def get_workflows_config(self) -> Dict[str, Any]:
        """
        Get workflows configuration.

        Returns:
            dict: Workflows configuration
        """
        return self.get_section('workflows')

    def get_teams_config(self) -> Dict[str, Any]:
        """
        Get agent teams configuration.

        Returns:
            dict: Agent teams configuration
        """
        return self.get_section('agent_teams')

    def get_quality_gates(self) -> Dict[str, Any]:
        """
        Get quality gates configuration.

        Returns:
            dict: Quality gates configuration
        """
        return self.get_section('quality_gates')

    def get_checklists_config(self) -> Dict[str, Any]:
        """
        Get checklists configuration.

        Returns:
            dict: Checklists configuration
        """
        return self.get_section('checklists')

    def get_templates_config(self) -> Dict[str, Any]:
        """
        Get templates configuration.

        Returns:
            dict: Templates configuration
        """
        return self.get_section('templates')

    def get_knowledge_base_config(self) -> Dict[str, Any]:
        """
        Get knowledge base configuration.

        Returns:
            dict: Knowledge base configuration
        """
        return self.get_section('knowledge_base')

    def get_integration_config(self) -> Dict[str, Any]:
        """
        Get integration configuration.

        Returns:
            dict: Integration configuration
        """
        return self.get_section('integration')

    def get_agent_by_name(self, agent_name: str) -> Optional[Dict[str, Any]]:
        """
        Get configuration for a specific agent.

        Args:
            agent_name: Name of the agent

        Returns:
            dict: Agent configuration or None if not found
        """
        agents = self.get_agents_config()
        return agents.get(agent_name)

    def get_command_by_name(self, command_name: str) -> Optional[Dict[str, Any]]:
        """
        Get configuration for a specific command.

        Args:
            command_name: Name of the command

        Returns:
            dict: Command configuration or None if not found
        """
        commands = self.get_commands_config()
        return commands.get(command_name)

    def get_agents_by_wave(self, wave_name: str) -> List[Dict[str, Any]]:
        """
        Get all agents assigned to a specific wave.

        Args:
            wave_name: Name of the wave

        Returns:
            list: List of agent configurations
        """
        agents = self.get_agents_config()
        wave_agents = []

        for agent_name, agent_config in agents.items():
            if agent_config.get('wave') == wave_name:
                agent_info = agent_config.copy()
                agent_info['name'] = agent_name
                wave_agents.append(agent_info)

        return sorted(wave_agents, key=lambda x: x.get('priority', 99))

    def get_commands_by_wave(self, wave_name: str) -> List[Dict[str, Any]]:
        """
        Get all commands associated with a specific wave.

        Args:
            wave_name: Name of the wave

        Returns:
            list: List of command configurations
        """
        commands = self.get_commands_config()
        wave_commands = []

        for command_name, command_config in commands.items():
            if command_config.get('wave') == wave_name:
                command_info = command_config.copy()
                command_info['name'] = command_name
                wave_commands.append(command_info)

        return wave_commands

    def validate_configuration(self) -> List[str]:
        """
        Validate the configuration for completeness and consistency.

        Returns:
            list: List of validation errors
        """
        errors = []

        # Check required sections
        required_sections = ['wave_phases', 'agents', 'commands']
        for section in required_sections:
            if section not in self._config:
                errors.append(f"Missing required section: {section}")

        # Validate wave phases
        wave_phases = self._config.get('wave_phases', [])
        if not wave_phases:
            errors.append("No wave phases defined")

        # Validate agents
        agents = self.get_agents_config()
        for agent_name, agent_config in agents.items():
            if 'wave' not in agent_config:
                errors.append(f"Agent {agent_name} missing wave assignment")
            elif agent_config['wave'] not in wave_phases and agent_config['wave'] != 'CROSS_WAVE':
                errors.append(f"Agent {agent_name} assigned to unknown wave: {agent_config['wave']}")

        # Validate commands
        commands = self.get_commands_config()
        for command_name, command_config in commands.items():
            if 'agents' in command_config:
                for agent_name in command_config['agents']:
                    if agent_name not in agents:
                        errors.append(f"Command {command_name} references unknown agent: {agent_name}")

        return errors

    def generate_ide_config(self, build_stats: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate IDE-compatible configuration.

        Args:
            build_stats: Build statistics

        Returns:
            dict: IDE configuration
        """
        methodology_info = self.get_methodology_info()

        ide_config = {
            'metadata': {
                'name': methodology_info['name'],
                'version': methodology_info['version'],
                'description': methodology_info['description'],
                'methodology': methodology_info['methodology'],
                'generated_at': datetime.now().isoformat(),
                'generator': 'nWave IDE Bundle Builder'
            },
            'methodology': {
                'wave_phases': methodology_info['wave_phases'],
                'total_phases': len(methodology_info['wave_phases'])
            },
            'agents': self._generate_agents_index(),
            'commands': self._generate_commands_index(),
            'teams': self._generate_teams_index(),
            'workflows': self._generate_workflows_index(),
            'quality_gates': self.get_quality_gates(),
            'build_info': {
                'stats': build_stats,
                'validation_errors': self.validate_configuration()
            }
        }

        return ide_config

    def _generate_agents_index(self) -> Dict[str, Any]:
        """Generate agents index for IDE config."""
        agents = self.get_agents_config()
        agents_index = {}

        for agent_name, agent_config in agents.items():
            agents_index[agent_name] = {
                'wave': agent_config.get('wave'),
                'role': agent_config.get('role'),
                'priority': agent_config.get('priority'),
                'file': f"{agent_name}.md"
            }

        return agents_index

    def _generate_commands_index(self) -> Dict[str, Any]:
        """Generate commands index for IDE config."""
        commands = self.get_commands_config()
        commands_index = {}

        for command_name, command_config in commands.items():
            commands_index[command_name] = {
                'description': command_config.get('description'),
                'wave': command_config.get('wave'),
                'agents': command_config.get('agents', []),
                'outputs': command_config.get('outputs', []),
                'file': f"{command_name}.md"
            }

        return commands_index

    def _generate_teams_index(self) -> Dict[str, Any]:
        """Generate teams index for IDE config."""
        teams = self.get_teams_config()
        teams_index = {}

        for team_name, team_config in teams.items():
            teams_index[team_name] = {
                'description': team_config.get('description'),
                'scope': team_config.get('scope'),
                'methodology_focus': team_config.get('methodology_focus'),
                'file': f"{team_name}-team.md"
            }

        return teams_index

    def _generate_workflows_index(self) -> Dict[str, Any]:
        """Generate workflows index for IDE config."""
        workflows = self.get_workflows_config()
        workflows_index = {}

        for workflow_name, workflow_config in workflows.items():
            workflows_index[workflow_name] = {
                'name': workflow_config.get('name'),
                'description': workflow_config.get('description'),
                'phases': workflow_config.get('phases', []),
                'file': f"{workflow_name}-orchestrator.md"
            }

        return workflows_index

    def export_config(self, output_file: Path, format: str = 'json') -> bool:
        """
        Export configuration to a file.

        Args:
            output_file: Output file path
            format: Export format ('json' or 'yaml')

        Returns:
            bool: True if successful
        """
        try:
            if format.lower() == 'json':
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(self._config, f, indent=2, ensure_ascii=False)
            elif format.lower() == 'yaml':
                with open(output_file, 'w', encoding='utf-8') as f:
                    yaml.dump(self._config, f, default_flow_style=False, sort_keys=False)
            else:
                logging.error(f"Unsupported export format: {format}")
                return False

            logging.info(f"Exported configuration to: {output_file}")
            return True

        except Exception as e:
            logging.error(f"Error exporting configuration: {e}")
            return False
