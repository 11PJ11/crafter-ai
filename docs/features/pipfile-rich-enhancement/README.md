# Pipfile Enhancement and Rich Console Integration

## Overview

This feature enhances the nWave installer system with the Rich library for improved console output, replacing the legacy `Colors` class with a modern, context-aware logging system.

## Changes Summary

### Production Dependencies
- Added `rich` to `[packages]` section of Pipfile for enhanced terminal rendering

### New Module: `rich_console.py`
Location: `scripts/install/rich_console.py`

Provides three logger types for different execution contexts:
- **RichLogger**: Full Rich styling with spinners, tables, and panels for interactive terminals
- **PlainLogger**: Plain text output without ANSI codes for CI environments
- **SilentLogger**: File-only logging for Claude Code context (no console output)

### Removed: `Colors` class
The legacy `Colors` class has been completely removed from `install_utils.py` and all install scripts. ANSI color handling is now managed by Rich or the individual logger implementations.

## API Reference

### ConsoleFactory

The recommended way to get the appropriate logger:

```python
from scripts.install.rich_console import ConsoleFactory

# Automatically selects logger based on context
logger = ConsoleFactory.create_logger()
logger.info("Installation started")
logger.warn("Warning message")
logger.error("Error occurred")
logger.step("Processing files...")

# Check if Rich is available
if ConsoleFactory.is_rich_available():
    print("Rich features enabled")
```

### RichLogger

Full-featured logger with Rich styling:

```python
from scripts.install.rich_console import RichLogger
from pathlib import Path

# Create logger with optional file logging
logger = RichLogger(log_file=Path("/tmp/install.log"), silent=False)

# Basic logging (green, yellow, red, blue)
logger.info("Information message")     # Green
logger.warn("Warning message")          # Yellow
logger.error("Error message")           # Red
logger.step("Step message")             # Blue

# Progress spinner for long operations
with logger.progress_spinner("Installing framework..."):
    # ... long operation
    pass

# Rich table output
logger.table(
    headers=["Component", "Status", "Count"],
    rows=[
        ["Agents", "OK", "41"],
        ["Commands", "OK", "12"],
    ],
    title="Validation Results"
)

# Rich panel for summaries
logger.panel(
    "Installation completed successfully!\nVersion: 1.2.3",
    title="nWave Framework",
    style="green"
)
```

### PlainLogger

Plain text logger for CI environments (no colors, no spinners):

```python
from scripts.install.rich_console import PlainLogger

logger = PlainLogger(log_file=None, silent=False)
logger.info("CI-safe logging")  # Outputs: [2025-01-30 10:00:00] INFO: CI-safe logging
```

### SilentLogger

File-only logger for Claude Code context:

```python
from scripts.install.rich_console import SilentLogger
from pathlib import Path

logger = SilentLogger(log_file=Path("/tmp/silent.log"))
logger.info("Only written to file, not console")
```

## Context Detection

The `ConsoleFactory` uses `context_detector.py` to automatically select the appropriate logger:

| Context | Logger Type | Behavior |
|---------|-------------|----------|
| Claude Code (`CLAUDE_CODE` env var set) | SilentLogger | File-only, JSON output for machine parsing |
| CI Environment (`GITHUB_ACTIONS`, `GITLAB_CI`, `CI`, `JENKINS_URL`) | PlainLogger | Plain text, no colors |
| Interactive Terminal (TTY) | RichLogger | Full Rich styling |

## Migration Guide

### From `Colors` class

**Before (Legacy):**
```python
from scripts.install.install_utils import Colors

print(f"{Colors.GREEN}Success{Colors.NC}")
print(f"{Colors.RED}Error{Colors.NC}")
```

**After (Rich):**
```python
from scripts.install.rich_console import ConsoleFactory

logger = ConsoleFactory.create_logger()
logger.info("Success")
logger.error("Error")
```

### From direct ANSI codes

**Before:**
```python
print("\033[0;32mSuccess\033[0m")
```

**After:**
```python
from scripts.install.rich_console import RichLogger

logger = RichLogger()
logger.info("Success")
# Or for styled printing
logger.print_styled("Success", style="green")
```

## Fallback Behavior

When Rich is not installed, `RichLogger` gracefully falls back to ANSI color codes:
- Green: `\033[0;32m`
- Yellow: `\033[1;33m`
- Red: `\033[0;31m`
- Blue: `\033[0;34m`

This ensures the installer works even without the Rich dependency.

## Testing

Run the test suite:

```bash
pipenv run pytest tests/unit/test_rich_console.py -v
```

Test coverage includes:
- Logger output for all methods (info, warn, error, step)
- Silent mode behavior
- File logging
- Context-based factory selection
- Rich fallback when unavailable
- PlainLogger ANSI-free output
- SilentLogger console suppression
- Table and panel output
- Progress spinner execution

## Files Changed

| File | Change |
|------|--------|
| `Pipfile` | Added `rich = "*"` to `[packages]` |
| `scripts/install/rich_console.py` | New module (RichLogger, PlainLogger, SilentLogger, ConsoleFactory) |
| `scripts/install/install_utils.py` | Removed `Colors` class |
| `scripts/install/output_formatter.py` | Uses Rich panels instead of ANSI codes |
| `scripts/install/install_nwave.py` | Migrated from Colors to Rich |
| `scripts/install/uninstall_nwave.py` | Migrated from Colors to Rich |
| `scripts/install/update_nwave.py` | Migrated from Colors to Rich |
| `scripts/install/verify_nwave.py` | Migrated from Colors to Rich |
| `scripts/install/enhanced_backup_system.py` | Migrated from Colors to Rich |
| `tests/unit/test_rich_console.py` | New test file (34 test cases) |

## Breaking Changes

- **`Colors` class removed**: Any external code importing `Colors` from `install_utils` will break
- The `Colors` class was internal to install scripts and not part of the public API

## Related Documentation

- [Rich Library Documentation](https://rich.readthedocs.io/)
- [Roadmap](./roadmap.yaml)
