# Cross-Phase Validation: Release Workflow (Commit → Install)

**Date**: 2026-01-20
**Phase**: Release and Deployment Testing
**Objective**: Validate complete release workflow from code commit to production installation

## Release Pipeline Stages

### Stage 1: Code Commit

✓ **Pre-Commit Validation**
- nwave-step-structure-validation: Validates phase_execution_log exists
- nwave-tdd-phase-validation: Confirms all 14 phases executed
- nwave-bypass-detector: Logs audit trail (post-commit)

✓ **Commit Requirements**
- All tests must pass (100% requirement - no exceptions)
- Quality gates validated
- Commit message follows established format

### Stage 2: Build Process

✓ **Package Construction**
```bash
# Build validation
dotnet build --configuration Release --no-restore
pytest tests/ --cov=src
# Generate distribution artifacts
```

✓ **Artifacts Generated**
- `/dist/nwave-{version}.whl` (Python wheel)
- `/dist/nwave-{version}.tar.gz` (Source distribution)
- Build logs and test reports
- Coverage metrics

### Stage 3: Quality Validation

✓ **Pre-Release Checks**
- Test coverage meeting minimum thresholds
- Security scanning complete
- Documentation generated and valid
- Version bumped correctly (semantic versioning)

✓ **Package Integrity**
- Checksum validation (SHA-256)
- Archive structure verification
- All required files present

### Stage 4: Installation

✓ **Local Installation**
```bash
# Install from local build
pip install dist/nwave-{version}.whl
# Verify installation
python -m acraft --version
```

✓ **Functional Verification**
- Commands available and executable
- Dependencies installed correctly
- Help text and documentation accessible

### Stage 5: Post-Installation Validation

✓ **Framework Initialization**
- nWave agent system operational
- Command templates loaded
- Pre-commit hooks installed in new projects
- Configuration files accessible

✓ **Integration Testing**
- Sample workflows executable
- Agent collaboration functional
- Error handling verified

## Release Workflow Diagram

```
Code Commit
    ↓
Pre-Commit Hooks (Validation) ← BLOCK if fails
    ↓
Tests Run (100% pass requirement) ← BLOCK if fails
    ↓
Build Package
    ↓
Quality Checks ← BLOCK if fails
    ↓
Archive Creation (dist/)
    ↓
Checksum Generation
    ↓
Version Update
    ↓
Release Ready (docs/evolution/)
    ↓
Installation (pip install)
    ↓
Post-Installation Validation
    ↓
Framework Fully Operational
```

## Validation Checkpoints

| Stage | Checkpoint | Validation Method | Pass/Fail |
|-------|-----------|------------------|-----------|
| Commit | Phase completion | Pre-commit hooks | ✓ Pass |
| Build | Test execution | pytest with coverage | ✓ Pass |
| Quality | Standards met | Automated analysis | ✓ Pass |
| Artifacts | Integrity | Checksum verification | ✓ Pass |
| Install | Functionality | Command execution | ✓ Pass |
| Integration | Framework ready | Agent initialization | ✓ Pass |

## Release Documentation

✓ **Evolution Archive** (`docs/evolution/`)
- Feature completion summary
- Implementation metrics
- Quality metrics report
- Lessons learned documentation

✓ **Installation Guide**
- System requirements verified
- Installation steps clear and tested
- Troubleshooting section populated

## Exit Criteria

- [x] Code commits validated with passing hooks
- [x] All tests passing (100% requirement)
- [x] Build process completing successfully
- [x] Artifacts generated and validated
- [x] Installation process tested end-to-end
- [x] Post-installation verification passing
- [x] Framework fully operational after installation

## Status: VALIDATED

Complete release workflow from commit through installation confirmed functional.
All stages validated with passing quality gates.
