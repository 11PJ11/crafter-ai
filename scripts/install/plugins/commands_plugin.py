"""
Wrapper plugin for commands installation.

Encapsulates the _install_commands() method from NWaveInstaller,
maintaining backward compatibility while enabling plugin-based orchestration.
"""

import shutil

from scripts.install.install_utils import PathUtils
from scripts.install.plugins.base import (
    InstallationPlugin,
    InstallContext,
    PluginResult,
)


class CommandsPlugin(InstallationPlugin):
    """Plugin for installing commands into the nWave framework."""

    def __init__(self):
        """Initialize commands plugin with name and priority."""
        super().__init__(name="commands", priority=20)

    def install(self, context: InstallContext) -> PluginResult:
        """Install commands into the framework.

        Args:
            context: InstallContext with shared installation utilities

        Returns:
            PluginResult indicating success or failure of installation
        """
        try:
            context.logger.info("  📦 Installing commands...")

            # Determine source and target directories
            commands_source = context.framework_source / "commands"
            commands_target = context.claude_dir / "commands"

            if not commands_source.exists():
                return PluginResult(
                    success=False,
                    plugin_name=self.name,
                    message="Commands source directory does not exist",
                    errors=[f"Source not found: {commands_source}"],
                )

            # Copy command files (preserving directory structure)
            installed_files = []
            for item in commands_source.iterdir():
                target = commands_target / item.name
                if item.is_dir():
                    if target.exists():
                        shutil.rmtree(target)
                    shutil.copytree(item, target)
                    # Collect installed file paths
                    for file in target.rglob("*.md"):
                        installed_files.append(str(file))
                else:
                    target.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(item, target)
                    installed_files.append(str(target))

            copied_count = PathUtils.count_files(commands_target, "*.md")
            context.logger.info(f"  ✅ Commands installed ({copied_count} files)")

            return PluginResult(
                success=True,
                plugin_name=self.name,
                message=f"Commands installed successfully ({copied_count} files)",
                installed_files=installed_files,
            )
        except Exception as e:
            context.logger.error(f"  ❌ Failed to install commands: {e}")
            return PluginResult(
                success=False,
                plugin_name=self.name,
                message=f"Commands installation failed: {e!s}",
                errors=[str(e)],
            )

    def verify(self, context: InstallContext) -> PluginResult:
        """Verify commands were installed correctly.

        Args:
            context: InstallContext with shared installation utilities

        Returns:
            PluginResult indicating verification success or failure
        """
        try:
            context.logger.info("  🔎 Verifying commands...")

            target_commands_dir = context.claude_dir / "commands" / "nw"

            # Check target directory exists
            if not target_commands_dir.exists():
                return PluginResult(
                    success=False,
                    plugin_name=self.name,
                    message="Commands verification failed: target directory does not exist",
                    errors=["Target directory not found"],
                )

            # Check for command files
            command_files = list(target_commands_dir.glob("*.md"))
            if not command_files:
                return PluginResult(
                    success=False,
                    plugin_name=self.name,
                    message="Commands verification failed: no command files found",
                    errors=["No .md files in target directory"],
                )

            context.logger.info(f"  ✅ Verified {len(command_files)} command files")

            return PluginResult(
                success=True,
                plugin_name=self.name,
                message=f"Commands verification passed ({len(command_files)} files)",
            )
        except Exception as e:
            context.logger.error(f"  ❌ Failed to verify commands: {e}")
            return PluginResult(
                success=False,
                plugin_name=self.name,
                message=f"Commands verification failed: {e!s}",
                errors=[str(e)],
            )
