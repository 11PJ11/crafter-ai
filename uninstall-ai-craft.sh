#!/bin/bash
# AI-Craft Framework Uninstallation Script for Linux/WSL
# Completely removes AI-Craft framework from global Claude config directory
#
# Usage: ./uninstall-ai-craft.sh [--backup] [--force] [--help]

set -euo pipefail

# Script configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CLAUDE_CONFIG_DIR="$HOME/.claude"
UNINSTALL_LOG="$CLAUDE_CONFIG_DIR/ai-craft-uninstall.log"

# Backup configuration
BACKUP_TIMESTAMP=$(date +%Y%m%d-%H%M%S)
BACKUP_DIR="$CLAUDE_CONFIG_DIR/backups/ai-craft-uninstall-$BACKUP_TIMESTAMP"

# Default options
BACKUP_BEFORE_REMOVAL=false
FORCE_REMOVAL=false

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
    --help           Show this help message

${BLUE}EXAMPLES:${NC}
    $0                      # Interactive uninstall with confirmation
    $0 --backup             # Create backup before removal
    $0 --force              # Uninstall without confirmation prompts

${BLUE}WHAT GETS REMOVED:${NC}
    - All AI-Craft agents in agents/cai/ directory
    - All CAI commands in commands/cai/ directory (14 essential commands)
    - Manual system documentation in manuals/cai/ directory
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
    
    # Check for agents directory
    if [[ -d "$CLAUDE_CONFIG_DIR/agents/cai" ]]; then
        installation_found=true
        info "Found AI-Craft agents in: $CLAUDE_CONFIG_DIR/agents/cai"
    fi
    
    # Check for commands directory
    if [[ -d "$CLAUDE_CONFIG_DIR/commands/cai" ]]; then
        installation_found=true
        info "Found AI-Craft commands in: $CLAUDE_CONFIG_DIR/commands/cai"
    fi

    # Check for manuals directory
    if [[ -d "$CLAUDE_CONFIG_DIR/manuals/cai" ]]; then
        installation_found=true
        info "Found AI-Craft manuals in: $CLAUDE_CONFIG_DIR/manuals/cai"
    fi
    
    # Check for configuration files
    if [[ -f "$CLAUDE_CONFIG_DIR/agents/cai/constants.md" ]]; then
        installation_found=true
        info "Found AI-Craft configuration files"
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
    echo -e "${RED}WARNING: This will completely remove the AI-Craft framework from your system.${NC}"
    echo ""
    echo -e "${YELLOW}The following will be removed:${NC}"
    echo -e "${YELLOW}  - All AI-Craft agents (41+ specialized agents)${NC}"
    echo -e "${YELLOW}  - All CAI commands (14 essential commands)${NC}"
    echo -e "${YELLOW}  - Manual system documentation${NC}"
    echo -e "${YELLOW}  - Configuration files (constants.md, manifest)${NC}"
    echo -e "${YELLOW}  - Claude Code workflow hooks for CAI agents${NC}"
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
    
    info "Creating backup before removal..."
    
    mkdir -p "$BACKUP_DIR"
    
    # Backup agents directory if it exists
    if [[ -d "$CLAUDE_CONFIG_DIR/agents/cai" ]]; then
        mkdir -p "$BACKUP_DIR/agents"
        cp -r "$CLAUDE_CONFIG_DIR/agents/cai" "$BACKUP_DIR/agents/"
        info "Backed up agents directory"
    fi
    
    # Backup commands directory if it exists
    if [[ -d "$CLAUDE_CONFIG_DIR/commands/cai" ]]; then
        mkdir -p "$BACKUP_DIR/commands"
        cp -r "$CLAUDE_CONFIG_DIR/commands/cai" "$BACKUP_DIR/commands/"
        info "Backed up commands directory"
    fi

    # Backup manuals directory if it exists
    if [[ -d "$CLAUDE_CONFIG_DIR/manuals/cai" ]]; then
        mkdir -p "$BACKUP_DIR/manuals"
        cp -r "$CLAUDE_CONFIG_DIR/manuals/cai" "$BACKUP_DIR/manuals/"
        info "Backed up manuals directory"
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
AI-Craft Framework Uninstall Backup
Created: $(date)
Source: $(hostname):$CLAUDE_CONFIG_DIR
Backup Type: Pre-uninstall backup
Backup contents:
  - AI-Craft agents, commands, and manual system
  - Configuration files and logs
  - Complete framework state before removal
EOF
    
    info "Backup created successfully at: $BACKUP_DIR"
}

remove_agents() {
    info "Removing AI-Craft agents..."
    
    if [[ -d "$CLAUDE_CONFIG_DIR/agents/cai" ]]; then
        rm -rf "$CLAUDE_CONFIG_DIR/agents/cai"
        info "Removed agents/cai directory"
    fi
    
    # Remove agents directory if it's empty and only contained cai
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
    info "Removing AI-Craft commands..."

    if [[ -d "$CLAUDE_CONFIG_DIR/commands/cai" ]]; then
        rm -rf "$CLAUDE_CONFIG_DIR/commands/cai"
        info "Removed commands/cai directory"
    fi

    # Remove commands directory if it's empty and only contained cai
    if [[ -d "$CLAUDE_CONFIG_DIR/commands" ]]; then
        if [[ -z "$(ls -A "$CLAUDE_CONFIG_DIR/commands" 2>/dev/null)" ]]; then
            rmdir "$CLAUDE_CONFIG_DIR/commands" 2>/dev/null
            info "Removed empty commands directory"
        else
            info "Kept commands directory (contains other files)"
        fi
    fi
}

remove_manuals() {
    info "Removing AI-Craft manual system..."

    if [[ -d "$CLAUDE_CONFIG_DIR/manuals/cai" ]]; then
        rm -rf "$CLAUDE_CONFIG_DIR/manuals/cai"
        info "Removed manuals/cai directory"
    fi

    # Remove manuals directory if it's empty and only contained cai
    if [[ -d "$CLAUDE_CONFIG_DIR/manuals" ]]; then
        if [[ -z "$(ls -A "$CLAUDE_CONFIG_DIR/manuals" 2>/dev/null)" ]]; then
            rmdir "$CLAUDE_CONFIG_DIR/manuals" 2>/dev/null
            info "Removed empty manuals directory"
        else
            info "Kept manuals directory (contains other files)"
        fi
    fi
}

remove_craft_ai_hooks() {
    info "Removing Craft-AI workflow hooks..."

    # Remove CAI-specific hook files (preserve other hooks)
    if [[ -d "$CLAUDE_CONFIG_DIR/hooks" ]]; then
        # Remove CAI-specific directories
        rm -rf "$CLAUDE_CONFIG_DIR/hooks/workflow" 2>/dev/null || true
        rm -rf "$CLAUDE_CONFIG_DIR/hooks/code-quality" 2>/dev/null || true
        rm -rf "$CLAUDE_CONFIG_DIR/hooks/lib" 2>/dev/null || true
        rm -rf "$CLAUDE_CONFIG_DIR/hooks/config" 2>/dev/null || true
        rm -rf "$CLAUDE_CONFIG_DIR/hooks/formatters" 2>/dev/null || true
        rm -rf "$CLAUDE_CONFIG_DIR/hooks/legacy" 2>/dev/null || true
        rm -f "$CLAUDE_CONFIG_DIR/hooks/verify-installation.sh" 2>/dev/null || true
        rm -f "$CLAUDE_CONFIG_DIR/hooks/test_"*.sh 2>/dev/null || true
        info "Removed CAI hook files"
    fi

    # Remove hooks directory if it's empty after CAI removal
    if [[ -d "$CLAUDE_CONFIG_DIR/hooks" ]]; then
        if [[ -z "$(ls -A "$CLAUDE_CONFIG_DIR/hooks" 2>/dev/null)" ]]; then
            rmdir "$CLAUDE_CONFIG_DIR/hooks" 2>/dev/null
            info "Removed empty hooks directory"
        else
            info "Kept hooks directory (contains other files)"
        fi
    fi

    # Surgically remove CAI hooks from settings.local.json
    clean_hook_settings
}

clean_hook_settings() {
    local settings_file="$CLAUDE_CONFIG_DIR/settings.local.json"

    if [[ ! -f "$settings_file" ]]; then
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

settings_file = os.path.expanduser("~/.claude/settings.local.json")

try:
    with open(settings_file, 'r') as f:
        settings = json.load(f)
except Exception as e:
    print(f"Error reading settings: {e}")
    sys.exit(1)

# Remove CAI-specific hooks by ID
if 'hooks' in settings:
    for event in list(settings['hooks'].keys()):
        # Filter out CAI hooks by ID
        settings['hooks'][event] = [
            hook for hook in settings['hooks'][event]
            if not any(
                h.get('id', '').startswith('cai-')
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

remove_config_files() {
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
    if [[ -d "$CLAUDE_CONFIG_DIR/agents/cai" ]]; then
        error "AI-Craft agents directory still exists"
        ((errors++))
    fi
    
    # Check that commands are removed
    if [[ -d "$CLAUDE_CONFIG_DIR/commands/cai" ]]; then
        error "AI-Craft commands directory still exists"
        ((errors++))
    fi

    # Check that manuals are removed
    if [[ -d "$CLAUDE_CONFIG_DIR/manuals/cai" ]]; then
        error "AI-Craft manuals directory still exists"
        ((errors++))
    fi

    # Check that CAI hooks are removed
    if [[ -d "$CLAUDE_CONFIG_DIR/hooks/workflow" ]] || [[ -d "$CLAUDE_CONFIG_DIR/hooks/code-quality" ]]; then
        error "AI-Craft hook directories still exist"
        ((errors++))
    fi

    # Check that CAI hooks are removed from settings
    if [[ -f "$CLAUDE_CONFIG_DIR/settings.local.json" ]]; then
        if grep -q '"cai-' "$CLAUDE_CONFIG_DIR/settings.local.json" 2>/dev/null; then
            warn "CAI hooks may still be configured in settings.local.json"
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
    local report_file="$CLAUDE_CONFIG_DIR/ai-craft-uninstall-report.txt"
    
    cat > "$report_file" << EOF
AI-Craft Framework Uninstallation Report
========================================
Uninstalled: $(date)
Computer: $(hostname)
User: $(whoami)

Uninstall Summary:
- AI-Craft agents removed from: $CLAUDE_CONFIG_DIR/agents/cai
- CAI commands removed from: $CLAUDE_CONFIG_DIR/commands/cai (14 essential commands)
- Manual system removed from: $CLAUDE_CONFIG_DIR/manuals/cai
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
    info "AI-Craft Framework Uninstallation Script"
    info "======================================="
    
    # Check for installation
    check_installation
    
    # Confirm removal
    confirm_removal
    
    # Create backup if requested
    create_backup
    
    # Remove components
    remove_agents
    remove_commands
    remove_manuals
    remove_craft_ai_hooks
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
    info "✅ AI-Craft Framework uninstalled successfully!"
    echo ""
    info "Summary:"
    info "- All AI-Craft agents removed"
    info "- All CAI commands removed (14 essential commands)"
    info "- AI-Craft manual system removed"
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
    info "The AI-Craft framework has been completely removed from your system."
}

# Execute main function
main "$@"