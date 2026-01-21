# nWave Scripts Directory

Organized scripts for AI-Craft/nWave framework operations, validation, and installation.

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
├── install/             # Installation tools (shell-based, Python conversion planned)
│   ├── install-ai-craft.sh         # Framework installation
│   ├── uninstall-ai-craft.sh       # Framework removal
│   ├── update-ai-craft.sh          # Update pipeline
│   └── enhanced-backup-system.sh   # Backup management
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

Install AI-Craft framework:
```bash
bash scripts/install/install-ai-craft.sh
```

Update framework:
```bash
bash scripts/install/update-ai-craft.sh
```

Uninstall framework:
```bash
bash scripts/install/uninstall-ai-craft.sh
```

## Integration

All validators are integrated as pre-commit hooks. See `.pre-commit-config.yaml` for configuration.

## Development

When adding new validators:
1. Create validator in `scripts/validation/`
2. Add to `coordinator.py`
3. Update `scripts/hooks/validate-structure.py` if needed
4. Add pre-commit hook entry in `.pre-commit-config.yaml`

## Cross-Platform Support

- **Validators**: Python 3.8+ (Windows, Mac, Linux)
- **Installation**: Shell scripts (Unix/Mac only - Python conversion planned)
- **Hooks**: Mixed shell + Python

## Testing

Validators have tests in `tests/`:
- `tests/test_release_packaging.py`
- `tests/test_release_validation.py`
- `tests/test_step_file_format.py`
- `tests/acceptance/test_validator_acceptance.py`
