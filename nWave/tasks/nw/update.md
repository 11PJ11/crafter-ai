# NW-UPDATE: Update nWave to Latest Release

**Wave**: CROSS_WAVE
**Command**: `/nw:update`

## Overview

Update nWave to the latest GitHub Release with backup protection, checksum validation, and user content preservation. Delegates to `nWave/cli/update_cli.py`.

## Usage

```bash
/nw:update
```

## Update Flow

1. Compare installed version against latest GitHub Release
2. Warn on major version changes or local customizations
3. Create full backup of `~/.claude/` before modifications
4. Download and validate release asset (SHA256 checksum)
5. Replace nWave content while preserving user customizations
6. Confirm success

## Content Boundaries

**Replaced** (nWave core): `~/.claude/{agents,commands,templates,data,checklists}/nw/*`

**Preserved** (user content): Everything not prefixed with `nw`, including `~/.claude/CLAUDE.md`

## Safety

- Backup at `~/.claude.backup.{YYYYMMDDHHMMSS}/` (last 3 retained)
- Atomic: download completes and checksum validates before any files change
- Network failures leave installation unchanged

## Prerequisites

Python 3, curl/wget, tar, shasum

## Technical Entry Points

- **CLI**: `nWave/cli/update_cli.py` -> `main()`
- **Service**: `nWave/core/versioning/application/update_service.py` -> `UpdateService.update()`

## Related Commands

- `/nw:version` - Check installed version
