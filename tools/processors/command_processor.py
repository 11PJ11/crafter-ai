"""
Command Processor

Processes nWave task files and converts them into IDE-compatible command files
with wave assignments and embedded dependencies.
"""

import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
import yaml

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from utils.dependency_resolver import DependencyResolver


class CommandProcessor:
    """Processes task files into IDE command files."""

    def __init__(self, source_dir: Path, output_dir: Path, file_manager):
        self.source_dir = Path(source_dir)
        self.output_dir = Path(output_dir)
        self.file_manager = file_manager
        self.dependency_resolver = DependencyResolver(source_dir, file_manager)

    def get_command_info_from_config(self, task_name: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract command information from framework-catalog.yaml.

        Args:
            task_name: Name of the task/command
            config: Full configuration dictionary

        Returns:
            dict: Command information
        """
        commands = config.get('commands', {})

        # Look for exact match first
        if task_name in commands:
            return commands[task_name]

        # Look for task name without extension
        task_base = Path(task_name).stem
        if task_base in commands:
            return commands[task_base]

        # Look for commands that might match (case insensitive)
        for cmd_name, cmd_info in commands.items():
            if cmd_name.lower() == task_base.lower():
                return cmd_info

        # Return default command info
        return {
            'description': f'Execute {task_base} task',
            'wave': 'UNKNOWN',
            'agents': [],
            'outputs': []
        }

    def get_wave_info(self, wave_name: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get wave information from configuration.

        Args:
            wave_name: Name of the wave
            config: Full configuration dictionary

        Returns:
            dict: Wave information
        """
        wave_phases = config.get('wave_phases', [])
        if wave_name in wave_phases:
            return {
                'name': wave_name,
                'index': wave_phases.index(wave_name),
                'total_phases': len(wave_phases)
            }
        return {'name': wave_name, 'index': -1, 'total_phases': len(wave_phases)}

    def generate_command_frontmatter(self, task_name: str, command_info: Dict[str, Any]) -> str:
        """
        Generate Claude Code compatible YAML frontmatter for slash commands.

        Args:
            task_name: Name of the task/command
            command_info: Command information from config

        Returns:
            str: Formatted YAML frontmatter
        """
        task_base = Path(task_name).stem

        # Get base description from config
        description = command_info.get('description', f'Execute {task_base} command')

        # Get argument hint from config (preferred) or use fallback
        argument_hint = command_info.get('argument_hint', '')

        # Append argument hint to description for better UI visibility
        if argument_hint:
            description = f"{description} {argument_hint}"

        # Build frontmatter dictionary
        frontmatter = {
            'description': description
        }

        # Also add separate argument-hint field for Claude Code
        if argument_hint:
            frontmatter['argument-hint'] = argument_hint

        try:
            yaml_content = yaml.dump(frontmatter, default_flow_style=False, sort_keys=False)
            return f"---\n{yaml_content}---\n\n"
        except Exception as e:
            logging.error(f"Failed to generate command frontmatter: {e}")
            return ""

    def generate_command_header(self, task_name: str, command_info: Dict[str, Any], wave_info: Dict[str, Any]) -> str:
        """
        Generate command header with metadata.

        Args:
            task_name: Name of the task
            command_info: Command information from config
            wave_info: Wave information

        Returns:
            str: Formatted command header
        """
        task_base = Path(task_name).stem
        wave_name = command_info.get('wave', 'UNKNOWN')

        header_parts = [
            f"# /{task_base} Command",
            "",
            f"**Wave**: {wave_name}",
            f"**Description**: {command_info.get('description', 'No description available')}",
            ""
        ]

        # Add wave progression if available
        if wave_info['index'] >= 0:
            progress = f"{wave_info['index'] + 1}/{wave_info['total_phases']}"
            header_parts.append(f"**Wave Progress**: {progress}")

        # Add associated agents
        agents = command_info.get('agents', [])
        if agents:
            agent_list = ", ".join(agents)
            header_parts.append(f"**Primary Agents**: {agent_list}")

        # Add expected outputs
        outputs = command_info.get('outputs', [])
        if outputs:
            output_list = ", ".join(outputs)
            header_parts.append(f"**Expected Outputs**: {output_list}")

        header_parts.append("")
        header_parts.append("## Implementation")
        header_parts.append("")

        return "\n".join(header_parts)

    def process_task_dependencies(self, task_content: str) -> str:
        """
        Process any dependencies referenced in the task content.

        Args:
            task_content: Original task content

        Returns:
            str: Task content with dependencies embedded
        """
        # For now, return the original content
        # In the future, we could parse for dependency references and embed them
        return task_content

    def generate_command_content(self, task_file: Path, config: Dict[str, Any]) -> str:
        """
        Generate complete command content with Claude Code compatible YAML frontmatter.

        Args:
            task_file: Path to source task file
            config: Configuration dictionary

        Returns:
            str: Complete command content with frontmatter
        """
        try:
            # Read source task file
            task_content = self.file_manager.read_file(task_file)
            if not task_content:
                raise ValueError(f"Could not read task file: {task_file}")

            # Get command and wave information
            task_name = task_file.name
            command_info = self.get_command_info_from_config(task_name, config)
            wave_info = self.get_wave_info(command_info.get('wave', 'UNKNOWN'), config)

            # CRITICAL: Generate Claude Code compatible YAML frontmatter FIRST
            frontmatter = self.generate_command_frontmatter(task_name, command_info)

            # Generate command header
            header = self.generate_command_header(task_name, command_info, wave_info)

            # Process task content
            processed_content = self.process_task_dependencies(task_content)

            # Combine frontmatter, header and content
            return f"{frontmatter}{header}{processed_content}"

        except Exception as e:
            logging.error(f"Error generating command content for {task_file}: {e}")
            raise

    def process_task(self, task_file: Path, config: Dict[str, Any]) -> bool:
        """
        Process a single task file into a command.

        Args:
            task_file: Path to task file to process
            config: Configuration dictionary

        Returns:
            bool: True if successful
        """
        try:
            task_name = task_file.stem
            logging.info(f"Processing command: {task_name}")

            # Generate command content
            command_content = self.generate_command_content(task_file, config)

            # Determine output path
            output_path = self.output_dir / "commands" / "nw" / f"{task_name}.md"

            # Write output file
            success = self.file_manager.write_file(output_path, command_content)

            if success:
                logging.debug(f"Generated command: {output_path}")
                return True
            else:
                logging.error(f"Failed to write command file: {output_path}")
                return False

        except Exception as e:
            logging.error(f"Error processing task {task_file}: {e}")
            return False

    def get_command_info(self, task_file: Path, config: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Extract command information for configuration generation.

        Args:
            task_file: Path to task file
            config: Configuration dictionary

        Returns:
            dict: Command information or None if extraction fails
        """
        try:
            task_name = task_file.name
            command_info = self.get_command_info_from_config(task_name, config)

            return {
                'name': task_file.stem,
                'file': task_file.name,
                'description': command_info.get('description'),
                'wave': command_info.get('wave'),
                'agents': command_info.get('agents', []),
                'outputs': command_info.get('outputs', [])
            }

        except Exception as e:
            logging.error(f"Error extracting command info from {task_file}: {e}")
            return None
