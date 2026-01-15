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
    Installs the nWave methodology framework to your global Claude config directory.
    This makes all specialized agents and commands available across all projects.

USAGE:
    $0 [OPTIONS]

OPTIONS:
    --backup-only    Create backup of existing AI-Craft installation without installing
    --restore        Restore from the most recent backup
    --dry-run        Show what would be installed without making any changes
    --help           Show this help message

EXAMPLES:
    $0                      # Install nWave framework
    $0 --dry-run            # Show what would be installed (no changes made)
    $0 --backup-only        # Create backup only
    $0 --restore           # Restore from latest backup

WHAT GETS INSTALLED:
    - nWave specialized agents (DISCUSS→DESIGN→DISTILL→DEVELOP→DELIVER methodology)
    - nWave command interface for workflow orchestration
    - ATDD (Acceptance Test Driven Development) integration
    - Outside-In TDD with double-loop architecture
    - Quality validation network with Level 1-6 refactoring
    - 14-phase TDD enforcement hooks (installed in target projects via /nw:develop)

AUTOMATIC BUILD:
    This script automatically:
    1. Runs source embedding to update embedded hooks/templates
    2. Builds the IDE bundle if dist/ide/ doesn't exist
    3. Rebuilds if source files are newer than distribution
    No manual build step required!

INSTALLATION LOCATION:
    ~/.claude/agents/nw/    # nWave agent specifications
    ~/.claude/commands/nw/  # nWave command integrations

For more information: https://github.com/11PJ11/crafter-ai
EOF
}

# Run source embedding to ensure embedded content is up to date
run_embedding() {
    local embed_script="$PROJECT_ROOT/tools/embed_sources.py"

    if [[ -f "$embed_script" ]]; then
        info "Running source embedding to update embedded content..."
        if python3 "$embed_script" > /dev/null 2>&1; then
            info "Source embedding completed"
        else
            warn "Source embedding had issues, continuing anyway..."
        fi
    fi
}

# Build the IDE bundle
build_framework() {
    info "Building IDE bundle..."

    local build_script="$PROJECT_ROOT/scripts/build-ide-bundle.sh"

    if [[ ! -f "$build_script" ]]; then
        error "Build script not found at: $build_script"
        exit 1
    fi

    # Run build script (suppress verbose output, show errors)
    if bash "$build_script" 2>&1 | grep -E "(ERROR|Build completed|✅)" ; then
        info "Build completed successfully"
    else
        error "Build failed"
        exit 1
    fi
}

# Check if source framework exists, build if necessary
check_source() {
    info "Checking source framework..."

    # First, run embedding to ensure sources are up to date
    run_embedding

    # Check if dist/ide exists
    if [[ ! -d "$FRAMEWORK_SOURCE" ]]; then
        info "Distribution not found, building framework..."
        build_framework
    fi

    # Check for the built IDE distribution structure
    if [[ ! -d "$FRAMEWORK_SOURCE/agents/nw" ]] || [[ ! -d "$FRAMEWORK_SOURCE/commands/nw" ]]; then
        info "Distribution incomplete, rebuilding framework..."
        build_framework
    fi

    # Check if source files are newer than distribution
    local source_dir="$PROJECT_ROOT/nWave"
    local newest_source=$(find "$source_dir" -name "*.md" -o -name "*.py" -o -name "*.json" 2>/dev/null | xargs ls -t 2>/dev/null | head -1)
    local newest_dist=$(find "$FRAMEWORK_SOURCE" -name "*.md" 2>/dev/null | xargs ls -t 2>/dev/null | head -1)

    if [[ -n "$newest_source" ]] && [[ -n "$newest_dist" ]]; then
        if [[ "$newest_source" -nt "$newest_dist" ]]; then
            info "Source files are newer than distribution, rebuilding..."
            build_framework
        fi
    fi

    local agent_count=$(find "$FRAMEWORK_SOURCE/agents/nw" -name "*.md" ! -name "README.md" | wc -l)
    local command_count=$(find "$FRAMEWORK_SOURCE/commands/nw" -name "*.md" ! -name "README.md" | wc -l)

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
        if [[ -d "$FRAMEWORK_SOURCE/agents/nw" ]]; then
            local agent_count=$(find "$FRAMEWORK_SOURCE/agents/nw" -name "*.md" ! -name "README.md" | wc -l)
            info "${YELLOW}[DRY RUN]${NC} Would create: $CLAUDE_CONFIG_DIR/agents/nw"
            info "${YELLOW}[DRY RUN]${NC} Would install $agent_count agent files"
        fi

        # Show commands that would be installed
        info "${YELLOW}[DRY RUN]${NC} Would install commands..."
        if [[ -d "$FRAMEWORK_SOURCE/commands/nw" ]]; then
            local command_count=$(find "$FRAMEWORK_SOURCE/commands/nw" -name "*.md" ! -name "README.md" | wc -l)
            info "${YELLOW}[DRY RUN]${NC} Would create: $CLAUDE_CONFIG_DIR/commands"
            info "${YELLOW}[DRY RUN]${NC} Would install $command_count command files"
        fi

        return 0
    fi

    info "Installing AI-Craft framework to: $CLAUDE_CONFIG_DIR"

    # Create target directories
    mkdir -p "$CLAUDE_CONFIG_DIR"

    # Copy agents directory (excluding README.md)
    # Uses built dist/ide first, falls back to source nWave/agents if incomplete
    info "Installing agents..."
    local source_agent_dir="$PROJECT_ROOT/nWave/agents"
    local dist_agent_dir="$FRAMEWORK_SOURCE/agents/nw"
    local dist_agent_count=0
    local source_agent_count=0

    if [[ -d "$dist_agent_dir" ]]; then
        dist_agent_count=$(find "$dist_agent_dir" -name "*.md" ! -name "README.md" 2>/dev/null | wc -l)
    fi
    if [[ -d "$source_agent_dir" ]]; then
        source_agent_count=$(find "$source_agent_dir" -name "*.md" ! -name "README.md" 2>/dev/null | wc -l)
    fi

    mkdir -p "$CLAUDE_CONFIG_DIR/agents/nw"

    # Use dist if it has most agents, otherwise fall back to source
    if [[ $dist_agent_count -ge $((source_agent_count / 2)) ]] && [[ $dist_agent_count -gt 5 ]]; then
        info "Installing from built distribution ($dist_agent_count agents)..."
        find "$dist_agent_dir" -name "*.md" ! -name "README.md" | while read -r file; do
            local relative_path="${file#$dist_agent_dir/}"
            local target_file="$CLAUDE_CONFIG_DIR/agents/nw/$relative_path"
            local target_dir=$(dirname "$target_file")
            mkdir -p "$target_dir"
            cp "$file" "$target_file"
        done
    else
        # Fallback: copy from source (agents work without embedding)
        info "Build incomplete ($dist_agent_count/$source_agent_count agents), using source files..."
        find "$source_agent_dir" -name "*.md" ! -name "README.md" | while read -r file; do
            local relative_path="${file#$source_agent_dir/}"
            local target_file="$CLAUDE_CONFIG_DIR/agents/nw/$relative_path"
            local target_dir=$(dirname "$target_file")
            mkdir -p "$target_dir"
            cp "$file" "$target_file"
        done
    fi

    local copied_agents=$(find "$CLAUDE_CONFIG_DIR/agents/nw" -name "*.md" | wc -l)
    info "Installed $copied_agents agent files"

    # Copy commands directory
    info "Installing commands..."
    if [[ -d "$FRAMEWORK_SOURCE/commands/nw" ]]; then
        mkdir -p "$CLAUDE_CONFIG_DIR/commands"
        cp -r "$FRAMEWORK_SOURCE/commands/"* "$CLAUDE_CONFIG_DIR/commands/"

        local copied_commands=$(find "$CLAUDE_CONFIG_DIR/commands" -name "*.md" | wc -l)
        info "Installed $copied_commands command files"

        if [[ -d "$CLAUDE_CONFIG_DIR/commands/nw" ]]; then
            local dw_commands=$(find "$CLAUDE_CONFIG_DIR/commands/nw" -name "*.md" | wc -l)
            info "  - DW commands: $dw_commands essential commands"
        fi
    fi

    # Copy utility scripts for target projects
    info "Installing utility scripts..."
    local scripts_source="$PROJECT_ROOT/scripts"
    local scripts_target="$CLAUDE_CONFIG_DIR/scripts"

    mkdir -p "$scripts_target"

    # Helper function to extract version from Python script (macOS compatible)
    get_script_version() {
        local script_path="$1"
        if [[ -f "$script_path" ]]; then
            # Use awk for portability (grep -P not available on macOS)
            awk -F'"' '/__version__/ {print $2; exit}' "$script_path" 2>/dev/null || echo "0.0.0"
        else
            echo "0.0.0"
        fi
    }

    # Helper function to compare semver (returns 0 if $1 > $2, 1 if $1 <= $2)
    version_gt() {
        test "$(printf '%s\n' "$1" "$2" | sort -V | head -n 1)" != "$1"
    }

    # Copy/update the nWave target hooks installer
    local source_script="$scripts_source/install_nwave_target_hooks.py"
    local target_script="$scripts_target/install_nwave_target_hooks.py"
    if [[ -f "$source_script" ]]; then
        local source_ver=$(get_script_version "$source_script")
        local target_ver=$(get_script_version "$target_script")
        if version_gt "$source_ver" "$target_ver"; then
            cp "$source_script" "$target_script"
            info "Upgraded install_nwave_target_hooks.py ($target_ver → $source_ver)"
        elif [[ ! -f "$target_script" ]]; then
            cp "$source_script" "$target_script"
            info "Installed install_nwave_target_hooks.py (v$source_ver)"
        else
            info "install_nwave_target_hooks.py already up-to-date (v$target_ver)"
        fi
    fi

    # Copy/update the step file validator
    source_script="$scripts_source/validate_step_file.py"
    target_script="$scripts_target/validate_step_file.py"
    if [[ -f "$source_script" ]]; then
        local source_ver=$(get_script_version "$source_script")
        local target_ver=$(get_script_version "$target_script")
        if version_gt "$source_ver" "$target_ver"; then
            cp "$source_script" "$target_script"
            info "Upgraded validate_step_file.py ($target_ver → $source_ver)"
        elif [[ ! -f "$target_script" ]]; then
            cp "$source_script" "$target_script"
            info "Installed validate_step_file.py (v$source_ver)"
        else
            info "validate_step_file.py already up-to-date (v$target_ver)"
        fi
    fi

    local copied_scripts=$(find "$scripts_target" -name "*.py" 2>/dev/null | wc -l)
    if [[ $copied_scripts -gt 0 ]]; then
        info "Total $copied_scripts utility script(s) installed"
    fi

    # Install templates (canonical schema files)
    info "Installing templates..."
    local templates_source="$PROJECT_ROOT/nWave/templates"
    local templates_target="$CLAUDE_CONFIG_DIR/templates"

    mkdir -p "$templates_target"

    # Copy the canonical step file schema
    local schema_file="step-tdd-cycle-schema.json"
    if [[ -f "$templates_source/$schema_file" ]]; then
        cp "$templates_source/$schema_file" "$templates_target/$schema_file"
        info "Installed canonical schema: $schema_file"
    fi

    local copied_templates=$(find "$templates_target" -name "*.json" 2>/dev/null | wc -l)
    if [[ $copied_templates -gt 0 ]]; then
        info "Total $copied_templates template(s) installed"
    fi
}

# Validate installation
validate_installation() {
    info "Validating installation..."

    local errors=0

    # Check that agents are installed
    if [[ ! -d "$CLAUDE_CONFIG_DIR/agents/nw" ]]; then
        error "Missing DW agents directory"
        ((errors++)) || true
    fi

    # Check that commands are installed
    if [[ ! -d "$CLAUDE_CONFIG_DIR/commands/nw" ]]; then
        error "Missing DW commands directory"
        ((errors++)) || true
    fi

    # Check essential DW commands exist
    local essential_commands=("discuss" "design" "distill" "develop" "deliver")
    for cmd in "${essential_commands[@]}"; do
        if [[ ! -f "$CLAUDE_CONFIG_DIR/commands/nw/$cmd.md" ]]; then
            error "Missing essential DW command: $cmd.md"
            ((errors++)) || true
        fi
    done

    # Count installed files
    local total_agents=$(find "$CLAUDE_CONFIG_DIR/agents/nw" -name "*.md" 2>/dev/null | wc -l)
    local total_commands=$(find "$CLAUDE_CONFIG_DIR/commands" -name "*.md" 2>/dev/null | wc -l)

    info "Installation summary:"
    info "  - Agents installed: $total_agents"
    info "  - Commands installed: $total_commands"
    info "  - Installation directory: $CLAUDE_CONFIG_DIR"

    if [[ -d "$CLAUDE_CONFIG_DIR/agents/nw" ]]; then
        info "  - nWave agents: Available"
    fi

    if [[ -d "$CLAUDE_CONFIG_DIR/commands/nw" ]]; then
        info "  - nWave commands: Available"
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
- Use nWave commands: '/nw:discuss', '/nw:design', '/nw:distill', '/nw:develop', '/nw:deliver'
- Use '/nw:start "feature description"' to initialize nWave workflow
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
        info "${GREEN}✅ nWave Framework installed successfully!${NC}"
        info ""
        info "Framework Components Installed:"
        info "- nWave specialized agents (DISCUSS→DESIGN→DISTILL→DEVELOP→DELIVER)"
        info "- nWave command interface for workflow orchestration"
        info "- ATDD and Outside-In TDD integration"
        info ""
        info "Next steps:"
        info "1. Navigate to any project directory"
        info "2. Use nWave commands to orchestrate development workflow"
        info "3. Access agents through the dw category in Claude Code"
        info ""
        info "nWave methodology available:"
        info "- ${BLUE}/nw:discuss${NC} - Requirements gathering and business analysis"
        info "- ${BLUE}/nw:design${NC} - Architecture design with visual representation"
        info "- ${BLUE}/nw:distill${NC} - Acceptance test creation and business validation"
        info "- ${BLUE}/nw:develop${NC} - Outside-In TDD implementation with refactoring"
        info "- ${BLUE}/nw:deliver${NC} - Production readiness validation"
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
