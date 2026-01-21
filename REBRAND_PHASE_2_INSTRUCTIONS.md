# nWave Rebranding - Phase 2 Instructions

**Prepared**: 2026-01-21
**Status**: Ready for Execution
**Objective**: Complete bulk updates to remaining ~80 files

---

## Overview

Phase 2 completes the nWave → nWave rebranding by systematically updating all remaining documentation, configuration, and source code files. This should be executed after Phase 1 has been committed to main branch.

## Files to Update in Phase 2

### Documentation Files (40+ files)

#### Installation & Getting Started Guides
- `docs/installation/installation-guide.md`
- `docs/installation/uninstall-guide.md`

#### How-To Guides
- `docs/guides/ci-cd-integration-guide.md`
- `docs/guides/validation-checklist.md`
- Other guide files in `docs/guides/`

#### Troubleshooting
- `docs/troubleshooting/troubleshooting-guide.md`

#### Analysis & Audit Documents
- `docs/analysis/RENAME_MAPPING.md`
- `docs/analysis/DOCUMENTATION_FILENAME_AUDIT.md`
- `docs/analysis/ci-pipeline-investigation.md`
- `docs/analysis/root-cause-analysis.md`
- `docs/analysis/divio-audit/*.md` (all files)

#### Agent Specifications
- `nWave/agents/*.md` (all agent files)

#### Task Documentation
- `nWave/tasks/nw/*.md` (all task files)

#### Data & Research
- `nWave/data/**/*.md` (all data files)

### Configuration & Build Files (15+ files)

#### CI/CD Workflows
- `.github/workflows/ci.yml`
- `.github/workflows/release.yml`

#### Framework Configuration
- `nWave/framework-catalog.yaml`

#### Workflow Templates
- `nWave/templates/*.yaml` (all template files)

#### Data Configuration
- `nWave/data/config/*.yaml`

### Source Code & Scripts (25+ files)

#### Validation Scripts
- `scripts/validation/validate_agents.py`
- `scripts/validation/validate_documentation_versions.py`
- Other validation scripts

#### Framework Tools
- `scripts/framework/create-reviewer-agents.py`

#### Archive Scripts
- `scripts/archive/*.py` (all archived scripts)

#### Test Files
- `tests/validation/cross_phase_validation.py`
- `tests/acceptance/*.py` and `tests/acceptance/*.sh`

#### Build Tools
- `tools/build_ide_bundle.py`
- `tools/*.py` (all tool files)

#### Documentation
- `scripts/README.md`
- `nWave/hooks/README.md`
- `tools/README.md`

---

## Execution Steps

### Step 1: Backup Current State

```bash
# Create backup of Phase 1 completed state
git add .
git commit -m "chore(rebrand): Phase 1 complete - ready for Phase 2

See REBRAND_PHASE_1_SUMMARY.md for details"

# Create tag for reference
git tag rebrand-phase-1-complete
```

### Step 2: Execute Bulk Replacements

#### Method A: Using sed (Recommended - One-liner)

```bash
# Navigate to repository root
cd /mnt/c/Repositories/Projects/nwave

# Execute bulk replacement
find . -type f \( -name "*.md" -o -name "*.py" -o -name "*.yaml" -o -name "*.yml" \) \
  ! -path "./.git/*" \
  ! -path "./.mypy_cache/*" \
  ! -path "./.pytest_cache/*" \
  ! -path "./dist/*" \
  -exec sed -i \
    -e 's/nWave/nWave/g' \
    -e 's/nwave/nwave/g' \
    -e 's/NWAVE/NWAVE/g' \
    -e 's/NWave/NWave/g' \
    -e 's/nWave/nWave/g' \
    -e 's/nwave/nwave/g' \
    {} +

echo "Bulk replacement complete"
```

#### Method B: Using Python Script (More Control)

Create `scripts/rebrand-phase-2.py`:

```python
#!/usr/bin/env python3
"""Phase 2 bulk replacement script for nWave -> nWave rebranding."""

import os
import re
from pathlib import Path

PATTERNS = [
    (r'\bnWave\b', 'nWave'),
    (r'\bnwave\b', 'nwave'),
    (r'\bNWAVE\b', 'NWAVE'),
    (r'\bNWave\b', 'NWave'),
    (r'\bnWave\b', 'nWave'),
    (r'\bnwave\b', 'nwave'),
]

EXCLUDE_DIRS = {'.git', '.mypy_cache', '.pytest_cache', 'dist', '__pycache__'}
INCLUDE_EXTENSIONS = {'.md', '.py', '.yaml', '.yml', '.json'}

def should_process(filepath):
    """Check if file should be processed."""
    path = Path(filepath)
    # Skip excluded directories
    for excluded in EXCLUDE_DIRS:
        if excluded in path.parts:
            return False
    # Only process included extensions
    return path.suffix in INCLUDE_EXTENSIONS

def process_file(filepath):
    """Apply replacements to a single file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        original_content = content
        for pattern, replacement in PATTERNS:
            content = re.sub(pattern, replacement, content)

        if content != original_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
    except Exception as e:
        print(f"Error processing {filepath}: {e}")
    return False

def main():
    """Process all eligible files."""
    root = Path('.')
    updated_count = 0

    for filepath in root.rglob('*'):
        if filepath.is_file() and should_process(str(filepath)):
            if process_file(filepath):
                print(f"✓ Updated: {filepath}")
                updated_count += 1

    print(f"\nTotal files updated: {updated_count}")

if __name__ == '__main__':
    main()
```

Execute:
```bash
python3 scripts/rebrand-phase-2.py
```

### Step 3: Verify Replacements

```bash
# Check for any remaining nWave references (excluding git/cache)
echo "=== Checking for remaining nWave references ==="
grep -r "nWave" . \
  --exclude-dir=.git \
  --exclude-dir=.mypy_cache \
  --exclude-dir=.pytest_cache \
  --exclude-dir=dist \
  2>/dev/null || echo "✓ No nWave references found"

echo ""
echo "=== Checking for remaining nwave references ==="
grep -r "nwave" . \
  --exclude-dir=.git \
  --exclude-dir=.mypy_cache \
  --exclude-dir=.pytest_cache \
  --exclude-dir=dist \
  2>/dev/null || echo "✓ No nwave references found"
```

### Step 4: Run Validation

```bash
# Run pre-commit hooks
echo "Running pre-commit validation..."
pre-commit run --all-files

# Run test suite
echo "Running test suite..."
pytest -v

# Check YAML syntax
echo "Checking YAML files..."
python3 -m yamllint -d relaxed nWave/ .pre-commit-config.yaml .dependency-map.yaml
```

### Step 5: Update Version Tags (if needed)

For files with version tags, update from 1.0.x → 1.1.x:

```bash
# Find files with version tags
grep -r "version.*1\.0\." . \
  --include="*.md" \
  --include="*.py" \
  --include="*.yaml" \
  ! -path "./.git/*" | head -20

# Manual update of remaining 1.0.x versions to 1.1.x
# (verify context before updating)
```

### Step 6: Commit Phase 2 Changes

```bash
# Add all changes
git add .

# Verify changes
git status

# Commit with detailed message
git commit -m "chore(rebrand): Rebrand nWave to nWave Phase 2 - Bulk updates

- Update all documentation files (40+ files)
- Update configuration and build files (15+ files)
- Update source code and scripts (25+ files)
- Verify all cross-references and links
- Validate 5-layer testing framework references
- All pre-commit hooks pass
- All 58 tests passing"

# Create completion tag
git tag rebrand-phase-2-complete
```

---

## Verification Checklist

### Pre-Commit Validation
- [ ] YAML files valid syntax
- [ ] No trailing whitespace
- [ ] No broken links in markdown
- [ ] JSON files valid (if any)

### Code Quality
- [ ] No import errors
- [ ] All Python files syntactically correct
- [ ] All function/class names valid
- [ ] Type hints preserved

### Testing
- [ ] All 58 unit tests pass
- [ ] All 12 integration tests pass
- [ ] No new test failures
- [ ] No skipped tests

### Documentation
- [ ] No orphaned nWave references
- [ ] All links point to valid files
- [ ] Version tags consistent
- [ ] No broken markdown syntax

### Specific Validations

```bash
# Verify no nWave references remain
if grep -r "nWave" . --exclude-dir=.git --exclude-dir=.mypy_cache; then
    echo "ERROR: nWave references found!"
    exit 1
fi

# Verify nWave is now primary term
if ! grep -r "nWave" . --include="README.md" --exclude-dir=.git > /dev/null; then
    echo "ERROR: nWave not found in README!"
    exit 1
fi

# Verify 5-layer testing framework mentioned
if ! grep -r "5-layer\|Layer 5" . --include="*.md" --exclude-dir=.git | grep -q "Mutation"; then
    echo "WARNING: Layer 5 Mutation Testing reference may be missing"
fi

echo "✓ All validations passed"
```

---

## Rollback Plan (if needed)

If issues occur during Phase 2:

```bash
# Option 1: Revert to Phase 1 tag
git reset --hard rebrand-phase-1-complete
git clean -fd

# Option 2: Cherry-pick specific commits
git revert <commit-hash>

# Option 3: Manual cleanup
git restore .  # Discard all changes in working directory
```

---

## Known Challenges & Solutions

### Challenge 1: File Encoding
**Issue**: Some files may have non-UTF-8 encoding
**Solution**: Use `-exec sed -i` with explicit encoding handling or Python script with fallback

```bash
# Safe replacement with encoding handling
find . -name "*.md" -o -name "*.py" | while read file; do
    iconv -f ISO-8859-1 -t UTF-8 "$file" > "$file.tmp" 2>/dev/null && \
    sed -i 's/nWave/nWave/g' "$file.tmp" && \
    mv "$file.tmp" "$file"
done
```

### Challenge 2: Binary Files
**Issue**: sed may try to process binary files
**Solution**: Use `file` command to filter

```bash
find . ! -path "./.git/*" ! -path "./.mypy_cache/*" -type f | \
while read file; do
    if file "$file" | grep -q "text"; then
        sed -i 's/nWave/nWave/g' "$file"
    fi
done
```

### Challenge 3: Large Files
**Issue**: Performance on very large files
**Solution**: Process in parallel with GNU Parallel

```bash
find . -name "*.md" -o -name "*.py" | \
parallel --pipe sed 's/nWave/nWave/g' > /tmp/batch.txt
```

---

## Timing Estimates

- **Bulk Replacement**: 2-5 minutes
- **Verification**: 5-10 minutes
- **Testing**: 10-15 minutes
- **Commit & Tag**: 2-3 minutes

**Total Phase 2 Time**: 20-35 minutes

---

## Post-Phase-2 Tasks

### Immediate (Same Day)
1. Monitor CI/CD pipeline for failures
2. Check installation script functionality
3. Verify documentation rendering

### Next Business Day
1. Deploy to staging environment
2. Test installation on all platforms (Windows, Mac, Linux)
3. Verify all agent activation
4. Validate framework functionality

### Before Production Release
1. Create release notes documenting rebrand
2. Update GitHub repository description
3. Update all external documentation
4. Announce rebrand to users

---

## Contact & Support

For questions during Phase 2 execution:
- Review REBRAND_CHANGELOG.md for detailed change log
- Check REBRAND_PHASE_1_SUMMARY.md for Phase 1 status
- Refer to git history for specific changes per file

---

## Success Criteria

Phase 2 is complete when:
- ✅ All 101 files have been reviewed and updated
- ✅ No nWave references remain (except git history)
- ✅ All pre-commit hooks pass
- ✅ All 58 tests pass
- ✅ Documentation links are valid
- ✅ Version tags are consistent
- ✅ Framework is fully functional
- ✅ Installation works on all platforms

---

**Prepared by**: Lyra (Claude Code Assistant)
**Date**: 2026-01-21
**Status**: Ready for Execution
**Expected Completion**: Within 1 hour of Phase 2 start
