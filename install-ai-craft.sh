#!/bin/bash
# AI-Craft Framework Installation Script
# Installs the AI-Craft ATDD agent framework to global Claude config directory
# 
# Usage: ./install-ai-craft.sh [--backup-only] [--restore] [--help]

set -e  # Exit on any error

# Script configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CLAUDE_CONFIG_DIR="$HOME/.claude"
BACKUP_DIR="$CLAUDE_CONFIG_DIR/backups/ai-craft-$(date +%Y%m%d-%H%M%S)"
FRAMEWORK_SOURCE="$SCRIPT_DIR/.claude"
INSTALL_LOG="$CLAUDE_CONFIG_DIR/ai-craft-install.log"

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
AI-Craft Framework Installation Script

DESCRIPTION:
    Installs the AI-Craft ATDD agent framework to your global Claude config directory.
    This makes all 41+ specialized agents and the cai/atdd command available across all projects.

USAGE:
    $0 [OPTIONS]

OPTIONS:
    --backup-only    Create backup of existing AI-Craft installation without installing
    --restore        Restore from the most recent backup
    --help           Show this help message

EXAMPLES:
    $0                      # Install AI-Craft framework
    $0 --backup-only        # Create backup only
    $0 --restore           # Restore from latest backup

WHAT GETS INSTALLED:
    - 41+ specialized AI agents in 9 categories
    - cai/atdd command interface with intelligent project analysis
    - Centralized configuration system (constants.md)
    - Wave processing architecture for clean ATDD workflows
    - Quality validation network with Level 1-6 refactoring
    - Second Way DevOps: Observability agents (metrics, logs, traces, performance)
    - Third Way DevOps: Experimentation agents (A/B testing, hypothesis validation, learning synthesis)

INSTALLATION LOCATION:
    ~/.claude/agents/       # All agent specifications
    ~/.claude/commands/     # Command integrations

FILES EXCLUDED:
    - README.md files (project-specific documentation)
    - docs/ directory (project working files)
    - Git configuration and project metadata

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
    
    if [[ ! -f "$FRAMEWORK_SOURCE/agents/cai/constants.md" ]]; then
        error "Framework appears incomplete - constants.md not found"
        exit 1
    fi
    
    local agent_count=$(find "$FRAMEWORK_SOURCE/agents/cai" -name "*.md" ! -name "README.md" | wc -l)
    info "Found framework with $agent_count agent files"
    
    if [[ $agent_count -lt 40 ]]; then
        warn "Expected 40+ agents, found only $agent_count. Continuing anyway..."
    fi
}

# Create backup of existing installation
create_backup() {
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
    rm -rf "$CLAUDE_CONFIG_DIR/agents" "$CLAUDE_CONFIG_DIR/commands/cai" 2>/dev/null || true
    
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
    info "Installing AI-Craft framework to: $CLAUDE_CONFIG_DIR"
    
    # Create target directories
    mkdir -p "$CLAUDE_CONFIG_DIR"
    
    # Copy agents directory (excluding README.md)
    info "Installing agents..."
    if [[ -d "$FRAMEWORK_SOURCE/agents/cai" ]]; then
        # Create target structure
        mkdir -p "$CLAUDE_CONFIG_DIR/agents/cai"
        
        # Copy all agent files except README.md
        find "$FRAMEWORK_SOURCE/agents/cai" -name "*.md" ! -name "README.md" | while read -r file; do
            local relative_path="${file#$FRAMEWORK_SOURCE/agents/cai/}"
            local target_file="$CLAUDE_CONFIG_DIR/agents/cai/$relative_path"
            local target_dir=$(dirname "$target_file")
            
            mkdir -p "$target_dir"
            cp "$file" "$target_file"
        done
        
        local copied_agents=$(find "$CLAUDE_CONFIG_DIR/agents/cai" -name "*.md" | wc -l)
        info "Installed $copied_agents agent files"
    fi
    
    # Copy commands directory
    info "Installing commands..."
    if [[ -d "$FRAMEWORK_SOURCE/commands" ]]; then
        mkdir -p "$CLAUDE_CONFIG_DIR/commands"
        cp -r "$FRAMEWORK_SOURCE/commands/"* "$CLAUDE_CONFIG_DIR/commands/"
        
        local copied_commands=$(find "$CLAUDE_CONFIG_DIR/commands" -name "*.md" | wc -l)
        info "Installed $copied_commands command files"
    fi
}

# Validate installation
validate_installation() {
    info "Validating installation..."
    
    local errors=0
    
    # Check constants.md exists
    if [[ ! -f "$CLAUDE_CONFIG_DIR/agents/cai/constants.md" ]]; then
        error "Missing constants.md - core configuration file"
        ((errors++))
    fi
    
    # Check cai/atdd command exists
    if [[ ! -f "$CLAUDE_CONFIG_DIR/commands/cai/atdd.md" ]]; then
        error "Missing cai/atdd command file"
        ((errors++))
    fi
    
    # Count installed files
    local total_agents=$(find "$CLAUDE_CONFIG_DIR/agents/cai" -name "*.md" 2>/dev/null | wc -l)
    local total_commands=$(find "$CLAUDE_CONFIG_DIR/commands" -name "*.md" 2>/dev/null | wc -l)
    
    info "Installation summary:"
    info "  - Agents installed: $total_agents"
    info "  - Commands installed: $total_commands"
    info "  - Installation directory: $CLAUDE_CONFIG_DIR"
    
    # Check agent categories
    local categories=("requirements-analysis" "architecture-design" "test-design" "development" "quality-validation" "refactoring" "coordination" "observability" "experimentation")
    for category in "${categories[@]}"; do
        if [[ -d "$CLAUDE_CONFIG_DIR/agents/cai/$category" ]]; then
            local count=$(find "$CLAUDE_CONFIG_DIR/agents/cai/$category" -name "*.md" | wc -l)
            info "  - $category: $count agents"
        else
            warn "  - $category: directory not found"
        fi
    done
    
    if [[ $total_agents -lt 40 ]]; then
        warn "Expected 40+ agents, found $total_agents"
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
    local manifest_file="$CLAUDE_CONFIG_DIR/ai-craft-manifest.txt"
    
    cat > "$manifest_file" << EOF
AI-Craft Framework Installation Manifest
========================================
Installed: $(date)
Source: $SCRIPT_DIR
Version: Production Ready (2025-01-13)

Installation Summary:
- Total agents: $(find "$CLAUDE_CONFIG_DIR/agents" -name "*.md" | wc -l)
- Total commands: $(find "$CLAUDE_CONFIG_DIR/commands" -name "*.md" | wc -l)
- Installation directory: $CLAUDE_CONFIG_DIR
- Backup directory: $BACKUP_DIR

Framework Components:
- 41+ specialized AI agents with Single Responsibility Principle
- Wave processing architecture with clean context isolation
- cai/atdd command interface with intelligent project analysis
- Centralized configuration system (constants.md)
- Quality validation network with Level 1-6 refactoring
- Second Way DevOps: Observability agents (metrics, logs, traces, performance)
- Third Way DevOps: Experimentation agents (A/B testing, hypothesis validation, learning synthesis)

Agent Categories:
$(for category in requirements-analysis architecture-design test-design development quality-validation refactoring coordination observability experimentation; do
    if [[ -d "$CLAUDE_CONFIG_DIR/agents/$category" ]]; then
        count=$(find "$CLAUDE_CONFIG_DIR/agents/$category" -name "*.md" | wc -l)
        echo "- $category: $count agents"
    fi
done)

Usage:
- Use 'cai/atdd "feature description"' in any project
- All agents available globally across projects
- Centralized constants work project-wide

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
        info "${GREEN}✅ AI-Craft Framework installed successfully!${NC}"
        info ""
        info "Next steps:"
        info "1. Navigate to any project directory"
        info "2. Use: ${BLUE}cai/atdd \"your feature description\"${NC}"
        info "3. Access 41+ specialized agents globally"
        info ""
        info "For help: cai/atdd --help"
        info "Documentation: https://github.com/11PJ11/crafter-ai"
    else
        error "Installation failed validation"
        warn "You can restore the previous installation with: $0 --restore"
        exit 1
    fi
}

# Run main function with all arguments
main "$@"