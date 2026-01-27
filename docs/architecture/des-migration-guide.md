# DES Module Directory Structure Migration Guide

**Status**: Ready for Implementation
**Complexity**: Moderate
**Estimated Time**: 2-3 hours
**Risk Level**: Low (changes confined to DES module, extensive test suite)

---

## Overview

This guide provides step-by-step instructions for migrating the DES module from mixed concerns (Option A) to hexagonal layers organization (Option B).

### Key Principles

1. **No functional changes** - Only organizational restructuring
2. **Tests guide the migration** - Full test suite validates at each step
3. **Backward compatibility** - Use convenience imports in `__init__.py` to minimize external changes
4. **Verification at each step** - Run tests after each phase

---

## Phase 1: Prepare for Migration (No code changes yet)

### Step 1.1: Create Feature Branch

```bash
git checkout -b feature/des-restructuring-hexagonal-layers
git branch -u origin/determinism
```

### Step 1.2: Document Current Import Patterns

```bash
# Find all imports from src.des
grep -r "from src.des" /mnt/c/Repositories/Projects/ai-craft --include="*.py" > /tmp/des-imports-before.txt

# Count by pattern
grep -r "from src.des\.orchestrator" /mnt/c/Repositories/Projects/ai-craft --include="*.py" | wc -l
grep -r "from src.des\.turn_counter" /mnt/c/Repositories/Projects/ai-craft --include="*.py" | wc -l
grep -r "from src.des\.ports" /mnt/c/Repositories/Projects/ai-craft --include="*.py" | wc -l
grep -r "from src.des\.adapters" /mnt/c/Repositories/Projects/ai-craft --include="*.py" | wc -l
```

### Step 1.3: Verify Current Tests Pass

```bash
pytest tests/des/ -v
pytest tests/acceptance/ -v --tb=short
```

**Expected**: All tests pass ✓

---

## Phase 2: Create New Directory Structure

### Step 2.1: Create Directories (use absolute paths)

```bash
# Create domain layer
mkdir -p /mnt/c/Repositories/Projects/ai-craft/src/des/domain

# Create application layer
mkdir -p /mnt/c/Repositories/Projects/ai-craft/src/des/application

# Create ports with subcategories
mkdir -p /mnt/c/Repositories/Projects/ai-craft/src/des/ports/driver_ports
mkdir -p /mnt/c/Repositories/Projects/ai-craft/src/des/ports/driven_ports

# Create adapters with subcategories
mkdir -p /mnt/c/Repositories/Projects/ai-craft/src/des/adapters/drivers/hooks
mkdir -p /mnt/c/Repositories/Projects/ai-craft/src/des/adapters/drivers/validators
mkdir -p /mnt/c/Repositories/Projects/ai-craft/src/des/adapters/driven/filesystem
mkdir -p /mnt/c/Repositories/Projects/ai-craft/src/des/adapters/driven/time
mkdir -p /mnt/c/Repositories/Projects/ai-craft/src/des/adapters/driven/logging
mkdir -p /mnt/c/Repositories/Projects/ai-craft/src/des/adapters/driven/config
mkdir -p /mnt/c/Repositories/Projects/ai-craft/src/des/adapters/driven/task_invocation
```

### Step 2.2: Verify Directories Created

```bash
tree -L 4 /mnt/c/Repositories/Projects/ai-craft/src/des
```

Expected output structure:
```
src/des/
├── adapters/
│   ├── driven/
│   │   ├── config/
│   │   ├── filesystem/
│   │   ├── logging/
│   │   ├── task_invocation/
│   │   └── time/
│   └── drivers/
│       ├── hooks/
│       └── validators/
├── application/
├── domain/
├── ports/
│   ├── driven_ports/
│   └── driver_ports/
```

### Step 2.3: Create Test Directories

```bash
mkdir -p /mnt/c/Repositories/Projects/ai-craft/tests/des/unit/domain
mkdir -p /mnt/c/Repositories/Projects/ai-craft/tests/des/unit/application
mkdir -p /mnt/c/Repositories/Projects/ai-craft/tests/des/unit/ports
mkdir -p /mnt/c/Repositories/Projects/ai-craft/tests/des/integration
mkdir -p /mnt/c/Repositories/Projects/ai-craft/tests/des/acceptance
mkdir -p /mnt/c/Repositories/Projects/ai-craft/tests/des/e2e
```

---

## Phase 3: Move Files to New Locations

### Step 3.1: Move Domain Layer Files

```bash
# Move turn management domain logic
mv /mnt/c/Repositories/Projects/ai-craft/src/des/turn_counter.py \
   /mnt/c/Repositories/Projects/ai-craft/src/des/domain/turn_counter.py

mv /mnt/c/Repositories/Projects/ai-craft/src/des/turn_config.py \
   /mnt/c/Repositories/Projects/ai-craft/src/des/domain/turn_config.py

# Move timeout tracking domain logic
mv /mnt/c/Repositories/Projects/ai-craft/src/des/timeout_monitor.py \
   /mnt/c/Repositories/Projects/ai-craft/src/des/domain/timeout_monitor.py

# Move validation domain logic
mv /mnt/c/Repositories/Projects/ai-craft/src/des/invocation_limits_validator.py \
   /mnt/c/Repositories/Projects/ai-craft/src/des/domain/invocation_limits_validator.py
```

### Step 3.2: Move Application Layer Files

```bash
# Move orchestrator
mv /mnt/c/Repositories/Projects/ai-craft/src/des/orchestrator.py \
   /mnt/c/Repositories/Projects/ai-craft/src/des/application/orchestrator.py

# Move config loader (application service)
mv /mnt/c/Repositories/Projects/ai-craft/src/des/config_loader.py \
   /mnt/c/Repositories/Projects/ai-craft/src/des/application/config_loader.py

# Move validator (application service)
mv /mnt/c/Repositories/Projects/ai-craft/src/des/validator.py \
   /mnt/c/Repositories/Projects/ai-craft/src/des/application/validator.py

# Move hooks (could stay as file or move later - intermediate step)
mv /mnt/c/Repositories/Projects/ai-craft/src/des/hooks.py \
   /mnt/c/Repositories/Projects/ai-craft/src/des/application/hooks.py
```

### Step 3.3: Reorganize Ports

```bash
# Move PRIMARY (driver) ports
mv /mnt/c/Repositories/Projects/ai-craft/src/des/ports/hook_port.py \
   /mnt/c/Repositories/Projects/ai-craft/src/des/ports/driver_ports/hook_port.py

mv /mnt/c/Repositories/Projects/ai-craft/src/des/ports/validator_port.py \
   /mnt/c/Repositories/Projects/ai-craft/src/des/ports/driver_ports/validator_port.py

# Move SECONDARY (driven) ports
mv /mnt/c/Repositories/Projects/ai-craft/src/des/ports/filesystem_port.py \
   /mnt/c/Repositories/Projects/ai-craft/src/des/ports/driven_ports/filesystem_port.py

mv /mnt/c/Repositories/Projects/ai-craft/src/des/ports/time_provider_port.py \
   /mnt/c/Repositories/Projects/ai-craft/src/des/ports/driven_ports/time_provider_port.py

mv /mnt/c/Repositories/Projects/ai-craft/src/des/ports/logging_port.py \
   /mnt/c/Repositories/Projects/ai-craft/src/des/ports/driven_ports/logging_port.py

mv /mnt/c/Repositories/Projects/ai-craft/src/des/ports/config_port.py \
   /mnt/c/Repositories/Projects/ai-craft/src/des/ports/driven_ports/config_port.py

mv /mnt/c/Repositories/Projects/ai-craft/src/des/ports/task_invocation_port.py \
   /mnt/c/Repositories/Projects/ai-craft/src/des/ports/driven_ports/task_invocation_port.py
```

### Step 3.4: Reorganize Adapters

```bash
# Move PRIMARY adapters (drivers)
mv /mnt/c/Repositories/Projects/ai-craft/src/des/adapters/real_hook.py \
   /mnt/c/Repositories/Projects/ai-craft/src/des/adapters/drivers/hooks/real_hook.py

mv /mnt/c/Repositories/Projects/ai-craft/src/des/adapters/real_validator.py \
   /mnt/c/Repositories/Projects/ai-craft/src/des/adapters/drivers/validators/real_validator.py

# Move SECONDARY adapters (driven)
mv /mnt/c/Repositories/Projects/ai-craft/src/des/adapters/real_filesystem.py \
   /mnt/c/Repositories/Projects/ai-craft/src/des/adapters/driven/filesystem/real_filesystem.py

mv /mnt/c/Repositories/Projects/ai-craft/src/des/adapters/system_time.py \
   /mnt/c/Repositories/Projects/ai-craft/src/des/adapters/driven/time/system_time.py

mv /mnt/c/Repositories/Projects/ai-craft/src/des/adapters/structured_logger.py \
   /mnt/c/Repositories/Projects/ai-craft/src/des/adapters/driven/logging/structured_logger.py

mv /mnt/c/Repositories/Projects/ai-craft/src/des/adapters/silent_logger.py \
   /mnt/c/Repositories/Projects/ai-craft/src/des/adapters/driven/logging/silent_logger.py

mv /mnt/c/Repositories/Projects/ai-craft/src/des/adapters/environment_config_adapter.py \
   /mnt/c/Repositories/Projects/ai-craft/src/des/adapters/driven/config/environment_config_adapter.py

mv /mnt/c/Repositories/Projects/ai-craft/src/des/adapters/in_memory_config_adapter.py \
   /mnt/c/Repositories/Projects/ai-craft/src/des/adapters/driven/config/in_memory_config_adapter.py

mv /mnt/c/Repositories/Projects/ai-craft/src/des/adapters/claude_code_task_adapter.py \
   /mnt/c/Repositories/Projects/ai-craft/src/des/adapters/driven/task_invocation/claude_code_task_adapter.py

mv /mnt/c/Repositories/Projects/ai-craft/src/des/adapters/mocked_task_adapter.py \
   /mnt/c/Repositories/Projects/ai-craft/src/des/adapters/driven/task_invocation/mocked_task_adapter.py
```

### Step 3.5: Create __init__.py Files

**Create domain __init__.py:**
```bash
cat > /mnt/c/Repositories/Projects/ai-craft/src/des/domain/__init__.py << 'EOF'
"""Domain layer - Core business logic independent of external concerns."""

from src.des.domain.turn_counter import TurnCounter
from src.des.domain.timeout_monitor import TimeoutMonitor
from src.des.domain.turn_config import TurnLimitConfig, ConfigLoader
from src.des.domain.invocation_limits_validator import InvocationLimitsValidator, InvocationLimitsResult

__all__ = [
    "TurnCounter",
    "TimeoutMonitor",
    "TurnLimitConfig",
    "ConfigLoader",
    "InvocationLimitsValidator",
    "InvocationLimitsResult",
]
EOF
```

**Create application __init__.py:**
```bash
cat > /mnt/c/Repositories/Projects/ai-craft/src/des/application/__init__.py << 'EOF'
"""Application layer - Orchestration and business process management."""

from src.des.application.orchestrator import DESOrchestrator, ExecuteStepResult

__all__ = [
    "DESOrchestrator",
    "ExecuteStepResult",
]
EOF
```

**Create ports/driver_ports __init__.py:**
```bash
cat > /mnt/c/Repositories/Projects/ai-craft/src/des/ports/driver_ports/__init__.py << 'EOF'
"""Driver ports - Inbound interfaces (how external systems call the application)."""

from src.des.ports.driver_ports.hook_port import HookPort, HookResult
from src.des.ports.driver_ports.validator_port import ValidatorPort, ValidationResult

__all__ = [
    "HookPort",
    "HookResult",
    "ValidatorPort",
    "ValidationResult",
]
EOF
```

**Create ports/driven_ports __init__.py:**
```bash
cat > /mnt/c/Repositories/Projects/ai-craft/src/des/ports/driven_ports/__init__.py << 'EOF'
"""Driven ports - Outbound interfaces (how the application calls external systems)."""

from src.des.ports.driven_ports.filesystem_port import FileSystemPort
from src.des.ports.driven_ports.time_provider_port import TimeProvider
from src.des.ports.driven_ports.logging_port import LoggingPort
from src.des.ports.driven_ports.task_invocation_port import TaskInvocationPort
from src.des.ports.driven_ports.config_port import ConfigPort

__all__ = [
    "FileSystemPort",
    "TimeProvider",
    "LoggingPort",
    "TaskInvocationPort",
    "ConfigPort",
]
EOF
```

**Create adapters/drivers __init__.py:**
```bash
cat > /mnt/c/Repositories/Projects/ai-craft/src/des/adapters/drivers/__init__.py << 'EOF'
"""Primary adapters (drivers) - Entry points and inbound interfaces."""
EOF
```

**Create adapters/driven __init__.py:**
```bash
cat > /mnt/c/Repositories/Projects/ai-craft/src/des/adapters/driven/__init__.py << 'EOF'
"""Secondary adapters (driven) - Infrastructure and external integrations."""
EOF
```

---

## Phase 4: Update Internal Imports

### Step 4.1: Update Imports in Domain Files

**File**: `/mnt/c/Repositories/Projects/ai-craft/src/des/domain/timeout_monitor.py`

Update import:
```python
# OLD
from src.des.ports.time_provider_port import TimeProvider

# NEW
from src.des.ports.driven_ports.time_provider_port import TimeProvider
```

### Step 4.2: Update Imports in Application Files

**File**: `/mnt/c/Repositories/Projects/ai-craft/src/des/application/orchestrator.py`

Update imports:
```python
# OLD imports
from src.des.ports.hook_port import HookPort, HookResult
from src.des.ports.validator_port import ValidatorPort, ValidationResult
from src.des.ports.filesystem_port import FileSystemPort
from src.des.ports.time_provider_port import TimeProvider
from src.des.turn_counter import TurnCounter
from src.des.timeout_monitor import TimeoutMonitor
from src.des.invocation_limits_validator import InvocationLimitsValidator, InvocationLimitsResult

# NEW imports
from src.des.ports.driver_ports.hook_port import HookPort, HookResult
from src.des.ports.driver_ports.validator_port import ValidatorPort, ValidationResult
from src.des.ports.driven_ports.filesystem_port import FileSystemPort
from src.des.ports.driven_ports.time_provider_port import TimeProvider
from src.des.domain.turn_counter import TurnCounter
from src.des.domain.timeout_monitor import TimeoutMonitor
from src.des.domain.invocation_limits_validator import InvocationLimitsValidator, InvocationLimitsResult
```

Update adapter imports in `create_with_defaults()`:
```python
# OLD
from src.des.adapters.real_hook import RealSubagentStopHook
from src.des.adapters.real_validator import RealTemplateValidator
from src.des.adapters.real_filesystem import RealFileSystem
from src.des.adapters.system_time import SystemTimeProvider

# NEW
from src.des.adapters.drivers.hooks.real_hook import RealSubagentStopHook
from src.des.adapters.drivers.validators.real_validator import RealTemplateValidator
from src.des.adapters.driven.filesystem.real_filesystem import RealFileSystem
from src.des.adapters.driven.time.system_time import SystemTimeProvider
```

### Step 4.3: Update Imports in Adapter Files

**File**: `/mnt/c/Repositories/Projects/ai-craft/src/des/adapters/drivers/hooks/real_hook.py`

```python
# OLD
from src.des.ports.hook_port import HookPort, HookResult
from src.des.application.hooks import HookResult  # if used

# NEW
from src.des.ports.driver_ports.hook_port import HookPort, HookResult
```

**File**: `/mnt/c/Repositories/Projects/ai-craft/src/des/adapters/driven/time/system_time.py`

```python
# OLD
from src.des.ports.time_provider_port import TimeProvider

# NEW
from src.des.ports.driven_ports.time_provider_port import TimeProvider
```

### Step 4.4: Create Backward Compatibility __init__.py

**File**: `/mnt/c/Repositories/Projects/ai-craft/src/des/__init__.py`

Create convenience imports to minimize breaking changes:
```python
"""DES (Deterministic Execution System) module.

This module provides orchestration for command-origin task filtering with
deterministic turn counting, timeout monitoring, and validation.

Convenience exports for backward compatibility:
- Import from src.des for public API
- Import from src.des.{domain,application,ports,adapters} for specific layers
"""

# Application layer - Public API
from src.des.application.orchestrator import DESOrchestrator, ExecuteStepResult

# Domain layer - Core logic
from src.des.domain.turn_counter import TurnCounter
from src.des.domain.timeout_monitor import TimeoutMonitor
from src.des.domain.turn_config import TurnLimitConfig, ConfigLoader
from src.des.domain.invocation_limits_validator import InvocationLimitsValidator, InvocationLimitsResult

# Ports - Abstractions
from src.des.ports.driver_ports.hook_port import HookPort, HookResult
from src.des.ports.driver_ports.validator_port import ValidatorPort, ValidationResult
from src.des.ports.driven_ports.filesystem_port import FileSystemPort
from src.des.ports.driven_ports.time_provider_port import TimeProvider
from src.des.ports.driven_ports.logging_port import LoggingPort
from src.des.ports.driven_ports.task_invocation_port import TaskInvocationPort
from src.des.ports.driven_ports.config_port import ConfigPort

# Adapters - Implementations
from src.des.adapters.drivers.hooks.real_hook import RealSubagentStopHook
from src.des.adapters.drivers.validators.real_validator import RealTemplateValidator
from src.des.adapters.driven.filesystem.real_filesystem import RealFileSystem
from src.des.adapters.driven.time.system_time import SystemTimeProvider
from src.des.adapters.driven.logging.structured_logger import StructuredLogger
from src.des.adapters.driven.logging.silent_logger import SilentLogger
from src.des.adapters.driven.config.environment_config_adapter import EnvironmentConfigAdapter
from src.des.adapters.driven.config.in_memory_config_adapter import InMemoryConfigAdapter
from src.des.adapters.driven.task_invocation.claude_code_task_adapter import ClaudeCodeTaskAdapter
from src.des.adapters.driven.task_invocation.mocked_task_adapter import MockedTaskAdapter

__all__ = [
    # Application
    "DESOrchestrator",
    "ExecuteStepResult",
    # Domain
    "TurnCounter",
    "TimeoutMonitor",
    "TurnLimitConfig",
    "ConfigLoader",
    "InvocationLimitsValidator",
    "InvocationLimitsResult",
    # Ports
    "HookPort",
    "HookResult",
    "ValidatorPort",
    "ValidationResult",
    "FileSystemPort",
    "TimeProvider",
    "LoggingPort",
    "TaskInvocationPort",
    "ConfigPort",
    # Adapters
    "RealSubagentStopHook",
    "RealTemplateValidator",
    "RealFileSystem",
    "SystemTimeProvider",
    "StructuredLogger",
    "SilentLogger",
    "EnvironmentConfigAdapter",
    "InMemoryConfigAdapter",
    "ClaudeCodeTaskAdapter",
    "MockedTaskAdapter",
]
```

### Step 4.5: Use Automated Search/Replace for External Imports

```bash
# Find all external files importing from src.des
grep -r "from src.des import\|from src.des\." /mnt/c/Repositories/Projects/ai-craft --include="*.py" \
  --exclude-dir=src/des | cut -d: -f1 | sort | uniq > /tmp/files-to-update.txt

# For orchestrator imports
sed -i 's/from src\.des import DESOrchestrator/from src.des import DESOrchestrator/g' $(cat /tmp/files-to-update.txt)

# For turn_counter imports (if not already using convenience import)
sed -i 's/from src\.des\.turn_counter/from src.des.domain.turn_counter/g' $(cat /tmp/files-to-update.txt)
```

---

## Phase 5: Update Tests

### Step 5.1: Move Test Doubles

```bash
# Test doubles remain in adapters/ but create __init__ files
cat > /mnt/c/Repositories/Projects/ai-craft/tests/des/adapters/__init__.py << 'EOF'
"""Test doubles - Mock implementations of ports for testing."""
EOF
```

### Step 5.2: Update Test Imports

Update all test files to use new import paths.

**Example**: Update `tests/unit/des/test_orchestrator.py` (if exists):
```python
# OLD
from src.des.orchestrator import DESOrchestrator

# NEW
from src.des.application.orchestrator import DESOrchestrator
from tests.des.adapters.mocked_hook import MockedHook
from tests.des.adapters.mocked_time import MockedTimeProvider
```

### Step 5.3: Create Symbolic Link in tests/ (Optional)

To help with test imports:
```bash
ln -s /mnt/c/Repositories/Projects/ai-craft/tests/des/adapters \
      /mnt/c/Repositories/Projects/ai-craft/tests/adapters_des 2>/dev/null || true
```

---

## Phase 6: Verification

### Step 6.1: Check File Organization

```bash
# Verify new structure exists
find /mnt/c/Repositories/Projects/ai-craft/src/des -type f -name "*.py" | sort

# Expected files in new locations:
# src/des/domain/turn_counter.py
# src/des/domain/timeout_monitor.py
# src/des/application/orchestrator.py
# src/des/ports/driver_ports/hook_port.py
# src/des/adapters/drivers/hooks/real_hook.py
# etc.
```

### Step 6.2: Run Full Test Suite

```bash
# Unit tests
pytest /mnt/c/Repositories/Projects/ai-craft/tests/des/ -v --tb=short

# Acceptance tests
pytest /mnt/c/Repositories/Projects/ai-craft/tests/acceptance/ -v --tb=short

# Integration tests
pytest /mnt/c/Repositories/Projects/ai-craft/tests/integration/ -v --tb=short 2>/dev/null || true
```

**Expected**: All tests pass ✓

### Step 6.3: Check for Import Errors

```bash
# Try importing from convenience module
python3 -c "from src.des import DESOrchestrator, TurnCounter; print('✓ Imports work')"

# Try importing from new paths
python3 -c "from src.des.application.orchestrator import DESOrchestrator; print('✓ Application imports work')"

python3 -c "from src.des.domain.turn_counter import TurnCounter; print('✓ Domain imports work')"

python3 -c "from src.des.ports.driver_ports.hook_port import HookPort; print('✓ Ports imports work')"

python3 -c "from src.des.adapters.drivers.hooks.real_hook import RealSubagentStopHook; print('✓ Adapter imports work')"
```

### Step 6.4: Verify Circular Dependencies

```bash
# Use tools to check for circular imports
python3 -m pip install pydeps 2>/dev/null || true

# Generate dependency graph
pydeps /mnt/c/Repositories/Projects/ai-craft/src/des --no-show 2>/dev/null || true
```

---

## Phase 7: Commit and Documentation

### Step 7.1: Stage Changes

```bash
cd /mnt/c/Repositories/Projects/ai-craft

# Stage all changes
git add -A

# Review changes
git status
```

### Step 7.2: Create Commit

```bash
git commit -m "refactor(des): Reorganize module structure to hexagonal layers

BREAKING CHANGE: Internal import paths have changed. See MIGRATION.md for details.

Changes:
- Move domain logic to src/des/domain/ (turn_counter, timeout_monitor, etc.)
- Move application services to src/des/application/ (orchestrator, services)
- Reorganize ports: driver_ports/ (inbound) and driven_ports/ (outbound)
- Reorganize adapters: drivers/ (primary) and driven/ (secondary)
- Create backward compatibility imports in src/des/__init__.py

Benefits:
- Explicit hexagonal architecture in file system
- Clear layer separation and responsibilities
- Improved code discoverability
- Better test organization
- Enforces architectural discipline

Migration:
- Existing code can use 'from src.des import X' (unchanged)
- New code should use specific layer imports for clarity
- See docs/architecture/des-migration-guide.md for details

Tests: All passing (unit, integration, acceptance)
"
```

### Step 7.3: Update Documentation

Update `/mnt/c/Repositories/Projects/ai-craft/docs/ARCHITECTURE.md` to include:

```markdown
## DES Module Structure

The DES (Deterministic Execution System) module follows hexagonal architecture:

### Layer Organization

- **domain/**: Core business logic (independent of external concerns)
- **application/**: Orchestration and business process services
- **ports/**: Abstract interfaces (what the core needs)
  - driver_ports/: Inbound interfaces (how external systems call us)
  - driven_ports/: Outbound interfaces (how we call external systems)
- **adapters/**: Concrete implementations (specific technologies)
  - drivers/: Primary adapters (entry points)
  - driven/: Secondary adapters (dependencies)

### Importing

For backward compatibility, use convenience imports:
```python
from src.des import DESOrchestrator, TurnCounter
```

For clarity in new code, use explicit layer imports:
```python
from src.des.application.orchestrator import DESOrchestrator
from src.des.domain.turn_counter import TurnCounter
```

See docs/architecture/des-directory-structure-analysis.md for detailed analysis.
```

### Step 7.4: Push Changes

```bash
git push origin feature/des-restructuring-hexagonal-layers
```

---

## Rollback Procedure (If Needed)

If migration encounters issues:

```bash
# Reset to before migration
git reset --hard HEAD~1

# Return to original branch
git checkout determinism

# Delete feature branch
git branch -D feature/des-restructuring-hexagonal-layers
```

---

## Validation Checklist

- [ ] All directories created in new structure
- [ ] All files moved to new locations
- [ ] All __init__.py files created with proper exports
- [ ] All internal imports updated to new paths
- [ ] External API preserved via convenience imports in src/des/__init__.py
- [ ] All unit tests pass
- [ ] All integration tests pass
- [ ] All acceptance tests pass
- [ ] No circular import errors
- [ ] Commit message documents the change
- [ ] Documentation updated

---

## Post-Migration Guidelines

### For Future Development

1. **Add new domain logic**: Place in `src/des/domain/`
2. **Add new application service**: Place in `src/des/application/`
3. **Add new port abstraction**: Place in `src/des/ports/driver_ports/` or `src/des/ports/driven_ports/`
4. **Add new adapter**:
   - If it's an inbound interface (entry point) → `src/des/adapters/drivers/{domain}/`
   - If it's an outbound integration → `src/des/adapters/driven/{concern}/`

### Code Review Focus

During code review of DES changes, verify:
1. Domain logic has no external dependencies
2. Adapters only import from ports
3. Application imports from domain + ports (never adapters)
4. Test structure mirrors source structure
5. New __init__.py files export public API

---

## Success Criteria

✓ All tests pass without modification
✓ No breaking changes to external API (backward-compatible through __init__.py)
✓ Directory structure clearly shows hexagonal layers
✓ Developers can easily locate where to add new code
✓ Documentation updated with new structure
