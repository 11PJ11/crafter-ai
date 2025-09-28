"""
Workflow Processor

Processes 5D-WAVE workflow YAML files and converts them into orchestrator agent files
that guide multi-phase 5D-WAVE methodology execution.
"""

import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
import yaml

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from utils.dependency_resolver import DependencyResolver


class WorkflowProcessor:
    """Processes workflow files into orchestrator agent files."""

    def __init__(self, source_dir: Path, output_dir: Path, file_manager):
        self.source_dir = Path(source_dir)
        self.output_dir = Path(output_dir)
        self.file_manager = file_manager
        self.dependency_resolver = DependencyResolver(source_dir, file_manager)

    def load_workflow_config(self, workflow_file: Path) -> Optional[Dict[str, Any]]:
        """
        Load workflow configuration from YAML file.

        Args:
            workflow_file: Path to workflow YAML file

        Returns:
            dict: Workflow configuration or None if loading fails
        """
        try:
            content = self.file_manager.read_file(workflow_file)
            if not content:
                return None

            return yaml.safe_load(content)

        except yaml.YAMLError as e:
            logging.error(f"Failed to parse workflow YAML {workflow_file}: {e}")
            return None
        except Exception as e:
            logging.error(f"Error loading workflow config {workflow_file}: {e}")
            return None

    def get_workflow_info_from_config(self, workflow_name: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract workflow information from main config.yaml.

        Args:
            workflow_name: Name of the workflow
            config: Full configuration dictionary

        Returns:
            dict: Workflow information
        """
        workflows = config.get('workflows', {})

        # Look for exact match first
        if workflow_name in workflows:
            return workflows[workflow_name]

        # Look for workflow name without extension
        workflow_base = Path(workflow_name).stem.replace('-', '_')
        if workflow_base in workflows:
            return workflows[workflow_base]

        # Return default workflow info
        return {
            'name': workflow_name,
            'description': f'{workflow_name} workflow orchestration',
            'phases': config.get('wave_phases', ['DISCUSS', 'DESIGN', 'DISTILL', 'DEVELOP', 'DEMO'])
        }

    def generate_orchestrator_header(self, workflow_name: str, workflow_config: Dict[str, Any], main_config: Dict[str, Any]) -> str:
        """
        Generate header for orchestrator agent.

        Args:
            workflow_name: Name of the workflow
            workflow_config: Workflow-specific configuration
            main_config: Main configuration dictionary

        Returns:
            str: Formatted orchestrator header
        """
        workflow_base = Path(workflow_name).stem
        workflow_info = self.get_workflow_info_from_config(workflow_name, main_config)

        # Extract workflow metadata
        workflow_meta = workflow_config.get('workflow', {})
        workflow_title = workflow_meta.get('name', workflow_base.replace('-', ' ').title())

        header_parts = [
            f"# {workflow_base}-orchestrator",
            "",
            "ACTIVATION-NOTICE: This is a workflow orchestrator agent that guides complete 5D-WAVE methodology execution.",
            "",
            "CRITICAL: This orchestrator coordinates multi-phase workflows. Follow the phase guidance and agent coordination patterns defined below.",
            "",
            f"## Orchestrator Identity",
            f"**Workflow**: {workflow_title}",
            f"**Description**: {workflow_info.get('description', 'Multi-phase 5D-WAVE orchestration')}",
            f"**Methodology**: 5D-WAVE ({' → '.join(workflow_info.get('phases', []))})",
            ""
        ]

        return "\n".join(header_parts)

    def generate_phase_guidance(self, workflow_config: Dict[str, Any], main_config: Dict[str, Any]) -> str:
        """
        Generate phase guidance section.

        Args:
            workflow_config: Workflow configuration
            main_config: Main configuration dictionary

        Returns:
            str: Phase guidance content
        """
        workflow_info = workflow_config.get('workflow', {})
        phases = workflow_info.get('phases', main_config.get('wave_phases', []))

        if not phases:
            return "## Phase Guidance\n\nNo phases defined for this workflow.\n"

        guidance_parts = [
            "## Phase Guidance",
            "",
            "Execute the 5D-WAVE methodology in the following sequence:",
            ""
        ]

        for i, phase in enumerate(phases, 1):
            guidance_parts.extend([
                f"### {i}. {phase} Wave",
                ""
            ])

            # Add phase-specific guidance
            phase_guidance = self.get_phase_specific_guidance(phase, main_config)
            guidance_parts.extend(phase_guidance)
            guidance_parts.append("")

        return "\n".join(guidance_parts)

    def get_phase_specific_guidance(self, phase: str, config: Dict[str, Any]) -> List[str]:
        """
        Get specific guidance for a phase.

        Args:
            phase: Phase name
            config: Main configuration dictionary

        Returns:
            list: Phase guidance lines
        """
        # Get agents assigned to this phase
        phase_agents = []
        agents = config.get('agents', {})

        for agent_name, agent_info in agents.items():
            if agent_info.get('wave') == phase:
                role = agent_info.get('role', 'Unknown')
                priority = agent_info.get('priority', 'Normal')
                phase_agents.append(f"- **{agent_name}** ({role}) - Priority: {priority}")

        guidance = []

        # Standard phase descriptions
        phase_descriptions = {
            'DISCUSS': [
                "**Objective**: Gather and analyze business requirements",
                "**Focus**: Stakeholder collaboration, requirements clarity, business value",
                "**Outputs**: Requirements document, user stories, acceptance criteria"
            ],
            'DESIGN': [
                "**Objective**: Create system architecture and design",
                "**Focus**: Technical design, architecture patterns, component boundaries",
                "**Outputs**: Architecture document, design diagrams, technical specifications"
            ],
            'DISTILL': [
                "**Objective**: Create acceptance tests and validation scenarios",
                "**Focus**: Test scenarios, business validation, acceptance criteria",
                "**Outputs**: Acceptance tests, test scenarios, validation frameworks"
            ],
            'DEVELOP': [
                "**Objective**: Implement solution using Outside-In TDD",
                "**Focus**: Test-driven development, code quality, systematic refactoring",
                "**Outputs**: Working code, test suite, refactored implementation"
            ],
            'DEMO': [
                "**Objective**: Validate production readiness and demonstrate value",
                "**Focus**: Production deployment, stakeholder validation, business value",
                "**Outputs**: Production deployment, stakeholder demo, value metrics"
            ]
        }

        # Add standard description
        if phase in phase_descriptions:
            guidance.extend(phase_descriptions[phase])
            guidance.append("")

        # Add assigned agents
        if phase_agents:
            guidance.append("**Primary Agents**:")
            guidance.extend(phase_agents)
        else:
            guidance.append("**Primary Agents**: None specifically assigned")

        return guidance

    def generate_workflow_definition(self, workflow_config: Dict[str, Any]) -> str:
        """
        Generate embedded workflow definition.

        Args:
            workflow_config: Workflow configuration

        Returns:
            str: Workflow definition content
        """
        try:
            yaml_content = yaml.dump(workflow_config, default_flow_style=False, sort_keys=False)
            return f"## Workflow Definition\n\n```yaml\n{yaml_content}```\n"

        except Exception as e:
            logging.error(f"Failed to generate workflow YAML: {e}")
            return "## Workflow Definition\n\nWorkflow definition unavailable.\n"

    def generate_agent_coordination(self, workflow_config: Dict[str, Any], main_config: Dict[str, Any]) -> str:
        """
        Generate agent coordination section.

        Args:
            workflow_config: Workflow configuration
            main_config: Main configuration dictionary

        Returns:
            str: Agent coordination content
        """
        coordination_parts = [
            "## Agent Coordination",
            "",
            "This orchestrator coordinates the following agent interactions:",
            ""
        ]

        # Get all agents and their wave assignments
        agents = main_config.get('agents', {})
        wave_agents = {}

        for agent_name, agent_info in agents.items():
            wave = agent_info.get('wave', 'UNKNOWN')
            if wave not in wave_agents:
                wave_agents[wave] = []
            wave_agents[wave].append({
                'name': agent_name,
                'role': agent_info.get('role', 'Unknown'),
                'priority': agent_info.get('priority', 'Normal')
            })

        # Add coordination by wave
        for wave, wave_agent_list in wave_agents.items():
            if wave == 'UNKNOWN':
                continue

            coordination_parts.extend([
                f"### {wave} Wave Coordination",
                ""
            ])

            for agent in sorted(wave_agent_list, key=lambda x: x['priority']):
                coordination_parts.append(f"- **{agent['name']}**: {agent['role']}")

            coordination_parts.append("")

        return "\n".join(coordination_parts)

    def generate_orchestrator_content(self, workflow_file: Path, config: Dict[str, Any]) -> str:
        """
        Generate complete orchestrator agent content.

        Args:
            workflow_file: Path to source workflow file
            config: Main configuration dictionary

        Returns:
            str: Complete orchestrator content
        """
        try:
            # Load workflow configuration
            workflow_config = self.load_workflow_config(workflow_file)
            if not workflow_config:
                raise ValueError(f"Could not load workflow config: {workflow_file}")

            workflow_name = workflow_file.name

            # Generate content sections
            content_parts = []

            # Header
            header = self.generate_orchestrator_header(workflow_name, workflow_config, config)
            content_parts.append(header)

            # Phase guidance
            phase_guidance = self.generate_phase_guidance(workflow_config, config)
            content_parts.append(phase_guidance)

            # Agent coordination
            agent_coordination = self.generate_agent_coordination(workflow_config, config)
            content_parts.append(agent_coordination)

            # Workflow definition
            workflow_def = self.generate_workflow_definition(workflow_config)
            content_parts.append(workflow_def)

            return "\n".join(content_parts)

        except Exception as e:
            logging.error(f"Error generating orchestrator content for {workflow_file}: {e}")
            raise

    def process_workflow(self, workflow_file: Path, config: Dict[str, Any]) -> bool:
        """
        Process a single workflow file into an orchestrator agent.

        Args:
            workflow_file: Path to workflow file to process
            config: Configuration dictionary

        Returns:
            bool: True if successful
        """
        try:
            workflow_name = workflow_file.stem
            logging.info(f"Processing workflow: {workflow_name}")

            # Generate orchestrator content
            orchestrator_content = self.generate_orchestrator_content(workflow_file, config)

            # Determine output path - workflows become orchestrator agents
            output_path = self.output_dir / "agents" / "dw" / f"{workflow_name}-orchestrator.md"

            # Write output file
            success = self.file_manager.write_file(output_path, orchestrator_content)

            if success:
                logging.debug(f"Generated orchestrator: {output_path}")
                return True
            else:
                logging.error(f"Failed to write orchestrator file: {output_path}")
                return False

        except Exception as e:
            logging.error(f"Error processing workflow {workflow_file}: {e}")
            return False

    def get_workflow_info(self, workflow_file: Path, config: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Extract workflow information for configuration generation.

        Args:
            workflow_file: Path to workflow file
            config: Configuration dictionary

        Returns:
            dict: Workflow information or None if extraction fails
        """
        try:
            workflow_config = self.load_workflow_config(workflow_file)
            if not workflow_config:
                return None

            workflow_info = self.get_workflow_info_from_config(workflow_file.name, config)
            workflow_meta = workflow_config.get('workflow', {})

            return {
                'name': workflow_file.stem,
                'file': f"{workflow_file.stem}-orchestrator.md",
                'description': workflow_info.get('description'),
                'phases': workflow_info.get('phases', []),
                'type': 'orchestrator'
            }

        except Exception as e:
            logging.error(f"Error extracting workflow info from {workflow_file}: {e}")
            return None