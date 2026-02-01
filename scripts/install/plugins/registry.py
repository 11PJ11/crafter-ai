"""
Plugin registry with topological sort dependency resolution.

Uses Kahn's algorithm for topological sorting to determine plugin
execution order while respecting dependencies.
"""

from typing import Dict, List, Set

from scripts.install.plugins.base import (
    InstallationPlugin,
    PluginResult,
    InstallContext,
)


class PluginRegistry:
    """Registry for managing plugins and their execution order.

    Uses topological sort (Kahn's algorithm) to resolve plugin dependencies
    and detect circular dependencies.
    """

    def __init__(self):
        """Initialize empty plugin registry."""
        self.plugins: Dict[str, InstallationPlugin] = {}

    def register(self, plugin: InstallationPlugin) -> None:
        """Register a plugin.

        Args:
            plugin: InstallationPlugin instance to register

        Raises:
            ValueError: If plugin with same name already registered
        """
        if plugin.name in self.plugins:
            raise ValueError(f"Plugin '{plugin.name}' already registered")
        self.plugins[plugin.name] = plugin

    def _detect_cycle_dfs(
        self,
        node: str,
        visited: Set[str],
        rec_stack: Set[str],
        graph: Dict[str, List[str]],
    ) -> bool:
        """Detect cycle using depth-first search.

        Args:
            node: Current node being visited
            visited: Set of all visited nodes
            rec_stack: Set of nodes in current recursion stack
            graph: Adjacency list representation of dependencies

        Returns:
            True if cycle detected, False otherwise
        """
        visited.add(node)
        rec_stack.add(node)

        if node in graph:
            for neighbor in graph[node]:
                if neighbor not in visited:
                    if self._detect_cycle_dfs(neighbor, visited, rec_stack, graph):
                        return True
                elif neighbor in rec_stack:
                    return True

        rec_stack.remove(node)
        return False

    def _topological_sort_kahn(self) -> List[str]:
        """Topological sort using Kahn's algorithm.

        Performs topological sort to determine plugin execution order
        while respecting dependencies.

        Returns:
            List of plugin names in execution order

        Raises:
            ValueError: If circular dependency detected or missing dependency
        """
        # Build adjacency list and in-degree count
        graph: Dict[str, List[str]] = {}
        in_degree: Dict[str, int] = {}

        for name in self.plugins:
            graph[name] = []
            in_degree[name] = 0

        for plugin in self.plugins.values():
            for dep in plugin.get_dependencies():
                if dep not in self.plugins:
                    raise ValueError(
                        f"Plugin '{plugin.name}' depends on missing plugin '{dep}'"
                    )
                graph[dep].append(plugin.name)
                in_degree[plugin.name] += 1

        # Collect nodes with no incoming edges
        queue = [name for name in self.plugins if in_degree[name] == 0]

        # Sort by priority for deterministic ordering when no dependencies
        queue.sort(key=lambda x: (in_degree[x], self.plugins[x].priority))

        sorted_order = []
        while queue:
            # Remove node with lowest priority (earliest execution)
            queue.sort(key=lambda x: self.plugins[x].priority)
            node = queue.pop(0)
            sorted_order.append(node)

            # For each neighbor
            for neighbor in graph[node]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)

        # Check if all nodes are in sorted order (no cycle)
        if len(sorted_order) != len(self.plugins):
            raise ValueError("Circular dependency detected in plugins")

        return sorted_order

    def get_execution_order(self) -> List[str]:
        """Get plugin execution order respecting dependencies.

        Returns:
            List of plugin names in execution order

        Raises:
            ValueError: If circular dependency or missing dependency detected
        """
        return self._topological_sort_kahn()

    def install_all(self, context: InstallContext) -> Dict[str, PluginResult]:
        """Install all plugins in dependency order.

        Args:
            context: InstallContext with shared installation utilities

        Returns:
            Dictionary mapping plugin names to their installation results
        """
        results = {}
        order = self.get_execution_order()

        for plugin_name in order:
            plugin = self.plugins[plugin_name]
            result = plugin.install(context)
            results[plugin_name] = result

            if not result.success:
                context.logger.error(f"Plugin installation failed: {result.message}")
                break

        return results

    def verify_all(self, context: InstallContext) -> Dict[str, PluginResult]:
        """Verify all plugins in dependency order.

        Args:
            context: InstallContext with shared installation utilities

        Returns:
            Dictionary mapping plugin names to their verification results
        """
        results = {}
        order = self.get_execution_order()

        for plugin_name in order:
            plugin = self.plugins[plugin_name]
            result = plugin.verify(context)
            results[plugin_name] = result

        return results
