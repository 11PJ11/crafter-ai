#!/bin/bash

# Enhanced Backup System for AI-Craft Framework Installation
# Prevents configuration loss and enables framework coexistence

set -euo pipefail

# Configuration
CLAUDE_CONFIG_DIR="$HOME/.claude"
BACKUP_ROOT_DIR="$CLAUDE_CONFIG_DIR/backups"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_DIR="$BACKUP_ROOT_DIR/pre_ai_craft_$TIMESTAMP"
MANIFEST_FILE="$BACKUP_DIR/backup_manifest.json"

# Logging
LOG_FILE="$CLAUDE_CONFIG_DIR/backup_system.log"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a "$LOG_FILE"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1" | tee -a "$LOG_FILE"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1" | tee -a "$LOG_FILE"
}

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1" | tee -a "$LOG_FILE"
}

# Backup System Functions

create_backup_structure() {
    log_info "Creating backup directory structure..."

    mkdir -p "$BACKUP_DIR"/{agents,commands,config,metadata}
    mkdir -p "$BACKUP_ROOT_DIR/restore_scripts"

    if [[ $? -eq 0 ]]; then
        log_success "Backup directory structure created at: $BACKUP_DIR"
    else
        log_error "Failed to create backup directory structure"
        exit 1
    fi
}

scan_existing_configuration() {
    log_info "Scanning existing Claude configuration..."

    local config_summary=""

    # Scan agents directory
    if [[ -d "$CLAUDE_CONFIG_DIR/agents" ]]; then
        local agent_count=$(find "$CLAUDE_CONFIG_DIR/agents" -name "*.md" 2>/dev/null | wc -l)
        config_summary+="Agents: $agent_count files found\n"
        log_info "Found $agent_count agent specification files"
    else
        config_summary+="Agents: No agents directory found\n"
        log_info "No agents directory found"
    fi

    # Scan commands directory
    if [[ -d "$CLAUDE_CONFIG_DIR/commands" ]]; then
        local cmd_count=$(find "$CLAUDE_CONFIG_DIR/commands" -name "*.md" 2>/dev/null | wc -l)
        config_summary+="Commands: $cmd_count files found\n"
        log_info "Found $cmd_count command files"
    else
        config_summary+="Commands: No commands directory found\n"
        log_info "No commands directory found"
    fi

    # Scan for SuperClaude specific files
    local sc_commands=0
    if [[ -d "$CLAUDE_CONFIG_DIR/commands" ]]; then
        sc_commands=$(find "$CLAUDE_CONFIG_DIR/commands" -name "*.md" -exec grep -l "sc:" {} \; 2>/dev/null | wc -l)
        config_summary+="SuperClaude Commands: $sc_commands files found\n"
        log_info "Found $sc_commands SuperClaude command files"
    fi

    # Scan configuration files
    local config_files=0
    if [[ -f "$CLAUDE_CONFIG_DIR/settings.local.json" ]]; then
        config_files=$((config_files + 1))
        config_summary+="Settings: settings.local.json found\n"
    fi

    echo -e "$config_summary" > "$BACKUP_DIR/metadata/scan_summary.txt"
    log_success "Configuration scan completed"
}

detect_framework_conflicts() {
    log_info "Detecting potential framework conflicts..."

    local conflicts_found=false
    local conflict_report="$BACKUP_DIR/metadata/conflict_analysis.json"

    # Initialize conflict report
    cat > "$conflict_report" << EOF
{
    "scan_timestamp": "$(date -Iseconds)",
    "conflicts_detected": false,
    "conflict_details": [],
    "recommendations": []
}
EOF

    # Check for AI-Craft existing installation
    if [[ -d "$CLAUDE_CONFIG_DIR/agents/cai" ]]; then
        log_warn "Existing AI-Craft installation detected"
        conflicts_found=true

        # Update conflict report
        jq '.conflicts_detected = true |
            .conflict_details += [{
                "type": "existing_ai_craft",
                "severity": "HIGH",
                "description": "AI-Craft agents already exist",
                "location": "agents/cai/",
                "recommendation": "Backup and merge with new installation"
            }]' "$conflict_report" > "${conflict_report}.tmp" && mv "${conflict_report}.tmp" "$conflict_report"
    fi

    # Check for SuperClaude commands
    if [[ -d "$CLAUDE_CONFIG_DIR/commands" ]]; then
        local sc_cmd_count=$(find "$CLAUDE_CONFIG_DIR/commands" -name "*.md" -exec grep -l "sc:" {} \; 2>/dev/null | wc -l)
        if [[ $sc_cmd_count -gt 0 ]]; then
            log_warn "SuperClaude commands detected: $sc_cmd_count files"
            conflicts_found=true

            # Update conflict report
            jq --arg count "$sc_cmd_count" '.conflicts_detected = true |
                .conflict_details += [{
                    "type": "superclaud_commands",
                    "severity": "CRITICAL",
                    "description": ("SuperClaude commands found: " + $count + " files"),
                    "location": "commands/",
                    "recommendation": "Implement namespace separation (/sc/ vs /cai/)"
                }]' "$conflict_report" > "${conflict_report}.tmp" && mv "${conflict_report}.tmp" "$conflict_report"
        fi
    fi

    # Check for command name collisions
    local ai_craft_commands=("atdd" "root-why")
    for cmd in "${ai_craft_commands[@]}"; do
        if [[ -f "$CLAUDE_CONFIG_DIR/commands/$cmd.md" ]]; then
            log_warn "Command collision detected: $cmd.md already exists"
            conflicts_found=true

            # Update conflict report
            jq --arg cmd "$cmd" '.conflicts_detected = true |
                .conflict_details += [{
                    "type": "command_collision",
                    "severity": "MEDIUM",
                    "description": ("Command file collision: " + $cmd + ".md"),
                    "location": ("commands/" + $cmd + ".md"),
                    "recommendation": "Rename existing or use namespace prefix"
                }]' "$conflict_report" > "${conflict_report}.tmp" && mv "${conflict_report}.tmp" "$conflict_report"
        fi
    done

    if [[ "$conflicts_found" == true ]]; then
        log_error "Framework conflicts detected! See: $conflict_report"
        return 1
    else
        log_success "No framework conflicts detected"
        return 0
    fi
}

backup_existing_configuration() {
    log_info "Creating comprehensive backup of existing configuration..."

    # Backup agents directory
    if [[ -d "$CLAUDE_CONFIG_DIR/agents" ]]; then
        cp -r "$CLAUDE_CONFIG_DIR/agents" "$BACKUP_DIR/agents/"
        log_success "Agents directory backed up"
    fi

    # Backup commands directory
    if [[ -d "$CLAUDE_CONFIG_DIR/commands" ]]; then
        cp -r "$CLAUDE_CONFIG_DIR/commands" "$BACKUP_DIR/commands/"
        log_success "Commands directory backed up"
    fi

    # Backup configuration files
    if [[ -f "$CLAUDE_CONFIG_DIR/settings.local.json" ]]; then
        cp "$CLAUDE_CONFIG_DIR/settings.local.json" "$BACKUP_DIR/config/"
        log_success "Configuration files backed up"
    fi

    # Create backup manifest
    generate_backup_manifest

    log_success "Configuration backup completed successfully"
}

generate_backup_manifest() {
    log_info "Generating backup manifest..."

    local total_files=0
    local agents_count=0
    local commands_count=0
    local config_count=0
    local superclaud_commands=0

    # Count backed up files
    if [[ -d "$BACKUP_DIR/agents" ]]; then
        agents_count=$(find "$BACKUP_DIR/agents" -type f -name "*.md" 2>/dev/null | wc -l)
        total_files=$((total_files + agents_count))
    fi

    if [[ -d "$BACKUP_DIR/commands" ]]; then
        commands_count=$(find "$BACKUP_DIR/commands" -type f -name "*.md" 2>/dev/null | wc -l)
        superclaud_commands=$(find "$BACKUP_DIR/commands" -name "*.md" -exec grep -l "sc:" {} \; 2>/dev/null | wc -l)
        total_files=$((total_files + commands_count))
    fi

    if [[ -d "$BACKUP_DIR/config" ]]; then
        config_count=$(find "$BACKUP_DIR/config" -type f 2>/dev/null | wc -l)
        total_files=$((total_files + config_count))
    fi

    # Generate manifest JSON
    cat > "$MANIFEST_FILE" << EOF
{
    "backup_metadata": {
        "timestamp": "$(date -Iseconds)",
        "backup_dir": "$BACKUP_DIR",
        "backup_type": "pre_ai_craft_installation",
        "claude_config_dir": "$CLAUDE_CONFIG_DIR"
    },
    "backup_summary": {
        "total_files": $total_files,
        "agents_backed_up": $agents_count,
        "commands_backed_up": $commands_count,
        "superclaud_commands": $superclaud_commands,
        "config_files_backed_up": $config_count
    },
    "backup_structure": {
        "agents": "$(if [[ -d $BACKUP_DIR/agents ]]; then echo true; else echo false; fi)",
        "commands": "$(if [[ -d $BACKUP_DIR/commands ]]; then echo true; else echo false; fi)",
        "config": "$(if [[ -d $BACKUP_DIR/config ]]; then echo true; else echo false; fi)",
        "metadata": true
    },
    "restoration_info": {
        "restoration_script": "$BACKUP_ROOT_DIR/restore_scripts/restore_$TIMESTAMP.sh",
        "conflict_analysis": "$BACKUP_DIR/metadata/conflict_analysis.json",
        "scan_summary": "$BACKUP_DIR/metadata/scan_summary.txt"
    },
    "framework_analysis": {
        "ai_craft_present": $(if [[ -d "$CLAUDE_CONFIG_DIR/agents/cai" ]]; then echo true; else echo false; fi),
        "superclaud_present": $(if [[ $superclaud_commands -gt 0 ]]; then echo true; else echo false; fi),
        "conflicts_detected": $(if [[ -f "$BACKUP_DIR/metadata/conflict_analysis.json" ]]; then jq '.conflicts_detected' "$BACKUP_DIR/metadata/conflict_analysis.json"; else echo false; fi)
    }
}
EOF

    log_success "Backup manifest generated: $MANIFEST_FILE"
}

generate_restoration_script() {
    log_info "Generating restoration script..."

    local restore_script="$BACKUP_ROOT_DIR/restore_scripts/restore_$TIMESTAMP.sh"

    cat > "$restore_script" << 'EOF'
#!/bin/bash

# AI-Craft Framework Configuration Restoration Script
# Generated automatically by enhanced backup system

set -euo pipefail

BACKUP_DIR="__BACKUP_DIR__"
CLAUDE_CONFIG_DIR="__CLAUDE_CONFIG_DIR__"
MANIFEST_FILE="$BACKUP_DIR/backup_manifest.json"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_error() { echo -e "${RED}[ERROR]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }

echo "=== AI-Craft Configuration Restoration ==="
echo "Backup Location: $BACKUP_DIR"
echo "Restore Target: $CLAUDE_CONFIG_DIR"
echo ""

if [[ ! -f "$MANIFEST_FILE" ]]; then
    log_error "Backup manifest not found: $MANIFEST_FILE"
    exit 1
fi

# Display backup information
echo "Backup Information:"
jq -r '.backup_metadata | "Timestamp: \(.timestamp)\nBackup Type: \(.backup_type)"' "$MANIFEST_FILE"
echo ""

# Show what will be restored
echo "Files to Restore:"
jq -r '.backup_summary | "Total Files: \(.total_files)\nAgents: \(.agents_backed_up)\nCommands: \(.commands_backed_up)\nSuperClaude Commands: \(.superclaud_commands)\nConfig Files: \(.config_files_backed_up)"' "$MANIFEST_FILE"
echo ""

read -p "Continue with restoration? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Restoration cancelled."
    exit 0
fi

# Backup current state before restoration
CURRENT_BACKUP="$CLAUDE_CONFIG_DIR/backups/pre_restore_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$CURRENT_BACKUP"
if [[ -d "$CLAUDE_CONFIG_DIR/agents" ]]; then
    cp -r "$CLAUDE_CONFIG_DIR/agents" "$CURRENT_BACKUP/" 2>/dev/null || true
fi
if [[ -d "$CLAUDE_CONFIG_DIR/commands" ]]; then
    cp -r "$CLAUDE_CONFIG_DIR/commands" "$CURRENT_BACKUP/" 2>/dev/null || true
fi
log_success "Current configuration backed up to: $CURRENT_BACKUP"

# Restore agents
if [[ -d "$BACKUP_DIR/agents" ]]; then
    mkdir -p "$CLAUDE_CONFIG_DIR/agents"
    cp -r "$BACKUP_DIR/agents"/* "$CLAUDE_CONFIG_DIR/agents/" 2>/dev/null || true
    log_success "Agents restored"
fi

# Restore commands
if [[ -d "$BACKUP_DIR/commands" ]]; then
    mkdir -p "$CLAUDE_CONFIG_DIR/commands"
    cp -r "$BACKUP_DIR/commands"/* "$CLAUDE_CONFIG_DIR/commands/" 2>/dev/null || true
    log_success "Commands restored"
fi

# Restore config files
if [[ -d "$BACKUP_DIR/config" ]]; then
    cp -r "$BACKUP_DIR/config"/* "$CLAUDE_CONFIG_DIR/" 2>/dev/null || true
    log_success "Configuration files restored"
fi

echo ""
log_success "Configuration restoration completed successfully!"
echo "Current state backup available at: $CURRENT_BACKUP"
EOF

    # Replace placeholders
    sed -i "s|__BACKUP_DIR__|$BACKUP_DIR|g" "$restore_script"
    sed -i "s|__CLAUDE_CONFIG_DIR__|$CLAUDE_CONFIG_DIR|g" "$restore_script"

    chmod +x "$restore_script"
    log_success "Restoration script generated: $restore_script"
}

implement_namespace_separation() {
    log_info "Implementing namespace separation for framework coexistence..."

    # Create namespace directory structure
    mkdir -p "$CLAUDE_CONFIG_DIR/commands/sc" 2>/dev/null || true
    mkdir -p "$CLAUDE_CONFIG_DIR/commands/cai" 2>/dev/null || true

    # Move SuperClaude commands to sc/ namespace if they exist
    if [[ -d "$CLAUDE_CONFIG_DIR/commands" ]]; then
        find "$CLAUDE_CONFIG_DIR/commands" -maxdepth 1 -name "*.md" -exec grep -l "sc:" {} \; | while read -r sc_file; do
            if [[ -f "$sc_file" ]]; then
                local filename=$(basename "$sc_file")
                mv "$sc_file" "$CLAUDE_CONFIG_DIR/commands/sc/$filename" 2>/dev/null || true
                log_info "Moved SuperClaude command to namespace: sc/$filename"
            fi
        done
    fi

    log_success "Namespace separation implemented"
}

# Main backup execution function
execute_comprehensive_backup() {
    log_info "Starting comprehensive backup system for AI-Craft installation..."

    # Create backup structure
    create_backup_structure

    # Scan existing configuration
    scan_existing_configuration

    # Detect potential conflicts
    if ! detect_framework_conflicts; then
        log_warn "Conflicts detected, but backup will continue..."
    fi

    # Backup existing configuration
    backup_existing_configuration

    # Generate restoration script
    generate_restoration_script

    # Implement namespace separation
    implement_namespace_separation

    log_success "Comprehensive backup completed successfully!"
    echo ""
    echo "=== Backup Summary ==="
    echo "Backup Location: $BACKUP_DIR"
    echo "Manifest File: $MANIFEST_FILE"
    echo "Restoration Script: $BACKUP_ROOT_DIR/restore_scripts/restore_$TIMESTAMP.sh"
    echo ""
    echo "Framework installation can now proceed safely."
    echo "Use 'bash restore_$TIMESTAMP.sh' to restore if needed."
}

# Command line interface
case "${1:-}" in
    "backup")
        execute_comprehensive_backup
        ;;
    "restore")
        if [[ -z "${2:-}" ]]; then
            log_error "Please specify backup timestamp for restoration"
            echo "Usage: $0 restore TIMESTAMP"
            echo "Available backups:"
            ls -1 "$BACKUP_ROOT_DIR" 2>/dev/null | grep "pre_ai_craft_" || echo "No backups found"
            exit 1
        fi
        RESTORE_TIMESTAMP="$2"
        RESTORE_SCRIPT="$BACKUP_ROOT_DIR/restore_scripts/restore_$RESTORE_TIMESTAMP.sh"
        if [[ -f "$RESTORE_SCRIPT" ]]; then
            bash "$RESTORE_SCRIPT"
        else
            log_error "Restoration script not found: $RESTORE_SCRIPT"
            exit 1
        fi
        ;;
    "list")
        echo "Available backups:"
        ls -la "$BACKUP_ROOT_DIR" 2>/dev/null | grep "pre_ai_craft_" || echo "No backups found"
        ;;
    "status")
        echo "Backup System Status:"
        echo "Claude Config Directory: $CLAUDE_CONFIG_DIR"
        echo "Backup Root Directory: $BACKUP_ROOT_DIR"
        echo "Log File: $LOG_FILE"
        echo ""
        if [[ -d "$BACKUP_ROOT_DIR" ]]; then
            local backup_count=$(ls -1 "$BACKUP_ROOT_DIR" 2>/dev/null | grep -c "pre_ai_craft_" || echo 0)
            echo "Available backups: $backup_count"
        else
            echo "No backup directory found"
        fi
        ;;
    *)
        echo "AI-Craft Enhanced Backup System"
        echo ""
        echo "Usage: $0 {backup|restore|list|status}"
        echo ""
        echo "Commands:"
        echo "  backup          Create comprehensive backup before AI-Craft installation"
        echo "  restore TIMESTAMP  Restore from specific backup"
        echo "  list           List available backups"
        echo "  status         Show backup system status"
        echo ""
        echo "Examples:"
        echo "  $0 backup                    # Create backup before installation"
        echo "  $0 restore 20250914_143022   # Restore specific backup"
        echo "  $0 list                      # Show available backups"
        exit 1
        ;;
esac
