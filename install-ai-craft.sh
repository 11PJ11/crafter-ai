#!/bin/bash
# AI-Craft Framework Installation Script for Linux/WSL
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
AI-Craft Framework Installation Script for Linux/WSL

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
    - 14+ CAI command interface with intelligent project analysis
    - Manual system with Linux-style documentation for all commands
    - /cai:man command for comprehensive documentation access
    - Enhanced argument hints for improved command visibility
    - Centralized configuration system (constants.md)
    - Wave processing architecture for clean ATDD workflows
    - Quality validation network with Level 1-6 refactoring
    - Auto-lint and format hooks for code quality (Python, JavaScript, JSON, etc.)
    - Second Way DevOps: Observability agents (metrics, logs, traces, performance)
    - Third Way DevOps: Experimentation agents (A/B testing, hypothesis validation, learning synthesis)

INSTALLATION LOCATION:
    ~/.claude/agents/       # All agent specifications
    ~/.claude/commands/     # Command integrations
    ~/.claude/manuals/      # Manual system documentation

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

    # Backup existing manuals directory
    if [[ -d "$CLAUDE_CONFIG_DIR/manuals" ]]; then
        cp -r "$CLAUDE_CONFIG_DIR/manuals" "$BACKUP_DIR/"
        info "Backed up manuals directory"
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
    rm -rf "$CLAUDE_CONFIG_DIR/agents" "$CLAUDE_CONFIG_DIR/commands/cai" "$CLAUDE_CONFIG_DIR/manuals" 2>/dev/null || true

    # Restore from backup
    if [[ -d "$latest_backup/agents" ]]; then
        cp -r "$latest_backup/agents" "$CLAUDE_CONFIG_DIR/"
        info "Restored agents directory"
    fi

    if [[ -d "$latest_backup/commands" ]]; then
        cp -r "$latest_backup/commands" "$CLAUDE_CONFIG_DIR/"
        info "Restored commands directory"
    fi

    if [[ -d "$latest_backup/manuals" ]]; then
        cp -r "$latest_backup/manuals" "$CLAUDE_CONFIG_DIR/"
        info "Restored manuals directory"
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

        # List installed CAI commands for verification
        if [[ -d "$CLAUDE_CONFIG_DIR/commands/cai" ]]; then
            local cai_commands=$(find "$CLAUDE_CONFIG_DIR/commands/cai" -name "*.md" | wc -l)
            info "  - CAI commands: $cai_commands essential commands"
        fi
    fi

    # Install manual system
    info "Installing manual system..."
    if [[ -d "$FRAMEWORK_SOURCE/manuals" ]]; then
        mkdir -p "$CLAUDE_CONFIG_DIR/manuals/cai"
        cp -r "$FRAMEWORK_SOURCE/manuals/cai/"*.json "$CLAUDE_CONFIG_DIR/manuals/cai/"

        local copied_manuals=$(find "$CLAUDE_CONFIG_DIR/manuals/cai" -name "*.json" 2>/dev/null | wc -l)
        info "Installed $copied_manuals manual files"

        # Verify essential manual files
        if [[ -f "$CLAUDE_CONFIG_DIR/manuals/cai/index.json" ]]; then
            info "  - Manual system index: installed"
        fi
    fi

    # Install hooks
    install_craft_ai_hooks
}

# Install Craft-AI specific hooks (surgical approach)
install_craft_ai_hooks() {
    info "Installing Craft-AI workflow hooks..."

    # Create hooks directory structure (no cai subdirectory)
    mkdir -p "$CLAUDE_CONFIG_DIR/hooks"

    # Copy hooks directly to the hooks directory (preserve other hooks)
    if [[ -d "$FRAMEWORK_SOURCE/hooks" ]]; then
        # Copy the entire modular hook structure directly
        cp -r "$FRAMEWORK_SOURCE/hooks/"* "$CLAUDE_CONFIG_DIR/hooks/"

        # Make scripts executable
        find "$CLAUDE_CONFIG_DIR/hooks" -name "*.sh" -exec chmod +x {} \;
        find "$CLAUDE_CONFIG_DIR/hooks" -name "*.py" -exec chmod +x {} \;

        local hook_files=$(find "$CLAUDE_CONFIG_DIR/hooks" -type f -name "*.sh" -o -name "*.py" | wc -l)
        info "Installed $hook_files Craft-AI hook files to hooks/"
    else
        warn "Hook source directory not found: $FRAMEWORK_SOURCE/hooks"
    fi

    # Merge hooks into settings (preserve existing)
    merge_hook_settings
}

# Surgically merge hook settings without overwriting existing
merge_hook_settings() {
    local settings_file="$CLAUDE_CONFIG_DIR/settings.local.json"
    local hooks_config="$CLAUDE_CONFIG_DIR/hooks/config/hooks-config.json"

    # Create backup of current settings
    if [[ -f "$settings_file" ]]; then
        cp "$settings_file" "$settings_file.pre-cai-backup"
        info "Created backup: $settings_file.pre-cai-backup"
    fi

    # Use Python to surgically merge CAI hooks
    if [[ -f "$hooks_config" ]] && command -v python3 >/dev/null 2>&1; then
        python3 << 'PYTHON_SCRIPT'
import json
import os
import sys

settings_file = os.path.expanduser("~/.claude/settings.local.json")
hooks_config = os.path.expanduser("~/.claude/hooks/config/hooks-config.json")

# Load CAI hooks configuration
try:
    with open(hooks_config, 'r') as f:
        cai_config = json.load(f)
except Exception as e:
    print(f"Error loading hooks config: {e}")
    sys.exit(1)

# Load existing settings or create new
settings = {}
if os.path.exists(settings_file):
    try:
        with open(settings_file, 'r') as f:
            settings = json.load(f)
    except Exception:
        settings = {}

# Initialize hooks if not present
if 'hooks' not in settings:
    settings['hooks'] = {}

# Merge CAI hooks without removing existing ones
cai_hooks = cai_config.get('hooks', {})
for event, new_hooks_list in cai_hooks.items():
    if event not in settings['hooks']:
        settings['hooks'][event] = []

    # Add new CAI hooks without duplicating
    for new_hook in new_hooks_list:
        # Check if this CAI hook already exists (by id)
        hook_id = new_hook.get('hooks', [{}])[0].get('id', '')
        exists = any(
            h.get('hooks', [{}])[0].get('id') == hook_id
            for h in settings['hooks'][event]
            if 'hooks' in h and h['hooks'] and hook_id
        )
        if not exists and hook_id:
            # Update command path to use actual home directory
            for hook in new_hook.get('hooks', []):
                if 'command' in hook and '$HOME' in hook['command']:
                    hook['command'] = hook['command'].replace('$HOME', os.path.expanduser('~'))
            settings['hooks'][event].append(new_hook)

# Initialize permissions if not present
if 'permissions' not in settings:
    settings['permissions'] = {'allow': [], 'deny': [], 'ask': []}

# Add CAI-specific permissions without duplicating
cai_permissions = cai_config.get('permissions', {}).get('allow', [])
for perm in cai_permissions:
    # Replace $HOME with actual path
    perm = perm.replace('$HOME', os.path.expanduser('~'))
    if perm not in settings['permissions']['allow']:
        settings['permissions']['allow'].append(perm)

# Save merged settings
try:
    with open(settings_file, 'w') as f:
        json.dump(settings, f, indent=2)
    print("Successfully merged Craft-AI hooks into settings")
except Exception as e:
    print(f"Error saving settings: {e}")
    sys.exit(1)
PYTHON_SCRIPT

        if [[ $? -eq 0 ]]; then
            info "Successfully merged CAI hooks into settings.local.json"
        else
            warn "Failed to merge hooks configuration - manual setup may be required"
        fi
    else
        warn "Python3 not available or hooks config missing - hooks not configured"
    fi
}

# Validate hook installation
validate_hooks() {
    info "Validating hook installation..."

    local errors=0

    # Check hook files exist - updated for refactored modular structure
    local required_workflow_hooks=("state-initializer.sh" "input-validator.sh" "stage-transition.sh")
    local required_quality_hooks=("lint-format.sh")

    for hook in "${required_workflow_hooks[@]}"; do
        if [[ ! -f "$CLAUDE_CONFIG_DIR/hooks/workflow/$hook" ]]; then
            error "Missing workflow hook: $hook"
            ((errors++))
        fi
    done

    for hook in "${required_quality_hooks[@]}"; do
        if [[ ! -f "$CLAUDE_CONFIG_DIR/hooks/code-quality/$hook" ]]; then
            error "Missing quality hook: $hook"
            ((errors++))
        fi
    done

    # Check core library exists
    if [[ ! -f "$CLAUDE_CONFIG_DIR/hooks/lib/HookManager.sh" ]]; then
        error "Missing core hook library: HookManager.sh"
        ((errors++))
    fi

    # Check hook permissions
    for hook in "$CLAUDE_CONFIG_DIR/hooks/"**/*.{sh,py}; do
        if [[ -f "$hook" ]] && [[ ! -x "$hook" ]]; then
            warn "Hook not executable: $hook"
            chmod +x "$hook" 2>/dev/null || true
        fi
    done

    # Check settings integration
    if [[ -f "$CLAUDE_CONFIG_DIR/settings.local.json" ]]; then
        if grep -q '"cai-' "$CLAUDE_CONFIG_DIR/settings.local.json" 2>/dev/null; then
            info "CAI hooks configured in settings.local.json"
        else
            warn "CAI hooks may not be properly configured in settings"
        fi
    else
        warn "settings.local.json not found"
    fi

    if [[ $errors -eq 0 ]]; then
        info "Hook validation: ${GREEN}PASSED${NC}"
        return 0
    else
        error "Hook validation: ${RED}FAILED${NC} ($errors errors)"
        return 1
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
    
    # Check essential CAI commands exist
    local essential_commands=("brownfield" "refactor" "start" "discuss" "architect" "develop" "transition" "validate" "complete" "skeleton" "help" "man")
    for cmd in "${essential_commands[@]}"; do
        if [[ ! -f "$CLAUDE_CONFIG_DIR/commands/cai/$cmd.md" ]]; then
            error "Missing essential CAI command: $cmd.md"
            ((errors++))
        fi
    done

    # Check manual system files
    if [[ ! -f "$CLAUDE_CONFIG_DIR/manuals/cai/index.json" ]]; then
        error "Missing manual system index file"
        ((errors++))
    fi

    local manual_files=$(find "$CLAUDE_CONFIG_DIR/manuals/cai" -name "*.json" 2>/dev/null | wc -l)
    if [[ $manual_files -lt 14 ]]; then
        warn "Expected 14+ manual files, found $manual_files"
    fi
    
    # Count installed files
    local total_agents=$(find "$CLAUDE_CONFIG_DIR/agents/cai" -name "*.md" 2>/dev/null | wc -l)
    local total_commands=$(find "$CLAUDE_CONFIG_DIR/commands" -name "*.md" 2>/dev/null | wc -l)
    local total_manuals=$(find "$CLAUDE_CONFIG_DIR/manuals/cai" -name "*.json" 2>/dev/null | wc -l)

    info "Installation summary:"
    info "  - Agents installed: $total_agents"
    info "  - Commands installed: $total_commands"
    info "  - Manuals installed: $total_manuals"
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
- 11 essential CAI commands: brownfield, refactor, start, discuss, architect, develop, transition, validate, complete, skeleton, help
- Centralized configuration system (constants.md)
- Quality validation network with Level 1-6 refactoring
- Auto-lint and format hooks for code quality (Python, JavaScript, JSON, etc.)
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
- Use CAI commands: 'cai:brownfield', 'cai:refactor', 'cai:start', etc.
- Use 'cai:start "feature description"' to initialize ATDD workflow
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
    
    if validate_installation && validate_hooks; then
        create_manifest
        info ""
        info "${GREEN}✅ AI-Craft Framework installed successfully!${NC}"
        info ""
        info "Framework Components Installed:"
        info "- 41+ specialized AI agents"
        info "- 11 essential CAI commands (brownfield, refactor, start, skeleton, etc.)"
        info "- Claude Code workflow hooks"
        info "- Auto-lint and format hooks for code quality"
        info "- Quality validation network"
        info ""
        info "Next steps:"
        info "1. Navigate to any project directory"
        info "2. Use: ${BLUE}cai:start \"your feature description\"${NC} to initialize ATDD workflow"
        info "3. Use: ${BLUE}cai:brownfield${NC} for existing codebase analysis"
        info "4. Use: ${BLUE}cai:help${NC} for interactive guidance and command reference"
        info "5. Agents will automatically follow ATDD workflow"
        info ""
        info "${YELLOW}Hook System Logging Configuration:${NC}"
        info "- Default: Silent operation (HOOK_LOG_LEVEL=0)"
        info "- Enable logging: ${BLUE}echo 'export HOOK_LOG_LEVEL=2' >> ~/.bashrc${NC}"
        info "- Test logging: ${BLUE}env HOOK_LOG_LEVEL=3 ~/.claude/hooks/code-quality/lint-format.sh test.py${NC}"
        info "- Full guide: ${BLUE}LOGGING_CONFIGURATION.md${NC}"
        info ""
        info "Command examples:"
        info "- ${BLUE}cai:brownfield --legacy \"my-project\"${NC}"
        info "- ${BLUE}cai:refactor \"module\" --level 3${NC}"
        info "- ${BLUE}cai:start \"new feature\" --interactive${NC}"
        info "Documentation: https://github.com/11PJ11/crafter-ai"
    else
        error "Installation failed validation"
        warn "You can restore the previous installation with: $0 --restore"
        exit 1
    fi
}

# Run main function with all arguments
main "$@"