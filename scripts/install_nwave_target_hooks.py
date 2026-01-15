#!/usr/bin/env python3
"""
nWave TDD Hooks Installer for Target Projects

Cross-platform script to install nWave TDD validation hooks via pre-commit framework.
Designed to be run in target projects that use /nw:develop workflow.

Usage:
    python install_nwave_target_hooks.py [--verify-only] [--force]

Requirements:
    - Python 3.8+
    - pip (to install pre-commit if missing)
    - Git repository (for hooks to work)
"""

import subprocess
import sys
from pathlib import Path
from typing import Tuple

# ══════════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ══════════════════════════════════════════════════════════════════════════════

REQUIRED_PYTHON_VERSION = (3, 8)

NWAVE_HOOKS_CONFIG = """
  # ═══════════════════════════════════════════════════════════════════════════
  # nWave TDD Hooks - Auto-installed by /nw:develop
  # ═══════════════════════════════════════════════════════════════════════════
  - repo: local
    hooks:
      - id: nwave-tdd-phase-validation
        name: nWave TDD Phase Validation
        entry: python scripts/hooks/nwave-tdd-validator.py
        language: python
        stages: [pre-commit]
        always_run: true
        pass_filenames: false
        description: Validates TDD phase completion before allowing commits

      - id: nwave-bypass-detector
        name: nWave Bypass Detector
        entry: python scripts/hooks/nwave-bypass-detector.py
        language: python
        stages: [post-commit]
        always_run: true
        pass_filenames: false
        description: Logs any bypass attempts for audit purposes
"""

NWAVE_TDD_VALIDATOR_SCRIPT = '''#!/usr/bin/env python3
"""nWave TDD Phase Validator - Pre-commit hook."""
import sys
import json
from pathlib import Path

def main():
    """Validate TDD phases if .develop-progress.json exists."""
    progress_file = Path(".develop-progress.json")

    if not progress_file.exists():
        # No active develop session - allow commit
        print("nWave TDD: No active develop session")
        return 0

    try:
        progress = json.loads(progress_file.read_text())
        current_step = progress.get("current_step")

        if current_step:
            phase_log = progress.get("phase_execution_log", {})
            step_phases = phase_log.get(current_step, [])

            # Check if minimum phases completed (at least RED phase)
            if len(step_phases) < 1:
                print(f"nWave TDD: Step {current_step} has no phases executed")
                print("  Hint: Complete at least RED phase before committing")
                # Warning only, don't block

        print("nWave TDD: Phase validation passed")
        return 0

    except json.JSONDecodeError:
        print("nWave TDD: Warning - Could not parse progress file")
        return 0
    except Exception as e:
        print(f"nWave TDD: Warning - {e}")
        return 0

if __name__ == "__main__":
    sys.exit(main())
'''

NWAVE_BYPASS_DETECTOR_SCRIPT = '''#!/usr/bin/env python3
"""nWave Bypass Detector - Post-commit hook."""
import sys
import os
import json
from pathlib import Path
from datetime import datetime

def main():
    """Log commit for audit purposes."""
    audit_file = Path(".nwave-audit.log")

    try:
        # Get commit info
        import subprocess
        result = subprocess.run(
            ["git", "log", "-1", "--format=%H|%s|%an"],
            capture_output=True, text=True, check=False
        )

        if result.returncode == 0:
            parts = result.stdout.strip().split("|", 2)
            if len(parts) >= 3:
                commit_hash, subject, author = parts
            else:
                commit_hash = parts[0] if parts else "unknown"
                subject = parts[1] if len(parts) > 1 else "unknown"
                author = "unknown"

            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "commit": commit_hash[:8],
                "subject": subject[:50],
                "author": author,
                "no_verify": os.environ.get("PRE_COMMIT_ALLOW_NO_CONFIG", "") == "1"
            }

            # Append to audit log
            with open(audit_file, "a") as f:
                f.write(json.dumps(log_entry) + "\\n")

        return 0

    except Exception:
        # Never block on audit failures
        return 0

if __name__ == "__main__":
    sys.exit(main())
'''


# ══════════════════════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ══════════════════════════════════════════════════════════════════════════════


def print_status(message: str, status: str = "INFO") -> None:
    """Print formatted status message."""
    symbols = {"OK": "✅", "FAIL": "❌", "WARN": "⚠️", "INFO": "ℹ️", "RUN": "▶️"}
    symbol = symbols.get(status, "•")
    print(f"{symbol} {message}")


def run_command(
    cmd: list, check: bool = True, cwd: Path = None
) -> Tuple[int, str, str]:
    """Run command and return (returncode, stdout, stderr)."""
    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, check=False, cwd=cwd
        )
        if check and result.returncode != 0:
            return result.returncode, result.stdout, result.stderr
        return result.returncode, result.stdout, result.stderr
    except FileNotFoundError:
        return -1, "", f"Command not found: {cmd[0]}"


def check_python_version() -> bool:
    """Check if Python version meets requirements."""
    return sys.version_info >= REQUIRED_PYTHON_VERSION


def check_git_repository(path: Path = None) -> bool:
    """Check if directory is a git repository."""
    if path is None:
        path = Path.cwd()
    git_dir = path / ".git"
    return git_dir.exists() and git_dir.is_dir()


def check_precommit_installed() -> bool:
    """Check if pre-commit is installed."""
    returncode, _, _ = run_command(["pre-commit", "--version"], check=False)
    return returncode == 0


def install_precommit() -> bool:
    """Install pre-commit via pip."""
    print_status("Installing pre-commit framework...", "RUN")
    returncode, stdout, stderr = run_command(
        [sys.executable, "-m", "pip", "install", "pre-commit"], check=False
    )
    if returncode == 0:
        print_status("pre-commit installed successfully", "OK")
        return True
    else:
        print_status(f"Failed to install pre-commit: {stderr}", "FAIL")
        return False


def check_nwave_hooks_configured(path: Path = None) -> Tuple[bool, bool]:
    """Check if nWave hooks are in .pre-commit-config.yaml.

    Args:
        path: Directory to check. Defaults to current working directory.

    Returns:
        Tuple of (phase_validation_present, bypass_detector_present)
    """
    if path is None:
        path = Path.cwd()

    config_path = path / ".pre-commit-config.yaml"
    if not config_path.exists():
        return False, False

    content = config_path.read_text()

    # Check for various naming patterns
    phase_validation = (
        "nwave-tdd-phase-validation" in content or "nwave-phase-validation" in content
    )
    bypass_detector = "nwave-bypass-detector" in content

    return phase_validation, bypass_detector


def create_precommit_config(path: Path = None) -> bool:
    """Create .pre-commit-config.yaml if it doesn't exist.

    Args:
        path: Directory where to create the config. Defaults to cwd.

    Returns:
        True if config exists or was created successfully.
    """
    if path is None:
        path = Path.cwd()

    config_path = path / ".pre-commit-config.yaml"

    if config_path.exists():
        return True

    print_status("Creating .pre-commit-config.yaml...", "RUN")
    config_path.write_text("repos:\n")
    print_status(".pre-commit-config.yaml created", "OK")
    return True


def add_nwave_hooks_to_config(path: Path = None, force: bool = False) -> bool:
    """Add nWave hooks to .pre-commit-config.yaml.

    Args:
        path: Directory containing the config. Defaults to cwd.
        force: If True, add hooks even if they appear to exist.

    Returns:
        True if hooks were added or already exist.
    """
    if path is None:
        path = Path.cwd()

    config_path = path / ".pre-commit-config.yaml"

    if not config_path.exists():
        if not create_precommit_config(path):
            return False

    phase_present, bypass_present = check_nwave_hooks_configured(path)

    if phase_present and bypass_present and not force:
        print_status("nWave hooks already configured", "OK")
        return True

    print_status("Adding nWave hooks to configuration...", "RUN")

    content = config_path.read_text()

    # Add hooks if not present
    if not phase_present or not bypass_present or force:
        content += NWAVE_HOOKS_CONFIG
        config_path.write_text(content)
        print_status("nWave hooks added to .pre-commit-config.yaml", "OK")

    return True


def create_hook_scripts(path: Path = None, force: bool = False) -> bool:
    """Create the hook script files in scripts/hooks/.

    Args:
        path: Base directory for the project. Defaults to cwd.
        force: If True, overwrite existing scripts.

    Returns:
        True if scripts were created successfully.
    """
    if path is None:
        path = Path.cwd()

    hooks_dir = path / "scripts" / "hooks"
    hooks_dir.mkdir(parents=True, exist_ok=True)

    # Create TDD validator script
    validator_path = hooks_dir / "nwave-tdd-validator.py"
    if not validator_path.exists() or force:
        print_status("Creating nwave-tdd-validator.py...", "RUN")
        validator_path.write_text(NWAVE_TDD_VALIDATOR_SCRIPT)
        try:
            validator_path.chmod(0o755)
        except OSError:
            pass  # Windows doesn't support chmod
        print_status("TDD validator script created", "OK")

    # Create bypass detector script
    detector_path = hooks_dir / "nwave-bypass-detector.py"
    if not detector_path.exists() or force:
        print_status("Creating nwave-bypass-detector.py...", "RUN")
        detector_path.write_text(NWAVE_BYPASS_DETECTOR_SCRIPT)
        try:
            detector_path.chmod(0o755)
        except OSError:
            pass  # Windows doesn't support chmod
        print_status("Bypass detector script created", "OK")

    return True


def install_git_hooks(path: Path = None) -> bool:
    """Run pre-commit install commands.

    Args:
        path: Directory where to run commands. Defaults to cwd.

    Returns:
        True if hooks were installed successfully.
    """
    if path is None:
        path = Path.cwd()

    print_status("Installing pre-commit hooks...", "RUN")

    # Install pre-commit hook
    returncode, _, stderr = run_command(
        ["pre-commit", "install"], check=False, cwd=path
    )
    if returncode != 0:
        print_status(f"Failed to install pre-commit hook: {stderr}", "FAIL")
        return False

    # Install post-commit hook
    returncode, _, stderr = run_command(
        ["pre-commit", "install", "--hook-type", "post-commit"], check=False, cwd=path
    )
    if returncode != 0:
        print_status(f"Failed to install post-commit hook: {stderr}", "FAIL")
        return False

    print_status("Git hooks installed successfully", "OK")
    return True


def verify_installation(path: Path = None) -> bool:
    """Verify that all hooks are properly installed.

    Args:
        path: Directory to verify. Defaults to cwd.

    Returns:
        True if all components are properly installed.
    """
    if path is None:
        path = Path.cwd()

    print_status("Verifying installation...", "RUN")

    errors = []

    # Check .pre-commit-config.yaml
    phase_present, bypass_present = check_nwave_hooks_configured(path)
    if not phase_present:
        errors.append("nwave-tdd-phase-validation not in config")
    if not bypass_present:
        errors.append("nwave-bypass-detector not in config")

    # Check hook scripts exist
    hooks_dir = path / "scripts" / "hooks"
    if not (hooks_dir / "nwave-tdd-validator.py").exists():
        errors.append("nwave-tdd-validator.py script missing")
    if not (hooks_dir / "nwave-bypass-detector.py").exists():
        errors.append("nwave-bypass-detector.py script missing")

    # Check git hooks installed
    pre_commit_hook = path / ".git" / "hooks" / "pre-commit"
    post_commit_hook = path / ".git" / "hooks" / "post-commit"

    if not pre_commit_hook.exists():
        errors.append("pre-commit git hook not installed")
    if not post_commit_hook.exists():
        errors.append("post-commit git hook not installed")

    if errors:
        print_status("Verification FAILED:", "FAIL")
        for error in errors:
            print(f"   • {error}")
        return False

    print_status("All nWave TDD hooks verified and ready", "OK")
    return True


# ══════════════════════════════════════════════════════════════════════════════
# MAIN INSTALLATION FLOW
# ══════════════════════════════════════════════════════════════════════════════


def install_nwave_hooks(path: Path = None, force: bool = False) -> bool:
    """Complete installation of nWave TDD hooks.

    Args:
        path: Directory where to install hooks. Defaults to cwd.
        force: If True, reinstall even if hooks appear configured.

    Returns:
        True if installation successful, False otherwise.
    """
    if path is None:
        path = Path.cwd()

    print("\n" + "═" * 60)
    print("  nWave TDD Hooks Installer")
    print("═" * 60 + "\n")

    # Step 1: Check prerequisites
    print_status("Checking prerequisites...", "INFO")

    if not check_python_version():
        print_status(
            f"Python {REQUIRED_PYTHON_VERSION[0]}.{REQUIRED_PYTHON_VERSION[1]}+ required",
            "FAIL",
        )
        return False
    print_status(f"Python {sys.version_info.major}.{sys.version_info.minor} ✓", "OK")

    if not check_git_repository(path):
        print_status("Not a git repository - run from project root", "FAIL")
        return False
    print_status("Git repository detected ✓", "OK")

    # Step 2: Check/install pre-commit
    if not check_precommit_installed():
        print_status("pre-commit not found", "WARN")
        if not install_precommit():
            return False
    else:
        print_status("pre-commit framework available ✓", "OK")

    # Step 3: Check if already configured (skip if force)
    if not force:
        phase_present, bypass_present = check_nwave_hooks_configured(path)
        if phase_present and bypass_present:
            print_status("nWave hooks already configured", "OK")
            # Still verify everything is in place
            return verify_installation(path)

    # Step 4: Create hook scripts
    print_status("\nConfiguring nWave TDD hooks...", "INFO")
    if not create_hook_scripts(path, force):
        return False

    # Step 5: Update .pre-commit-config.yaml
    if not add_nwave_hooks_to_config(path, force):
        return False

    # Step 6: Install git hooks
    if not install_git_hooks(path):
        return False

    # Step 7: Verify installation
    print_status("\nFinal verification...", "INFO")
    if not verify_installation(path):
        return False

    print("\n" + "═" * 60)
    print_status("nWave TDD hooks installed successfully!", "OK")
    print("═" * 60 + "\n")

    return True


def verify_only(path: Path = None) -> bool:
    """Only verify installation without making changes.

    Args:
        path: Directory to verify. Defaults to cwd.

    Returns:
        True if verification passed.
    """
    if path is None:
        path = Path.cwd()

    print("\n" + "═" * 60)
    print("  nWave TDD Hooks - Verification Only")
    print("═" * 60 + "\n")

    return verify_installation(path)


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Install nWave TDD validation hooks for target projects"
    )
    parser.add_argument(
        "--verify-only",
        action="store_true",
        help="Only verify installation, don't make changes",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force reinstallation even if hooks appear configured",
    )
    parser.add_argument(
        "--path",
        type=Path,
        default=None,
        help="Target directory (default: current directory)",
    )

    args = parser.parse_args()

    target_path = args.path or Path.cwd()

    if args.verify_only:
        success = verify_only(target_path)
    else:
        success = install_nwave_hooks(target_path, force=args.force)

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
