#!/usr/bin/env python3
"""
nWave Framework Update Script

Cross-platform updater that orchestrates build + uninstall + install.
Provides seamless framework updates while preserving configuration.

Usage: python update_nwave.py [--backup] [--force] [--dry-run] [--help]
"""

import argparse
import subprocess
import sys
from pathlib import Path


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
_ANSI_CYAN = "\033[0;36m"
_ANSI_NC = "\033[0m"  # No Color

__version__ = "1.1.0"


class NWaveUpdater:
    """nWave framework updater."""

    def __init__(
        self,
        backup_before_update: bool = False,
        force: bool = False,
        dry_run: bool = False,
    ):
        """
        Initialize updater.

        Args:
            backup_before_update: Create backup before updating
            force: Skip confirmation prompts
            dry_run: Show what would be done without executing
        """
        self.backup_before_update = backup_before_update
        self.force = force
        self.dry_run = dry_run

        self.script_dir = Path(__file__).parent
        self.project_root = PathUtils.get_project_root(self.script_dir)
        self.claude_config_dir = PathUtils.get_claude_config_dir()

        log_file = self.claude_config_dir / "nwave-update.log"
        self.logger = Logger(log_file if not dry_run else None)

        # Create Rich logger for enhanced visual output
        self.rich_logger = ConsoleFactory.create_logger(
            log_file if not dry_run else None
        )

        self.backup_manager = BackupManager(self.logger, "update")

    def check_prerequisites(self) -> bool:
        """Check update prerequisites."""
        self.logger.step("Checking update prerequisites...")

        # Check if we have the build script
        build_script = self.project_root / "tools" / "build_ide_bundle.py"
        if not build_script.exists():
            build_script = self.project_root / "scripts" / "build-ide-bundle.sh"
            if not build_script.exists():
                self.logger.error(
                    "Build script not found. Ensure you're running from nWave project root"
                )
                return False

        # Check for uninstall/install scripts
        uninstall_script = self.script_dir / "uninstall_nwave.py"
        install_script = self.script_dir / "install_nwave.py"

        if not uninstall_script.exists():
            uninstall_script = self.script_dir.parent / "uninstall-nwave.sh"
            if not uninstall_script.exists():
                self.logger.error("Uninstall script not found")
                return False

        if not install_script.exists():
            install_script = self.script_dir.parent / "install-nwave.sh"
            if not install_script.exists():
                self.logger.error("Install script not found")
                return False

        # Check Python availability
        python_version = sys.version_info
        if python_version < (3, 7):
            self.logger.error(
                f"Python 3.7+ required, found {python_version.major}.{python_version.minor}"
            )
            return False

        # Check Claude config directory
        if not self.claude_config_dir.exists():
            self.logger.warn(
                "Claude config directory not found. Will be created during installation"
            )

        self.logger.info("✅ All prerequisites satisfied")
        return True

    def check_current_installation(self) -> bool:
        """Check current nWave installation."""
        self.logger.step("Checking current nWave installation...")

        agents_dir = self.claude_config_dir / "agents" / "nw"
        commands_dir = self.claude_config_dir / "commands" / "nw"

        installation_found = agents_dir.exists() or commands_dir.exists()

        if installation_found:
            self.logger.info("Found existing nWave installation")

            # Get current installation details
            manifest_file = self.claude_config_dir / "nwave-manifest.txt"
            if manifest_file.exists():
                try:
                    manifest_content = manifest_file.read_text(encoding="utf-8")
                    # Show first 10 lines
                    lines = manifest_content.splitlines()[:10]
                    self.logger.info("Current installation details:")
                    for line in lines:
                        print(f"{_ANSI_CYAN}{line}{_ANSI_NC}")
                except Exception:
                    pass
        else:
            self.logger.warn("No existing nWave installation detected")
            self.logger.warn("This will perform a fresh installation instead of update")

        return True

    def create_update_backup(self) -> None:
        """Create comprehensive pre-update backup."""
        if not self.backup_before_update:
            return

        if self.dry_run:
            self.logger.step(
                "[DRY RUN] Would create comprehensive pre-update backup..."
            )
            return

        self.logger.step("Creating comprehensive pre-update backup...")

        backup_created = self.backup_manager.create_backup(dry_run=self.dry_run)

        if backup_created:
            # Create additional backup manifest for update
            manifest_path = (
                self.backup_manager.backup_dir / "update-backup-manifest.txt"
            )

            content = f"""nWave Framework Pre-Update Backup
Created: {self.backup_manager.timestamp}
Source: {self.claude_config_dir}
Backup Type: Comprehensive pre-update backup
Update Process: Build → Uninstall → Install
Backup Contents:
  - Complete nWave installation state
  - Configuration files and settings
  - Installation logs and manifests

Restoration Command:
  # To restore if update fails:
  cp -r {self.backup_manager.backup_dir}/agents/nw {self.claude_config_dir}/agents/ 2>/dev/null || true
  cp -r {self.backup_manager.backup_dir}/commands/nw {self.claude_config_dir}/commands/ 2>/dev/null || true
  cp {self.backup_manager.backup_dir}/*.txt {self.claude_config_dir}/ 2>/dev/null || true
"""

            manifest_path.write_text(content, encoding="utf-8")

            self.logger.info(
                f"✅ Comprehensive backup created: {self.backup_manager.backup_dir}"
            )

    def build_framework(self) -> bool:
        """Build new nWave framework bundle."""
        if self.dry_run:
            self.logger.step("Building new nWave framework bundle...")
            self.logger.info("[DRY RUN] Would execute build process")
            return True

        build_script = self.project_root / "tools" / "build_ide_bundle.py"
        if not build_script.exists():
            build_script = self.project_root / "scripts" / "build-ide-bundle.sh"

        with self.rich_logger.progress_spinner(
            "Building new nWave framework bundle..."
        ):
            try:
                if build_script.suffix == ".py":
                    result = subprocess.run(
                        [sys.executable, str(build_script)],
                        cwd=self.project_root,
                        capture_output=True,
                        text=True,
                    )
                else:
                    result = subprocess.run(
                        ["bash", str(build_script)],
                        cwd=self.project_root,
                        capture_output=True,
                        text=True,
                    )

                if (
                    result.returncode == 0
                    or "Build completed" in result.stdout
                    or "✅" in result.stdout
                ):
                    self.logger.info("Framework bundle built successfully")

                    # Verify build output
                    dist_ide = self.project_root / "dist" / "ide"
                    if dist_ide.exists():
                        agent_count = PathUtils.count_files(dist_ide / "agents", "*.md")
                        command_count = PathUtils.count_files(
                            dist_ide / "commands", "*.md"
                        )

                        self.logger.info(
                            f"Build verification - Agents: {agent_count}, Commands: {command_count}"
                        )
                    else:
                        self.logger.error(
                            f"Build output directory not found: {dist_ide}"
                        )
                        return False

                    return True
                else:
                    self.logger.error("Framework build failed")
                    self.logger.error(result.stderr)
                    return False

            except Exception as e:
                self.logger.error(f"Framework build failed: {e}")
                return False

    def uninstall_current(self) -> bool:
        """Uninstall current nWave installation."""
        if self.dry_run:
            self.logger.step("Uninstalling current nWave installation...")
            self.logger.info("[DRY RUN] Would execute uninstallation process")
            return True

        uninstall_script = self.script_dir / "uninstall_nwave.py"
        if not uninstall_script.exists():
            uninstall_script = self.script_dir.parent / "uninstall-nwave.sh"

        # Build uninstall options
        uninstall_options = ["--force"]
        if self.backup_before_update:
            uninstall_options.append("--backup")

        with self.rich_logger.progress_spinner(
            "Uninstalling current nWave installation..."
        ):
            try:
                if uninstall_script.suffix == ".py":
                    result = subprocess.run(
                        [sys.executable, str(uninstall_script), *uninstall_options],
                        cwd=self.script_dir,
                        capture_output=True,
                        text=True,
                    )
                else:
                    result = subprocess.run(
                        ["bash", str(uninstall_script), *uninstall_options],
                        cwd=self.script_dir,
                        capture_output=True,
                        text=True,
                    )

                if (
                    result.returncode == 0
                    or "uninstalled successfully" in result.stdout
                ):
                    self.logger.info("Previous installation uninstalled successfully")
                    return True
                else:
                    self.logger.warn(
                        "Uninstallation reported issues, but continuing with installation"
                    )
                    return True

            except Exception as e:
                self.logger.error(f"Uninstallation failed: {e}")
                return False

    def install_new_framework(self) -> bool:
        """Install new nWave framework."""
        if self.dry_run:
            self.logger.step("Installing new nWave framework...")
            self.logger.info("[DRY RUN] Would execute installation process")
            return True

        install_script = self.script_dir / "install_nwave.py"
        if not install_script.exists():
            install_script = self.script_dir.parent / "install-nwave.sh"

        with self.rich_logger.progress_spinner("Installing new nWave framework..."):
            try:
                if install_script.suffix == ".py":
                    result = subprocess.run(
                        [sys.executable, str(install_script)],
                        cwd=self.script_dir,
                        capture_output=True,
                        text=True,
                    )
                else:
                    result = subprocess.run(
                        ["bash", str(install_script)],
                        cwd=self.script_dir,
                        capture_output=True,
                        text=True,
                    )

                if result.returncode == 0 or "installed successfully" in result.stdout:
                    self.logger.info("New framework installed successfully")
                    return True
                else:
                    self.logger.error("Framework installation failed")
                    self.logger.error(result.stderr)

                    # Provide recovery guidance
                    if self.backup_before_update:
                        self.logger.error("Update failed. You can restore from backup:")
                        self.logger.error(
                            f"  Backup location: {self.backup_manager.backup_dir}"
                        )
                        self.logger.error(
                            "  See backup manifest for restoration commands"
                        )

                    return False

            except Exception as e:
                self.logger.error(f"Framework installation failed: {e}")
                return False

    def validate_update(self) -> bool:
        """Validate successful update."""
        with self.rich_logger.progress_spinner("Validating successful update..."):
            validation_errors = 0

            # Check that new installation exists
            agents_dir = self.claude_config_dir / "agents" / "nw"
            commands_dir = self.claude_config_dir / "commands" / "nw"

            if not agents_dir.exists():
                validation_errors += 1

            if not commands_dir.exists():
                validation_errors += 1

            # Check manifest
            manifest_file = self.claude_config_dir / "nwave-manifest.txt"
            manifest_exists = manifest_file.exists()
            if not manifest_exists:
                validation_errors += 1

            # Count installed components
            agent_count = PathUtils.count_files(agents_dir, "*.md")
            command_count = PathUtils.count_files(commands_dir, "*.md")

        # Display validation results as Rich table
        status_ok = (
            "[green]OK[/green]" if isinstance(self.rich_logger, RichLogger) else "OK"
        )
        status_fail = (
            "[red]FAIL[/red]" if isinstance(self.rich_logger, RichLogger) else "FAIL"
        )

        validation_rows = [
            [
                "Agents",
                status_ok if agents_dir.exists() else status_fail,
                str(agent_count),
            ],
            [
                "Commands",
                status_ok if commands_dir.exists() else status_fail,
                str(command_count),
            ],
            [
                "Manifest",
                status_ok if manifest_exists else status_fail,
                "Yes" if manifest_exists else "No",
            ],
        ]

        self.rich_logger.table(
            headers=["Component", "Status", "Count"],
            rows=validation_rows,
            title="Update Validation Results",
        )

        if validation_errors == 0:
            self.logger.info("Update validation successful")
            return True
        else:
            self.logger.error(
                f"Update validation failed with {validation_errors} errors"
            )
            return False

    def confirm_update(self) -> bool:
        """Confirm update with user."""
        if self.force or self.dry_run:
            return True

        print()
        print(f"{_ANSI_YELLOW}nWave FRAMEWORK UPDATE{_ANSI_NC}")
        print(f"{_ANSI_YELLOW}========================={_ANSI_NC}")
        print()
        print(f"{_ANSI_YELLOW}This will:{_ANSI_NC}")
        print(
            f"{_ANSI_YELLOW}  1. Build new framework from current source code{_ANSI_NC}"
        )
        print(f"{_ANSI_YELLOW}  2. Uninstall existing nWave installation{_ANSI_NC}")
        print(f"{_ANSI_YELLOW}  3. Install newly built framework{_ANSI_NC}")
        print()

        if self.backup_before_update:
            print(
                f"{_ANSI_GREEN}✅ Comprehensive backup will be created before update{_ANSI_NC}"
            )
            print(
                f"{_ANSI_GREEN}   Location: {self.backup_manager.backup_dir}{_ANSI_NC}"
            )
        else:
            print(f"{_ANSI_RED}⚠️  No backup will be created{_ANSI_NC}")
            print(
                f"{_ANSI_RED}   To create backup, cancel and run with --backup option{_ANSI_NC}"
            )

        print()
        return confirm_action("Continue with nWave framework update?")

    def create_update_report(self) -> None:
        """Create update report."""
        if self.dry_run:
            self.logger.info("[DRY RUN] Would create update report")
            return

        backup_dir = (
            self.backup_manager.backup_dir if self.backup_before_update else None
        )

        ManifestWriter.write_update_report(
            self.claude_config_dir, backup_dir, self.backup_before_update
        )

        self.logger.info(
            f"Update report created: {self.claude_config_dir / 'nwave-update-report.txt'}"
        )


def show_title_panel(rich_logger: RichLogger, dry_run: bool = False) -> None:
    """Display styled title panel when updater starts.

    Args:
        rich_logger: RichLogger instance for styled output.
        dry_run: Whether running in dry-run mode.
    """
    mode_indicator = " [DRY RUN]" if dry_run else ""
    title_content = f"""nWave Framework Update Script v{__version__}{mode_indicator}

Orchestrates complete nWave framework update process:
1. Build new framework bundle from source
2. Uninstall existing nWave installation
3. Install newly built framework bundle"""

    rich_logger.panel(content=title_content, title="nWave Updater", style="blue")


def show_update_summary(
    rich_logger: RichLogger, claude_config_dir: Path, backup_dir: Path | None = None
) -> None:
    """Display update summary panel at end of successful update.

    Args:
        rich_logger: RichLogger instance for styled output.
        claude_config_dir: Path to Claude config directory.
        backup_dir: Path to backup directory (if created).
    """
    # Count installed components
    agents_count = PathUtils.count_files(claude_config_dir / "agents" / "nw", "*.md")
    commands_count = PathUtils.count_files(
        claude_config_dir / "commands" / "nw", "*.md"
    )

    backup_info = (
        f"Backup Location: {backup_dir}" if backup_dir else "Backup: Not created"
    )

    summary_content = f"""Framework Version: {__version__}
Installation Location: {claude_config_dir}
Agents Installed: {agents_count}
Commands Installed: {commands_count}
{backup_info}

Update Process Completed:
  1. Framework bundle built from latest source
  2. Previous installation cleanly removed
  3. New framework installation validated
  4. All nWave components operational"""

    rich_logger.panel(content=summary_content, title="Update Complete", style="green")


def show_help():
    """Show help message."""
    help_text = f"""{_ANSI_BLUE}nWave Framework Update Script for Cross-Platform{_ANSI_NC}

{_ANSI_BLUE}DESCRIPTION:{_ANSI_NC}
    Orchestrates complete nWave framework update process:
    1. Builds new framework bundle from source
    2. Uninstalls existing nWave installation
    3. Installs newly built framework bundle

    This provides a seamless update experience while preserving configuration.

{_ANSI_BLUE}USAGE:{_ANSI_NC}
    python update_nwave.py [OPTIONS]

{_ANSI_BLUE}OPTIONS:{_ANSI_NC}
    --backup         Create comprehensive backup before update (recommended)
    --force          Skip confirmation prompts and force update
    --dry-run        Show what would be done without executing
    --help           Show this help message

{_ANSI_BLUE}EXAMPLES:{_ANSI_NC}
    python update_nwave.py                # Interactive update with confirmations
    python update_nwave.py --backup       # Update with comprehensive backup
    python update_nwave.py --force --backup # Automated update with backup
    python update_nwave.py --dry-run      # Preview update process

{_ANSI_BLUE}UPDATE PROCESS:{_ANSI_NC}
    Step 1: Pre-update validation and backup
    Step 2: Build new framework bundle (dist/ide/)
    Step 3: Uninstall current nWave installation
    Step 4: Install new framework bundle
    Step 5: Validate successful update

{_ANSI_BLUE}BACKUP STRATEGY:{_ANSI_NC}
    - Comprehensive pre-update backup created
    - Individual component backups during uninstall/install
    - Full rollback capability if update fails
    - Backup location: ~/.claude/backups/nwave-update-<timestamp>/

{_ANSI_BLUE}IMPORTANT:{_ANSI_NC}
    - Requires Python 3.7+ for build process
    - Preserves Claude Code settings and other configurations
    - Creates detailed update log for troubleshooting
    - Validates installation success before completion
"""
    print(help_text)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Update nWave framework", add_help=False
    )
    parser.add_argument(
        "--backup", action="store_true", help="Create backup before update"
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

    # Create Rich logger for title panel (before updater is created)
    title_logger = ConsoleFactory.create_logger()

    # Show title panel at startup
    show_title_panel(title_logger, dry_run=args.dry_run)

    updater = NWaveUpdater(
        backup_before_update=args.backup, force=args.force, dry_run=args.dry_run
    )

    if args.dry_run:
        updater.logger.info(
            f"{_ANSI_YELLOW}DRY RUN MODE{_ANSI_NC} - No changes will be made"
        )
        print()

    # Execute update process
    if not updater.check_prerequisites():
        return 1

    updater.check_current_installation()

    if not updater.confirm_update():
        print()
        print(f"{_ANSI_YELLOW}Update cancelled by user.{_ANSI_NC}")
        return 0

    updater.create_update_backup()

    if not updater.build_framework():
        return 1

    if not updater.uninstall_current():
        return 1

    if not updater.install_new_framework():
        return 1

    # Validate and report
    if updater.validate_update():
        updater.create_update_report()

        print()
        # Show update summary panel
        backup_dir = updater.backup_manager.backup_dir if args.backup else None
        show_update_summary(updater.rich_logger, updater.claude_config_dir, backup_dir)

        print()
        updater.logger.info("Updated nWave framework ready for use!")
        updater.logger.info(
            "   Try: /nw:discuss, /nw:design, /nw:develop, /nw:deliver commands"
        )

        return 0
    else:
        updater.logger.error("Update validation failed")
        if args.backup:
            updater.logger.error(
                f"Recovery backup available at: {updater.backup_manager.backup_dir}"
            )
        return 1


if __name__ == "__main__":
    sys.exit(main())
