# Plugin System Walking Skeleton

**Feature**: Plugin Architecture for nWave Installer
**Purpose**: Minimal E2E path proving plugin infrastructure works
**Date**: 2026-02-03
**Status**: Ready for Implementation (FIRST TEST TO IMPLEMENT)

---

## Executive Summary

### What is the Walking Skeleton?

**The absolute minimum path that proves the plugin system works end-to-end**: Installing ONE simple wrapper plugin (AgentsPlugin) through the complete plugin infrastructure from discovery → registration → installation → verification.

### Why This Specific Path?

This path was chosen as the minimum viable slice because it:
- **Touches all architectural layers**: Plugin infrastructure (base.py, registry.py) → Plugin implementation (agents_plugin.py) → Installation orchestration (PluginRegistry.install_all()) → Verification
- **Proves core architecture**: Demonstrates that plugin discovery, topological sorting, and installation orchestration work correctly
- **Simplest plugin**: AgentsPlugin is a wrapper around existing `_install_agents()` logic - minimal complexity, maximum architectural validation
- **Observable outcome**: Agent files installed at `~/.claude/agents/nw/` - clear, verifiable success criterion

### What This Proves About the Architecture

✅ **Plugin infrastructure operational**
- `InstallationPlugin` base class works
- `PluginRegistry` discovers and registers plugins
- Topological sort (Kahn's algorithm) orders plugins correctly
- `InstallContext` dependency injection works

✅ **End-to-end installation flow**
- Plugin discovered by registry
- Plugin `install()` method executes
- Production service integration (calls actual installation logic)
- Installation produces observable filesystem changes

✅ **Verification framework functional**
- Plugin `verify()` method executes
- Verification passes when installation succeeded
- Verification fails when installation incomplete

---

## Walking Skeleton Path

### Preconditions

**System State Before Test**:
- ✅ Plugin infrastructure exists (Phase 1 complete):
  - `scripts/install/plugins/base.py` with `InstallationPlugin`, `InstallContext`, `PluginResult`
  - `scripts/install/plugins/registry.py` with `PluginRegistry` and topological sort
  - Unit tests passing (10/10 tests green)

- ✅ AgentsPlugin implemented:
  - `scripts/install/plugins/agents_plugin.py` created
  - Implements `install()` and `verify()` methods
  - Wraps existing `_install_agents()` logic (no reimplementation)

- ⚠️ Installer NOT YET modified:
  - `install_framework()` still calls `_install_agents()` directly
  - Plugin orchestration not active yet (Phase 3)
  - This is expected - walking skeleton tests plugin infrastructure independently

**Test Environment**:
- Fresh installation target directory (e.g., `tmp/test-install/`)
- No existing `~/.claude/agents/nw/` directory
- Agent source files available at `nWave/agents/nw/` (verified to exist)

### The Minimal Path (Step by Step)

#### Step 1: Plugin Discovery
**Entry Condition**: AgentsPlugin class exists with correct interface
**Action**: PluginRegistry discovers AgentsPlugin
**Exit Condition**: AgentsPlugin registered in PluginRegistry

**Components Touched**:
- `PluginRegistry` (plugin discovery mechanism)
- `AgentsPlugin.__init__()` (plugin metadata: name="agents", priority=10)

**Verification**:
```python
registry = PluginRegistry()
plugins = registry.get_registered_plugins()
assert "agents" in [p.name for p in plugins]
```

---

#### Step 2: Dependency Resolution
**Entry Condition**: AgentsPlugin registered
**Action**: PluginRegistry resolves plugin dependencies (AgentsPlugin has no dependencies)
**Exit Condition**: Installation order determined (AgentsPlugin ready for installation)

**Components Touched**:
- `PluginRegistry._topological_sort()` (Kahn's algorithm)
- AgentsPlugin dependency list (empty: `[]`)

**Verification**:
```python
install_order = registry.get_installation_order()
assert "agents" in install_order
```

---

#### Step 3: Context Creation
**Entry Condition**: Installation order determined
**Action**: Create `InstallContext` with required utilities
**Exit Condition**: InstallContext populated with all required fields

**Components Touched**:
- `InstallContext` dataclass
- Injected utilities: `logger`, `claude_dir`, `backup_manager`, etc.

**Verification**:
```python
context = InstallContext(
    claude_dir=Path("/tmp/test-install/.claude"),
    scripts_dir=Path("scripts/install"),
    logger=logging.getLogger(),
    # ... other required fields
)
assert context.claude_dir.exists()
```

---

#### Step 4: Plugin Installation
**Entry Condition**: InstallContext created, AgentsPlugin ready
**Action**: Call `AgentsPlugin.install(context)`
**Exit Condition**: Agent files copied to `context.claude_dir/agents/nw/`

**Components Touched**:
- `AgentsPlugin.install()`
- Existing `_install_agents()` logic (via wrapper pattern)
- Filesystem operations (copy agent files)

**Verification**:
```python
result = agents_plugin.install(context)
assert result.success is True
assert (context.claude_dir / "agents" / "nw").exists()
assert len(list((context.claude_dir / "agents" / "nw").glob("*.md"))) >= 10
```

---

#### Step 5: Plugin Verification
**Entry Condition**: Installation completed (result.success == True)
**Action**: Call `AgentsPlugin.verify(context)`
**Exit Condition**: Verification confirms agent files installed correctly

**Components Touched**:
- `AgentsPlugin.verify()`
- File existence checks
- Agent count validation

**Verification**:
```python
verify_result = agents_plugin.verify(context)
assert verify_result.success is True
assert "Agents verification passed" in verify_result.message
```

---

### Postconditions

**System State After Walking Skeleton Completes**:
- ✅ Agent files exist at `{test_dir}/.claude/agents/nw/`
- ✅ At least 10 agent `.md` files installed
- ✅ `PluginResult` returned with `success=True`
- ✅ Verification passed

**What Has Been Proven**:
- Plugin infrastructure works end-to-end (discovery → installation → verification)
- Dependency injection via `InstallContext` functional
- Plugin wrapper pattern successfully calls existing installer logic
- Topological sort correctly handles single plugin (trivial case)
- Observable filesystem changes confirm installation succeeded

---

## Walking Skeleton Acceptance Test

```gherkin
Feature: Plugin System Infrastructure Validation
  As a developer
  I want to install a single plugin through the plugin infrastructure
  So that I can verify the plugin system works end-to-end before adding complexity

Scenario: Install AgentsPlugin successfully via PluginRegistry
  Given plugin infrastructure exists (base.py, registry.py)
  And AgentsPlugin is implemented with install() and verify() methods
  And a clean test installation directory exists
  And agent source files are available at nWave/agents/nw/

  When I create a PluginRegistry instance
  And I register AgentsPlugin with the registry
  And I create an InstallContext with test directory path
  And I call registry.install_plugin("agents", context)

  Then AgentsPlugin.install() executes successfully
  And agent files are copied to {test_dir}/.claude/agents/nw/
  And at least 10 agent .md files exist in the target directory
  And AgentsPlugin.verify() returns success
  And the installation is functional (agents directory accessible)
```

---

## Components Touched

This walking skeleton validates the following architectural components:

### Plugin Infrastructure (Phase 1 - Complete)
- [x] `InstallationPlugin` base class (interface contract)
- [x] `InstallContext` dataclass (dependency injection)
- [x] `PluginResult` dataclass (result communication)
- [x] `PluginRegistry` (plugin discovery and orchestration)
- [x] Topological sort algorithm (Kahn's implementation)

### Plugin Implementation (Phase 2 - Walking Skeleton Subset)
- [x] `AgentsPlugin` class (wrapper around existing logic)
- [ ] CommandsPlugin (not needed for walking skeleton)
- [ ] TemplatesPlugin (not needed for walking skeleton)
- [ ] UtilitiesPlugin (not needed for walking skeleton)

### Installation Orchestration
- [x] Plugin registration (`registry.register()`)
- [x] Installation order determination (`get_installation_order()`)
- [x] Context creation (`InstallContext(...)`)
- [x] Plugin execution (`plugin.install(context)`)
- [x] Verification (`plugin.verify(context)`)

### Integration Points
- [x] Existing installer logic (`_install_agents()` via wrapper)
- [x] Filesystem operations (file copy, directory creation)
- [ ] BackupManager integration (nice-to-have, not critical for walking skeleton)
- [ ] InstallationVerifier integration (nice-to-have, not critical for walking skeleton)

---

## What This Proves

### ✅ Proves (Architectural Validation)

1. **Plugin Interface Contract Works**
   - `InstallationPlugin` base class provides correct interface
   - `install()` and `verify()` methods callable with correct signatures
   - `PluginResult` return type communicates success/failure

2. **Dependency Injection Functional**
   - `InstallContext` successfully passes utilities to plugin
   - Plugin accesses `context.claude_dir`, `context.logger`, etc.
   - No circular dependencies (plugin doesn't need installer class)

3. **Plugin Discovery Operational**
   - `PluginRegistry` discovers AgentsPlugin
   - Plugin metadata (name, priority) accessible
   - Registration mechanism works

4. **Topological Sort Correct** (Trivial Case)
   - Single plugin with no dependencies sorted correctly
   - Kahn's algorithm executes without errors
   - Installation order deterministic

5. **Wrapper Pattern Viable**
   - AgentsPlugin successfully delegates to existing `_install_agents()` logic
   - No need to reimplement installation logic
   - Backward compatibility maintained

6. **End-to-End Integration**
   - Complete flow works: discovery → registration → installation → verification
   - Observable outcome (files installed) confirms success
   - No integration breakage between components

### ❌ Does NOT Prove (Out of Scope)

1. **Multiple Plugin Orchestration**
   - Walking skeleton uses ONE plugin only
   - Does not test dependency resolution between multiple plugins
   - Complex topological sort scenarios not covered

2. **Error Handling Robustness**
   - Happy path only (no error injection)
   - Circular dependency detection not tested (requires ≥2 plugins)
   - Installation failure scenarios not covered

3. **Complete Plugin Set**
   - Only AgentsPlugin tested
   - CommandsPlugin, TemplatesPlugin, UtilitiesPlugin, DESPlugin not involved
   - Inter-plugin dependencies not validated

4. **Installer Switchover**
   - Walking skeleton tests plugin infrastructure independently
   - `install_framework()` NOT modified to use PluginRegistry (Phase 3)
   - Full orchestration integration not yet proven

5. **Production-Like Scenarios**
   - Test uses clean directory, not realistic upgrade scenario
   - BackupManager not exercised
   - Rollback mechanisms not tested

6. **DES Plugin Extensibility**
   - DES plugin not included (Phase 4)
   - External plugin addition not demonstrated
   - Extensibility claim not yet proven

---

## Next Steps After Walking Skeleton

Once this minimal path works (all tests green), expand in this order:

### Immediate Expansion (Phase 2 Completion)
1. **Add CommandsPlugin**
   - Second wrapper plugin (priority=20)
   - Tests dependency resolution with 2 plugins
   - Validates topological sort with multiple nodes

2. **Add TemplatesPlugin**
   - Third wrapper plugin (priority=30)
   - Tests 3-plugin orchestration
   - Validates installation order correctness

3. **Add UtilitiesPlugin**
   - Fourth wrapper plugin (priority=40)
   - Completes wrapper plugin set
   - Tests realistic plugin count (4 plugins)

### Integration Expansion (Phase 3)
4. **Integrate with Installer**
   - Modify `install_framework()` to call `PluginRegistry.install_all()`
   - Test that plugin-based installation produces identical results to pre-plugin baseline
   - Create integration checkpoint test suite (file tree comparison)

5. **Add Error Scenarios**
   - Test plugin installation failure handling
   - Test verification failure behavior
   - Test circular dependency detection (requires malformed plugins)

### Extensibility Validation (Phase 4)
6. **Add DESPlugin**
   - External plugin not part of installer core
   - Proves extensibility claim ("add new features without modifying installer")
   - Validates DES-specific dependencies (templates, utilities)

### Robustness Hardening (Phase 5)
7. **Add Adversarial Tests**
   - Missing dependencies (plugin depends on non-existent plugin)
   - Circular dependencies (A depends on B, B depends on A)
   - Installation failures (filesystem errors, permission issues)
   - Verification failures (partial installation, corrupted files)

---

## Implementation Priority

**CRITICAL**: This walking skeleton MUST be implemented FIRST, before ANY other acceptance tests.

**Rationale**:
- Proves architecture works at foundational level
- Unblocks confidence in plugin infrastructure
- Provides template for expanding to other plugins
- Catches integration issues early (before complex scenarios)

**Timeline Estimate**: 2-4 hours
- 1 hour: Implement walking skeleton test (Gherkin + step definitions)
- 1 hour: Implement AgentsPlugin wrapper (if not complete)
- 1 hour: Debug integration issues
- 1 hour: Document learnings and expand test suite

**Success Criterion**: Walking skeleton test passes (green), proving plugin infrastructure works end-to-end for ONE plugin.

---

## Walking Skeleton Test Implementation Guide

### Test Structure

```python
# tests/acceptance/test_plugin_walking_skeleton.py

import pytest
from pathlib import Path
from scripts.install.plugins.registry import PluginRegistry
from scripts.install.plugins.agents_plugin import AgentsPlugin
from scripts.install.plugins.base import InstallContext

@pytest.fixture
def clean_test_directory(tmp_path):
    """Provide clean test installation directory."""
    test_dir = tmp_path / ".claude"
    test_dir.mkdir(parents=True, exist_ok=True)
    return test_dir

@pytest.fixture
def install_context(clean_test_directory):
    """Create InstallContext for testing."""
    return InstallContext(
        claude_dir=clean_test_directory,
        scripts_dir=Path("scripts/install"),
        templates_dir=Path("nWave/templates"),
        logger=logging.getLogger("test"),
        dry_run=False,
    )

def test_walking_skeleton_install_agents_plugin(install_context):
    """
    Walking Skeleton: Install single plugin (AgentsPlugin) through complete infrastructure.

    This is the MINIMUM viable test proving plugin system works end-to-end.
    """
    # GIVEN: Plugin infrastructure exists
    registry = PluginRegistry()
    agents_plugin = AgentsPlugin()

    # WHEN: Register and install single plugin
    registry.register(agents_plugin)
    result = registry.install_plugin("agents", install_context)

    # THEN: Installation succeeds
    assert result.success, f"Installation failed: {result.message}"

    # THEN: Agent files exist
    agents_dir = install_context.claude_dir / "agents" / "nw"
    assert agents_dir.exists(), "Agents directory not created"

    agent_files = list(agents_dir.glob("*.md"))
    assert len(agent_files) >= 10, f"Expected ≥10 agents, found {len(agent_files)}"

    # THEN: Verification passes
    verify_result = agents_plugin.verify(install_context)
    assert verify_result.success, f"Verification failed: {verify_result.message}"
```

### Expected Test Output

```
tests/acceptance/test_plugin_walking_skeleton.py::test_walking_skeleton_install_agents_plugin PASSED [100%]

======================== 1 passed in 0.25s ========================
```

**If this test passes**: Plugin infrastructure proven, expand to Phase 2 (add more plugins)
**If this test fails**: Fix plugin infrastructure before proceeding (architecture broken)

---

## Conclusion

This walking skeleton represents the **steel thread** through the entire plugin system architecture. It touches every major component (base classes, registry, plugin implementation, installation, verification) with the **absolute minimum complexity** (one plugin, no dependencies, wrapper pattern).

**Once this passes, we know**:
- The plugin architecture is sound
- Dependency injection works
- Plugin orchestration functions
- Observable outcomes are achievable

**Then we can confidently expand** to multiple plugins (Phase 2), installer integration (Phase 3), DES plugin (Phase 4), and comprehensive testing (Phase 5).

**This is NOT the full DISTILL wave** - it's the **FIRST thing to implement** that proves the architecture works before creating comprehensive acceptance tests.

---

**Document Status**: COMPLETE - Ready for implementation
**Next Step**: Implement walking skeleton test FIRST, then expand to full acceptance test suite
**Author**: Quinn (Acceptance Designer)
**Date**: 2026-02-03
