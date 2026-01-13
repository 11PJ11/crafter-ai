#!/bin/bash
# AI-Craft Framework Uninstallation Script for Linux/WSL
# Completely removes AI-Craft framework from global Claude config directory
#
# Usage: ./uninstall-ai-craft.sh [--backup] [--force] [--help]

set -euo pipefail

# Script configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CLAUDE_CONFIG_DIR="${CLAUDE_CONFIG_DIR:-$HOME/.claude}"
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
    This removes all specialized agents, commands, configuration files, logs, and backups.

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
    - All nWave agents in agents/nw/ directory
    - All DW commands in commands/nw/ directory
    - AI-Craft configuration files (manifest)
    - AI-Craft installation logs and backup directories

${BLUE}IMPORTANT:${NC}
    This action cannot be undone unless you use --backup option.
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

    echo "$log_entry" >> "$UNINSTALL_LOG" 2>/dev/null || true
}

info() { log_message "INFO" "$1"; }
warn() { log_message "WARN" "$1"; }
error() { log_message "ERROR" "$1"; }

check_installation() {
    info "Checking for AI-Craft installation..."

    local installation_found=false

    if [[ -d "$CLAUDE_CONFIG_DIR/agents/nw" ]]; then
        installation_found=true
        info "Found nWave agents in: $CLAUDE_CONFIG_DIR/agents/nw"
    fi

    if [[ -d "$CLAUDE_CONFIG_DIR/commands/nw" ]]; then
        installation_found=true
        info "Found nWave commands in: $CLAUDE_CONFIG_DIR/commands/nw"
    fi

    if [[ -f "$CLAUDE_CONFIG_DIR/ai-craft-manifest.txt" ]]; then
        installation_found=true
        info "Found AI-Craft manifest file"
    fi

    if [[ -f "$CLAUDE_CONFIG_DIR/ai-craft-install.log" ]]; then
        installation_found=true
        info "Found AI-Craft installation logs"
    fi

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
    echo -e "${YELLOW}  - All nWave agents${NC}"
    echo -e "${YELLOW}  - All nWave commands${NC}"
    echo -e "${YELLOW}  - Configuration files and manifest${NC}"
    echo -e "${YELLOW}  - Installation logs and backup directories${NC}"
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
        return 0
    fi

    info "Creating backup before removal..."
    mkdir -p "$BACKUP_DIR"

    if [[ -d "$CLAUDE_CONFIG_DIR/agents/nw" ]]; then
        mkdir -p "$BACKUP_DIR/agents"
        cp -r "$CLAUDE_CONFIG_DIR/agents/nw" "$BACKUP_DIR/agents/"
        info "Backed up agents/nw directory"
    fi

    if [[ -d "$CLAUDE_CONFIG_DIR/commands/nw" ]]; then
        mkdir -p "$BACKUP_DIR/commands"
        cp -r "$CLAUDE_CONFIG_DIR/commands/nw" "$BACKUP_DIR/commands/"
        info "Backed up commands/nw directory"
    fi

    if [[ -f "$CLAUDE_CONFIG_DIR/ai-craft-manifest.txt" ]]; then
        cp "$CLAUDE_CONFIG_DIR/ai-craft-manifest.txt" "$BACKUP_DIR/"
        info "Backed up manifest file"
    fi

    if [[ -f "$CLAUDE_CONFIG_DIR/ai-craft-install.log" ]]; then
        cp "$CLAUDE_CONFIG_DIR/ai-craft-install.log" "$BACKUP_DIR/"
        info "Backed up installation log"
    fi

    cat > "$BACKUP_DIR/uninstall-backup-manifest.txt" << EOF
Framework Uninstall Backup
Created: $(date)
Source: $(hostname):$CLAUDE_CONFIG_DIR
Backup Type: Pre-uninstall backup
EOF

    info "Backup created successfully at: $BACKUP_DIR"
}

remove_agents() {
    if [[ "$DRY_RUN" == "true" ]]; then
        info "${YELLOW}[DRY RUN]${NC} Would remove nWave agents..."
        if [[ -d "$CLAUDE_CONFIG_DIR/agents/nw" ]]; then
            info "${YELLOW}[DRY RUN]${NC} Would remove agents/nw directory"
        fi
        return 0
    fi

    info "Removing nWave agents..."

    if [[ -d "$CLAUDE_CONFIG_DIR/agents/nw" ]]; then
        rm -rf "$CLAUDE_CONFIG_DIR/agents/nw"
        info "Removed agents/nw directory"
    fi

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
        info "${YELLOW}[DRY RUN]${NC} Would remove nWave commands..."
        if [[ -d "$CLAUDE_CONFIG_DIR/commands/nw" ]]; then
            info "${YELLOW}[DRY RUN]${NC} Would remove commands/nw directory"
        fi
        return 0
    fi

    info "Removing nWave commands..."

    if [[ -d "$CLAUDE_CONFIG_DIR/commands/nw" ]]; then
        rm -rf "$CLAUDE_CONFIG_DIR/commands/nw"
        info "Removed commands/nw directory"
    fi

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
    if [[ "$DRY_RUN" == "true" ]]; then
        info "${YELLOW}[DRY RUN]${NC} Would remove AI-Craft configuration files..."
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
        return 0
    fi

    info "Removing AI-Craft backup directories..."

    local backup_count=0
    if [[ -d "$CLAUDE_CONFIG_DIR/backups" ]]; then
        for backup_dir in "$CLAUDE_CONFIG_DIR/backups"/ai-craft-*; do
            if [[ -d "$backup_dir" ]]; then
                # Skip the backup we just created during this uninstall
                if [[ "$BACKUP_BEFORE_REMOVAL" == "true" ]] && [[ "$backup_dir" == "$BACKUP_DIR" ]]; then
                    info "Preserving current uninstall backup: $(basename "$backup_dir")"
                    continue
                fi
                rm -rf "$backup_dir"
                ((backup_count++)) || true
            fi
        done
    fi

    if [[ $backup_count -gt 0 ]]; then
        info "Removed $backup_count old AI-Craft backup directories"
    else
        info "No old AI-Craft backup directories found"
    fi
}

validate_removal() {
    if [[ "$DRY_RUN" == "true" ]]; then
        info "${YELLOW}[DRY RUN]${NC} Would validate complete removal"
        return 0
    fi

    info "Validating complete removal..."

    local errors=0

    if [[ -d "$CLAUDE_CONFIG_DIR/agents/nw" ]]; then
        error "nWave agents directory still exists"
        ((errors++)) || true
    fi

    if [[ -d "$CLAUDE_CONFIG_DIR/commands/nw" ]]; then
        error "nWave commands directory still exists"
        ((errors++)) || true
    fi

    if [[ -f "$CLAUDE_CONFIG_DIR/ai-craft-manifest.txt" ]]; then
        error "AI-Craft manifest file still exists"
        ((errors++)) || true
    fi

    if [[ -f "$CLAUDE_CONFIG_DIR/ai-craft-install.log" ]]; then
        error "AI-Craft installation log still exists"
        ((errors++)) || true
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
    if [[ "$DRY_RUN" == "true" ]]; then
        info "${YELLOW}[DRY RUN]${NC} Would create uninstall report"
        return 0
    fi

    local report_file="$CLAUDE_CONFIG_DIR/framework-uninstall-report.txt"

    cat > "$report_file" << EOF
Framework Uninstallation Report
===============================
Uninstalled: $(date)
Computer: $(hostname)
User: $(whoami)

Uninstall Summary:
- nWave agents removed from: $CLAUDE_CONFIG_DIR/agents/nw/
- nWave commands removed from: $CLAUDE_CONFIG_DIR/commands/nw/
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

    check_installation
    confirm_removal
    create_backup

    remove_agents
    remove_commands
    remove_config_files
    remove_backups

    if ! validate_removal; then
        error "Uninstallation failed validation"
        exit 1
    fi

    create_uninstall_report

    echo ""
    info "✅ Framework uninstalled successfully!"
    echo ""
    info "Summary:"
    info "- All nWave agents removed"
    info "- All nWave commands removed"
    info "- Configuration files cleaned"
    info "- Backup directories removed"

    if [[ "$BACKUP_BEFORE_REMOVAL" == "true" ]]; then
        echo ""
        info "💾 Backup available at:"
        info "   $BACKUP_DIR"
    fi

    echo ""
    info "The framework has been completely removed from your system."
}

main "$@"
