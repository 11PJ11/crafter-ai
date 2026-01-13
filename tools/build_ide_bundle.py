#!/usr/bin/env python3
"""
5D-WAVE IDE Bundle Builder

Main orchestrator script that transforms 5D-WAVE methodology source files
into IDE-compatible distributions organized under the "dw" category.

Usage:
    python build_ide_bundle.py [options]

Options:
    --source-dir    Source directory (default: 5d-wave)
    --output-dir    Output directory (default: dist/ide)
    --clean         Clean output directory before build
    --verbose       Enable verbose logging
    --dry-run       Show what would be built without creating files
"""

import argparse
import logging
import sys
import shutil
from pathlib import Path
from typing import Dict, List, Optional
import yaml
import json
from datetime import datetime

# Import our processing modules
from processors.agent_processor import AgentProcessor
from processors.command_processor import CommandProcessor
from processors.team_processor import TeamProcessor
from processors.workflow_processor import WorkflowProcessor
from utils.config_manager import ConfigManager
from utils.file_manager import FileManager


class IDEBundleBuilder:
    """Main builder class that orchestrates the 5D-WAVE IDE bundling process."""

    def __init__(self, source_dir: Path, output_dir: Path, dry_run: bool = False):
        self.source_dir = Path(source_dir)
        self.output_dir = Path(output_dir)
        self.dry_run = dry_run

        # Initialize components
        self.file_manager = FileManager(dry_run=dry_run)
        self.config_manager = ConfigManager(self.source_dir / "config.yaml")

        # Initialize processors
        self.agent_processor = AgentProcessor(self.source_dir, self.output_dir, self.file_manager)
        self.command_processor = CommandProcessor(self.source_dir, self.output_dir, self.file_manager)
        self.team_processor = TeamProcessor(self.source_dir, self.output_dir, self.file_manager)
        self.workflow_processor = WorkflowProcessor(self.source_dir, self.output_dir, self.file_manager)

        # Build statistics
        self.stats = {
            'agents_processed': 0,
            'commands_processed': 0,
            'teams_processed': 0,
            'workflows_processed': 0,
            'errors': 0,
            'warnings': 0
        }

    def validate_source(self) -> bool:
        """Validate that the source directory contains required 5D-WAVE structure."""
        required_dirs = ['agents', 'tasks', 'workflows', 'templates', 'data']
        required_files = ['config.yaml']

        logging.info(f"Validating source directory: {self.source_dir}")

        # Check required directories
        for dir_name in required_dirs:
            dir_path = self.source_dir / dir_name
            if not dir_path.exists():
                logging.error(f"Required directory missing: {dir_path}")
                return False
            logging.debug(f"✓ Found directory: {dir_name}")

        # Check required files
        for file_name in required_files:
            file_path = self.source_dir / file_name
            if not file_path.exists():
                logging.error(f"Required file missing: {file_path}")
                return False
            logging.debug(f"✓ Found file: {file_name}")

        logging.info("Source validation completed successfully")
        return True

    def prepare_output_structure(self) -> None:
        """Create the output directory structure."""
        output_dirs = [
            self.output_dir / "agents" / "dw",
            self.output_dir / "commands" / "dw"
        ]

        for dir_path in output_dirs:
            self.file_manager.ensure_directory(dir_path)
            logging.debug(f"Created output directory: {dir_path}")

    def process_agents(self) -> None:
        """Process all agent files (reviewers now embedded via critique-dimensions.md)."""
        logging.info("Processing agents...")
        agents_dir = self.source_dir / "agents"

        if not agents_dir.exists():
            logging.warning(f"Agents directory not found: {agents_dir}")
            return

        # Process agent files
        agent_files = list(agents_dir.glob("*.md"))
        logging.info(f"Found {len(agent_files)} agent files")

        for agent_file in agent_files:
            try:
                logging.info(f"Processing agent: {agent_file.stem}")
                self.agent_processor.process_agent(agent_file)
                self.stats['agents_processed'] += 1
            except Exception as e:
                logging.error(f"Error processing agent {agent_file.name}: {e}")
                self.stats['errors'] += 1

    def process_commands(self) -> None:
        """Process all task files into commands."""
        logging.info("Processing commands...")
        tasks_dir = self.source_dir / "tasks" / "dw"

        if not tasks_dir.exists():
            logging.warning(f"Tasks directory not found: {tasks_dir}")
            return

        task_files = list(tasks_dir.glob("*.md"))
        logging.info(f"Found {len(task_files)} task files")

        for task_file in task_files:
            try:
                logging.debug(f"Processing task: {task_file.name}")
                self.command_processor.process_task(task_file, self.config_manager.get_config())
                self.stats['commands_processed'] += 1
            except Exception as e:
                logging.error(f"Error processing task {task_file.name}: {e}")
                self.stats['errors'] += 1

    def process_teams(self) -> None:
        """Process all team files into massive agents."""
        logging.info("Processing teams...")
        teams_dir = self.source_dir / "agent-teams"

        if not teams_dir.exists():
            logging.warning(f"Agent teams directory not found: {teams_dir}")
            return

        team_files = list(teams_dir.glob("*.yaml"))
        logging.info(f"Found {len(team_files)} team files")

        for team_file in team_files:
            try:
                logging.debug(f"Processing team: {team_file.name}")
                self.team_processor.process_team(team_file, self.config_manager.get_config())
                self.stats['teams_processed'] += 1
            except Exception as e:
                logging.error(f"Error processing team {team_file.name}: {e}")
                self.stats['errors'] += 1

    def process_workflows(self) -> None:
        """Process all workflow files into orchestrator agents."""
        logging.info("Processing workflows...")
        workflows_dir = self.source_dir / "workflows"

        if not workflows_dir.exists():
            logging.warning(f"Workflows directory not found: {workflows_dir}")
            return

        workflow_files = list(workflows_dir.glob("*.yaml"))
        logging.info(f"Found {len(workflow_files)} workflow files")

        for workflow_file in workflow_files:
            try:
                logging.debug(f"Processing workflow: {workflow_file.name}")
                self.workflow_processor.process_workflow(workflow_file, self.config_manager.get_config())
                self.stats['workflows_processed'] += 1
            except Exception as e:
                logging.error(f"Error processing workflow {workflow_file.name}: {e}")
                self.stats['errors'] += 1

    def generate_config(self) -> None:
        """Generate the IDE configuration file."""
        logging.info("Generating IDE configuration...")

        config_output_path = self.output_dir / "agents" / "dw" / "config.json"

        try:
            ide_config = self.config_manager.generate_ide_config(self.stats)

            if not self.dry_run:
                with open(config_output_path, 'w', encoding='utf-8') as f:
                    json.dump(ide_config, f, indent=2, ensure_ascii=False)
                logging.info(f"Generated IDE config: {config_output_path}")
            else:
                logging.info(f"[DRY RUN] Would generate IDE config: {config_output_path}")

        except Exception as e:
            logging.error(f"Error generating IDE config: {e}")
            self.stats['errors'] += 1

    def print_summary(self) -> None:
        """Print build summary statistics."""
        print("\n" + "="*60)
        print("5D-WAVE IDE Bundle Build Summary")
        print("="*60)
        print(f"Agents processed:    {self.stats['agents_processed']}")
        print(f"Commands processed:  {self.stats['commands_processed']}")
        print(f"Teams processed:     {self.stats['teams_processed']}")
        print(f"Workflows processed: {self.stats['workflows_processed']}")
        print(f"Warnings:            {self.stats['warnings']}")
        print(f"Errors:              {self.stats['errors']}")
        print(f"Output directory:    {self.output_dir}")

        if self.dry_run:
            print("\n[DRY RUN MODE] No files were actually created")

        if self.stats['errors'] > 0:
            print(f"\n⚠️  Build completed with {self.stats['errors']} errors")
            return False
        else:
            print("\n✅ Build completed successfully!")
            return True

    def build(self) -> bool:
        """Execute the complete build process."""
        start_time = datetime.now()
        logging.info(f"Starting 5D-WAVE IDE bundle build at {start_time}")

        try:
            # Validation
            if not self.validate_source():
                logging.error("Source validation failed")
                return False

            # Preparation
            self.prepare_output_structure()

            # Processing
            self.process_agents()
            self.process_commands()
            self.process_teams()
            self.process_workflows()

            # Configuration
            self.generate_config()

            # Summary
            end_time = datetime.now()
            duration = end_time - start_time
            logging.info(f"Build completed in {duration.total_seconds():.2f} seconds")

            return self.print_summary()

        except KeyboardInterrupt:
            logging.info("Build interrupted by user")
            return False
        except Exception as e:
            logging.error(f"Unexpected error during build: {e}")
            return False


def setup_logging(verbose: bool = False) -> None:
    """Configure logging based on verbosity level."""
    level = logging.DEBUG if verbose else logging.INFO
    format_str = '%(asctime)s - %(levelname)s - %(message)s'

    logging.basicConfig(
        level=level,
        format=format_str,
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('build.log', mode='w')
        ]
    )


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Build 5D-WAVE IDE bundles from methodology source files"
    )
    parser.add_argument(
        "--source-dir",
        type=Path,
        default="../5d-wave",
        help="Source directory containing 5D-WAVE files (default: ../5d-wave)"
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default="../dist/ide",
        help="Output directory for IDE bundles (default: ../dist/ide)"
    )
    parser.add_argument(
        "--clean",
        action="store_true",
        help="Clean output directory before build"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose logging"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be built without creating files"
    )

    args = parser.parse_args()

    # Setup logging
    setup_logging(args.verbose)

    # Clean output directory if requested
    if args.clean and args.output_dir.exists():
        import shutil
        if not args.dry_run:
            shutil.rmtree(args.output_dir)
            logging.info(f"Cleaned output directory: {args.output_dir}")
        else:
            logging.info(f"[DRY RUN] Would clean output directory: {args.output_dir}")

    # Build
    builder = IDEBundleBuilder(args.source_dir, args.output_dir, args.dry_run)
    success = builder.build()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()