# Local CI/CD Validation

This document describes how to run CI/CD validation checks locally before pushing code, ensuring that issues are caught early.

## Overview

The local validation environment mirrors the GitHub Actions CI/CD pipeline, allowing you to catch errors before they reach the remote repository.

**Benefits:**
- ✅ Catch YAML syntax errors before commit
- ✅ Validate tests pass locally
- ✅ Ensure build succeeds
- ✅ Check security issues
- ✅ Faster feedback loop
- ✅ Avoid failed CI/CD runs

## Quick Start

### 1. Run Full Local CI Validation

```bash
./scripts/local-ci.sh
```

This runs all the same checks as GitHub Actions CI/CD:
1. YAML file validation
2. Python test suite (pytest)
3. Build process validation
4. Shell script syntax checks
5. Shellcheck linting **NEW**
6. Python linting (Ruff) **NEW**
7. Python formatting check (Ruff) **NEW**
8. Security validation (no hardcoded credentials)
9. nWave framework validation
10. Documentation checks

### 2. Fast Mode (Skip Build)

For quicker validation during development:

```bash
./scripts/local-ci.sh --fast
```

### 3. Verbose Output

For detailed debugging information:

```bash
./scripts/local-ci.sh --verbose
```

## Individual Validation Scripts

### YAML Validation

Validates all YAML files in the repository:

```bash
python3 scripts/validation/validate_yaml_files.py
```

**Verbose mode:**
```bash
python3 scripts/validation/validate_yaml_files.py --verbose
```

This checks:
- ✅ YAML syntax correctness
- ✅ Proper structure (no mixed list/dict indentation)
- ✅ Valid multi-document YAML files
- ✅ Template files (nWave/templates/)

**Exit codes:**
- `0`: All YAML files valid
- `1`: One or more files have errors

### Run Tests Only

```bash
npm test
```

Runs the full pytest test suite (219 tests).

### Run Build Only

```bash
npm run build
```

Builds the nWave IDE bundle from source files.

## Pre-Commit Hooks

Pre-commit hooks automatically run validation before each commit.

### Install Pre-Commit Hooks

```bash
# Install pre-commit (if not already installed)
pip install pre-commit

# Install hooks for this repository
pre-commit install
```

### Pre-Commit Validation Includes:

1. **nWave Version Auto-Increment** - Auto-bumps version when nWave files change
2. **Pytest Test Validation** - Runs all tests
3. **Documentation Version Validation** - Checks doc versions are synchronized
4. **Conflict Detection** - Detects conflicts between related files
5. **Code Formatter Check** - Ensures ruff/mypy are available
6. **YAML File Validation** - Validates all YAML syntax
7. **Shell Syntax Check** - Validates shell script syntax (bash -n) **NEW**
8. **Shellcheck Linting** - Lints shell scripts for best practices **NEW**
9. **Ruff Linting** - Python code linting
10. **Ruff Formatting** - Python code formatting check
11. **Standard Checks** - Trailing whitespace, EOF, merge conflicts, private keys

### Run Pre-Commit Manually

```bash
# Run on all files
pre-commit run --all-files

# Run on staged files only
pre-commit run

# Run specific hook
pre-commit run yaml-validation
```

### Bypass Pre-Commit (Emergency Only)

**⚠️ NOT RECOMMENDED** - Only use in emergencies:

```bash
git commit --no-verify
```

This will be logged in `.git/hooks/pre-commit.log` for audit.

## CI/CD Alignment Matrix - 100% Parity

| Check | Local Script | Pre-Commit | CI/CD | Notes |
|-------|-------------|------------|-------|-------|
| YAML Validation | ✅ local-ci.sh | ✅ yaml-validation hook | ✅ quality-gates | **100% parity** |
| Python Tests | ✅ npm test | ✅ pytest-validation | ✅ build-and-test | **100% parity** |
| Build Process | ✅ npm run build | ❌ (too slow) | ✅ build-and-test | Pre-commit skips (slow) |
| Shell Syntax | ✅ local-ci.sh | ✅ bash -n hook | ✅ quality-gates | **100% parity** |
| Shellcheck | ✅ local-ci.sh | ✅ shellcheck hook | ✅ quality-gates | **100% parity** |
| Ruff Linting | ✅ local-ci.sh | ✅ ruff hook | ✅ quality-gates | **100% parity** |
| Ruff Formatting | ✅ local-ci.sh | ✅ ruff-format hook | ✅ quality-gates | **100% parity** |
| Security Scan | ✅ local-ci.sh | ❌ (security context) | ✅ quality-gates | Pre-commit skips |
| Agent Count | ✅ local-ci.sh | ❌ (informational) | ✅ quality-gates | Pre-commit skips |
| Documentation | ✅ local-ci.sh | ❌ (informational) | ✅ documentation-check | Pre-commit skips |

**Key Achievement**: Every CI check now has a local equivalent - zero gaps!

## Common Issues and Solutions

### Issue: YAML Validation Fails

```
✗ nWave/templates/AGENT_TEMPLATE.yaml
  Line 2043, Col 11: while parsing a block collection, expected <block end>, but found '?'
```

**Cause:** Mixed list items (`-`) with dictionary keys at the same indentation level.

**Solution:**
```yaml
# ❌ WRONG - dictionary key at same level as list items
section:
  - item1
  - item2
  validation: "text"

# ✅ CORRECT - wrap list with 'items:' key
section:
  items:
    - item1
    - item2
  validation: "text"
```

### Issue: Multiple YAML Documents Error

```
expected a single document in the stream but found another document
```

**Cause:** Multiple `---` separators in a file that should be single-document YAML.

**Solution:** Remove extra `---` separators or ensure multi-document YAML is intentional.

### Issue: Tests Pass Locally But Fail in CI

**Cause:** Environment differences between local and CI.

**Solution:**
1. Run `./scripts/local-ci.sh` to ensure all checks pass
2. Verify Python and Node versions match CI (Python 3.12, Node 18.x/20.x)
3. Check that all dependencies are installed: `npm ci`
4. Review `.github/workflows/` for any CI-specific configuration

### Issue: Pre-Commit is Slow

**Solution:**
```bash
# Skip slow hooks for quick commits
SKIP=pytest-validation git commit -m "quick fix"

# Or use local-ci.sh in fast mode instead
./scripts/local-ci.sh --fast
```

## Workflow Integration

### Recommended Development Workflow

1. **Make changes** to code/configuration
2. **Run quick validation**:
   ```bash
   ./scripts/local-ci.sh --fast
   ```
3. **Fix any issues** identified
4. **Run full validation** before commit:
   ```bash
   ./scripts/local-ci.sh
   ```
5. **Commit** (pre-commit hooks run automatically)
6. **Push** to remote (CI/CD runs automatically)

### CI/CD Failure Recovery

If CI/CD fails after push:

1. **Check GitHub Actions logs** for specific error
2. **Run local validation**:
   ```bash
   ./scripts/local-ci.sh --verbose
   ```
3. **Reproduce the error locally**
4. **Fix the issue**
5. **Verify fix with local validation**
6. **Commit and push** again

## Consolidated Workflow Architecture

**Single Unified CI Workflow**: `.github/workflows/ci.yml`

The previous duplicate workflows (`ci.yml` and `ci-cd-pipeline.yml`) have been **consolidated** into a single workflow with these jobs:

1. **build-and-test** - Matrix build (3 OS × 2 Node versions = 6 builds total, not 12)
2. **quality-gates** - YAML, shellcheck, ruff linting, security, agent/command validation
3. **documentation-check** - Required documentation validation
4. **unix-installer-test** - Dry-run installer tests (Ubuntu + macOS)
5. **windows-installer-test** - Dry-run installer test (Windows)
6. **release** - Automated release on version tags
7. **ci-summary** - Final status report

**Zero Duplication**: Matrix builds run once, not twice (6 builds instead of 12).

## Adding New Validation Checks

To add a new validation check that mirrors CI/CD:

1. **Add to CI workflow** (`.github/workflows/ci.yml` → `quality-gates` job)
2. **Add to local-ci.sh** script
3. **Add to pre-commit** (if fast enough - typically <2 seconds)
4. **Update this documentation**

Example:
```bash
# In scripts/local-ci.sh
print_header "10. New Validation Check"
run_check "New check description" "command-to-run"
```

## Maintenance

### Update Pre-Commit Hooks

```bash
# Update to latest versions
pre-commit autoupdate

# Re-install hooks
pre-commit install --install-hooks
```

### Clean Pre-Commit Cache

```bash
pre-commit clean
```

## References

- GitHub Actions Workflows: `.github/workflows/`
- Local CI Script: `scripts/local-ci.sh`
- YAML Validator: `scripts/validation/validate_yaml_files.py`
- Pre-Commit Config: `.pre-commit-config.yaml`
- CI/CD Documentation: `docs/ci-cd/`
