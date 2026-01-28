"""
Command Processor

Processes nWave task files and converts them into IDE-compatible command files
with wave assignments and embedded dependencies.
"""

import logging
import re
from pathlib import Path
from typing import Dict, Optional, Any
import yaml

import sys

sys.path.append(str(Path(__file__).parent.parent))
from utils.dependency_resolver import DependencyResolver
from processors.template_processor import TemplateProcessor


class CommandProcessor:
    """Processes task files into IDE command files."""

    def __init__(self, source_dir: Path, output_dir: Path, file_manager):
        self.source_dir = Path(source_dir)
        self.output_dir = Path(output_dir)
        self.file_manager = file_manager
        self.dependency_resolver = DependencyResolver(source_dir, file_manager)

        # Initialize template processor for schema variable substitution
        schema_path = self.source_dir / "templates" / "step-tdd-cycle-schema.json"
        try:
            self.template_processor = TemplateProcessor(schema_path)
            logging.info(f"TemplateProcessor initialized with schema: {schema_path}")
        except Exception as e:
            logging.warning(f"Could not initialize TemplateProcessor: {e}")
            self.template_processor = None

    def process_template_variables(self, content: str) -> str:
        """
        Process template variables using canonical schema.

        Replaces template variables like {{SCHEMA_TDD_PHASES}} with actual values
        from the canonical schema. This ensures documentation reflects the current
        schema without manual synchronization.

        Args:
            content: Content containing template variable placeholders

        Returns:
            str: Content with template variables replaced by actual values
        """
        if not self.template_processor:
            logging.debug(
                "TemplateProcessor not initialized, skipping template processing"
            )
            return content

        try:
            # Get template variables from schema
            variables = self.template_processor.extract_variables_dict()

            # Replace all template variables
            processed = content
            for var_name, var_value in variables.items():
                placeholder = f"{{{{{var_name}}}}}"
                if placeholder in processed:
                    logging.debug(f"Replacing template variable: {var_name}")
                    processed = processed.replace(placeholder, var_value)

            # Log any unprocessed template variables (potential issues)
            import re

            unprocessed = re.findall(r"\{\{[A-Z_]+\}\}", processed)
            if unprocessed:
                unique_unprocessed = set(unprocessed)
                logging.warning(
                    f"Found unprocessed template variables: {unique_unprocessed}"
                )

            return processed

        except Exception as e:
            logging.error(f"Error processing template variables: {e}")
            # Return original content if processing fails
            return content

    def validate_template_resolution(self, content: str, file_path: str) -> None:
        """
        Ensure all template variables were resolved.

        Raises:
            ValueError: If unresolved template variables are found

        Args:
            content: Processed content to validate
            file_path: Path to file being processed (for error messages)
        """
        unresolved_pattern = r"\{\{SCHEMA_[A-Z_]+\}\}"
        matches = re.findall(unresolved_pattern, content)

        if matches:
            unique_matches = sorted(set(matches))
            raise ValueError(
                f"Unresolved template variables in {file_path}: {unique_matches}\n"
                f"Check that TemplateProcessor initialized correctly and all variables are defined."
            )

    def process_embed_injections(self, content: str) -> str:
        """
        Process BUILD:INJECT markers and replace with embed file content.

        Finds markers in format:
        <!-- BUILD:INJECT:START:path/to/file.md -->
        <!-- Content will be injected here at build time -->
        <!-- BUILD:INJECT:END -->

        And replaces the entire marker region with the actual file content.

        Args:
            content: Content containing injection markers

        Returns:
            str: Content with markers replaced by actual embed file content
        """
        marker_pattern = re.compile(
            r"<!-- BUILD:INJECT:START:(.+?) -->\n.*?<!-- BUILD:INJECT:END -->",
            re.DOTALL,
        )

        def replace_marker(match):
            embed_path = match.group(1).strip()

            # Resolve path relative to project root (parent of source_dir which is nWave)
            project_root = self.source_dir.parent
            embed_full_path = project_root / embed_path

            try:
                embed_content = self.file_manager.read_file(embed_full_path)
                if not embed_content:
                    error_msg = f"Could not read embed file: {embed_path}"
                    logging.error(error_msg)
                    raise FileNotFoundError(error_msg)

                logging.info(f"Injecting embed content from: {embed_path}")

                # Keep the markers for documentation purposes
                return f"<!-- BUILD:INJECT:START:{embed_path} -->\n{embed_content.strip()}\n<!-- BUILD:INJECT:END -->"

            except Exception as e:
                logging.error(f"Error processing embed injection for {embed_path}: {e}")
                raise

        # Find all markers and replace them
        result = marker_pattern.sub(replace_marker, content)

        # Log summary of injections
        matches = marker_pattern.findall(content)
        if matches:
            logging.info(f"Processed {len(matches)} embed injection(s)")

        return result

    def get_command_info_from_config(
        self, task_name: str, config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Extract command information from framework-catalog.yaml.

        Args:
            task_name: Name of the task/command
            config: Full configuration dictionary

        Returns:
            dict: Command information
        """
        commands = config.get("commands", {})

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
            "description": f"Execute {task_base} task",
            "wave": "UNKNOWN",
            "agents": [],
            "outputs": [],
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
        wave_phases = config.get("wave_phases", [])
        if wave_name in wave_phases:
            return {
                "name": wave_name,
                "index": wave_phases.index(wave_name),
                "total_phases": len(wave_phases),
            }
        return {"name": wave_name, "index": -1, "total_phases": len(wave_phases)}

    def generate_command_frontmatter(
        self, task_name: str, command_info: Dict[str, Any]
    ) -> str:
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
        description = command_info.get("description", f"Execute {task_base} command")

        # Get argument hint from config (preferred) or use fallback
        argument_hint = command_info.get("argument_hint", "")

        # Append argument hint to description for better UI visibility
        if argument_hint:
            description = f"{description} {argument_hint}"

        # Build frontmatter dictionary
        frontmatter = {"description": description}

        # Also add separate argument-hint field for Claude Code
        if argument_hint:
            frontmatter["argument-hint"] = argument_hint

        try:
            yaml_content = yaml.dump(
                frontmatter, default_flow_style=False, sort_keys=False
            )
            return f"---\n{yaml_content}---\n\n"
        except Exception as e:
            logging.error(f"Failed to generate command frontmatter: {e}")
            return ""

    def generate_command_header(
        self, task_name: str, command_info: Dict[str, Any], wave_info: Dict[str, Any]
    ) -> str:
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
        wave_name = command_info.get("wave", "UNKNOWN")

        header_parts = [
            f"# /{task_base} Command",
            "",
            f"**Wave**: {wave_name}",
            f"**Description**: {command_info.get('description', 'No description available')}",
            "",
        ]

        # Add wave progression if available
        if wave_info["index"] >= 0:
            progress = f"{wave_info['index'] + 1}/{wave_info['total_phases']}"
            header_parts.append(f"**Wave Progress**: {progress}")

        # Add associated agents
        agents = command_info.get("agents", [])
        if agents:
            agent_list = ", ".join(agents)
            header_parts.append(f"**Primary Agents**: {agent_list}")

        # Add expected outputs
        outputs = command_info.get("outputs", [])
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

            # Process BUILD:INJECT markers FIRST (before any other processing)
            task_content = self.process_embed_injections(task_content)

            # Process template variables SECOND (after embeds, before other transforms)
            task_content = self.process_template_variables(task_content)

            # Validate template resolution (ensures no unprocessed variables remain)
            self.validate_template_resolution(task_content, str(task_file))

            # Get command and wave information
            task_name = task_file.name
            command_info = self.get_command_info_from_config(task_name, config)
            wave_info = self.get_wave_info(command_info.get("wave", "UNKNOWN"), config)

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

    def get_command_info(
        self, task_file: Path, config: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
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
                "name": task_file.stem,
                "file": task_file.name,
                "description": command_info.get("description"),
                "wave": command_info.get("wave"),
                "agents": command_info.get("agents", []),
                "outputs": command_info.get("outputs", []),
            }

        except Exception as e:
            logging.error(f"Error extracting command info from {task_file}: {e}")
            return None
