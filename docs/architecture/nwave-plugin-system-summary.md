# nWave Plugin System - Executive Summary

**Version:** 1.0
**Date:** 2026-02-03
**Status:** FUTURE DESIGN - NOT IMPLEMENTED

---

> **⚠️ IMPORTANTE: QUESTO È UN DOCUMENTO DI DESIGN, NON L'IMPLEMENTAZIONE ATTUALE**
>
> **Status Attuale (2026-02-03)**: Il sistema plugin descritto in questo documento è una proposta di design **NON implementata**. L'installer attuale è monolitico.
>
> **Implementazione Attuale**: Vedere `docs/architecture/nwave-installer-current-implementation.md`
>
> **Piano di Implementazione**: Questo design è previsto per implementazione futura.

---

## Quick Overview

The **nWave Plugin System** transforms the monolithic nWave installer into a flexible, modular architecture where components (agents, commands, DES, etc.) are independent plugins that can be:

- ✅ Installed/uninstalled independently
- ✅ Versioned and upgraded separately
- ✅ Dependency-managed automatically
- ✅ Validated through standard interfaces

**DES is planned as the reference plugin implementation**, demonstrating all plugin interfaces and best practices.

---

## The Problem

### Current State
```
┌───────────────────────────────────────┐
│      Monolithic install_nwave.py      │
│                                       │
│  ├─ Install agents                    │
│  ├─ Install commands                  │
│  ├─ Install templates                 │
│  ├─ Install utilities                 │
│  └─ Install DES (hardcoded)           │
│      ├─ DES module                    │
│      ├─ DES scripts                   │
│      ├─ DES templates                 │
│      └─ DES hooks                     │
└───────────────────────────────────────┘
```

**Problems:**
- ❌ DES tightly coupled to core installer
- ❌ Cannot install/uninstall DES independently
- ❌ Cannot add new components without modifying installer
- ❌ Cannot test DES installation in isolation
- ❌ Cannot version DES separately from nWave

---

## The Solution

### Plugin Architecture
```
┌────────────────────────────────────────────────────────────┐
│                  NWaveInstaller (Orchestrator)             │
│                                                            │
│  Creates InstallContext → Delegates to PluginRegistry     │
└────────────────────┬───────────────────────────────────────┘
                     │
                     ▼
┌────────────────────────────────────────────────────────────┐
│                    PluginRegistry                          │
│                                                            │
│  ├─ Discovers plugins                                     │
│  ├─ Resolves dependencies (topological sort)              │
│  └─ Executes plugins in order                             │
└────────────────────┬───────────────────────────────────────┘
                     │
                     ▼
┌────────────────────────────────────────────────────────────┐
│                  Plugin Implementations                    │
│                                                            │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐ │
│  │ Agents   │  │Commands  │  │Templates │  │Utilities │ │
│  │Priority:│  │Priority:│  │Priority:│  │Priority:│ │
│  │   10     │  │   20     │  │   30     │  │   40     │ │
│  └──────────┘  └──────────┘  └──────────┘  └────┬─────┘ │
│                                                   │       │
│                                                   │       │
│                                           ┌───────▼─────┐ │
│                                           │     DES     │ │
│                                           │   Plugin    │ │
│                                           │  Priority:  │ │
│                                           │     50      │ │
│                                           │             │ │
│                                           │ Depends on: │ │
│                                           │ - templates │ │
│                                           │ - utilities │ │
│                                           └─────────────┘ │
└────────────────────────────────────────────────────────────┘
```

---

## Key Components

### 1. InstallationPlugin (Base Interface)

```python
class InstallationPlugin(ABC):
    """Base class for all plugins."""

    def __init__(self, name: str, priority: int = 100):
        self.name = name
        self.priority = priority  # Lower = earlier execution
        self.dependencies: List[str] = []

    @abstractmethod
    def install(self, context: InstallContext) -> PluginResult:
        """Install plugin components."""
        pass

    @abstractmethod
    def verify(self, context: InstallContext) -> PluginResult:
        """Verify installation succeeded."""
        pass
```

**Key Design Principles:**
- Abstract base class enforces interface compliance
- Priority-based execution (core plugins first, extensions later)
- Explicit dependency declaration
- Standardized result format (`PluginResult`)

### 2. PluginRegistry (Dependency Manager)

```python
class PluginRegistry:
    """Manages plugin discovery, registration, and execution."""

    def register(self, plugin: InstallationPlugin) -> None:
        """Register a plugin (validates no duplicates)."""
        pass

    def get_execution_order(self) -> List[str]:
        """Resolve dependencies using Kahn's topological sort."""
        pass

    def install_all(self, context: InstallContext) -> Dict[str, PluginResult]:
        """Install all plugins in dependency order."""
        pass

    def verify_all(self, context: InstallContext) -> Dict[str, PluginResult]:
        """Verify all plugins."""
        pass
```

**Key Features:**
- **Topological Sort**: Kahn's algorithm resolves dependencies
- **Circular Dependency Detection**: Fails fast on invalid dependencies
- **Priority Ordering**: When no dependencies, uses priority for deterministic order

### 3. InstallContext (Shared State)

```python
@dataclass
class InstallContext:
    """Shared context passed to all plugins."""
    claude_dir: Path              # ~/.claude
    scripts_dir: Path             # ~/.claude/scripts
    templates_dir: Path           # ~/.claude/templates
    logger: Any                   # Logger instance
    backup_manager: Any           # BackupManager for safe overwrites
    dry_run: bool = False         # Dry-run mode flag
    metadata: Dict[str, Any]      # Plugin-to-plugin communication
```

**Design Rationale:**
- **Dependency Injection**: Plugins receive utilities via context
- **Immutable During Installation**: Plugins read, don't modify
- **Metadata Dictionary**: Enables inter-plugin data sharing

---

## DES Plugin Implementation

### Structure

```python
class DESPlugin(InstallationPlugin):
    """Plugin for DES (Definition of Enforcement System)."""

    def __init__(self):
        super().__init__(name="des", priority=50)
        self.dependencies = ["templates", "utilities"]  # DES needs these first

    def install(self, context: InstallContext) -> PluginResult:
        """Three-phase installation."""
        # Phase 1: Install DES Python module → ~/.claude/lib/python/des/
        # Phase 2: Install DES scripts → ~/.claude/scripts/
        # Phase 3: Install DES templates → ~/.claude/templates/
        pass

    def verify(self, context: InstallContext) -> PluginResult:
        """Verify DES installation."""
        # 1. Test DES module importable (subprocess import check)
        # 2. Verify scripts exist
        # 3. Verify templates exist
        pass
```

### Installation Phases

| Phase | What | Where | Verification |
|-------|------|-------|--------------|
| **1** | DES Python module | `~/.claude/lib/python/des/` | Import test: `from des.application import DESOrchestrator` |
| **2** | DES scripts | `~/.claude/scripts/` | File existence: `check_stale_phases.py`, `scope_boundary_check.py` |
| **3** | DES templates | `~/.claude/templates/` | File existence: `.pre-commit-config-nwave.yaml`, `.des-audit-README.md` |

### Dependencies

```
templates (priority 30)
    ↓
utilities (priority 40, depends on templates)
    ↓
des (priority 50, depends on templates + utilities)
```

**Why Dependencies Matter:**
- DES templates require `templates` plugin to create directory structure
- DES scripts rely on `utilities` plugin infrastructure
- Registry automatically orders DES after dependencies

---

## Dependency Resolution Algorithm

### Kahn's Topological Sort

```
Given plugins with dependencies:
  agents       (priority 10, deps: [])
  commands     (priority 20, deps: [])
  templates    (priority 30, deps: [])
  utilities    (priority 40, deps: ["templates"])
  des          (priority 50, deps: ["templates", "utilities"])

Execution Order:
  1. agents      (no deps, priority 10)
  2. commands    (no deps, priority 20)
  3. templates   (no deps, priority 30)
  4. utilities   (deps satisfied, priority 40)
  5. des         (deps satisfied, priority 50)
```

### Algorithm Steps

1. **Build Dependency Graph**: Create edges from dependencies to dependents
2. **Calculate In-Degree**: Count incoming edges for each plugin
3. **Process Zero In-Degree Nodes**: Start with plugins that have no dependencies
4. **Remove Edges**: As plugins execute, reduce in-degree of dependents
5. **Repeat**: Continue until all plugins processed
6. **Detect Cycles**: If plugins remain with in-degree > 0, circular dependency exists

**Example Circular Dependency Detection:**
```
plugin_a depends on plugin_b
plugin_b depends on plugin_c
plugin_c depends on plugin_a  ← CYCLE!

Result: ValueError("Circular dependency detected in plugins")
```

---

## Installation Workflow

### Full Installation

```bash
python install_nwave.py
```

**Steps:**
1. Create `InstallContext` with paths and utilities
2. Discover and register plugins
3. Resolve dependencies (topological sort)
4. Install plugins in order
5. Verify each plugin
6. Update manifest with installed plugins
7. Display summary table

### Selective Installation

```bash
# Install only DES (and its dependencies)
python install_nwave.py --plugin=des

# Result: Installs templates, utilities, and des (skips agents, commands)
```

### Uninstallation

```bash
# Uninstall DES
python install_nwave.py --uninstall=des

# Steps:
# 1. Check no other plugins depend on DES
# 2. Create backup
# 3. Remove DES files
# 4. Update manifest
```

---

## Benefits

### For Users

| Benefit | Before | After |
|---------|--------|-------|
| **Modularity** | Install entire framework or nothing | Choose which plugins to install |
| **Flexibility** | DES always installed | DES optional, install when needed |
| **Disk Space** | ~50MB for full framework | ~30MB core, ~20MB DES (optional) |
| **Uninstall** | Remove entire framework | Uninstall specific plugins |

### For Developers

| Benefit | Before | After |
|---------|--------|-------|
| **Extensibility** | Modify core installer for new components | Create new plugin, register it |
| **Testability** | Test entire installer | Test plugins in isolation |
| **Maintainability** | Single 800+ line file | Multiple focused plugin files |
| **Versioning** | Single version for everything | Independent plugin versions |

### For Architecture

| Benefit | Before | After |
|---------|--------|-------|
| **Coupling** | Tight coupling between components | Loose coupling via plugin interface |
| **Dependency Management** | Manual ordering, error-prone | Automatic topological sort |
| **Error Isolation** | One failure breaks everything | Plugin failures isolated |
| **Evolution** | Changing one part risks breaking others | Plugins evolve independently |

---

## Usage Examples

### Example 1: Install Core + DES

```bash
# Full installation (default)
python install_nwave.py

# Installed:
#   ✅ agents
#   ✅ commands
#   ✅ templates
#   ✅ utilities
#   ✅ des
```

### Example 2: Install Core Only

```bash
# Exclude DES
python install_nwave.py --exclude=des

# Installed:
#   ✅ agents
#   ✅ commands
#   ✅ templates
#   ✅ utilities
#   ❌ des (excluded)
```

### Example 3: Add DES Later

```bash
# Assume core already installed, now add DES
python install_nwave.py --plugin=des

# Result:
#   Dependencies already satisfied (templates, utilities exist)
#   Install only DES plugin
```

### Example 4: Dry-Run

```bash
# Preview what would be installed
python install_nwave.py --dry-run

# Output:
#   [DRY-RUN] Would install agents (10 files)
#   [DRY-RUN] Would install commands (15 files)
#   [DRY-RUN] Would install templates (5 files)
#   [DRY-RUN] Would install utilities (2 files)
#   [DRY-RUN] Would install des (module + 4 files)
```

---

## Future Plugins

### Planned Extensions

1. **Mutation Testing Plugin**
   - Install mutation testing tools (cosmic-ray, mutmut)
   - Configure with DES enforcement
   - Priority: 60, depends on: des

2. **VS Code Integration Plugin**
   - Install VS Code extension
   - Configure workspace settings
   - Add snippets and keybindings
   - Priority: 70, depends on: agents, commands

3. **GitHub Actions Plugin**
   - Install CI/CD workflows
   - Configure DES enforcement in CI
   - Setup mutation testing pipeline
   - Priority: 80, depends on: des

4. **Documentation Generator Plugin**
   - Install Sphinx/MkDocs
   - Configure automatic API docs
   - Setup documentation templates
   - Priority: 90, depends on: templates

---

## Migration Path

### Phase 1: Current State (✅ COMPLETED)
- ✅ Monolithic installer (`install_nwave.py`)
- ✅ DES hook installer as separate script (`install_des_hooks.py`)
- ✅ Helper methods extracted to `install_utils.py`

### Phase 2: Plugin Infrastructure (❌ NOT STARTED)
- ❌ Plugin base classes - TO BE IMPLEMENTED
- ❌ Plugin registry with dependency resolution - TO BE IMPLEMENTED
- ❌ DES plugin implementation - TO BE IMPLEMENTED
- ❌ Core plugins (agents, commands, templates, utilities) - TO BE IMPLEMENTED

### Phase 3: Integration (❌ NOT STARTED)
- ❌ Integrate plugins into NWaveInstaller - TO BE IMPLEMENTED
- ❌ Selective installation support - TO BE IMPLEMENTED
- ❌ Uninstallation support - TO BE IMPLEMENTED

### Phase 4: Advanced Features (⏳ FUTURE)
- ⏳ Dynamic plugin discovery
- ⏳ Plugin versioning and updates
- ⏳ Third-party plugin support

---

## Quick Reference

### Plugin Interface Checklist

When creating a new plugin:

```python
class MyPlugin(InstallationPlugin):
    def __init__(self):
        super().__init__(name="my-plugin", priority=100)
        self.dependencies = ["templates"]  # If needed

    def install(self, context: InstallContext) -> PluginResult:
        # 1. Use context.logger for logging
        # 2. Respect context.dry_run flag
        # 3. Use context.backup_manager for safe overwrites
        # 4. Return PluginResult(success=True/False, ...)
        pass

    def verify(self, context: InstallContext) -> PluginResult:
        # 1. Verify files exist
        # 2. Test imports work
        # 3. Run functional tests
        # 4. Return PluginResult
        pass
```

### Command Reference

> **NOTE**: Questi comandi descrivono funzionalità FUTURE non ancora implementate. Attualmente, solo `python install_nwave.py` è supportato e installa tutti i componenti.

```bash
# Full installation (✅ CURRENT)
python install_nwave.py

# Selective installation (❌ FUTURE)
python install_nwave.py --plugin=des

# Exclude plugins (❌ FUTURE)
python install_nwave.py --exclude=des

# Uninstall plugin (❌ FUTURE)
python install_nwave.py --uninstall=des

# Dry-run mode (✅ CURRENT)
python install_nwave.py --dry-run

# Restore from backup (✅ CURRENT)
python install_nwave.py --restore
```

---

## Key Takeaways (FUTURE DESIGN)

1. **DES will become a plugin** - Will be installable/uninstallable independently (FUTURE)
2. **Dependency resolution will be automatic** - Topological sort will handle ordering (FUTURE)
3. **Plugin interface will be simple** - Inherit base class, implement install/verify (FUTURE)
4. **System will be extensible** - New plugins can be added without modifying core (FUTURE)
5. **Will be backward compatible** - Default installation will include all plugins (FUTURE)

---

## Next Steps

1. **Review Full Architecture Document**: [nwave-plugin-system-architecture.md](./nwave-plugin-system-architecture.md)
2. **Integrate Plugins into Installer**: Modify `install_nwave.py` to use plugin system
3. **Test Installation Workflow**: Verify full and selective installations
4. **Document Plugin Development**: Create plugin development guide
5. **Plan Future Plugins**: Design mutation testing, VS Code, GitHub Actions plugins

---

**Status:** ✅ Design Complete, Ready for Implementation

**Full Documentation:** [nwave-plugin-system-architecture.md](./nwave-plugin-system-architecture.md)
