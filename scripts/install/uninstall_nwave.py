#!/usr/bin/env python3
"""
nWave Framework Uninstallation Script

Cross-platform uninstaller for the nWave methodology framework.
Completely removes nWave framework from global Claude config directory.

Usage: python uninstall_nwave.py [--backup] [--force] [--dry-run] [--help]
"""

import argparse
import shutil
import sys

try:
    from scripts.install.install_utils import (
        BackupManager,
        Logger,
        ManifestWriter,
        PathUtils,
        confirm_action,
    )
    from scripts.install.rich_console import ConsoleFactory, RichLogger
except ImportError:
    from install_utils import (
        BackupManager,
        Logger,
        ManifestWriter,
        PathUtils,
        confirm_action,
    )
    from rich_console import ConsoleFactory, RichLogger

# ANSI color codes for terminal output (fallback when Rich unavailable)
_ANSI_GREEN = "\033[0;32m"
_ANSI_RED = "\033[0;31m"
_ANSI_YELLOW = "\033[1;33m"
_ANSI_BLUE = "\033[0;34m"
_ANSI_NC = "\033[0m"  # No Color

__version__ = "1.1.0"


class NWaveUninstaller:
    """nWave framework uninstaller."""

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
        log_file = self.claude_config_dir / "nwave-uninstall.log"
        self.logger = Logger(log_file if not dry_run else None)

        # Create Rich logger for enhanced visual output
        self.rich_logger = ConsoleFactory.create_logger(
            log_file if not dry_run else None
        )

        self.backup_manager = BackupManager(self.logger, "uninstall")

    def check_installation(self) -> bool:
        """Check for existing nWave installation."""
        self.logger.info("Checking for nWave installation...")

        installation_found = False

        agents_dir = self.claude_config_dir / "agents" / "nw"
        commands_dir = self.claude_config_dir / "commands" / "nw"
        manifest_file = self.claude_config_dir / "nwave-manifest.txt"
        install_log = self.claude_config_dir / "nwave-install.log"
        backups_dir = self.claude_config_dir / "backups"

        if agents_dir.exists():
            installation_found = True
            self.logger.info(f"Found nWave agents in: {agents_dir}")

        if commands_dir.exists():
            installation_found = True
            self.logger.info(f"Found nWave commands in: {commands_dir}")

        if manifest_file.exists():
            installation_found = True
            self.logger.info("Found nWave manifest file")

        if install_log.exists():
            installation_found = True
            self.logger.info("Found nWave installation logs")

        if backups_dir.exists():
            nwave_backups = list(backups_dir.glob("nwave-*"))
            if nwave_backups:
                installation_found = True
                self.logger.info("Found nWave backup directories")

        if not installation_found:
            self.logger.info("No nWave installation found")
            print()
            print(f"{_ANSI_YELLOW}No nWave framework installation detected.{_ANSI_NC}")
            print(f"{_ANSI_YELLOW}Nothing to uninstall.{_ANSI_NC}")
            return False

        return True

    def confirm_removal(self) -> bool:
        """Confirm uninstallation with user."""
        if self.force:
            return True

        print()
        print(
            f"{_ANSI_RED}WARNING: This will completely remove the framework installation from your system.{_ANSI_NC}"
        )
        print()
        print(f"{_ANSI_YELLOW}The following will be removed:{_ANSI_NC}")
        print(f"{_ANSI_YELLOW}  - All nWave agents{_ANSI_NC}")
        print(f"{_ANSI_YELLOW}  - All nWave commands{_ANSI_NC}")
        print(f"{_ANSI_YELLOW}  - Configuration files and manifest{_ANSI_NC}")
        print(f"{_ANSI_YELLOW}  - Installation logs and backup directories{_ANSI_NC}")
        print()

        if self.backup_before_removal:
            print(f"{_ANSI_GREEN}A backup will be created before removal at:{_ANSI_NC}")
            print(f"{_ANSI_GREEN}  {self.backup_manager.backup_dir}{_ANSI_NC}")
            print()
        else:
            print(
                f"{_ANSI_RED}WARNING: No backup will be created. This action cannot be undone.{_ANSI_NC}"
            )
            print(
                f"{_ANSI_RED}To create a backup, cancel and run with --backup option.{_ANSI_NC}"
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

        with self.rich_logger.progress_spinner("Removing nWave agents..."):
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

        with self.rich_logger.progress_spinner("Removing nWave commands..."):
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
                        self.logger.info(
                            "Kept commands directory (contains other files)"
                        )
                except OSError:
                    self.logger.info("Kept commands directory (contains other files)")

    def remove_config_files(self) -> None:
        """Remove nWave configuration files."""
        if self.dry_run:
            self.logger.info("[DRY RUN] Would remove nWave configuration files...")
            return

        with self.rich_logger.progress_spinner("Removing nWave configuration files..."):
            config_files = ["nwave-manifest.txt", "nwave-install.log"]

            for config_file in config_files:
                file_path = self.claude_config_dir / config_file
                if file_path.exists():
                    file_path.unlink()
                    self.logger.info(f"Removed {config_file}")

    def remove_backups(self) -> None:
        """Remove nWave backup directories."""
        if self.dry_run:
            self.logger.info("[DRY RUN] Would remove nWave backup directories...")
            return

        with self.rich_logger.progress_spinner("Removing nWave backup directories..."):
            backup_count = 0
            backups_dir = self.claude_config_dir / "backups"

            if backups_dir.exists():
                for backup_dir in backups_dir.glob("nwave-*"):
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
                self.logger.info(f"Removed {backup_count} old nWave backup directories")
            else:
                self.logger.info("No old nWave backup directories found")

    def validate_removal(self) -> bool:
        """Validate complete removal."""
        if self.dry_run:
            self.logger.info("[DRY RUN] Would validate complete removal")
            return True

        with self.rich_logger.progress_spinner("Validating complete removal..."):
            agents_nw_dir = self.claude_config_dir / "agents" / "nw"
            commands_nw_dir = self.claude_config_dir / "commands" / "nw"
            manifest_file = self.claude_config_dir / "nwave-manifest.txt"
            install_log = self.claude_config_dir / "nwave-install.log"

            agents_removed = not agents_nw_dir.exists()
            commands_removed = not commands_nw_dir.exists()
            manifest_removed = not manifest_file.exists()
            log_removed = not install_log.exists()

        # Display validation results as Rich table
        status_ok = (
            "[green]Removed[/green]"
            if isinstance(self.rich_logger, RichLogger)
            else "Removed"
        )
        status_fail = (
            "[red]Exists[/red]"
            if isinstance(self.rich_logger, RichLogger)
            else "Exists"
        )

        validation_rows = [
            ["Agents", status_ok if agents_removed else status_fail],
            ["Commands", status_ok if commands_removed else status_fail],
            ["Manifest", status_ok if manifest_removed else status_fail],
            ["Install Log", status_ok if log_removed else status_fail],
        ]

        self.rich_logger.table(
            headers=["Component", "Status"],
            rows=validation_rows,
            title="Uninstall Validation Results",
        )

        errors = sum(
            [
                not agents_removed,
                not commands_removed,
                not manifest_removed,
                not log_removed,
            ]
        )

        if errors == 0:
            self.logger.info(
                f"Uninstallation validation: {_ANSI_GREEN}PASSED{_ANSI_NC}"
            )
            return True
        else:
            self.logger.error(
                f"Uninstallation validation: {_ANSI_RED}FAILED{_ANSI_NC} ({errors} errors)"
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


def show_title_panel(rich_logger: RichLogger, dry_run: bool = False) -> None:
    """Display styled title panel when uninstaller starts.

    Args:
        rich_logger: RichLogger instance for styled output.
        dry_run: Whether running in dry-run mode.
    """
    mode_indicator = " [DRY RUN]" if dry_run else ""
    title_content = f"""nWave Framework Uninstallation Script v{__version__}{mode_indicator}

Completely removes the nWave methodology framework from
your global Claude config directory."""

    rich_logger.panel(content=title_content, title="nWave Uninstaller", style="red")


def show_uninstall_summary(rich_logger: RichLogger, backup_dir=None) -> None:
    """Display uninstallation summary panel at end of successful uninstall.

    Args:
        rich_logger: RichLogger instance for styled output.
        backup_dir: Path to backup directory (if created).
    """
    backup_info = (
        f"Backup Location: {backup_dir}\nBackup contains complete pre-removal state"
        if backup_dir
        else "Backup: Not created"
    )

    summary_content = f"""Framework Removed Successfully

Components Removed:
  - All nWave agents
  - All nWave commands
  - Configuration files
  - Installation logs
  - Old backup directories

{backup_info}

The framework has been completely removed from your system."""

    rich_logger.panel(
        content=summary_content, title="Uninstall Complete", style="green"
    )


def show_help():
    """Show help message."""
    help_text = f"""{_ANSI_BLUE}nWave Framework Uninstallation Script for Cross-Platform{_ANSI_NC}

{_ANSI_BLUE}DESCRIPTION:{_ANSI_NC}
    Completely removes the nWave ATDD agent framework from your global Claude config directory.
    This removes all specialized agents, commands, configuration files, logs, and backups.

{_ANSI_BLUE}USAGE:{_ANSI_NC}
    python uninstall_nwave.py [OPTIONS]

{_ANSI_BLUE}OPTIONS:{_ANSI_NC}
    --backup         Create backup before removal (recommended)
    --force          Skip confirmation prompts
    --dry-run        Show what would be removed without making any changes
    --help           Show this help message

{_ANSI_BLUE}EXAMPLES:{_ANSI_NC}
    python uninstall_nwave.py              # Interactive uninstall with confirmation
    python uninstall_nwave.py --dry-run    # Show what would be removed
    python uninstall_nwave.py --backup     # Create backup before removal
    python uninstall_nwave.py --force      # Uninstall without confirmation prompts

{_ANSI_BLUE}WHAT GETS REMOVED:{_ANSI_NC}
    - All nWave agents in agents/nw/ directory
    - All DW commands in commands/nw/ directory
    - nWave configuration files (manifest)
    - nWave installation logs and backup directories

{_ANSI_BLUE}IMPORTANT:{_ANSI_NC}
    This action cannot be undone unless you use --backup option.
"""
    print(help_text)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Uninstall nWave framework", add_help=False
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

    # Create Rich logger for title panel (before uninstaller is created)
    title_logger = ConsoleFactory.create_logger()

    # Show title panel at startup
    show_title_panel(title_logger, dry_run=args.dry_run)

    uninstaller = NWaveUninstaller(
        backup_before_removal=args.backup, force=args.force, dry_run=args.dry_run
    )

    if args.dry_run:
        uninstaller.logger.info(
            f"{_ANSI_YELLOW}DRY RUN MODE{_ANSI_NC} - No changes will be made"
        )

    # Check for installation
    if not uninstaller.check_installation():
        return 0

    # Confirm removal
    if not uninstaller.confirm_removal():
        print()
        print(f"{_ANSI_YELLOW}Uninstallation cancelled by user.{_ANSI_NC}")
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

    print()
    # Show uninstall summary panel
    backup_dir = uninstaller.backup_manager.backup_dir if args.backup else None
    show_uninstall_summary(uninstaller.rich_logger, backup_dir)

    return 0


if __name__ == "__main__":
    sys.exit(main())
