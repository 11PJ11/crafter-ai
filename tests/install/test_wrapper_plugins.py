"""
Tests for wrapper plugins that encapsulate existing installer methods.

These tests validate that wrapper plugins correctly call the existing
installer methods and maintain backward compatibility.
"""

from pathlib import Path
from unittest.mock import Mock
from scripts.install.plugins import (
    InstallationPlugin,
    InstallContext,
    PluginResult,
)


class TestAgentsPlugin:
    """Tests for agents wrapper plugin."""

    def test_agents_plugin_inherits_from_installation_plugin(self):
        """Verify AgentsPlugin is an InstallationPlugin."""
        from scripts.install.plugins.agents_plugin import AgentsPlugin

        assert issubclass(AgentsPlugin, InstallationPlugin)

    def test_agents_plugin_initialization(self):
        """Verify AgentsPlugin initializes with correct name and priority."""
        from scripts.install.plugins.agents_plugin import AgentsPlugin

        plugin = AgentsPlugin()
        assert plugin.name == "agents"
        assert plugin.priority == 10  # High priority

    def test_agents_plugin_install_returns_plugin_result(self):
        """Verify AgentsPlugin.install() returns PluginResult."""
        from scripts.install.plugins.agents_plugin import AgentsPlugin

        plugin = AgentsPlugin()
        context = Mock(spec=InstallContext)
        context.logger = Mock()

        result = plugin.install(context)

        assert isinstance(result, PluginResult)

    def test_agents_plugin_install_success(self):
        """Verify successful agents plugin installation."""
        from scripts.install.plugins.agents_plugin import AgentsPlugin

        plugin = AgentsPlugin()
        context = Mock(spec=InstallContext)
        context.dry_run = False
        context.project_root = Path("/tmp/test")
        context.logger = Mock()

        result = plugin.install(context)

        assert result.success is True
        assert result.plugin_name == "agents"
        assert "installed" in result.message.lower()

    def test_agents_plugin_verify_returns_plugin_result(self):
        """Verify AgentsPlugin.verify() returns PluginResult."""
        from scripts.install.plugins.agents_plugin import AgentsPlugin

        plugin = AgentsPlugin()
        context = Mock(spec=InstallContext)
        context.project_root = Path("/tmp/test")
        context.logger = Mock()

        result = plugin.verify(context)

        assert isinstance(result, PluginResult)


class TestCommandsPlugin:
    """Tests for commands wrapper plugin."""

    def test_commands_plugin_inherits_from_installation_plugin(self):
        """Verify CommandsPlugin is an InstallationPlugin."""
        from scripts.install.plugins.commands_plugin import CommandsPlugin

        assert issubclass(CommandsPlugin, InstallationPlugin)

    def test_commands_plugin_initialization(self):
        """Verify CommandsPlugin initializes with correct name and priority."""
        from scripts.install.plugins.commands_plugin import CommandsPlugin

        plugin = CommandsPlugin()
        assert plugin.name == "commands"
        assert plugin.priority == 20

    def test_commands_plugin_install_returns_plugin_result(self):
        """Verify CommandsPlugin.install() returns PluginResult."""
        from scripts.install.plugins.commands_plugin import CommandsPlugin

        plugin = CommandsPlugin()
        context = Mock(spec=InstallContext)
        context.logger = Mock()

        result = plugin.install(context)

        assert isinstance(result, PluginResult)

    def test_commands_plugin_install_success(self):
        """Verify successful commands plugin installation."""
        from scripts.install.plugins.commands_plugin import CommandsPlugin

        plugin = CommandsPlugin()
        context = Mock(spec=InstallContext)
        context.dry_run = False
        context.project_root = Path("/tmp/test")
        context.logger = Mock()

        result = plugin.install(context)

        assert result.success is True
        assert result.plugin_name == "commands"

    def test_commands_plugin_verify_returns_plugin_result(self):
        """Verify CommandsPlugin.verify() returns PluginResult."""
        from scripts.install.plugins.commands_plugin import CommandsPlugin

        plugin = CommandsPlugin()
        context = Mock(spec=InstallContext)
        context.project_root = Path("/tmp/test")
        context.logger = Mock()

        result = plugin.verify(context)

        assert isinstance(result, PluginResult)


class TestTemplatesPlugin:
    """Tests for templates wrapper plugin."""

    def test_templates_plugin_inherits_from_installation_plugin(self):
        """Verify TemplatesPlugin is an InstallationPlugin."""
        from scripts.install.plugins.templates_plugin import TemplatesPlugin

        assert issubclass(TemplatesPlugin, InstallationPlugin)

    def test_templates_plugin_initialization(self):
        """Verify TemplatesPlugin initializes with correct name and priority."""
        from scripts.install.plugins.templates_plugin import TemplatesPlugin

        plugin = TemplatesPlugin()
        assert plugin.name == "templates"
        assert plugin.priority == 30

    def test_templates_plugin_install_returns_plugin_result(self):
        """Verify TemplatesPlugin.install() returns PluginResult."""
        from scripts.install.plugins.templates_plugin import TemplatesPlugin

        plugin = TemplatesPlugin()
        context = Mock(spec=InstallContext)
        context.logger = Mock()

        result = plugin.install(context)

        assert isinstance(result, PluginResult)

    def test_templates_plugin_install_success(self):
        """Verify successful templates plugin installation."""
        from scripts.install.plugins.templates_plugin import TemplatesPlugin

        plugin = TemplatesPlugin()
        context = Mock(spec=InstallContext)
        context.dry_run = False
        context.project_root = Path("/tmp/test")
        context.logger = Mock()

        result = plugin.install(context)

        assert result.success is True
        assert result.plugin_name == "templates"

    def test_templates_plugin_verify_returns_plugin_result(self):
        """Verify TemplatesPlugin.verify() returns PluginResult."""
        from scripts.install.plugins.templates_plugin import TemplatesPlugin

        plugin = TemplatesPlugin()
        context = Mock(spec=InstallContext)
        context.project_root = Path("/tmp/test")
        context.logger = Mock()

        result = plugin.verify(context)

        assert isinstance(result, PluginResult)


class TestUtilitiesPlugin:
    """Tests for utilities wrapper plugin."""

    def test_utilities_plugin_inherits_from_installation_plugin(self):
        """Verify UtilitiesPlugin is an InstallationPlugin."""
        from scripts.install.plugins.utilities_plugin import UtilitiesPlugin

        assert issubclass(UtilitiesPlugin, InstallationPlugin)

    def test_utilities_plugin_initialization(self):
        """Verify UtilitiesPlugin initializes with correct name and priority."""
        from scripts.install.plugins.utilities_plugin import UtilitiesPlugin

        plugin = UtilitiesPlugin()
        assert plugin.name == "utilities"
        assert plugin.priority == 40

    def test_utilities_plugin_install_returns_plugin_result(self):
        """Verify UtilitiesPlugin.install() returns PluginResult."""
        from scripts.install.plugins.utilities_plugin import UtilitiesPlugin

        plugin = UtilitiesPlugin()
        context = Mock(spec=InstallContext)
        context.logger = Mock()

        result = plugin.install(context)

        assert isinstance(result, PluginResult)

    def test_utilities_plugin_install_success(self):
        """Verify successful utilities plugin installation."""
        from scripts.install.plugins.utilities_plugin import UtilitiesPlugin

        plugin = UtilitiesPlugin()
        context = Mock(spec=InstallContext)
        context.dry_run = False
        context.project_root = Path("/tmp/test")
        context.logger = Mock()

        result = plugin.install(context)

        assert result.success is True
        assert result.plugin_name == "utilities"

    def test_utilities_plugin_verify_returns_plugin_result(self):
        """Verify UtilitiesPlugin.verify() returns PluginResult."""
        from scripts.install.plugins.utilities_plugin import UtilitiesPlugin

        plugin = UtilitiesPlugin()
        context = Mock(spec=InstallContext)
        context.project_root = Path("/tmp/test")
        context.logger = Mock()

        result = plugin.verify(context)

        assert isinstance(result, PluginResult)


class TestPluginIntegration:
    """Integration tests for all wrapper plugins."""

    def test_all_plugins_implement_install_method(self):
        """Verify all wrapper plugins implement install() method."""
        from scripts.install.plugins.agents_plugin import AgentsPlugin
        from scripts.install.plugins.commands_plugin import CommandsPlugin
        from scripts.install.plugins.templates_plugin import TemplatesPlugin
        from scripts.install.plugins.utilities_plugin import UtilitiesPlugin

        plugins = [
            AgentsPlugin(),
            CommandsPlugin(),
            TemplatesPlugin(),
            UtilitiesPlugin(),
        ]

        for plugin in plugins:
            assert hasattr(plugin, "install")
            assert callable(plugin.install)

    def test_all_plugins_implement_verify_method(self):
        """Verify all wrapper plugins implement verify() method."""
        from scripts.install.plugins.agents_plugin import AgentsPlugin
        from scripts.install.plugins.commands_plugin import CommandsPlugin
        from scripts.install.plugins.templates_plugin import TemplatesPlugin
        from scripts.install.plugins.utilities_plugin import UtilitiesPlugin

        plugins = [
            AgentsPlugin(),
            CommandsPlugin(),
            TemplatesPlugin(),
            UtilitiesPlugin(),
        ]

        for plugin in plugins:
            assert hasattr(plugin, "verify")
            assert callable(plugin.verify)

    def test_plugins_execute_in_priority_order(self):
        """Verify plugins execute in correct priority order when no dependencies."""
        from scripts.install.plugins.registry import PluginRegistry
        from scripts.install.plugins.agents_plugin import AgentsPlugin
        from scripts.install.plugins.commands_plugin import CommandsPlugin
        from scripts.install.plugins.templates_plugin import TemplatesPlugin
        from scripts.install.plugins.utilities_plugin import UtilitiesPlugin

        registry = PluginRegistry()
        registry.register(UtilitiesPlugin())  # priority 40
        registry.register(TemplatesPlugin())  # priority 30
        registry.register(CommandsPlugin())  # priority 20
        registry.register(AgentsPlugin())  # priority 10

        execution_order = registry.get_execution_order()

        # Should be sorted by priority (lower = earlier)
        assert execution_order == ["agents", "commands", "templates", "utilities"]

    def test_wrapper_plugins_no_dependencies_by_default(self):
        """Verify wrapper plugins have no dependencies by default."""
        from scripts.install.plugins.agents_plugin import AgentsPlugin
        from scripts.install.plugins.commands_plugin import CommandsPlugin
        from scripts.install.plugins.templates_plugin import TemplatesPlugin
        from scripts.install.plugins.utilities_plugin import UtilitiesPlugin

        plugins = [
            AgentsPlugin(),
            CommandsPlugin(),
            TemplatesPlugin(),
            UtilitiesPlugin(),
        ]

        for plugin in plugins:
            assert plugin.get_dependencies() == []
