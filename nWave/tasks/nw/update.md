# NW-UPDATE: Update nWave to Latest Release

**Command**: `/nw:update`

## Purpose

Update nWave to the latest GitHub Release safely with full backup protection, checksum validation, and user content preservation.

## Usage

```bash
/nw:update
```

## Overview

The `/nw:update` command performs a safe, atomic update of nWave from GitHub Releases:

1. **Check for updates** - Compare installed version against latest GitHub Release
2. **Display warnings** - Alert on major version changes or local customizations
3. **Create backup** - Full backup of `~/.claude/` before any modifications
4. **Download release** - Fetch the release asset from GitHub
5. **Validate checksum** - Verify SHA256 integrity before installation
6. **Install update** - Replace nWave content while preserving user customizations
7. **Confirm success** - Display completion message

## User Content Preservation

During update, only nWave-prefixed content is replaced:

**Replaced (Core Content):**
- `~/.claude/agents/nw/*`
- `~/.claude/commands/nw/*`
- `~/.claude/templates/nw/*`
- `~/.claude/data/nw/*`
- `~/.claude/checklists/nw/*`

**Preserved (User Content):**
- `~/.claude/agents/<your-custom-agents>/*`
- `~/.claude/commands/<your-custom-commands>/*`
- `~/.claude/CLAUDE.md`
- Any content not prefixed with `nw`

## Safety Features

### Backup Protection
- Full backup created BEFORE any modifications
- Backup location: `~/.claude.backup.{YYYYMMDDHHMMSS}/`
- Rolling retention: Last 3 backups preserved
- Manual rollback possible by copying backup to `~/.claude/`

### Atomic Updates
- Download completes fully before installation begins
- Checksum validated before any files are modified
- Network failures leave installation unchanged

### Warning Prompts
- **Major version change**: "Major version change detected (1.x to 2.x). This may break existing workflows. Continue? [y/N]"
- **Local customizations**: "Local customizations detected. Update will overwrite."

## Output Examples

### Update Available
```
Update available: v1.2.3 -> v1.3.0
Continue with update? [y/N]: y
Update complete.
```

### Already Up-to-Date
```
Already up to date (v1.3.0).
```

### Network Error
```
Unable to check for updates: network error
```

### Checksum Failure
```
Download corrupted (checksum mismatch). Update aborted. Your nWave installation is unchanged.
```

## Prerequisites

| Tool | Purpose | Required |
|------|---------|----------|
| Python 3 | Runtime environment | Yes |
| curl/wget | Download release assets | Yes |
| tar | Extract archive | Yes |
| shasum | Verify checksum | Yes |

## Error Handling

| Scenario | Behavior |
|----------|----------|
| Network unavailable | Error message, installation unchanged |
| Download fails mid-stream | Partial file deleted, installation unchanged |
| Checksum mismatch | Corrupted download deleted, installation unchanged |
| No write permissions | Error with permission fix suggestion |

## Technical Details

### CLI Entry Point
The command delegates to the CLI implementation:
- **File**: `nWave/cli/update_cli.py`
- **Function**: `main()`

### Application Service
- **File**: `nWave/core/versioning/application/update_service.py`
- **Class**: `UpdateService`
- **Method**: `update()`

### Hexagonal Architecture
```
CLI (update_cli.py)              <- Driving Adapter
       |
       v
UpdateService                    <- Application Service
       |
       +---> GitHubAPIPort       <- Driven Port (release metadata)
       +---> DownloadPort        <- Driven Port (fetch assets)
       +---> ChecksumPort        <- Driven Port (validate integrity)
       +---> FileSystemPort      <- Driven Port (backup, install)
```

## Related Commands

- `/nw:version` - Check installed version and update availability
- `/nw:forge` - Build custom local distribution
- `/nw:forge:install` - Install built distribution

## See Also

- [Requirements](docs/features/versioning-release-management/requirements.md) - Full user story for US-002
- [Architecture](docs/features/versioning-release-management/architecture.md) - Hexagonal design details
