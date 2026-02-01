"""
Unit tests for plugin registry and dependency resolution.

Tests topological sort, cycle detection, priority ordering, and missing dependencies.
"""

import pytest
from scripts.install.plugins.base import (
    InstallationPlugin,
    PluginResult,
    InstallContext,
)
from scripts.install.plugins.registry import PluginRegistry


class MockPlugin(InstallationPlugin):
    """Mock plugin for testing."""

    def __init__(self, name: str, priority: int = 100, dependencies=None):
        super().__init__(name, priority)
        if dependencies:
            self.set_dependencies(dependencies)
        self.install_called = False
        self.verify_called = False

    def install(self, context: InstallContext) -> PluginResult:
        self.install_called = True
        return PluginResult(
            success=True,
            plugin_name=self.name,
            message=f"{self.name} installed",
        )

    def verify(self, context: InstallContext) -> PluginResult:
        self.verify_called = True
        return PluginResult(
            success=True,
            plugin_name=self.name,
            message=f"{self.name} verified",
        )


@pytest.fixture
def registry():
    """Create fresh registry for each test."""
    return PluginRegistry()


class TestTopologicalSort:
    """Test topological sort with simple dependencies."""

    def test_sort_with_linear_dependency(self, registry):
        """Topological sort respects linear dependency chain."""
        # A depends on nothing
        # B depends on A
        # C depends on B
        registry.register(MockPlugin("A", priority=10))
        registry.register(MockPlugin("B", priority=20, dependencies=["A"]))
        registry.register(MockPlugin("C", priority=30, dependencies=["B"]))

        order = registry.get_execution_order()
        assert order == ["A", "B", "C"], "Linear dependency not sorted correctly"

    def test_sort_with_multiple_dependencies(self, registry):
        """Topological sort handles multiple independent dependencies."""
        # A, B independent
        # C depends on both A and B
        registry.register(MockPlugin("A", priority=10))
        registry.register(MockPlugin("B", priority=20))
        registry.register(MockPlugin("C", priority=30, dependencies=["A", "B"]))

        order = registry.get_execution_order()
        assert order.index("A") < order.index("C"), "A should execute before C"
        assert order.index("B") < order.index("C"), "B should execute before C"

    def test_priority_ordering_no_dependencies(self, registry):
        """Priority ordering when no dependencies exist."""
        # Register with various priorities - should execute by priority
        registry.register(MockPlugin("High", priority=10))
        registry.register(MockPlugin("Medium", priority=50))
        registry.register(MockPlugin("Low", priority=100))

        order = registry.get_execution_order()
        assert order == ["High", "Medium", "Low"], "Priority ordering failed"


class TestCycleDetection:
    """Test circular dependency detection."""

    def test_detect_simple_cycle(self, registry):
        """Detect cycle A -> B -> A."""
        registry.register(MockPlugin("A", priority=10, dependencies=["B"]))
        registry.register(MockPlugin("B", priority=20, dependencies=["A"]))

        with pytest.raises(ValueError, match="Circular dependency"):
            registry.get_execution_order()

    def test_detect_self_cycle(self, registry):
        """Detect plugin depending on itself."""
        registry.register(MockPlugin("A", priority=10, dependencies=["A"]))

        with pytest.raises(ValueError, match="Circular dependency"):
            registry.get_execution_order()

    def test_detect_complex_cycle(self, registry):
        """Detect cycle A -> B -> C -> A."""
        registry.register(MockPlugin("A", priority=10, dependencies=["C"]))
        registry.register(MockPlugin("B", priority=20, dependencies=["A"]))
        registry.register(MockPlugin("C", priority=30, dependencies=["B"]))

        with pytest.raises(ValueError, match="Circular dependency"):
            registry.get_execution_order()


class TestMissingDependency:
    """Test missing dependency error handling."""

    def test_missing_dependency_error(self, registry):
        """Clear error when dependency plugin not registered."""
        registry.register(MockPlugin("A", priority=10, dependencies=["NonExistent"]))

        with pytest.raises(ValueError, match="missing plugin"):
            registry.get_execution_order()


class TestPluginInstallation:
    """Test plugin installation through registry."""

    def test_install_all_respects_dependencies(self, registry, tmp_path):
        """Installation order respects dependencies."""
        # Create mock context
        context = InstallContext(
            claude_dir=tmp_path,
            scripts_dir=tmp_path / "scripts",
            templates_dir=tmp_path / "templates",
            logger=type(
                "MockLogger", (), {"error": lambda x: None, "info": lambda x: None}
            )(),
            project_root=tmp_path,
            framework_source=tmp_path,
            backup_manager=None,
            installation_verifier=None,
            rich_logger=None,
            dry_run=False,
        )

        plugin_a = MockPlugin("A", priority=10)
        plugin_b = MockPlugin("B", priority=20, dependencies=["A"])
        plugin_c = MockPlugin("C", priority=30, dependencies=["B"])

        registry.register(plugin_a)
        registry.register(plugin_b)
        registry.register(plugin_c)

        results = registry.install_all(context)

        # Verify all plugins were installed
        assert all(r.success for r in results.values()), (
            "All plugins should install successfully"
        )
        assert plugin_a.install_called, "Plugin A should be installed"
        assert plugin_b.install_called, "Plugin B should be installed"
        assert plugin_c.install_called, "Plugin C should be installed"


class TestPluginRegistration:
    """Test plugin registration."""

    def test_duplicate_registration_raises_error(self, registry):
        """Registering duplicate plugin names raises error."""
        registry.register(MockPlugin("A"))
        with pytest.raises(ValueError, match="already registered"):
            registry.register(MockPlugin("A"))

    def test_successful_registration(self, registry):
        """Plugin successfully registers."""
        plugin = MockPlugin("A")
        registry.register(plugin)
        assert "A" in registry.plugins
        assert registry.plugins["A"] == plugin
