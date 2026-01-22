# Workflow Migration Guide

## Current State

The repository currently has **3 workflows**:

1. **`ci.yml`** - Basic CI with pytest (Python 3.11, 3.12)
2. **`release.yml`** - Release automation on version tags
3. **`ci-cd.yml`** (NEW) - Comprehensive CI/CD pipeline

## New Workflow Advantages

The new `ci-cd.yml` provides:

### Enhanced Testing
- ✅ **Broader Python coverage**: 3.8, 3.10, 3.12 (vs. 3.11, 3.12)
- ✅ **Pre-commit validation**: All hooks run automatically
- ✅ **Agent sync verification**: Ensures framework consistency
- ✅ **YAML validation**: Framework catalog structure checks
- ✅ **Documentation version checks**: Prevents version drift
- ✅ **Coverage reporting**: XML and HTML coverage reports

### Better Release Process
- ✅ **Version consistency checks**: Tag must match framework-catalog.yaml
- ✅ **SHA256 checksums**: Automatic checksum generation
- ✅ **Auto-generated release notes**: Comprehensive release documentation
- ✅ **Pre-release detection**: Beta/RC tags marked automatically
- ✅ **Artifact retention**: 90 days for releases (vs. default)

### Improved Developer Experience
- ✅ **Job summaries**: Clear status in GitHub Actions UI
- ✅ **Better error messages**: Specific failure reasons
- ✅ **Conditional execution**: Releases only on tags
- ✅ **Artifact uploads**: Test results and coverage preserved
- ✅ **Comprehensive documentation**: Inline comments explain each step

## Migration Options

### Option 1: Replace Existing Workflows (Recommended)

**Benefits**:
- Single workflow to maintain
- No duplicate runs
- Comprehensive quality gates
- Better resource utilization

**Steps**:
```bash
# Backup existing workflows
mv .github/workflows/ci.yml .github/workflows/ci.yml.backup
mv .github/workflows/release.yml .github/workflows/release.yml.backup

# The new ci-cd.yml is already in place
git add .github/workflows/ci-cd.yml
git add .github/workflows/*.backup
git commit -m "ci: migrate to comprehensive ci-cd.yml workflow"
git push
```

**Rollback if needed**:
```bash
mv .github/workflows/ci.yml.backup .github/workflows/ci.yml
mv .github/workflows/release.yml.backup .github/workflows/release.yml
rm .github/workflows/ci-cd.yml
```

### Option 2: Run in Parallel (Testing Phase)

**Benefits**:
- Test new workflow without disruption
- Compare results side-by-side
- Gradual migration

**Steps**:
1. Keep all three workflows active
2. Monitor runs for 1-2 weeks
3. Compare execution times and results
4. Once confident, disable old workflows:

```yaml
# Add to ci.yml and release.yml
on:
  # Temporarily disabled - testing ci-cd.yml
  workflow_dispatch:  # Manual trigger only
```

### Option 3: Keep Separate (Not Recommended)

**Drawbacks**:
- Duplicate CI runs (wastes resources)
- Confusion about which workflow to trust
- Higher maintenance burden
- Inconsistent quality gates

## Comparison Matrix

| Feature | ci.yml | release.yml | ci-cd.yml (NEW) |
|---------|--------|-------------|-----------------|
| **Python Versions** | 3.11, 3.12 | 3.11 only | 3.8, 3.10, 3.12 |
| **Pre-commit Hooks** | ❌ | ❌ | ✅ |
| **Agent Sync Check** | ❌ | ❌ | ✅ |
| **YAML Validation** | ❌ | ❌ | ✅ |
| **Coverage Reports** | ❌ | ❌ | ✅ XML + HTML |
| **Version Consistency** | ❌ | ❌ | ✅ |
| **Checksums** | ❌ | ❌ | ✅ SHA256 |
| **Release Notes** | ❌ | Basic | ✅ Auto-generated |
| **Pre-release Detection** | ❌ | ❌ | ✅ |
| **Job Summaries** | ❌ | ❌ | ✅ |
| **Artifact Retention** | Default | Default | 14d (tests), 90d (releases) |
| **Documentation** | Minimal | Minimal | ✅ Comprehensive |

## Recommended Action

**Migrate to `ci-cd.yml` and archive old workflows:**

```bash
# 1. Test the new workflow
git add .github/workflows/ci-cd.yml
git commit -m "ci: add comprehensive ci-cd workflow"
git push

# 2. Wait for workflow to complete successfully

# 3. Archive old workflows
mkdir -p .github/workflows/archive
mv .github/workflows/ci.yml .github/workflows/archive/
mv .github/workflows/release.yml .github/workflows/archive/

# 4. Commit migration
git add .github/workflows/
git commit -m "ci: migrate to unified ci-cd.yml workflow

- Replaces ci.yml and release.yml
- Adds comprehensive quality gates
- Improves release automation
- See .github/workflows/MIGRATION.md for details"
git push
```

## Validation Checklist

After migration, verify:

- [ ] CI runs on push to master/develop
- [ ] CI runs on pull requests
- [ ] All 246 tests pass
- [ ] Pre-commit hooks execute successfully
- [ ] Test artifacts uploaded (check Actions tab)
- [ ] Coverage reports generated
- [ ] Release workflow triggers on version tags
- [ ] Release artifacts include all expected files
- [ ] SHA256 checksums generated
- [ ] Release notes auto-generated

## Rollback Plan

If issues arise:

```bash
# Restore old workflows
mv .github/workflows/archive/ci.yml .github/workflows/
mv .github/workflows/archive/release.yml .github/workflows/

# Remove new workflow
rm .github/workflows/ci-cd.yml

# Commit rollback
git add .github/workflows/
git commit -m "ci: rollback to ci.yml + release.yml"
git push
```

## Testing New Workflow

Before full migration, test with:

```bash
# Trigger CI manually (requires workflow_dispatch)
gh workflow run ci-cd.yml

# Or push to a test branch
git checkout -b test-ci-cd
git push origin test-ci-cd

# Watch the run
gh run watch
```

## Questions?

- Review [CI-CD-README.md](../../docs/CI-CD-README.md) for detailed documentation
- Check workflow comments in `ci-cd.yml` for implementation details
- Open an issue if migration assistance needed

---

**Recommendation**: Migrate to `ci-cd.yml` for comprehensive quality gates and better automation.

Migration date: _________
Performed by: _________
Validation complete: ☐
