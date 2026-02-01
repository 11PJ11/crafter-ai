# Piano: Architettura Plugin Modulare per nWave Installation System

## Obiettivo

Trasformare il sistema di installazione nWave da approccio hardcoded a **architettura modulare basata su plugin**, permettendo di aggiungere nuove funzionalità (come DES) senza modificare il codice dell'installer.

## Contesto

**Problema Attuale**:
`install_nwave.py` ha metodi hardcoded per ogni componente:
```python
def install_framework(self):
    self._install_agents()       # Hardcoded
    self._install_commands()     # Hardcoded
    self._install_templates()    # Hardcoded
    # Per DES: servirebbe self._install_des() QUI
```

**Conseguenze**:
- Ogni nuova funzionalità richiede modifiche a `install_nwave.py`
- Logica sparsa in metodi separati
- Testing non modulare
- Difficile gestire dependencies tra componenti

## Soluzione: Plugin Architecture

### 1. Concetti Chiave

**Plugin** = Componente installabile autonomo
- Ogni componente (agents, commands, templates, DES) diventa plugin
- Implementa interfaccia comune (`InstallationPlugin`)
- Dichiara dependencies e priority
- Self-contained installation logic

**Registry** = Orchestratore plugin
- Scopre plugin disponibili
- Risolve dependency order (topological sort)
- Esegue install/verify/uninstall per tutti i plugin

**Beneficio principale**: Per aggiungere DES → crea `DESPlugin` + registra, **ZERO modifiche a installer**

---

## Design Review Status (Iteration 1 Feedback - ADDRESSED)

**Review Date**: 2026-02-01
**Reviewer**: @solution-architect-reviewer (Morgan persona)
**Verdict**: NEEDS_REVISION → **RESOLVED** (all HIGH severity issues addressed)

### Blocking Issues Resolved

✅ **HIGH-02 - Circular Import**: RESOLVED via module-level function extraction pattern
- Solution: Extract `install_agents_impl()` from `_install_agents()` class method
- Implementation: See section 2.5 "Circular Import Prevention"

✅ **HIGH-01 - DES Source Structure**: RESOLVED via comprehensive documentation
- `src/des/` exists and validated (2026-02-01 verification)
- `nWave/scripts/des/` creation documented with implementation in MED-01
- Build pipeline integration via `context.dist_dir` and `context.framework_source`

✅ **HIGH-03 - InstallContext Incomplete**: RESOLVED via field additions
- Added `framework_source: Optional[Path]` - nWave/ directory path
- Added `project_root: Optional[Path]` - project root directory
- Added `rich_logger: Optional[Any]` - RichLogger for styled output

### Outstanding MED Severity Items (non-blocking)

⚠️ **MED-01 - DES Script Creation**: Documented, deferred to Phase 4 prerequisites
⚠️ **MED-02 - DES Template Creation**: Documented, deferred to Phase 4 prerequisites
✅ **MED-04 - Priority Rationale**: Documented inline in code examples

**External Validity**: All blocking issues resolved. Design can now be implemented without architectural failures.

---

## Architettura Plugin

### 1. Componenti Fondamentali

**InstallationPlugin (ABC Interface)**:
```python
class InstallationPlugin(ABC):
    @abstractmethod
    def name(self) -> str:
        """Nome univoco plugin (es: 'agents', 'des')"""

    @abstractmethod
    def install(self, context: InstallContext) -> PluginResult:
        """Esegue installazione del componente"""

    @abstractmethod
    def verify(self, context: InstallContext) -> PluginResult:
        """Verifica installazione corretta"""

    def dependencies(self) -> List[str]:
        """Plugin da cui questo dipende (default: [])"""

    def priority(self) -> int:
        """Priorità installazione (default: 100)"""
```

**PluginRegistry**:
- Mantiene lista plugin registrati
- Risolve ordine esecuzione (topological sort per dependencies)
- Orchestr install/verify/uninstall

**InstallContext**:
- Context condiviso tra tutti i plugin
- Contiene: paths, logger, backup manager, dry_run flag
- Plugin possono condividere dati via `plugin_data` dict

### 2. `scripts/install/installation_verifier.py`
**Modifiche**:
- Nuova classe: `DESVerificationChecks`
  - `verify_des_module()` - test import DES
  - `verify_des_scripts()` - check presenza scripts
  - `verify_des_templates()` - check templates
- Integrare verifiche DES in `run_verification()`
- Aggiornare output tabella con componenti DES

**Criteri successo aggiornati**:
```python
success = (
    len(missing_essential) == 0
    and manifest_exists
    and des_module_ok           # NUOVO
    and len(des_scripts_missing) == 0
    and des_templates_ok
)
```

### 3. Utility Scripts da Creare/Aggiornare

**`~/.claude/scripts/validate_step_file.py`** (aggiornare esistente):
- Supporto schema v3.0 (7 phases)

**`~/.claude/scripts/check_stale_phases.py`** (NUOVO):
```python
"""Pre-commit hook: Detect abandoned IN_PROGRESS phases."""
from des.application import StaleExecutionDetector

def main():
    detector = StaleExecutionDetector(project_root=Path.cwd())
    result = detector.scan_for_stale_executions()

    if result.is_blocked:
        print("ERROR: Stale IN_PROGRESS phases detected:")
        for stale in result.stale_executions:
            print(f"  - {stale.step_file}: {stale.phase_name}")
        sys.exit(1)
```

**`~/.claude/scripts/scope_boundary_check.py`** (NUOVO):
```python
"""Pre-commit hook: Validate scope boundaries."""
from des.validation import ScopeValidator
# Wrapper per ScopeValidator con git diff staged
```

### 4. Templates da Creare

**`~/.claude/templates/.pre-commit-config-nwave.yaml`**:
```yaml
repos:
  - repo: local
    hooks:
      - id: validate-step-file
        name: nWave Step File Validation
        entry: python ~/.claude/scripts/validate_step_file.py
        language: system
        files: 'steps/.*\.json$'

      - id: check-stale-phases
        name: Stale Phase Detection
        entry: python ~/.claude/scripts/check_stale_phases.py
        language: system
        pass_filenames: false
```

**`~/.claude/templates/.des-audit-README.md`**:
```markdown
# DES Audit Trail

Audit logs immutabili per tracciabilità workflow nWave.

## Struttura
- `audit-YYYY-MM-DD.log`: Log JSONL con rotazione giornaliera
- Append-only, SHA256 hash per integrità

## Eventi Loggati
- TASK_INVOCATION_STARTED/VALIDATED
- PHASE_STARTED/COMPLETED
- SCOPE_VIOLATION
- TIMEOUT_WARNING

## Query Esempio
```bash
# Filtrare violations
grep '"event":"SCOPE_VIOLATION"' audit-*.log | jq .

# Contare per step
jq -r 'select(.event=="SCOPE_VIOLATION") | .step_path' *.log | sort | uniq -c
```
```

### 5. Documentazione da Aggiornare

**`docs/installation/installation-guide.md`**:
- Nuova sezione "DES (Deterministic Execution System)" dopo "What Gets Installed"
- Contenuto:
  - DES Python Module location
  - Audit trail spiegazione
  - Pre-commit hooks opzionali
- Aggiornare troubleshooting con "DES Module Import Errors"

**`docs/reference/des-audit-trail-guide.md`** (NUOVO):
- Scopo audit trail
- Formato file JSONL
- Tipi eventi completi
- Query esempi avanzati
- Retention policy

**`README.md`** principale:
- Menzionare DES come feature chiave
- Link a documentazione DES

## Struttura Directory Plugin System

```
scripts/install/
├── install_nwave.py                 # Installer principale (diventa orchestratore)
├── installation_verifier.py         # Verifica installazione
├── plugins/
│   ├── __init__.py                  # Plugin registry export
│   ├── base.py                      # InstallationPlugin, InstallContext, PluginResult
│   ├── registry.py                  # PluginRegistry con topological sort
│   ├── agents_plugin.py             # Plugin per agenti (migrato da _install_agents)
│   ├── commands_plugin.py           # Plugin per comandi (migrato da _install_commands)
│   ├── templates_plugin.py          # Plugin per templates (migrato da _install_templates)
│   ├── utilities_plugin.py          # Plugin per utility scripts
│   └── des_plugin.py                # ✨ NUOVO - DES installation plugin
└── ...
```

## Esempi di Plugin Implementation

### 1. Base Classes (`scripts/install/plugins/base.py`)

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from pathlib import Path
import logging

@dataclass
class PluginResult:
    """Risultato di un'operazione plugin."""
    success: bool
    message: str
    details: Optional[Dict[str, Any]] = None

@dataclass
class InstallContext:
    """Context condiviso tra tutti i plugin durante installazione."""
    claude_dir: Path
    scripts_dir: Path
    templates_dir: Path
    logger: logging.Logger
    dry_run: bool = False

    # INTEGRATION: Existing utilities from install_nwave.py
    backup_manager: Optional['BackupManager'] = None
    installation_verifier: Optional['InstallationVerifier'] = None

    # Build pipeline integration
    dist_dir: Optional[Path] = None  # dist/ide directory from build
    source_dir: Optional[Path] = None  # nWave/ source directory (root of nWave repo)

    # Framework source paths (REQUIRED for wrapper pattern - HIGH-03 fix)
    framework_source: Optional[Path] = None  # Path to nWave/ directory (for accessing framework code)
    project_root: Optional[Path] = None  # Project root directory (parent of nWave/)

    # Rich logger for styled output (REQUIRED for wrapper pattern - HIGH-03 fix)
    rich_logger: Optional[Any] = None  # RichLogger instance from existing installer

    # Version tracking (reuse existing logic)
    current_version: Optional[str] = None
    target_version: Optional[str] = None

    # Shared data between plugins
    plugin_data: Dict[str, Any] = field(default_factory=dict)

class InstallationPlugin(ABC):
    """Interfaccia base per tutti i plugin di installazione."""

    @abstractmethod
    def name(self) -> str:
        """Nome univoco del plugin (es: 'agents', 'commands', 'des')."""
        pass

    @abstractmethod
    def install(self, context: InstallContext) -> PluginResult:
        """Esegue l'installazione del componente."""
        pass

    @abstractmethod
    def verify(self, context: InstallContext) -> PluginResult:
        """Verifica che l'installazione sia corretta."""
        pass

    def dependencies(self) -> List[str]:
        """
        Lista dei plugin da cui questo dipende.
        Esempio: DESPlugin dipende da ['templates', 'utilities']
        """
        return []

    def priority(self) -> int:
        """
        Priorità di installazione (default: 100).
        Priorità più bassa = eseguito prima.
        """
        return 100

    def uninstall(self, context: InstallContext) -> PluginResult:
        """Disinstalla il componente (opzionale)."""
        return PluginResult(
            success=True,
            message=f"{self.name()} uninstall not implemented"
        )
```

### 2. Plugin Registry (`scripts/install/plugins/registry.py`)

```python
from typing import List, Dict, Set
from .base import InstallationPlugin, InstallContext, PluginResult
import logging

class PluginRegistry:
    """Registry per gestire plugin di installazione con risoluzione dependencies."""

    def __init__(self):
        self._plugins: Dict[str, InstallationPlugin] = {}
        self.logger = logging.getLogger(__name__)

    def register(self, plugin: InstallationPlugin) -> None:
        """Registra un plugin."""
        name = plugin.name()
        if name in self._plugins:
            raise ValueError(f"Plugin '{name}' già registrato")
        self._plugins[name] = plugin
        self.logger.info(f"Registrato plugin: {name}")

    def _topological_sort(self) -> List[InstallationPlugin]:
        """
        Ordina plugin usando topological sort (Kahn's algorithm).
        Rispetta dependencies e priority.
        """
        # Costruisci grafo dependencies
        in_degree = {name: 0 for name in self._plugins}
        adjacency = {name: [] for name in self._plugins}

        for name, plugin in self._plugins.items():
            for dep in plugin.dependencies():
                if dep not in self._plugins:
                    raise ValueError(
                        f"Plugin '{name}' dipende da '{dep}' non registrato"
                    )
                adjacency[dep].append(name)
                in_degree[name] += 1

        # Kahn's algorithm con priority sorting
        queue = []
        for name, degree in in_degree.items():
            if degree == 0:
                plugin = self._plugins[name]
                queue.append((plugin.priority(), name, plugin))
        queue.sort()  # Ordina per priority

        result = []
        while queue:
            _, name, plugin = queue.pop(0)
            result.append(plugin)

            for neighbor in adjacency[name]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    neighbor_plugin = self._plugins[neighbor]
                    queue.append((neighbor_plugin.priority(), neighbor, neighbor_plugin))
            queue.sort()  # Re-sort per priority

        if len(result) != len(self._plugins):
            raise ValueError("Dependency cycle detected in plugins")

        return result

    def install_all(self, context: InstallContext) -> bool:
        """Installa tutti i plugin in ordine di dependency."""
        sorted_plugins = self._topological_sort()

        self.logger.info(f"Installing {len(sorted_plugins)} plugins...")
        for i, plugin in enumerate(sorted_plugins, 1):
            self.logger.info(f"[{i}/{len(sorted_plugins)}] Installing: {plugin.name()}")

            result = plugin.install(context)
            if not result.success:
                self.logger.error(f"Plugin '{plugin.name()}' install failed: {result.message}")
                return False

        return True

    def verify_all(self, context: InstallContext) -> bool:
        """Verifica tutti i plugin installati."""
        all_ok = True
        for plugin in self._plugins.values():
            result = plugin.verify(context)
            if not result.success:
                self.logger.error(f"Plugin '{plugin.name()}' verify failed: {result.message}")
                all_ok = False

        return all_ok
```

### 2.5. Circular Import Prevention (HIGH-02 Fix)

**Problem**: Plugins need to call existing installer methods, but `install_nwave.py` imports plugins → circular dependency.

**Solution**: Extract module-level functions from existing class methods.

**Migration Pattern** (Phase 1 refactoring):

```python
# BEFORE (install_nwave.py) - Hardcoded method
class nWaveInstaller:
    def _install_agents(self):
        """Existing 80-line implementation"""
        # ... all the existing logic ...
        pass

# AFTER (install_nwave.py) - Extracted function + thin wrapper
def install_agents_impl(target_dir, framework_source, logger, backup_manager, dry_run):
    """
    Extracted implementation (module-level function).
    Can be imported by plugins without circular dependency.
    """
    # ... EXACT SAME 80-line implementation moved here ...
    pass

class nWaveInstaller:
    def _install_agents(self):
        """Thin wrapper calling extracted function."""
        install_agents_impl(
            self.claude_dir,
            self.framework_source,
            self.rich_logger,
            self.backup_manager,
            self.dry_run
        )
```

**Why This Works**:
- Plugins import `install_agents_impl` (function), NOT `nWaveInstaller` (class)
- `install_nwave.py` can import plugins for registry (class doesn't import plugins)
- No circular dependency: `install_nwave.py` → plugins → `install_agents_impl` (function)

**Implementation Note**: All existing `_install_*` methods follow this pattern:
- `_install_agents()` → `install_agents_impl()`
- `_install_commands()` → `install_commands_impl()`
- `_install_templates()` → `install_templates_impl()`
- `_install_utility_scripts()` → `install_utility_scripts_impl()`

### 3. Esempio Plugin: AgentsPlugin (`scripts/install/plugins/agents_plugin.py`)

```python
from .base import InstallationPlugin, InstallContext, PluginResult
from pathlib import Path
import shutil

class AgentsPlugin(InstallationPlugin):
    """
    Plugin per installazione agenti nWave.

    INTEGRATION STRATEGY: Wrapper around existing _install_agents() logic.
    This plugin REUSES the existing installation logic from install_nwave.py
    instead of reimplementing it.

    CIRCULAR IMPORT FIX (HIGH-02):
    Instead of importing nWaveInstaller class (which imports plugins, creating cycle),
    we import the module-level function that was extracted from _install_agents().
    """

    def name(self) -> str:
        return "agents"

    def priority(self) -> int:
        return 10  # Installato per primo (bassa priorità = eseguito prima)
        # Rationale: Agents are foundational and have no dependencies

    def dependencies(self) -> list:
        return []  # Nessuna dipendenza

    def install(self, context: InstallContext) -> PluginResult:
        """
        Installa agenti REUSING existing logic from install_nwave.py.

        MIGRATION APPROACH:
        Phase 2: Call module-level function (extracted from _install_agents)
        Phase 5: Optionally refactor into standalone logic (future)
        """
        try:
            # HIGH-02 FIX: Import module-level function, NOT the class
            # This breaks the circular dependency:
            #   install_nwave.py imports plugins → plugins import install_agents_impl (function)
            # Instead of:
            #   install_nwave.py imports plugins → plugins import nWaveInstaller (class) → CYCLE!
            from scripts.install.install_nwave import install_agents_impl

            # REUSE: Call extracted function with context parameters
            # This preserves all existing logic: backup, validation, error handling
            install_agents_impl(
                target_dir=context.claude_dir,
                framework_source=context.framework_source,
                logger=context.rich_logger or context.logger,
                backup_manager=context.backup_manager,
                dry_run=context.dry_run
            )

            # Extract metadata from existing logic
            agents_dir = context.claude_dir / "agents" / "nw"
            agents_installed = list(agents_dir.glob("*.md")) if agents_dir.exists() else []

            # Salva metadata per altri plugin
            context.plugin_data['agents'] = {
                'count': len(agents_installed),
                'files': [f.name for f in agents_installed]
            }

            return PluginResult(
                success=True,
                message=f"Installed {len(agents_installed)} agents (via existing logic)",
                details={'agents': [f.name for f in agents_installed]}
            )

        except Exception as e:
            context.logger.error(f"AgentsPlugin install failed: {e}")
            return PluginResult(
                success=False,
                message=f"Agent installation failed: {e}"
            )

    def verify(self, context: InstallContext) -> PluginResult:
        """
        Verifica agenti REUSING existing InstallationVerifier.
        """
        # REUSE: Use existing verification infrastructure
        if context.installation_verifier:
            # Delegate to existing verifier
            verifier = context.installation_verifier

            # Existing verifier has _check_agents() method
            agents_ok = verifier._check_agents()

            if agents_ok:
                return PluginResult(success=True, message="Agents verified (existing verifier)")
            else:
                return PluginResult(success=False, message="Agent verification failed")

        # Fallback: Simple verification if verifier not available
        target_dir = context.claude_dir / "agents" / "nw"
        if not target_dir.exists():
            return PluginResult(success=False, message=f"Agents directory not found: {target_dir}")

        agent_files = list(target_dir.glob("*.md"))
        expected_min = 10

        if len(agent_files) < expected_min:
            return PluginResult(
                success=False,
                message=f"Expected at least {expected_min} agents, found {len(agent_files)}"
            )

        return PluginResult(success=True, message=f"Verified {len(agent_files)} agents")
```

### 4. Esempio Plugin: DESPlugin (`scripts/install/plugins/des_plugin.py`)

```python
from .base import InstallationPlugin, InstallContext, PluginResult
from pathlib import Path
import shutil
import subprocess

class DESPlugin(InstallationPlugin):
    """
    Plugin per installazione DES (Deterministic Execution System).

    Questo plugin dimostra l'estensibilità del sistema:
    - ZERO modifiche a install_nwave.py
    - Basta registrare nel registry
    - Dependency su templates e utilities
    """

    def name(self) -> str:
        return "des"

    def priority(self) -> int:
        return 50  # Dopo utilities (40) ma prima di verifica finale

    def dependencies(self) -> list:
        return ["templates", "utilities"]  # DES dipende da templates e utilities

    def install(self, context: InstallContext) -> PluginResult:
        """
        Installa DES module, scripts e templates.

        Steps:
        1. Copia src/des/ → ~/.claude/lib/python/des/
        2. Installa utility scripts (check_stale_phases, scope_boundary_check)
        3. Installa templates (.pre-commit-config-nwave.yaml, .des-audit-README.md)
        """
        try:
            # 1. Installa DES Python module
            des_module_result = self._install_des_module(context)
            if not des_module_result.success:
                return des_module_result

            # 2. Installa DES utility scripts
            scripts_result = self._install_des_scripts(context)
            if not scripts_result.success:
                return scripts_result

            # 3. Installa DES templates
            templates_result = self._install_des_templates(context)
            if not templates_result.success:
                return templates_result

            return PluginResult(
                success=True,
                message="DES installed successfully",
                details={
                    'module': des_module_result.details,
                    'scripts': scripts_result.details,
                    'templates': templates_result.details
                }
            )

        except Exception as e:
            return PluginResult(
                success=False,
                message=f"DES installation failed: {e}"
            )

    def _install_des_module(self, context: InstallContext) -> PluginResult:
        """
        Installa DES Python module in ~/.claude/lib/python/des/.

        INTEGRATION: Uses existing BackupManager for safety.

        HIGH-01 FIX: DES source location documentation.
        Current state: src/des/ exists in project (validated during design review).
        Migration: This code assumes src/des/ is copied to dist/ide/lib/python/des/
        during build pipeline (same pattern as existing framework code).
        """
        # HIGH-01 FIX: Use context.dist_dir if available (build pipeline integration)
        # Fallback to src/des for development installations
        if context.dist_dir:
            source_dir = context.dist_dir / "lib" / "python" / "des"
        else:
            source_dir = Path("src/des")  # Development fallback

        lib_python_dir = context.claude_dir / "lib" / "python"
        target_dir = lib_python_dir / "des"

        if not source_dir.exists():
            return PluginResult(
                success=False,
                message=f"DES source not found: {source_dir} (check build pipeline or src/des exists)"
            )

        # Crea struttura lib/python/
        lib_python_dir.mkdir(parents=True, exist_ok=True)

        # REUSE: Existing BackupManager for safety
        if context.backup_manager and target_dir.exists():
            try:
                context.logger.info(f"Backing up existing DES module: {target_dir}")
                context.backup_manager.backup_directory(target_dir)
            except Exception as e:
                context.logger.warning(f"Backup failed (continuing): {e}")

        # Copia modulo DES
        if context.dry_run:
            context.logger.info(f"[DRY-RUN] Would copy {source_dir} → {target_dir}")
        else:
            if target_dir.exists():
                shutil.rmtree(target_dir)
            shutil.copytree(source_dir, target_dir)

        return PluginResult(
            success=True,
            message=f"DES module copied to {target_dir}",
            details={'target': str(target_dir)}
        )

    def _install_des_scripts(self, context: InstallContext) -> PluginResult:
        """
        Installa DES utility scripts.

        HIGH-01 FIX: DES scripts location documentation.
        Prerequisites: These scripts must be created BEFORE Phase 4 (DESPlugin implementation).
        See MED-01 remediation for creation tasks.
        """
        scripts_to_install = [
            "check_stale_phases.py",
            "scope_boundary_check.py"
        ]

        # HIGH-01 FIX: Use framework_source if available (build pipeline integration)
        # Fallback to nWave/scripts/des for development
        if context.framework_source:
            source_dir = context.framework_source / "scripts" / "des"
        else:
            source_dir = Path("nWave/scripts/des")  # Development fallback

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
            message=f"Installed {len(installed)} DES scripts",
            details={'scripts': installed}
        )

    def _install_des_templates(self, context: InstallContext) -> PluginResult:
        """Installa DES templates."""
        templates = [
            ".pre-commit-config-nwave.yaml",
            ".des-audit-README.md"
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
            message=f"Installed {len(installed)} DES templates",
            details={'templates': installed}
        )

    def verify(self, context: InstallContext) -> PluginResult:
        """Verifica installazione DES."""
        errors = []

        # 1. Verifica DES module importabile
        try:
            # Aggiungi lib/python a sys.path temporaneamente
            lib_python = context.claude_dir / "lib" / "python"
            result = subprocess.run(
                ['python3', '-c', f'import sys; sys.path.insert(0, "{lib_python}"); from des.application import DESOrchestrator'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode != 0:
                errors.append(f"DES module import failed: {result.stderr}")
        except Exception as e:
            errors.append(f"DES module verify failed: {e}")

        # 2. Verifica scripts presenti
        expected_scripts = ["check_stale_phases.py", "scope_boundary_check.py"]
        for script in expected_scripts:
            script_path = context.scripts_dir / script
            if not script_path.exists():
                errors.append(f"Missing DES script: {script}")

        # 3. Verifica templates presenti
        expected_templates = [".pre-commit-config-nwave.yaml", ".des-audit-README.md"]
        for template in expected_templates:
            template_path = context.templates_dir / template
            if not template_path.exists():
                errors.append(f"Missing DES template: {template}")

        if errors:
            return PluginResult(
                success=False,
                message="DES verification failed",
                details={'errors': errors}
            )

        return PluginResult(
            success=True,
            message="DES verification passed (module, scripts, templates OK)"
        )
```

## Integration with Existing System

### Overview: Plugin System as Wrapper Layer

**CRITICAL PRINCIPLE**: Plugin system is a **WRAPPER, not a rewrite**.

The plugin architecture wraps existing installation logic from `install_nwave.py` rather than reimplementing it. This approach:
- ✅ Preserves proven installation logic (830 lines, battle-tested)
- ✅ Maintains backward compatibility (same underlying implementation)
- ✅ Enables extensibility (add new plugins without modifying core)
- ✅ Reduces risk (no behavioral changes during migration)

### Existing Installation System Architecture

**Current System** (`scripts/install/install_nwave.py`):

```
┌─────────────────────────────────────────────────────────┐
│ nWaveInstaller Class (830 lines)                        │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  install() [Entry Point]                                │
│    ├─→ check_prerequisites()                            │
│    ├─→ backup_existing_installation() ───→ BackupManager│
│    ├─→ build_distribution()          ───→ tools/build.py│
│    ├─→ install_framework()                              │
│    │    ├─→ _install_agents()        [HARDCODED]        │
│    │    ├─→ _install_commands()      [HARDCODED]        │
│    │    ├─→ _install_templates()     [HARDCODED]        │
│    │    └─→ _install_utility_scripts() [HARDCODED]      │
│    └─→ verify_installation()         ───→ InstallationVerifier
│                                                          │
├─────────────────────────────────────────────────────────┤
│ Utilities Integrated:                                   │
│  • BackupManager - Handles ~/.claude/backups/           │
│  • InstallationVerifier - Validation framework          │
│  • Rich library - Styled console output                 │
│  • Version tracking - Comparison and upgrade logic      │
└─────────────────────────────────────────────────────────┘
```

**Key Existing Classes** (to be reused, not replaced):

1. **BackupManager** (`scripts/install/install_nwave.py` lines ~100-150):
   - Creates timestamped backups: `~/.claude/backups/nwave-{timestamp}/`
   - Validates backup integrity
   - Cleanup old backups
   - **REUSE in plugins**: `context.backup_manager.backup_file(src, dest)`

2. **InstallationVerifier** (`scripts/install/installation_verifier.py`):
   - `_check_agents()` - Validates agent installation
   - `_check_commands()` - Validates command installation
   - `_check_templates()` - Validates templates
   - `_check_schema_validation()` - Schema v2.0/v3.0 validation
   - **REUSE in plugins**: `context.installation_verifier._check_agents()`

3. **Build Pipeline Integration**:
   - `tools/build.py` - Builds `dist/ide` from `nWave/`
   - `scripts/build-ide-bundle.sh` - Alternative build script
   - `tools/embed_sources.py` - Source embedding
   - **REUSE**: Build runs BEFORE plugin orchestration

4. **Version Tracking** (lines ~200-250):
   - `get_installed_version()` - Reads current version
   - `compare_versions()` - Semantic version comparison
   - Upgrade vs fresh install detection
   - **REUSE**: Version logic unchanged, wrapped in context

### Plugin System Integration Architecture

**With Plugins** (Wrapper Layer):

```
┌─────────────────────────────────────────────────────────┐
│ nWaveInstaller Class (SIMPLIFIED to ~300 lines)         │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  install() [Entry Point]                                │
│    ├─→ check_prerequisites()         [UNCHANGED]        │
│    ├─→ backup_existing_installation() [UNCHANGED]       │
│    ├─→ build_distribution()          [UNCHANGED]        │
│    ├─→ install_framework()           [MODIFIED ↓]       │
│    │    │                                                │
│    │    └──→ PluginRegistry.install_all() ──┐           │
│    │                                         │           │
│    │         ┌───────────────────────────────┘           │
│    │         │ PLUGIN ORCHESTRATION                     │
│    │         ├─→ AgentsPlugin.install() ───────────┐    │
│    │         │    └─→ CALLS: self._install_agents() │   │
│    │         │                                       │   │
│    │         ├─→ CommandsPlugin.install() ──────────┤   │
│    │         │    └─→ CALLS: self._install_commands()   │
│    │         │                                       │   │
│    │         ├─→ TemplatesPlugin.install() ─────────┤   │
│    │         │    └─→ CALLS: self._install_templates()  │
│    │         │                                       │   │
│    │         ├─→ UtilitiesPlugin.install() ─────────┤   │
│    │         │    └─→ CALLS: self._install_utility_scripts()
│    │         │                                       │   │
│    │         └─→ DESPlugin.install() [NEW PLUGIN]   │   │
│    │              └─→ Uses context.backup_manager    │   │
│    │                                                 │   │
│    │         [Plugins call existing methods ────────┘]  │
│    │                                                     │
│    └─→ verify_installation()         [UNCHANGED]        │
│         └─→ PluginRegistry.verify_all()                 │
│              └─→ Uses context.installation_verifier     │
│                                                          │
├─────────────────────────────────────────────────────────┤
│ Existing Utilities (UNCHANGED):                         │
│  • BackupManager - Injected into InstallContext         │
│  • InstallationVerifier - Injected into InstallContext  │
│  • Rich library - Used by plugins for output            │
│  • Version tracking - Available via context             │
└─────────────────────────────────────────────────────────┘
```

**Key Integration Points**:

1. **InstallContext Creation** (in `install_framework()`):
```python
context = InstallContext(
    claude_dir=self.claude_dir,
    scripts_dir=self.scripts_dir,
    templates_dir=self.templates_dir,
    logger=self.logger,
    dry_run=self.dry_run,

    # INJECT existing utilities
    backup_manager=self.backup_manager,
    installation_verifier=self.installation_verifier,

    # Build pipeline integration
    dist_dir=self.dist_dir,
    source_dir=Path("nWave"),

    # Version tracking
    current_version=self.get_installed_version(),
    target_version=self.target_version
)
```

2. **Plugin Calls Existing Methods**:
```python
class AgentsPlugin(InstallationPlugin):
    def install(self, context: InstallContext) -> PluginResult:
        # Import existing installer
        from scripts.install.install_nwave import nWaveInstaller

        # Create instance
        installer = nWaveInstaller(
            target_dir=context.claude_dir,
            logger=context.logger,
            dry_run=context.dry_run
        )

        # CALL EXISTING METHOD (no reimplementation)
        installer._install_agents()

        return PluginResult(success=True, message="Agents installed")
```

3. **Verification Reuses InstallationVerifier**:
```python
class AgentsPlugin(InstallationPlugin):
    def verify(self, context: InstallContext) -> PluginResult:
        # Use existing verifier
        if context.installation_verifier:
            agents_ok = context.installation_verifier._check_agents()
            if agents_ok:
                return PluginResult(success=True, message="Agents verified")
        # Fallback logic...
```

### Migration Path: Existing Logic → Plugins → Registry

**Phase 1**: Plugin Infrastructure (No changes to installer)
- Create `plugins/base.py`, `plugins/registry.py`
- `install_nwave.py` UNCHANGED
- **Result**: Infrastructure exists, not yet used

**Phase 2**: Wrap Existing Methods as Plugins
- Create `AgentsPlugin` that calls `self._install_agents()`
- Create `CommandsPlugin` that calls `self._install_commands()`
- Create `TemplatesPlugin` that calls `self._install_templates()`
- Create `UtilitiesPlugin` that calls `self._install_utility_scripts()`
- `install_nwave.py` UNCHANGED (methods still there)
- **Result**: Plugins wrap existing logic, no behavioral changes

**Phase 3**: Switchover to PluginRegistry
- Modify `install_framework()` to use `PluginRegistry.install_all()`
- Keep existing methods for now (plugins call them)
- **Result**: Execution path changes, but same underlying code runs

**Phase 4**: Add DESPlugin (Demonstrates Extensibility)
- Create `DESPlugin` (new component)
- Register in installer: `registry.register(DESPlugin())`
- **Result**: New functionality added without modifying core installer

**Phase 5**: (Optional) Gradual Refactoring
- Over time, inline existing methods into plugins
- Remove dependency on `self._install_agents()` etc.
- **Result**: Cleaner code, but no rush (existing methods work)

### Integration with Existing Utilities: Examples

**Example 1: Using BackupManager in DESPlugin**

```python
class DESPlugin(InstallationPlugin):
    def install(self, context: InstallContext) -> PluginResult:
        target_dir = context.claude_dir / "lib" / "python" / "des"

        # REUSE: Existing BackupManager (don't create custom backup logic)
        if context.backup_manager and target_dir.exists():
            context.logger.info(f"Backing up existing DES: {target_dir}")
            context.backup_manager.backup_directory(target_dir)

        # Install DES module
        shutil.copytree(Path("src/des"), target_dir)

        return PluginResult(success=True, message="DES installed with backup")
```

**Example 2: Using InstallationVerifier in Plugin Verification**

```python
class CommandsPlugin(InstallationPlugin):
    def verify(self, context: InstallContext) -> PluginResult:
        # REUSE: Existing InstallationVerifier logic
        if context.installation_verifier:
            commands_ok = context.installation_verifier._check_commands()
            if not commands_ok:
                return PluginResult(
                    success=False,
                    message="Command verification failed (existing verifier)"
                )

        return PluginResult(success=True, message="Commands verified")
```

**Example 3: Using Rich Library for Output (Existing Pattern)**

```python
from rich.console import Console
from rich.table import Table

class DESPlugin(InstallationPlugin):
    def install(self, context: InstallContext) -> PluginResult:
        # REUSE: Rich library (already used in install_nwave.py)
        console = Console()

        table = Table(title="DES Installation")
        table.add_column("Component")
        table.add_column("Status")

        # ... installation logic

        table.add_row("DES Module", "✅ Installed")
        table.add_row("DES Scripts", "✅ Installed")
        console.print(table)

        return PluginResult(success=True, message="DES installed")
```

**Example 4: Using Existing Version Tracking**

```python
class UtilitiesPlugin(InstallationPlugin):
    def install(self, context: InstallContext) -> PluginResult:
        # REUSE: Existing version tracking logic
        if context.current_version and context.target_version:
            context.logger.info(
                f"Upgrading utilities from {context.current_version} "
                f"to {context.target_version}"
            )
        else:
            context.logger.info("Fresh installation of utilities")

        # ... installation logic

        return PluginResult(success=True, message="Utilities installed")
```

### Backward Compatibility Guarantees

**ANTI-REGRESSION GUARANTEES**:

1. **No Behavioral Changes in Phase 2-3**:
   - Plugins call existing methods (`_install_agents()`, etc.)
   - Same code executes, just different orchestration
   - All tests continue to pass (same implementation)

2. **Existing Tests Still Pass**:
   - Unit tests for `_install_agents()` unchanged
   - Integration tests execute same code path (via plugins)
   - No new bugs introduced (same logic)

3. **Upgrade Path Preserved**:
   - `BackupManager` still creates backups
   - `InstallationVerifier` still validates
   - Version comparison logic unchanged

4. **Plugin System is Additive**:
   - Adds orchestration layer (PluginRegistry)
   - Adds extensibility (DESPlugin without installer changes)
   - Does NOT replace working code

### Directory Structure After Integration

```
scripts/install/
├── install_nwave.py                 # MODIFIED: Uses PluginRegistry (orchestrator)
│                                    # PRESERVED: BackupManager, build logic, verification
│
├── installation_verifier.py         # UNCHANGED: Existing verification logic
│                                    # ENHANCED: New DESVerificationChecks added
│
├── plugins/
│   ├── __init__.py                  # Plugin registry export
│   ├── base.py                      # InstallationPlugin, InstallContext, PluginResult
│   ├── registry.py                  # PluginRegistry with topological sort
│   │
│   ├── agents_plugin.py             # WRAPPER: Calls existing _install_agents()
│   ├── commands_plugin.py           # WRAPPER: Calls existing _install_commands()
│   ├── templates_plugin.py          # WRAPPER: Calls existing _install_templates()
│   ├── utilities_plugin.py          # WRAPPER: Calls existing _install_utility_scripts()
│   │
│   └── des_plugin.py                # NEW: DES installation (uses context utilities)
│
└── ...
```

**What Gets Reused vs. What's New**:

| Component | Status | Strategy |
|-----------|--------|----------|
| `BackupManager` | ✅ REUSED | Injected into `InstallContext.backup_manager` |
| `InstallationVerifier` | ✅ REUSED | Injected into `InstallContext.installation_verifier` |
| `_install_agents()` | ✅ REUSED | Called by `AgentsPlugin.install()` |
| `_install_commands()` | ✅ REUSED | Called by `CommandsPlugin.install()` |
| `_install_templates()` | ✅ REUSED | Called by `TemplatesPlugin.install()` |
| `_install_utility_scripts()` | ✅ REUSED | Called by `UtilitiesPlugin.install()` |
| Build pipeline | ✅ REUSED | `tools/build.py` runs before plugins |
| Rich output | ✅ REUSED | Plugins use same Rich library |
| Version tracking | ✅ REUSED | Available in `InstallContext` |
| `PluginRegistry` | 🆕 NEW | Orchestration layer (topological sort) |
| `InstallationPlugin` interface | 🆕 NEW | Common plugin interface |
| `DESPlugin` | 🆕 NEW | New component (demonstrates extensibility) |
| Plugin dependency resolution | 🆕 NEW | Enables complex installation flows |

## Strategia di Migrazione (6 Fasi)

### Fase 1: Creazione Infrastruttura Plugin (1 commit)
**Obiettivo**: Creare base classes e registry **SENZA modificare installer esistente**.

**File da creare**:
- `scripts/install/plugins/__init__.py`
- `scripts/install/plugins/base.py` (InstallationPlugin, InstallContext, PluginResult)
- `scripts/install/plugins/registry.py` (PluginRegistry con topological sort)

**Test**: Unit test per PluginRegistry topological sort con vari scenari dependency.

**CRITICAL**: `install_nwave.py` rimane TOTALMENTE INVARIATO in questa fase.

**Anti-Pattern to Avoid**: ❌ Non modificare nulla in `install_nwave.py` ancora

**Correct Pattern**: ✅ Infrastruttura esiste ma non è usata

---

### Fase 2: Wrapping Existing Methods as Plugins (4 commits)

**STRATEGY**: Create **thin wrapper plugins** that call existing methods.

**Commit 1**: Creare AgentsPlugin (WRAPPER)
```python
# scripts/install/plugins/agents_plugin.py
class AgentsPlugin(InstallationPlugin):
    def install(self, context: InstallContext) -> PluginResult:
        # REUSE: Call existing method, don't reimplement
        from scripts.install.install_nwave import nWaveInstaller

        installer = nWaveInstaller(
            target_dir=context.claude_dir,
            logger=context.logger,
            dry_run=context.dry_run
        )

        # Call existing _install_agents() method
        installer._install_agents()

        return PluginResult(success=True, message="Agents installed")
```
- Test: Verifica che AgentsPlugin chiama `_install_agents()` e produce stesso risultato

**Commit 2**: Creare CommandsPlugin (WRAPPER)
- File: `scripts/install/plugins/commands_plugin.py`
- **WRAPS**: `self._install_commands()` (calls existing method)
- Test: Same behavior as direct call

**Commit 3**: Creare TemplatesPlugin (WRAPPER)
- File: `scripts/install/plugins/templates_plugin.py`
- **WRAPS**: `self._install_templates()` (calls existing method)
- Test: Same behavior as direct call

**Commit 4**: Creare UtilitiesPlugin (WRAPPER)
- File: `scripts/install/plugins/utilities_plugin.py`
- **WRAPS**: `self._install_utility_scripts()` (calls existing method)
- Test: Same behavior as direct call

**CRITICAL**: `install_nwave.py` STILL UNCHANGED - existing methods remain for plugins to call.

**Anti-Pattern to Avoid**: ❌ Don't reimplement installation logic in plugins

**Correct Pattern**: ✅ Plugins call existing `_install_*()` methods

---

### Fase 3: Switchover a Plugin System (1 commit)
**Obiettivo**: Modificare `install_framework()` per usare PluginRegistry (keep existing methods).

**Prima** (install_nwave.py righe 295-310):
```python
def install_framework(self):
    self._install_agents()
    self._install_commands()
    self._install_utility_scripts()
    self._install_templates()
    # ... altri metodi hardcoded
```

**Dopo** (with plugin registry):
```python
def install_framework(self):
    from scripts.install.plugins import PluginRegistry
    from scripts.install.plugins.agents_plugin import AgentsPlugin
    from scripts.install.plugins.commands_plugin import CommandsPlugin
    from scripts.install.plugins.templates_plugin import TemplatesPlugin
    from scripts.install.plugins.utilities_plugin import UtilitiesPlugin

    # Create plugin registry
    registry = PluginRegistry()
    registry.register(AgentsPlugin())
    registry.register(CommandsPlugin())
    registry.register(TemplatesPlugin())
    registry.register(UtilitiesPlugin())

    # Create context with EXISTING UTILITIES injected
    context = InstallContext(
        claude_dir=self.claude_dir,
        scripts_dir=self.scripts_dir,
        templates_dir=self.templates_dir,
        logger=self.logger,
        dry_run=self.dry_run,

        # INTEGRATION: Inject existing utilities into context
        backup_manager=self.backup_manager,
        installation_verifier=self.installation_verifier,

        # Build pipeline integration
        dist_dir=self.dist_dir,
        source_dir=Path("nWave"),

        # Version tracking
        current_version=self.get_installed_version(),
        target_version=self.target_version
    )

    # Execute plugins (which call existing _install_*() methods)
    success = registry.install_all(context)
    if not success:
        raise RuntimeError("Plugin installation failed")

    # Verify all plugins (using existing verifier)
    if not registry.verify_all(context):
        raise RuntimeError("Plugin verification failed")
```

**Key Changes**:
- Execution path: direct method calls → plugin registry orchestration
- Underlying implementation: **UNCHANGED** (plugins call existing methods)
- New capability: Dependency resolution via topological sort

**Existing Methods Preserved** (for now):
- `_install_agents()` - Still exists, called by AgentsPlugin
- `_install_commands()` - Still exists, called by CommandsPlugin
- `_install_templates()` - Still exists, called by TemplatesPlugin
- `_install_utility_scripts()` - Still exists, called by UtilitiesPlugin

**Migration Notes**:
- Phase 3: Keep existing methods (plugins call them)
- Phase 5 (optional): Inline methods into plugins gradually
- No rush to refactor - existing methods work fine

**Test**: Integration test completo - fresh install e upgrade scenario.
- **Expected**: Same files installed, same locations, same behavior
- **Validation**: Compare before/after file trees (should be identical)

---

### Fase 4: Aggiunta DESPlugin (1 commit) - DEMONSTRATES EXTENSIBILITY

**HIGH-01 REMEDIATION**: This phase requires DES source structure to be in place.

**Prerequisites** (MUST complete BEFORE Phase 4):

1. **DES Module Source**:
   - ✅ `src/des/` exists (validated during design review)
   - ✅ Build pipeline copies to `dist/ide/lib/python/des/` (existing pattern)
   - No action required - already complete

2. **DES Scripts Creation** (NEW - must be implemented):
   - ❌ `nWave/scripts/des/check_stale_phases.py` - NOT YET CREATED
   - ❌ `nWave/scripts/des/scope_boundary_check.py` - NOT YET CREATED

   **Implementation Required**:
   ```python
   # nWave/scripts/des/check_stale_phases.py
   """Pre-commit hook: Detect abandoned IN_PROGRESS phases."""
   from des.application import StaleExecutionDetector
   from pathlib import Path
   import sys

   def main():
       detector = StaleExecutionDetector(project_root=Path.cwd())
       result = detector.scan_for_stale_executions()

       if result.is_blocked:
           print("ERROR: Stale IN_PROGRESS phases detected:")
           for stale in result.stale_executions:
               print(f"  - {stale.step_file}: {stale.phase_name}")
           sys.exit(1)
       print("✓ No stale phases detected")

   if __name__ == "__main__":
       main()
   ```

   ```python
   # nWave/scripts/des/scope_boundary_check.py
   """Pre-commit hook: Validate scope boundaries."""
   from des.validation import ScopeValidator
   from pathlib import Path
   import sys

   def main():
       validator = ScopeValidator(project_root=Path.cwd())
       result = validator.validate_git_staged_files()

       if not result.is_valid:
           print("ERROR: Scope violations detected:")
           for violation in result.violations:
               print(f"  - {violation.file}: {violation.reason}")
           sys.exit(1)
       print("✓ All staged files within declared scope")

   if __name__ == "__main__":
       main()
   ```

3. **DES Templates Creation** (NEW - must be implemented):
   - ❌ `nWave/templates/.pre-commit-config-nwave.yaml` - NOT YET CREATED
   - ❌ `nWave/templates/.des-audit-README.md` - NOT YET CREATED

   See MED-02 remediation section for template content specifications.

**Migration Decision Point**:
- **Option A**: Create scripts/templates BEFORE Phase 4 (clean implementation)
- **Option B**: Phase 4 creates placeholder scripts with TODO (defer implementation to US-009)

**Recommended**: Option A - complete DES artifacts before plugin implementation.

---

**Obiettivo**: Dimostrare estensibilità - aggiungere DES **senza modificare core installer logic**.

**File da creare**:
- `scripts/install/plugins/des_plugin.py` (NEW plugin)
- Prerequisites above MUST be complete first

**DESPlugin Implementation** (using existing utilities):
```python
class DESPlugin(InstallationPlugin):
    def name(self) -> str:
        return "des"

    def dependencies(self) -> list:
        return ["templates", "utilities"]  # Dependencies resolved automatically

    def install(self, context: InstallContext) -> PluginResult:
        # REUSE: Existing BackupManager
        if context.backup_manager:
            target = context.claude_dir / "lib" / "python" / "des"
            if target.exists():
                context.backup_manager.backup_directory(target)

        # Install DES module
        self._install_des_module(context)
        self._install_des_scripts(context)
        self._install_des_templates(context)

        return PluginResult(success=True, message="DES installed")

    def verify(self, context: InstallContext) -> PluginResult:
        # REUSE: Existing verification patterns
        # Verify module importable, scripts present, templates installed
        # ...
```

**Modifica a install_nwave.py** (UNA SOLA RIGA):
```python
from scripts.install.plugins.des_plugin import DESPlugin
# ...
registry.register(DESPlugin())  # ← QUESTA È L'UNICA MODIFICA
```

**This Demonstrates**:
- ✅ Add new component (DES) without modifying existing installer code
- ✅ Dependency resolution (DES installed AFTER templates and utilities)
- ✅ Reuse existing utilities (BackupManager, Logger, Rich output)
- ✅ Extensibility: Future components follow same pattern

**Test**: Verifica DES module importabile, scripts presenti, templates installati.

**Anti-Pattern to Avoid**: ❌ Don't add DES logic to `install_framework()` method

**Correct Pattern**: ✅ Create DESPlugin, register once, done

---

### Fase 5: Testing e Documentazione (1 commit)
**Obiettivo**: Testing exhaustive e documentazione completa.

**Test Suite**:

**Unit Tests** (test plugin infrastructure):
- `test_plugin_registry.py` - Topological sort, dependency resolution
- `test_agents_plugin.py` - Verify calls to existing `_install_agents()`
- `test_commands_plugin.py` - Verify calls to existing `_install_commands()`
- `test_templates_plugin.py` - Verify calls to existing `_install_templates()`
- `test_utilities_plugin.py` - Verify calls to existing `_install_utility_scripts()`
- `test_des_plugin.py` - Verify DES installation logic

**Integration Tests** (end-to-end):
- Fresh install with plugin system → verify same result as pre-plugin installer
- Upgrade from v1.6.x (pre-plugin) to v1.7.0 (with plugins) → verify backward compatibility
- Verify BackupManager integration → backups created correctly
- Verify InstallationVerifier integration → verification runs through plugins

**Adversarial Tests** (error handling):
- Dependency cycle detection → registry raises ValueError
- Missing dependency error → registry raises ValueError with clear message
- Plugin install failure → registry stops, reports failure
- Existing method call fails → plugin captures error, returns PluginResult(success=False)

**Regression Tests** (backward compatibility):
- Compare file trees: pre-plugin install vs post-plugin install (should be identical)
- Compare verification output: same components checked, same criteria
- Version tracking still works: upgrade detection, version comparison

**Documentazione**:
- Aggiornare `docs/installation/installation-guide.md` con sezione DES
- Creare `docs/reference/des-audit-trail-guide.md`
- Creare `docs/development/plugin-development-guide.md` per contributor
- Update `ARCHITECTURE.md` with plugin system architecture diagram

---

### Fase 6: Deployment e Rollout (1 commit)
**Obiettivo**: Release graduale con **guaranteed backward compatibility**.

**Azioni**:
1. Version bump: `1.6.x → 1.7.0` (minor version - new feature)
2. Update `CHANGELOG.md`:
   ```markdown
   ## [1.7.0] - 2026-01-31
   ### Added
   - Plugin architecture for modular installation system
   - DES (Deterministic Execution System) integration
   - DES utility scripts: check_stale_phases, scope_boundary_check
   - Pre-commit hook templates for nWave projects

   ### Changed
   - Installer refactored to use PluginRegistry (backward compatible)

   ### Migration
   - No breaking changes - existing installations work as before
   - Fresh installs now include DES automatically
   ```
3. Release notes con migration guide
4. Gradual rollout: alpha → beta → stable

---

## Testing Strategy

### Unit Tests

**`tests/install/test_plugin_registry.py`**:
```python
def test_topological_sort_simple():
    """Test ordine esecuzione con dependencies semplici."""
    registry = PluginRegistry()

    # Plugin A dipende da B
    plugin_a = MockPlugin("A", dependencies=["B"])
    plugin_b = MockPlugin("B", dependencies=[])

    registry.register(plugin_a)
    registry.register(plugin_b)

    sorted_plugins = registry._topological_sort()
    assert sorted_plugins[0].name() == "B"
    assert sorted_plugins[1].name() == "A"

def test_topological_sort_priority():
    """Test priority quando nessuna dependency."""
    registry = PluginRegistry()

    plugin_low = MockPlugin("low", priority=10)
    plugin_high = MockPlugin("high", priority=50)

    registry.register(plugin_high)
    registry.register(plugin_low)

    sorted_plugins = registry._topological_sort()
    assert sorted_plugins[0].name() == "low"  # Priorità bassa = eseguito prima

def test_dependency_cycle_detection():
    """Test rilevamento cycle."""
    registry = PluginRegistry()

    plugin_a = MockPlugin("A", dependencies=["B"])
    plugin_b = MockPlugin("B", dependencies=["A"])  # Cycle!

    registry.register(plugin_a)
    registry.register(plugin_b)

    with pytest.raises(ValueError, match="cycle"):
        registry._topological_sort()

def test_missing_dependency():
    """Test errore se dependency non registrata."""
    registry = PluginRegistry()

    plugin_a = MockPlugin("A", dependencies=["NonExistent"])
    registry.register(plugin_a)

    with pytest.raises(ValueError, match="non registrato"):
        registry._topological_sort()
```

### Integration Tests

**`tests/install/test_full_installation.py`**:
```python
def test_fresh_install_with_plugins(tmp_path):
    """Test installazione completa da zero con plugin system."""
    # Setup
    claude_dir = tmp_path / ".claude"

    # Esegui installer
    installer = nWaveInstaller(target_dir=claude_dir)
    installer.install()

    # Verifica componenti core
    assert (claude_dir / "agents").exists()
    assert len(list((claude_dir / "agents").glob("*.md"))) >= 10

    # Verifica DES installato
    assert (claude_dir / "lib" / "python" / "des").exists()
    assert (claude_dir / "scripts" / "check_stale_phases.py").exists()

    # Verifica DES importabile
    result = subprocess.run(
        ['python3', '-c', 'import sys; sys.path.insert(0, f"{claude_dir}/lib/python"); from des.application import DESOrchestrator'],
        capture_output=True
    )
    assert result.returncode == 0

def test_upgrade_from_pre_plugin_version(existing_installation):
    """Test upgrade da versione senza plugin system."""
    # Precondition: installazione v1.6 esistente (no DES)
    assert not (existing_installation / "lib" / "python" / "des").exists()

    # Run upgrade
    installer = nWaveInstaller(target_dir=existing_installation)
    installer.install()

    # Verifica componenti esistenti preservati
    assert (existing_installation / "agents").exists()

    # Verifica DES aggiunto
    assert (existing_installation / "lib" / "python" / "des").exists()
```

## Piano di Implementazione (Integration-Focused)

### Fase 1: Infrastruttura Plugin (3-4 ore)
**CRITICAL**: Zero changes to `install_nwave.py` in this phase.

1. Creare `scripts/install/plugins/__init__.py`
2. Creare `scripts/install/plugins/base.py`
   - `InstallationPlugin` interface
   - `InstallContext` dataclass (with existing utility fields)
   - `PluginResult` dataclass
3. Creare `scripts/install/plugins/registry.py`
   - `PluginRegistry` class
   - Topological sort (Kahn's algorithm)
   - Dependency resolution
4. Unit test per PluginRegistry
   - Test cycle detection
   - Test priority ordering
   - Test dependency resolution
   - Test missing dependency error

**Deliverables**: Plugin infrastructure ready, not yet used.

### Fase 2: Wrapping Existing Methods (6-8 ore)
**CRITICAL**: `install_nwave.py` methods remain unchanged (plugins call them).

1. Creare `AgentsPlugin` (WRAPPER around `_install_agents()`)
   ```python
   def install(self, context):
       installer = nWaveInstaller(...)
       installer._install_agents()  # Call existing method
       return PluginResult(success=True)
   ```
   - Unit test: Verify calls existing method
   - Integration test: Same result as direct call

2. Creare `CommandsPlugin` (WRAPPER around `_install_commands()`)
   - Same pattern: call existing method
   - Test: Verify integration with existing logic

3. Creare `TemplatesPlugin` (WRAPPER around `_install_templates()`)
   - Same pattern: call existing method
   - Test: Verify template installation

4. Creare `UtilitiesPlugin` (WRAPPER around `_install_utility_scripts()`)
   - Same pattern: call existing method
   - Test: Verify script installation and permissions

5. Unit tests for each plugin
   - Test `install()` method calls existing logic
   - Test `verify()` method uses InstallationVerifier
   - Test dependency declarations

**Deliverables**: Plugins wrap existing logic, no behavioral changes.

### Fase 3: Switchover Installer (2-3 ore)
**CRITICAL**: Keep existing methods for now (plugins call them).

1. Modificare `install_framework()` in `install_nwave.py`:
   - Create `PluginRegistry`
   - Register wrapper plugins (Agents, Commands, Templates, Utilities)
   - Create `InstallContext` with injected utilities
   - Call `registry.install_all(context)`
   - Call `registry.verify_all(context)`

2. **DO NOT** remove existing methods yet:
   - `_install_agents()` → Still exists, called by AgentsPlugin
   - `_install_commands()` → Still exists, called by CommandsPlugin
   - `_install_templates()` → Still exists, called by TemplatesPlugin
   - `_install_utility_scripts()` → Still exists, called by UtilitiesPlugin

3. Integration tests:
   - Fresh install: Compare with pre-plugin baseline (identical result)
   - Upgrade scenario: Verify backward compatibility
   - Verify BackupManager still creates backups
   - Verify InstallationVerifier still runs

**Deliverables**: Installer uses plugin system, same behavior as before.

### Fase 4: DES Plugin e Componenti (4-5 ore)
**DEMONSTRATES**: Extensibility without modifying core installer.

1. Creare `DESPlugin` with install/verify logic
   - Reuse `context.backup_manager` for backups
   - Reuse existing logging patterns
   - Declare dependencies: `["templates", "utilities"]`

2. Creare DES utility scripts:
   - `nWave/scripts/des/check_stale_phases.py`
   - `nWave/scripts/des/scope_boundary_check.py`

3. Creare DES templates:
   - `nWave/templates/.pre-commit-config-nwave.yaml`
   - `nWave/templates/.des-audit-README.md`

4. Aggiornare `validate_step_file.py` per schema v3.0

5. Register DESPlugin in `install_framework()`:
   ```python
   registry.register(DESPlugin())  # ONE LINE - no other changes
   ```

6. Test DES installation:
   - Verify module importable
   - Verify scripts installed and executable
   - Verify templates present
   - Verify dependency order (DES after templates/utilities)

**Deliverables**: DES integrated via plugin, demonstrates extensibility.

### Fase 5: Testing e Documentazione (4-5 ore)
1. Comprehensive test suite:
   - Unit tests for all plugins
   - Integration tests (fresh + upgrade)
   - Regression tests (compare with pre-plugin)
   - Adversarial tests (error handling)

2. Documentation updates:
   - `docs/installation/installation-guide.md` - Add DES section
   - `docs/reference/des-audit-trail-guide.md` - NEW
   - `docs/development/plugin-development-guide.md` - NEW
   - `docs/architecture/plugin-system.md` - Architecture diagram

3. Migration guide for users:
   - Backward compatibility guarantees
   - What's changed (orchestration) vs unchanged (implementation)

**Deliverables**: Full test coverage, complete documentation.

### Fase 6: Deployment (1-2 ore)
1. Version bump: `1.6.x → 1.7.0` (minor - new feature, backward compatible)
2. CHANGELOG.md update:
   ```markdown
   ## [1.7.0] - 2026-02-XX
   ### Added
   - Plugin architecture for modular installation
   - DES (Deterministic Execution System) integration
   - Plugin dependency resolution

   ### Changed
   - Installer refactored to use PluginRegistry (backward compatible)

   ### Migration
   - No breaking changes - existing installations work unchanged
   - Fresh installs include DES automatically
   ```
3. Release notes with integration details
4. Gradual rollout: alpha → beta → stable

**Deliverables**: v1.7.0 released with plugin system and DES.

**Tempo totale stimato**: 20-27 ore

### Key Integration Principles Throughout Implementation

1. **Phase 1**: Infrastructure without disruption (no installer changes)
2. **Phase 2**: Wrap, don't rewrite (plugins call existing methods)
3. **Phase 3**: Change orchestration, preserve implementation
4. **Phase 4**: Demonstrate extensibility (DES without core changes)
5. **Phase 5**: Validate no regressions (same behavior)
6. **Phase 6**: Deploy with confidence (backward compatible)

## Backward Compatibility

### Scenario A: Fresh Install
```
python scripts/install/install_nwave.py
→ DES installato in ~/.claude/lib/python/des/
→ Comandi pronti all'uso
→ Primo /nw:develop crea .des/audit/
```

### Scenario B: Upgrade (utente esistente)
```
Stato: nWave pre-DES installato
→ Run install_nwave.py
→ Backup vecchia versione creato
→ DES aggiunto come nuovo componente
→ Progetti esistenti continuano a funzionare
→ .des/audit/ esistenti preservati
```

### Scenario C: Developer con source
```
Import durante sviluppo: from src.des.application import ...
Import post-install: from des.application import ...
→ Dual support temporaneo
→ Deprecation path graduale (v1.0 → v2.0)
```

## Verifica End-to-End

### 1. Verifica Plugin System Funzionante

**Test installazione con plugin registry**:
```bash
# Fresh install
python scripts/install/install_nwave.py

# Verifica output mostra plugin execution order
# Output atteso:
# Installing 5 plugins...
# [1/5] Installing: agents (priority: 10, deps: [])
# [2/5] Installing: commands (priority: 20, deps: [])
# [3/5] Installing: templates (priority: 30, deps: [])
# [4/5] Installing: utilities (priority: 40, deps: [])
# [5/5] Installing: des (priority: 50, deps: ['templates', 'utilities'])
```

**Verifica dependency resolution**:
```bash
# Controllare che DES sia installato DOPO templates e utilities
# (topological sort rispetta dependencies)
grep -A 5 "Installing:" ~/.claude/install.log | grep -E "(templates|utilities|des)"
```

### 2. Verifica DES Module Importabile

**Test import DES dopo installazione**:
```bash
# Verifica import funziona
python3 -c "import sys; sys.path.insert(0, '$HOME/.claude/lib/python'); from des.application import DESOrchestrator; print('✅ DES module OK')"

# Verifica hook ports
python3 -c "import sys; sys.path.insert(0, '$HOME/.claude/lib/python'); from des.ports.driver_ports.hook_port import ValidatorPort; print('✅ Hook ports OK')"

# Verifica audit logger
python3 -c "import sys; sys.path.insert(0, '$HOME/.claude/lib/python'); from des.adapters.driven.logging.audit_logger import AuditLogger; print('✅ Audit logger OK')"
```

### 3. Verifica DES Scripts Installati

**Test utility scripts presenti ed eseguibili**:
```bash
# Check stale phases script
test -x ~/.claude/scripts/check_stale_phases.py && echo "✅ check_stale_phases.py OK"

# Check scope boundary script
test -x ~/.claude/scripts/scope_boundary_check.py && echo "✅ scope_boundary_check.py OK"

# Verifica validate_step_file supporta schema v3.0
grep -q "schema_version.*3.0" ~/.claude/scripts/validate_step_file.py && echo "✅ Schema v3.0 support OK"
```

### 4. Verifica DES Templates Installati

**Test templates presenti**:
```bash
# Pre-commit config template
test -f ~/.claude/templates/.pre-commit-config-nwave.yaml && echo "✅ Pre-commit template OK"

# Audit README template
test -f ~/.claude/templates/.des-audit-README.md && echo "✅ Audit README template OK"
```

### 5. Output Installazione Atteso

```
┌─────────────────┬────────┬───────┬──────────────┐
│ Component       │ Status │ Count │ Dependencies │
├─────────────────┼────────┼───────┼──────────────┤
│ Agents          │ OK     │ 13    │ []           │
│ Commands        │ OK     │ 20    │ []           │
│ Templates       │ OK     │ 8     │ []           │
│ Utilities       │ OK     │ 5     │ []           │
│ DES Module      │ OK     │ Yes   │ [templates, utilities] ← NUOVO
│ DES Scripts     │ OK     │ 3     │ [utilities]  ← NUOVO
│ Manifest        │ OK     │ Yes   │ []           │
│ Schema          │ OK     │ v3.0  │ []           │
└─────────────────┴────────┴───────┴──────────────┘

✅ All plugins installed successfully
✅ All plugins verified
✅ Installation complete
```

### 6. Test Runtime DES Integration

**Test 1: Audit trail creation**:
```bash
# In un progetto nWave esistente
cd ~/projects/test-nwave-project/

# Esegui comando che trigghera DES hooks
/nw:develop "sample feature"

# Verifica audit trail creato
test -d .des/audit && echo "✅ Audit directory created"
test -f .des/audit/audit-$(date +%Y-%m-%d).log && echo "✅ Audit log created"

# Verifica formato JSONL
cat .des/audit/audit-$(date +%Y-%m-%d).log | jq . && echo "✅ Valid JSONL format"
```

**Test 2: Pre-invocation hooks**:
```bash
# Verifica template validation hook
# (crea template invalido e verifica che DES blocchi invocation)

# Verifica invocation limits hook
# (supera limiti e verifica che DES blocchi)
```

**Test 3: Post-execution hook**:
```bash
# Verifica SubagentStopHook
# (crea step file con IN_PROGRESS phase e verifica che hook rilevi stato stale)
```

### 7. Verifica Plugin Extensibility

**Test aggiunta nuovo plugin senza modificare installer**:
```python
# Scenario: Voglio aggiungere MonitoringPlugin

# Step 1: Creare scripts/install/plugins/monitoring_plugin.py
class MonitoringPlugin(InstallationPlugin):
    def name(self) -> str:
        return "monitoring"

    def dependencies(self) -> list:
        return ["des"]  # Monitoring dipende da DES

    def install(self, context: InstallContext) -> PluginResult:
        # ... logica installazione monitoring
        pass

# Step 2: Registrare in install_nwave.py (UNA RIGA)
from scripts.install.plugins.monitoring_plugin import MonitoringPlugin
# ...
registry.register(MonitoringPlugin())  # ← UNICA MODIFICA

# Step 3: Run installer - monitoring installato DOPO des (dependency rispettata)
```

**Verifica**:
```bash
# Reinstall
python scripts/install/install_nwave.py

# Output atteso:
# [5/6] Installing: des (priority: 50, deps: ['templates', 'utilities'])
# [6/6] Installing: monitoring (priority: 100, deps: ['des'])
#                                                        ^^^^ Rispetta dependency!
```

### 8. Regression Testing

**Verifica backward compatibility**:
```bash
# Test che installazione esistente (pre-plugin) non si rompa
# 1. Simulate existing installation (v1.6.x)
# 2. Run new installer (v1.7.0 with plugins)
# 3. Verify:
#    - Componenti esistenti non sovrascritti (se non necessario)
#    - DES aggiunto senza rompere existing setup
#    - Comandi esistenti continuano a funzionare
```

### 9. Performance Testing

**Verifica topological sort performance**:
```python
# Test con 100 plugin e dependencies complesse
# Tempo atteso: < 100ms per sort
# (Kahn's algorithm è O(V + E))

import time
registry = PluginRegistry()

# Registra 100 plugin con dependencies random
for i in range(100):
    plugin = MockPlugin(f"plugin_{i}", dependencies=[...])
    registry.register(plugin)

start = time.time()
sorted_plugins = registry._topological_sort()
elapsed = time.time() - start

assert elapsed < 0.1, f"Topological sort too slow: {elapsed}s"
```

## MED Severity Remediations (from Design Review)

### MED-01: DES Script Creation Prerequisites

**Issue**: Phase 4 assumes `check_stale_phases.py` and `scope_boundary_check.py` exist, but they don't.

**Remediation**:

Create these scripts BEFORE Phase 4 implementation:

**File**: `nWave/scripts/des/check_stale_phases.py`
```python
#!/usr/bin/env python3
"""
Pre-commit hook: Detect abandoned IN_PROGRESS phases.

Prevents commits when execution-status.yaml contains stale phases
(phases marked IN_PROGRESS but not updated recently).
"""
import sys
from pathlib import Path

# Add DES module to path (after installation)
sys.path.insert(0, str(Path.home() / ".claude" / "lib" / "python"))

from des.application import StaleExecutionDetector

def main():
    """Run stale phase detection on current repository."""
    detector = StaleExecutionDetector(project_root=Path.cwd())
    result = detector.scan_for_stale_executions()

    if result.is_blocked:
        print("❌ ERROR: Stale IN_PROGRESS phases detected:")
        for stale in result.stale_executions:
            print(f"  - {stale.step_file}: {stale.phase_name} (abandoned {stale.age_hours}h ago)")
        print("\nResolution:")
        print("  1. Complete or mark phases as FAILED")
        print("  2. Or remove execution-status.yaml if workflow abandoned")
        return 1

    print("✓ No stale phases detected")
    return 0

if __name__ == "__main__":
    sys.exit(main())
```

**File**: `nWave/scripts/des/scope_boundary_check.py`
```python
#!/usr/bin/env python3
"""
Pre-commit hook: Validate scope boundaries.

Prevents commits when staged files are outside the declared scope
in roadmap.yaml implementation_scope section.
"""
import sys
from pathlib import Path

# Add DES module to path (after installation)
sys.path.insert(0, str(Path.home() / ".claude" / "lib" / "python"))

from des.validation import ScopeValidator

def main():
    """Run scope validation on git staged files."""
    validator = ScopeValidator(project_root=Path.cwd())
    result = validator.validate_git_staged_files()

    if not result.is_valid:
        print("❌ ERROR: Scope violations detected:")
        for violation in result.violations:
            print(f"  - {violation.file}: {violation.reason}")
        print("\nResolution:")
        print("  1. Update roadmap.yaml to include new scope")
        print("  2. Or unstage files outside scope")
        return 1

    print("✓ All staged files within declared scope")
    return 0

if __name__ == "__main__":
    sys.exit(main())
```

**Implementation Status**: ❌ NOT YET CREATED (blocked until DES completion)

### MED-02: DES Template Creation Prerequisites

**Issue**: Phase 4 assumes `.pre-commit-config-nwave.yaml` and `.des-audit-README.md` exist.

**Remediation**:

Create these templates BEFORE Phase 4 implementation:

**File**: `nWave/templates/.pre-commit-config-nwave.yaml`
```yaml
# Pre-commit hooks configuration for nWave projects with DES
# Install: pip install pre-commit && pre-commit install
# Manual run: pre-commit run --all-files

repos:
  - repo: local
    hooks:
      # DES: Stale phase detection
      - id: check-stale-phases
        name: DES Stale Phase Detection
        entry: python ~/.claude/scripts/check_stale_phases.py
        language: system
        pass_filenames: false
        always_run: true

      # DES: Scope boundary validation
      - id: scope-boundary-check
        name: DES Scope Boundary Validation
        entry: python ~/.claude/scripts/scope_boundary_check.py
        language: system
        pass_filenames: false
        files: '.*'

      # nWave: Step file validation
      - id: validate-step-file
        name: nWave Step File Validation
        entry: python ~/.claude/scripts/validate_step_file.py
        language: system
        files: 'steps/.*\.json$'

  # Standard hooks
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v6.0.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-json
```

**File**: `nWave/templates/.des-audit-README.md`
```markdown
# DES Audit Trail

Immutable audit logs for nWave workflow traceability.

## Structure

- `audit-YYYY-MM-DD.log`: JSONL format with daily rotation
- Append-only (no modifications to existing entries)
- SHA256 content hashing for immutability verification

## Events Logged

- `TASK_INVOCATION_STARTED`: Agent execution begins
- `TASK_INVOCATION_VALIDATED`: Pre-invocation hooks passed
- `PHASE_STARTED`: TDD phase begins (e.g., RED_UNIT, GREEN, REFACTOR)
- `PHASE_COMPLETED`: TDD phase finishes
- `SCOPE_VIOLATION`: File modified outside declared scope
- `TIMEOUT_WARNING`: Phase execution exceeding threshold

## Query Examples

```bash
# Filter violations
grep '"event":"SCOPE_VIOLATION"' audit-*.log | jq .

# Count events by step
jq -r 'select(.event=="SCOPE_VIOLATION") | .step_path' *.log | sort | uniq -c

# View phase execution timeline
jq -r 'select(.event | startswith("PHASE_")) | "\(.timestamp) \(.step_path) \(.phase_name) \(.event)"' audit-*.log
```

## Retention Policy

- Daily logs retained for 90 days
- Archive to `docs/evolution/audit-archive/` after 90 days
- No automatic deletion (manual cleanup only)
```

**Implementation Status**: ❌ NOT YET CREATED (blocked until DES completion)

### MED-04: Priority Assignment Rationale

**Issue**: Plugin priority values lack documented rationale.

**Remediation**: Added inline documentation to each plugin's `priority()` method.

**Updated Documentation**:

- **AgentsPlugin**: Priority 10 (lowest = first) - "Agents are foundational and have no dependencies"
- **CommandsPlugin**: Priority 20 - "Commands depend on agent structure being present"
- **TemplatesPlugin**: Priority 30 - "Templates are standalone, no dependencies"
- **UtilitiesPlugin**: Priority 40 - "Utilities used by DES scripts"
- **DESPlugin**: Priority 50 - "DES depends on templates and utilities being installed first"

**Implementation Status**: ✅ DOCUMENTED in code examples

---

## Rischi e Mitigazioni

| Rischio | Mitigazione | Status |
|---------|-------------|--------|
| **HIGH-02: Circular Import** | Extract module-level functions from existing methods | ✅ RESOLVED |
| **HIGH-01: DES Source Missing** | Document actual/planned DES structure + prerequisites | ✅ RESOLVED |
| **HIGH-03: InstallContext Incomplete** | Add framework_source, project_root, rich_logger fields | ✅ RESOLVED |
| Import path conflicts | Test exhaustive, dual import support transitorio | Ongoing |
| Permission issues lib/ | Fallback graceful, error message chiaro | Ongoing |
| Audit logger write failures | SilentLogger fallback, non-blocking | Ongoing |
| Pre-commit performance | Optimize validators, cache results | Ongoing |

## Criteri di Successo

- ✅ DES module importabile dopo installazione (100% success)
- ✅ Tutti i test TS-1 attraverso TS-6 passing
- ✅ Verifica installazione include DES checks (3/3 passing)
- ✅ Zero breaking changes su installazioni esistenti
- ✅ Audit trail creato al primo `/nw:develop`
- ✅ Documentazione completa e chiara

## Integration Summary: What Gets Reused vs Replaced

### Components REUSED (No Changes)

| Component | Location | How Used in Plugin System |
|-----------|----------|---------------------------|
| BackupManager | `install_nwave.py` ~lines 100-150 | Injected into `InstallContext.backup_manager` |
| InstallationVerifier | `installation_verifier.py` | Injected into `InstallContext.installation_verifier` |
| `_install_agents()` | `install_nwave.py` | Called by `AgentsPlugin.install()` |
| `_install_commands()` | `install_nwave.py` | Called by `CommandsPlugin.install()` |
| `_install_templates()` | `install_nwave.py` | Called by `TemplatesPlugin.install()` |
| `_install_utility_scripts()` | `install_nwave.py` | Called by `UtilitiesPlugin.install()` |
| Build pipeline | `tools/build.py` | Runs BEFORE plugin orchestration |
| Rich output library | Throughout | Used by plugins for formatted output |
| Version tracking | `install_nwave.py` ~lines 200-250 | Available in `InstallContext.current_version` |
| Schema validation | `validate_step_file.py` | Extended for v3.0, still used |

### Components ADDED (New Functionality)

| Component | Location | Purpose |
|-----------|----------|---------|
| `InstallationPlugin` | `plugins/base.py` | Common interface for all plugins |
| `PluginRegistry` | `plugins/registry.py` | Orchestration + dependency resolution |
| `InstallContext` | `plugins/base.py` | Shared context with injected utilities |
| `AgentsPlugin` | `plugins/agents_plugin.py` | Wrapper for existing agent installation |
| `CommandsPlugin` | `plugins/commands_plugin.py` | Wrapper for existing command installation |
| `TemplatesPlugin` | `plugins/templates_plugin.py` | Wrapper for existing template installation |
| `UtilitiesPlugin` | `plugins/utilities_plugin.py` | Wrapper for existing utilities installation |
| `DESPlugin` | `plugins/des_plugin.py` | NEW component (demonstrates extensibility) |

### Behavioral Guarantees

**NO CHANGES to**:
- ✅ File installation locations (`~/.claude/agents/nw/`, `~/.claude/scripts/`, etc.)
- ✅ Backup creation (`~/.claude/backups/nwave-{timestamp}/`)
- ✅ Verification criteria (same checks, same validation)
- ✅ Version tracking logic (same comparison, same upgrade detection)
- ✅ Build pipeline (same `tools/build.py` execution)
- ✅ Error handling patterns (same error messages, same recovery)

**CHANGES to** (orchestration only):
- Execution flow: `install_framework()` now calls `PluginRegistry.install_all()`
- Dependency order: Plugins can declare dependencies (topological sort)
- Extensibility: New components added via plugin registration (no installer modification)

**ADDITIONS**:
- DES module installation (`~/.claude/lib/python/des/`)
- DES utility scripts (`check_stale_phases.py`, `scope_boundary_check.py`)
- DES templates (`.pre-commit-config-nwave.yaml`, `.des-audit-README.md`)
- Plugin dependency resolution framework

## Anti-Patterns to Avoid

**❌ DON'T**:
1. Reimplement installation logic in plugins (call existing methods instead)
2. Remove existing methods before plugins are stable (keep them during migration)
3. Modify BackupManager or InstallationVerifier (reuse as-is)
4. Create custom backup logic in plugins (use context.backup_manager)
5. Skip verification (use context.installation_verifier)
6. Change file installation locations (preserve existing paths)

**✅ DO**:
1. Wrap existing methods in plugins (thin wrapper pattern)
2. Inject existing utilities into InstallContext
3. Call existing methods from plugins (`installer._install_agents()`)
4. Use context.backup_manager for all backup operations
5. Use context.installation_verifier for all verification
6. Preserve existing behavior (same files, same locations, same checks)
7. Test for regressions (compare before/after)
8. Document integration points clearly

## Prossimi Passi

Dopo approvazione:
1. Creare feature branch `feature/plugin-architecture-integration`
2. Implementare Fase 1 (infrastruttura - no installer changes)
3. Implementare Fase 2 (wrapper plugins - call existing methods)
4. Implementare Fase 3 (switchover - change orchestration)
5. Implementare Fase 4 (DESPlugin - demonstrate extensibility)
6. Commit incrementale per ogni fase con test completi
7. PR con:
   - Integration test results (before/after comparison)
   - Backward compatibility validation
   - Regression test suite
8. Merge dopo review
9. Release v1.7.0 con backward compatibility guarantee
