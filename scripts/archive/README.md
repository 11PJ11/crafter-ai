# Archived Scripts

This directory contains scripts that are no longer actively used but preserved for reference.

## Archived Scripts

### Adversarial Testing (LLM-Based)
- **run-adversarial-tests.py** (2,000+ lines)
- **execute-adversarial-tests.py**

**Reason for archival**: Require active LLM invocation, cannot be automated in CI/CD. Claude Code has embedded safety/compliance. Low value for 2,000+ lines of code.

**Future use**: Can be resurrected if security testing becomes a priority.

### Agent Catalog Conflict Detection
- **agent-catalog-conflict-detection.sh**

**Reason for archival**: References `nWave/catalogs/` directory that doesn't exist. Project evolved to embedded documentation (no separate catalogs).

**Replacement**: Created `validate_readme_index.py` for deterministic README validation instead.

### Duplicate Validators
- **validate-agent-compliance-v2.py** (394 lines)

**Reason for archival**: Merged into `scripts/validation/validate_agents.py`. Single source of truth for agent compliance validation.

### One-Time Migrations
- **migrate_step_files.py** (11KB)

**Reason for archival**: One-time data migration for step file format updates. Migration complete, no longer needed.

## Restoration

If you need to restore any archived script:
1. Check git history: `git log --follow scripts/archive/<script-name>`
2. Copy from archive to appropriate location
3. Update imports and paths as needed
4. Test thoroughly before use

## Deletion Policy

Archived scripts are kept for:
- Historical reference
- Understanding design evolution
- Potential future resurrection

Scripts may be permanently deleted after:
- 1 year in archive with no access
- Confirmed obsolescence
- Team consensus
