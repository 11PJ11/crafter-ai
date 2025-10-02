#!/bin/bash
# AI-Craft Framework Uninstallation Script for Linux/WSL
# Completely removes AI-Craft framework from global Claude config directory
#
# Usage: ./uninstall-ai-craft.sh [--backup] [--force] [--help]

set -euo pipefail

# Script configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CLAUDE_CONFIG_DIR="/mnt/c/Users/alexd/.claude"
UNINSTALL_LOG="$CLAUDE_CONFIG_DIR/ai-craft-uninstall.log"

# Backup configuration
BACKUP_TIMESTAMP=$(date +%Y%m%d-%H%M%S)
BACKUP_DIR="$CLAUDE_CONFIG_DIR/backups/ai-craft-uninstall-$BACKUP_TIMESTAMP"

# Default options
BACKUP_BEFORE_REMOVAL=false
FORCE_REMOVAL=false
DRY_RUN=false

# Color constants
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;36m'
readonly NC='\033[0m' # No Color

show_help() {
    cat << EOF
${BLUE}AI-Craft Framework Uninstallation Script for Linux/WSL${NC}

${BLUE}DESCRIPTION:${NC}
    Completely removes the AI-Craft ATDD agent framework from your global Claude config directory.
    This removes all 41+ specialized agents, commands, configuration files, logs, and backups.

${BLUE}USAGE:${NC}
    $0 [OPTIONS]

${BLUE}OPTIONS:${NC}
    --backup         Create backup before removal (recommended)
    --force          Skip confirmation prompts
    --dry-run        Show what would be removed without making any changes
    --help           Show this help message

${BLUE}EXAMPLES:${NC}
    $0                      # Interactive uninstall with confirmation
    $0 --dry-run            # Show what would be removed (no changes made)
    $0 --backup             # Create backup before removal
    $0 --force              # Uninstall without confirmation prompts

${BLUE}WHAT GETS REMOVED:${NC}
    - All 5D-WAVE agents in agents/dw/ directory
    - All DW commands in commands/dw/ directory
    - AI-Craft configuration files (constants.md, manifest)
    - AI-Craft installation logs and backup directories
    - AI-Craft project state files

${BLUE}IMPORTANT:${NC}
    This action cannot be undone unless you use --backup option.
    All customizations and local changes will be lost.
EOF
}

log_message() {
    local level="$1"
    local message="$2"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    local log_entry="[$timestamp] $level: $message"
    
    case $level in
        "INFO")  echo -e "${GREEN}$log_entry${NC}" ;;
        "WARN")  echo -e "${YELLOW}$log_entry${NC}" ;;
        "ERROR") echo -e "${RED}$log_entry${NC}" ;;
        *)       echo "$log_entry" ;;
    esac
    
    # Write to log file (ignore errors)
    echo "$log_entry" >> "$UNINSTALL_LOG" 2>/dev/null || true
}

info() {
    log_message "INFO" "$1"
}

warn() {
    log_message "WARN" "$1"
}

error() {
    log_message "ERROR" "$1"
}

check_installation() {
    info "Checking for AI-Craft installation..."
    
    local installation_found=false
    
    # Check for 5D-WAVE agents directory
    if [[ -d "$CLAUDE_CONFIG_DIR/agents/dw" ]]; then
        installation_found=true
        info "Found 5D-WAVE agents in: $CLAUDE_CONFIG_DIR/agents/dw"
    fi

    # Check for 5D-WAVE commands directory
    if [[ -d "$CLAUDE_CONFIG_DIR/commands/dw" ]]; then
        installation_found=true
        info "Found 5D-WAVE commands in: $CLAUDE_CONFIG_DIR/commands/dw"
    fi

    
    # Check for configuration files
    if [[ -f "$CLAUDE_CONFIG_DIR/agents/dw/config.json" ]]; then
        installation_found=true
        info "Found 5D-WAVE configuration files"
    fi
    
    # Check for manifest
    if [[ -f "$CLAUDE_CONFIG_DIR/ai-craft-manifest.txt" ]]; then
        installation_found=true
        info "Found AI-Craft manifest file"
    fi
    
    # Check for installation logs
    if [[ -f "$CLAUDE_CONFIG_DIR/ai-craft-install.log" ]]; then
        installation_found=true
        info "Found AI-Craft installation logs"
    fi
    
    # Check for backup directories
    if [[ -d "$CLAUDE_CONFIG_DIR/backups" ]]; then
        if find "$CLAUDE_CONFIG_DIR/backups" -maxdepth 1 -name "ai-craft-*" -type d | grep -q .; then
            installation_found=true
            info "Found AI-Craft backup directories"
        fi
    fi
    
    if [[ "$installation_found" == "false" ]]; then
        info "No AI-Craft installation found"
        echo ""
        echo -e "${YELLOW}No AI-Craft framework installation detected.${NC}"
        echo -e "${YELLOW}Nothing to uninstall.${NC}"
        exit 0
    fi
    
    return 0
}

confirm_removal() {
    if [[ "$FORCE_REMOVAL" == "true" ]]; then
        return 0
    fi
    
    echo ""
    echo -e "${RED}WARNING: This will completely remove the framework installation from your system.${NC}"
    echo ""
    echo -e "${YELLOW}The following will be removed:${NC}"
    echo -e "${YELLOW}  - All 5D-WAVE agents${NC}"
    echo -e "${YELLOW}  - All 5D-WAVE commands${NC}"
    echo -e "${YELLOW}  - Configuration files and manifest${NC}"
    echo -e "${YELLOW}  - Claude Code workflow hooks${NC}"
    echo -e "${YELLOW}  - Installation logs and backup directories${NC}"
    echo -e "${YELLOW}  - Any customizations or local changes${NC}"
    echo ""
    
    if [[ "$BACKUP_BEFORE_REMOVAL" == "true" ]]; then
        echo -e "${GREEN}A backup will be created before removal at:${NC}"
        echo -e "${GREEN}  $BACKUP_DIR${NC}"
        echo ""
    else
        echo -e "${RED}WARNING: No backup will be created. This action cannot be undone.${NC}"
        echo -e "${RED}To create a backup, cancel and run with --backup option.${NC}"
        echo ""
    fi
    
    read -p "Are you sure you want to proceed? (y/N): " -r
    if [[ ! $REPLY =~ ^[Yy]([Ee][Ss])?$ ]]; then
        echo ""
        echo -e "${YELLOW}Uninstallation cancelled by user.${NC}"
        exit 0
    fi
}

create_backup() {
    if [[ "$BACKUP_BEFORE_REMOVAL" == "false" ]]; then
        return 0
    fi

    if [[ "$DRY_RUN" == "true" ]]; then
        info "${YELLOW}[DRY RUN]${NC} Would create backup before removal..."
        info "${YELLOW}[DRY RUN]${NC} Would create backup directory: $BACKUP_DIR"

        if [[ -d "$CLAUDE_CONFIG_DIR/agents/dw" ]]; then
            info "${YELLOW}[DRY RUN]${NC} Would backup agents/dw directory"
        fi

        if [[ -d "$CLAUDE_CONFIG_DIR/commands/dw" ]]; then
            info "${YELLOW}[DRY RUN]${NC} Would backup commands/dw directory"
        fi

        if [[ -d "$CLAUDE_CONFIG_DIR/hooks" ]]; then
            info "${YELLOW}[DRY RUN]${NC} Would backup hooks directory"
        fi

        if [[ -f "$CLAUDE_CONFIG_DIR/settings.local.json" ]]; then
            info "${YELLOW}[DRY RUN]${NC} Would backup settings.local.json"
        fi

        if [[ -f "$CLAUDE_CONFIG_DIR/ai-craft-manifest.txt" ]]; then
            info "${YELLOW}[DRY RUN]${NC} Would backup manifest file"
        fi

        if [[ -f "$CLAUDE_CONFIG_DIR/ai-craft-install.log" ]]; then
            info "${YELLOW}[DRY RUN]${NC} Would backup installation log"
        fi

        info "${YELLOW}[DRY RUN]${NC} Would create backup manifest: $BACKUP_DIR/uninstall-backup-manifest.txt"
        return 0
    fi

    info "Creating backup before removal..."

    mkdir -p "$BACKUP_DIR"

    # Backup agents directory if it exists
    if [[ -d "$CLAUDE_CONFIG_DIR/agents/dw" ]]; then
        mkdir -p "$BACKUP_DIR/agents"
        cp -r "$CLAUDE_CONFIG_DIR/agents/dw" "$BACKUP_DIR/agents/"
        info "Backed up agents/dw directory"
    fi

    # Backup commands directory if it exists
    if [[ -d "$CLAUDE_CONFIG_DIR/commands/dw" ]]; then
        mkdir -p "$BACKUP_DIR/commands"
        cp -r "$CLAUDE_CONFIG_DIR/commands/dw" "$BACKUP_DIR/commands/"
        info "Backed up commands/dw directory"
    fi

    # Backup hooks directory if it exists
    if [[ -d "$CLAUDE_CONFIG_DIR/hooks" ]]; then
        mkdir -p "$BACKUP_DIR/hooks"
        cp -r "$CLAUDE_CONFIG_DIR/hooks/"* "$BACKUP_DIR/hooks/" 2>/dev/null || true
        info "Backed up hooks directory"
    fi

    # Backup current settings.local.json
    if [[ -f "$CLAUDE_CONFIG_DIR/settings.local.json" ]]; then
        cp "$CLAUDE_CONFIG_DIR/settings.local.json" "$BACKUP_DIR/settings.local.json.backup"
        info "Backed up settings.local.json"
    fi

    # Backup configuration files
    if [[ -f "$CLAUDE_CONFIG_DIR/ai-craft-manifest.txt" ]]; then
        cp "$CLAUDE_CONFIG_DIR/ai-craft-manifest.txt" "$BACKUP_DIR/"
        info "Backed up manifest file"
    fi

    if [[ -f "$CLAUDE_CONFIG_DIR/ai-craft-install.log" ]]; then
        cp "$CLAUDE_CONFIG_DIR/ai-craft-install.log" "$BACKUP_DIR/"
        info "Backed up installation log"
    fi

    # Create backup manifest
    cat > "$BACKUP_DIR/uninstall-backup-manifest.txt" << EOF
Framework Uninstall Backup
Created: $(date)
Source: $(hostname):$CLAUDE_CONFIG_DIR
Backup Type: Pre-uninstall backup
Backup contents:
  - 5D-WAVE agents and commands
  - Configuration files and logs
  - Complete framework state before removal
EOF

    info "Backup created successfully at: $BACKUP_DIR"
}

remove_agents() {
    if [[ "$DRY_RUN" == "true" ]]; then
        info "${YELLOW}[DRY RUN]${NC} Would remove 5D-WAVE agents..."

        if [[ -d "$CLAUDE_CONFIG_DIR/agents/dw" ]]; then
            info "${YELLOW}[DRY RUN]${NC} Would remove agents/dw directory"
        fi

        if [[ -d "$CLAUDE_CONFIG_DIR/agents" ]]; then
            if [[ -z "$(ls -A "$CLAUDE_CONFIG_DIR/agents" 2>/dev/null)" ]]; then
                info "${YELLOW}[DRY RUN]${NC} Would remove empty agents directory"
            else
                info "${YELLOW}[DRY RUN]${NC} Would keep agents directory (contains other files)"
            fi
        fi
        return 0
    fi

    info "Removing 5D-WAVE agents..."

    # Remove 5D-WAVE structure
    if [[ -d "$CLAUDE_CONFIG_DIR/agents/dw" ]]; then
        rm -rf "$CLAUDE_CONFIG_DIR/agents/dw"
        info "Removed agents/dw directory"
    fi

    # Remove agents directory if it's empty and only contained framework files
    if [[ -d "$CLAUDE_CONFIG_DIR/agents" ]]; then
        if [[ -z "$(ls -A "$CLAUDE_CONFIG_DIR/agents" 2>/dev/null)" ]]; then
            rmdir "$CLAUDE_CONFIG_DIR/agents" 2>/dev/null
            info "Removed empty agents directory"
        else
            info "Kept agents directory (contains other files)"
        fi
    fi
}

remove_commands() {
    if [[ "$DRY_RUN" == "true" ]]; then
        info "${YELLOW}[DRY RUN]${NC} Would remove 5D-WAVE commands..."

        if [[ -d "$CLAUDE_CONFIG_DIR/commands/dw" ]]; then
            info "${YELLOW}[DRY RUN]${NC} Would remove commands/dw directory"
        fi

        if [[ -d "$CLAUDE_CONFIG_DIR/commands" ]]; then
            if [[ -z "$(ls -A "$CLAUDE_CONFIG_DIR/commands" 2>/dev/null)" ]]; then
                info "${YELLOW}[DRY RUN]${NC} Would remove empty commands directory"
            else
                info "${YELLOW}[DRY RUN]${NC} Would keep commands directory (contains other files)"
            fi
        fi
        return 0
    fi

    info "Removing 5D-WAVE commands..."

    # Remove 5D-WAVE structure
    if [[ -d "$CLAUDE_CONFIG_DIR/commands/dw" ]]; then
        rm -rf "$CLAUDE_CONFIG_DIR/commands/dw"
        info "Removed commands/dw directory"
    fi

    # Remove commands directory if it's empty and only contained framework files
    if [[ -d "$CLAUDE_CONFIG_DIR/commands" ]]; then
        if [[ -z "$(ls -A "$CLAUDE_CONFIG_DIR/commands" 2>/dev/null)" ]]; then
            rmdir "$CLAUDE_CONFIG_DIR/commands" 2>/dev/null
            info "Removed empty commands directory"
        else
            info "Kept commands directory (contains other files)"
        fi
    fi
}


remove_framework_hooks() {
    if [[ "$DRY_RUN" == "true" ]]; then
        info "${YELLOW}[DRY RUN]${NC} Would remove 5D-WAVE workflow hooks safely..."

        if [[ ! -d "$CLAUDE_CONFIG_DIR/hooks" ]]; then
            info "${YELLOW}[DRY RUN]${NC} No hooks directory found, would skip hook removal"
            return 0
        fi

        local managed_dirs=("workflow" "code-quality" "lib" "config" "formatters" "legacy")
        local total_would_remove=0
        local total_would_preserve=0

        for dir in "${managed_dirs[@]}"; do
            if [[ -d "$CLAUDE_CONFIG_DIR/hooks/$dir" ]]; then
                local would_remove=0
                local would_preserve=0

                while IFS= read -r -d '' file; do
                    if grep -q "# Part of Claude Code SuperClaude\|# AI-Craft Framework" "$file" 2>/dev/null; then
                        ((would_remove++))
                        ((total_would_remove++))
                    else
                        ((would_preserve++))
                        ((total_would_preserve++))
                    fi
                done < <(find "$CLAUDE_CONFIG_DIR/hooks/$dir" -type f -print0 2>/dev/null)

                if [[ $would_remove -gt 0 ]]; then
                    info "${YELLOW}[DRY RUN]${NC} Would remove $would_remove AI-Craft file(s) from hooks/$dir"
                fi

                if [[ $would_preserve -gt 0 ]]; then
                    warn "${YELLOW}[DRY RUN]${NC} Would preserve $would_preserve custom file(s) in hooks/$dir"
                fi

                if [[ $would_preserve -eq 0 ]] && [[ $would_remove -gt 0 ]]; then
                    info "${YELLOW}[DRY RUN]${NC} Would remove empty hooks/$dir directory"
                else
                    info "${YELLOW}[DRY RUN]${NC} Would keep hooks/$dir directory (contains custom files)"
                fi
            fi
        done

        info "${YELLOW}[DRY RUN]${NC} Summary: Would remove $total_would_remove AI-Craft files, preserve $total_would_preserve custom files"
        info "${YELLOW}[DRY RUN]${NC} Would clean hook settings from settings.local.json"
        info "${YELLOW}[DRY RUN]${NC} Would clean global settings from settings.json"
        return 0
    fi

    info "Removing 5D-WAVE workflow hooks safely..."

    if [[ ! -d "$CLAUDE_CONFIG_DIR/hooks" ]]; then
        info "No hooks directory found, skipping hook removal"
        return 0
    fi

    # Define AI-Craft managed directories
    local managed_dirs=("workflow" "code-quality" "lib" "config" "formatters" "legacy")

    local total_removed=0
    local total_preserved=0

    # Remove only AI-Craft files (identified by marker comment), preserve custom files
    for dir in "${managed_dirs[@]}"; do
        if [[ -d "$CLAUDE_CONFIG_DIR/hooks/$dir" ]]; then
            info "Processing hooks/$dir directory..."

            local removed_count=0
            local preserved_count=0

            # Process each file in the directory
            while IFS= read -r -d '' file; do
                # Check if file has AI-Craft marker comment
                if grep -q "# Part of Claude Code SuperClaude\|# AI-Craft Framework" "$file" 2>/dev/null; then
                    rm -f "$file"
                    ((removed_count++))
                    ((total_removed++))
                else
                    warn "Preserving custom file: ${file#$CLAUDE_CONFIG_DIR/hooks/}"
                    ((preserved_count++))
                    ((total_preserved++))
                fi
            done < <(find "$CLAUDE_CONFIG_DIR/hooks/$dir" -type f -print0 2>/dev/null)

            if [[ $removed_count -gt 0 ]]; then
                info "Removed $removed_count AI-Craft file(s) from hooks/$dir"
            fi

            if [[ $preserved_count -gt 0 ]]; then
                warn "Preserved $preserved_count custom file(s) in hooks/$dir"
            fi

            # Only remove directory if it's empty
            if [[ -z "$(ls -A "$CLAUDE_CONFIG_DIR/hooks/$dir" 2>/dev/null)" ]]; then
                rmdir "$CLAUDE_CONFIG_DIR/hooks/$dir" 2>/dev/null && \
                    info "Removed empty hooks/$dir directory"
            else
                info "Kept hooks/$dir directory (contains ${preserved_count} custom file(s))"
            fi
        fi
    done

    # Remove standalone framework files
    if [[ -f "$CLAUDE_CONFIG_DIR/hooks/verify-installation.sh" ]]; then
        rm -f "$CLAUDE_CONFIG_DIR/hooks/verify-installation.sh"
        ((total_removed++))
    fi

    # Remove test files
    local test_file_count=$(find "$CLAUDE_CONFIG_DIR/hooks" -maxdepth 1 -name "test_*.sh" 2>/dev/null | wc -l)
    if [[ $test_file_count -gt 0 ]]; then
        find "$CLAUDE_CONFIG_DIR/hooks" -maxdepth 1 -name "test_*.sh" -delete 2>/dev/null || true
        total_removed=$((total_removed + test_file_count))
    fi

    info "Hook removal summary: $total_removed AI-Craft files removed, $total_preserved custom files preserved"

    # Remove hooks directory if it's empty after framework removal
    if [[ -d "$CLAUDE_CONFIG_DIR/hooks" ]]; then
        if [[ -z "$(ls -A "$CLAUDE_CONFIG_DIR/hooks" 2>/dev/null)" ]]; then
            rmdir "$CLAUDE_CONFIG_DIR/hooks" 2>/dev/null
            info "Removed empty hooks directory"
        else
            info "Kept hooks directory (contains $total_preserved custom file(s))"
        fi
    fi

    # Surgically remove CAI hooks from settings.local.json
    clean_hook_settings

    # Clean global settings.json as well
    clean_global_settings
}

clean_hook_settings() {
    local settings_file="$CLAUDE_CONFIG_DIR/settings.local.json"

    if [[ ! -f "$settings_file" ]]; then
        return 0
    fi

    if [[ "$DRY_RUN" == "true" ]]; then
        info "${YELLOW}[DRY RUN]${NC} Would clean CAI hooks from settings.local.json"
        info "${YELLOW}[DRY RUN]${NC} Would create backup: $settings_file.pre-uninstall-backup"
        return 0
    fi

    # Backup before modification
    cp "$settings_file" "$settings_file.pre-uninstall-backup"
    info "Created backup: $settings_file.pre-uninstall-backup"

    # Use Python to surgically remove only CAI hooks
    if command -v python3 >/dev/null 2>&1; then
        python3 << 'PYTHON_SCRIPT'
import json
import os
import sys

settings_file = "/mnt/c/Users/alexd/.claude/settings.local.json"

try:
    with open(settings_file, 'r') as f:
        settings = json.load(f)
except Exception as e:
    print(f"Error reading settings: {e}")
    sys.exit(1)

# Remove framework-specific hooks by ID
if 'hooks' in settings:
    for event in list(settings['hooks'].keys()):
        # Filter out framework hooks by ID
        settings['hooks'][event] = [
            hook for hook in settings['hooks'][event]
            if not any(
                h.get('id', '').startswith('dw-')
                for h in hook.get('hooks', [])
            )
        ]

        # Remove empty hook arrays
        if not settings['hooks'][event]:
            del settings['hooks'][event]

# Remove CAI-specific permissions
if 'permissions' in settings and 'allow' in settings['permissions']:
    settings['permissions']['allow'] = [
        perm for perm in settings['permissions']['allow']
        if not ('hooks/**' in perm or 'craft-ai' in perm)
    ]

# Save cleaned settings
try:
    with open(settings_file, 'w') as f:
        json.dump(settings, f, indent=2)
    print("Successfully removed Craft-AI hooks from settings")
except Exception as e:
    print(f"Error saving settings: {e}")
    sys.exit(1)
PYTHON_SCRIPT

        if [[ $? -eq 0 ]]; then
            info "Successfully cleaned CAI hooks from settings.local.json"
        else
            warn "Failed to clean hooks configuration - manual cleanup may be required"
        fi
    else
        warn "Python3 not available - hooks configuration not cleaned"
    fi
}

# Clean global settings.json (remove only AI-Craft hooks, keep everything else)
clean_global_settings() {
    local global_settings="$CLAUDE_CONFIG_DIR/settings.json"

    if [[ ! -f "$global_settings" ]]; then
        if [[ "$DRY_RUN" == "true" ]]; then
            info "${YELLOW}[DRY RUN]${NC} Global settings.json not found, would skip cleanup"
        else
            info "Global settings.json not found, skipping cleanup"
        fi
        return 0
    fi

    if [[ "$DRY_RUN" == "true" ]]; then
        info "${YELLOW}[DRY RUN]${NC} Would clean AI-Craft hooks from settings.json"
        info "${YELLOW}[DRY RUN]${NC} Would create backup: $global_settings.pre-uninstall-backup"
        return 0
    fi

    # Backup before modification
    cp "$global_settings" "$global_settings.pre-uninstall-backup"
    info "Created backup: $global_settings.pre-uninstall-backup"

    # Use Python to surgically remove only AI-Craft hooks
    if command -v python3 >/dev/null 2>&1; then
        python3 << 'PYTHON_SCRIPT'
import json
import os
import sys

global_settings_file = "/mnt/c/Users/alexd/.claude/settings.json"

try:
    with open(global_settings_file, 'r') as f:
        settings = json.load(f)
except Exception as e:
    print(f"Error reading global settings: {e}")
    sys.exit(1)

# Remove AI-Craft hooks from PostToolUse while keeping other hooks
if 'hooks' in settings and 'PostToolUse' in settings['hooks']:
    # Remove only AI-Craft hooks by exact path match (safer than substring matching)
    ai_craft_hook_paths = [
        '/mnt/c/Users/alexd/.claude/hooks/code-quality/lint-format.sh',
        '/mnt/c/Users/alexd/.claude/hooks/workflow/hooks-dispatcher.sh'
    ]

    # Filter out only hooks with exact AI-Craft paths
    settings['hooks']['PostToolUse'] = [
        hook for hook in settings['hooks']['PostToolUse']
        if not any(
            any(path in h.get('command', '') for path in ai_craft_hook_paths)
            for h in hook.get('hooks', [])
        )
    ]

    # Remove PostToolUse section if it's empty
    if not settings['hooks']['PostToolUse']:
        del settings['hooks']['PostToolUse']

    # Remove hooks section if it's empty
    if not settings['hooks']:
        del settings['hooks']

# Save cleaned settings
try:
    with open(global_settings_file, 'w') as f:
        json.dump(settings, f, indent=2)
    print("Successfully removed AI-Craft hooks from global settings")
except Exception as e:
    print(f"Error saving global settings: {e}")
    sys.exit(1)
PYTHON_SCRIPT

        if [[ $? -eq 0 ]]; then
            info "Successfully cleaned AI-Craft hooks from settings.json"
        else
            warn "Failed to clean global settings - manual cleanup may be required"
        fi
    else
        warn "Python3 not available - global settings not cleaned"
    fi
}

remove_config_files() {
    if [[ "$DRY_RUN" == "true" ]]; then
        info "${YELLOW}[DRY RUN]${NC} Would remove AI-Craft configuration files..."

        if [[ -f "$CLAUDE_CONFIG_DIR/ai-craft-manifest.txt" ]]; then
            info "${YELLOW}[DRY RUN]${NC} Would remove ai-craft-manifest.txt"
        fi

        if [[ -f "$CLAUDE_CONFIG_DIR/ai-craft-install.log" ]]; then
            info "${YELLOW}[DRY RUN]${NC} Would remove ai-craft-install.log"
        fi
        return 0
    fi

    info "Removing AI-Craft configuration files..."

    if [[ -f "$CLAUDE_CONFIG_DIR/ai-craft-manifest.txt" ]]; then
        rm -f "$CLAUDE_CONFIG_DIR/ai-craft-manifest.txt"
        info "Removed ai-craft-manifest.txt"
    fi

    if [[ -f "$CLAUDE_CONFIG_DIR/ai-craft-install.log" ]]; then
        rm -f "$CLAUDE_CONFIG_DIR/ai-craft-install.log"
        info "Removed ai-craft-install.log"
    fi
}

remove_backups() {
    if [[ "$DRY_RUN" == "true" ]]; then
        info "${YELLOW}[DRY RUN]${NC} Would remove AI-Craft backup directories..."

        local backup_count=0
        if [[ -d "$CLAUDE_CONFIG_DIR/backups" ]]; then
            for backup_dir in "$CLAUDE_CONFIG_DIR/backups"/ai-craft-*; do
                if [[ -d "$backup_dir" ]]; then
                    ((backup_count++))
                fi
            done
        fi

        if [[ $backup_count -gt 0 ]]; then
            info "${YELLOW}[DRY RUN]${NC} Would remove $backup_count AI-Craft backup directories"
        else
            info "${YELLOW}[DRY RUN]${NC} No AI-Craft backup directories found"
        fi
        return 0
    fi

    info "Removing AI-Craft backup directories..."

    local backup_count=0
    if [[ -d "$CLAUDE_CONFIG_DIR/backups" ]]; then
        for backup_dir in "$CLAUDE_CONFIG_DIR/backups"/ai-craft-*; do
            if [[ -d "$backup_dir" ]]; then
                rm -rf "$backup_dir"
                ((backup_count++))
            fi
        done
    fi

    if [[ $backup_count -gt 0 ]]; then
        info "Removed $backup_count AI-Craft backup directories"
    else
        info "No AI-Craft backup directories found"
    fi
}

remove_project_files() {
    if [[ "$DRY_RUN" == "true" ]]; then
        info "${YELLOW}[DRY RUN]${NC} Would remove AI-Craft project files..."

        if [[ -d "$CLAUDE_CONFIG_DIR/projects" ]]; then
            for project_dir in "$CLAUDE_CONFIG_DIR/projects"/*ai-craft*; do
                if [[ -d "$project_dir" ]]; then
                    info "${YELLOW}[DRY RUN]${NC} Would remove project directory: $(basename "$project_dir")"
                fi
            done
        fi
        return 0
    fi

    info "Removing AI-Craft project files..."

    if [[ -d "$CLAUDE_CONFIG_DIR/projects" ]]; then
        for project_dir in "$CLAUDE_CONFIG_DIR/projects"/*ai-craft*; do
            if [[ -d "$project_dir" ]]; then
                rm -rf "$project_dir"
                info "Removed project directory: $(basename "$project_dir")"
            fi
        done
    fi
}

validate_removal() {
    info "Validating complete removal..."

    local errors=0

    # Check that agents are removed
    if [[ -d "$CLAUDE_CONFIG_DIR/agents/dw" ]]; then
        error "5D-WAVE agents directory still exists"
        ((errors++))
    fi

    # Check that commands are removed
    if [[ -d "$CLAUDE_CONFIG_DIR/commands/dw" ]]; then
        error "5D-WAVE commands directory still exists"
        ((errors++))
    fi

    # Check that framework hooks are removed
    if [[ -d "$CLAUDE_CONFIG_DIR/hooks/workflow" ]] || [[ -d "$CLAUDE_CONFIG_DIR/hooks/code-quality" ]]; then
        error "Framework hook directories still exist"
        ((errors++))
    fi

    # Check that framework hooks are removed from settings
    if [[ -f "$CLAUDE_CONFIG_DIR/settings.local.json" ]]; then
        if grep -q '"dw-' "$CLAUDE_CONFIG_DIR/settings.local.json" 2>/dev/null; then
            warn "5D-WAVE hooks may still be configured in settings.local.json"
        fi
    fi

    # Check that config files are removed
    if [[ -f "$CLAUDE_CONFIG_DIR/ai-craft-manifest.txt" ]]; then
        error "AI-Craft manifest file still exists"
        ((errors++))
    fi
    
    if [[ -f "$CLAUDE_CONFIG_DIR/ai-craft-install.log" ]]; then
        error "AI-Craft installation log still exists"
        ((errors++))
    fi
    
    # Check for remaining backup directories
    if [[ -d "$CLAUDE_CONFIG_DIR/backups" ]]; then
        for backup_dir in "$CLAUDE_CONFIG_DIR/backups"/ai-craft-*; do
            if [[ -d "$backup_dir" ]]; then
                error "AI-Craft backup directory still exists: $(basename "$backup_dir")"
                ((errors++))
            fi
        done
    fi
    
    if [[ $errors -eq 0 ]]; then
        info "Uninstallation validation: ${GREEN}PASSED${NC}"
        return 0
    else
        error "Uninstallation validation: ${RED}FAILED${NC} ($errors errors)"
        return 1
    fi
}

create_uninstall_report() {
    local report_file="$CLAUDE_CONFIG_DIR/framework-uninstall-report.txt"

    cat > "$report_file" << EOF
Framework Uninstallation Report
===============================
Uninstalled: $(date)
Computer: $(hostname)
User: $(whoami)

Uninstall Summary:
- 5D-WAVE agents removed from: $CLAUDE_CONFIG_DIR/agents/dw/
- 5D-WAVE commands removed from: $CLAUDE_CONFIG_DIR/commands/dw/
- Configuration files removed
- Installation logs removed
- Backup directories cleaned

$(if [[ "$BACKUP_BEFORE_REMOVAL" == "true" ]]; then
cat << BACKUP_INFO
Backup Information:
- Backup created: $BACKUP_DIR
- Backup contains: Complete framework state before removal

BACKUP_INFO
fi)Uninstallation completed successfully.
Framework completely removed from system.
EOF

    info "Uninstallation report created: $report_file"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --backup)
            BACKUP_BEFORE_REMOVAL=true
            shift
            ;;
        --force)
            FORCE_REMOVAL=true
            shift
            ;;
        --dry-run)
            DRY_RUN=true
            info "${YELLOW}DRY RUN MODE${NC} - No changes will be made"
            shift
            ;;
        --help|-h)
            show_help
            exit 0
            ;;
        *)
            echo "ERROR: Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Main execution
main() {
    info "Framework Uninstallation Script"
    info "==============================="
    
    # Check for installation
    check_installation
    
    # Confirm removal
    confirm_removal
    
    # Create backup if requested
    create_backup
    
    # Remove components
    remove_agents
    remove_commands
    remove_framework_hooks
    remove_config_files
    remove_backups
    remove_project_files
    
    # Validate removal
    if ! validate_removal; then
        error "Uninstallation failed validation"
        exit 1
    fi
    
    # Create report
    create_uninstall_report
    
    # Success message
    echo ""
    info "✅ Framework uninstalled successfully!"
    echo ""
    info "Summary:"
    info "- All 5D-WAVE agents removed"
    info "- All 5D-WAVE commands removed"
    info "- Claude Code workflow hooks removed"
    info "- Configuration files cleaned"
    info "- Backup directories removed"
    
    if [[ "$BACKUP_BEFORE_REMOVAL" == "true" ]]; then
        echo ""
        info "💾 Backup available at:"
        info "   $BACKUP_DIR"
        info "   Use this backup to restore if needed"
    fi
    
    echo ""
    info "The framework has been completely removed from your system."
}

# Execute main function
main "$@"