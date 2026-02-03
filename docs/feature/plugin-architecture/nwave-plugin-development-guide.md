# nWave Plugin Development Guide (FUTURE DESIGN)

**Version:** 1.0
**Date:** 2026-02-03
**For:** Developers creating new nWave plugins
**Status:** FUTURE DESIGN - NOT IMPLEMENTED

---

> **⚠️ IMPORTANTE: QUESTO È UN DOCUMENTO DI DESIGN, NON L'IMPLEMENTAZIONE ATTUALE**
>
> **Status Attuale (2026-02-03)**: Questo documento descrive come sviluppare plugin per un sistema **non ancora implementato**. Le classi base (`InstallationPlugin`, `PluginRegistry`, `InstallContext`) **non esistono** nel codice attuale.
>
> **Implementazione Attuale**: L'installer attuale è monolitico. Vedere `docs/architecture/nwave-installer-current-implementation.md` per la documentazione dell'implementazione corrente.
>
> **Per Implementatori**: Questo documento può essere usato come riferimento per implementare il sistema plugin descritto in `nwave-plugin-system-architecture.md`.

---

## Quick Start

### 5-Minute Plugin Creation

```python
# File: scripts/install/plugins/my_plugin.py

from scripts.install.plugins.base import (
    InstallationPlugin,
    InstallContext,
    PluginResult,
)

class MyPlugin(InstallationPlugin):
    """Plugin for installing MyComponent."""

    def __init__(self):
        super().__init__(name="my-plugin", priority=100)
        self.dependencies = []  # Add dependencies if needed

    def install(self, context: InstallContext) -> PluginResult:
        """Install my component."""
        try:
            context.logger.info("Installing MyPlugin...")

            if context.dry_run:
                context.logger.info("[DRY-RUN] Would install MyPlugin")
                return PluginResult(success=True, plugin_name=self.name)

            # Your installation logic here
            # Example: Copy files, create directories, etc.

            return PluginResult(
                success=True,
                plugin_name=self.name,
                message="MyPlugin installed successfully"
            )
        except Exception as e:
            return PluginResult(
                success=False,
                plugin_name=self.name,
                message=f"Installation failed: {e}",
                errors=[str(e)]
            )

    def verify(self, context: InstallContext) -> PluginResult:
        """Verify installation."""
        try:
            context.logger.info("Verifying MyPlugin...")

            # Your verification logic here
            # Example: Check files exist, test imports, etc.

            return PluginResult(
                success=True,
                plugin_name=self.name,
                message="Verification passed"
            )
        except Exception as e:
            return PluginResult(
                success=False,
                plugin_name=self.name,
                message=f"Verification failed: {e}",
                errors=[str(e)]
            )
```

---

## Plugin Interface Reference

### Required Methods

#### 1. `__init__(self)`

Initialize your plugin with name, priority, and dependencies.

```python
def __init__(self):
    super().__init__(
        name="my-plugin",      # Unique identifier (lowercase, hyphenated)
        priority=100           # Execution order (lower = earlier)
    )
    self.dependencies = [      # List of plugin names this depends on
        "templates",
        "utilities"
    ]
```

**Priority Guidelines:**
- `10-40`: Core framework plugins (agents, commands, templates, utilities)
- `50-80`: Extension plugins (DES, mutation testing, IDE integrations)
- `90+`: Optional/advanced plugins (docs generators, analytics)

#### 2. `install(self, context: InstallContext) -> PluginResult`

Perform installation of your plugin's components.

```python
def install(self, context: InstallContext) -> PluginResult:
    """Install plugin components.

    Args:
        context: Shared installation context with utilities

    Returns:
        PluginResult indicating success or failure
    """
    try:
        # 1. Check dry-run mode
        if context.dry_run:
            context.logger.info("[DRY-RUN] Would install...")
            return PluginResult(success=True, plugin_name=self.name)

        # 2. Create directories if needed
        target_dir = context.claude_dir / "my-plugin"
        target_dir.mkdir(parents=True, exist_ok=True)

        # 3. Backup existing files (if overwriting)
        if context.backup_manager and target_dir.exists():
            context.backup_manager.backup_directory(target_dir)

        # 4. Copy/install files
        # ... your installation logic ...

        # 5. Log progress
        context.logger.info(f"Installed to {target_dir}")

        # 6. Return success
        return PluginResult(
            success=True,
            plugin_name=self.name,
            message="Installation complete",
            installed_files=[target_dir]
        )

    except Exception as e:
        # Always return PluginResult, even on error
        return PluginResult(
            success=False,
            plugin_name=self.name,
            message=f"Installation failed: {e}",
            errors=[str(e)]
        )
```

#### 3. `verify(self, context: InstallContext) -> PluginResult`

Verify installation succeeded.

```python
def verify(self, context: InstallContext) -> PluginResult:
    """Verify plugin installation.

    Args:
        context: Shared installation context

    Returns:
        PluginResult indicating verification success or failure
    """
    errors = []

    # 1. Check files exist
    required_files = [
        context.scripts_dir / "my_script.py",
        context.templates_dir / "my_template.yaml",
    ]

    for file_path in required_files:
        if not file_path.exists():
            errors.append(f"Missing file: {file_path}")

    # 2. Test functionality (optional but recommended)
    try:
        import subprocess
        result = subprocess.run(
            ["python3", "-c", "import my_module"],
            capture_output=True,
            timeout=5
        )
        if result.returncode != 0:
            errors.append(f"Import failed: {result.stderr}")
    except Exception as e:
        errors.append(f"Verification error: {e}")

    # 3. Return result
    if errors:
        return PluginResult(
            success=False,
            plugin_name=self.name,
            message="Verification failed",
            errors=errors
        )

    return PluginResult(
        success=True,
        plugin_name=self.name,
        message="Verification passed"
    )
```

---

## InstallContext Reference

### Available Properties

```python
@dataclass
class InstallContext:
    """Shared context passed to all plugins."""

    # Directory paths
    claude_dir: Path              # ~/.claude
    scripts_dir: Path             # ~/.claude/scripts
    templates_dir: Path           # ~/.claude/templates

    # Utilities
    logger: Any                   # Logger instance
    backup_manager: Any           # BackupManager for safe overwrites
    rich_logger: Any              # RichLogger for styled output

    # Source locations
    project_root: Path = None     # nWave project root
    framework_source: Path = None # dist/ide directory
    dist_dir: Path = None         # Built distribution directory

    # Flags
    dry_run: bool = False         # Dry-run mode (don't modify files)

    # Inter-plugin communication
    metadata: Dict[str, Any]      # Shared data between plugins
```

### Usage Examples

#### Logging
```python
# Simple logging
context.logger.info("Installing plugin...")
context.logger.warn("Configuration not found, using defaults")
context.logger.error("Installation failed")

# Rich styled output
if context.rich_logger:
    context.rich_logger.progress_spinner("Installing files...")
    context.rich_logger.table(
        headers=["File", "Status"],
        rows=[["file1.py", "✅"], ["file2.py", "✅"]],
        title="Installation Summary"
    )
```

#### Backup Management
```python
# Backup before overwrite
target_dir = context.claude_dir / "my-plugin"

if context.backup_manager and target_dir.exists():
    context.logger.info(f"Backing up {target_dir}")
    context.backup_manager.backup_directory(target_dir)

# Now safe to overwrite
shutil.rmtree(target_dir)
shutil.copytree(source_dir, target_dir)
```

#### Dry-Run Mode
```python
if context.dry_run:
    context.logger.info(f"[DRY-RUN] Would copy {source} → {target}")
    context.logger.info(f"[DRY-RUN] Would create directory {target_dir}")
    return PluginResult(success=True, plugin_name=self.name)

# Actual installation
shutil.copy2(source, target)
```

#### Inter-Plugin Communication
```python
# Plugin A saves data
context.metadata["plugin-a"] = {
    "version": "1.0.0",
    "installed_files": ["/path/to/file"]
}

# Plugin B reads data
plugin_a_data = context.metadata.get("plugin-a", {})
if plugin_a_data:
    version = plugin_a_data["version"]
    context.logger.info(f"Plugin A version: {version}")
```

---

## Common Patterns

### Pattern 1: Copy Files from Source

```python
def install(self, context: InstallContext) -> PluginResult:
    """Copy files from source to target."""
    import shutil

    # Determine source location
    if context.framework_source:
        source_dir = context.framework_source / "my-plugin"
    else:
        source_dir = context.project_root / "nWave" / "my-plugin"

    if not source_dir.exists():
        return PluginResult(
            success=False,
            plugin_name=self.name,
            message=f"Source not found: {source_dir}"
        )

    # Target location
    target_dir = context.claude_dir / "my-plugin"

    # Backup if exists
    if context.backup_manager and target_dir.exists():
        context.backup_manager.backup_directory(target_dir)

    # Copy files
    if not context.dry_run:
        if target_dir.exists():
            shutil.rmtree(target_dir)
        shutil.copytree(source_dir, target_dir)

    return PluginResult(
        success=True,
        plugin_name=self.name,
        message=f"Copied to {target_dir}"
    )
```

### Pattern 2: Install Python Module

```python
def _install_module(self, context: InstallContext) -> PluginResult:
    """Install Python module to ~/.claude/lib/python/."""
    import shutil

    source_dir = context.project_root / "src" / "my_module"
    lib_python_dir = context.claude_dir / "lib" / "python"
    target_dir = lib_python_dir / "my_module"

    lib_python_dir.mkdir(parents=True, exist_ok=True)

    if not context.dry_run:
        if target_dir.exists():
            shutil.rmtree(target_dir)
        shutil.copytree(source_dir, target_dir)

    return PluginResult(
        success=True,
        plugin_name=self.name,
        message=f"Module installed to {target_dir}"
    )
```

### Pattern 3: Install Scripts

```python
def _install_scripts(self, context: InstallContext) -> PluginResult:
    """Install utility scripts."""
    import shutil

    scripts_to_install = [
        "my_script1.py",
        "my_script2.py",
    ]

    source_dir = context.project_root / "scripts" / "my-plugin"
    target_dir = context.scripts_dir

    installed = []
    for script_name in scripts_to_install:
        source = source_dir / script_name
        target = target_dir / script_name

        if source.exists():
            if not context.dry_run:
                shutil.copy2(source, target)
                target.chmod(0o755)  # Make executable
            installed.append(script_name)

    return PluginResult(
        success=True,
        plugin_name=self.name,
        message=f"Installed {len(installed)} scripts"
    )
```

### Pattern 4: Install Templates

```python
def _install_templates(self, context: InstallContext) -> PluginResult:
    """Install template files."""
    import shutil

    templates = [
        "template1.yaml",
        "template2.json",
    ]

    source_dir = context.project_root / "nWave" / "templates"
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
        plugin_name=self.name,
        message=f"Installed {len(installed)} templates"
    )
```

### Pattern 5: Multi-Phase Installation

```python
def install(self, context: InstallContext) -> PluginResult:
    """Multi-phase installation."""

    # Phase 1: Install module
    result = self._install_module(context)
    if not result.success:
        return result

    # Phase 2: Install scripts
    result = self._install_scripts(context)
    if not result.success:
        return result

    # Phase 3: Install templates
    result = self._install_templates(context)
    if not result.success:
        return result

    # All phases successful
    return PluginResult(
        success=True,
        plugin_name=self.name,
        message="All installation phases complete"
    )
```

---

## Verification Patterns

### Pattern 1: File Existence Check

```python
def verify(self, context: InstallContext) -> PluginResult:
    """Verify files exist."""
    errors = []

    expected_files = [
        context.scripts_dir / "my_script.py",
        context.templates_dir / "my_template.yaml",
    ]

    for file_path in expected_files:
        if not file_path.exists():
            errors.append(f"Missing file: {file_path}")

    if errors:
        return PluginResult(
            success=False,
            plugin_name=self.name,
            errors=errors
        )

    return PluginResult(success=True, plugin_name=self.name)
```

### Pattern 2: Module Import Test

```python
def verify(self, context: InstallContext) -> PluginResult:
    """Verify module can be imported."""
    import subprocess

    lib_python = context.claude_dir / "lib" / "python"

    try:
        result = subprocess.run(
            [
                "python3",
                "-c",
                f'import sys; sys.path.insert(0, "{lib_python}"); '
                f'import my_module'
            ],
            capture_output=True,
            text=True,
            timeout=5
        )

        if result.returncode != 0:
            return PluginResult(
                success=False,
                plugin_name=self.name,
                message=f"Import failed: {result.stderr}"
            )

        return PluginResult(success=True, plugin_name=self.name)

    except Exception as e:
        return PluginResult(
            success=False,
            plugin_name=self.name,
            message=f"Verification failed: {e}"
        )
```

### Pattern 3: Functional Test

```python
def verify(self, context: InstallContext) -> PluginResult:
    """Verify functionality works."""
    import subprocess

    script_path = context.scripts_dir / "my_script.py"

    try:
        # Run script and check output
        result = subprocess.run(
            ["python3", str(script_path), "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )

        if result.returncode != 0:
            return PluginResult(
                success=False,
                plugin_name=self.name,
                message=f"Script failed: {result.stderr}"
            )

        # Check output format
        if not result.stdout.startswith("1.0"):
            return PluginResult(
                success=False,
                plugin_name=self.name,
                message=f"Unexpected version: {result.stdout}"
            )

        return PluginResult(success=True, plugin_name=self.name)

    except Exception as e:
        return PluginResult(
            success=False,
            plugin_name=self.name,
            message=f"Functional test failed: {e}"
        )
```

---

## Testing Your Plugin

### Unit Test Template

```python
# File: tests/install/plugins/test_my_plugin.py

import pytest
from pathlib import Path
from unittest.mock import Mock

from scripts.install.plugins.my_plugin import MyPlugin
from scripts.install.plugins.base import InstallContext


def test_my_plugin_install():
    """Test plugin installation."""
    # Create mock context
    context = InstallContext(
        claude_dir=Path("/tmp/test-claude"),
        scripts_dir=Path("/tmp/test-claude/scripts"),
        templates_dir=Path("/tmp/test-claude/templates"),
        logger=Mock(),
        dry_run=True,  # Use dry-run for unit tests
    )

    # Create plugin
    plugin = MyPlugin()

    # Install
    result = plugin.install(context)

    # Verify
    assert result.success
    assert result.plugin_name == "my-plugin"
    assert "installed" in result.message.lower()


def test_my_plugin_verify():
    """Test plugin verification."""
    # Create mock context with files
    context = InstallContext(
        claude_dir=Path("/tmp/test-claude"),
        scripts_dir=Path("/tmp/test-claude/scripts"),
        templates_dir=Path("/tmp/test-claude/templates"),
        logger=Mock(),
    )

    # Create expected files
    context.scripts_dir.mkdir(parents=True, exist_ok=True)
    (context.scripts_dir / "my_script.py").touch()

    # Create plugin
    plugin = MyPlugin()

    # Verify
    result = plugin.verify(context)

    # Check result
    assert result.success
```

### Integration Test Template

```python
# File: tests/install/test_my_plugin_integration.py

import pytest
from pathlib import Path
from scripts.install.install_nwave import NWaveInstaller


def test_my_plugin_integration():
    """Test plugin integrates with installer."""
    test_dir = Path("/tmp/test-nwave-my-plugin")
    test_dir.mkdir(exist_ok=True)

    # Create installer
    installer = NWaveInstaller(dry_run=False)
    installer.claude_config_dir = test_dir

    # Install only my plugin (and dependencies)
    success = installer.install_selective(["my-plugin"])

    # Verify
    assert success
    assert (test_dir / "my-plugin").exists()
```

---

## Registration

### Add Plugin to Installer

Edit `scripts/install/install_nwave.py`:

```python
def _discover_plugins(self) -> PluginRegistry:
    """Discover and register all available plugins."""
    registry = PluginRegistry()

    # Import plugin modules
    from scripts.install.plugins.agents_plugin import AgentsPlugin
    from scripts.install.plugins.commands_plugin import CommandsPlugin
    from scripts.install.plugins.templates_plugin import TemplatesPlugin
    from scripts.install.plugins.utilities_plugin import UtilitiesPlugin
    from scripts.install.plugins.des_plugin import DESPlugin
    from scripts.install.plugins.my_plugin import MyPlugin  # ADD THIS

    # Register plugins
    registry.register(AgentsPlugin())
    registry.register(CommandsPlugin())
    registry.register(TemplatesPlugin())
    registry.register(UtilitiesPlugin())
    registry.register(DESPlugin())
    registry.register(MyPlugin())  # ADD THIS

    return registry
```

---

## Dependency Management

### Declaring Dependencies

```python
class MyPlugin(InstallationPlugin):
    def __init__(self):
        super().__init__(name="my-plugin", priority=100)

        # Declare dependencies (list of plugin names)
        self.dependencies = [
            "templates",    # Needs templates directory
            "utilities"     # Needs utilities scripts
        ]
```

### Dependency Resolution

The `PluginRegistry` automatically:
1. Detects your dependencies
2. Orders plugins using topological sort
3. Ensures dependencies install before your plugin
4. Detects circular dependencies (fails fast)

**Example:**
```
If:
  templates (priority 30, no deps)
  utilities (priority 40, depends on templates)
  my-plugin (priority 100, depends on templates, utilities)

Then execution order:
  1. templates  (no deps)
  2. utilities  (templates satisfied)
  3. my-plugin  (templates and utilities satisfied)
```

---

## Best Practices

### 1. Always Handle Dry-Run Mode

```python
if context.dry_run:
    context.logger.info(f"[DRY-RUN] Would install to {target_dir}")
    return PluginResult(success=True, plugin_name=self.name)

# Actual installation only if not dry-run
shutil.copytree(source, target)
```

### 2. Use Backup Manager for Safety

```python
if context.backup_manager and target_dir.exists():
    context.backup_manager.backup_directory(target_dir)

# Now safe to overwrite
```

### 3. Return Structured Results

```python
# ✅ GOOD: Always return PluginResult
return PluginResult(
    success=True,
    plugin_name=self.name,
    message="Installation complete",
    installed_files=[target_dir]
)

# ❌ BAD: Don't return bool or None
return True  # Wrong!
```

### 4. Handle Exceptions Gracefully

```python
try:
    # Installation logic
    pass
except Exception as e:
    # Always return PluginResult, even on error
    return PluginResult(
        success=False,
        plugin_name=self.name,
        message=f"Installation failed: {e}",
        errors=[str(e)]
    )
```

### 5. Verify Installation Thoroughly

```python
def verify(self, context: InstallContext) -> PluginResult:
    """Verify with multiple checks."""
    errors = []

    # Check 1: Files exist
    if not file_path.exists():
        errors.append(f"Missing: {file_path}")

    # Check 2: Module imports
    try:
        import my_module
    except ImportError as e:
        errors.append(f"Import failed: {e}")

    # Check 3: Functional test
    try:
        result = subprocess.run(["my_script", "--test"])
        if result.returncode != 0:
            errors.append("Functional test failed")
    except Exception as e:
        errors.append(f"Test error: {e}")

    # Return aggregated result
    if errors:
        return PluginResult(
            success=False,
            plugin_name=self.name,
            errors=errors
        )

    return PluginResult(success=True, plugin_name=self.name)
```

### 6. Use Clear Priority Values

```python
# Core plugins: 10-40
AgentsPlugin(priority=10)
CommandsPlugin(priority=20)
TemplatesPlugin(priority=30)
UtilitiesPlugin(priority=40)

# Extension plugins: 50-80
DESPlugin(priority=50)
MutationTestingPlugin(priority=60)
VSCodePlugin(priority=70)

# Optional/advanced plugins: 90+
DocsGeneratorPlugin(priority=90)
AnalyticsPlugin(priority=100)
```

### 7. Document Your Plugin

```python
class MyPlugin(InstallationPlugin):
    """Plugin for installing MyComponent.

    MyComponent provides X functionality for nWave projects.

    Installation includes:
    - Python module → ~/.claude/lib/python/my_module/
    - Utility scripts → ~/.claude/scripts/
    - Templates → ~/.claude/templates/

    Dependencies:
    - templates: Required for template directory structure
    - utilities: Required for script infrastructure

    Example usage:
        python install_nwave.py --plugin=my-plugin
    """
```

---

## Troubleshooting

### Common Issues

#### Issue 1: Plugin Not Found

**Error:** `ValueError: Plugin 'my-plugin' depends on missing plugin 'xyz'`

**Solution:** Ensure dependency plugin is registered before your plugin:
```python
registry.register(XYZPlugin())  # Dependency first
registry.register(MyPlugin())   # Then your plugin
```

#### Issue 2: Circular Dependency

**Error:** `ValueError: Circular dependency detected in plugins`

**Solution:** Review your dependencies. Example circular dependency:
```python
PluginA depends on PluginB
PluginB depends on PluginC
PluginC depends on PluginA  # ← Circular!
```

Fix by removing circular dependency or refactoring.

#### Issue 3: Files Not Found During Verification

**Error:** `Missing file: /path/to/file`

**Solution:** Ensure `install()` actually copies files:
```python
if not context.dry_run:  # Check this flag
    shutil.copy2(source, target)
```

#### Issue 4: Import Test Fails

**Error:** `Import failed: ModuleNotFoundError: No module named 'my_module'`

**Solution:** Check module installed to correct location:
```python
lib_python = context.claude_dir / "lib" / "python"
target = lib_python / "my_module"  # Correct path

# Verify in subprocess
result = subprocess.run([
    "python3", "-c",
    f'import sys; sys.path.insert(0, "{lib_python}"); import my_module'
])
```

---

## Examples

See these reference implementations:
- **DES Plugin**: `scripts/install/plugins/des_plugin.py`
- **Agents Plugin**: `scripts/install/plugins/agents_plugin.py`
- **Templates Plugin**: `scripts/install/plugins/templates_plugin.py`

---

## Summary

> **NOTE**: Questa checklist descrive funzionalità FUTURE. Le classi base del plugin system, la directory `plugins/` e i comandi `--plugin=` **non esistono** ancora nell'implementazione attuale.

### Plugin Creation Checklist

- [ ] Create plugin file: `scripts/install/plugins/my_plugin.py`
- [ ] Inherit from `InstallationPlugin`
- [ ] Define `__init__` with name, priority, dependencies
- [ ] Implement `install(context)` method
- [ ] Implement `verify(context)` method
- [ ] Handle `context.dry_run` flag
- [ ] Use `context.backup_manager` for safety
- [ ] Return `PluginResult` from both methods
- [ ] Write unit tests: `tests/install/plugins/test_my_plugin.py`
- [ ] Write integration test: `tests/install/test_my_plugin_integration.py`
- [ ] Register plugin in `install_nwave.py`
- [ ] Test installation: `python install_nwave.py --plugin=my-plugin`
- [ ] Test verification passes
- [ ] Document plugin in README or docstring

---

**Next Steps:**
1. Review [nwave-plugin-system-architecture.md](./nwave-plugin-system-architecture.md) for complete architecture
2. Review [nwave-plugin-system-summary.md](./nwave-plugin-system-summary.md) for quick overview
3. Study existing plugins in `scripts/install/plugins/`
4. Create your plugin using this guide
5. Submit for review

---

**Happy Plugin Development!** 🚀
