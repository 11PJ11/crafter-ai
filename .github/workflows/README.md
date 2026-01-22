# GitHub Actions Workflows

This directory contains automated workflows for the nWave framework.

## Active Workflows

### `ci-cd.yml` - CI/CD Pipeline

**Purpose**: Comprehensive testing, validation, and automated releases

**Triggers**:
- Push to `master` or `develop`
- Pull requests to `master` or `develop`
- Version tags (e.g., `v1.4.8`)

**Quality Gates**:
1. Pre-commit hooks validation
2. Pytest suite (246 tests)
3. Agent name synchronization
4. YAML validation
5. Documentation version checks
6. Cross-platform testing (Linux, Windows, macOS)
7. Multi-Python version (3.8, 3.10, 3.12)

**Outputs**:
- Test results and coverage reports (on every push/PR)
- GitHub releases with artifacts (on version tags only)

## Quick Commands

### View Workflow Status
```bash
gh run list --workflow=ci-cd.yml
```

### Watch Latest Run
```bash
gh run watch
```

### View Workflow Logs
```bash
gh run view --log
```

### Trigger Manual Run (if enabled)
```bash
gh workflow run ci-cd.yml
```

## Badge Status

Add to README.md:

```markdown
![CI/CD Status](https://github.com/{owner}/{repo}/actions/workflows/ci-cd.yml/badge.svg)
```

## Documentation

See [CI-CD-README.md](../../docs/CI-CD-README.md) for complete documentation.

## Workflow Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   GitHub Event Trigger                   │
│  (push/PR to master/develop OR version tag v*)          │
└─────────────────────┬───────────────────────────────────┘
                      │
                      ▼
        ┌─────────────────────────────┐
        │   Job 1: CI (Matrix)        │
        │   - 9 parallel combinations │
        │   - 5 quality gates         │
        │   - Test suite (246 tests)  │
        └──────────┬──────────────────┘
                   │
         ┌─────────┴─────────┐
         │   All tests pass? │
         └─────────┬─────────┘
                   │
        ┌──────────▼──────────┐
        │  Is version tag?    │
        └──┬──────────────┬───┘
           │              │
           NO             YES
           │              │
           ▼              ▼
      ┌────────┐    ┌──────────────────┐
      │  Stop  │    │ Job 2: Build     │
      └────────┘    │ - IDE bundle     │
                    │ - Packages       │
                    │ - Checksums      │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │ Job 3: Release   │
                    │ - Create release │
                    │ - Upload assets  │
                    │ - Generate notes │
                    └──────────────────┘
```

## File Structure

```
.github/workflows/
├── ci-cd.yml          # Main CI/CD pipeline
└── README.md          # This file
```

## Troubleshooting

### Workflow Not Triggering

**Check**:
- Branch protection rules
- Workflow file syntax: `yamllint ci-cd.yml`
- Repository settings → Actions → General

### Permission Errors

**Fix**: Ensure repository settings allow Actions to:
- Write to repository
- Create releases
- Upload artifacts

Settings → Actions → General → Workflow permissions:
- ✅ Read and write permissions

### Failed Quality Gates

**Debug locally**:
```bash
# Pre-commit
pre-commit run --all-files

# Pytest
pytest tests/ -v

# Agent sync
python scripts/framework/sync_agent_names.py --verify
```

## Best Practices

1. **Never bypass quality gates** in CI
2. **Test locally** before pushing
3. **Version tags** should match `framework-catalog.yaml`
4. **Review workflow logs** for failures
5. **Keep workflows fast** (current: < 10 min total)

## Maintenance

- **Review quarterly**: Update action versions
- **Monitor**: Execution times and cache hit rates
- **Optimize**: Add/remove quality gates as needed

---

Last updated: 2026-01-22
