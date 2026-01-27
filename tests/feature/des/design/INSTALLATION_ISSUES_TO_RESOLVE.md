# Installation Architecture Issues to Resolve

**Status**: NEEDS_REVISION
**Document**: installation-architecture.md v1.1
**Reviewer**: solution-architect-reviewer (Morgan)
**Date**: 2026-01-23
**Review Assessment**: NEEDS_REVISION (6 HIGH severity blocking issues)

---

## ⚠️ BLOCKING ISSUES (Must Resolve Before Implementation)

### 1. CLI Wrapper Installation Location Ambiguous
**Severity**: HIGH
**Section**: 2.2.3
**Estimated Effort**: 2-4 hours

**Issue**: No precedence rules for `~/.local/bin` vs `/usr/local/bin`, no Windows strategy specified.

**Impact**:
- Conflicts on multi-user systems
- Unpredictable behavior across platforms
- Installation may fail or install to wrong location

**Recommendation**: Implement platform-specific installation strategy with clear precedence rules.

**Action Required**:
```python
def get_cli_install_path() -> Path:
    """Determine CLI wrapper installation path with platform-specific precedence."""
    if sys.platform == "win32":
        # Windows: Use %LOCALAPPDATA%\Programs\nwave\bin
        return Path(os.environ["LOCALAPPDATA"]) / "Programs" / "nwave" / "bin"
    else:
        # Unix: Prefer ~/.local/bin (user), fallback /usr/local/bin (sudo)
        user_bin = Path.home() / ".local" / "bin"
        if user_bin.exists() or not os.access("/usr/local/bin", os.W_OK):
            return user_bin
        return Path("/usr/local/bin")
```

---

### 2. Venv symlinks=True Conflicts with Windows
**Severity**: HIGH
**Section**: 2.2.1
**Estimated Effort**: 1-2 hours

**Issue**: `venv.create(symlinks=True)` fails on Windows without Developer Mode enabled.

**Impact**:
- Installation fails for standard Windows users
- Requires elevated privileges or Developer Mode
- Inconsistent behavior across platforms

**Recommendation**: Platform-conditional venv creation.

**Action Required**:
```python
def create_virtual_environment(venv_path: Path) -> bool:
    """Create venv with platform-appropriate symlink strategy."""
    use_symlinks = sys.platform != "win32"  # Symlinks on Unix, copies on Windows

    venv.create(
        venv_path,
        system_site_packages=False,
        clear=False,
        symlinks=use_symlinks,  # Platform-conditional
        with_pip=True
    )
```

---

### 3. Import Path Breaking Change Without Compatibility Shim
**Severity**: HIGH
**Section**: 2.3.1 vs 12.3 (contradiction)
**Estimated Effort**: 3-4 hours

**Issue**: Section 12.3 claims "backward compatible" but Section 2.3.1 says "no compatibility shim needed".

**Impact**:
- Existing hooks break after upgrade
- Users experience silent failures
- Migration friction for early adopters

**Recommendation**: Implement compatibility shim OR acknowledge breaking change with migration guide.

**Action Required** (Option 1 - Shim):
```python
# In des/__init__.py
import sys
import importlib

class CompatibilityShim:
    """Redirect old imports (des.*) to new location (nwave.des.*)."""

    def find_module(self, fullname, path=None):
        if fullname.startswith("des."):
            return self
        return None

    def load_module(self, fullname):
        new_name = fullname.replace("des.", "nwave.des.", 1)
        return importlib.import_module(new_name)

sys.meta_path.insert(0, CompatibilityShim())
```

**Action Required** (Option 2 - Breaking Change):
- Update Section 12.3 to document breaking change
- Provide migration guide: `sed -i 's/from des\./from nwave.des./g' ~/.claude/hooks/*.py`
- Add upgrade warning during migration

---

### 4. Backup ID Validation Missing (Security Risk)
**Severity**: HIGH (Security Vulnerability)
**Section**: 10.4
**Estimated Effort**: 2 hours

**Issue**: `restore_backup(backup_id)` vulnerable to directory traversal attack (`../../etc/passwd`).

**Impact**:
- Security vulnerability
- Arbitrary file read/write
- Potential system compromise

**Recommendation**: Validate backup ID with regex whitelist and path traversal prevention.

**Action Required**:
```python
import re
from pathlib import Path

def validate_backup_id(backup_id: str) -> bool:
    """Validate backup ID prevents directory traversal."""
    # Whitelist: YYYYMMDD-HHMMSS format only
    if not re.match(r'^\d{8}-\d{6}$', backup_id):
        raise ValueError(f"Invalid backup ID format: {backup_id}")

    # Prevent directory traversal
    backup_path = BACKUP_DIR / backup_id
    if not backup_path.resolve().is_relative_to(BACKUP_DIR.resolve()):
        raise ValueError(f"Directory traversal detected: {backup_id}")

    return True

def restore_backup(backup_id: str) -> bool:
    """Restore backup with validated ID."""
    validate_backup_id(backup_id)  # Security gate
    backup_path = BACKUP_DIR / backup_id
    # ... restore logic
```

---

### 5. SubagentStop Hook Error Handling Missing
**Severity**: HIGH
**Section**: 3.2
**Estimated Effort**: 2-3 hours

**Issue**: If venv corrupted, hook crashes → Claude Code crashes.

**Impact**:
- Claude Code instability
- Poor user experience
- No graceful degradation

**Recommendation**: Add graceful degradation for hook errors.

**Action Required**:
```python
def check_hook_configured() -> tuple[bool, str]:
    """Verify SubagentStop hook is configured and executable."""
    hook_path = CLAUDE_DIR / "hooks" / "subagent-stop.py"

    if not hook_path.exists():
        return False, "Hook not installed"

    # Test hook execution with graceful error handling
    try:
        result = subprocess.run(
            [get_venv_python(), str(hook_path), "--test"],
            capture_output=True,
            timeout=5,
            check=False  # Don't raise on non-zero exit
        )

        if result.returncode != 0:
            # Hook exists but fails - provide recovery guidance
            return False, f"Hook execution failed: {result.stderr.decode()[:100]}"

        return True, "Hook operational"

    except subprocess.TimeoutExpired:
        return False, "Hook timeout (check venv integrity)"
    except Exception as e:
        # Graceful degradation - don't crash Claude Code
        return False, f"Hook error: {str(e)[:100]}"
```

---

### 6. Compatibility Shim Contradiction
**Severity**: HIGH
**Section**: 2.3.1 vs 12.3
**Estimated Effort**: 1 hour

**Issue**: Two sections contradict each other about compatibility shim.

**Impact**:
- Implementation confusion
- Unclear migration strategy
- Documentation inconsistency

**Recommendation**: Resolve contradiction - choose one approach and update both sections.

**Action Required**:
1. Decide: Implement shim (Option 1) OR acknowledge breaking change (Option 2)
2. Update Section 2.3.1 to match Section 12.3
3. Ensure consistency across both sections
4. Document decision rationale

---

## 📊 Summary

| Category | Count | Total Effort |
|----------|-------|--------------|
| **HIGH Severity (Blocking)** | 6 | 12-17 hours |
| **MEDIUM Severity** | 4 | 6-9 hours |
| **LOW Severity** | 3 | 4-5 hours |
| **TOTAL** | 13 | 22-31 hours |

## ✅ Architecture Strengths

Despite blocking issues, the architecture has significant strengths:
- ✅ Excellent venv isolation using stdlib-only approach
- ✅ Robust backup/rollback strategy with automatic failure recovery
- ✅ Thorough cross-platform considerations
- ✅ Zero-dependency constraint maintained
- ✅ Comprehensive acceptance criteria fulfillment (57 AC)

**Overall Maturity**: 80% - Fundamentally sound, requires issue resolution before implementation.

---

## 🎯 Next Steps

1. **Resolve 6 blocking issues** (12-17 hours estimated)
2. **Re-review architecture** with solution-architect-reviewer
3. **Verify all HIGH severity issues resolved**
4. **Obtain APPROVED status**
5. **Proceed to implementation**

---

**Note**: These issues were identified during systematic architecture review on 2026-01-23. They must be resolved before proceeding to DEVELOP wave implementation.
