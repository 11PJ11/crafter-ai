#!/bin/bash
# HookManager - Main facade for modular hook system
# Part of Claude Code SuperClaude modular hook system

set -euo pipefail

# Source core modules
HOOK_LIB_DIR="$(dirname "${BASH_SOURCE[0]}")"
source "${HOOK_LIB_DIR}/config/HookConfig.sh"
source "${HOOK_LIB_DIR}/logging/LogManager.sh"
source "${HOOK_LIB_DIR}/tools/ToolDetector.sh"

# Initialize hook system
init_hook_system() {
    hook_log "$LOG_LEVEL_DEBUG" "HookManager" "Initializing modular hook system v${HOOK_CONFIG_VERSION}"

    # Verify configuration
    if [ -f "$(get_hook_config_path)" ]; then
        hook_log "$LOG_LEVEL_DEBUG" "HookManager" "Configuration file found"
        return 0
    else
        hook_log "$LOG_LEVEL_ERROR" "HookManager" "Configuration file not found"
        return 1
    fi
}