# AI-Craft Framework Uninstallation Guide

Complete guide for removing the AI-Craft ATDD agent framework from your system.

## Overview

The AI-Craft framework consists of 41+ specialized AI agents, commands, configuration files, and supporting infrastructure installed in your global Claude configuration directory. This guide provides comprehensive instructions for complete removal.

## ⚠️ Important Warnings

- **Irreversible Action**: Uninstallation permanently removes all AI-Craft components
- **Custom Configurations Lost**: Any customizations or local changes will be deleted
- **Backup Recommended**: Use the `--backup` option to preserve your installation before removal
- **System Impact**: Removal affects all projects that use AI-Craft commands globally

## Quick Uninstall

For immediate removal without backup:

### Windows (PowerShell)
```powershell
.\uninstall-ai-craft.ps1 -Force
```

### Windows (Command Prompt)
```cmd
uninstall-ai-craft.bat --force
```

### Linux/Mac
```bash
./uninstall-ai-craft.sh --force
```

## Safe Uninstall with Backup

Recommended approach that creates a backup before removal:

### Windows (PowerShell)
```powershell
.\uninstall-ai-craft.ps1 -Backup
```

### Windows (Command Prompt)
```cmd
uninstall-ai-craft.bat --backup
```

### Linux/Mac
```bash
./uninstall-ai-craft.sh --backup
```

## What Gets Removed

The uninstall scripts remove all AI-Craft components:

### Agent Files
- **Location**: `~/.claude/agents/cai/`
- **Contents**: All 41+ specialized agents across 9 categories:
  - Requirements Analysis (5 agents)
  - Architecture Design (3 agents) 
  - Test Design (1 agent)
  - Development (1 agent)
  - Quality Validation (8 agents)
  - Refactoring (2 agents)
  - Coordination (11 agents)
  - Observability (4 agents)
  - Experimentation (4 agents)
  - Configuration (1 constants.md file)

### Command Files
- **Location**: `~/.claude/commands/cai/`
- **Contents**: All AI-Craft commands including:
  - `cai/atdd` - Main ATDD workflow command
  - Supporting command infrastructure (20 command files)

### Configuration Files
- **ai-craft-manifest.txt** - Installation manifest and metadata
- **ai-craft-install.log** - Installation history and logs
- **constants.md** - Framework configuration (if not in cai subdirectory)

### Backup Directories
- **Location**: `~/.claude/backups/ai-craft-*`
- **Contents**: All previous AI-Craft installation backups
- **Note**: Current uninstall backup (if created) is preserved

### Project State Files
- **Location**: `~/.claude/projects/*ai-craft*`
- **Contents**: AI-Craft related project state and metadata

## Uninstall Scripts Reference

### Windows Batch Script (`uninstall-ai-craft.bat`)

```cmd
# Interactive uninstall with confirmation
uninstall-ai-craft.bat

# Create backup before removal
uninstall-ai-craft.bat --backup

# Force removal without prompts
uninstall-ai-craft.bat --force

# Show help information
uninstall-ai-craft.bat --help
```

**Features**:
- Interactive confirmation prompts
- Optional backup creation
- Comprehensive validation
- Detailed logging
- Color-coded output
- Error handling and recovery

### PowerShell Script (`uninstall-ai-craft.ps1`)

```powershell
# Interactive uninstall with confirmation
.\uninstall-ai-craft.ps1

# Create backup before removal  
.\uninstall-ai-craft.ps1 -Backup

# Force removal without prompts
.\uninstall-ai-craft.ps1 -Force

# Show help information
.\uninstall-ai-craft.ps1 -Help
```

**Features**:
- PowerShell native parameter handling
- Rich console formatting
- Comprehensive error handling
- Progress indicators
- Detailed validation
- Cross-platform PowerShell support

### Bash Script (`uninstall-ai-craft.sh`)

```bash
# Interactive uninstall with confirmation
./uninstall-ai-craft.sh

# Create backup before removal
./uninstall-ai-craft.sh --backup

# Force removal without prompts  
./uninstall-ai-craft.sh --force

# Show help information
./uninstall-ai-craft.sh --help
```

**Features**:
- POSIX compliance
- Color-coded terminal output
- Signal handling
- Comprehensive validation
- Detailed error reporting
- Cross-platform compatibility

## Backup and Recovery

### Backup Creation

When using the `--backup` option, a complete backup is created at:
```
~/.claude/backups/ai-craft-uninstall-YYYYMMDD-HHMMSS/
```

**Backup Contents**:
- Complete agents/cai directory structure
- Complete commands/cai directory structure
- Configuration files (manifest, logs)
- Backup manifest with metadata

### Recovery from Backup

To restore from an uninstall backup:

1. **Locate Backup Directory**:
   ```bash
   ls ~/.claude/backups/ai-craft-uninstall-*
   ```

2. **Restore Agents**:
   ```bash
   cp -r ~/.claude/backups/ai-craft-uninstall-*/agents/cai ~/.claude/agents/
   ```

3. **Restore Commands**:
   ```bash
   cp -r ~/.claude/backups/ai-craft-uninstall-*/commands/cai ~/.claude/commands/
   ```

4. **Restore Configuration**:
   ```bash
   cp ~/.claude/backups/ai-craft-uninstall-*/ai-craft-manifest.txt ~/.claude/
   cp ~/.claude/backups/ai-craft-uninstall-*/ai-craft-install.log ~/.claude/
   ```

### Manual Backup

To create a manual backup before uninstall:

```bash
# Create backup directory
BACKUP_DIR="$HOME/.claude/backups/manual-backup-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$BACKUP_DIR"

# Backup agents and commands
cp -r "$HOME/.claude/agents/cai" "$BACKUP_DIR/agents/" 2>/dev/null || true
cp -r "$HOME/.claude/commands/cai" "$BACKUP_DIR/commands/" 2>/dev/null || true

# Backup configuration files
cp "$HOME/.claude/ai-craft-manifest.txt" "$BACKUP_DIR/" 2>/dev/null || true
cp "$HOME/.claude/ai-craft-install.log" "$BACKUP_DIR/" 2>/dev/null || true
```

## Manual Uninstall

If scripts are not available, manual removal steps:

### 1. Remove Agent Files
```bash
# Remove AI-Craft agents
rm -rf ~/.claude/agents/cai

# Remove agents directory if empty
rmdir ~/.claude/agents 2>/dev/null || true
```

### 2. Remove Command Files
```bash
# Remove AI-Craft commands
rm -rf ~/.claude/commands/cai

# Remove commands directory if empty
rmdir ~/.claude/commands 2>/dev/null || true
```

### 3. Remove Configuration Files
```bash
# Remove configuration and log files
rm -f ~/.claude/ai-craft-manifest.txt
rm -f ~/.claude/ai-craft-install.log
```

### 4. Remove Backup Directories
```bash
# Remove all AI-Craft backups
rm -rf ~/.claude/backups/ai-craft-*
```

### 5. Remove Project Files
```bash
# Remove AI-Craft project state files
rm -rf ~/.claude/projects/*ai-craft*
```

## Verification

### Check Complete Removal

After uninstall, verify removal:

```bash
# Check for remaining AI-Craft files
find ~/.claude -name "*ai-craft*" -o -name "*cai*" 2>/dev/null
```

Expected result: No output (complete removal) or only uninstall-related files.

### Common Remaining Files

These files are **expected** after uninstall:
- `ai-craft-uninstall.log` - Uninstall process log
- `ai-craft-uninstall-report.txt` - Uninstall completion report
- `backups/ai-craft-uninstall-*` - Uninstall backup (if created)

## Troubleshooting

### Permission Errors

If you encounter permission errors:

#### Windows
```cmd
# Run as Administrator
Right-click Command Prompt/PowerShell → "Run as administrator"
```

#### Linux/Mac
```bash
# Add execute permissions
chmod +x uninstall-ai-craft.sh

# Run with sudo if needed (rarely required)
sudo ./uninstall-ai-craft.sh
```

### Partial Removal

If uninstall fails partially:

1. **Check Validation Errors**: Review uninstall log for specific failures
2. **Manual Cleanup**: Remove remaining files manually (see Manual Uninstall section)
3. **Re-run Script**: Execute uninstall script again with `--force` option
4. **Clean System Restore**: Use system restore point if available (Windows)

### Files in Use

If files are locked/in use:

1. **Close Claude Code**: Ensure Claude Code is completely closed
2. **Close Terminal**: Close any terminal windows that might have files open
3. **Restart System**: Restart computer to release file locks
4. **Safe Mode**: Run uninstall in safe mode (Windows) if necessary

### Script Not Found

If uninstall scripts are missing:

1. **Check Directory**: Ensure you're in the AI-Craft project directory
2. **Download Scripts**: Re-download AI-Craft framework to get uninstall scripts
3. **Manual Removal**: Use manual uninstall steps above
4. **Verify Path**: Check file paths and permissions

## Post-Uninstall

### Verify Claude Code Functionality

After uninstall:

1. **Test Claude Code**: Verify Claude Code works without AI-Craft
2. **Check Commands**: Ensure no `cai/atdd` commands remain accessible
3. **Clean Environment**: Restart terminal/IDE to clear cached paths
4. **Update Projects**: Update project documentation to reflect removal

### Alternative Frameworks

Consider these alternatives after AI-Craft removal:

1. **Native Claude Code**: Use built-in Claude Code functionality
2. **Custom Agents**: Create custom agent configurations
3. **Other Frameworks**: Explore other AI development frameworks
4. **Manual Workflows**: Implement manual ATDD workflows

## Support

### Getting Help

If you encounter issues:

1. **Check Logs**: Review uninstall logs for specific error messages
2. **Documentation**: Re-read this uninstall guide thoroughly
3. **Community Support**: Seek help from AI-Craft community forums
4. **Issue Reports**: Report bugs in AI-Craft GitHub repository

### Reporting Issues

When reporting uninstall issues:

1. **Include System Info**: OS version, PowerShell/Bash version
2. **Attach Logs**: Include complete uninstall log file
3. **Describe Steps**: Exact commands and options used
4. **Error Messages**: Complete error messages and stack traces
5. **Environment**: Any custom configurations or modifications

## Reinstallation

To reinstall AI-Craft after removal:

1. **Download Framework**: Get latest AI-Craft release
2. **Run Installer**: Execute appropriate install script
3. **Verify Installation**: Confirm all components installed correctly
4. **Restore Configurations**: Restore custom configurations from backup
5. **Test Functionality**: Verify all commands and agents work properly

---

## Quick Reference

| Platform | Script | Interactive | With Backup | Force |
|----------|--------|-------------|-------------|--------|
| Windows CMD | `uninstall-ai-craft.bat` | Default | `--backup` | `--force` |
| PowerShell | `uninstall-ai-craft.ps1` | Default | `-Backup` | `-Force` |
| Linux/Mac | `uninstall-ai-craft.sh` | Default | `--backup` | `--force` |

**Safety Checklist**:
- ✅ Backup important customizations
- ✅ Close all Claude Code instances
- ✅ Verify backup creation (if using --backup)
- ✅ Review what will be removed
- ✅ Have recovery plan if needed

The AI-Craft framework uninstall scripts provide comprehensive, safe removal with optional backup functionality. Choose the approach that best fits your needs and risk tolerance.