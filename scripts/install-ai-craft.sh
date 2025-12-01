#!/bin/bash
# AI-Craft Framework Installation Script for Linux/WSL
# Installs the AI-Craft ATDD agent framework to global Claude config directory
#
# Usage: ./install-ai-craft.sh [--backup-only] [--restore] [--help]

set -e  # Exit on any error

# Script configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
CLAUDE_CONFIG_DIR="${CLAUDE_CONFIG_DIR:-$HOME/.claude}"
BACKUP_DIR="$CLAUDE_CONFIG_DIR/backups/ai-craft-$(date +%Y%m%d-%H%M%S)"
FRAMEWORK_SOURCE="$PROJECT_ROOT/dist/ide"
INSTALL_LOG="$CLAUDE_CONFIG_DIR/ai-craft-install.log"
DRY_RUN=false

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    local level="$1"
    shift
    local message="$*"
    echo -e "${BLUE}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} ${level}: $message"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $level: $message" >> "$INSTALL_LOG" 2>/dev/null || true
}

info() { log "${GREEN}INFO${NC}" "$@"; }
warn() { log "${YELLOW}WARN${NC}" "$@"; }
error() { log "${RED}ERROR${NC}" "$@"; }

# Help function
show_help() {
    cat << EOF
AI-Craft Framework Installation Script for Linux/WSL

DESCRIPTION:
    Installs the 5D-WAVE methodology framework to your global Claude config directory.
    This makes all specialized agents and commands available across all projects.

USAGE:
    $0 [OPTIONS]

OPTIONS:
    --backup-only    Create backup of existing AI-Craft installation without installing
    --restore        Restore from the most recent backup
    --dry-run        Show what would be installed without making any changes
    --help           Show this help message

EXAMPLES:
    $0                      # Install 5D-WAVE framework
    $0 --dry-run            # Show what would be installed (no changes made)
    $0 --backup-only        # Create backup only
    $0 --restore           # Restore from latest backup

WHAT GETS INSTALLED:
    - 5D-WAVE specialized agents (DISCUSS→DESIGN→DISTILL→DEVELOP→DELIVER methodology)
    - 5D-WAVE command interface for workflow orchestration
    - ATDD (Acceptance Test Driven Development) integration
    - Outside-In TDD with double-loop architecture
    - Quality validation network with Level 1-6 refactoring

INSTALLATION LOCATION:
    ~/.claude/agents/dw/    # 5D-WAVE agent specifications
    ~/.claude/commands/dw/  # 5D-WAVE command integrations

FILES INCLUDED:
    - All built 5D-WAVE agents and commands from dist/ide/

For more information: https://github.com/11PJ11/crafter-ai
EOF
}

# Check if source framework exists
check_source() {
    info "Checking source framework..."

    if [[ ! -d "$FRAMEWORK_SOURCE" ]]; then
        error "AI-Craft framework source not found at: $FRAMEWORK_SOURCE"
        error "Please run this script from the ai-craft project directory."
        exit 1
    fi

    # Check for the built IDE distribution structure
    if [[ ! -d "$FRAMEWORK_SOURCE/agents/dw" ]]; then
        error "Framework appears incomplete - agents/dw directory not found"
        error "Please build the framework first: cd tools && python3 build_ide_bundle.py"
        exit 1
    fi

    if [[ ! -d "$FRAMEWORK_SOURCE/commands/dw" ]]; then
        error "Framework appears incomplete - commands/dw directory not found"
        error "Please build the framework first: cd tools && python3 build_ide_bundle.py"
        exit 1
    fi

    local agent_count=$(find "$FRAMEWORK_SOURCE/agents/dw" -name "*.md" ! -name "README.md" | wc -l)
    local command_count=$(find "$FRAMEWORK_SOURCE/commands/dw" -name "*.md" ! -name "README.md" | wc -l)

    info "Found framework with $agent_count agent files and $command_count commands"

    if [[ $agent_count -lt 10 ]]; then
        warn "Expected 10+ agents, found only $agent_count. Continuing anyway..."
    fi
}

# Create backup of existing installation
create_backup() {
    if [[ "$DRY_RUN" == "true" ]]; then
        info "${YELLOW}[DRY RUN]${NC} Would create backup of existing AI-Craft installation..."

        if [[ ! -d "$CLAUDE_CONFIG_DIR/agents" ]] && [[ ! -d "$CLAUDE_CONFIG_DIR/commands" ]]; then
            info "${YELLOW}[DRY RUN]${NC} No existing AI-Craft installation found, would skip backup"
            return 0
        fi

        info "${YELLOW}[DRY RUN]${NC} Would create backup directory: $BACKUP_DIR"

        if [[ -d "$CLAUDE_CONFIG_DIR/agents" ]]; then
            info "${YELLOW}[DRY RUN]${NC} Would backup agents directory"
        fi

        if [[ -d "$CLAUDE_CONFIG_DIR/commands" ]]; then
            info "${YELLOW}[DRY RUN]${NC} Would backup commands directory"
        fi

        info "${YELLOW}[DRY RUN]${NC} Would create backup manifest at: $BACKUP_DIR/backup-manifest.txt"
        return 0
    fi

    info "Creating backup of existing AI-Craft installation..."

    if [[ ! -d "$CLAUDE_CONFIG_DIR/agents" ]] && [[ ! -d "$CLAUDE_CONFIG_DIR/commands" ]]; then
        info "No existing AI-Craft installation found, skipping backup"
        return 0
    fi

    mkdir -p "$BACKUP_DIR"

    # Backup existing agents directory
    if [[ -d "$CLAUDE_CONFIG_DIR/agents" ]]; then
        cp -r "$CLAUDE_CONFIG_DIR/agents" "$BACKUP_DIR/"
        info "Backed up agents directory"
    fi

    # Backup existing commands directory
    if [[ -d "$CLAUDE_CONFIG_DIR/commands" ]]; then
        cp -r "$CLAUDE_CONFIG_DIR/commands" "$BACKUP_DIR/"
        info "Backed up commands directory"
    fi

    # Create backup manifest
    cat > "$BACKUP_DIR/backup-manifest.txt" << EOF
AI-Craft Framework Backup
Created: $(date)
Source: $(hostname):$CLAUDE_CONFIG_DIR
Backup contents:
$(find "$BACKUP_DIR" -type f -name "*.md" | wc -l) framework files
EOF

    info "Backup created at: $BACKUP_DIR"
    return 0
}

# Restore from backup
restore_backup() {
    info "Looking for backups to restore..."

    local latest_backup=$(find "$CLAUDE_CONFIG_DIR/backups" -name "ai-craft-*" -type d 2>/dev/null | sort | tail -1)

    if [[ -z "$latest_backup" ]]; then
        error "No backups found in $CLAUDE_CONFIG_DIR/backups"
        exit 1
    fi

    info "Restoring from backup: $latest_backup"

    # Remove current installation
    rm -rf "$CLAUDE_CONFIG_DIR/agents" "$CLAUDE_CONFIG_DIR/commands" 2>/dev/null || true

    # Restore from backup
    if [[ -d "$latest_backup/agents" ]]; then
        cp -r "$latest_backup/agents" "$CLAUDE_CONFIG_DIR/"
        info "Restored agents directory"
    fi

    if [[ -d "$latest_backup/commands" ]]; then
        cp -r "$latest_backup/commands" "$CLAUDE_CONFIG_DIR/"
        info "Restored commands directory"
    fi

    info "Restoration complete from backup: $latest_backup"
}

# Install framework files
install_framework() {
    if [[ "$DRY_RUN" == "true" ]]; then
        info "${YELLOW}[DRY RUN]${NC} Would install AI-Craft framework to: $CLAUDE_CONFIG_DIR"

        info "${YELLOW}[DRY RUN]${NC} Would create target directory: $CLAUDE_CONFIG_DIR"

        # Show agents that would be installed
        info "${YELLOW}[DRY RUN]${NC} Would install agents..."
        if [[ -d "$FRAMEWORK_SOURCE/agents/dw" ]]; then
            local agent_count=$(find "$FRAMEWORK_SOURCE/agents/dw" -name "*.md" ! -name "README.md" | wc -l)
            info "${YELLOW}[DRY RUN]${NC} Would create: $CLAUDE_CONFIG_DIR/agents/dw"
            info "${YELLOW}[DRY RUN]${NC} Would install $agent_count agent files"
        fi

        # Show commands that would be installed
        info "${YELLOW}[DRY RUN]${NC} Would install commands..."
        if [[ -d "$FRAMEWORK_SOURCE/commands/dw" ]]; then
            local command_count=$(find "$FRAMEWORK_SOURCE/commands/dw" -name "*.md" ! -name "README.md" | wc -l)
            info "${YELLOW}[DRY RUN]${NC} Would create: $CLAUDE_CONFIG_DIR/commands"
            info "${YELLOW}[DRY RUN]${NC} Would install $command_count command files"
        fi

        return 0
    fi

    info "Installing AI-Craft framework to: $CLAUDE_CONFIG_DIR"

    # Create target directories
    mkdir -p "$CLAUDE_CONFIG_DIR"

    # Copy agents directory (excluding README.md)
    info "Installing agents..."
    if [[ -d "$FRAMEWORK_SOURCE/agents/dw" ]]; then
        mkdir -p "$CLAUDE_CONFIG_DIR/agents/dw"

        find "$FRAMEWORK_SOURCE/agents/dw" -name "*.md" ! -name "README.md" | while read -r file; do
            local relative_path="${file#$FRAMEWORK_SOURCE/agents/dw/}"
            local target_file="$CLAUDE_CONFIG_DIR/agents/dw/$relative_path"
            local target_dir=$(dirname "$target_file")

            mkdir -p "$target_dir"
            cp "$file" "$target_file"
        done

        local copied_agents=$(find "$CLAUDE_CONFIG_DIR/agents/dw" -name "*.md" | wc -l)
        info "Installed $copied_agents agent files"
    fi

    # Copy commands directory
    info "Installing commands..."
    if [[ -d "$FRAMEWORK_SOURCE/commands/dw" ]]; then
        mkdir -p "$CLAUDE_CONFIG_DIR/commands"
        cp -r "$FRAMEWORK_SOURCE/commands/"* "$CLAUDE_CONFIG_DIR/commands/"

        local copied_commands=$(find "$CLAUDE_CONFIG_DIR/commands" -name "*.md" | wc -l)
        info "Installed $copied_commands command files"

        if [[ -d "$CLAUDE_CONFIG_DIR/commands/dw" ]]; then
            local dw_commands=$(find "$CLAUDE_CONFIG_DIR/commands/dw" -name "*.md" | wc -l)
            info "  - DW commands: $dw_commands essential commands"
        fi
    fi
}

# Validate installation
validate_installation() {
    info "Validating installation..."

    local errors=0

    # Check that agents are installed
    if [[ ! -d "$CLAUDE_CONFIG_DIR/agents/dw" ]]; then
        error "Missing DW agents directory"
        ((errors++)) || true
    fi

    # Check that commands are installed
    if [[ ! -d "$CLAUDE_CONFIG_DIR/commands/dw" ]]; then
        error "Missing DW commands directory"
        ((errors++)) || true
    fi

    # Check essential DW commands exist
    local essential_commands=("discuss" "design" "distill" "develop" "deliver")
    for cmd in "${essential_commands[@]}"; do
        if [[ ! -f "$CLAUDE_CONFIG_DIR/commands/dw/$cmd.md" ]]; then
            error "Missing essential DW command: $cmd.md"
            ((errors++)) || true
        fi
    done

    # Count installed files
    local total_agents=$(find "$CLAUDE_CONFIG_DIR/agents/dw" -name "*.md" 2>/dev/null | wc -l)
    local total_commands=$(find "$CLAUDE_CONFIG_DIR/commands" -name "*.md" 2>/dev/null | wc -l)

    info "Installation summary:"
    info "  - Agents installed: $total_agents"
    info "  - Commands installed: $total_commands"
    info "  - Installation directory: $CLAUDE_CONFIG_DIR"

    if [[ -d "$CLAUDE_CONFIG_DIR/agents/dw" ]]; then
        info "  - 5D-WAVE agents: Available"
    fi

    if [[ -d "$CLAUDE_CONFIG_DIR/commands/dw" ]]; then
        info "  - 5D-WAVE commands: Available"
    fi

    if [[ $total_agents -lt 10 ]]; then
        warn "Expected 10+ agents, found $total_agents"
    fi

    if [[ $errors -eq 0 ]]; then
        info "Installation validation: ${GREEN}PASSED${NC}"
        return 0
    else
        error "Installation validation: ${RED}FAILED${NC} ($errors errors)"
        return 1
    fi
}

# Create installation manifest
create_manifest() {
    if [[ "$DRY_RUN" == "true" ]]; then
        info "${YELLOW}[DRY RUN]${NC} Would create installation manifest"
        return 0
    fi

    local manifest_file="$CLAUDE_CONFIG_DIR/ai-craft-manifest.txt"

    cat > "$manifest_file" << EOF
AI-Craft Framework Installation Manifest
========================================
Installed: $(date)
Source: $SCRIPT_DIR
Version: Production Ready

Installation Summary:
- Total agents: $(find "$CLAUDE_CONFIG_DIR/agents" -name "*.md" | wc -l)
- Total commands: $(find "$CLAUDE_CONFIG_DIR/commands" -name "*.md" | wc -l)
- Installation directory: $CLAUDE_CONFIG_DIR
- Backup directory: $BACKUP_DIR

Framework Components:
- 41+ specialized AI agents with Single Responsibility Principle
- Wave processing architecture with clean context isolation
- Essential DW commands: discuss, design, distill, develop, deliver
- Quality validation network with Level 1-6 refactoring

Usage:
- Use 5D-WAVE commands: '/dw:discuss', '/dw:design', '/dw:distill', '/dw:develop', '/dw:deliver'
- Use '/dw:start "feature description"' to initialize 5D-WAVE workflow
- All agents available globally across projects

For help: https://github.com/11PJ11/crafter-ai
EOF

    info "Installation manifest created: $manifest_file"
}

# Main installation process
main() {
    info "AI-Craft Framework Installation Script"
    info "======================================"

    # Parse command line arguments
    case "${1:-}" in
        --help|-h)
            show_help
            exit 0
            ;;
        --dry-run)
            DRY_RUN=true
            info "${YELLOW}DRY RUN MODE${NC} - No changes will be made"
            ;;
        --backup-only)
            check_source
            create_backup
            info "Backup completed successfully"
            exit 0
            ;;
        --restore)
            restore_backup
            info "Restoration completed successfully"
            exit 0
            ;;
        "")
            # Normal installation
            ;;
        *)
            error "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac

    # Normal installation process
    check_source
    create_backup
    install_framework

    if validate_installation; then
        create_manifest
        info ""
        info "${GREEN}✅ 5D-WAVE Framework installed successfully!${NC}"
        info ""
        info "Framework Components Installed:"
        info "- 5D-WAVE specialized agents (DISCUSS→DESIGN→DISTILL→DEVELOP→DELIVER)"
        info "- 5D-WAVE command interface for workflow orchestration"
        info "- ATDD and Outside-In TDD integration"
        info ""
        info "Next steps:"
        info "1. Navigate to any project directory"
        info "2. Use 5D-WAVE commands to orchestrate development workflow"
        info "3. Access agents through the dw category in Claude Code"
        info ""
        info "5D-WAVE methodology available:"
        info "- ${BLUE}/dw:discuss${NC} - Requirements gathering and business analysis"
        info "- ${BLUE}/dw:design${NC} - Architecture design with visual representation"
        info "- ${BLUE}/dw:distill${NC} - Acceptance test creation and business validation"
        info "- ${BLUE}/dw:develop${NC} - Outside-In TDD implementation with refactoring"
        info "- ${BLUE}/dw:deliver${NC} - Production readiness validation"
        info ""
        info "Documentation: https://github.com/11PJ11/crafter-ai"
    else
        error "Installation failed validation"
        warn "You can restore the previous installation with: $0 --restore"
        exit 1
    fi
}

# Run main function with all arguments
main "$@"
