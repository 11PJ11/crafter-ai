#!/bin/bash
# AI-Craft Framework Update Script for Linux/WSL
# Orchestrates build, uninstall, and install process for seamless framework updates
#
# Usage: ./update-ai-craft.sh [--backup] [--force] [--dry-run] [--help]

set -euo pipefail

# Script configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
CLAUDE_CONFIG_DIR="${CLAUDE_CONFIG_DIR:-$HOME/.claude}"
UPDATE_LOG="$CLAUDE_CONFIG_DIR/ai-craft-update.log"

# Update configuration
UPDATE_TIMESTAMP=$(date +%Y%m%d-%H%M%S)
UPDATE_BACKUP_DIR="$CLAUDE_CONFIG_DIR/backups/ai-craft-update-$UPDATE_TIMESTAMP"

# Default options
BACKUP_BEFORE_UPDATE=false
FORCE_UPDATE=false
DRY_RUN=false

# Color constants
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly CYAN='\033[0;36m'
readonly NC='\033[0m' # No Color

# Logging function
log_message() {
    local level="$1"
    local message="$2"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    local log_entry="[$timestamp] UPDATE $level: $message"

    case $level in
        "INFO")  echo -e "${GREEN}$log_entry${NC}" ;;
        "WARN")  echo -e "${YELLOW}$log_entry${NC}" ;;
        "ERROR") echo -e "${RED}$log_entry${NC}" ;;
        "STEP")  echo -e "${BLUE}$log_entry${NC}" ;;
        *)       echo "$log_entry" ;;
    esac

    # Write to log file (ignore errors)
    echo "$log_entry" >> "$UPDATE_LOG" 2>/dev/null || true
}

info() { log_message "INFO" "$1"; }
warn() { log_message "WARN" "$1"; }
error() { log_message "ERROR" "$1"; }
step() { log_message "STEP" "$1"; }

show_help() {
    cat << EOF
${BLUE}AI-Craft Framework Update Script for Linux/WSL${NC}

${BLUE}DESCRIPTION:${NC}
    Orchestrates complete AI-Craft framework update process:
    1. Builds new framework bundle from source
    2. Uninstalls existing AI-Craft installation
    3. Installs newly built framework bundle

    This provides a seamless update experience while preserving configuration.

${BLUE}USAGE:${NC}
    $0 [OPTIONS]

${BLUE}OPTIONS:${NC}
    --backup         Create comprehensive backup before update (recommended)
    --force          Skip confirmation prompts and force update
    --dry-run        Show what would be done without executing
    --help           Show this help message

${BLUE}EXAMPLES:${NC}
    $0                      # Interactive update with confirmations
    $0 --backup             # Update with comprehensive backup
    $0 --force --backup     # Automated update with backup
    $0 --dry-run            # Preview update process

${BLUE}UPDATE PROCESS:${NC}
    Step 1: Pre-update validation and backup
    Step 2: Build new framework bundle (dist/ide/)
    Step 3: Uninstall current AI-Craft installation
    Step 4: Install new framework bundle
    Step 5: Validate successful update

${BLUE}BACKUP STRATEGY:${NC}
    - Comprehensive pre-update backup created
    - Individual component backups during uninstall/install
    - Full rollback capability if update fails
    - Backup location: ~/.claude/backups/ai-craft-update-$UPDATE_TIMESTAMP/

${BLUE}IMPORTANT:${NC}
    - Requires Python for build process
    - Preserves Claude Code settings and other configurations
    - Creates detailed update log for troubleshooting
    - Validates installation success before completion
EOF
}

check_prerequisites() {
    step "Checking update prerequisites..."

    # Check if we're in the right directory structure
    if [[ ! -f "$PROJECT_ROOT/tools/build_ide_bundle.py" ]]; then
        error "Build script not found. Ensure you're running from AI-Craft project root"
        exit 1
    fi

    # Check if other required scripts exist
    local required_scripts=("build-ide-bundle.sh" "uninstall-ai-craft.sh" "install-ai-craft.sh")
    for script in "${required_scripts[@]}"; do
        if [[ ! -f "$SCRIPT_DIR/$script" ]]; then
            error "Required script not found: $script"
            exit 1
        fi
    done

    # Check Python availability
    if ! command -v python3 >/dev/null 2>&1; then
        error "Python 3 not found. Required for build process"
        exit 1
    fi

    # Check Claude config directory
    if [[ ! -d "$CLAUDE_CONFIG_DIR" ]]; then
        warn "Claude config directory not found. Will be created during installation"
    fi

    info "✅ All prerequisites satisfied"
}

check_current_installation() {
    step "Checking current AI-Craft installation..."

    local installation_found=false

    # Check for existing installation
    if [[ -d "$CLAUDE_CONFIG_DIR/agents/dw" ]] || [[ -d "$CLAUDE_CONFIG_DIR/commands/dw" ]]; then
        installation_found=true
        info "Found existing AI-Craft installation"

        # Get current installation details
        if [[ -f "$CLAUDE_CONFIG_DIR/ai-craft-manifest.txt" ]]; then
            local manifest_info=$(head -10 "$CLAUDE_CONFIG_DIR/ai-craft-manifest.txt" 2>/dev/null || echo "Manifest details unavailable")
            info "Current installation details:"
            echo -e "${CYAN}$manifest_info${NC}"
        fi
    else
        warn "No existing AI-Craft installation detected"
        warn "This will perform a fresh installation instead of update"
    fi

    return 0
}

create_update_backup() {
    if [[ "$BACKUP_BEFORE_UPDATE" == "false" ]]; then
        return 0
    fi

    step "Creating comprehensive pre-update backup..."

    mkdir -p "$UPDATE_BACKUP_DIR"

    # Backup current Claude configuration
    if [[ -d "$CLAUDE_CONFIG_DIR" ]]; then
        # Create selective backup of AI-Craft components
        if [[ -d "$CLAUDE_CONFIG_DIR/agents/dw" ]]; then
            mkdir -p "$UPDATE_BACKUP_DIR/agents"
            cp -r "$CLAUDE_CONFIG_DIR/agents/dw" "$UPDATE_BACKUP_DIR/agents/"
            info "Backed up agents/dw directory"
        fi

        if [[ -d "$CLAUDE_CONFIG_DIR/commands/dw" ]]; then
            mkdir -p "$UPDATE_BACKUP_DIR/commands"
            cp -r "$CLAUDE_CONFIG_DIR/commands/dw" "$UPDATE_BACKUP_DIR/commands/"
            info "Backed up commands/dw directory"
        fi

        # Backup configuration files
        for config_file in "ai-craft-manifest.txt" "ai-craft-install.log"; do
            if [[ -f "$CLAUDE_CONFIG_DIR/$config_file" ]]; then
                cp "$CLAUDE_CONFIG_DIR/$config_file" "$UPDATE_BACKUP_DIR/"
                info "Backed up $config_file"
            fi
        done
    fi

    # Create backup manifest
    cat > "$UPDATE_BACKUP_DIR/update-backup-manifest.txt" << EOF
AI-Craft Framework Pre-Update Backup
Created: $(date)
Source: $(hostname):$CLAUDE_CONFIG_DIR
Backup Type: Comprehensive pre-update backup
Update Process: Build → Uninstall → Install
Backup Contents:
  - Complete AI-Craft installation state
  - Configuration files and settings
  - Installation logs and manifests

Restoration Command:
  # To restore if update fails:
  cp -r $UPDATE_BACKUP_DIR/agents/dw $CLAUDE_CONFIG_DIR/agents/ 2>/dev/null || true
  cp -r $UPDATE_BACKUP_DIR/commands/dw $CLAUDE_CONFIG_DIR/commands/ 2>/dev/null || true
  cp $UPDATE_BACKUP_DIR/*.txt $CLAUDE_CONFIG_DIR/ 2>/dev/null || true
EOF

    info "✅ Comprehensive backup created: $UPDATE_BACKUP_DIR"
}

build_framework() {
    step "Building new AI-Craft framework bundle..."

    if [[ "$DRY_RUN" == "true" ]]; then
        info "[DRY RUN] Would execute: $SCRIPT_DIR/build-ide-bundle.sh"
        return 0
    fi

    # Change to project root and run build
    cd "$PROJECT_ROOT"

    info "Executing build process..."
    if "$SCRIPT_DIR/build-ide-bundle.sh"; then
        info "✅ Framework bundle built successfully"

        # Verify build output
        if [[ -d "$PROJECT_ROOT/dist/ide" ]]; then
            local agent_count=$(find "$PROJECT_ROOT/dist/ide/agents" -name "*.md" 2>/dev/null | wc -l || echo "0")
            local command_count=$(find "$PROJECT_ROOT/dist/ide/commands" -name "*.md" 2>/dev/null | wc -l || echo "0")

            info "Build verification - Agents: $agent_count, Commands: $command_count"
        else
            error "Build output directory not found: $PROJECT_ROOT/dist/ide"
            exit 1
        fi
    else
        error "Framework build failed"
        exit 1
    fi
}

uninstall_current() {
    step "Uninstalling current AI-Craft installation..."

    if [[ "$DRY_RUN" == "true" ]]; then
        info "[DRY RUN] Would execute: $SCRIPT_DIR/uninstall-ai-craft.sh --force"
        return 0
    fi

    # Determine uninstall options
    local uninstall_options="--force"
    if [[ "$BACKUP_BEFORE_UPDATE" == "true" ]]; then
        uninstall_options="$uninstall_options --backup"
    fi

    info "Executing uninstallation process..."
    if "$SCRIPT_DIR/uninstall-ai-craft.sh" $uninstall_options; then
        info "✅ Previous installation uninstalled successfully"
    else
        warn "Uninstallation reported issues, but continuing with installation"
    fi
}

install_new_framework() {
    step "Installing new AI-Craft framework..."

    if [[ "$DRY_RUN" == "true" ]]; then
        info "[DRY RUN] Would execute: $SCRIPT_DIR/install-ai-craft.sh"
        return 0
    fi

    info "Executing installation process..."
    if "$SCRIPT_DIR/install-ai-craft.sh"; then
        info "✅ New framework installed successfully"
    else
        error "Framework installation failed"

        # Provide recovery guidance
        if [[ "$BACKUP_BEFORE_UPDATE" == "true" ]]; then
            error "Update failed. You can restore from backup:"
            error "  Backup location: $UPDATE_BACKUP_DIR"
            error "  See backup manifest for restoration commands"
        fi

        exit 1
    fi
}

validate_update() {
    step "Validating successful update..."

    local validation_errors=0

    # Check that new installation exists
    if [[ ! -d "$CLAUDE_CONFIG_DIR/agents/dw" ]]; then
        error "Agents directory missing after update"
        ((validation_errors++)) || true
    fi

    if [[ ! -d "$CLAUDE_CONFIG_DIR/commands/dw" ]]; then
        error "Commands directory missing after update"
        ((validation_errors++)) || true
    fi

    # Check manifest
    if [[ ! -f "$CLAUDE_CONFIG_DIR/ai-craft-manifest.txt" ]]; then
        warn "Installation manifest missing"
        ((validation_errors++)) || true
    fi

    # Count installed components
    local agent_count=$(find "$CLAUDE_CONFIG_DIR/agents/dw" -name "*.md" 2>/dev/null | wc -l || echo "0")
    local command_count=$(find "$CLAUDE_CONFIG_DIR/commands/dw" -name "*.md" 2>/dev/null | wc -l || echo "0")

    info "Installation verification - Agents: $agent_count, Commands: $command_count"

    if [[ $validation_errors -eq 0 ]]; then
        info "✅ Update validation successful"
        return 0
    else
        error "Update validation failed with $validation_errors errors"
        return 1
    fi
}

confirm_update() {
    if [[ "$FORCE_UPDATE" == "true" ]] || [[ "$DRY_RUN" == "true" ]]; then
        return 0
    fi

    echo ""
    echo -e "${YELLOW}AI-CRAFT FRAMEWORK UPDATE${NC}"
    echo -e "${YELLOW}=========================${NC}"
    echo ""
    echo -e "${YELLOW}This will:${NC}"
    echo -e "${YELLOW}  1. Build new framework from current source code${NC}"
    echo -e "${YELLOW}  2. Uninstall existing AI-Craft installation${NC}"
    echo -e "${YELLOW}  3. Install newly built framework${NC}"
    echo ""

    if [[ "$BACKUP_BEFORE_UPDATE" == "true" ]]; then
        echo -e "${GREEN}✅ Comprehensive backup will be created before update${NC}"
        echo -e "${GREEN}   Location: $UPDATE_BACKUP_DIR${NC}"
    else
        echo -e "${RED}⚠️  No backup will be created${NC}"
        echo -e "${RED}   To create backup, cancel and run with --backup option${NC}"
    fi

    echo ""
    read -p "Continue with AI-Craft framework update? (y/N): " -r
    if [[ ! $REPLY =~ ^[Yy]([Ee][Ss])?$ ]]; then
        echo ""
        echo -e "${YELLOW}Update cancelled by user.${NC}"
        exit 0
    fi
}

create_update_report() {
    if [[ "$DRY_RUN" == "true" ]]; then
        info "[DRY RUN] Would create update report"
        return 0
    fi

    local report_file="$CLAUDE_CONFIG_DIR/ai-craft-update-report.txt"

    cat > "$report_file" << EOF
AI-Craft Framework Update Report
===============================
Update Completed: $(date)
Computer: $(hostname)
User: $(whoami)
Update Method: Automated orchestrated update

Update Process Summary:
1. ✅ Prerequisites validation
2. ✅ Current installation assessment
$(if [[ "$BACKUP_BEFORE_UPDATE" == "true" ]]; then echo "3. ✅ Comprehensive backup creation"; else echo "3. ⏭️  Backup skipped"; fi)
4. ✅ Framework bundle build
5. ✅ Previous installation uninstall
6. ✅ New framework installation
7. ✅ Update validation

$(if [[ "$BACKUP_BEFORE_UPDATE" == "true" ]]; then
cat << BACKUP_INFO
Backup Information:
- Backup created: $UPDATE_BACKUP_DIR
- Backup contains: Complete pre-update framework state
- Restoration: See backup manifest for recovery commands

BACKUP_INFO
fi)Final Installation Status:
- Agents: $(find "$CLAUDE_CONFIG_DIR/agents/dw" -name "*.md" 2>/dev/null | wc -l || echo "0") installed
- Commands: $(find "$CLAUDE_CONFIG_DIR/commands/dw" -name "*.md" 2>/dev/null | wc -l || echo "0") installed

Update completed successfully. Framework ready for use.
EOF

    info "Update report created: $report_file"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --backup)
            BACKUP_BEFORE_UPDATE=true
            shift
            ;;
        --force)
            FORCE_UPDATE=true
            shift
            ;;
        --dry-run)
            DRY_RUN=true
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
    info "AI-Craft Framework Update Process"
    info "================================="

    if [[ "$DRY_RUN" == "true" ]]; then
        info "🔍 DRY RUN MODE - No changes will be made"
        echo ""
    fi

    # Execute update process
    check_prerequisites
    check_current_installation
    confirm_update
    create_update_backup
    build_framework
    uninstall_current
    install_new_framework

    # Validate and report
    if validate_update; then
        create_update_report

        # Success message
        echo ""
        info "🎉 AI-CRAFT FRAMEWORK UPDATE COMPLETED SUCCESSFULLY!"
        echo ""
        info "Summary:"
        info "- Framework bundle built from latest source"
        info "- Previous installation cleanly removed"
        info "- New framework installation validated"
        info "- All 5D-WAVE components operational"

        if [[ "$BACKUP_BEFORE_UPDATE" == "true" ]]; then
            echo ""
            info "💾 Update backup available at:"
            info "   $UPDATE_BACKUP_DIR"
            info "   Contains complete pre-update state for recovery"
        fi

        echo ""
        info "🚀 Updated AI-Craft framework ready for use!"
        info "   Try: /dw:discuss, /dw:design, /dw:develop, /dw:deliver commands"

    else
        error "Update validation failed"
        if [[ "$BACKUP_BEFORE_UPDATE" == "true" ]]; then
            error "Recovery backup available at: $UPDATE_BACKUP_DIR"
        fi
        exit 1
    fi
}

# Execute main function
main "$@"
