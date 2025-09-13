#!/bin/bash
# AI-Craft Framework Uninstallation Script for Linux/Mac
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
${BLUE}AI-Craft Framework Uninstallation Script for Linux/Mac${NC}

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
    - All AI-Craft commands in commands/cai/ directory
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
    echo -e "${YELLOW}  - All AI-Craft commands (cai/atdd and related commands)${NC}"
    echo -e "${YELLOW}  - Configuration files (constants.md, manifest)${NC}"
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
  - AI-Craft agents and commands
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
- AI-Craft commands removed from: $CLAUDE_CONFIG_DIR/commands/cai
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
    info "- All AI-Craft commands removed"
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