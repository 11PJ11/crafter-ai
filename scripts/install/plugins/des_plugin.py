"""DES (Deterministic Execution System) installation plugin."""

import shutil
import subprocess
from pathlib import Path

from .base import InstallationPlugin, InstallContext, PluginResult


class DESPlugin(InstallationPlugin):
    """Plugin for installing DES (Deterministic Execution System).

    Demonstrates extensibility: adding DES requires only plugin registration
    without modifying core installer logic.
    """

    # DES scripts installed to ~/.claude/scripts/
    DES_SCRIPTS = [
        "check_stale_phases.py",
        "scope_boundary_check.py",
    ]

    # DES templates installed to ~/.claude/templates/
    DES_TEMPLATES = [
        ".pre-commit-config-nwave.yaml",
        ".des-audit-README.md",
    ]

    def __init__(self):
        """Initialize DES plugin with name, priority, and dependencies."""
        super().__init__(name="des", priority=50)
        self.dependencies = ["templates", "utilities"]

    def validate_prerequisites(self, context: InstallContext) -> PluginResult:
        """Validate that DES prerequisites exist before installation.

        Checks for:
        1. DES scripts directory at nWave/scripts/des/
        2. DES templates at nWave/templates/

        Returns:
            PluginResult with success=False and clear error message if missing.
        """
        errors = []

        # Check for DES scripts directory
        scripts_dir = self._get_scripts_source_dir(context)
        if not scripts_dir.exists():
            errors.append(
                "DES scripts not found: nWave/scripts/des/. "
                "Ensure prerequisite scripts are created before DES installation."
            )
        else:
            # Check for required script files
            missing_scripts = []
            for script_name in self.DES_SCRIPTS:
                script_path = scripts_dir / script_name
                if not script_path.exists():
                    missing_scripts.append(script_name)
            if missing_scripts:
                errors.append(
                    f"Missing DES scripts: {', '.join(missing_scripts)}. "
                    f"Required scripts: {', '.join(self.DES_SCRIPTS)}"
                )

        # Check for DES templates
        templates_dir = (
            context.project_root / "nWave" / "templates"
            if context.project_root
            else Path("nWave/templates")
        )
        missing_templates = []
        for template_name in self.DES_TEMPLATES:
            template_path = templates_dir / template_name
            if not template_path.exists():
                missing_templates.append(template_name)

        if missing_templates:
            errors.append(
                f"DES templates not found: {', '.join(missing_templates)}. "
                f"Ensure prerequisite templates exist at nWave/templates/ before DES installation."
            )

        if errors:
            return PluginResult(
                success=False,
                plugin_name="des",
                message=f"DES prerequisite validation failed: {errors[0]}",
                errors=errors,
            )

        return PluginResult(
            success=True,
            plugin_name="des",
            message="DES prerequisites validated successfully",
        )

    def _get_scripts_source_dir(self, context: InstallContext) -> Path:
        """Get the source directory for DES scripts."""
        if context.framework_source:
            source_dir = context.framework_source / "scripts" / "des"
            if source_dir.exists():
                return source_dir
        if context.project_root:
            return context.project_root / "nWave" / "scripts" / "des"
        return Path("nWave/scripts/des")

    def install(self, context: InstallContext) -> PluginResult:
        """Install DES module, scripts, and templates.

        Validates prerequisites before installation to ensure graceful failure
        with clear error messages when required files are missing.
        """
        try:
            # Validate prerequisites first - fail fast with clear message
            prereq_result = self.validate_prerequisites(context)
            if not prereq_result.success:
                context.logger.error(
                    f"DES prerequisite check failed: {prereq_result.message}"
                )
                return prereq_result

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
            # Use dist directory if available (build pipeline), fallback to src/
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
            # Use framework source if available, fallback to nWave/scripts/des
            if context.framework_source:
                source_dir = context.framework_source / "scripts" / "des"
                if not source_dir.exists():
                    # Fallback to nWave/scripts/des if framework source doesn't have DES scripts
                    source_dir = context.project_root / "nWave" / "scripts" / "des"
            else:
                source_dir = Path("nWave/scripts/des")

            target_dir = context.claude_dir / "scripts"
            target_dir.mkdir(parents=True, exist_ok=True)

            installed = []
            for script_name in self.DES_SCRIPTS:
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
            # Use project_root for consistent path resolution
            source_dir = context.project_root / "nWave" / "templates"
            target_dir = context.claude_dir / "templates"
            target_dir.mkdir(parents=True, exist_ok=True)

            installed = []
            for template_name in self.DES_TEMPLATES:
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
                    f'import sys; sys.path.insert(0, "{lib_python}"); from des.application import DESOrchestrator',
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
        for script in self.DES_SCRIPTS:
            script_path = context.claude_dir / "scripts" / script
            if not script_path.exists():
                errors.append(f"Missing DES script: {script}")

        # 3. Verify templates present
        for template in self.DES_TEMPLATES:
            template_path = context.claude_dir / "templates" / template
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
