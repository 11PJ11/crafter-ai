#!/usr/bin/env python3
"""
AI-Craft Framework Uninstallation Script

Cross-platform uninstaller for the nWave methodology framework.
Completely removes AI-Craft framework from global Claude config directory.

Usage: python uninstall_ai_craft.py [--backup] [--force] [--dry-run] [--help]
"""

import argparse
import shutil
import sys

from install_utils import (
    BackupManager,
    Colors,
    Logger,
    ManifestWriter,
    PathUtils,
    confirm_action,
)

__version__ = "1.0.0"


class AIUninstaller:
    """AI-Craft framework uninstaller."""

    def __init__(
        self,
        backup_before_removal: bool = False,
        force: bool = False,
        dry_run: bool = False,
    ):
        """
        Initialize uninstaller.

        Args:
            backup_before_removal: Create backup before uninstalling
            force: Skip confirmation prompts
            dry_run: Show what would be done without executing
        """
        self.backup_before_removal = backup_before_removal
        self.force = force
        self.dry_run = dry_run

        self.claude_config_dir = PathUtils.get_claude_config_dir()
        log_file = self.claude_config_dir / "ai-craft-uninstall.log"
        self.logger = Logger(log_file if not dry_run else None)

        self.backup_manager = BackupManager(self.logger, "uninstall")

    def check_installation(self) -> bool:
        """Check for existing AI-Craft installation."""
        self.logger.info("Checking for AI-Craft installation...")

        installation_found = False

        agents_dir = self.claude_config_dir / "agents" / "nw"
        commands_dir = self.claude_config_dir / "commands" / "nw"
        manifest_file = self.claude_config_dir / "ai-craft-manifest.txt"
        install_log = self.claude_config_dir / "ai-craft-install.log"
        backups_dir = self.claude_config_dir / "backups"

        if agents_dir.exists():
            installation_found = True
            self.logger.info(f"Found nWave agents in: {agents_dir}")

        if commands_dir.exists():
            installation_found = True
            self.logger.info(f"Found nWave commands in: {commands_dir}")

        if manifest_file.exists():
            installation_found = True
            self.logger.info("Found AI-Craft manifest file")

        if install_log.exists():
            installation_found = True
            self.logger.info("Found AI-Craft installation logs")

        if backups_dir.exists():
            ai_craft_backups = list(backups_dir.glob("ai-craft-*"))
            if ai_craft_backups:
                installation_found = True
                self.logger.info("Found AI-Craft backup directories")

        if not installation_found:
            self.logger.info("No AI-Craft installation found")
            print()
            print(
                f"{Colors.YELLOW}No AI-Craft framework installation detected.{Colors.NC}"
            )
            print(f"{Colors.YELLOW}Nothing to uninstall.{Colors.NC}")
            return False

        return True

    def confirm_removal(self) -> bool:
        """Confirm uninstallation with user."""
        if self.force:
            return True

        print()
        print(
            f"{Colors.RED}WARNING: This will completely remove the framework installation from your system.{Colors.NC}"
        )
        print()
        print(f"{Colors.YELLOW}The following will be removed:{Colors.NC}")
        print(f"{Colors.YELLOW}  - All nWave agents{Colors.NC}")
        print(f"{Colors.YELLOW}  - All nWave commands{Colors.NC}")
        print(f"{Colors.YELLOW}  - Configuration files and manifest{Colors.NC}")
        print(f"{Colors.YELLOW}  - Installation logs and backup directories{Colors.NC}")
        print()

        if self.backup_before_removal:
            print(
                f"{Colors.GREEN}A backup will be created before removal at:{Colors.NC}"
            )
            print(f"{Colors.GREEN}  {self.backup_manager.backup_dir}{Colors.NC}")
            print()
        else:
            print(
                f"{Colors.RED}WARNING: No backup will be created. This action cannot be undone.{Colors.NC}"
            )
            print(
                f"{Colors.RED}To create a backup, cancel and run with --backup option.{Colors.NC}"
            )
            print()

        return confirm_action("Are you sure you want to proceed?")

    def create_backup(self) -> None:
        """Create backup before removal."""
        if not self.backup_before_removal:
            return

        self.backup_manager.create_backup(dry_run=self.dry_run)

    def remove_agents(self) -> None:
        """Remove nWave agents."""
        if self.dry_run:
            self.logger.info("[DRY RUN] Would remove nWave agents...")
            agents_nw_dir = self.claude_config_dir / "agents" / "nw"
            if agents_nw_dir.exists():
                self.logger.info("[DRY RUN] Would remove agents/nw directory")
            return

        self.logger.info("Removing nWave agents...")

        agents_nw_dir = self.claude_config_dir / "agents" / "nw"
        if agents_nw_dir.exists():
            shutil.rmtree(agents_nw_dir)
            self.logger.info("Removed agents/nw directory")

        # Remove parent agents directory if empty
        agents_dir = self.claude_config_dir / "agents"
        if agents_dir.exists():
            try:
                if not any(agents_dir.iterdir()):
                    agents_dir.rmdir()
                    self.logger.info("Removed empty agents directory")
                else:
                    self.logger.info("Kept agents directory (contains other files)")
            except OSError:
                self.logger.info("Kept agents directory (contains other files)")

    def remove_commands(self) -> None:
        """Remove nWave commands."""
        if self.dry_run:
            self.logger.info("[DRY RUN] Would remove nWave commands...")
            commands_nw_dir = self.claude_config_dir / "commands" / "nw"
            if commands_nw_dir.exists():
                self.logger.info("[DRY RUN] Would remove commands/nw directory")
            return

        self.logger.info("Removing nWave commands...")

        commands_nw_dir = self.claude_config_dir / "commands" / "nw"
        if commands_nw_dir.exists():
            shutil.rmtree(commands_nw_dir)
            self.logger.info("Removed commands/nw directory")

        # Remove parent commands directory if empty
        commands_dir = self.claude_config_dir / "commands"
        if commands_dir.exists():
            try:
                if not any(commands_dir.iterdir()):
                    commands_dir.rmdir()
                    self.logger.info("Removed empty commands directory")
                else:
                    self.logger.info("Kept commands directory (contains other files)")
            except OSError:
                self.logger.info("Kept commands directory (contains other files)")

    def remove_config_files(self) -> None:
        """Remove AI-Craft configuration files."""
        if self.dry_run:
            self.logger.info("[DRY RUN] Would remove AI-Craft configuration files...")
            return

        self.logger.info("Removing AI-Craft configuration files...")

        config_files = ["ai-craft-manifest.txt", "ai-craft-install.log"]

        for config_file in config_files:
            file_path = self.claude_config_dir / config_file
            if file_path.exists():
                file_path.unlink()
                self.logger.info(f"Removed {config_file}")

    def remove_backups(self) -> None:
        """Remove AI-Craft backup directories."""
        if self.dry_run:
            self.logger.info("[DRY RUN] Would remove AI-Craft backup directories...")
            return

        self.logger.info("Removing AI-Craft backup directories...")

        backup_count = 0
        backups_dir = self.claude_config_dir / "backups"

        if backups_dir.exists():
            for backup_dir in backups_dir.glob("ai-craft-*"):
                if backup_dir.is_dir():
                    # Skip the backup we just created during this uninstall
                    if (
                        self.backup_before_removal
                        and backup_dir == self.backup_manager.backup_dir
                    ):
                        self.logger.info(
                            f"Preserving current uninstall backup: {backup_dir.name}"
                        )
                        continue

                    shutil.rmtree(backup_dir)
                    backup_count += 1

        if backup_count > 0:
            self.logger.info(f"Removed {backup_count} old AI-Craft backup directories")
        else:
            self.logger.info("No old AI-Craft backup directories found")

    def validate_removal(self) -> bool:
        """Validate complete removal."""
        if self.dry_run:
            self.logger.info("[DRY RUN] Would validate complete removal")
            return True

        self.logger.info("Validating complete removal...")

        errors = 0

        agents_nw_dir = self.claude_config_dir / "agents" / "nw"
        if agents_nw_dir.exists():
            self.logger.error("nWave agents directory still exists")
            errors += 1

        commands_nw_dir = self.claude_config_dir / "commands" / "nw"
        if commands_nw_dir.exists():
            self.logger.error("nWave commands directory still exists")
            errors += 1

        manifest_file = self.claude_config_dir / "ai-craft-manifest.txt"
        if manifest_file.exists():
            self.logger.error("AI-Craft manifest file still exists")
            errors += 1

        install_log = self.claude_config_dir / "ai-craft-install.log"
        if install_log.exists():
            self.logger.error("AI-Craft installation log still exists")
            errors += 1

        if errors == 0:
            self.logger.info(
                f"Uninstallation validation: {Colors.GREEN}PASSED{Colors.NC}"
            )
            return True
        else:
            self.logger.error(
                f"Uninstallation validation: {Colors.RED}FAILED{Colors.NC} ({errors} errors)"
            )
            return False

    def create_uninstall_report(self) -> None:
        """Create uninstallation report."""
        if self.dry_run:
            self.logger.info("[DRY RUN] Would create uninstall report")
            return

        backup_dir = (
            self.backup_manager.backup_dir if self.backup_before_removal else None
        )

        ManifestWriter.write_uninstall_report(self.claude_config_dir, backup_dir)

        self.logger.info(
            f"Uninstallation report created: {self.claude_config_dir / 'framework-uninstall-report.txt'}"
        )


def show_help():
    """Show help message."""
    help_text = f"""{Colors.BLUE}AI-Craft Framework Uninstallation Script for Cross-Platform{Colors.NC}

{Colors.BLUE}DESCRIPTION:{Colors.NC}
    Completely removes the AI-Craft ATDD agent framework from your global Claude config directory.
    This removes all specialized agents, commands, configuration files, logs, and backups.

{Colors.BLUE}USAGE:{Colors.NC}
    python uninstall_ai_craft.py [OPTIONS]

{Colors.BLUE}OPTIONS:{Colors.NC}
    --backup         Create backup before removal (recommended)
    --force          Skip confirmation prompts
    --dry-run        Show what would be removed without making any changes
    --help           Show this help message

{Colors.BLUE}EXAMPLES:{Colors.NC}
    python uninstall_ai_craft.py              # Interactive uninstall with confirmation
    python uninstall_ai_craft.py --dry-run    # Show what would be removed
    python uninstall_ai_craft.py --backup     # Create backup before removal
    python uninstall_ai_craft.py --force      # Uninstall without confirmation prompts

{Colors.BLUE}WHAT GETS REMOVED:{Colors.NC}
    - All nWave agents in agents/nw/ directory
    - All DW commands in commands/nw/ directory
    - AI-Craft configuration files (manifest)
    - AI-Craft installation logs and backup directories

{Colors.BLUE}IMPORTANT:{Colors.NC}
    This action cannot be undone unless you use --backup option.
"""
    print(help_text)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Uninstall AI-Craft framework", add_help=False
    )
    parser.add_argument(
        "--backup", action="store_true", help="Create backup before removal"
    )
    parser.add_argument(
        "--force", action="store_true", help="Skip confirmation prompts"
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Show what would be done"
    )
    parser.add_argument("--help", "-h", action="store_true", help="Show help")

    args = parser.parse_args()

    if args.help:
        show_help()
        return 0

    uninstaller = AIUninstaller(
        backup_before_removal=args.backup, force=args.force, dry_run=args.dry_run
    )

    uninstaller.logger.info("Framework Uninstallation Script")
    uninstaller.logger.info("=" * 31)

    if args.dry_run:
        uninstaller.logger.info(
            f"{Colors.YELLOW}DRY RUN MODE{Colors.NC} - No changes will be made"
        )

    # Check for installation
    if not uninstaller.check_installation():
        return 0

    # Confirm removal
    if not uninstaller.confirm_removal():
        print()
        print(f"{Colors.YELLOW}Uninstallation cancelled by user.{Colors.NC}")
        return 0

    # Create backup
    uninstaller.create_backup()

    # Remove components
    uninstaller.remove_agents()
    uninstaller.remove_commands()
    uninstaller.remove_config_files()
    uninstaller.remove_backups()

    # Validate and report
    if not uninstaller.validate_removal():
        uninstaller.logger.error("Uninstallation failed validation")
        return 1

    uninstaller.create_uninstall_report()

    # Success message
    print()
    uninstaller.logger.info("✅ Framework uninstalled successfully!")
    print()
    uninstaller.logger.info("Summary:")
    uninstaller.logger.info("- All nWave agents removed")
    uninstaller.logger.info("- All nWave commands removed")
    uninstaller.logger.info("- Configuration files cleaned")
    uninstaller.logger.info("- Backup directories removed")

    if args.backup:
        print()
        uninstaller.logger.info("💾 Backup available at:")
        uninstaller.logger.info(f"   {uninstaller.backup_manager.backup_dir}")

    print()
    uninstaller.logger.info(
        "The framework has been completely removed from your system."
    )

    return 0


if __name__ == "__main__":
    sys.exit(main())
