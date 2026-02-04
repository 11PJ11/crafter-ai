# nWave Plugin System Architecture

**Version:** 1.7.0
**Date:** 2026-02-04
**Status:** IMPLEMENTED
**Author:** Solution Architect (Morgan)

---

> **Plugin System: PRODUCTION READY (v1.7.0)**
>
> This architecture is fully implemented. The installer uses the plugin-based system described in this document.
>
> **Implementation**: See `scripts/install/plugins/` for production code.
>
> **Evolution Document**: See `docs/evolution/2026-02-03-plugin-architecture.md` for implementation history.

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Context and Problem Statement](#context-and-problem-statement)
3. [Architecture Goals](#architecture-goals)
4. [System Architecture](#system-architecture)
5. [Plugin Interface Design](#plugin-interface-design)
6. [Plugin Lifecycle Management](#plugin-lifecycle-management)
7. [DES as Reference Plugin Implementation](#des-as-reference-plugin-implementation)
8. [Plugin Discovery and Registration](#plugin-discovery-and-registration)
9. [Dependency Resolution](#dependency-resolution)
10. [Installation and Uninstallation](#installation-and-uninstallation)
11. [Verification and Validation](#verification-and-validation)
12. [Configuration Management](#configuration-management)
13. [Error Handling and Recovery](#error-handling-and-recovery)
14. [Future Plugin Extensions](#future-plugin-extensions)
15. [Migration Path](#migration-path)
16. [Testing Strategy](#testing-strategy)
17. [References](#references)

---

## Executive Summary

This document describes the architecture of the **nWave Plugin System**, a modular extension framework that enables the installation, management, and uninstallation of nWave components as independent plugins. The system transforms the monolithic nWave installer into a flexible, extensible architecture where components can be:

- **Independently installed and uninstalled** without affecting core nWave functionality
- **Versioned and upgraded** separately from the core framework
- **Dependency-managed** through automatic resolution and topological sorting
- **Validated** through standardized verification interfaces

The **DES (Definition of Enforcement System)** is planned as the reference implementation, demonstrating:
- Plugin structure and interface compliance
- Dependency declaration and resolution
- Installation, verification, and uninstallation workflows
- Integration with nWave's hexagonal architecture

**Key Benefits:**
- ✅ **Modularity**: Components can be added/removed independently
- ✅ **Maintainability**: Plugin isolation reduces system complexity
- ✅ **Extensibility**: New plugins can be added without modifying core installer
- ✅ **Testability**: Each plugin can be tested in isolation
- ✅ **Flexibility**: Users can choose which plugins to install

---

## Architecture Refinements (Post-Journey Analysis)

**Refinement Date**: 2026-02-03
**Analyst**: Luna (Experience Designer) + Morgan (Solution Architect)
**Status**: 9 gaps resolved, implementation readiness improved to 8.5/10

### Refinement Summary

Following Luna's comprehensive journey quality validation and Morgan's gap analysis, the plugin system architecture has been refined to address 9 identified gaps and 3 critical decision points. This section documents architectural changes and additions to the original design.

### Key Architectural Enhancements

**1. Version Strategy Clarified (GAP-ARCH-00)**
- **Issue**: Version discontinuity detected (1.2.0 → 1.7.0 jump) in journey milestones
- **Resolution**: Incremental semantic versioning strategy defined
- **Implementation**:
  ```
  Phase 1 complete: 1.2.1 (infrastructure patch)
  Phase 3 complete: 1.3.0 (plugin orchestration minor)
  Phase 4 complete: 1.4.0 (DES feature minor)
  Phase 6 complete: 1.7.0 (production marketing version)
  ```
- **Impact**: Clear communication of progress, enables intermediate rollback points

**2. Circular Import Prevention Validation (GAP-ARCH-01)**
- **Issue**: Module-level function extraction pattern documented but not validated
- **Resolution**: Proof-of-concept requirement added as mandatory prerequisite (PREREQ-2.1)
- **Validation Strategy**:
  - Create AgentsPlugin as proof-of-concept
  - Test: `python3 -c "from scripts.install.plugins.agents_plugin import AgentsPlugin"`
  - Validate NO circular import error before implementing other plugins
- **Impact**: De-risks Phase 2, validates core integration strategy (estimated 2-3 hours)

**3. Plugin Verification Fallback Pattern (GAP-ARCH-03)**
- **Issue**: Verification strategy incomplete if `installation_verifier` unavailable
- **Resolution**: Fallback pattern added to architecture
- **Pattern**:
  ```python
  def verify(self, context):
      # PRIMARY: Use existing verifier
      if context.installation_verifier:
          return context.installation_verifier._check_agents()

      # FALLBACK: Minimal file existence check
      target_dir = context.claude_dir / "agents" / "nw"
      if not target_dir.exists():
          return PluginResult(success=False, message="Directory not found")

      # Count files, validate threshold
      agent_files = list(target_dir.glob("*.md"))
      return PluginResult(
          success=len(agent_files) >= 10,
          message=f"Verified {len(agent_files)} agents"
      )
  ```
- **Impact**: Plugins work independently, enables isolated testing, graceful degradation

**4. DES Prerequisites Mandated (GAP-PREREQ-01, GAP-PREREQ-02)**
- **Issue**: DES scripts and templates don't exist yet, blocking Phase 4
- **Resolution**: Creation mandated as prerequisites before Phase 4
- **Required Files**:
  - `nWave/scripts/des/check_stale_phases.py` (4-6 hours)
  - `nWave/scripts/des/scope_boundary_check.py` (4-6 hours)
  - `nWave/templates/.pre-commit-config-nwave.yaml` (1-2 hours)
  - `nWave/templates/.des-audit-README.md` (1-2 hours)
- **Impact**: Phase 4 unblocked, DES installation complete on first try

**5. Integration Checkpoint Automation (GAP-PROCESS-01)**
- **Issue**: Integration checkpoints described but not automated
- **Resolution**: Test specification created for Phase 3 switchover validation
- **Test**:
  ```python
  def test_switchover_preserves_installation_behavior(tmp_path):
      """Validate plugin-based installation produces identical results."""
      # Compare file trees (baseline vs plugin)
      assert baseline_files == plugin_files
      # Compare verification results
      assert baseline_verification == plugin_verification
      # Compare file contents
      for file_path in baseline_files:
          assert baseline_content == plugin_content
  ```
- **Impact**: Automated regression detection, increases Phase 3 confidence (4-6 hours)

**6. InstallContext Validation Strategy (GAP-ARCH-02)**
- **Issue**: InstallContext may be missing fields needed by wrapper plugins
- **Resolution**: Continuous validation during Phase 2 implementation
- **Strategy**:
  - Review ALL utilities used by `_install_*()` methods during wrapper plugin creation
  - Add missing utilities to InstallContext BEFORE Phase 3 switchover
  - Potential missing: `build_manager`, `manifest_writer`, `preflight_checker`
- **Impact**: Prevents mid-implementation surprises (1-2 hours validation)

### Architecture Decision Outcomes

**DECISION-01: DES Script Creation Timing**
- **Decision**: Create scripts BEFORE Phase 4 (Option A)
- **Rationale**: Clean implementation without placeholders, unblocks Phase 4, modest effort
- **Trade-off**: +6 hours to timeline, but prevents technical debt

**DECISION-02: Circular Import Mitigation**
- **Decision**: Extract module-level functions (Option A)
- **Rationale**: Clean separation, testable, no runtime overhead, proven pattern
- **Trade-off**: Requires refactoring (1-2 hours per plugin), but validates before Phase 2 commit

**DECISION-03: Wrapper Plugin Verification**
- **Decision**: Fallback to minimal file existence check (Option B)
- **Rationale**: Robustness, independent testing, graceful degradation
- **Trade-off**: +20 lines per plugin, but significantly improves reliability

### New Architectural Patterns

**PATTERN-01: Module-Level Function Extraction**
```python
# install_nwave.py - Refactored for circular import prevention
def install_agents_impl(target_dir, framework_source, logger, backup_manager, dry_run):
    """Extracted implementation (module-level function)."""
    # ... existing 80-line logic moved here ...
    pass

class nWaveInstaller:
    def _install_agents(self):
        """Thin wrapper calling extracted function."""
        return install_agents_impl(
            self.claude_dir, self.framework_source, self.rich_logger,
            self.backup_manager, self.dry_run
        )
```

**PATTERN-02: Fallback Verification**
```python
class PluginBase:
    def verify(self, context: InstallContext) -> PluginResult:
        # PRIMARY: Delegate to installation_verifier
        if context.installation_verifier:
            return self._verify_with_verifier(context)

        # FALLBACK: Minimal file existence + count validation
        return self._verify_fallback(context)
```

**PATTERN-03: Integration Checkpoint Testing**
```python
# Baseline capture before switchover
baseline_files = capture_installation_state(baseline_installer)

# Plugin installation after switchover
plugin_files = capture_installation_state(plugin_installer)

# Automated comparison
assert baseline_files == plugin_files, "Regression detected!"
```

### Prerequisites Added

**Phase 2 Prerequisites**:
- PREREQ-2.1: Circular import proof-of-concept (2-3 hours) ⚠️ BLOCKS Phase 2
- PREREQ-2.2: InstallContext validation (1-2 hours, continuous)
- PREREQ-2.3: Verification fallback logic definition (2 hours)

**Phase 3 Prerequisites**:
- PREREQ-3.2: Integration checkpoint test suite (4-6 hours)
- PREREQ-3.3: Rollback procedure documentation (1 hour)

**Phase 4 Prerequisites**:
- PREREQ-4.1: DES scripts creation (4-6 hours) ⚠️ BLOCKS Phase 4
- PREREQ-4.2: DES templates creation (1-2 hours) ⚠️ BLOCKS Phase 4
- PREREQ-4.4: Build pipeline validation (30 minutes, optional)

**Total Prerequisite Effort**: 16-21 hours (many can be parallelized with phase work)

### Implementation Readiness

**Before Refinement**: 7.5/10
- Gaps: DES prerequisites missing, circular import unvalidated, integration checkpoints manual

**After Refinement**: 8.5/10
- ✅ All 9 gaps resolved with implementation guidance
- ✅ All 3 decision points finalized with rationale
- ✅ Prerequisites clearly documented with estimated effort
- ✅ 4 architectural patterns added
- ✅ Validation strategies defined

**Remaining Work**: Implementation execution (prerequisite creation + phase work)

### Documentation Additions

- **architecture-decisions.md**: Complete gap analysis with architectural rationale
- **prerequisites.md**: Phase-specific prerequisites checklist with blocking items
- **design-refinement-summary.md**: Summary of changes and business impact
- **design.md**: Updated with refinements section
- **nwave-plugin-system-architecture.md**: This section added

### References

For complete gap analysis, decision rationale, and implementation specifications:
- See `docs/feature/plugin-architecture/architecture-decisions.md`
- See `docs/feature/plugin-architecture/prerequisites.md`
- See `docs/feature/plugin-architecture/design-refinement-summary.md`

---

## Context and Problem Statement

### Current State

The nWave framework currently uses a **monolithic installer** (`install_nwave.py`) that handles:
- Framework core (agents, commands, templates, utilities)
- DES module installation (Python module, scripts, templates, hooks)
- All installation logic tightly coupled within `NWaveInstaller` class

**Problems with Current Approach:**
1. **Tight Coupling**: DES installation logic embedded in core installer
2. **No Modularity**: Cannot install/uninstall DES independently
3. **Limited Extensibility**: Adding new components requires modifying core installer
4. **Testing Complexity**: Cannot test DES installation in isolation
5. **Version Management**: Cannot version DES separately from nWave core

### Business Needs

The nWave ecosystem requires:
- **DES as optional plugin** - users may not need enforcement in all projects
- **Future extensibility** - planned plugins include:
  - Quality validation plugins (mutation testing, coverage analysis)
  - IDE integrations (VS Code, JetBrains)
  - CI/CD pipeline plugins (GitHub Actions, GitLab CI)
  - Reporting and analytics plugins
- **Independent lifecycle management** - plugins evolve at different rates

### Technical Requirements

1. **Plugin Interface**: Standardized contract for all plugins
2. **Dependency Resolution**: Automatic ordering based on dependencies
3. **Lifecycle Management**: Install, verify, uninstall operations
4. **Backward Compatibility**: Existing installations must continue working
5. **Error Recovery**: Failed plugins should not break entire installation
6. **Configuration Isolation**: Each plugin manages its own configuration

---

## Architecture Goals

### Primary Goals

1. **Modularity**
   - Plugins are self-contained, independent units
   - Core framework remains stable while plugins evolve
   - Clear separation of concerns between core and plugins

2. **Extensibility**
   - New plugins can be added without modifying core installer
   - Plugin registry dynamically discovers and loads plugins
   - Third-party plugins supported through standard interface

3. **Maintainability**
   - Each plugin owns its installation, verification, and uninstallation logic
   - Plugin failures are isolated and do not cascade
   - Clear error messages and recovery procedures

4. **Testability**
   - Plugins can be tested independently
   - Mock contexts enable unit testing without full installation
   - Integration tests validate plugin interactions

5. **User Experience**
   - Simple plugin installation: `python install_nwave.py --plugin=des`
   - Clear feedback on installation progress and status
   - Easy uninstallation: `python install_nwave.py --uninstall=des`

### Non-Goals (Out of Scope)

- ❌ Runtime plugin loading/hot-swapping (installation-time only)
- ❌ Plugin marketplace or repository (local plugins only for now)
- ❌ Complex plugin versioning with dependency constraints (simple version checks only)
- ❌ Plugin sandboxing or security isolation (trusted plugins assumed)

---

## System Architecture

### High-Level Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                     nWave Installation System                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │              NWaveInstaller (Orchestrator)                 │  │
│  │  - Coordinates installation workflow                       │  │
│  │  - Creates InstallContext (shared state)                   │  │
│  │  - Delegates to PluginRegistry                             │  │
│  └───────────────┬───────────────────────────────────────────┘  │
│                  │                                                │
│                  │ creates context and delegates                 │
│                  ▼                                                │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │                    PluginRegistry                          │  │
│  │  - Discovers and registers plugins                         │  │
│  │  - Resolves dependencies (topological sort)                │  │
│  │  - Executes plugins in correct order                       │  │
│  └───────────────┬───────────────────────────────────────────┘  │
│                  │                                                │
│                  │ manages                                        │
│                  ▼                                                │
│  ┌──────────────────────────────────────────────────────────────┐
│  │                  Plugin Implementations                       │
│  ├──────────────────────────────────────────────────────────────┤
│  │                                                               │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │  │ Agents   │  │Commands  │  │Templates │  │Utilities │   │
│  │  │ Plugin   │  │ Plugin   │  │ Plugin   │  │ Plugin   │   │
│  │  │Priority:│  │Priority:│  │Priority:│  │Priority:│   │
│  │  │   10     │  │   20     │  │   30     │  │   40     │   │
│  │  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘   │
│  │       │             │             │             │           │
│  │       │             │             │             │           │
│  │       │             │             │             ▼           │
│  │       │             │             │       ┌──────────┐     │
│  │       │             │             │       │   DES    │     │
│  │       │             │             │       │  Plugin  │     │
│  │       │             │             │       │Priority:│     │
│  │       │             │             │       │   50     │     │
│  │       │             │             │       └────┬─────┘     │
│  │       │             │             │            │           │
│  │       └─────────────┴─────────────┴────────────┘           │
│  │                           │                                 │
│  │                    depends on                               │
│  │                           │                                 │
│  └───────────────────────────┼─────────────────────────────────┘
│                              │                                  │
│                              │ uses                             │
│                              ▼                                  │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │                   InstallContext                           │ │
│  │  Shared installation state and utilities:                  │ │
│  │  - claude_dir: Path to .claude directory                   │ │
│  │  - logger: Logging instance                                │ │
│  │  - backup_manager: Backup/restore utilities                │ │
│  │  - dry_run: Flag for dry-run mode                          │ │
│  │  - metadata: Plugin-specific shared data                   │ │
│  └───────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

### Component Responsibilities

#### 1. NWaveInstaller (Orchestrator)
- Initializes installation environment
- Creates `InstallContext` with shared utilities
- Discovers and registers plugins
- Delegates installation workflow to `PluginRegistry`
- Handles high-level error reporting and recovery

#### 2. PluginRegistry (Dependency Manager)
- Maintains registry of available plugins
- Resolves plugin dependencies using Kahn's topological sort
- Detects circular dependencies
- Executes plugins in correct order
- Aggregates installation results

#### 3. InstallContext (Shared State)
- Provides shared utilities (logger, backup manager, verifier)
- Exposes installation paths (claude_dir, scripts_dir, templates_dir)
- Maintains metadata dictionary for inter-plugin communication
- Supports dry-run mode for safe testing

#### 4. Plugin Implementations
- Self-contained installation logic for specific components
- Declare dependencies on other plugins
- Implement standard `install()` and `verify()` interface
- Handle component-specific installation, verification, and cleanup

---

## Plugin Interface Design

### Base Plugin Interface

All plugins inherit from `InstallationPlugin` abstract base class:

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List

@dataclass
class PluginResult:
    """Result of plugin installation/verification."""
    success: bool
    plugin_name: str
    message: str = ""
    errors: List[str] = field(default_factory=list)
    installed_files: List[Path] = field(default_factory=list)

@dataclass
class InstallContext:
    """Shared context passed to all plugins."""
    claude_dir: Path              # ~/.claude
    scripts_dir: Path             # ~/.claude/scripts
    templates_dir: Path           # ~/.claude/templates
    logger: Any                   # Logger instance
    project_root: Path = None     # nWave project root
    framework_source: Path = None # dist/ide directory
    backup_manager: Any = None    # BackupManager instance
    rich_logger: Any = None       # RichLogger for styled output
    dry_run: bool = False         # Dry-run mode flag
    dist_dir: Path = None         # Built distribution directory
    metadata: Dict[str, Any] = field(default_factory=dict)

class InstallationPlugin(ABC):
    """Base class for installation plugins."""

    def __init__(self, name: str, priority: int = 100):
        """
        Initialize plugin.

        Args:
            name: Unique plugin identifier
            priority: Execution priority (lower = earlier)
        """
        self.name = name
        self.priority = priority
        self.dependencies: List[str] = []

    @abstractmethod
    def install(self, context: InstallContext) -> PluginResult:
        """Install this plugin's components."""
        pass

    @abstractmethod
    def verify(self, context: InstallContext) -> PluginResult:
        """Verify plugin installation was successful."""
        pass

    def get_dependencies(self) -> List[str]:
        """Return list of plugin names this plugin depends on."""
        return self.dependencies
```

### Interface Design Rationale

1. **Abstract Base Class (ABC)**
   - Enforces interface compliance at import time
   - Python's ABC prevents instantiation of incomplete plugins
   - Clear contract: all plugins MUST implement `install()` and `verify()`

2. **Dataclass Results**
   - Structured return values with type hints
   - Easy to serialize for logging and reporting
   - `PluginResult` enables rich feedback and error tracking

3. **InstallContext as Dependency Injection**
   - Plugins receive all necessary utilities via context
   - Eliminates need for plugins to create their own loggers, backup managers, etc.
   - Context is immutable during installation (plugins read, don't modify)
   - `metadata` dictionary enables plugin-to-plugin communication

4. **Priority-Based Execution**
   - Lower priority = earlier execution
   - Core plugins (agents, commands) execute first (priority 10-40)
   - Extension plugins (DES) execute after core (priority 50+)
   - Allows future plugins to insert at appropriate execution point

5. **Dependency Declaration**
   - Explicit `dependencies: List[str]` in each plugin
   - Registry resolves dependencies automatically
   - Circular dependencies detected and rejected

---

## Plugin Lifecycle Management

### Installation Lifecycle

```
┌─────────────────────────────────────────────────────────────────┐
│                    Plugin Installation Lifecycle                 │
└─────────────────────────────────────────────────────────────────┘

1. DISCOVERY
   ├─ Scan scripts/install/plugins/ directory
   ├─ Import all *_plugin.py modules
   └─ Instantiate plugin classes

2. REGISTRATION
   ├─ Register plugins with PluginRegistry
   ├─ Validate no duplicate plugin names
   └─ Collect dependencies from each plugin

3. DEPENDENCY RESOLUTION
   ├─ Build dependency graph
   ├─ Detect circular dependencies (fail fast if found)
   ├─ Topological sort using Kahn's algorithm
   └─ Produce execution order: [agents, commands, templates, utilities, des]

4. INSTALLATION (for each plugin in order)
   ├─ Call plugin.install(context)
   ├─ Log installation progress
   ├─ Collect PluginResult
   └─ STOP if plugin fails (unless --continue-on-error flag)

5. VERIFICATION (for each plugin in order)
   ├─ Call plugin.verify(context)
   ├─ Validate installed files exist
   ├─ Run plugin-specific validation logic
   └─ Report verification results

6. MANIFEST UPDATE
   ├─ Record installed plugins in nwave-manifest.txt
   ├─ Include plugin versions and dependencies
   └─ Save installation metadata
```

### Uninstallation Lifecycle

```
┌─────────────────────────────────────────────────────────────────┐
│                  Plugin Uninstallation Lifecycle                 │
└─────────────────────────────────────────────────────────────────┘

1. DEPENDENCY CHECK
   ├─ Load installed plugins from manifest
   ├─ Check if other plugins depend on target plugin
   └─ STOP if dependents exist (e.g., can't uninstall templates if DES depends on it)

2. BACKUP
   ├─ Create backup of plugin files
   ├─ Record backup location in manifest
   └─ Enable rollback if uninstall fails

3. UNINSTALLATION
   ├─ Call plugin.uninstall(context)  [if implemented]
   ├─ Remove installed files
   ├─ Clean up configuration
   └─ Log uninstallation progress

4. MANIFEST UPDATE
   ├─ Remove plugin from installed list
   ├─ Record uninstallation timestamp
   └─ Preserve backup reference for rollback

5. VERIFICATION
   ├─ Confirm plugin files removed
   ├─ Verify no orphaned configuration
   └─ Check system still functional
```

---

## DES as Reference Plugin Implementation

The **DES Plugin** serves as the canonical example of plugin implementation, demonstrating all required interfaces and best practices.

### DES Plugin Structure

```python
"""DES (Definition of Enforcement System) installation plugin."""

import shutil
import subprocess
from pathlib import Path

from .base import InstallContext, InstallationPlugin, PluginResult


class DESPlugin(InstallationPlugin):
    """Plugin for installing DES (Definition of Enforcement System)."""

    def __init__(self):
        """Initialize DES plugin with name, priority, and dependencies."""
        super().__init__(name="des", priority=50)
        self.dependencies = ["templates", "utilities"]  # DES requires these first

    def install(self, context: InstallContext) -> PluginResult:
        """Install DES module, scripts, and templates."""
        try:
            # Install DES module
            module_result = self._install_des_module(context)
            if not module_result.success:
                return module_result

            # Install DES scripts
            scripts_result = self._install_des_scripts(context)
            if not scripts_result.success:
                return scripts_result

            # Install DES templates
            templates_result = self._install_des_templates(context)
            if not templates_result.success:
                return templates_result

            return PluginResult(
                success=True,
                plugin_name="des",
                message="DES installed successfully",
            )

        except Exception as e:
            return PluginResult(
                success=False,
                plugin_name="des",
                message=f"DES installation failed: {e}",
            )

    def _install_des_module(self, context: InstallContext) -> PluginResult:
        """Install DES Python module to ~/.claude/lib/python/des/."""
        try:
            # Source: dist/lib/python/des or src/des
            if hasattr(context, "dist_dir") and context.dist_dir:
                source_dir = context.dist_dir / "lib" / "python" / "des"
            else:
                source_dir = Path("src/des")

            if not source_dir.exists():
                return PluginResult(
                    success=False,
                    plugin_name="des",
                    message=f"DES source not found: {source_dir}",
                )

            # Target: ~/.claude/lib/python/des
            lib_python_dir = context.claude_dir / "lib" / "python"
            target_dir = lib_python_dir / "des"

            lib_python_dir.mkdir(parents=True, exist_ok=True)

            # Backup existing if present
            if context.backup_manager and target_dir.exists():
                context.logger.info(f"Backing up existing DES module: {target_dir}")
                context.backup_manager.backup_directory(target_dir)

            # Copy module
            if context.dry_run:
                context.logger.info(f"[DRY-RUN] Would copy {source_dir} → {target_dir}")
            else:
                if target_dir.exists():
                    shutil.rmtree(target_dir)
                shutil.copytree(source_dir, target_dir)

            return PluginResult(
                success=True,
                plugin_name="des",
                message=f"DES module copied to {target_dir}",
            )

        except Exception as e:
            return PluginResult(
                success=False,
                plugin_name="des",
                message=f"DES module install failed: {e}",
            )

    def _install_des_scripts(self, context: InstallContext) -> PluginResult:
        """Install DES utility scripts."""
        try:
            scripts_to_install = [
                "check_stale_phases.py",
                "scope_boundary_check.py",
            ]

            # Source: framework_source/scripts/des or nWave/scripts/des
            if context.framework_source:
                source_dir = context.framework_source / "scripts" / "des"
            else:
                source_dir = Path("nWave/scripts/des")

            target_dir = context.scripts_dir

            installed = []
            for script_name in scripts_to_install:
                source = source_dir / script_name
                target = target_dir / script_name

                if source.exists():
                    if not context.dry_run:
                        shutil.copy2(source, target)
                        target.chmod(0o755)
                    installed.append(script_name)

            return PluginResult(
                success=True,
                plugin_name="des",
                message=f"Installed {len(installed)} DES scripts",
            )

        except Exception as e:
            return PluginResult(
                success=False,
                plugin_name="des",
                message=f"DES scripts install failed: {e}",
            )

    def _install_des_templates(self, context: InstallContext) -> PluginResult:
        """Install DES templates."""
        try:
            templates = [
                ".pre-commit-config-nwave.yaml",
                ".des-audit-README.md",
            ]

            source_dir = Path("nWave/templates")
            target_dir = context.templates_dir

            installed = []
            for template_name in templates:
                source = source_dir / template_name
                target = target_dir / template_name

                if source.exists():
                    if not context.dry_run:
                        shutil.copy2(source, target)
                    installed.append(template_name)

            return PluginResult(
                success=True,
                plugin_name="des",
                message=f"Installed {len(installed)} DES templates",
            )

        except Exception as e:
            return PluginResult(
                success=False,
                plugin_name="des",
                message=f"DES templates install failed: {e}",
            )

    def verify(self, context: InstallContext) -> PluginResult:
        """Verify DES installation."""
        errors = []

        # 1. Verify DES module importable
        try:
            lib_python = context.claude_dir / "lib" / "python"
            result = subprocess.run(
                [
                    "python3",
                    "-c",
                    f'import sys; sys.path.insert(0, "{lib_python}"); '
                    f'from des.application import DESOrchestrator',
                ],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode != 0:
                errors.append(f"DES module import failed: {result.stderr}")
        except Exception as e:
            errors.append(f"DES module verify failed: {e}")

        # 2. Verify scripts present
        expected_scripts = ["check_stale_phases.py", "scope_boundary_check.py"]
        for script in expected_scripts:
            script_path = context.scripts_dir / script
            if not script_path.exists():
                errors.append(f"Missing DES script: {script}")

        # 3. Verify templates present
        expected_templates = [".pre-commit-config-nwave.yaml", ".des-audit-README.md"]
        for template in expected_templates:
            template_path = context.templates_dir / template
            if not template_path.exists():
                errors.append(f"Missing DES template: {template}")

        if errors:
            return PluginResult(
                success=False,
                plugin_name="des",
                message="DES verification failed",
                errors=errors,
            )

        return PluginResult(
            success=True,
            plugin_name="des",
            message="DES verification passed (module, scripts, templates OK)",
        )
```

### DES Plugin Key Features

1. **Dependency Declaration**
   ```python
   self.dependencies = ["templates", "utilities"]
   ```
   - DES requires templates and utilities plugins to be installed first
   - Registry automatically orders DES after these dependencies

2. **Three-Phase Installation**
   - **Phase 1**: DES Python module → `~/.claude/lib/python/des/`
   - **Phase 2**: DES utility scripts → `~/.claude/scripts/`
   - **Phase 3**: DES templates → `~/.claude/templates/`

3. **Comprehensive Verification**
   - Module importability test (subprocess import check)
   - File existence validation (scripts and templates)
   - Structured error reporting

4. **Backup Integration**
   - Uses `context.backup_manager` for safe overwrites
   - Enables rollback if installation fails

5. **Dry-Run Support**
   - Respects `context.dry_run` flag
   - Logs actions without modifying filesystem

---

## Plugin Discovery and Registration

### Discovery Mechanism

```python
# In NWaveInstaller.__init__()

def _discover_plugins(self) -> PluginRegistry:
    """Discover and register all available plugins."""
    registry = PluginRegistry()

    # Import plugin modules
    from scripts.install.plugins.agents_plugin import AgentsPlugin
    from scripts.install.plugins.commands_plugin import CommandsPlugin
    from scripts.install.plugins.templates_plugin import TemplatesPlugin
    from scripts.install.plugins.utilities_plugin import UtilitiesPlugin
    from scripts.install.plugins.des_plugin import DESPlugin

    # Register plugins
    registry.register(AgentsPlugin())
    registry.register(CommandsPlugin())
    registry.register(TemplatesPlugin())
    registry.register(UtilitiesPlugin())
    registry.register(DESPlugin())

    return registry
```

### Registration Process

```python
class PluginRegistry:
    """Registry for managing plugins and their execution order."""

    def __init__(self):
        """Initialize empty plugin registry."""
        self.plugins: Dict[str, InstallationPlugin] = {}

    def register(self, plugin: InstallationPlugin) -> None:
        """Register a plugin.

        Raises:
            ValueError: If plugin with same name already registered
        """
        if plugin.name in self.plugins:
            raise ValueError(f"Plugin '{plugin.name}' already registered")
        self.plugins[plugin.name] = plugin
```

### Future: Dynamic Discovery

For extensibility, future versions can support dynamic discovery:

```python
def _discover_plugins_dynamic(self) -> PluginRegistry:
    """Dynamically discover plugins from plugins directory."""
    registry = PluginRegistry()
    plugins_dir = Path(__file__).parent / "plugins"

    # Find all *_plugin.py files
    for plugin_file in plugins_dir.glob("*_plugin.py"):
        if plugin_file.name == "base.py":
            continue

        # Import module dynamically
        module_name = plugin_file.stem
        spec = importlib.util.spec_from_file_location(module_name, plugin_file)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Find InstallationPlugin subclasses
        for item_name in dir(module):
            item = getattr(module, item_name)
            if (isinstance(item, type) and
                issubclass(item, InstallationPlugin) and
                item is not InstallationPlugin):
                registry.register(item())

    return registry
```

---

## Dependency Resolution

### Topological Sort Algorithm (Kahn's Algorithm)

The `PluginRegistry` uses **Kahn's algorithm** for topological sorting to determine plugin execution order.

#### Algorithm Steps

```python
def _topological_sort_kahn(self) -> List[str]:
    """Topological sort using Kahn's algorithm."""

    # Step 1: Build adjacency list and in-degree count
    graph: Dict[str, List[str]] = {}
    in_degree: Dict[str, int] = {}

    for name in self.plugins:
        graph[name] = []
        in_degree[name] = 0

    # Step 2: Build edges (dependency → dependent)
    for plugin in self.plugins.values():
        for dep in plugin.get_dependencies():
            if dep not in self.plugins:
                raise ValueError(
                    f"Plugin '{plugin.name}' depends on missing plugin '{dep}'"
                )
            graph[dep].append(plugin.name)
            in_degree[plugin.name] += 1

    # Step 3: Collect nodes with no incoming edges (no dependencies)
    queue = [name for name in self.plugins if in_degree[name] == 0]

    # Step 4: Sort by priority for deterministic ordering
    queue.sort(key=lambda x: self.plugins[x].priority)

    sorted_order = []

    # Step 5: Process nodes
    while queue:
        # Remove node with lowest priority (earliest execution)
        queue.sort(key=lambda x: self.plugins[x].priority)
        node = queue.pop(0)
        sorted_order.append(node)

        # For each neighbor (dependent)
        for neighbor in graph[node]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)

    # Step 6: Check if all nodes processed (no cycle)
    if len(sorted_order) != len(self.plugins):
        raise ValueError("Circular dependency detected in plugins")

    return sorted_order
```

#### Example Dependency Resolution

Given plugins with dependencies:
```
agents       (priority 10, dependencies: [])
commands     (priority 20, dependencies: [])
templates    (priority 30, dependencies: [])
utilities    (priority 40, dependencies: ["templates"])
des          (priority 50, dependencies: ["templates", "utilities"])
```

**Execution Order:**
```
1. agents      (no dependencies, priority 10)
2. commands    (no dependencies, priority 20)
3. templates   (no dependencies, priority 30)
4. utilities   (depends on templates, priority 40)
5. des         (depends on templates and utilities, priority 50)
```

#### Circular Dependency Detection

If circular dependency exists:
```
plugin_a depends on plugin_b
plugin_b depends on plugin_c
plugin_c depends on plugin_a  ← CIRCULAR DEPENDENCY
```

The topological sort will fail with:
```
ValueError: Circular dependency detected in plugins
```

---

## Installation and Uninstallation

### Installation Workflow

```python
class NWaveInstaller:
    """nWave framework installer with plugin support."""

    def install_framework(self) -> bool:
        """Install framework using plugin system."""

        # Step 1: Create installation context
        context = InstallContext(
            claude_dir=self.claude_config_dir,
            scripts_dir=self.claude_config_dir / "scripts",
            templates_dir=self.claude_config_dir / "templates",
            logger=self.logger,
            project_root=self.project_root,
            framework_source=self.framework_source,
            backup_manager=self.backup_manager,
            rich_logger=self.rich_logger,
            dry_run=self.dry_run,
        )

        # Step 2: Discover and register plugins
        registry = self._discover_plugins()

        # Step 3: Install all plugins in dependency order
        results = registry.install_all(context)

        # Step 4: Check for failures
        failed_plugins = [
            name for name, result in results.items() if not result.success
        ]

        if failed_plugins:
            self.logger.error(f"Failed plugins: {', '.join(failed_plugins)}")
            return False

        # Step 5: Verify all plugins
        verify_results = registry.verify_all(context)

        failed_verifications = [
            name for name, result in verify_results.items() if not result.success
        ]

        if failed_verifications:
            self.logger.error(f"Verification failed: {', '.join(failed_verifications)}")
            return False

        return True
```

### Selective Plugin Installation

```bash
# Install only specific plugins
python install_nwave.py --plugin=agents --plugin=commands --plugin=des

# Install core without DES
python install_nwave.py --exclude=des

# Install only DES (assumes core already installed)
python install_nwave.py --plugin=des
```

Implementation:
```python
def install_selective(self, plugin_names: List[str]) -> bool:
    """Install only specified plugins."""
    registry = self._discover_plugins()

    # Filter to requested plugins and their dependencies
    selected_plugins = set(plugin_names)

    # Add dependencies recursively
    def add_dependencies(plugin_name: str):
        if plugin_name not in registry.plugins:
            raise ValueError(f"Unknown plugin: {plugin_name}")
        selected_plugins.add(plugin_name)
        for dep in registry.plugins[plugin_name].get_dependencies():
            add_dependencies(dep)

    for name in plugin_names:
        add_dependencies(name)

    # Filter registry to selected plugins
    filtered_registry = PluginRegistry()
    for name in selected_plugins:
        filtered_registry.register(registry.plugins[name])

    # Install filtered set
    context = self._create_context()
    results = filtered_registry.install_all(context)

    # Check results...
```

### Uninstallation Workflow

```python
def uninstall_plugin(self, plugin_name: str) -> bool:
    """Uninstall a specific plugin."""

    # Step 1: Load manifest to check installed plugins
    manifest = self._load_manifest()

    if plugin_name not in manifest["installed_plugins"]:
        self.logger.error(f"Plugin '{plugin_name}' is not installed")
        return False

    # Step 2: Check for dependents
    dependents = self._find_dependents(plugin_name, manifest)

    if dependents:
        self.logger.error(
            f"Cannot uninstall '{plugin_name}': required by {', '.join(dependents)}"
        )
        self.logger.info(f"Uninstall {', '.join(dependents)} first")
        return False

    # Step 3: Create backup
    plugin_files = manifest["installed_plugins"][plugin_name]["files"]
    backup_dir = self.backup_manager.create_backup(plugin_files)

    # Step 4: Uninstall plugin
    plugin_class = self._load_plugin_class(plugin_name)
    plugin = plugin_class()

    context = self._create_context()
    result = plugin.uninstall(context) if hasattr(plugin, "uninstall") else None

    if result and not result.success:
        self.logger.error(f"Uninstall failed: {result.message}")
        self.logger.info(f"Rolling back from backup: {backup_dir}")
        self.backup_manager.restore_backup(backup_dir)
        return False

    # Step 5: Remove files
    for file_path in plugin_files:
        if file_path.exists():
            file_path.unlink()

    # Step 6: Update manifest
    del manifest["installed_plugins"][plugin_name]
    self._save_manifest(manifest)

    self.logger.info(f"Plugin '{plugin_name}' uninstalled successfully")
    return True
```

---

## Verification and Validation

### Plugin Verification Interface

Each plugin implements `verify()` method for post-installation validation:

```python
class InstallationPlugin(ABC):
    @abstractmethod
    def verify(self, context: InstallContext) -> PluginResult:
        """Verify plugin installation was successful."""
        pass
```

### Verification Strategies

#### 1. File Existence Validation
```python
def verify(self, context: InstallContext) -> PluginResult:
    """Verify files were installed."""
    errors = []

    expected_files = [
        context.scripts_dir / "script1.py",
        context.templates_dir / "template1.yaml",
    ]

    for file_path in expected_files:
        if not file_path.exists():
            errors.append(f"Missing file: {file_path}")

    if errors:
        return PluginResult(
            success=False,
            plugin_name=self.name,
            message="Verification failed",
            errors=errors,
        )

    return PluginResult(success=True, plugin_name=self.name)
```

#### 2. Module Importability Test
```python
def verify(self, context: InstallContext) -> PluginResult:
    """Verify module can be imported."""
    try:
        lib_python = context.claude_dir / "lib" / "python"
        result = subprocess.run(
            [
                "python3",
                "-c",
                f'import sys; sys.path.insert(0, "{lib_python}"); '
                f'import my_module',
            ],
            capture_output=True,
            text=True,
            timeout=5,
        )

        if result.returncode != 0:
            return PluginResult(
                success=False,
                plugin_name=self.name,
                message=f"Import failed: {result.stderr}",
            )

        return PluginResult(success=True, plugin_name=self.name)

    except Exception as e:
        return PluginResult(
            success=False,
            plugin_name=self.name,
            message=f"Verification failed: {e}",
        )
```

#### 3. Functional Validation
```python
def verify(self, context: InstallContext) -> PluginResult:
    """Verify plugin functionality."""
    try:
        # Test plugin-specific functionality
        # Example: Run a command and check output
        result = subprocess.run(
            [context.scripts_dir / "my_script.py", "--version"],
            capture_output=True,
            text=True,
            timeout=5,
        )

        if result.returncode != 0 or not result.stdout.startswith("1.0"):
            return PluginResult(
                success=False,
                plugin_name=self.name,
                message=f"Functional test failed: {result.stderr}",
            )

        return PluginResult(success=True, plugin_name=self.name)

    except Exception as e:
        return PluginResult(
            success=False,
            plugin_name=self.name,
            message=f"Functional verification failed: {e}",
        )
```

### Verification Reporting

```python
def validate_installation(self) -> bool:
    """Run verification for all installed plugins."""
    registry = self._discover_plugins()
    context = self._create_context()

    verify_results = registry.verify_all(context)

    # Display results as Rich table
    validation_rows = []
    for plugin_name, result in verify_results.items():
        status = "✅ OK" if result.success else "❌ FAIL"
        message = result.message
        validation_rows.append([plugin_name, status, message])

    self.rich_logger.table(
        headers=["Plugin", "Status", "Details"],
        rows=validation_rows,
        title="Plugin Verification Results",
    )

    # Return overall success
    all_passed = all(result.success for result in verify_results.values())
    return all_passed
```

---

## Configuration Management

### Plugin Manifest

The `nwave-manifest.txt` file tracks installed plugins:

```json
{
  "version": "1.2.0",
  "installed_at": "2026-02-03T10:30:00Z",
  "installation_mode": "full",
  "installed_plugins": {
    "agents": {
      "version": "1.2.0",
      "installed_at": "2026-02-03T10:30:10Z",
      "files": [
        "~/.claude/agents/nw/business-analyst.md",
        "~/.claude/agents/nw/solution-architect.md"
      ]
    },
    "commands": {
      "version": "1.2.0",
      "installed_at": "2026-02-03T10:30:15Z",
      "files": [
        "~/.claude/commands/nw/discuss.md",
        "~/.claude/commands/nw/design.md"
      ]
    },
    "templates": {
      "version": "1.2.0",
      "installed_at": "2026-02-03T10:30:20Z",
      "files": [
        "~/.claude/templates/step-tdd-cycle-schema.json"
      ]
    },
    "utilities": {
      "version": "1.2.0",
      "installed_at": "2026-02-03T10:30:25Z",
      "files": [
        "~/.claude/scripts/install_nwave_target_hooks.py",
        "~/.claude/scripts/validate_step_file.py"
      ]
    },
    "des": {
      "version": "1.0.0",
      "installed_at": "2026-02-03T10:30:30Z",
      "dependencies": ["templates", "utilities"],
      "files": [
        "~/.claude/lib/python/des/",
        "~/.claude/scripts/check_stale_phases.py",
        "~/.claude/scripts/scope_boundary_check.py",
        "~/.claude/templates/.pre-commit-config-nwave.yaml",
        "~/.claude/templates/.des-audit-README.md"
      ],
      "configuration": {
        "hooks_installed": true,
        "hook_config_file": "~/.claude/settings.local.json"
      }
    }
  },
  "backups": [
    {
      "timestamp": "2026-02-03T10:29:00Z",
      "location": "~/.claude/backups/nwave-20260203-102900"
    }
  ]
}
```

### Plugin-Specific Configuration

Plugins can store configuration in `InstallContext.metadata`:

```python
def install(self, context: InstallContext) -> PluginResult:
    """Install plugin and save configuration."""

    # Perform installation...

    # Save plugin-specific metadata
    context.metadata[self.name] = {
        "hooks_installed": True,
        "hook_config_file": str(context.claude_dir / "settings.local.json"),
    }

    return PluginResult(success=True, plugin_name=self.name)
```

The metadata is persisted to the manifest by the installer.

---

## Error Handling and Recovery

### Error Handling Strategy

#### 1. Fail Fast on Critical Errors
```python
def install_all(self, context: InstallContext) -> Dict[str, PluginResult]:
    """Install all plugins in dependency order."""
    results = {}
    order = self.get_execution_order()

    for plugin_name in order:
        plugin = self.plugins[plugin_name]
        result = plugin.install(context)
        results[plugin_name] = result

        if not result.success:
            context.logger.error(f"Plugin installation failed: {result.message}")
            break  # STOP on first failure

    return results
```

#### 2. Continue on Error (Optional Flag)
```python
def install_all(
    self,
    context: InstallContext,
    continue_on_error: bool = False
) -> Dict[str, PluginResult]:
    """Install all plugins, optionally continuing on errors."""
    results = {}
    order = self.get_execution_order()

    for plugin_name in order:
        plugin = self.plugins[plugin_name]
        result = plugin.install(context)
        results[plugin_name] = result

        if not result.success:
            context.logger.error(f"Plugin installation failed: {result.message}")

            if not continue_on_error:
                break  # STOP on first failure
            else:
                context.logger.warn(f"Continuing despite failure in '{plugin_name}'")

    return results
```

### Recovery Mechanisms

#### 1. Automatic Rollback
```python
def install_framework(self) -> bool:
    """Install framework with automatic rollback on failure."""

    # Create backup before installation
    backup_dir = self.backup_manager.create_backup()

    try:
        registry = self._discover_plugins()
        context = self._create_context()
        results = registry.install_all(context)

        # Check for failures
        failed_plugins = [
            name for name, result in results.items() if not result.success
        ]

        if failed_plugins:
            self.logger.error(f"Installation failed: {', '.join(failed_plugins)}")
            self.logger.info("Rolling back to previous state...")
            self.backup_manager.restore_backup(backup_dir)
            return False

        return True

    except Exception as e:
        self.logger.error(f"Installation error: {e}")
        self.logger.info("Rolling back to previous state...")
        self.backup_manager.restore_backup(backup_dir)
        return False
```

#### 2. Manual Rollback
```bash
# User-initiated rollback
python install_nwave.py --restore
```

Implementation:
```python
def restore_backup(self) -> bool:
    """Restore from most recent backup."""
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

    # Restore...
```

#### 3. Partial Uninstall and Retry
```bash
# Uninstall failed plugin and retry
python install_nwave.py --uninstall=des
python install_nwave.py --plugin=des
```

---

## Future Plugin Extensions

### Planned Plugins

#### 1. Mutation Testing Plugin
```python
class MutationTestingPlugin(InstallationPlugin):
    """Plugin for mutation testing integration."""

    def __init__(self):
        super().__init__(name="mutation-testing", priority=60)
        self.dependencies = ["des"]  # Requires DES for enforcement

    def install(self, context: InstallContext) -> PluginResult:
        """Install mutation testing tools and configuration."""
        # Install cosmic-ray or mutmut
        # Configure mutation testing workflow
        # Integrate with DES hooks
        pass
```

#### 2. VS Code Integration Plugin
```python
class VSCodePlugin(InstallationPlugin):
    """Plugin for VS Code integration."""

    def __init__(self):
        super().__init__(name="vscode", priority=70)
        self.dependencies = ["agents", "commands"]

    def install(self, context: InstallContext) -> PluginResult:
        """Install VS Code extension and configuration."""
        # Install .vscode/extensions/nwave-vscode/
        # Configure workspace settings
        # Add snippets and keybindings
        pass
```

#### 3. GitHub Actions Plugin
```python
class GitHubActionsPlugin(InstallationPlugin):
    """Plugin for GitHub Actions CI/CD integration."""

    def __init__(self):
        super().__init__(name="github-actions", priority=80)
        self.dependencies = ["des"]

    def install(self, context: InstallContext) -> PluginResult:
        """Install GitHub Actions workflows."""
        # Copy .github/workflows/nwave-ci.yml to target project
        # Configure DES enforcement in CI
        # Setup mutation testing in pipeline
        pass
```

#### 4. Documentation Generator Plugin
```python
class DocsGeneratorPlugin(InstallationPlugin):
    """Plugin for automatic documentation generation."""

    def __init__(self):
        super().__init__(name="docs-generator", priority=90)
        self.dependencies = ["templates"]

    def install(self, context: InstallContext) -> PluginResult:
        """Install documentation generation tools."""
        # Install Sphinx or MkDocs configuration
        # Setup automatic API documentation
        # Configure documentation templates
        pass
```

### Third-Party Plugin Support

Future: Allow community-developed plugins:

```bash
# Install from plugin package
python install_nwave.py --plugin-package=/path/to/my-plugin.nwave

# Install from registry (future)
python install_nwave.py --plugin=community/slack-notifications
```

Plugin package structure:
```
my-plugin.nwave/
├── plugin.json          # Metadata
├── __init__.py
├── my_plugin.py         # Plugin implementation
├── requirements.txt     # Python dependencies
└── README.md
```

---

## Migration Path

### Phase 1: Current State (✅ COMPLETED)
- ✅ Monolithic installer (`install_nwave.py`)
- ✅ DES hook installer as separate script (`install_des_hooks.py`)
- ✅ Helper methods extracted to `install_utils.py`
- ✅ No plugin abstraction

### Phase 2: Plugin Infrastructure (❌ NOT STARTED)
- ❌ `InstallationPlugin` base class - TO BE IMPLEMENTED
- ❌ `PluginRegistry` with dependency resolution - TO BE IMPLEMENTED
- ❌ `InstallContext` for shared state - TO BE IMPLEMENTED
- ❌ Core plugins (agents, commands, templates, utilities) - TO BE IMPLEMENTED
- ❌ DES plugin - TO BE IMPLEMENTED
- ❌ Integration with `NWaveInstaller` - TO BE IMPLEMENTED

### Phase 3: Migration Complete (❌ NOT STARTED)
- ❌ All installation logic moved to plugins - TO BE IMPLEMENTED
- ❌ `NWaveInstaller` becomes thin orchestrator - TO BE IMPLEMENTED
- ❌ Selective installation supported (`--plugin=des`) - TO BE IMPLEMENTED
- ❌ Uninstallation supported (`--uninstall=des`) - TO BE IMPLEMENTED

### Phase 4: Enhanced Features (⏳ FUTURE)
- ⏳ Dynamic plugin discovery
- ⏳ Plugin versioning with update support
- ⏳ Plugin configuration UI
- ⏳ Plugin marketplace integration

---

## Testing Strategy

### Unit Testing

#### Testing Individual Plugins
```python
def test_des_plugin_install():
    """Test DES plugin installation in isolation."""

    # Create mock context
    context = InstallContext(
        claude_dir=Path("/tmp/test-claude"),
        scripts_dir=Path("/tmp/test-claude/scripts"),
        templates_dir=Path("/tmp/test-claude/templates"),
        logger=Mock(),
        dry_run=False,
    )

    # Create plugin
    plugin = DESPlugin()

    # Install
    result = plugin.install(context)

    # Verify
    assert result.success
    assert "DES installed successfully" in result.message
```

#### Testing Dependency Resolution
```python
def test_topological_sort():
    """Test dependency resolution with topological sort."""

    registry = PluginRegistry()

    # Register plugins with dependencies
    agent_plugin = AgentsPlugin()  # No dependencies
    template_plugin = TemplatesPlugin()  # No dependencies
    utility_plugin = UtilitiesPlugin()  # Depends on templates
    des_plugin = DESPlugin()  # Depends on templates, utilities

    registry.register(agent_plugin)
    registry.register(template_plugin)
    registry.register(utility_plugin)
    registry.register(des_plugin)

    # Get execution order
    order = registry.get_execution_order()

    # Verify order respects dependencies
    assert order.index("templates") < order.index("utilities")
    assert order.index("utilities") < order.index("des")
```

#### Testing Circular Dependency Detection
```python
def test_circular_dependency_detection():
    """Test that circular dependencies are detected."""

    registry = PluginRegistry()

    # Create plugins with circular dependency
    plugin_a = Mock(
        name="plugin_a",
        priority=10,
        get_dependencies=Mock(return_value=["plugin_b"])
    )
    plugin_b = Mock(
        name="plugin_b",
        priority=20,
        get_dependencies=Mock(return_value=["plugin_c"])
    )
    plugin_c = Mock(
        name="plugin_c",
        priority=30,
        get_dependencies=Mock(return_value=["plugin_a"])  # Circular!
    )

    registry.register(plugin_a)
    registry.register(plugin_b)
    registry.register(plugin_c)

    # Verify circular dependency detected
    with pytest.raises(ValueError, match="Circular dependency detected"):
        registry.get_execution_order()
```

### Integration Testing

#### Testing Full Installation Workflow
```python
def test_full_installation():
    """Test complete installation workflow."""

    # Setup test environment
    test_dir = Path("/tmp/test-nwave-install")
    test_dir.mkdir(exist_ok=True)

    # Create installer
    installer = NWaveInstaller(dry_run=False)
    installer.claude_config_dir = test_dir

    # Run installation
    success = installer.install_framework()

    # Verify all plugins installed
    assert success
    assert (test_dir / "agents" / "nw").exists()
    assert (test_dir / "commands" / "nw").exists()
    assert (test_dir / "templates").exists()
    assert (test_dir / "scripts").exists()
    assert (test_dir / "lib" / "python" / "des").exists()
```

#### Testing Selective Installation
```python
def test_selective_installation():
    """Test installing only specific plugins."""

    test_dir = Path("/tmp/test-nwave-selective")
    test_dir.mkdir(exist_ok=True)

    installer = NWaveInstaller(dry_run=False)
    installer.claude_config_dir = test_dir

    # Install only DES and its dependencies
    success = installer.install_selective(["des"])

    # Verify DES and dependencies installed
    assert success
    assert (test_dir / "templates").exists()  # Dependency
    assert (test_dir / "scripts").exists()  # Dependency (utilities)
    assert (test_dir / "lib" / "python" / "des").exists()  # DES itself

    # Verify non-dependencies NOT installed
    assert not (test_dir / "agents" / "nw").exists()
    assert not (test_dir / "commands" / "nw").exists()
```

### Acceptance Testing

#### User Story: Install nWave with DES
```gherkin
Feature: Install nWave framework with DES plugin

  Scenario: Complete installation
    Given I have Python 3.9+ installed
    And I have cloned the nWave repository
    When I run "python install_nwave.py"
    Then the installation should succeed
    And the DES module should be importable
    And DES scripts should be executable
    And DES templates should exist
```

#### User Story: Uninstall DES Plugin
```gherkin
Feature: Uninstall DES plugin

  Scenario: Uninstall DES without affecting core
    Given nWave and DES are installed
    When I run "python install_nwave.py --uninstall=des"
    Then the DES plugin should be uninstalled
    And DES files should be removed
    And core nWave should still function
    And agents and commands should remain installed
```

---

## References

### Related Documentation

1. **[DES-RESTRUCTURING-INDEX.md](./DES-RESTRUCTURING-INDEX.md)** - DES module architecture and hexagonal organization
2. **[DES-RESTRUCTURING-SUMMARY.md](./DES-RESTRUCTURING-SUMMARY.md)** - Executive summary of DES restructuring
3. **[des-hexagonal-structure-diagram.md](./des-hexagonal-structure-diagram.md)** - Visual DES architecture diagrams

### Source Code References

- `scripts/install/install_nwave.py` - Main installer orchestrator
- `scripts/install/install_des_hooks.py` - DES hook installation utility
- `scripts/install/plugins/base.py` - Plugin interface definitions
- `scripts/install/plugins/registry.py` - Plugin registry and dependency resolution
- `scripts/install/plugins/des_plugin.py` - DES plugin implementation
- `src/des/` - DES module source code (hexagonal architecture)

### External References

- **Kahn's Algorithm**: [Topological Sorting](https://en.wikipedia.org/wiki/Topological_sorting)
- **Hexagonal Architecture**: [Alistair Cockburn's Hexagonal Architecture](https://alistair.cockburn.us/hexagonal-architecture/)
- **Plugin Architecture**: [Martin Fowler on Plugin Pattern](https://martinfowler.com/articles/plugins.html)
- **Dependency Injection**: [Inversion of Control Containers](https://martinfowler.com/articles/injection.html)

---

## Document Maintenance

**Version History:**
- v1.0 (2026-02-03): Initial architecture design

**Next Review:** After Phase 3 completion (full migration to plugin system)

**Status:** ✅ Complete and Ready for Implementation

---

## Appendices

### Appendix A: Plugin Development Checklist

When creating a new plugin:

- [ ] Create plugin class inheriting from `InstallationPlugin`
- [ ] Define unique plugin name and priority
- [ ] Declare dependencies in `self.dependencies`
- [ ] Implement `install(context)` method
- [ ] Implement `verify(context)` method
- [ ] Handle `context.dry_run` flag appropriately
- [ ] Use `context.backup_manager` for safe overwrites
- [ ] Log installation progress using `context.logger`
- [ ] Return structured `PluginResult` with success/errors
- [ ] Write unit tests for plugin in isolation
- [ ] Write integration tests with dependencies
- [ ] Document plugin in README or plugin docstring

### Appendix B: Glossary

- **Plugin**: Self-contained module handling installation of specific nWave component
- **Plugin Registry**: Central registry managing plugin discovery, registration, and execution
- **Install Context**: Shared state object passed to all plugins during installation
- **Plugin Result**: Structured return value indicating success/failure of plugin operation
- **Topological Sort**: Algorithm for ordering plugins based on dependencies
- **Kahn's Algorithm**: Specific topological sort algorithm used for dependency resolution
- **Dependency Graph**: Directed acyclic graph (DAG) representing plugin dependencies
- **Circular Dependency**: Invalid dependency configuration where plugins depend on each other in a cycle
- **Dry-Run Mode**: Installation simulation mode that logs actions without modifying filesystem
- **Backup Manager**: Utility for creating backups before installation and restoring on failure

---

**End of Document**
