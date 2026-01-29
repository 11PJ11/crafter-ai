#!/usr/bin/env python3
"""
nWave Framework Installation Script

Cross-platform installer for the nWave methodology framework.
Installs specialized agents and commands to global Claude config directory.

Usage: python install_nwave.py [--backup-only] [--restore] [--dry-run] [--help]
"""

import argparse
import subprocess
import sys
from pathlib import Path

# Support both standalone execution and package import
try:
    from scripts.install.install_utils import (
        BackupManager,
        Colors,
        Logger,
        ManifestWriter,
        PathUtils,
        VersionUtils,
    )
    from scripts.install.preflight_checker import PreflightChecker
    from scripts.install.output_formatter import format_error
    from scripts.install.installation_verifier import InstallationVerifier
except ImportError:
    # Fallback for standalone execution from scripts/install directory
    from install_utils import (  # noqa: F401
        BackupManager,
        Colors,
        Logger,
        ManifestWriter,
        PathUtils,
        VersionUtils,
    )
    from preflight_checker import PreflightChecker  # noqa: F401
    from output_formatter import format_error  # noqa: F401
    from installation_verifier import InstallationVerifier  # noqa: F401

__version__ = "1.2.0"


class NWaveInstaller:
    """nWave framework installer."""

    def __init__(self, dry_run: bool = False, force_rebuild: bool = False):
        """Initialize installer."""
        self.dry_run = dry_run
        self.force_rebuild = force_rebuild
        self.script_dir = Path(__file__).parent
        self.project_root = PathUtils.get_project_root(self.script_dir)
        self.claude_config_dir = PathUtils.get_claude_config_dir()
        self.framework_source = self.project_root / "dist" / "ide"

        log_file = self.claude_config_dir / "nwave-install.log"
        self.logger = Logger(log_file if not dry_run else None)

        self.backup_manager = BackupManager(self.logger, "install")

    def run_embedding(self) -> bool:
        """Run source embedding to update embedded content."""
        embed_script = self.project_root / "tools" / "embed_sources.py"

        if not embed_script.exists():
            return True  # Not critical

        self.logger.info("Running source embedding to update embedded content...")

        try:
            result = subprocess.run(
                [sys.executable, str(embed_script)],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=60,
            )

            if result.returncode == 0:
                self.logger.info("Source embedding completed")
                return True
            else:
                self.logger.warn("Source embedding had issues, continuing anyway...")
                return True
        except Exception as e:
            self.logger.warn(f"Source embedding failed: {e}, continuing anyway...")
            return True

    def build_framework(self) -> bool:
        """Build the IDE bundle."""
        self.logger.info("Building IDE bundle...")

        build_script = self.project_root / "scripts" / "build-ide-bundle.sh"

        if not build_script.exists():
            # Try Python build script as fallback
            build_script = self.project_root / "tools" / "build.py"
            if not build_script.exists():
                self.logger.error(f"Build script not found at: {build_script}")
                return False

            try:
                result = subprocess.run(
                    [sys.executable, str(build_script)],
                    cwd=self.project_root,
                    capture_output=True,
                    text=True,
                )

                if result.returncode == 0:
                    self.logger.info("Build completed successfully")
                    return True
                else:
                    self.logger.error("Build failed")
                    self.logger.error(result.stderr)
                    return False
            except Exception as e:
                self.logger.error(f"Build failed: {e}")
                return False
        else:
            # Run shell script
            try:
                result = subprocess.run(
                    ["bash", str(build_script)],
                    cwd=self.project_root,
                    capture_output=True,
                    text=True,
                )

                # Look for success indicators
                if "Build completed" in result.stdout or "✅" in result.stdout:
                    self.logger.info("Build completed successfully")
                    return True
                else:
                    self.logger.error("Build failed")
                    return False
            except Exception as e:
                self.logger.error(f"Build failed: {e}")
                return False

    def check_source(self) -> bool:
        """Check if source framework exists, build if necessary."""
        self.logger.info("Checking source framework...")

        # Run embedding first
        self.run_embedding()

        # Force rebuild if requested
        if self.force_rebuild:
            self.logger.info("Force rebuild requested, rebuilding framework...")
            if not self.build_framework():
                return False
            return True

        # Check if dist/ide exists
        if not self.framework_source.exists():
            self.logger.info("Distribution not found, building framework...")
            if not self.build_framework():
                return False

        # Check for built IDE distribution structure
        agents_dir = self.framework_source / "agents" / "nw"
        commands_dir = self.framework_source / "commands" / "nw"

        if not agents_dir.exists() or not commands_dir.exists():
            self.logger.info("Distribution incomplete, rebuilding framework...")
            if not self.build_framework():
                return False

        # Check if source files are newer than distribution
        source_dir = self.project_root / "nWave"
        newest_source = PathUtils.find_newest_file(source_dir)
        newest_dist = PathUtils.find_newest_file(self.framework_source)

        if newest_source and newest_dist:
            if newest_source.stat().st_mtime > newest_dist.stat().st_mtime:
                self.logger.info(
                    "Source files are newer than distribution, rebuilding..."
                )
                if not self.build_framework():
                    return False

        agent_count = PathUtils.count_files(agents_dir, "*.md")
        command_count = PathUtils.count_files(commands_dir, "*.md")

        self.logger.info(
            f"Found framework with {agent_count} agent files and {command_count} commands"
        )

        if agent_count < 10:
            self.logger.warn(
                f"Expected 10+ agents, found only {agent_count}. Continuing anyway..."
            )

        return True

    def create_backup(self) -> None:
        """Create backup of existing installation."""
        self.backup_manager.create_backup(dry_run=self.dry_run)

    def restore_backup(self) -> bool:
        """Restore from most recent backup."""
        self.logger.info("Looking for backups to restore...")

        backup_root = self.claude_config_dir / "backups"
        if not backup_root.exists():
            self.logger.error(f"No backups found in {backup_root}")
            return False

        # Find latest backup
        backups = sorted(backup_root.glob("nwave-*"))
        if not backups:
            self.logger.error("No nWave backups found")
            return False

        latest_backup = backups[-1]
        self.logger.info(f"Restoring from backup: {latest_backup}")

        # Remove current installation
        agents_dir = self.claude_config_dir / "agents"
        commands_dir = self.claude_config_dir / "commands"

        if agents_dir.exists():
            import shutil

            shutil.rmtree(agents_dir)
        if commands_dir.exists():
            import shutil

            shutil.rmtree(commands_dir)

        # Restore from backup
        backup_agents = latest_backup / "agents"
        backup_commands = latest_backup / "commands"

        if backup_agents.exists():
            import shutil

            shutil.copytree(backup_agents, agents_dir)
            self.logger.info("Restored agents directory")

        if backup_commands.exists():
            import shutil

            shutil.copytree(backup_commands, commands_dir)
            self.logger.info("Restored commands directory")

        self.logger.info(f"Restoration complete from backup: {latest_backup}")
        return True

    def install_framework(self) -> bool:
        """Install framework files."""
        if self.dry_run:
            self.logger.info(
                f"[DRY RUN] Would install nWave framework to: {self.claude_config_dir}"
            )
            self.logger.info(
                f"[DRY RUN] Would create target directory: {self.claude_config_dir}"
            )

            # Show what would be installed
            agents_dir = self.framework_source / "agents" / "nw"
            commands_dir = self.framework_source / "commands" / "nw"

            if agents_dir.exists():
                agent_count = PathUtils.count_files(agents_dir, "*.md")
                self.logger.info(f"[DRY RUN] Would install {agent_count} agent files")

            if commands_dir.exists():
                command_count = PathUtils.count_files(commands_dir, "*.md")
                self.logger.info(
                    f"[DRY RUN] Would install {command_count} command files"
                )

            return True

        self.logger.info(f"Installing nWave framework to: {self.claude_config_dir}")

        # Create target directories
        self.claude_config_dir.mkdir(parents=True, exist_ok=True)

        # Install agents
        self._install_agents()

        # Install commands
        self._install_commands()

        # Install utility scripts
        self._install_utility_scripts()

        # Install templates
        self._install_templates()

        return True

    def _install_agents(self):
        """Install agent files."""
        self.logger.info("Installing agents...")

        source_agent_dir = self.project_root / "nWave" / "agents"
        dist_agent_dir = self.framework_source / "agents" / "nw"
        target_agent_dir = self.claude_config_dir / "agents" / "nw"

        target_agent_dir.mkdir(parents=True, exist_ok=True)

        # Count agents
        dist_agent_count = (
            PathUtils.count_files(dist_agent_dir, "*.md")
            if dist_agent_dir.exists()
            else 0
        )
        source_agent_count = (
            PathUtils.count_files(source_agent_dir, "*.md")
            if source_agent_dir.exists()
            else 0
        )

        # Use dist if it has most agents, otherwise fall back to source
        if dist_agent_count >= (source_agent_count // 2) and dist_agent_count > 5:
            self.logger.info(
                f"Installing from built distribution ({dist_agent_count} agents)..."
            )
            PathUtils.copy_tree_with_filter(
                dist_agent_dir, target_agent_dir, exclude_patterns=["README.md"]
            )
        else:
            self.logger.info(
                f"Build incomplete ({dist_agent_count}/{source_agent_count} agents), using source files..."
            )
            PathUtils.copy_tree_with_filter(
                source_agent_dir, target_agent_dir, exclude_patterns=["README.md"]
            )

        copied_agents = PathUtils.count_files(target_agent_dir, "*.md")
        self.logger.info(f"Installed {copied_agents} agent files")

    def _install_commands(self):
        """Install command files."""
        self.logger.info("Installing commands...")

        commands_source = self.framework_source / "commands"
        commands_target = self.claude_config_dir / "commands"

        if commands_source.exists():
            import shutil

            for item in commands_source.iterdir():
                target = commands_target / item.name
                if item.is_dir():
                    if target.exists():
                        shutil.rmtree(target)
                    shutil.copytree(item, target)
                else:
                    shutil.copy2(item, target)

            copied_commands = PathUtils.count_files(commands_target, "*.md")
            self.logger.info(f"Installed {copied_commands} command files")

            dw_commands_dir = commands_target / "nw"
            if dw_commands_dir.exists():
                dw_commands = PathUtils.count_files(dw_commands_dir, "*.md")
                self.logger.info(f"  - DW commands: {dw_commands} essential commands")

    def _install_utility_scripts(self):
        """Install utility scripts for target projects."""
        self.logger.info("Installing utility scripts...")

        scripts_source = self.project_root / "scripts"
        scripts_target = self.claude_config_dir / "scripts"
        scripts_target.mkdir(parents=True, exist_ok=True)

        # List of utility scripts to install with version checking
        utility_scripts = ["install_nwave_target_hooks.py", "validate_step_file.py"]

        installed_count = 0
        for script_name in utility_scripts:
            source_script = scripts_source / script_name
            target_script = scripts_target / script_name

            if not source_script.exists():
                continue

            source_ver = VersionUtils.extract_version_from_file(source_script)
            target_ver = (
                VersionUtils.extract_version_from_file(target_script)
                if target_script.exists()
                else "0.0.0"
            )

            if VersionUtils.compare_versions(source_ver, target_ver) > 0:
                import shutil

                shutil.copy2(source_script, target_script)
                self.logger.info(
                    f"Upgraded {script_name} ({target_ver} → {source_ver})"
                )
                installed_count += 1
            elif not target_script.exists():
                import shutil

                shutil.copy2(source_script, target_script)
                self.logger.info(f"Installed {script_name} (v{source_ver})")
                installed_count += 1
            else:
                self.logger.info(f"{script_name} already up-to-date (v{target_ver})")

        if installed_count > 0:
            total_scripts = PathUtils.count_files(scripts_target, "*.py")
            self.logger.info(f"Total {total_scripts} utility script(s) installed")

    def _install_templates(self):
        """Install template files."""
        self.logger.info("Installing templates...")

        templates_source = self.project_root / "nWave" / "templates"
        templates_target = self.claude_config_dir / "templates"
        templates_target.mkdir(parents=True, exist_ok=True)

        # Install canonical schema
        schema_file = "step-tdd-cycle-schema.json"
        source_schema = templates_source / schema_file

        if source_schema.exists():
            import shutil

            shutil.copy2(source_schema, templates_target / schema_file)
            self.logger.info(f"Installed canonical schema: {schema_file}")

        copied_templates = PathUtils.count_files(templates_target, "*.json")
        if copied_templates > 0:
            self.logger.info(f"Total {copied_templates} template(s) installed")

    def _validate_schema_template(self) -> bool:
        """Validate TDD cycle schema template has required fields."""
        schema_file = (
            self.claude_config_dir / "templates" / "step-tdd-cycle-schema.json"
        )

        if not schema_file.exists():
            self.logger.error("Schema template not found at expected location")
            return False

        try:
            import json

            with open(schema_file, "r") as f:
                schema = json.load(f)

            # Check for schema_version field
            if "schema_version" not in schema:
                self.logger.error(
                    "Schema template missing 'schema_version' field - installation may have used stale source"
                )
                return False

            schema_version = schema.get("schema_version")
            if schema_version != "2.0":
                self.logger.warn(
                    f"Schema version is {schema_version}, expected 2.0 (8-phase TDD optimization)"
                )

            # Check phase count
            phase_exec_log = schema.get("tdd_cycle", {}).get("phase_execution_log", [])
            if len(phase_exec_log) != 8:
                self.logger.error(
                    f"Schema has {len(phase_exec_log)} phases, expected 8 (v2.0). "
                    f"Installation source may be stale."
                )
                return False

            self.logger.info(f"  - TDD cycle schema: v{schema_version} with 8 phases ✓")
            return True

        except Exception as e:
            self.logger.error(f"Failed to validate schema template: {e}")
            return False

    def validate_installation(self) -> bool:
        """Validate installation using shared InstallationVerifier.

        Uses the InstallationVerifier module for consistent verification logic
        between standalone verification and post-build verification.

        Returns:
            True if verification passed, False otherwise.
        """
        self.logger.info("Validating installation...")

        # Use shared InstallationVerifier for consistent verification
        verifier = InstallationVerifier(claude_config_dir=self.claude_config_dir)
        result = verifier.run_verification()

        # Validate schema template (additional check specific to installer)
        schema_valid = self._validate_schema_template()

        # Log verification results
        self.logger.info("Installation summary:")
        self.logger.info(f"  - Agents installed: {result.agent_file_count}")
        self.logger.info(f"  - Commands installed: {result.command_file_count}")
        self.logger.info(f"  - Installation directory: {self.claude_config_dir}")
        self.logger.info(f"  - Manifest exists: {result.manifest_exists}")

        agents_dir = self.claude_config_dir / "agents" / "nw"
        commands_dir = self.claude_config_dir / "commands" / "nw"

        if agents_dir.exists():
            self.logger.info("  - nWave agents: Available")

        if commands_dir.exists():
            self.logger.info("  - nWave commands: Available")

        if result.agent_file_count < 10:
            self.logger.warn(f"Expected 10+ agents, found {result.agent_file_count}")

        # Report missing essential files
        if result.missing_essential_files:
            for missing_file in result.missing_essential_files:
                self.logger.error(f"Missing essential command: {missing_file}")

        # Determine overall success
        overall_success = result.success and schema_valid

        if overall_success:
            self.logger.info(
                f"Installation validation: {Colors.GREEN}PASSED{Colors.NC}"
            )
            return True
        else:
            error_count = len(result.missing_essential_files) + (0 if schema_valid else 1)
            if not result.manifest_exists:
                error_count += 1
            self.logger.error(
                f"Installation validation: {Colors.RED}FAILED{Colors.NC} ({error_count} errors)"
            )
            return False

    def create_manifest(self) -> None:
        """Create installation manifest."""
        if self.dry_run:
            self.logger.info("[DRY RUN] Would create installation manifest")
            return

        ManifestWriter.write_install_manifest(
            self.claude_config_dir, self.backup_manager.backup_dir, self.script_dir
        )

        self.logger.info(
            f"Installation manifest created: {self.claude_config_dir / 'nwave-manifest.txt'}"
        )


def show_help():
    """Show help message."""
    help_text = f"""{Colors.BLUE}nWave Framework Installation Script for Cross-Platform{Colors.NC}

{Colors.BLUE}DESCRIPTION:{Colors.NC}
    Installs the nWave methodology framework to your global Claude config directory.
    This makes all specialized agents and commands available across all projects.

{Colors.BLUE}USAGE:{Colors.NC}
    python install_nwave.py [OPTIONS]

{Colors.BLUE}OPTIONS:{Colors.NC}
    --backup-only     Create backup of existing nWave installation without installing
    --restore         Restore from the most recent backup
    --force-rebuild   Force rebuild of distribution before installation (ensures fresh source)
    --dry-run         Show what would be installed without making any changes
    --help            Show this help message

{Colors.BLUE}EXAMPLES:{Colors.NC}
    python install_nwave.py                    # Install nWave framework
    python install_nwave.py --force-rebuild    # Rebuild and install with latest sources
    python install_nwave.py --dry-run          # Show what would be installed
    python install_nwave.py --backup-only      # Create backup only
    python install_nwave.py --restore          # Restore from latest backup

{Colors.BLUE}TROUBLESHOOTING:{Colors.NC}
    If installation doesn't pick up recent changes, use --force-rebuild:
    python install_nwave.py --force-rebuild

{Colors.BLUE}WHAT GETS INSTALLED:{Colors.NC}
    - nWave specialized agents (DISCUSS→DESIGN→DISTILL→DEVELOP→DELIVER methodology)
    - nWave command interface for workflow orchestration
    - ATDD (Acceptance Test Driven Development) integration
    - Outside-In TDD with double-loop architecture
    - Quality validation network with continuous refactoring
    - 8-phase TDD enforcement with schema versioning

{Colors.BLUE}INSTALLATION LOCATION:{Colors.NC}
    ~/.claude/agents/nw/    # nWave agent specifications
    ~/.claude/commands/nw/  # nWave command integrations
    ~/.claude/templates/    # TDD cycle schema templates

For more information: https://github.com/11PJ11/crafter-ai
"""
    print(help_text)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Install nWave framework", add_help=False
    )
    parser.add_argument("--backup-only", action="store_true", help="Create backup only")
    parser.add_argument("--restore", action="store_true", help="Restore from backup")
    parser.add_argument(
        "--force-rebuild", action="store_true", help="Force rebuild of distribution"
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Show what would be done"
    )
    parser.add_argument("--help", "-h", action="store_true", help="Show help")

    args = parser.parse_args()

    if args.help:
        show_help()
        return 0

    # Run preflight checks BEFORE any build or installation actions
    # This validates the environment is suitable for installation
    preflight = PreflightChecker()
    preflight_results = preflight.run_all_checks()

    if preflight.has_blocking_failures(preflight_results):
        # Display formatted error for each failed check
        for failed_check in preflight.get_failed_checks(preflight_results):
            error_message = format_error(
                error_code=failed_check.error_code,
                message=failed_check.message,
                remediation=failed_check.remediation or "No remediation available.",
                recoverable=False,
            )
            print(error_message)
        return 1

    installer = NWaveInstaller(dry_run=args.dry_run, force_rebuild=args.force_rebuild)

    installer.logger.info("nWave Framework Installation Script")
    installer.logger.info("=" * 38)

    if args.dry_run:
        installer.logger.info(
            f"{Colors.YELLOW}DRY RUN MODE{Colors.NC} - No changes will be made"
        )

    # Handle backup-only mode
    if args.backup_only:
        if not installer.check_source():
            return 1
        installer.create_backup()
        installer.logger.info("Backup completed successfully")
        return 0

    # Handle restore mode
    if args.restore:
        if installer.restore_backup():
            installer.logger.info("Restoration completed successfully")
            return 0
        else:
            return 1

    # Normal installation
    if not installer.check_source():
        return 1

    installer.create_backup()

    if not installer.install_framework():
        return 1

    if installer.validate_installation():
        installer.create_manifest()

        print()
        installer.logger.info(
            f"{Colors.GREEN}✅ nWave Framework installed successfully!{Colors.NC}"
        )
        print()
        installer.logger.info("Framework Components Installed:")
        installer.logger.info(
            "- nWave specialized agents (DISCUSS→DESIGN→DISTILL→DEVELOP→DELIVER)"
        )
        installer.logger.info("- nWave command interface for workflow orchestration")
        installer.logger.info("- ATDD and Outside-In TDD integration")
        print()
        installer.logger.info("Next steps:")
        installer.logger.info("1. Navigate to any project directory")
        installer.logger.info(
            "2. Use nWave commands to orchestrate development workflow"
        )
        installer.logger.info("3. Access agents through the dw category in Claude Code")
        print()
        installer.logger.info("nWave methodology available:")
        installer.logger.info(
            f"- {Colors.BLUE}/nw:discuss{Colors.NC} - Requirements gathering and business analysis"
        )
        installer.logger.info(
            f"- {Colors.BLUE}/nw:design{Colors.NC} - Architecture design with visual representation"
        )
        installer.logger.info(
            f"- {Colors.BLUE}/nw:distill{Colors.NC} - Acceptance test creation and business validation"
        )
        installer.logger.info(
            f"- {Colors.BLUE}/nw:develop{Colors.NC} - Outside-In TDD implementation with refactoring"
        )
        installer.logger.info(
            f"- {Colors.BLUE}/nw:deliver{Colors.NC} - Production readiness validation"
        )
        print()
        installer.logger.info("Documentation: https://github.com/11PJ11/crafter-ai")
        return 0
    else:
        installer.logger.error("Installation failed validation")
        installer.logger.warn(
            "You can restore the previous installation with: python install_nwave.py --restore"
        )
        return 1


if __name__ == "__main__":
    sys.exit(main())
