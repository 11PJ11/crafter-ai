"""
Agent Processor

Processes nWave agent .md files with embedded YAML configuration blocks,
extracts and embeds dependencies, and generates IDE-compatible agent files.
"""

import logging
import re
from pathlib import Path
from typing import Dict, List, Optional, Any
import yaml

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))
from utils.dependency_resolver import DependencyResolver


class AgentProcessor:
    """Processes agent files for IDE bundle generation."""

    def __init__(self, source_dir: Path, output_dir: Path, file_manager):
        self.source_dir = Path(source_dir)
        self.output_dir = Path(output_dir)
        self.file_manager = file_manager
        self.dependency_resolver = DependencyResolver(source_dir, file_manager)

    def extract_yaml_block(self, content: str) -> tuple[Optional[Dict[str, Any]], str]:
        """
        Extract YAML configuration block from agent markdown file.

        Returns:
            tuple: (yaml_config, remaining_content)
        """
        # Look for YAML block between ```yaml and ```
        yaml_pattern = r"```yaml\n(.*?)\n```"
        match = re.search(yaml_pattern, content, re.DOTALL)

        if not match:
            logging.warning("No YAML configuration block found in agent file")
            return None, content

        yaml_content = match.group(1)

        # Strip HTML comments (BUILD:INJECT markers) before parsing
        # These are processed separately by process_embed_injections()
        yaml_content_clean = re.sub(
            r"^\s*<!--.*?-->\s*$", "", yaml_content, flags=re.MULTILINE
        )

        try:
            yaml_config = yaml.safe_load(yaml_content_clean)
            # Remove the YAML block from content since we'll rebuild it
            remaining_content = content[: match.start()] + content[match.end() :]
            return yaml_config, remaining_content
        except yaml.YAMLError as e:
            logging.error(f"Failed to parse YAML configuration: {e}")
            return None, content

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

    def process_dependencies(self, yaml_config: Dict[str, Any]) -> str:
        """
        Process and embed dependencies based on agent configuration.

        Args:
            yaml_config: Agent YAML configuration

        Returns:
            str: Embedded dependencies content
        """
        if not yaml_config or "dependencies" not in yaml_config:
            return ""

        dependencies = yaml_config["dependencies"]
        embedded_content = []

        # Process each dependency type
        for dep_type, dep_files in dependencies.items():
            if not dep_files:
                continue

            # Add section header
            section_title = dep_type.replace("_", " ").title()
            embedded_content.append(f"\n## Embedded {section_title}\n")

            # Process each file in this dependency type
            for dep_file in dep_files:
                try:
                    file_content = self.dependency_resolver.resolve_dependency(
                        dep_type, dep_file
                    )
                    if file_content:
                        embedded_content.append(f"### {dep_file}\n")

                        # Determine content format based on file extension
                        if dep_file.endswith((".yaml", ".yml")):
                            embedded_content.append(f"```yaml\n{file_content}\n```\n")
                        else:
                            embedded_content.append(f"{file_content}\n")
                    else:
                        error_msg = (
                            f"Could not resolve dependency: {dep_type}/{dep_file}"
                        )
                        logging.error(error_msg)
                        raise FileNotFoundError(error_msg)

                except Exception as e:
                    logging.error(
                        f"Error processing dependency {dep_type}/{dep_file}: {e}"
                    )
                    raise

        return "\n".join(embedded_content)

    def generate_frontmatter(
        self, agent_file: Path, yaml_config: Dict[str, Any]
    ) -> str:
        """
        Generate Claude Code compatible YAML frontmatter.

        Args:
            agent_file: Path to agent file (for extracting agent name)
            yaml_config: Agent YAML configuration

        Returns:
            str: Formatted YAML frontmatter
        """
        if not yaml_config:
            logging.warning("No YAML config available for frontmatter generation")
            return ""

        # Extract agent metadata
        agent_name = agent_file.stem
        agent_info = yaml_config.get("agent", {})

        # Get description from multiple possible sources
        description = (
            agent_info.get("whenToUse")
            or agent_info.get("description")
            or agent_info.get("title")
            or f"{agent_name} specialized agent"
        )

        # Build frontmatter dictionary
        frontmatter = {
            "name": agent_name,
            "description": description,
            "model": yaml_config.get("model", "inherit"),
        }

        try:
            yaml_content = yaml.dump(
                frontmatter, default_flow_style=False, sort_keys=False
            )
            return f"---\n{yaml_content}---\n\n"
        except Exception as e:
            logging.error(f"Failed to generate frontmatter: {e}")
            return ""

    def rebuild_yaml_block(self, yaml_config: Dict[str, Any]) -> str:
        """
        Rebuild the YAML configuration block with resolved paths.

        Args:
            yaml_config: Agent YAML configuration

        Returns:
            str: Formatted YAML block
        """
        if not yaml_config:
            return ""

        # Resolve any {root} placeholders in the configuration
        resolved_config = self.dependency_resolver.resolve_placeholders(yaml_config)

        try:
            yaml_content = yaml.dump(
                resolved_config, default_flow_style=False, sort_keys=False
            )
            return f"```yaml\n{yaml_content}```\n"
        except Exception as e:
            logging.error(f"Failed to generate YAML block: {e}")
            return ""

    def generate_agent_content(self, agent_file: Path) -> str:
        """
        Generate complete agent content with embedded dependencies and embed injections.

        Args:
            agent_file: Path to source agent file

        Returns:
            str: Complete agent content with Claude Code compatible YAML frontmatter
        """
        try:
            # Read source file
            source_content = self.file_manager.read_file(agent_file)
            if not source_content:
                raise ValueError(f"Could not read agent file: {agent_file}")

            # Extract YAML configuration
            yaml_config, remaining_content = self.extract_yaml_block(source_content)

            # Process embed injection markers in the main content
            processed_content = self.process_embed_injections(remaining_content)

            # Build output content
            output_parts = []

            # CRITICAL: Generate Claude Code compatible YAML frontmatter FIRST
            if yaml_config:
                frontmatter = self.generate_frontmatter(agent_file, yaml_config)
                if frontmatter:
                    output_parts.append(
                        frontmatter.rstrip()
                    )  # Remove trailing newlines, we'll add them consistently
                else:
                    logging.warning(
                        f"Failed to generate frontmatter for {agent_file.name}, agent may not be recognized by Claude Code"
                    )

            # Add the main content (with embed injections processed)
            output_parts.append(processed_content.strip())

            # Process and embed dependencies
            if yaml_config:
                embedded_deps = self.process_dependencies(yaml_config)
                if embedded_deps:
                    output_parts.append(embedded_deps)

                # Add resolved YAML configuration at the end
                yaml_block = self.rebuild_yaml_block(yaml_config)
                if yaml_block:
                    output_parts.append("\n## Agent Configuration\n")
                    output_parts.append(yaml_block)

            return "\n\n".join(filter(None, output_parts))

        except Exception as e:
            logging.error(f"Error generating agent content for {agent_file}: {e}")
            raise

    def process_agent(self, agent_file: Path) -> bool:
        """
        Process a single agent file.

        Args:
            agent_file: Path to agent file to process

        Returns:
            bool: True if successful
        """
        try:
            agent_name = agent_file.stem
            logging.info(f"Processing agent: {agent_name}")

            # Generate agent content with embedded dependencies
            agent_content = self.generate_agent_content(agent_file)

            # Determine output path
            output_path = self.output_dir / "agents" / "nw" / f"{agent_name}.md"

            # Write output file
            success = self.file_manager.write_file(output_path, agent_content)

            if success:
                logging.debug(f"Generated agent: {output_path}")
                return True
            else:
                logging.error(f"Failed to write agent file: {output_path}")
                return False

        except Exception as e:
            logging.error(f"Error processing agent {agent_file}: {e}")
            raise

    def get_agent_info(self, agent_file: Path) -> Optional[Dict[str, Any]]:
        """
        Extract agent information for configuration generation.

        Args:
            agent_file: Path to agent file

        Returns:
            dict: Agent information or None if extraction fails
        """
        try:
            content = self.file_manager.read_file(agent_file)
            if not content:
                return None

            yaml_config, _ = self.extract_yaml_block(content)
            if not yaml_config:
                return None

            agent_info = yaml_config.get("agent", {})
            agent_info["file"] = agent_file.stem

            return agent_info

        except Exception as e:
            logging.error(f"Error extracting agent info from {agent_file}: {e}")
            return None
