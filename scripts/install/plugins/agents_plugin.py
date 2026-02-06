"""
Wrapper plugin for agents installation.

Encapsulates the _install_agents() method from NWaveInstaller,
maintaining backward compatibility while enabling plugin-based orchestration.
"""

from scripts.install.install_utils import PathUtils
from scripts.install.plugins.base import (
    InstallationPlugin,
    InstallContext,
    PluginResult,
)


class AgentsPlugin(InstallationPlugin):
    """Plugin for installing agents into the nWave framework."""

    def __init__(self):
        """Initialize agents plugin with name and priority."""
        super().__init__(name="agents", priority=10)

    def install(self, context: InstallContext) -> PluginResult:
        """Install agents into the framework.

        Args:
            context: InstallContext with shared installation utilities

        Returns:
            PluginResult indicating success or failure of installation
        """
        try:
            context.logger.info("  📦 Installing agents...")

            # Determine source and target directories
            source_agent_dir = context.project_root / "nWave" / "agents"
            dist_agent_dir = context.framework_source / "agents" / "nw"
            target_agent_dir = context.claude_dir / "agents" / "nw"

            # Create target directory
            target_agent_dir.mkdir(parents=True, exist_ok=True)

            # Count agents in each source location
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

            # Select source: prefer dist if it has sufficient agents
            if dist_agent_count >= (source_agent_count % 2) and dist_agent_count > 5:
                context.logger.info(
                    f"  ⏳ From distribution ({dist_agent_count} agents)..."
                )
                selected_source = dist_agent_dir
            else:
                context.logger.info(
                    f"  ⏳ From source ({source_agent_count} agents)..."
                )
                selected_source = source_agent_dir

            # Copy agent files
            copied_count = PathUtils.copy_tree_with_filter(
                selected_source, target_agent_dir, exclude_patterns=["README.md"]
            )

            # Collect installed file paths
            installed_files = [str(f) for f in target_agent_dir.glob("*.md")]

            context.logger.info(f"  ✅ Agents installed ({copied_count} files)")

            return PluginResult(
                success=True,
                plugin_name=self.name,
                message=f"Agents installed successfully ({copied_count} files)",
                installed_files=installed_files,
            )
        except Exception as e:
            context.logger.error(f"Failed to install agents: {e!s}")
            return PluginResult(
                success=False,
                plugin_name=self.name,
                message=f"Agents installation failed: {e!s}",
                errors=[str(e)],
            )

    def verify(self, context: InstallContext) -> PluginResult:
        """Verify agents were installed correctly.

        Args:
            context: InstallContext with shared installation utilities

        Returns:
            PluginResult indicating verification success or failure
        """
        try:
            context.logger.info("Verifying agents installation...")

            target_agent_dir = context.claude_dir / "agents" / "nw"

            # Check target directory exists
            if not target_agent_dir.exists():
                return PluginResult(
                    success=False,
                    plugin_name=self.name,
                    message="Agents verification failed: target directory does not exist",
                    errors=["Target directory not found"],
                )

            # Check for agent files
            agent_files = list(target_agent_dir.glob("*.md"))
            if not agent_files:
                return PluginResult(
                    success=False,
                    plugin_name=self.name,
                    message="Agents verification failed: no agent files found",
                    errors=["No .md files in target directory"],
                )

            context.logger.info(f"Verified {len(agent_files)} agent files")

            return PluginResult(
                success=True,
                plugin_name=self.name,
                message=f"Agents verification passed ({len(agent_files)} files)",
            )
        except Exception as e:
            context.logger.error(f"Failed to verify agents: {e!s}")
            return PluginResult(
                success=False,
                plugin_name=self.name,
                message=f"Agents verification failed: {e!s}",
                errors=[str(e)],
            )
