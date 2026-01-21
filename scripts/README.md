<!-- version: 1.4.0 -->

# nWave Scripts Directory

Organized scripts for nWave/nWave framework operations, validation, and installation.

## Directory Structure

```
scripts/
├── validation/          # Python-based validators
│   ├── validate_agents.py          # Agent compliance validation
│   ├── validate_commands.py        # Command template validation
│   ├── validate_steps.py           # Step file validation
│   ├── validate_formatter_env.py   # Dev environment checks
│   ├── validate_readme_index.py    # Documentation sync validation
│   └── coordinator.py              # Orchestrates all validators
│
├── framework/           # nWave framework operations
│   ├── release_package.py          # Release packaging orchestrator
│   ├── release_packager.py         # Core packaging system
│   ├── release_validation.py       # Release error detection
│   └── validate_tdd_phases_ci.py   # CI/CD TDD validation
│
├── hooks/               # Pre-commit hooks
│   ├── validate-structure.py       # Structure validation coordinator
│   ├── version-bump.sh             # Auto version increment
│   ├── validate-tests.sh           # Pytest wrapper
│   ├── validate-docs.sh            # Doc version validation
│   └── detect-conflicts.sh         # Agent/command coupling detection
│
├── install/             # Installation tools (Python cross-platform + legacy shell)
│   ├── install_nwave.py          # Framework installation (RECOMMENDED)
│   ├── uninstall_nwave.py        # Framework removal (RECOMMENDED)
│   ├── update_nwave.py           # Update pipeline (RECOMMENDED)
│   ├── enhanced_backup_system.py    # Backup management (RECOMMENDED)
│   ├── install_utils.py             # Shared utilities module
│   ├── install-nwave.sh          # Legacy shell version
│   ├── uninstall-nwave.sh        # Legacy shell version
│   ├── update-nwave.sh           # Legacy shell version
│   ├── enhanced-backup-system.sh    # Legacy shell version
│   └── README.md                    # Detailed installation docs
│
├── archive/             # Historical/unused scripts
│   ├── run-adversarial-tests.py    # LLM-based testing (archived)
│   ├── execute-adversarial-tests.py # LLM-based testing (archived)
│   ├── agent-catalog-conflict-detection.sh # Outdated design (archived)
│   ├── validate-agent-compliance-v2.py # Merged into v1 (archived)
│   └── migrate_step_files.py       # One-time migration (archived)
│
└── build-ide-bundle.sh  # IDE bundle build script
```

## Usage

### Validation

Run all validators:
```bash
python scripts/validation/coordinator.py
```

Run fast validators only:
```bash
python scripts/validation/coordinator.py --fast
```

Run individual validators:
```bash
python scripts/validation/validate_agents.py
python scripts/validation/validate_commands.py
python scripts/validation/validate_steps.py
```

### Framework Operations

Package a release:
```bash
python scripts/framework/release_package.py
```

Validate TDD phases in CI:
```bash
python scripts/framework/validate_tdd_phases_ci.py
```

### Pre-Commit Hooks

Pre-commit hooks are automatically executed via `.pre-commit-config.yaml`.

Manual execution:
```bash
pre-commit run --all-files
```

### Installation

Install nWave framework (Python - cross-platform):
```bash
python scripts/install/install_nwave.py
```

Update framework:
```bash
python scripts/install/update_nwave.py --backup
```

Uninstall framework:
```bash
python scripts/install/uninstall_nwave.py --backup
```

Legacy shell versions (Unix/Mac only):
```bash
bash scripts/install/install-nwave.sh  # Legacy
bash scripts/install/update-nwave.sh   # Legacy
bash scripts/install/uninstall-nwave.sh # Legacy
```

See `scripts/install/README.md` for detailed installation documentation.

## Integration

All validators are integrated as pre-commit hooks. See `.pre-commit-config.yaml` for configuration.

## Development

When adding new validators:
1. Create validator in `scripts/validation/`
2. Add to `coordinator.py`
3. Update `scripts/hooks/validate-structure.py` if needed
4. Add pre-commit hook entry in `.pre-commit-config.yaml`

## Cross-Platform Support

- **Validators**: Python 3.7+ (Windows, Mac, Linux)
- **Installation**: Python 3.7+ (Windows, Mac, Linux) - **RECOMMENDED**
  - Legacy shell scripts available for Unix/Mac (not maintained)
- **Hooks**: Mixed shell + Python (Python preferred)

## Testing

Validators have tests in `tests/`:
- `tests/test_release_packaging.py`
- `tests/test_release_validation.py`
- `tests/test_step_file_format.py`
- `tests/acceptance/test_validator_acceptance.py`
