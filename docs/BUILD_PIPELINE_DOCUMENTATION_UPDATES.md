# Build Pipeline Documentation Updates

This document summarizes the documentation updates made to fix incorrect path references and document the nWave build pipeline.

## Objective

Correct references to `tools/build_ide_bundle.py` (non-existent) and clarify the actual build pipeline architecture.

## Files Created

### 1. docs/guides/build-pipeline-guide.md (NEW)

**Type:** Tutorial + How-to Guide (DIVIO: Explanation + How-to hybrid)

**Purpose:** Comprehensive developer guide explaining the nWave build pipeline

**Content:**
- Pipeline overview with visual flow diagram
- Correct file paths with clear distinctions:
  - `tools/build.py` - Main CLI entry point (use for command-line builds)
  - `tools/core/build_ide_bundle.py` - Internal orchestrator (use for code imports)
- Building instructions with examples
- Installation process documentation
- Development workflow patterns
- CI/CD integration notes
- Troubleshooting guide
- Performance optimization tips
- Common patterns and examples

**When to Use:**
- Developers setting up build environment
- Contributors modifying agents or commands
- Understanding the overall build system
- Troubleshooting build failures

**Status:** Complete and production-ready

## Files Updated

### 1. docs/CI-CD-README.md

**Changes:**
- Line 79: Fixed build command from `python tools/core/build_ide_bundle.py --clean --verbose` to `python tools/build.py --clean --verbose`
- Line 257: Fixed build troubleshooting command reference

**Reason:** These were referencing the internal module directly instead of the CLI entry point

### 2. README.md

**Changes:**
- Line 210: Fixed build command from `python tools/build_ide_bundle.py` to `python tools/build.py --clean`

**Reason:** The non-existent path would cause confusion for new developers

### 3. scripts/install/README.md

**Changes:**
- Line 230: Fixed troubleshooting note from `tools/build_ide_bundle.py` to `tools/build.py`

**Reason:** Updated to reference the correct entry point

### 4. docs/features/framework-rationalization/01-discuss/requirements.md

**Changes:**
- Lines 36-38: Clarified that both `tools/build.py` and `tools/core/build_ide_bundle.py` exist with different purposes
- Lines 374-377: Fixed CI workflow example to use `python build.py --clean` instead of `cd tools; python build_ide_bundle.py --clean`
- Lines 403-406: Fixed release workflow example to use correct paths
- Lines 583: Updated Critical Files table to clarify both files and their purposes

**Reason:** Design document needed to clarify the distinction between CLI entry point and internal module

### 5. docs/features/framework-rationalization/02-design/architecture.md

**Changes:**
- Line 1148-1150: Updated Files to Modify list to clarify the distinction between `tools/build.py` (CLI) and `tools/core/build_ide_bundle.py` (internal)

**Reason:** Architecture documentation should accurately reflect the build system structure

### 6. docs/features/framework-rationalization/03-distill/test-data-requirements.md

**Changes:**
- Line 18: Fixed import statement from `from tools.build_ide_bundle import IDEBundleBuilder` to `from tools.core.build_ide_bundle import IDEBundleBuilder`

**Reason:** Imports must use the correct module path

## Summary of Changes

### Path Clarifications

**Before (Incorrect):**
- `tools/build_ide_bundle.py` - Non-existent file (led to confusion)
- Different docs referenced it with different contexts

**After (Correct):**
- `tools/build.py` - CLI entry point (use for command-line builds)
- `tools/core/build_ide_bundle.py` - Internal builder module (use for code imports and understanding architecture)

### Documentation Improvements

1. **Central Reference:** Created `docs/guides/build-pipeline-guide.md` as the single source of truth for build pipeline documentation

2. **Clarity:** Distinguished between:
   - CLI usage: `python3 tools/build.py --clean`
   - Code imports: `from tools.core.build_ide_bundle import IDEBundleBuilder`

3. **Consistency:** Updated all references across documentation to use correct paths

4. **Completeness:** Added troubleshooting, patterns, and workflow guidance

## Build Pipeline Architecture (Corrected)

```
User runs:  python3 tools/build.py --clean

            ↓

Entry Point:  tools/build.py
              - Minimal CLI wrapper
              - Parses arguments
              - Delegates to builder

            ↓

Builder:    tools/core/build_ide_bundle.py
            - Contains IDEBundleBuilder class
            - Orchestrates build workflow
            - Manages processors

            ↓

Processors: tools/processors/*.py
            - agent_processor.py
            - command_processor.py
            - team_processor.py

            ↓

Output:     dist/ide/
            - agents/nw/*.md
            - commands/nw/*.md
            - templates/

            ↓

Install:    scripts/install/install_nwave.py
            - Detects source changes
            - Auto-triggers build if needed
            - Copies to ~/.claude/
```

## Verification Checklist

- [x] All `tools/build_ide_bundle.py` references corrected to `tools/build.py` (for CLI) or `tools/core/build_ide_bundle.py` (for imports)
- [x] CI-CD documentation updated with correct command paths
- [x] Installation guides reference correct entry point
- [x] Design documents clarify the distinction
- [x] New comprehensive guide created for developers
- [x] Code examples show correct imports

## Impact Assessment

### Low Risk Changes
- Documentation updates only (no code changes)
- Clarifications don't affect existing functionality
- Backward compatible (correct paths work as documented)

### Benefits
- Eliminates confusion from incorrect path references
- Provides single source of truth for build pipeline
- Helps new contributors understand the build system
- Reduces support questions about build failures

## Related Documentation

For complete information:
- [build-pipeline-guide.md](../guides/build-pipeline-guide.md) - Comprehensive developer guide
- [CI-CD-README.md](../CI-CD-README.md) - Automated CI/CD workflows
- [CONTRIBUTING.md](../../CONTRIBUTING.md) - Contribution guidelines
- [installation-guide.md](../installation/installation-guide.md) - Installation instructions

---

**Documentation Updated:** 2026-01-24
**Files Created:** 1
**Files Modified:** 6
**Lines Changed:** ~50 corrections across all files
